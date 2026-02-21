# UVic Job Board Scraper & Resume Matcher

## Overview

This project automates the process of collecting co-op job postings from the **University of Victoria's Learning in Motion (LIM) job board** and comparing them against your resume.

It is a two-part workflow:

1. **Scraping**: Extracts job metadata, job descriptions, and qualifications.
2. **Matching**: Sends your resume and all scraped postings to a local resume-matcher API for comparison.

The result is a ranked list of job matches saved to file.

---

## Enhanced Features

* **Automated runner script** with three operation modes
* **Virtual environment management** (auto-created and activated)
* **Browser fallback support** (Chrome with Firefox fallback)
* **Cookie-based session persistence** for automated login
* **Dependency auto-installation** and validation

---

## Quick Start

```bash
# Clone the repository
git clone https://github.com/briannguyen03/lim_scraper.git
cd lim_scraper

# Make the runner script executable
chmod +x run.sh

# Run the interactive menu
./run.sh
```

## Usage Guide

### Runner Script Modes

The `run.sh` script provides three operation modes:

1. **Manual login (no cookies)**
   - Opens browser for manual login
   - No cookies saved
   - Good for one-time use

2. **Manual login with cookie saving**
   - Opens browser for manual login  
   - Saves session cookies to `cookies/` directory
   - Required for future automated runs

3. **Automated run with saved cookies**
   - Uses previously saved cookies
   - Attempts automated login
   - Falls back to manual if cookies expire

### First-Time Setup

1. Run `./run.sh` and select option 4 "Check dependencies and setup"
2. The script will:
   - Create a Python virtual environment
   - Install required dependencies (selenium, requests)
   - Validate browser installations
   - Create necessary directories

3. Place your resume in the `resume/` directory (PDF, DOCX, or TXT format)

### Recommended Workflow

1. First run: Use mode 2 to save cookies
2. Subsequent runs: Use mode 3 for automation
3. If cookies expire: Use mode 2 to refresh

### Manual Scraping (Legacy)

If you prefer to run without the runner script:

```bash
python job_scrape.py
```

* A browser window will open
* Log in manually (including 2FA if required)
* Once job postings are visible, press ENTER
* Every 10 jobs, the script pauses - press ENTER to continue or type `match` to proceed to matching

### Matching

At the end of scraping, if job descriptions are found, the script automatically calls the matcher:

```bash
python match-client.py
```

This sends your resume + scraped jobs to the matcher API at `http://localhost:3000/api/upload`.
Results are written to `job_matches.txt`.

---

## Project Structure

```
.
├── run.sh              # Main runner script with virtual environment support
├── job_scrape.py       # Enhanced scraper with cookie/browser fallback support
├── match-client.py     # Client: sends resume + jobs to matcher API
├── venv/               # Python virtual environment (auto-created)
├── cookies/            # Saved browser profiles for session persistence
│   ├── chrome_profile/
│   └── firefox_profile/
├── job_desc/           # Job description text files (populated at runtime)
├── resume/             # Directory to store your resume (user-provided)
├── data/               # Additional data storage
├── uvic_jobs.tsv       # Tab-separated job metadata (created at runtime)
├── job_matches.txt     # JSON output of resume matcher results (created at runtime)
└── scraper.log         # Log file for debugging
```

---

## Requirements

* **Python 3.x** with venv or virtualenv support
* **Google Chrome** or **Firefox** browser
* **ChromeDriver** or **GeckoDriver** (auto-detected with helpful errors)
* **resume-matcher API** (optional, for matching functionality)

---

## Notes

* You must manually log in to LIM on first run; the scraper does not handle credentials
* The matcher API must be running locally on port 3000 to enable matching
* If no job descriptions are scraped, the matcher will be skipped
* Logs are saved to `scraper.log` with [*] for info and [error] for errors
