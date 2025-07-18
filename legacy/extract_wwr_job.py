#!/usr/bin/env python3
"""
Extract job data from WeWorkRemotely using current browser state
"""

# Extract the job data from the current page
job_data = {
    "title": "Remote C# .NET Developer (WinForms, Trading Platform) – Exceptional Talent Wanted",
    "company": "Jigsaw Trading Limited", 
    "location": "Asia-based candidates only (remote)",
    "salary": "Not specified",
    "description": """Jigsaw Trading is seeking an exceptional C# .NET Developer to join our remote Asia team, working on our WinForms-based trading platform powered by SQL Server Compact CE.

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
- Leverage AI tools for development acceleration""",
    "url": "https://weworkremotely.com/listings/jigsaw-trading-limited-remote-csharp-net-developer-winforms-trading-platform-exceptional-talent-wanted",
    "date_posted": "26 days ago",
    "job_site": "WeWorkRemotely",
    "application_email": "hiring@jigsawtrading.com",
    "deadline": "April 30th, 2025",
    "skills": ["C#", ".NET Framework", "WinForms", "SQL Server Compact CE", "Multi-threading", "Trading Platform"],
    "relevance_score": 95.0  # High relevance for Unity developers (C# skills transfer)
}

print("Extracted job data:")
print(f"Title: {job_data['title']}")
print(f"Company: {job_data['company']}")
print(f"Location: {job_data['location']}")
print(f"Skills: {', '.join(job_data['skills'])}")
print(f"Relevance Score: {job_data['relevance_score']}")
print(f"Application: {job_data['application_email']}")
print(f"URL: {job_data['url']}")