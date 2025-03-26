import requests
from bs4 import BeautifulSoup
import json
import time
import random
import os
from fake_useragent import UserAgent

# Initialize random user agent generator
ua = UserAgent()

def get_headers():
    """Generate random headers for each request"""
    return {
        'User-Agent': ua.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.google.com/',
        'DNT': '1',
        'Connection': 'keep-alive'
    }

def scrape_match_results():
    """Scrape match results with anti-blocking measures"""
    url = 'https://www.espncricinfo.com/records/tournament/team-match-results/icc-men-s-t20-world-cup-2022-23-14450'
    
    try:
        # Random delay + headers
        time.sleep(random.uniform(2, 5))
        response = requests.get(
            url,
            headers=get_headers(),
            timeout=15,
            cookies={'cookie_consent': 'true'}  # Bypass cookie wall if needed
        )
        
        # Check for Cloudflare/WAF challenges
        if response.status_code == 403 or "Access Denied" in response.text:
            raise Exception("Blocked by WAF - Try proxies or selenium")
        
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Updated CSS selector (verify in browser DevTools)
        rows = soup.select('table.ds-table tbody tr')
        
        if not rows:
            print("Debug: Page HTML Structure:")
            print(soup.prettify()[:2000])  # Print first 2000 chars for analysis
            raise Exception("Table rows not found - Selector may need update")
        
        matches = []
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 7:
                matches.append({
                    'team1': cols[0].get_text(strip=True),
                    'team2': cols[1].get_text(strip=True),
                    'winner': cols[2].get_text(strip=True),
                    'margin': cols[3].get_text(strip=True),
                    'ground': cols[4].get_text(strip=True),
                    'date': cols[5].get_text(strip=True),
                    'scorecard': cols[6].find('a')['href'] if cols[6].find('a') else None
                })
        
        return {'matches': matches}
    
    except Exception as e:
        print(f"SCRAPING FAILED: {str(e)}")
        return {'error': str(e)}

def save_data(data):
    """Save data with timestamp for debugging"""
    os.makedirs('output', exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"output/matches_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Data saved to {filename}")
    return filename

if __name__ == '__main__':
    print("Starting enhanced scraper...")
    
    # First try with basic requests
    data = scrape_match_results()
    
    if 'error' in data:
        print("\nFALLBACK: Trying with Selenium...")
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            
            options = Options()
            options.add_argument(f"user-agent={ua.random}")
            options.add_argument("--headless")  # Run in background
            
            driver = webdriver.Chrome(options=options)
            driver.get(url)
            time.sleep(5)  # Wait for JavaScript
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            rows = soup.select('table.ds-table tbody tr')
            # ... (same extraction logic as above)
            
            driver.quit()
        except Exception as e:
            print(f"Selenium also failed: {e}")
    
    save_data(data)
    print("Process completed. Check output folder.")