from django.http import JsonResponse
from django.core import serializers
import requests 
import objectpath
import json
import sys

def index(request):

    # get all goalie games
    r_url = "https://api.nhle.com/stats/rest/goalies?isAggregate=false&reportType=goalie_basic&isGame=true&reportName=goaliesummary&sort=[{%22property%22:%22wins%22,%22direction%22:%22DESC%22}]&cayenneExp=leagueId=133%20and%20gameDate%3E=%222018-10-07%22%20and%20gameDate%3C=%222019-04-10%2023:59:59%22%20and%20gameTypeId=2"
    r = requests.get(r_url)
    
    print('Ran API request')

    # print(r.json()['data'])

    tree = objectpath.Tree(r.json())
    result = tree.execute('$.data[@.playerName is "Carey Price"]')

    print('result 1')
    print(result)
    print('result 2')

    ids = []

    print('entries 1')
    for game in result:
        print(game)
        ids.append(game['gameId'])
    print('entries 2')

    # tree_obj = objectpath.Tree(r.json()['data'])

    # print(tree_obj)

    # print('Generated tree with objectpath')

    # search for games by goalie X
    # game_records = tree_obj.execute('$..[?(@.playerName == "Jack Campbell")].gameId')
    
    # print('Got games from object tree')

    # # for each game, get team's pp stats
    # for entry in game_records:
    #     print(entry['gameId'])

    print(ids)

    # for gameId in ids:
        


    # games_serialized = serializers.serialize('json', ids)

    return JsonResponse(json.dumps(ids), safe=False) 