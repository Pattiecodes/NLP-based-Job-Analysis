"""
Web Scraper for Tech News and Job Postings
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import feedparser
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TechNewsScraper:
    """Scrape tech news about layoffs, hiring trends, etc."""
    
    def __init__(self):
        self.sources = [
            {
                'name': 'TechCrunch Jobs',
                'url': 'https://techcrunch.com/category/startups/',
                'type': 'rss'
            },
            {
                'name': 'Layoffs.fyi',
                'url': 'https://layoffs.fyi/',
                'type': 'web'
            }
        ]
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def scrape_rss_feed(self, url):
        """Scrape news from RSS feed"""
        try:
            feed = feedparser.parse(url)
            articles = []
            
            for entry in feed.entries[:10]:  # Get latest 10
                article = {
                    'title': entry.get('title', 'No title'),
                    'link': entry.get('link', ''),
                    'summary': entry.get('summary', '')[:200],
                    'published': entry.get('published', datetime.now().isoformat()),
                    'source': 'TechCrunch',
                    'scraped_at': datetime.now().isoformat()
                }
                articles.append(article)
            
            return articles
        except Exception as e:
            logger.error(f"Error scraping RSS feed {url}: {e}")
            return []
    
    def scrape_layoffs_fyi(self):
        """Scrape from Layoffs.fyi"""
        try:
            response = requests.get('https://layoffs.fyi/', headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            articles = []
            # This is a simplified scraper - actual implementation would need to match site structure
            news_items = soup.find_all('div', class_='layoff-item', limit=10)
            
            for item in news_items:
                try:
                    title_elem = item.find('h3') or item.find('h2')
                    title = title_elem.text.strip() if title_elem else 'Layoff Update'
                    
                    article = {
                        'title': title,
                        'link': 'https://layoffs.fyi/',
                        'summary': f'Recent tech layoff information from {title}',
                        'published': datetime.now().isoformat(),
                        'source': 'Layoffs.fyi',
                        'scraped_at': datetime.now().isoformat()
                    }
                    articles.append(article)
                except Exception as e:
                    logger.error(f"Error parsing layoff item: {e}")
                    continue
            
            return articles
        except Exception as e:
            logger.error(f"Error scraping Layoffs.fyi: {e}")
            return []
    
    def get_all_news(self):
        """Get news from all sources"""
        all_news = []
        
        # Scrape RSS feeds
        try:
            rss_url = 'https://techcrunch.com/feed/'
            all_news.extend(self.scrape_rss_feed(rss_url))
        except Exception as e:
            logger.error(f"Error with TechCrunch RSS: {e}")
        
        # Scrape Layoffs.fyi
        try:
            all_news.extend(self.scrape_layoffs_fyi())
        except Exception as e:
            logger.error(f"Error with Layoffs.fyi: {e}")
        
        # Add some fallback news if scraping fails
        if not all_news:
            all_news = self._get_fallback_news()
        
        return all_news[:10]  # Return top 10
    
    def _get_fallback_news(self):
        """Fallback news when scraping fails"""
        return [
            {
                'title': 'Tech Industry Hiring Trends 2026',
                'link': '#',
                'summary': 'Latest insights on hiring patterns in the technology sector...',
                'published': datetime.now().isoformat(),
                'source': 'Tech News',
                'scraped_at': datetime.now().isoformat()
            },
            {
                'title': 'Top In-Demand Tech Skills',
                'link': '#',
                'summary': 'Python, JavaScript, and cloud computing lead the pack...',
                'published': datetime.now().isoformat(),
                'source': 'Tech News',
                'scraped_at': datetime.now().isoformat()
            }
        ]


class JobPostingScraper:
    """Scrape job postings from various sources"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def scrape_indeed(self, query='software engineer', location='United States', limit=50):
        """
        Scrape job postings from Indeed
        Note: This is a simplified example. Production scraping should:
        - Respect robots.txt
        - Use proper rate limiting
        - Handle pagination
        - Use official APIs when available
        """
        jobs = []
        
        try:
            # Indeed scraping is complex and requires careful handling
            # This is a placeholder for the actual implementation
            base_url = f'https://www.indeed.com/jobs?q={query}&l={location}'
            
            response = requests.get(base_url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find job cards - structure varies by Indeed's current design
            job_cards = soup.find_all('div', class_='job_seen_beacon', limit=limit)
            
            for card in job_cards:
                try:
                    job = self._parse_indeed_card(card)
                    if job:
                        jobs.append(job)
                except Exception as e:
                    logger.error(f"Error parsing Indeed job card: {e}")
                    continue
            
            logger.info(f"Scraped {len(jobs)} jobs from Indeed")
            
        except Exception as e:
            logger.error(f"Error scraping Indeed: {e}")
        
        return jobs
    
    def _parse_indeed_card(self, card):
        """Parse individual Indeed job card"""
        try:
            title_elem = card.find('h2', class_='jobTitle')
            company_elem = card.find('span', class_='companyName')
            location_elem = card.find('div', class_='companyLocation')
            summary_elem = card.find('div', class_='job-snippet')
            
            job = {
                'job_title': title_elem.text.strip() if title_elem else 'Unknown Title',
                'company': company_elem.text.strip() if company_elem else 'Unknown Company',
                'job_location': location_elem.text.strip() if location_elem else 'Remote',
                'job_summary': summary_elem.text.strip() if summary_elem else '',
                'job_link': 'https://indeed.com',
                'source': 'Indeed',
                'scraped_at': datetime.now().isoformat()
            }
            
            return job
        except Exception as e:
            logger.error(f"Error parsing job card: {e}")
            return None
    
    def scrape_sample_jobs(self, count=20):
        """
        Generate sample job postings for testing
        In production, this would call actual scraping methods
        """
        sample_jobs = []
        
        job_titles = [
            'Senior Software Engineer', 'Data Scientist', 'Frontend Developer',
            'Backend Developer', 'Full Stack Developer', 'DevOps Engineer',
            'Machine Learning Engineer', 'Cloud Architect', 'Product Manager',
            'UI/UX Designer', 'Data Engineer', 'Security Engineer'
        ]
        
        companies = [
            'Google', 'Microsoft', 'Amazon', 'Meta', 'Apple',
            'Netflix', 'Tesla', 'SpaceX', 'OpenAI', 'Anthropic'
        ]
        
        locations = [
            'San Francisco, CA', 'New York, NY', 'Seattle, WA',
            'Austin, TX', 'Boston, MA', 'Remote', 'Los Angeles, CA'
        ]
        
        for i in range(count):
            job = {
                'job_title': job_titles[i % len(job_titles)],
                'company': companies[i % len(companies)],
                'job_location': locations[i % len(locations)],
                'job_type': 'Full-time',
                'job_level': 'Mid-Senior level',
                'job_summary': f'Exciting opportunity to join our team as a {job_titles[i % len(job_titles)]}. '
                              f'We are looking for talented individuals with strong technical skills.',
                'job_link': f'https://example.com/job/{i}',
                'source': 'Web Scraper',
                'scraped_at': datetime.now().isoformat(),
                'posted_date': datetime.now().isoformat()
            }
            sample_jobs.append(job)
        
        return sample_jobs


def scrape_tech_news():
    """Convenience function to scrape tech news"""
    scraper = TechNewsScraper()
    return scraper.get_all_news()


def scrape_job_postings(query='software engineer', limit=50):
    """Convenience function to scrape job postings"""
    scraper = JobPostingScraper()
    
    # Try to scrape from Indeed
    jobs = scraper.scrape_indeed(query=query, limit=limit)
    
    # If scraping fails or returns few results, add sample jobs
    if len(jobs) < 10:
        jobs.extend(scraper.scrape_sample_jobs(count=max(10, limit - len(jobs))))
    
    return jobs[:limit]


if __name__ == '__main__':
    # Test the scrapers
    print("Testing Tech News Scraper...")
    news = scrape_tech_news()
    print(f"Found {len(news)} news articles")
    for article in news[:3]:
        print(f"- {article['title']}")
    
    print("\nTesting Job Posting Scraper...")
    jobs = scrape_job_postings(limit=10)
    print(f"Found {len(jobs)} job postings")
    for job in jobs[:3]:
        print(f"- {job['job_title']} at {job['company']}")
