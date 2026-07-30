import subprocess
import eel

eel.init('Gui')

def get_video_info(file):
    cmd = f'ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate -of default=noprint_wrappers=1:nokey=1 "{file}"'
    info = subprocess.check_output(cmd, shell=True).decode("utf-8").strip().split("\n")
    width, height, framerate = int(info[0]), int(info[1]), eval(info[2])
    return {"width": width, "height": height, "fps": framerate}

def main(submission_file, player, bsr):
    final_video_name = f"Gui/Videos/{player}_{bsr}.mp4"

    # Get video information
    intro_info = get_video_info("intro.mp4")
    submission_info = get_video_info(submission_file)

    # Determine the highest resolution and framerate
    max_width = max(intro_info["width"], submission_info["width"])
    max_height = max(intro_info["height"], submission_info["height"])
    max_fps = max(intro_info["fps"], submission_info["fps"])

    # Prepare the FFmpeg command with the updated resolution and framerate
    cmd = f'ffmpeg -i "intro.mp4" -i "{submission_file}" -filter_complex "[0:v:0]scale={max_width}:{max_height}:force_original_aspect_ratio=decrease,pad={max_width}:{max_height}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={max_fps}[v0];[0:a:0]asetrate=48000[a0];[1:v:0]scale={max_width}:{max_height}:force_original_aspect_ratio=decrease,pad={max_width}:{max_height}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={max_fps}[v1];[1:a:0]asetrate=48000[a1];[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]" -map "[v]" -map "[a]" -c:v libx264 -crf 23 -c:a aac "{final_video_name}"'
    subprocess.run(cmd, shell=True)

    eel.Show("editor")
    eel.Videos(final_video_name, "editor", player, bsr)
    eel.EnableStartButton()
    #eel.Show("uploader")