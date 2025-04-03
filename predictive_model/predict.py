# -*- coding: utf-8 -*-
"""
Enhanced Cricket Performance Analytics Pipeline
- Handles missing values in regression models
- Improved feature engineering
- Robust error handling
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
import matplotlib.pyplot as plt
import seaborn as sns
import re

# ------------------------------
# 1. Data Loading with Robust Cleaning
# ------------------------------
def load_match_data(filepath):
    """Load match summary data with basic cleaning"""
    df = pd.read_csv(filepath)
    df.columns = df.columns.str.strip().str.lower()
    return df

def load_player_data(filepath):
    """Load and standardize player metadata"""
    df = pd.read_csv(filepath)
    df.columns = df.columns.str.strip().str.lower()
    return df.rename(columns={
        'name': 'name',
        'team': 'team',
        'battingstyle': 'battingStyle',
        'bowlingstyle': 'bowlingStyle'
    })

def safe_numeric_conversion(series):
    """Convert series to numeric with advanced cleaning"""
    if series.dtype == object:
        series = series.astype(str).apply(
            lambda x: re.sub(r'(\d+\.\d+)\.\d+', r'\1', x) if pd.notna(x) else x
        )
    return pd.to_numeric(series, errors='coerce')

def load_batting_data(filepath):
    """Load batting data with rigorous numeric validation"""
    df = pd.read_csv(filepath)
    df.columns = df.columns.str.strip().str.lower()
    
    # Clean and convert numeric columns
    numeric_cols = ['runs', 'balls', '4s', '6s', 'sr']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = safe_numeric_conversion(df[col])
    
    return df.rename(columns={'out/not_out': 'dismissal'})

def load_bowling_data(filepath):
    """Load bowling data with economy rate validation"""
    df = pd.read_csv(filepath)
    df.columns = df.columns.str.strip().str.lower()
    
    # Special handling for economy rate
    if 'economy' in df.columns:
        df['economy'] = safe_numeric_conversion(df['economy'])
        # Validate reasonable range
        df['economy'] = df['economy'].clip(0, 20)  # Assume economy between 0-20
    
    return df

# ------------------------------
# 2. Feature Engineering
# ------------------------------
def create_features(batting, bowling):
    """Generate performance metrics for analysis"""
    # Batting features
    batting_features = batting.groupby('batsmanname').agg({
        'runs': ['sum', 'mean'],
        'balls': 'sum',
        'sr': 'mean',
        '4s': 'sum',
        '6s': 'sum',
        'match_id': 'count'
    })
    batting_features.columns = [
        'total_runs', 'avg_runs', 'balls_faced',
        'strike_rate', 'fours', 'sixes', 'innings_played'
    ]
    batting_features = batting_features.reset_index()
    
    # Bowling features
    bowling_features = bowling.groupby('bowlername').agg({
        'wickets': 'sum',
        'economy': 'mean',
        'overs': 'sum',
        'match_id': 'count'
    })
    bowling_features.columns = [
        'total_wickets', 'avg_economy',
        'overs_bowled', 'matches_played'
    ]
    bowling_features = bowling_features.reset_index()
    
    return batting_features, bowling_features

# ------------------------------
# 3. Regression Models with Missing Value Handling
# ------------------------------
def build_regression_models(batting, bowling):
    """Train predictive models for player performance with proper NaN handling"""
    print("\n=== PERFORMANCE PREDICTION MODELS ===")
    
    # Batting model (predict total runs)
    X_bat = batting[['innings_played', 'balls_faced', 'strike_rate']].copy()
    y_bat = batting['total_runs'].copy()
    
    # Handle missing values - impute with median
    imputer = SimpleImputer(strategy='median')
    X_bat_imputed = imputer.fit_transform(X_bat)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X_bat_imputed, y_bat, test_size=0.2, random_state=42
    )
    
    # Create pipeline with imputer and model
    bat_model = make_pipeline(
        SimpleImputer(strategy='median'),
        LinearRegression()
    )
    bat_model.fit(X_train, y_train)
    batting['predicted_runs'] = bat_model.predict(X_bat_imputed)
    
    print("\nBatting Model Results:")
    print(f"R-squared: {bat_model.score(X_test, y_test):.3f}")
    print("Feature Coefficients:")
    coefs = bat_model.named_steps['linearregression'].coef_
    for feat, coef in zip(X_bat.columns, coefs):
        print(f"{feat:>15}: {coef:>7.2f}")
    
    # Bowling model (predict economy rate)
    X_bowl = bowling[['matches_played', 'overs_bowled', 'total_wickets']].copy()
    y_bowl = bowling['avg_economy'].copy()
    
    # Handle missing values
    X_bowl_imputed = imputer.fit_transform(X_bowl)
    
    # Split data
    X_train_bowl, X_test_bowl, y_train_bowl, y_test_bowl = train_test_split(
        X_bowl_imputed, y_bowl, test_size=0.2, random_state=42
    )
    
    bowl_model = make_pipeline(
        SimpleImputer(strategy='median'),
        LinearRegression()
    )
    bowl_model.fit(X_train_bowl, y_train_bowl)
    bowling['predicted_economy'] = bowl_model.predict(X_bowl_imputed)
    
    print("\nBowling Model Results:")
    print(f"R-squared: {bowl_model.score(X_test_bowl, y_test_bowl):.3f}")
    print("Feature Coefficients:")
    bowl_coefs = bowl_model.named_steps['linearregression'].coef_
    for feat, coef in zip(X_bowl.columns, bowl_coefs):
        print(f"{feat:>15}: {coef:>7.2f}")
    
    return batting, bowling

# ------------------------------
# 4. Player Clustering
# ------------------------------
def cluster_players(batting, bowling):
    """Identify player segments using K-means with proper scaling"""
    print("\n=== PLAYER SEGMENTATION ===")
    
    # Batting clusters - drop rows with missing values
    bat_features = batting[['strike_rate', 'avg_runs', 'sixes']].dropna()
    bat_scaled = StandardScaler().fit_transform(bat_features)
    
    kmeans_bat = KMeans(n_clusters=4, random_state=42)
    batting.loc[bat_features.index, 'cluster'] = kmeans_bat.fit_predict(bat_scaled)
    
    print("\nBatting Clusters Profile:")
    print(batting.groupby('cluster').agg({
        'strike_rate': 'mean',
        'avg_runs': 'mean',
        'sixes': 'mean'
    }).round(2))
    
    # Bowling clusters - drop rows with missing values
    bowl_features = bowling[['avg_economy', 'total_wickets']].dropna()
    bowl_scaled = StandardScaler().fit_transform(bowl_features)
    
    kmeans_bowl = KMeans(n_clusters=3, random_state=42)
    bowling.loc[bowl_features.index, 'cluster'] = kmeans_bowl.fit_predict(bowl_scaled)
    
    # Visualization
    plt.figure(figsize=(15,6))
    
    plt.subplot(1,2,1)
    sns.scatterplot(data=batting.dropna(subset=['cluster']), 
                    x='strike_rate', y='avg_runs',
                    hue='cluster', palette='viridis', s=100)
    plt.title("Batsmen Clusters", fontsize=14)
    
    plt.subplot(1,2,2)
    sns.scatterplot(data=bowling.dropna(subset=['cluster']), 
                    x='avg_economy', y='total_wickets',
                    hue='cluster', palette='rocket', s=100)
    plt.title("Bowler Clusters", fontsize=14)
    
    plt.tight_layout()
    plt.savefig('player_clusters.png', dpi=300, bbox_inches='tight')
    print("\nSaved cluster visualization: player_clusters.png")

# ------------------------------
# Main Execution
# ------------------------------
def main():
    print("Cricket Analytics Pipeline Started")
    
    try:
        # Load and clean data
        print("\n[1/4] Loading and validating data...")
        matches = load_match_data('dim_match_summary.csv')
        players = load_player_data('dim_players_no_images.csv')
        batting = load_batting_data('fact_batting_summary.csv')
        bowling = load_bowling_data('fact_bowling_summary.csv')
        
        # Feature engineering
        print("[2/4] Creating performance features...")
        batting_features, bowling_features = create_features(batting, bowling)
        
        # Predictive modeling
        print("[3/4] Building regression models...")
        batting_pred, bowling_pred = build_regression_models(
            batting_features, bowling_features
        )
        
        # Player segmentation
        print("[4/4] Clustering players...")
        cluster_players(batting_pred, bowling_pred)
        
        print("\nPipeline executed successfully!")
        print("Outputs generated:")
        print("- Batting/bowling performance predictions")
        print("- Player cluster visualization (player_clusters.png)")
        
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        print("\nTroubleshooting steps:")
        print("1. Verify all input files exist")
        print("2. Check for malformed numeric values in CSVs")
        print("3. Ensure required packages are installed")
        raise

if __name__ == "__main__":
    main()