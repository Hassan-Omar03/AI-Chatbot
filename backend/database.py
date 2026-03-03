"""
Database module for knowledge base management.
Supports both JSON and SQLite backends.
"""

import json
import sqlite3
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class KnowledgeBase:
    """Base class for knowledge base operations."""
    
    def search(self, query: str) -> Optional[Dict[str, Any]]:
        """Search knowledge base for matching answer."""
        raise NotImplementedError
    
    def add_answer(self, intent: str, answer: str, keywords: List[str]) -> bool:
        """Add new answer to knowledge base."""
        raise NotImplementedError
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Get all answers from knowledge base."""
        raise NotImplementedError


class JSONKnowledgeBase(KnowledgeBase):
    """JSON file-based knowledge base."""
    
    def __init__(self, db_path: str = "./data/knowledge_base.json"):
        self.db_path = db_path
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Create database file if it doesn't exist."""
        os.makedirs(os.path.dirname(self.db_path) or ".", exist_ok=True)
        if not os.path.exists(self.db_path):
            with open(self.db_path, 'w') as f:
                json.dump({"answers": []}, f)
    
    def search(self, query: str) -> Optional[Dict[str, Any]]:
        """Search for best matching answer using whole-word keyword matching."""
        import re
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            query_lower = query.lower().strip()

            best_match = None
            best_score = 0

            for item in data.get("answers", []):
                score = 0
                for keyword in item.get("keywords", []):
                    kw = keyword.lower().strip()
                    # Whole-word / whole-phrase match (not substring)
                    pattern = r'(?<![a-z])' + re.escape(kw) + r'(?![a-z])'
                    if re.search(pattern, query_lower):
                        # Longer keywords = more specific = higher score
                        score += len(kw.split())

                if score > best_score:
                    best_score = score
                    best_match = item

            if best_match and best_score > 0:
                logger.info(f"KB match: '{best_match.get('intent')}' (score={best_score})")
                return best_match

            return None
        except Exception as e:
            logger.error(f"Error searching knowledge base: {e}")
            return None
    
    def add_answer(self, intent: str, answer: str, keywords: List[str]) -> bool:
        """Add new answer to knowledge base."""
        try:
            with open(self.db_path, 'r') as f:
                data = json.load(f)
            
            new_answer = {
                "id": len(data.get("answers", [])) + 1,
                "intent": intent,
                "answer": answer,
                "keywords": keywords
            }
            
            data["answers"].append(new_answer)
            
            with open(self.db_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Added new answer for intent: {intent}")
            return True
        except Exception as e:
            logger.error(f"Error adding answer: {e}")
            return False
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Get all answers from knowledge base."""
        try:
            with open(self.db_path, 'r') as f:
                data = json.load(f)
            return data.get("answers", [])
        except Exception as e:
            logger.error(f"Error retrieving answers: {e}")
            return []


class SQLiteKnowledgeBase(KnowledgeBase):
    """SQLite database-based knowledge base."""
    
    def __init__(self, db_path: str = "./data/knowledge_base.db"):
        self.db_path = db_path
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Create database and tables if they don't exist."""
        os.makedirs(os.path.dirname(self.db_path) or ".", exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                intent TEXT NOT NULL,
                answer TEXT NOT NULL,
                keywords TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def search(self, query: str) -> Optional[Dict[str, Any]]:
        """Search for matching answer by keywords."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query_lower = query.lower()
            cursor.execute("SELECT id, intent, answer, keywords FROM answers")
            
            for row in cursor.fetchall():
                keywords = json.loads(row[3])
                for keyword in keywords:
                    if keyword.lower() in query_lower:
                        logger.info(f"Found matching answer for query: {query}")
                        conn.close()
                        return {
                            "id": row[0],
                            "intent": row[1],
                            "answer": row[2],
                            "keywords": keywords
                        }
            
            conn.close()
            return None
        except Exception as e:
            logger.error(f"Error searching knowledge base: {e}")
            return None
    
    def add_answer(self, intent: str, answer: str, keywords: List[str]) -> bool:
        """Add new answer to knowledge base."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            keywords_json = json.dumps(keywords)
            cursor.execute(
                "INSERT INTO answers (intent, answer, keywords) VALUES (?, ?, ?)",
                (intent, answer, keywords_json)
            )
            
            conn.commit()
            conn.close()
            
            logger.info(f"Added new answer for intent: {intent}")
            return True
        except Exception as e:
            logger.error(f"Error adding answer: {e}")
            return False
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Get all answers from knowledge base."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT id, intent, answer, keywords FROM answers")
            results = []
            
            for row in cursor.fetchall():
                results.append({
                    "id": row[0],
                    "intent": row[1],
                    "answer": row[2],
                    "keywords": json.loads(row[3])
                })
            
            conn.close()
            return results
        except Exception as e:
            logger.error(f"Error retrieving answers: {e}")
            return []


def get_knowledge_base(db_type: str = "json", db_path: str = None) -> KnowledgeBase:
    """Factory function to get appropriate knowledge base instance."""
    if db_type.lower() == "sqlite":
        return SQLiteKnowledgeBase(db_path or "./data/knowledge_base.db")
    else:
        return JSONKnowledgeBase(db_path or "./data/knowledge_base.json")
