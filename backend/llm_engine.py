"""
LLM Engine — FULLY OFFLINE version.
Uses a built-in smart NLP engine with:
  - TF-IDF cosine similarity (pure Python, no external libs)
  - Rule-based pattern matching
  - Rich knowledge-driven response templates
  - Zero internet dependency
"""

import re
import math
import logging
import os
from typing import Optional, Dict, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    """Unified response from any LLM engine."""
    text: str
    confidence: float
    model: str
    is_success: bool


# ─── Offline NLP Engine ───────────────────────────────────────────────────────

SYSTEM_PROMPT = ""  # Not used in offline mode

DEFAULT_CONFIDENCE = 75.0


class OfflineNLPEngine:
    """
    Fully offline NLP engine.
    Uses TF-IDF cosine similarity + rule patterns + response templates.
    No internet. No Ollama. No external APIs whatsoever.
    """

    MODEL_NAME = "offline-nlp-v2"

    # ── Built-in response library ─────────────────────────────────────────────
    RESPONSES: List[Dict] = [
        # Greetings
        {
            "patterns": [r"\bhello\b", r"\bhi\b", r"\bhey\b", r"\bgreetings\b",
                         r"\bgood\s+(morning|afternoon|evening|day)\b", r"\bwhat'?s\s+up\b"],
            "response": (
                "Hello! 👋 Welcome! I'm your AI assistant, ready to help you.\n\n"
                "You can ask me about:\n"
                "• **Services & Features** — what we offer and how it works\n"
                "• **Pricing & Plans** — costs, subscriptions, billing\n"
                "• **Account Help** — login, password, profile settings\n"
                "• **Technical Support** — troubleshooting and errors\n"
                "• **FAQs** — common questions answered instantly\n\n"
                "What can I help you with today?"
            ),
            "confidence": 98.0,
            "intent": "greeting"
        },
        # How are you
        {
            "patterns": [r"\bhow\s+are\s+you\b", r"\bhow'?s\s+it\s+going\b", r"\byou\s+okay\b"],
            "response": (
                "I'm doing great, thank you for asking! 😊\n\n"
                "I'm fully operational and ready to assist you. "
                "What would you like to know today?"
            ),
            "confidence": 97.0,
            "intent": "greeting"
        },
        # What are you / who are you
        {
            "patterns": [r"\bwho\s+are\s+you\b", r"\bwhat\s+are\s+you\b",
                         r"\btell\s+me\s+about\s+yourself\b", r"\byour\s+name\b"],
            "response": (
                "I'm an **AI Assistant** — a smart offline chatbot designed to help you instantly.\n\n"
                "🤖 **What I do:**\n"
                "• Answer your questions immediately from a local knowledge base\n"
                "• Handle FAQs, services info, pricing, and account help\n"
                "• Work 100% offline — no internet required\n"
                "• Escalate complex issues to human support when needed\n\n"
                "Ask me anything and I'll do my best to help!"
            ),
            "confidence": 96.0,
            "intent": "information_request"
        },
        # Pricing / cost / how much
        {
            "patterns": [r"\bpric(e|ing|es)\b", r"\bcost\b", r"\bhow\s+much\b",
                         r"\bfee\b", r"\bcharge\b", r"\bplan(s)?\b", r"\bsubscri(be|ption)\b"],
            "response": (
                "Here's an overview of our pricing options:\n\n"
                "💰 **Free Tier** — $0/month\n"
                "• Basic features, up to 100 requests/day\n"
                "• Community support\n\n"
                "🚀 **Pro Plan** — $29/month\n"
                "• Unlimited requests\n"
                "• Priority support\n"
                "• Advanced analytics\n\n"
                "🏢 **Enterprise** — Custom pricing\n"
                "• Dedicated infrastructure\n"
                "• SLA guarantees\n"
                "• 24/7 dedicated support team\n\n"
                "Would you like more details about any specific plan?"
            ),
            "confidence": 91.0,
            "intent": "billing"
        },
        # Payment / invoice / billing issue
        {
            "patterns": [r"\bpayment\b", r"\binvoice\b", r"\bbilling\b",
                         r"\brefund\b", r"\bcharg(e|ed)\b", r"\btransaction\b"],
            "response": (
                "For billing and payment inquiries:\n\n"
                "📋 **Common Billing Questions:**\n"
                "• **Payment methods:** Credit/debit cards, PayPal, bank transfer\n"
                "• **Billing cycle:** Monthly or annually (15% discount on annual)\n"
                "• **Invoices:** Available in your account dashboard under Billing\n"
                "• **Refunds:** 30-day money-back guarantee on all plans\n\n"
                "If you have a specific billing issue, our support team is happy to help. "
                "Type **'contact support'** to reach them."
            ),
            "confidence": 90.0,
            "intent": "billing"
        },
        # Account / login / password
        {
            "patterns": [r"\baccount\b", r"\blogin\b", r"\bsign\s*(in|up)\b",
                         r"\bpassword\b", r"\bforgot\b", r"\bregist(er|ration)\b",
                         r"\bprofile\b", r"\buser(name)?\b"],
            "response": (
                "Here's help with account management:\n\n"
                "🔐 **Account Help:**\n"
                "• **Forgot password?** Click 'Forgot Password' on the login page\n"
                "• **Can't sign in?** Clear browser cache and try again\n"
                "• **New account:** Click 'Sign Up' on our homepage\n"
                "• **Update profile:** Go to Settings → Profile in your dashboard\n"
                "• **Delete account:** Contact support — we'll process it within 24h\n\n"
                "Still having trouble? Type **'contact support'** for personal assistance."
            ),
            "confidence": 92.0,
            "intent": "account"
        },
        # Features / what can you do / capabilities
        {
            "patterns": [r"\bfeature(s)?\b", r"\bcapabilit(y|ies)\b", r"\bwhat\s+can\b",
                         r"\bfunction(s|ality)?\b", r"\bservice(s)?\b", r"\boff?er\b"],
            "response": (
                "Here's what our system offers:\n\n"
                "✨ **Core Features:**\n"
                "• 🤖 AI-powered customer support — 24/7 instant responses\n"
                "• 📚 Smart knowledge base — thousands of FAQ answers\n"
                "• 🔒 Offline operation — works without internet\n"
                "• 📊 Analytics dashboard — track usage and performance\n"
                "• 🎫 Support ticketing — escalate complex issues automatically\n"
                "• 🔗 API access — integrate with your existing systems\n\n"
                "Would you like details about any specific feature?"
            ),
            "confidence": 90.0,
            "intent": "information_request"
        },
        # Technical error / not working / broken
        {
            "patterns": [r"\berror\b", r"\bnot\s+work(ing)?\b", r"\bbroken\b",
                         r"\bbug\b", r"\bcrash\b", r"\bissue\b", r"\bproblem\b",
                         r"\bfail(ing|ed)?\b", r"\btrouble(shoot)?\b"],
            "response": (
                "I'm sorry you're experiencing an issue! Let me help troubleshoot.\n\n"
                "🔧 **Quick Fixes to Try:**\n"
                "1. **Refresh** the page or restart the application\n"
                "2. **Clear browser cache** (Ctrl+Shift+Delete)\n"
                "3. **Check your connection** — ensure you're connected\n"
                "4. **Try a different browser** — Chrome, Firefox, Edge\n"
                "5. **Disable browser extensions** temporarily\n\n"
                "📋 **If the issue persists:**\n"
                "Please note down:\n"
                "• What exactly happened (error message if any)\n"
                "• When it started\n"
                "• What you were doing\n\n"
                "Type **'contact support'** to submit a ticket with these details."
            ),
            "confidence": 87.0,
            "intent": "technical"
        },
        # Security / privacy / data
        {
            "patterns": [r"\bsecur(e|ity|ity)\b", r"\bprivacy\b", r"\bdata\b",
                         r"\bencrypt(ed|ion)?\b", r"\bsafe\b", r"\bprotect\b", r"\bGDPR\b"],
            "response": (
                "Your security is our top priority. Here's what we do:\n\n"
                "🔒 **Security Measures:**\n"
                "• **End-to-end encryption** — all data encrypted in transit (TLS 1.3)\n"
                "• **At-rest encryption** — data stored with AES-256 encryption\n"
                "• **GDPR compliant** — full data privacy compliance\n"
                "• **2FA support** — two-factor authentication available\n"
                "• **No third-party sharing** — your data stays private\n"
                "• **Regular audits** — quarterly security assessments\n\n"
                "For our full Privacy Policy, visit Settings → Privacy in your dashboard."
            ),
            "confidence": 90.0,
            "intent": "information_request"
        },
        # API / integration / developer
        {
            "patterns": [r"\bapi\b", r"\bintegrat(e|ion)\b", r"\bdeveloper\b",
                         r"\bwebhook\b", r"\bendpoint\b", r"\brest\b", r"\bsdk\b"],
            "response": (
                "Here's our API information for developers:\n\n"
                "⚙️ **API Overview:**\n"
                "• **REST API** — full CRUD operations via HTTP/HTTPS\n"
                "• **Authentication** — API key or OAuth 2.0\n"
                "• **Rate limits** — 1,000 req/min (Pro), unlimited (Enterprise)\n"
                "• **Formats** — JSON request/response\n"
                "• **Webhooks** — real-time event notifications\n\n"
                "📚 **Documentation:** Available at `/docs` in your dashboard\n\n"
                "Need an API key? Go to Settings → API → Generate Key."
            ),
            "confidence": 88.0,
            "intent": "technical"
        },
        # Contact / talk to human / support team
        {
            "patterns": [r"\bcontact\b", r"\btalk\s+to\s+(a\s+)?(human|person|agent|someone)\b",
                         r"\bsupport\s+team\b", r"\breal\s+person\b", r"\blive\s+(chat|agent)\b",
                         r"\bspeak\s+(to|with)\b", r"\beach\s+out\b"],
            "response": (
                "I'll connect you with our support team right away! 🙋\n\n"
                "📞 **Contact Options:**\n"
                "• 📧 **Email:** support@yourcompany.com\n"
                "• 📞 **Phone:** 1-800-YOUR-NUMBER\n"
                "• 💬 **Live Chat:** Available Mon-Fri, 9AM-6PM EST\n\n"
                "⏰ **Response Times:**\n"
                "• Email: Within 24 hours\n"
                "• Phone: Immediate during business hours\n"
                "• Tickets: Within 4 hours for Pro/Enterprise\n\n"
                "Your question has been noted and a ticket will be created if needed."
            ),
            "confidence": 95.0,
            "intent": "help"
        },
        # Hours / availability / when are you open
        {
            "patterns": [r"\bhours\b", r"\bopen\b", r"\bavailable\b",
                         r"\bwhen\b.*\bsupport\b", r"\boffice\s+hours\b", r"\bbusiness\s+hours\b"],
            "response": (
                "Here are our availability hours:\n\n"
                "🕘 **Support Hours:**\n"
                "• **Monday – Friday:** 9:00 AM – 6:00 PM EST\n"
                "• **Saturday:** 10:00 AM – 2:00 PM EST\n"
                "• **Sunday:** Closed\n\n"
                "🤖 **AI Chatbot (that's me!):** Available 24/7, 365 days\n\n"
                "For urgent issues outside business hours, email us and mark it **URGENT** — "
                "our on-call team monitors critical issues."
            ),
            "confidence": 90.0,
            "intent": "information_request"
        },
        # Thank you / thanks
        {
            "patterns": [r"\bthank(s| you)\b", r"\bappreciat(e|ion)\b",
                         r"\bawesome\b", r"\bgreat\b.*\bhelp\b", r"\bperfect\b"],
            "response": (
                "You're very welcome! 😊 It was my pleasure to help.\n\n"
                "Is there anything else I can assist you with? "
                "I'm always here whenever you need me!"
            ),
            "confidence": 97.0,
            "intent": "goodbye"
        },
        # Goodbye / bye
        {
            "patterns": [r"\bbye\b", r"\bgoodbye\b", r"\bsee\s+you\b",
                         r"\btake\s+care\b", r"\bfarewell\b", r"\bciao\b"],
            "response": (
                "Goodbye! 👋 Have a wonderful day!\n\n"
                "Don't hesitate to come back if you ever need help. "
                "I'm available 24/7 whenever you need assistance. Take care! 😊"
            ),
            "confidence": 97.0,
            "intent": "goodbye"
        },
        # What is this / about
        {
            "patterns": [r"\bwhat\s+is\s+this\b", r"\babout\s+this\b",
                         r"\btelll?\s+more\b", r"\bmore\s+info\b", r"\blearn\s+more\b"],
            "response": (
                "This is an **AI-powered support chatbot** built for instant, accurate answers!\n\n"
                "🌟 **Key Points:**\n"
                "• Runs **100% offline** — no internet required\n"
                "• Answers instantly from a local knowledge base\n"
                "• Smart escalation to human support when unsure\n"
                "• Fast, secure, and private — your data never leaves this system\n\n"
                "Just type your question and I'll help right away!"
            ),
            "confidence": 93.0,
            "intent": "information_request"
        },
        # How does it work
        {
            "patterns": [r"\bhow\s+(does\s+it|do\s+you|does\s+this)\s+work\b",
                         r"\bexplain\b", r"\bprocess\b", r"\bhow\s+is\b.*\bhandled\b"],
            "response": (
                "Here's how I work under the hood:\n\n"
                "⚡ **My Response Pipeline:**\n"
                "1. 📥 **Receive** your message\n"
                "2. 🔍 **Analyze** intent and keywords (offline NLP)\n"
                "3. 📚 **Search** the local knowledge base first\n"
                "4. 🤖 **Generate** a response if not in knowledge base\n"
                "5. 📊 **Evaluate** confidence score\n"
                "6. 🎫 **Escalate** to human support if confidence is low\n\n"
                "Everything runs locally — no data sent to any cloud server!"
            ),
            "confidence": 91.0,
            "intent": "information_request"
        },
        # Offline / no internet
        {
            "patterns": [r"\boffline\b", r"\bno\s+internet\b", r"\bwithout\s+internet\b",
                         r"\blocal\b", r"\binternet\s+(connection|required)\b"],
            "response": (
                "Yes! I work **100% offline** — that's one of my key features! 🎉\n\n"
                "✅ **What works offline:**\n"
                "• All chat responses and knowledge base lookups\n"
                "• Support ticket logging\n"
                "• Intent detection and NLP processing\n"
                "• All API endpoints\n\n"
                "❌ **Only these need internet (if configured):**\n"
                "• Sending email notifications for support tickets\n"
                "• Syncing with cloud backup (optional)\n\n"
                "The core chat system runs entirely on your local machine!"
            ),
            "confidence": 95.0,
            "intent": "information_request"
        },
    ]

    def __init__(self):
        self.is_available = True
        self.model = self.MODEL_NAME
        logger.info("✅ Offline NLP Engine initialized — fully local, no internet required")

    def _check_availability(self) -> bool:
        return True  # Always available — no external dependency

    def generate_response(self, prompt: str) -> LLMResponse:
        """
        Generate a response using offline NLP:
        1. Rule-based pattern matching (fast, exact)
        2. TF-IDF cosine similarity (semantic matching)
        3. Fallback response
        """
        prompt_clean = prompt.strip()
        if not prompt_clean:
            return LLMResponse(
                text="Please type a message and I'll be happy to help!",
                confidence=85.0,
                model=self.model,
                is_success=True
            )

        # Step 1: Try rule-based pattern matching
        result = self._match_patterns(prompt_clean)
        if result:
            return LLMResponse(
                text=result["response"],
                confidence=result["confidence"],
                model=self.model,
                is_success=True
            )

        # Step 2: TF-IDF cosine similarity across all response triggers
        result = self._tfidf_match(prompt_clean)
        if result and result["confidence"] >= 55.0:
            return LLMResponse(
                text=result["response"],
                confidence=result["confidence"],
                model=self.model,
                is_success=True
            )

        # Step 3: Fallback — helpful but honest message
        return LLMResponse(
            text=self._fallback_response(prompt_clean),
            confidence=45.0,
            model=self.model,
            is_success=True
        )

    def _match_patterns(self, text: str) -> Optional[Dict]:
        """Try exact regex pattern matching."""
        text_lower = text.lower()
        for entry in self.RESPONSES:
            for pattern in entry["patterns"]:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    return entry
        return None

    def _tfidf_match(self, query: str) -> Optional[Dict]:
        """TF-IDF cosine similarity matching (pure Python, no libraries)."""
        # Build corpus from pattern triggers
        corpus_items = []
        for entry in self.RESPONSES:
            # Combine all patterns as a pseudo-document
            doc_text = " ".join(entry["patterns"])
            # Also add the intent as extra weight
            doc_text += " " + entry.get("intent", "")
            corpus_items.append((doc_text, entry))

        query_tokens = self._tokenize(query)
        if not query_tokens:
            return None

        # Compute TF-IDF
        all_docs = [self._tokenize(item[0]) for item in corpus_items]
        vocab = list(set(t for doc in all_docs for t in doc) | set(query_tokens))

        def tf(tokens: List[str], term: str) -> float:
            return tokens.count(term) / len(tokens) if tokens else 0.0

        def idf(term: str) -> float:
            containing = sum(1 for doc in all_docs if term in doc)
            return math.log((len(all_docs) + 1) / (containing + 1)) + 1.0

        idf_cache = {term: idf(term) for term in vocab}

        def tfidf_vector(tokens: List[str]) -> Dict[str, float]:
            return {term: tf(tokens, term) * idf_cache[term] for term in vocab}

        def cosine_sim(v1: Dict[str, float], v2: Dict[str, float]) -> float:
            dot = sum(v1.get(t, 0) * v2.get(t, 0) for t in vocab)
            mag1 = math.sqrt(sum(v ** 2 for v in v1.values()))
            mag2 = math.sqrt(sum(v ** 2 for v in v2.values()))
            return dot / (mag1 * mag2) if (mag1 * mag2) > 0 else 0.0

        query_vec = tfidf_vector(query_tokens)

        best_score = 0.0
        best_entry = None
        for i, (doc_text, entry) in enumerate(corpus_items):
            doc_vec = tfidf_vector(all_docs[i])
            score = cosine_sim(query_vec, doc_vec)
            if score > best_score:
                best_score = score
                best_entry = entry

        if best_entry and best_score > 0.05:
            # Scale to 55-85 confidence range
            confidence = min(85.0, 55.0 + best_score * 150.0)
            return {
                "response": best_entry["response"],
                "confidence": confidence,
                "intent": best_entry.get("intent", "general")
            }
        return None

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenizer — lowercase, remove punctuation, split."""
        text = re.sub(r'[\\()?*+^${}|\[\]]', ' ', text.lower())
        text = re.sub(r'[^\w\s]', ' ', text)
        stopwords = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to",
            "for", "of", "with", "by", "from", "is", "are", "was", "were",
            "be", "been", "have", "has", "do", "does", "it", "its", "you",
            "your", "i", "we", "they", "this", "that", "b", "s", "d", "w"
        }
        return [w for w in text.split() if w not in stopwords and len(w) > 1]

    def _fallback_response(self, query: str) -> str:
        """Generate a helpful fallback response."""
        query_short = query[:100] + ("..." if len(query) > 100 else "")
        return (
            f"I appreciate your question! I want to make sure I give you the right answer.\n\n"
            f"I don't have a specific answer for: *\"{query_short}\"*\n\n"
            f"Here's what I can help with:\n"
            f"• **Pricing & Plans** — type 'pricing'\n"
            f"• **Account help** — type 'account'\n"
            f"• **Technical support** — type 'technical issue'\n"
            f"• **Features** — type 'features'\n"
            f"• **Contact support** — type 'contact support'\n\n"
            f"Or if you'd like to speak with a person, type **'talk to support'** and I'll "
            f"create a ticket for you right away!"
        )


# ─── Groq Cloud Engine (kept for reference but NOT used in offline mode) ──────
class GroqEngine:
    """
    Cloud Groq engine — requires internet.
    NOT used in offline mode. Stub only.
    """
    GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

    def __init__(self, api_key: str, model: str = "llama3-70b-8192"):
        self.api_key = api_key
        self.model = model
        self.is_available = False  # Force disabled — use offline mode
        logger.warning("⚠️  Groq engine created but disabled — system is in OFFLINE mode")

    def _check_availability(self) -> bool:
        return False

    def generate_response(self, prompt: str) -> LLMResponse:
        return LLMResponse(
            text="Cloud AI is disabled. Using offline mode.",
            confidence=0.0,
            model=self.model,
            is_success=False
        )


# ─── Ollama Local Engine (kept for reference) ─────────────────────────────────
class OllamaEngine:
    """Ollama local engine — requires Ollama installation."""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3"):
        import requests as _req
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._requests = _req
        self.is_available = self._check_availability()

    def _check_availability(self) -> bool:
        try:
            r = self._requests.get(f"{self.base_url}/api/tags", timeout=3)
            if r.status_code == 200:
                logger.info(f"✅ Ollama running at {self.base_url}")
                return True
        except Exception:
            pass
        logger.warning(f"⚠️  Ollama not available at {self.base_url} — using offline NLP fallback")
        return False

    def generate_response(self, prompt: str) -> LLMResponse:
        if not self.is_available:
            # Fall back to offline engine automatically
            offline = OfflineNLPEngine()
            return offline.generate_response(prompt)
        try:
            payload = {
                "model": self.model,
                "prompt": f"You are a helpful assistant. Answer clearly and concisely.\n\nUser: {prompt}",
                "stream": False
            }
            r = self._requests.post(f"{self.base_url}/api/generate", json=payload, timeout=60)
            if r.status_code == 200:
                raw = r.json().get("response", "")
                return LLMResponse(
                    text=raw.strip(),
                    confidence=82.0,
                    model=self.model,
                    is_success=True
                )
        except Exception as e:
            logger.error(f"Ollama error: {e}")
        # Fall back to offline
        offline = OfflineNLPEngine()
        return offline.generate_response(prompt)

    def _extract_confidence(self, text: str) -> float:
        match = re.search(r'confidence[\s:]+(\d+)', text, re.IGNORECASE)
        if match:
            return min(100.0, float(match.group(1)))
        return DEFAULT_CONFIDENCE

    def _clean_text(self, text: str) -> str:
        if "CONFIDENCE:" in text.upper():
            return text.split("CONFIDENCE:")[0].strip()
        return text.strip()


# ─── Factory ──────────────────────────────────────────────────────────────────
class LLMFactory:
    """Creates the right LLM engine based on config."""

    @staticmethod
    def create_engine(engine_type: str = "offline", **kwargs):
        """
        engine_type: "offline" (recommended), "ollama", or "groq"
        """
        et = engine_type.lower()

        if et == "offline":
            return OfflineNLPEngine()

        elif et == "ollama":
            engine = OllamaEngine(
                base_url=kwargs.get("base_url", "http://localhost:11434"),
                model=kwargs.get("model", "llama3")
            )
            # If Ollama is not available, seamlessly downgrade to offline
            if not engine.is_available:
                logger.info("↩️  Ollama unavailable — falling back to offline NLP engine")
                return OfflineNLPEngine()
            return engine

        elif et == "groq":
            # In offline mode, ignore Groq and use offline engine
            logger.info("ℹ️  Groq requested but OFFLINE mode active — using offline NLP engine")
            return OfflineNLPEngine()

        else:
            logger.warning(f"Unknown engine type '{engine_type}' — using offline NLP engine")
            return OfflineNLPEngine()
