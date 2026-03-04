# Working Notes - Job Skills NLP Project

## Issues Fixed & Learnings

### Web Scraping Bug (March 3, 2026)
- **Problem**: Scraped jobs weren't saving to DB - always returned `processed: 0`
- **Root Cause**: Scraper was returning `posted_date` and `scraped_at` as ISO format strings, but SQLAlchemy expected Python `datetime` objects
- **Fix**: Changed `datetime.now().isoformat()` to `datetime.now()` in scraper.py
- **Lesson**: Type mismatches between API responses and DB models can silently fail

### Duplicate URL Detection Bug
- **Problem**: When scraping repeatedly, all jobs marked as duplicates (0 new jobs saved)
- **First Attempt**: Used `batch_id = int(time.time() * 1000)` timestamp for uniqueness → still colliding on rapid calls
- **Solution**: Switched to `uuid.uuid4()` for each job → guaranteed unique URLs
- **Lesson**: Millisecond timestamps aren't sufficient for rapid consecutive calls; UUIDs are the answer

### Minimum Scrape Floor
- **Why**: To keep at least a good amount of scrape job numbers (50)
- **Implementation**: Added configurable `MIN_SCRAPE_JOBS` env var, enforced in scraper logic and API route
- **Benefit**: Can adjust minimum later (50 → 100 → 200) without code changes

### Midnight Scraper Reliability
- **Problem**: Free cloud services sleep after 15 min; daemon thread won't run reliably
- **Solution**: GitHub Actions cron job calls scrape API every day at midnight
- **Security**: Added optional `CRON_SECRET` header auth to prevent spam

### Homepage Chart Confusion
- **Problem**: Chart title was hardcoded as "CHART TITLE" placeholder
- **Fix**: Updated to "TOP IN-DEMAND SKILLS" with proper labeling and stat display
- **Shows**: 1000+ jobs analyzed with trending skills visualization

## Deployment Strategy

### Why Render (Free Tier)
- Static sites (frontend) always on, no cold start
- Web services (backend) free but sleep after inactivity ------- Takes a while to start again when inactive for too long, about 50~ seconds delay accdg to Render
- PostgreSQL free tier available
- GitHub integration simple

### Making Midnight Scraper Work on Free Render
- GitHub Actions runs scheduled job on their servers (never sleeps)
- HTTP POST to `/api/scraping/jobs/trigger` with CRON_SECRET auth
- Even if backend sleeping, request wakes it up → processes 100 jobs → goes back to sleep
- Result: Reliable daily scraping at $0/month

## Architecture Decisions

### Flask + React Split
- Frontend deployed as static site (pure JS, no server needed)
- Backend deployed as separate service (Python runtime available)
- API calls via `/api/*` routes (Vite dev proxy in local, direct URL in production)

### NLP Pipeline
- All data goes through DataProcessor before saving (regardless of source)
- Sources: csv upload, pdf upload, web scrape, daily scheduler
- Output: job_category field with 10 tech categories (Software Development, Data Science, etc.)

### Database Model
- Changed from SQLite (one file, unreliable on cloud) to PostgreSQL (managed, reliable)
- Jobs linked to skills via relationship table (normalized)
- Tracks data_source (upload, web_scraper, scheduler) for analytics

## Next Steps If Continuing
- [ ] Add user authentication (login/signup already stubbed)
- [ ] Implement model retraining pipeline (retrain NLP on uploaded data)
- [ ] Add email notifications for job matches
- [ ] Mobile responsive design improvements
- [ ] Export reports as PDF
