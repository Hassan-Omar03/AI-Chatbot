# Configuration Reference

Complete guide to all configuration options and environment variables.

## Environment Variables (.env)

Located in `backend/.env`

### Ollama Configuration

#### OLLAMA_BASE_URL
- **Type**: String (URL)
- **Default**: `http://localhost:11434`
- **Description**: Base URL of Ollama server
- **Examples**:
  - Local: `http://localhost:11434`
  - Network: `http://192.168.1.100:11434`
  - Docker: `http://ollama:11434`

#### OLLAMA_MODEL
- **Type**: String
- **Default**: `llama2`
- **Description**: LLM model to use
- **Available Models**:
  - `llama2` - Default, balanced (4GB)
  - `mistral` - Fast and capable (4GB)
  - `neural-chat` - Small and fast (2GB)
  - `dolphin-phi` - Ultra lightweight (1.6GB)
  - `llama2-uncensored` - Larger variant (7GB)
- **Example**:
  ```env
  OLLAMA_MODEL=mistral
  ```

### Confidence & Safety

#### CONFIDENCE_THRESHOLD
- **Type**: Integer (0-100)
- **Default**: `70`
- **Description**: Minimum confidence score for accepting AI response
- **Behavior**:
  - Score < threshold → Escalate to support
  - Score ≥ threshold → Return AI response
- **Recommendations**:
  - `50-60`: Accept more responses, higher false positives
  - `70` (default): Good balance
  - `80-90`: Only confident responses, more escalations
- **Example**:
  ```env
  CONFIDENCE_THRESHOLD=75
  ```

### Database Configuration

#### DATABASE_PATH
- **Type**: String (File path)
- **Default**: `./data/knowledge_base.json`
- **Description**: Path to knowledge base file/database
- **Supported Paths**:
  - Relative: `./data/knowledge_base.json`
  - Absolute: `/var/lib/knowledge_base.json`
  - Docker: `/app/data/knowledge_base.json`
- **Example**:
  ```env
  DATABASE_PATH=/data/knowledge_base.json
  ```

#### DB_TYPE
- **Type**: String
- **Default**: `json`
- **Allowed Values**:
  - `json` - JSON file (simple, no server needed)
  - `sqlite` - SQLite database (structured, better for large datasets)
- **Comparison**:
  | Feature | JSON | SQLite |
  |---------|------|--------|
  | Setup | Instant | Requires init |
  | Scale | < 1000 items | Unlimited |
  | Query Speed | Slow (O(n)) | Fast (indexed) |
  | Transactions | No | Yes |
  | Backup | File copy | Easy |
- **Example**:
  ```env
  DB_TYPE=sqlite
  DATABASE_PATH=./data/knowledge_base.db
  ```

### Server Configuration

#### SERVER_HOST
- **Type**: String (IP address or hostname)
- **Default**: `127.0.0.1`
- **Description**: Server binding address
- **Options**:
  - `127.0.0.1` - Localhost only (secure)
  - `0.0.0.0` - All interfaces (accessible from network)
  - `192.168.1.100` - Specific interface
- **Security Note**: Use `127.0.0.1` for local use, `0.0.0.0` requires authentication for production
- **Example**:
  ```env
  SERVER_HOST=0.0.0.0
  ```

#### SERVER_PORT
- **Type**: Integer
- **Default**: `8000`
- **Description**: Server listening port
- **Common Ports**:
  - `8000` - Default
  - `5000` - Alternative
  - `3000` - Node.js style
  - `80` - Production (requires sudo)
- **Troubleshooting**: If port is in use, pick different port:
  ```env
  SERVER_PORT=8001
  ```

### Logging

#### LOG_LEVEL
- **Type**: String
- **Default**: `INFO`
- **Allowed Values**:
  - `DEBUG` - Very verbose (all actions logged)
  - `INFO` - Standard (important events)
  - `WARNING` - Only warnings and errors
  - `ERROR` - Only errors
  - `CRITICAL` - Only critical failures
- **Use Cases**:
  - Development: `DEBUG`
  - Production: `INFO` or `WARNING`
  - Troubleshooting: `DEBUG`
- **Example**:
  ```env
  LOG_LEVEL=DEBUG
  ```

## Complete Example Configurations

### Development Setup

```env
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# Confidence & Safety
CONFIDENCE_THRESHOLD=70

# Database
DATABASE_PATH=./data/knowledge_base.json
DB_TYPE=json

# Server
SERVER_HOST=127.0.0.1
SERVER_PORT=8000

# Logging
LOG_LEVEL=DEBUG
```

### Production Setup

```env
# Ollama Configuration
OLLAMA_BASE_URL=http://ollama-server.internal:11434
OLLAMA_MODEL=mistral

# Confidence & Safety
CONFIDENCE_THRESHOLD=80

# Database
DATABASE_PATH=/var/lib/knowledge_base.db
DB_TYPE=sqlite

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# Logging
LOG_LEVEL=INFO
```

### Docker Setup

```env
# Ollama Configuration
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama2

# Confidence & Safety
CONFIDENCE_THRESHOLD=70

# Database
DATABASE_PATH=/app/data/knowledge_base.json
DB_TYPE=json

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# Logging
LOG_LEVEL=INFO
```

### Performance Setup (Fast Responses)

```env
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=neural-chat  # Smaller model

# Confidence & Safety
CONFIDENCE_THRESHOLD=60    # Accept more responses

# Database
DATABASE_PATH=./data/knowledge_base.json
DB_TYPE=json

# Server
SERVER_HOST=127.0.0.1
SERVER_PORT=8000

# Logging
LOG_LEVEL=INFO
```

### Quality Setup (Better Responses)

```env
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2-uncensored  # Larger model

# Confidence & Safety
CONFIDENCE_THRESHOLD=80         # Only confident responses

# Database
DATABASE_PATH=./data/knowledge_base.db
DB_TYPE=sqlite

# Server
SERVER_HOST=127.0.0.1
SERVER_PORT=8000

# Logging
LOG_LEVEL=DEBUG
```

## Configuration by Use Case

### Customer Support Chatbot

```env
# High confidence for good customer experience
CONFIDENCE_THRESHOLD=75
OLLAMA_MODEL=mistral
DB_TYPE=sqlite
LOG_LEVEL=INFO
```

### Internal Knowledge Assistant

```env
# Lower threshold OK for internal use
CONFIDENCE_THRESHOLD=60
OLLAMA_MODEL=llama2
DB_TYPE=json
LOG_LEVEL=DEBUG
```

### Mobile-Accessible System

```env
# Accessible from any device
SERVER_HOST=0.0.0.0
# Fast responses (smaller model)
OLLAMA_MODEL=neural-chat
CONFIDENCE_THRESHOLD=70
```

### Resource-Constrained Environment

```env
# Minimal resource usage
OLLAMA_MODEL=dolphin-phi    # Smallest model
CONFIDENCE_THRESHOLD=50      # Accept more to reduce escalations
DB_TYPE=json                 # Simpler than SQLite
LOG_LEVEL=WARNING
```

## Knowledge Base Configuration

### JSON Knowledge Base Structure

File: `data/knowledge_base.json`

```json
{
  "answers": [
    {
      "id": 1,
      "intent": "category_name",
      "answer": "The answer text",
      "keywords": ["keyword1", "keyword2", "keyword3"]
    }
  ]
}
```

**Best Practices**:
- Keep `keywords` array small (3-7 items)
- Use single words or short phrases
- Make keywords specific but not overly technical
- Include variations: "return", "refund", "money back"

### SQLite Database Schema

Automatically created on first use:

```sql
CREATE TABLE answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    intent TEXT NOT NULL,
    answer TEXT NOT NULL,
    keywords TEXT NOT NULL,  -- JSON array as string
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Port Configuration

### Default Port Layout

| Service | Port | Host | Path |
|---------|------|------|------|
| Ollama | 11434 | localhost | /api |
| FastAPI | 8000 | localhost | / |
| Frontend | Browser | - | frontend/index.html |
| Nginx | 80 | 0.0.0.0 | / (if using Docker) |

### Changing Ports

If ports conflict:

```env
# Change FastAPI port
SERVER_PORT=8001

# For Ollama, restart with different port:
# ollama serve --port 11435
```

Then update frontend to use new port:
```javascript
// In frontend/index.html
const API_URL = "http://localhost:8001";
```

## SSL/TLS Configuration

For HTTPS (production):

1. **Get certificate** (Let's Encrypt):
```bash
certbot certonly --standalone -d yourdomain.com
```

2. **Update Nginx** (if using Docker):
```nginx
server {
    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    # ... rest of config
}
```

3. **Or use FastAPI directly**:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 \
  --ssl-keyfile=/path/to/key.pem \
  --ssl-certfile=/path/to/cert.pem
```

## Database Comparison

### When to use JSON

✅ **Use JSON when**:
- Learning/development
- Small knowledge base (< 500 items)
- Single machine deployment
- Frequent manual edits
- No concurrent writes

```env
DB_TYPE=json
DATABASE_PATH=./data/knowledge_base.json
```

### When to use SQLite

✅ **Use SQLite when**:
- Production deployment
- Large knowledge base (> 1000 items)
- Better query performance needed
- Need transactions
- API-driven updates

```env
DB_TYPE=sqlite
DATABASE_PATH=./data/knowledge_base.db
```

## Performance Tuning

### Response Time Tuning

**Faster Responses**:
```env
OLLAMA_MODEL=neural-chat          # Smaller model
CONFIDENCE_THRESHOLD=50            # Fewer checks
DB_TYPE=json                       # Simpler lookups
```

**Better Quality**:
```env
OLLAMA_MODEL=llama2-uncensored    # Larger model
CONFIDENCE_THRESHOLD=80            # More filtering
DB_TYPE=sqlite                     # Indexed queries
```

### Memory Tuning

**Low Memory (4GB)**:
```env
OLLAMA_MODEL=dolphin-phi
```

**Medium Memory (8GB)**:
```env
OLLAMA_MODEL=neural-chat
```

**High Memory (16GB+)**:
```env
OLLAMA_MODEL=llama2-uncensored
```

## Docker Environment Variables

In `docker-compose.yml`:

```yaml
environment:
  - OLLAMA_BASE_URL=http://ollama:11434
  - OLLAMA_MODEL=llama2
  - CONFIDENCE_THRESHOLD=70
  - DATABASE_PATH=/app/data/knowledge_base.json
  - DB_TYPE=json
  - SERVER_HOST=0.0.0.0
  - SERVER_PORT=8000
  - LOG_LEVEL=INFO
```

Override at runtime:
```bash
docker-compose up -e OLLAMA_MODEL=mistral
```

## Validation

### Check Configuration

```python
import os
from dotenv import load_dotenv

load_dotenv()

config = {
    'ollama_base_url': os.getenv('OLLAMA_BASE_URL'),
    'model': os.getenv('OLLAMA_MODEL'),
    'threshold': int(os.getenv('CONFIDENCE_THRESHOLD', 70)),
    'db_type': os.getenv('DB_TYPE'),
    'db_path': os.getenv('DATABASE_PATH'),
    'host': os.getenv('SERVER_HOST'),
    'port': int(os.getenv('SERVER_PORT', 8000)),
    'log_level': os.getenv('LOG_LEVEL'),
}

for key, value in config.items():
    print(f"{key}: {value}")
```

### Test Connectivity

```bash
# Test Ollama
curl http://localhost:11434/api/tags

# Test Backend
curl http://localhost:8000/health
```

## Resetting to Defaults

```bash
# Restore default configuration
cd backend
cp .env.example .env
```

## Troubleshooting Configuration

### "Key error" in logs

- Missing environment variable
- Check `.env` file exists
- Run `cp .env.example .env`

### "Port already in use"

- Change `SERVER_PORT` in `.env`
- Or kill existing process

### "Cannot connect to Ollama"

- Check `OLLAMA_BASE_URL` is correct
- Verify Ollama is running
- For Docker, use `http://ollama:11434` not `localhost`

### "Slow responses"

- Check `OLLAMA_MODEL` is lightweight
- Monitor logs: `LOG_LEVEL=DEBUG`
- Check available RAM

---

**For more information, see README.md and SETUP.md**
