#!/usr/bin/env python3
"""
Debug script for Dice.com scraper - Enhanced debugging
"""

import requests
import json
import re
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

def debug_dice_request():
    """Debug the Dice.com request and response."""
    query = "web developer"
    location = "Remote"
    
    # Dice.com search URL
    search_url = f"https://www.dice.com/jobs?q={quote_plus(query)}&location={quote_plus(location)}&radius=30&radiusUnit=mi&page=1&pageSize=20&language=en"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0'
    }
    
    print(f"🔍 Testing URL: {search_url}")
    print(f"🔍 Headers: {headers}")
    
    try:
        response = requests.get(search_url, headers=headers, timeout=15)
        
        print(f"\n📊 Response Status: {response.status_code}")
        print(f"📊 Response Headers: {dict(response.headers)}")
        print(f"📊 Content Length: {len(response.text)}")
        
        # Save the raw HTML for inspection
        with open('/Users/tyler/Desktop/job-searcher/dice_debug.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("💾 Saved raw HTML to dice_debug.html")
        
        # Check for various indicators
        content = response.text
        
        print(f"\n🔍 Looking for job-related content...")
        
        # Check for common job-related terms
        job_indicators = [
            "job", "position", "career", "hiring", "employment",
            "salary", "company", "location", "apply"
        ]
        
        for indicator in job_indicators:
            count = content.lower().count(indicator)
            print(f"   - '{indicator}': {count} occurrences")
        
        # Check for React/Next.js indicators
        print(f"\n🔍 Looking for React/Next.js indicators...")
        react_indicators = [
            "__NEXT_DATA__", "__INITIAL_STATE__", "window.__NEXT_DATA__",
            "react", "next", "props", "pageProps"
        ]
        
        for indicator in react_indicators:
            if indicator in content:
                print(f"   ✅ Found: {indicator}")
            else:
                print(f"   ❌ Not found: {indicator}")
        
        # Try to find JSON patterns
        print(f"\n🔍 Looking for JSON data patterns...")
        json_patterns = [
            r'window\.__NEXT_DATA__\s*=\s*({.+?});',
            r'window\.__INITIAL_STATE__\s*=\s*({.+?});',
            r'"jobs":\s*(\[.+?\])',
            r'"searchResults":\s*({.+?})',
        ]
        
        for i, pattern in enumerate(json_patterns):
            matches = re.search(pattern, content, re.DOTALL)
            if matches:
                print(f"   ✅ Pattern {i+1} matched: {len(matches.group(1))} characters")
                # Save first 500 chars of JSON for inspection
                json_sample = matches.group(1)[:500]
                print(f"   📝 Sample: {json_sample}...")
            else:
                print(f"   ❌ Pattern {i+1} not found")
        
        # Try HTML parsing
        print(f"\n🔍 Trying HTML parsing...")
        soup = BeautifulSoup(content, 'html.parser')
        
        job_selectors = [
            '.search-result',
            '.job-tile',
            '.job-card',
            '[data-testid="job-card"]',
            '.serp-result-content',
            '.diceui-card',
            '.card',
            'article',
            '[data-testid="search-result-card"]'
        ]
        
        for selector in job_selectors:
            elements = soup.select(selector)
            print(f"   - '{selector}': {len(elements)} elements found")
            if elements:
                # Show first element's text (truncated)
                first_text = elements[0].get_text(strip=True)[:200]
                print(f"     📝 First element text: {first_text}...")
        
        # Check for anti-bot measures
        print(f"\n🔍 Checking for anti-bot measures...")
        bot_indicators = [
            "captcha", "bot", "blocked", "forbidden", "access denied",
            "cloudflare", "security", "verification"
        ]
        
        for indicator in bot_indicators:
            if indicator in content.lower():
                print(f"   ⚠️  Found potential bot blocker: {indicator}")
        
        # Check title and meta tags
        print(f"\n🔍 Page metadata...")
        title = soup.find('title')
        if title:
            print(f"   📄 Title: {title.get_text(strip=True)}")
        
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            print(f"   📄 Description: {meta_desc.get('content', '')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    debug_dice_request()