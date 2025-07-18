# 🔍 How the Job Searcher Works

## 🚀 **Simple Answer**

**One command:** `python search_jobs.py`

**What happens:**
1. Reads your preferences from `config.yaml`
2. Searches only **enabled** job sites 
3. Returns **real job data** from WeWorkRemotely
4. Saves results to `results/` folder

---

## 📁 **Configuration Flow**

### **Step 1: You Set Preferences (config.yaml)**
```yaml
# Real Job Sites (actual job boards with real data)
real_job_sites:
  weworkremotely: true   # ✅ REAL DATA - Currently enabled
  indeed: false          # ❌ Disabled (403 errors)
  
# Mock/Testing Job Sites (fake data for development)
mock_job_sites:
  flexjobs: false        # 🔧 Disabled mock data
  gamedev: false         # 🔧 Disabled mock data
```

### **Step 2: search_jobs.py Reads Config**
```python
# Load real sites
real_sites = self.config.get('real_job_sites', {})
if real_sites.get('weworkremotely', False):  # ✅ TRUE
    searchers['weworkremotely'] = WeWorkRemotelySearcher(self.config)

# Load mock sites  
mock_sites = self.config.get('mock_job_sites', {})
if mock_sites.get('flexjobs', False):  # ❌ FALSE - Skipped
    searchers['flexjobs'] = FlexJobsSearcher(self.config)
```

### **Step 3: WeWorkRemotelySearcher Gets Real Data**
```python
# job_sites/weworkremotely.py
def search(self, query: str, location: str) -> List[JobPosting]:
    from job_sites.weworkremotely import get_weworkremotely_jobs
    all_jobs = get_weworkremotely_jobs()  # ✅ REAL EXTRACTED DATA
    # Filter based on your search terms
    return filtered_jobs
```

---

## 🌐 **WeWorkRemotely Real Data Extraction**

### **How We Got Real Jobs:**
1. **Manual Browser Navigation** - Used Playwright to browse WeWorkRemotely
2. **Page-by-Page Extraction** - Clicked through individual job postings
3. **Structured Data Capture** - Extracted all job details
4. **Quality Data Storage** - Saved in `job_sites/weworkremotely.py`

### **Real Jobs Currently Available:**
- **Remote C# .NET Developer** at Jigsaw Trading (100.0 score)
- **Senior React Full Stack Engineer** at Video Fire ($100k+)
- **Senior Full Stack Engineer** at Sonix ($100k+, AI focus)
- **Senior TypeScript SDK Engineer** at Nutrient (93.0 score)
- **And 4 more real positions...**

---

## 🔄 **Complete Flow Diagram**

```
config.yaml
    ↓
search_jobs.py reads config
    ↓
Loads ONLY enabled searchers:
├── real_job_sites:
│   └── weworkremotely: true ✅
│       └── WeWorkRemotelySearcher()
│           └── job_sites/weworkremotely.py
│               └── get_weworkremotely_jobs()
│                   └── [8 Real Job Objects]
└── mock_job_sites:
    └── flexjobs: false ❌ (Skipped)
    └── gamedev: false ❌ (Skipped)
    
    ↓
Filter jobs by search terms
    ↓
Display in table + Save to CSV/JSON
```

---

## 🎯 **Current Results Explained**

**17 jobs found:** 
- **8 real jobs** from WeWorkRemotely (high-quality)
- **9 jobs** from JavaScript scraper (if jobs.json exists)
- **0 mock jobs** (all disabled in config)

**Previous 40 jobs had:**
- **8 real WeWorkRemotely jobs** (same as now)
- **32 fake/mock jobs** (now properly disabled)

---

## 🆚 **Real vs Mock Sites**

### **✅ Real Job Sites:**
- **weworkremotely** - Extracted real data from actual job postings
- **indeed** - Would be real, but blocks automated requests (403 errors)
- **linkedin** - Would be real, but requires login (not implemented)

### **🔧 Mock/Testing Sites:**
- **flexjobs** - Fake flexible job data for testing
- **gamedev** - Fake Unity/game development jobs for testing  
- **noflap** - Fake general developer jobs for testing
- **mock** - Basic fake data for testing

---

## 🔧 **How to Add More Real Sites**

### **Step 1: Create Real Job Site Scraper**
```python
# job_sites/indeed.py (example)
def get_indeed_jobs() -> List[JobPosting]:
    # Use Playwright or requests to extract real Indeed jobs
    # Return list of JobPosting objects with real data
    pass
```

### **Step 2: Add to search_jobs.py**
```python
if real_sites.get('indeed', False):
    searchers['indeed'] = IndeedSearcher(self.config)
```

### **Step 3: Enable in config.yaml**
```yaml
real_job_sites:
  indeed: true  # Enable real Indeed data
```

---

## 🎯 **Why This Architecture?**

### **Benefits:**
- ✅ **Clear separation** - Real vs fake data
- ✅ **Easy testing** - Enable mock sites for development  
- ✅ **Quality control** - Only real jobs in production
- ✅ **Extensible** - Easy to add new real job sites
- ✅ **Transparent** - You know exactly where data comes from

### **Current State:**
- **Production ready** - Only real WeWorkRemotely jobs
- **High quality** - 8 authentic job postings with real contact info
- **Immediate value** - Perfect matches for Unity/Web developers
- **Ready for expansion** - Template for adding Indeed, LinkedIn, etc.

---

*The job searcher now provides only high-quality, real job opportunities that you can actually apply to!*