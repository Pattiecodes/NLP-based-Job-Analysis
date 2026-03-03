"""
Main Flask Application
ITS120L - Job Skills NLP Analysis Platform
"""
from flask import Flask, jsonify, request, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime, timedelta
from daily_scraper import start_daily_scraper

# Initialize Flask app
app = Flask(__name__)
CORS(app, supports_credentials=True, origins=['http://localhost:3000'])

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///job_skills_nlp.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = '../uploads'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# Create directory for uploads
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database
from models import db
db.init_app(app)

# Import routes
from routes import analysis_routes, upload_routes, dashboard_routes, auth_routes, download_routes, scraping_routes

# Register blueprints
app.register_blueprint(analysis_routes.bp)
app.register_blueprint(upload_routes.bp)
app.register_blueprint(dashboard_routes.bp)
app.register_blueprint(auth_routes.bp)
app.register_blueprint(download_routes.download_routes)
app.register_blueprint(scraping_routes.bp)

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

# Root endpoint
@app.route('/')
def index():
    return jsonify({
        'message': 'Job Skills NLP Analysis API',
        'version': '1.0.0',
        'endpoints': {
            'health': '/api/health',
            'dashboard': '/api/dashboard',
            'analysis': '/api/analysis',
            'upload': '/api/upload'
        }
    })

if __name__ == '__main__':
    # Create upload directory if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Start daily background scraping (runs every 12:00 AM local time)
    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        start_daily_scraper(app)
    
    # Run application
    app.run(debug=True, host='0.0.0.0', port=5000)
