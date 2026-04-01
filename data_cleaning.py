import pandas as pd

# --- Load Data ---
df = pd.read_csv('season_stats.csv')
team_df = pd.read_csv('team_stats.csv')

# --- Merge ---
combined_df = df.merge(team_df, on=["team", "year", "conf"], how="left")

# --- Filter & Drop Columns ---
combined_df = combined_df[combined_df['g'] >= 5]

combined_df = combined_df.drop(columns=[
    "num", "g", "ppg", "oreb", "dreb", "rpg", "apg", "tov", "spg",
    "efg", "id", "fgm", "ftm", "fta", "two_a", "two_m", "three_m", "three_a",
    "dunk_m", "dunk_a", "dunk_pct", "rim_m", "rim_a", "mid_m", "mid_a", "pick", "fga",
    "barthag_rk", "adj_o_rk", "adj_d_rk", "adj_t_rk", "seed", "rec"
])

# --- Transfer Feature Engineering ---
combined_df = combined_df.sort_values(["player", "year"])

combined_df["previous_team"] = combined_df.groupby("player")["team"].shift(1)
combined_df["previous_conference"] = combined_df.groupby("player")["conf"].shift(1)

combined_df["is_transfer"] = (
    combined_df["previous_team"].notna() &
    (combined_df["team"] != combined_df["previous_team"])
)

combined_df.loc[~combined_df["is_transfer"], "previous_team"] = pd.NA
combined_df.loc[~combined_df["is_transfer"], "previous_conference"] = pd.NA

previous_stats = ["ortg", "drtg", "ts", "usg", "porpag", "adj_oe", "adj_de", "bpm", "adj_o", "adj_d", "barthag"]
for stat in previous_stats:
    col = "previous_team_adjo" if stat == "adj_o" else \
          "previous_team_adjd" if stat == "adj_d" else f"previous_{stat}"
    combined_df[col] = combined_df.groupby("player")[stat].shift(1)

# --- Change Columns ---
combined_df["change_ortg"]      = combined_df["ortg"]    - combined_df["previous_ortg"]
combined_df["change_drtg"]      = combined_df["drtg"]    - combined_df["previous_drtg"]
combined_df["change_ts"]        = combined_df["ts"]      - combined_df["previous_ts"]
combined_df["change_usg"]       = combined_df["usg"]     - combined_df["previous_usg"]
combined_df["change_porpag"]    = combined_df["porpag"]  - combined_df["previous_porpag"]
combined_df["change_adj_oe"]    = combined_df["adj_oe"]  - combined_df["previous_adj_oe"]
combined_df["change_adj_de"]    = combined_df["adj_de"]  - combined_df["previous_adj_de"]
combined_df["change_bpm"]       = combined_df["bpm"]     - combined_df["previous_bpm"]
combined_df["change_team_adjo"] = combined_df["adj_o"]   - combined_df["previous_team_adjo"]
combined_df["change_team_adjd"] = combined_df["adj_d"]   - combined_df["previous_team_adjd"]
combined_df["change_barthag"]   = combined_df["barthag"] - combined_df["previous_barthag"]

# --- Transfer Subsets ---
df_transfers = combined_df[combined_df["is_transfer"] == True].copy()
df_transfers = df_transfers[
    (df_transfers["change_bpm"] >= -30) & (df_transfers["change_bpm"] <= 30) &
    (df_transfers["mpg"] >= 5)
]

a10_transfers = df_transfers[df_transfers["conf"] == "A10"].copy()

# --- Barthag Movement Category ---
def categorize_barthag_movement(change_barthag):
    if pd.isna(change_barthag):
        return None
    elif change_barthag > 0.1:
        return "up"
    elif change_barthag < -0.1:
        return "down"
    else:
        return "lateral"

df_transfers["barthag_movement"] = df_transfers["change_barthag"].apply(categorize_barthag_movement)
a10_transfers["barthag_movement"] = a10_transfers["change_barthag"].apply(categorize_barthag_movement)
