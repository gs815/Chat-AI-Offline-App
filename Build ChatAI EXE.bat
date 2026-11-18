@echo off
setlocal
cd /d "%~dp0"
python -m pip install --upgrade pyinstaller
if errorlevel 1 goto error
python -m PyInstaller --noconfirm --clean --windowed --onefile --icon "icon.ico" --add-data "icon.ico;." --name "ChatAI" ChatAI.pyw
if errorlevel 1 goto error
echo.
echo Application created at dist\ChatAI.exe
pause
exit /b 0
:error
echo.
echo Build failed. Check your Internet connection and Python installation.
pause
exit /b 1
