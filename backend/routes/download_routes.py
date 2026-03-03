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
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['ID', 'Title', 'Company', 'Location', 'Job Level', 'Job Type', 'Job Skills', 'Summary'])
        
        # Write data
        for job in jobs:
            # Get skills as comma-separated string
            skill_names = ', '.join([skill.skill_name for skill in job.skills]) if job.skills else ''
            
            writer.writerow([
                job.id,
                job.job_title,
                job.company,
                job.job_location or '',
                job.job_level or '',
                job.job_type or '',
                skill_names,
                job.job_summary or ''
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
        skills = TrendingSkill.query.order_by(TrendingSkill.mention_count.desc()).all()
        
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
    """Download all analysis results as CSV"""
    try:
        results = AnalysisResult.query.all()
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['ID', 'Analysis Type', 'Model Version', 'Created At', 'Data Summary'])
        
        # Write data
        for result in results:
            # Create summary of result data
            if result.analysis_type == 'clustering':
                summary = f"Clusters: {result.result_data.get('n_clusters', 'N/A')}"
            elif result.analysis_type == 'topic_modeling':
                summary = f"Topics: {result.result_data.get('n_topics', 'N/A')}"
            else:
                summary = 'Other analysis'
            
            writer.writerow([
                result.id,
                result.analysis_type,
                result.model_version or '',
                result.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                summary
            ])
        
        # Create response
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = 'attachment; filename=analysis_results.csv'
        response.headers['Content-Type'] = 'text/csv'
        
        return response
    except Exception as e:
        return {'error': str(e)}, 500

@download_routes.route('/api/download/clusters', methods=['GET'])
def download_clusters():
    """Download clustering results as CSV"""
    try:
        clustering_result = AnalysisResult.query.filter_by(analysis_type='clustering').first()
        
        if not clustering_result:
            return {'error': 'No clustering results found'}, 404
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Cluster ID', 'Job Count', 'Top Keywords'])
        
        # Write data
        clusters = clustering_result.result_data.get('clusters', [])
        for cluster in clusters:
            keywords_str = ', '.join(cluster.get('top_keywords', []))
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
        return {'error': str(e)}, 500

@download_routes.route('/api/download/topics', methods=['GET'])
def download_topics():
    """Download topic modeling results as CSV"""
    try:
        topic_result = AnalysisResult.query.filter_by(analysis_type='topic_modeling').first()
        
        if not topic_result:
            return {'error': 'No topic modeling results found'}, 404
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Topic ID', 'Weight', 'Keywords'])
        
        # Write data
        topics = topic_result.result_data.get('topics', [])
        for topic in topics:
            keywords_str = ', '.join(topic.get('keywords', []))
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
        return {'error': str(e)}, 500
