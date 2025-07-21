#!/usr/bin/env python3
"""
Debug script to analyze Hitmarker.net HTML structure
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from rich.console import Console

console = Console()

def debug_hitmarker():
    """Debug what Hitmarker.net actually returns."""
    
    url = "https://hitmarker.net/jobs"
    
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
    }
    
    console.print(f"[blue]Fetching {url}...[/blue]")
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        console.print(f"[green]Status: {response.status_code}[/green]")
        console.print(f"[cyan]Content-Type: {response.headers.get('content-type', 'unknown')}[/cyan]")
        console.print(f"[yellow]Content Length: {len(response.content)} bytes[/yellow]")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Save raw HTML for inspection
        with open('hitmarker_debug.html', 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        console.print(f"[green]✅ Saved raw HTML to hitmarker_debug.html[/green]")
        
        # Look for any JavaScript data
        scripts = soup.find_all('script')
        console.print(f"[cyan]Found {len(scripts)} script tags[/cyan]")
        
        # Look for window.BASE_STATE or similar data
        for i, script in enumerate(scripts):
            if script.string and ('BASE_STATE' in script.string or 'job' in script.string.lower()):
                console.print(f"[yellow]Script {i} contains job-related data[/yellow]")
                script_content = script.string[:500] + "..." if len(script.string) > 500 else script.string
                console.print(f"[dim]{script_content}[/dim]")
                
                # Try to extract job data
                if 'BASE_STATE' in script.string:
                    try:
                        # Extract the BASE_STATE object
                        base_state_match = re.search(r'window\.BASE_STATE\s*=\s*({.*?});', script.string, re.DOTALL)
                        if base_state_match:
                            base_state_str = base_state_match.group(1)
                            # This might be complex JSON, let's save it
                            with open('hitmarker_base_state.json', 'w') as f:
                                f.write(base_state_str)
                            console.print(f"[green]✅ Saved BASE_STATE to hitmarker_base_state.json[/green]")
                    except Exception as e:
                        console.print(f"[red]Error extracting BASE_STATE: {e}[/red]")
        
        # Check for job-related elements
        console.print(f"\n[bold]Looking for job elements...[/bold]")
        
        # Common selectors
        selectors_to_try = [
            '.job-listing', '.job-card', '.job-item', '.job', '.listing',
            'article', '.opportunity', '[data-job]', '.position',
            'a[href*="/jobs/"]'
        ]
        
        for selector in selectors_to_try:
            elements = soup.select(selector)
            if elements:
                console.print(f"[green]✅ Found {len(elements)} elements with selector: {selector}[/green]")
                # Show first element
                if elements:
                    console.print(f"[dim]First element: {str(elements[0])[:200]}...[/dim]")
            else:
                console.print(f"[red]❌ No elements found for: {selector}[/red]")
        
        # Look for any links containing "/jobs/"
        job_links = soup.find_all('a', href=True)
        job_links = [link for link in job_links if '/jobs/' in link.get('href', '')]
        console.print(f"\n[cyan]Found {len(job_links)} links containing '/jobs/'[/cyan]")
        
        for i, link in enumerate(job_links[:5]):  # Show first 5
            console.print(f"[dim]  {i+1}. {link.get('href')} - {link.get_text(strip=True)[:50]}...[/dim]")
        
        # Check if it's a SPA (Single Page Application)
        app_elements = soup.select('#app, [data-app], .app-root, #root, .vue-app, .react-app')
        if app_elements:
            console.print(f"[yellow]⚠️  Detected SPA structure: {[elem.name + '.' + '.'.join(elem.get('class', [])) for elem in app_elements]}[/yellow]")
        
        # Look for any data attributes that might contain job data
        data_elements = soup.find_all(attrs=lambda x: x and any(key.startswith('data-') for key in x.keys()))
        console.print(f"\n[cyan]Found {len(data_elements)} elements with data attributes[/cyan]")
        
        for elem in data_elements[:3]:  # Show first 3
            data_attrs = {k: v for k, v in elem.attrs.items() if k.startswith('data-')}
            console.print(f"[dim]  {elem.name}: {data_attrs}[/dim]")
    
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")

if __name__ == "__main__":
    debug_hitmarker()