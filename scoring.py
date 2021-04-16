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

    # df_all.to_csv('test.csv')

    return df_all


def helper_get_df_scores(dict_weights):

    """
    Get scores for any set of columns/weights
    :param dict_weights: Dictionary Ex.) {"true_shooting_percentage": 0.4,"made_three_point_field_goals": 0.4, "field_goal_pct": 0.2}
    :return: DataFrame
    """

    cols_id = ["slug", "name", "age", "position"]
    df_scores = df_ranks[cols_id]
    df_scores["score"] = 0

    for key in dict_weights:
        df_scores[key + "_score"] = df_ranks[key + "_pctRank"] * dict_weights[key]

    for key in dict_weights:
        df_scores["score"] += df_scores[key+"_score"]

    return df_scores


def get_df_score_shooter():

    """
    Get shooter scores
    :param df_ranks: DataFrame, from get_df_pct_ranks()
    :return: DataFrame
    """

    dict_weights = {"true_shooting_percentage": 0.4,
                    "made_three_point_field_goals": 0.4,
                    "field_goal_pct": 0.2}

    df_shooter = helper_get_df_scores(dict_weights)
    # df_shooter.to_csv('test.csv', index=False)
    return df_shooter


def get_df_score_scorer():

    """
    Get scorer scores
    :param df_ranks: DataFrame, from get_df_pct_ranks()
    :return: DataFrame
    """

    dict_weights = {"points_per_game": 0.4,
                    "made_field_goals": 0.3,
                    "offensive_win_shares": 0.3}

    df_scorer = helper_get_df_scores(dict_weights)

    return df_scorer


def get_df_score_rebounder():

    dict_weights = {"rebounds_per_game": 0.5,
                    "total_rebound_percentage": 0.5}

    df_rebounder = helper_get_df_scores(dict_weights)

    return df_rebounder


def get_df_score_passer():

    dict_weights = {"assists_per_game": 0.5,
                    "assist_percentage": 0.5}

    df_passer = helper_get_df_scores(dict_weights)

    return df_passer


def get_df_score_defender():

    dict_weights = {"defensive_win_shares": 0.5,
                    "steal_percentage": 0.25,
                    "block_percentage": 0.25}

    df_defender = helper_get_df_scores(dict_weights)

    return df_defender

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Main Function
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


if __name__ == '__main__':

    df = pd.read_pickle(PICKLE_PATH_ALL_STATS)

    df_ranks = get_df_pct_ranks(df)
    df = get_df_score_defender()
    df.to_csv('test.csv', index=False)
    print(df)



