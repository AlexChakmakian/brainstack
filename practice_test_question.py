"""
BrainStack - Practice Test Question Class
Represents a single question in a practice test.
"""

import uuid
import re
from difflib import SequenceMatcher
from typing import Optional, Dict, Any


class PracticeTestQuestion:
    """Represents a single question in a practice test."""
    
    def __init__(self, question_id: Optional[str] = None, question: str = "", 
                 correct_answer: str = "", user_answer: Optional[str] = None,
                 is_correct: Optional[bool] = None):
        """
        Initialize a practice test question.
        
        Args:
            question_id: Unique identifier (auto-generated if None)
            question: The question text
            correct_answer: The correct answer
            user_answer: User's answer (None if not answered yet)
            is_correct: Whether the user's answer is correct (None if not answered)
        """
        self.id = question_id or self._generate_id()
        self.question = question
        self.correct_answer = correct_answer
        self.user_answer = user_answer
        self.is_correct = is_correct
    
    def _generate_id(self) -> str:
        """Generate a unique ID for the question."""
        return str(uuid.uuid4())
    
    def submit_answer(self, user_answer: str) -> bool:
        """
        Submit an answer to this question.
        Uses fuzzy matching - if similarity is >= 85%, marks as correct.
        Allows for minor typos, missing spaces, or small differences.
        """
        self.user_answer = user_answer
        
        # Normalize: lowercase, remove extra whitespace
        normalize = lambda t: re.sub(r'\s+', ' ', t.strip().lower())
        user_norm = normalize(user_answer)
        correct_norm = normalize(self.correct_answer)
        
        # Check exact match or 85%+ similarity
        self.is_correct = (user_norm == correct_norm or 
                          SequenceMatcher(None, user_norm, correct_norm).ratio() >= 0.85)
        return self.is_correct
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert question to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'question': self.question,
            'correct_answer': self.correct_answer,
            'user_answer': self.user_answer,
            'is_correct': self.is_correct
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PracticeTestQuestion':
        """Create question from dictionary."""
        return cls(
            question_id=data.get('id'),
            question=data.get('question', ''),
            correct_answer=data.get('correct_answer', ''),
            user_answer=data.get('user_answer'),
            is_correct=data.get('is_correct')
        )

