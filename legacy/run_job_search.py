#!/usr/bin/env python3
"""
Hybrid Job Search Runner
Runs JavaScript scraper followed by Python analysis and processing.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
import time
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

def run_command(command, description):
    """Run a command and return success status."""
    console = Console()
    
    with Progress(
        SpinnerColumn(),
        TextColumn(f"[progress.description]{description}"),
        console=console
    ) as progress:
        task = progress.add_task(description, total=None)
        
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                progress.update(task, completed=True)
                return True, result.stdout
            else:
                progress.update(task, completed=True)
                console.print(f"[red]Error: {result.stderr}[/red]")
                return False, result.stderr
                
        except Exception as e:
            progress.update(task, completed=True)
            console.print(f"[red]Error running command: {e}[/red]")
            return False, str(e)

def main():
    """Main function to run the hybrid job search."""
    console = Console()
    
    console.print(Panel.fit(
        "[bold blue]Hybrid Job Search[/bold blue]\\n"
        "JavaScript scraping + Python analysis",
        border_style="blue"
    ))
    
    # Check if Node.js is installed
    success, _ = run_command("node --version", "Checking Node.js installation")
    if not success:
        console.print("[red]Node.js is not installed. Please install Node.js first.[/red]")
        sys.exit(1)
    
    # Install JavaScript dependencies if needed
    if not Path("node_modules").exists():
        success, _ = run_command("npm install", "Installing JavaScript dependencies")
        if not success:
            console.print("[red]Failed to install JavaScript dependencies.[/red]")
            sys.exit(1)
    
    # Run JavaScript scraper
    console.print("\\n[bold yellow]Phase 1: JavaScript Scraping[/bold yellow]")
    success, output = run_command("node scraper.js", "Running JavaScript scraper")
    if not success:
        console.print("[red]JavaScript scraper failed.[/red]")
        sys.exit(1)
    
    # Check if jobs.json was created
    if not Path("jobs.json").exists():
        console.print("[red]No jobs.json file was created by the scraper.[/red]")
        sys.exit(1)
    
    # Show scraper results
    with open("jobs.json", "r") as f:
        scraped_jobs = json.load(f)
    
    console.print(f"[green]✓ JavaScript scraper found {len(scraped_jobs)} jobs[/green]")
    
    # Run Python processor
    console.print("\n[bold yellow]Phase 2: Python Processing[/bold yellow]")
    success, output = run_command("source venv/bin/activate && python3 job_searcher.py", "Running Python analysis")
    if not success:
        console.print("[red]Python processor failed.[/red]")
        sys.exit(1)
    
    console.print("\\n[bold green]✓ Job search completed successfully![/bold green]")
    console.print("Check the results directory for output files.")

if __name__ == "__main__":
    main()
