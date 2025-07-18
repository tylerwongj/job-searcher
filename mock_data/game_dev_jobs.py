#!/usr/bin/env python3
"""
Mock Game Development jobs data for testing Unity and game dev opportunities
"""

from datetime import datetime
from typing import List, Dict

def get_game_dev_jobs_data() -> List[Dict]:
    """
    Generate mock game development job data.
    This simulates what specialized game dev job sites might return.
    """
    return [
        {
            'title': 'Unity Developer - Mobile Games',
            'company': 'GameStudio Pro',
            'location': 'Remote',
            'salary': '$70,000 - $95,000',
            'description': 'Unity developer for mobile game projects. Experience with C#, Unity 2022+, and mobile optimization required. Work on hyper-casual and mid-core games for iOS and Android.',
            'url': 'https://gamedevjobs.com/unity-mobile-1'
        },
        {
            'title': 'Senior Unity Developer',
            'company': 'Indie Games Inc',
            'location': 'Remote',
            'salary': '$85,000 - $120,000',
            'description': 'Senior Unity developer for indie game studio. Work on PC and console games using Unity and C#. Lead technical decisions and mentor junior developers.',
            'url': 'https://gamedevjobs.com/senior-unity-2'
        },
        {
            'title': 'Game Developer - Unity & C#',
            'company': 'Virtual Reality Studios',
            'location': 'Remote',
            'salary': '$75,000 - $110,000',
            'description': 'VR game developer using Unity and C#. Experience with VR/AR development preferred. Work on immersive experiences for Oculus, PSVR, and SteamVR.',
            'url': 'https://gamedevjobs.com/vr-unity-3'
        },
        {
            'title': 'Frontend Game Developer',
            'company': 'Web Games Co',
            'location': 'Remote',
            'salary': '$65,000 - $90,000',
            'description': 'Frontend developer for web-based games. JavaScript, WebGL, and Three.js experience required. Build browser games and interactive experiences.',
            'url': 'https://gamedevjobs.com/frontend-game-4'
        },
        {
            'title': 'Full Stack Developer - Gaming Platform',
            'company': 'GameTech Solutions',
            'location': 'Remote',
            'salary': '$80,000 - $115,000',
            'description': 'Full stack developer for gaming platform. React, Node.js, and game integration APIs. Build tools and platforms that support game developers.',
            'url': 'https://gamedevjobs.com/fullstack-platform-5'
        }
    ]

def get_unity_specific_jobs() -> List[Dict]:
    """Get jobs specifically for Unity developers."""
    all_jobs = get_game_dev_jobs_data()
    return [job for job in all_jobs if 'unity' in job['title'].lower() or 'unity' in job['description'].lower()]

if __name__ == "__main__":
    """Test the mock data."""
    from rich.console import Console
    
    console = Console()
    test_jobs = get_game_dev_jobs_data()
    unity_jobs = get_unity_specific_jobs()
    
    console.print("[yellow]Mock Game Development Jobs:[/yellow]")
    for job in test_jobs:
        console.print(f"  • {job['title']} at {job['company']}")
    
    console.print(f"\n[cyan]Unity-specific jobs: {len(unity_jobs)}/{len(test_jobs)}[/cyan]")