'''
job_scrape.py

Brian Nguyen 
9-07-2025

Scrapes LIM for coop job. Saves all jobs to uvic_jobs.tsv, and matches using match-client.py
note: need to start the server to accept post API endpoint
'''

import os
import time
import re
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class UVicJobBoardScraper:
    def __init__(self):
        self.driver = webdriver.Chrome()

    def clean_filename(self, title):
        return re.sub(r'[\\/*?:"<>|]', "_", title)

    def login_and_scrape(self):
        self.driver.get("https://learninginmotion.uvic.ca/myAccount/co-op/postings.htm")
        print("🔐 Please log in manually (2FA if needed).")
        input("✅ Once job listings are visible, press ENTER to continue...")

        os.makedirs("job_desc", exist_ok=True)

        print("📥 Extracting job listings...")
        time.sleep(2)
        rows = self.driver.find_elements(By.CSS_SELECTOR, "table#postingsTable tbody tr")
        jobs_data = []

        for index, row in enumerate(rows):

            if index > 0 and index % 10 == 0:  # pause every 5 jobs
                user_input = input("⏸️ Paused. Press ENTER to resume or type 'match' to proceed to matching...")
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
                print(f"✅ {index+1}: {title}")

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
                print(f"⚠️ Error on row {index+1}: {e}")
                continue

        with open("uvic_jobs.tsv", "w", encoding="utf-8") as f:
            f.write("JobID\tTitle\tCompany\tDivision\tPosition Type\tLocation\tApplied\tDeadline\n")
            for job in jobs_data:
                f.write("\t".join(job) + "\n")

        print(f"✅ Scraping complete. Saved {len(jobs_data)} jobs and descriptions.")
        self.driver.quit()


if __name__ == "__main__":
    scraper = UVicJobBoardScraper()
    scraper.login_and_scrape()

    if os.listdir("job_desc"):
        print("📤 Running matcher client...")
        subprocess.run(["python3", "match-client.py"])
    else:
        print("⚠️ No job descriptions found. Skipping matcher.")

