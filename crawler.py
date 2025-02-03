import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin
import re
from collections import deque
from datetime import datetime, timedelta
import threading

class RateLimiter:
    def __init__(self, requests_per_minute=60, burst_limit=10):
        self.requests_per_minute = requests_per_minute
        self.burst_limit = burst_limit
        self.requests = deque()
        self.lock = threading.Lock()
    
    def can_make_request(self):
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)
        
        with self.lock:
            # Remove requests older than 1 minute
            while self.requests and self.requests[0] < minute_ago:
                self.requests.popleft()
            
            # Check if we're within limits
            if len(self.requests) >= self.requests_per_minute:
                return False
            
            # Check burst limit (no more than burst_limit requests per second)
            last_second = now - timedelta(seconds=1)
            recent_requests = sum(1 for req in self.requests if req > last_second)
            if recent_requests >= self.burst_limit:
                return False
            
            self.requests.append(now)
            return True
    
    def wait_if_needed(self):
        while not self.can_make_request():
            time.sleep(0.1)




#DataHandler
from dataclasses import dataclass
from typing import List, Optional
import json
import hashlib

@dataclass
class PersonData:
    name: str
    professional_title: Optional[str] = None
    company: Optional[str] = None
    education: List[str] = None
    public_links: List[str] = None
    last_updated: str = None

class DataHandler:
    def __init__(self, storage_path: str = "data/"):
        self.storage_path = storage_path
        self.ensure_storage_exists()
    
    def ensure_storage_exists(self):
        os.makedirs(self.storage_path, exist_ok=True)
    
    def generate_id(self, data: PersonData) -> str:
        """Generate a unique ID based on name and other identifiers"""
        identifier = f"{data.name}_{data.professional_title}_{data.company}"
        return hashlib.sha256(identifier.encode()).hexdigest()[:12]
    
    def save_person_data(self, data: PersonData):
        """Save person data with privacy considerations"""
        person_id = self.generate_id(data)
        
        # Remove any sensitive data before saving
        sanitized_data = self.sanitize_data(data)
        
        file_path = os.path.join(self.storage_path, f"{person_id}.json")
        with open(file_path, 'w') as f:
            json.dump(sanitized_data.__dict__, f)
        
        return person_id
    
    def sanitize_data(self, data: PersonData) -> PersonData:
        """Remove or mask potentially sensitive information"""
        # Create a copy to avoid modifying the original
        sanitized = PersonData(
            name=data.name,
            professional_title=data.professional_title,
            company=data.company,
            education=data.education,
            public_links=[link for link in (data.public_links or [])
                         if self.is_safe_link(link)],
            last_updated=datetime.now().isoformat()
        )
        
        return sanitized
    
    def is_safe_link(self, link: str) -> bool:
        """Verify if a link is to an allowed public profile"""
        allowed_domains = [
            'linkedin.com/in/',
            'github.com/',
            'scholar.google.com/',
            'twitter.com/',
        ]
        return any(domain in link.lower() for domain in allowed_domains)



#EnhancedWebCrawler
class EnhancedWebCrawler:
    def __init__(self):
        self.rate_limiter = RateLimiter(requests_per_minute=60)
        self.data_handler = DataHandler()
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'ResponsibleBot/1.0 (Educational Research)',
            'Accept': 'text/html,application/xhtml+xml',
            'Accept-Language': 'en-US,en;q=0.5'
        }
    
    def search_person(self, name: str) -> PersonData:
        self.rate_limiter.wait_if_needed()
        
        person_data = PersonData(name=name)
        
        # Search different platforms
        linkedin_info = self.search_linkedin(name)
        github_info = self.search_github(name)
        scholar_info = self.search_scholar(name)
        
        # Combine information
        self.combine_info(person_data, linkedin_info, github_info, scholar_info)
        
        # Save data
        self.data_handler.save_person_data(person_data)
        
        return person_data
    
    def search_linkedin(self, name: str) -> dict:
        """Search LinkedIn for public profiles"""
        self.rate_limiter.wait_if_needed()
        
        search_url = f"https://www.google.com/search?q=site:linkedin.com/in/ {name}"
        response = self.session.get(search_url)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Implementation of LinkedIn specific parsing
            # Only extract public information from search results
            return self.parse_linkedin_results(soup)
        
        return {}
    
    def parse_linkedin_results(self, soup) -> dict:
        """Parse LinkedIn results with privacy considerations"""
        results = {}
        
        # Find public profile links
        links = soup.find_all('a')
        public_profiles = [
            link.get('href') for link in links
            if 'linkedin.com/in/' in str(link.get('href', ''))
        ]
        
        if public_profiles:
            results['public_links'] = public_profiles[:1]  # Only take the first match
        
        return results
    


#Loggins and filterng    
import logging
from typing import Optional

class CrawlerLogger:
    def __init__(self):
        self.logger = logging.getLogger('WebCrawler')
        self.logger.setLevel(logging.INFO)
        
        # Add file handler
        fh = logging.FileHandler('crawler.log')
        fh.setLevel(logging.INFO)
        
        # Add console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.WARNING)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
    
    def log_search(self, name: str, success: bool, error: Optional[Exception] = None):
        if success:
            self.logger.info(f"Successfully searched for {name}")
        else:
            self.logger.error(f"Failed to search for {name}: {str(error)}")