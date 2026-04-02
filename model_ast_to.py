import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from data_cleaning import df_transfers

# ---------------------------------------------------------------------------
# Feature selection
# Only use information available BEFORE the current season to avoid leakage:
# player profile, previous season stats, and new team context.
# ---------------------------------------------------------------------------
CATEGORICAL = ['pos', 'exp', 'hgt', 'conf']

NUMERICAL = [
    # Previous season performance
    'previous_ast_to', 'previous_bpm', 'previous_ortg', 'previous_drtg',
    'previous_ts', 'previous_usg', 'previous_porpag', 'previous_adj_oe',
    'previous_adj_de', 'previous_barthag', 'previous_team_adjo', 'previous_team_adjd',
    # New team context
    'barthag', 'adj_o', 'adj_d', 'adj_t', 'wab',
    # Change in team quality
    'change_barthag', 'change_team_adjo', 'change_team_adjd',
    # Playing time
    'mpg',
]

FEATURES = CATEGORICAL + NUMERICAL
TARGET = 'change_ast_to'

model_df = df_transfers[FEATURES + [TARGET]].dropna(subset=[TARGET])

X = model_df[FEATURES]
y = model_df[TARGET]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# ---------------------------------------------------------------------------
# Preprocessing pipeline
# ---------------------------------------------------------------------------
numerical_pipe = Pipeline([
    ('imputer', SimpleImputer(strategy='mean')),
    ('scaler', StandardScaler()),
])

categorical_pipe = Pipeline([
    ('imputer', SimpleImputer(strategy='most_frequent')),
    ('onehot', OneHotEncoder(handle_unknown='ignore')),
])

preprocessor = ColumnTransformer([
    ('num', numerical_pipe, NUMERICAL),
    ('cat', categorical_pipe, CATEGORICAL),
])

# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------
model = Pipeline([
    ('preprocessor', preprocessor),
    ('rf', RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)),
])

model.fit(X_train, y_train)
preds = model.predict(X_test)

print(f"MAE: {mean_absolute_error(y_test, preds):.3f}")
print(f"R²:  {r2_score(y_test, preds):.3f}")

# ---------------------------------------------------------------------------
# Feature importances
# ---------------------------------------------------------------------------
rf = model.named_steps['rf']
ohe_features = (
    model.named_steps['preprocessor']
    .named_transformers_['cat']
    .named_steps['onehot']
    .get_feature_names_out(CATEGORICAL)
    .tolist()
)
feature_names = NUMERICAL + ohe_features
importances = pd.Series(rf.feature_importances_, index=feature_names).sort_values(ascending=False)

plt.figure(figsize=(10, 6))
sns.barplot(x=importances.head(15).values, y=importances.head(15).index)
plt.title('Top 15 Feature Importances — change_ast_to Model')
plt.xlabel('Importance')
plt.tight_layout()
plt.show()

# ---------------------------------------------------------------------------
# Actual vs Predicted
# ---------------------------------------------------------------------------
plt.figure(figsize=(7, 6))
plt.scatter(y_test, preds, alpha=0.4)
plt.axline((0, 0), slope=1, color='red', linestyle='--', label='Perfect fit')
plt.xlabel('Actual change_ast_to')
plt.ylabel('Predicted change_ast_to')
plt.title('Actual vs Predicted change_ast_to')
plt.legend()
plt.tight_layout()
plt.show()
