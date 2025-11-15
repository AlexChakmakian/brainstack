"""
BrainStack - Flask Application
Main entry point for the flashcard learning app
"""

from flask import Flask, request, jsonify, render_template, send_from_directory
import os
from storage import StorageManager
from flashcard import Flashcard
from deck import Deck
from user import User

# Initialize Flask app
app = Flask(__name__)

# Initialize storage manager
storage = StorageManager()

# Global variables to cache data
_cached_decks = None
_cached_user = None


def get_decks():
    """Get cached decks or load from storage."""
    global _cached_decks
    if _cached_decks is None:
        _cached_decks = storage.load_decks()
    return _cached_decks


def get_user():
    """Get cached user or load from storage."""
    global _cached_user
    if _cached_user is None:
        _cached_user = storage.load_user()
    return _cached_user


def save_decks():
    """Save decks to storage and update cache."""
    global _cached_decks
    if _cached_decks is not None:
        storage.save_decks(_cached_decks)


def save_user():
    """Save user to storage and update cache."""
    global _cached_user
    if _cached_user is not None:
        storage.save_user(_cached_user)


@app.route('/')
def index():
    """Serve the main dashboard page."""
    return send_from_directory('static', 'index.html')


@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files."""
    return send_from_directory('static', filename)


# API Routes

@app.route('/api/decks', methods=['GET'])
def get_decks_api():
    """Get all decks."""
    try:
        decks = get_decks()
        return jsonify({
            'success': True,
            'decks': [deck.to_dict() for deck in decks]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/decks', methods=['POST'])
def create_deck():
    """Create a new deck."""
    try:
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({
                'success': False,
                'error': 'Deck name is required'
            }), 400
        
        deck = Deck(
            name=data['name'],
            description=data.get('description', '')
        )
        
        decks = get_decks()
        decks.append(deck)
        save_decks()
        
        return jsonify({
            'success': True,
            'deck': deck.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/decks/<deck_id>', methods=['GET'])
def get_deck(deck_id):
    """Get a specific deck with its cards."""
    try:
        deck = storage.get_deck_by_id(deck_id)
        if not deck:
            return jsonify({
                'success': False,
                'error': 'Deck not found'
            }), 404
        
        return jsonify({
            'success': True,
            'deck': deck.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/decks/<deck_id>', methods=['DELETE'])
def delete_deck(deck_id):
    """Delete a deck."""
    try:
        success = storage.delete_deck(deck_id)
        if not success:
            return jsonify({
                'success': False,
                'error': 'Deck not found'
            }), 404
        
        # Update cache
        global _cached_decks
        _cached_decks = storage.load_decks()
        
        return jsonify({
            'success': True,
            'message': 'Deck deleted successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/decks/<deck_id>/cards', methods=['POST'])
def add_card_to_deck(deck_id):
    """Add a card to a deck."""
    try:
        data = request.get_json()
        if not data or 'front' not in data or 'back' not in data:
            return jsonify({
                'success': False,
                'error': 'Front and back content are required'
            }), 400
        
        card = Flashcard(data['front'], data['back'])
        success = storage.add_card_to_deck(deck_id, card)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Deck not found'
            }), 404
        
        # Update cache
        global _cached_decks
        _cached_decks = storage.load_decks()
        
        return jsonify({
            'success': True,
            'card': card.to_dict()
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/cards/<card_id>', methods=['DELETE'])
def delete_card(card_id):
    """Delete a card from any deck."""
    try:
        decks = get_decks()
        card_found = False
        
        for deck in decks:
            if deck.remove_card(card_id):
                card_found = True
                break
        
        if not card_found:
            return jsonify({
                'success': False,
                'error': 'Card not found'
            }), 404
        
        save_decks()
        
        return jsonify({
            'success': True,
            'message': 'Card deleted successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/study/<deck_id>', methods=['POST'])
def record_study_result(deck_id):
    """Record study results for cards."""
    try:
        data = request.get_json()
        if not data or 'results' not in data:
            return jsonify({
                'success': False,
                'error': 'Study results are required'
            }), 400
        
        deck = storage.get_deck_by_id(deck_id)
        if not deck:
            return jsonify({
                'success': False,
                'error': 'Deck not found'
            }), 404
        
        # Record results for each card
        for result in data['results']:
            card_id = result.get('card_id')
            is_correct = result.get('is_correct', False)
            
            card = deck.get_card(card_id)
            if card:
                card.record_study_result(is_correct)
        
        # Update deck in storage
        storage.update_deck(deck)
        
        # Update user stats
        user = get_user()
        total_cards = len(data['results'])
        correct_count = sum(1 for r in data['results'] if r.get('is_correct', False))
        incorrect_count = total_cards - correct_count
        
        user.record_study_session(total_cards, correct_count, incorrect_count)
        save_user()
        
        return jsonify({
            'success': True,
            'message': 'Study results recorded'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/progress', methods=['GET'])
def get_progress():
    """Get user progress statistics."""
    try:
        user = get_user()
        decks = get_decks()
        
        # Calculate overall stats
        total_decks = len(decks)
        total_cards = sum(deck.get_total_cards() for deck in decks)
        
        # Get deck-specific stats
        deck_stats = []
        for deck in decks:
            stats = deck.get_study_stats()
            deck_stats.append({
                'deck_id': deck.id,
                'deck_name': deck.name,
                **stats
            })
        
        return jsonify({
            'success': True,
            'progress': {
                'user': user.to_dict(),
                'total_decks': total_decks,
                'total_cards': total_cards,
                'deck_stats': deck_stats
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Initialize with some sample data if no data exists
    if not os.path.exists('data/flashcards.json'):
        print("Creating initial data file...")
        storage.save_data(storage._get_default_data())
    
    print("Starting BrainStack server...")
    print("Open your browser and go to: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
