#!/usr/bin/env python3
"""
Basic test of job searcher functionality
"""

import yaml
import requests
from bs4 import BeautifulSoup
from rich.console import Console

console = Console()

# Test configuration loading
try:
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    console.print("[green]✓ Configuration loaded successfully[/green]")
    console.print(f"Search terms: {config.get('search_terms', [])}")
    console.print(f"Locations: {config.get('locations', [])}")
    console.print(f"Job sites enabled: {config.get('job_sites', {})}")
except Exception as e:
    console.print(f"[red]✗ Config error: {e}[/red]")
    exit(1)

# Test basic web request
try:
    response = requests.get('https://httpbin.org/get', timeout=10)
    console.print(f"[green]✓ Basic web request works (status: {response.status_code})[/green]")
except Exception as e:
    console.print(f"[red]✗ Web request failed: {e}[/red]")

# Test job site access (just check if sites are accessible)
test_urls = {
    'indeed': 'https://www.indeed.com',
    'stackoverflow': 'https://stackoverflow.com'
}

for site, url in test_urls.items():
    try:
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        if response.status_code == 200:
            console.print(f"[green]✓ {site.title()} accessible[/green]")
        else:
            console.print(f"[yellow]⚠ {site.title()} returned status {response.status_code}[/yellow]")
    except Exception as e:
        console.print(f"[red]✗ {site.title()} failed: {e}[/red]")

console.print("\n[blue]Basic functionality test complete![/blue]")