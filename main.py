"""
    Project name: Prize Pick Predictions
    Author: Kevin Huy Trinh
    Date created: March, 2022
    Python Version: 3.11.1
    Description: Linear regression python program that makes
        recommendations on betting in favor/against a player's prize
        pick line_score value using numerous machine learning algorithms. 
"""

#api link --> https://api.prizepicks.com/projections?league_id=7

import json
from tabulate import tabulate
from find_player import get_player_stats
import time

pre_json = "pre_formatted_projections.json" #where we copied and paste api into
post_json = "post_formatted_projections.json" #after it gets cleaned up & formatted


# reads the pre_formmatted json file
with open(pre_json, "r") as file:
    data = json.load(file)
    # Format the JSON with indentation
    json_str = json.dumps(data, indent=4)


# pre_formmatted json --> post_formatted json
json_dict = json.loads(json_str)
with open(pre_json, "w") as file:
    json.dump(json_dict, file, indent=4)


# Create dictionary to store results
results = {}

# Loop through included data to get player names and IDs
for item in data['included']:
    if item['type'] == 'new_player':
        player_id = item['id']
        player_name = item['attributes']['name']
        results[player_id] = {
            'name': player_name,
            'strike_values': []
        }

# Loop through projection data and match player IDs to add stat_type and line_score
for projection in data['data']:
    if projection['type'] == 'projection':
        player_id = projection['relationships']['new_player']['data']['id']
        stat_type = projection['attributes']['stat_type']
        line_score = projection['attributes']['line_score']
        results[player_id]['strike_values'].append({
            'stat_type': stat_type,
            'line_score': line_score
        })
        # Add player attributes to results dictionary
        for player in data['included']:
            if player['type'] == 'new_player' and player['id'] == player_id:
                results[player_id]['attributes'] = player['attributes']

# Write results to JSON file
with open(post_json, 'w') as f:
    json.dump(results, f, indent=2)
with open(post_json, 'r') as f:
    data = json.load(f)

#lengths and member counts
num_players = len(data)
players_printed = 0

table = []
with open('output.txt', 'w') as f:
    for idx, key in enumerate(data):
        # the attribute values
        name = data[key]['name']
        team_name = data[key]['attributes']['team_name']
        team_city_state = data[key]['attributes']['market']

        # initialize values to "--" which is N/A
        n_a = "--"

        points = n_a
        rebounds = n_a
        assists = n_a
        turnovers = n_a
        points_assists = n_a
        points_rebounds = n_a
        points_rebounds_assists = n_a


        # check if player has stat_type and update value accordingly
        for item in data[key]['strike_values']:
            if item['stat_type'] == 'Points':
                points = item['line_score']
            elif item['stat_type'] == 'Turnovers':
                turnovers = item['line_score']
            elif item['stat_type'] == 'Rebounds':
                rebounds = item['line_score']
            elif item['stat_type'] == 'Assists':
                assists = item['line_score']
            elif item['stat_type'] == 'Pts+Asts':
                points_assists = item['line_score']
            elif item['stat_type'] == 'Pts+Rebs':
                points_rebounds = item['line_score']
            elif item['stat_type'] == 'Pts+Rebs+Asts':
                points_rebounds_assists = item['line_score']


        try:
            player_name = name
            fp_player_stats, fp_player_id, fp_team_name, fp_points, fp_rebounds, fp_assists, fp_turnovers, fp_blocks, fp_steals, fp_ftm, fp_points_rebounds, fp_points_assists, fp_points_rebounds_assists = get_player_stats(
                player_name)
            # Print player stats
            print("Player stats for: " + player_name)
            print("Player ID: " + str(fp_player_id))
            print("Team: " + fp_team_name)
            print("Points per game: " + str(fp_points))
            print("Rebounds per game: " + str(fp_rebounds))
            print("Assists per game: " + str(fp_assists))
            print("Turnovers per game: " + str(fp_turnovers))
            print("Blocks per game: " + str(fp_blocks))
            print("Steals per game: " + str(fp_steals))
            print("Free throws made per game: " + str(fp_ftm))
            print("Points + rebounds per game: " + str(fp_points_rebounds))
            print("Points + assists per game: " + str(fp_points_assists))
            print("Points + rebounds + assists per game: " + str(fp_points_rebounds_assists))
            print("\n\n")
            #time.sleep(1) #to avoid being rate limited
        except:
            print(f"Failed to find {player_name}. Now skipping. \n\n")


        table.append([idx+1, name, team_name, points, fp_points, rebounds, fp_rebounds, assists, turnovers, points_assists, points_rebounds, points_rebounds_assists])
        players_printed += 1
    f.write(tabulate(table, headers=['##', 'Name', 'Team Name', 'Pts', "FP-Pts", "Rebs", "FP_reb", "Ast", "T.O", "Pts+Ast", "Pts+Rebs", "Pts+Rebs+Ast"], tablefmt='orgtbl') + "\n\n")

    #number of players with atleast 1 missing stat
    num_na_stats = sum(1 for row in table if n_a in row)
    f.write(f"{num_na_stats} players have at least one 'N/A' stat.\n")
    f.write(f"A total of {num_players} player objects in json file.\n")
    f.write(f"{players_printed}/{num_players} were printed out in table format.\n\n")

print(tabulate(table, headers=['##', 'Name', 'Team Name', 'Pts', "FP-Pts", "Rebs", "FP_reb", "Ast", "T.O", "Pts+Ast", "Pts+Rebs", "Pts+Rebs+Ast"], tablefmt='orgtbl') + "\n")

print(f"\n{num_na_stats} players have at least one missing stat.")
print(f"A total of {num_players} player objects in json file.")
print(f"{players_printed}/{num_players} were printed out in table format.\n\n")
