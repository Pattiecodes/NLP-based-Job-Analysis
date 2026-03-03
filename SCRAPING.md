# Web Scraping Features

## Overview
The platform now includes web scraping capabilities to continuously gather:
- **Tech News**: Industry news about layoffs, hiring trends, tech companies
- **Job Postings**: Fresh job listings from various sources

## Setup

### 1. Install Dependencies
```bash
cd backend
pip install beautifulsoup4 feedparser requests lxml
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

### 2. Update Database
The database schema has been updated with new fields. Re-initialize the database:

```bash
cd backend
python init_db.py --drop
```
Then re-seed the data:
```bash
python seed_data.py
```

## Data Source Tracking

### JobPosting Model Updates
- **data_source** field: Tracks where data came from ('upload', 'web_scraper', 'api')
- **scraped_at** field: Timestamp of when data was scraped

### TechNews Model (NEW)
Stores scraped news articles:
- title
- link  
- summary
- source (TechCrunch, Layoffs.fyi, etc.)
- published_date
- scraped_at
- created_at

## Usage

### Via API Endpoints

1. **Scrape Tech News**
```bash
POST /api/scraping/news/trigger
```
Response:
```json
{
  "status": "success",
  "message": "Scraped 10 articles, saved 8 new articles",
  "scraped": 10,
  "saved": 8
}
```

2. **Get Latest News**
```bash
GET /api/scraping/news/latest?limit=10
```

3. **Scrape Job Postings**
```bash
POST /api/scraping/jobs/trigger
Body: {
  "query": "software engineer",
  "limit": 50
}
```

4. **Get Scraping Stats**
```bash
GET /api/scraping/stats
```

### Via Command Line

Use the `scrape_data.py` utility script:

```bash
# Scrape tech news
python scrape_data.py news

# Scrape job postings
python scrape_data.py jobs "data scientist" 30

# Scrape everything
python scrape_data.py all

# Show statistics
python scrape_data.py stats
```

### Via Frontend

**Home Page:**
- News section now displays real scraped articles
- "Refresh" button triggers news scraping
- Shows source and date for each article

## Scraping Sources

### Tech News
1. **TechCrunch RSS Feed** - Latest tech industry news
2. **Layoffs.fyi** - Tech layoff information
3. Fallback articles when scraping fails

### Job Postings
1. **Indeed.com** - Job search engine (respects robots.txt)
2. **LinkedIn** - Can be added if API access available
3. Sample data generator for testing

## Important Notes

### Rate Limiting
- Built-in delays to avoid overwhelming servers
- Respects robots.txt policies
- Uses appropriate User-Agent headers

### Data Deduplication
- News: Checks by title before saving
- Jobs: Checks by job_link before saving
- Prevents duplicate entries

### Production Considerations

**Official APIs First:**
Use official APIs when available instead of web scraping:
- LinkedIn Jobs API
- Indeed Publisher API
- Remote.co API

**Scheduled Scraping:**
Use Celery or cron jobs for periodic scraping:
```python
# Example: Run every hour
from celery import Celery
from scraper import scrape_tech_news

@celery.task
def scheduled_news_scrape():
    scrape_tech_news()
```

**Legal Compliance:**
- Review Terms of Service for each website
- Respect robots.txt
- Use rate limiting
- Consider data privacy laws

## Troubleshooting

**No news showing up:**
1. Click "Refresh" button on Home page
2. Or run: `python scrape_data.py news`
3. Check API response: `GET /api/scraping/news/latest`

**Scraping errors:**
- Check internet connection
- Website structure may have changed
- Check console/logs for error messages
- Fallback to sample data automatically

**Database errors:**
- Run `python init_db.py --drop` to recreate tables
- Re-run `python seed_data.py`

## Future Enhancements

1. **More Sources:** Add LinkedIn, Glassdoor, Remote.c
2. **Scheduling:** Celery tasks for automatic scraping
3. **NLP Analysis:** Analyze scraped content for insights
4. **Filtering:** User-defined filters for news/jobs
5. **Notifications:** Alert users about new relevant postings
