import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

from data_cleaning import df_transfers, a10_transfers

MAJOR_CONFERENCES = ['ACC', 'B10', 'BE', 'SEC', 'MVC', 'MAAC', 'NEC', 'P12', 'AE', 'SC', 'Amer', 'A10']


# --- Correlation Heatmap ---
def plot_correlation_heatmap():
    change_columns = [
        'change_ortg', 'change_drtg', 'change_ts', 'change_usg',
        'change_porpag', 'change_adj_oe', 'change_adj_de', 'change_bpm',
        'change_team_adjo', 'change_team_adjd'
    ]
    plt.figure(figsize=(12, 10))
    sns.heatmap(df_transfers[change_columns].corr(), annot=True, cmap='coolwarm', fmt=".2f")
    plt.title('Correlation Matrix of Change Data')
    plt.tight_layout()
    plt.show()


# --- BPM Change by Barthag Movement ---
def plot_bpm_by_barthag():
    sns.boxplot(x='barthag_movement', y='change_bpm', data=df_transfers)
    plt.title('BPM Change by Transfer Direction')
    plt.show()


def plot_ts_by_barthag():
    sns.boxplot(x='barthag_movement', y='change_ts', data=df_transfers)
    plt.title('True Shooting Change by Transfer Direction')
    plt.show()


def plot_drtg_by_barthag():
    sns.boxplot(x='barthag_movement', y='change_drtg', data=df_transfers)
    plt.title('Defensive Rating Change by Transfer Direction')
    plt.show()


def plot_ortg_by_barthag():
    sns.boxplot(x='barthag_movement', y='change_ortg', data=df_transfers)
    plt.title('Offensive Rating Change by Transfer Direction')
    plt.show()


def plot_usg_by_barthag():
    sns.boxplot(x='barthag_movement', y='change_usg', data=df_transfers)
    plt.title('Usage Rate Change by Transfer Direction')
    plt.show()


# --- A10-Specific Barthag Movement Plots ---
def plot_a10_usg_by_barthag():
    sns.boxplot(x='barthag_movement', y='change_usg', data=a10_transfers)
    plt.title('Usage Rate Change by Transfer Direction (A10)')
    plt.show()


def plot_a10_bpm_by_barthag():
    sns.boxplot(x='barthag_movement', y='change_bpm', data=a10_transfers)
    plt.title('BPM Change by Transfer Direction in the A10')
    plt.show()


def plot_a10_drtg_by_barthag():
    sns.boxplot(x='barthag_movement', y='change_drtg', data=a10_transfers)
    plt.title('Defensive Rating Change by Transfer Direction in the A10')
    plt.show()


def plot_a10_ortg_by_barthag():
    sns.boxplot(x='barthag_movement', y='change_ortg', data=a10_transfers)
    plt.title('Offensive Rating Change by Transfer Direction in the A10')
    plt.show()


def plot_a10_usg2_by_barthag():
    sns.boxplot(x='barthag_movement', y='change_usg', data=a10_transfers)
    plt.title('Usage Rate Change by Transfer Direction in the A10')
    plt.show()


# --- KDE Plots ---
def plot_kde_bpm():
    sns.kdeplot(data=df_transfers, x='change_bpm', hue='barthag_movement', fill=True, alpha=0.5)
    plt.title('KDE: BPM Change by Barthag Movement')
    plt.show()


def plot_kde_usg():
    sns.kdeplot(data=df_transfers, x='change_usg', hue='barthag_movement', fill=True, alpha=0.5)
    plt.title('KDE: Usage Rate Change by Barthag Movement')
    plt.show()


def plot_kde_drtg():
    sns.kdeplot(data=df_transfers, x='change_drtg', hue='barthag_movement', fill=True, alpha=0.5)
    plt.title('KDE: Defensive Rating Change by Barthag Movement')
    plt.show()


# --- ANOVA Results ---
def print_anova_results():
    for metric in ['change_bpm', 'change_usg', 'change_drtg']:
        up      = df_transfers[df_transfers['barthag_movement'] == 'up'][metric]
        down    = df_transfers[df_transfers['barthag_movement'] == 'down'][metric]
        lateral = df_transfers[df_transfers['barthag_movement'] == 'lateral'][metric]
        f_stat, p_value = stats.f_oneway(up, down, lateral)
        print(f"{metric}: F={f_stat:.4f}, p={p_value:.4e}")


# --- Scatter Plots ---
def plot_bpm_scatter():
    sns.scatterplot(data=df_transfers, x='previous_bpm', y='change_bpm')
    plt.title('Previous BPM vs Change in BPM')
    plt.show()


def plot_a10_previous_conference_count():
    sns.countplot(
        x="previous_conference",
        order=a10_transfers['previous_conference'].value_counts().index,
        data=a10_transfers
    )
    plt.xticks(rotation=45, ha="right")
    plt.xlabel("Previous Conference")
    plt.ylabel("Number of Transfers")
    plt.title("Previous Conferences of Transfers into the A-10")
    plt.tight_layout()
    plt.show()


# --- BPM/USG by Previous Conference ---
def plot_bpm_by_prev_conf():
    plt.figure(figsize=(14, 7))
    sns.boxplot(
        data=df_transfers[df_transfers['previous_conference'].isin(MAJOR_CONFERENCES)],
        x="previous_conference", y="change_bpm"
    )
    plt.xticks(rotation=45, ha="right")
    plt.xlabel("Previous Conference")
    plt.ylabel("Change in BPM")
    plt.title("Change in BPM by Previous Conference (mpg >= 5)")
    plt.tight_layout()
    plt.show()


def plot_usg_by_prev_conf():
    plt.figure(figsize=(14, 7))
    sns.boxplot(
        data=df_transfers[df_transfers['previous_conference'].isin(MAJOR_CONFERENCES)],
        x="previous_conference", y="change_usg"
    )
    plt.xticks(rotation=45, ha="right")
    plt.xlabel("Previous Conference")
    plt.ylabel("Change in Usage Rate")
    plt.title("Change in Usage Rate by Previous Conference (mpg >= 5)")
    plt.tight_layout()
    plt.show()


# --- A10 Transfers by Previous Conference ---
def plot_a10_bpm_by_prev_conf():
    conf_counts = a10_transfers['previous_conference'].value_counts()
    included = conf_counts[conf_counts >= 4].index.tolist()
    plt.figure(figsize=(14, 7))
    sns.boxplot(
        data=a10_transfers[(a10_transfers['mpg'] >= 5) & (a10_transfers['previous_conference'].isin(included))],
        x="previous_conference", y="change_bpm"
    )
    plt.xticks(rotation=45, ha="right")
    plt.xlabel("Previous Conference")
    plt.ylabel("Change in BPM")
    plt.title("Change in BPM by Previous Conference (A-10 Transfers, mpg >= 5, Min 4 Transfers)")
    plt.tight_layout()
    plt.show()


def plot_a10_raw_bpm_by_prev_conf():
    conf_counts = a10_transfers['previous_conference'].value_counts()
    included = conf_counts[conf_counts >= 5].index.tolist()
    plt.figure(figsize=(14, 7))
    sns.boxplot(
        data=a10_transfers[(a10_transfers['mpg'] >= 5) & (a10_transfers['previous_conference'].isin(included))],
        x="previous_conference", y="bpm"
    )
    plt.xticks(rotation=45, ha="right")
    plt.xlabel("Previous Conference")
    plt.ylabel("BPM")
    plt.title("BPM by Previous Conference (A-10 Transfers, mpg >= 5, Min 5 Transfers)")
    plt.tight_layout()
    plt.show()


# --- TS/ORTG vs USG Scatter (A10 Transfers) ---
A10_CONF_FILTER = ['ACC', 'B10', 'BE', 'SEC', 'MVC', 'MAAC', 'NEC', 'P12', 'AE']

def plot_a10_ts_vs_usg():
    plt.figure(figsize=(10, 6))
    sns.scatterplot(
        data=a10_transfers[a10_transfers['previous_conference'].isin(A10_CONF_FILTER)],
        x="usg", y="ts", hue="previous_conference", alpha=0.7
    )
    plt.xlabel("Usage Rate")
    plt.ylabel("True Shooting %")
    plt.title("True Shooting vs Usage Rate (Transfers into the A-10)")
    plt.legend(title="Previous Conference", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    plt.show()


def plot_a10_ortg_vs_usg():
    plt.figure(figsize=(10, 6))
    sns.scatterplot(
        data=a10_transfers[
            a10_transfers['previous_conference'].isin(A10_CONF_FILTER) &
            (a10_transfers['mpg'] >= 5)
        ],
        x="usg", y="ortg", hue="previous_conference", alpha=0.7
    )
    plt.xlabel("Usage Rate")
    plt.ylabel("Offensive Rating")
    plt.title("Offensive Rating vs Usage Rate (Transfers into the A-10)")
    plt.legend(title="Previous Conference", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    plot_correlation_heatmap()
    plot_bpm_by_barthag()
    plot_ts_by_barthag()
    plot_drtg_by_barthag()
    plot_ortg_by_barthag()
    plot_usg_by_barthag()
    plot_a10_usg_by_barthag()
    plot_a10_bpm_by_barthag()
    plot_a10_drtg_by_barthag()
    plot_a10_ortg_by_barthag()
    plot_kde_bpm()
    plot_kde_usg()
    plot_kde_drtg()
    print_anova_results()
    plot_bpm_scatter()
    plot_a10_previous_conference_count()
    plot_bpm_by_prev_conf()
    plot_usg_by_prev_conf()
    plot_a10_bpm_by_prev_conf()
    plot_a10_raw_bpm_by_prev_conf()
    plot_a10_ts_vs_usg()
    plot_a10_ortg_vs_usg()
