@echo off
setlocal
 title True Science Stories - Factory
 cd /d "%~dp0"
 if not exist "%~dp0launch.py" (
  echo ERROR: launch.py missing. Extract the entire ZIP before launching.
  goto finish
 )
 if not exist "%~dp0runtime\installed.json" (
  echo Setup is not complete. Starting setup...
  call "%~dp0SETUP_AND_START.bat"
  exit /b
 )
 if not exist "%~dp0runtime\venv\Scripts\python.exe" (
  echo Python environment missing. Starting setup...
  call "%~dp0SETUP_AND_START.bat"
  exit /b
 )
 "%~dp0runtime\venv\Scripts\python.exe" "%~dp0update.py" --auto
 if errorlevel 1 goto finish
 "%~dp0runtime\venv\Scripts\python.exe" "%~dp0launch.py"
 echo.
 echo Factory returned exit code: %errorlevel%
 :finish
 echo Press any key to close this window.
 pause >nul
 endlocal
