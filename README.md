# BSITA EDITOR
Generates thumbnail and video w/intro for BSITA YT channel by getting information from the ScoreSaber and BeatLeader API

## Auto setup [Linux Only]
**This is an experimental method for setting up the software. From my testing, it works, tell me if I'm wrong**
* Run ```StartLinux.sh```

## Manual installation [Linux & Windows]
1. Install Python
2. Create a venv in the repo's root directory and activate it it
   ```
   python -m venv .venv
   source .venv/bin/activate
   ```
   * On Windows, you activate the venv with this command
     ```
     .venv\bin\activate
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
### Auto Start [Linux Only]
* Run ```StartLinux.sh```

### Manual usage [Linux & Windows]
1. Make sure you are running the venv created during setup, run this in the root folder
  ```
   source .venv/bin/activate
   ```
   * On Windows, you activate the venv with this command
     ```
     .venv\bin\activate
     ```
  - You should be automatically redirected to the WebUI, otherwise, open http://localhost:8000/index.html
2. Fill out the web form with the required information, then click Start Program
  - **ScoreSaber/BeatLeader:** select the leaderboard
  - **Profile ID:** the ID after ../u/ on ScoreSaber or BeatLeader. Paste the ID, not the whole link. Works with numerical IDs and vanity URLs
  - **Leaderboard ID:** the ID after ../difficulty/ on ScoreSaber or the ID after ../global/ on BeatLeader. Paste the ID, not the whole link. If ../difficulty/ID isn't visible, try changing difficulty on ScoreSaber then switching back. On BeatLeader don't copy the number after the leaderboard ID
  - **Score & Notes:** accuracy in percentage and some extra information (pp, CS level, important feat...)
  - **Google Drive link:** Google Drive link to the video. Must be shared as "Anyone with the link" and should point to the video file directly, not a folder
3. Google Drive download progress will be visible from the terminal you used to run ```main.py```
4. Some information regarding the data obtained from ScoreSaber will be logged in the WebUI
5. Wait for FFmpeg to finish encoding the video, progress is shown in the terminal window
6. Once the encoding finished, you'll be able to preview and download the video from the WebUI, or grab it from ```/Gui/Videos```
   * The thumbnail will be saved in ```/Gui/Thumbnails```
   * The generated title and description can be copied from the latest file in ```/transcripts```

## Usage example
* Using me (Ryleeeee) as an example
1. Player's ScoreSaber profile is https://scoresaber.com/u/ryleeeee
   * Copy ```ryleeeee``` and paste it in **Profile ID**
2. Map leaderboard is https://scoresaber.com/map/66837/difficulty/497707
   * Copy ```497707``` and paste it in **Leaderboard ID**
3. Acc is 49.83%
   * Paste the acc in **Score & Notes**
     * Use this field for any other extra information, for example FC, FS, #1 ITA, Second Pass ITA, CS Level 100, 727pp SS...
4. Map is Level 29 on Challenge Saber
   * Add "Level 29 CS" after the acc. The field for this example will look like "49.83% Level 29 CS First Pass ITA"
5. Video is hosted on Google Drive: https://drive.google.com/file/d/143kDU7AYHvt8WPHr0l334cw1fnKBlxha/view?usp=drive_link
   * Verify that the link points directly to the video, then paste it in **Google Drive link**
6. Press **Start Program**
   * Check the terminal window for download progress from Google Drive
   * The WebUI will log all the data gathered from the ScoreSaber leaderboard and player
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
7. Once encoding is finished, the video can be found at ```/Gui/Videos/WDG_Ryleeeee_284b0.mp4```
   * The program will log the generated description, which can be also copied from ```/transcripts```
     ```
     Description:

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
* Dependencies are reported as missing when starting ```main.py```
  * Make sure you're using the venv you've setup during the installation
     ```
    source .venv/bin/activate
     ```
     * On Windows, you activate the venv with this command
     ```
     .venv\bin\activate
     ```
    - If you've never created the venv in the first place, follow the installation guide above
  * Install the dependencies that are reported as missing by using ```pip```
    * Assuming you are currently running in the venv

* Errors regarding deprecated or not found functions in some pip libraries
  * Make sure you are running the latest version of all librarires

* FFmpeg not found
  * Make sure you've installed FFmpeg as instructed above. If it's already installed, make sure FFmpeg is in PATH
    
## Known issues
* Currently only generates generic thumbnails with no custom colors. Support for custom colors will be added

## Upcoming features
* Custom colors in thumbnails for all players
* Hardware encoding for FFmpeg for faster renders
* Better GUI
* Thumbnail preview
* Optional input field for custom player name
* Show generated title and description cleanly in the WebUI
* Better README
* Auto start script for Windows

**Only tested on EndeavourOS Linux. It should work on all OSes, tell me if I'm wrong because idk**

For any issues regarding this software, contact Ryleeeee or Ivy
