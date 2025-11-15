"""
BrainStack - Flashcard Class
Represents a single flashcard with front and back content.
"""

import json
from datetime import datetime
from typing import List, Optional, Dict, Any


class Flashcard:
    """Represents a single flashcard with front and back content."""
    
    def __init__(self, front: str, back: str, card_id: Optional[str] = None):
        """
        Initialize a flashcard.
        
        Args:
            front: The question/prompt side of the card
            back: The answer side of the card
            card_id: Unique identifier (auto-generated if None)
        """
        self.id = card_id or self._generate_id()
        self.front = front
        self.back = back
        self.created_at = datetime.now().isoformat()
        self.times_studied = 0
        self.correct_count = 0
        self.incorrect_count = 0
    
    def _generate_id(self) -> str:
        """Generate a unique ID for the flashcard."""
        import uuid
        return str(uuid.uuid4())
    
    def record_study_result(self, is_correct: bool):
        """Record the result of studying this card."""
        self.times_studied += 1
        if is_correct:
            self.correct_count += 1
        else:
            self.incorrect_count += 1
    
    def get_accuracy(self) -> float:
        """Calculate accuracy percentage for this card."""
        if self.times_studied == 0:
            return 0.0
        return (self.correct_count / self.times_studied) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert flashcard to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'front': self.front,
            'back': self.back,
            'created_at': self.created_at,
            'times_studied': self.times_studied,
            'correct_count': self.correct_count,
            'incorrect_count': self.incorrect_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Flashcard':
        """Create flashcard from dictionary."""
        card = cls(data['front'], data['back'], data['id'])
        card.created_at = data.get('created_at', datetime.now().isoformat())
        card.times_studied = data.get('times_studied', 0)
        card.correct_count = data.get('correct_count', 0)
        card.incorrect_count = data.get('incorrect_count', 0)
        return card
