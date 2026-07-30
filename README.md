# BSITA EDITOR
Generates thumbnail and video w/intro for BSITA YT channel by getting information from the ScoreSaber API

## Installation
1. Install Python
2. Create a venv in the repo's root directory and activate it it
   ```
   python -m venv .venv
   source .venv/bin/activate
   ```
3. Upgrade pip to the latest version
   ```
   pip install --upgrade pip
   ```
4. Install all the required dependencies
   ```
   pip install --upgrade pillow eel moviepy gdown
   ```
5. Install FFmpeg for your OS: https://www.ffmpeg.org/download.html
   * Windows:
     1. Download and extract ffmpeg > drop it in the C drive
     2. Click start, search "**Environment Variable**", click "**Edit the System Environment Variables**"
     3. Advanced tab > click Environment Variables
     4. Look for "**PATH**" in the top box > click and Edit > New
     5. Enter or copy paste the file path to the ffmpeg folder which should be ```C:\ffmpeg\bin``` if you put it in the C drive.
     6. Open cmd and just enter ```ffmpeg -version``` to see if it's working. Should list the version and all that stuff.

   * Linux:
     * Arch Linux:
       ```
       sudo pacman -S ffmpeg
       ```
     * Ubuntu:
       ```
       sudo apt install ffmpeg
       ```
     * Fedora:
       * Allow free and nonfree repositories by enabling RPMFusion: https://rpmfusion.org/Configuration#Installing_Free_and_Nonfree_Repositories
       ```
       sudo dnf install ffmpeg --allowerasing
       ```

7. Start ```main.py```
   ```
   python main.py
   ```

## Usage
1. Make sure you are running the venv created during setup, run this in the root folder
  ```
   source .venv/bin/activate
   ```
  - You should be automatically redirected to the WebUI, otherwise, open http://localhost:8000/index.html
2. Fill out the web form with the required information, then click Start Program
  - **ScoreSaber/BeatLeader:** the ID after ../u/ on ScoreSaber. Paste the ID, not the whole link. **ScoreSaber only for now**, works with numerical IDs and vanity URLs
  - **Leaderboard ID:** the ID after ../difficulty/ on ScoreSaber. Paste the ID, not the whole link. **ScoreSaber only for now**, if ../difficulty/ID isn't visible, try changing difficulty on ScoreSaber then switching back
  - **Score & Notes:** accuracy in percentage and some extra information (pp, CS level, important feat...)
  - **Google Drive link:** Google Drive link to the video. Must be shared as "Anyone with the link" and should point to the video file directly, not a folder
3. Google Drive download progress will be visible from the terminal you used to run ```main.py```
4. Some information regarding the data obtained from ScoreSaber will be logged in the WebUI
5. Wait for FFmpeg to finish encoding the video, progress is shown in the terminal window
6. Once the encoding finished, you'll be able to preview and download the video from the WebUI. The thumbnail will be saved in ```/Gui/Thumbnails```

## Troubleshooting
* Dependencies are reported as missing when starting ```main.py```
  * Make sure you're using the venv you've setup during the installation
     ```
    source .venv/bin/activate
     ```
    - If you've never created the venv in the first place, follow the installation guide above
  * Install the dependencies that are reported as missing by using ```pip```
    * Assuming you are currently running in the venv

* Errors regarding deprecated or not found functions in some pip libraries
  * Make sure you are running the latest version of all librarires

* FFmpeg not found
  * Make sure you've installed FFmpeg as instructed above. If it's already installed, make sure FFmpeg is in PATH
    
## Known issues
* Only works with ScoreSaber. BeatLeader support will be added
* Currently only generates generic thumbnails with no custom colors. Support for custom colors will be added

## Upcoming features
* BeatLeader support
* Custom colors in thumbnails for all players
* Hardware encoding for FFmpeg for faster renders
* Better GUI
* Thumbnail preview
* Optional input field for custom player name
* Better README

**Only tested on EndeavourOS Linux. It should work on all OSes, tell me if I'm wrong because idk**

For any issues regarding this software, contact Ryleeeee or Ivy
