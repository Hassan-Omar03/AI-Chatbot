@echo off
setlocal enabledelayedexpansion
title AI Chatbot - Demo Server Launcher
color 0A

set "NGROK_EXE=C:\Users\hp\AppData\Local\Microsoft\WinGet\Links\ngrok.exe"
set "BAT_DIR=%~dp0"
set "RELEASE_DIR=%BAT_DIR%release\"
set "DEMO_FILE=%BAT_DIR%DEMO - AI Chatbot.html"

echo.
echo ============================================================
echo   AI Chatbot - Demo Server Setup
echo   Starts backend + gets public URL for client demo
echo ============================================================
echo.

if not exist "%RELEASE_DIR%chatbot-server.exe" (
    echo [ERROR] chatbot-server.exe not found in release folder!
    pause
    exit /b 1
)

echo [1/4] Stopping any old servers...
taskkill /F /IM chatbot-server.exe >nul 2>&1
taskkill /F /IM ngrok.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo [2/4] Starting chatbot backend...
start /B "" "%RELEASE_DIR%chatbot-server.exe"

echo [3/4] Waiting for backend on port 8000...
set /a tries=0
:waitloop
set /a tries+=1
if %tries% gtr 40 (
    echo [WARN] Backend slow to start, continuing anyway...
    goto start_ngrok
)
netstat -an 2>nul | find ":8000" >nul 2>&1
if %errorlevel% equ 0 (
    echo Backend is UP on port 8000!
    goto start_ngrok
)
timeout /t 1 /nobreak >nul
goto waitloop

:start_ngrok
echo.
echo [4/4] Starting ngrok tunnel...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath '%NGROK_EXE%' -ArgumentList 'http 8000' -WindowStyle Minimized"

echo Waiting for ngrok to connect...
timeout /t 12 /nobreak >nul

echo Getting your public URL...
for /f "delims=" %%U in ('powershell -NoProfile -ExecutionPolicy Bypass -Command "try{$r=(Invoke-WebRequest 'http://localhost:4040/api/tunnels' -UseBasicParsing).Content|ConvertFrom-Json;($r.tunnels|Where-Object{$_.proto-eq 'https'}).public_url}catch{''}"') do set "NGROK_URL=%%U"

if "!NGROK_URL!"=="" (
    echo.
    echo ============================================================
    echo  Could not auto-detect ngrok URL.
    echo  Look at the ngrok window that opened (minimized in taskbar)
    echo  Copy the Forwarding https URL from there.
    echo  Then open DEMO - AI Chatbot.html in Notepad,
    echo  find REPLACE_WITH_YOUR_SERVER_URL and paste your URL.
    echo ============================================================
    pause
    goto end
)

echo.
echo ============================================================
echo  SUCCESS! Your public URL is:
echo.
echo  !NGROK_URL!
echo.
echo ============================================================
echo.

REM Reset old URL back to placeholder if needed
powershell -NoProfile -ExecutionPolicy Bypass -Command "$f='%DEMO_FILE%';$c=[System.IO.File]::ReadAllText($f);if($c -notmatch 'REPLACE_WITH_YOUR_SERVER_URL'){$c=$c -replace 'https://[a-zA-Z0-9-]+\.ngrok[a-zA-Z0-9.-]*','REPLACE_WITH_YOUR_SERVER_URL';[System.IO.File]::WriteAllText($f,$c)}" >nul 2>&1

REM Patch demo HTML with the live ngrok URL
powershell -NoProfile -ExecutionPolicy Bypass -Command "$f='%DEMO_FILE%';$c=[System.IO.File]::ReadAllText($f);$c=$c -replace 'REPLACE_WITH_YOUR_SERVER_URL','!NGROK_URL!';[System.IO.File]::WriteAllText($f,$c)"

if %errorlevel% equ 0 (
    echo [OK] DEMO - AI Chatbot.html updated with your ngrok URL!
    echo      Send this file to your client now.
) else (
    echo [WARN] Could not update file automatically. Edit manually.
)

echo.
echo Opening demo in your browser to verify...
timeout /t 2 /nobreak >nul
start "" "%DEMO_FILE%"

echo.
echo ============================================================
echo  SEND THIS FILE TO CLIENT:  DEMO - AI Chatbot.html
echo.
echo  KEEP THIS WINDOW + NGROK WINDOW OPEN!
echo  Closing them = client loses access to the bot.
echo.
echo  After payment: send them AI-Chatbot-Client.zip
echo ============================================================
echo.
echo Press any key to exit (servers keep running in background)
pause >nul

:end
