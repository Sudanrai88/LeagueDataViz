# -*- coding: utf-8 -*-
"""
Created on Tue May  6 09:33:22 2025
@author: SudanRai
"""

import pandas as pd
import matplotlib.pyplot as plt
from pycirclize import Circos

AGG_PLAYERS = [
    "Sudan", "Ethan", "Charlie", "Theo", "Robin", "Fubuki", "Tino", "Lewis", "James", "Miti", "Ohm",
    "WasAecac", "Szabi", "Kyle", "All_carry", "All_jungle", "All_support", "All_aram"
]

BASE_PATH = "C:/Users/SudanRai/.spyder-py3/PythonProjects/Model1/data"

ROLE_CONFIGS = {
    "carry": {
        "file": f"{BASE_PATH}/classic_stats_radar_ready_short.csv",
        "filter_role": "carry",
        "output": f"{BASE_PATH}/Carry1.png",
        "ref_name": "All_carry",
        "metrics": [
            "riotIdGameName", "role", "challenges.kda_norm", "challenges.goldPerMinute_norm", "challenges.killParticipation_norm",
            "challenges.laneMinionsFirst10Minutes_norm", "challenges.teamDamagePercentage_norm", "challenges.damagePerMinute_norm",
            "challenges.visionScorePerMinute_norm", "damageDealtToObjectives_norm", "challenges.turretPlatesTaken_norm", "kills_norm",
            "deaths_norm", "assists_norm", "assistMePings_norm", "csPerMinute_norm"
        ],
        "columns": [
            "Summoner", "Role", "KDA", "Gold p/m", "Kill Participation", "Minions@10min", "Team DMG%", "DMG p/m",
            "Vision Score p/m", "Objective Damage", "Turret Plates Taken", "Kills", "Deaths", "Assists", "HELP ME pings", "CS p/m"
        ],
        "figsize": (20, 40), "dpi": 100
    },
    "jungle": {
        "file": f"{BASE_PATH}/classic_stats_radar_ready_short.csv",
        "filter_role": "jungle",
        "output": f"{BASE_PATH}/Jungle1.png",
        "ref_name": "All_jungle",
        "metrics": [
            "riotIdGameName", "role", "challenges.kda_norm", "challenges.goldPerMinute_norm", "challenges.killParticipation_norm",
            "challenges.laneMinionsFirst10Minutes_norm", "challenges.teamDamagePercentage_norm", "challenges.damagePerMinute_norm",
            "challenges.visionScorePerMinute_norm", "damageDealtToObjectives_norm", "challenges.turretPlatesTaken_norm", "kills_norm",
            "deaths_norm", "assists_norm", "assistMePings_norm", "junglecsPerMinute_norm"
        ],
        "columns": [
            "Summoner", "Role", "KDA", "Gold p/m", "Kill Participation", "LaneMinions@10min", "Team DMG%", "DMG p/m",
            "Vision Score p/m", "Objective Damage", "Turret Plates Taken", "Kills", "Deaths", "Assists", "HELP ME pings", "Jungle CS p/m"
        ],
        "figsize": (20, 40), "dpi": 100
    },
    "support": {
        "file": f"{BASE_PATH}/classic_stats_radar_ready_short.csv",
        "filter_role": "support",
        "output": f"{BASE_PATH}/Support1.png",
        "ref_name": "All_support",
        "metrics": [
            "riotIdGameName", "role", "challenges.kda_norm", "challenges.goldPerMinute_norm", "challenges.killParticipation_norm",
            "challenges.laneMinionsFirst10Minutes_norm", "challenges.teamDamagePercentage_norm", "challenges.effectiveHealAndShielding_norm",
            "totalTimeCCDealt_norm", "challenges.saveAllyFromDeath_norm", "challenges.wardTakedownsBefore20M_norm",
            "challenges.damagePerMinute_norm", "challenges.visionScorePerMinute_norm", "kills_norm", "deaths_norm",
            "assists_norm", "assistMePings_norm", "csPerMinute_norm", "enemyMissingPings_norm"
        ],
        "columns": [
            "Summoner", "Role", "KDA", "Gold p/m", "Kill Participation", "LaneMinions@10min", "Team DMG%", "Effective heal/shield",
            "CC Time", "Saved ally from death", "Ward Takedowns", "DMG p/m", "Vision Score p/m", "Kills", "Deaths", "Assists",
            "HELP ME pings", "CS p/m", "DONT INT pings"
        ],
        "figsize": (20, 40), "dpi": 100
    },
    "aram": {
        "file": f"{BASE_PATH}/aram_stats_radar_ready_short.csv",
        "filter_role": None,
        "output": f"{BASE_PATH}/Aram1.png",
        "ref_name": "All_aram",
        "metrics": [
            "riotIdGameName", "role", "challenges.kda_norm", "challenges.goldPerMinute_norm", "challenges.killParticipation_norm",
            "challenges.teamDamagePercentage_norm", "challenges.damagePerMinute_norm", "kills_norm", "deaths_norm", "assists_norm",
            "assistMePings_norm", "enemyMissingPings_norm", "timeDead_norm", "csPerMinute_norm",
            "challenges.dodgeSkillShotsSmallWindow_norm", "challenges.effectiveHealAndShielding_norm", "challenges.skillshotsDodged_norm"
        ],
        "columns": [
            "Summoner", "Role", "KDA", "Gold p/m", "Kill Participation", "Team DMG%", "DMG p/m", "Kills", "Deaths", "Assists",
            "HELP ME pings", "Why are you inting pings", "Time dead", "CS p/m", "Small window dodges", "Effective heal/shield", "Skills dodged"
        ],
        "figsize": (20, 60), "dpi": 100
    }
}

PLAYER_COLORS = {
    "Sudan": "Red", "Ethan": "skyblue", "Charlie": "lime", "James": "magenta", "Lewis": "brown", "Miti": "yellow",
    "Robin": "green", "Tino": "orange", "Theo": "purple", "Fubuki": "salmon", "Ohm": "cyan", "WasAecac": "darkgreen",
    "Szabi": "darkgray", "Kyle": "darkblue"
}


def generate_radar_charts(config: dict):
    df = pd.read_csv(config["file"])
    df = df[df["games_played"] >= 3]
    df = df[df["riotIdGameName"].isin(AGG_PLAYERS)]
    df = df[config["metrics"]]
    df.columns = config["columns"]

    if config["filter_role"]:
        df = df[df["Role"] == config["filter_role"]]

    df = df.drop(columns="Role").set_index("Summoner")
    ref_row = config["ref_name"]
    ref_data = df.loc[[ref_row]]
    player_data = df.drop(index=ref_row)

    num_plots = len(player_data)
    rows = (num_plots + 1) // 2

    fig = plt.figure(figsize=config["figsize"], dpi=config["dpi"])
    fig.subplots(rows, 2, subplot_kw=dict(polar=True))
    fig.subplots_adjust(wspace=0.5, hspace=0.2)

    for player, ax in zip(player_data.index, fig.axes):
        chart_df = pd.concat([player_data.loc[[player]], ref_data])
        cmap = PLAYER_COLORS.copy()
        cmap[ref_row] = "lightgray"

        circos = Circos.radar_chart(
            chart_df,
            vmax=1,
            fill=True,
            marker_size=6,
            cmap=cmap,
            grid_interval_ratio=0.2,
            line_kws_handler=lambda row: dict(lw=1.5, ls="dashed") if row == ref_row else dict(lw=2, ls="solid"),
            marker_kws_handler=lambda row: dict(marker="o", facecolor='none', edgecolor="darkgray", lw=1)
            if row == ref_row else dict(marker="D", ec="grey", lw=0.5),
        )
        circos.plotfig(ax=ax)
        ax.set_title(player, fontsize=20)

    fig.savefig(config["output"])


# Generate charts for all roles
for role in ROLE_CONFIGS:
    generate_radar_charts(ROLE_CONFIGS[role])
