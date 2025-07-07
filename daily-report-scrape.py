import argparse
import time
from selenium import webdriver
from selenium.webdriver.common.by import By


class SlackScraper:
    def __init__(self, url: str):
        self.url = url
        self.driver = webdriver.Chrome()

    def login_and_scrape(self):
        print("🔑 Opening Slack login...")
        self.driver.get("https://slack.com/signin")

        print("➡️ Please log in manually.")
        input("✅ After login, press ENTER to continue to the target channel...")

        print(f"🔗 Navigating to: {self.url}")
        self.driver.get(self.url)
        input("🧭 Press ENTER once the channel has fully loaded...")

        print("🔄 Scrolling to load more messages...")
        for _ in range(10):  # Adjust scroll depth
            self.driver.execute_script("""
                const el = document.querySelector('[data-qa="slack_kit_scrollbar"]');
                if (el) el.scrollTop = 0;
            """)
            time.sleep(1.5)

        print("📥 Extracting messages...")
        list_items = self.driver.find_elements(By.CSS_SELECTOR, "div[role='listitem']")
        report_messages = []

        for item in list_items:
            label = item.get_attribute("aria-label") or ""
            if "daily report" in label.lower():
                report_messages.append(item.text.strip())

        print(f"✅ Found {len(report_messages)} messages.")
        with open("slack_reports.txt", "w", encoding="utf-8") as f:
            for i, msg in enumerate(report_messages):
                print(f"{i+1}: {msg}")
                f.write(msg + "\n\n")

        self.driver.quit()


def main():
    parser = argparse.ArgumentParser(description="Scrape messages from a Slack private channel.")
    parser.add_argument("url", help="URL to the Slack private channel or DM")
    args = parser.parse_args()

    scraper = SlackScraper(args.url)
    scraper.login_and_scrape()


if __name__ == "__main__":
    main()
