# match_results_scraper.py
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import time
import random

# Configuration
OUTPUT_DIR = 'output'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Bright Data Scraping Browser credentials
load_dotenv()
SCRAPING_BROWSER_URL = (
    f"http://brd-customer-{os.getenv('BRIGHTDATA_CUSTOMER_ID')}"
    f"-zone-{os.getenv('BRIGHTDATA_ZONE')}:"
    f"{os.getenv('BRIGHTDATA_PASSWORD')}@"
    f"{os.getenv('BRIGHTDATA_HOST')}:"
    f"{os.getenv('BRIGHTDATA_PORT')}"
)

def scrape_match_results():
    """Fixed version of match results scraper"""
    print("Initializing browser...")
    
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    # Add random user agent to help avoid detection
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    driver = webdriver.Remote(
        command_executor=SCRAPING_BROWSER_URL,
        options=options
    )
    
    try:
        # Access target page
        url = "https://stats.espncricinfo.com/ci/engine/records/team/match_results.html?id=14450;type=tournament"
        print(f"Accessing: {url}")
        driver.get(url)
        
        # More generic wait condition
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table tbody tr"))
        )
        
        # Add random delay to mimic human behavior
        time.sleep(random.uniform(2, 5))
        
        # Parse page
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        matches = []
        
        # Fixed selector - get all data rows (skip header)
        rows = soup.select('table tbody tr')
        print(f"Found {len(rows)} rows")
        
        for row in rows[1:]:  # skip
            cols = row.find_all('td')
            if len(cols) >= 7:
                matches.append({
                    'team1': cols[0].get_text(strip=True),
                    'team2': cols[1].get_text(strip=True),
                    'winner': cols[2].get_text(strip=True),
                    'margin': cols[3].get_text(strip=True),
                    'ground': cols[4].get_text(strip=True),
                    'matchDate': cols[5].get_text(strip=True),
                    'scorecard': cols[6].get_text(strip=True)
                })
        
        # save results
        output_file = os.path.join(OUTPUT_DIR, 'match_results.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({'matches': matches}, f, indent=2, ensure_ascii=False)
        
        print(f"Success! Saved {len(matches)} matches to {output_file}")
        
        return matches
        
    except Exception as e:
        print(f"Error: {str(e)}")
        driver.save_screenshot(os.path.join(OUTPUT_DIR, 'debug_fixed.png'))
        return []
    finally:
        driver.quit()

if __name__ == '__main__':
    scrape_match_results()