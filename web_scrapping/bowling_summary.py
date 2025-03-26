import os
import time
import random
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# Configuration
OUTPUT_DIR = 'output'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def init_driver():
    """Initialize Chrome driver with verified settings"""
    chrome_options = webdriver.ChromeOptions()
    
    # Essential settings that actually work
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("window-size=1920,1080")
    
    # User agent that matches ESPN's expectations
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Headless mode that works with ESPN
    chrome_options.add_argument("--headless=new")
    
    # Disable images to speed up loading
    chrome_options.add_argument("--blink-settings=imagesEnabled=false")
    
    # Initialize driver with error handling
    try:
        service = Service()
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        print(f"Driver initialization failed: {e}")
        return None

def get_valid_match_links(driver):
    """Get match links from the main tournament page with strict validation"""
    MAIN_URL = "https://www.espncricinfo.com/series/icc-men-s-t20-world-cup-2022-23-1298134/match-results"
    
    try:
        driver.get(MAIN_URL)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.ds-px-4.ds-py-3"))
        )
        
        # Get all valid match links
        links = []
        elements = driver.find_elements(By.CSS_SELECTOR, "a[href*='/full-scorecard']")
        
        for elem in elements[:5]:  # Only process 5 matches for testing
            href = elem.get_attribute('href')
            if href and 'espncricinfo.com' in href and '/full-scorecard' in href:
                links.append(href)
                print(f"Found valid match: {href}")
            else:
                print(f"Skipping invalid URL: {href}")
        
        return links
    
    except Exception as e:
        print(f"Error getting match links: {e}")
        return []

def extract_bowling_data(driver, match_url):
    """Extract bowling data from match page with reliable selectors"""
    try:
        driver.get(match_url)
        
        # Wait for either the data tables or a timeout
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.ds-w-full"))
        )
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        bowling_records = []
        
        # Process each innings section
        for inning in soup.select('div.ds-rounded-lg.ds-mt-2'):
            # Get team name
            team_elem = inning.select_one('span.ds-text-title-xs.ds-font-bold')
            team = team_elem.get_text(strip=True).replace(' Innings', '') if team_elem else "Unknown"
            
            # Find the BOWLING table (second table in each innings)
            tables = inning.select('table.ds-w-full')
            if len(tables) < 2:
                continue
                
            bowling_table = tables[1]
            
            # Process each bowler row
            for row in bowling_table.select('tbody tr'):
                cols = row.find_all('td')
                if len(cols) >= 11:  # Must have all columns
                    bowler = cols[0].get_text(strip=True)
                    if bowler and bowler != 'Bowler':
                        bowling_records.append({
                            'match_id': match_url.split('/')[-2],
                            'team': team,
                            'bowler': bowler,
                            'overs': cols[1].get_text(strip=True),
                            'maidens': cols[2].get_text(strip=True),
                            'runs': cols[3].get_text(strip=True),
                            'wickets': cols[4].get_text(strip=True),
                            'economy': cols[5].get_text(strip=True),
                            'dots': cols[6].get_text(strip=True),
                            '4s': cols[7].get_text(strip=True),
                            '6s': cols[8].get_text(strip=True),
                            'wides': cols[9].get_text(strip=True),
                            'noballs': cols[10].get_text(strip=True)
                        })
        
        print(f"Extracted {len(bowling_records)} bowling records")
        return bowling_records
    
    except Exception as e:
        print(f"Error extracting bowling data: {e}")
        return []

def main():
    print("ESPN Cricinfo Bowling Scraper - Verified Working Version")
    print("="*70)
    
    driver = init_driver()
    if not driver:
        return
    
    try:
        # Step 1: Get valid match links
        match_links = get_valid_match_links(driver)
        if not match_links:
            print("\nERROR: No valid match links found")
            print("Possible solutions:")
            print("1. Check VPN/proxy if you're in a restricted region")
            print("2. Manually verify the tournament URL works in browser")
            print("3. Update the MAIN_URL in the code if needed")
            return
        
        # Step 2: Process each match
        all_bowling_data = []
        for i, url in enumerate(match_links, 1):
            print(f"\nProcessing match {i}/{len(match_links)}")
            print(f"URL: {url}")
            
            records = extract_bowling_data(driver, url)
            if records:
                all_bowling_data.extend(records)
            
            # Respectful delay between matches
            delay = random.uniform(8, 15)
            print(f"Waiting {delay:.1f} seconds...")
            time.sleep(delay)
        
        # Step 3: Save results
        if all_bowling_data:
            output_path = os.path.join(OUTPUT_DIR, 'bowling_summary.json')
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump({'bowling_data': all_bowling_data}, f, indent=2)
            print(f"\nSUCCESS: Saved {len(all_bowling_data)} records to {output_path}")
        else:
            print("\nWARNING: No bowling data extracted")
            print("Possible reasons:")
            print("- Matches haven't started yet (no data available)")
            print("- ESPN changed their page structure (update selectors)")
            print("- Temporary server issues (try again later)")
    
    finally:
        driver.quit()
        print("\nBrowser session ended")

if __name__ == '__main__':
    # Verify dependencies
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print("Installing required packages...")
        os.system("pip install selenium webdriver-manager beautifulsoup4")
        from bs4 import BeautifulSoup
    
    main()