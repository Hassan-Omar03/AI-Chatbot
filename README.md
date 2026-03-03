# 🤖 Local AI Chatbot System
**Powered by Llama 3 (Ollama) + FastAPI + Local Knowledge Base**

---

## 📦 What's Inside

```
chatbot-system/
├── start.bat               ← Double-click to run on Windows
├── requirements.txt        ← Python dependencies
│
├── backend/
│   ├── main.py             ← FastAPI app (the brain)
│   ├── llm_engine.py       ← Llama 3 via Ollama integration
│   ├── intent_detector.py  ← NLP intent classification
│   ├── database.py         ← Knowledge base (JSON / SQLite)
│   ├── safety.py           ← Safety trigger & support escalation
│   └── .env.example        ← Configuration template
│
├── frontend/
│   └── index.html          ← Chat UI (open in any browser)
│
└── data/
    └── knowledge_base.json ← Your Q&A database (edit freely!)
```

---

## 🚀 Quick Start (Windows)

### Step 1 — Install Ollama + Pull Llama 3
1. Download: [https://ollama.com/download](https://ollama.com/download)
2. Open a terminal and run:
   ```bash
   ollama serve
   ollama pull llama3
   ```

### Step 2 — Run the Chatbot
Double-click `start.bat`  
*(It installs dependencies, opens your browser, and starts the API)*

### Step 3 — Start Chatting
Your browser opens `frontend/index.html` automatically.  
The API runs at `http://localhost:8000`

---

## 🔄 How It Works

```
User Message
     ↓
[1] Intent Detection (NLP keyword scoring)
     ↓
[2] Knowledge Base Search  ──→ Found? Return instant answer (100% confidence)
     ↓  (not found)
[3] Llama 3 Generation (Ollama local model)
     ↓
[4] Safety Check: confidence ≥ 70%?
     ├─ YES → Return AI response
     └─ NO  → Create support ticket + show contact info
```

---

## ⚙️ Configuration

Edit `backend/.env`:

| Variable              | Default                  | Description                    |
|-----------------------|--------------------------|--------------------------------|
| `OLLAMA_MODEL`        | `llama3`                 | Model to use (llama3, llama2…) |
| `OLLAMA_BASE_URL`     | `http://localhost:11434` | Ollama server URL              |
| `CONFIDENCE_THRESHOLD`| `70`                     | Escalation threshold (0–100)   |
| `DB_TYPE`             | `json`                   | `json` or `sqlite`             |
| `SUPPORT_EMAIL`       | `support@company.com`    | Shown on escalation            |
| `SUPPORT_PHONE`       | `1-800-COMPANY`          | Shown on escalation            |

---

## 📚 Customising the Knowledge Base

Edit `data/knowledge_base.json` to add your own Q&A pairs:

```json
{
  "answers": [
    {
      "id": 16,
      "intent": "my_custom_intent",
      "answer": "Your answer text here.",
      "keywords": ["keyword1", "keyword2", "phrase that triggers this"],
      "category": "general"
    }
  ]
}
```
Or use the API endpoint to add entries at runtime:
```
POST http://localhost:8000/knowledge-base/add
```

---

## 🛡️ Safety Escalation

When the AI's confidence drops below the threshold (default 70%), it:
1. Creates a support ticket (logged to `data/support_log.json`)
2. Returns a friendly message with your support contact info
3. Shows a ticket ID the user can reference

View all tickets: `GET http://localhost:8000/support/tickets`  
View stats: `GET http://localhost:8000/support/stats`

---

## 🌐 API Endpoints

| Method | Endpoint                  | Description                    |
|--------|---------------------------|--------------------------------|
| `POST` | `/chat`                   | Send a message, get a response |
| `GET`  | `/health`                 | System health check            |
| `GET`  | `/knowledge-base`         | List all KB entries            |
| `POST` | `/knowledge-base/add`     | Add a new KB entry             |
| `POST` | `/support-trigger`        | Manually create a support ticket |
| `GET`  | `/support/tickets`        | View recent support tickets    |
| `GET`  | `/support/stats`          | Escalation statistics          |
| `GET`  | `/docs`                   | Interactive Swagger API docs   |

---

## 💡 Tips

- **No Ollama?** The bot still works — it uses the Knowledge Base only.
- **Test the API** via Swagger UI at `http://localhost:8000/docs`
- **Add more intents** in `backend/intent_detector.py`
- **Switch to SQLite** by setting `DB_TYPE=sqlite` in `.env`

---

*Built with FastAPI · Ollama · Llama 3 · Vanilla JS*
