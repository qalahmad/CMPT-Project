import requests
from bs4 import BeautifulSoup
import json
import os

def scrape_match_results():
    url = 'https://stats.espncricinfo.com/ci/engine/records/team/match_results.html?id=14450;type=tournament'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    match_summary = []
    rows = soup.select('table.engineTable > tbody > tr.data1')
    
    for row in rows:
        tds = row.find_all('td')
        match_summary.append({
            'team1': tds[0].get_text(strip=True),
            'team2': tds[1].get_text(strip=True),
            'winner': tds[2].get_text(strip=True),
            'margin': tds[3].get_text(strip=True),
            'ground': tds[4].get_text(strip=True),
            'matchDate': tds[5].get_text(strip=True),
            'scorecard': tds[6].get_text(strip=True)
        })
    
    # Save to JSON
    os.makedirs('output', exist_ok=True)
    with open('output/match_results.json', 'w') as f:
        json.dump({'matchSummary': match_summary}, f, indent=4)
    
    return {'matchSummary': match_summary}

if __name__ == '__main__':
    results = scrape_match_results()
    print("Data saved to output/match_results.json")