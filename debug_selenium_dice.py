#!/usr/bin/env python3
"""
Debug script to analyze Dice.com structure with Selenium
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

def debug_dice_selenium():
    """Debug Dice.com structure using Selenium."""
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Setup driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # Load Dice.com job search
        url = "https://www.dice.com/jobs?q=web+developer&location=Remote&radius=30&radiusUnit=mi&page=1&pageSize=20&language=en"
        print(f"Loading: {url}")
        
        driver.get(url)
        
        # Wait for page to load
        time.sleep(5)
        
        print(f"Page title: {driver.title}")
        print(f"Current URL: {driver.current_url}")
        
        # Save full page source
        page_source = driver.page_source
        with open('/Users/tyler/Desktop/job-searcher/dice_selenium_full_debug.html', 'w', encoding='utf-8') as f:
            f.write(page_source)
        print("Saved full page source to dice_selenium_full_debug.html")
        
        # Try to find job elements with various selectors
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
            "article",
            "div[id*='job']",
            "div[class*='job']",
            "a[href*='/jobs/detail/']"
        ]
        
        print("\n🔍 Testing job element selectors:")
        for selector in job_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"  {selector}: {len(elements)} elements")
                
                if elements and len(elements) > 0:
                    # Show first element's HTML
                    first_elem_html = elements[0].get_attribute('outerHTML')[:500]
                    print(f"    First element HTML: {first_elem_html}...")
                    
                    # Try to find text content
                    first_elem_text = elements[0].text[:200]
                    print(f"    First element text: {first_elem_text}...")
                    
            except Exception as e:
                print(f"  {selector}: Error - {e}")
        
        # Look for common job-related text patterns
        print("\n🔍 Looking for job-related text patterns:")
        job_patterns = [
            "developer", "engineer", "software", "programmer",
            "javascript", "python", "react", "java",
            "remote", "salary", "full time", "part time"
        ]
        
        page_text = driver.page_source.lower()
        for pattern in job_patterns:
            count = page_text.count(pattern)
            print(f"  '{pattern}': {count} occurrences")
        
        # Check for specific Dice.com elements
        print("\n🔍 Looking for Dice.com specific elements:")
        dice_selectors = [
            "[data-testid]",
            ".diceui-card",
            "[class*='dice']",
            "[id*='dice']"
        ]
        
        for selector in dice_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"  {selector}: {len(elements)} elements")
                if elements:
                    print(f"    Sample data-testid values: {[elem.get_attribute('data-testid') for elem in elements[:5]]}")
            except Exception as e:
                print(f"  {selector}: Error - {e}")
        
        # Look for links to job details
        print("\n🔍 Looking for job detail links:")
        job_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/jobs/detail/']")
        print(f"Found {len(job_links)} job detail links")
        
        for i, link in enumerate(job_links[:3]):
            print(f"  Link {i+1}: {link.get_attribute('href')}")
            print(f"    Text: {link.text}")
            print(f"    Parent HTML: {link.find_element(By.XPATH, '..').get_attribute('outerHTML')[:200]}...")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_dice_selenium()