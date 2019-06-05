from django.http import JsonResponse
from django.core import serializers
import requests 
import objectpath
import json
import sys
import datetime

def index(request):

    # NHL API CALL 1
    # get all goalie games (hardcoded to 2018-2019 season by start and end dates)
    r_url = "https://api.nhle.com/stats/rest/goalies?isAggregate=false&reportType=goalie_basic&isGame=true&reportName=goaliesummary&sort=[{%22property%22:%22wins%22,%22direction%22:%22DESC%22}]&cayenneExp=leagueId=133%20and%20gameDate%3E=%222018-10-07%22%20and%20gameDate%3C=%222019-04-10%2023:59:59%22%20and%20gameTypeId=2"
    r = requests.get(r_url)

    goalie_name = request.GET.get('goalie_name', '')

    # parse goalie games listing for querying
    tree = objectpath.Tree(r.json())
    result = tree.execute(f"$.data[@.playerName is '{goalie_name}']")

    ids = [] # keep track of game ids for the goalie
    goalie_team_abbrev = "not found"

    # Save game_ids list
    for game in result:
        ids.append(game['gameId'])
        goalie_team_abbrev = game['teamAbbrev']

    # Return if goalie not found with 404 not found response
    if goalie_team_abbrev == 'not found':
        return JsonResponse({"error": "goalie not found"}, safe=False, status=404) 

    # determine team id for goalie
    team_id = team_id_from_abbrev(goalie_team_abbrev)

    # NHL API CALL 2
    # get all skater game records for the goalie's team
    r_url_2 = ("https://api.nhle.com/stats/rest/skaters?isAggregate=false&reportType=basic&isGame=true&reportName=skaterpowerplay&sort=[{%22property%22:%22ppPoints%22,%22direction%22:%22DESC%22},{%22property%22:%22ppGoals%22,%22direction%22:%22DESC%22},{%22property%22:%22ppAssists%22,%22direction%22:%22DESC%22}]&factCayenneExp=gamesPlayed%3E=1&cayenneExp=leagueId=133%20and%20gameDate%3E=%222018-10-03%22%20and%20gameDate%3C=%222019-05-04%2023:59:59%22%20and%20gameTypeId=2%20and%20teamId=" + str(team_id))
    r2 = requests.get(r_url_2)

    # save a record to this array after parsing each goalie's game for the skaters
    game_summaries = []

    # season summary counters
    total_pp_time = 0
    total_pp_shots = 0
    total_pp_goals = 0
    total_pp_assists = 0

    # parse game records to tree for querying in loop
    tree1 = objectpath.Tree(r2.json())

    for gameId in ids:
        # game summary counters
        game_pp_time_sum = 0
        game_pp_shots_sum = 0
        game_pp_goals_sum = 0
        game_pp_assists_sum = 0
        player_records_count = 0
        opp_team = ''

        # query game records for current goalie's game
        records = tree1.execute(f'$.data[@.gameId is "{gameId}"]')

        # parse each skater's game record
        for player in records:
            # update game summary counters
            game_pp_time_sum += player['ppTimeOnIce']
            game_pp_shots_sum += player['ppShots']
            game_pp_assists_sum += player['ppAssists']
            game_pp_goals_sum += player['ppGoals']
            opp_team = player['opponentTeamAbbrev']
            if player['ppTimeOnIce'] > 0:
                player_records_count += 1

        # update season summary counters
        total_pp_time += game_pp_time_sum
        total_pp_shots += game_pp_shots_sum
        total_pp_goals += game_pp_goals_sum
        total_pp_assists += game_pp_assists_sum

        # format final game summary and add to list
        gs = {
            'gameId': gameId,
            'opp_team': opp_team,
            'num_players_with_pp_time': player_records_count,
            'total_player_pp_time': str(datetime.timedelta(seconds=game_pp_time_sum)),
            'total_pp_shots': game_pp_shots_sum,
            'total_pp_goals': game_pp_goals_sum,
            'total_pp_assists': game_pp_assists_sum
        }
        game_summaries.append(gs)

    # format season stats to be returned
    season_stats = {
        'goalie_name': goalie_name,
        'team_abbrev': goalie_team_abbrev,
        'team_id': team_id,
        'num_games': len(game_summaries),
        'total_pp_time': str(datetime.timedelta(seconds=total_pp_time)),
        'total_pp_shots': total_pp_shots,
        'total_pp_goals': total_pp_goals,
        'total_pp_assists': total_pp_assists,
        'avg_pp_shots_per_60_mins': ((float(total_pp_shots)/float(total_pp_time)) * 3600), # rate per sec * num secs in hour
        'avg_pp_goals_per_60_mins': ((float(total_pp_goals)/float(total_pp_time)) * 3600),
        'avg_pp_assists_per_60_mins': ((float(total_pp_assists)/float(total_pp_time)) * 3600)
    }

    # format final return json
    rtn = {
        'season_summary': season_stats,
        'game_summaries': game_summaries
    }

    # return data with 200 response code
    return JsonResponse(rtn, safe=False) 


def team_id_from_abbrev(goalie_team_abbrev):
    # seems to be no logic ordering to these team ids...
    team_abbrev_with_id = {
		"ANA" : 24,
		"ARI" : 53,
		"BOS" : 6,
		"BUF" : 7,
		"CGY" : 20,
		"CAR" : 12,
        "CHI": 16,
        "COL": 21,
        "CBJ": 29,
        "DAL": 25,
        "DET": 17,
        "EDM": 22,
        "FLA": 13,
        "LAK": 26,
        "MIN": 30,
        "MTL": 8,
        "NSH": 18,
        "NJD": 1,
        "NYI": 2,
        "NYR": 3,
        "OTT": 9,
        "PHI": 4,
        "PIT": 5,
        "SJS": 28,
        "STL": 19,
        "TBL": 14,
        "TOR": 10,
        "VAN": 23,
        "VGK": 54,
        "WSH": 15,
        "WPG": 52
	}

    return team_abbrev_with_id[goalie_team_abbrev]