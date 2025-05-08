League of Legends Radar Chart Performance Dashboard (Find the inter*)

This project extracts, aggregates, normalizes, and visualizes **League of Legends match data** into radar charts for comparative analysis across different roles (Carry, Jungle, Support, ARAM). It mimics a potential application in HR analytics—such as department- or employee-level visual metric dashboards (e.g. absence, ER cases, turnover).

## 📊 Features

- ✅ Pull match data from the Riot Games API
- ✅ Track player accounts and match histories
- ✅ Normalize player performance across key metrics using role-based quantiles
- ✅ Visualize each player's performance vs. role average using radar charts
- ✅ Supports multiple roles and game modes: `classic` and `aram`

---
1. Extract and Process Match Data - Add your own friends etc, add riot_api to .env as LEAGUE_API_KEY
python main.py
2. Normalize the Data - Change to choose gamemode (classic / aram)
python normalize_data.py
3. Generate Radar Charts - Add the people to generate 
python visualise_data.py

Output: Carry1.png, Jungle1.png, Support1.png, Aram1.png in /data

---
🧱 Project Structure
Model1/
│
├── src/
│ └── service/
│ └── api_service.py # Functions for API interaction and data aggregation
│
├── data/
│ └── *.csv # Match data storage and radar-ready processed files
│
├── main.py # Pulls match data, calculates feature metrics
├── normalize_data.py # Role-aware normalization and radar prep
├── visualise_data.py # Radar chart generation using pycirclize
├── .env # Add your own Riot API Key

---
Setup:
pip install pandas python-dotenv matplotlib pycirclize

Next steps:

Looking to integrate this into a discord bot with rules -> /find ["summonerName, tag"]. which will give a chart for the selected users.
This may need a database, mabye looking into user MMR or ranking so it can take averages / upper lower bands from this ranking.
This will need some sort of storage that is permanent, a local db of somesort or mabye a s3 bucket. May not need to be relational?

*It was me in top lane, ap jax top...
