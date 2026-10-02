from flask import Flask, render_template, request, jsonify
import sqlite3
import os

app = Flask(__name__)

def init_db():
    """Initialize SQLite database for storing high scores."""
    conn = sqlite3.connect('highscore.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS highscore (
            id INTEGER PRIMARY KEY,
            score INTEGER NOT NULL
        )
    ''')
    cursor.execute('SELECT COUNT(*) FROM highscore')
    if cursor.fetchone()[0] == 0:
        cursor.execute('INSERT INTO highscore (id, score) VALUES (1, 0)')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    """Serve the main playable web game page."""
    return render_template('index.html')

@app.route('/api/highscore', methods=['GET'])
def get_highscore():
    """Retrieve the current highest score."""
    conn = sqlite3.connect('highscore.db')
    cursor = conn.cursor()
    cursor.execute('SELECT score FROM highscore WHERE id = 1')
    row = cursor.fetchone()
    score = row[0] if row else 0
    conn.close()
    return jsonify({'highscore': score})

@app.route('/api/highscore', methods=['POST'])
def save_highscore():
    """Update high score if the new score exceeds existing high score."""
    data = request.get_json() or {}
    new_score = data.get('score', 0)
    
    conn = sqlite3.connect('highscore.db')
    cursor = conn.cursor()
    cursor.execute('SELECT score FROM highscore WHERE id = 1')
    row = cursor.fetchone()
    current_score = row[0] if row else 0
    
    if new_score > current_score:
        cursor.execute('UPDATE highscore SET score = ? WHERE id = 1', (new_score,))
        conn.commit()
        updated = True
    else:
        updated = False
        
    conn.close()
    return jsonify({'status': 'success', 'updated': updated})

if __name__ == '__main__':
    init_db()
    # Port dynamically binds to cloud hosting providers like Heroku/Render if present
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)