#!/usr/bin/env python3
"""
Alternative gaming job scrapers - InGameJob.com and RemoteGameJobs.com
These sites appear more scrapeable than Hitmarker.net as of 2024
"""

import requests
import time
from typing import List, Dict, Any
from rich.console import Console
from datetime import datetime
from urllib.parse import quote_plus, urljoin
from bs4 import BeautifulSoup
import re

# JobPosting class for gaming job data
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

def get_ingamejob_jobs(search_terms: List[str] = None, max_jobs: int = 20) -> List[JobPosting]:
    """
    Fetch jobs from InGameJob.com - appears to be more scrapeable than Hitmarker
    """
    console = Console()
    
    try:
        base_url = "https://ingamejob.com/en"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
        
        console.print(f"[blue]🎮 Fetching jobs from InGameJob.com...[/blue]")
        
        response = requests.get(base_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try multiple selectors for job listings
        job_selectors = [
            '.job-card',
            '.job-item', 
            '.job-listing',
            'a[href*="/job/"]',
            '.premium-jobs a',
            '.new-jobs a'
        ]
        
        job_elements = []
        for selector in job_selectors:
            job_elements = soup.select(selector)
            if job_elements:
                console.print(f"[green]✅ Found {len(job_elements)} jobs using selector: {selector}[/green]")
                break
        
        job_postings = []
        
        for job_elem in job_elements[:max_jobs]:
            try:
                job_posting = parse_ingamejob_element(job_elem, search_terms, base_url)
                if job_posting:
                    job_postings.append(job_posting)
            except Exception as e:
                console.print(f"[red]⚠️  Error parsing InGameJob: {e}[/red]")
                continue
        
        # Sort by relevance score
        job_postings.sort(key=lambda x: x.relevance_score, reverse=True)
        
        console.print(f"[cyan]📊 Processed {len(job_postings)} jobs from InGameJob[/cyan]")
        return job_postings
        
    except Exception as e:
        console.print(f"[red]❌ Error fetching InGameJob jobs: {e}[/red]")
        return []

def get_remotegamejobs_jobs(search_terms: List[str] = None, max_jobs: int = 20) -> List[JobPosting]:
    """
    Fetch jobs from RemoteGameJobs.com - focuses on remote gaming positions
    """
    console = Console()
    
    try:
        base_url = "https://remotegamejobs.com"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        
        console.print(f"[blue]🎮 Fetching jobs from RemoteGameJobs.com...[/blue]")
        
        response = requests.get(base_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try selectors based on analysis
        job_selectors = [
            '.job-box',
            '.job-listing',
            '.job-card',
            'a[href*="/jobs/"]'
        ]
        
        job_elements = []
        for selector in job_selectors:
            job_elements = soup.select(selector)
            if job_elements:
                console.print(f"[green]✅ Found {len(job_elements)} jobs using selector: {selector}[/green]")
                break
        
        job_postings = []
        
        for job_elem in job_elements[:max_jobs]:
            try:
                job_posting = parse_remotegamejobs_element(job_elem, search_terms, base_url)
                if job_posting:
                    job_postings.append(job_posting)
            except Exception as e:
                console.print(f"[red]⚠️  Error parsing RemoteGameJobs: {e}[/red]")
                continue
        
        # Sort by relevance score
        job_postings.sort(key=lambda x: x.relevance_score, reverse=True)
        
        console.print(f"[cyan]📊 Processed {len(job_postings)} jobs from RemoteGameJobs[/cyan]")
        return job_postings
        
    except Exception as e:
        console.print(f"[red]❌ Error fetching RemoteGameJobs jobs: {e}[/red]")
        return []

def parse_ingamejob_element(job_elem, search_terms: List[str], base_url: str) -> JobPosting:
    """Parse a job element from InGameJob.com"""
    try:
        # Extract title
        title_elem = job_elem.find(['h2', 'h3', 'h4', '.job-title']) or job_elem
        title = title_elem.get_text(strip=True) if title_elem else 'Unknown Position'
        
        # Extract company
        company = 'Unknown Company'
        # Look for company info in various ways
        company_elem = job_elem.find(class_=re.compile(r'company', re.I))
        if company_elem:
            company = company_elem.get_text(strip=True)
        
        # Extract location
        location_elem = job_elem.find(class_=re.compile(r'location', re.I))
        location = location_elem.get_text(strip=True) if location_elem else 'Remote/Not specified'
        
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
        
        # Calculate relevance
        relevance_score = calculate_gaming_relevance_score(title, description, company, search_terms)
        
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
            job_site="InGameJob",
            relevance_score=relevance_score
        )
        
    except Exception as e:
        return None

def parse_remotegamejobs_element(job_elem, search_terms: List[str], base_url: str) -> JobPosting:
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
        relevance_score = calculate_gaming_relevance_score(title, description, company, search_terms)
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
            job_site="RemoteGameJobs",
            relevance_score=min(relevance_score, 100.0)
        )
        
    except Exception as e:
        return None

def calculate_gaming_relevance_score(title: str, description: str, company: str, search_terms: List[str] = None) -> float:
    """Calculate relevance score for gaming jobs"""
    if not search_terms:
        search_terms = ['unity', 'game', 'c#', 'web', 'frontend', 'backend']
    
    score = 0.0
    title_lower = title.lower()
    description_lower = description.lower()
    company_lower = company.lower()
    
    # Unity/Game development bonus
    unity_terms = ['unity', 'unreal', 'c#', 'csharp', 'game developer', 'gamedev', '3d', 'mobile game', 'indie']
    for term in unity_terms:
        if term in title_lower:
            score += 25
        if term in description_lower:
            score += 15
        if term in company_lower:
            score += 10
    
    # Gaming industry terms
    gaming_terms = ['game', 'gaming', 'esports', 'indie', 'studio', 'entertainment', 'interactive']
    for term in gaming_terms:
        if term in title_lower:
            score += 20
        if term in description_lower:
            score += 10
        if term in company_lower:
            score += 15
    
    # Web development terms
    web_terms = ['react', 'javascript', 'typescript', 'frontend', 'backend', 'full stack', 'web', 'node']
    for term in web_terms:
        if term in title_lower:
            score += 15
        if term in description_lower:
            score += 8
    
    # General programming terms
    general_terms = ['developer', 'engineer', 'programmer', 'software', 'coding', 'technical']
    for term in general_terms:
        if term in title_lower:
            score += 10
        if term in description_lower:
            score += 5
    
    return max(min(score, 100.0), 0.0)

class GamingJobsSearcher:
    """Job searcher for gaming industry using multiple alternative sites"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.console = Console()
    
    def search_jobs(self, query: str) -> List[JobPosting]:
        """Search for jobs across multiple gaming job sites"""
        search_terms = query.lower().split()
        
        if 'search_terms' in self.config:
            search_terms.extend([term.lower() for term in self.config['search_terms']])
        
        all_jobs = []
        
        # Search InGameJob
        time.sleep(2)  # Respectful delay
        ingame_jobs = get_ingamejob_jobs(search_terms=search_terms, max_jobs=10)
        all_jobs.extend(ingame_jobs)
        
        # Search RemoteGameJobs
        time.sleep(2)  # Respectful delay
        remote_jobs = get_remotegamejobs_jobs(search_terms=search_terms, max_jobs=10)
        all_jobs.extend(remote_jobs)
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_jobs = []
        for job in all_jobs:
            if job.url not in seen_urls:
                unique_jobs.append(job)
                seen_urls.add(job.url)
        
        # Sort by relevance
        unique_jobs.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return unique_jobs[:15]  # Return top 15 most relevant

if __name__ == "__main__":
    """Test the alternative gaming job scrapers"""
    console = Console()
    
    console.print("[yellow]🧪 Testing alternative gaming job scrapers...[/yellow]")
    
    # Test InGameJob
    console.print("\n[blue]Testing InGameJob.com...[/blue]")
    ingame_jobs = get_ingamejob_jobs(['unity', 'developer'], max_jobs=3)
    
    for job in ingame_jobs:
        console.print(f"\n[bold blue]🎮 {job.title}[/bold blue]")
        console.print(f"   🏢 {job.company}")
        console.print(f"   📍 {job.location}")
        console.print(f"   🔗 {job.url}")
        console.print(f"   ⭐ Relevance: {job.relevance_score:.1f}/100")
    
    # Test RemoteGameJobs
    console.print("\n[blue]Testing RemoteGameJobs.com...[/blue]")
    remote_jobs = get_remotegamejobs_jobs(['unity', 'developer'], max_jobs=3)
    
    for job in remote_jobs:
        console.print(f"\n[bold green]🎮 {job.title}[/bold green]")
        console.print(f"   🏢 {job.company}")
        console.print(f"   📍 {job.location}")
        console.print(f"   🔗 {job.url}")
        console.print(f"   ⭐ Relevance: {job.relevance_score:.1f}/100")