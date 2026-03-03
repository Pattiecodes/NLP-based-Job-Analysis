"""
Database Models
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        # Use pbkdf2:sha256 with 100k iterations (faster than default 260k)
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'created_at': self.created_at.isoformat()
        }

class JobPosting(db.Model):
    __tablename__ = 'job_postings'
    
    id = db.Column(db.Integer, primary_key=True)
    job_title = db.Column(db.String(255), nullable=False)
    company = db.Column(db.String(255))
    job_location = db.Column(db.String(255))
    job_level = db.Column(db.String(100))
    job_type = db.Column(db.String(100))
    job_category = db.Column(db.String(100))  # NLP-derived category
    job_summary = db.Column(db.Text)
    job_link = db.Column(db.String(500), unique=True)
    search_country = db.Column(db.String(100))
    search_city = db.Column(db.String(100))
    posted_date = db.Column(db.DateTime)
    data_source = db.Column(db.String(50), default='upload')  # upload, web_scraper, api
    scraped_at = db.Column(db.DateTime)
    cluster_id = db.Column(db.Integer)  # ML cluster assignment
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    skills = db.relationship('JobSkill', backref='job', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'job_title': self.job_title,
            'company': self.company,
            'job_location': self.job_location,
            'job_level': self.job_level,
            'job_type': self.job_type,
            'job_category': self.job_category,
            'job_summary': self.job_summary,
            'job_link': self.job_link,
            'search_country': self.search_country,
            'search_city': self.search_city,
            'posted_date': self.posted_date.isoformat() if self.posted_date else None,
            'data_source': self.data_source,
            'cluster_id': self.cluster_id,
            'created_at': self.created_at.isoformat()
        }

class JobSkill(db.Model):
    __tablename__ = 'job_skills'
    
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job_postings.id'), nullable=False)
    skill_name = db.Column(db.String(255), nullable=False)
    is_technical = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'job_id': self.job_id,
            'skill_name': self.skill_name,
            'is_technical': self.is_technical
        }

class TrendingSkill(db.Model):
    __tablename__ = 'trending_skills'
    
    id = db.Column(db.Integer, primary_key=True)
    skill_name = db.Column(db.String(255), unique=True, nullable=False)
    mention_count = db.Column(db.Integer, default=0)
    is_technical = db.Column(db.Boolean, default=False)
    category = db.Column(db.String(100))  # programming, cloud, data, etc.
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'skill_name': self.skill_name,
            'mention_count': self.mention_count,
            'is_technical': self.is_technical,
            'category': self.category,
            'updated_at': self.updated_at.isoformat()
        }

class AnalysisResult(db.Model):
    __tablename__ = 'analysis_results'
    
    id = db.Column(db.Integer, primary_key=True)
    analysis_type = db.Column(db.String(100))  # clustering, topic_modeling, tfidf
    result_data = db.Column(db.JSON)
    model_version = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'analysis_type': self.analysis_type,
            'result_data': self.result_data,
            'model_version': self.model_version,
            'created_at': self.created_at.isoformat()
        }

class UploadHistory(db.Model):
    __tablename__ = 'upload_history'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50))
    file_size = db.Column(db.Integer)
    records_processed = db.Column(db.Integer)
    status = db.Column(db.String(50))  # pending, processing, completed, failed
    error_message = db.Column(db.Text)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'records_processed': self.records_processed,
            'status': self.status,
            'error_message': self.error_message,
            'uploaded_at': self.uploaded_at.isoformat(),
            'processed_at': self.processed_at.isoformat() if self.processed_at else None
        }

class TechNews(db.Model):
    __tablename__ = 'tech_news'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    link = db.Column(db.String(500))
    summary = db.Column(db.Text)
    source = db.Column(db.String(100))  # TechCrunch, Layoffs.fyi, etc.
    published_date = db.Column(db.String(200))
    scraped_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'link': self.link,
            'summary': self.summary,
            'source': self.source,
            'published_date': self.published_date,
            'scraped_at': self.scraped_at.isoformat(),
            'created_at': self.created_at.isoformat()
        }
