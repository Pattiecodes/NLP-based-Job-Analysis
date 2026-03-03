import sys
import logging
logging.basicConfig(level=logging.DEBUG)

print("=== Testing Scraper Direct Call ===", file=sys.stderr)
sys.stderr.flush()

from scraper import scrape_job_postings

print("Calling scrape_job_postings...", file=sys.stderr)
sys.stderr.flush()

jobs = scrape_job_postings('python developer', limit=3)

print(f"Returned {len(jobs)} jobs", file=sys.stderr)
sys.stderr.flush()

for i, job in enumerate(jobs):
    print(f"\n=== Job {i} ===", file=sys.stderr)
    for key, val in job.items():
        print(f"{key}: {val}", file=sys.stderr)
    sys.stderr.flush()

print("\n=== Now testing save ===", file=sys.stderr)
sys.stderr.flush()

from app import app
from models import db, JobPosting
from data_processor import DataProcessor

with app.app_context():
    processor = DataProcessor()
    
    for i, job in enumerate(jobs[:1]):
        print(f"\nProcessing job {i}: {job.get('job_title')}", file=sys.stderr)
        
        job_link = job.get('job_link', '')
        print(f"  job_link: '{job_link}'", file=sys.stderr)
        
        # Check if exists
        existing = JobPosting.query.filter_by(job_link=job_link).first()
        print(f"  Exists in DB: {existing is not None}", file=sys.stderr)
        
        # Try to save
        result = processor.process_and_save_job(job, source='web_scraper')
        print(f"  Save result: {result}", file=sys.stderr)
        sys.stderr.flush()
