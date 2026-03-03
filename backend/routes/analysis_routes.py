"""
Analysis Routes - ML model inference and analysis
"""
from flask import Blueprint, jsonify, request
import pickle
import os
import pandas as pd
from models import JobPosting, db
from sqlalchemy import or_

bp = Blueprint('analysis', __name__, url_prefix='/api/analysis')

# Load models on startup
MODEL_PATH = '../output'

def load_model(filename):
    """Load a pickled model"""
    try:
        filepath = os.path.join(MODEL_PATH, filename)
        with open(filepath, 'rb') as f:
            return pickle.load(f)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return None

# Models will be loaded lazily when needed
models = {}

@bp.route('/skills/extract', methods=['POST'])
def extract_skills():
    """Extract skills from job description text"""
    data = request.get_json()
    
    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400
    
    text = data['text']
    
    # TODO: Implement skill extraction using the NLP pipeline
    # For now, return mock data
    return jsonify({
        'skills': ['Python', 'SQL', 'AWS', 'Machine Learning'],
        'is_mock': True
    })

@bp.route('/cluster/predict', methods=['POST'])
def predict_cluster():
    """Predict job cluster for given text"""
    data = request.get_json()
    
    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400
    
    # Load models if not already loaded
    if 'tfidf_vectorizer' not in models:
        models['tfidf_vectorizer'] = load_model('tfidf_vectorizer.pkl')
    if 'kmeans_model' not in models:
        models['kmeans_model'] = load_model('kmeans_model.pkl')
    
    if not models['tfidf_vectorizer'] or not models['kmeans_model']:
        return jsonify({'error': 'Models not available'}), 500
    
    try:
        # Transform text
        text_vector = models['tfidf_vectorizer'].transform([data['text']])
        
        # Predict cluster
        cluster = int(models['kmeans_model'].predict(text_vector)[0])
        
        return jsonify({
            'cluster': cluster,
            'confidence': 0.85  # TODO: Calculate actual confidence
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/topic/predict', methods=['POST'])
def predict_topic():
    """Predict dominant topic for given text"""
    data = request.get_json()
    
    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400
    
    # Load models if not already loaded
    if 'lda_model' not in models:
        models['lda_model'] = load_model('lda_model.pkl')
    
    if not models['lda_model']:
        return jsonify({'error': 'LDA model not available'}), 500
    
    try:
        # TODO: Implement topic prediction
        return jsonify({
            'topic': 0,
            'distribution': [0.1, 0.2, 0.3, 0.15, 0.25],
            'is_mock': True
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/search', methods=['GET'])
def search_jobs():
    """Search for jobs by keywords"""
    query = request.args.get('q', '')
    limit = request.args.get('limit', 20, type=int)
    
    if not query:
        return jsonify({'jobs': []})
    
    # Search in job titles and summaries
    jobs = JobPosting.query.filter(
        or_(
            JobPosting.job_title.ilike(f'%{query}%'),
            JobPosting.job_summary.ilike(f'%{query}%')
        )
    ).limit(limit).all()
    
    return jsonify({
        'jobs': [job.to_dict() for job in jobs],
        'count': len(jobs)
    })
