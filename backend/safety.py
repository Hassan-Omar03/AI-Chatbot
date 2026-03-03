"""
Safety System — handles low-confidence responses and support escalation.
Logs all escalations and provides contact info to users.
"""

import logging
import json
import os
import random
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class SupportTicket:
    """A logged escalation ticket."""
    id: str
    timestamp: str
    user_message: str
    ai_response: str
    confidence_score: float
    intent: str
    reason: str   # "low_confidence" | "llm_unavailable" | "manual_escalation"


class SafetySystem:
    """
    Monitors AI confidence and escalates to human support when needed.
    All escalations are logged to a JSON file for audit and review.
    """

    def __init__(
        self,
        log_file: str = "./data/support_log.json",
        threshold: float = 70.0,
        support_email: str = "support@company.com",
        support_phone: str = "1-800-COMPANY"
    ):
        self.log_file = log_file
        self.threshold = threshold
        self.support_email = support_email
        self.support_phone = support_phone
        self._ensure_log_exists()

    def _ensure_log_exists(self):
        """Create the log file if it doesn't exist."""
        os.makedirs(os.path.dirname(self.log_file) or ".", exist_ok=True)
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                json.dump({"tickets": [], "total_escalations": 0}, f, indent=2)

    def evaluate_confidence(self, llm_confidence: float, response_text: str) -> Dict[str, Any]:
        """
        Check if confidence meets the threshold.
        Returns a dict with escalation decision.
        """
        below_threshold = llm_confidence < self.threshold
        if below_threshold:
            logger.warning(
                f"Confidence {llm_confidence:.1f}% is below threshold {self.threshold}% — escalating"
            )
        return {
            "is_confident": not below_threshold,
            "confidence_score": llm_confidence,
            "threshold": self.threshold,
            "requires_escalation": below_threshold
        }

    def trigger_support(
        self,
        user_message: str,
        ai_response: str,
        confidence_score: float,
        intent: str,
        reason: str = "low_confidence"
    ) -> SupportTicket:
        """
        Create and log a support escalation ticket.
        Returns the created SupportTicket.
        """
        ticket = SupportTicket(
            id=self._generate_ticket_id(),
            timestamp=datetime.now().isoformat(),
            user_message=user_message,
            ai_response=ai_response,
            confidence_score=confidence_score,
            intent=intent,
            reason=reason
        )
        self._log_ticket(ticket)
        logger.info(f"🎫 Support ticket created: {ticket.id} (reason: {reason})")
        return ticket

    def _generate_ticket_id(self) -> str:
        """Generate a unique human-readable ticket ID."""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        suffix = random.randint(1000, 9999)
        return f"TKT-{timestamp}-{suffix}"

    def _log_ticket(self, ticket: SupportTicket):
        """Write ticket to the JSON log file."""
        try:
            with open(self.log_file, "r") as f:
                data = json.load(f)
            data["tickets"].append(asdict(ticket))
            data["total_escalations"] = len(data["tickets"])
            with open(self.log_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to log support ticket: {e}")

    def get_support_message(self, ticket_id: Optional[str] = None) -> str:
        """
        Return a user-friendly escalation message with ticket ID and contact info.
        """
        base = (
            "I'm not confident enough to give you a reliable answer to that question.\n\n"
            "Here's how to get help from our support team:\n"
            f"📧 Email: {self.support_email}\n"
            f"📞 Phone: {self.support_phone}\n"
        )
        if ticket_id:
            base += f"\nYour support ticket has been created automatically.\n🎫 Ticket ID: **{ticket_id}**\n"
            base += "Please keep this ID for reference — our team will respond shortly."
        else:
            base += "\nPlease contact us and describe your issue."
        return base

    def get_contact_info(self) -> Dict[str, str]:
        """Return support contact info as a structured dict."""
        return {
            "email": self.support_email,
            "phone": self.support_phone
        }

    def get_tickets(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retrieve logged support tickets (most recent first)."""
        try:
            with open(self.log_file, "r") as f:
                data = json.load(f)
            tickets = data.get("tickets", [])
            tickets_sorted = list(reversed(tickets))  # most recent first
            return tickets_sorted[:limit] if limit else tickets_sorted
        except Exception as e:
            logger.error(f"Error reading tickets: {e}")
            return []

    def get_stats(self) -> Dict[str, Any]:
        """Return escalation statistics."""
        try:
            with open(self.log_file, "r") as f:
                data = json.load(f)
            tickets = data.get("tickets", [])
            if not tickets:
                return {
                    "total_escalations": 0,
                    "escalations_by_reason": {},
                    "average_confidence": 0.0,
                    "most_common_intent": None
                }

            reasons: Dict[str, int] = {}
            intents: Dict[str, int] = {}
            total_conf = 0.0

            for t in tickets:
                reason = t.get("reason", "unknown")
                intent = t.get("intent", "unknown")
                reasons[reason] = reasons.get(reason, 0) + 1
                intents[intent] = intents.get(intent, 0) + 1
                total_conf += t.get("confidence_score", 0.0)

            most_common_intent = max(intents, key=intents.get) if intents else None

            return {
                "total_escalations": len(tickets),
                "escalations_by_reason": reasons,
                "average_confidence": round(total_conf / len(tickets), 2),
                "most_common_intent": most_common_intent,
                "intents_breakdown": intents
            }
        except Exception as e:
            logger.error(f"Error calculating stats: {e}")
            return {"total_escalations": 0, "escalations_by_reason": {}, "average_confidence": 0.0}
