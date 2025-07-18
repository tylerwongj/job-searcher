# Job Sites Scrapers

This folder contains scrapers for different job sites. Each file represents a specific job board and contains the logic to extract real job data.

## 📁 **Current Job Sites**

### `weworkremotely.py`
- **Status:** ✅ Active (Real data)
- **Jobs:** 8 high-quality remote positions  
- **Best for:** Unity developers (C# skills), Web developers (React/Full-stack)
- **Extraction method:** Manual browser navigation + data extraction
- **Update frequency:** Manual (when needed)

## 🚀 **How to Add New Job Sites**

Use `weworkremotely.py` as a template:

### **Step 1: Create new file**
```python
# job_sites/indeed.py
# job_sites/stackoverflow.py  
# job_sites/remoteok.py
```

### **Step 2: Copy template structure**
```python
from job_sites.weworkremotely import JobPosting

def get_SITENAME_jobs() -> List[JobPosting]:
    """Extract jobs from SITENAME using Playwright or requests."""
    
    # Step 1: Navigate to job site
    # Step 2: Get job listing URLs  
    # Step 3: Extract detailed job information
    # Step 4: Create JobPosting objects
    # Step 5: Calculate relevance scores
    # Step 6: Return sorted list
    
    jobs = [
        JobPosting(
            title="Job Title",
            company="Company Name", 
            location="Remote",
            salary="$100,000",
            description="Full job description...",
            url="https://jobsite.com/job/123",
            date_posted="2 days ago",
            job_site="SiteName",
            relevance_score=85.0
        )
    ]
    
    return jobs
```

### **Step 3: Add to main job searcher**
In `job_searcher.py`, add new searcher class:

```python
class NewSiteSearcher(JobSiteSearcher):
    def search(self, query: str, location: str) -> List[JobPosting]:
        from job_sites.newsite import get_newsite_jobs
        all_jobs = get_newsite_jobs()
        # Filter and return relevant jobs
        return filtered_jobs
```

### **Step 4: Enable in config**
In `config.yaml`:
```yaml
job_sites:
  newsite: true  # Enable the new site
```

## 🔧 **Extraction Methods**

### **Method 1: Playwright (Recommended)**
For sites that need browser automation:
```python
async with async_playwright() as p:
    browser = await p.chromium.launch(headless=True)
    page = await browser.new_page()
    await page.goto('https://jobsite.com/jobs')
    # Extract data...
```

### **Method 2: Requests + BeautifulSoup**
For simple HTML scraping:
```python
import requests
from bs4 import BeautifulSoup

response = requests.get('https://jobsite.com/api/jobs')
soup = BeautifulSoup(response.content, 'html.parser')
# Extract data...
```

### **Method 3: API Integration**
For sites with public APIs:
```python
import requests

response = requests.get('https://api.jobsite.com/jobs', 
                       headers={'Authorization': 'Bearer TOKEN'})
jobs_data = response.json()
# Process data...
```

## 🎯 **Best Practices**

1. **Respect robots.txt** - Check site's crawling policies
2. **Add delays** - Don't overwhelm servers (1-2 seconds between requests)
3. **Handle errors** - Graceful fallbacks for network issues
4. **Real data only** - No mock/fake job postings
5. **Accurate scores** - Calculate relevance based on actual job content
6. **Update regularly** - Keep job data fresh (daily/weekly)

## 📊 **Relevance Scoring Guide**

- **90-100:** Perfect matches (exact skill requirements)
- **80-89:** Excellent matches (very relevant)  
- **70-79:** Good matches (some relevance)
- **60-69:** Fair matches (loose relevance)
- **<60:** Poor matches (low relevance)

## 🔍 **Testing Job Sites**

Test each scraper independently:
```bash
cd job_sites
python weworkremotely.py
python indeed.py  
python newsite.py
```

## 🚨 **Troubleshooting**

**Common issues:**
- **403 Forbidden:** Site blocking requests (try different User-Agent)
- **Rate limiting:** Add delays between requests
- **Captcha:** May need manual solving or different approach
- **Structure changes:** Update selectors when site changes

**Solutions:**
- Use rotating User-Agents
- Implement request delays
- Add retry logic with exponential backoff
- Monitor for site structure changes