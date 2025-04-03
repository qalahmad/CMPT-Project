import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import os

# Set page configuration
st.set_page_config(
    page_title="T20 Cricket Dashboard",
    page_icon="🏏",
    layout="wide"
)

# Cache data loading to improve performance
@st.cache_data
def load_data():
    try:
        # Adjust these paths based on your actual file locations
        match_data = pd.read_csv('../data_cleaning_and_transformation/dim_match_summary.csv')
        player_data = pd.read_csv('../data_cleaning_and_transformation/dim_players_no_images.csv')
        batting_data = pd.read_csv('../data_cleaning_and_transformation/fact_batting_summary.csv')
        bowling_data = pd.read_csv('../data_cleaning_and_transformation/fact_bowling_summary.csv')
        
        return match_data, player_data, batting_data, bowling_data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None, None

# Load images for visualizations
def load_images():
    images = {}
    try:
        images['team_win_rates'] = '../data_analysis_and_visualization/team_win_rates.png'
        images['bowling_economy'] = '../data_analysis_and_visualization/bowling_economy.png'
        images['player_clusters'] = '../predictive_model/player_clusters.png'
    except Exception as e:
        st.error(f"Error loading images: {e}")
    return images

# Main function
def main():
    # Sidebar
    st.sidebar.title("T20 Cricket Analysis")
    
    # Load data
    match_data, player_data, batting_data, bowling_data = load_data()
    images = load_images()
    
    # Navigation
    page = st.sidebar.selectbox(
        "Select Page",
        ["Home/Overview", "Batting Analysis", "Bowling Analysis", "Player Clusters", "Team Analysis"]
    )
    
    # Add filters to sidebar
    if match_data is not None and player_data is not None:
        all_teams = pd.concat([match_data['team1'], match_data['team2']]).unique()
        selected_team = st.sidebar.multiselect("Select Teams", all_teams)
        
        if 'playingrole' in player_data.columns:
            roles = player_data['playingrole'].unique()
            selected_roles = st.sidebar.multiselect("Select Player Roles", roles)
    
    # Pages
    if page == "Home/Overview":
        display_overview(match_data, batting_data, bowling_data)
    
    elif page == "Batting Analysis":
        display_batting_analysis(batting_data, player_data)
    
    elif page == "Bowling Analysis":
        display_bowling_analysis(bowling_data, player_data)
    
    elif page == "Player Clusters":
        display_player_clusters(images)
    
    elif page == "Team Analysis":
        display_team_analysis(match_data, images)

# Page functions
def display_overview(match_data, batting_data, bowling_data):
    st.title("T20 Cricket Dashboard - Overview")
    
    if match_data is None or batting_data is None or bowling_data is None:
        st.warning("Data not found. Please check your data files.")
        return
    
    # Calculate key metrics
    total_matches = len(match_data) if match_data is not None else 0
    total_runs = batting_data['runs'].sum() if batting_data is not None else 0
    total_wickets = bowling_data['wickets'].sum() if bowling_data is not None else 0
    
    # Display metrics in columns
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Matches", total_matches)
    with col2:
        st.metric("Total Runs", total_runs)
    with col3:
        st.metric("Total Wickets", total_wickets)
    
    # Additional information
    st.subheader("About This Dashboard")
    st.write("""
    This dashboard provides comprehensive analysis of T20 cricket data, including batting 
    and bowling statistics, team performance metrics, and player clustering analysis.
    
    Use the sidebar to navigate between different sections and apply filters to the data.
    """)

def display_batting_analysis(batting_data, player_data):
    st.title("Batting Analysis")
    
    if batting_data is None or player_data is None:
        st.warning("Data not found. Please check your data files.")
        return
    
    # Top run scorers
    st.subheader("Top Run Scorers")
    top_batsmen = batting_data.groupby('batsmanname').agg({
        'runs': 'sum',
        'balls': 'sum',
        '4s': 'sum', 
        '6s': 'sum'
    }).reset_index()
    
    # Calculate strike rate
    top_batsmen['strike_rate'] = (top_batsmen['runs'] / top_batsmen['balls']) * 100
    top_batsmen['boundary_percentage'] = ((top_batsmen['4s'] + top_batsmen['6s']) / top_batsmen['balls']) * 100
    
    # Sort and display top 10
    top_batsmen = top_batsmen.sort_values('runs', ascending=False).head(10)
    
    # Bar chart for top run scorers
    fig = px.bar(
        top_batsmen, 
        x='batsmanname', 
        y='runs',
        title='Top 10 Run Scorers',
        labels={'batsmanname': 'Batsman', 'runs': 'Total Runs'},
        color='runs'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Scatter plot for strike rate vs boundary percentage
    st.subheader("Strike Rate vs Boundary Percentage")
    fig = px.scatter(
        top_batsmen,
        x='strike_rate',
        y='boundary_percentage',
        size='runs',
        hover_name='batsmanname',
        title='Strike Rate vs Boundary Percentage',
        labels={
            'strike_rate': 'Strike Rate',
            'boundary_percentage': 'Boundary Percentage (%)',
            'runs': 'Total Runs'
        }
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Display data table
    st.subheader("Detailed Batting Statistics")
    st.dataframe(top_batsmen)

def display_bowling_analysis(bowling_data, player_data):
    st.title("Bowling Analysis")
    
    if bowling_data is None or player_data is None:
        st.warning("Data not found. Please check your data files.")
        return
    
    # Top wicket takers
    st.subheader("Top Wicket Takers")
    top_bowlers = bowling_data.groupby('bowlername').agg({
        'wickets': 'sum',
        'runs': 'sum',
        'overs': 'sum'
    }).reset_index()
    
    # Calculate economy rate
    top_bowlers['economy'] = top_bowlers['runs'] / top_bowlers['overs']
    
    # Sort and display top 10
    top_bowlers = top_bowlers.sort_values('wickets', ascending=False).head(10)
    
    # Bar chart for top wicket takers
    fig = px.bar(
        top_bowlers,
        x='bowlername',
        y='wickets',
        title='Top 10 Wicket Takers',
        labels={'bowlername': 'Bowler', 'wickets': 'Total Wickets'},
        color='wickets'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Show bowling economy visualization
    st.subheader("Bowling Economy Analysis")
    try:
        img_path = '../data_analysis_and_visualization/bowling_economy.png'
        st.image(img_path, caption="Bowling Economy Analysis")
    except:
        st.error("Could not load bowling economy image. Please check file path.")
    
    # Display data table
    st.subheader("Detailed Bowling Statistics")
    st.dataframe(top_bowlers)

def display_player_clusters(images):
    st.title("Player Clusters Analysis")
    
    # Display player clusters image
    st.subheader("Player Clustering")
    try:
        if os.path.exists(images['player_clusters']):
            st.image(images['player_clusters'], caption="Player Clusters")
        else:
            st.error("Player clusters image not found.")
    except:
        st.error("Could not load player clusters image. Please check file path.")
    
    # Cluster descriptions
    st.subheader("Cluster Descriptions")
    
    cluster_info = {
        "Cluster 1: High-Risk Batters": "Players with high strike rates but inconsistent scoring",
        "Cluster 2: Anchors": "Batters who build innings with good averages but moderate strike rates",
        "Cluster 3: Economical Bowlers": "Bowlers who maintain tight lines and low economy rates",
        "Cluster 4: Wicket-Taking Bowlers": "Bowlers focused on taking wickets rather than economy",
        "Cluster 5: All-Rounders": "Players contributing with both bat and ball"
    }
    
    for cluster, description in cluster_info.items():
        st.markdown(f"**{cluster}**: {description}")

def display_team_analysis(match_data, images):
    st.title("Team Analysis")
    
    if match_data is None:
        st.warning("Match data not found. Please check your data files.")
        return
    
    # Calculate team win rates
    st.subheader("Team Win Rates")
    
    all_teams = pd.concat([match_data['team1'], match_data['team2']]).unique()
    
    results = []
    for team in all_teams:
        total = ((match_data['team1'] == team) | (match_data['team2'] == team)).sum()
        wins = (match_data['winner'] == team).sum()
        win_rate = (wins/total)*100 if total > 0 else 0
        
        results.append({
            'Team': team, 
            'Matches': total,
            'Wins': wins,
            'WinRate': win_rate
        })
    
    results_df = pd.DataFrame(results).sort_values('WinRate', ascending=False)
    
    # Bar chart for win rates
    fig = px.bar(
        results_df,
        x='Team',
        y='WinRate',
        title='Team Win Rates (%)',
        labels={'Team': 'Team', 'WinRate': 'Win Rate (%)'},
        color='WinRate'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Display team win rates image if available
    try:
        if os.path.exists(images['team_win_rates']):
            st.image(images['team_win_rates'], caption="Team Win Rates")
    except:
        st.error("Could not load team win rates image. Please check file path.")
    
    # Head-to-head analysis
    st.subheader("Head-to-Head Analysis")
    
    # Create selection for two teams
    col1, col2 = st.columns(2)
    with col1:
        team1 = st.selectbox("Select Team 1", all_teams)
    with col2:
        team2 = st.selectbox("Select Team 2", all_teams, index=1 if len(all_teams) > 1 else 0)
    
    # Calculate head-to-head stats
    head_to_head = match_data[
        ((match_data['team1'] == team1) & (match_data['team2'] == team2)) |
        ((match_data['team1'] == team2) & (match_data['team2'] == team1))
    ]
    
    team1_wins = (head_to_head['winner'] == team1).sum()
    team2_wins = (head_to_head['winner'] == team2).sum()
    
    # Display head-to-head metrics
    st.subheader(f"{team1} vs {team2}")
    
    metric_col1, metric_col2, metric_col3 = st.columns(3)
    with metric_col1:
        st.metric("Total Matches", len(head_to_head))
    with metric_col2:
        st.metric(f"{team1} Wins", team1_wins)
    with metric_col3:
        st.metric(f"{team2} Wins", team2_wins)

if __name__ == "__main__":
    main() 