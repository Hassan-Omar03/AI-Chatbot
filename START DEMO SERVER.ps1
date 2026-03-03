# ── AI Chatbot Demo Server Launcher ─────────────────────────────
# Right-click → Run with PowerShell

$Host.UI.RawUI.WindowTitle = "AI Chatbot - Demo Launcher"
$RELEASE    = "$PSScriptRoot\release\chatbot-server.exe"
$DEMO_FILE  = "$PSScriptRoot\DEMO - AI Chatbot.html"
$NGROK_EXE  = "C:\Users\hp\AppData\Local\Microsoft\WinGet\Links\ngrok.exe"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  AI Chatbot - Demo Server Launcher" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# ── Stop old processes ───────────────────────────────────────────
Write-Host "[1/4] Stopping old servers..." -ForegroundColor Yellow
Stop-Process -Name "chatbot-server" -Force -ErrorAction SilentlyContinue
Stop-Process -Name "ngrok"          -Force -ErrorAction SilentlyContinue
Start-Sleep 2

# ── Start backend ────────────────────────────────────────────────
Write-Host "[2/4] Starting chatbot backend..." -ForegroundColor Yellow
Start-Process -FilePath $RELEASE -WorkingDirectory "$PSScriptRoot\release" -WindowStyle Hidden

# ── Wait for port 8000 ──────────────────────────────────────────
Write-Host "[3/4] Waiting for backend on port 8000..." -ForegroundColor Yellow
$ready = $false
for ($i = 0; $i -lt 40; $i++) {
    $conn = netstat -an 2>$null | Select-String ":8000"
    if ($conn) { $ready = $true; break }
    Start-Sleep 1
}
if ($ready) {
    Write-Host "      Backend is UP!" -ForegroundColor Green
} else {
    Write-Host "      [WARN] Backend slow, continuing anyway..." -ForegroundColor Yellow
}

# ── Start ngrok ──────────────────────────────────────────────────
Write-Host "[4/4] Starting ngrok tunnel..." -ForegroundColor Yellow
Start-Process -FilePath $NGROK_EXE -ArgumentList "http 8000" -WindowStyle Minimized
Write-Host "      Waiting for tunnel to establish (12s)..." -ForegroundColor Gray
Start-Sleep 12

# ── Get public URL ───────────────────────────────────────────────
Write-Host "      Getting your public URL..." -ForegroundColor Gray
try {
    $resp = (Invoke-WebRequest 'http://localhost:4040/api/tunnels' -UseBasicParsing).Content | ConvertFrom-Json
    $NGROK_URL = ($resp.tunnels | Where-Object { $_.proto -eq 'https' }).public_url
} catch {
    $NGROK_URL = $null
}

if (-not $NGROK_URL) {
    Write-Host ""
    Write-Host "[ERROR] Could not get ngrok URL automatically." -ForegroundColor Red
    Write-Host "        Check the ngrok window in your taskbar." -ForegroundColor Red
    Write-Host "        Copy the https URL and paste it manually in DEMO - AI Chatbot.html" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit
}

# ── Patch demo HTML ──────────────────────────────────────────────
Write-Host "      Patching DEMO - AI Chatbot.html with URL..." -ForegroundColor Gray
$content = [System.IO.File]::ReadAllText($DEMO_FILE)
# Reset any old ngrok URL back to placeholder first
$content = $content -replace 'https://[a-zA-Z0-9-]+\.ngrok[a-zA-Z0-9.-]*', 'REPLACE_WITH_YOUR_SERVER_URL'
# Now insert new URL
$content = $content -replace 'REPLACE_WITH_YOUR_SERVER_URL', $NGROK_URL
[System.IO.File]::WriteAllText($DEMO_FILE, $content)

# ── Open demo in browser ─────────────────────────────────────────
Start-Process $DEMO_FILE

# ── Done! ────────────────────────────────────────────────────────
Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  SUCCESS!" -ForegroundColor Green
Write-Host ""
Write-Host "  Public URL : $NGROK_URL" -ForegroundColor White
Write-Host ""
Write-Host "  SEND THIS FILE TO CLIENT:" -ForegroundColor Cyan
Write-Host "  DEMO - AI Chatbot.html" -ForegroundColor White
Write-Host ""
Write-Host "  Keep this window open while client is testing." -ForegroundColor Yellow
Write-Host "  Close it to stop the demo (client loses access)." -ForegroundColor Yellow
Write-Host ""
Write-Host "  After payment: send AI-Chatbot-Client.zip" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Read-Host "Press Enter to exit (servers keep running)"
