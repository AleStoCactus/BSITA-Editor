@echo off
setlocal
cd /d "%~dp0"

echo === BSITA EDITOR Launcher ===

rem ----------------------------------------------------------------------------
rem 1. Dependency checks (Python and FFmpeg), installed with winget when missing
rem ----------------------------------------------------------------------------
set "PYTHON="
where py >nul 2>nul && set "PYTHON=py -3"
if not defined PYTHON (
    where python >nul 2>nul && python --version >nul 2>nul && set "PYTHON=python"
)
if not defined PYTHON (
    echo --^> Python not found, installing it with winget...
    winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
    if errorlevel 1 goto :python_error
    echo --^> Python installed. Close this window and run StartWindows.bat again to reload PATH.
    goto :end
)

where ffmpeg >nul 2>nul
if errorlevel 1 (
    echo --^> FFmpeg not found, installing it with winget...
    winget install -e --id Gyan.FFmpeg --accept-package-agreements --accept-source-agreements
    if errorlevel 1 goto :ffmpeg_error
    echo --^> FFmpeg installed. Close this window and run StartWindows.bat again to reload PATH.
    goto :end
)

rem ----------------------------------------------------------------------------
rem 2. Virtual environment setup
rem ----------------------------------------------------------------------------
if not exist ".venv\Scripts\activate.bat" (
    echo --^> Creating virtual environment ^(.venv^)...
    %PYTHON% -m venv .venv
    if errorlevel 1 goto :venv_error
) else (
    echo --^> Virtual environment ^(.venv^) already exists.
)

echo --^> Activating virtual environment...
call .venv\Scripts\activate.bat

rem ----------------------------------------------------------------------------
rem 3. Pip dependencies
rem ----------------------------------------------------------------------------
echo --^> Checking/upgrading Python dependencies...
python -m pip install --upgrade pip --quiet
python -m pip install --upgrade pillow eel moviepy gdown requests numpy --quiet

rem ----------------------------------------------------------------------------
rem 4. Launch
rem ----------------------------------------------------------------------------
echo --^> Starting BSITA EDITOR...
echo ======================================
python main.py
goto :end

:python_error
echo Error: could not install Python. Install it from https://www.python.org/downloads/ and check "Add python.exe to PATH".
goto :end

:ffmpeg_error
echo Error: could not install FFmpeg. Install it manually as explained in the README.
goto :end

:venv_error
echo Error: could not create the virtual environment.
goto :end

:end
echo.
echo Program finished. Press any key to close...
pause >nul
