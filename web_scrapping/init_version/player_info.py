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

def get_players_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    match_div = soup.find('div', string=lambda text: text and "Match Details" in text)
    team1 = match_div.find_next_sibling().find('span').get_text(strip=True).replace(" Innings", "")
    team2 = match_div.find_next_sibling().find_next_sibling().find('span').get_text(strip=True).replace(" Innings", "")
    
    players_data = []
    tables = soup.select('div > table.ci-scorecard-table')
    
    # First innings batting
    first_innings_rows = tables[0].select('tbody > tr')
    for row in first_innings_rows:
        if len(row.find_all('td')) >= 8:
            tds = row.find_all('td')
            if tds[0].find('a'):
                players_data.append({
                    'name': tds[0].find('a').get_text(strip=True).replace('\xa0', ''),
                    'team': team1,
                    'link': f"https://www.espncricinfo.com{tds[0].find('a')['href']}"
                })
    
    # Second innings batting
    second_innings_rows = tables[1].select('tbody > tr')
    for row in second_innings_rows:
        if len(row.find_all('td')) >= 8:
            tds = row.find_all('td')
            if tds[0].find('a'):
                players_data.append({
                    'name': tds[0].find('a').get_text(strip=True).replace('\xa0', ''),
                    'team': team2,
                    'link': f"https://www.espncricinfo.com{tds[0].find('a')['href']}"
                })
    
    # Bowling players
    tables = soup.select('div > table.ds-table')
    
    # First innings bowling
    first_innings_rows = tables[1].select('tbody > tr')
    for row in first_innings_rows:
        if len(row.find_all('td')) >= 11:
            tds = row.find_all('td')
            if tds[0].find('a'):
                players_data.append({
                    'name': tds[0].find('a').get_text(strip=True).replace('\xa0', ''),
                    'team': team2,
                    'link': f"https://www.espncricinfo.com{tds[0].find('a')['href']}"
                })
    
    # Second innings bowling
    second_innings_rows = tables[3].select('tbody > tr')
    for row in second_innings_rows:
        if len(row.find_all('td')) >= 11:
            tds = row.find_all('td')
            if tds[0].find('a'):
                players_data.append({
                    'name': tds[0].find('a').get_text(strip=True).replace('\xa0', ''),
                    'team': team1,
                    'link': f"https://www.espncricinfo.com{tds[0].find('a')['href']}"
                })
    
    return players_data

def scrape_player_info(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    batting_style = soup.find('p', string='Batting Style').find_next('span').get_text(strip=True) if soup.find('p', string='Batting Style') else ''
    bowling_style = soup.find('p', string='Bowling Style').find_next('span').get_text(strip=True) if soup.find('p', string='Bowling Style') else ''
    playing_role = soup.find('p', string='Playing Role').find_next('span').get_text(strip=True) if soup.find('p', string='Playing Role') else ''
    
    bio = soup.select_one('div.ci-player-bio-content p').get_text(strip=True) if soup.select_one('div.ci-player-bio-content p') else ''
    
    return {
        'battingStyle': batting_style,
        'bowlingStyle': bowling_style,
        'playingRole': playing_role,
        'content': bio
    }

if __name__ == '__main__':
    os.makedirs('output', exist_ok=True)
    all_player_info = []
    
    match_links = get_match_links()
    for link in match_links[:5]:  # Limit to 5 matches for testing
        players = get_players_data(link)
        for player in players:
            info = scrape_player_info(player['link'])
            player_info = {
                'name': player['name'],
                'team': player['team'],
                'battingStyle': info['battingStyle'],
                'bowlingStyle': info['bowlingStyle'],
                'playingRole': info['playingRole'],
                'description': info['content']
            }
            all_player_info.append(player_info)
    
    with open('output/player_info.json', 'w') as f:
        json.dump({'playerInfo': all_player_info}, f, indent=4)
    
    print("Data saved to output/player_info.json")