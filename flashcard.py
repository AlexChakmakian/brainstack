"""
BrainStack - Flashcard Learning App
OOP Classes for Flashcard, Deck, and User management
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
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at,
            'total_study_sessions': self.total_study_sessions,
            'total_cards_studied': self.total_cards_studied,
            'total_correct': self.total_correct,
            'total_incorrect': self.total_incorrect
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
        return user
