@echo off
title AI Chatbot — Fix Antivirus Block
color 0E
setlocal

set "BAT_DIR=%~dp0"

echo.
echo  ╔══════════════════════════════════════════════════════╗
echo  ║          AI Chatbot — Antivirus Fix Tool             ║
echo  ║   This adds the chatbot folder to Windows Defender   ║
echo  ║   exclusions so it stops being blocked.              ║
echo  ╚══════════════════════════════════════════════════════╝
echo.
echo  Folder to allow: %BAT_DIR%
echo.

REM Check if running as admin
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo  ─────────────────────────────────────────────────
    echo  This tool needs ADMINISTRATOR rights to work.
    echo.
    echo  HOW TO RUN AS ADMIN:
    echo  1. Close this window
    echo  2. Right-click "FIX - Allow in Antivirus.bat"
    echo  3. Click "Run as administrator"
    echo  4. Click Yes on the popup
    echo  ─────────────────────────────────────────────────
    echo.
    pause
    exit /b 1
)

echo  Adding exclusion to Windows Defender...
powershell -Command "Add-MpPreference -ExclusionPath '%BAT_DIR%'" 2>nul
if %errorlevel% equ 0 (
    echo.
    echo  ╔══════════════════════════════════════════════════════╗
    echo  ║   ✓  SUCCESS! Folder added to Defender exclusions.   ║
    echo  ║                                                      ║
    echo  ║   Now run: START CHATBOT.bat                         ║
    echo  ╚══════════════════════════════════════════════════════╝
) else (
    echo.
    echo  ╔══════════════════════════════════════════════════════╗
    echo  ║   Windows Defender exclusion may have failed.        ║
    echo  ║                                                      ║
    echo  ║   MANUAL FIX:                                        ║
    echo  ║   1. Search "Windows Security" in Start              ║
    echo  ║   2. Go to: Virus protection → Manage settings       ║
    echo  ║   3. Scroll down to "Exclusions" → Add exclusion     ║
    echo  ║   4. Select "Folder" and pick this chatbot folder    ║
    echo  ╚══════════════════════════════════════════════════════╝
)

echo.
echo  Also checking if chatbot-server.exe was quarantined...
REM Try to restore from quarantine if it was deleted by antivirus
if not exist "%BAT_DIR%chatbot-server.exe" (
    echo.
    echo  WARNING: chatbot-server.exe is missing!
    echo  It was likely removed by your antivirus.
    echo.
    echo  To restore it:
    echo  1. Open Windows Security
    echo  2. Go to "Virus ^& threat protection"
    echo  3. Click "Protection history"
    echo  4. Find chatbot-server.exe and click "Restore"
    echo.
)

echo.
pause
