# player_scraper.py
import os
import time
import json
import random
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# Load credentials
load_dotenv()
SCRAPING_BROWSER_URL = (
    f"http://brd-customer-{os.getenv('BRIGHTDATA_CUSTOMER_ID')}"
    f"-zone-{os.getenv('BRIGHTDATA_ZONE')}:{os.getenv('BRIGHTDATA_PASSWORD')}@"
    f"{os.getenv('BRIGHTDATA_HOST')}:{os.getenv('BRIGHTDATA_PORT')}"
)

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def clean_text(text):
    return text.replace('\xa0', ' ').replace('\u2020', '').replace('\u2021', '').strip()


def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0")
    return webdriver.Remote(command_executor=SCRAPING_BROWSER_URL, options=options)


def get_match_links():
    url = "https://stats.espncricinfo.com/ci/engine/records/team/match_results.html?id=14450;type=tournament"
    driver = setup_driver()
    links = []
    try:
        driver.get(url)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.engineTable"))
        )
        soup = BeautifulSoup(driver.page_source, "html.parser")
        rows = soup.select("table.engineTable tr.data1")

        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 7:
                a_tag = cols[6].find("a")
                if a_tag and a_tag.get("href"):
                    full_link = "https://www.espncricinfo.com" + a_tag["href"]
                    links.append(full_link)

        return links
    finally:
        driver.quit()


def get_players_from_match(match_url):
    driver = setup_driver()
    players = []
    try:
        driver.get(match_url)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.ci-scorecard-table"))
        )
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Get team names
        match_info_divs = soup.find_all("div", class_="ds-text-tight-m")
        teams = [div.get_text(strip=True).replace(" Innings", "") for div in soup.select("span.ds-text-title-xs")]

        if len(teams) < 2:
            print("Failed to detect team names.")
            return []

        team1, team2 = teams[:2]

        # Batting tables
        scorecard_tables = soup.select("table.ci-scorecard-table")
        for idx, table in enumerate(scorecard_tables[:2]):
            team = team1 if idx == 0 else team2
            rows = table.select("tbody tr")
            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 8:
                    a_tag = cols[0].find("a")
                    if a_tag and a_tag.get("href"):
                        players.append({
                            "name": clean_text(a_tag.text),
                            "team": team,
                            "url": "https://www.espncricinfo.com" + a_tag["href"]
                        })

        # Bowling tables
        bowl_tables = soup.select("div > table.ds-table")
        for idx, table in enumerate([1, 3]):
            if len(bowl_tables) > table:
                team = team2 if idx == 0 else team1
                rows = bowl_tables[table].select("tbody tr")
                for row in rows:
                    cols = row.find_all("td")
                    if len(cols) >= 11:
                        a_tag = cols[0].find("a")
                        if a_tag and a_tag.get("href"):
                            players.append({
                                "name": clean_text(a_tag.text),
                                "team": team,
                                "url": "https://www.espncricinfo.com" + a_tag["href"]
                            })

        return players
    finally:
        driver.quit()


def get_player_profile(url):
    driver = setup_driver()
    try:
        driver.get(url)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.ds-grid"))
        )
        soup = BeautifulSoup(driver.page_source, "html.parser")

        def extract(label):
            divs = soup.select("div.ds-grid > div")
            for div in divs:
                p = div.find("p")
                if p and p.text.strip() == label:
                    span = div.find("span")
                    if span:
                        return clean_text(span.text)
            return None

        description_tag = soup.select_one("div.ci-player-bio-content > p")
        return {
            "battingStyle": extract("Batting Style"),
            "bowlingStyle": extract("Bowling Style"),
            "playingRole": extract("Playing Role"),
            "description": clean_text(description_tag.text) if description_tag else None
        }
    finally:
        driver.quit()


def main():
    print("Stage 1: Fetching match links...")
    match_links = get_match_links()
    print(f"Found {len(match_links)} matches.")

    all_players = []

    for i, match_url in enumerate(match_links[:3]):  # Limit to 3 matches for now
        print(f"\nStage 2: Fetching players from match {i+1}")
        players = get_players_from_match(match_url)
        print(f"Found {len(players)} players.")

        for player in players:
            print(f"Stage 3: Fetching profile for {player['name']}")
            profile = get_player_profile(player["url"])
            all_players.append({**player, **profile})

            # Save after every player
            with open(os.path.join(OUTPUT_DIR, "players_full_data.json"), "w", encoding="utf-8") as f:
                json.dump(all_players, f, indent=2, ensure_ascii=False)

            time.sleep(random.uniform(2, 5))  # polite delay

    print(f"\nCompleted: {len(all_players)} players collected.")


if __name__ == "__main__":
    main()
