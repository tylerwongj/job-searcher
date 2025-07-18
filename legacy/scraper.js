const puppeteer = require('puppeteer');
const fs = require('fs-extra');
const path = require('path');
const yaml = require('yaml');
const ora = require('ora');

const loadConfig = () => {
  const configPath = path.resolve(__dirname, 'config.yaml');
  const file = fs.readFileSync(configPath, 'utf8');
  return yaml.parse(file);
};

const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));
const axios = require('axios');

// Scrape AngelList using their public API
const scrapeAngelList = async (config) => {
  const jobs = [];
  try {
    // AngelList API endpoint (this may need authentication in practice)
    const response = await axios.get('https://angel.co/api/1/jobs', {
      params: {
        filter: 'remote',
        limit: 20
      },
      timeout: 10000
    });
    
    // Process AngelList jobs (adjust based on actual API response)
    if (response.data && response.data.jobs) {
      for (const job of response.data.jobs) {
        jobs.push({
          title: job.title,
          company: job.company?.name || 'Unknown',
          location: job.location || 'Remote',
          url: job.url || '',
          description: job.description || 'No description available'
        });
      }
    }
  } catch (error) {
    console.log('AngelList scraping failed:', error.message);
  }
  return jobs;
};

// Scrape RemoteOK using their API
const scrapeRemoteOK = async (config) => {
  const jobs = [];
  try {
    const response = await axios.get('https://remoteok.io/api', {
      headers: {
        'User-Agent': 'Mozilla/5.0 (compatible; JobSearcher/1.0)'
      },
      timeout: 10000
    });
    
    if (response.data && Array.isArray(response.data)) {
      // Skip the first item (it's metadata)
      const jobData = response.data.slice(1, 11); // Get first 10 jobs
      
      for (const job of jobData) {
        if (job.position && job.company) {
          jobs.push({
            title: job.position,
            company: job.company,
            location: job.location || 'Remote',
            url: job.url || `https://remoteok.io/remote-jobs/${job.id}`,
            description: job.description || 'No description available'
          });
        }
      }
    }
  } catch (error) {
    console.log('RemoteOK scraping failed:', error.message);
  }
  return jobs;
};

const scrapeJobs = async (config) => {
  const spinner = ora('Starting job scraper...').start();
  
  try {
    const jobs = [];
    
    spinner.text = 'Scraping jobs...';
    
    // Try to scrape real job sites
    try {
      // Example: AngelList (allows scraping)
      const angelListJobs = await scrapeAngelList(config);
      jobs.push(...angelListJobs);
      
      // Example: RemoteOK (has API)
      const remoteOkJobs = await scrapeRemoteOK(config);
      jobs.push(...remoteOkJobs);
      
    } catch (error) {
      console.log('Real scraping failed, using mock data');
      
      // Fallback to mock data
      const mockJobs = [
        {
          title: 'Software Developer',
          company: 'Tech Corp',
          location: 'Remote',
          url: 'https://example.com/job1',
          description: 'Looking for a skilled developer with Python and JavaScript experience.'
        },
        {
          title: 'Full Stack Engineer',
          company: 'Startup Inc',
          location: 'San Francisco, CA',
          url: 'https://example.com/job2',
          description: 'Join our team building modern web applications with React and Node.js.'
        },
        {
          title: 'Backend Developer',
          company: 'Enterprise Solutions',
          location: 'New York, NY',
          url: 'https://example.com/job3',
          description: 'Python developer needed for API development and database design.'
        }
      ];
      
      jobs.push(...mockJobs);
    }
    
    spinner.succeed(`Scraping complete. Found ${jobs.length} jobs.`);
    
    const outputPath = path.resolve(__dirname, 'jobs.json');
    fs.writeFileSync(outputPath, JSON.stringify(jobs, null, 2));
    console.log(`Jobs saved to ${outputPath}`);
    
  } catch (error) {
    spinner.fail('Scraping failed');
    console.error('Error:', error.message);
    
    // Create empty jobs file so Python script doesn't fail
    const outputPath = path.resolve(__dirname, 'jobs.json');
    fs.writeFileSync(outputPath, JSON.stringify([], null, 2));
  }
};

(async () => {
  const config = loadConfig();
  await scrapeJobs(config);
})();
