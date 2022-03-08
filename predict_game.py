from riotwatcher import LolWatcher, ApiError
import pandas as pd
import time
from tqdm import tqdm
from constants import ACCESS_TOKEN
import numpy as np
from scipy.stats.mstats import gmean

# define region / set up lolwatcher
lol_watcher = LolWatcher(ACCESS_TOKEN)
platform = ['br1', 'eun1', 'euw1', 'jp1', 'kr', 'la1', 'la2', 'na1', 'oc1', 'tr1', 'ru']
while True:
    my_region = input('Region: (i.e. na1, kr): ')
    if my_region not in platform:
        print('not a valid region. please enter again')
        continue
    else:
        break

# Champion base stat
latest = lol_watcher.data_dragon.versions_for_region(my_region)['n']['champion']
champ = lol_watcher.data_dragon.champions(latest, False, 'en_US')
champ_keys = {}
for champion in champ['data'].keys():
    champ_keys[int(champ['data'][champion]['key'])] = champion

champs = pd.DataFrame.from_dict(champ['data'], orient='index')
champs = pd.DataFrame(champs.stats.values.tolist(), index=champs['id'])

champ_stats = {}
for champion in champ['data']:
    champ_stats[champion] = champ['data'][champion]['stats']

champ_stats_df = pd.DataFrame.from_dict(champ_stats, orient = 'index')
champ_stats_df.index = champ_stats_df.index.str.lower()
champ_stats_df.head()

summoner_ids = {}
analysis_type = input('Before champion selection? (Y/N) ').lower()
if analysis_type == 'y':
    for i in range(1,6):
        while True:
            try:
                summoner = input(f'Summoner {i}: ')
                summoner_ids[lol_watcher.summoner.by_name(my_region, summoner)['puuid']] = summoner
            except ApiError as err:
                print(err.response.status_code)
                if err.response.status_code == 429:
                    print('Too many requests!! Waiting 2 minutes...')
                    time.sleep(120)
                if err.response.status_code == 404:
                    print('Summoner not found')
            else:
                break
elif analysis_type == 'n':
    while True:
        try:
            summoner_name = input('Summoner Name: ')
            summoner_id = lol_watcher.summoner.by_name(my_region, summoner_name)['id']
            summoners = lol_watcher.spectator.by_summoner(my_region, summoner_id)['participants']
        except ApiError as err:
            if err.response.status_code == 404:
                print('Summoner not in game, please try again')
            elif err.response.status_code == 403:
                print('Invalid path or invalid API')
                ACCESS_TOKEN = input('Enter new API token if expired: ')
                lol_watcher = LolWatcher(ACCESS_TOKEN)
        else:
            break
    while True:
        team_choice = input('Ally/Enemy team? (A/E) ')
        if team_choice not in ['a', 'e']:
            print('Please enter a or e')
            continue
        else:
            break
    teamIds = [100, 200]
    curr_teamIds = {summoner['summonerName']:summoner['teamId'] for summoner in summoners}
    if summoner_name not in curr_teamIds:
        summoner_name = input('summonerName is not correct. please check capitalization and reenter: ')
    curr_champIds = []
    if team_choice.lower() == 'a':
        teamId = curr_teamIds[summoner_name]
    elif team_choice.lower() == 'e':
        teamIds.remove(curr_teamIds[summoner_name])
        teamId = teamIds[0]
    for summoner in summoners:
        if summoner['teamId'] == teamId:
            while True:
                try:
                    summoner_ids[lol_watcher.summoner.by_name(my_region, summoner['summonerName'])['puuid']] = summoner['summonerName']
                    curr_champIds.append(summoner['championId'])
                except ApiError as err:
                    print(err.response.status_code)
                    if err.response.status_code == 429:
                        print('Too many requests!! Waiting 2 minutes...')
                        time.sleep(120)
                    if err.response.status_code == 404:
                        print('Summoner not found')
                else:
                    break
print(', '.join(summoner_ids.values()))

player_stats = []
americas = ['br1', 'la1', 'la2', 'na1']
asia = ['jp1', 'kr', 'oc1', 'tr1', 'ru']
europe = ['eun1', 'euw1']
if my_region in americas:
    region = 'americas'
elif my_region in asia:
    region = 'asia'
elif my_region in europe:
    region = 'europe'
for id, name in tqdm(summoner_ids.items(), bar_format='{l_bar}{bar:20}{r_bar}{bar:-20b}'):
    while True:
        try:
            matchlist = lol_watcher.match.matchlist_by_puuid(region, id, start = 0, count = 19)
        except ApiError as err:
                print(err.response.status_code)
                if err.response.status_code == 429:
                    print('Too many requests!! Waiting 2 minutes...')
                    time.sleep(120)
                if err.response.status_code == 404:
                    print('Match not found')
        else:
            break
    for match in tqdm(matchlist, leave = False, bar_format='{l_bar}{bar:20}{r_bar}{bar:-20b}'):
        while True:
            try:
                match_info = lol_watcher.match.by_id(region, match)
            except ApiError as err:
                print(err.response.status_code)
                if err.response.status_code == 429:
                    print('Too many requests!! Waiting 2 minutes...')
                    time.sleep(120)
                if err.response.status_code == 404:
                    print('Match not found')
            else:
                break
        for player in match_info['info']['participants']:
            if player['puuid'] == id and match_info['info']['gameType'] == 'MATCHED_GAME':
                player['summonerName'] = name
                player_stats.append(player)

player_stats_df = pd.DataFrame(player_stats).drop(columns=['championId', 'challenges'])
player_stats_df['championName'] = player_stats_df['championName'].str.lower()

columns = ['assists', 'baronKills', 'bountyLevel', 'champExperience', 'champLevel', 'damageDealtToBuildings', 'damageDealtToObjectives', 'damageDealtToTurrets', 'deaths', 'doubleKills', 'dragonKills', 'firstTowerAssist', 'firstTowerKill', 'goldEarned', 'goldSpent', 'inhibitorKills', 'inhibitorTakedowns', 'inhibitorsLost', 'killingSprees', 'kills', 'largestKillingSpree', 'largestMultiKill', 'longestTimeSpentLiving', 'magicDamageDealt', 'magicDamageDealtToChampions', 'magicDamageTaken', 'neutralMinionsKilled', 'physicalDamageDealt', 'physicalDamageDealtToChampions', 'quadraKills', 'sightWardsBoughtInGame', 'totalDamageDealt', 'totalDamageDealtToChampions', 'totalDamageTaken', 'totalHeal', 'totalTimeSpentDead', 'tripleKills', 'turretKills', 'turretTakedowns', 'turretsLost', 'unrealKills', 'visionScore']

player_stats_df_summary = player_stats_df.groupby(['summonerName', 'championName', 'teamPosition'])[columns].mean()
player_stats_df_summary = player_stats_df_summary.reset_index(level='teamPosition')
player_stats_df_summary['teamPosition'].replace('', np.nan, inplace=True)
player_stats_df_summary.dropna(subset=['teamPosition'], inplace=True)
player_stats_df_summary.reset_index(level = 'summonerName', inplace=True)

# Combine player stat and champion base stat
player_combined = player_stats_df_summary.join(champ_stats_df[['crit', 'critperlevel']])
player_combined = player_combined.reset_index().rename(columns={'index':'championName'})
print(player_combined.summonerName.unique())

if analysis_type == 'y':
    champion_selection = []
    for summoner in summoner_ids.values():
        while True:
            champion_selection_input = input(f"{summoner}'s champion: ")
            if champion_selection_input not in champ_stats_df.index.str.lower():
                print('not a valid champion name. please enter again')
                continue
            else:
                break
        champion_selection.append(champion_selection_input)

    while True:
        print(', '.join(champion_selection))
        champion_fix = input('Would you like to fix any champions? (Y/N) ')
        if champion_fix.lower() == 'y':
            champion_num = int(input('Please enter the position of the champion (1-5): '))-1
            new_champ = input('Please enter the name of the new champion: ')
            champion_selection[champion_num] = new_champ
            continue
        elif champion_fix.lower() == 'n':
            break
elif analysis_type == 'n':
    champion_selection = [champ_keys[champId].lower() for champId in curr_champIds]

positions = ['TOP', 'JUNGLE', 'MIDDLE', 'BOTTOM', 'UTILITY']
summoner_names = {}
for key, value in summoner_ids.items():
    while True:
        position = input('Position for ' + value + '? ').lower()
        if position == 'top':
            position = 'TOP'
        elif position == 'jg':
            position = 'JUNGLE'
        elif position == 'mid':
            position = 'MIDDLE'
        elif position == 'ad':
            position = 'BOTTOM'
        elif position == 'sup':
            position = 'UTILITY'
        if position not in positions:
            print('Wrong position name. Please enter again')
            continue
        else:
            break
    summoner_names[value] = position

current_team = pd.DataFrame(
    {'summonerName': [key for key in summoner_names], 'championName':champion_selection, 'teamPosition': [value for value in summoner_names.values()]}
)
current_team_stats = pd.merge(current_team, player_combined, 'left', on = ['summonerName', 'championName', 'teamPosition']).fillna(0)
#current_team_stats.drop(current_team_stats.filter(regex='^armor|^attack|championTransform|consumablesPurchased|damageSelfMitigated|detectorWardsPlaced|^firstBlood|gameEnded|^hp|^item|largestCriticalStrike|movespeed|^mp|^nexus|^objective|participantId|pentaKills|physicalDamageTaken|profileIcon|^spell|^summoner[1-2]|summonerLevel|summonerId|teamId|teamEarly|^time|totalDamageShielded|totalHealsOnTeammates|totalMinionsKilled|totalTimeCC|totalUnitsHealed|^trueDamage|visionWards|^wards').columns, axis=1, inplace=True)

current_team_stats['kda'] = round((current_team_stats['kills'] + current_team_stats['deaths']) / current_team_stats['deaths'], 2)

print(current_team_stats[['summonerName', 'championName', 'teamPosition', 'kda']])

current_team_out = current_team_stats.drop(columns=['summonerName', 'championName', 'kda'])
current_team_out['i'] = 0
current_team_out = current_team_out.pivot(index = 'i', columns = 'teamPosition').select_dtypes(include=[np.number, 'bool'])
current_team_out.columns = ["_".join(map(str,a)) for a in current_team_out.columns.to_flat_index()]

import xgboost as xgb
import joblib

# Import training dataset
import xgboost as xgb
import joblib


tier = input('Tier? ').lower()
tier = '_'.join(tier.split(sep=', '))
scaler = joblib.load('trained_models/scaler_' + tier + '.joblib')
rfc = joblib.load('trained_models/rfc_' + tier + '.joblib')

xgboost = xgb.XGBClassifier()
xgboost.load_model('trained_models/xgb_' + tier + '.json')

# Test dataset
x_curr = current_team_out.reindex(sorted(current_team_out.columns), axis=1)
x_curr_scaled = scaler.transform(x_curr)

# Fit and predict

## Random Forest
rf_result = rfc.predict(x_curr_scaled)
rf_prob = rfc.predict_proba(x_curr_scaled)
if rf_result:
    print(f'Random Forest result: Win ({round(rf_prob[0][1] * 100, 2)}%)')
else:
    print(f'Random Forest result: Lose ({round(rf_prob[0][0] * 100, 2)}%)')

## XGBoost
xgb_result = xgboost.predict(x_curr_scaled)
xgb_prob = xgboost.predict_proba(x_curr_scaled)
if xgb_result:
    print(f'XGB result: Win ({round(xgb_prob[0][1] * 100, 2)}%)')
else:
    print(f'XGB result: Lose ({round(xgb_prob[0][0] * 100, 2)}%)')

avg_result = (rf_prob + xgb_prob) / 2
if avg_result[0][0] > 0.5:
    print(f'Average result: Lose ({round(avg_result[0][0], 2) * 100}%)')
else:
    print(f'Average result: Win ({round(avg_result[0][1], 2) * 100}%)')