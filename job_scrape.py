'''
job_scrape.py

Brian Nguyen 
9-07-2025

Scrapes LIM for coop job. Saves all jobs to uvic_jobs.tsv, and matches using match-client.py
note: need to start the server to accept post API endpoint

Updated to support:
- Multiple browser options (Chrome with fallback to Firefox)
- Cookie saving/loading modes
- Environment variable configuration via run.sh
- Selenium 4.6.0+ automatic driver management
- Improved browser detection for macOS
'''

import os
import time
import re
import subprocess
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService


class UVicJobBoardScraper:
    def __init__(self):
        self.mode = os.environ.get('SCRAPER_MODE', 'manual')
        self.save_cookies = os.environ.get('SAVE_COOKIES', 'false').lower() == 'true'
        self.browser_choice = os.environ.get('SCRAPER_BROWSER', 'chrome')
        
        print(f"[*] Initializing scraper with mode: {self.mode}, browser: {self.browser_choice}, save_cookies: {self.save_cookies}")
        
        self.driver = self.setup_driver()
        
    def setup_driver(self):
        print(f"[*] Setting up {self.browser_choice} driver...")
        
        if self.browser_choice == 'chrome':
            return self.setup_chrome_driver()
        elif self.browser_choice == 'firefox':
            return self.setup_firefox_driver()
        else:
            print(f"[error] Unsupported browser: {self.browser_choice}")
            sys.exit(1)
    
    def setup_chrome_driver(self):
        options = ChromeOptions()
        
        # Add options for cookie saving/loading
        if self.save_cookies or self.mode == 'auto':
            chrome_profile_dir = os.environ.get('CHROME_USER_DATA_DIR')
            if chrome_profile_dir and os.path.exists(chrome_profile_dir):
                print(f"[*] Using Chrome profile from: {chrome_profile_dir}")
                options.add_argument(f'--user-data-dir={chrome_profile_dir}')
            elif self.mode == 'auto':
                print("[error] Chrome profile directory not specified for auto mode")
                sys.exit(1)
        
        # Add common options
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        try:
            # Try to import webdriver_manager, install if not available
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                print("[*] Setting up ChromeDriver automatically...")
                service = ChromeService(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=options)
            except ImportError:
                print("[*] webdriver-manager not available, trying direct Chrome driver...")
                driver = webdriver.Chrome(options=options)
            
            print("[*] Chrome driver initialized successfully")
            return driver
        except Exception as e:
            print(f"[error] Failed to initialize Chrome driver: {e}")
            print("[*] Attempting to fallback to Firefox...")
            return self.setup_firefox_fallback()
    
    def setup_firefox_driver(self):
        options = FirefoxOptions()
        
        # Add options for cookie saving/loading
        if self.save_cookies or self.mode == 'auto':
            firefox_profile_dir = os.environ.get('FIREFOX_PROFILE_DIR')
            if firefox_profile_dir and os.path.exists(firefox_profile_dir):
                print(f"[*] Using Firefox profile from: {firefox_profile_dir}")
                # For Firefox, we need to create a profile
                from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
                profile = FirefoxProfile(firefox_profile_dir)
                options.profile = profile
        
        # Add common options
        options.set_preference('dom.webdriver.enabled', False)
        options.set_preference('useAutomationExtension', False)
        options.set_preference('devtools.jsonview.enabled', False)
        
        try:
            # Try to import webdriver_manager, install if not available
            try:
                from webdriver_manager.firefox import GeckoDriverManager
                print("[*] Setting up GeckoDriver automatically...")
                service = FirefoxService(GeckoDriverManager().install())
                driver = webdriver.Firefox(service=service, options=options)
            except ImportError:
                print("[*] webdriver-manager not available, trying direct Firefox driver...")
                driver = webdriver.Firefox(options=options)
            
            print("[*] Firefox driver initialized successfully")
            return driver
        except Exception as e:
            print(f"[error] Failed to initialize Firefox driver: {e}")
            
            # If we were trying Firefox as primary choice, try Chrome as fallback
            if self.browser_choice == 'firefox':
                print("[*] Attempting to fallback to Chrome...")
                self.browser_choice = 'chrome'
                return self.setup_chrome_driver()
            else:
                raise
    
    def setup_firefox_fallback(self):
        """Fallback to Firefox when Chrome fails"""
        print("[*] Setting up Firefox as fallback...")
        self.browser_choice = 'firefox'
        return self.setup_firefox_driver()
    
    def clean_filename(self, title):
        return re.sub(r'[\\/*?:"<>|]', "_", title)
    
    def login_and_scrape(self):
        self.driver.get("https://learninginmotion.uvic.ca/myAccount/co-op/postings.htm")
        
        if self.mode == 'manual':
            print("[*] Please log in manually (2FA if needed).")
            input("[*] Once job listings are visible, press ENTER to continue...")
        elif self.mode == 'auto':
            print("[*] Attempting automated login with saved cookies...")
            # Wait for page to load and check if we're logged in
            time.sleep(5)
            
            # Check if we're on the login page or job listings page
            current_url = self.driver.current_url
            if 'postings.htm' in current_url:
                # Check for job listings table
                try:
                    self.driver.find_element(By.CSS_SELECTOR, "table#postingsTable")
                    print("[*] Successfully logged in with saved cookies")
                except NoSuchElementException:
                    print("[error] Saved cookies may have expired or are invalid")
                    print("[*] Falling back to manual login...")
                    input("[*] Please log in manually, then press ENTER to continue...")
            else:
                print(f"[error] Not on the expected page. Current URL: {current_url}")
                print("[*] Falling back to manual login...")
                input("[*] Please log in manually, then press ENTER to continue...")
        
        os.makedirs("job_desc", exist_ok=True)
        
        print("[*] Extracting job listings...")
        time.sleep(2)
        rows = self.driver.find_elements(By.CSS_SELECTOR, "table#postingsTable tbody tr")
        jobs_data = []
        
        for index, row in enumerate(rows):
            if index > 0 and index % 10 == 0:  # pause every 10 jobs
                user_input = input("[*] Paused. Press ENTER to resume or type 'match' to proceed to matching...")
                if user_input == 'match':
                    break
            
            try:
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) < 10:
                    continue
                
                job_id = cols[2].text.strip()
                title_elem = row.find_element(By.CSS_SELECTOR, "a.np-view-btn-" + job_id)
                title = title_elem.text.strip()
                company = cols[4].text.strip()
                division = cols[5].text.strip()
                position_type = cols[6].text.strip()
                location = cols[7].text.strip()
                applied = cols[8].text.strip()
                deadline = cols[9].text.strip()
                
                jobs_data.append([job_id, title, company, division, position_type, location, applied, deadline])
                print(f"[*] {index+1}: {title}")
                
                # Let the site open the new tab
                original_tabs = self.driver.window_handles
                title_elem.click()
                
                WebDriverWait(self.driver, 10).until(
                    lambda d: len(d.window_handles) > len(original_tabs)
                )
                
                new_tab = [tab for tab in self.driver.window_handles if tab not in original_tabs][0]
                self.driver.switch_to.window(new_tab)
                time.sleep(3)
                
                try:
                    label_els = self.driver.find_elements(By.CSS_SELECTOR, "table.table-bordered td[style='width: 25%;']")
                    description = ""
                    qualifications = ""
                    
                    for label_el in label_els:
                        label_text = label_el.text.strip()
                        if "Job Description:" in label_text:
                            desc_td = label_el.find_element(By.XPATH, "following-sibling::td")
                            desc_span = desc_td.find_element(By.CSS_SELECTOR, "span[class^='np-view-question']")
                            description = desc_span.get_attribute("innerText").strip()
                        elif "Qualifications:" in label_text:
                            qual_td = label_el.find_element(By.XPATH, "following-sibling::td")
                            qual_span = qual_td.find_element(By.CSS_SELECTOR, "span[class^='np-view-question']")
                            qualifications = qual_span.get_attribute("innerText").strip()
                
                except NoSuchElementException:
                    pass  
                
                # Always apply fallbacks and format text
                if not description:
                    description = "Description not found."
                if not qualifications:
                    qualifications = "Qualifications not found."
                
                combined_text = f"--- Job Description ---\n{description}\n\n--- Qualifications ---\n{qualifications}"
                
                filename = self.clean_filename(title) + ".txt"
                with open(f"job_desc/{filename}", "w", encoding="utf-8") as f:
                    f.write(combined_text)
                
                self.driver.close()
                self.driver.switch_to.window(original_tabs[0])
            
            except (Exception, TimeoutException) as e:
                print(f"[error] Error on row {index+1}: {e}")
                continue
        
        with open("uvic_jobs.tsv", "w", encoding="utf-8") as f:
            f.write("JobID\tTitle\tCompany\tDivision\tPosition Type\tLocation\tApplied\tDeadline\n")
            for job in jobs_data:
                f.write("\t".join(job) + "\n")
        
        print(f"[*] Scraping complete. Saved {len(jobs_data)} jobs and descriptions.")
        
        # Save cookies if requested
        if self.save_cookies:
            print("[*] Cookies have been saved in the browser profile for future use.")
        
        self.driver.quit()


if __name__ == "__main__":
    scraper = UVicJobBoardScraper()
    scraper.login_and_scrape()
    
    if os.listdir("job_desc"):
        print("[*] Running matcher client...")
        subprocess.run(["python3", "match-client.py"])
    else:
        print("[*] No job descriptions found. Skipping matcher.")
