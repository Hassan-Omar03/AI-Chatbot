@echo off
REM ============================================================
REM  Local AI Chatbot — Windows Startup Script
REM  Flow: User → Intent → Knowledge Base → Llama 3 → Safety
REM ============================================================
setlocal enabledelayedexpansion

title Local AI Chatbot Startup

echo.
echo  ╔══════════════════════════════════════════╗
echo  ║    Local AI Chatbot — Startup Script     ║
echo  ║    Powered by Llama 3 + FastAPI          ║
echo  ╚══════════════════════════════════════════╝
echo.

REM ── Check Python (use py launcher, not Microsoft Store python) ──────────
py -3 --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERROR] Python is not installed or not found in PATH.
    echo          Install from: https://python.org/downloads/
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('py -3 --version 2^>^&1') do echo  [OK] %%v found

REM ── Ensure data directory ────────────────────────────────
if not exist data mkdir data
echo  [OK] Data directory ready

REM ── Install Python dependencies ──────────────────────────
echo.
echo  Installing Python dependencies...
py -3 -m pip install -q -r requirements.txt
if %errorlevel% neq 0 (
    echo  [ERROR] Failed to install dependencies.
    echo          Try manually: py -3 -m pip install -r requirements.txt
    pause
    exit /b 1
)
echo  [OK] Dependencies installed

REM ── Create .env from example if not present ──────────────
if not exist backend\.env (
    if exist backend\.env.example (
        copy backend\.env.example backend\.env >nul
        echo  [OK] Created backend\.env from example
        echo       Edit it to configure your model and settings.
    )
)

REM ── Check Ollama ─────────────────────────────────────────
echo.
echo  Checking Ollama (local Llama 3)...
curl -s --connect-timeout 3 http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% equ 0 (
    echo  [OK] Ollama is running
) else (
    echo.
    echo  [WARN] Ollama is NOT running.
    echo.
    echo         To start Ollama:
    echo           1. Open a new terminal
    echo           2. Run: ollama serve
    echo           3. Then pull Llama 3: ollama pull llama3
    echo.
    echo         The chatbot will still work using the Knowledge Base only.
    echo         Press any key to continue anyway, or Ctrl+C to cancel.
    pause >nul
)

REM ── Open the frontend in browser ─────────────────────────
echo.
echo  Opening frontend in browser...
start "" "frontend\index.html"

REM ── Start FastAPI backend ─────────────────────────────────
echo.
echo  Starting FastAPI backend on http://127.0.0.1:8000
echo  API Docs: http://127.0.0.1:8000/docs
echo.
echo  Press Ctrl+C to stop the server.
echo  ──────────────────────────────────────────────────────
cd backend
py -3 main.py

pause
