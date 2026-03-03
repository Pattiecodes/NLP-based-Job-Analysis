"""
Data Processing Pipeline
Processes uploaded and scraped data through NLP and ML models
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Optional
import logging
from datetime import datetime
import pickle
import os

from models import db, JobPosting, JobSkill, TrendingSkill
from nlp_categorizer import get_categorizer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataProcessor:
    """Process job data through NLP and ML pipeline"""
    
    def __init__(self):
        self.categorizer = get_categorizer()
        self.vectorizer = None
        self.kmeans_model = None
        self.lda_model = None
        
        # Try to load existing models
        self.load_models()
    
    def load_models(self):
        """Load pre-trained ML models if they exist"""
        try:
            # Load TF-IDF vectorizer
            vectorizer_path = '../output/tfidf_vectorizer.pkl'
            if os.path.exists(vectorizer_path):
                with open(vectorizer_path, 'rb') as f:
                    self.vectorizer = pickle.load(f)
                logger.info("Loaded TF-IDF vectorizer")
            
            # Load K-Means model
            kmeans_path = '../output/kmeans_model.pkl'
            if os.path.exists(kmeans_path):
                with open(kmeans_path, 'rb') as f:
                    self.kmeans_model = pickle.load(f)
                logger.info("Loaded K-Means model")
            
            # Load LDA model
            lda_path = '../output/lda_model.pkl'
            if os.path.exists(lda_path):
                with open(lda_path, 'rb') as f:
                    self.lda_model = pickle.load(f)
                logger.info("Loaded LDA model")
                
        except Exception as e:
            logger.warning(f"Could not load models: {e}")
    
    def process_single_job(self, job_data: Dict, source: str = 'upload') -> Dict:
        """
        Process a single job posting through NLP pipeline
        
        Args:
            job_data: Raw job data
            source: Data source ('upload', 'web_scraper', 'api')
            
        Returns:
            Processed job data with NLP categorization
        """
        # Run NLP categorization
        nlp_results = self.categorizer.analyze_job(job_data)
        
        # Update job data with NLP results
        processed_data = {
            **job_data,
            'job_type': nlp_results['job_type'],
            'job_level': nlp_results['job_level'],
            'job_category': nlp_results['job_category'],
            'data_source': source,
            'extracted_skills': nlp_results['extracted_skills']
        }
        
        # Predict cluster if model is loaded
        if self.kmeans_model and self.vectorizer:
            try:
                text = f"{job_data.get('job_title', '')} {job_data.get('job_summary', '')}"
                if text.strip():
                    X = self.vectorizer.transform([text])
                    cluster_id = self.kmeans_model.predict(X)[0]
                    processed_data['cluster_id'] = int(cluster_id)
            except Exception as e:
                logger.warning(f"Could not predict cluster: {e}")
        
        return processed_data
    
    def process_and_save_job(self, job_data: Dict, source: str = 'upload') -> Optional[JobPosting]:
        """
        Process and save a single job to database
        
        Args:
            job_data: Raw job data
            source: Data source
            
        Returns:
            Saved JobPosting object or None if failed
        """
        try:
            # Check if job already exists
            job_link = job_data.get('job_link', '')
            if job_link:
                existing = JobPosting.query.filter_by(job_link=job_link).first()
                if existing:
                    logger.info(f"Job already exists: {job_link}")
                    return None
            
            # Process through NLP
            processed = self.process_single_job(job_data, source)
            
            # Create JobPosting with NLP results
            job = JobPosting(
                job_title=processed.get('job_title', ''),
                company=processed.get('company', ''),
                job_location=processed.get('job_location', ''),
                job_type=processed.get('job_type', 'Full-time'),
                job_level=processed.get('job_level', 'Mid level'),
                job_category=processed.get('job_category'),  # NLP categorization
                job_summary=processed.get('job_summary', ''),
                job_link=job_link or f"internal_{datetime.now().timestamp()}",
                search_country=processed.get('search_country'),
                search_city=processed.get('search_city'),
                cluster_id=processed.get('cluster_id'),  # ML clustering
                data_source=source,
                scraped_at=datetime.now() if source == 'web_scraper' else None,
                posted_date=processed.get('posted_date')
            )
            
            db.session.add(job)
            db.session.flush()  # Get job.id
            
            # Save extracted skills
            for skill_name in processed.get('extracted_skills', []):
                skill = JobSkill(
                    job_id=job.id,
                    skill_name=skill_name,
                    is_technical=True
                )
                db.session.add(skill)
                
                # Update trending skills
                self.update_trending_skill(skill_name)
            
            db.session.commit()
            logger.info(f"Saved job: {job.job_title} ({source})")
            return job
            
        except Exception as e:
            logger.error(f"Error processing job: {e}")
            db.session.rollback()
            return None
    
    def update_trending_skill(self, skill_name: str):
        """Update or create trending skill"""
        skill = TrendingSkill.query.filter_by(skill_name=skill_name).first()
        if skill:
            skill.mention_count += 1
        else:
            skill = TrendingSkill(
                skill_name=skill_name,
                mention_count=1,
                is_technical=True,
                category='Technical'
            )
            db.session.add(skill)
    
    def process_csv_file(self, filepath: str, source: str = 'upload') -> Dict:
        """
        Process a CSV file of job postings
        
        Args:
            filepath: Path to CSV file
            source: Data source
            
        Returns:
            Processing statistics
        """
        try:
            df = pd.read_csv(filepath)
            
            # Map common CSV column names
            column_mapping = {
                'title': 'job_title',
                'job title': 'job_title',
                'position': 'job_title',
                'location': 'job_location',
                'summary': 'job_summary',
                'description': 'job_summary',
                'link': 'job_link',
                'url': 'job_link'
            }
            
            # Rename columns to match our schema
            df.columns = df.columns.str.lower().str.strip()
            df = df.rename(columns=column_mapping)
            
            processed_count = 0
            skipped_count = 0
            
            for _, row in df.iterrows():
                job_data = row.to_dict()
                result = self.process_and_save_job(job_data, source)
                if result:
                    processed_count += 1
                else:
                    skipped_count += 1
            
            return {
                'total': len(df),
                'processed': processed_count,
                'skipped': skipped_count,
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Error processing CSV: {e}")
            return {
                'total': 0,
                'processed': 0,
                'skipped': 0,
                'status': 'error',
                'error': str(e)
            }
    
    def process_batch_jobs(self, jobs: List[Dict], source: str = 'upload') -> Dict:
        """
        Process a batch of job postings
        
        Args:
            jobs: List of job data dictionaries
            source: Data source
            
        Returns:
            Processing statistics
        """
        processed_count = 0
        skipped_count = 0
        
        for job_data in jobs:
            result = self.process_and_save_job(job_data, source)
            if result:
                processed_count += 1
            else:
                skipped_count += 1
        
        return {
            'total': len(jobs),
            'processed': processed_count,
            'skipped': skipped_count,
            'status': 'success'
        }


# Global processor instance
_processor = None

def get_processor() -> DataProcessor:
    """Get or create global processor instance"""
    global _processor
    if _processor is None:
        _processor = DataProcessor()
    return _processor


def process_uploaded_file(filepath: str, source: str = 'upload') -> Dict:
    """
    Convenience function to process an uploaded file
    
    Args:
        filepath: Path to uploaded file
        source: Data source
        
    Returns:
        Processing statistics
    """
    processor = get_processor()
    return processor.process_csv_file(filepath, source)


def process_job(job_data: Dict, source: str = 'upload') -> Optional[JobPosting]:
    """
    Convenience function to process a single job
    
    Args:
        job_data: Job data
        source: Data source
        
    Returns:
        Saved JobPosting or None
    """
    processor = get_processor()
    return processor.process_and_save_job(job_data, source)


if __name__ == '__main__':
    # Test the processor
    test_job = {
        'job_title': 'Senior Python Developer',
        'company': 'Tech Corp',
        'job_location': 'San Francisco, CA',
        'job_summary': 'We are seeking an experienced Python developer with Django and AWS experience.',
        'job_link': 'https://example.com/job/123'
    }
    
    processor = DataProcessor()
    processed = processor.process_single_job(test_job, 'test')
    
    print("Processed Job Data:")
    print(f"  Type: {processed['job_type']}")
    print(f"  Level: {processed['job_level']}")
    print(f"  Category: {processed['job_category']}")
    print(f"  Skills: {', '.join(processed['extracted_skills'])}")
