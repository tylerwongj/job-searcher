#!/usr/bin/env python3
"""
Dice.com job scraper - Tech-focused job board
Website: https://dice.com
"""

import requests
import time
import json
import re
from typing import List, Dict, Any
from rich.console import Console
from datetime import datetime
from urllib.parse import quote_plus

# Simple JobPosting class for Dice data
class JobPosting:
    def __init__(self, title: str, company: str, location: str, salary: str, 
                 description: str, url: str, date_posted: str, job_site: str, 
                 relevance_score: float = 0.0):
        self.title = title
        self.company = company
        self.location = location
        self.salary = salary
        self.description = description
        self.url = url
        self.date_posted = date_posted
        self.job_site = job_site
        self.relevance_score = relevance_score
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'salary': self.salary,
            'description': self.description,
            'url': self.url,
            'date_posted': self.date_posted,
            'job_site': self.job_site,
            'relevance_score': self.relevance_score
        }

def get_dice_jobs(search_terms: List[str] = None, location: str = "Remote", max_jobs: int = 20) -> List[JobPosting]:
    """
    Fetch real job data from Dice.com using web scraping.
    
    Args:
        search_terms: List of terms to search for
        location: Location to search in
        max_jobs: Maximum number of jobs to return
    
    Returns:
        List of JobPosting objects with real data
    """
    console = Console()
    
    try:
        # Build search query
        if search_terms:
            query = " ".join(search_terms)
        else:
            query = "web developer"
        
        # Dice.com search URL
        search_url = f"https://www.dice.com/jobs?q={quote_plus(query)}&location={quote_plus(location)}&radius=30&radiusUnit=mi&page=1&pageSize=20&language=en"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        
        console.print(f"[blue]🎲 Fetching jobs from Dice.com...[/blue]")
        console.print(f"[dim]Query: {query}, Location: {location}[/dim]")
        
        # Make request with respectful delay
        response = requests.get(search_url, headers=headers, timeout=15)
        
        # Check for blocking
        if response.status_code == 403:
            console.print(f"[red]❌ Dice.com blocked the request (403 Forbidden)[/red]")
            return []
        
        response.raise_for_status()
        
        # Dice uses React/Next.js, so job data is often in JSON within the page
        page_content = response.text
        
        # Look for JSON data in the page (Next.js data)
        job_postings = []
        
        # Try to find JSON data embedded in the page
        json_patterns = [
            r'window\.__NEXT_DATA__\s*=\s*({.+?});',
            r'window\.__INITIAL_STATE__\s*=\s*({.+?});',
            r'"jobs":\s*(\[.+?\])',
            r'"searchResults":\s*({.+?})',
        ]
        
        jobs_found = False
        
        for pattern in json_patterns:
            matches = re.search(pattern, page_content, re.DOTALL)
            if matches:
                try:
                    json_str = matches.group(1)
                    data = json.loads(json_str)
                    
                    # Extract jobs from various possible structures
                    jobs_data = extract_jobs_from_data(data)
                    
                    if jobs_data:
                        console.print(f"[green]✅ Found {len(jobs_data)} jobs in JSON data[/green]")
                        jobs_found = True
                        
                        # Process jobs
                        for job_data in jobs_data[:max_jobs]:
                            job_posting = create_job_posting_from_dice(job_data, search_terms)
                            if job_posting:
                                job_postings.append(job_posting)
                        
                        break
                        
                except (json.JSONDecodeError, KeyError) as e:
                    continue
        
        # Fallback: Parse HTML directly if JSON extraction fails
        if not jobs_found:
            console.print(f"[yellow]⚠️  JSON extraction failed, trying HTML parsing...[/yellow]")
            job_postings = parse_dice_html(page_content, search_terms, max_jobs)
        
        # Sort by relevance score (highest first)
        job_postings.sort(key=lambda x: x.relevance_score, reverse=True)
        
        console.print(f"[cyan]📊 Processed {len(job_postings)} jobs from Dice.com[/cyan]")
        
        return job_postings
        
    except requests.RequestException as e:
        console.print(f"[red]❌ Error fetching Dice jobs: {e}[/red]")
        return []
    except Exception as e:
        console.print(f"[red]❌ Unexpected error: {e}[/red]")
        return []

def extract_jobs_from_data(data: Dict) -> List[Dict]:
    """Extract job listings from various JSON data structures."""
    jobs = []
    
    # Try different possible data structures
    possible_paths = [
        ['props', 'pageProps', 'jobs'],
        ['props', 'pageProps', 'searchResults', 'jobs'],
        ['props', 'pageProps', 'initialState', 'jobs'],
        ['jobs'],
        ['searchResults', 'jobs'],
        ['data', 'jobs'],
    ]
    
    for path in possible_paths:
        current = data
        try:
            for key in path:
                if isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    break
            else:
                # Successfully navigated the path
                if isinstance(current, list):
                    return current
        except (KeyError, TypeError):
            continue
    
    return jobs

def parse_dice_html(page_content: str, search_terms: List[str], max_jobs: int) -> List[JobPosting]:
    """Fallback HTML parsing for Dice.com when JSON extraction fails."""
    try:
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(page_content, 'html.parser')
        job_postings = []
        
        # Look for job cards/listings in various possible selectors
        job_selectors = [
            '.search-result',
            '.job-tile',
            '.job-card',
            '[data-testid="job-card"]',
            '.serp-result-content'
        ]
        
        job_elements = []
        for selector in job_selectors:
            job_elements = soup.select(selector)
            if job_elements:
                break
        
        if not job_elements:
            return []
        
        for job_elem in job_elements[:max_jobs]:
            try:
                # Extract job details
                title_elem = job_elem.select_one('h3 a, h2 a, .job-title a, [data-testid="job-title"] a')
                title = title_elem.get_text(strip=True) if title_elem else 'Unknown Position'
                
                # Job URL
                job_url = title_elem.get('href', '') if title_elem else ''
                if job_url and not job_url.startswith('http'):
                    job_url = 'https://dice.com' + job_url
                
                # Company
                company_elem = job_elem.select_one('.company, .employer, [data-testid="company"]')
                company = company_elem.get_text(strip=True) if company_elem else 'Unknown Company'
                
                # Location
                location_elem = job_elem.select_one('.location, .job-location, [data-testid="location"]')
                location = location_elem.get_text(strip=True) if location_elem else 'Not specified'
                
                # Salary
                salary_elem = job_elem.select_one('.salary, .compensation, [data-testid="salary"]')
                salary = salary_elem.get_text(strip=True) if salary_elem else 'Salary not specified'
                
                # Description (brief)
                desc_elem = job_elem.select_one('.description, .job-summary, .snippet')
                description = desc_elem.get_text(strip=True) if desc_elem else f"{title} at {company}"
                
                # Calculate relevance score
                relevance_score = calculate_dice_relevance_score(title, description, search_terms)
                
                job_posting = JobPosting(
                    title=title,
                    company=company,
                    location=location,
                    salary=salary,
                    description=description[:500],
                    url=job_url or 'https://dice.com',
                    date_posted=datetime.now().strftime('%Y-%m-%d'),
                    job_site="Dice",
                    relevance_score=relevance_score
                )
                
                job_postings.append(job_posting)
                
            except Exception as e:
                continue
        
        return job_postings
        
    except Exception as e:
        return []

def create_job_posting_from_dice(job_data: Dict, search_terms: List[str]) -> JobPosting:
    """Create JobPosting from Dice job data."""
    try:
        title = job_data.get('title', job_data.get('jobTitle', 'Unknown Position'))
        company = job_data.get('company', job_data.get('companyName', 'Unknown Company'))
        location = job_data.get('location', job_data.get('jobLocation', 'Not specified'))
        
        # Handle salary
        salary = 'Salary not specified'
        if 'salary' in job_data:
            salary = str(job_data['salary'])
        elif 'minSalary' in job_data and 'maxSalary' in job_data:
            min_sal = job_data['minSalary']
            max_sal = job_data['maxSalary']
            salary = f"${min_sal:,} - ${max_sal:,}"
        
        # Description
        description = job_data.get('description', job_data.get('summary', ''))
        if not description:
            description = f"{title} position at {company}"
        
        # Job URL
        job_url = job_data.get('url', job_data.get('jobUrl', 'https://dice.com'))
        if job_url and not job_url.startswith('http'):
            job_url = 'https://dice.com' + job_url
        
        # Date posted
        date_posted = job_data.get('datePosted', datetime.now().strftime('%Y-%m-%d'))
        
        # Calculate relevance score
        relevance_score = calculate_dice_relevance_score(title, description, search_terms)
        
        return JobPosting(
            title=title,
            company=company,
            location=location,
            salary=salary,
            description=description[:500],
            url=job_url,
            date_posted=date_posted,
            job_site="Dice",
            relevance_score=relevance_score
        )
        
    except Exception as e:
        return None

def calculate_dice_relevance_score(title: str, description: str, search_terms: List[str] = None) -> float:
    """Calculate relevance score for a Dice job."""
    if not search_terms:
        search_terms = ['unity', 'web', 'react', 'javascript', 'c#', 'typescript', 'frontend', 'backend', 'full stack']
    
    score = 0.0
    title_lower = title.lower()
    description_lower = description.lower()
    
    # Unity/Game development bonus
    unity_terms = ['unity', 'game', 'c#', 'csharp', 'gamedev', 'unreal', '3d']
    for term in unity_terms:
        if term in title_lower:
            score += 20
        if term in description_lower:
            score += 10
    
    # Web development terms
    web_terms = ['react', 'javascript', 'typescript', 'frontend', 'backend', 'full stack', 'web', 'node', 'vue', 'angular']
    for term in web_terms:
        if term in title_lower:
            score += 15
        if term in description_lower:
            score += 8
    
    # General programming terms
    general_terms = ['developer', 'engineer', 'software', 'programmer', 'coding']
    for term in general_terms:
        if term in title_lower:
            score += 5
        if term in description_lower:
            score += 3
    
    # Tech skills bonus
    tech_terms = ['python', 'java', 'sql', 'aws', 'docker', 'kubernetes', 'api', 'database']
    for term in tech_terms:
        if term in title_lower:
            score += 8
        if term in description_lower:
            score += 4
    
    return min(score, 100.0)  # Cap at 100

class DiceSearcher:
    """Job searcher for Dice.com using web scraping."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.console = Console()
    
    def search_jobs(self, query: str, location: str = "Remote") -> List[JobPosting]:
        """Search for jobs on Dice.com."""
        search_terms = query.lower().split()
        
        # Get search terms from config
        if 'search_terms' in self.config:
            search_terms.extend([term.lower() for term in self.config['search_terms']])
        
        # Respectful delay
        time.sleep(2)
        
        return get_dice_jobs(search_terms=search_terms, location=location, max_jobs=20)

if __name__ == "__main__":
    """Test the Dice scraper."""
    console = Console()
    
    console.print("[yellow]🧪 Testing Dice.com scraper...[/yellow]")
    
    # Test with Unity and web development terms
    search_terms = ['unity', 'react', 'javascript', 'c#', 'web developer']
    jobs = get_dice_jobs(search_terms=search_terms, max_jobs=5)
    
    console.print(f"\n[green]Found {len(jobs)} jobs:[/green]")
    
    for job in jobs:
        console.print(f"\n[bold blue]🎲 {job.title}[/bold blue]")
        console.print(f"   🏢 {job.company}")
        console.print(f"   📍 {job.location}")
        console.print(f"   💰 {job.salary}")
        console.print(f"   🔗 {job.url}")
        console.print(f"   ⭐ Relevance: {job.relevance_score:.1f}/100")