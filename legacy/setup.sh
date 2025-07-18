#!/bin/bash

# Job Searcher Setup Script
echo "Setting up Job Searcher Application..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.8 or later."
    exit 1
fi

# Check Python version
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "Python version: $python_version"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing required packages..."
pip install -r requirements.txt

# Create results directory
echo "Creating results directory..."
mkdir -p results

echo ""
echo "Setup complete!"
echo ""
echo "To use the job searcher:"
echo "1. Edit config.yaml to customize your search criteria"
echo "2. Activate the virtual environment: source venv/bin/activate"
echo "3. Run the app: python job_searcher.py"
echo ""
echo "Example usage:"
echo "  python job_searcher.py                    # Run with default config"
echo "  python job_searcher.py --config my.yaml  # Use custom config"
echo "  python job_searcher.py --no-save         # Don't save results"
echo "  python job_searcher.py --quiet           # Minimal output"
echo ""
echo "Configuration:"
echo "- Edit config.yaml to set your search terms, locations, and preferences"
echo "- Results will be saved in the 'results' directory"
echo "- Check the HTML report for the best viewing experience"
