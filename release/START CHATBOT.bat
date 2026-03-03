@echo off
title AI Chatbot — Starting...
color 0A
setlocal EnableDelayedExpansion

echo.
echo  ╔══════════════════════════════════════════════════════╗
echo  ║              AI Chatbot — Launcher                   ║
echo  ║         Powered by Offline AI Engine                 ║
echo  ╚══════════════════════════════════════════════════════╝
echo.

REM ── Get the folder this bat file lives in ─────────────────────────────────
set "BAT_DIR=%~dp0"

REM ── Ensure we are NOT running from inside a ZIP ───────────────────────────
echo  Checking environment...

REM ── Check chatbot-server.exe exists ──────────────────────────────────────
if not exist "%BAT_DIR%chatbot-server.exe" (
    echo.
    echo  ╔══════════════════════════════════════════════════════╗
    echo  ║  ERROR: chatbot-server.exe was not found!            ║
    echo  ║                                                      ║
    echo  ║  You are probably running from INSIDE THE ZIP.       ║
    echo  ║                                                      ║
    echo  ║  HOW TO FIX:                                         ║
    echo  ║  1. Close this window                                ║
    echo  ║  2. Right-click the ZIP file                         ║
    echo  ║  3. Click "Extract All..."                           ║
    echo  ║  4. Choose a folder and click Extract                ║
    echo  ║  5. Open the extracted folder                        ║
    echo  ║  6. Double-click START CHATBOT.bat again             ║
    echo  ╚══════════════════════════════════════════════════════╝
    echo.
    pause
    exit /b 1
)

REM ── Check _internal folder exists ─────────────────────────────────────────
if not exist "%BAT_DIR%_internal" (
    echo.
    echo  ╔══════════════════════════════════════════════════════╗
    echo  ║  ERROR: _internal folder missing!                    ║
    echo  ║                                                      ║
    echo  ║  The _internal folder is required.                   ║
    echo  ║  It must be in the SAME folder as chatbot-server.exe ║
    echo  ║                                                      ║
    echo  ║  HOW TO FIX:                                         ║
    echo  ║  Make sure you extracted ALL files from the ZIP,     ║
    echo  ║  not just some of them.                              ║
    echo  ╚══════════════════════════════════════════════════════╝
    echo.
    pause
    exit /b 1
)

REM ── Ensure data folder exists ─────────────────────────────────────────────
if not exist "%BAT_DIR%data" mkdir "%BAT_DIR%data"

REM ── Kill any leftover old server instance (clean restart) ─────────────────
taskkill /F /IM chatbot-server.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM ── Start the chatbot backend server ─────────────────────────────────────
echo  [1/3] Starting AI backend server...
echo.
echo  NOTE: If a blue "Windows protected your PC" screen appears,
echo        click "More info" and then "Run anyway" — it is safe.
echo.
start "" "%BAT_DIR%chatbot-server.exe"

REM ── Give it time to unpack and initialize ─────────────────────────────────
echo  [2/3] Waiting for server to initialize...
echo        (This may take 10-30 seconds on first run)
timeout /t 6 /nobreak >nul

REM ── Wait for port 8000 (up to 90 seconds total) ───────────────────────────
set /a tries=0
:waitloop
set /a tries+=1

if %tries% gtr 84 (
    echo.
    echo  ─────────────────────────────────────────────
    echo  WARNING: Server is taking longer than expected.
    echo  Opening browser anyway — it may not work yet.
    echo  If chat shows an error, wait 30 more seconds
    echo  then click the "Retry Now" button in the chat.
    echo  ─────────────────────────────────────────────
    goto open_browser
)

REM Show progress dots every 10 tries
set /a "mod=%tries% %% 10"
if %mod% equ 0 (
    set /a secs=%tries%+6
    echo  Still waiting... (!secs! seconds elapsed)
)

netstat -an 2>nul | find "127.0.0.1:8000" >nul 2>&1
if %errorlevel% equ 0 goto open_browser
netstat -an 2>nul | find "0.0.0.0:8000" >nul 2>&1
if %errorlevel% equ 0 goto open_browser

timeout /t 1 /nobreak >nul
goto waitloop

:open_browser
echo.
echo  [3/3] Server is ready! Opening chat in your browser...
echo.
start "" "%BAT_DIR%frontend\index.html"

echo  ╔══════════════════════════════════════════════════════╗
echo  ║   ✓  Chatbot is RUNNING!                             ║
echo  ║                                                      ║
echo  ║   ⚠  IMPORTANT: Keep THIS window open!               ║
echo  ║      Closing it will stop the chatbot.               ║
echo  ║                                                      ║
echo  ║   To stop: just close this black window.             ║
echo  ╚══════════════════════════════════════════════════════╝
echo.
echo  Server log output (do not close this window):
echo  ──────────────────────────────────────────────

REM Keep window alive while server runs
:keepalive
timeout /t 5 /nobreak >nul
tasklist /FI "IMAGENAME eq chatbot-server.exe" 2>nul | find /i "chatbot-server.exe" >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  ╔══════════════════════════════════════════════════════╗
    echo  ║  The server stopped unexpectedly!                    ║
    echo  ║                                                      ║
    echo  ║  This is usually caused by:                          ║
    echo  ║  - Antivirus blocking chatbot-server.exe             ║
    echo  ║                                                      ║
    echo  ║  HOW TO FIX:                                         ║
    echo  ║  1. Run: FIX - Allow in Antivirus.bat                ║
    echo  ║  2. Then run START CHATBOT.bat again                  ║
    echo  ║                                                      ║
    echo  ║  OR run: DIAGNOSE (run if broken).bat                ║
    echo  ║  and send the report to your developer.              ║
    echo  ╚══════════════════════════════════════════════════════╝
    echo.
    pause
    exit /b 1
)
goto keepalive
