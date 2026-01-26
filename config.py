import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'pixel_master_secret_key_prod')
    DB_NAME = "pixelmaster.db"
    
    # AI Provider Config
    # We use strip() to remove any accidental quotes (e.g. "sk-...") from the .env file
    _key = os.getenv('SILICONFLOW_API_KEY', '')
    SILICONFLOW_API_KEY = _key.strip().strip('"').strip("'")