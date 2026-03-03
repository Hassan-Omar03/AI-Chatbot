@echo off
REM ============================================================
REM  Chatbot EXE Builder — Works on ANY Windows PC
REM  Output: release\ folder (zip and send to client)
REM ============================================================
setlocal enabledelayedexpansion
title Building Chatbot...

echo.
echo  ==========================================
echo   Building Chatbot EXE for Distribution
echo  ==========================================
echo.

REM Stop any running server first
taskkill /F /IM chatbot-server.exe >nul 2>&1

REM Install build tools
echo [1/5] Installing PyInstaller...
pip install pyinstaller -q
if %errorlevel% neq 0 ( echo [ERROR] pip failed & pause & exit /b 1 )
echo Done.

REM Clean old build
echo [2/5] Cleaning old build files...
if exist "backend\build"  rmdir /S /Q "backend\build"
if exist "backend\dist"   rmdir /S /Q "backend\dist"
if exist "release"        rmdir /S /Q "release"
echo Done.

REM Build the exe (onedir = folder, more compatible than onefile)
echo [3/5] Building EXE (takes 1-3 minutes, please wait)...
cd backend
python -m PyInstaller --noconfirm ^
  --name "chatbot-server" ^
  --onedir ^
  --console ^
  --hidden-import uvicorn ^
  --hidden-import uvicorn.main ^
  --hidden-import uvicorn.config ^
  --hidden-import uvicorn.lifespan ^
  --hidden-import uvicorn.lifespan.off ^
  --hidden-import uvicorn.lifespan.on ^
  --hidden-import uvicorn.protocols ^
  --hidden-import uvicorn.protocols.http ^
  --hidden-import uvicorn.protocols.http.auto ^
  --hidden-import uvicorn.protocols.http.h11_impl ^
  --hidden-import uvicorn.loops ^
  --hidden-import uvicorn.loops.asyncio ^
  --hidden-import uvicorn.loops.auto ^
  --hidden-import fastapi ^
  --hidden-import starlette ^
  --hidden-import starlette.routing ^
  --hidden-import starlette.middleware ^
  --hidden-import starlette.middleware.cors ^
  --hidden-import pydantic ^
  --hidden-import pydantic.main ^
  --hidden-import dotenv ^
  --hidden-import requests ^
  --hidden-import email.mime.text ^
  --hidden-import email.mime.multipart ^
  --hidden-import logging ^
  --hidden-import json ^
  --hidden-import sqlite3 ^
  --hidden-import re ^
  --add-data ".env.example;." ^
  main.py

if %errorlevel% neq 0 (
    echo [ERROR] Build failed! See above for details.
    cd ..
    pause
    exit /b 1
)
cd ..
echo Done.

REM Assemble the release folder
echo [4/5] Creating release package...

mkdir "release"
mkdir "release\data"
mkdir "release\frontend"

REM Copy exe folder contents (onedir output)
xcopy /E /Q /Y "backend\dist\chatbot-server\*" "release\"

REM Copy data
copy /Y "data\knowledge_base.json" "release\data\"
echo {"tickets":[]} > "release\data\support_log.json"

REM Copy frontend
copy /Y "frontend\index.html" "release\frontend\"

REM Copy env example
copy /Y "backend\.env.example" "release\.env.example"

REM Create a ready-to-use .env with Groq (client fills in their own key if needed)
(
echo # AI Chatbot Configuration
echo # ========================
echo.
echo # AI Provider: groq (online, free) or ollama (local install required)
echo AI_PROVIDER=groq
echo.
echo # Get FREE API key from: https://console.groq.com
echo GROQ_API_KEY=
echo GROQ_MODEL=llama-3.3-70b-versatile
echo.
echo # Confidence threshold (70 = escalate if AI is less than 70% sure)
echo CONFIDENCE_THRESHOLD=70
echo.
echo # Support contact info
echo SUPPORT_EMAIL=support@yourcompany.com
echo SUPPORT_PHONE=1-800-YOUR-NUMBER
echo.
echo # Server settings (do not change unless port 8000 is busy)
echo SERVER_HOST=127.0.0.1
echo SERVER_PORT=8000
) > "release\.env"

REM Create the double-click launcher
(
echo @echo off
echo title AI Chatbot
echo color 0A
echo echo.
echo echo  ====================================================
echo echo   AI Chatbot - Starting...
echo echo  ====================================================
echo echo.
echo echo  Opening chat in your browser...
echo start "" "frontend\index.html"
echo echo.
echo echo  Starting AI server (keep this window open^)...
echo echo  Press Ctrl+C to stop the chatbot.
echo echo.
echo chatbot-server.exe
echo pause
) > "release\START CHATBOT.bat"

REM Create README
(
echo AI CHATBOT - Quick Start
echo ========================
echo.
echo 1. Double-click "START CHATBOT.bat"
echo 2. Browser opens automatically
echo 3. Start chatting!
echo.
echo NOTES:
echo - Keep the black terminal window open while chatting
echo - Closing the terminal will stop the chatbot
echo - Internet needed for AI answers (uses Groq free API^)
echo - Without internet: uses Knowledge Base (local answers^)
echo.
echo SETUP YOUR API KEY (for AI answers^):
echo 1. Go to https://console.groq.com
echo 2. Sign up free, create an API key
echo 3. Open .env file in Notepad
echo 4. Paste your key after GROQ_API_KEY=
echo 5. Save and restart
echo.
echo TO ADD YOUR OWN ANSWERS:
echo Edit data\knowledge_base.json in Notepad
) > "release\README.txt"

REM Zip the release
echo [5/5] Creating ZIP file...
powershell -Command "Compress-Archive -Force -Path 'release\*' -DestinationPath 'chatbot-for-client.zip'"
echo Done.

echo.
echo  ==========================================
echo   BUILD COMPLETE!
echo.
echo   CLIENT PACKAGE:
echo     chatbot-for-client.zip   (send this!)
echo.
echo   CONTENTS (release\ folder):
echo     START CHATBOT.bat  - double-click to run
echo     chatbot-server.exe - the AI engine
echo     frontend\          - chat interface
echo     data\              - knowledge base
echo     .env               - configuration
echo     README.txt         - instructions
echo  ==========================================
echo.
pause
