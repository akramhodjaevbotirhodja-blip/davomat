@echo off
chcp 65001 >nul
title Davomat tizimi
cd /d "%~dp0"
echo.
echo   Davomat tizimi ishga tushmoqda...
echo   Bu oynani YOPMANG - server shu yerda ishlaydi.
echo.
python run.py
pause
