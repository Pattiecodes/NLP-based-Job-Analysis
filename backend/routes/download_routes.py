from flask import Blueprint, make_response
import csv
import io
from sqlalchemy import func
from models import db, JobPosting, JobSkill, TrendingSkill, AnalysisResult

download_routes = Blueprint('download_routes', __name__)


def _format_date(value):
    if not value:
        return ''
    if hasattr(value, 'strftime'):
        return value.strftime('%Y-%m-%d')
    return str(value)


def _format_datetime(value):
    if not value:
        return ''
    if hasattr(value, 'strftime'):
        return value.strftime('%Y-%m-%d %H:%M:%S')
    return str(value)

@download_routes.route('/api/download/jobs', methods=['GET'])
def download_jobs():
    """Download all job postings as CSV"""
    try:
        jobs = JobPosting.query.all()
        
        if not jobs:
            return {'error': 'No job postings found'}, 404
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['ID', 'Title', 'Company', 'Location', 'Job Level', 'Job Type', 'Job Category', 'Data Source', 'Posted Date'])
        
        # Write data
        for job in jobs:
            writer.writerow([
                job.id,
                job.job_title or '',
                job.company or '',
                job.job_location or '',
                job.job_level or '',
                job.job_type or '',
                job.job_category or '',
                job.data_source or '',
                _format_date(job.posted_date)
            ])
        
        # Create response
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = 'attachment; filename=job_postings.csv'
        response.headers['Content-Type'] = 'text/csv'
        
        return response
    except Exception as e:
        return {'error': str(e)}, 500

@download_routes.route('/api/download/skills', methods=['GET'])
def download_skills():
    """Download top trending skills as CSV"""
    try:
        # Words to exclude (same as dashboard)
        exclude_words = {
            'benefits', 'compensation', 'employee', 'employees', 'experience',
            'team', 'leadership', 'management', 'ability', 'skills', 'skill',
            'training', 'knowledge', 'understanding', 'background',
            'degree', 'certificate', 'certification', 'years', 'year',
            'required', 'preferred', 'strong', 'excellent', 'good'
        }
        
        all_skills = TrendingSkill.query.order_by(TrendingSkill.mention_count.desc()).all()
        
        # Filter out meaningless words
        skills = [s for s in all_skills if s.skill_name.lower() not in exclude_words]
        
        if not skills:
            return {'error': 'No skills found'}, 404
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Rank', 'Skill', 'Count', 'Category'])
        
        # Write data
        for idx, skill in enumerate(skills, 1):
            writer.writerow([
                idx,
                skill.skill_name,
                skill.mention_count,
                skill.category or 'General'
            ])
        
        # Create response
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = 'attachment; filename=top_skills.csv'
        response.headers['Content-Type'] = 'text/csv'
        
        return response
    except Exception as e:
        return {'error': str(e)}, 500

@download_routes.route('/api/download/analysis', methods=['GET'])
def download_analysis():
    """Download NLP-processed job analysis results as CSV"""
    try:
        # Get all jobs with NLP analysis fields + aggregated extracted skill count
        rows = db.session.query(
            JobPosting.id,
            JobPosting.job_title,
            JobPosting.company,
            JobPosting.job_location,
            JobPosting.job_category,
            JobPosting.job_type,
            JobPosting.job_level,
            JobPosting.data_source,
            JobPosting.cluster_id,
            JobPosting.posted_date,
            JobPosting.scraped_at,
            func.count(JobSkill.id).label('skill_count')
        ).outerjoin(
            JobSkill, JobSkill.job_id == JobPosting.id
        ).group_by(
            JobPosting.id,
            JobPosting.job_title,
            JobPosting.company,
            JobPosting.job_location,
            JobPosting.job_category,
            JobPosting.job_type,
            JobPosting.job_level,
            JobPosting.data_source,
            JobPosting.cluster_id,
            JobPosting.posted_date,
            JobPosting.scraped_at
        ).all()

        if not rows:
            return {'error': 'No analysis results found'}, 404
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header - comprehensive NLP analysis results
        writer.writerow([
            'Job ID', 'Title', 'Company', 'Location', 
            'NLP Category', 'Job Type', 'Job Level', 
            'Data Source', 'Cluster ID', 'Posted Date', 'Scraped At',
            'Extracted Skills Count'
        ])
        
        # Write data - showing NLP analysis results
        for row in rows:
            writer.writerow([
                row.id,
                row.job_title or '',
                row.company or '',
                row.job_location or '',
                row.job_category or 'Uncategorized',
                row.job_type or '',
                row.job_level or '',
                row.data_source or '',
                row.cluster_id if row.cluster_id is not None else 'N/A',
                _format_date(row.posted_date),
                _format_datetime(row.scraped_at),
                int(row.skill_count or 0)
            ])
        
        # Create response
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = 'attachment; filename=nlp_analysis_results.csv'
        response.headers['Content-Type'] = 'text/csv'
        
        return response
    except Exception as e:
        print(f"Error in download_analysis: {str(e)}")
        return {'error': str(e)}, 500

@download_routes.route('/api/download/clusters', methods=['GET'])
def download_clusters():
    """Download clustering results as CSV"""
    try:
        clustering_result = AnalysisResult.query.filter_by(analysis_type='clustering').first()
        
        if not clustering_result:
            return {'error': 'No clustering results found'}, 404
        
        if not clustering_result.result_data or 'clusters' not in clustering_result.result_data:
            return {'error': 'Invalid clustering data format'}, 500
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Cluster ID', 'Job Count', 'Top Keywords'])
        
        # Write data
        clusters = clustering_result.result_data.get('clusters', [])
        
        if not clusters:
            return {'error': 'No clusters found in results'}, 404
        
        for cluster in clusters:
            keywords = cluster.get('top_keywords', [])
            keywords_str = ', '.join(keywords) if isinstance(keywords, list) else str(keywords)
            writer.writerow([
                cluster.get('cluster_id', ''),
                cluster.get('job_count', 0),
                keywords_str
            ])
        
        # Create response
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = 'attachment; filename=clusters.csv'
        response.headers['Content-Type'] = 'text/csv'
        
        return response
    except Exception as e:
        print(f"Error in download_clusters: {str(e)}")
        return {'error': str(e)}, 500

@download_routes.route('/api/download/topics', methods=['GET'])
def download_topics():
    """Download topic modeling results as CSV"""
    try:
        topic_result = AnalysisResult.query.filter_by(analysis_type='topic_modeling').first()
        
        if not topic_result:
            return {'error': 'No topic modeling results found'}, 404
        
        if not topic_result.result_data or 'topics' not in topic_result.result_data:
            return {'error': 'Invalid topic modeling data format'}, 500
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Topic ID', 'Weight', 'Keywords'])
        
        # Write data
        topics = topic_result.result_data.get('topics', [])
        
        if not topics:
            return {'error': 'No topics found in results'}, 404
        
        for topic in topics:
            keywords = topic.get('keywords', [])
            keywords_str = ', '.join(keywords) if isinstance(keywords, list) else str(keywords)
            writer.writerow([
                topic.get('topic_id', ''),
                topic.get('weight', 0),
                keywords_str
            ])
        
        # Create response
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = 'attachment; filename=topics.csv'
        response.headers['Content-Type'] = 'text/csv'
        
        return response
    except Exception as e:
        print(f"Error in download_topics: {str(e)}")
        return {'error': str(e)}, 500
