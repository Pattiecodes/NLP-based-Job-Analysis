"""
Daily scraping scheduler for automatic data refresh.
"""
import logging
import os
import threading
import time
from datetime import datetime, timedelta

from data_processor import get_processor
from models import TechNews, db
from scraper import scrape_job_postings, scrape_tech_news

logger = logging.getLogger(__name__)

_scheduler_thread = None
_stop_event = threading.Event()


def _seconds_until_next_midnight():
    now = datetime.now()
    next_midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return max((next_midnight - now).total_seconds(), 1)


def _save_news_articles(news_articles):
    saved_count = 0
    for article in news_articles:
        existing = TechNews.query.filter_by(title=article.get('title')).first()
        if existing:
            continue

        news = TechNews(
            title=article.get('title', 'No Title'),
            link=article.get('link', ''),
            summary=article.get('summary', ''),
            source=article.get('source', 'Unknown'),
            published_date=article.get('published', datetime.now().isoformat()),
            scraped_at=datetime.now()
        )
        db.session.add(news)
        saved_count += 1

    db.session.commit()
    return saved_count


def _run_daily_scrape(app):
    logger.info('Daily scraper started. Waiting for next 12:00 AM run...')

    while not _stop_event.is_set():
        wait_seconds = _seconds_until_next_midnight()
        logger.info('Next scheduled scrape in %.1f minutes', wait_seconds / 60)

        interrupted = _stop_event.wait(timeout=wait_seconds)
        if interrupted:
            break

        try:
            with app.app_context():
                jobs = scrape_job_postings(query='software engineer', limit=100)
                processor = get_processor()
                job_stats = processor.process_batch_jobs(jobs, source='scheduler')

                news_articles = scrape_tech_news()
                saved_news = _save_news_articles(news_articles)

                logger.info(
                    'Scheduled scrape complete: jobs total=%s processed=%s skipped=%s, news scraped=%s saved=%s',
                    job_stats.get('total', 0),
                    job_stats.get('processed', 0),
                    job_stats.get('skipped', 0),
                    len(news_articles),
                    saved_news
                )
        except Exception as exc:
            logger.error('Scheduled scraping failed: %s', exc, exc_info=True)


def start_daily_scraper(app):
    """Start background scheduler thread for midnight scraping."""
    global _scheduler_thread

    if os.getenv('DISABLE_DAILY_SCRAPER', '0') == '1':
        logger.info('Daily scraper is disabled via DISABLE_DAILY_SCRAPER=1')
        return

    if _scheduler_thread and _scheduler_thread.is_alive():
        return

    _stop_event.clear()
    _scheduler_thread = threading.Thread(
        target=_run_daily_scrape,
        args=(app,),
        daemon=True,
        name='daily-scraper-thread'
    )
    _scheduler_thread.start()
