/**
 * BrainStack - Frontend JavaScript
 * Handles all client-side functionality for the flashcard app
 */

class BrainStackApp {
    constructor() {
        this.currentDeck = null;
        this.currentCardIndex = 0;
        this.studyResults = [];
        this.isCardFlipped = false;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.checkLogin();
        this.loadDashboard();
    }
    
    async checkLogin() {
        try {
            const response = await fetch('/api/current-user');
            if (!response.ok) {
                window.location.href = '/login';
                return;
            }
        } catch (error) {
            window.location.href = '/login';
        }
    }
    
    toggleSettingsMenu() {
        const dropdown = document.getElementById('settingsDropdown');
        dropdown.classList.toggle('show');
    }
    
    async logout() {
        try {
            await this.apiCall('/api/logout', 'POST');
            window.location.href = '/login';
        } catch (error) {
            console.error('Logout failed:', error);
            window.location.href = '/login';
        }
    }
    
    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.switchPage(e.target.dataset.page));
        });
        
        // Dashboard
        document.getElementById('createDeckBtn').addEventListener('click', () => this.showDeckModal());
        document.getElementById('saveDeck').addEventListener('click', () => this.saveDeck());
        document.getElementById('cancelDeck').addEventListener('click', () => this.hideDeckModal());
        document.getElementById('closeModal').addEventListener('click', () => this.hideDeckModal());
        
        // Card Editor
        document.getElementById('addCardBtn').addEventListener('click', () => this.showCardModal());
        document.getElementById('saveCard').addEventListener('click', () => this.saveCard());
        document.getElementById('cancelCard').addEventListener('click', () => this.hideCardModal());
        document.getElementById('closeCardModal').addEventListener('click', () => this.hideCardModal());
        
        // Study Mode
        document.getElementById('studyDeckSelect').addEventListener('change', (e) => this.selectStudyDeck(e.target.value));
        document.getElementById('flipCardBtn').addEventListener('click', () => this.flipCard());
        document.getElementById('nextCardBtn').addEventListener('click', () => this.nextCard());
        document.getElementById('correctBtn').addEventListener('click', () => this.recordResult(true));
        document.getElementById('incorrectBtn').addEventListener('click', () => this.recordResult(false));
        
        // Navigation
        document.getElementById('backToDashboard').addEventListener('click', () => this.showDashboard());
        
        // Settings menu
        document.getElementById('settingsBtn').addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleSettingsMenu();
        });
        
        document.getElementById('settingsDropdown').addEventListener('click', (e) => {
            e.stopPropagation();
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', () => {
            document.getElementById('settingsDropdown').classList.remove('show');
        });
        
        // Logout
        document.getElementById('logoutBtn').addEventListener('click', () => {
            this.logout();
        });
        
        // Close modals when clicking outside
        window.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.hideDeckModal();
                this.hideCardModal();
            }
        });
    }
    
    // Navigation Methods
    switchPage(pageName) {
        // Update nav buttons
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-page="${pageName}"]`).classList.add('active');
        
        // Show/hide pages
        document.querySelectorAll('.page').forEach(page => {
            page.classList.remove('active');
        });
        document.getElementById(pageName).classList.add('active');
        
        // Load page-specific data
        switch(pageName) {
            case 'dashboard':
                this.loadDashboard();
                break;
            case 'study':
                this.loadStudyPage();
                break;
            case 'progress':
                this.loadProgressPage();
                break;
        }
    }
    
    showDashboard() {
        this.switchPage('dashboard');
    }
    
    // API Methods
    async apiCall(endpoint, method = 'GET', data = null) {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            }
        };
        
        if (data) {
            options.body = JSON.stringify(data);
        }
        
        try {
            const response = await fetch(endpoint, options);
            const result = await response.json();
            
            if (response.status === 401) {
                window.location.href = '/login';
                return;
            }
            
            if (!result.success) {
                throw new Error(result.error || 'API call failed');
            }
            
            return result;
        } catch (error) {
            console.error('API Error:', error);
            alert(`Error: ${error.message}`);
            throw error;
        }
    }
    
    // Dashboard Methods
    async loadDashboard() {
        try {
            const result = await this.apiCall('/api/decks');
            this.displayDecks(result.decks);
        } catch (error) {
            console.error('Failed to load decks:', error);
        }
    }
    
    displayDecks(decks) {
        const container = document.getElementById('decksList');
        
        if (decks.length === 0) {
            container.innerHTML = `
                <div class="text-center" style="grid-column: 1 / -1; padding: 40px;">
                    <h3>No decks yet</h3>
                    <p>Create your first deck to get started!</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = decks.map(deck => `
            <div class="deck-card" data-deck-id="${deck.id}">
                <h3>${deck.name}</h3>
                <p>${deck.description || 'No description'}</p>
                <div class="deck-stats">
                    <span>Cards: ${deck.cards.length}</span>
                    <span>Created: ${new Date(deck.created_at).toLocaleDateString()}</span>
                </div>
                <div class="deck-actions">
                    <button class="btn btn-primary btn-small" onclick="app.editDeck('${deck.id}')">Edit</button>
                    <button class="btn btn-secondary btn-small" onclick="app.deleteDeck('${deck.id}')">Delete</button>
                </div>
            </div>
        `).join('');
    }
    
    showDeckModal(deckId = null) {
        const modal = document.getElementById('deckModal');
        const title = document.getElementById('modalTitle');
        const form = document.getElementById('deckForm');
        
        if (deckId) {
            title.textContent = 'Edit Deck';
            // Load deck data for editing
            this.loadDeckForEdit(deckId);
        } else {
            title.textContent = 'Create New Deck';
            form.reset();
        }
        
        modal.style.display = 'block';
    }
    
    hideDeckModal() {
        document.getElementById('deckModal').style.display = 'none';
    }
    
    async saveDeck() {
        const name = document.getElementById('deckName').value.trim();
        const description = document.getElementById('deckDescription').value.trim();
        
        if (!name) {
            alert('Deck name is required');
            return;
        }
        
        try {
            const data = { name, description };
            await this.apiCall('/api/decks', 'POST', data);
            this.hideDeckModal();
            this.loadDashboard();
        } catch (error) {
            console.error('Failed to save deck:', error);
        }
    }
    
    async deleteDeck(deckId) {
        if (!confirm('Are you sure you want to delete this deck? This action cannot be undone.')) {
            return;
        }
        
        try {
            await this.apiCall(`/api/decks/${deckId}`, 'DELETE');
            this.loadDashboard();
        } catch (error) {
            console.error('Failed to delete deck:', error);
        }
    }
    
    async editDeck(deckId) {
        try {
            const result = await this.apiCall(`/api/decks/${deckId}`);
            this.currentDeck = result.deck;
            this.showDeckEditor();
        } catch (error) {
            console.error('Failed to load deck for editing:', error);
        }
    }
    
    showDeckEditor() {
        document.getElementById('editorDeckName').textContent = this.currentDeck.name;
        this.displayCards(this.currentDeck.cards);
        
        // Hide all pages and show editor
        document.querySelectorAll('.page').forEach(page => {
            page.classList.remove('active');
        });
        document.getElementById('deckEditor').classList.add('active');
    }
    
    displayCards(cards) {
        const container = document.getElementById('cardsList');
        
        if (cards.length === 0) {
            container.innerHTML = `
                <div class="text-center" style="padding: 40px;">
                    <h3>No cards yet</h3>
                    <p>Add your first card to get started!</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = cards.map(card => `
            <div class="card-item">
                <div class="card-content">
                    <div class="card-front">
                        <strong>Front:</strong> ${card.front}
                    </div>
                    <div class="card-back">
                        <strong>Back:</strong> ${card.back}
                    </div>
                </div>
                <div class="card-actions">
                    <button class="btn btn-danger btn-small" onclick="app.deleteCard('${card.id}')">Delete</button>
                </div>
            </div>
        `).join('');
    }
    
    showCardModal() {
        document.getElementById('cardModal').style.display = 'block';
        document.getElementById('cardForm').reset();
    }
    
    hideCardModal() {
        document.getElementById('cardModal').style.display = 'none';
    }
    
    async saveCard() {
        const front = document.getElementById('cardFrontInput').value.trim();
        const back = document.getElementById('cardBackInput').value.trim();
        
        if (!front || !back) {
            alert('Both front and back content are required');
            return;
        }
        
        try {
            const data = { front, back };
            await this.apiCall(`/api/decks/${this.currentDeck.id}/cards`, 'POST', data);
            this.hideCardModal();
            this.editDeck(this.currentDeck.id); // Reload the deck
        } catch (error) {
            console.error('Failed to save card:', error);
        }
    }
    
    async deleteCard(cardId) {
        if (!confirm('Are you sure you want to delete this card?')) {
            return;
        }
        
        try {
            await this.apiCall(`/api/cards/${cardId}`, 'DELETE');
            this.editDeck(this.currentDeck.id); // Reload the deck
        } catch (error) {
            console.error('Failed to delete card:', error);
        }
    }
    
    // Study Mode Methods
    async loadStudyPage() {
        try {
            const result = await this.apiCall('/api/decks');
            this.populateStudyDeckSelect(result.decks);
        } catch (error) {
            console.error('Failed to load decks for study:', error);
        }
    }
    
    populateStudyDeckSelect(decks) {
        const select = document.getElementById('studyDeckSelect');
        select.innerHTML = '<option value="">Select a deck to study</option>';
        
        decks.forEach(deck => {
            if (deck.cards.length > 0) {
                const option = document.createElement('option');
                option.value = deck.id;
                option.textContent = `${deck.name} (${deck.cards.length} cards)`;
                select.appendChild(option);
            }
        });
    }
    
    async selectStudyDeck(deckId) {
        if (!deckId) {
            this.resetStudyMode();
            return;
        }
        
        try {
            const result = await this.apiCall(`/api/decks/${deckId}`);
            this.currentDeck = result.deck;
            this.currentCardIndex = 0;
            this.studyResults = [];
            this.isCardFlipped = false;
            this.showCurrentCard();
        } catch (error) {
            console.error('Failed to load deck for study:', error);
        }
    }
    
    showCurrentCard() {
        if (!this.currentDeck || this.currentDeck.cards.length === 0) {
            return;
        }
        
        const card = this.currentDeck.cards[this.currentCardIndex];
        const frontElement = document.getElementById('cardFront');
        const backElement = document.getElementById('cardBack');
        const answerElement = document.getElementById('cardAnswer');
        
        frontElement.innerHTML = `<h3>${card.front}</h3>`;
        answerElement.textContent = card.back;
        
        // Show front, hide back
        document.getElementById('cardFront').classList.remove('hidden');
        document.getElementById('cardBack').classList.add('hidden');
        
        // Enable/disable buttons
        document.getElementById('flipCardBtn').disabled = false;
        document.getElementById('nextCardBtn').disabled = true;
        document.getElementById('correctBtn').disabled = true;
        document.getElementById('incorrectBtn').disabled = true;
        
        this.isCardFlipped = false;
    }
    
    flipCard() {
        if (this.isCardFlipped) {
            document.getElementById('cardFront').classList.remove('hidden');
            document.getElementById('cardBack').classList.add('hidden');
            document.getElementById('flipCardBtn').textContent = 'Flip Card';
            this.isCardFlipped = false;
        } else {
            document.getElementById('cardFront').classList.add('hidden');
            document.getElementById('cardBack').classList.remove('hidden');
            document.getElementById('flipCardBtn').textContent = 'Show Question';
            this.isCardFlipped = true;
            
            // Enable feedback buttons
            document.getElementById('correctBtn').disabled = false;
            document.getElementById('incorrectBtn').disabled = false;
        }
    }
    
    recordResult(isCorrect) {
        const card = this.currentDeck.cards[this.currentCardIndex];
        this.studyResults.push({
            card_id: card.id,
            is_correct: isCorrect
        });
        
        this.nextCard();
    }
    
    nextCard() {
        this.currentCardIndex++;
        
        if (this.currentCardIndex >= this.currentDeck.cards.length) {
            this.finishStudySession();
        } else {
            this.showCurrentCard();
        }
    }
    
    async finishStudySession() {
        try {
            await this.apiCall('/api/study/' + this.currentDeck.id, 'POST', {
                results: this.studyResults
            });
            
            alert(`Study session complete! You studied ${this.studyResults.length} cards.`);
            this.resetStudyMode();
        } catch (error) {
            console.error('Failed to record study results:', error);
        }
    }
    
    resetStudyMode() {
        document.getElementById('studyDeckSelect').value = '';
        document.getElementById('cardFront').innerHTML = '<h3>Select a deck to start studying</h3><p>Choose a deck from the dropdown above</p>';
        document.getElementById('cardBack').classList.add('hidden');
        document.getElementById('flipCardBtn').disabled = true;
        document.getElementById('nextCardBtn').disabled = true;
        document.getElementById('correctBtn').disabled = true;
        document.getElementById('incorrectBtn').disabled = true;
        
        this.currentDeck = null;
        this.currentCardIndex = 0;
        this.studyResults = [];
        this.isCardFlipped = false;
    }
    
    // Progress Methods
    async loadProgressPage() {
        try {
            const result = await this.apiCall('/api/progress');
            this.displayProgress(result.progress);
        } catch (error) {
            console.error('Failed to load progress:', error);
        }
    }
    
    displayProgress(progress) {
        // Overall stats
        document.getElementById('totalCardsStudied').textContent = progress.user.total_cards_studied;
        const accuracy = progress.user.total_cards_studied > 0 ? 
            (progress.user.total_correct / progress.user.total_cards_studied * 100).toFixed(1) : 0;
        document.getElementById('overallAccuracy').textContent = accuracy + '%';
        document.getElementById('totalSessions').textContent = progress.user.total_study_sessions;
        
        // Deck stats
        const deckStatsContainer = document.getElementById('deckStats');
        if (progress.deck_stats.length === 0) {
            deckStatsContainer.innerHTML = '<p>No study data available yet.</p>';
            return;
        }
        
        deckStatsContainer.innerHTML = progress.deck_stats.map(deck => `
            <div class="stat-item">
                <span class="stat-label">${deck.deck_name}:</span>
                <span class="stat-value">${deck.total_cards} cards, ${deck.accuracy}% accuracy</span>
            </div>
        `).join('');
    }
}

// Initialize the app when the page loads
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new BrainStackApp();
});
