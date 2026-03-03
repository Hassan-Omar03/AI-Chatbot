"""
FastAPI Backend for Local AI Chat System — FULLY OFFLINE.
Flow: User → Intent Detection → Knowledge Base → Offline NLP → Safety Check → Response
No internet required. No external APIs. All processing is local.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import logging
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# ─── Path Resolution (works in both dev mode and PyInstaller exe) ─────────────
def get_base_dir() -> Path:
    """Get the directory where the exe/script is running from."""
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller exe — use the exe's directory
        return Path(sys.executable).parent
    else:
        # Running as Python script — use the script's parent (backend/)
        return Path(__file__).parent

def get_bundle_dir() -> Path:
    """Get the bundled resources dir (inside the exe or source tree)."""
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    return Path(__file__).parent

BASE_DIR   = get_base_dir()        # Where exe lives / where backend/ is
BUNDLE_DIR = get_bundle_dir()      # Where bundled files are (inside exe)

# DATA_DIR: next to exe when packaged, or ../data/ when in dev (backend/ → project/data/)
if getattr(sys, 'frozen', False):
    DATA_DIR = BASE_DIR / "data"   # exe mode: data/ folder next to exe
else:
    DATA_DIR = BASE_DIR.parent / "data"  # dev mode: go up from backend/ to project root

DATA_DIR.mkdir(exist_ok=True)

# Load .env from same folder as exe/script
env_file = BASE_DIR / ".env"
if not env_file.exists():
    # Try bundle dir (packed inside exe)
    bundled_env = BUNDLE_DIR / ".env.example"
    if bundled_env.exists():
        import shutil
        shutil.copy(bundled_env, env_file)
load_dotenv(env_file)


from llm_engine import LLMFactory
from intent_detector import IntentDetector
from database import get_knowledge_base
from safety import SafetySystem

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# ─── Initialize FastAPI ────────────────────────────────────────────────────────
app = FastAPI(
    title="Local AI Chatbot API",
    description="FastAPI backend with Llama 3 (Ollama), local knowledge base, and safety escalation",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Initialize Components ────────────────────────────────────────────────────
# OFFLINE MODE: Always use offline NLP engine regardless of AI_PROVIDER setting.
# This guarantees the system works with zero internet dependency.
ai_provider = os.getenv("AI_PROVIDER", "offline").lower()

if ai_provider == "ollama":
    # Try Ollama — if unavailable, auto-falls-back to offline NLP
    llm_engine = LLMFactory.create_engine(
        engine_type="ollama",
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        model=os.getenv("OLLAMA_MODEL", "llama3")
    )
else:
    # offline or groq → always use fully offline NLP engine
    llm_engine = LLMFactory.create_engine(engine_type="offline")

intent_detector = IntentDetector()

# Always resolve DB path relative to where the exe/script lives
db_path = str(DATA_DIR / "knowledge_base.json")

knowledge_base = get_knowledge_base(
    db_type=os.getenv("DB_TYPE", "json"),
    db_path=db_path
)


safety_system = SafetySystem(
    log_file=str(DATA_DIR / "support_log.json"),
    threshold=float(os.getenv("CONFIDENCE_THRESHOLD", "70")),
    support_email=os.getenv("SUPPORT_EMAIL", "support@company.com"),
    support_phone=os.getenv("SUPPORT_PHONE", "1-800-COMPANY")
)

logger.info(f"✅ LLM Engine: {llm_engine.model} | Available: {llm_engine.is_available}")
logger.info(f"✅ Knowledge Base: {db_path}")
logger.info(f"✅ Confidence Threshold: {safety_system.threshold}%")


# ─── Pydantic Models ──────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = "anonymous"
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    confidence: float
    intent: str
    source: str          # "knowledge_base" | "llm" | "support"
    ticket_id: Optional[str] = None
    support_contact: Optional[dict] = None


class HealthResponse(BaseModel):
    status: str
    ollama_available: bool
    knowledge_base_ready: bool
    model: str
    kb_entries: int
    offline_mode: bool = True


class SupportTicketRequest(BaseModel):
    user_message: str
    user_id: Optional[str] = "anonymous"
    reason: str = "manual_escalation"


class KnowledgeBaseItem(BaseModel):
    intent: str
    answer: str
    keywords: List[str]


# ─── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/", tags=["Info"])
async def root():
    """API overview with all available endpoints."""
    return {
        "name": "Local AI Chatbot API",
        "version": "2.0.0",
        "model": llm_engine.model,
        "endpoints": {
            "POST /chat": "Send a message and get AI response",
            "GET  /health": "System health check",
            "GET  /knowledge-base": "List all KB entries",
            "POST /knowledge-base/add": "Add new KB entry",
            "POST /support-trigger": "Manually create support ticket",
            "GET  /support/tickets": "List recent support tickets",
            "GET  /support/stats": "Safety system statistics",
            "GET  /docs": "Interactive Swagger API docs"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Health check — offline mode: always healthy, no external deps."""
    kb_items = knowledge_base.get_all()

    return HealthResponse(
        status="healthy",
        ollama_available=llm_engine.is_available,
        knowledge_base_ready=True,
        model=llm_engine.model,
        kb_entries=len(kb_items),
        offline_mode=True
    )


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    """
    Main chat endpoint — the full pipeline:
    1. Validate input
    2. Detect intent via NLP
    3. Search knowledge base (instant, confident answers)
    4. Call Llama 3 via Ollama if KB has no match
    5. Safety check: if confidence < threshold → escalate to support
    6. Return structured response
    """
    user_message = request.message.strip()

    if not user_message:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    if len(user_message) > 2000:
        raise HTTPException(status_code=400, detail="Message too long (max 2000 characters).")

    logger.info(f"[{request.user_id}] Message: {user_message[:80]}...")

    # Step 1: Detect intent
    intent_result = intent_detector.detect_intent(user_message)
    logger.info(f"Intent: {intent_result.intent} ({intent_result.confidence:.1f}%)")

    # Step 2: Knowledge base lookup (high-confidence, no LLM needed)
    kb_answer = knowledge_base.search(user_message)
    if kb_answer:
        logger.info(f"KB hit: {kb_answer.get('intent', 'unknown')}")
        return ChatResponse(
            response=kb_answer["answer"],
            confidence=100.0,
            intent=kb_answer.get("intent", intent_result.intent),
            source="knowledge_base"
        )

    # Step 3: Generate response via LLM (Groq or Ollama)
    llm_response = llm_engine.generate_response(user_message)

    # Step 4: Handle LLM failure
    if not llm_response.is_success:
        # Offline / KB-only mode — give a helpful message without escalating
        logger.warning(f"LLM unavailable — responding in KB-only mode")
        return ChatResponse(
            response=(
                "I can only answer questions from my knowledge base right now. "
                "I don't have a specific answer for that question.\n\n"
                "Try asking about: **pricing**, **accounts**, **features**, "
                "**security**, **API**, or **support contact**.\n\n"
                "If you need further help, please contact our support team."
            ),
            confidence=50.0,
            intent=intent_result.intent,
            source="knowledge_base"
        )

    # Step 5: Safety confidence check
    eval_result = safety_system.evaluate_confidence(llm_response.confidence, llm_response.text)

    if eval_result["requires_escalation"]:
        ticket = safety_system.trigger_support(
            user_message=user_message,
            ai_response=llm_response.text,
            confidence_score=llm_response.confidence,
            intent=intent_result.intent,
            reason="low_confidence"
        )
        logger.warning(f"Low confidence ({llm_response.confidence:.1f}%) — ticket: {ticket.id}")
        return ChatResponse(
            response=safety_system.get_support_message(ticket.id),
            confidence=llm_response.confidence,
            intent=intent_result.intent,
            source="support",
            ticket_id=ticket.id,
            support_contact=safety_system.get_contact_info()
        )

    # Step 6: Return confident LLM response
    logger.info(f"LLM response delivered — confidence: {llm_response.confidence:.1f}%")
    return ChatResponse(
        response=llm_response.text,
        confidence=llm_response.confidence,
        intent=intent_result.intent,
        source="llm"
    )


@app.post("/support-trigger", tags=["Support"])
async def trigger_support(request: SupportTicketRequest):
    """Manually create a support escalation ticket."""
    ticket = safety_system.trigger_support(
        user_message=request.user_message,
        ai_response="",
        confidence_score=0.0,
        intent="manual_support_request",
        reason=request.reason
    )
    return {
        "ticket_id": ticket.id,
        "message": safety_system.get_support_message(ticket.id),
        "timestamp": ticket.timestamp,
        "contact": safety_system.get_contact_info()
    }


@app.get("/support/tickets", tags=["Support"])
async def get_support_tickets(limit: int = 20):
    """Get recent support tickets."""
    tickets = safety_system.get_tickets(limit=limit)
    return {"tickets": tickets, "total": len(tickets)}


@app.get("/support/stats", tags=["Support"])
async def get_support_stats():
    """Get safety system escalation statistics."""
    return safety_system.get_stats()


@app.get("/knowledge-base", tags=["Knowledge Base"])
async def list_knowledge_base():
    """List all knowledge base entries."""
    items = knowledge_base.get_all()
    return {"items": items, "total": len(items)}


@app.post("/knowledge-base/add", tags=["Knowledge Base"])
async def add_knowledge_base_item(item: KnowledgeBaseItem):
    """Add a new answer to the knowledge base."""
    success = knowledge_base.add_answer(
        intent=item.intent,
        answer=item.answer,
        keywords=item.keywords
    )
    if success:
        return {"status": "success", "message": f"Added entry for intent: {item.intent}"}
    raise HTTPException(status_code=500, detail="Failed to add entry to knowledge base.")


# ─── Entry Point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import asyncio
    import multiprocessing
    import uvicorn
    from uvicorn import Config, Server

    # Required for PyInstaller to support multiprocessing
    multiprocessing.freeze_support()

    host = os.getenv("SERVER_HOST", "127.0.0.1")
    port = int(os.getenv("SERVER_PORT", "8000"))

    logger.info(f"🚀 Starting Local AI Chatbot API on http://{host}:{port}")
    logger.info(f"📚 Swagger Docs: http://{host}:{port}/docs")

    # ── PyInstaller-compatible uvicorn startup ─────────────────────────────────
    # DO NOT use uvicorn.run("main:app", ...) — broken inside frozen exe
    # Use Config+Server+asyncio pattern instead — works in both dev and exe mode
    config = Config(
        app=app,          # pass app object directly, not "main:app" string
        host=host,
        port=port,
        reload=False,
        log_level=os.getenv("LOG_LEVEL", "info").lower(),
        access_log=True,
    )
    server = Server(config=config)
    asyncio.run(server.serve())
