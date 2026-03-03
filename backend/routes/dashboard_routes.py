"""
Dashboard Routes
"""
from flask import Blueprint, jsonify
from models import JobPosting, TrendingSkill, AnalysisResult, db
from sqlalchemy import func
import pandas as pd
import os

bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')

@bp.route('/stats', methods=['GET'])
def get_dashboard_stats():
    """Get overall dashboard statistics"""
    # Words to exclude from skill count (same as trending skills)
    exclude_words = {
        'benefits', 'compensation', 'employee', 'employees', 'experience',
        'team', 'leadership', 'management', 'ability', 'skills', 'skill',
        'training', 'knowledge', 'understanding', 'background',
        'degree', 'certificate', 'certification', 'years', 'year',
        'required', 'preferred', 'strong', 'excellent', 'good'
    }
    
    total_jobs = db.session.query(func.count(JobPosting.id)).scalar()
    total_companies = db.session.query(func.count(func.distinct(JobPosting.company))).scalar()
    total_locations = db.session.query(func.count(func.distinct(JobPosting.job_location))).scalar()
    
    # Count only valid skills (exclude meaningless words)
    all_skills = TrendingSkill.query.all()
    total_skills = len([s for s in all_skills if s.skill_name.lower() not in exclude_words])
    
    return jsonify({
        'total_jobs': total_jobs or 0,
        'total_companies': total_companies or 0,
        'total_locations': total_locations or 0,
        'total_skills': total_skills or 0
    })

@bp.route('/top-skills', methods=['GET'])
def get_top_skills():
    """Get top trending skills"""
    limit = 50
    
    # Words to exclude from trending skills
    exclude_words = {
        'benefits', 'compensation', 'employee', 'employees', 'experience',
        'team', 'leadership', 'management', 'ability', 'skills', 'skill',
        'training', 'knowledge', 'understanding', 'background',
        'degree', 'certificate', 'certification', 'years', 'year',
        'required', 'preferred', 'strong', 'excellent', 'good'
    }
    
    # Try to get from database first
    all_skills = TrendingSkill.query\
        .order_by(TrendingSkill.mention_count.desc())\
        .limit(200)\
        .all()
    
    # Filter out meaningless words
    skills = [s for s in all_skills if s.skill_name.lower() not in exclude_words][:limit]
    
    if skills:
        # Format for frontend charts (expects "Skill" and "Count" keys)
        skills_data = [
            {
                'Skill': skill.skill_name,
                'Count': skill.mention_count,
                'category': skill.category,
                'is_technical': skill.is_technical
            }
            for skill in skills
        ]
        return jsonify({
            'skills': skills_data
        })
    
    # Fallback to CSV if database is empty
    try:
        csv_path = os.path.join('..', 'output', 'top_skills.csv')
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            skills_data = df.head(limit).to_dict('records')
            return jsonify({
                'skills': skills_data,
                'source': 'csv'
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    return jsonify({'skills': []})

@bp.route('/job-distribution', methods=['GET'])
def get_job_distribution():
    """Get job distribution by level, type, location"""
    
    # Job level distribution
    job_levels = db.session.query(
        JobPosting.job_level,
        func.count(JobPosting.id).label('count')
    ).group_by(JobPosting.job_level)\
     .order_by(func.count(JobPosting.id).desc())\
     .limit(10)\
     .all()
    
    # Prefer NLP job category distribution when available
    category_count = db.session.query(func.count(JobPosting.id))\
        .filter(JobPosting.job_category.isnot(None))\
        .filter(JobPosting.job_category != '')\
        .scalar() or 0

    if category_count > 0:
        job_types = db.session.query(
            JobPosting.job_category,
            func.count(JobPosting.id).label('count')
        ).filter(JobPosting.job_category.isnot(None))\
         .filter(JobPosting.job_category != '')\
         .group_by(JobPosting.job_category)\
         .order_by(func.count(JobPosting.id).desc())\
         .all()
        job_type_source = 'nlp_category'
    else:
        job_types = db.session.query(
            JobPosting.job_type,
            func.count(JobPosting.id).label('count')
        ).group_by(JobPosting.job_type)\
         .order_by(func.count(JobPosting.id).desc())\
         .all()
        job_type_source = 'job_type'
    
    # Top locations
    top_locations = db.session.query(
        JobPosting.job_location,
        func.count(JobPosting.id).label('count')
    ).group_by(JobPosting.job_location)\
     .order_by(func.count(JobPosting.id).desc())\
     .limit(15)\
     .all()
    
    # Top companies
    top_companies = db.session.query(
        JobPosting.company,
        func.count(JobPosting.id).label('count')
    ).group_by(JobPosting.company)\
     .order_by(func.count(JobPosting.id).desc())\
     .limit(15)\
     .all()
    
    return jsonify({
        'job_levels': [{'level': level, 'count': count} for level, count in job_levels],
        'job_types': [{'type': type_, 'count': count} for type_, count in job_types],
        'job_type_source': job_type_source,
        'top_locations': [{'location': loc, 'count': count} for loc, count in top_locations],
        'top_companies': [{'company': comp, 'count': count} for comp, count in top_companies]
    })

@bp.route('/topics', methods=['GET'])
def get_topics():
    """Get LDA topic modeling results"""
    analysis = AnalysisResult.query\
        .filter_by(analysis_type='topic_modeling')\
        .order_by(AnalysisResult.created_at.desc())\
        .first()
    
    if analysis:
        return jsonify({
            'topics': analysis.result_data,
            'model_version': analysis.model_version,
            'created_at': analysis.created_at.isoformat()
        })
    
    return jsonify({'topics': []})

@bp.route('/clusters', methods=['GET'])
def get_clusters():
    """Get K-Means clustering results"""
    analysis = AnalysisResult.query\
        .filter_by(analysis_type='clustering')\
        .order_by(AnalysisResult.created_at.desc())\
        .first()
    
    if analysis:
        return jsonify({
            'clusters': analysis.result_data,
            'model_version': analysis.model_version,
            'created_at': analysis.created_at.isoformat()
        })
    
    return jsonify({'clusters': []})
