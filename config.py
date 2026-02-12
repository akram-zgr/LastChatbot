import os
from datetime import timedelta

class Config:
    # Flask settings
    SECRET_KEY = '9102d310950bace6b3fe5e7366b37d3e'
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = 'sqlite:///batna_chatbot.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Google Gemini API settings
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyDWOLb3EV4uhDeA6spKxn2KiLDpnNz0jtk').strip()
    GEMINI_MODEL = 'models/gemini-3-flash-preview'  # or 'gemini-1.5-flash', 'gemini-1.5-pro'
    

    # Email settings
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'chatbotunivbatna2@gmail.com'
    MAIL_PASSWORD = 'mqal kvrx akjq gwxb'
    MAIL_DEFAULT_SENDER = 'noreply@batnauniversity.com'
    
    # Session settings
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Security settings
    SESSION_COOKIE_SECURE = False  # localhost
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
