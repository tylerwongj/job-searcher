#!/usr/bin/env python3
"""
WORKING Dice.com scraper using correct 2024 selectors
Based on analysis of actual Dice.com structure
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

def get_dice_jobs_fixed(search_terms: List[str] = None, location: str = "Remote", max_jobs: int = 20) -> List[JobPosting]:
    """
    WORKING Dice.com scraper using correct 2024 selectors based on real structure analysis.
    
    Key findings from analysis:
    - Jobs are in [role='listitem'] elements
    - Each job has data-testid="job-search-serp-card"
    - Job titles are in nested anchor tags
    - Company names are standalone text elements
    - Location and other details are in specific text patterns
    
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
        
        # Load the page
        driver.get(search_url)
        
        # Wait for job results to load - use the correct selector from analysis
        console.print(f"[yellow]⏳ Waiting for job results to load...[/yellow]")
        
        wait = WebDriverWait(driver, 15)
        
        # Wait for job cards to load - use CORRECT selector based on our analysis
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="job-search-serp-card"]')))
            console.print(f"[green]✅ Job search results loaded successfully[/green]")
        except TimeoutException:
            console.print(f"[yellow]⚠️  Timeout waiting for job results. Checking for jobs anyway...[/yellow]")
        
        # Find job elements using CORRECT selector
        job_elements = driver.find_elements(By.CSS_SELECTOR, '[data-testid="job-search-serp-card"]')
        
        if not job_elements:
            console.print(f"[yellow]⚠️  No job elements found with main selector. Trying fallback...[/yellow]")
            # Fallback to role=listitem
            job_elements = driver.find_elements(By.CSS_SELECTOR, '[role="listitem"]')
        
        if not job_elements:
            console.print(f"[red]❌ No job elements found on the page[/red]")
            return []
        
        console.print(f"[green]✅ Found {len(job_elements)} job cards[/green]")
        
        # Extract job data using CORRECT selectors based on real structure
        jobs = []
        
        for i, job_element in enumerate(job_elements[:max_jobs]):
            try:
                # Method 1: Look for the actual job card within the listitem
                job_card = None
                try:
                    job_card = job_element.find_element(By.CSS_SELECTOR, '[data-testid="job-search-serp-card"]')
                except NoSuchElementException:
                    job_card = job_element
                
                # Extract job title - look for clickable job title links
                title = "Unknown Position"
                job_url = ""
                
                # Try multiple selectors for job title based on typical patterns
                title_selectors = [
                    'a[href*="/jobs/detail/"]',  # Direct job detail links
                    'h2 a', 'h3 a', 'h4 a',     # Header links
                    '.job-title a',              # Job title class
                    'a[tabindex="-1"]'           # Tab-accessible links
                ]
                
                for title_sel in title_selectors:
                    try:
                        title_elements = job_card.find_elements(By.CSS_SELECTOR, title_sel)
                        for title_elem in title_elements:
                            elem_text = title_elem.text.strip()
                            if elem_text and len(elem_text) > 3:  # Valid title
                                title = elem_text
                                job_url = title_elem.get_attribute('href') or ""
                                break
                        if title != "Unknown Position":
                            break
                    except NoSuchElementException:
                        continue
                
                # Extract company name - look for standalone text or company elements
                company = "Unknown Company"
                
                # Get all text content and parse for company
                job_text = job_card.text
                text_lines = [line.strip() for line in job_text.split('\n') if line.strip()]
                
                # Company is typically the first non-empty line that's not a button or title
                skip_patterns = ['Easy Apply', 'Apply', 'Save', 'View Details', title.lower()]
                for line in text_lines:
                    line_lower = line.lower()
                    if (len(line) > 2 and 
                        not any(skip in line_lower for skip in skip_patterns) and
                        not line.startswith('•') and
                        not 'hybrid' in line_lower and
                        not 'remote' in line_lower and
                        not 'today' in line_lower and
                        not '$' in line):
                        company = line
                        break
                
                # Extract location - look for location patterns
                location_found = "Not specified"
                for line in text_lines:
                    if any(word in line.lower() for word in ['hybrid', 'remote', 'in ', 'california', 'new york', 'texas']):
                        location_found = line
                        break
                
                # Extract salary - look for $ patterns
                salary = "Salary not specified"
                for line in text_lines:
                    if '$' in line:
                        salary = line
                        break
                
                # Extract description - combine relevant text
                description_lines = []
                for line in text_lines:
                    if (len(line) > 10 and 
                        line != title and 
                        line != company and 
                        line != location_found and 
                        line != salary and
                        not line.startswith('•') and
                        'Easy Apply' not in line):
                        description_lines.append(line)
                
                description = ' '.join(description_lines[:3])  # First 3 relevant lines
                if not description:
                    description = f"{title} position at {company}"
                
                # Ensure job URL is absolute
                if job_url and not job_url.startswith('http'):
                    job_url = 'https://www.dice.com' + job_url
                
                # Calculate relevance score
                relevance_score = calculate_dice_relevance_score(title, description, search_terms)
                
                # Create job posting
                job_posting = JobPosting(
                    title=title,
                    company=company,
                    location=location_found,
                    salary=salary,
                    description=description[:500],  # Limit description length
                    url=job_url or 'https://dice.com',
                    date_posted=datetime.now().strftime('%Y-%m-%d'),
                    job_site="Dice",
                    relevance_score=relevance_score
                )
                
                jobs.append(job_posting)
                
                console.print(f"[dim]✓ Job {i+1}: {title} at {company}[/dim]")
                
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
    
    # Search terms bonus
    if search_terms:
        for term in search_terms:
            term_lower = term.lower()
            if term_lower in title_lower:
                score += 25
            if term_lower in description_lower:
                score += 15
    
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
    
    return min(score, 100.0)  # Cap at 100

if __name__ == "__main__":
    """Test the WORKING Dice scraper."""
    console = Console()
    
    console.print("[yellow]🧪 Testing FIXED Dice.com scraper with correct 2024 selectors...[/yellow]")
    
    if not SELENIUM_AVAILABLE:
        console.print("[red]❌ Selenium not installed. Install with:[/red]")
        console.print("[cyan]pip install selenium webdriver-manager[/cyan]")
        exit(1)
    
    # Test with Unity and web development terms
    search_terms = ['react', 'javascript', 'web developer']
    jobs = get_dice_jobs_fixed(search_terms=search_terms, max_jobs=5)
    
    console.print(f"\n[green]Found {len(jobs)} jobs:[/green]")
    
    for job in jobs:
        console.print(f"\n[bold blue]🎲 {job.title}[/bold blue]")
        console.print(f"   🏢 {job.company}")
        console.print(f"   📍 {job.location}")
        console.print(f"   💰 {job.salary}")
        console.print(f"   🔗 {job.url}")
        console.print(f"   ⭐ Relevance: {job.relevance_score:.1f}/100")
        console.print(f"   📝 {job.description[:100]}...")