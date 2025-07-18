# 🔧 Mock Data for Testing

This folder contains all the fake/mock job data used for testing and development. **None of this data represents real job opportunities.**

## 📁 **Mock Data Files**

### `flexible_jobs.py`
- **Purpose:** Simulates FlexJobs-style flexible work opportunities
- **Data:** Part-time, contract, and flexible hour positions
- **Use Case:** Testing flexible work filtering and display

### `game_dev_jobs.py`  
- **Purpose:** Simulates specialized game development job sites
- **Data:** Unity, VR, mobile game, and web game positions
- **Use Case:** Testing Unity/game developer specific searches

### `basic_jobs.py`
- **Purpose:** General mock job data for basic testing
- **Data:** Generic software developer positions with random companies
- **Use Case:** General testing and development

## 🚨 **Important Notes**

### **⚠️ This is ALL FAKE DATA:**
- Companies don't exist (TechCorp Global, GameStudio Pro, etc.)
- URLs don't work (https://flexjobs.com/job/fake-123)
- Contact information is fake
- Salaries are made up
- Job descriptions are generic templates

### **✅ Real Data Location:**
- **Real jobs:** `job_sites/weworkremotely.py`
- **Real companies:** Jigsaw Trading, Nutrient, Video Fire, etc.
- **Real URLs:** Actual WeWorkRemotely job posting links
- **Real contact:** hiring@jigsawtrading.com, etc.

## 🔧 **How Mock Data is Used**

### **In config.yaml:**
```yaml
# These control mock data (currently all disabled)
mock_job_sites:
  flexjobs: false        # Uses flexible_jobs.py
  gamedev: false         # Uses game_dev_jobs.py  
  mock: false            # Uses basic_jobs.py
```

### **In search_jobs.py:**
```python
# Mock searchers that use this data
if mock_sites.get('flexjobs', False):
    searchers['flexjobs'] = FlexJobsSearcher()  # Uses flexible_jobs.py

if mock_sites.get('gamedev', False): 
    searchers['gamedev'] = GameDevJobsSearcher()  # Uses game_dev_jobs.py

if mock_sites.get('mock', False):
    searchers['mock'] = MockJobSearcher()  # Uses basic_jobs.py
```

## 🧪 **Testing Mock Data**

Test individual mock data files:
```bash
cd mock_data
python flexible_jobs.py
python game_dev_jobs.py  
python basic_jobs.py
```

## 🎯 **Why Mock Data Exists**

1. **Development:** Test the app without hitting real APIs
2. **Testing:** Verify filtering and scoring algorithms
3. **Demos:** Show how the app works with different job types
4. **Fallback:** Provide data when real sites are down

## 🚫 **Current Status: DISABLED**

All mock data is currently **disabled** in `config.yaml` so you only see **real job opportunities**. This ensures you're not wasting time on fake jobs.

To enable for testing:
```yaml
mock_job_sites:
  flexjobs: true   # Enable mock flexible jobs
  gamedev: true    # Enable mock game dev jobs
```

---

*Remember: Only apply to jobs from the **real_job_sites** section!*