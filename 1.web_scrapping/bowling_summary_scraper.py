# complete_bowling_scraper.py
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

# Configuration
OUTPUT_DIR = 'output'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Bright Data credentials
load_dotenv()
SCRAPING_BROWSER_URL = (
    f"http://brd-customer-{os.getenv('BRIGHTDATA_CUSTOMER_ID')}"
    f"-zone-{os.getenv('BRIGHTDATA_ZONE')}:"
    f"{os.getenv('BRIGHTDATA_PASSWORD')}@"
    f"{os.getenv('BRIGHTDATA_HOST')}:"
    f"{os.getenv('BRIGHTDATA_PORT')}"
)

def get_driver():
    """Initialize and return a WebDriver instance"""
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    return webdriver.Remote(command_executor=SCRAPING_BROWSER_URL, options=options)

def get_match_links():
    """Collect all match scorecard links from the tournament page"""
    print("Fetching match links...")
    driver = get_driver()
    
    try:
        url = "https://stats.espncricinfo.com/ci/engine/records/team/match_results.html?id=14450;type=tournament"
        driver.get(url)
        
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Match results')]"))
        )
        time.sleep(3)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        links = []
        
        # Find all scorecard links
        for row in soup.select('tr.data1, tr.data2'):
            link_tag = row.select_one('td:nth-child(7) a')
            if link_tag and 'scorecard' in link_tag['href']:
                link = "https://www.espncricinfo.com" + link_tag['href']
                links.append(link)
        
        # Fallback if standard method fails
        if not links:
            for table in soup.find_all('table'):
                for row in table.find_all('tr'):
                    cols = row.find_all('td')
                    if len(cols) > 6:
                        link_tag = cols[6].find('a')
                        if link_tag and 'scorecard' in link_tag['href']:
                            link = "https://www.espncricinfo.com" + link_tag['href']
                            links.append(link)
        
        return links
        
    finally:
        driver.quit()

def scrape_bowling_data(url):
    """Scrape bowling data from a single match page"""
    print(f"Processing: {url}")
    driver = get_driver()
    
    try:
        driver.get(url)
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.ds-table"))
        )
        time.sleep(2)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        match_data = []
        
        # Get match info
        teams = [span.get_text(strip=True).replace(" Innings", "") 
                for span in soup.select('span.ds-text-title-xs')[:2]]
        if len(teams) != 2:
            return []
        
        match_info = f"{teams[0]} vs {teams[1]}"
        
        # Process bowling tables (2nd and 4th tables)
        tables = soup.select('table.ds-table')
        for inning, table_idx in enumerate([1, 3]):  # 2nd and 4th tables contain bowling data
            if table_idx >= len(tables):
                continue
                
            for row in tables[table_idx].select('tbody tr'):
                cols = row.find_all('td')
                if len(cols) >= 11:
                    match_data.append({
                        "match": match_info,
                        "bowlingTeam": teams[1 - inning],  # 0=team2 bowls first, 1=team1 bowls second
                        "bowlerName": cols[0].get_text(strip=True),
                        "overs": cols[1].get_text(strip=True),
                        "maiden": cols[2].get_text(strip=True),
                        "runs": cols[3].get_text(strip=True),
                        "wickets": cols[4].get_text(strip=True),
                        "economy": cols[5].get_text(strip=True),
                        "0s": cols[6].get_text(strip=True),
                        "4s": cols[7].get_text(strip=True),
                        "6s": cols[8].get_text(strip=True),
                        "wides": cols[9].get_text(strip=True),
                        "noBalls": cols[10].get_text(strip=True),
                        "matchURL": url
                    })
        
        return match_data
        
    except Exception as e:
        print(f"Error processing {url}: {str(e)}")
        return []
    finally:
        driver.quit()

def main():
    """Main execution function"""
    # Get all match links
    match_links = get_match_links()
    print(f"\nFound {len(match_links)} match links")
    
    if not match_links:
        print("No matches found. Exiting.")
        return
    
    # Process matches and collect data
    all_bowling_data = []
    
    for i, link in enumerate(match_links, 1):
        print(f"\nProcessing match {i}/{len(match_links)}")
        bowling_data = scrape_bowling_data(link)
        
        if bowling_data:
            all_bowling_data.extend(bowling_data)
            print(f"Added {len(bowling_data)} bowling records")
        
        # Save progress after every 5 matches
        if i % 5 == 0 or i == len(match_links):
            output_file = os.path.join(OUTPUT_DIR, 'bowling_data.json')
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(all_bowling_data, f, indent=2, ensure_ascii=False)
            print(f"Saved progress ({len(all_bowling_data)} total records)")
        
        # Random delay between requests
        time.sleep(random.uniform(3, 8))
    
    print(f"\nCompleted! Final data saved to {output_file}")
    print(f"Total bowling records collected: {len(all_bowling_data)}")

if __name__ == '__main__':
    main()