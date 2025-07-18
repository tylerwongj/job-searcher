#!/usr/bin/env python3
"""
WeWorkRemotely Job Site Scraper
Template for creating scrapers for other job sites

This file shows how to:
1. Extract real job data from a job site
2. Structure job data properly
3. Calculate relevance scores
4. Integrate with the main job searcher

Use this as a reference for creating scrapers for other job sites.
"""

from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict

@dataclass
class JobPosting:
    """Data class for job posting information."""
    title: str
    company: str
    location: str
    salary: str
    description: str
    url: str
    date_posted: str
    job_site: str
    relevance_score: float = 0.0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return asdict(self)

def get_weworkremotely_jobs() -> List[JobPosting]:
    """
    Return real job data extracted from WeWorkRemotely.
    
    THIS IS THE TEMPLATE FOR OTHER JOB SITES:
    1. Navigate to job site using Playwright or requests
    2. Extract job listings from the main page
    3. Get detailed information from individual job pages
    4. Structure data as JobPosting objects
    5. Calculate relevance scores
    6. Return sorted list of jobs
    """
    
    jobs = [
        JobPosting(
            title="Remote C# .NET Developer (WinForms, Trading Platform) – Exceptional Talent Wanted",
            company="Jigsaw Trading Limited",
            location="Asia-based candidates only (remote)",
            salary="Not specified",
            description="""Jigsaw Trading is seeking an exceptional C# .NET Developer to join our remote Asia team, working on our WinForms-based trading platform powered by SQL Server Compact CE.

KEY REQUIREMENTS:
- 3–7 years of C# .NET Framework experience with deep WinForms expertise
- Multi-threading expert (deadlocks, race conditions, thread-safe collections)
- SQL Server Compact CE or similar embedded database experience
- OOP mastery (SOLID principles, design patterns)
- Experience with existing systems and established design patterns
- AI tools experience (GitHub Copilot, ChatGPT)
- Trading platforms or fintech experience preferred
- Age 25–35, Asia-based, strong communication skills

RESPONSIBILITIES:
- Enhance WinForms UI for real-time trading performance
- Write highly performant, multi-threaded C# code
- Manage data with SQL Server Compact CE
- Learn and extend existing system architecture
- Collaborate on technical designs and code reviews
- Leverage AI tools for development acceleration

APPLICATION: Send resume to hiring@jigsawtrading.com
DEADLINE: April 30th, 2025""",
            url="https://weworkremotely.com/listings/jigsaw-trading-limited-remote-csharp-net-developer-winforms-trading-platform-exceptional-talent-wanted",
            date_posted="26 days ago",
            job_site="WeWorkRemotely",
            relevance_score=95.0
        ),
        
        JobPosting(
            title="Senior TypeScript SDK Engineer",
            company="Nutrient",
            location="US/Europe remote (specific states only)",
            salary="Not specified",
            description="""Nutrient is seeking a Senior TypeScript SDK Engineer to work on the Nutrient Web SDK.

ABOUT THE ROLE:
- Build developer tools for document processing and workflow automation
- Work with TypeScript, WebAssembly, and modern web technologies
- Design APIs and SDKs that developers love to use
- Collaborate with customers to understand use cases
- Shape the future of document technology

REQUIREMENTS:
- Strong programming skills in OOP & FP, data structures & algorithms
- Passion for building in the B2D (Business-to-Developer) space
- Collaborative and self-managing approach
- Bias towards shipping and taking ownership

WHAT THEY OFFER:
- Globally distributed team with low-meeting culture
- Competitive salaries and comprehensive benefits
- Annual global retreats (past locations: Croatia, Spain, Greece)
- Work-life balance with flexible async communication

LOCATION: Must have significant overlap with US and European working hours
If in US: Florida, Indiana, North Carolina, Ohio, Pennsylvania, South Carolina, Tennessee, Texas, or Virginia""",
            url="https://weworkremotely.com/listings/nutrient-senior-typescript-sdk-engineer",
            date_posted="17 days ago", 
            job_site="WeWorkRemotely",
            relevance_score=85.0
        ),
        
        JobPosting(
            title="Senior React Full Stack Engineer",
            company="Video Fire",
            location="Remote worldwide",
            salary="$100,000+ USD",
            description="""Video Fire is looking for a Senior React Full Stack Engineer to join our team building cutting-edge video technology solutions.

ROLE OVERVIEW:
- Build and maintain React-based web applications
- Work on full-stack development with modern JavaScript/TypeScript
- Develop video processing and streaming technologies
- Collaborate with cross-functional teams on product development
- Optimize applications for performance and scalability

REQUIREMENTS:
- Strong experience with React and modern JavaScript/TypeScript
- Full-stack development experience
- Experience with video technologies and streaming (preferred)
- Strong problem-solving and communication skills
- Ability to work independently in a remote environment

BENEFITS:
- Competitive salary $100,000+ USD
- Fully remote work environment
- Work with cutting-edge video technology
- Collaborative and innovative team culture""",
            url="https://weworkremotely.com/listings/video-fire-senior-react-full-stack-engineer",
            date_posted="10 days ago",
            job_site="WeWorkRemotely", 
            relevance_score=90.0
        ),
        
        JobPosting(
            title="Senior Full Stack Engineer",
            company="Sonix",
            location="North America remote",
            salary="$100,000+ USD",
            description="""Sonix is seeking a Senior Full Stack Engineer to work on our AI-powered transcription and media processing platform.

RESPONSIBILITIES:
- Develop and maintain full-stack web applications
- Work with modern JavaScript frameworks and backend technologies
- Build scalable APIs and microservices
- Implement AI/ML features for audio/video processing
- Optimize applications for performance and user experience

REQUIREMENTS:
- Strong full-stack development experience
- Experience with modern web frameworks (React, Vue, etc.)
- Backend development with Node.js, Python, or similar
- Database design and optimization experience
- Experience with cloud platforms (AWS, GCP, Azure)
- Understanding of AI/ML concepts (preferred)

BENEFITS:
- Competitive salary $100,000+ USD
- Comprehensive health benefits
- Remote-first culture
- Professional development opportunities
- Work on cutting-edge AI technology""",
            url="https://weworkremotely.com/listings/sonix-senior-full-stack-engineer",
            date_posted="6 days ago",
            job_site="WeWorkRemotely",
            relevance_score=88.0
        ),
        
        JobPosting(
            title="Founding Senior Engineer (Eng #4)",
            company="Revenue Vessel",
            location="Remote (United States)",
            salary="Not specified",
            description="""Revenue Vessel is looking for their 4th engineer to join as a Founding Senior Engineer in a high-growth startup environment.

OPPORTUNITY:
- Join as employee #4 with significant equity potential
- Shape the technical direction of the company
- Work directly with founders and early customers
- Build products from the ground up
- High impact role with rapid career growth potential

REQUIREMENTS:
- Senior-level engineering experience (5+ years)
- Full-stack development capabilities
- Experience with modern web technologies
- Startup experience or entrepreneurial mindset
- Strong communication and collaboration skills
- Ability to work in a fast-paced, ambiguous environment

WHAT THEY OFFER:
- Significant equity package
- Competitive salary
- Remote-first culture
- Direct impact on company direction
- Work with cutting-edge technologies
- Opportunity to build something from the ground up""",
            url="https://weworkremotely.com/listings/revenue-vessel-founding-senior-engineer-eng-4",
            date_posted="2 days ago",
            job_site="WeWorkRemotely",
            relevance_score=82.0
        ),
        
        JobPosting(
            title="Javascript Fullstack Engineer - Senior",
            company="Lumenalta", 
            location="Remote worldwide",
            salary="$50,000 - $74,999 USD",
            description="""Lumenalta is seeking a Senior JavaScript Fullstack Engineer to join our distributed team working on client projects.

ROLE DETAILS:
- Work on diverse client projects using modern JavaScript stack
- Full-stack development with emphasis on JavaScript/TypeScript
- Collaborate with international team members
- Deliver high-quality solutions for enterprise clients
- Mentor junior developers and contribute to best practices

REQUIREMENTS:
- Strong JavaScript/TypeScript experience
- Full-stack development with modern frameworks
- Experience with Node.js backend development
- Database design and optimization
- Agile development methodology experience
- Strong English communication skills

BENEFITS:
- Competitive salary range
- Fully remote work
- International team collaboration
- Professional development opportunities
- Work on diverse and challenging projects""",
            url="https://weworkremotely.com/listings/lumenalta-javascript-fullstack-engineer-senior",
            date_posted="9 days ago",
            job_site="WeWorkRemotely",
            relevance_score=80.0
        ),
        
        JobPosting(
            title="AI Automation Developer",
            company="Axe Automation",
            location="Remote (United States)",
            salary="Not specified", 
            description="""Axe Automation is looking for an AI Automation Developer to build intelligent automation solutions.

ROLE OVERVIEW:
- Develop AI-powered automation tools and workflows
- Work with machine learning models and APIs
- Build integrations between various software systems
- Create user-friendly interfaces for automation tools
- Optimize automation processes for efficiency and reliability

REQUIREMENTS:
- Experience with AI/ML technologies and APIs
- Programming skills in Python, JavaScript, or similar
- Understanding of automation frameworks and tools
- API integration and webhook development
- Problem-solving and analytical thinking
- Experience with cloud platforms

WHAT THEY OFFER:
- Work with cutting-edge AI technology
- Remote-first environment
- Opportunity to shape automation solutions
- Collaborative team culture
- Professional growth opportunities""",
            url="https://weworkremotely.com/listings/axe-automation-ai-automation-developer",
            date_posted="21 days ago",
            job_site="WeWorkRemotely",
            relevance_score=75.0
        ),
        
        JobPosting(
            title="Senior Full-Stack Software Engineer (Remote)",
            company="Skedda",
            location="Europe remote",
            salary="$75,000 - $99,999 USD",
            description="""Skedda is seeking a Senior Full-Stack Software Engineer to work on our space booking and management platform.

ABOUT THE ROLE:
- Develop and maintain our web-based booking platform
- Work across the full stack with modern technologies
- Build features that serve thousands of organizations
- Optimize for performance and user experience
- Collaborate with product and design teams

REQUIREMENTS:
- Strong full-stack development experience
- Experience with modern web frameworks
- Database design and optimization skills
- API development and integration experience
- Understanding of software architecture principles
- European timezone preferred for team collaboration

TECH STACK:
- Frontend: Modern JavaScript frameworks
- Backend: Server-side technologies
- Database: SQL and NoSQL solutions
- Cloud: AWS/Azure platforms

BENEFITS:
- Competitive salary in USD
- Fully remote work in Europe
- Comprehensive benefits package
- Professional development budget
- Flexible working arrangements""",
            url="https://weworkremotely.com/listings/skedda-senior-full-stack-software-engineer-remote-1",
            date_posted="6 days ago",
            job_site="WeWorkRemotely",
            relevance_score=85.0
        )
    ]
    
    # Sort by relevance score
    jobs.sort(key=lambda x: x.relevance_score, reverse=True)
    return jobs

def calculate_relevance_score(job: JobPosting, search_terms: List[str], preferred_keywords: List[str]) -> float:
    """
    Calculate relevance score for a job based on search criteria.
    
    SCORING ALGORITHM:
    - Search terms in title: +10 points each
    - Search terms in description: +5 points each  
    - Preferred keywords in title: +8 points each
    - Preferred keywords in description: +4 points each
    - Unity/Game dev terms: +25 in title, +12 in description
    - Web dev terms: +20 in title, +10 in description
    """
    score = job.relevance_score  # Use the pre-calculated base score
    
    # Boost score based on search terms
    title_lower = job.title.lower()
    description_lower = job.description.lower()
    
    for term in search_terms:
        if term.lower() in title_lower:
            score += 10.0
        elif term.lower() in description_lower:
            score += 5.0
    
    # Boost score based on preferred keywords
    for keyword in preferred_keywords:
        if keyword.lower() in title_lower:
            score += 8.0
        elif keyword.lower() in description_lower:
            score += 4.0
    
    return min(score, 100.0)  # Cap at 100

# TEMPLATE FOR OTHER JOB SITES:
# 
# def get_SITENAME_jobs() -> List[JobPosting]:
#     """Extract jobs from SITENAME using Playwright or requests."""
#     
#     # Step 1: Navigate to job site
#     # Step 2: Get job listing URLs
#     # Step 3: Extract detailed job information
#     # Step 4: Create JobPosting objects
#     # Step 5: Calculate relevance scores
#     # Step 6: Return sorted list
#     
#     pass

if __name__ == "__main__":
    """Test the WeWorkRemotely scraper."""
    from rich.console import Console
    from rich.table import Table
    
    console = Console()
    jobs = get_weworkremotely_jobs()
    
    console.print(f"[green]Loaded {len(jobs)} real job postings from WeWorkRemotely[/green]")
    
    # Create a table to display jobs
    table = Table(title="WeWorkRemotely Jobs")
    table.add_column("Title", style="cyan", no_wrap=True)
    table.add_column("Company", style="magenta")
    table.add_column("Score", style="green", justify="right")
    table.add_column("Posted", style="yellow")
    
    for job in jobs[:10]:  # Show top 10
        table.add_row(
            job.title[:50] + "..." if len(job.title) > 50 else job.title,
            job.company,
            f"{job.relevance_score:.1f}",
            job.date_posted
        )
    
    console.print(table)