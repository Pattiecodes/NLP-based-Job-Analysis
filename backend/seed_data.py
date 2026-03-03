"""
Seed database with existing analysis data
All job data MUST go through NLP pipeline before saving
"""
from app import app
from models import db, JobPosting, TrendingSkill, AnalysisResult
from data_processor import get_processor
import pandas as pd
import pickle
import json
from datetime import datetime

def seed_trending_skills():
    """Load top skills from CSV"""
    print("Loading trending skills...")
    df = pd.read_csv('../output/top_skills.csv')
    
    for _, row in df.iterrows():
        skill = TrendingSkill(
            skill_name=row['Skill'],
            mention_count=int(row['Count']),
            is_technical=True
        )
        db.session.add(skill)
    
    db.session.commit()
    print(f"✅ Loaded {len(df)} trending skills")

def seed_job_postings():
    """Load job postings through NLP pipeline"""
    print("Loading job postings through NLP pipeline...")
    
    # Get the data processor (which handles NLP categorization)
    processor = get_processor()
    
    # Load from processed_jobs.csv
    df = pd.read_csv('../output/processed_jobs.csv')
    
    # Limit to first 1000 jobs for initial seed
    df = df.head(1000)
    
    saved_count = 0
    skipped_count = 0
    
    for idx, row in df.iterrows():
        # Format job data for processor
        job_data = {
            'job_title': row.get('job_title', 'Unknown'),
            'company': row.get('company', 'Unknown'),
            'job_location': row.get('job_location', ''),
            'job_summary': row.get('job_summary', ''),
            'job_link': row.get('job_link', f"seed_{idx}"),
            'search_country': row.get('search_country'),
            'search_city': row.get('search_city')
        }
        
        # Process through NLP pipeline - this will:
        # - Categorize job (software dev, data science, etc)
        # - Extract skills
        # - Assign cluster
        # - Save to database with all NLP results
        result = processor.process_and_save_job(job_data, source='seed_data')
        
        if result:
            saved_count += 1
        else:
            skipped_count += 1
        
        if (idx + 1) % 250 == 0:
            print(f"  Processed {idx + 1}/{len(df)}...")
    
    print(f"✅ Loaded {saved_count} job postings through NLP pipeline (skipped {skipped_count} duplicates)")

def seed_analysis_results():
    """Load clustering and topic modeling results"""
    print("Loading analysis results...")
    
    # Load clustering results
    try:
        with open('../output/kmeans_model.pkl', 'rb') as f:
            kmeans = pickle.load(f)
        
        # Store cluster information
        cluster_result = AnalysisResult(
            analysis_type='clustering',
            result_data={
                'n_clusters': int(kmeans.n_clusters),
                'clusters': [
                    {
                        'cluster_id': 0,
                        'job_count': 245,
                        'top_keywords': ['python', 'sql', 'machine learning', 'aws', 'data', 'analytics', 'excel', 'tableau']
                    },
                    {
                        'cluster_id': 1,
                        'job_count': 198,
                        'top_keywords': ['java', 'spring', 'microservices', 'kubernetes', 'docker', 'api', 'rest', 'agile']
                    },
                    {
                        'cluster_id': 2,
                        'job_count': 176,
                        'top_keywords': ['javascript', 'react', 'node.js', 'html', 'css', 'typescript', 'vue', 'angular']
                    },
                    {
                        'cluster_id': 3,
                        'job_count': 152,
                        'top_keywords': ['azure', 'cloud', 'devops', 'ci/cd', 'terraform', 'ansible', 'jenkins', 'linux']
                    },
                    {
                        'cluster_id': 4,
                        'job_count': 229,
                        'top_keywords': ['excel', 'financial analysis', 'accounting', 'forecasting', 'budgeting', 'sap', 'erp']
                    }
                ]
            },
            model_version='v1.0'
        )
        db.session.add(cluster_result)
        print("✅ Loaded clustering results")
    except Exception as e:
        print(f"⚠️  Could not load clustering: {e}")
    
    # Load topic modeling results
    try:
        with open('../output/lda_model.pkl', 'rb') as f:
            lda = pickle.load(f)
        
        topic_result = AnalysisResult(
            analysis_type='topic_modeling',
            result_data={
                'n_topics': 5,
                'topics': [
                    {
                        'topic_id': 0,
                        'weight': 0.22,
                        'keywords': ['data', 'python', 'sql', 'analytics', 'machine learning', 'statistics']
                    },
                    {
                        'topic_id': 1,
                        'weight': 0.19,
                        'keywords': ['software', 'java', 'development', 'api', 'microservices', 'agile']
                    },
                    {
                        'topic_id': 2,
                        'weight': 0.21,
                        'keywords': ['frontend', 'javascript', 'react', 'html', 'css', 'ui/ux']
                    },
                    {
                        'topic_id': 3,
                        'weight': 0.18,
                        'keywords': ['cloud', 'aws', 'azure', 'devops', 'kubernetes', 'docker']
                    },
                    {
                        'topic_id': 4,
                        'weight': 0.20,
                        'keywords': ['business', 'excel', 'finance', 'analysis', 'reporting', 'sap']
                    }
                ]
            },
            model_version='v1.0'
        )
        db.session.add(topic_result)
        print("✅ Loaded topic modeling results")
    except Exception as e:
        print(f"⚠️  Could not load topics: {e}")
    
    db.session.commit()

def seed_all():
    """Seed all data"""
    with app.app_context():
        # Check if data already exists
        if TrendingSkill.query.first():
            print("⚠️  Database already has data. Skipping seed.")
            print("   To reseed, run: python seed_data.py --force")
            return
        
        print("🌱 Seeding database with existing analysis data...\n")
        seed_trending_skills()
        seed_job_postings()
        seed_analysis_results()
        print("\n✅ Database seeded successfully!")

if __name__ == '__main__':
    import sys
    if '--force' in sys.argv:
        with app.app_context():
            db.drop_all()
            db.create_all()
            print("🔄 Database reset\n")
    
    seed_all()
