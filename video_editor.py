import glob
import subprocess
import eel

eel.init('Gui')

CODECS = {"h264": "H.264", "hevc": "HEVC (H.265)", "av1": "AV1"}

# Constant quality for each codec, the values give roughly the same quality as libx264 -crf 23
QUALITY = {"h264": "23", "hevc": "26", "av1": "30"}

def make_encoder(id, name, codec, args, input_args=None, filter=None):
    return {"id": id, "name": name, "codec": codec, "input_args": input_args or [], "filter": filter, "args": args}

# CPU encoders, the first one that works for each codec is kept
def cpu_candidates(codec):
    if codec == "h264":
        return [make_encoder("cpu", "CPU (libx264)", "libx264", ["-crf", "23"])]
    if codec == "hevc":
        return [make_encoder("cpu", "CPU (libx265)", "libx265", ["-crf", "28", "-tag:v", "hvc1"])]
    return [
        make_encoder("cpu", "CPU (SVT-AV1)", "libsvtav1", ["-crf", "35", "-preset", "8"]),
        make_encoder("cpu", "CPU (libaom-av1)", "libaom-av1", ["-crf", "35", "-b:v", "0", "-cpu-used", "6", "-row-mt", "1"]),
    ]

# Hardware encoders in order of preference. The first working candidate of each id is kept
def hardware_candidates(codec):
    q = QUALITY[codec]
    tag = ["-tag:v", "hvc1"] if codec == "hevc" else []
    amf_qp = ["-qp_i", q, "-qp_p", q] + (["-qp_b", q] if codec == "h264" else [])
    candidates = [
        make_encoder("nvenc", "NVIDIA NVENC", f"{codec}_nvenc", ["-rc", "vbr", "-cq", q, "-b:v", "0", *tag]),
        make_encoder("qsv", "Intel Quick Sync", f"{codec}_qsv", ["-global_quality", q, *tag]),
        make_encoder("amf", "AMD AMF", f"{codec}_amf", ["-quality", "balanced", "-rc", "cqp", *amf_qp, *tag]),
    ]
    # VAAPI (AMD/Intel on Linux) needs a render device and frames uploaded to the GPU
    vaapi_quality = ["-rc_mode", "CQP", "-global_quality", q] if codec == "av1" else ["-qp", q]
    for device in sorted(glob.glob("/dev/dri/renderD*")):
        candidates.append(make_encoder("vaapi", "VAAPI", f"{codec}_vaapi", [*vaapi_quality, *tag], ["-vaapi_device", device], "format=nv12,hwupload"))
    # VideoToolbox can't encode AV1. Constant quality only works on Apple Silicon, Intel Macs fall back to a fixed bitrate
    if codec != "av1":
        candidates.append(make_encoder("videotoolbox", "Apple VideoToolbox", f"{codec}_videotoolbox", ["-q:v", "65", *tag]))
        candidates.append(make_encoder("videotoolbox", "Apple VideoToolbox", f"{codec}_videotoolbox", ["-b:v", "12M", *tag]))
    return candidates

def encoder_works(encoder):
    # Encode a few blank frames to check that the hardware and drivers are actually usable
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", *encoder["input_args"], "-f", "lavfi", "-i", "color=c=black:s=1280x720:r=30"]
    if encoder["filter"]:
        cmd += ["-vf", encoder["filter"]]
    cmd += ["-frames:v", "10", "-c:v", encoder["codec"], *encoder["args"], "-f", "null", "-"]
    try:
        return subprocess.run(cmd, capture_output=True, timeout=30).returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False

available_encoders = None

# Returns {codec: [encoders]} with only the codecs that have at least one working encoder.
# The CPU encoder, when available, is always the last one of each list
def get_available_encoders():
    global available_encoders
    if available_encoders is None:
        try:
            compiled = subprocess.run(["ffmpeg", "-hide_banner", "-encoders"], capture_output=True, text=True).stdout.split()
        except OSError:
            compiled = []
        available_encoders = {}
        for codec in CODECS:
            encoders = []
            for encoder in hardware_candidates(codec) + cpu_candidates(codec):
                found = any(e["id"] == encoder["id"] for e in encoders)
                if not found and encoder["codec"] in compiled and encoder_works(encoder):
                    encoders.append(encoder)
            if encoders:
                available_encoders[codec] = encoders
        if "h264" not in available_encoders:
            # Keep at least libx264 so the list is never empty, FFmpeg will report the error if it's missing
            available_encoders["h264"] = cpu_candidates("h264")
    return available_encoders

def select_encoder(codec, encoder_id):
    encoders = get_available_encoders()
    if codec not in encoders:
        print(f"[warning] Codec {codec} not available, using H.264")
        codec = "h264"
    for encoder in encoders[codec]:
        if encoder["id"] == encoder_id:
            return encoder
    if encoder_id != "auto":
        print(f"[warning] Encoder {encoder_id} not available, using automatic selection")
    return encoders[codec][0]

def fallback_encoder(codec):
    # CPU encoder of the same codec, or libx264 if the codec has no CPU encoder
    for encoder in get_available_encoders().get(codec, []):
        if encoder["id"] == "cpu":
            return encoder
    return cpu_candidates("h264")[0]

def get_video_info(file):
    cmd = f'ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate -of default=noprint_wrappers=1:nokey=1 "{file}"'
    info = subprocess.check_output(cmd, shell=True).decode("utf-8").strip().split("\n")
    width, height, framerate = int(info[0]), int(info[1]), eval(info[2])
    return {"width": width, "height": height, "fps": framerate}

def build_command(submission_file, final_video_name, width, height, fps, encoder):
    video_filter = f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={fps}"
    filter_complex = f"[0:v:0]{video_filter}[v0];[0:a:0]asetrate=48000[a0];[1:v:0]{video_filter}[v1];[1:a:0]asetrate=48000[a1];[v0][a0][v1][a1]concat=n=2:v=1:a=1"
    if encoder["filter"]:
        filter_complex += f"[vc][a];[vc]{encoder['filter']}[v]"
    else:
        filter_complex += "[v][a]"
    return ["ffmpeg", "-y", *encoder["input_args"], "-i", "intro.mp4", "-i", submission_file, "-filter_complex", filter_complex, "-map", "[v]", "-map", "[a]", "-c:v", encoder["codec"], *encoder["args"], "-c:a", "aac", final_video_name]

def main(submission_file, file_name, codec="h264", encoder_id="auto"):
    final_video_name = f"Gui/Videos/{file_name}.mp4"

    # Get video information
    intro_info = get_video_info("intro.mp4")
    submission_info = get_video_info(submission_file)

    # Determine the highest resolution and framerate
    max_width = max(intro_info["width"], submission_info["width"])
    max_height = max(intro_info["height"], submission_info["height"])
    max_fps = max(intro_info["fps"], submission_info["fps"])

    # Encode with the selected encoder, falling back to the CPU if the hardware encoder fails
    encoder = select_encoder(codec, encoder_id)
    eel.print_output(f"Encoding with {encoder['name']} ({encoder['codec']})...")
    print(f"--> Encoding with {encoder['name']} ({encoder['codec']})")
    result = subprocess.run(build_command(submission_file, final_video_name, max_width, max_height, max_fps, encoder))
    if result.returncode != 0 and encoder["id"] != "cpu":
        cpu = fallback_encoder(codec)
        print(f"[warning] {encoder['name']} encoding failed, retrying with {cpu['name']}")
        eel.print_output(f"[warning] {encoder['name']} encoding failed, retrying with {cpu['name']}")
        result = subprocess.run(build_command(submission_file, final_video_name, max_width, max_height, max_fps, cpu))
    if result.returncode != 0:
        eel.print_output("[error] FFmpeg failed to encode the video, check the terminal for details")
    else:
        eel.print_output("Encoding complete")
        eel.Show("editor")
        eel.Videos(final_video_name, "editor", file_name)
    eel.EnableStartButton()
    #eel.Show("uploader")
