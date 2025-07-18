#!/usr/bin/env python3
"""
Mock FlexJobs data for testing flexible work opportunities
"""

from datetime import datetime
from typing import List, Dict

def get_flexible_jobs_data(query: str) -> List[Dict]:
    """
    Generate mock flexible/remote job data based on query.
    This simulates what FlexJobs might return.
    """
    return [
        {
            'title': f'Remote {query} - Flexible Hours',
            'company': 'FlexTech Solutions',
            'location': 'Remote',
            'salary': '$75,000 - $110,000',
            'description': f'Flexible remote {query} position with work-life balance focus. Choose your hours, work from anywhere. We value results over hours worked.',
            'url': 'https://flexjobs.com/job/remote-dev-flex-1'
        },
        {
            'title': f'Part-time {query}',
            'company': 'Balance Corp',
            'location': 'Remote',
            'salary': '$45/hour',
            'description': f'Part-time {query} role perfect for work-life balance. 20-30 hours per week, flexible schedule. Great for side projects or family time.',
            'url': 'https://flexjobs.com/job/parttime-dev-2'
        },
        {
            'title': f'Contract {query} - 6 months',
            'company': 'ProjectPro Inc',
            'location': 'Remote',
            'salary': '$80/hour',
            'description': f'Contract {query} position for exciting 6-month project. Potential for extension. Work with cutting-edge technology stack.',
            'url': 'https://flexjobs.com/job/contract-dev-3'
        }
    ]

if __name__ == "__main__":
    """Test the mock data."""
    from rich.console import Console
    
    console = Console()
    test_jobs = get_flexible_jobs_data("unity developer")
    
    console.print("[yellow]Mock FlexJobs Data:[/yellow]")
    for job in test_jobs:
        console.print(f"  • {job['title']} at {job['company']}")