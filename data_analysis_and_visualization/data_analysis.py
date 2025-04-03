import pandas as pd
from scipy.stats import ttest_ind

def main():
    # Load raw data
    batting = pd.read_csv('fact_bating_summary.csv')
    bowling = pd.read_csv('fact_bowling_summary.csv')
    players = pd.read_csv('dim_players.csv')

    # Fix column names
    batting.rename(columns={'teamInnings': 'team', 'battingPos': 'position'}, inplace=True)

    # Aggregate batting stats
    batting_agg = batting.groupby('batsmanName').agg(
        total_innings=('match_id', 'nunique'),
        total_runs=('runs', 'sum'),
        total_balls=('balls', 'sum'),
        total_4s=('4s', 'sum'),
        total_6s=('6s', 'sum'),
        avg_strike_rate=('SR', 'mean')
    ).reset_index()

    # Aggregate bowling stats
    bowling_agg = bowling.groupby('bowlerName').agg(
        total_innings_bowled=('match_id', 'nunique'),
        total_wickets=('wickets', 'sum'),
        total_0s=('0s', 'sum'),
        total_overs=('overs', 'sum'),
        avg_economy=('economy', 'mean')
    ).reset_index()

    # Merge datasets
    df = pd.merge(players, batting_agg, left_on='name', right_on='batsmanName', how='left')
    df = pd.merge(df, bowling_agg, left_on='name', right_on='bowlerName', how='left')

    # Filter players
    df_filtered = df[
        ((df['total_innings'].fillna(0) >= 3) |
        (df['total_innings_bowled'].fillna(0) >= 3))
    ]
    df_filtered = df_filtered[df_filtered['avg_strike_rate'].fillna(0) <= 200]

    # Hypothesis testing
    openers = df_filtered[df_filtered['playingRole'].str.contains('Top order', na=False)]
    non_openers = df_filtered[~df_filtered['name'].isin(openers['name'])]
    
    t_stat, p_value = ttest_ind(
        openers['total_runs'].dropna(),
        non_openers['total_runs'].dropna(),
        equal_var=False
    )
    print(f"Hypothesis Test Results:\nT-stat: {t_stat:.2f}, P-value: {p_value:.4f}")

    # Save cleaned data
    df_filtered.to_csv('cleaned_player_data.csv', index=False)
    print("\nCleaned data saved to cleaned_player_data.csv")

if __name__ == "__main__":
    main()