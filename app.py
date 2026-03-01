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
WORD_LIST = [
    "PYTHON", "FLASK", "JAVASCRIPT", "HTML", "CSS", "DATABASE",
    "ALGORITHM", "FUNCTION", "VARIABLE", "CONSTANT", "ITERATION",
    "RECURSION", "ARRAY", "DICTIONARY", "STRING", "BOOLEAN",
    "INTEGER", "FLOAT", "NETWORK", "SECURITY", "ENCRYPTION",
    "DISPLAY", "KEYBOARD", "MONITOR", "PROGRAM", "COMPILE",
    "DEBUG", "ERROR", "WARNING", "EXCEPTION", "LIBRARY"
]

# Dictionary to store leaderboard data: {player_name: highest_score}
leaderboard = {}

# Current game state (stores active games)
active_games = {}


# ===========================
# UTILITY FUNCTIONS
# ===========================

def generate_word_grid(size=30, num_words=8):
    """
    Generate a random letter grid with hidden words.
    
    Args:
        size: Grid dimensions (30x30)
        num_words: Number of words to hide in the grid
        
    Returns:
        tuple: (grid, hidden_words) where grid is 2D list and hidden_words is list of words
    """
    # Create empty grid filled with random letters
    grid = [[random.choice(string.ascii_uppercase) for _ in range(size)] for _ in range(size)]
    
    # Select random words to hide
    hidden_words = random.sample(WORD_LIST, min(num_words, len(WORD_LIST)))
    
    # Place words in the grid (horizontal and vertical for simplicity)
    for word in hidden_words:
        # Randomly decide direction (horizontal or vertical)
        if random.choice([True, False]):  # Horizontal
            row = random.randint(0, size - 1)
            col = random.randint(0, size - len(word) - 1)
            for i, letter in enumerate(word):
                grid[row][col + i] = letter
        else:  # Vertical
            row = random.randint(0, size - len(word) - 1)
            col = random.randint(0, size - 1)
            for i, letter in enumerate(word):
                grid[row + i][col] = letter
    
    return grid, hidden_words


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
