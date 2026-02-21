# Enhanced UVic Job Board Scraper - Usage Guide

## New Features

The scraper now includes a comprehensive runner script (`run.sh`) with three modes:

### Mode 1: Manual Login (No Cookie Saving)
- Opens browser for manual login
- No cookies are saved
- Good for one-time use or testing

### Mode 2: Manual Login with Cookie Saving  
- Opens browser for manual login
- Saves session cookies to `cookies/` directory
- Allows future automated runs

### Mode 3: Automated Run with Saved Cookies
- Uses previously saved cookies
- Attempts automated login
- Falls back to manual if cookies expire

## Virtual Environment Support

The runner script now automatically:
1. Creates a Python virtual environment in `venv/` directory
2. Activates the virtual environment
3. Installs all dependencies (selenium, requests) in the virtual environment
4. Runs all Python scripts within the virtual environment

## Browser Support

- **Primary**: Chrome (with automatic ChromeDriver detection)
- **Fallback**: Firefox (if Chrome fails or not available)
- Driver auto-detection with helpful error messages

## Setup

1. Make sure you have Python 3 and pip installed
2. Run the script - it will handle everything automatically:
   ```bash
   chmod +x run.sh
   ./run.sh
   ```
3. Select option 4 "Check dependencies and setup" on first run
4. Place your resume in the `resume/` directory

## Quick Start

```bash
# Make run.sh executable
chmod +x run.sh

# Run the interactive menu
./run.sh

# First time: Select option 4 to setup dependencies
# Then: Select option 2 to save cookies for future automation
# Subsequent runs: Select option 3 for automated login
```

## Directory Structure

```
lim_scraper/
├── run.sh              # Main runner script
├── job_scrape.py       # Updated scraper with cookie support
├── match-client.py     # Matcher client (unchanged)
├── venv/               # Python virtual environment (auto-created)
├── cookies/            # Saved browser profiles
│   ├── chrome_profile/
│   └── firefox_profile/
├── job_desc/           # Job descriptions
├── resume/             # Your resume files
├── data/               # Additional data
├── uvic_jobs.tsv       # Job metadata
├── job_matches.txt     # Matching results
└── scraper.log         # Log file
```

## Workflow Recommendation

1. **First time**: Run mode 2 to save cookies
2. **Subsequent runs**: Use mode 3 for automation
3. **If cookies expire**: Fallback to mode 2 to refresh

## Notes

- The script checks for dependencies automatically
- Logs are saved to `scraper.log`
- Error messages use `[error]` prefix
- Info messages use `[*]` prefix (no emojis)
- Virtual environment is automatically managed
