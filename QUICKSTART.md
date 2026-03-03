# Quick Start Guide - 5 Minutes to Running AI

## Step 1: Install Ollama (2 minutes)

1. Download Ollama: https://ollama.ai
2. Install and run the installer
3. Ollama will start automatically

Verify installation:
```bash
ollama --version
```

## Step 2: Pull Llama Model (2 minutes)

```bash
ollama pull llama2
```

This downloads the 4GB model. On slow internet, this may take 5-10 minutes.

## Step 3: Start Backend (1 minute)

### On macOS/Linux:
```bash
chmod +x start.sh
./start.sh
```

### On Windows:
Double-click `start.bat` or run:
```cmd
start.bat
```

### Manual startup:
```bash
pip install -r requirements.txt
cd backend
python main.py
```

You should see:
```
Starting server on 127.0.0.1:8000
LLM Model: llama2
Confidence Threshold: 70%
Uvicorn running on http://127.0.0.1:8000
```

## Step 4: Open Frontend (30 seconds)

Open `frontend/index.html` in your web browser.

Or start a local server:
```bash
cd frontend
python -m http.server 8080
# Visit http://localhost:8080
```

## Start Chatting!

Type a message and press Enter. You should see:
- Response from the AI
- Confidence score (%)
- Source (knowledge_base, llm, or support)

## What's Running?

- **Ollama**: http://localhost:11434 (LLM inference)
- **FastAPI Backend**: http://localhost:8000 (REST API)
- **Frontend**: Your browser (Chat interface)

All running locally. No cloud, no APIs, no limits.

## Test the System

Try these queries:

1. **Knowledge Base Hit**: "What are your hours?" (returns exact answer)
2. **LLM Response**: "What should I have for lunch?" (AI generates answer)
3. **Low Confidence**: "Tell me something philosophical" (may trigger support)

## Common Issues

### "Cannot connect to API"
- Make sure backend is running: `python backend/main.py`
- Check CORS is enabled in `main.py`
- Verify ports 8000 and 11434 are available

### "Ollama is offline"
- Start Ollama: `ollama serve`
- System will still work with knowledge base only

### "Slow responses"
- First query is slow (model loading)
- Subsequent queries are faster
- For very slow: check CPU/RAM usage

## What's Next?

1. **Add to Knowledge Base**: Edit `data/knowledge_base.json` with your business info
2. **Adjust Confidence**: Edit `backend/.env` to change CONFIDENCE_THRESHOLD
3. **Use Different Model**: `ollama pull mistral` then update `.env`
4. **Check Logs**: Look in `data/support_log.json` for escalated requests

## System Requirements

- Python 3.8+ (check: `python3 --version`)
- 4GB RAM minimum (8GB recommended)
- 4GB disk space for model
- Modern web browser

## Production Use

For production deployment:
1. Follow README.md's "Production Deployment" section
2. Add authentication
3. Use PostgreSQL instead of JSON
4. Set up SSL/TLS
5. Configure proper error handling

## Support Files

- `README.md` - Full documentation
- `backend/main.py` - API implementation
- `frontend/index.html` - Web UI
- `data/knowledge_base.json` - Q&A database
- `data/support_log.json` - Escalation logs (auto-created)

---

**Congratulations! You now have a fully working local AI system!**

No cloud providers. No API keys. No monthly bills. Just pure, local AI power.
