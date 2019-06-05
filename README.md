# NHL API Project

## Summary

This project is a very simple Python/ Django application I wrote in one evening.

Through monitoring HTTP requests that the NHL's stats page (http://www.nhl.com/stats/player) makes when running its various reports, I captured the undocumented GET calls, figured out how they worked and wrote a wrapper API that will retrieve and aggregate the Powerplay stats for a given goalie's teammates in games they played in.  

This could show if certain goalies help to influence their team's Powerplay in some way (confidence instilled in team allowing them to take further risks, puck playing ability on zone clearances, etc.).  

*Of course*, it is not a very "advanced statistic" but its interesting to look at and is an example of my work with Python, Django and NHL statistics.

## Setup

First, if you don't already have it installed, please install Docker following the steps at https://docs.docker.com/install/. You will also need the docker-compose tool which can be installed easily through a package manager such as brew with `brew install docker-compose`.

Next, run `git clone https://github.com/TPedron/nhl_api_project.git` to clone the repository to your local machine.

Note that both projects will need to be brought up together so the application can perform.

Then run the following commands in the project root directory:

```
cd nhl_api_project
docker-compose build
docker-compose up
```

That will bring the application up and running.  If there are any questions with these steps, please let me know.

If all of the above worked successfully, go to your web browser (or a tool such as Postman) and follow the API instructions below.

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

**Request:** (I chose a goalie with only 1 game played last season to have a small payload example for this doc)

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
        "total_pp_goals": 1,
        "total_pp_assists": 2,
        "avg_pp_shots_per_60_mins": 120,
        "avg_pp_goals_per_60_mins": 120,
        "avg_pp_assists_per_60_mins": 240
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

* *Note* that the `total_pp_time` is a sum of all the time all players spent on the powerplay, not the amount of minutes the goalie spent on the powerplay.  This explains why the number is so high.


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

## Comparing Freddy Andersen and Garret Sparks

As a quick example of this, if you compare the `season_summary` json for both Andersen and Sparks last season, you can see that the Leafs put up better powerplay numbers on average per 60 minutes with Andersen in net than with Sparks.  See below:

**Andersen**
```json
"season_summary": {
    "goalie_name": "Frederik Andersen",
    "team_abbrev": "TOR",
    "team_id": 10,
    "num_games": 58,
    "total_pp_time": "21:46:52",
    "total_pp_shots": 259,
    "total_pp_goals": 37,
    "total_pp_assists": 72,
    "avg_pp_shots_per_60_mins": 11.891037086160281,
    "avg_pp_goals_per_60_mins": 1.6987195837371831,
    "avg_pp_assists_per_60_mins": 3.3056164872723564
}
```

**Sparks**
```json
"season_summary": {
    "goalie_name": "Garret Sparks",
    "team_abbrev": "TOR",
    "team_id": 10,
    "num_games": 20,
    "total_pp_time": "6:27:45",
    "total_pp_shots": 97,
    "total_pp_goals": 8,
    "total_pp_assists": 16,
    "avg_pp_shots_per_60_mins": 15.009671179883945,
    "avg_pp_goals_per_60_mins": 1.2379110251450678,
    "avg_pp_assists_per_60_mins": 2.4758220502901356
}
```

Of course this is not factoring the large sample size difference, the caliber of the competition or any other factors.  Really, this is simple comparison meant for example purposes.

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
* Currently doesn't handle the case of a goalie playing for multiple teams in the season (such as Michael Hutchinson)
* Ideally the NHL API Calls are not hardcoded as they are in the project at the moment.
* Right now all the data queries and calculations are done in memory using a JSON query library called ObjectPath.  This was due to the fact that the only data I had access to was via the NHL API instead of a proper database.  If I had a database to query, that would allow me to push most calculations and queries to the db-layer and prevent so much data from being pulled into memory.