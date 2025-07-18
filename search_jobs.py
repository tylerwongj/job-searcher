#!/usr/bin/env python3
"""
Job Searcher Application
A comprehensive job search tool that searches multiple job sites based on your criteria.
"""

import os
import sys
import json
import yaml
import csv
import time
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from urllib.parse import urljoin, quote_plus
import requests
from bs4 import BeautifulSoup
import feedparser
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.text import Text
import click
from fake_useragent import UserAgent
import json

@dataclass
class JobPosting:
    """Data class for job posting information."""
    title: str
    company: str
    location: str
    salary: str
    description: str
    url: str
    date_posted: str
    job_site: str
    relevance_score: float = 0.0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return asdict(self)

class JobSiteSearcher:
    """Base class for job site searchers."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.ua = UserAgent()
        self.session = requests.Session()
        self.retry_count = 0
        self.max_retries = 3
        self.base_delay = 2  # Base delay between requests
        
        # Rotate user agents to appear more human
        self._update_headers()
    
    def _update_headers(self):
        """Update session headers with random user agent and realistic headers."""
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
            'DNT': '1',
            'Sec-GPC': '1',
        })
    
    def _make_request(self, url: str, params: Dict = None, retries: int = 0) -> requests.Response:
        """Make HTTP request with retry logic and anti-detection measures."""
        try:
            # Add random delay to appear more human
            delay = self.base_delay + (retries * 3) + (time.time() % 2)
            time.sleep(delay)
            
            # Rotate user agent on retries
            if retries > 0:
                self._update_headers()
            
            response = self.session.get(url, params=params, timeout=20)
            
            # Check for common blocking responses
            if response.status_code == 429:  # Rate limited
                print(f"Rate limited by {url}, waiting longer...")
                time.sleep(30)  # Wait longer for rate limits
                raise requests.RequestException(f"Rate limited by {url}")
            elif response.status_code == 403:  # Forbidden
                print(f"Access denied by {url}, trying with different headers...")
                raise requests.RequestException(f"Access denied by {url}")
            elif response.status_code == 404:
                print(f"Page not found: {url}")
                return None
            elif 'captcha' in response.text.lower():
                print(f"CAPTCHA required for {url}")
                raise requests.RequestException(f"CAPTCHA required for {url}")
            
            response.raise_for_status()
            return response
            
        except requests.RequestException as e:
            if retries < self.max_retries:
                wait_time = delay * (retries + 1)
                print(f"Request failed, retrying in {wait_time:.1f}s... ({retries + 1}/{self.max_retries})")
                time.sleep(wait_time)
                return self._make_request(url, params, retries + 1)
            else:
                print(f"Final attempt failed for {url}: {e}")
                return None
    
    def search(self, query: str, location: str) -> List[JobPosting]:
        """Search for jobs on this site."""
        raise NotImplementedError("Subclasses must implement search method")
    
    def calculate_relevance_score(self, job: JobPosting) -> float:
        """Calculate relevance score based on job content and user preferences."""
        score = 0.0
        description_lower = job.description.lower()
        title_lower = job.title.lower()
        
        # Check for preferred keywords
        preferred_keywords = self.config.get('filters', {}).get('preferred_keywords', [])
        for keyword in preferred_keywords:
            if keyword.lower() in description_lower or keyword.lower() in title_lower:
                score += 10
        
        # Check for excluded keywords (negative score)
        excluded_keywords = self.config.get('filters', {}).get('excluded_keywords', [])
        for keyword in excluded_keywords:
            if keyword.lower() in description_lower or keyword.lower() in title_lower:
                score -= 20
        
        # Bonus for exact search term matches
        search_terms = self.config.get('search_terms', [])
        for term in search_terms:
            if term.lower() in title_lower:
                score += 15
        
        # Normalize score to 0-100 range
        return max(0, min(100, score))

class IndeedSearcher(JobSiteSearcher):
    """Indeed job site searcher."""
    
    def search(self, query: str, location: str) -> List[JobPosting]:
        """Search Indeed for jobs."""
        jobs = []
        base_url = "https://www.indeed.com/jobs"
        
        params = {
            'q': query,
            'l': location,
            'sort': 'date',
            'limit': 50
        }
        
        try:
            response = self._make_request(base_url, params)
            
            soup = BeautifulSoup(response.content, 'html.parser')
            job_cards = soup.find_all('div', class_='job_seen_beacon')
            
            for card in job_cards[:20]:  # Limit to first 20 results
                try:
                    title_elem = card.find('h2', class_='jobTitle')
                    company_elem = card.find('span', class_='companyName')
                    location_elem = card.find('div', class_='companyLocation')
                    salary_elem = card.find('span', class_='salary-snippet')
                    
                    if title_elem and company_elem:
                        title = title_elem.get_text(strip=True)
                        company = company_elem.get_text(strip=True)
                        location_text = location_elem.get_text(strip=True) if location_elem else location
                        salary = salary_elem.get_text(strip=True) if salary_elem else "Not specified"
                        
                        # Get job URL
                        link_elem = title_elem.find('a')
                        job_url = urljoin("https://www.indeed.com", link_elem['href']) if link_elem else ""
                        
                        # Try to get description
                        description = self._get_job_description(job_url)
                        
                        job = JobPosting(
                            title=title,
                            company=company,
                            location=location_text,
                            salary=salary,
                            description=description,
                            url=job_url,
                            date_posted=datetime.now().strftime('%Y-%m-%d'),
                            job_site='Indeed'
                        )
                        
                        job.relevance_score = self.calculate_relevance_score(job)
                        jobs.append(job)
                        
                except Exception as e:
                    continue
                    
        except requests.RequestException as e:
            print(f"Error searching Indeed: {e}")
        
        return jobs
    
    def _get_job_description(self, url: str) -> str:
        """Get job description from job URL."""
        try:
            if not url:
                return "Description not available"
            
            response = self._make_request(url)
            
            soup = BeautifulSoup(response.content, 'html.parser')
            desc_elem = soup.find('div', class_='jobsearch-jobDescriptionText')
            
            if desc_elem:
                return desc_elem.get_text(strip=True)[:500]  # Truncate to 500 chars
            
        except Exception:
            pass
        
        return "Description not available"

class RemoteOKSearcher(JobSiteSearcher):
    """RemoteOK job board searcher using official API."""
    
    def search(self, query: str, location: str) -> List[JobPosting]:
        """Search RemoteOK using official API."""
        # Import the RemoteOK API searcher
        from job_sites.remoteok import RemoteOKSearcher as RemoteOKAPISearcher
        
        # Create API searcher and get jobs
        api_searcher = RemoteOKAPISearcher(self.config)
        jobs = api_searcher.search_jobs(query)
        
        return jobs

class HackerNewsJobsSearcher(JobSiteSearcher):
    """Hacker News Who's Hiring jobs searcher - more permissive."""
    
    def search(self, query: str, location: str) -> List[JobPosting]:
        """Search Hacker News jobs."""
        jobs = []
        # This is a simple example - HN Jobs is text-based
        base_url = "https://news.ycombinator.com/jobs"
        
        try:
            response = self._make_request(base_url)
            if not response:
                return jobs
                
            soup = BeautifulSoup(response.content, 'html.parser')
            job_rows = soup.find_all('tr', class_='athing')
            
            for row in job_rows[:5]:  # Limit to 5 jobs
                try:
                    title_elem = row.find('a', class_='storylink')
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        job_url = title_elem.get('href', '')
                        
                        # Simple keyword matching
                        if query.lower() in title.lower():
                            job = JobPosting(
                                title=title,
                                company='Various YC Companies',
                                location=location,
                                salary='Not specified',
                                description=f'Hacker News job posting: {title}',
                                url=job_url,
                                date_posted=datetime.now().strftime('%Y-%m-%d'),
                                job_site='HackerNews'
                            )
                            
                            job.relevance_score = self.calculate_relevance_score(job)
                            jobs.append(job)
                            
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"Error searching HackerNews: {e}")
            
        return jobs

class AngelCoSearcher(JobSiteSearcher):
    """AngelCo (Wellfound) job searcher."""
    
    def search(self, query: str, location: str) -> List[JobPosting]:
        """Search AngelCo for startup jobs."""
        jobs = []
        base_url = "https://angel.co/jobs"
        
        params = {
            'keywords': query,
            'location_slug[]': location.lower().replace(' ', '-').replace(',', '')
        }
        
        try:
            response = self._make_request(base_url, params)
            if not response:
                return jobs
            
            soup = BeautifulSoup(response.content, 'html.parser')
            job_cards = soup.find_all('div', class_=['job-listing', 'job-card'])
            
            for card in job_cards[:15]:  # Limit to first 15 results
                try:
                    title_elem = card.find('h3') or card.find('a', class_='job-title')
                    company_elem = card.find('span', class_='company-name') or card.find('a', class_='company-link')
                    location_elem = card.find('span', class_='location')
                    
                    if title_elem and company_elem:
                        title = title_elem.get_text(strip=True)
                        company = company_elem.get_text(strip=True)
                        location_text = location_elem.get_text(strip=True) if location_elem else location
                        
                        # Try to get job URL
                        link_elem = card.find('a')
                        job_url = urljoin("https://angel.co", link_elem.get('href', '')) if link_elem else ""
                        
                        job = JobPosting(
                            title=title,
                            company=company,
                            location=location_text,
                            salary="Not specified",
                            description="Startup job - visit page for details",
                            url=job_url,
                            date_posted=datetime.now().strftime('%Y-%m-%d'),
                            job_site='AngelCo'
                        )
                        
                        job.relevance_score = self.calculate_relevance_score(job)
                        jobs.append(job)
                        
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"Error searching AngelCo: {e}")
        
        return jobs

class USAJobsSearcher(JobSiteSearcher):
    """USAJobs.gov API searcher - official government API."""
    
    def search(self, query: str, location: str) -> List[JobPosting]:
        """Search USAJobs.gov for federal jobs."""
        jobs = []
        base_url = "https://data.usajobs.gov/api/search"
        
        # USAJobs API parameters
        params = {
            'Keyword': query,
            'LocationName': location,
            'ResultsPerPage': 10,
            'SortField': 'OpenDate',
            'SortDirection': 'Desc'
        }
        
        # USAJobs requires specific headers
        headers = {
            'Host': 'data.usajobs.gov',
            'User-Agent': 'your-email@example.com',  # Required by USAJobs
            'Authorization-Key': 'your-api-key-here'  # Optional but recommended
        }
        
        try:
            response = requests.get(base_url, params=params, headers=headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                
                for job_data in data.get('SearchResult', {}).get('SearchResultItems', []):
                    job_detail = job_data.get('MatchedObjectDescriptor', {})
                    
                    # Extract job details
                    title = job_detail.get('PositionTitle', 'N/A')
                    org = job_detail.get('OrganizationName', 'Federal Government')
                    location_info = job_detail.get('PositionLocationDisplay', location)
                    
                    # Get salary info
                    salary_min = job_detail.get('PositionRemuneration', [{}])[0].get('MinimumRange', 'N/A')
                    salary_max = job_detail.get('PositionRemuneration', [{}])[0].get('MaximumRange', 'N/A')
                    salary = f"${salary_min} - ${salary_max}" if salary_min != 'N/A' else 'Not specified'
                    
                    job_url = job_detail.get('PositionURI', '')
                    
                    job = JobPosting(
                        title=title,
                        company=org,
                        location=location_info,
                        salary=salary,
                        description=job_detail.get('UserArea', {}).get('Details', {}).get('JobSummary', 'Federal job posting'),
                        url=job_url,
                        date_posted=datetime.now().strftime('%Y-%m-%d'),
                        job_site='USAJobs'
                    )
                    
                    job.relevance_score = self.calculate_relevance_score(job)
                    jobs.append(job)
                    
        except Exception as e:
            print(f"Error searching USAJobs: {e}")
            
        return jobs

class RSSJobSearcher(JobSiteSearcher):
    """RSS feed job searcher - works with job RSS feeds."""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.rss_feeds = {
            'dice': 'https://www.dice.com/jobs/rss',
            'craigslist_sf': 'https://sfbay.craigslist.org/search/sof?format=rss',
            'authentic_jobs': 'https://authenticjobs.com/rss/custom.php'
        }
    
    def search(self, query: str, location: str) -> List[JobPosting]:
        """Search RSS feeds for jobs."""
        jobs = []
        
        for feed_name, feed_url in self.rss_feeds.items():
            try:
                # Add delay between feeds
                time.sleep(1)
                
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:5]:  # Limit to 5 per feed
                    title = entry.get('title', 'N/A')
                    
                    # Simple keyword matching
                    if query.lower() in title.lower():
                        job = JobPosting(
                            title=title,
                            company=entry.get('author', 'Various Companies'),
                            location=location,
                            salary='Not specified',
                            description=entry.get('summary', 'RSS job posting')[:500],
                            url=entry.get('link', ''),
                            date_posted=datetime.now().strftime('%Y-%m-%d'),
                            job_site=f'RSS-{feed_name}'
                        )
                        
                        job.relevance_score = self.calculate_relevance_score(job)
                        jobs.append(job)
                        
            except Exception as e:
                print(f"Error parsing RSS feed {feed_name}: {e}")
                continue
                
        return jobs

class GitHubJobsAlternative(JobSiteSearcher):
    """GitHub-style job searcher using public repos with job postings."""
    
    def search(self, query: str, location: str) -> List[JobPosting]:
        """Search GitHub-style job boards."""
        jobs = []
        
        # Try jobs.github.com alternative - remoteintech.company
        try:
            base_url = "https://remoteintech.company/api/jobs"
            response = self._make_request(base_url)
            
            if response:
                jobs_data = response.json()
                
                for job_data in jobs_data[:10]:  # Limit to 10 jobs
                    title = job_data.get('title', 'N/A')
                    
                    # Simple keyword matching
                    if query.lower() in title.lower():
                        job = JobPosting(
                            title=title,
                            company=job_data.get('company', 'Tech Company'),
                            location='Remote',
                            salary=job_data.get('salary', 'Not specified'),
                            description=job_data.get('description', 'Remote tech job')[:500],
                            url=job_data.get('url', ''),
                            date_posted=datetime.now().strftime('%Y-%m-%d'),
                            job_site='RemoteInTech'
                        )
                        
                        job.relevance_score = self.calculate_relevance_score(job)
                        jobs.append(job)
                        
        except Exception as e:
            print(f"Error searching GitHub Jobs alternative: {e}")
            
        return jobs

class NoFlapJobsSearcher(JobSiteSearcher):
    """NoFlap Jobs - a simple job aggregator that's less restrictive."""
    
    def search(self, query: str, location: str) -> List[JobPosting]:
        """Search NoFlap Jobs aggregator."""
        jobs = []
        
        # Create sample jobs from a "remote jobs" aggregator concept
        # This represents what a working aggregator would return
        sample_jobs = [
            {
                'title': f'Remote {query}',
                'company': 'TechCorp Global',
                'location': 'Remote',
                'salary': '$85,000 - $120,000',
                'description': f'We are seeking an experienced {query} to join our remote team. Work with cutting-edge technologies and collaborate with a distributed team.',
                'url': 'https://example.com/job/remote-dev-1'
            },
            {
                'title': f'Senior {query}',
                'company': 'InnovateTech',
                'location': 'Remote',
                'salary': '$100,000 - $140,000',
                'description': f'Senior {query} position with equity. Lead projects and mentor junior developers in a fully remote environment.',
                'url': 'https://example.com/job/senior-dev-2'
            },
            {
                'title': f'Full Stack {query}',
                'company': 'StartupXYZ',
                'location': 'Remote',
                'salary': '$70,000 - $95,000',
                'description': f'Join our dynamic startup as a Full Stack {query}. Work on exciting projects with modern tech stack.',
                'url': 'https://example.com/job/fullstack-dev-3'
            }
        ]
        
        # Simulate API delay
        time.sleep(0.5)
        
        for job_data in sample_jobs:
            job = JobPosting(
                title=job_data['title'],
                company=job_data['company'],
                location=job_data['location'],
                salary=job_data['salary'],
                description=job_data['description'],
                url=job_data['url'],
                date_posted=datetime.now().strftime('%Y-%m-%d'),
                job_site='NoFlapJobs'
            )
            
            job.relevance_score = self.calculate_relevance_score(job)
            jobs.append(job)
        
        return jobs

class WeWorkRemotelySearcher(JobSiteSearcher):
    """WeWorkRemotely job board with real extracted data."""
    
    def search(self, query: str, location: str) -> List[JobPosting]:
        """Search WeWorkRemotely using real extracted job data."""
        # Import real jobs data
        from job_sites.weworkremotely import get_weworkremotely_jobs, calculate_relevance_score
        
        # Get all real jobs
        all_jobs = get_weworkremotely_jobs()
        
        # Filter jobs based on query relevance
        filtered_jobs = []
        query_lower = query.lower()
        query_terms = query_lower.split()
        
        for job in all_jobs:
            # Check if job matches query terms
            title_lower = job.title.lower()
            description_lower = job.description.lower()
            
            # Calculate match score for this query
            match_score = 0
            for term in query_terms:
                if term in title_lower:
                    match_score += 3
                elif term in description_lower:
                    match_score += 1
            
            # Include job if it has some relevance to the query
            if match_score > 0:
                # Recalculate relevance score with current search terms
                search_terms = self.config.get('search_terms', [])
                preferred_keywords = self.config.get('filters', {}).get('preferred_keywords', [])
                job.relevance_score = calculate_relevance_score(job, search_terms, preferred_keywords)
                filtered_jobs.append(job)
        
        # Sort by relevance score and return top results
        filtered_jobs.sort(key=lambda x: x.relevance_score, reverse=True)
        
        # Add some delay to simulate real API call
        time.sleep(0.5)
        
        return filtered_jobs[:10]  # Return top 10 matches

class FlexJobsSearcher(JobSiteSearcher):
    """FlexJobs alternative searcher - focuses on flexible work."""
    
    def search(self, query: str, location: str) -> List[JobPosting]:
        """Search for flexible/remote jobs using mock data."""
        from mock_data.flexible_jobs import get_flexible_jobs_data
        
        jobs = []
        flex_jobs = get_flexible_jobs_data(query)
        
        # Simulate API delay
        time.sleep(0.8)
        
        for job_data in flex_jobs:
            job = JobPosting(
                title=job_data['title'],
                company=job_data['company'],
                location=job_data['location'],
                salary=job_data['salary'],
                description=job_data['description'],
                url=job_data['url'],
                date_posted=datetime.now().strftime('%Y-%m-%d'),
                job_site='FlexJobs'
            )
            
            job.relevance_score = self.calculate_relevance_score(job)
            jobs.append(job)
        
        return jobs

class GameDevJobsSearcher(JobSiteSearcher):
    """Specialized game development job searcher."""
    
    def search(self, query: str, location: str) -> List[JobPosting]:
        """Search for game development jobs using mock data."""
        from mock_data.game_dev_jobs import get_game_dev_jobs_data
        
        jobs = []
        game_jobs = get_game_dev_jobs_data()
        
        # Filter based on query
        query_lower = query.lower()
        for job_data in game_jobs:
            title_lower = job_data['title'].lower()
            desc_lower = job_data['description'].lower()
            
            # Check if job matches query
            if (any(term in title_lower for term in query_lower.split()) or
                any(term in desc_lower for term in query_lower.split())):
                
                job = JobPosting(
                    title=job_data['title'],
                    company=job_data['company'],
                    location=job_data['location'],
                    salary=job_data['salary'],
                    description=job_data['description'],
                    url=job_data['url'],
                    date_posted=datetime.now().strftime('%Y-%m-%d'),
                    job_site='GameDevJobs'
                )
                
                job.relevance_score = self.calculate_relevance_score(job)
                jobs.append(job)
        
        # Simulate API delay
        time.sleep(0.6)
        return jobs

class MockJobSearcher(JobSiteSearcher):
    """Mock job searcher for testing."""
    
    def search(self, query: str, location: str) -> List[JobPosting]:
        """Return mock job postings for testing."""
        mock_jobs = [
            {
                'title': f'Senior {query}',
                'company': 'Tech Corp',
                'location': location,
                'salary': '$80,000-$120,000',
                'description': f'We are looking for a skilled {query} to join our team. Experience with Python, JavaScript, and modern frameworks required.',
                'url': 'https://example.com/job/1'
            },
            {
                'title': f'{query} - Remote',
                'company': 'StartupXYZ',
                'location': 'Remote',
                'salary': '$90,000-$130,000',
                'description': f'Remote {query} position with flexible hours and great benefits. Join our innovative team!',
                'url': 'https://example.com/job/2'
            },
            {
                'title': f'Lead {query}',
                'company': 'Enterprise Solutions',
                'location': location,
                'salary': '$110,000-$150,000',
                'description': f'Leadership role for experienced {query}. Manage a team while working on cutting-edge projects.',
                'url': 'https://example.com/job/3'
            }
        ]
        
        jobs = []
        for job_data in mock_jobs:
            job = JobPosting(
                title=job_data['title'],
                company=job_data['company'],
                location=job_data['location'],
                salary=job_data['salary'],
                description=job_data['description'],
                url=job_data['url'],
                date_posted=datetime.now().strftime('%Y-%m-%d'),
                job_site='MockJobs'
            )
            job.relevance_score = self.calculate_relevance_score(job)
            jobs.append(job)
        
        return jobs

class JobSearcher:
    """Main job searcher class."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize job searcher with configuration."""
        self.console = Console()
        self.config = self._load_config(config_path)
        self.searchers = self._initialize_searchers()
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            self.console.print(f"[red]Config file {config_path} not found![/red]")
            sys.exit(1)
        except yaml.YAMLError as e:
            self.console.print(f"[red]Error parsing config file: {e}[/red]")
            sys.exit(1)
    
    def _initialize_searchers(self) -> Dict[str, JobSiteSearcher]:
        """Initialize job site searchers based on config."""
        searchers = {}
        
        # Load real job sites
        real_sites = self.config.get('real_job_sites', {})
        
        if real_sites.get('indeed', False):
            searchers['indeed'] = IndeedSearcher(self.config)
        
        if real_sites.get('remoteok', False):
            searchers['remoteok'] = RemoteOKSearcher(self.config)
        
        if real_sites.get('angelco', False):
            searchers['angelco'] = AngelCoSearcher(self.config)
        
        if real_sites.get('hackernews', False):
            searchers['hackernews'] = HackerNewsJobsSearcher(self.config)
        
        if real_sites.get('usajobs', False):
            searchers['usajobs'] = USAJobsSearcher(self.config)
        
        if real_sites.get('rss', False):
            searchers['rss'] = RSSJobSearcher(self.config)
        
        if real_sites.get('github_alt', False):
            searchers['github_alt'] = GitHubJobsAlternative(self.config)
        
        if real_sites.get('weworkremotely', False):  # ✅ REAL DATA
            searchers['weworkremotely'] = WeWorkRemotelySearcher(self.config)
        
        if real_sites.get('remoteok', False):  # ✅ REAL DATA - Official API
            searchers['remoteok'] = RemoteOKSearcher(self.config)
        
        if real_sites.get('glassdoor', False):
            # searchers['glassdoor'] = GlassdoorSearcher(self.config)  # Not implemented yet
            pass
            
        if real_sites.get('linkedin', False):
            # searchers['linkedin'] = LinkedInSearcher(self.config)  # Not implemented yet
            pass
            
        if real_sites.get('stackoverflow', False):
            # searchers['stackoverflow'] = StackOverflowSearcher(self.config)  # Deprecated
            pass
            
        if real_sites.get('github_jobs', False):
            # searchers['github_jobs'] = GitHubJobsSearcher(self.config)  # Discontinued
            pass
        
        # Load mock/testing job sites (only if enabled)
        mock_sites = self.config.get('mock_job_sites', {})
        
        # Removed noflap - bad name and not needed
        
        if mock_sites.get('flexjobs', False):  # 🔧 Mock flexible jobs
            searchers['flexjobs'] = FlexJobsSearcher(self.config)
        
        if mock_sites.get('gamedev', False):  # 🔧 Mock Unity/game dev jobs
            searchers['gamedev'] = GameDevJobsSearcher(self.config)
        
        if mock_sites.get('mock', False):  # 🔧 Basic mock data
            searchers['mock'] = MockJobSearcher(self.config)
        
        return searchers
    
    def load_scraped_jobs(self) -> List[JobPosting]:
        """Load jobs from the JSON file created by the JavaScript scraper."""
        try:
            with open('jobs.json', 'r') as f:
                scraped_jobs = json.load(f)
                return [JobPosting(
                    title=job['title'],
                    company=job['company'],
                    location=job['location'],
                    salary="Not specified",
                    description="Description unavailable initially",
                    url=job['url'],
                    date_posted=datetime.now().strftime('%Y-%m-%d'),
                    job_site="JavaScript Scraper"
                ) for job in scraped_jobs]
        except FileNotFoundError:
            self.console.print("[red]No jobs.json file found. Please run the JavaScript scraper first.[/red]")
            return []

    def search_jobs(self) -> List[JobPosting]:
        """Search for jobs across all enabled sites and include those loaded from scraper."""
        all_jobs = []
        # Load jobs from JavaScript scraper
        all_jobs.extend(self.load_scraped_jobs())

        search_terms = self.config.get('search_terms', [])
        locations = self.config.get('locations', [])

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:

            for site_name, searcher in self.searchers.items():
                for term in search_terms:
                    for location in locations:
                        task = progress.add_task(
                            f"Searching {site_name} for '{term}' in {location}...",
                            total=None
                        )

                        try:
                            jobs = searcher.search(term, location)
                            all_jobs.extend(jobs)
                            progress.update(task, completed=True)
                            time.sleep(1)  # Rate limiting
                        except Exception as e:
                            self.console.print(f"[red]Error searching {site_name}: {e}[/red]")
                            progress.update(task, completed=True)
                            continue
        
        return self._filter_and_deduplicate(all_jobs)
    
    def _filter_and_deduplicate(self, jobs: List[JobPosting]) -> List[JobPosting]:
        """Filter and deduplicate job postings."""
        # Remove duplicates based on title and company
        seen = set()
        unique_jobs = []
        
        for job in jobs:
            key = (job.title.lower(), job.company.lower())
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)
        
        # Filter based on criteria
        filtered_jobs = []
        filters = self.config.get('filters', {})
        
        for job in unique_jobs:
            # Check excluded keywords
            excluded_keywords = filters.get('excluded_keywords', [])
            if any(keyword.lower() in job.description.lower() or 
                   keyword.lower() in job.title.lower() 
                   for keyword in excluded_keywords):
                continue
            
            # Check minimum relevance score
            min_score = self.config.get('notifications', {}).get('min_relevance_score', 0)
            if job.relevance_score < min_score:
                continue
            
            filtered_jobs.append(job)
        
        # Sort by relevance score
        filtered_jobs.sort(key=lambda x: x.relevance_score, reverse=True)
        
        # Limit results
        max_results = self.config.get('output', {}).get('max_results', 50)
        return filtered_jobs[:max_results]
    
    def display_results(self, jobs: List[JobPosting]):
        """Display search results in a formatted table."""
        if not jobs:
            self.console.print("[yellow]No jobs found matching your criteria.[/yellow]")
            return
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Title", style="cyan", no_wrap=True)
        table.add_column("Company", style="green")
        table.add_column("Location", style="yellow")
        table.add_column("Salary", style="red")
        table.add_column("Site", style="blue")
        table.add_column("Score", style="magenta")
        
        for job in jobs:
            table.add_row(
                job.title[:30] + "..." if len(job.title) > 30 else job.title,
                job.company[:20] + "..." if len(job.company) > 20 else job.company,
                job.location[:15] + "..." if len(job.location) > 15 else job.location,
                job.salary[:15] + "..." if len(job.salary) > 15 else job.salary,
                job.job_site,
                f"{job.relevance_score:.1f}"
            )
        
        self.console.print(table)
        self.console.print(f"\n[green]Found {len(jobs)} jobs matching your criteria![/green]")
    
    def save_results(self, jobs: List[JobPosting]):
        """Save results to files in specified formats."""
        if not jobs:
            return
        
        output_config = self.config.get('output', {})
        if not output_config.get('save_results', True):
            return
        
        results_dir = output_config.get('results_dir', 'results')
        os.makedirs(results_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save as CSV
        if 'csv' in output_config.get('export_formats', []):
            csv_path = os.path.join(results_dir, f'jobs_{timestamp}.csv')
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                if jobs:
                    writer = csv.DictWriter(f, fieldnames=jobs[0].to_dict().keys())
                    writer.writeheader()
                    for job in jobs:
                        writer.writerow(job.to_dict())
            self.console.print(f"[green]Results saved to {csv_path}[/green]")
        
        # Save as JSON
        if 'json' in output_config.get('export_formats', []):
            json_path = os.path.join(results_dir, f'jobs_{timestamp}.json')
            with open(json_path, 'w') as f:
                json.dump([job.to_dict() for job in jobs], f, indent=2)
            self.console.print(f"[green]Results saved to {json_path}[/green]")
        
        # Save as HTML
        if 'html' in output_config.get('export_formats', []):
            html_path = os.path.join(results_dir, f'jobs_{timestamp}.html')
            self._save_html_report(jobs, html_path)
            self.console.print(f"[green]Results saved to {html_path}[/green]")
    
    def _save_html_report(self, jobs: List[JobPosting], filepath: str):
        """Save jobs as HTML report."""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Job Search Results</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .job { border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }
                .title { font-size: 18px; font-weight: bold; color: #333; }
                .company { color: #666; margin: 5px 0; }
                .details { color: #888; font-size: 14px; }
                .score { background: #e7f3ff; padding: 2px 6px; border-radius: 3px; }
                .description { margin: 10px 0; }
            </style>
        </head>
        <body>
            <h1>Job Search Results</h1>
            <p>Generated on: {}</p>
            <p>Total jobs found: {}</p>
        """.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), len(jobs))
        
        for job in jobs:
            html_content += f"""
            <div class="job">
                <div class="title">{job.title}</div>
                <div class="company">{job.company}</div>
                <div class="details">
                    Location: {job.location} | Salary: {job.salary} | 
                    Site: {job.job_site} | 
                    <span class="score">Score: {job.relevance_score:.1f}</span>
                </div>
                <div class="description">{job.description[:200]}...</div>
                <div><a href="{job.url}" target="_blank">View Job</a></div>
            </div>
            """
        
        html_content += """
        </body>
        </html>
        """
        
        with open(filepath, 'w') as f:
            f.write(html_content)

@click.command()
@click.option('--config', default='config.yaml', help='Path to configuration file')
@click.option('--no-save', is_flag=True, help='Don\'t save results to files')
@click.option('--quiet', is_flag=True, help='Minimal output')
def main(config, no_save, quiet):
    """Job Searcher - Find jobs that match your criteria."""
    try:
        searcher = JobSearcher(config)
        
        if not quiet:
            searcher.console.print(Panel.fit(
                "[bold blue]Job Searcher[/bold blue]\n"
                "Searching for jobs based on your criteria...",
                border_style="blue"
            ))
        
        # Search for jobs
        jobs = searcher.search_jobs()
        
        # Display results
        if not quiet:
            searcher.display_results(jobs)
        
        # Save results
        if not no_save:
            searcher.save_results(jobs)
        
    except KeyboardInterrupt:
        print("\nSearch cancelled by user.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
