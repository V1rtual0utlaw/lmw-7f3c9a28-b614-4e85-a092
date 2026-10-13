@echo off
setlocal
 title True Science Stories - Setup
 echo True Science Stories - automatic setup
 echo This window will stay open if setup stops.
 echo.
 cd /d "%~dp0"
 if not exist "%~dp0SETUP.ps1" (
  echo ERROR: SETUP.ps1 is missing beside this launcher.
  echo Extract ALL files from the ZIP first. Do not run from inside the ZIP.
  goto finish
 )
 if not exist "%~dp0factory.py" (
  echo ERROR: Factory files are missing. Extract the entire ZIP first.
  goto finish
 )
 if not exist "%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" (
  echo ERROR: Windows PowerShell was not found on this computer.
  goto finish
 )
 echo Folder: %~dp0
 echo Starting Windows PowerShell...
 "%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0BOOTSTRAP.ps1"
 echo.
 echo Installer returned exit code: %errorlevel%
 :finish
 echo.
 echo If setup stopped, copy the error above or send logs\bootstrap.log.
 echo Press any key to close this window.
 pause >nul
 endlocal
