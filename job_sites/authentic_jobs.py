#!/usr/bin/env python3
"""
Authentic Jobs API scraper - Creative and tech jobs
Official API: https://authenticjobs.com/api/
"""

import requests
import time
from typing import List, Dict, Any
from rich.console import Console
from datetime import datetime

# Simple JobPosting class for Authentic Jobs data
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

def get_authentic_jobs(search_terms: List[str] = None, max_jobs: int = 20) -> List[JobPosting]:
    """
    Fetch real job data from Authentic Jobs using their official API.
    
    Args:
        search_terms: List of terms to search for
        max_jobs: Maximum number of jobs to return
    
    Returns:
        List of JobPosting objects with real data
    """
    console = Console()
    
    try:
        # Note: Authentic Jobs API requires a key, but for testing we'll try without
        # In production, you'd need to register for an API key
        base_url = "https://authenticjobs.com/api"
        
        # Try to get recent jobs first (no key required for some endpoints)
        recent_url = f"{base_url}/posts/recent/"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        
        console.print(f"[blue]🎨 Fetching jobs from Authentic Jobs API...[/blue]")
        
        # Make API request with respectful delay
        response = requests.get(recent_url, headers=headers, timeout=10)
        
        if response.status_code == 403 or response.status_code == 404:
            # API discontinued or key required - fallback to web scraping
            console.print(f"[yellow]⚠️  API unavailable (404), switching to web scraping...[/yellow]")
            return scrape_authentic_jobs_web(search_terms, max_jobs)
        
        response.raise_for_status()
        
        # Parse JSON response
        jobs_data = response.json()
        
        if isinstance(jobs_data, dict) and 'listings' in jobs_data:
            jobs_list = jobs_data['listings']
        elif isinstance(jobs_data, list):
            jobs_list = jobs_data
        else:
            console.print(f"[red]❌ Unexpected API response format[/red]")
            return []
        
        console.print(f"[green]✅ Retrieved {len(jobs_list)} jobs from Authentic Jobs[/green]")
        
        # Convert to JobPosting objects
        job_postings = []
        
        for job_data in jobs_list[:max_jobs]:
            try:
                # Extract job details from API response
                title = job_data.get('title', 'Unknown Position')
                company = job_data.get('company', 'Unknown Company')
                location = job_data.get('location', 'Not specified')
                
                # Handle salary
                salary = job_data.get('salary', 'Salary not specified')
                
                # Description
                description = job_data.get('description', '')
                if not description:
                    description = f"{title} position at {company}."
                
                # Clean HTML from description if present
                if '<' in description:
                    from bs4 import BeautifulSoup
                    description = BeautifulSoup(description, 'html.parser').get_text()
                
                # Build job URL
                job_url = job_data.get('url', job_data.get('link', 'https://authenticjobs.com'))
                
                # Date posted
                date_posted = job_data.get('date_posted', datetime.now().strftime('%Y-%m-%d'))
                
                # Calculate relevance score
                relevance_score = calculate_relevance_score(job_data, search_terms)
                
                job_posting = JobPosting(
                    title=title,
                    company=company,
                    location=location,
                    salary=salary,
                    description=description[:500],  # Limit description length
                    url=job_url,
                    date_posted=date_posted,
                    job_site="Authentic Jobs",
                    relevance_score=relevance_score
                )
                
                job_postings.append(job_posting)
                
            except Exception as e:
                console.print(f"[red]⚠️  Error processing job: {e}[/red]")
                continue
        
        # Sort by relevance score (highest first)
        job_postings.sort(key=lambda x: x.relevance_score, reverse=True)
        
        console.print(f"[cyan]📊 Processed {len(job_postings)} jobs, scored by relevance[/cyan]")
        
        return job_postings
        
    except requests.RequestException as e:
        console.print(f"[red]❌ Error fetching Authentic Jobs: {e}[/red]")
        return []
    except Exception as e:
        console.print(f"[red]❌ Unexpected error: {e}[/red]")
        return []

def scrape_authentic_jobs_web(search_terms: List[str] = None, max_jobs: int = 20) -> List[JobPosting]:
    """
    Fallback web scraping for Authentic Jobs when API key is required.
    """
    console = Console()
    
    try:
        from bs4 import BeautifulSoup
        
        # Try main jobs page and search page
        urls_to_try = [
            "https://authenticjobs.com/jobs",
            "https://authenticjobs.com",
            "https://authenticjobs.com/search"
        ]
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
        
        soup = None
        working_url = None
        
        # Try different URLs to find working page
        for url in urls_to_try:
            try:
                console.print(f"[dim]Trying: {url}[/dim]")
                response = requests.get(url, headers=headers, timeout=15)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    working_url = url
                    break
            except:
                continue
        
        if not soup:
            console.print(f"[red]❌ Could not access any Authentic Jobs pages[/red]")
            return []
        
        console.print(f"[green]✅ Successfully loaded: {working_url}[/green]")
        
        # Try multiple selectors for job listings
        job_selectors = [
            'article.job-listing',
            '.job-listing',
            '.job-item', 
            '.job',
            'article',
            '.post',
            '.listing',
            '.opportunity',
            'div[data-job]',
            '.job-card'
        ]
        
        job_listings = []
        for selector in job_selectors:
            job_listings = soup.select(selector)
            if job_listings:
                console.print(f"[green]Found {len(job_listings)} jobs using selector: {selector}[/green]")
                break
        
        # If no structured listings found, look for any links that might be jobs
        if not job_listings:
            # Look for links that contain job-related keywords
            all_links = soup.find_all('a', href=True)
            job_listings = []
            for link in all_links:
                href = link.get('href', '')
                text = link.get_text(strip=True).lower()
                if any(word in href.lower() or word in text for word in ['job', 'position', 'career', 'work', 'developer', 'engineer']):
                    if len(text) > 10:  # Skip very short links
                        job_listings.append(link)
            
            console.print(f"[yellow]Found {len(job_listings)} potential job links[/yellow]")
        
        console.print(f"[green]✅ Found {len(job_listings)} job listings to parse[/green]")
        
        job_postings = []
        
        for job_elem in job_listings[:max_jobs]:
            try:
                # Extract job details
                title_elem = job_elem.find('h2') or job_elem.find('h3') or job_elem.find('.title')
                title = title_elem.get_text(strip=True) if title_elem else 'Unknown Position'
                
                company_elem = job_elem.find('.company') or job_elem.find('.employer')
                company = company_elem.get_text(strip=True) if company_elem else 'Unknown Company'
                
                location_elem = job_elem.find('.location') or job_elem.find('.job-location')
                location = location_elem.get_text(strip=True) if location_elem else 'Not specified'
                
                # Get job URL
                link_elem = job_elem.find('a', href=True) or title_elem.find('a', href=True) if title_elem else None
                job_url = link_elem['href'] if link_elem else 'https://authenticjobs.com'
                
                if job_url.startswith('/'):
                    job_url = 'https://authenticjobs.com' + job_url
                
                # Description (brief)
                desc_elem = job_elem.find('.description') or job_elem.find('.excerpt')
                description = desc_elem.get_text(strip=True) if desc_elem else f"{title} at {company}"
                
                # Mock relevance score for web scraping
                relevance_score = calculate_web_relevance_score(title, description, search_terms)
                
                job_posting = JobPosting(
                    title=title,
                    company=company,
                    location=location,
                    salary="Salary not specified",
                    description=description[:500],
                    url=job_url,
                    date_posted=datetime.now().strftime('%Y-%m-%d'),
                    job_site="Authentic Jobs",
                    relevance_score=relevance_score
                )
                
                job_postings.append(job_posting)
                
            except Exception as e:
                console.print(f"[red]⚠️  Error parsing job listing: {e}[/red]")
                continue
        
        console.print(f"[cyan]📊 Processed {len(job_postings)} jobs from web scraping[/cyan]")
        
        # Sort by relevance
        job_postings.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return job_postings
        
    except Exception as e:
        console.print(f"[red]❌ Web scraping error: {e}[/red]")
        return []

def calculate_relevance_score(job_data: Dict, search_terms: List[str] = None) -> float:
    """Calculate relevance score for a job based on search terms."""
    if not search_terms:
        search_terms = ['unity', 'web', 'react', 'javascript', 'c#', 'typescript', 'frontend', 'backend', 'full stack', 'creative', 'design']
    
    score = 0.0
    
    # Check title and description
    title = job_data.get('title', '').lower()
    description = job_data.get('description', '').lower()
    category = job_data.get('category', '').lower()
    
    # Unity/Game development bonus
    unity_terms = ['unity', 'game', 'c#', 'csharp', 'gamedev', 'unreal', '3d', 'mobile game']
    for term in unity_terms:
        if term in title:
            score += 20
        if term in description:
            score += 10
        if term in category:
            score += 15
    
    # Web development terms
    web_terms = ['react', 'javascript', 'typescript', 'frontend', 'backend', 'full stack', 'web', 'node', 'vue', 'angular']
    for term in web_terms:
        if term in title:
            score += 15
        if term in description:
            score += 8
        if term in category:
            score += 12
    
    # Creative/design terms (Authentic Jobs specialty)
    creative_terms = ['ui', 'ux', 'design', 'creative', 'visual', 'graphic', 'interactive']
    for term in creative_terms:
        if term in title:
            score += 10
        if term in description:
            score += 5
    
    # General programming terms
    general_terms = ['developer', 'engineer', 'software', 'programmer', 'coding']
    for term in general_terms:
        if term in title:
            score += 5
        if term in description:
            score += 3
    
    return min(score, 100.0)  # Cap at 100

def calculate_web_relevance_score(title: str, description: str, search_terms: List[str] = None) -> float:
    """Calculate relevance score for web-scraped data."""
    if not search_terms:
        search_terms = ['unity', 'web', 'react', 'javascript', 'c#', 'frontend', 'backend']
    
    score = 0.0
    title_lower = title.lower()
    description_lower = description.lower()
    
    for term in search_terms:
        if term.lower() in title_lower:
            score += 15
        if term.lower() in description_lower:
            score += 8
    
    return min(score, 100.0)

class AuthenticJobsSearcher:
    """Job searcher for Authentic Jobs using their API/web scraping."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.console = Console()
    
    def search_jobs(self, query: str) -> List[JobPosting]:
        """Search for jobs on Authentic Jobs."""
        search_terms = query.lower().split()
        
        # Get search terms from config
        if 'search_terms' in self.config:
            search_terms.extend([term.lower() for term in self.config['search_terms']])
        
        # Respect their robots.txt crawl delay
        time.sleep(3)
        
        return get_authentic_jobs(search_terms=search_terms, max_jobs=20)

if __name__ == "__main__":
    """Test the Authentic Jobs scraper."""
    console = Console()
    
    console.print("[yellow]🧪 Testing Authentic Jobs API/Scraper...[/yellow]")
    
    # Test with Unity and web development terms
    search_terms = ['unity', 'react', 'javascript', 'c#', 'web developer', 'creative']
    jobs = get_authentic_jobs(search_terms=search_terms, max_jobs=10)
    
    console.print(f"\n[green]Found {len(jobs)} jobs:[/green]")
    
    for job in jobs[:5]:  # Show top 5
        console.print(f"\n[bold blue]🎨 {job.title}[/bold blue]")
        console.print(f"   🏢 {job.company}")
        console.print(f"   📍 {job.location}")
        console.print(f"   💰 {job.salary}")
        console.print(f"   🔗 {job.url}")
        console.print(f"   ⭐ Relevance: {job.relevance_score:.1f}/100")