# AGENTS

This repository currently does not expose any OpenCode agents or skills.

## Overview
The project is a single‑package Python application that generates thumbnails, videos, titles and descriptions for the BSITA YouTube channel.  It consumes data from the ScoreSaber and BeatLeader APIs and uses FFmpeg (installed via `StartLinux.sh` / `StartWindows.bat`) to render video.

### Current entry points
| Path | Description |
|------|-------------|
| `main.py` | Main application executable. Runs the GUI web server and handles all user interactions.
| `video_editor.py` | Core logic for building videos, thumbnails and metadata.
| `StartLinux.sh` | Convenience script to install dependencies on Linux, create a virtual environment, and launch the app.
| `StartWindows.bat` | Same as above but for Windows.

## Future plans
We may expose agents that automate individual steps of the workflow (e.g. "generate thumbnail", "download beatmap", "upload video").  Those agents would be added to this file once implemented.

---
If you have ideas or want to contribute an agent, feel free to open a pull request or issue.