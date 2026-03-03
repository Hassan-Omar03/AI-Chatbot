@echo off
title AI Chatbot — Diagnostics
color 0B
setlocal EnableDelayedExpansion

set "BAT_DIR=%~dp0"
set "LOG=%BAT_DIR%DIAGNOSIS_REPORT.txt"

echo.
echo  ╔════════════════════════════════════════════════════╗
echo  ║         AI Chatbot — Diagnostics Tool              ║
echo  ║   Checking what's wrong. Saves a report file.     ║
echo  ╚════════════════════════════════════════════════════╝
echo.
echo  Running checks... please wait...
echo.

REM Write header to log
(
echo ================================================
echo  AI CHATBOT — DIAGNOSIS REPORT
echo  Generated: %DATE% %TIME%
echo ================================================
echo.
) > "%LOG%"

:: ── CHECK 1: Is this running from inside a ZIP? ──────────────────────────────
echo [CHECK 1] Checking if properly extracted from ZIP...
(echo [CHECK 1] Extraction Check:) >> "%LOG%"

REM If the path contains "AppData\Local\Temp" it's running from inside a ZIP
echo %BAT_DIR% | find /i "AppData\Local\Temp" >nul 2>&1
if %errorlevel% equ 0 (
    echo  [FAIL] Running from inside a ZIP or temp folder! ^<-- MAIN PROBLEM!
    echo   FAIL - Running from inside ZIP/temp. Path: %BAT_DIR% >> "%LOG%"
    echo   FIX: Right-click the ZIP, Extract All, then run from extracted folder >> "%LOG%"
    set "ALL_OK=0"
    set "IS_ZIP=1"
) else (
    echo  [OK] Not running from inside a ZIP
    echo   OK  - Not running from ZIP >> "%LOG%"
    set "IS_ZIP=0"
)
echo. >> "%LOG%"

:: ── CHECK 2: Files present ────────────────────────────────────────────────────
echo.
echo [CHECK 2] Checking required files...
(echo [CHECK 2] Required Files:) >> "%LOG%"

set "ALL_OK=1"

if exist "%BAT_DIR%chatbot-server.exe" (
    echo  [OK] chatbot-server.exe found
    echo   OK  - chatbot-server.exe >> "%LOG%"
) else (
    echo  [FAIL] chatbot-server.exe NOT FOUND ^<-- PROBLEM!
    echo   FAIL - chatbot-server.exe NOT FOUND >> "%LOG%"
    echo   Likely cause: Antivirus deleted or quarantined it >> "%LOG%"
    echo   FIX: Run 'FIX - Allow in Antivirus.bat' as Administrator, then restore from quarantine >> "%LOG%"
    set "ALL_OK=0"
)

if exist "%BAT_DIR%_internal" (
    echo  [OK] _internal folder found
    echo   OK  - _internal folder >> "%LOG%"
) else (
    echo  [FAIL] _internal folder NOT FOUND ^<-- PROBLEM!
    echo   FAIL - _internal folder NOT FOUND >> "%LOG%"
    echo   FIX: Re-extract the ZIP file completely >> "%LOG%"
    set "ALL_OK=0"
)

if exist "%BAT_DIR%frontend\index.html" (
    echo  [OK] frontend\index.html found
    echo   OK  - frontend\index.html >> "%LOG%"
) else (
    echo  [FAIL] frontend\index.html NOT FOUND ^<-- PROBLEM!
    echo   FAIL - frontend\index.html NOT FOUND >> "%LOG%"
    set "ALL_OK=0"
)

if exist "%BAT_DIR%.env" (
    echo  [OK] .env config file found
    echo   OK  - .env file >> "%LOG%"
) else (
    echo  [WARN] .env config file not found (will use defaults)
    echo   WARN - .env file not found >> "%LOG%"
)

if exist "%BAT_DIR%data\knowledge_base.json" (
    echo  [OK] data\knowledge_base.json found
    echo   OK  - knowledge_base.json >> "%LOG%"
) else (
    echo  [WARN] data\knowledge_base.json not found (will be created automatically)
    echo   WARN - knowledge_base.json not found (auto-created on start) >> "%LOG%"
)

echo. >> "%LOG%"

:: ── CHECK 3: Windows Version ──────────────────────────────────────────────────
echo.
echo [CHECK 3] Checking Windows version...
(echo [CHECK 3] Windows Version:) >> "%LOG%"
for /f "tokens=*" %%i in ('ver') do (
    echo  %%i
    echo   %%i >> "%LOG%"
)
echo. >> "%LOG%"

:: ── CHECK 4: Check if Python is installed (for info only — NOT required) ──────
echo.
echo [CHECK 4] Checking Python (for info only - NOT required)...
(echo [CHECK 4] Python Status (NOT required - exe is self-contained):) >> "%LOG%"
python --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('python --version 2^>^&1') do (
        echo  [INFO] Python found: %%i (not needed - exe is self-contained)
        echo   INFO - Python found: %%i (not needed) >> "%LOG%"
    )
) else (
    echo  [INFO] Python NOT installed - this is OK! The exe does not need Python.
    echo   INFO - Python not installed. This is FINE. The exe bundles Python inside it. >> "%LOG%"
)
echo. >> "%LOG%"

:: ── CHECK 5: Port 8000 ────────────────────────────────────────────────────────
echo.
echo [CHECK 5] Checking if port 8000 is already in use...
(echo [CHECK 5] Port 8000 Status:) >> "%LOG%"
netstat -an 2>nul | find "127.0.0.1:8000" >nul 2>&1
if %errorlevel% equ 0 (
    echo  [WARN] Port 8000 already in use - another server is running
    echo   WARN - Port 8000 occupied. Another instance may be running. >> "%LOG%"
    echo   FIX: Restart your computer and try again >> "%LOG%"
) else (
    netstat -an 2>nul | find "0.0.0.0:8000" >nul 2>&1
    if %errorlevel% equ 0 (
        echo  [WARN] Port 8000 in use (bound to all interfaces)
        echo   WARN - Port 8000 occupied (0.0.0.0:8000) >> "%LOG%"
    ) else (
        echo  [OK] Port 8000 is free
        echo   OK  - Port 8000 is free >> "%LOG%"
    )
)
echo. >> "%LOG%"

:: ── CHECK 6: Try to start the server (10 second test) ────────────────────────
echo.
echo [CHECK 6] Testing if chatbot-server.exe starts properly (10 sec test)...
(echo [CHECK 6] Server Start Test:) >> "%LOG%"

if exist "%BAT_DIR%chatbot-server.exe" (
    taskkill /F /IM chatbot-server.exe >nul 2>&1
    timeout /t 2 /nobreak >nul

    start /B "" "%BAT_DIR%chatbot-server.exe"
    echo  Waiting 10 seconds for server...
    timeout /t 10 /nobreak >nul

    netstat -an 2>nul | find "8000" >nul 2>&1
    if %errorlevel% equ 0 (
        echo  [OK] Server started successfully on port 8000!
        echo   OK  - Server started successfully on port 8000 >> "%LOG%"
    ) else (
        echo  [FAIL] Server did NOT start after 10 seconds ^<-- PROBLEM!
        echo   FAIL - Server did not bind to port 8000 after 10 seconds >> "%LOG%"
        echo   Most likely causes: >> "%LOG%"
        echo     1. Antivirus blocked or deleted chatbot-server.exe >> "%LOG%"
        echo        FIX: Right-click 'FIX - Allow in Antivirus.bat' as Administrator >> "%LOG%"
        echo     2. _internal folder missing >> "%LOG%"
        echo        FIX: Re-extract the ZIP file >> "%LOG%"
        echo     3. Files run from inside ZIP (not extracted) >> "%LOG%"
        echo        FIX: Right-click ZIP → Extract All → run from extracted folder >> "%LOG%"
        set "ALL_OK=0"
    )
    taskkill /F /IM chatbot-server.exe >nul 2>&1
) else (
    echo  [SKIP] chatbot-server.exe not found - skipping server test
    echo   SKIP - exe not found, cannot test >> "%LOG%"
)
echo. >> "%LOG%"

:: ── CHECK 7: Internet connectivity ────────────────────────────────────────────
echo.
echo [CHECK 7] Checking internet connection...
(echo [CHECK 7] Internet Connection:) >> "%LOG%"
ping -n 2 -w 3000 8.8.8.8 >nul 2>&1
if %errorlevel% equ 0 (
    echo  [OK] Internet connection working
    echo   OK  - Internet connected >> "%LOG%"
) else (
    echo  [WARN] No internet - AI will only use local knowledge base (limited answers)
    echo   WARN - No internet. AI responses will be limited to knowledge base only. >> "%LOG%"
)
echo. >> "%LOG%"

:: ── CHECK 8: Windows Defender status ──────────────────────────────────────────
echo.
echo [CHECK 8] Checking Windows Defender...
(echo [CHECK 8] Windows Defender:) >> "%LOG%"
powershell -Command "Get-MpComputerStatus | Select-Object -ExpandProperty RealTimeProtectionEnabled 2>$null" > "%TEMP%\av_check.txt" 2>nul
set /p AV_STATUS=< "%TEMP%\av_check.txt"
del "%TEMP%\av_check.txt" >nul 2>&1

if "!AV_STATUS!"=="True" (
    echo  [WARN] Windows Defender Real-Time Protection is ON
    echo         This may block chatbot-server.exe!
    echo   WARN - Windows Defender active. May block exe. >> "%LOG%"
    echo   FIX: Run 'FIX - Allow in Antivirus.bat' as Administrator >> "%LOG%"
) else (
    echo  [OK] Windows Defender not blocking (or is disabled)
    echo   OK  - Windows Defender not an issue >> "%LOG%"
)
echo. >> "%LOG%"

:: ── CHECK 9: Install location ──────────────────────────────────────────────────
(echo [CHECK 9] Install Location:) >> "%LOG%"
echo   Path: %BAT_DIR% >> "%LOG%"
echo. >> "%LOG%"

:: ── CHECK 10: Directory listing ────────────────────────────────────────────────
(echo [CHECK 10] Files in chatbot folder:) >> "%LOG%"
dir "%BAT_DIR%" /b >> "%LOG%" 2>nul
echo. >> "%LOG%"

:: ── SUMMARY ────────────────────────────────────────────────────────────────────
echo.
echo.
(echo ================================================) >> "%LOG%"
(echo  SUMMARY) >> "%LOG%"
(echo ================================================) >> "%LOG%"

if "%ALL_OK%"=="1" (
    echo  ╔════════════════════════════════════════════════╗
    echo  ║  ✓ No critical problems found!                  ║
    echo  ║  Send DIAGNOSIS_REPORT.txt to your developer.  ║
    echo  ╚════════════════════════════════════════════════╝
    (echo  All checks passed. Send this file to your developer.) >> "%LOG%"
) else (
    echo  ╔════════════════════════════════════════════════╗
    echo  ║  ✗ PROBLEMS FOUND - see FAIL items above        ║
    echo  ║                                                  ║
    echo  ║  Most likely fix:                                ║
    echo  ║  Right-click: FIX - Allow in Antivirus.bat      ║
    echo  ║  → Run as administrator                          ║
    echo  ║                                                  ║
    echo  ║  Then send DIAGNOSIS_REPORT.txt to developer.   ║
    echo  ╚════════════════════════════════════════════════╝
    (echo  PROBLEMS FOUND - see FAIL items above.) >> "%LOG%"
    (echo.) >> "%LOG%"
    (echo  MOST LIKELY FIX:) >> "%LOG%"
    (echo  Right-click 'FIX - Allow in Antivirus.bat' then click 'Run as administrator') >> "%LOG%"
)

echo.
echo  ──────────────────────────────────────────────────
echo  Report saved to: DIAGNOSIS_REPORT.txt
echo  Please send that file to your developer!
echo  ──────────────────────────────────────────────────
echo.
pause
