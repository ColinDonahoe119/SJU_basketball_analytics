# SJU Basketball Analytics — Transfer Portal Analysis

Analysis of NCAA men's basketball transfer portal data for Saint Joseph's University. The project segments transfer players into skill-based categories, measures their impact on team success, and builds predictive models for key performance metrics post-transfer.

---

## Dataset

| File | Description |
|---|---|
| `season_stats.csv` | Player-season statistics (per-game, efficiency, advanced) |
| `team_stats.csv` | Team-season metrics (barthag, adj_o, adj_d, adj_t, WAB) |
| `transfers.csv` | Transfer portal records |

**n = 3,840 transfer seasons** after filtering for minimum 5 games and 5 MPG.

Key metrics used: `barthag`, `WAB`, `BPM`, `oreb_rate`, `ast_to`, `ortg`, `drtg`, `ts`, `usg`, `porpag`

---

## Pipeline

```
data_cleaning.py
    └── transfer_category_analysis.py   # segmentation + team impact
    └── visualizations.py               # exploratory plots
    └── model_oreb_rate.py              # RF model: change in oreb_rate
    └── model_ast_to.py                 # RF model: change in ast/to
    └── build_pptx.py                   # generates transfers_analysis.pptx
```

---

## Files

### `data_cleaning.py`
Loads and merges player and team data, engineers transfer features:
- Identifies transfers by tracking team changes year-over-year
- Builds `previous_*` columns for each key stat (prior season values)
- Computes `change_*` columns (post-transfer minus pre-transfer)
- Exports `df_transfers` and `a10_transfers` for downstream scripts

### `transfer_category_analysis.py`
Segments transfers into three categories using 75th-percentile thresholds:

| Category | Criteria | n |
|---|---|---|
| A — Elite Rebounder | oreb_rate >= 7.70, ast/to < 1.45 | 924 |
| B — Elite Playmaker | ast/to >= 1.45, oreb_rate < 7.70 | 914 |
| C — Two-Way Engine | oreb_rate >= 7.70 AND ast/to >= 1.45 | 46 |

Key findings:
- **Two-Way Engines** land at the strongest programs (barthag 0.613, +0.104 change) and post the highest BPM (+2.55)
- **Elite Playmakers** show the largest stacking effect — teams with 2+ jump from barthag 0.544 to 0.659 (p < 0.0001)
- **Elite Rebounders** trend slightly down in program quality (-0.005 barthag change), trading up for role

Outputs 5 charts: scatter segmentation map, team success boxplots, barthag change bar chart, position breakdown, and category ranking.

### `visualizations.py`
Exploratory visualization library for the full transfer dataset and A-10 specific cuts. Functions include correlation heatmaps, BPM/usage/rating change by transfer direction (up/lateral/down in barthag), KDE plots, conference-of-origin breakdowns, and scatter plots for efficiency vs usage.

### `model_oreb_rate.py`
Random Forest model predicting `change_oreb_rate` (change in offensive rebound rate after transferring).

- **R² = 0.544 | MAE = 1.619 percentage points**
- Top features: `previous_oreb_rate` (0.38), `pos_C`, `pos_PF/C`, `mpg`, prior efficiency stats
- Key insight: a player's prior rebounding rate is by far the strongest signal — big men carry their rebounding identity across programs

### `model_ast_to.py`
Random Forest model predicting `change_ast_to` (change in assist-to-turnover ratio after transferring).

- **R² = 0.469 | MAE = 0.367**
- Top features: `previous_ast_to` (0.41), `mpg`, `adj_o` (destination offense quality), PG position tags
- Key insight: playmaking efficiency is habit-driven, but landing in a better offensive system and earning more minutes independently push ast/to upward

Both models use an 80/20 train/test split with 200 estimators, no data leakage (only pre-transfer features used).

### `build_pptx.py`
Generates `transfers_analysis.pptx` — a 13-slide presentation covering:
1. Title slide
2. Methodology & thresholds
3. Category A — Elite Rebounders
4. Category B — Elite Playmakers
5. Category C — Two-Way Engines
6. Winning impact comparison (charts)
7. The stacking effect (statistical table)
8. Player segmentation scatter map
9. Position breakdown by category
10. Summary & rankings
11. Actionable recommendations
12. oreb_rate model findings
13. ast/to model findings

---

## Requirements

```
pandas
numpy
matplotlib
seaborn
scikit-learn
scipy
python-pptx
```

Install with:
```bash
pip install pandas numpy matplotlib seaborn scikit-learn scipy python-pptx
```

---

## Usage

Run scripts in order:

```bash
python transfer_category_analysis.py   # generates charts
python model_oreb_rate.py              # trains oreb model, saves feature importance chart
python model_ast_to.py                 # trains ast/to model, saves feature importance chart
python build_pptx.py                   # builds the PowerPoint
```

`visualizations.py` can be run independently for exploratory analysis.
