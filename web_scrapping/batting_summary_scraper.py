# batting_summary_scraper.py
import json
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import random
import urllib.parse
import sys
import locale

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

def clean_text(text):
    """Clean special characters from text"""
    if not isinstance(text, str):
        return text
    return text.replace('\u2020', '').replace('\u2021', '').strip()

def get_match_links():
    """Stage 1: Get all match summary links from the results page"""
    print("Initializing browser for match links...")
    
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    try:
        driver = webdriver.Remote(
            command_executor=SCRAPING_BROWSER_URL,
            options=options
        )
        
        url = "https://stats.espncricinfo.com/ci/engine/records/team/match_results.html?id=14450;type=tournament"
        print(f"Accessing URL: {url}")
        driver.get(url)
        
        # Wait for table to load
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table.wicketTable"))
            )
            print("Main table loaded successfully")
        except:
            print("Table loading timeout, attempting to continue...")
        #   driver.save_screenshot(os.path.join(OUTPUT_DIR, 'debug_table_not_found.png'))
        
        # Additional loading time
        time.sleep(5)
        
        # Get page source
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        # Save page source for debugging
        # with open(os.path.join(OUTPUT_DIR, 'debug_page.html'), 'w', encoding='utf-8') as f:
        #     f.write(html)
        
        links = []
        
        # Find the main table
        main_table = soup.find('table', {'class': 'wicketTable'})
        if not main_table:
            main_table = soup.find('table')
        
        if main_table:
            rows = main_table.find_all('tr')
            print(f"Found {len(rows)} data rows")
            
            for row in rows[1:]:  # Skip header
                cols = row.find_all('td')
                if len(cols) >= 7:  # Ensure enough columns
                    scorecard = cols[6].find('a')
                    if scorecard and scorecard.has_attr('href'):
                        link = "https://www.espncricinfo.com" + scorecard['href']
                        links.append(link)
                        print(f"Found match link: {link}")
        else:
            print("Error: No tables found")
        #    driver.save_screenshot(os.path.join(OUTPUT_DIR, 'debug_no_table_found.png'))
        
        return links
        
    except Exception as e:
        print(f"Error getting match links: {str(e)}")
        if 'driver' in locals():
            driver.save_screenshot(os.path.join(OUTPUT_DIR, 'debug_error.png'))
        return []
    finally:
        if 'driver' in locals():
            driver.quit()

def scrape_batting_summary(url):
    """Stage 2: Scrape batting summary from a match page"""
    print(f"\nProcessing match: {url}")
    
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    driver = webdriver.Remote(
        command_executor=SCRAPING_BROWSER_URL,
        options=options
    )
    
    try:
        driver.get(url)
        
        # Wait for scorecard to load
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.ci-scorecard-table"))
        )
        
        time.sleep(3)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        batting_summary = []
        
        # Get match info
        teams = soup.find_all('span', class_='ds-text-title-xs')
        if len(teams) >= 2:
            team1 = clean_text(teams[0].get_text(strip=True)).replace(" Innings", "")
            team2 = clean_text(teams[1].get_text(strip=True)).replace(" Innings", "")
            match_info = f"{team1} vs {team2}"
            print(f"Match: {match_info}")
            
            # Process batting tables
            tables = soup.select('table.ci-scorecard-table')
            
            for i, table in enumerate(tables[:2]):  # Only first two innings
                innings = team1 if i == 0 else team2
                rows = table.select('tbody tr')
                
                for j, row in enumerate(rows):
                    cols = row.find_all('td')
                    if len(cols) >= 8:
                        batsman = {
                            "match": match_info,
                            "teamInnings": innings,
                            "battingPos": j+1,
                            "batsmanName": clean_text(cols[0].get_text(strip=True)),
                            "dismissal": clean_text(cols[1].get_text(strip=True)),
                            "runs": clean_text(cols[2].get_text(strip=True)),
                            "balls": clean_text(cols[3].get_text(strip=True)),
                            "4s": clean_text(cols[5].get_text(strip=True)),
                            "6s": clean_text(cols[6].get_text(strip=True)),
                            "SR": clean_text(cols[7].get_text(strip=True))
                        }
                        batting_summary.append(batsman)
                        print(f"Added batsman: {batsman['batsmanName']}")
        
        return batting_summary
        
    except Exception as e:
        print(f"Error processing match: {str(e)}")
        driver.save_screenshot(os.path.join(OUTPUT_DIR, f'debug_match_{url.split("/")[-1]}.png'))
        return []
    finally:
        driver.quit()

def main():
    """Main execution function"""
    # Stage 1: Get match links
    print("=== Stage 1: Fetching Match Links ===")
    match_links = get_match_links()
    print(f"\nFound {len(match_links)} match links")
    
    if not match_links:
        print("Error: No match links found. Please check:")
        print("1. Network connection and proxy settings")
        print("2. Debug files in output directory")
        print("3. If page structure has changed")
        return
    
    # Save links for reference
    with open(os.path.join(OUTPUT_DIR, 'match_links.json'), 'w', encoding='utf-8') as f:
        json.dump(match_links, f, indent=2)
    
    # Stage 2: Scrape batting data
    print("\n=== Stage 2: Scraping Batting Data ===")
    all_batting = []
    
    for i, link in enumerate(match_links[:5]):  # Process first 5 matches for testing
        print(f"\nProcessing match {i+1}/{len(match_links)}: {link}")
        batting_data = scrape_batting_summary(link)
        
        if batting_data:
            all_batting.extend(batting_data)
            print(f"Added {len(batting_data)} batting records")
        
        # Save progress
        try:
            with open(os.path.join(OUTPUT_DIR, 'batting_summary.json'), 'w', encoding='utf-8') as f:
                json.dump(all_batting, f, indent=2, ensure_ascii=False)
        except UnicodeEncodeError:
            print("UTF-8 encoding failed, trying ASCII fallback...", file=sys.stderr)
            with open(os.path.join(OUTPUT_DIR, 'batting_summary_ascii.json'), 'w', encoding='utf-8') as f:
                json.dump(all_batting, f, indent=2)
        
        # Random delay between requests
        delay = random.uniform(5, 15)
        print(f"Waiting {delay:.1f} seconds...")
        time.sleep(delay)
    
    print(f"\nCompleted! Collected {len(all_batting)} batting records in total")

if __name__ == '__main__':
    print(f"System default encoding: {locale.getpreferredencoding()}")
    main()