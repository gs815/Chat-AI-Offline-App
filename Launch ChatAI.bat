@echo off
setlocal
cd /d "%~dp0"
where pyw >nul 2>nul
if %errorlevel%==0 (
    start "" pyw "%~dp0ChatAI.pyw"
    exit /b 0
)
where pythonw >nul 2>nul
if %errorlevel%==0 (
    start "" pythonw "%~dp0ChatAI.pyw"
    exit /b 0
)
echo Python is not installed or is not available in PATH.
echo Install Python 3 for Windows and run this file again.
pause
