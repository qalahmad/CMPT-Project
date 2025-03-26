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

def scrape_batting_summary(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    match_div = soup.find('div', string=lambda text: text and "Match Details" in text)
    team1 = match_div.find_next_sibling().find('span').get_text(strip=True).replace(" Innings", "")
    team2 = match_div.find_next_sibling().find_next_sibling().find('span').get_text(strip=True).replace(" Innings", "")
    match_info = f"{team1} Vs {team2}"
    
    batting_summary = []
    tables = soup.select('div > table.ci-scorecard-table')
    
    # First innings
    first_innings_rows = tables[0].select('tbody > tr')
    for i, row in enumerate(first_innings_rows):
        if len(row.find_all('td')) >= 8:
            tds = row.find_all('td')
            batting_summary.append({
                'match': match_info,
                'teamInnings': team1,
                'battingPos': i+1,
                'batsmanName': tds[0].find('a').get_text(strip=True).replace('\xa0', ''),
                'dismissal': tds[1].get_text(strip=True),
                'runs': tds[2].find('strong').get_text(strip=True) if tds[2].find('strong') else tds[2].get_text(strip=True),
                'balls': tds[3].get_text(strip=True),
                '4s': tds[5].get_text(strip=True),
                '6s': tds[6].get_text(strip=True),
                'SR': tds[7].get_text(strip=True)
            })
    
    # Second innings
    second_innings_rows = tables[1].select('tbody > tr')
    for i, row in enumerate(second_innings_rows):
        if len(row.find_all('td')) >= 8:
            tds = row.find_all('td')
            batting_summary.append({
                'match': match_info,
                'teamInnings': team2,
                'battingPos': i+1,
                'batsmanName': tds[0].find('a').get_text(strip=True).replace('\xa0', ''),
                'dismissal': tds[1].get_text(strip=True),
                'runs': tds[2].find('strong').get_text(strip=True) if tds[2].find('strong') else tds[2].get_text(strip=True),
                'balls': tds[3].get_text(strip=True),
                '4s': tds[5].get_text(strip=True),
                '6s': tds[6].get_text(strip=True),
                'SR': tds[7].get_text(strip=True)
            })
    
    return batting_summary

if __name__ == '__main__':
    os.makedirs('output', exist_ok=True)
    all_batting_summaries = []
    
    match_links = get_match_links()
    for link in match_links:
        summary = scrape_batting_summary(link)
        all_batting_summaries.extend(summary)
    
    with open('output/batting_summary.json', 'w') as f:
        json.dump({'battingSummary': all_batting_summaries}, f, indent=4)
    
    print("Data saved to output/batting_summary.json")