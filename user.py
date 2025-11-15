"""
BrainStack - User Class
Represents a user with study progress tracking.
"""

import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from deck import Deck


class User:
    """Represents a user with study progress tracking."""
    
    def __init__(self, name: str = "Default User", user_id: Optional[str] = None):
        """
        Initialize a user.
        
        Args:
            name: User's name
            user_id: Unique identifier (auto-generated if None)
        """
        self.id = user_id or self._generate_id()
        self.name = name
        self.created_at = datetime.now().isoformat()
        self.total_study_sessions = 0
        self.total_cards_studied = 0
        self.total_correct = 0
        self.total_incorrect = 0
        # User has multiple (1 or more) Decks
        self.decks: List[Deck] = []
    
    def _generate_id(self) -> str:
        """Generate a unique ID for the user."""
        import uuid
        return str(uuid.uuid4())
    
    def record_study_session(self, cards_studied: int, correct: int, incorrect: int):
        """Record a study session."""
        self.total_study_sessions += 1
        self.total_cards_studied += cards_studied
        self.total_correct += correct
        self.total_incorrect += incorrect
    
    def get_overall_accuracy(self) -> float:
        """Calculate overall accuracy percentage."""
        if self.total_cards_studied == 0:
            return 0.0
        return (self.total_correct / self.total_cards_studied) * 100
    
    # Composition methods: User manages its Decks
    def add_deck(self, deck: Deck) -> None:
        """Add a deck to the user's collection."""
        self.decks.append(deck)
    
    def remove_deck(self, deck_id: str) -> bool:
        """Remove a deck from the user's collection by ID."""
        for i, deck in enumerate(self.decks):
            if deck.id == deck_id:
                del self.decks[i]
                return True
        return False
    
    def get_deck(self, deck_id: str) -> Optional[Deck]:
        """Get a deck by ID from the user's collection."""
        for deck in self.decks:
            if deck.id == deck_id:
                return deck
        return None
    
    def get_total_decks(self) -> int:
        """Get total number of decks owned by the user."""
        return len(self.decks)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at,
            'total_study_sessions': self.total_study_sessions,
            'total_cards_studied': self.total_cards_studied,
            'total_correct': self.total_correct,
            'total_incorrect': self.total_incorrect,
            'decks': [deck.to_dict() for deck in self.decks]  # Serialize composed decks
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create user from dictionary."""
        user = cls(data['name'], data['id'])
        user.created_at = data.get('created_at', datetime.now().isoformat())
        user.total_study_sessions = data.get('total_study_sessions', 0)
        user.total_cards_studied = data.get('total_cards_studied', 0)
        user.total_correct = data.get('total_correct', 0)
        user.total_incorrect = data.get('total_incorrect', 0)
        # Deserialize composed decks
        user.decks = [Deck.from_dict(deck_data) for deck_data in data.get('decks', [])]
        return user

