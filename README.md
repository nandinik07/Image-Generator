Pixel Master (Alina X) 🎨
Pixel Master (branded as Alina X) is a professional AI image generation platform designed to help creators turn text into stunning visual masterpieces instantly. Built with Flask and powered by the state-of-the-art Flux model (via SiliconFlow), it features a secure, responsive, and modern studio interface.

🚀 Features
Advanced AI Generation: Create high-fidelity images using the Flux.1-schnell model, known for superior prompt adherence.

Smart Prompt Enhancer: Built-in "Magic" tool to automatically expand simple ideas into detailed, professional prompts (e.g., adding "8k resolution, cinematic lighting").

Studio Controls: Full control over Aspect Ratios (Square, Portrait, Landscape) and Artistic Styles (Anime, 3D Render, Oil Painting, Cyberpunk, etc.).

Personal Gallery: Generated images are automatically saved to your history. View, manage, and Download high-res PNGs anytime.

Secure Authentication: Complete user system with secure Login, Signup, and Profile management.

Modern UI: A fully responsive, dark-themed dashboard that provides a premium creative experience on Desktop and Mobile.

🛠️ Tech Stack
Backend: Python, Flask

Database: SQLite (Auto-initialized)

Frontend: HTML5, CSS3 (Custom Dark Theme), Vanilla JavaScript

AI Provider: SiliconFlow API (Black Forest Labs FLUX.1 model)

Utilities: python-dotenv, requests, werkzeug (Security)

📋 Prerequisites
Python 3.8 or higher

A SiliconFlow API Key (for Flux model access)

📦 Installation & Setup
Clone the repository

Bash
git clone <your-repo-url>
cd "pixel master"
Create a Virtual Environment It is recommended to use a virtual environment to manage dependencies.

Bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
Install Dependencies

Bash
pip install -r requirements.txt
Environment Configuration Create a .env file in the project root. You need a SECRET_KEY for session security and your SILICONFLOW_API_KEY.

You can generate a random secret key by running:

Bash
python -c "import secrets; print(secrets.token_hex(16))"
.env File Content:

Ini, TOML
# Security
SECRET_KEY=paste_generated_key_here

# AI Provider
SILICONFLOW_API_KEY=sk-your_siliconflow_key_here
Run the Application

Bash
python app.py
Access the App Open your browser and navigate to: http://127.0.0.1:5001

Demo Login: test@example.com / password

📂 Project Structure
Plaintext
pixel master/
├── app.py                  # Main Flask application entry point
├── config.py               # Configuration and env loading
├── database.py             # Database connection and initialization
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (Sensitive - do not commit)
├── services/
│   └── image_service.py    # Logic for calling SiliconFlow/Flux API
├── static/
│   ├── css/
│   │   └── style.css       # Main stylesheet (Dark/Studio theme)
│   ├── js/
│   │   └── app.js          # Frontend logic (API calls, UI interactions)
│   └── logo.jpeg           # App branding (Alina X)
└── templates/
    ├── index.html          # Landing page
    ├── login.html          # Authentication (Login/Signup)
    ├── dashboard.html      # Main Studio/Creation interface
    ├── gallery.html        # User history and downloads
    └── profile.html        # User settings and stats
🔐 Security Note
This application uses Werkzeug security (Scrypt/PBKDF2) to hash user passwords before storing them in the SQLite database. Session data is signed using the SECRET_KEY defined in your environment variables to prevent tampering.

🤝 Contributing
Contributions, issues, and feature requests are welcome!

📄 License
This project is open-source and available under the MIT License.
