# machine_learning.py
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

def main():
    # Load cleaned data
    df = pd.read_csv('cleaned_player_data.csv')

    # --- Feature Engineering ---
    # Batting features
    df['boundary_pct'] = ((df['total_4s']*4 + df['total_6s']*6) / df['total_runs'].replace(0, np.nan)) * 100
    df['boundary_pct'] = df['boundary_pct'].replace([np.inf, -np.inf], np.nan)
    
    # Bowling features
    df['total_balls_bowled'] = df['total_overs'] * 6
    df['dot_ball_pct'] = (df['total_0s'] / df['total_balls_bowled'].replace(0, np.nan)) * 100

    # --- Runs Prediction Model ---
    batting_data = df[['total_innings', 'total_balls', 'avg_strike_rate', 'boundary_pct', 'total_runs']].dropna()
    X_bat = batting_data.iloc[:, :-1]
    y_bat = batting_data.iloc[:, -1]
    
    bat_model = LinearRegression()
    bat_model.fit(X_bat, y_bat)
    print(f"\n[Regression] Runs Prediction R²: {bat_model.score(X_bat, y_bat):.2f}")

    # --- Economy Prediction Model ---
    bowling_data = df[['total_innings_bowled', 'total_wickets', 'dot_ball_pct', 'avg_economy']].dropna()
    X_bowl = bowling_data.iloc[:, :-1]
    y_bowl = bowling_data.iloc[:, -1]
    
    bowl_model = LinearRegression()
    bowl_model.fit(X_bowl, y_bowl)
    print(f"[Regression] Economy Prediction R²: {bowl_model.score(X_bowl, y_bowl):.2f}")

    # --- Clustering Model: Batting Performance ---
    # Prepare batting data
    batting_cluster = df[['total_runs', 'avg_strike_rate']].dropna()
    batting_cluster = batting_cluster[batting_cluster['total_runs'] > 0]  # Remove players with 0 runs
    
    # Standardize features
    scaler = StandardScaler()
    batting_scaled = scaler.fit_transform(batting_cluster)
    
    # K-Means clustering
    kmeans_bat = KMeans(n_clusters=3, random_state=42)
    clusters_bat = kmeans_bat.fit_predict(batting_scaled)
    
    # Add clusters to dataframe
    batting_cluster = batting_cluster.copy()
    batting_cluster['Cluster'] = clusters_bat
    
    # Visualize batting clusters
    plt.figure(figsize=(10, 6))
    scatter = plt.scatter(
        batting_cluster['total_runs'], 
        batting_cluster['avg_strike_rate'], 
        c=batting_cluster['Cluster'], 
        cmap='viridis',
        alpha=0.7
    )
    plt.xlabel('Total Runs', fontsize=12)
    plt.ylabel('Strike Rate (Avg)', fontsize=12)
    plt.title('Batting Clusters: Runs vs Strike Rate', fontsize=14)
    plt.colorbar(scatter).set_label('Cluster')
    plt.grid(True, alpha=0.3)
    plt.savefig('batting_clusters.png', dpi=300)
    print("\n[Clustering] Batting clusters visualization saved to batting_clusters.png")

    # Cluster analysis
    print("\nBatting Cluster Profiles:")
    print(batting_cluster.groupby('Cluster').agg({
        'total_runs': ['mean', 'median', 'max'],
        'avg_strike_rate': ['mean', 'median']
    }))

    # --- Clustering Model: Bowling Performance ---
    # Prepare bowling data
    bowling_cluster = df[['avg_economy', 'total_wickets']].dropna()
    
    # Standardize features
    bowling_scaled = scaler.fit_transform(bowling_cluster)
    
    # K-Means clustering
    kmeans_bowl = KMeans(n_clusters=3, random_state=42)
    clusters_bowl = kmeans_bowl.fit_predict(bowling_scaled)
    
    # Add clusters to dataframe
    bowling_cluster = bowling_cluster.copy()
    bowling_cluster['Cluster'] = clusters_bowl
    
    # Visualize bowling clusters
    plt.figure(figsize=(10, 6))
    scatter = plt.scatter(
        bowling_cluster['avg_economy'], 
        bowling_cluster['total_wickets'], 
        c=bowling_cluster['Cluster'], 
        cmap='plasma',
        alpha=0.7
    )
    plt.xlabel('Economy Rate (Avg)', fontsize=12)
    plt.ylabel('Total Wickets', fontsize=12)
    plt.title('Bowling Clusters: Economy vs Wickets', fontsize=14)
    plt.colorbar(scatter).set_label('Cluster')
    plt.gca().invert_xaxis()  # Lower economy is better
    plt.grid(True, alpha=0.3)
    plt.savefig('bowling_clusters.png', dpi=300)
    print("\n[Clustering] Bowling clusters visualization saved to bowling_clusters.png")

    # Cluster analysis
    print("\nBowling Cluster Profiles:")
    print(bowling_cluster.groupby('Cluster').agg({
        'avg_economy': ['mean', 'median'],
        'total_wickets': ['mean', 'median', 'max']
    }))

if __name__ == "__main__":
    main()