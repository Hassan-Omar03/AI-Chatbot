"""
Intent Detection module using NLP.
Detects user intent from messages.
"""

import logging
from typing import Dict, List, Tuple
from dataclasses import dataclass
import re

logger = logging.getLogger(__name__)


@dataclass
class IntentResult:
    """Result from intent detection."""
    intent: str
    confidence: float
    keywords: List[str]


class IntentDetector:
    """Detect user intent from messages."""
    
    # Predefined intents with associated keywords
    INTENTS = {
        "greeting": {
            "keywords": ["hello", "hi", "hey", "greetings", "good morning", "good afternoon"],
            "confidence_boost": 0.9
        },
        "help": {
            "keywords": ["help", "support", "assist", "need help", "can you help"],
            "confidence_boost": 0.85
        },
        "question": {
            "keywords": ["what", "how", "why", "when", "where", "who"],
            "confidence_boost": 0.8
        },
        "complaint": {
            "keywords": ["problem", "issue", "not working", "broken", "error", "bug", "complaint"],
            "confidence_boost": 0.85
        },
        "information_request": {
            "keywords": ["information", "details", "tell me", "explain", "describe"],
            "confidence_boost": 0.8
        },
        "account": {
            "keywords": ["account", "login", "password", "profile", "user"],
            "confidence_boost": 0.85
        },
        "billing": {
            "keywords": ["price", "cost", "payment", "charge", "invoice", "billing"],
            "confidence_boost": 0.85
        },
        "technical": {
            "keywords": ["error", "crash", "lag", "slow", "technical", "system"],
            "confidence_boost": 0.8
        },
        "feedback": {
            "keywords": ["feedback", "suggestion", "improvement", "feature request"],
            "confidence_boost": 0.8
        },
        "goodbye": {
            "keywords": ["goodbye", "bye", "see you", "thanks", "thank you"],
            "confidence_boost": 0.9
        }
    }
    
    def __init__(self):
        self.intents = self.INTENTS
    
    def detect_intent(self, message: str) -> IntentResult:
        """
        Detect intent from user message.
        Returns IntentResult with detected intent and confidence score.
        """
        message_lower = message.lower()
        matched_intents = []
        
        # Score each intent based on keyword matches
        for intent_name, intent_data in self.intents.items():
            keywords = intent_data["keywords"]
            confidence_boost = intent_data["confidence_boost"]
            
            # Count keyword matches
            matched_keywords = []
            for keyword in keywords:
                if keyword in message_lower:
                    matched_keywords.append(keyword)
            
            if matched_keywords:
                # Calculate confidence based on number of matches
                match_score = (len(matched_keywords) / len(keywords))
                confidence = min(confidence_boost, 0.5 + match_score * 0.5) * 100
                
                matched_intents.append({
                    "intent": intent_name,
                    "confidence": confidence,
                    "keywords": matched_keywords
                })
        
        # Return highest confidence match or default
        if matched_intents:
            best_match = max(matched_intents, key=lambda x: x["confidence"])
            logger.info(f"Detected intent: {best_match['intent']} ({best_match['confidence']:.1f}%)")
            
            return IntentResult(
                intent=best_match["intent"],
                confidence=best_match["confidence"],
                keywords=best_match["keywords"]
            )
        else:
            # No specific intent detected
            return IntentResult(
                intent="general",
                confidence=50.0,
                keywords=[]
            )
    
    def extract_keywords(self, message: str) -> List[str]:
        """Extract important keywords from message."""
        # Remove common words
        common_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will", "would",
            "could", "should", "may", "might", "must", "can", "it", "its", "you",
            "your", "i", "my", "we", "our", "they", "them", "that", "this", "these"
        }
        
        # Tokenize message
        words = re.findall(r'\b\w+\b', message.lower())
        
        # Filter out common words and keep only meaningful ones
        keywords = [word for word in words if word not in common_words and len(word) > 2]
        
        return list(set(keywords))  # Return unique keywords
    
    def add_custom_intent(self, intent_name: str, keywords: List[str], confidence_boost: float = 0.8):
        """Add a custom intent at runtime."""
        if intent_name not in self.intents:
            self.intents[intent_name] = {
                "keywords": keywords,
                "confidence_boost": confidence_boost
            }
            logger.info(f"Added custom intent: {intent_name}")
        else:
            logger.warning(f"Intent {intent_name} already exists")
