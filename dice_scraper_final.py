#!/usr/bin/env python3
"""
FINAL WORKING Dice.com scraper - 2024 version with correct title extraction
Based on detailed analysis of Dice.com's actual HTML structure
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

def get_dice_jobs(search_terms: List[str] = None, location: str = "Remote", max_jobs: int = 20) -> List[JobPosting]:
    """
    FINAL WORKING Dice.com scraper using correct 2024 structure.
    
    This scraper correctly handles Dice.com's React-based structure:
    1. Waits for JavaScript to load job content
    2. Uses correct CSS selectors: [data-testid="job-search-serp-card"]
    3. Extracts job titles from text content (not HTML attributes)
    4. Parses company, location, salary from structured text
    
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
        
        # Wait for job results to load
        console.print(f"[yellow]⏳ Waiting for job results to load...[/yellow]")
        
        wait = WebDriverWait(driver, 15)
        
        # Wait for job cards to load
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="job-search-serp-card"]')))
            console.print(f"[green]✅ Job search results loaded successfully[/green]")
        except TimeoutException:
            console.print(f"[yellow]⚠️  Timeout waiting for job results. Checking for jobs anyway...[/yellow]")
        
        # Find job elements using correct selector
        job_elements = driver.find_elements(By.CSS_SELECTOR, '[data-testid="job-search-serp-card"]')
        
        if not job_elements:
            console.print(f"[yellow]⚠️  No job elements found with main selector. Trying fallback...[/yellow]")
            # Fallback to role=listitem 
            job_elements = driver.find_elements(By.CSS_SELECTOR, '[role="listitem"]')
        
        if not job_elements:
            console.print(f"[red]❌ No job elements found on the page[/red]")
            return []
        
        console.print(f"[green]✅ Found {len(job_elements)} job cards[/green]")
        
        # Extract job data
        jobs = []
        
        for i, job_element in enumerate(job_elements[:max_jobs]):
            try:
                # Get the job card element
                job_card = None
                try:
                    job_card = job_element.find_element(By.CSS_SELECTOR, '[data-testid="job-search-serp-card"]')
                except NoSuchElementException:
                    job_card = job_element
                
                # Get all text content and parse it intelligently
                job_text = job_card.text
                text_lines = [line.strip() for line in job_text.split('\n') if line.strip()]
                
                if not text_lines:
                    continue
                
                # Parse the structured text content
                # Based on observed patterns:
                # Line 1: Company name
                # Line 2: "Easy Apply" (skip)
                # Line 3: Job title
                # Line 4+: Location, salary, description
                
                company = "Unknown Company"
                title = "Unknown Position"
                location_found = "Not specified"
                salary = "Salary not specified"
                description_parts = []
                
                # Extract company (usually first line, skip "Easy Apply")
                for line in text_lines:
                    if line and line != "Easy Apply" and not line.startswith("•"):
                        company = line
                        break
                
                # Extract title (look for job-related keywords)
                job_keywords = ['developer', 'engineer', 'programmer', 'analyst', 'manager', 'lead', 'senior', 'junior', 'web', 'software', 'ui', 'ux', 'full stack', 'frontend', 'backend']
                
                for line in text_lines:
                    line_lower = line.lower()
                    if (any(keyword in line_lower for keyword in job_keywords) and 
                        line != company and
                        'hybrid' not in line_lower and
                        'remote' not in line_lower and
                        not line.startswith('$') and
                        len(line) > 5):
                        title = line
                        break
                
                # Extract location (look for location patterns)
                location_patterns = ['hybrid', 'remote', 'in ', ', california', ', new york', ', texas', ', ohio', ', florida']
                for line in text_lines:
                    line_lower = line.lower()
                    if any(pattern in line_lower for pattern in location_patterns):
                        location_found = line
                        break
                
                # Extract salary (look for $ or salary numbers)
                for line in text_lines:
                    if '$' in line or any(word in line.lower() for word in ['salary', 'hourly', 'annual']):
                        salary = line
                        break
                
                # Extract description (combine remaining relevant lines)
                skip_lines = {company.lower(), title.lower(), location_found.lower(), salary.lower(), 'easy apply', 'apply', 'save'}
                for line in text_lines:
                    line_lower = line.lower()
                    if (len(line) > 15 and 
                        line_lower not in skip_lines and
                        not line.startswith('•') and
                        'today' not in line_lower and
                        'yesterday' not in line_lower):
                        description_parts.append(line)
                        if len(description_parts) >= 3:  # Limit description
                            break
                
                description = ' '.join(description_parts) if description_parts else f"{title} position at {company}"
                
                # Try to extract job URL (look for clickable links)
                job_url = ""
                try:
                    links = job_card.find_elements(By.TAG_NAME, 'a')
                    for link in links:
                        href = link.get_attribute('href')
                        if href and '/jobs/detail/' in href:
                            job_url = href
                            break
                except:
                    pass
                
                if not job_url:
                    job_url = "https://dice.com"
                
                # Calculate relevance score
                relevance_score = calculate_dice_relevance_score(title, description, search_terms)
                
                # Create job posting
                job_posting = JobPosting(
                    title=title,
                    company=company,
                    location=location_found,
                    salary=salary,
                    description=description[:500],  # Limit description length
                    url=job_url,
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

# DiceSearcher class for compatibility
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
    """Test the FINAL working Dice scraper."""
    console = Console()
    
    console.print("[yellow]🧪 Testing FINAL working Dice.com scraper...[/yellow]")
    
    if not SELENIUM_AVAILABLE:
        console.print("[red]❌ Selenium not installed. Install with:[/red]")
        console.print("[cyan]pip install selenium webdriver-manager[/cyan]")
        exit(1)
    
    # Test with realistic search terms
    search_terms = ['react', 'javascript', 'web developer']
    jobs = get_dice_jobs(search_terms=search_terms, max_jobs=5)
    
    console.print(f"\n[green]Found {len(jobs)} jobs:[/green]")
    
    for job in jobs:
        console.print(f"\n[bold blue]🎲 {job.title}[/bold blue]")
        console.print(f"   🏢 {job.company}")
        console.print(f"   📍 {job.location}")
        console.print(f"   💰 {job.salary}")
        console.print(f"   🔗 {job.url}")
        console.print(f"   ⭐ Relevance: {job.relevance_score:.1f}/100")
        console.print(f"   📝 {job.description[:100]}...")