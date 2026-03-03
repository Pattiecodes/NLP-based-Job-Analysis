"""
NLP Job Categorizer
Uses natural language processing to categorize job postings
"""
import re
from typing import Dict, List, Optional
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Download required NLTK data (run once)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')


class JobCategorizer:
    """NLP-based job categorizer"""
    
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        
        # Job type keywords
        self.job_type_keywords = {
            'Full-time': [
                'full time', 'fulltime', 'full-time', 'permanent', 
                'regular', 'staff', 'employee'
            ],
            'Part-time': [
                'part time', 'parttime', 'part-time', 'flexible hours',
                'hours per week', 'hourly'
            ],
            'Contract': [
                'contract', 'contractor', 'consulting', 'consultant',
                'freelance', 'temporary', 'temp', 'project-based',
                'fixed-term', 'independent contractor'
            ],
            'Internship': [
                'intern', 'internship', 'co-op', 'coop', 'trainee',
                'student', 'graduate program', 'apprentice'
            ],
            'Remote': [
                'remote', 'work from home', 'wfh', 'distributed',
                'virtual', 'telecommute', 'anywhere'
            ]
        }
        
        # Job level keywords
        self.job_level_keywords = {
            'Entry level': [
                'entry level', 'junior', 'associate', 'graduate',
                'early career', '0-2 years', 'new grad'
            ],
            'Mid level': [
                'mid level', 'intermediate', 'experienced', 
                '3-5 years', '2-5 years', 'professional'
            ],
            'Senior level': [
                'senior', 'lead', 'principal', 'staff',
                'expert', '5+ years', '7+ years', 'advanced'
            ],
            'Executive': [
                'director', 'vp', 'vice president', 'cto', 'ceo',
                'cfo', 'head of', 'chief', 'executive', 'c-level'
            ],
            'Manager': [
                'manager', 'management', 'supervisor', 'team lead',
                'coordinator', 'administrator'
            ]
        }
        
        # Job category keywords (domain/field)
        self.job_category_keywords = {
            'Software Development': [
                'software', 'developer', 'engineer', 'programmer',
                'coding', 'backend', 'frontend', 'full stack',
                'web development', 'mobile development', 'app'
            ],
            'Data Science': [
                'data scientist', 'data analyst', 'machine learning',
                'ml engineer', 'ai', 'artificial intelligence',
                'statistics', 'analytics', 'big data'
            ],
            'DevOps': [
                'devops', 'sre', 'site reliability', 'infrastructure',
                'cloud engineer', 'platform engineer', 'ci/cd',
                'deployment', 'kubernetes', 'docker'
            ],
            'Product Management': [
                'product manager', 'product owner', 'pm',
                'product strategy', 'roadmap', 'agile'
            ],
            'Design': [
                'designer', 'ux', 'ui', 'user experience',
                'user interface', 'graphic design', 'visual'
            ],
            'Marketing': [
                'marketing', 'growth', 'seo', 'content',
                'social media', 'digital marketing', 'brand'
            ],
            'Sales': [
                'sales', 'account executive', 'business development',
                'account manager', 'sales engineer', 'sales representative'
            ],
            'Finance': [
                'finance', 'accounting', 'financial analyst',
                'accountant', 'controller', 'auditor', 'cpa'
            ],
            'Security': [
                'security', 'cybersecurity', 'information security',
                'security engineer', 'penetration tester', 'infosec'
            ],
            'Healthcare': [
                'nurse', 'nursing', 'physician', 'doctor', 'rn',
                'clinical', 'medical', 'healthcare', 'hospital',
                'therapeutic', 'patient care', 'practitioner'
            ],
            'Education': [
                'teacher', 'instructor', 'educator', 'professor',
                'academic', 'tutor', 'trainer', 'educational',
                'school', 'university', 'teaching'
            ],
            'Manufacturing': [
                'manufacturing', 'factory', 'production', 'fabrication',
                'assembly', 'plant', 'machine operator', 'technician',
                'forklift', 'welder', 'mechanical'
            ],
            'Hospitality': [
                'hotel', 'restaurant', 'chef', 'cook', 'server',
                'bartender', 'hospitality', 'housekeeping', 'front desk',
                'concierge', 'catering', 'leisure'
            ],
            'Construction': [
                'construction', 'carpenter', 'electrician', 'plumber',
                'hvac', 'builder', 'contractor', 'surveyor',
                'foreman', 'site manager', 'excavator'
            ],
            'Transportation': [
                'driver', 'truck driver', 'delivery', 'logistics',
                'warehouse', 'forklift', 'pilot', 'transportation',
                'shipping', 'commercial driver', 'cdl'
            ],
            'Customer Service': [
                'customer service', 'customer support', 'representative',
                'call center', 'support specialist', 'help desk',
                'customer care', 'service representative'
            ],
            'Human Resources': [
                'hr', 'human resources', 'recruiter', 'recruiting',
                'talent', 'payroll', 'benefits', 'compensation',
                'employee relations'
            ],
            'Legal': [
                'lawyer', 'attorney', 'legal', 'paralegal',
                'law firm', 'compliance', 'contract', 'counsel'
            ],
            'Agriculture': [
                'farm', 'farmer', 'agriculture', 'agricultural',
                'livestock', 'crop', 'ranch', 'horticulture'
            ],
            'Retail': [
                'retail', 'cashier', 'sales associate', 'store',
                'merchandise', 'inventory', 'shop', 'clerk'
            ]
        }
    
    def categorize_job_type(self, title: str, description: str = '') -> str:
        """
        Categorize job posting type using NLP
        
        Args:
            title: Job title
            description: Job description (optional)
            
        Returns:
            Job type category
        """
        text = f"{title} {description}".lower()
        
        scores = {}
        for job_type, keywords in self.job_type_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword.lower() in text:
                    # Weight title matches higher
                    if keyword.lower() in title.lower():
                        score += 3
                    else:
                        score += 1
            scores[job_type] = score
        
        # Return type with highest score, default to Full-time
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        
        return 'Full-time'
    
    def categorize_job_level(self, title: str, description: str = '') -> str:
        """
        Categorize job level using NLP
        
        Args:
            title: Job title
            description: Job description (optional)
            
        Returns:
            Job level category
        """
        text = f"{title} {description}".lower()
        
        scores = {}
        for level, keywords in self.job_level_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword.lower() in text:
                    # Weight title matches higher
                    if keyword.lower() in title.lower():
                        score += 3
                    else:
                        score += 1
            scores[level] = score
        
        # Return level with highest score, default to Mid level
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        
        return 'Mid level'
    
    def categorize_job_domain(self, title: str, description: str = '') -> str:
        """
        Categorize job domain/field using NLP
        
        Args:
            title: Job title
            description: Job description (optional)
            
        Returns:
            Job domain category
        """
        text = f"{title} {description}".lower()
        
        scores = {}
        for category, keywords in self.job_category_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword.lower() in text:
                    # Weight title matches higher
                    if keyword.lower() in title.lower():
                        score += 3
                    else:
                        score += 1
            scores[category] = score
        
        # Return category with highest score, default to Software Development
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        
        return 'Other'
    
    def extract_skills(self, text: str) -> List[str]:
        """
        Extract skills from job text using NLP
        
        Args:
            text: Job title and description
            
        Returns:
            List of extracted skills
        """
        # Common tech skills to look for
        common_skills = [
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#',
            'ruby', 'go', 'rust', 'swift', 'kotlin', 'scala',
            'react', 'angular', 'vue', 'node.js', 'django', 'flask',
            'spring', 'express', 'fastapi',
            'sql', 'postgresql', 'mysql', 'mongodb', 'redis',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes',
            'git', 'ci/cd', 'jenkins', 'terraform',
            'machine learning', 'deep learning', 'nlp', 'computer vision',
            'tensorflow', 'pytorch', 'scikit-learn',
            'pandas', 'numpy', 'matplotlib',
            'rest api', 'graphql', 'microservices',
            'agile', 'scrum', 'jira',
            'html', 'css', 'sass', 'webpack',
            'excel', 'tableau', 'power bi', 'looker'
        ]
        
        text_lower = text.lower()
        found_skills = []
        
        for skill in common_skills:
            # Use word boundary matching for better accuracy
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.append(skill.title())
        
        return found_skills
    
    def analyze_job(self, job_data: Dict) -> Dict:
        """
        Perform complete NLP analysis on a job posting
        
        Args:
            job_data: Dictionary containing job information
            
        Returns:
            Dictionary with categorization results
        """
        title = job_data.get('job_title', '')
        description = job_data.get('job_summary', '')
        
        return {
            'job_type': self.categorize_job_type(title, description),
            'job_level': self.categorize_job_level(title, description),
            'job_category': self.categorize_job_domain(title, description),
            'extracted_skills': self.extract_skills(f"{title} {description}")
        }


# Global instance
_categorizer = None

def get_categorizer() -> JobCategorizer:
    """Get or create global categorizer instance"""
    global _categorizer
    if _categorizer is None:
        _categorizer = JobCategorizer()
    return _categorizer


def categorize_job(job_data: Dict) -> Dict:
    """
    Convenience function to categorize a job posting
    
    Args:
        job_data: Job posting data
        
    Returns:
        Categorization results
    """
    categorizer = get_categorizer()
    return categorizer.analyze_job(job_data)


if __name__ == '__main__':
    # Test the categorizer
    categorizer = JobCategorizer()
    
    test_jobs = [
        {
            'job_title': 'Senior Software Engineer',
            'job_summary': 'We are looking for a senior software engineer with experience in Python, Django, and AWS.'
        },
        {
            'job_title': 'Junior Data Analyst Intern',
            'job_summary': 'Remote internship opportunity for students interested in data analytics and machine learning.'
        },
        {
            'job_title': 'Contract DevOps Engineer',
            'job_summary': '6-month contract position. Experience with Kubernetes, Docker, and CI/CD required.'
        }
    ]
    
    print("Testing Job Categorizer:\n")
    for job in test_jobs:
        result = categorizer.analyze_job(job)
        print(f"Title: {job['job_title']}")
        print(f"  Type: {result['job_type']}")
        print(f"  Level: {result['job_level']}")
        print(f"  Category: {result['job_category']}")
        print(f"  Skills: {', '.join(result['extracted_skills'][:5])}")
        print()
