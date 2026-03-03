"""
Scraping Routes - Web scraping operations
"""
from flask import Blueprint, jsonify, request
from models import db, TechNews, JobPosting, JobSkill
from scraper import scrape_tech_news, scrape_job_postings, get_min_scrape_jobs
from data_processor import get_processor
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)

bp = Blueprint('scraping', __name__, url_prefix='/api/scraping')

@bp.route('/news/trigger', methods=['POST'])
def trigger_news_scraping():
    """Trigger tech news scraping"""
    try:
        # Scrape news
        news_articles = scrape_tech_news()
        
        # Save to database
        saved_count = 0
        for article in news_articles:
            # Check if news already exists
            existing = TechNews.query.filter_by(title=article['title']).first()
            if not existing:
                news = TechNews(
                    title=article['title'],
                    link=article['link'],
                    summary=article['summary'],
                    source=article['source'],
                    published_date=article['published'],
                    scraped_at=datetime.now()
                )
                db.session.add(news)
                saved_count += 1
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'Scraped {len(news_articles)} articles, saved {saved_count} new articles',
            'scraped': len(news_articles),
            'saved': saved_count
        })
    except Exception as e:
        logger.error(f"Error in news scraping: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/news/latest', methods=['GET'])
def get_latest_news():
    """Get latest scraped tech news"""
    try:
        limit = request.args.get('limit', 10, type=int)
        news = TechNews.query.order_by(TechNews.scraped_at.desc()).limit(limit).all()
        
        return jsonify({
            'news': [n.to_dict() for n in news],
            'count': len(news)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/jobs/trigger', methods=['POST'])
def trigger_job_scraping():
    """Trigger job posting scraping with NLP processing"""
    try:
        cron_secret = os.getenv('CRON_SECRET')
        if cron_secret:
            provided_secret = request.headers.get('X-Cron-Secret') or request.args.get('cron_secret')
            if provided_secret != cron_secret:
                return jsonify({'error': 'Unauthorized'}), 401

        # Get parameters
        query = request.json.get('query', 'software engineer') if request.json else 'software engineer'
        requested_limit = request.json.get('limit', 50) if request.json else 50
        source = request.json.get('source', 'web_scraper') if request.json else 'web_scraper'
        try:
            requested_limit = int(requested_limit)
        except (TypeError, ValueError):
            requested_limit = 50

        if source not in ['web_scraper', 'scheduler']:
            source = 'web_scraper'

        # Enforce at least configured minimum jobs per user request
        min_scrape_jobs = get_min_scrape_jobs()
        limit = max(min_scrape_jobs, requested_limit)
        
        # Scrape jobs
        jobs = scrape_job_postings(query=query, limit=limit)
        
        # Process jobs through NLP and ML pipeline
        processor = get_processor()
        stats = processor.process_batch_jobs(jobs, source=source)
        
        return jsonify({
            'status': 'success',
            'message': f'Scraped {stats["total"]} jobs, processed {stats["processed"]} new jobs through NLP pipeline',
            'requested_limit': requested_limit,
            'min_scrape_jobs': min_scrape_jobs,
            'effective_limit': limit,
            'source': source,
            'scraped': stats['total'],
            'saved': stats['processed'],
            'skipped': stats['skipped']
        })
    except Exception as e:
        logger.error(f"Error in job scraping: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/stats', methods=['GET'])
def get_scraping_stats():
    """Get statistics about scraped data"""
    try:
        total_news = TechNews.query.count()
        total_scraped_jobs = JobPosting.query.filter_by(data_source='web_scraper').count()
        total_uploaded_jobs = JobPosting.query.filter_by(data_source='upload').count()
        
        latest_news_scrape = db.session.query(db.func.max(TechNews.scraped_at)).scalar()
        latest_job_scrape = db.session.query(db.func.max(JobPosting.scraped_at)).scalar()
        
        return jsonify({
            'news': {
                'total': total_news,
                'last_scraped': latest_news_scrape.isoformat() if latest_news_scrape else None
            },
            'jobs': {
                'total_scraped': total_scraped_jobs,
                'total_uploaded': total_uploaded_jobs,
                'last_scraped': latest_job_scrape.isoformat() if latest_job_scrape else None
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
