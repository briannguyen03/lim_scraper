# UVic Job Board Scraper & Resume Matcher

## Overview

This project automates the process of collecting co-op job postings from the **University of Victoria’s Learning in Motion (LIM) job board** and comparing them against your resume.

It is a two-part workflow:

1. **Scraping**: Extracts job metadata, job descriptions, and qualifications.
2. **Matching**: Sends your resume and all scraped postings to a local resume-matcher API for comparison.

if you just want the scraped jobs then comment out "subprocess.run(["python3", "match-client.py"])" in job_scrape.py

The result is a ranked list of job matches saved to file.

---

## Features

* Automated Selenium scraping of LIM job postings.
* Saves:

  * Structured job metadata → `uvic_jobs.tsv`.
  * Individual job descriptions → `job_desc/*.txt`.
* Calls a local API to match postings with your resume.
* Saves match results to `job_matches.txt`.
* Supports resume formats: **PDF, TXT, DOCX**.

---

## Requirements

* **Python 3.x**
* **Selenium** (`pip install selenium`)
* **Google Chrome** + matching **ChromeDriver** in PATH
* **requests** (`pip install requests`)
* A running **resume-matcher API** (local server on `http://localhost:3000/api/upload`)

---

## Directory Setup

The following directories must exist before running:

```
job_desc/   # Populated automatically with scraped job descriptions
resume/     # Place your resume here (PDF, TXT, or DOCX)
```

Example:

```
resume/
 └── BrianNguyen.pdf
```

---

## Installation

Clone the repository and install dependencies:

```bash
git clone <repo-url>
cd job-board-scraper
pip install -r requirements.txt
```

---

## Usage

### 1. Run the Scraper

Start by scraping the UVic LIM job board:

```bash
python job_scrape.py
```

* A Chrome window will open.
* Log in manually (including 2FA if required).
* Once the job postings are visible, return to the terminal and press **ENTER**.
* Job descriptions will be saved to `job_desc/` and metadata to `uvic_jobs.tsv`.
* Every 10 jobs, the script pauses — press **ENTER** to continue or type `match` to stop scraping and proceed to resume matching.

### 2. Run the Matcher (automatic)

At the end of scraping, if job descriptions are found, the script automatically calls:

```bash
python match-client.py
```

This sends your resume + scraped jobs to the matcher API.
Results are written to:

```
job_matches.txt
```

---

## Project Structure

```
.
├── job_scrape.py      # Scraper: extracts jobs from UVic LIM
├── match-client.py    # Client: sends resume + jobs to matcher API
├── uvic_jobs.tsv      # Tab-separated job metadata (created at runtime)
├── job_matches.txt    # JSON output of resume matcher results (created at runtime)
├── job_desc/          # Job description text files (populated at runtime)
└── resume/            # Directory to store your resume (user-provided)
```

---

## Notes

* You must manually log in to LIM; the scraper does not handle credentials.
* Ensure ChromeDriver version matches your installed Chrome browser.
* The matcher API must be running locally on port 3000 before using this project.
* If no job descriptions are scraped, `match-client.py` will be skipped.
