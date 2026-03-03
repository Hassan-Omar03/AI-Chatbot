# Local AI Chat - Next.js Setup Guide

This is a **Next.js 16 application** with a local AI backend that works entirely offline.

## What You Have

- **Frontend**: Modern React chat interface (Next.js App Router)
- **Backend**: Next.js API routes that connect to Ollama (local LLM)
- **Knowledge Base**: SQLite/JSON database with predefined Q&A
- **Intent Detection**: NLP engine to understand user queries
- **Safety System**: Confidence scoring and support escalation

## Quick Start (5 minutes)

### 1. Install Ollama

Download and install Ollama from [ollama.ai](https://ollama.ai)

### 2. Pull a Model

```bash
ollama pull llama2
# or for a smaller, faster model:
ollama pull mistral
```

Keep Ollama running in the background. It will listen on `http://localhost:11434`

### 3. Start the Application

```bash
# Install dependencies
npm install
# or if using pnpm:
pnpm install

# Start the Next.js dev server
npm run dev
# or with pnpm:
pnpm dev
```

The app will be available at `http://localhost:3000`

### 4. Start Chatting

- Open `http://localhost:3000` in your browser
- Type a message and press Enter
- Watch the system respond with answers from the knowledge base or Ollama

## How It Works

```
User Types Message (UI)
         ↓
    /api/chat endpoint
         ↓
    Intent Detection (NLP)
         ↓
    Knowledge Base Lookup
         ↓
    ✅ Found? → Return answer (100% confidence)
    ❌ Not Found? → Query Ollama
         ↓
    Confidence Scoring
         ↓
    ✅ High (>70%)? → Return response
    ❌ Low (<70%)? → Create support ticket
         ↓
    Response back to UI
```

## Project Structure

```
app/
├── page.tsx              # Main chat UI
├── api/
│   ├── chat/route.ts    # Chat endpoint with NLP, KB lookup, Ollama
│   └── health/route.ts  # Health check endpoint
└── layout.tsx

data/
├── knowledge_base.json  # Q&A database (easily customizable)
├── chat_stats.json      # Auto-generated stats
└── chat_logs.json       # Auto-generated chat history

requirements.txt         # Python dependencies (if using standalone backend)
```

## Configuration

### Change the LLM Model

Edit `/app/api/chat/route.ts` and change the `model` parameter:

```typescript
body: JSON.stringify({
  model: 'llama2',  // Change this to 'mistral', 'neural-chat', etc.
  prompt: `Answer this question concisely...`,
  ...
})
```

### Adjust Confidence Threshold

Edit `/app/api/chat/route.ts` to change when support tickets are created:

```typescript
const CONFIDENCE_THRESHOLD = 0.7  // Change to 0.5, 0.8, etc.
```

### Customize the Knowledge Base

Edit `/data/knowledge_base.json` to add your own Q&A pairs:

```json
{
  "entries": [
    {
      "id": "kb-011",
      "question": "What is my question?",
      "answer": "This is my answer",
      "keywords": ["keyword1", "keyword2"],
      "category": "general",
      "confidence": 0.95
    }
  ]
}
```

## API Endpoints

### POST /api/chat
Send a user message and get a response.

**Request:**
```json
{
  "message": "What are your business hours?"
}
```

**Response:**
```json
{
  "response": "Our customer support team is available 24/7...",
  "confidence": 0.95,
  "source": "knowledge_base",
  "support_ticket_id": null,
  "intent": "help"
}
```

### GET /api/health
Check system health and stats.

**Response:**
```json
{
  "ollama_available": true,
  "database_ready": true,
  "uptime": 3600,
  "total_chats": 42,
  "average_confidence": 0.82
}
```

## Troubleshooting

### 404 Error on `/api/chat`

**Problem**: API endpoint not found

**Solution**: 
- Make sure you're accessing `http://localhost:3000` (not `http://localhost:3000/api/chat`)
- The API is only available from the UI
- Check browser console for error details

### "Cannot connect to backend"

**Problem**: The frontend shows an error that it can't reach the backend

**Solution**:
- Make sure Ollama is running: `ollama serve` (on Windows/Mac, it runs automatically)
- Check that Ollama is listening on `http://localhost:11434`
- Try `curl http://localhost:11434/api/tags` to test Ollama

### "Thinking..." takes too long

**Problem**: The AI is slow to respond

**Solution**:
- Smaller models like `mistral` are faster than `llama2`
- Pull a faster model: `ollama pull mistral`
- Ensure you have enough RAM (minimum 8GB recommended)

### Model not found

**Problem**: Error saying the model isn't available

**Solution**:
- Pull the model first: `ollama pull llama2`
- Check available models: `ollama list`
- Make sure the model name in the code matches exactly

## Production Deployment

### Build for production:

```bash
npm run build
npm start
```

### Using Docker:

```bash
docker-compose up
```

This will start:
- Ollama on port 11434
- Next.js backend on port 3000
- Nginx reverse proxy on port 80

### Environment Variables

No environment variables needed for local development. For production with different Ollama hosts, you can set:

```bash
OLLAMA_URL=http://your-ollama-host:11434
```

## Data Storage

- **Chat logs**: Stored in `/data/chat_logs.json`
- **Statistics**: Stored in `/data/chat_stats.json`
- **Knowledge base**: Stored in `/data/knowledge_base.json`

All data is local - nothing is sent to external servers.

## Next Steps

1. **Customize your knowledge base**: Edit `/data/knowledge_base.json`
2. **Add more intents**: Edit the `INTENT_KEYWORDS` in `/app/api/chat/route.ts`
3. **Adjust settings**: Change confidence thresholds, timeouts, etc.
4. **Deploy**: Push to GitHub and deploy to Vercel, Railway, etc.

## Support

For issues or questions:
- Check the troubleshooting section above
- Review the chat logs in `/data/chat_logs.json`
- Check the browser console for errors
