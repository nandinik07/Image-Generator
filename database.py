import sqlite3
from config import Config
from werkzeug.security import generate_password_hash

def get_db_connection():
    conn = sqlite3.connect(Config.DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    # Users Table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT DEFAULT 'Artist',
        email TEXT UNIQUE,
        password TEXT
    )''')

    # Creations Table
    c.execute('''CREATE TABLE IF NOT EXISTS creations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        prompt TEXT,
        style TEXT,
        aspect_ratio TEXT,
        image_data TEXT, 
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Seed/Update Demo User with Hashed Password
    user = c.execute('SELECT * FROM users WHERE id = 1').fetchone()
    demo_pass_hash = generate_password_hash("password")
    
    if not user:
        c.execute('INSERT INTO users (id, name, email, password) VALUES (1, "Demo Artist", "test@example.com", ?)', (demo_pass_hash,))
    else:
        # Update existing demo user to use hash if they are still using plain text "password"
        if user['password'] == 'password':
            c.execute('UPDATE users SET password = ? WHERE id = 1', (demo_pass_hash,))
        
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()