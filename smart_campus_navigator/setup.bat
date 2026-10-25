@echo off
setlocal
cd /d "%~dp0"
py -3 --version >nul 2>&1
if errorlevel 1 (
  echo Install Python 3.11 or newer from python.org, with the Python launcher.
  pause
  exit /b 1
)
py -3 -c "import sys; sys.exit(sys.version_info < (3,11))"
if errorlevel 1 (
  echo Python 3.11 or newer is required.
  pause
  exit /b 1
)
if not exist ".venv\Scripts\python.exe" py -3 -m venv .venv
if not exist ".venv\Scripts\python.exe" exit /b 1
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 (
  echo Installation failed. Check your internet connection and retry setup.bat.
  pause
  exit /b 1
)
echo Setup complete. Use run.bat to launch the application.
pause
