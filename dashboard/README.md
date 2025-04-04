# T20 Cricket Dashboard

An interactive dashboard for analyzing T20 cricket data using Streamlit.

## Features

- Home/Overview: Key metrics (total runs, wickets, win rates)
- Batting Analysis: Top scorers, strike rate vs. boundary percentage
- Bowling Analysis: Wicket-takers, economy vs. dot ball percentage
- Player Clusters: Visualize pre-generated cluster images and player groupings
- Team Analysis: Win rates, head-to-head comparisons

## Setup and Installation

1. Make sure you have Python 3.7+ installed
2. Install the required packages:

```bash
pip install -r requirements.txt
```

## Running the Dashboard

Navigate to the dashboard directory and run:

```bash
streamlit run app.py
```

This will start the Streamlit server and open the dashboard in your default web browser.

## Data Files

The dashboard looks for the following data files:

- `../data_cleaning_and_transformation/dim_match_summary.csv`
- `../data_cleaning_and_transformation/dim_players_no_images.csv`
- `../data_cleaning_and_transformation/fact_batting_summary.csv`
- `../data_cleaning_and_transformation/fact_bowling_summary.csv`

And the following image files:

- `../data_analysis_and_visualization/team_win_rates.png`
- `../data_analysis_and_visualization/bowling_economy.png`
- `../predictive_model/player_clusters.png`

## Filtering Data

Use the sidebar to filter by:

- Teams
- Player roles (opener, all-rounder, etc.)
- Match venues (if available)
