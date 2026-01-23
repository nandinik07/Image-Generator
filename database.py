import sqlite3
from config import Config

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

    # Creations Table (Stores images)
    # Note: For production, store image files on S3/Disk and paths here. 
    # For this standalone app, we store Base64 strings to keep it portable.
    c.execute('''CREATE TABLE IF NOT EXISTS creations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        prompt TEXT,
        style TEXT,
        aspect_ratio TEXT,
        image_data TEXT, 
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Seed Demo User
    user = c.execute('SELECT * FROM users WHERE id = 1').fetchone()
    if not user:
        c.execute('INSERT INTO users (id, name, email, password) VALUES (1, "Demo Artist", "test@example.com", "password")')
        
    conn.commit()
    conn.close()

init_db()