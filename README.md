# T20 Cricket Analysis Project Pipeline Documentation

## Project Overview
This project is a comprehensive data analysis system for T20 cricket, focusing on player performance analysis and optimal team selection. The project follows a structured pipeline from data collection to interactive visualization.

The data we collected and cleaned is under the `data_collection_and_cleaning_output` folder.

## Project Structure
The project is organized into 5 main stages:

### 1. Web Scraping (`1_web_scrapping/`)
Files:
- `player_info_scraper.py`: Scrapes player profiles and basic information
- `batting_summary_scraper.py`: Collects detailed batting statistics
- `bowling_summary_scraper.py`: Gathers bowling performance data
- `match_results_scraper.py`: Extracts match results and team information

Purpose: Collects raw cricket data from various sources using web scraping techniques.

### 2. Data Cleaning and Transformation (`2_data_cleaning_and_transformation/`)
Files:
- `data_cleaning.py`: Main script for data preprocessing
- Output files:
  - `dim_players.csv`: Player dimension table
  - `dim_players_no_images.csv`: Player data without images
  - `fact_batting_summary.csv`: Batting statistics
  - `fact_bowling_summary.csv`: Bowling statistics
  - `dim_match_summary.csv`: Match results and context

Purpose: Cleans and transforms raw data into a structured format suitable for analysis.

### 3. Data Analysis and Visualization (`3_data_analysis_and_visualization/`)
Files:
- `cricket_analysis_1.py`: Initial analysis and basic statistics
- `cricket_analysis_2.py`: Advanced statistical analysis
- Output visualizations:
  - `bowling_economy.png`: Bowling performance analysis
  - `team_win_rates.png`: Team performance visualization

Purpose: Performs statistical analysis and generates static visualizations.

### 4. Predictive Modeling (`4_predictive_model/`)
Files:
- `predict.py`: Machine learning models and clustering
- Output:
  - `player_clusters.png`: Visualization of player clusters

Purpose: Implements machine learning models for player clustering and performance prediction.

### 5. Dashboard (`5_dashboard/`)
Files:
- `app.py`: Main Streamlit application
- `requirements.txt`: Project dependencies
- `README.md`: Dashboard documentation

Purpose: Provides an interactive interface for exploring the analysis results.

## Execution Pipeline

### Stage 1: Data Collection
1. Run web scraping scripts in order:
   ```bash
   python 1_web_scrapping/player_info_scraper.py
   python 1_web_scrapping/batting_summary_scraper.py
   python 1_web_scrapping/bowling_summary_scraper.py
   python 1_web_scrapping/match_results_scraper.py
   ```

### Stage 2: Data Cleaning
1. Execute the data cleaning script:
   ```bash
   python 2_data_cleaning_and_transformation/data_cleaning.py
   ```
   This will generate the cleaned CSV files in the same directory.

### Stage 3: Analysis
1. Run the analysis scripts:
   ```bash
   python 3_data_analysis_and_visualization/cricket_analysis_1.py
   python 3_data_analysis_and_visualization/cricket_analysis_2.py
   ```
   This will generate static visualizations and analysis results.

### Stage 4: Predictive Modeling
1. Execute the prediction script:
   ```bash
   python 4_predictive_model/predict.py
   ```
   This will generate player clusters and performance predictions.

### Stage 5: Dashboard
1. Install required dependencies:
   ```bash
   pip install -r 5_dashboard/requirements.txt
   ```
2. Run the dashboard:
   ```bash
   cd 5_dashboard
   streamlit run app.py
   ```

## File Dependencies
- Web scraping scripts generate raw data that feeds into the data cleaning process
- Cleaned CSV files from Stage 2 are used as input for analysis in Stage 3
- Analysis results and cleaned data are used for predictive modeling in Stage 4
- All previous stages' outputs are integrated into the dashboard in Stage 5

## Data Flow
1. Raw data → Web scraping scripts
2. Raw data → Data cleaning → Cleaned CSV files
3. Cleaned data → Analysis scripts → Visualizations and insights
4. Cleaned data + Analysis results → Predictive models → Player clusters
5. All previous outputs → Dashboard → Interactive visualization