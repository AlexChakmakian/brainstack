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
        return {'users': {}}
    
    def get_user(self, username: str) -> User:
        """Get user by username."""
        data = self.load_data()
        users = data.get('users', {})
        user_data = users.get(username)
        if user_data:
            try:
                return User.from_dict(user_data)
            except Exception:
                return User(name=username)
        return None
    
    def create_user(self, username: str) -> User:
        """Create a new user."""
        user = User(name=username)
        self.save_user(username, user)
        return user
    
    def save_user(self, username: str, user: User) -> bool:
        """Save user data to storage."""
        data = self.load_data()
        if 'users' not in data:
            data['users'] = {}
        data['users'][username] = user.to_dict()
        return self.save_data(data)
    
    def user_exists(self, username: str) -> bool:
        """Check if user exists."""
        return self.get_user(username) is not None
    
    def load_decks(self, username: str) -> List[Deck]:
        """Load all decks from storage (from user's composition)."""
        user = self.get_user(username)
        return user.decks if user else []
    
    def save_decks(self, username: str, decks: List[Deck]) -> bool:
        """Save all decks to storage (to user's composition)."""
        user = self.get_user(username)
        if not user:
            return False
        user.decks = decks
        return self.save_user(username, user)
    
    def get_deck_by_id(self, username: str, deck_id: str) -> Deck:
        """Get a specific deck by ID from user's decks."""
        user = self.get_user(username)
        return user.get_deck(deck_id) if user else None
    
    def add_deck(self, username: str, deck: Deck) -> bool:
        """Add a new deck to user's collection."""
        user = self.get_user(username)
        if not user:
            return False
        user.add_deck(deck)
        return self.save_user(username, user)
    
    def update_deck(self, username: str, deck: Deck) -> bool:
        """Update an existing deck in user's collection."""
        user = self.get_user(username)
        if not user:
            return False
        for i, existing_deck in enumerate(user.decks):
            if existing_deck.id == deck.id:
                user.decks[i] = deck
                return self.save_user(username, user)
        return False
    
    def delete_deck(self, username: str, deck_id: str) -> bool:
        """Delete a deck from user's collection."""
        user = self.get_user(username)
        if not user:
            return False
        success = user.remove_deck(deck_id)
        if success:
            return self.save_user(username, user)
        return False
    
    def add_card_to_deck(self, username: str, deck_id: str, card: Flashcard) -> bool:
        """Add a card to a specific deck."""
        deck = self.get_deck_by_id(username, deck_id)
        if deck:
            deck.add_card(card.front, card.back)
            return self.update_deck(username, deck)
        return False