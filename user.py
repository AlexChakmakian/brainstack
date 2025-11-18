"""
BrainStack - User Class
Represents a user with study progress tracking.
"""

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from werkzeug.security import generate_password_hash, check_password_hash
from deck import Deck
from practice_test import PracticeTest


class User:
    """Represents a user with study progress tracking."""
    
    def __init__(self, name: str = "Default User", user_id: Optional[str] = None, password_hash: Optional[str] = None):
        """
        Initialize a user.
        
        Args:
            name: User's name
            user_id: Unique identifier (auto-generated if None)
            password_hash: Hashed password (optional for existing users)
        """
        self.id = user_id or self._generate_id()
        self.name = name
        self.password_hash = password_hash
        self.created_at = datetime.now().isoformat()
        self.total_study_sessions = 0
        self.total_cards_studied = 0
        self.total_correct = 0
        self.total_incorrect = 0
        # User has multiple (1 or more) Decks
        self.decks: List[Deck] = []
        # User has multiple (0 or more) PracticeTests
        self.practice_tests: List[PracticeTest] = []
    
    def _generate_id(self) -> str:
        """Generate a unique ID for the user."""
        return str(uuid.uuid4())
    
    def set_password(self, password: str):
        """Set the user's password (hashed)."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """Check if the provided password matches the user's password."""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
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
        return next((deck for deck in self.decks if deck.id == deck_id), None)
    
    def get_total_decks(self) -> int:
        """Get total number of decks owned by the user."""
        return len(self.decks)
    
    # Composition methods: User manages its PracticeTests
    def add_practice_test(self, practice_test: PracticeTest) -> None:
        """Add a practice test to the user's collection."""
        self.practice_tests.append(practice_test)
    
    def remove_practice_test(self, test_id: str) -> bool:
        """Remove a practice test from the user's collection by ID."""
        for i, test in enumerate(self.practice_tests):
            if test.id == test_id:
                del self.practice_tests[i]
                return True
        return False
    
    def get_practice_test(self, test_id: str) -> Optional[PracticeTest]:
        """Get a practice test by ID from the user's collection."""
        return next((test for test in self.practice_tests if test.id == test_id), None)
    
    def get_total_practice_tests(self) -> int:
        """Get total number of practice tests owned by the user."""
        return len(self.practice_tests)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'password_hash': self.password_hash,
            'created_at': self.created_at,
            'total_study_sessions': self.total_study_sessions,
            'total_cards_studied': self.total_cards_studied,
            'total_correct': self.total_correct,
            'total_incorrect': self.total_incorrect,
            'decks': [deck.to_dict() for deck in self.decks],  # Serialize composed decks
            'practice_tests': [test.to_dict() for test in self.practice_tests]  # Serialize composed practice tests
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create user from dictionary."""
        user = cls(data['name'], data['id'], data.get('password_hash'))
        user.created_at = data.get('created_at', datetime.now().isoformat())
        user.total_study_sessions = data.get('total_study_sessions', 0)
        user.total_cards_studied = data.get('total_cards_studied', 0)
        user.total_correct = data.get('total_correct', 0)
        user.total_incorrect = data.get('total_incorrect', 0)
        # Deserialize composed decks
        user.decks = [Deck.from_dict(deck_data) for deck_data in data.get('decks', [])]
        # Deserialize composed practice tests
        user.practice_tests = [
            PracticeTest.from_dict(test_data) 
            for test_data in data.get('practice_tests', [])
        ]
        return user

