"""
BrainStack - Storage Management
Handles JSON file operations for saving and loading flashcard data
"""

import json
import os
from typing import List, Dict, Any
from flashcard import Flashcard
from deck import Deck
from user import User


class StorageManager:
    """Manages data persistence for the BrainStack application."""
    
    def __init__(self, data_file: str = "data/flashcards.json"):
        self.data_file = data_file
        self.ensure_data_directory()
    
    def ensure_data_directory(self):
        """Ensure the data directory exists."""
        data_dir = os.path.dirname(self.data_file)
        if data_dir and not os.path.exists(data_dir):
            os.makedirs(data_dir)
    
    def load_data(self) -> Dict[str, Any]:
        """Load data from JSON file."""
        if not os.path.exists(self.data_file):
            return self._get_default_data()
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return self._get_default_data()
    
    def save_data(self, data: Dict[str, Any]) -> bool:
        """Save data to JSON file."""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False
    
    def _get_default_data(self) -> Dict[str, Any]:
        """Get default data structure."""
        return {
            'user': {
                'id': 'default-user',
                'name': 'Default User',
                'created_at': '2024-01-01T00:00:00',
                'total_study_sessions': 0,
                'total_cards_studied': 0,
                'total_correct': 0,
                'total_incorrect': 0,
                'decks': []  # Decks are now part of user (composition)
            }
        }
    
    def load_decks(self) -> List[Deck]:
        """Load all decks from storage (from user's composition)."""
        user = self.load_user()
        return user.decks
    
    def save_decks(self, decks: List[Deck]) -> bool:
        """Save all decks to storage (to user's composition)."""
        user = self.load_user()
        user.decks = decks
        return self.save_user(user)
    
    def load_user(self) -> User:
        """Load user data from storage."""
        data = self.load_data()
        user_data = data.get('user', {})
        try:
            return User.from_dict(user_data)
        except Exception:
            return User()
    
    def save_user(self, user: User) -> bool:
        """Save user data to storage."""
        data = self.load_data()
        data['user'] = user.to_dict()
        return self.save_data(data)
    
    def get_deck_by_id(self, deck_id: str) -> Deck:
        """Get a specific deck by ID from user's decks."""
        user = self.load_user()
        return user.get_deck(deck_id)
    
    def add_deck(self, deck: Deck) -> bool:
        """Add a new deck to user's collection."""
        user = self.load_user()
        user.add_deck(deck)
        return self.save_user(user)
    
    def update_deck(self, deck: Deck) -> bool:
        """Update an existing deck in user's collection."""
        user = self.load_user()
        for i, existing_deck in enumerate(user.decks):
            if existing_deck.id == deck.id:
                user.decks[i] = deck
                return self.save_user(user)
        return False
    
    def delete_deck(self, deck_id: str) -> bool:
        """Delete a deck from user's collection."""
        user = self.load_user()
        success = user.remove_deck(deck_id)
        if success:
            return self.save_user(user)
        return False
    
    def add_card_to_deck(self, deck_id: str, card: Flashcard) -> bool:
        """Add a card to a specific deck."""
        deck = self.get_deck_by_id(deck_id)
        if deck:
            deck.add_card(card.front, card.back)
            return self.update_deck(deck)
        return False
    
    def delete_card_from_deck(self, deck_id: str, card_id: str) -> bool:
        """Delete a card from a specific deck."""
        deck = self.get_deck_by_id(deck_id)
        if deck:
            success = deck.remove_card(card_id)
            if success:
                return self.update_deck(deck)
        return False