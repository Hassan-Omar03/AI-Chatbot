# Complete Setup Guide

Detailed installation instructions for all platforms.

## System Requirements

- **Operating System**: macOS, Linux, or Windows 10+
- **RAM**: 8GB minimum (16GB recommended)
- **Disk Space**: 10GB available (for models and dependencies)
- **CPU**: Intel/AMD with 4+ cores
- **Python**: 3.8 or higher
- **Modern Web Browser**: Chrome, Firefox, Safari, or Edge

## Prerequisites Installation

### macOS

1. **Install Homebrew** (if not installed):
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

2. **Install Python 3**:
```bash
brew install python@3.11
brew link python@3.11
```

3. **Verify Python**:
```bash
python3 --version
pip3 --version
```

4. **Install Ollama**:
```bash
brew install ollama
```

Or download from https://ollama.ai

### Linux (Ubuntu/Debian)

1. **Update package manager**:
```bash
sudo apt update
sudo apt upgrade -y
```

2. **Install Python 3**:
```bash
sudo apt install -y python3 python3-pip python3-venv
```

3. **Verify installation**:
```bash
python3 --version
pip3 --version
```

4. **Install Ollama**:
```bash
curl https://ollama.ai/install.sh | sh
```

### Linux (Fedora/RHEL)

```bash
sudo dnf install python3 python3-pip
curl https://ollama.ai/install.sh | sh
```

### Windows 10/11

1. **Install Python 3**:
   - Download from https://www.python.org/downloads/
   - Run installer
   - Check "Add Python to PATH"
   - Click "Install Now"

2. **Verify Python**:
   ```cmd
   python --version
   pip --version
   ```

3. **Install Ollama**:
   - Download from https://ollama.ai
   - Run installer
   - Follows on-screen instructions

## Project Setup

### 1. Clone or Extract Project

```bash
# If you have the project as a zip file
unzip local-ai-backend.zip
cd local-ai-backend

# Or clone from repository (if available)
git clone https://github.com/username/local-ai-backend.git
cd local-ai-backend
```

### 2. Create Python Virtual Environment

**macOS/Linux**:
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows**:
```cmd
python -m venv venv
venv\Scripts\activate
```

### 3. Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Download LLM Model

This step downloads Llama 2 model (~4GB). On a typical internet connection, this takes 5-15 minutes.

```bash
ollama pull llama2
```

**Alternative models** (faster but less capable):
```bash
ollama pull neural-chat    # Smaller, faster model
ollama pull mistral        # Good balance
ollama pull dolphin-phi    # Lightweight
```

### 5. Setup Backend Configuration

```bash
cd backend
cp .env.example .env
```

Edit `.env` if needed (optional - defaults are good):
```bash
nano .env    # macOS/Linux
# or
notepad .env # Windows
```

## Running the System

### Option A: Automated Startup (Recommended)

**macOS/Linux**:
```bash
chmod +x start.sh
./start.sh
```

**Windows**:
```cmd
start.bat
```

This script will:
1. Check for Python and Ollama
2. Install dependencies
3. Create `.env` file (if missing)
4. Start Ollama (if available)
5. Start FastAPI backend

### Option B: Manual Startup

#### Terminal 1: Start Ollama

```bash
ollama serve
```

You should see:
```
Listening on 127.0.0.1:11434
```

#### Terminal 2: Start Backend

```bash
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

#### Terminal 3: Serve Frontend

```bash
cd frontend
python -m http.server 8080
```

Or just open `frontend/index.html` directly in browser.

### Option C: Docker Deployment

#### Prerequisites

- Install Docker Desktop: https://www.docker.com/products/docker-desktop

#### Start with Docker Compose

```bash
docker-compose up -d
```

This starts:
- Ollama on port 11434
- FastAPI backend on port 8000
- Nginx on port 80

Check status:
```bash
docker-compose ps
```

View logs:
```bash
docker-compose logs -f backend
docker-compose logs -f ollama
```

Stop:
```bash
docker-compose down
```

## First Launch

### 1. Access the Interface

Open in your web browser:
```
frontend/index.html    (local file)
or
http://localhost:8080 (if using HTTP server)
or
http://localhost      (if using Docker)
```

### 2. Check System Status

The sidebar should show:
- ✅ All Systems Online (green light)
- Model: llama2
- API: http://localhost:8000

If status shows "LLM Offline", ensure Ollama is running.

### 3. Test with Knowledge Base

Type: "What are your hours?"

Expected response: Predefined answer from knowledge base with 100% confidence.

### 4. Test with LLM

Type: "What is the capital of France?"

Expected response: AI-generated answer with confidence score.

## Verification Checklist

- [ ] Python 3 installed (`python3 --version`)
- [ ] Ollama installed (`ollama --version`)
- [ ] Project extracted/cloned
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip list`)
- [ ] Llama 2 downloaded (`ollama list`)
- [ ] `.env` file created in backend folder
- [ ] Ollama running (`curl http://localhost:11434/api/tags`)
- [ ] Backend running (terminal shows "Uvicorn running")
- [ ] Frontend accessible in browser
- [ ] System status shows green light
- [ ] Knowledge base test works
- [ ] LLM test works

## Common Setup Issues

### Issue: "Python not found"

**Solution**: Python not in PATH
```bash
# macOS - Check installation
which python3

# Windows - Reinstall with "Add to PATH" checked
```

### Issue: "pip: command not found"

**Solution**: Use python -m pip instead
```bash
python -m pip install -r requirements.txt
```

### Issue: "Ollama not found"

**Solution**: Install Ollama from https://ollama.ai or:
```bash
# macOS
brew install ollama

# Linux
curl https://ollama.ai/install.sh | sh
```

### Issue: "Port 8000 already in use"

**Solution**: Kill existing process or use different port
```bash
# macOS/Linux - Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Windows - Use different port
# Edit backend/.env: SERVER_PORT=8001
```

### Issue: "Out of memory" during inference

**Solution**: Reduce model context or use smaller model
```bash
# Use faster model
ollama pull neural-chat

# Edit backend/.env
OLLAMA_MODEL=neural-chat
```

### Issue: Slow responses

**Solution**: 
1. First request is slower (model loads): This is normal
2. Check available RAM: `free -h` (Linux)
3. Try smaller model: `ollama pull mistral`
4. Disable other applications

## Next Steps After Setup

1. **Customize Knowledge Base**:
   - Edit `data/knowledge_base.json`
   - Add your business information
   - Test with relevant queries

2. **Adjust Confidence Threshold**:
   - Edit `backend/.env`
   - Change `CONFIDENCE_THRESHOLD` value
   - Restart backend

3. **Monitor System**:
   - Check `data/support_log.json` for escalations
   - Review confidence scores in UI
   - Adjust parameters as needed

4. **Production Deployment** (Optional):
   - Follow README.md > Production Deployment section
   - Add authentication
   - Use PostgreSQL for persistence
   - Set up SSL/TLS

## Updating the System

### Update Python Packages

```bash
pip install --upgrade -r requirements.txt
```

### Update Ollama

**macOS**:
```bash
brew upgrade ollama
```

**Other platforms**: Reinstall from https://ollama.ai

### Update Model

```bash
ollama pull llama2    # Latest version of current model
ollama pull mistral   # Different model
```

## Uninstall

### Remove Virtual Environment

```bash
# Deactivate first
deactivate

# Remove venv folder
rm -rf venv          # macOS/Linux
rmdir /s venv        # Windows
```

### Remove Ollama

**macOS**:
```bash
brew uninstall ollama
```

**Windows**: Use Control Panel > Programs > Uninstall

**Linux**:
```bash
sudo rm /usr/local/bin/ollama
```

### Clean Up

```bash
# Remove data if desired
rm -rf data/

# Keep code for reinstall
```

## Performance Tuning

### For Faster Responses

```bash
# Use GPU (NVIDIA/AMD)
# Ollama auto-detects, ensure drivers installed

# Use smaller model
ollama pull neural-chat

# Reduce token generation length
# Edit backend/llm_engine.py - adjust prompts
```

### For More Accurate Responses

```bash
# Use larger model
ollama pull llama2-uncensored

# Increase confidence threshold
# Edit backend/.env: CONFIDENCE_THRESHOLD=80
```

### For Better Knowledge Base Matching

```bash
# Add more keywords to each answer
# Edit data/knowledge_base.json
# Expand keywords array for each item

# Add semantically similar terms
"keywords": ["return", "refund", "money back", "send back", "exchange"]
```

## Getting Help

1. **Check logs**:
   ```bash
   tail -f data/support_log.json  # Support escalations
   # Or check terminal where backend is running
   ```

2. **Test API directly**:
   ```bash
   curl http://localhost:8000/health
   ```

3. **Check knowledge base**:
   ```bash
   curl http://localhost:8000/knowledge-base
   ```

4. **Review documentation**:
   - README.md - Full documentation
   - API_EXAMPLES.md - API testing
   - QUICKSTART.md - Quick reference

## What's Next?

Once everything is running:

1. Explore API_EXAMPLES.md for advanced usage
2. Customize knowledge base with your data
3. Test different models in Ollama
4. Monitor support tickets for low-confidence responses
5. Adjust confidence threshold based on your needs
6. Consider production deployment when ready

---

**Congratulations! You should now have a fully functional local AI system!**

For issues, check the troubleshooting section above or review the README.md file.
