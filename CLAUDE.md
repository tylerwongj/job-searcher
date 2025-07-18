# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Primary Commands
```bash
# Main execution - run the job searcher
python search_jobs.py

# Install Python dependencies  
pip install -r requirements.txt

# Install JavaScript dependencies (for legacy scraper)
npm install

# Run legacy JavaScript scraper (creates jobs.json)
node legacy/scraper.js
npm run scrape
```

### Testing & Development
```bash
# Test individual job site scrapers
python job_sites/weworkremotely.py

# Command line options
python search_jobs.py --config custom_config.yaml
python search_jobs.py --no-save     # Don't save results to files
python search_jobs.py --quiet       # Minimal output
```

## Architecture Overview

### Core Data Flow
**Configuration → Scrapers → Processing → Output**

1. **Configuration Loading**: `config.yaml` defines search terms, enabled job sites, filters, and output preferences
2. **Scraper Execution**: Job site scrapers extract data (real from WeWorkRemotely, mock from others)
3. **Data Processing**: Relevance scoring, filtering, deduplication, and ranking
4. **Output Generation**: CSV, JSON, HTML reports plus markdown summary

### Key Components

**Main Entry Point**: `search_jobs.py` - Primary executable that orchestrates the entire job search process

**Job Site Architecture**: 
- Base class `JobSiteSearcher` provides common functionality (HTTP requests, rate limiting, relevance scoring)
- Individual scrapers in `job_sites/` inherit from base and implement site-specific extraction
- Configuration-driven enablement through `config.yaml` (real_job_sites vs mock_job_sites)

**Data Structure**: `JobPosting` dataclass with fields: title, company, location, salary, description, url, date_posted, job_site, relevance_score

### Real vs Mock Data Strategy
- **Real Data**: Only WeWorkRemotely currently provides real extracted job data (8 curated high-quality jobs)
- **Mock Data**: FlexJobs, GameDevJobs, NoFlapJobs provide test data when real sites block requests
- **Hybrid Approach**: System gracefully falls back to mock data when real scraping fails

## Key Technical Details

### Relevance Scoring Algorithm
- Search terms in title: +10 points each
- Search terms in description: +5 points each  
- Preferred keywords in title: +8 points each
- Preferred keywords in description: +4 points each
- Excluded keywords: -20 points each
- Unity/Game dev bonus: +25 title, +12 description
- Score range: 0-100, capped at 100

### Anti-Detection Measures
- User-Agent rotation using `fake-useragent` library
- 2-5 second delays between requests
- Realistic browser-like HTTP headers
- Retry logic with exponential backoff (up to 3 retries)
- Rate limiting detection (handles 429 and 403 responses)

### Configuration System
`config.yaml` structure:
- **search_terms**: Unity, game dev, web dev, C# developer, etc.
- **real_job_sites**: WeWorkRemotely (enabled), others (disabled due to blocking)
- **mock_job_sites**: FlexJobs, GameDevJobs, NoFlapJobs for testing
- **filters**: Salary range, experience levels, preferred/excluded keywords
- **output**: File formats (CSV/JSON/HTML), results directory, max results

## Current Job Site Status

### Enabled Sites (Real Data)
- ✅ **WeWorkRemotely**: 8 high-quality jobs manually extracted and curated

### Blocked Sites (in config but disabled)
- ❌ **Indeed**: Returns 403 Forbidden errors
- ❌ **RemoteOK**: Returns HTML instead of JSON API responses  
- ❌ **LinkedIn/Glassdoor**: Require user login
- ❌ **GitHub Jobs**: Service discontinued

### Mock/Testing Sites
- 🔧 **FlexJobs**: Simulated flexible work positions
- 🔧 **GameDevJobs**: Simulated Unity and game development jobs
- 🔧 **NoFlapJobs**: General developer positions for testing

## Adding New Job Sites

### Development Process
1. Create new scraper file in `job_sites/` directory
2. Use `weworkremotely.py` as template for structure and patterns
3. Add new searcher class to `search_jobs.py` in `_initialize_searchers()` method
4. Enable in `config.yaml` under `real_job_sites` or `mock_job_sites`
5. Test independently before integration

### Scraper Implementation
Each scraper must return `List[JobPosting]` with proper relevance scoring. Use base class `JobSiteSearcher` for common functionality like HTTP requests and scoring.

## Output System

### Generated Files
- `results/jobs_YYYYMMDD_HHMMSS.csv` - Spreadsheet format
- `results/jobs_YYYYMMDD_HHMMSS.json` - Data format  
- `results/jobs_YYYYMMDD_HHMMSS.html` - Web page format
- `job_opportunities_summary.md` - Human-readable summary with top opportunities

### Console Output
Uses `rich` library for colored tables, progress bars, and formatted terminal output

## Dependencies

### Python Dependencies
- **requests**: HTTP client for API calls and web scraping
- **beautifulsoup4**: HTML parsing and data extraction
- **rich**: Beautiful console output with colors and tables
- **pyyaml**: Configuration file parsing
- **click**: Command-line interface framework
- **fake-useragent**: User-Agent string rotation

### JavaScript Dependencies (Legacy)
- **puppeteer**: Browser automation for complex sites
- **playwright**: Alternative browser automation
- **axios**: HTTP client for API requests
- **cheerio**: Server-side jQuery for HTML parsing

## Error Handling & Limitations

### Current Challenges
- Most major job sites block automated requests with CAPTCHA and rate limiting
- API restrictions limit access to job board APIs  
- JavaScript-heavy SPAs require browser automation

### Resilience Features
- Graceful fallbacks to mock data when real scraping fails
- Individual site failures don't break entire search
- Network timeouts with retry logic (20-second timeout)
- CAPTCHA detection and reporting

## Quality Assurance

- Real data priority over mock data
- Manual review of relevance scoring algorithm results
- Comprehensive error logging and handling
- CSV/JSON/HTML output verification