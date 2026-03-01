# Word Search Game 🔍

A beginner-friendly multiplayer word search game built with Flask and vanilla JavaScript.

## Features

- **Interactive 30x30 letter grid** - Randomly generated for each game
- **60-second gameplay** - Find as many words as possible before time runs out
- **Score tracking** - 1 point per letter found
- **Leaderboard** - Track high scores across all players
- **Responsive design** - Works on desktop, tablet, and mobile
- **Simple architecture** - Great for learning Flask and web development

## Project Structure

```
py-game/
├── app.py                 # Flask backend application
├── requirements.txt       # Python dependencies
├── templates/             # HTML templates
│   ├── index.html        # Home page (name entry & leaderboard)
│   └── game.html         # Game page (word search interface)
├── static/
│   ├── css/
│   │   └── style.css     # Styling for entire application
│   └── js/
│       └── game.js       # (Optional) Separate JS file for cleaner code
└── README.md             # This file
```

## Technologies

- **Backend**: Python 3.7+ with Flask 2.3.3
- **Frontend**: HTML5, CSS3, Vanilla JavaScript (ES6+)
- **Storage**: In-memory (dictionary) - resets when app restarts
- **Port**: 5000 (default Flask port)

## Installation & Setup

### Prerequisites

- Python 3.7 or higher installed
- pip (Python package manager)
- Git (optional, for cloning)

### Step 1: Clone or Download the Project

```bash
# If using git
git clone <repository-url>
cd py-game

# OR manually download and navigate to the folder
```

### Step 2: Create a Virtual Environment (Recommended)

Virtual environments keep project dependencies isolated from your system Python.

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

After activation, you should see `(venv)` at the start of your terminal line.

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs Flask and all other required packages.

### Step 4: Run the Application

```bash
python app.py
```

You should see output like:
```
 * Serving Flask app 'app'
 * Running on http://127.0.0.1:5000
```

### Step 5: Open in Browser

Go to: **http://localhost:5000**

## How to Play

1. **Enter your name** on the home page
2. **Click "Start Game"** to begin
3. **Search for hidden words** in the 30x30 letter grid
4. **Type words** (minimum 3 letters) in the search box
5. **Submit** by pressing Enter or clicking the button
6. **Score points**: 1 point per letter in the word
7. **Beat the clock**: You have 60 seconds!
8. **Submit your score** to join the leaderboard

## Game Rules

- ✅ Words must be exactly as hidden in the grid
- ✅ Minimum word length: 3 letters
- ✅ Each word can only be found once
- ✅ Score = total letters in all found words
- ✅ Time limit: 60 seconds per game

## File Descriptions

### app.py
The main Flask application containing:
- **Route handlers** (`/`, `/game`, `/api/*`) - URL endpoints
- **Word list** - Dictionary of valid words to hide
- **Grid generation** - Algorithm to create 30x30 grid with hidden words
- **Validation logic** - Checks if submitted words are valid
- **Leaderboard storage** - Tracks high scores in memory
- **Error handlers** - Handles missing pages and errors

### requirements.txt
Lists all Python package dependencies needed to run the app.
- Flask: Web framework
- Werkzeug, Jinja2, MarkupSafe, Click, itsdangerous: Flask dependencies

### templates/index.html
Home page template where:
- Users enter their name
- Game instructions are displayed
- Current leaderboard is shown
- Forms submit to `/api/start-game` endpoint

### templates/game.html
Game page with:
- 30x30 word search grid
- Word input box
- Timer (countdown from 60 seconds)
- Score tracker
- Found words list
- Game over modal

### static/css/style.css
Comprehensive stylesheet with:
- Color scheme and typography
- Layout components (grid, cards, modals)
- Responsive design (mobile-first approach)
- Animations and transitions
- Dark gradient background

## API Endpoints

### `POST /api/start-game`
Starts a new game session.
```json
Request: {"player_name": "John"}
Response: {
  "success": true,
  "session_id": "John_1632940800.0",
  "grid": [[...30x30 grid...]],
  "time_limit": 60
}
```

### `POST /api/submit-word`
Submits a word for validation.
```json
Request: {"session_id": "...", "word": "PYTHON"}
Response: {
  "valid": true,
  "points": 6,
  "score": 42,
  "message": "✓ Correct! +6 points"
}
```

### `POST /api/end-game`
Ends the game and saves score to leaderboard.
```json
Request: {"session_id": "..."}
Response: {
  "success": true,
  "player_name": "John",
  "score": 150,
  "words_found": ["PYTHON", "FLASK", ...]
}
```

### `GET /api/leaderboard`
Retrieves top players.
```json
Response: [
  {"rank": 1, "name": "Alice", "score": 200},
  {"rank": 2, "name": "Bob", "score": 150}
]
```

## Troubleshooting

### Port 5000 Already in Use
```bash
# Find process using port 5000 and kill it
# Or run Flask on a different port:
python app.py
# Then modify line in app.py: app.run(debug=True, port=5001)
```

### Module Not Found Error
```bash
# Make sure you've activated the virtual environment and installed requirements:
pip install -r requirements.txt
```

### Grid Not Showing
- Check browser console for JavaScript errors (F12)
- Clear browser cache and refresh
- Try a different browser

### Words Not Being Found
- Words are case-insensitive (handled by `.upper()`)
- Check that words are in the WORD_LIST in `app.py`
- Verify the word exists in the current game's grid

## Future Enhancements

- **Database integration** - Use SQLite/PostgreSQL for permanent leaderboard
- **Word direction support** - Diagonal and reverse words
- **Difficulty levels** - Change grid size and word count
- **Sound effects** - Audio feedback for correct words
- **User accounts** - Login system with player profiles
- **Multiplayer mode** - Real-time competition
- **Word hints** - Help feature to find words
- **Better word validation** - Check coordinates in grid
- **Statistics** - Track player history and achievements
- **Deployment** - Host on Heroku, AWS, or other cloud platforms

## Deployment to Web

### Using Heroku (Free Alternative Ended)

### Using PythonAnywhere
1. Sign up at pythonanywhere.com
2. Upload your project
3. Configure WSGI file
4. Set custom domain if desired

### Using AWS/Google Cloud
1. Create a virtual machine
2. Install Python and dependencies
3. Run with a production server (Gunicorn)
4. Set up domain name and SSL

### Using GitHub + Vercel
Deploy the backend separately and frontend separately for better scalability.

## Development Tips

1. **Hot reload** - Flask auto-reloads on code changes (debug=True)
2. **Browser DevTools** - Press F12 to see console errors
3. **Test endpoints** - Use Postman or curl to test API routes
4. **Debugging** - Add `print()` statements or use Python debugger
5. **Logs** - Check terminal output for Flask logs

## License

This project is open source and free to use for educational purposes.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review code comments for explanations
3. Check browser console (F12) for JavaScript errors
4. Review Flask terminal output for backend errors

---

**Built with ❤️ for learning web development with Python and JavaScript**
