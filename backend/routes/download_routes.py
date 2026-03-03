from flask import Blueprint, send_file, make_response
import csv
import io
from models import db, JobPosting, TrendingSkill, AnalysisResult

download_routes = Blueprint('download_routes', __name__)

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
                job.posted_date.strftime('%Y-%m-%d') if job.posted_date else ''
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
        # Get all jobs with their NLP analysis results
        jobs = JobPosting.query.all()
        
        if not jobs:
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
        for job in jobs:
            skill_count = len(job.skills) if job.skills else 0
            
            writer.writerow([
                job.id,
                job.job_title or '',
                job.company or '',
                job.job_location or '',
                job.job_category or 'Uncategorized',  # NLP categorization
                job.job_type or '',
                job.job_level or '',
                job.data_source or '',
                job.cluster_id if job.cluster_id is not None else 'N/A',
                job.posted_date.strftime('%Y-%m-%d') if job.posted_date else '',
                job.scraped_at.strftime('%Y-%m-%d %H:%M:%S') if job.scraped_at else '',
                skill_count  # Number of skills extracted by NLP
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
