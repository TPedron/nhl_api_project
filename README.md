# NHL API Project

## Summary

This project is a very simple Python/ Django application I wrote in one evening.

Through monitoring HTTP requests that http://www.nhl.com/stats/player? makes when running its various reports, I captured the undocumented GET calls being made and wrote a wrapper API that will retrieve and aggregate the Powerplay stats for a goale's teams in games they played.  This could show if certain goalies help to influence their team's Powerplay in some way (confidence instilled in team allowing them to take further risks, puck playing ability on zone clearances, etc.)

## Setup

First, if you don't already have it installed, please install Docker following the steps at https://docs.docker.com/install/. You will also need the docker-compose tool which can be installed easily through a package manager such as brew with brew install docker-compose.

Next, run git clone `https://github.com/TPedron/nhl_api_project.git` to clone the repository to your local machine, then continue on to each subsection below.

Note that both projects will need to be brought up together so the application can perform.

Then run the following commands in the project root directory:

```
docker-compose build
docker-compose up
```

That will bring the application up and running.

Then, go to your web browser of a tool such as Postman and follow the API instructions below.

## API

### Request
There is a single `GET` resource exposed by this application called `/goalie_pp_support`.  It accepts a single query parameter called `goalie_name` which is the first name & last name of a goalie to retrieve data for.

**Format:** 
```
http://localhost:8000/goalie_pp_support/?goalie_name=<goalie_first_name goalie_last_name>
```

**Example:**
For example, we can retrieve the Toronto Maple Leafs' powerplay statistics for games  Freddy Andersen played in with the following request:
```
http://localhost:8000/goalie_pp_support/?goalie_name=Frederik%20Andersen
```

### Response

#### Success

**Request:** (I chose a goalie with only 1 game played last season to have a small payload example)

```
http://localhost:8000/goalie_pp_support/?goalie_name=Charlie%20Lindgren
```

**Response:**

*Status Code = 200*

```json
{
    "season_summary": {
        "goalie_name": "Charlie Lindgren",
        "team_abbrev": "MTL",
        "team_id": 8,
        "num_games": 1,
        "total_pp_time": "0:00:30",
        "total_pp_shots": 1,
        "total_pp_goals": 2,
        "total_pp_assists": 1
    },
    "game_summaries": [
        {
        "gameId": 2018021259,
        "opp_team": "TOR",
        "num_players_with_pp_time": 5,
        "total_player_pp_time": "0:00:30",
        "total_pp_shots": 1,
        "total_pp_goals": 1,
        "total_pp_assists": 2
        }
    ]
}
```


#### Failure

If the provided `goalie_name` query param cannot be found in the NHL database, the following error response is returned:

**Request:**
```
http://localhost:8000/goalie_pp_support/?goalie_name=Tom%20Pedron
```

**Response:**

*Status Code = 404*

```json
{
    "error": "goalie not found"
}
```

## Limitations Due to NHL API

The NHL API I am leveraging is not documented and technically not a public API.  It is not very flexible and does not expose a "normalized data model" in ways that are queryable (unable to search for associated data to returned data records).  Its responses are also not meant to be used for data retrieval purposes in apps such as this.  As a result, there is a lot of data processed here and a lot of it is not actually needed for the aggregations made.

The flow is as such:

* First, get a listing of all goalie game summaries from the 2018-2019 season
    * Search through it to find the provided `goalie_name`
        * If found, continue
        * If not found, return error json
* Filter on the above list to save a list of all game_ids for games the desired goalie played in during the season
* Get a listing of all player stats from all games played by skaters for the same team as the goalie (They do not allow you to query from specific games like I would like to do with the game_ids list)
* For each game the goalie played, query the player stats listing for records from that game, update powerplay counts for game and season summaries
* Return season and game summaries json

Access to a proper data stream for the purposes of this app would change this flow to be more optimized and process much less data.

As well, the NHL assigns each team a `team_id` however there seems to be no logical ordering to it.  The `team_id_from_abbrev` helper function in `views.py` holds a hardcoded mapping of team abbreviation to team_id which is not ideal but is the best I have for now.

## Areas For Improvement

Obviously, since this app was put together in a single evening, there are many areas for improvement.
* All of the logic is held in the the single index view which is not very clean.
* There are no player/team/game models that would easy the data parsing and processing steps.
* There is no caching of data records (this app retrieves a lot of data repeatedly rom the NHL API)
* The endpoint is not very RESTful and not really even an index call
    * Ideally the index endpoint would be set up as `goalies/` and would return a list of goalie ids.
    * Using those goalie_ids, you would then make a call such as `goalies/<goalie id>/pp_support` to retrieve the individual goalie powerplay support stats.




