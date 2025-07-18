# 🎯 Job Searcher - Find Unity & Web Development Jobs

A comprehensive job search tool that finds real remote job opportunities for Unity developers and web developers. Currently searches WeWorkRemotely with real job data extracted from actual job postings.

## 🚀 **Quick Start**

### **Run the Job Searcher:**
```bash
python search_jobs.py
```

That's it! The app will:
- Search all enabled job sites (WeWorkRemotely, FlexJobs, GameDevJobs)
- Use your search terms from `config.yaml` 
- Display results ranked by relevance score
- Save results to `results/` folder in CSV and JSON formats

## 📁 **Project Structure**

```
job-searcher/
├── search_jobs.py           # 🚀 MAIN FILE - Run this!
├── config.yaml              # ⚙️ Search preferences
├── requirements.txt         # 📦 Dependencies
├── job_opportunities_summary.md  # 📊 Latest results summary
├── job_sites/               # 🌐 Job site scrapers
│   ├── README.md           # 📖 How to add new job sites
│   └── weworkremotely.py   # 🔥 WeWorkRemotely scraper (real data)
├── results/                # 📈 Search results (CSV/JSON)
├── legacy/                 # 🗂️ Old scripts and tests
└── venv/                   # 🐍 Python virtual environment
```

## ⚙️ **Configuration**

Edit `config.yaml` to customize your search:

```yaml
# What jobs to search for
search_terms:
  - "unity developer"
  - "game developer" 
  - "c# developer"
  - "web developer"
  - "frontend developer"
  - "full stack developer"

# Real Job Sites (actual job boards with real data)
real_job_sites:
  weworkremotely: true   # ✅ Real data from WeWorkRemotely
  indeed: false          # ❌ Blocks automated requests
  linkedin: false        # ❌ Requires login

# Mock/Testing Job Sites (fake data for development)
mock_job_sites:
  flexjobs: false        # 🔧 Mock flexible jobs (disabled)
  gamedev: false         # 🔧 Mock Unity jobs (disabled)
  noflap: false          # 🔧 Mock general jobs (disabled)
```

## 🎯 **Current Results**

**Real WeWorkRemotely Jobs Found:**
- 🔥 **Remote C# .NET Developer** at Jigsaw Trading (100.0 score) - Perfect for Unity devs!
- ⚛️ **Senior React Full Stack Engineer** at Video Fire (100.0 score, $100k+)
- 🚀 **Senior Full Stack Engineer** at Sonix (100.0 score, $100k+, AI focus)
- 📱 **Senior TypeScript SDK Engineer** at Nutrient (93.0 score)
- ⭐ **Founding Senior Engineer** at Revenue Vessel (86.0 score, startup equity)

## 📊 **Understanding Relevance Scores**

- **100.0:** Perfect match (apply immediately!)
- **90-99:** Excellent match (high priority)
- **80-89:** Very good match (good opportunity)
- **70-79:** Good match (worth considering)
- **<70:** Fair match (backup options)

## 🔧 **Dependencies**

Install required packages:
```bash
pip install -r requirements.txt
```

**Key dependencies:**
- `beautifulsoup4` - HTML parsing
- `requests` - HTTP requests  
- `rich` - Beautiful console output
- `pyyaml` - Configuration files
- `click` - Command line interface

## 🌐 **Adding New Job Sites**

See `job_sites/README.md` for detailed instructions on adding new job sites like Indeed, Stack Overflow Jobs, RemoteOK, etc.

## 📈 **Output Files**

After running, check these files:
- `results/jobs_YYYYMMDD_HHMMSS.csv` - Spreadsheet format
- `results/jobs_YYYYMMDD_HHMMSS.json` - Data format
- `job_opportunities_summary.md` - Human-readable summary

## 🎮 **Perfect for Unity Developers**

The job searcher found that **Unity developers have excellent opportunities** in:
- **Fintech/Trading platforms** (C# skills transfer perfectly)
- **Game development studios** (direct Unity experience)
- **Web development** (transferable programming skills)

## 🌐 **Perfect for Web Developers**

Found multiple **$100k+ remote positions** in:
- **React/Full-stack development**
- **TypeScript/JavaScript roles** 
- **AI/Video technology companies**
- **Startup founding engineer positions**

## 🚨 **Troubleshooting**

**Common issues:**
- **ImportError:** Run `pip install -r requirements.txt`
- **No jobs found:** Check `config.yaml` settings
- **Permission errors:** Ensure write access to `results/` folder

## 📞 **Support**

- Check `legacy/test_basic.py` for debugging
- Review `job_sites/README.md` for scraper issues
- Update search terms in `config.yaml` for different results

---

*Last updated: July 17, 2025 - Real job data from WeWorkRemotely*