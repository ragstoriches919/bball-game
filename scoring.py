import pandas as pd
import nba_api
from nba_api.stats.endpoints import commonplayerinfo
from nba_api.stats.endpoints import playercareerstats
import basketball_reference_web_scraper as bball
from basketball_reference_web_scraper import client

PICKLE_PATH_BASIC_STATS = r"C:\Users\ragst\PycharmProjects\bball_game_stats\pickled_files\stats_basic.pkl"
PICKLE_PATH_ADV_STATS = r"C:\Users\ragst\PycharmProjects\bball_game_stats\pickled_files\stats_advanced.pkl"
PICKLE_PATH_ALL_STATS = r"C:\Users\ragst\PycharmProjects\bball_game_stats\pickled_files\stats_all.pkl"

import nba_stats as stats

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Functions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def get_df_pct_ranks(df_all):

    """
    Returns percentile ranks for each player for all stats.
    Percentile ranks are calculated by position.
    :param df_all: DataFrame
    :return:
    """

    cols_stats = ['games_played', 'games_started',
       'minutes_played', 'made_field_goals', 'attempted_field_goals',
       'made_three_point_field_goals', 'attempted_three_point_field_goals',
       'made_free_throws', 'attempted_free_throws', 'offensive_rebounds',
       'defensive_rebounds', 'assists', 'steals', 'blocks', 'turnovers',
       'personal_fouls', 'points', 'points_per_game', 'assists_per_game',
       'rebounds', 'rebounds_per_game', 'field_goal_pct',
       'field_goal_pct_three_pt', 'player_efficiency_rating',
       'true_shooting_percentage', 'three_point_attempt_rate',
       'free_throw_attempt_rate', 'offensive_rebound_percentage',
       'defensive_rebound_percentage', 'total_rebound_percentage',
       'assist_percentage', 'steal_percentage', 'block_percentage',
       'turnover_percentage', 'usage_percentage', 'offensive_win_shares',
       'defensive_win_shares', 'win_shares', 'win_shares_per_48_minutes',
       'offensive_box_plus_minus', 'defensive_box_plus_minus',
       'box_plus_minus', 'value_over_replacement_player']

    min_minutes_played = df_all["minutes_played"].quantile(0.3)
    df_all = df_all.loc[df_all["minutes_played"] >= min_minutes_played]

    cols_groupby = ['position']
    for col in cols_stats:
        df_all[col + "_pctRank"] = df_all.groupby(cols_groupby)[col].rank(pct=True)

    df_all.to_csv('test.csv')

    return df_all

def get_score_shooter(df):

    """

    :param df: DataFrame, from nba_stats.df.get_df_all_stats()
    :return: DataFrame
    """
    pass
    cols_groupby = ["slug", "name", "age", "position"]
    weight_tsp = 0.5
    weight_3pm = 0.3
    weight_fgp = 0.2



    pass

def get_score_scorer(df_basic, df_adv):
    pass

def get_score_rebounder(df_basic, df_adv):
    pass

def get_score_passer(df_basic, df_adv):
    pass

def get_score_defender(df_basic, df_adv):
    pass

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Main Function
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__ == '__main__':

    df = pd.read_pickle(PICKLE_PATH_ALL_STATS)

    get_df_pct_ranks(df)