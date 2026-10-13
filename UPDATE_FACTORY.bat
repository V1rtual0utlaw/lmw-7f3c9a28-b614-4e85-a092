@echo off
setlocal
cd /d "%~dp0"
if not exist "runtime\venv\Scripts\python.exe" (
 echo Complete factory setup first.
 goto finish
)
if "%~1"=="" (
 "runtime\venv\Scripts\python.exe" update.py
) else (
 "runtime\venv\Scripts\python.exe" update.py "%~1"
)
:finish
pause
endlocal
