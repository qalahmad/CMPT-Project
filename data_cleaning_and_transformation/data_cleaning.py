import pandas as pd
import json

with open('t20_wc_match_results.json') as f:
    data = json.load(f)

#get matches from the json
df_match = pd.DataFrame(data[0]['matchSummary'])
print(df_match.head(10).to_string())

df_match.rename({'scorecard': 'match_id'}, axis = 'columns', inplace = True)
print(df_match.head(10).to_string())



match_ids_dict = {}

for index, row in df_match.iterrows():
    key1 = row['team1'] + ' Vs ' + row['team2']
    key2 = row['team2'] + ' Vs ' + row['team1'] #can be omitted? because it just repeats itself on the line 22 basically
    match_ids_dict[key1] = row['match_id']
    match_ids_dict[key2] = row['match_id'] #either one can be omitted? (Namibia vs Sri Lanka        or     Sri Lanka vs Namibia)

#print(match_ids_dict)
match_ids_df = pd.DataFrame.from_dict(match_ids_dict, orient='index')
print(match_ids_df.head(10).to_string(), match_ids_df.shape)


with open('t20_wc_batting_summary.json') as f:
    data = json.load(f)
    all_records = []
    for rec in data:
        all_records.extend(rec['battingSummary'])

df_batting = pd.DataFrame(all_records)
print(df_batting.head(11).to_string())


df_batting['out/not_out'] = df_batting.dismissal.apply(lambda x: "out" if len(x)>0 else "not_out")
print(df_batting.head(11).to_string())

df_batting['match_id'] = df_batting['match'].map(match_ids_dict)
print(df_batting.head().to_string())

df_batting.drop(columns=["dismissal"], inplace=True)
print(df_batting.head(10).to_string())

df_batting['batsmanName'] = df_batting['batsmanName'].apply(lambda x: x.replace('â€', ''))
df_batting['batsmanName'] = df_batting['batsmanName'].apply(lambda x: x.replace('\xa0', ''))
print(df_batting.head().to_string())
print(df_batting.shape)

df_batting.to_csv('fact_bating_summary.csv', index = False)

with open('t20_wc_bowling_summary.json') as f:
    data = json.load(f)
    all_records = []
    for rec in data:
        all_records.extend(rec['bowlingSummary'])
print(all_records[:2])


df_bowling = pd.DataFrame(all_records)
print(df_bowling.shape)
print(df_bowling.head().to_string())

df_bowling['match_id'] = df_bowling['match'].map(match_ids_dict)
print(df_bowling.head().to_string())
df_bowling.to_csv('fact_bowling_summary.csv', index = False)

with open('t20_wc_player_info.json') as f:
    data = json.load(f)
df_players = pd.DataFrame(data)
print(df_players.shape)
print(df_players.head(10).to_string())

df_players['name'] = df_players['name'].apply(lambda x: x.replace('â€', ''))
df_players['name'] = df_players['name'].apply(lambda x: x.replace('†', ''))
df_players['name'] = df_players['name'].apply(lambda x: x.replace('\xa0', ''))
print(df_players.head(10).to_string())
df_players.to_csv('dim_players_no_images.csv', index = False)