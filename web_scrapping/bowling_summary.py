import requests
from bs4 import BeautifulSoup
import json
import os

def get_match_links():
    url = 'https://stats.espncricinfo.com/ci/engine/records/team/match_results.html?id=14450;type=tournament'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    links = []
    rows = soup.select('table.engineTable > tbody > tr.data1')
    
    for row in rows:
        link = row.find_all('td')[6].find('a')['href']
        links.append(f"https://www.espncricinfo.com{link}")
    
    return links

def scrape_bowling_summary(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    match_div = soup.find('div', string=lambda text: text and "Match Details" in text)
    team1 = match_div.find_next_sibling().find('span').get_text(strip=True).replace(" Innings", "")
    team2 = match_div.find_next_sibling().find_next_sibling().find('span').get_text(strip=True).replace(" Innings", "")
    match_info = f"{team1} Vs {team2}"
    
    bowling_summary = []
    tables = soup.select('div > table.ds-table')
    
    # First innings (team2 bowling)
    first_innings_rows = tables[1].select('tbody > tr')
    for row in first_innings_rows:
        if len(row.find_all('td')) >= 11:
            tds = row.find_all('td')
            bowling_summary.append({
                'match': match_info,
                'bowlingTeam': team2,
                'bowlerName': tds[0].find('a').get_text(strip=True).replace('\xa0', ''),
                'overs': tds[1].get_text(strip=True),
                'maiden': tds[2].get_text(strip=True),
                'runs': tds[3].get_text(strip=True),
                'wickets': tds[4].get_text(strip=True),
                'economy': tds[5].get_text(strip=True),
                '0s': tds[6].get_text(strip=True),
                '4s': tds[7].get_text(strip=True),
                '6s': tds[8].get_text(strip=True),
                'wides': tds[9].get_text(strip=True),
                'noBalls': tds[10].get_text(strip=True)
            })
    
    # Second innings (team1 bowling)
    second_innings_rows = tables[3].select('tbody > tr')
    for row in second_innings_rows:
        if len(row.find_all('td')) >= 11:
            tds = row.find_all('td')
            bowling_summary.append({
                'match': match_info,
                'bowlingTeam': team1,
                'bowlerName': tds[0].find('a').get_text(strip=True).replace('\xa0', ''),
                'overs': tds[1].get_text(strip=True),
                'maiden': tds[2].get_text(strip=True),
                'runs': tds[3].get_text(strip=True),
                'wickets': tds[4].get_text(strip=True),
                'economy': tds[5].get_text(strip=True),
                '0s': tds[6].get_text(strip=True),
                '4s': tds[7].get_text(strip=True),
                '6s': tds[8].get_text(strip=True),
                'wides': tds[9].get_text(strip=True),
                'noBalls': tds[10].get_text(strip=True)
            })
    
    return bowling_summary

if __name__ == '__main__':
    os.makedirs('output', exist_ok=True)
    all_bowling_summaries = []
    
    match_links = get_match_links()
    for link in match_links:
        summary = scrape_bowling_summary(link)
        all_bowling_summaries.extend(summary)
    
    with open('output/bowling_summary.json', 'w') as f:
        json.dump({'bowlingSummary': all_bowling_summaries}, f, indent=4)
    
    print("Data saved to output/bowling_summary.json")