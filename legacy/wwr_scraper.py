#!/usr/bin/env python3
"""
WeWorkRemotely Job Scraper using Playwright
Extracts real job data from WeWorkRemotely programming jobs section
"""

import asyncio
import json
import sys
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from playwright.async_api import async_playwright, Browser, Page
import yaml
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

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
    skills: List[str] = None
    application_email: str = ""
    deadline: str = ""
    
    def __post_init__(self):
        if self.skills is None:
            self.skills = []
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return asdict(self)

class WeWorkRemotelyPlaywrightScraper:
    """Scraper for WeWorkRemotely using Playwright for real job data."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.search_terms = config.get('search_terms', [])
        self.preferred_keywords = config.get('filters', {}).get('preferred_keywords', [])
        self.jobs = []
        
    def calculate_relevance_score(self, job_data: Dict) -> float:
        """Calculate relevance score based on title, description, and skills."""
        score = 0.0
        title_lower = job_data['title'].lower()
        description_lower = job_data['description'].lower()
        skills_text = ' '.join(job_data.get('skills', [])).lower()
        
        # Check search terms in title (high weight)
        for term in self.search_terms:
            if term.lower() in title_lower:
                score += 30.0
            elif term.lower() in description_lower:
                score += 15.0
                
        # Check preferred keywords
        for keyword in self.preferred_keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in title_lower:
                score += 20.0
            elif keyword_lower in description_lower:
                score += 10.0
            elif keyword_lower in skills_text:
                score += 15.0
                
        # Bonus for specific Unity/Game Dev terms
        unity_terms = ['unity', 'c#', 'game', 'unreal', 'gamedev']
        for term in unity_terms:
            if term in title_lower:
                score += 25.0
            elif term in description_lower:
                score += 12.0
                
        # Bonus for web development terms
        web_terms = ['react', 'javascript', 'typescript', 'node.js', 'frontend', 'fullstack', 'full-stack']
        for term in web_terms:
            if term in title_lower:
                score += 20.0
            elif term in description_lower:
                score += 10.0
                
        return min(score, 100.0)  # Cap at 100
        
    async def extract_job_details(self, page: Page, job_url: str) -> Optional[Dict]:
        """Extract detailed job information from a job posting page."""
        try:
            await page.goto(job_url, wait_until='domcontentloaded')
            await page.wait_for_timeout(2000)  # Wait for content to load
            
            # Extract job details
            title_elem = page.locator('h2').first
            title = await title_elem.text_content() if await title_elem.count() > 0 else "Unknown Title"
            
            # Extract company name from breadcrumb or company section
            company_elem = page.locator('[data-testid="company-name"], .company-name').first
            if await company_elem.count() == 0:
                # Fallback: look for company in the job details section
                company_elem = page.locator('text=/posted by|company/i').first
            company = await company_elem.text_content() if await company_elem.count() > 0 else "Unknown Company"
            
            # Extract description - get the main job content
            description_elem = page.locator('.listing-container, .job-description, .listing').first
            description = await description_elem.text_content() if await description_elem.count() > 0 else ""
            
            # Clean up description
            description = description.strip()[:2000] if description else "No description available"
            
            # Extract posting date
            date_elem = page.locator('text=/\\d+d|\\d+ days? ago|posted \\d+ days?/i').first
            date_posted = await date_elem.text_content() if await date_elem.count() > 0 else "Unknown"
            
            # Extract salary if mentioned
            salary_elem = page.locator('text=/\\$[\\d,]+|salary|compensation/i').first
            salary = await salary_elem.text_content() if await salary_elem.count() > 0 else "Not specified"
            
            # Extract skills from skills section
            skills = []
            skill_links = page.locator('a[href*="/remote-jobs-"]')
            skill_count = await skill_links.count()
            for i in range(min(skill_count, 10)):  # Limit to 10 skills
                skill_text = await skill_links.nth(i).text_content()
                if skill_text and skill_text.strip():
                    skills.append(skill_text.strip())
            
            # Extract application email if available
            email_elem = page.locator('a[href^="mailto:"]').first
            application_email = ""
            if await email_elem.count() > 0:
                href = await email_elem.get_attribute('href')
                if href and 'mailto:' in href:
                    application_email = href.replace('mailto:', '').split('?')[0]
            
            # Extract location information
            location_elem = page.locator('text=/location|remote|anywhere/i').first
            location = await location_elem.text_content() if await location_elem.count() > 0 else "Remote"
            
            return {
                'title': title,
                'company': company,
                'location': location,
                'salary': salary,
                'description': description,
                'url': job_url,
                'date_posted': date_posted,
                'job_site': 'WeWorkRemotely',
                'skills': skills,
                'application_email': application_email,
                'deadline': ""
            }
            
        except Exception as e:
            console.print(f"[red]Error extracting job details from {job_url}: {e}[/red]")
            return None
    
    async def scrape_job_listings(self, max_jobs: int = 10) -> List[JobPosting]:
        """Scrape job listings from WeWorkRemotely programming section."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                # Navigate to WeWorkRemotely programming jobs
                console.print("[blue]Navigating to WeWorkRemotely programming jobs...[/blue]")
                await page.goto('https://weworkremotely.com/categories/remote-full-stack-programming-jobs', 
                               wait_until='domcontentloaded')
                await page.wait_for_timeout(3000)
                
                # Find job listing links - WeWorkRemotely uses specific structure
                # Wait for content to load
                await page.wait_for_selector('li', timeout=10000)
                
                # Get job listing containers - each job is in a listitem
                job_links = page.locator('li a[href*="/listings/"]')
                job_count = await job_links.count()
                
                # If that doesn't work, try alternative selector
                if job_count == 0:
                    job_links = page.locator('article a[href*="/listings/"], .job a[href*="/listings/"]')
                    job_count = await job_links.count()
                
                # Debug: print page content if no jobs found
                if job_count == 0:
                    page_content = await page.content()
                    console.print(f"[yellow]Debug: Page title: {await page.title()}[/yellow]")
                    if '/listings/' in page_content:
                        console.print("[yellow]Debug: Found /listings/ in page content but no matching links[/yellow]")
                    else:
                        console.print("[yellow]Debug: No /listings/ found in page content[/yellow]")
                
                console.print(f"[green]Found {job_count} job listings[/green]")
                
                # Extract URLs for detailed scraping
                job_urls = []
                for i in range(min(job_count, max_jobs)):
                    href = await job_links.nth(i).get_attribute('href')
                    if href and '/listings/' in href:
                        full_url = f"https://weworkremotely.com{href}"
                        job_urls.append(full_url)
                
                console.print(f"[blue]Extracting details from {len(job_urls)} jobs...[/blue]")
                
                # Extract detailed information for each job
                jobs = []
                with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
                    task = progress.add_task("Scraping jobs...", total=len(job_urls))
                    
                    for job_url in job_urls:
                        progress.update(task, description=f"Processing job {len(jobs)+1}/{len(job_urls)}")
                        
                        job_data = await self.extract_job_details(page, job_url)
                        if job_data:
                            # Calculate relevance score
                            relevance_score = self.calculate_relevance_score(job_data)
                            job_data['relevance_score'] = relevance_score
                            
                            # Create JobPosting object
                            job = JobPosting(**job_data)
                            jobs.append(job)
                            
                            console.print(f"[green]✓[/green] {job.title} at {job.company} (Score: {relevance_score:.1f})")
                        
                        progress.advance(task)
                        await page.wait_for_timeout(1000)  # Be respectful with requests
                
                return jobs
                
            except Exception as e:
                console.print(f"[red]Error during scraping: {e}[/red]")
                return []
            finally:
                await browser.close()

async def main():
    """Main function to run the scraper."""
    # Load configuration
    try:
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        console.print("[red]config.yaml not found. Using default config.[/red]")
        config = {
            'search_terms': ['unity developer', 'game developer', 'c# developer', 'web developer', 'frontend developer'],
            'filters': {
                'preferred_keywords': ['unity', 'c#', 'game development', 'javascript', 'react', 'typescript']
            }
        }
    
    # Create scraper and get jobs
    scraper = WeWorkRemotelyPlaywrightScraper(config)
    jobs = await scraper.scrape_job_listings(max_jobs=15)
    
    if jobs:
        console.print(f"\n[green]Successfully scraped {len(jobs)} jobs![/green]")
        
        # Sort by relevance score
        jobs.sort(key=lambda x: x.relevance_score, reverse=True)
        
        # Display top jobs
        console.print("\n[bold blue]Top Job Matches:[/bold blue]")
        for job in jobs[:5]:
            console.print(f"[green]• {job.title}[/green] at [cyan]{job.company}[/cyan]")
            console.print(f"  Score: {job.relevance_score:.1f} | Posted: {job.date_posted}")
            console.print(f"  Skills: {', '.join(job.skills[:5])}")
            console.print(f"  URL: {job.url}")
            console.print()
        
        # Save to JSON file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"wwr_jobs_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump([job.to_dict() for job in jobs], f, indent=2, ensure_ascii=False)
        
        console.print(f"[green]Jobs saved to {filename}[/green]")
        
    else:
        console.print("[red]No jobs found or scraping failed.[/red]")

if __name__ == "__main__":
    # Install playwright if needed
    try:
        asyncio.run(main())
    except ImportError:
        console.print("[red]Playwright not installed. Install with: pip install playwright[/red]")
        console.print("[red]Then run: playwright install[/red]")
        sys.exit(1)