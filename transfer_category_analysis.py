"""
Transfer Portal Player Category Analysis
Categories:
  A — Elite Rebounders  (high oreb_rate only)
  B — Elite Playmakers  (high ast_to only)
  C — Two-Way Engines   (high in BOTH)
Team success proxy: barthag (overall team strength) and wab (wins above bubble)
"""

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from scipy import stats

# ---------------------------------------------------------------------------
# 0. Load & merge
# ---------------------------------------------------------------------------
BASE = r"C:\Users\colin\OneDrive - Saint Joseph's University\Documents\SJU_Basketball_Analytics"

players = pd.read_csv(f"{BASE}/season_stats.csv")
teams   = pd.read_csv(f"{BASE}/team_stats.csv")

df = players.merge(teams, on=["team", "year", "conf"], how="left")
df = df[df["g"] >= 5].copy()

# ---------------------------------------------------------------------------
# 1. Identify transfers (same logic as data_cleaning.py)
# ---------------------------------------------------------------------------
df = df.sort_values(["player", "year"])
df["previous_team"] = df.groupby("player")["team"].shift(1)
df["is_transfer"] = df["previous_team"].notna() & (df["team"] != df["previous_team"])

# Previous-season team stats for the "before" comparison
prev_team = (
    teams.rename(columns={"barthag": "prev_barthag", "wab": "prev_wab",
                           "adj_o": "prev_adj_o", "adj_d": "prev_adj_d"})
         [["team", "year", "prev_barthag", "prev_wab", "prev_adj_o", "prev_adj_d"]]
)
df["prev_year"] = df["year"] - 1
df = df.merge(
    prev_team.rename(columns={"team": "previous_team", "year": "prev_year"}),
    on=["previous_team", "prev_year"], how="left"
)

transfers = df[df["is_transfer"]].copy()
transfers = transfers[(transfers["mpg"] >= 5) &
                      transfers["oreb_rate"].notna() &
                      transfers["ast_to"].notna()].copy()

print(f"Transfer rows available: {len(transfers)}")

# ---------------------------------------------------------------------------
# STEP 1: Define thresholds
# ---------------------------------------------------------------------------
oreb_thresh = transfers["oreb_rate"].quantile(0.75)
asto_thresh  = transfers["ast_to"].quantile(0.75)

print(f"\nThresholds")
print(f"  oreb_rate 75th pct : {oreb_thresh:.3f}")
print(f"  ast_to    75th pct : {asto_thresh:.3f}")

hi_oreb = transfers["oreb_rate"] >= oreb_thresh
hi_asto  = transfers["ast_to"]   >= asto_thresh

# ---------------------------------------------------------------------------
# STEP 2: Segment
# ---------------------------------------------------------------------------
transfers["category"] = "Other"
transfers.loc[ hi_oreb & ~hi_asto, "category"] = "A - Elite Rebounder"
transfers.loc[~hi_oreb &  hi_asto, "category"] = "B - Elite Playmaker"
transfers.loc[ hi_oreb &  hi_asto, "category"] = "C - Two-Way Engine"

cat_players = transfers[transfers["category"] != "Other"].copy()

# --- per-category summary ---
print("\n" + "="*60)
print("STEP 2: Category Counts")
print("="*60)
print(cat_players["category"].value_counts().to_string())

stat_cols = ["oreb_rate", "ast_to", "bpm", "ortg", "ts", "usg", "mpg"]
for cat in ["A - Elite Rebounder", "B - Elite Playmaker", "C - Two-Way Engine"]:
    sub = cat_players[cat_players["category"] == cat]
    print(f"\n--- {cat}  (n={len(sub)}) ---")
    print(sub[stat_cols].mean().round(3).to_string())
    print("\nPosition breakdown:")
    print(sub["pos"].value_counts().head(6).to_string())
    print("\nTop 5 conferences of origin:")
    print(sub["previous_team"].value_counts().head(5).to_string())

# ---------------------------------------------------------------------------
# STEP 3: Winning Impact
# ---------------------------------------------------------------------------
print("\n" + "="*60)
print("STEP 3: Winning Impact (destination team — barthag & wab)")
print("="*60)

for metric in ["barthag", "wab"]:
    print(f"\n  Metric: {metric}")
    for cat in ["A - Elite Rebounder", "B - Elite Playmaker", "C - Two-Way Engine"]:
        in_cat  = cat_players[cat_players["category"] == cat][metric].dropna()
        out_cat = transfers[(transfers["category"] == "Other")][metric].dropna()
        t, p = stats.ttest_ind(in_cat, out_cat, equal_var=False)
        print(f"  {cat[:22]:22s}  mean={in_cat.mean():.4f}  other mean={out_cat.mean():.4f}  p={p:.4f}")

# Before vs After (destination team)
print("\n--- Before/After: team barthag at destination vs previous school ---")
for cat in ["A - Elite Rebounder", "B - Elite Playmaker", "C - Two-Way Engine"]:
    sub = cat_players[cat_players["category"] == cat].dropna(subset=["barthag", "prev_barthag"])
    change = sub["barthag"] - sub["prev_barthag"]
    print(f"  {cat[:22]:22s}  avg barthag change: {change.mean():+.4f}  n={len(sub)}")

# Correlation: count of category players per team-year vs team barthag
print("\n--- Correlation: # category players on team vs barthag ---")
team_counts = (
    cat_players.groupby(["team", "year", "category"])
    .size()
    .reset_index(name="n_players")
    .merge(teams[["team","year","barthag","wab"]], on=["team","year"], how="left")
)
for cat in ["A - Elite Rebounder", "B - Elite Playmaker", "C - Two-Way Engine"]:
    sub = team_counts[team_counts["category"] == cat].dropna(subset=["barthag"])
    r, p = stats.pearsonr(sub["n_players"], sub["barthag"])
    print(f"  {cat[:22]:22s}  r={r:.3f}  p={p:.4f}  n={len(sub)}")

# Stacking: teams with 2+ vs exactly 1
print("\n--- Stacking check: 2+ same-category players vs 1 ---")
for cat in ["A - Elite Rebounder", "B - Elite Playmaker", "C - Two-Way Engine"]:
    sub = team_counts[team_counts["category"] == cat].dropna(subset=["barthag"])
    one  = sub[sub["n_players"] == 1]["barthag"]
    many = sub[sub["n_players"] >= 2]["barthag"]
    if len(many) >= 5:
        t, p = stats.ttest_ind(many, one, equal_var=False)
        print(f"  {cat[:22]:22s}  1-player mean={one.mean():.4f}  2+mean={many.mean():.4f}  p={p:.4f}  n2+={len(many)}")
    else:
        print(f"  {cat[:22]:22s}  not enough 2+ teams (n={len(many)})")

# ---------------------------------------------------------------------------
# STEP 4: Summary table
# ---------------------------------------------------------------------------
rows = []
for cat in ["A - Elite Rebounder", "B - Elite Playmaker", "C - Two-Way Engine"]:
    sub = cat_players[cat_players["category"] == cat]
    dest_barthag = sub["barthag"].mean()
    prev_barthag = sub["prev_barthag"].mean()
    dest_wab     = sub["wab"].mean()
    rows.append({
        "Category": cat,
        "n": len(sub),
        "Avg oreb_rate": round(sub["oreb_rate"].mean(), 3),
        "Avg ast_to":    round(sub["ast_to"].mean(), 3),
        "Avg BPM":       round(sub["bpm"].mean(), 3),
        "Dest barthag":  round(dest_barthag, 4),
        "Prev barthag":  round(prev_barthag, 4),
        "Barthag Chg":   round(dest_barthag - prev_barthag, 4),
        "Dest WAB":      round(dest_wab, 3),
    })

summary = pd.DataFrame(rows).sort_values("Dest barthag", ascending=False)
print("\n" + "="*60)
print("STEP 4: Summary Table (sorted by destination team barthag)")
print("="*60)
print(summary.to_string(index=False))

# ---------------------------------------------------------------------------
# Charts
# ---------------------------------------------------------------------------
sns.set_theme(style="whitegrid", palette="muted")
PALETTE = {
    "A - Elite Rebounder": "#2196F3",
    "B - Elite Playmaker": "#4CAF50",
    "C - Two-Way Engine":  "#FF5722",
    "Other":               "#BDBDBD",
}

# --- Chart 1: oreb_rate vs ast_to scatter with categories ---
fig, ax = plt.subplots(figsize=(9, 7))
for cat, grp in transfers.groupby("category"):
    ax.scatter(grp["oreb_rate"], grp["ast_to"],
               alpha=0.35 if cat == "Other" else 0.65,
               s=18 if cat == "Other" else 35,
               color=PALETTE[cat], label=cat, zorder=3 if cat != "Other" else 1)
ax.axvline(oreb_thresh, color="gray", linestyle="--", linewidth=1, alpha=0.7)
ax.axhline(asto_thresh,  color="gray", linestyle="--", linewidth=1, alpha=0.7)
ax.set_xlabel("oreb_rate")
ax.set_ylabel("ast_to")
ax.set_title("Transfer Players — oreb_rate vs ast_to (category segmentation)")
ax.legend(markerscale=1.8)
plt.tight_layout()
plt.savefig(f"{BASE}/chart_scatter_categories.png", dpi=150)
plt.close()
print("\nSaved: chart_scatter_categories.png")

# --- Chart 2: Destination barthag by category (box) ---
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
plot_cats = ["A - Elite Rebounder", "B - Elite Playmaker", "C - Two-Way Engine", "Other"]
for ax, metric, label in zip(axes,
                              ["barthag", "wab"],
                              ["Destination Team barthag", "Destination Team WAB"]):
    data = [transfers[transfers["category"] == c][metric].dropna().values for c in plot_cats]
    bp = ax.boxplot(data, patch_artist=True, notch=False,
                    medianprops=dict(color="black", linewidth=2))
    for patch, cat in zip(bp["boxes"], plot_cats):
        patch.set_facecolor(PALETTE[cat])
        patch.set_alpha(0.7)
    ax.set_xticks(range(1, len(plot_cats)+1))
    ax.set_xticklabels(["A\nRebounder", "B\nPlaymaker", "C\nTwo-Way", "Other"], fontsize=9)
    ax.set_ylabel(label)
    ax.set_title(label + " by Category")
plt.suptitle("Team Success at Destination School by Transfer Category", fontsize=12)
plt.tight_layout()
plt.savefig(f"{BASE}/chart_boxplot_team_success.png", dpi=150)
plt.close()
print("Saved: chart_boxplot_team_success.png")

# --- Chart 3: Barthag change (destination − previous school) ---
fig, ax = plt.subplots(figsize=(8, 5))
cats = ["A - Elite Rebounder", "B - Elite Playmaker", "C - Two-Way Engine"]
changes = []
errors  = []
for cat in cats:
    sub = cat_players[cat_players["category"] == cat].dropna(subset=["barthag", "prev_barthag"])
    ch = sub["barthag"] - sub["prev_barthag"]
    changes.append(ch.mean())
    errors.append(ch.sem() * 1.96)
colors = [PALETTE[c] for c in cats]
bars = ax.bar(["A\nRebounder", "B\nPlaymaker", "C\nTwo-Way"],
              changes, color=colors, alpha=0.75, edgecolor="black",
              yerr=errors, capsize=5, error_kw=dict(elinewidth=1.2))
ax.axhline(0, color="black", linewidth=0.8)
ax.set_ylabel("Avg barthag change (destination − previous school)")
ax.set_title("Destination vs Previous School Barthag - by Transfer Category\n(95% CI error bars)")
plt.tight_layout()
plt.savefig(f"{BASE}/chart_barthag_change.png", dpi=150)
plt.close()
print("Saved: chart_barthag_change.png")

# --- Chart 4: Top positions per category ---
fig, axes = plt.subplots(1, 3, figsize=(14, 5))
for ax, cat in zip(axes, cats):
    sub = cat_players[cat_players["category"] == cat]["pos"].value_counts().head(6)
    sub.plot(kind="barh", ax=ax, color=PALETTE[cat], alpha=0.75, edgecolor="black")
    ax.invert_yaxis()
    ax.set_title(cat.split(" — ")[-1] if " — " in cat else cat, fontsize=10)
    ax.set_xlabel("Count")
    ax.set_ylabel("")
plt.suptitle("Position Breakdown by Transfer Category", fontsize=12)
plt.tight_layout()
plt.savefig(f"{BASE}/chart_position_breakdown.png", dpi=150)
plt.close()
print("Saved: chart_position_breakdown.png")

# --- Chart 5: Summary ranking bar ---
fig, ax = plt.subplots(figsize=(8, 4))
summary_sorted = summary.sort_values("Dest barthag", ascending=True)
colors_sorted  = [PALETTE[c] for c in summary_sorted["Category"]]
ax.barh(summary_sorted["Category"], summary_sorted["Dest barthag"],
        color=colors_sorted, alpha=0.75, edgecolor="black")
ax.set_xlabel("Avg Destination Team barthag")
ax.set_title("Category Ranking by Destination Team Strength (barthag)")
plt.tight_layout()
plt.savefig(f"{BASE}/chart_category_ranking.png", dpi=150)
plt.close()
print("Saved: chart_category_ranking.png")

print("\nAnalysis complete.")
