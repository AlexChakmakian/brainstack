# BrainStack - Flashcard Learning App

A modern, object-oriented flashcard learning application built with Python Flask backend and vanilla HTML/CSS/JavaScript frontend.

## Features

- **Dashboard**: View all your flashcard decks with statistics
- **Deck Editor**: Create, edit, and manage flashcard decks
- **Study Mode**: Interactive flashcard studying with flip functionality
- **Progress Tracking**: Monitor your learning progress and accuracy
- **Local Storage**: All data stored in `data/flashcards.json`

## Architecture

```
brainstack/
├── main.py              # Flask app entry point
├── flashcard.py         # OOP Classes: Flashcard, Deck, User
├── storage.py           # JSON data persistence
├── requirements.txt     # Python dependencies
├── static/
│   ├── index.html      # Main HTML page
│   ├── style.css       # Modern CSS styling
│   └── script.js       # Frontend JavaScript
└── data/
    └── flashcards.json # Local data storage
```

## Installation & Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   python main.py
   ```

3. **Open your browser:**
   Navigate to `http://localhost:5000`

## API Endpoints

- `GET /api/decks` - List all decks
- `POST /api/decks` - Create new deck
- `GET /api/decks/<id>` - Get specific deck with cards
- `DELETE /api/decks/<id>` - Delete deck
- `POST /api/decks/<id>/cards` - Add card to deck
- `DELETE /api/cards/<id>` - Delete card
- `POST /api/study/<deck_id>` - Record study results
- `GET /api/progress` - Get user progress statistics

## Object-Oriented Design

### Flashcard Class
- Represents individual flashcards with front/back content
- Tracks study statistics (times studied, accuracy)
- Methods for recording study results

### Deck Class
- Manages collections of flashcards
- Provides study statistics and progress tracking
- Handles card addition/removal

### User Class
- Tracks overall learning progress
- Records study sessions and accuracy
- Provides comprehensive statistics

## Features

### Dashboard
- View all flashcard decks
- Create new decks
- Edit existing decks
- Delete decks
- View deck statistics

### Study Mode
- Select deck to study
- Flip cards to reveal answers
- Record correct/incorrect responses
- Track study progress

### Progress Tracking
- Overall study statistics
- Per-deck performance metrics
- Accuracy tracking
- Study session history

## Technology Stack

- **Backend**: Python Flask
- **Frontend**: Vanilla HTML, CSS, JavaScript
- **Storage**: Local JSON file
- **Styling**: Modern CSS with Roboto font
- **Architecture**: RESTful API with clean separation of concerns

## Getting Started

1. Run `python main.py`
2. Open `http://localhost:5000` in your browser
3. Create your first deck
4. Add some flashcards
5. Start studying!

The app will automatically create the data directory and initialize with default settings.
