import pandas as pd
import nba_api
from nba_api.stats.endpoints import commonplayerinfo
from nba_api.stats.endpoints import playercareerstats
import basketball_reference_web_scraper as bball
from basketball_reference_web_scraper import client
import cfg as c

# PICKLE_PATH_BASIC_STATS = r"C:\Users\ragst\PycharmProjects\bball_game_stats\pickled_files\stats_basic.pkl"
# PICKLE_PATH_ADV_STATS = r"C:\Users\ragst\PycharmProjects\bball_game_stats\pickled_files\stats_advanced.pkl"
# PICKLE_PATH_ALL_STATS = r"C:\Users\ragst\PycharmProjects\bball_game_stats\pickled_files\stats_all.pkl"

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Functions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def get_df_basic_player_stats(year):

    """
    Aggregates all relevant BASIC stats for players in given year
    :param year: Integer Ex.) 2021
    :return: DataFrame
    """

    basic = client.players_season_totals(season_end_year=year)

    df_basic = pd.json_normalize(basic)
    df_basic["position"] = df_basic["positions"].astype(str).str.split(":").str[1]
    df_basic["position"] = df_basic["position"].map(lambda x: x.lstrip(" '").rstrip(">]'"))

    cols_groupby = ["slug", "name", "age", "position"]
    cols_basic = ["games_played", "games_started", "minutes_played", "made_field_goals", "attempted_field_goals",
                "made_three_point_field_goals", "attempted_three_point_field_goals", "made_free_throws",
                "attempted_free_throws", "offensive_rebounds", "defensive_rebounds", "assists", "steals", "blocks",
                "turnovers", "personal_fouls", "points"]

    df_stats = df_basic.groupby(cols_groupby)[cols_basic].sum().reset_index()
    df_stats["points_per_game"] = df_stats["points"] / df_stats["games_played"]
    df_stats["assists_per_game"] = df_stats["assists"] / df_stats["games_played"]
    df_stats["rebounds"] = df_stats["offensive_rebounds"] + df_stats["defensive_rebounds"]
    df_stats["rebounds_per_game"] = df_stats["rebounds"] / df_stats["games_played"]
    df_stats["made_three_point_field_goals_per_game"] = df_stats["made_three_point_field_goals"] / df_stats["games_played"]

    df_stats["field_goal_pct"] = df_stats["made_field_goals"] / df_stats["attempted_field_goals"]
    df_stats["field_goal_pct_three_pt"] = df_stats["made_three_point_field_goals"] / df_stats["attempted_three_point_field_goals"]

    df_stats.to_pickle(c.PICKLE_PATH_BASIC_STATS)

    return df_stats


def get_df_advanced_player_stats(year):

    """
    Aggregates all relevant ADVANCED stats for players in given year
    :param year: Integer Ex.) 2021
    :return: DataFrame
    """

    adv = client.players_advanced_season_totals(season_end_year=year)
    
    df_advanced = pd.json_normalize(adv)
    df_advanced["position"] = df_advanced["positions"].astype(str).str.split(":").str[1]
    df_advanced["position"] = df_advanced["position"].map(lambda x: x.lstrip(" '").rstrip(">]'"))

    cols_groupby = ["slug", "name", "age", "position"]
    cols_adv = ['player_efficiency_rating',
       'true_shooting_percentage', 'three_point_attempt_rate',
       'free_throw_attempt_rate', 'offensive_rebound_percentage',
       'defensive_rebound_percentage', 'total_rebound_percentage',
       'assist_percentage', 'steal_percentage', 'block_percentage',
       'turnover_percentage', 'usage_percentage', 'offensive_win_shares',
       'defensive_win_shares', 'win_shares', 'win_shares_per_48_minutes',
       'offensive_box_plus_minus', 'defensive_box_plus_minus',
       'box_plus_minus', 'value_over_replacement_player']

    cols_adv_contrib = [col + "_contrib" for col in cols_adv]

    df_total_minutes = df_advanced.groupby(cols_groupby)["minutes_played"].sum().reset_index()
    df_total_minutes = df_total_minutes.rename(columns = {"minutes_played": "minutues_played_total"})

    df_stats = pd.merge(df_advanced, df_total_minutes, on=cols_groupby)
    df_stats["weight"] = df_stats["minutes_played"] / df_stats["minutues_played_total"]

    print(df_stats.columns)

    # Get contribs
    for col in cols_adv:
        df_stats[col+"_contrib"] = df_stats[col] * df_stats["weight"]

    # Aggregate contributions to get final df
    df_stats_agg = df_stats.groupby(cols_groupby)[cols_adv_contrib].sum().reset_index()

    # Remove "contrib" column name from all contrib columns
    cols_df_stats_agg = [col.replace("_contrib", "") for col in df_stats_agg.columns]
    df_stats_agg.columns = cols_df_stats_agg

    df_stats.to_pickle(c.PICKLE_PATH_ADV_STATS)

    return df_stats_agg


def get_df_all_stats(year, use_pickle=False):

    """
    Combines all relevant BASIC and ADVANCED stats for players in given year
    :param year: Integer
    :param use_pickle: Boolean
    :return:
    """

    print("Getting all stats for {}".format(year))

    cols_merge = ["slug", "name", "age", "position"]

    if use_pickle:
        df_basic = pd.read_pickle(c.PICKLE_PATH_BASIC_STATS)
        df_adv = pd.read_pickle(c.PICKLE_PATH_ADV_STATS)
    else:
        df_basic = get_df_basic_player_stats(year)
        df_adv = get_df_advanced_player_stats(year)

    df_all = pd.merge(df_basic, df_adv, on=cols_merge)

    # Remove accent marks
    df_all["name"] = df_all["name"].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')

    df_all.to_pickle(c.PICKLE_PATH_ALL_STATS)

    return df_all

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Main Function
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__ == '__main__':

    year = 2021
    # get_df_all_stats(2021, use_pickle=False)

    df = get_df_basic_player_stats(year)
    print(df)