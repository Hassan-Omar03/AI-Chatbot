' ================================================
'  AI Chatbot — Silent Launcher
'  Double-click to start without a black window.
'  Windows 7, 8, 10, 11 compatible.
' ================================================

On Error Resume Next

Dim shell, fso, appDir, serverExe, htmlFile, i

Set shell = CreateObject("WScript.Shell")
Set fso   = CreateObject("Scripting.FileSystemObject")

' Get the folder where this VBS file lives
appDir    = fso.GetParentFolderName(WScript.ScriptFullName)
serverExe = appDir & "\chatbot-server.exe"
htmlFile  = appDir & "\frontend\index.html"

' ── Check that server exe exists ──────────────────────
If Not fso.FileExists(serverExe) Then
    MsgBox "ERROR: chatbot-server.exe not found!" & vbCrLf & vbCrLf & _
           "CAUSE 1: You are running from inside the ZIP." & vbCrLf & _
           "FIX: Right-click the ZIP → Extract All → run from extracted folder." & vbCrLf & vbCrLf & _
           "CAUSE 2: Antivirus deleted chatbot-server.exe." & vbCrLf & _
           "FIX: Run 'FIX - Allow in Antivirus.bat' as Administrator." & vbCrLf & vbCrLf & _
           "Expected file at: " & serverExe, _
           vbCritical, "AI Chatbot — Error"
    WScript.Quit
End If

' ── Check that frontend exists ─────────────────────────
If Not fso.FileExists(htmlFile) Then
    MsgBox "ERROR: frontend\index.html not found!" & vbCrLf & vbCrLf & _
           "FIX: Make sure you extracted ALL files from the ZIP." & vbCrLf & _
           "Expected: " & htmlFile, _
           vbCritical, "AI Chatbot — Error"
    WScript.Quit
End If

' ── Check _internal folder exists ─────────────────────
Dim internalDir
internalDir = appDir & "\_internal"
If Not fso.FolderExists(internalDir) Then
    MsgBox "ERROR: _internal folder not found!" & vbCrLf & vbCrLf & _
           "FIX: Make sure you extracted ALL files from the ZIP." & vbCrLf & _
           "The _internal folder must be in the same folder as chatbot-server.exe.", _
           vbCritical, "AI Chatbot — Error"
    WScript.Quit
End If

' ── Ensure data folder exists ──────────────────────────
If Not fso.FolderExists(appDir & "\data") Then
    fso.CreateFolder(appDir & "\data")
End If

' ── Kill any old server instance ──────────────────────
shell.Run "taskkill /F /IM chatbot-server.exe", 0, True
WScript.Sleep 1500

' ── Start backend server silently ─────────────────────
shell.Run """" & serverExe & """", 0, False

' ── Wait up to 60 seconds for server to start ─────────
' Check every second — opens browser as soon as ready
WScript.Sleep 4000

Dim winHttp
Set winHttp = CreateObject("WinHttp.WinHttpRequest.5.1")

Dim serverReady
serverReady = False

For i = 1 To 60
    WScript.Sleep 1000
    On Error Resume Next
    winHttp.Open "GET", "http://localhost:8000/health", False
    winHttp.SetTimeouts 2000, 2000, 3000, 3000
    winHttp.Send
    If winHttp.Status = 200 Then
        serverReady = True
        Exit For
    End If
    On Error GoTo 0
Next

' ── Check if server actually started ──────────────────
If Not serverReady Then
    ' Server didn't respond — but still try opening UI (may be partially up)
    Dim msg
    msg = "WARNING: The chatbot server did not respond within 60 seconds." & vbCrLf & vbCrLf & _
          "The browser will still open. If the chat shows an error:" & vbCrLf & _
          "1. Wait another 30 seconds" & vbCrLf & _
          "2. Click the Retry button in the chat" & vbCrLf & vbCrLf & _
          "If it still doesn't work, try:" & vbCrLf & _
          "Right-click 'FIX - Allow in Antivirus.bat' → Run as administrator"
    MsgBox msg, vbExclamation, "AI Chatbot — Slow Start"
End If

' ── Open the chat UI ──────────────────────────────────
shell.Run """" & htmlFile & """", 1, False

Set shell   = Nothing
Set fso     = Nothing
Set winHttp = Nothing
