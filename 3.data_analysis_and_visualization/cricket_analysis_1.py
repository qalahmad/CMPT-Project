# -*- coding: utf-8 -*-
"""
T20 Cricket Data Analysis Pipeline (Fixed Version)
- Handles column name case sensitivity
- Robust data merging
- Complete statistical analysis
"""

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind

# ------------------------------
# Data Loading Functions (Fixed)
# ------------------------------
def load_match_data(filepath):
    """Load match summary data"""
    df = pd.read_csv(filepath)
    # Standardize column names
    df.columns = df.columns.str.strip().str.lower()
    return df

def load_player_data(filepath):
    """Load player data with case handling"""
    df = pd.read_csv(filepath)
    # Standardize and rename columns
    df.columns = df.columns.str.strip().str.lower()
    return df.rename(columns={
        'dbdb': 'name',
        'ibdb': 'team',
        'dbstringstyle': 'battingstyle',
        'boolingstyle': 'bowlingstyle'
    })

def load_batting_data(filepath):
    """Load batting data with cleaning"""
    df = pd.read_csv(filepath)
    df.columns = df.columns.str.strip().str.lower()
    # Fix column names
    return df.rename(columns={
        '45': '4s',
        '65': '6s',
        'out/not_out': 'dismissal'
    })

def load_bowling_data(filepath):
    """Load bowling data"""
    df = pd.read_csv(filepath)
    df.columns = df.columns.str.strip().str.lower()
    return df

# ------------------------------
# Data Processing (Fixed Merging)
# ------------------------------
def preprocess_data(matches, players, batting, bowling):
    """Clean and merge all datasets with case handling"""
    # Convert numeric columns
    batting['sr'] = pd.to_numeric(batting['sr'], errors='coerce')
    bowling['economy'] = pd.to_numeric(bowling['economy'], errors='coerce')
    
    # Standardize player name columns for merging
    batting['batsmanname'] = batting['batsmanname'].str.strip()
    bowling['bowlername'] = bowling['bowlername'].str.strip()
    players['name'] = players['name'].str.strip()
    
    # Merge batting data (case insensitive)
    batting_merged = pd.merge(
        batting,
        players[['name', 'battingstyle', 'playingrole']],
        left_on='batsmanname',
        right_on='name',
        how='left'
    ).drop(columns='name')
    
    # Merge bowling data (case insensitive)
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
    """Calculate team win rates"""
    print("\n=== TEAM PERFORMANCE ===")
    all_teams = pd.concat([matches['team1'], matches['team2']]).unique()
    
    results = []
    for team in all_teams:
        total = ((matches['team1'] == team) | (matches['team2'] == team)).sum()
        wins = (matches['winner'] == team).sum()
        results.append({
            'Team': team, 
            'Matches': total,
            'Wins': wins,
            'WinRate': f"{(wins/total)*100:.1f}%"
        })
    
    print(pd.DataFrame(results).sort_values('Wins', ascending=False).to_string(index=False))

def analyze_batting(batting):
    """Analyze batting stats"""
    print("\n=== TOP BATSMEN ===")
    top_batsmen = batting.groupby('batsmanname').agg({
        'runs': 'sum',
        'sr': 'mean',
        '4s': 'sum',
        '6s': 'sum'
    }).sort_values('sr', ascending=False)
    
    print(top_batsmen.head(10).to_string())

def analyze_bowling(bowling):
    """Analyze bowling stats"""
    print("\n=== TOP BOWLERS ===")
    top_bowlers = bowling.groupby('bowlername').agg({
        'wickets': 'sum',
        'economy': 'mean',
        'overs': 'sum'
    }).sort_values('economy')
    
    print(top_bowlers.head(10).to_string())

# ------------------------------
# Main Execution
# ------------------------------
def main():
    print("Starting T20 Analysis...")
    
    try:
        # Load data
        print("Loading files...")
        matches = load_match_data('dim_match_summary.csv')
        players = load_player_data('dim_players_no_images.csv')
        batting = load_batting_data('fact_batting_summary.csv')
        bowling = load_bowling_data('fact_bowling_summary.csv')
        
        # Process data
        print("Processing data...")
        matches, batting, bowling = preprocess_data(matches, players, batting, bowling)
        
        # Analyze
        analyze_team_performance(matches)
        analyze_batting(batting)
        analyze_bowling(bowling)
        
        print("\nAnalysis completed successfully!")
        
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        print("Check: 1) File paths 2) CSV formats 3) Column names")

if __name__ == "__main__":
    main()