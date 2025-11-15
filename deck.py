"""
BrainStack - Deck Class
Represents a collection of flashcards.
"""

import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from flashcard import Flashcard


class Deck:
    """Represents a collection of flashcards."""
    
    def __init__(self, name: str, description: str = "", deck_id: Optional[str] = None):
        """
        Initialize a deck.
        
        Args:
            name: Name of the deck
            description: Optional description of the deck
            deck_id: Unique identifier (auto-generated if None)
        """
        self.id = deck_id or self._generate_id()
        self.name = name
        self.description = description
        self.created_at = datetime.now().isoformat()
        self.cards: List[Flashcard] = []
    
    def _generate_id(self) -> str:
        """Generate a unique ID for the deck."""
        import uuid
        return str(uuid.uuid4())
    
    def add_card(self, front: str, back: str) -> Flashcard:
        """Add a new flashcard to the deck."""
        card = Flashcard(front, back)
        self.cards.append(card)
        return card
    
    def remove_card(self, card_id: str) -> bool:
        """Remove a card from the deck by ID."""
        for i, card in enumerate(self.cards):
            if card.id == card_id:
                del self.cards[i]
                return True
        return False
    
    def get_card(self, card_id: str) -> Optional[Flashcard]:
        """Get a card by ID."""
        for card in self.cards:
            if card.id == card_id:
                return card
        return None
    
    def get_total_cards(self) -> int:
        """Get total number of cards in the deck."""
        return len(self.cards)
    
    def get_study_stats(self) -> Dict[str, Any]:
        """Get study statistics for the deck."""
        total_studied = sum(card.times_studied for card in self.cards)
        total_correct = sum(card.correct_count for card in self.cards)
        total_incorrect = sum(card.incorrect_count for card in self.cards)
        
        accuracy = 0.0
        if total_studied > 0:
            accuracy = (total_correct / total_studied) * 100
        
        return {
            'total_cards': self.get_total_cards(),
            'total_studied': total_studied,
            'total_correct': total_correct,
            'total_incorrect': total_incorrect,
            'accuracy': round(accuracy, 2)
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert deck to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at,
            'cards': [card.to_dict() for card in self.cards]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Deck':
        """Create deck from dictionary."""
        deck = cls(data['name'], data.get('description', ''), data['id'])
        deck.created_at = data.get('created_at', datetime.now().isoformat())
        deck.cards = [Flashcard.from_dict(card_data) for card_data in data.get('cards', [])]
        return deck

