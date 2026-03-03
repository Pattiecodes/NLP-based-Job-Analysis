# ML & NLP Data Processing Pipeline

## Overview
All job data (uploaded and web scraped) now goes through an NLP and ML processing pipeline before being saved to the database. This ensures consistent categorization, skill extraction, and cluster assignment.

## Pipeline Architecture

```
Data Input (Upload/Scrape)
        ↓
  NLP Categorizer
  - Job Type Classification
  - Job Level Classification  
  - Job Domain/Category
  - Skill Extraction
        ↓
   ML Models (Optional)
  - TF-IDF Vectorization
  - K-Means Clustering
  - LDA Topic Modeling
        ↓
   Save to Database
  - JobPosting with categories
  - JobSkills extracted
  - TrendingSkills updated
```

## NLP Categorizer

### Features
The `nlp_categorizer.py` uses keyword matching and NLP techniques to:

1. **Job Type Classification**
   - Full-time
   - Part-time
   - Contract
   - Internship
   - Remote

2. **Job Level Classification**
   - Entry level
   - Mid level
   - Senior level
   - Manager
   - Executive

3. **Job Domain/Category**
   - Software Development
   - Data Science
   - DevOps
   - Product Management
   - Design
   - Marketing
   - Sales
   - Finance
   - Security

4. **Skill Extraction**
   - Extracts technical skills from job text
   - Recognizes 50+ common tech skills
   - Uses word boundary matching for accuracy

### Usage Example
```python
from nlp_categorizer import categorize_job

job_data = {
    'job_title': 'Senior Python Developer',
    'job_summary': 'We need an experienced Python dev with Django and AWS.'
}

result = categorize_job(job_data)
# Returns:
# {
#     'job_type': 'Full-time',
#     'job_level': 'Senior level',
#     'job_category': 'Software Development',
#     'extracted_skills': ['Python', 'Django', 'Aws']
# }
```

## Data Processor

The `data_processor.py` module handles the full pipeline:

### Single Job Processing
```python
from data_processor import process_job

job = process_job(job_data, source='upload')
# Automatically:
# - Runs NLP categorization
# - Predicts ML cluster (if models loaded)
# - Extracts and saves skills
# - Updates trending skills
# - Saves to database
```

### Batch CSV Processing
```python
from data_processor import process_uploaded_file

stats = process_uploaded_file('jobs.csv', source='upload')
# Returns:
# {
#     'total': 100,
#     'processed': 95,
#     'skipped': 5,
#     'status': 'success'
# }
```

## Database Schema Updates

### JobPosting Model
New fields added:
- `job_category` (String): NLP-derived domain category
- `cluster_id` (Integer): ML cluster assignment
- `data_source` (String): 'upload', 'web_scraper', or 'api'
- `scraped_at` (DateTime): When data was scraped

### JobSkill Model
- Stores extracted skills per job
- Linked to JobPosting via foreign key

### TrendingSkill Model
- Automatically updated when skills are extracted
- `mention_count` incremented for each occurrence

## API Integration

### Upload Endpoint
`POST /api/upload/file`

Now automatically processes CSV files:
1. Accepts file upload
2. Runs through NLP pipeline
3. Saves processed jobs
4. Returns statistics

Response:
```json
{
  "message": "File uploaded and processed successfully",
  "upload_id": 123,
  "filename": "20260303_120000_jobs.csv",
  "status": "completed",
  "stats": {
    "total": 50,
    "processed": 48,
    "skipped": 2
  }
}
```

### Scraping Endpoint
`POST /api/scraping/jobs/trigger`

Processes scraped jobs through pipeline:
```json
{
  "query": "data scientist",
  "limit": 50
}
```

Response:
```json
{
  "status": "success",
  "message": "Scraped 50 jobs, processed 45 new jobs through NLP pipeline",
  "scraped": 50,
  "saved": 45,
  "skipped": 5
}
```

## ML Models

### Loading Pre-trained Models
The processor automatically loads models if available:
- `output/tfidf_vectorizer.pkl` - TF-IDF vectorizer
- `output/kmeans_model.pkl` - K-Means clustering
- `output/lda_model.pkl` - LDA topic model

If models exist, jobs are automatically assigned cluster IDs.

### Training New Models
Use the Jupyter notebook `job_skills_nlp.ipynb` to:
1. Load processed job data
2. Train clustering models
3. Train topic models
4. Save models to `output/` directory

The next time data is processed, new models will be used automatically.

## Dashboard Integration

### Job Type Distribution Chart
The dashboard now uses NLP-categorized job types:
- Data is automatically categorized during processing
- No manual categorization needed
- Chart shows real distribution of job types

### Query Example
```python
from sqlalchemy import func
from models import JobPosting

# Get job type distribution
job_types = db.session.query(
    JobPosting.job_type,
    func.count(JobPosting.id).label('count')
).group_by(JobPosting.job_type).all()
```

## Setup & Installation

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Re-initialize Database
The schema has changed with new fields:
```bash
python init_db.py --drop
python seed_data.py
```

### 3. Download NLTK Data
NLTK data is downloaded automatically on first run:
- punkt tokenizer
- stopwords corpus

Or manually:
```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
```

## Testing

### Test NLP Categorizer
```bash
cd backend
python nlp_categorizer.py
```

### Test Data Processor
```bash
python data_processor.py
```

### Upload Test File
Use the Upload page to upload a CSV with columns:
- job_title (or title)
- company
- location (or job_location)
- summary (or job_summary)

The system will automatically:
- Categorize job types
- Determine job levels
- Extract skills
- Assign to clusters (if models exist)

## Benefits

1. **Consistency**: All jobs categorized the same way
2. **Automation**: No manual categorization needed
3. **Insights**: Better analytics with structured categories
4. **Scalability**: Process thousands of jobs automatically
5. **Flexibility**: Easy to add new categories/keywords
6. **Skills Tracking**: Automatic skill extraction and trending

## Future Improvements

1. **Deep Learning**: Use transformer models (BERT) for better categorization
2. **Skill Ontology**: Build comprehensive skill taxonomy
3. **Salary Prediction**: Predict salary ranges based on skills
4. **Location Analysis**: Analyze geographic job trends
5. **Company Insights**: Track hiring patterns by company
6. **Real-time Processing**: Use Celery for async processing
7. **API Integration**: Connect to LinkedIn, Indeed APIs

## Troubleshooting

**Issue**: Jobs not categorized
- Solution: Check if NLP categorizer is working: `python nlp_categorizer.py`

**Issue**: No cluster_id assigned
- Solution: Train and save ML models in notebook

**Issue**: Skills not extracted
- Solution: Ensure job_summary field has content

**Issue**: Upload fails
- Solution: Check CSV column names match expected format

## References

- NLP Categorizer: `backend/nlp_categorizer.py`
- Data Processor: `backend/data_processor.py`
- Upload Routes: `backend/routes/upload_routes.py`
- Scraping Routes: `backend/routes/scraping_routes.py`
- Models: `backend/models.py`
