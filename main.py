# -*- coding: utf-8 -*-
"""
@author: SudanRai

Test radar chart metrics, something similar to be done with HR data in warehouse? Can aggregate Employee/ Department metrics e.g. Turnover, Absence, Holidays taken, ER cases, WFH, Flex requests etc.
"""

import pandas as pd
import os
from dotenv import load_dotenv
import glob
from datetime import datetime
from src.service import api_service

# === Configuration ===
load_dotenv()

api_key = os.getenv('LEAGUE_API_KEY')
print(api_key)

data_dir = "C:/Users/SudanRai/.spyder-py3/PythonProjects/Model1/data"
read_ids_path = os.path.join(data_dir, "read_match_ids.csv")

#Add your own name_dict and agg_account dictionaries here
#These dictionaries map player names to their respective regions and aggregated account names.
name_dict = {
    "Bensaski": "EUW", "c1ev": "EUW", "chazzapro": "chaz", "SlashFang": "EUW",
    "Arrr": "EUW", "Combo Goblin": "EUW", "CJA IeattheGOD": "EUW",
    "Blind Insight": "EUW", "Ten Bae": "EUW", "Ieatyourdog": "EUW",
    "Postalscream": "EUW", "SIashFang": "EUW", "GandiTi": "EUW", "ProChikensPie": "EUW", "WasAecac": "EUW", "ganen": "03417", "Szabi20023": "EUW",  "nemeni": "sack", "HappyBunny52": "sleep"}
agg_account = {
    "Bensaski": "Sudan", "c1ev": "Ethan", "chazzapro": "Charlie", "SlashFang": "Theo",
    "Arrr": "Robin", "Combo Goblin": "Robin", "CJA IeattheGOD": "Fubuki",
    "Blind Insight": "Tino", "Ten Bae": "Lewis", "Ieatyourdog": "Fubuki",
    "Postalscream": "James", "SIashFang": "Sudan", "GandiTi": "Miti", "ProChikensPie": "Ohm", "WasAecac": "WasAecac", "ganen": "Sudan", "Szabi20023": "Szabi", "nemeni": "Kyle", "HappyBunny52": "Kyle"}

riotID = list(name_dict.keys())

# === Fetch New Match IDs ===
puuid_list = api_service.get_account_data(api_key, name_dict)
match_id_list = pd.Series(api_service.get_match_ids(puuid_list, api_key, 100)).drop_duplicates()

if os.path.exists(read_ids_path):
    read_ids = pd.read_csv(read_ids_path, header=None)[0].tolist()
else:
    read_ids = []

new_ids = match_id_list[~match_id_list.isin(read_ids)].reset_index(drop=True)

new_batch_paths = []

if not new_ids.empty:
    print(f"{len(new_ids)} new match IDs to process.")

    def batch_list(lst, n):
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    for i, batch in enumerate(batch_list(new_ids, 100)):
        batch_data = api_service.get_match_data(batch.tolist(), api_key)
        batch_filename = os.path.join(data_dir, f"match_batch_{timestamp}_{i}.csv")
        batch_data.to_csv(batch_filename, index=False)
        new_batch_paths.append(batch_filename)
        print(f"Batch {i + 1}: Extracted {len(batch)} matches")

    pd.Series(read_ids + new_ids.tolist()).drop_duplicates().to_csv(read_ids_path, index=False, header=False)
else:
    print("No new match IDs to process.")

# === Load and Combine New Batches ===
all_files = glob.glob(os.path.join(data_dir, "match_batch*"))
all_batches = pd.concat([pd.read_csv(f) for f in all_files], ignore_index=True)

# === Feature Selection === (Check full list of columns in the data and seelct the ones you want to keep)
selected_cols = [
    "riotIdGameName", "puuid", "challenges.damagePerMinute", "challenges.dodgeSkillShotsSmallWindow",
    "challenges.goldPerMinute", "challenges.kda", "challenges.killParticipation",
    "challenges.laneMinionsFirst10Minutes", "challenges.quickSoloKills", "challenges.saveAllyFromDeath",
    "challenges.skillshotsDodged", "challenges.survivedSingleDigitHpCount",
    "challenges.teamDamagePercentage", "challenges.visionScorePerMinute", "assists", "assistMePings",
    "championName", "championId", "damageDealtToBuildings", "damageDealtToObjectives", "dangerPings",
    "enemyMissingPings", "kills", "deaths", "dragonKills", "challenges.earlyLaningPhaseGoldExpAdvantage",
    "challenges.laningPhaseGoldExpAdvantage", "champExperience", "goldEarned", "neutralMinionsKilled",
    "totalAllyJungleMinionsKilled", "totalEnemyJungleMinionsKilled", "totalMinionsKilled",
    "challenges.laneMinionsFirst10Minutes", "challenges.maxCsAdvantageOnLaneOpponent", "win_y",
    "gameMode", "gameDuration", "challenges.turretPlatesTaken", "challenges.soloKills",
    "challenges.killParticipation", "challenges.kda", "challenges.damageTakenOnTeamPercentage",
    "totalTimeSpentDead", "teamId", "summoner1Id", "summoner2Id", "champLevel",
    "challenges.maxLevelLeadLaneOpponent", "gameId", "item0", "item1", "item2", "item3",
    "item4", "item5", "item6", "totalHealsOnTeammates", "challenges.effectiveHealAndShielding", "totalTimeCCDealt", "challenges.wardTakedownsBefore20M"
]

existing_cols = [col for col in selected_cols if col in all_batches.columns]

# Some extra columns to be added derived from the existing ones
match_data_cut = all_batches[existing_cols]
match_data_cut["junglecsPerMinute"] = match_data_cut["neutralMinionsKilled"] / (match_data_cut["gameDuration"] / 60)
match_data_cut["csPerMinute"] = match_data_cut["totalMinionsKilled"] / (match_data_cut["gameDuration"] / 60)
match_data_cut["timeDead"] = match_data_cut["totalTimeSpentDead"] / match_data_cut["gameDuration"]

#Temp storage if needed / want to check
match_data_cut.to_csv(os.path.join(data_dir, "columnValuesCut.csv"), index=False)


match_data = pd.read_csv(os.path.join(data_dir, "columnValuesCut.csv"))


api_service.aggregate_classic(match_data, riotID, agg_account, data_dir)
api_service.aggregate_aram(match_data, riotID, agg_account, data_dir)
