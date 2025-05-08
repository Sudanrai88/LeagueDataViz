import pandas as pd
from pathlib import Path
# gamemodes are classic or aram so far
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

# --- 3. ROLE‑AWARE MIN‑MAX NORMALISATION ---
norm_df = df.copy()
for col in numeric_cols:
    # Compute 5th and 95th percentiles for each role
    role_q = df.groupby(ROLE_COL)[col].quantile([0.01, 0.93]).unstack()
    role_q.columns = ["q05", "q95"]

    r05 = df[ROLE_COL].map(role_q["q05"])
    r95 = df[ROLE_COL].map(role_q["q95"])

    denom = (r95 - r05).where((r95 - r05) != 0, 1)  # prevent divide-by-zero
    norm_df[col + "_norm"] = ((df[col] - r05) / denom).clip(0, 1)  # Clip to [0, 1] range

norm_df.to_csv(CSV_OUT_2)

# --- 4. LONG FORMAT (ONE ROW = ONE METRIC VALUE) ---
id_vars = [c for c in norm_df.columns if c not in numeric_cols and not c.endswith("_norm")]

raw_long = norm_df.melt(id_vars=id_vars,
                        value_vars=numeric_cols,
                        var_name="Metric",
                        value_name="Raw_Value")

norm_long = norm_df.melt(id_vars=id_vars,
                         value_vars=[c + "_norm" for c in numeric_cols],
                         var_name="Metric_norm",
                         value_name="Normalized_Value")

norm_long["Metric"] = norm_long["Metric_norm"].str[:-5]
norm_long = norm_long.drop(columns="Metric_norm")

radar_ready = pd.merge(raw_long, norm_long, on=id_vars + ["Metric"])

# --- 5. SAVE ---
radar_ready.to_csv(CSV_OUT, index=False)


print(f"File saved to: {CSV_OUT}")
