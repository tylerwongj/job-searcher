#!/usr/bin/env python3
"""
RemoteOK job scraper using their official API
Official API: https://remoteok.com/api
"""

import requests
import time
from typing import List, Dict, Any
from rich.console import Console

# Simple JobPosting class for RemoteOK data
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

def get_remoteok_jobs(search_terms: List[str] = None, max_jobs: int = 20) -> List[JobPosting]:
    """
    Fetch real job data from RemoteOK using their official API.
    
    Args:
        search_terms: List of terms to search for (Unity, React, etc.)
        max_jobs: Maximum number of jobs to return
    
    Returns:
        List of JobPosting objects with real data
    """
    console = Console()
    
    try:
        # RemoteOK official API endpoint
        api_url = "https://remoteok.com/api"
        
        # Set headers to be respectful
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        
        console.print(f"[blue]🌐 Fetching jobs from RemoteOK API...[/blue]")
        
        # Make API request
        response = requests.get(api_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse JSON response
        jobs_data = response.json()
        
        # Filter out the first item (it's usually metadata)
        if jobs_data and isinstance(jobs_data[0], dict) and 'legal' in jobs_data[0]:
            jobs_data = jobs_data[1:]
        
        console.print(f"[green]✅ Retrieved {len(jobs_data)} jobs from RemoteOK[/green]")
        
        # Convert to JobPosting objects
        job_postings = []
        
        for job_data in jobs_data[:max_jobs]:
            try:
                # Extract job details
                title = job_data.get('position', 'Unknown Position')
                company = job_data.get('company', 'Unknown Company')
                location = job_data.get('location', 'Remote')
                
                # Handle salary - RemoteOK provides min/max
                salary_min = job_data.get('salary_min', 0)
                salary_max = job_data.get('salary_max', 0)
                
                if salary_min and salary_max:
                    salary = f"${salary_min:,} - ${salary_max:,}"
                elif salary_min:
                    salary = f"${salary_min:,}+"
                else:
                    salary = "Salary not specified"
                
                # Description from job data
                description = job_data.get('description', '')
                if not description:
                    description = f"{title} position at {company}. "
                    tags = job_data.get('tags', [])
                    if tags:
                        description += f"Skills: {', '.join(tags[:5])}"
                
                # Build job URL
                job_id = job_data.get('id', 'unknown')
                url = f"https://remoteok.com/remote-jobs/{job_id}"
                
                # Date posted
                date_posted = job_data.get('date', 'Unknown')
                
                # Calculate relevance score
                relevance_score = calculate_relevance_score(job_data, search_terms)
                
                job_posting = JobPosting(
                    title=title,
                    company=company,
                    location=location,
                    salary=salary,
                    description=description,
                    url=url,
                    date_posted=date_posted,
                    job_site="RemoteOK",
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
        console.print(f"[red]❌ Error fetching RemoteOK jobs: {e}[/red]")
        return []
    except Exception as e:
        console.print(f"[red]❌ Unexpected error: {e}[/red]")
        return []

def calculate_relevance_score(job_data: Dict, search_terms: List[str] = None) -> float:
    """Calculate relevance score for a job based on search terms."""
    if not search_terms:
        search_terms = ['unity', 'web', 'react', 'javascript', 'c#', 'typescript', 'frontend', 'backend', 'full stack']
    
    score = 0.0
    
    # Check title
    title = job_data.get('position', '').lower()
    description = job_data.get('description', '').lower()
    tags = [tag.lower() for tag in job_data.get('tags', [])]
    
    # Unity/Game development bonus
    unity_terms = ['unity', 'game', 'c#', 'csharp', 'gamedev', 'unreal']
    for term in unity_terms:
        if term in title:
            score += 20
        if term in description:
            score += 10
        if term in tags:
            score += 15
    
    # Web development terms
    web_terms = ['react', 'javascript', 'typescript', 'frontend', 'backend', 'full stack', 'web', 'node', 'vue', 'angular']
    for term in web_terms:
        if term in title:
            score += 15
        if term in description:
            score += 8
        if term in tags:
            score += 12
    
    # General programming terms
    general_terms = ['developer', 'engineer', 'software', 'programmer', 'coding']
    for term in general_terms:
        if term in title:
            score += 5
        if term in description:
            score += 3
    
    # Remote work bonus
    if job_data.get('location', '').lower() == 'remote':
        score += 10
    
    # Salary bonus
    if job_data.get('salary_min', 0) > 0:
        score += 5
    
    return min(score, 100.0)  # Cap at 100

class RemoteOKSearcher:
    """Job searcher for RemoteOK using their official API."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.console = Console()
    
    def search_jobs(self, query: str) -> List[JobPosting]:
        """Search for jobs on RemoteOK."""
        search_terms = query.lower().split()
        
        # Get search terms from config
        if 'search_terms' in self.config:
            search_terms.extend([term.lower() for term in self.config['search_terms']])
        
        return get_remoteok_jobs(search_terms=search_terms, max_jobs=30)

if __name__ == "__main__":
    """Test the RemoteOK scraper."""
    console = Console()
    
    console.print("[yellow]🧪 Testing RemoteOK API...[/yellow]")
    
    # Test with Unity and web development terms
    search_terms = ['unity', 'react', 'javascript', 'c#', 'web developer']
    jobs = get_remoteok_jobs(search_terms=search_terms, max_jobs=10)
    
    console.print(f"\n[green]Found {len(jobs)} jobs:[/green]")
    
    for job in jobs[:5]:  # Show top 5
        console.print(f"\n[bold blue]📋 {job.title}[/bold blue]")
        console.print(f"   🏢 {job.company}")
        console.print(f"   📍 {job.location}")
        console.print(f"   💰 {job.salary}")
        console.print(f"   🔗 {job.url}")
        console.print(f"   ⭐ Relevance: {job.relevance_score:.1f}/100")