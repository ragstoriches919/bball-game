import pandas as pd
import numpy as np
import datetime
import nba_stats as stats

import cfg as c

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Helper Functions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def list_diff(li1, li2):

    """
    Get difference of two lists
    :param li1: List
    :param li2: List
    :return: List
    """

    li_dif = [i for i in li1 + li2 if i not in li1 or i not in li2]
    return li_dif


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Work Functions
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
       'rebounds', 'rebounds_per_game', 'made_three_point_field_goals_per_game', 'field_goal_pct',
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
    df_ranks = df_all.loc[df_all["minutes_played"] >= min_minutes_played]

    cols_groupby = ['position']
    for col in cols_stats:
        df_ranks[col + "_pctRank"] = df_ranks.groupby(cols_groupby)[col].rank(pct=True)
        df_ranks[col + "_pctRankOverall"] = df_ranks[col].rank(pct=True)

    df_ranks.to_pickle(c.PICKLE_PATH_PCT_RANKS)

    return df_ranks


def helper_get_df_scores(dict_weights):

    """
    Get scores for any set of columns/weights
    :param dict_weights: Dictionary Ex.) {"true_shooting_percentage": 0.4,"made_three_point_field_goals": 0.4, "field_goal_pct": 0.2}
    :return: DataFrame
    """

    df_ranks = pd.read_pickle(c.PICKLE_PATH_PCT_RANKS)
    cols_id = ["slug", "name", "age", "position"]
    df_scores = df_ranks[cols_id]
    df_scores["score"] = 0

    for key in dict_weights:
        df_scores[key + "_score"] = (df_ranks[key + "_pctRank"] * dict_weights[key] * 0.5) + \
                                    (df_ranks[key + "_pctRankOverall"] * dict_weights[key] * 0.5)

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
                    "made_three_point_field_goals_per_game": 0.4,
                    "field_goal_pct": 0.2}

    df_shooter = helper_get_df_scores(dict_weights)
    df_shooter = df_shooter.rename(columns = {"score": "score_shooter"})

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
    df_scorer = df_scorer.rename(columns = {"score": "score_scorer"})


    return df_scorer


def get_df_score_rebounder():

    """
    Get rebounder scores
    :param df_ranks: DataFrame, from get_df_pct_ranks()
    :return: DataFrame
    """

    dict_weights = {"rebounds_per_game": 0.5,
                    "total_rebound_percentage": 0.5}

    df_rebounder = helper_get_df_scores(dict_weights)
    df_rebounder = df_rebounder.rename(columns={"score": "score_rebounder"})

    return df_rebounder


def get_df_score_passer():

    """
    Get passer scores
    :param df_ranks: DataFrame, from get_df_pct_ranks()
    :return: DataFrame
    """

    dict_weights = {"assists_per_game": 0.5,
                    "assist_percentage": 0.5}

    df_passer = helper_get_df_scores(dict_weights)
    df_passer = df_passer.rename(columns={"score": "score_passer"})

    return df_passer


def get_df_score_defender():

    """
    Get defender scores
    :param df_ranks: DataFrame, from get_df_pct_ranks()
    :return: DataFrame
    """

    dict_weights = {"defensive_win_shares": 0.5,
                    "steal_percentage": 0.25,
                    "block_percentage": 0.25}

    df_defender = helper_get_df_scores(dict_weights)
    df_defender = df_defender.rename(columns={"score": "score_defender"})

    return df_defender


def get_df_player_caliber(df_all_scores):

    df_all_scores["rank_player"] = df_all_scores["score_agg"].rank(ascending=False)
    df_all_scores["rank_player_pct"] = df_all_scores["score_agg"].rank(pct=True)

    df_all_scores["caliber"] = np.where(df_all_scores["rank_player"] <= 5, "superstar",
                                        np.where(df_all_scores["rank_player"] <= 40, "star",
                                                 np.where(df_all_scores["rank_player"] <= 150, "role_player", "bench_warmer")))

    return df_all_scores


def get_df_player_labels(df_all_scores):

    slice = df_all_scores[['score_defender', 'score_passer', 'score_rebounder', 'score_scorer', 'score_shooter']]
    index_list = np.argsort(-slice.values, axis=1)
    array_col_order = slice.columns[index_list]
    df_temp = pd.DataFrame(data = array_col_order)

    for col in df_temp.columns:
        df_temp[col] = df_temp[col].str.replace("score_", "")
    #
    df_temp["labels_ordered"] = ""
    for col in df_temp.columns:
        if col != "labels_ordered":

            if col == df_temp[4].name:
                df_temp["labels_ordered"] += (df_temp[col].astype(str))
            else:
                df_temp["labels_ordered"] += (df_temp[col].astype(str) + ",")

    df_all_scores = df_all_scores.reset_index(drop=True)
    df_all_scores = df_all_scores.join(df_temp, lsuffix='_left', rsuffix='_right')

    # Finally, assign the labels!
    df_all_scores["labels"] = np.where(df_all_scores["caliber"] == "superstar", df_all_scores["labels_ordered"].str.split(",").str[:4],
                                       np.where(df_all_scores["caliber"] == "star", df_all_scores["labels_ordered"].str.split(",").str[:3],
                                       np.where(df_all_scores["caliber"] == "role_player", df_all_scores["labels_ordered"].str.split(",").str[:2],
                                                df_all_scores["labels_ordered"].str.split(",").str[:1])))

    return df_all_scores


def get_df_all_scores(year, use_pickle=False):

    """
    Combination of player scores, basic + advanced stats, and pct ranks
    The big data set!
    :param year: Integer Ex.) 2021
    :param use_pickle: Boolean
    :return: DataFrame
    """

    cols_id = ["slug", "name", "age", "position"]

    if not use_pickle:
        stats.get_df_all_stats(year, use_pickle=use_pickle)

    df_scorer = get_df_score_scorer()
    df_shooter = get_df_score_shooter()
    df_passer = get_df_score_passer()
    df_rebounder = get_df_score_rebounder()
    df_defender = get_df_score_defender()

    df_all_scores = pd.merge(df_scorer, df_shooter, on=cols_id)
    df_all_scores = pd.merge(df_all_scores, df_passer, on=cols_id)
    df_all_scores = pd.merge(df_all_scores, df_rebounder, on=cols_id)
    df_all_scores = pd.merge(df_all_scores, df_defender, on=cols_id)

    df_all_scores["score_agg"] = 0
    for col in df_all_scores.columns:
        if "score_" in col and col != "score_agg":
            df_all_scores["score_agg"] += df_all_scores[col]

    df_all_scores = df_all_scores.sort_values(by=["score_agg"], ascending=False)

    # Add year
    df_all_scores["year"] = year

    # Re-Order Columns
    cols_score = []
    for col in df_all_scores.columns:
        if "score_" in col:
            cols_score.append(col)
    cols_score.sort()
    cols_in_order = cols_id + cols_score + list_diff(list(df_all_scores.columns), (cols_id + cols_score) )
    df_all_scores = df_all_scores[cols_in_order]

    df_all_scores.to_pickle(c.PICKLE_PATH_ALL_SCORES)
    df_all_scores.to_csv('scores.csv', index=False)
    return df_all_scores


def get_df_all_player_stats_in_one_year(year, use_pickle=False):

    df_all_stats = get_df_all_scores(year, use_pickle=use_pickle)
    df_all_stats = get_df_player_caliber(df_all_stats)
    df_all_stats = get_df_player_labels(df_all_stats)

    df_all_stats.to_pickle(c.PICKLE_PATH_ALL_SCORES)
    df_all_stats.to_csv('scores.csv', index=False)


    return df_all_stats

#
# def get_df_all_scores_and_labels(year, use_pickle=False):
#
#     if use_pickle:
#         df_all_scores = pd.read_pickle(c.PICKLE_PATH_ALL_SCORES)
#     else:
#         df_all_scores = get_df_all_scores(year, use_pickle=False)
#
#     df_all_scores = get_df_player_labels(df_all_scores)
#
#     df_all_scores.to_pickle(c.PICKLE_PATH_ALL_SCORES)
#     df_all_scores.to_csv('scores.csv', index=False)
#
#     return df_all_scores


def get_df_all_scores_for_all_years():

    """
    Returns all scores and stats for all players in every year.
    :return: DataFrame
    """

    df_all_scores = None

    for year in range(2000, datetime.datetime.today().year + 1):
        df = get_df_all_player_stats_in_one_year(year, use_pickle=False)
        if df_all_scores is None:
            df_all_scores = df
        else:
            df_all_scores = pd.concat([df_all_scores, df])
        # print(df.columns)


    df_all_scores.to_pickle(c.PICKLE_PATH_ALL_SCORES_ALL_YEARS)

    return df_all_scores


def get_df_random_players(year, num_players, caliber=None, label=None, use_pickle=False):

    if use_pickle:
        df_scores = pd.read_pickle(c.PICKLE_PATH_ALL_SCORES_ALL_YEARS)
        df_scores = df_scores.loc[df_scores["year"]==year]
    else:
        df_scores = get_df_all_player_stats_in_one_year(year, use_pickle=use_pickle)

    # Caliber
    if caliber is not None:
        df_scores = df_scores.loc[df_scores["caliber"] == caliber.lower()]

    # Label
    if label is not None:
        df_scores = df_scores.loc[df_scores["position"].str.contains(label)]

    df_players = df_scores.sample(num_players)
    df_players = df_players.sort_values(by="score_agg", ascending=False)

    print(df_players)

    return df_players

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Main Function
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if __name__ == '__main__':

    # get_df_all_scores(2021, use_pickle=False)
    # df_all_scores = pd.read_pickle(c.PICKLE_PATH_ALL_SCORES)
    # df = get_df_player_labels(df_all_scores)
    # print(df)

    # get_df_all_scores_for_all_years()

    get_df_random_players(2021, 10, caliber="star")

    # df = get_df_all_player_stats_in_one_year(2000)
    # print(df)