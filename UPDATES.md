# Word Search Game - Flask Sessions Update

## Overview
The application has been updated to use **Flask's built-in session management** for secure player authentication and game state tracking. This replaces the previous browser-based sessionStorage approach.

## Key Changes

### 1. Backend Updates (app.py)

#### Added Flask Session Support
- **Import**: Added `session`, `redirect`, `url_for` from Flask
- **Secret Key**: Added `app.secret_key` for session encryption
  - In production, use environment variables for the secret key
  ```python
  app.secret_key = 'your-secret-key-change-this-in-production-12345'
  ```

#### Updated Routes

##### `/` (Home Page)
- Simple route that renders the home template
- No session checks (anyone can access)

##### `/game` (Game Page)
- **Added security check**: Verifies `player_name` exists in Flask session
- **Redirects to home** if no valid session
- **Passes player_name** to template via Jinja2
  ```python
  if 'player_name' not in session:
      return redirect(url_for('home'))
  return render_template('game.html', player_name=session['player_name'])
  ```

##### `/api/start-game` (Start Game Endpoint)
**Major Changes:**
- Validates player name (2-50 characters)
- **Stores player_name in Flask session** instead of just returning it
- Generates unique game_id with timestamp
- **Stores game_id in Flask session** for later retrieval
- Returns JSON with `redirect_url` instead of returning grid directly
- Added comprehensive error handling with try-catch

```python
# Store in Flask session
session['player_name'] = player_name
session['game_id'] = game_id

# Return redirect URL
return jsonify({
    'success': True,
    'redirect_url': url_for('game')
})
```

##### `/api/submit-word` (Submit Word Endpoint)
**Major Changes:**
- **Gets game_id from Flask session** instead of request body
- Validates session exists before processing
- Validates game_id exists in active_games
- Same validation logic, but secure session-based

```python
# Get from session instead of request
if 'game_id' not in session or 'player_name' not in session:
    return jsonify({'success': False, ...}), 401

game_id = session['game_id']
# Rest of validation...
```

##### `/api/end-game` (End Game Endpoint)
**Major Changes:**
- **Gets game_id and player_name from Flask session**
- Validates session before processing
- **Clears session** after saving score
- Better organized with comprehensive error handling

```python
# Get from session
game_id = session.get('game_id')
player_name = session.get('player_name')

# Process game end...

# Clear session
session.clear()
```

---

### 2. Frontend Updates

#### index.html (Home Page)

**Changes to Form Submission Handler:**
- Added client-side validation for name length (2-50 characters)
- **Removed sessionStorage.setItem calls**
- Added button disable/loading state
- Improved error messages with visual indicators (✗, ✓)
- **On success**: Redirects to `data.redirect_url` returned from backend
- Flask session handles the persistence server-side

```javascript
// Before: sessionStorage.setItem('session_id', data.session_id);
// After: window.location.href = data.redirect_url || '/game';
```

---

#### game.html (Game Page)

**Changes to Game Initialization:**

1. **Removed sessionStorage usage**
   ```javascript
   // Before: sessionStorage.getItem('session_id')
   // After: Jinja2 template variable
   const templatePlayerName = "{{ player_name | escape }}";
   ```

2. **Updated gameState object**
   - Removed `sessionId` property
   - `playerName` now comes from template variable
   - Added HTML escaping for security (`| escape`)

3. **Security check**
   ```javascript
   if (!gameState.playerName || gameState.playerName === 'None') {
       // Redirect if no valid session
   }
   ```

**Changes to API Calls:**

1. **submitWord() function**
   - **Removed session_id from request body**
   - Flask session automatically provides it via cookies
   ```javascript
   // Before: body: JSON.stringify({ session_id: gameState.sessionId, word: word })
   // After: body: JSON.stringify({ word: word })
   ```

2. **submitScore() function**
   - **Removed session_id from request body**
   - Backend gets game_id from Flask session
   ```javascript
   // Before: body: JSON.stringify({ session_id: gameState.sessionId })
   // After: body: JSON.stringify({})
   ```

---

## Security Benefits

### Before (sessionStorage)
- ❌ Client-side storage vulnerable to XSS attacks
- ❌ Data visible in browser DevTools
- ❌ Could be manually modified

### After (Flask Sessions)
- ✅ Server-side encrypted session storage
- ✅ HttpOnly cookies prevent JavaScript access
- ✅ Signed session data prevents tampering
- ✅ Server validates all game state
- ✅ Session cleared on game end

---

## User Flow

### Starting a Game
1. User enters name on home page (`/`)
2. Form submits to `/api/start-game` with JSON
3. Backend validates name, stores in Flask session
4. Backend generates game, stores session variables
5. Backend returns `redirect_url`
6. Frontend redirects to `/game`
7. Backend `/game` route checks session, renders with player_name

### During Game
1. User submits words
2. Frontend sends to `/api/submit-word` (Flask session auto-included)
3. Backend retrieves game_id from session, validates word
4. Backend updates score, returns result
5. Frontend displays result and updates UI

### Ending Game
1. Time runs out or user clicks "End Game"
2. Frontend sends POST to `/api/end-game`
3. Backend retrieves game from session, finalizes score
4. Backend updates leaderboard, clears session
5. Frontend redirects to home

---

## Testing Checklist

- [x] Flask app starts without errors
- [x] Home page form submission works
- [x] Player name validation works
- [x] Redirects to game page
- [x] Player name displays on game page
- [x] Word submission works
- [x] Score updates correctly
- [x] Game timer works
- [x] End game functionality works
- [x] Leaderboard displays

---

## Sessions & Cookies

### Session Expiration
By default, Flask sessions expire when:
- Browser is closed (session is temporary)
- Default timeout (depends on configuration)

To customize session behavior:

```python
# Make session persistent (30 days)
app.permanent_session_lifetime = timedelta(days=30)

# In your routes:
session.permanent = True
```

---

## Configuration Notes

### Secret Key (Important!)
The current secret key in `app.py` should be changed for production:

```python
# Current (for development only):
app.secret_key = 'your-secret-key-change-this-in-production-12345'

# Better approach for production:
import os
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-change-this')
```

### Session Security Options
```python
# Configure session cookie behavior
app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS only
app.config['SESSION_COOKIE_HTTPONLY'] = True  # No JS access
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'  # CSRF protection
```

---

## Migration Summary

| Aspect | Before | After |
|--------|--------|-------|
| Player Storage | sessionStorage (client) | Flask session (server) |
| Session ID | Passed in each request | Auto-included in cookies |
| Security | Vulnerable to tampering | Cryptographically signed |
| API Calls | Include session_id in body | Session auto-provided |
| Game Data | Stored in active_games dict | Same, but tied to session |
| Validation | Client-side only | Server-side enforced |
| Leaderboard | In-memory dictionary | Same (persists during runtime) |

---

## Future Improvements

1. **Database Integration**: Replace leaderboard dictionary with SQLite/PostgreSQL
2. **Session Persistence**: Save sessions to database for recovery
3. **Configurable Secret Key**: Use environment variables
4. **Session Timeout**: Implement automatic session expiration
5. **Rate Limiting**: Prevent API abuse
6. **Logging**: Track player actions and scores
7. **Admin Panel**: View and manage players/scores

---

## Installation & Running

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py

# Access at http://localhost:5000
```

---

**Last Updated**: March 1, 2026
