AI CHATBOT — Quick Start Guide
================================

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️  READ THIS FIRST — BEFORE YOU DO ANYTHING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  You DO NOT need Python. You DO NOT need to install anything.
  Just follow the 3 steps below.


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HOW TO START IN 3 STEPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  STEP 1: Extract the ZIP file  ← DO THIS FIRST!
  ─────────────────────────────────────────────
  ⚠️  DO NOT run files from inside the ZIP!
  ⚠️  DO NOT just double-click the ZIP file!

  RIGHT-CLICK the ZIP file → "Extract All..."
  → Choose a folder → Click "Extract"
  → Then open the EXTRACTED folder (not the ZIP)

  STEP 2: Double-click "START CHATBOT.bat"
  ─────────────────────────────────────────
  A black window will appear — this is the server.
  Wait 10–30 seconds. Your browser will open automatically.
  If a blue "Windows protected your PC" screen appears,
  click "More info" → "Run anyway" — the file is safe.

  STEP 3: Keep the black window open while you chat
  ─────────────────────────────────────────────────
  The black window = the AI server running.
  Do NOT close it while using the chatbot.
  To stop the chatbot, just close that black window.


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
IF IT'S NOT WORKING — DO THESE STEPS IN ORDER:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  STEP 1: Make sure you extracted the ZIP  (see above)
  ────────────────────────────────────────────────────
  This is the #1 cause of problems. Files must be extracted
  from the ZIP before running — not opened inside the ZIP.

  STEP 2: Allow in Antivirus  (if server stops quickly)
  ──────────────────────────────────────────────────────
  If the black window disappears within a few seconds:
  → Right-click: "FIX - Allow in Antivirus.bat"
  → Click "Run as administrator"
  → Then run START CHATBOT.bat again

  STEP 3: If browser shows "Backend not responding"
  ──────────────────────────────────────────────────
  → Make sure START CHATBOT.bat is still open (black window)
  → Wait 30 more seconds, then click "Retry Now" in the chat
  → If still not working, close everything and try again

  STEP 4: Run the diagnostics tool
  ────────────────────────────────
  → Double-click: "DIAGNOSE (run if broken).bat"
  → Wait for it to finish (about 15 seconds)
  → Send the "DIAGNOSIS_REPORT.txt" file to your developer


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
COMMON ERRORS AND THEIR FIXES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ❌ Browser shows: "Backend not responding" or "Server not responding"
  ✅ FIX: Make sure START CHATBOT.bat is running (black window is open)
          Wait 30 seconds after starting before chatting
          Click the Retry button in the chat

  ❌ "Windows protected your PC" blue screen appears
  ✅ FIX: Click "More info" → "Run anyway" — the file is safe

  ❌ Black window opens and closes immediately
  ✅ FIX: Antivirus is blocking the file.
          Right-click "FIX - Allow in Antivirus.bat" → Run as administrator
          Then run START CHATBOT.bat again

  ❌ Nothing happens when double-clicking START CHATBOT.bat
  ✅ FIX: You are probably running from inside the ZIP.
          Right-click the ZIP → Extract All → run from extracted folder

  ❌ chatbot-server.exe is missing
  ✅ FIX: Antivirus deleted it. Open Windows Security →
          Virus & threat protection → Protection history →
          Find chatbot-server.exe → click Restore
          Then run "FIX - Allow in Antivirus.bat" as Administrator

  ❌ Chat works but AI gives wrong/no answers
  ✅ This is normal if there is no internet — the AI uses local
          knowledge only. Check your internet connection.


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FILES IN THIS PACKAGE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  START CHATBOT.bat             ← Run this to start  (DOUBLE-CLICK THIS)
  FIX - Allow in Antivirus.bat  ← Run if server is blocked by antivirus
  DIAGNOSE (run if broken).bat  ← Run if something is wrong
  chatbot-server.exe            ← The AI backend  (do not delete!)
  _internal/                    ← Required support files  (do not delete!)
  frontend/index.html           ← The chat interface
  data/knowledge_base.json      ← Q&A answers database
  .env                          ← Settings (API key, etc.)
  README.txt                    ← This file


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REQUIREMENTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ✔ Windows 7, 8, 10, or 11  (64-bit)
  ✔ Internet connection  (for AI responses via Groq Cloud)
  ✔ Any modern browser  (Chrome, Edge, Firefox)
  ✘ Python NOT needed — it's built into the chatbot-server.exe!
  ✘ No installation needed — just extract and run!

