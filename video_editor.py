import glob
import subprocess
import eel

eel.init('Gui')

CPU_ENCODER = {"id": "cpu", "name": "CPU (libx264)", "codec": "libx264", "input_args": [], "filter": None, "args": ["-crf", "23"]}

# Hardware encoders in order of preference. The first working candidate of each id is kept,
# quality settings roughly match libx264 -crf 23
def hardware_candidates():
    candidates = [
        {"id": "nvenc", "name": "NVIDIA NVENC", "codec": "h264_nvenc", "input_args": [], "filter": None, "args": ["-rc", "vbr", "-cq", "23", "-b:v", "0"]},
        {"id": "qsv", "name": "Intel Quick Sync", "codec": "h264_qsv", "input_args": [], "filter": None, "args": ["-global_quality", "23"]},
        {"id": "amf", "name": "AMD AMF", "codec": "h264_amf", "input_args": [], "filter": None, "args": ["-quality", "balanced", "-rc", "cqp", "-qp_i", "23", "-qp_p", "23", "-qp_b", "23"]},
    ]
    # VAAPI (AMD/Intel on Linux) needs a render device and frames uploaded to the GPU
    for device in sorted(glob.glob("/dev/dri/renderD*")):
        candidates.append({"id": "vaapi", "name": "VAAPI", "codec": "h264_vaapi", "input_args": ["-vaapi_device", device], "filter": "format=nv12,hwupload", "args": ["-qp", "23"]})
    # Constant quality only works on Apple Silicon, Intel Macs fall back to a fixed bitrate
    candidates.append({"id": "videotoolbox", "name": "Apple VideoToolbox", "codec": "h264_videotoolbox", "input_args": [], "filter": None, "args": ["-q:v", "65"]})
    candidates.append({"id": "videotoolbox", "name": "Apple VideoToolbox", "codec": "h264_videotoolbox", "input_args": [], "filter": None, "args": ["-b:v", "12M"]})
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

def get_available_encoders():
    global available_encoders
    if available_encoders is None:
        try:
            compiled = subprocess.run(["ffmpeg", "-hide_banner", "-encoders"], capture_output=True, text=True).stdout.split()
        except OSError:
            compiled = []
        available_encoders = []
        for encoder in hardware_candidates():
            found = any(e["id"] == encoder["id"] for e in available_encoders)
            if not found and encoder["codec"] in compiled and encoder_works(encoder):
                available_encoders.append(encoder)
        available_encoders.append(CPU_ENCODER)
    return available_encoders

def select_encoder(encoder_id):
    if encoder_id == "cpu":
        return CPU_ENCODER
    encoders = get_available_encoders()
    for encoder in encoders:
        if encoder["id"] == encoder_id:
            return encoder
    if encoder_id != "auto":
        print(f"[warning] Encoder {encoder_id} not available, using automatic selection")
    return encoders[0]

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

def main(submission_file, player, bsr, encoder_id="auto"):
    final_video_name = f"Gui/Videos/{player}_{bsr}.mp4"

    # Get video information
    intro_info = get_video_info("intro.mp4")
    submission_info = get_video_info(submission_file)

    # Determine the highest resolution and framerate
    max_width = max(intro_info["width"], submission_info["width"])
    max_height = max(intro_info["height"], submission_info["height"])
    max_fps = max(intro_info["fps"], submission_info["fps"])

    # Encode with the selected encoder, falling back to the CPU if the hardware encoder fails
    encoder = select_encoder(encoder_id)
    print(f"--> Encoding with {encoder['name']}")
    result = subprocess.run(build_command(submission_file, final_video_name, max_width, max_height, max_fps, encoder))
    if result.returncode != 0 and encoder is not CPU_ENCODER:
        print(f"[warning] {encoder['name']} encoding failed, retrying with {CPU_ENCODER['name']}")
        subprocess.run(build_command(submission_file, final_video_name, max_width, max_height, max_fps, CPU_ENCODER))

    eel.Show("editor")
    eel.Videos(final_video_name, "editor", player, bsr)
    eel.EnableStartButton()
    #eel.Show("uploader")
