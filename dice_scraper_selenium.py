#!/usr/bin/env python3
"""
Modern Dice.com scraper using Selenium for JavaScript rendering
Handles client-side rendered React applications
"""

import time
import json
from typing import List, Dict, Any
from datetime import datetime
from urllib.parse import quote_plus
from rich.console import Console

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.service import Service
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

# JobPosting class
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

def setup_chrome_driver(headless: bool = True) -> webdriver.Chrome:
    """Setup Chrome WebDriver with optimal settings for scraping."""
    if not SELENIUM_AVAILABLE:
        raise ImportError("Selenium not installed. Run: pip install selenium webdriver-manager")
    
    chrome_options = Options()
    
    if headless:
        chrome_options.add_argument("--headless=new"  # Force headless mode)
    
    # Performance and security options
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-images")  # Faster loading
    chrome_options.add_argument("--disable-javascript-console")
    
    # User agent to avoid detection
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    try:
        # Use webdriver-manager to automatically download and manage ChromeDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(30)
        return driver
    except Exception as e:
        raise Exception(f"Failed to setup Chrome driver: {e}")

def get_dice_jobs_selenium(search_terms: List[str] = None, location: str = "Remote", max_jobs: int = 20) -> List[JobPosting]:
    """
    Fetch real job data from Dice.com using Selenium for JavaScript rendering.
    
    Args:
        search_terms: List of terms to search for
        location: Location to search in
        max_jobs: Maximum number of jobs to return
    
    Returns:
        List of JobPosting objects with real data
    """
    console = Console()
    
    if not SELENIUM_AVAILABLE:
        console.print("[red]❌ Selenium not available. Install with: pip install selenium webdriver-manager[/red]")
        return []
    
    driver = None
    try:
        # Build search query
        if search_terms:
            query = " ".join(search_terms)
        else:
            query = "web developer"
        
        # Setup driver
        console.print(f"[blue]🎲 Setting up browser for Dice.com...[/blue]")
        driver = setup_chrome_driver(headless=True)
        
        # Build search URL
        search_url = f"https://www.dice.com/jobs?q={quote_plus(query)}&location={quote_plus(location)}&radius=30&radiusUnit=mi&page=1&pageSize=20&language=en"
        
        console.print(f"[blue]🎲 Loading Dice.com job search...[/blue]")
        console.print(f"[dim]Query: {query}, Location: {location}[/dim]")
        console.print(f"[dim]URL: {search_url}[/dim]")
        
        # Load the page
        driver.get(search_url)
        
        # Wait for page to load and job results to appear
        console.print(f"[yellow]⏳ Waiting for job results to load...[/yellow]")
        
        # Try multiple selectors for job cards
        job_selectors = [
            "[data-testid='job-card']",
            "[data-testid='search-result-card']", 
            ".search-result-card",
            ".job-listing",
            ".job-tile",
            ".search-result",
            ".serp-result",
            "[role='listitem']",
            ".card",
            "article"
        ]
        
        job_elements = []
        wait = WebDriverWait(driver, 15)
        
        # Try each selector until we find job elements
        for selector in job_selectors:
            try:
                console.print(f"[dim]Trying selector: {selector}[/dim]")
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                job_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                
                if job_elements:
                    console.print(f"[green]✅ Found {len(job_elements)} job elements with selector: {selector}[/green]")
                    break
                    
            except TimeoutException:
                continue
        
        if not job_elements:
            console.print(f"[yellow]⚠️  No job elements found. Checking page content...[/yellow]")
            
            # Debug: Save page source for inspection
            page_source = driver.page_source
            with open('/Users/tyler/Desktop/job-searcher/dice_selenium_debug.html', 'w') as f:
                f.write(page_source)
            console.print(f"[dim]Saved page source to dice_selenium_debug.html for inspection[/dim]")
            
            # Check if we're on the right page
            if "Search Jobs" in driver.title:
                console.print(f"[yellow]⚠️  On correct page but no job results loaded. Possible causes:[/yellow]")
                console.print(f"[dim]- No matching jobs for query[/dim]")
                console.print(f"[dim]- Different selectors needed[/dim]")
                console.print(f"[dim]- Bot detection active[/dim]")
            
            return []
        
        # Extract job data
        jobs = []
        console.print(f"[cyan]📊 Extracting job data from {len(job_elements)} elements...[/cyan]")
        
        for i, element in enumerate(job_elements[:max_jobs]):
            try:
                # Extract job title
                title_selectors = [
                    "h2 a", "h3 a", "h4 a",
                    "[data-testid='job-title'] a",
                    ".job-title a",
                    "a[href*='/jobs/detail/']",
                    ".title a"
                ]
                
                title = "Unknown Position"
                job_url = ""
                
                for title_sel in title_selectors:
                    try:
                        title_elem = element.find_element(By.CSS_SELECTOR, title_sel)
                        title = title_elem.text.strip()
                        job_url = title_elem.get_attribute('href') or ""
                        if title:
                            break
                    except NoSuchElementException:
                        continue
                
                # Extract company
                company_selectors = [
                    "[data-testid='company']",
                    ".company",
                    ".employer",
                    ".company-name"
                ]
                
                company = "Unknown Company"
                for comp_sel in company_selectors:
                    try:
                        company_elem = element.find_element(By.CSS_SELECTOR, comp_sel)
                        company = company_elem.text.strip()
                        if company:
                            break
                    except NoSuchElementException:
                        continue
                
                # Extract location
                location_selectors = [
                    "[data-testid='location']",
                    ".location",
                    ".job-location",
                    ".locality"
                ]
                
                job_location = "Not specified"
                for loc_sel in location_selectors:
                    try:
                        location_elem = element.find_element(By.CSS_SELECTOR, loc_sel)
                        job_location = location_elem.text.strip()
                        if job_location:
                            break
                    except NoSuchElementException:
                        continue
                
                # Extract salary
                salary_selectors = [
                    "[data-testid='salary']",
                    ".salary",
                    ".compensation",
                    ".pay"
                ]
                
                salary = "Salary not specified"
                for sal_sel in salary_selectors:
                    try:
                        salary_elem = element.find_element(By.CSS_SELECTOR, sal_sel)
                        salary = salary_elem.text.strip()
                        if salary:
                            break
                    except NoSuchElementException:
                        continue
                
                # Extract description/summary
                desc_selectors = [
                    ".description",
                    ".job-summary",
                    ".snippet",
                    ".summary",
                    "[data-testid='job-summary']"
                ]
                
                description = f"{title} at {company}"
                for desc_sel in desc_selectors:
                    try:
                        desc_elem = element.find_element(By.CSS_SELECTOR, desc_sel)
                        description = desc_elem.text.strip()
                        if description:
                            break
                    except NoSuchElementException:
                        continue
                
                # Ensure job URL is absolute
                if job_url and not job_url.startswith('http'):
                    job_url = 'https://www.dice.com' + job_url
                
                # Calculate relevance score
                relevance_score = calculate_dice_relevance_score(title, description, search_terms)
                
                # Create job posting
                job_posting = JobPosting(
                    title=title,
                    company=company,
                    location=job_location,
                    salary=salary,
                    description=description[:500],  # Limit description length
                    url=job_url or 'https://dice.com',
                    date_posted=datetime.now().strftime('%Y-%m-%d'),
                    job_site="Dice",
                    relevance_score=relevance_score
                )
                
                jobs.append(job_posting)
                
                console.print(f"[dim]Job {i+1}: {title} at {company}[/dim]")
                
            except Exception as e:
                console.print(f"[red]❌ Error extracting job {i+1}: {e}[/red]")
                continue
        
        # Sort by relevance score
        jobs.sort(key=lambda x: x.relevance_score, reverse=True)
        
        console.print(f"[green]✅ Successfully extracted {len(jobs)} jobs from Dice.com[/green]")
        
        return jobs
        
    except Exception as e:
        console.print(f"[red]❌ Error scraping Dice.com: {e}[/red]")
        return []
        
    finally:
        if driver:
            driver.quit()

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

if __name__ == "__main__":
    """Test the modern Dice scraper."""
    console = Console()
    
    console.print("[yellow]🧪 Testing modern Dice.com scraper with Selenium...[/yellow]")
    
    if not SELENIUM_AVAILABLE:
        console.print("[red]❌ Selenium not installed. Install with:[/red]")
        console.print("[cyan]pip install selenium webdriver-manager[/cyan]")
        exit(1)
    
    # Test with Unity and web development terms
    search_terms = ['unity', 'react', 'javascript', 'c#', 'web developer']
    jobs = get_dice_jobs_selenium(search_terms=search_terms, max_jobs=5)
    
    console.print(f"\n[green]Found {len(jobs)} jobs:[/green]")
    
    for job in jobs:
        console.print(f"\n[bold blue]🎲 {job.title}[/bold blue]")
        console.print(f"   🏢 {job.company}")
        console.print(f"   📍 {job.location}")
        console.print(f"   💰 {job.salary}")
        console.print(f"   🔗 {job.url}")
        console.print(f"   ⭐ Relevance: {job.relevance_score:.1f}/100")
        console.print(f"   📝 {job.description[:100]}...")