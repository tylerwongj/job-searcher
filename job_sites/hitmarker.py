#!/usr/bin/env python3
"""
Hitmarker.net job scraper - Gaming and esports jobs
Website: https://hitmarker.net/jobs
"""

import requests
import time
from typing import List, Dict, Any
from rich.console import Console
from datetime import datetime
from urllib.parse import quote_plus, urljoin
import re

# Simple JobPosting class for Hitmarker data
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

def get_hitmarker_jobs(search_terms: List[str] = None, max_jobs: int = 20) -> List[JobPosting]:
    """
    Fetch real job data from Hitmarker.net using web scraping.
    
    NOTE: As of July 2024, Hitmarker.net appears to have anti-scraping measures
    that return corrupted/encoded content. This function now falls back to
    alternative gaming job sites that are more scrapeable.
    
    Args:
        search_terms: List of terms to search for
        max_jobs: Maximum number of jobs to return
    
    Returns:
        List of JobPosting objects with real data
    """
    console = Console()
    
    try:
        # Hitmarker.net jobs page
        base_url = "https://hitmarker.net/jobs"
        
        # Build search URL with query parameters
        if search_terms:
            query = " ".join(search_terms)
            search_url = f"{base_url}?q={quote_plus(query)}"
        else:
            search_url = base_url
        
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
        }
        
        console.print(f"[blue]🎮 Attempting to fetch jobs from Hitmarker.net...[/blue]")
        
        # Make request with respectful delay
        response = requests.get(search_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Check if content looks corrupted/encoded (anti-scraping measure)
        content_preview = response.text[:200]
        if len(content_preview.strip()) < 50 or '\ufffd' in content_preview or not content_preview.isprintable():
            console.print(f"[yellow]⚠️  Hitmarker.net appears to have anti-scraping measures active[/yellow]")
            console.print(f"[cyan]🔄 Falling back to alternative gaming job sites...[/cyan]")
            return get_alternative_gaming_jobs(search_terms, max_jobs)
        
        # Parse HTML content
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find job listings - Hitmarker uses various possible selectors
        job_selectors = [
            '.job-listing',
            '.job-card',
            '.job-item',
            '.job',
            '.listing',
            'article',
            '.opportunity'
        ]
        
        job_elements = []
        for selector in job_selectors:
            job_elements = soup.select(selector)
            if job_elements:
                console.print(f"[green]✅ Found {len(job_elements)} jobs using selector: {selector}[/green]")
                break
        
        if not job_elements:
            # Try to find any links that look like job postings
            job_elements = soup.find_all('a', href=True)
            job_elements = [elem for elem in job_elements if '/jobs/' in elem.get('href', '')]
            console.print(f"[yellow]⚠️  Using fallback method, found {len(job_elements)} job links[/yellow]")
        
        if not job_elements:
            console.print(f"[yellow]⚠️  No jobs found on Hitmarker.net, using alternative sites...[/yellow]")
            return get_alternative_gaming_jobs(search_terms, max_jobs)
        
        job_postings = []
        
        for job_elem in job_elements[:max_jobs]:
            try:
                job_posting = parse_hitmarker_job_element(job_elem, search_terms)
                if job_posting:
                    job_postings.append(job_posting)
                    
            except Exception as e:
                console.print(f"[red]⚠️  Error parsing job: {e}[/red]")
                continue
        
        # Sort by relevance score (highest first)
        job_postings.sort(key=lambda x: x.relevance_score, reverse=True)
        
        console.print(f"[cyan]📊 Processed {len(job_postings)} jobs from Hitmarker[/cyan]")
        
        return job_postings
        
    except requests.RequestException as e:
        console.print(f"[red]❌ Error fetching Hitmarker jobs: {e}[/red]")
        console.print(f"[cyan]🔄 Trying alternative gaming job sites...[/cyan]")
        return get_alternative_gaming_jobs(search_terms, max_jobs)
    except Exception as e:
        console.print(f"[red]❌ Unexpected error: {e}[/red]")
        console.print(f"[cyan]🔄 Trying alternative gaming job sites...[/cyan]")
        return get_alternative_gaming_jobs(search_terms, max_jobs)

def parse_hitmarker_job_element(job_elem, search_terms: List[str]) -> JobPosting:
    """Parse a single job element from Hitmarker."""
    try:
        # Extract job title
        title_selectors = ['h1', 'h2', 'h3', '.title', '.job-title', '.position']
        title = 'Unknown Position'
        title_elem = None
        
        for selector in title_selectors:
            title_elem = job_elem.select_one(selector)
            if title_elem:
                title = title_elem.get_text(strip=True)
                break
        
        # If no title found in current element, it might be a link element itself
        if title == 'Unknown Position' and job_elem.name == 'a':
            title = job_elem.get_text(strip=True) or title_elem.get('title', 'Unknown Position')
        
        # Extract company
        company_selectors = ['.company', '.employer', '.organization', '.studio']
        company = 'Unknown Company'
        
        for selector in company_selectors:
            company_elem = job_elem.select_one(selector)
            if company_elem:
                company = company_elem.get_text(strip=True)
                break
        
        # Extract location
        location_selectors = ['.location', '.job-location', '.place', '.region']
        location = 'Not specified'
        
        for selector in location_selectors:
            location_elem = job_elem.select_one(selector)
            if location_elem:
                location = location_elem.get_text(strip=True)
                break
        
        # Extract job URL
        job_url = 'https://hitmarker.net'
        if job_elem.name == 'a' and job_elem.get('href'):
            job_url = job_elem['href']
        else:
            link_elem = job_elem.find('a', href=True)
            if link_elem:
                job_url = link_elem['href']
        
        # Make URL absolute
        if job_url.startswith('/'):
            job_url = 'https://hitmarker.net' + job_url
        elif not job_url.startswith('http'):
            job_url = 'https://hitmarker.net/jobs/' + job_url
        
        # Extract description/summary
        desc_selectors = ['.description', '.summary', '.excerpt', '.job-summary']
        description = f"{title} at {company}"
        
        for selector in desc_selectors:
            desc_elem = job_elem.select_one(selector)
            if desc_elem:
                description = desc_elem.get_text(strip=True)
                break
        
        # Extract salary if available
        salary_selectors = ['.salary', '.compensation', '.pay', '.wage']
        salary = 'Salary not specified'
        
        for selector in salary_selectors:
            salary_elem = job_elem.select_one(selector)
            if salary_elem:
                salary = salary_elem.get_text(strip=True)
                break
        
        # Calculate relevance score
        relevance_score = calculate_hitmarker_relevance_score(title, description, company, search_terms)
        
        # Don't create job if it has very low relevance (likely not a real job posting)
        if relevance_score < 5 and not any(term in title.lower() for term in ['unity', 'game', 'developer', 'engineer']):
            return None
        
        return JobPosting(
            title=title,
            company=company,
            location=location,
            salary=salary,
            description=description[:500],
            url=job_url,
            date_posted=datetime.now().strftime('%Y-%m-%d'),
            job_site="Hitmarker",
            relevance_score=relevance_score
        )
        
    except Exception as e:
        return None

def calculate_hitmarker_relevance_score(title: str, description: str, company: str, search_terms: List[str] = None) -> float:
    """Calculate relevance score for a Hitmarker job."""
    if not search_terms:
        search_terms = ['unity', 'game', 'c#', 'web', 'frontend', 'backend']
    
    score = 0.0
    title_lower = title.lower()
    description_lower = description.lower()
    company_lower = company.lower()
    
    # Unity/Game development bonus (this is a gaming site, so these should score high)
    unity_terms = ['unity', 'unreal', 'c#', 'csharp', 'game developer', 'gamedev', '3d', 'mobile game', 'indie', 'studio']
    for term in unity_terms:
        if term in title_lower:
            score += 25  # Higher bonus for game industry site
        if term in description_lower:
            score += 15
        if term in company_lower:
            score += 10
    
    # Gaming industry terms
    gaming_terms = ['game', 'gaming', 'esports', 'indie', 'studio', 'entertainment', 'interactive', 'digital']
    for term in gaming_terms:
        if term in title_lower:
            score += 20
        if term in description_lower:
            score += 10
        if term in company_lower:
            score += 15
    
    # Web development terms (for game company web roles)
    web_terms = ['react', 'javascript', 'typescript', 'frontend', 'backend', 'full stack', 'web', 'node', 'vue', 'angular']
    for term in web_terms:
        if term in title_lower:
            score += 15
        if term in description_lower:
            score += 8
    
    # General programming terms
    general_terms = ['developer', 'engineer', 'programmer', 'software', 'coding', 'technical', 'technology']
    for term in general_terms:
        if term in title_lower:
            score += 10
        if term in description_lower:
            score += 5
    
    # Creative/design terms (relevant for game industry)
    creative_terms = ['ui', 'ux', 'design', 'creative', 'visual', 'art', 'artist', 'animator']
    for term in creative_terms:
        if term in title_lower:
            score += 12
        if term in description_lower:
            score += 6
    
    # Reduce score for non-technical roles
    non_tech_terms = ['marketing', 'sales', 'business', 'finance', 'hr', 'admin', 'support']
    for term in non_tech_terms:
        if term in title_lower:
            score -= 10
    
    return max(min(score, 100.0), 0.0)  # Cap between 0-100

def get_alternative_gaming_jobs(search_terms: List[str] = None, max_jobs: int = 20) -> List[JobPosting]:
    """
    Fallback function to fetch jobs from alternative gaming job sites
    when Hitmarker.net is not accessible due to anti-scraping measures.
    """
    console = Console()
    console.print(f"[blue]🎮 Fetching jobs from RemoteGameJobs.com (alternative)...[/blue]")
    
    try:
        base_url = "https://remotegamejobs.com"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        
        response = requests.get(base_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try selectors for RemoteGameJobs
        job_elements = soup.select('.job-box')
        
        if not job_elements:
            job_elements = soup.select('a[href*="/jobs/"]')
        
        console.print(f"[green]✅ Found {len(job_elements)} jobs from alternative site[/green]")
        
        job_postings = []
        
        for job_elem in job_elements[:max_jobs]:
            try:
                job_posting = parse_alternative_job_element(job_elem, search_terms, base_url)
                if job_posting:
                    job_postings.append(job_posting)
            except Exception as e:
                continue
        
        # Sort by relevance score
        job_postings.sort(key=lambda x: x.relevance_score, reverse=True)
        
        console.print(f"[cyan]📊 Processed {len(job_postings)} jobs from alternative gaming sites[/cyan]")
        return job_postings
        
    except Exception as e:
        console.print(f"[red]❌ Error fetching from alternative sites: {e}[/red]")
        return []

def parse_alternative_job_element(job_elem, search_terms: List[str], base_url: str) -> JobPosting:
    """Parse a job element from RemoteGameJobs.com"""
    try:
        # Extract title
        title_elem = job_elem.find(['h2', 'h3', 'h4', '.job-title']) or job_elem
        title = title_elem.get_text(strip=True) if title_elem else 'Unknown Position'
        
        # Extract company
        company = 'Unknown Company'
        company_elem = job_elem.find(class_=re.compile(r'company', re.I))
        if company_elem:
            company = company_elem.get_text(strip=True)
        
        # Location is likely "Remote" for this site
        location = 'Remote'
        
        # Extract URL
        job_url = base_url
        if job_elem.name == 'a' and job_elem.get('href'):
            job_url = urljoin(base_url, job_elem['href'])
        else:
            link_elem = job_elem.find('a', href=True)
            if link_elem:
                job_url = urljoin(base_url, link_elem['href'])
        
        # Extract description
        desc_text = job_elem.get_text(strip=True)
        description = desc_text[:200] + "..." if len(desc_text) > 200 else desc_text
        
        # Calculate relevance (higher for remote gaming jobs)
        relevance_score = calculate_hitmarker_relevance_score(title, description, company, search_terms)
        relevance_score += 10  # Bonus for being on a remote gaming site
        
        if relevance_score < 5:
            return None
        
        return JobPosting(
            title=title,
            company=company,
            location=location,
            salary='Salary not specified',
            description=description,
            url=job_url,
            date_posted=datetime.now().strftime('%Y-%m-%d'),
            job_site="RemoteGameJobs (Alternative)",
            relevance_score=min(relevance_score, 100.0)
        )
        
    except Exception as e:
        return None

class HitmarkerSearcher:
    """Job searcher for Hitmarker.net using web scraping."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.console = Console()
    
    def search_jobs(self, query: str) -> List[JobPosting]:
        """Search for jobs on Hitmarker.net."""
        search_terms = query.lower().split()
        
        # Get search terms from config
        if 'search_terms' in self.config:
            search_terms.extend([term.lower() for term in self.config['search_terms']])
        
        # Respectful delay (their robots.txt doesn't specify, so be conservative)
        time.sleep(2)
        
        return get_hitmarker_jobs(search_terms=search_terms, max_jobs=15)

if __name__ == "__main__":
    """Test the Hitmarker scraper."""
    console = Console()
    
    console.print("[yellow]🧪 Testing Hitmarker.net scraper...[/yellow]")
    
    # Test with Unity and game development terms
    search_terms = ['unity', 'game developer', 'c#', 'unreal', 'indie']
    jobs = get_hitmarker_jobs(search_terms=search_terms, max_jobs=5)
    
    console.print(f"\n[green]Found {len(jobs)} jobs:[/green]")
    
    for job in jobs:
        console.print(f"\n[bold blue]🎮 {job.title}[/bold blue]")
        console.print(f"   🏢 {job.company}")
        console.print(f"   📍 {job.location}")
        console.print(f"   💰 {job.salary}")
        console.print(f"   🔗 {job.url}")
        console.print(f"   ⭐ Relevance: {job.relevance_score:.1f}/100")