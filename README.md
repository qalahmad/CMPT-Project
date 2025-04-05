# T20 Cricket Analysis and Best 11 Player Selection

## 1. Introduction and Problem Definition

This project addresses the challenge of data-driven player selection in T20 cricket. With the increasing competitiveness of T20 tournaments worldwide, team management requires objective analysis beyond traditional statistics to make optimal player selections. Our goal was to develop a comprehensive analytics system that:

1. Identifies the most valuable players across different roles (batting, bowling, all-rounders)
2. Clusters players based on performance patterns
3. Provides an interactive dashboard for visualization and decision support

The project refines the general concept of cricket analytics into a specific tool for selecting an optimal "Best 11" team based on statistical evidence rather than subjective judgment.

## 2. Data Collection and Preprocessing

### Data Sources

We collected comprehensive T20 cricket data including:

- Player profiles (dimensions, playing styles, roles)
- Match summaries (teams, venues, outcomes)
- Batting statistics (runs, strike rates, boundaries)
- Bowling statistics (wickets, economy rates, dot balls)

### Web Scraping

Data was collected using Python's BeautifulSoup and Requests libraries to extract information from cricket statistics websites. The scraping process was implemented to respect website terms of service with appropriate delays between requests.

### Data Cleaning

Several data quality issues were addressed:

- Inconsistent player name formats across different sources
- Missing values in player statistics
- Incorrectly formatted numeric fields (especially in batting statistics)
- Column name standardization (lowercasing, spaces removed)

The cleaning process transformed raw scraped data into structured CSV files:

- `dim_players.csv` and `dim_players_no_images.csv`: Player dimension tables
- `fact_bating_summary.csv`: Detailed batting statistics
- `fact_bowling_summary.csv`: Detailed bowling statistics
- `dim_match_summary.csv`: Match results and contextual information

Data transformation included:

- Converting string representations of numeric values
- Standardizing player names for reliable joining
- Calculating derived metrics like strike rates and economy rates
- Creating normalized dimensional data model for efficient analysis

## 3. Analysis Techniques

### Descriptive Statistics

We calculated comprehensive performance metrics including:

- Batting: Total runs, strike rates, boundary percentages
- Bowling: Wicket counts, economy rates, dot ball percentages
- Overall: Match win contributions, performance consistency

### Player Clustering

We implemented unsupervised machine learning (K-means clustering) to group players with similar performance profiles:

- Batters clustered by strike rate, average, and boundary percentage
- Bowlers grouped by economy rate, wicket-taking ability, and dot ball percentage
- All-rounders analyzed on combined batting and bowling metrics

### Predictive Modeling

Regression models were developed to:

- Predict player performance based on historical data
- Identify factors most strongly correlated with match outcomes
- Filter statistical noise to isolate consistent performer signals

## 4. Key Findings and Results

Our analysis revealed several significant insights:

1. **Batting Analysis**:

   - Top run-scorers were identified with detailed breakdowns of their scoring patterns
   - Clear trade-offs emerged between strike rate and consistency
   - Boundary percentage strongly correlates with match-winning contributions in T20

2. **Bowling Analysis**:

   - Economy rates showed greater impact on match outcomes than wicket counts
   - Specialist death bowlers demonstrated distinct statistical signatures
   - Dot ball percentage emerged as a critical metric for evaluating bowler effectiveness

3. **Team Performance**:

   - Win rates varied significantly across teams
   - Head-to-head statistics revealed specific team matchup dynamics
   - Home advantage quantified across different venues

4. **Player Clustering**:
   - Five distinct player archetypes emerged:
     - High-risk batters with exceptional strike rates but inconsistent scoring
     - Anchor batters who build innings with moderate strike rates
     - Economical bowlers maintaining tight lines and low economy
     - Wicket-hunting bowlers who prioritize dismissals over economy
     - Balanced all-rounders contributing meaningfully in both disciplines

## 5. Dashboard Implementation

We developed an interactive Streamlit dashboard to visualize our findings and support data-driven decision making. The dashboard includes:

1. **Home/Overview**: Key summary metrics including total matches, runs, and wickets

2. **Batting Analysis**:

   - Interactive bar charts of top run-scorers
   - Scatter plots displaying strike rate vs. boundary percentage
   - Detailed statistics tables

3. **Bowling Analysis**:

   - Visualizations of top wicket-takers
   - Economy rate analyses with comparative metrics
   - Detailed bowling statistics in tabular format

4. **Player Clusters**:

   - Visual representation of player groupings
   - Descriptive explanations of each cluster's characteristics
   - Filtering options to explore specific player types

5. **Team Analysis**:
   - Team win rate comparisons
   - Interactive head-to-head analysis between selected teams
   - Match outcome statistics

The dashboard was built using Python's Streamlit framework with data visualizations implemented through Plotly and Matplotlib. It provides filtering options for teams, player roles, and other dimensions to support targeted analysis.

## 6. Limitations and Future Work

Despite the project's achievements, several limitations should be acknowledged:

1. **Data Completeness**:

   - Player fielding statistics were not incorporated
   - Contextual factors like pitch conditions were not fully accounted for
   - Historical data was limited to recent seasons

2. **Analytical Constraints**:

   - Performance under pressure (e.g., playoffs vs. regular season) received limited analysis
   - Team chemistry factors were difficult to quantify
   - Opposition quality adjustments could be more sophisticated

3. **Technical Challenges**:
   - Real-time data updates would require API integration
   - More complex machine learning models could improve predictive accuracy
   - Dashboard performance optimization for larger datasets

Future enhancements would include:

- Integration of fielding metrics and detailed situational statistics
- Advanced machine learning techniques for more nuanced player evaluation
- Expanded API integration for automated data updates
- Opponent-adjusted performance metrics to better contextualize statistics

## Project Experience Summary

**T20 Cricket Analytics Platform Development**

Designed and implemented an end-to-end data analysis system to optimize player selection in T20 cricket. The project included web scraping data acquisition, comprehensive data cleaning, statistical analysis, machine learning modeling, and interactive dashboard development. Key accomplishments included:

- Implemented web scraping solutions to collect comprehensive player and match statistics
- Conducted thorough data preprocessing to create normalized dimensional data model
- Applied unsupervised learning techniques to identify five distinct player performance clusters
- Developed predictive models to forecast player performance and filter statistical noise
- Created an interactive Streamlit dashboard with dynamic visualizations and filtering options
- Delivered actionable insights to support data-driven "Best 11" player selection

The project demonstrates proficiency in the full data science workflow from data acquisition through analysis to interactive visualization, with practical application in sports analytics.

## Running the Project

### Requirements

To run this project, you'll need the following libraries:

- Python 3.7+
- pandas
- numpy
- matplotlib
- plotly
- streamlit
- beautifulsoup4
- requests
- scikit-learn

You can install these dependencies using:

```
pip install -r dashboard/requirements.txt
```

### Project Structure

- `web_scrapping/`: Scripts for data collection
- `data_cleaning_and_transformation/`: Data cleaning and preprocessing scripts
- `data_analysis_and_visualization/`: Analysis scripts and static visualizations
- `predictive_model/`: Machine learning models and cluster analysis
- `dashboard/`: Interactive Streamlit dashboard application

### Execution Order

1. Run the web scraping scripts to collect data (if needed)
2. Execute the data cleaning scripts
3. Run the analysis scripts to generate visualizations
4. Launch the dashboard with:
   ```
   cd dashboard
   streamlit run app.py
   ```

### Data Files

The project uses the following CSV files:

- `dim_players.csv`: Player information with images
- `dim_players_no_images.csv`: Player information without images
- `fact_bating_summary.csv`: Detailed batting statistics
- `fact_bowling_summary.csv`: Detailed bowling statistics
- `dim_match_summary.csv`: Match results and contextual information
