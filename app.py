"""
Word Search Game - Flask Backend Application
=============================================
This is the main application file that handles all server-side logic.

Features:
- Generates random 30x30 letter grids with hidden words
- Validates word submissions from players
- Tracks player scores and manages leaderboard
- Provides REST API endpoints for the frontend to communicate with

Technologies Used:
- Flask: Lightweight web framework for Python
- Random: Generate letter grids and select hidden words
- In-memory storage: For this version, data is stored in memory (resets on app restart)

Author: Your Name
Date: 2026
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import random
import string
from datetime import datetime

# Initialize Flask application
app = Flask(__name__)

# Set secret key for session management
# In production, use environment variables: os.environ.get('SECRET_KEY')
# Change this to a random string for security
app.secret_key = 'your-secret-key-change-this-in-production-12345'

# ===========================
# GLOBAL DATA STRUCTURES
# ===========================

# List of words that can be hidden in the grid
# Curated list of 25 common English words suitable for word search puzzles
WORD_LIST = [
    # Tech-related words
    "PYTHON", "FLASK", "JAVASCRIPT", "HTML", "CSS", "DATABASE",
    "ALGORITHM", "FUNCTION", "VARIABLE", "ITERATION", "RECURSION",
    
    # Computer terms
    "ARRAY", "DICTIONARY", "STRING", "BOOLEAN", "NETWORK",
    "SECURITY", "ENCRYPTION", "PROGRAM", "DEBUG", "LIBRARY",
    
    # General computing
    "COMPILE", "ERROR", "DISPLAY", "KEYBOARD", "MONITOR"
]


# Dictionary to store leaderboard data: {player_name: highest_score}
leaderboard = {}

# Current game state (stores active games)
active_games = {}


# ===========================
# WORD SEARCH GENERATOR CLASS
# ===========================

class WordSearchGenerator:
    """
    Generates realistic word search puzzles with hidden words in multiple directions.
    
    Features:
    - Places words horizontally, vertically, and diagonally
    - Supports forward and backward placement
    - Detects collisions and avoids overwriting
    - Fills empty cells with random letters
    - Tracks all successfully placed words
    """
    
    # Direction vectors: (row_delta, col_delta)
    # Allows words to be placed in 8 different directions
    DIRECTIONS = [
        (0, 1),   # Right (horizontal)
        (0, -1),  # Left (horizontal reverse)
        (1, 0),   # Down (vertical)
        (-1, 0),  # Up (vertical reverse)
        (1, 1),   # Down-right (diagonal)
        (-1, -1), # Up-left (diagonal reverse)
        (1, -1),  # Down-left (diagonal)
        (-1, 1),  # Up-right (diagonal reverse)
    ]
    
    def __init__(self, size=30, word_list=None):
        """
        Initialize the word search generator.
        
        Args:
            size: Grid dimensions (e.g., 30 creates a 30x30 grid)
            word_list: List of words to place (uses WORD_LIST if None)
        """
        self.size = size
        self.word_list = word_list or WORD_LIST
        # Initialize grid with None values (unfilled cells)
        self.grid = [[None for _ in range(size)] for _ in range(size)]
        self.placed_words = []  # Track successfully placed words
        self.word_positions = {}  # Store positions of each word for validation
    
    def can_place_word(self, word, row, col, direction):
        """
        Check if a word can be placed at the given position and direction.
        
        A word can be placed if:
        - All positions are within grid bounds
        - All positions are either empty (None) or contain the same letter
        - No collision with existing words (same letter at position = valid overlap)
        
        Args:
            word: Word to place (string)
            row: Starting row index
            col: Starting column index
            direction: Tuple (row_delta, col_delta) indicating direction
            
        Returns:
            bool: True if word can be placed, False otherwise
        """
        dr, dc = direction
        
        # Check each letter in the word
        for i, letter in enumerate(word):
            r = row + (dr * i)
            c = col + (dc * i)
            
            # Check bounds
            if r < 0 or r >= self.size or c < 0 or c >= self.size:
                return False
            
            # Check if cell is empty or matches the letter
            cell = self.grid[r][c]
            if cell is not None and cell != letter:
                return False  # Collision with different letter
        
        return True
    
    def place_word(self, word, row, col, direction):
        """
        Place a word on the grid at the given position and direction.
        
        Args:
            word: Word to place (string)
            row: Starting row index
            col: Starting column index
            direction: Tuple (row_delta, col_delta) indicating direction
        """
        dr, dc = direction
        positions = []
        
        # Place each letter
        for i, letter in enumerate(word):
            r = row + (dr * i)
            c = col + (dc * i)
            self.grid[r][c] = letter
            positions.append((r, c))
        
        # Track the placed word
        self.placed_words.append(word)
        self.word_positions[word] = positions
    
    def try_place_word(self, word, max_attempts=50):
        """
        Attempt to place a word on the grid with random starting positions.
        
        Tries multiple random positions and directions before giving up.
        
        Args:
            word: Word to place (string)
            max_attempts: Maximum number of random placements to try
            
        Returns:
            bool: True if word was successfully placed, False otherwise
        """
        # If word is too long for the grid, skip it
        if len(word) > self.size:
            return False
        
        # Try random placements
        for _ in range(max_attempts):
            # Random starting position
            row = random.randint(0, self.size - 1)
            col = random.randint(0, self.size - 1)
            
            # Random direction
            direction = random.choice(self.DIRECTIONS)
            
            # Try to place word
            if self.can_place_word(word, row, col, direction):
                self.place_word(word, row, col, direction)
                return True
        
        return False
    
    def fill_empty_cells(self):
        """
        Fill all empty cells (None) with random uppercase letters.
        
        This ensures the entire grid is filled with letters, making it
        look like a proper word search puzzle.
        """
        for row in range(self.size):
            for col in range(self.size):
                if self.grid[row][col] is None:
                    self.grid[row][col] = random.choice(string.ascii_uppercase)
    
    def generate(self):
        """
        Generate a complete word search puzzle.
        
        Process:
        1. Shuffle the word list for randomness
        2. Try to place each word in random positions/directions
        3. Fill remaining empty cells with random letters
        4. Return the final grid and list of placed words
        
        Returns:
            tuple: (grid, placed_words) where:
                - grid: 2D list of characters
                - placed_words: List of words successfully placed
        """
        # Shuffle word list for varied puzzles
        words = random.sample(self.word_list, min(len(self.word_list), 20))
        
        # Try to place each word
        for word in words:
            self.try_place_word(word)
        
        # Fill empty cells with random letters
        self.fill_empty_cells()
        
        # Return grid and list of successfully placed words
        return self.grid, self.placed_words


def generate_word_grid(size=30, num_words=None):
    """
    Generate a word search puzzle grid with hidden words.
    
    This is the main function used by the Flask app to create puzzles.
    
    Args:
        size: Grid dimensions (default 30x30)
        num_words: Not used (kept for backward compatibility)
        
    Returns:
        tuple: (grid, hidden_words) where:
            - grid: 2D list of characters representing the puzzle
            - hidden_words: List of words successfully hidden in the grid
            
    Example:
        >>> grid, words = generate_word_grid(30)
        >>> len(grid)  # Returns 30
        >>> len(grid[0])  # Returns 30 (each row has 30 columns)
        >>> len(words)  # Returns ~15-20 placed words
    """
    generator = WordSearchGenerator(size=size, word_list=WORD_LIST)
    grid, placed_words = generator.generate()
    
    return grid, placed_words



def is_valid_word(word, hidden_words):
    """
    Check if a word is in the list of hidden words.
    
    Args:
        word: Word to check (string)
        hidden_words: List of valid hidden words
        
    Returns:
        bool: True if word is valid and hidden, False otherwise
    """
    return word.upper() in hidden_words


# ===========================
# FLASK ROUTES (API ENDPOINTS)
# ===========================

@app.route('/')
def home():
    """
    Render the home page where users enter their name.
    This page provides a form for entering the player's name before starting the game.
    Returns: index.html template
    """
    return render_template('index.html')


@app.route('/game')
def game():
    """
    Render the game page where the word search happens.
    
    Security: This route checks that a player_name exists in the Flask session.
    If not, redirects back to home page.
    
    Returns: game.html template with player_name variable
    """
    # Check if player has started a game (name in session)
    if 'player_name' not in session:
        return redirect(url_for('home'))
    
    # Pass player name to template
    return render_template('game.html', player_name=session['player_name'])


@app.route('/api/start-game', methods=['POST'])
def start_game():
    """
    API endpoint to start a new game for a player.
    
    This endpoint validates the player name and sets up a new game session.
    The player name is stored in Flask session for security and continuity.
    
    Expected JSON payload:
        {
            "player_name": "John"
        }
    
    Returns:
        JSON: {
            "success": bool,
            "message": str,
            "redirect_url": "/game"  (on success)
        }
    """
    try:
        data = request.json
        player_name = data.get('player_name', '').strip() if data else ''
        
        # Validation: player name must not be empty
        if not player_name:
            return jsonify({
                'success': False,
                'message': 'Player name is required'
            }), 400
        
        # Validation: reasonable name length (2-50 characters)
        if len(player_name) < 2:
            return jsonify({
                'success': False,
                'message': 'Player name must be at least 2 characters'
            }), 400
        
        if len(player_name) > 50:
            return jsonify({
                'success': False,
                'message': 'Player name must not exceed 50 characters'
            }), 400
        
        # Store player name in Flask session
        # This makes it secure (signed, httponly by default) and persists across requests
        session['player_name'] = player_name
        
        # Generate game grid and words
        grid, hidden_words = generate_word_grid(size=30, num_words=8)
        
        # Create a unique game ID for this session
        # Using timestamp to allow multiple games from same player
        game_id = f"game_{datetime.now().timestamp()}"
        
        # Store game data in active_games dictionary
        # This is tied to the player's session
        active_games[game_id] = {
            'player_name': player_name,
            'grid': grid,
            'hidden_words': hidden_words,
            'found_words': set(),
            'score': 0,
            'start_time': datetime.now()
        }
        
        # Store current game ID in session so game page can access it
        session['game_id'] = game_id
        
        return jsonify({
            'success': True,
            'message': f'Game started for {player_name}',
            'redirect_url': url_for('game')
        })
    
    except Exception as e:
        print(f"Error in start_game: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred. Please try again.'
        }), 500


@app.route('/api/get-game-state', methods=['GET'])
def get_game_state():
    """
    API endpoint to fetch the current game state (grid and metadata).
    
    Called when the game page loads to get the word search grid to display.
    Uses Flask session to identify the current player and game.
    
    Returns:
        JSON: {
            "success": bool,
            "grid": 2D array of letters (30x30),
            "time_limit": 60 (seconds),
            "player_name": str
        }
    """
    # Check if player has an active game in their session
    if 'game_id' not in session or 'player_name' not in session:
        return jsonify({
            'success': False,
            'message': 'No active game session'
        }), 401
    
    game_id = session['game_id']
    player_name = session['player_name']
    
    # Validate game exists
    if game_id not in active_games:
        return jsonify({
            'success': False,
            'message': 'Invalid game session'
        }), 400
    
    game = active_games[game_id]
    
    return jsonify({
        'success': True,
        'grid': game['grid'],
        'time_limit': 60,
        'player_name': player_name,
        'word_count': len(game['hidden_words'])
    })


@app.route('/api/submit-word', methods=['POST'])
def submit_word():
    """
    API endpoint to submit a word found by the player.
    
    Validates the word against the current game's hidden words.
    Uses Flask session to identify the current player and game.
    
    Expected JSON payload:
        {
            "word": "PYTHON"
        }
    
    Returns:
        JSON: {
            "valid": bool,
            "score": int,
            "message": str,
            "points": int (if valid)
        }
    """
    # Check if player has an active game in their session
    if 'game_id' not in session or 'player_name' not in session:
        return jsonify({
            'success': False,
            'message': 'No active game session. Please start a new game.'
        }), 401
    
    game_id = session['game_id']
    
    # Validate game exists
    if game_id not in active_games:
        return jsonify({
            'success': False,
            'message': 'Invalid game session'
        }), 400
    
    data = request.json
    word = data.get('word', '').strip().upper()
    
    game = active_games[game_id]
    
    # Check if word is valid
    if not word or len(word) < 3:
        return jsonify({
            'valid': False,
            'message': 'Word must be at least 3 letters'
        })
    
    # Check if word was already found
    if word in game['found_words']:
        return jsonify({
            'valid': False,
            'message': 'Word already found!'
        })
    
    # Check if word is in hidden words
    if is_valid_word(word, game['hidden_words']):
        game['found_words'].add(word)
        # Score: 1 point per letter in the word
        points = len(word)
        game['score'] += points
        
        return jsonify({
            'valid': True,
            'points': points,
            'score': game['score'],
            'message': f"✓ Correct! +{points} points"
        })
    else:
        return jsonify({
            'valid': False,
            'message': 'Word not found in grid',
            'score': game['score']
        })


@app.route('/api/end-game', methods=['POST'])
def end_game():
    """
    API endpoint to end a game and save the score to leaderboard.
    
    Uses Flask session to identify the current player and game.
    Clears the session after saving the score.
    
    Returns:
        JSON: {
            "success": bool,
            "player_name": str,
            "score": int,
            "words_found": list
        }
    """
    # Check if player has an active game in their session
    if 'game_id' not in session or 'player_name' not in session:
        return jsonify({
            'success': False,
            'message': 'No active game session'
        }), 401
    
    game_id = session.get('game_id')
    player_name = session.get('player_name')
    
    if game_id not in active_games:
        return jsonify({
            'success': False,
            'message': 'Invalid game session'
        }), 400
    
    game = active_games[game_id]
    final_score = game['score']
    words_found = sorted(list(game['found_words']))
    
    # Update leaderboard with highest score
    if player_name not in leaderboard or leaderboard[player_name] < final_score:
        leaderboard[player_name] = final_score
    
    # Clean up active game
    del active_games[game_id]
    
    # Clear the session (player can start a new game from home page)
    session.clear()
    
    return jsonify({
        'success': True,
        'player_name': player_name,
        'score': final_score,
        'words_found': words_found
    })


@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """
    API endpoint to get the leaderboard.
    
    Returns:
        JSON: List of players sorted by score (highest first)
        [
            {"rank": 1, "name": "Alice", "score": 150},
            {"rank": 2, "name": "Bob", "score": 120},
            ...
        ]
    """
    # Sort leaderboard by score descending
    sorted_board = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)
    
    # Format for response
    board_data = [
        {'rank': idx + 1, 'name': name, 'score': score}
        for idx, (name, score) in enumerate(sorted_board)
    ]
    
    return jsonify(board_data)


# ===========================
# ERROR HANDLERS
# ===========================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors - page not found"""
    return render_template('index.html'), 404


if __name__ == '__main__':
    """
    Run the Flask development server.
    - debug=True enables hot-reload when code changes
    - port=5000 is the default Flask port
    - Access the app at http://localhost:5000
    """
    app.run(debug=True, port=5000)
