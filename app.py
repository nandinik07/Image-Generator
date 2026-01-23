from flask import Flask, render_template, request, jsonify, redirect, url_for
from config import Config
from database import get_db_connection, init_db
from services.image_service import ImageService
import json

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY

# Initialize DB
init_db()

# --- ROUTES: PAGES ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/app')
def dashboard():
    return render_template('dashboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        # Simple Mock Auth
        if email == 'test@example.com' and password == 'password':
            return redirect(url_for('dashboard'))
        else:
            error = "Invalid credentials. Try: test@example.com / password"
    return render_template('login.html', mode='login', error=error)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        return redirect(url_for('dashboard'))
    return render_template('login.html', mode='signup')

# --- ROUTES: API ---

@app.route('/api/generate', methods=['POST'])
def generate():
    data = request.json
    prompt = data.get('prompt')
    style = data.get('style', 'Cinematic')
    aspect_ratio = data.get('aspect_ratio', 'Square')
    
    if not prompt:
        return jsonify({'error': 'Prompt is required'}), 400

    # Translate aspect ratio to pixels (Flux supports these)
    size = "1024x1024" 
    if aspect_ratio == "Portrait": size = "1024x1024" 
    elif aspect_ratio == "Landscape": size = "1024x1024"

    try:
        # Call Service
        image_url = ImageService.generate_image(prompt, style, size)
        
        # Save to History
        conn = get_db_connection()
        conn.execute('INSERT INTO creations (user_id, prompt, style, aspect_ratio, image_data) VALUES (?, ?, ?, ?, ?)',
                     (1, prompt, style, aspect_ratio, image_url))
        conn.commit()
        conn.close()

        return jsonify({'image': image_url})

    except Exception as e:
        # Catch the specific error from the service and return it to the frontend
        print(f"GENERATION ERROR: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    conn = get_db_connection()
    creations = conn.execute('SELECT * FROM creations WHERE user_id = 1 ORDER BY created_at DESC').fetchall()
    conn.close()
    return jsonify([dict(c) for c in creations])

if __name__ == '__main__':
    app.run(debug=True, port=5001)