# -*- coding: utf-8 -*-
"""
T20 Cricket Data Analysis Pipeline
- Complete ETL process with robust data cleaning
- Comprehensive statistical analysis
- Advanced visualizations
"""

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind, spearmanr

# ------------------------------
# Data Loading Functions
# ------------------------------
def load_match_data(filepath):
    """Load and clean match summary data"""
    df = pd.read_csv(filepath)
    df.columns = df.columns.str.strip().str.lower()
    return df

def load_player_data(filepath):
    """Load and standardize player data"""
    df = pd.read_csv(filepath)
    df.columns = df.columns.str.strip().str.lower()
    return df.rename(columns={
        'dbdb': 'name',
        'ibdb': 'team',
        'dbstringstyle': 'battingstyle',
        'boolingstyle': 'bowlingstyle'
    })

def load_batting_data(filepath):
    """Load and clean batting performance data"""
    df = pd.read_csv(filepath)
    df.columns = df.columns.str.strip().str.lower()
    return df.rename(columns={
        '45': '4s',
        '65': '6s',
        'out/not_out': 'dismissal'
    })

def load_bowling_data(filepath):
    """Load and clean bowling performance data"""
    df = pd.read_csv(filepath)
    df.columns = df.columns.str.strip().str.lower()
    return df

# ------------------------------
# Data Processing (ETL)
# ------------------------------
def preprocess_data(matches, players, batting, bowling):
    """Clean, merge and transform all datasets"""
    # Clean player names
    players['name'] = players['name'].str.strip()
    batting['batsmanname'] = batting['batsmanname'].str.strip()
    bowling['bowlername'] = bowling['bowlername'].str.strip()
    
    # Convert numeric fields
    batting['sr'] = pd.to_numeric(batting['sr'], errors='coerce')
    bowling['economy'] = pd.to_numeric(bowling['economy'], errors='coerce')
    
    # Merge batting data with player info
    batting_merged = pd.merge(
        batting,
        players[['name', 'battingstyle', 'playingrole']],
        left_on='batsmanname',
        right_on='name',
        how='left'
    ).drop(columns='name')
    
    # Merge bowling data with player info
    bowling_merged = pd.merge(
        bowling,
        players[['name', 'bowlingstyle', 'playingrole']],
        left_on='bowlername',
        right_on='name',
        how='left'
    ).drop(columns='name')
    
    return matches, batting_merged, bowling_merged

# ------------------------------
# Analysis Functions
# ------------------------------
def analyze_team_performance(matches):
    """Calculate and visualize team performance metrics"""
    print("\n=== TEAM PERFORMANCE ANALYSIS ===")
    
    # Calculate win rates for all teams
    all_teams = pd.concat([matches['team1'], matches['team2']]).unique()
    results = []
    
    for team in all_teams:
        total = ((matches['team1'] == team) | (matches['team2'] == team)).sum()
        wins = (matches['winner'] == team).sum()
        results.append({
            'Team': team,
            'Matches': total,
            'Wins': wins,
            'WinRate': wins/total if total > 0 else 0
        })
    
    # Create and display results dataframe
    win_df = pd.DataFrame(results).sort_values('WinRate', ascending=False)
    print(win_df.to_string(index=False))
    
    # Visualize team performance
    plt.figure(figsize=(12, 6))
    sns.barplot(data=win_df, x='Team', y='WinRate')
    plt.title('Team Win Rates')
    plt.ylabel('Win Rate')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('team_win_rates.png', dpi=300)
    plt.close()
    print("\nSaved team_win_rates.png")

def analyze_batting_performance(batting):
    """Analyze and visualize batting statistics"""
    print("\n=== BATTING PERFORMANCE ANALYSIS ===")
    
    # Top batsmen by strike rate (min 30 runs)
    qualified = batting.groupby('batsmanname')['runs'].sum() >= 30
    top_batsmen = batting[batting['batsmanname'].isin(qualified[qualified].index)]
    
    batting_stats = top_batsmen.groupby('batsmanname').agg({
        'runs': 'sum',
        'sr': 'mean',
        '4s': 'sum',
        '6s': 'sum'
    }).sort_values('sr', ascending=False)
    
    print("\nTop Batsmen by Strike Rate (min 30 runs):")
    print(batting_stats.head(10).to_string())
    
    # Left vs Right handed batsmen comparison
    if 'battingstyle' in batting.columns:
        left_hand = batting[batting['battingstyle'].str.contains('Left', na=False)]['sr'].dropna()
        right_hand = batting[batting['battingstyle'].str.contains('Right', na=False)]['sr'].dropna()
        
        if len(left_hand) > 1 and len(right_hand) > 1:
            t_stat, p_value = ttest_ind(left_hand, right_hand)
            print(f"\nLeft vs Right Handed Batting SR Comparison:")
            print(f"Left-handed mean SR: {left_hand.mean():.2f}")
            print(f"Right-handed mean SR: {right_hand.mean():.2f}")
            print(f"T-test p-value: {p_value:.4f}")

def analyze_bowling_performance(bowling):
    """Analyze and visualize bowling statistics"""
    print("\n=== BOWLING PERFORMANCE ANALYSIS ===")
    
    # Full economy rate rankings
    bowling_stats = bowling.groupby('bowlername').agg({
        'economy': 'mean',
        'wickets': 'sum',
        'overs': 'sum'
    }).sort_values('economy')
    
    print("\nBowling Economy Rankings (All Bowlers):")
    print(bowling_stats.to_string())
    
    # Detailed economy statistics
    economy = bowling_stats['economy']
    print("\nEconomy Rate Statistics:")
    print(f"Mean: {economy.mean():.2f}")
    print(f"Median: {economy.median():.2f}")
    print(f"Standard Deviation: {economy.std():.2f}")
    print(f"25th Percentile: {np.percentile(economy, 25):.2f}")
    print(f"75th Percentile: {np.percentile(economy, 75):.2f}")
    
    # Economy distribution visualization
    plt.figure(figsize=(12, 6))
    sns.boxplot(x=bowling['economy'], whis=1.5)
    plt.title('Bowling Economy Rate Distribution')
    plt.xlabel('Economy Rate')
    plt.savefig('bowling_economy.png', dpi=300)
    plt.close()
    print("\nSaved bowling_economy.png")
    
    # Wickets vs Economy correlation
    if len(bowling) > 1:
        corr, p_value = spearmanr(bowling['wickets'], bowling['economy'])
        print("\nWickets vs Economy Correlation Analysis:")
        print(f"Spearman's rho: {corr:.2f}")
        print(f"P-value: {p_value:.4f}")

# ------------------------------
# Main Execution
# ------------------------------
def main():
    print("Starting T20 Cricket Data Analysis Pipeline...")
    
    try:
        # Load data
        print("\n[1/4] Loading data files...")
        matches = load_match_data('dim_match_summary.csv')
        players = load_player_data('dim_players_no_images.csv')
        batting = load_batting_data('fact_batting_summary.csv')
        bowling = load_bowling_data('fact_bowling_summary.csv')
        
        # Process data
        print("[2/4] Processing and merging data...")
        matches, batting, bowling = preprocess_data(matches, players, batting, bowling)
        
        # Perform analysis
        print("[3/4] Analyzing team performance...")
        analyze_team_performance(matches)
        
        print("[4/4] Analyzing player performance...")
        analyze_batting_performance(batting)
        analyze_bowling_performance(bowling)
        
        print("\nAnalysis completed successfully!")
        print("Visualizations saved to current directory.")
        
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        print("\nTroubleshooting steps:")
        print("1. Verify all CSV files exist in working directory")
        print("2. Check CSV files have correct column headers")
        print("3. Ensure required packages are installed")
        print("4. Validate data formats in CSV files")

if __name__ == "__main__":
    main()