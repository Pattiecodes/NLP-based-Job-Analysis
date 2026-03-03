"""
Web Scraping Utility Script
Run this to manually trigger web scraping for news and jobs
"""
from app import app
from scraper import scrape_tech_news, scrape_job_postings
from models import db, TechNews, JobPosting
from datetime import datetime
import sys

def scrape_and_save_news():
    """Scrape tech news and save to database"""
    print("🔍 Scraping tech news...")
    
    with app.app_context():
        news_articles = scrape_tech_news()
        print(f"Found {len(news_articles)} articles")
        
        saved_count = 0
        for article in news_articles:
            # Check if already exists
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
        print(f"✅ Saved {saved_count} new articles to database")
        return saved_count

def scrape_and_save_jobs(query='software engineer', limit=50):
    """Scrape job postings and save to database"""
    print(f"🔍 Scraping job postings for '{query}'...")
    
    with app.app_context():
        jobs = scrape_job_postings(query=query, limit=limit)
        print(f"Found {len(jobs)} job postings")
        
        saved_count = 0
        for job_data in jobs:
            # Check if already exists
            existing = JobPosting.query.filter_by(job_link=job_data['job_link']).first()
            if not existing:
                job = JobPosting(
                    job_title=job_data['job_title'],
                    company=job_data['company'],
                    job_location=job_data['job_location'],
                    job_type=job_data.get('job_type', 'Full-time'),
                    job_level=job_data.get('job_level', 'Not specified'),
                    job_summary=job_data['job_summary'],
                    job_link=job_data['job_link'],
                    data_source='web_scraper',
                    scraped_at=datetime.now(),
                    posted_date=datetime.now()
                )
                db.session.add(job)
                saved_count += 1
        
        db.session.commit()
        print(f"✅ Saved {saved_count} new jobs to database")
        return saved_count

def show_stats():
    """Show scraping statistics"""
    with app.app_context():
        total_news = TechNews.query.count()
        total_scraped_jobs = JobPosting.query.filter_by(data_source='web_scraper').count()
        total_uploaded_jobs = JobPosting.query.filter_by(data_source='upload').count()
        
        latest_news = db.session.query(db.func.max(TechNews.scraped_at)).scalar()
        latest_job = db.session.query(db.func.max(JobPosting.scraped_at)).scalar()
        
        print("\n📊 Scraping Statistics:")
        print(f"   News Articles: {total_news}")
        print(f"   Last news scrape: {latest_news or 'Never'}")
        print(f"   Scraped Jobs: {total_scraped_jobs}")
        print(f"   Uploaded Jobs: {total_uploaded_jobs}")
        print(f"   Last job scrape: {latest_job or 'Never'}")

if __name__ == '__main__':
    print("=" * 60)
    print("Web Scraping Utility")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'news':
            scrape_and_save_news()
        elif command == 'jobs':
            query = sys.argv[2] if len(sys.argv) > 2 else 'software engineer'
            limit = int(sys.argv[3]) if len(sys.argv) > 3 else 50
            scrape_and_save_jobs(query=query, limit=limit)
        elif command == 'all':
            scrape_and_save_news()
            scrape_and_save_jobs()
        elif command == 'stats':
            show_stats()
        else:
            print(f"Unknown command: {command}")
    else:
        print("\nUsage:")
        print("  python scrape_data.py news         - Scrape tech news")
        print("  python scrape_data.py jobs [query] [limit] - Scrape job postings")
        print("  python scrape_data.py all          - Scrape everything")
        print("  python scrape_data.py stats        - Show statistics")
        print("\nExamples:")
        print("  python scrape_data.py news")
        print("  python scrape_data.py jobs 'data scientist' 30")
        print("  python scrape_data.py all")
