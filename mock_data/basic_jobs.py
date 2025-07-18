#!/usr/bin/env python3
"""
Basic mock job data for general testing
"""

from datetime import datetime, timedelta
from typing import List, Dict
import random

def get_basic_mock_jobs() -> List[Dict]:
    """
    Generate basic mock job data for testing.
    This provides a variety of generic developer positions.
    """
    companies = [
        "TechCorp Global", "InnovateTech", "StartupXYZ", "CodeFactory Inc", 
        "DevSolutions Ltd", "FutureTech", "AppBuilders Co", "DataDriven Systems"
    ]
    
    job_titles = [
        "Software Engineer", "Full Stack Developer", "Backend Developer",
        "Frontend Developer", "Web Developer", "Software Developer",
        "Senior Developer", "Lead Developer", "Principal Engineer"
    ]
    
    locations = ["Remote", "San Francisco, CA", "New York, NY", "Austin, TX", "Seattle, WA"]
    
    jobs = []
    for i in range(6):  # Generate 6 mock jobs
        company = random.choice(companies)
        title = random.choice(job_titles)
        location = random.choice(locations)
        
        # Generate realistic salary ranges
        base_salary = random.randint(70, 140) * 1000
        max_salary = base_salary + random.randint(20, 40) * 1000
        
        job = {
            'title': title,
            'company': company,
            'location': location,
            'salary': f'${base_salary:,} - ${max_salary:,}',
            'description': f'{title} position at {company}. Work with modern technologies and collaborate with a distributed team. We offer competitive compensation, flexible work arrangements, and opportunities for growth.',
            'url': f'https://mockjobs.com/job/{company.lower().replace(" ", "-")}-{i+1}',
            'date_posted': (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d')
        }
        jobs.append(job)
    
    return jobs

def get_mock_job_by_query(query: str) -> List[Dict]:
    """Get mock jobs filtered by query terms."""
    base_jobs = get_basic_mock_jobs()
    
    # Modify some jobs to match the query
    if 'unity' in query.lower():
        base_jobs[0]['title'] = 'Unity Game Developer'
        base_jobs[0]['description'] = 'Unity developer position working on mobile and PC games. C# and Unity experience required.'
    
    if 'web' in query.lower() or 'frontend' in query.lower():
        base_jobs[1]['title'] = 'Senior Web Developer'
        base_jobs[1]['description'] = 'Web developer position using React, TypeScript, and modern web technologies.'
    
    if 'c#' in query.lower():
        base_jobs[2]['title'] = 'C# .NET Developer'
        base_jobs[2]['description'] = 'C# .NET developer for enterprise applications. ASP.NET Core and SQL Server experience preferred.'
    
    return base_jobs

if __name__ == "__main__":
    """Test the mock data."""
    from rich.console import Console
    
    console = Console()
    test_jobs = get_basic_mock_jobs()
    
    console.print("[yellow]Basic Mock Jobs Data:[/yellow]")
    for job in test_jobs:
        console.print(f"  • {job['title']} at {job['company']} - {job['salary']}")