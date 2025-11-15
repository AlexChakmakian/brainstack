"""
BrainStack - Flask Application
Main entry point for the flashcard learning app
"""

from flask import Flask, request, jsonify, render_template, send_from_directory, session, redirect
import os
from functools import wraps
from storage import StorageManager
from flashcard import Flashcard
from deck import Deck
from user import User

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

# Initialize storage manager
storage = StorageManager()


def get_current_username():
    """Get current username from session."""
    return session.get('username')


def login_required(f):
    """Decorator to require login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not get_current_username():
            return jsonify({'success': False, 'error': 'Not logged in'}), 401
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    """Serve the main dashboard page or redirect to login."""
    if not get_current_username():
        return redirect('/login')
    return send_from_directory('static', 'index.html')


@app.route('/login')
def login_page():
    """Serve the login page."""
    if get_current_username():
        return redirect('/')
    return send_from_directory('static', 'login.html')


@app.route('/api/login', methods=['POST'])
def login():
    """Handle user login."""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        
        if not username:
            return jsonify({'success': False, 'error': 'Username is required'}), 400
        
        # Create user if doesn't exist
        user = storage.get_user(username)
        if not user:
            user = storage.create_user(username)
        
        session['username'] = username
        return jsonify({'success': True, 'user': user.to_dict()})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/logout', methods=['POST'])
def logout():
    """Handle user logout."""
    session.pop('username', None)
    return jsonify({'success': True})


@app.route('/api/current-user', methods=['GET'])
def get_current_user():
    """Get current logged in user."""
    username = get_current_username()
    if not username:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    
    user = storage.get_user(username)
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404
    
    return jsonify({'success': True, 'user': user.to_dict()})


@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files."""
    return send_from_directory('static', filename)


# API Routes

@app.route('/api/decks', methods=['GET'])
@login_required
def get_decks_api():
    """Get all decks."""
    try:
        username = get_current_username()
        decks = storage.load_decks(username)
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
@login_required
def create_deck():
    """Create a new deck."""
    try:
        username = get_current_username()
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
        
        storage.add_deck(username, deck)
        
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
@login_required
def get_deck(deck_id):
    """Get a specific deck with its cards."""
    try:
        username = get_current_username()
        deck = storage.get_deck_by_id(username, deck_id)
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
@login_required
def delete_deck(deck_id):
    """Delete a deck."""
    try:
        username = get_current_username()
        success = storage.delete_deck(username, deck_id)
        if not success:
            return jsonify({
                'success': False,
                'error': 'Deck not found'
            }), 404
        
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
@login_required
def add_card_to_deck(deck_id):
    """Add a card to a deck."""
    try:
        username = get_current_username()
        data = request.get_json()
        if not data or 'front' not in data or 'back' not in data:
            return jsonify({
                'success': False,
                'error': 'Front and back content are required'
            }), 400
        
        card = Flashcard(data['front'], data['back'])
        success = storage.add_card_to_deck(username, deck_id, card)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Deck not found'
            }), 404
        
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
@login_required
def delete_card(card_id):
    """Delete a card from any deck."""
    try:
        username = get_current_username()
        decks = storage.load_decks(username)
        card_found = False
        
        for deck in decks:
            if deck.remove_card(card_id):
                card_found = True
                storage.update_deck(username, deck)
                break
        
        if not card_found:
            return jsonify({
                'success': False,
                'error': 'Card not found'
            }), 404
        
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
@login_required
def record_study_result(deck_id):
    """Record study results for cards."""
    try:
        username = get_current_username()
        data = request.get_json()
        if not data or 'results' not in data:
            return jsonify({
                'success': False,
                'error': 'Study results are required'
            }), 400
        
        deck = storage.get_deck_by_id(username, deck_id)
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
        storage.update_deck(username, deck)
        
        # Update user stats
        user = storage.get_user(username)
        total_cards = len(data['results'])
        correct_count = sum(1 for r in data['results'] if r.get('is_correct', False))
        incorrect_count = total_cards - correct_count
        
        user.record_study_session(total_cards, correct_count, incorrect_count)
        storage.save_user(username, user)
        
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
@login_required
def get_progress():
    """Get user progress statistics."""
    try:
        username = get_current_username()
        user = storage.get_user(username)
        decks = storage.load_decks(username)
        
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
    
    # Initialize with empty users dict if no data exists
    if not os.path.exists('data/flashcards.json'):
        print("Creating initial data file...")
        storage.save_data(storage._get_default_data())
    
    print("Starting BrainStack server...")
    print("Open your browser and go to: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
