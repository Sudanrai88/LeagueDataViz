import pandas as pd
from pathlib import Path
# gamemodes are classic or aram so far, change this to either "classic" or "aram" to save the data
gamemode = "classic"
# --- PARAMETERS ---
CSV_IN = Path(f'C:/Users/SudanRai/.spyder-py3/PythonProjects/Model1/data/{gamemode}_stats.csv')
CSV_OUT = Path(f'C:/Users/SudanRai/.spyder-py3/PythonProjects/Model1/data/{gamemode}_stats_radar_ready.csv')
CSV_OUT_2 = Path(f'C:/Users/SudanRai/.spyder-py3/PythonProjects/Model1/data/{gamemode}_stats_radar_ready_short.csv')
ROLE_COL = "role"          # change here if needed

# --- 1. LOAD ---
df = pd.read_csv(CSV_IN)

# Drop any duplicate metric columns that end with ".1"
dupe_cols = [c for c in df.columns if c.endswith(".1")]
if dupe_cols:
    df = df.drop(columns=dupe_cols)

# --- 2. IDENTIFY NUMERIC METRICS ---
numeric_cols = df.select_dtypes(include="number").columns.tolist()

# --- 3. ROLE‑AWARE MIN‑MAX NORMALISATION, this is completed against ALL players that the selected 'name_dict' has played with (past 100 games) ---
norm_df = df.copy()
for col in numeric_cols:
    # Compute 1st and 93rd percentiles for each role, this can be played around with to make your group of friends look better or worse
    # e.g. 0.01 and 0.93 are the 1st and 93rd percentiles, respectively.
    role_q = df.groupby(ROLE_COL)[col].quantile([0.01, 0.93]).unstack()
    role_q.columns = ["q05", "q95"]

    r05 = df[ROLE_COL].map(role_q["q05"])
    r95 = df[ROLE_COL].map(role_q["q95"])

    denom = (r95 - r05).where((r95 - r05) != 0, 1)  # prevent divide-by-zero
    norm_df[col + "_norm"] = ((df[col] - r05) / denom).clip(0, 1)  # Clip to [0, 1] range

norm_df.to_csv(CSV_OUT_2)
