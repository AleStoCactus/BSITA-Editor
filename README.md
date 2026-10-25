# BSITA EDITOR
Generates the thumbnail, the video with the intro, the title and the description for the BSITA YT channel, getting the information from the ScoreSaber and BeatLeader APIs.

## Features
* Video with the BSITA intro, encoded in **H.264**, **HEVC** or **AV1**, on the GPU when possible
* Thumbnail with the map cover, a blurred frame of the video, the player's name and the player's colored border
* **Border color picker**: every border is split in two halves (left and right), pick their colors and save them as the player's border
* Thumbnail and video preview in the WebUI
* Title and description ready to copy from the WebUI
* Optional custom player name
* Auto start scripts for Linux and Windows

## Quick start
### Linux
* Run `StartLinux.sh`. It installs Python and FFmpeg if they are missing, creates the venv, installs the dependencies and starts the program

### Windows
* Run `StartWindows.bat`. It installs Python and FFmpeg with `winget` if they are missing, creates the venv, installs the dependencies and starts the program
  * If Python or FFmpeg were just installed, close the window and run `StartWindows.bat` again so the new `PATH` is loaded

The WebUI opens automatically, otherwise open http://localhost:8000/index.html

## Manual installation
1. Install Python 3.10 or newer
2. Create a venv in the repo's root directory and activate it
   ```
   python -m venv .venv
   ```
   * Linux:
     ```
     source .venv/bin/activate
     ```
   * Windows:
     ```
     .venv\Scripts\activate
     ```
3. Upgrade pip and install the dependencies
   ```
   pip install --upgrade pip
   pip install --upgrade pillow eel moviepy gdown requests numpy
   ```
4. Install FFmpeg for your OS: https://www.ffmpeg.org/download.html
   * Windows:
     * With winget: `winget install Gyan.FFmpeg`
     * Manually:
       1. Download and extract FFmpeg, then move it to the C drive
       2. Click start, search "**Environment Variable**", click "**Edit the System Environment Variables**"
       3. Advanced tab > click Environment Variables
       4. Look for "**PATH**" in the top box > click and Edit > New
       5. Enter the path to the FFmpeg bin folder, `C:\ffmpeg\bin` if you put it in the C drive
     * Open cmd and run `ffmpeg -version` to check that it works
   * Linux:
     * Arch Linux: `sudo pacman -S ffmpeg`
     * Ubuntu: `sudo apt install ffmpeg`
     * Fedora: enable [RPMFusion](https://rpmfusion.org/Configuration#Installing_Free_and_Nonfree_Repositories), then `sudo dnf install ffmpeg --allowerasing`
5. Start `main.py` from the venv
   ```
   python main.py
   ```

## Usage
1. Fill out the **Play Info** form
   * **Leaderboard:** ScoreSaber or BeatLeader
   * **Profile ID:** the ID after `../u/` on ScoreSaber or BeatLeader. Paste the ID, not the whole link. Works with numerical IDs and vanity URLs
   * **Player name (optional):** replaces the name from the leaderboard in the thumbnail, the title, the file names and the border
   * **Leaderboard ID:** the ID after `../difficulty/` on ScoreSaber or the ID after `../global/` on BeatLeader. Paste the ID, not the whole link. If `../difficulty/ID` isn't visible, try changing difficulty on ScoreSaber then switching back. On BeatLeader don't copy the number after the leaderboard ID
   * **Score & Notes:** accuracy in percentage and some extra information (pp, CS level, important feat...), added to the title
   * **Description notes:** extra notes added at the start of the description
   * **Google Drive link:** link to the video. Must be shared as "Anyone with the link" and should point to the video file directly, not a folder
2. Choose the **Codec** and the **Encoder**, see [Codecs and encoders](#codecs-and-encoders)
3. Check the **Thumbnail Border**, see [Border colors](#border-colors)
4. Click **Start Program**
   * The data from the leaderboard and the progress are shown in the **Log**
   * The Google Drive download and FFmpeg progress are shown in the terminal
5. When it's done:
   * The **title and description** are shown in the WebUI with a **Copy** button, and saved in `/transcripts`
   * The **thumbnail** is shown in the WebUI and saved in `/Gui/Thumbnails`
   * The **video** can be previewed and downloaded from the WebUI, and is saved in `/Gui/Videos`

## Border colors
Every border in `/borders` is split in two halves, the left one and the right one, each with a single color. The border of a player is saved as `/borders/<player name in lowercase>.png`.

* When you enter the **Profile ID** (or the **Player name**), the colors of the player's border are loaded in the two color pickers, together with a preview
* If the player has no border yet, the colors of `default.png` are loaded and **Save these colors as the player's border** is checked, so a border is created for them
* Changing a color checks **Save these colors as the player's border** automatically. When it's checked, `default.png` is recolored with the chosen colors and saved as the player's border, replacing the old one
* When it's not checked, the player's saved border is used, or `default.png` if there is none

## Codecs and encoders
| Codec | Notes |
| --- | --- |
| **H.264** | Plays everywhere, the safe choice |
| **HEVC (H.265)** | Smaller files at the same quality |
| **AV1** | Smallest files at the same quality, slower on the CPU. Hardware encoding needs a recent GPU (NVIDIA RTX 40, Intel Arc, AMD RX 7000 or newer) |

When the WebUI opens, every encoder supported by your FFmpeg build is tested with a short encode, and only the codecs and encoders that work are listed:
* **NVIDIA NVENC** (`*_nvenc`): NVIDIA GPUs with the proprietary driver
* **Intel Quick Sync** (`*_qsv`): Intel GPUs
* **AMD AMF** (`*_amf`): AMD GPUs on Windows
* **VAAPI** (`*_vaapi`): AMD and Intel GPUs on Linux. Requires the VA-API driver (`mesa-va-drivers` for AMD, `intel-media-driver` for Intel)
* **Apple VideoToolbox** (`*_videotoolbox`): macOS, H.264 and HEVC only
* **CPU**: `libx264` for H.264, `libx265` for HEVC, `libsvtav1` (or `libaom-av1`) for AV1. Always available when your FFmpeg build includes them, slowest

**Auto** uses the first available encoder in the order above. If the hardware encoder fails during the render, the video is encoded again on the CPU with the same codec. The encoder in use is shown in the Log and in the terminal.

## Usage example
* Using me (Ryleeeee) as an example
1. Player's ScoreSaber profile is https://scoresaber.com/u/ryleeeee
   * Copy `ryleeeee` and paste it in **Profile ID**
2. Map leaderboard is https://scoresaber.com/map/66837/difficulty/497707
   * Copy `497707` and paste it in **Leaderboard ID**
3. Acc is 49.83% and the map is Level 29 on Challenge Saber
   * Write `49.83% Level 29 CS First Pass ITA` in **Score & Notes**
4. Video is hosted on Google Drive: https://drive.google.com/file/d/143kDU7AYHvt8WPHr0l334cw1fnKBlxha/view?usp=drive_link
   * Verify that the link points directly to the video, then paste it in **Google Drive link**
5. Press **Start Program**
   * The Log shows the data gathered from ScoreSaber
   ```
   Player: WDG_Ryleeeee
   Song name: I Will Fuck You Up Loli (Kawaii Ripper Remix)
   BSR: 284b0
   SS map ID: 66837
   Song artist: Loffciamcore
   Mapper: honk
   downloading video...
   download complete
   ```
6. Once encoding is finished, the video can be found at `/Gui/Videos/WDG_Ryleeeee_284b0.mp4`
   * The description is shown in the WebUI and saved in `/transcripts/WDG_Ryleeeee_284b0_transcript.txt`
     ```
     Player: https://scoresaber.com/u/ryleeeee
     Mappa: https://beatsaver.com/maps/284b0
     Mapper: honk
     Leaderboard: https://scoresaber.com/map/66837/difficulty/497707

     Join our Discord: https://discord.gg/m6NPkrhVFy

     Thumbnail design by @.benna_:
     https://www.instagram.com/draws_by_benna/
     Intro Animation by @pizzi7341:
     https://www.youtube.com/channel/UCc6spI8nRIAhM5-GB95GQpQ
     ```

## Troubleshooting
* Dependencies are reported as missing when starting `main.py`
  * Make sure you're using the venv created during the installation (`source .venv/bin/activate` on Linux, `.venv\Scripts\activate` on Windows)
  * If you've never created the venv, follow the installation guide above
  * Install the missing dependencies with `pip` from the venv
* Errors regarding deprecated or not found functions in some pip libraries
  * Make sure you are running the latest version of all libraries
* FFmpeg not found
  * Make sure you've installed FFmpeg as instructed above. If it's already installed, make sure FFmpeg is in `PATH`
* A codec or your GPU's encoder is not listed
  * Make sure your GPU drivers are installed and up to date
  * Check that your FFmpeg build includes the encoder, for example `ffmpeg -encoders | grep av1`
  * Hardware AV1 encoding needs a recent GPU, see [Codecs and encoders](#codecs-and-encoders)
* The video download fails
  * Make sure the Google Drive file is shared as "Anyone with the link"

**Only tested on EndeavourOS Linux. It should work on all OSes, tell me if I'm wrong because idk**

For any issues regarding this software, contact Ryleeeee or Ivy
