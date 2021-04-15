import pandas as pd
import nba_api
from nba_api.stats.endpoints import commonplayerinfo
from nba_api.stats.endpoints import playercareerstats
import basketball_reference_web_scraper as bball
from basketball_reference_web_scraper import client


def get_df_player_stats(year):

    """
    Aggregates all relevant stats for players in given year
    :param year: Integer Ex.) 2021
    :return: DataFrame
    """

    basic = client.players_season_totals(season_end_year=year)

    df_basic = pd.json_normalize(basic)
    df_basic["position"] = df_basic["positions"].astype(str).str.split(":").str[1]
    df_basic["position"] = df_basic["position"].map(lambda x: x.lstrip(" '").rstrip(">]'"))

    groupby_cols = ["slug", "name", "age"]
    sum_cols = ["games_played", "games_started", "minutes_played", "made_field_goals", "attempted_field_goals",
                "made_three_point_field_goals", "attempted_three_point_field_goals", "made_free_throws",
                "attempted_free_throws", "offensive_rebounds", "defensive_rebounds", "assists", "steals", "blocks",
                "turnovers", "personal_fouls", "points"]

    df_stats = df_basic.groupby(groupby_cols)[sum_cols].sum().reset_index()
    df_stats["points_per_game"] = df_stats["points"] / df_stats["games_played"]
    df_stats["assists_per_game"] = df_stats["assists"] / df_stats["games_played"]
    df_stats["rebounds"] = df_stats["offensive_rebounds"] + df_stats["defensive_rebounds"]
    df_stats["rebounds_per_game"] = df_stats["rebounds"] / df_stats["games_played"]
    df_stats["field_goal_pct"] = df_stats["made_field_goals"] / df_stats["attempted_field_goals"]
    df_stats["field_goal_pct_three_pt"] = df_stats["made_three_point_field_goals"] / df_stats["attempted_three_point_field_goals"]

    # df_stats.to_csv('test.csv')

    adv = client.players_advanced_season_totals(season_end_year=2018)
    df_advanced = pd.json_normalize(adv)



    return df_basic

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    get_df_player_stats(2021)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
