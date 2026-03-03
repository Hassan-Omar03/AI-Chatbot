@echo off
:: This launcher is compiled inside the EXE — client never sees it
:: It extracts the demo app to temp and launches it silently

set "TMP_DIR=%TEMP%\AIChatbotDemo"
if not exist "%TMP_DIR%" mkdir "%TMP_DIR%"

:: Copy the bundled HTML to temp folder
copy /Y "%~dp0app.html" "%TMP_DIR%\index.html" >nul 2>&1

:: Open it in the default browser
start "" "%TMP_DIR%\index.html"

:: Exit silently
exit
