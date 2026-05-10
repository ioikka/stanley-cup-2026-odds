@echo off
cd /d "%~dp0"
echo ================================
echo   Stanley Cup Odds Updater
echo   %DATE% %TIME%
echo ================================
echo.
python parse-odds.py
echo.
echo Done.
pause
