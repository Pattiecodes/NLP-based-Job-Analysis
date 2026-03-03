"""
Database initialization script
Run this to create all tables
"""
from app import app, db
from models import User, JobPosting, JobSkill, TrendingSkill, AnalysisResult, UploadHistory, TechNews

def init_db():
    """Initialize database with all tables"""
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✅ Database tables created successfully!")
        
        # Print table names
        print("\nCreated tables:")
        print("- users")
        print("- job_postings")
        print("- job_skills")
        print("- trending_skills")
        print("- analysis_results")
        print("- upload_history")
        print("- tech_news")

def drop_db():
    """Drop all tables (use with caution!)"""
    with app.app_context():
        db.drop_all()
        print("⚠️  All tables dropped!")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--drop':
        confirm = input("Are you sure you want to drop all tables? (yes/no): ")
        if confirm.lower() == 'yes':
            drop_db()
            init_db()
        else:
            print("Aborted.")
    else:
        init_db()
