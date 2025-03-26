import os
import time
import random
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup

# Configuration
OUTPUT_DIR = 'output'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def init_driver():
    """Initialize Chrome driver with anti-detection settings"""
    chrome_options = webdriver.ChromeOptions()
    
    # Anti-bot measures
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Random user agents
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
    ]
    chrome_options.add_argument(f"user-agent={random.choice(user_agents)}")
    
    # Headless mode
    chrome_options.add_argument("--headless=new")
    
    # Automatic ChromeDriver management
    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Remove automation flags
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def human_like_interaction(driver):
    """Simulate human-like interactions"""
    try:
        # Random scrolling
        for _ in range(random.randint(2, 5)):
            scroll_height = random.randint(200, 800)
            driver.execute_script(f"window.scrollBy(0, {scroll_height})")
            time.sleep(random.uniform(0.5, 2))
        
        # Random mouse movements
        actions = ActionChains(driver)
        for _ in range(random.randint(3, 7)):
            x_offset = random.randint(-50, 50)
            y_offset = random.randint(-50, 50)
            actions.move_by_offset(x_offset, y_offset).perform()
            time.sleep(random.uniform(0.2, 0.7))
    except Exception:
        pass

def get_match_links(driver):
    """Extract match links from tournament page"""
    BASE_URL = "https://www.espncricinfo.com/series/icc-men-s-t20-world-cup-2022-23-1298134/match-results"
    
    print(f"\nAccessing: {BASE_URL}")
    try:
        driver.get(BASE_URL)
        
        # Wait for page load
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='ds-mb-4']"))
        )
        
        # Human-like behavior
        human_like_interaction(driver)
        
        # Get all match cards
        match_cards = driver.find_elements(By.CSS_SELECTOR, "a[href*='/full-scorecard']")
        
        links = []
        for card in match_cards[:5]:  # Limit to 5 matches for testing
            match_url = card.get_attribute('href')
            if match_url and 'full-scorecard' in match_url:
                links.append(match_url)
                print(f"Found match: {card.text.strip() or 'No title'} | {match_url}")
        
        return links
    
    except TimeoutException:
        print("Error: Page load timeout")
        return []
    except Exception as e:
        print(f"Error getting match links: {e}")
        return []

def scrape_batting_data(driver, match_url):
    """Scrape batting data from match page"""
    print(f"\nProcessing: {match_url}")
    try:
        driver.get(match_url)
        
        # Wait for data tables
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.ci-scorecard-table"))
        )
        
        # Human-like behavior
        human_like_interaction(driver)
        
        # Parse HTML
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        batting_records = []
        
        # Process each innings
        for inning in soup.select('div[class*="ds-mb-4"]'):
            # Get team name
            team_name = inning.select_one('span.ds-text-title-xs.ds-font-bold')
            team = team_name.get_text(strip=True) if team_name else "Unknown Team"
            
            # Locate batting table
            batting_table = inning.select_one('table.ci-scorecard-table')
            if not batting_table:
                continue
                
            # Process each batsman row
            for row in batting_table.select('tbody tr'):
                cols = row.find_all('td')
                if len(cols) < 8:  # Skip incomplete rows
                    continue
                    
                batsman = cols[0].get_text(strip=True)
                # Skip special rows
                if not batsman or 'Extras' in batsman or 'TOTAL' in batsman:
                    continue
                    
                # Extract batting data
                batting_records.append({
                    'match_id': match_url.split('/')[-1],
                    'team': team.replace(' Innings', ''),
                    'batsman': batsman,
                    'runs': cols[2].get_text(strip=True),
                    'balls': cols[3].get_text(strip=True),
                    'fours': cols[5].get_text(strip=True),
                    'sixes': cols[6].get_text(strip=True),
                    'strike_rate': cols[7].get_text(strip=True)
                })
        
        print(f"Extracted {len(batting_records)} batting records")
        return batting_records
    
    except TimeoutException:
        print("Error: Data table load timeout")
        return []
    except Exception as e:
        print(f"Error scraping batting data: {e}")
        return []

def save_to_json(data, filename):
    """Save data to JSON file"""
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Data saved to {path}")

def main():
    print("="*50)
    print("ESPN Cricinfo Batting Data Scraper v4.0")
    print("="*50)
    
    driver = None
    try:
        # Initialize browser
        driver = init_driver()
        
        # Step 1: Get match links
        match_links = get_match_links(driver)
        if not match_links:
            print("\nError: No match links found")
            return
        
        # Step 2: Scrape batting data
        all_batting_data = []
        for i, link in enumerate(match_links, 1):
            print(f"\nProgress: {i}/{len(match_links)}")
            if batting_data := scrape_batting_data(driver, link):
                all_batting_data.extend(batting_data)
            
            # Randomized delay
            delay = random.uniform(8, 15)
            print(f"Waiting {delay:.1f} seconds...")
            time.sleep(delay)
        
        # Step 3: Save results
        if all_batting_data:
            save_to_json({'batting_records': all_batting_data}, 'batting_summary.json')
            print(f"\nSuccess: Collected {len(all_batting_data)} batting records")
        else:
            print("\nWarning: Found matches but no batting data")
    
    except Exception as e:
        print(f"\nMain program error: {e}")
    finally:
        if driver:
            driver.quit()
            print("Browser closed")

if __name__ == '__main__':
    # Ensure BeautifulSoup is available
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print("Installing BeautifulSoup...")
        os.system("pip install beautifulsoup4")
        from bs4 import BeautifulSoup
    
    main()