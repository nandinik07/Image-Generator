from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from config import Config
from database import get_db_connection, init_db
from services.image_service import ImageService
import json
import requests
import io

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY

# Initialize DB on startup
init_db()

# --- HELPERS ---

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- ROUTES: PAGES ---

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/app')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/gallery')
@login_required
def gallery():
    conn = get_db_connection()
    # Fetch images for the LOGGED-IN user
    creations = conn.execute('SELECT * FROM creations WHERE user_id = ? ORDER BY created_at DESC', 
                           (session['user_id'],)).fetchall()
    conn.close()
    return render_template('gallery.html', creations=creations)

# NEW: Profile Page
@app.route('/profile')
@login_required
def profile():
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    
    # Get stats
    creation_count = conn.execute('SELECT COUNT(*) FROM creations WHERE user_id = ?', (session['user_id'],)).fetchone()[0]
    
    conn.close()
    return render_template('profile.html', user=user, creation_count=creation_count)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    email = ""
    
    if request.method == 'POST':
        # Normalize email
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()
        
        # Check real database hash
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            return redirect(url_for('dashboard'))
        else:
            error = "Invalid credentials. Please try again."
            
    return render_template('login.html', mode='login', error=error, email=email)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    email = ""
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        name = request.form.get('name', 'Artist').strip()
        
        if not email or not password:
            error = "Please fill in all fields."
        else:
            conn = get_db_connection()
            user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
            
            if user:
                conn.close()
                error = "Email already registered. Please log in."
            else:
                hashed_password = generate_password_hash(password)
                try:
                    conn.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)', (name, email, hashed_password))
                    conn.commit()
                    conn.close()
                    return redirect(url_for('login'))
                except Exception as e:
                    conn.close()
                    print(e)
                    error = "An error occurred. Please try again."

    return render_template('login.html', mode='signup', error=error, email=email)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# --- ROUTES: API ---

@app.route('/api/generate', methods=['POST'])
@login_required
def generate():
    data = request.json
    prompt = data.get('prompt')
    style = data.get('style', 'Cinematic')
    aspect_ratio = data.get('aspect_ratio', 'Square')
    seed = data.get('seed', None)
    
    if not prompt:
        return jsonify({'error': 'Prompt is required'}), 400

    size = "1024x1024" 
    if aspect_ratio == "Portrait": size = "1024x1024" 
    elif aspect_ratio == "Landscape": size = "1024x1024"

    try:
        # Call Service
        image_url = ImageService.generate_image(prompt, style, size, seed)
        
        # Save to History for the SESSION user
        conn = get_db_connection()
        conn.execute('INSERT INTO creations (user_id, prompt, style, aspect_ratio, image_data) VALUES (?, ?, ?, ?, ?)',
                     (session['user_id'], prompt, style, aspect_ratio, image_url))
        conn.commit()
        conn.close()

        return jsonify({'image': image_url})

    except Exception as e:
        print(f"GENERATION ERROR: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/history', methods=['GET'])
@login_required
def get_history():
    conn = get_db_connection()
    # Fetch history for the SESSION user
    creations = conn.execute('SELECT * FROM creations WHERE user_id = ? ORDER BY created_at DESC', 
                           (session['user_id'],)).fetchall()
    conn.close()
    return jsonify([dict(c) for c in creations])

@app.route('/download/<int:image_id>')
@login_required
def download_image(image_id):
    conn = get_db_connection()
    # Ensure user owns the image before downloading
    image = conn.execute('SELECT * FROM creations WHERE id = ? AND user_id = ?', 
                       (image_id, session['user_id'])).fetchone()
    conn.close()
    
    if image:
        image_url = image['image_data']
        try:
            response = requests.get(image_url, timeout=30)
            if response.status_code == 200:
                return send_file(
                    io.BytesIO(response.content),
                    mimetype='image/png',
                    as_attachment=True,
                    download_name=f"pixelmaster_{image_id}.png"
                )
        except Exception as e:
            print(f"Download Error: {e}")
            
    return "Error downloading image or unauthorized", 404

if __name__ == '__main__':
    app.run(debug=True, port=5001)