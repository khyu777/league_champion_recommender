from riotwatcher import LolWatcher, ApiError
import pandas as pd
import time
from tqdm import tqdm
from constants import ACCESS_TOKEN
import sys
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

self_other = input('Self or other? (S/O) ').lower()
summoner_ids = {}
if self_other == 's':
    print('Please paste content from champion select chat:')
    summoner_names = [summoner.replace(' joined the lobby', '') for summoner in sys.stdin.read().split('\n')]
    summoner_names.remove('')
    for summoner in summoner_names:
        print(summoner)
        summoner_ids[lol_watcher.summoner.by_name(my_region, summoner)['puuid']] = summoner
    my_summoner_name = input('Your summoner name (or the name for other): ')
elif self_other == 'o':
    while True:
        try:
            my_summoner_name = input('Summoner name for other: ')
            summoner_id = lol_watcher.summoner.by_name(my_region, my_summoner_name)['id']
            summoners = lol_watcher.spectator.by_summoner(my_region, summoner_id)['participants']
        except ApiError as err:
            print(err.response.status_code)
            if err.response.status_code == 404:
                print('Summoner not in game, please try again')
        else:
            break
    team_choice = input('Ally/Enemy team? (A/E) ')
    teamIds = [100, 200]
    curr_teamIds = {summoner['summonerName']:summoner['teamId'] for summoner in summoners}
    if my_summoner_name not in curr_teamIds:
        my_summoner_name = input('summonerName is not correct. please check capitalization and reenter: ')
    curr_champIds = []
    if team_choice.lower() == 'a':
        teamId = curr_teamIds[my_summoner_name]
    elif team_choice.lower() == 'e':
        teamIds.remove(curr_teamIds[my_summoner_name])
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

while True:
    manual_auto = input('Manual or Auto? (M/A)? ').lower()
    if manual_auto not in ['m', 'a']:
        print('please enter M or A')
        continue
    else:
        break

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

champions = pd.DataFrame({'championName':champ_stats_df.index.str.lower()})
def get_stats(summoner, manual):
    summoner_position = summoner_names[summoner]
    my_summoner_stats_all = pd.merge(champions, player_combined[player_combined['summonerName']==summoner], 'left', on = 'championName')
    my_summoner_stats_all = my_summoner_stats_all.drop(columns=['summonerName', 'teamPosition']).add_suffix('_' + summoner_position)
    if manual:
        return my_summoner_stats_all
    else:
        return my_summoner_stats_all.dropna(thresh=2)
        
summoner_list = [summoner for summoner in summoner_names]
print(' / '.join(list(summoner_names)))
if manual_auto == 'm':
    champion_selection = []
    for summoner in summoner_ids.values():
        if summoner != my_summoner_name:
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

    # stats for all champs for my summoner
    my_summoner_stats_all = get_stats(my_summoner_name, True).rename(columns={'championName_'+summoner_names[my_summoner_name]:'championName'})

    # data for current team
    current_team = pd.DataFrame(
        {'summonerName': [key for key, value in summoner_names.items() if key != my_summoner_name], 'championName':champion_selection, 'teamPosition': [value for key, value in summoner_names.items() if key != my_summoner_name]}
    )
    current_team_stats = pd.merge(current_team, player_combined, 'left', on = ['summonerName', 'championName', 'teamPosition']).fillna(0)

    current_team_stats['kda'] = round((current_team_stats['kills'] + current_team_stats['deaths']) / current_team_stats['deaths'], 2)

    print(current_team_stats[['summonerName', 'championName', 'kda']])

    current_team_out = current_team_stats.drop(columns=['summonerName', 'championName', 'kda'])
    current_team_out['i'] = 0
    current_team_out = current_team_out.pivot(index = 'i', columns = 'teamPosition').select_dtypes(include=[np.number, 'bool'])
    current_team_out.columns = ["_".join(map(str,a)) for a in current_team_out.columns.to_flat_index()]

    # create dataset with all champions for my summoner + other 4 summoners
    all_summoners = current_team_out.merge(my_summoner_stats_all, how = 'cross').fillna(0)
    all_summoners = all_summoners.reindex(sorted(all_summoners.columns), axis=1)

elif manual_auto == 'a':
    # all combinations
    summoner_0 = get_stats(list(summoner_names)[0], False)
    summoner_1 = get_stats(list(summoner_names)[1], False)
    summoner_2 = get_stats(list(summoner_names)[2], False)
    summoner_3 = get_stats(list(summoner_names)[3], False)
    summoner_4 = get_stats(list(summoner_names)[4], False)

    summoner_all_comb = summoner_0.merge(summoner_1, how='cross').merge(summoner_2, how='cross').merge(summoner_3, how='cross').merge(summoner_4, how='cross')
    summoner_all_comb['championNames'] = summoner_all_comb['championName_'+summoner_names[summoner_list[0]]].str.title() + ' / ' + summoner_all_comb['championName_'+summoner_names[summoner_list[1]]].str.title() + ' / ' + summoner_all_comb['championName_'+summoner_names[summoner_list[2]]].str.title() + ' / ' + summoner_all_comb['championName_'+summoner_names[summoner_list[3]]].str.title() + ' / ' + summoner_all_comb['championName_'+summoner_names[summoner_list[4]]].str.title()
    summoner_all_comb = summoner_all_comb.reindex(sorted(summoner_all_comb.columns), axis=1)
    summoner_all_comb['count'] = [len(x.split(' / ')) for x in summoner_all_comb['championNames'].tolist()]
    summoner_all_comb['distinct_count'] = [len(set(x.split(' / '))) for x in summoner_all_comb['championNames'].tolist()]
    summoner_all_comb = summoner_all_comb[summoner_all_comb['count'] == summoner_all_comb['distinct_count']].drop(columns=['count', 'distinct_count'])

import xgboost as xgb
import joblib

tier = input('Tier? ').lower()
tier = '_'.join(tier.split(sep=', '))
scaler = joblib.load('trained_models/scaler_' + tier + '.joblib')
rfc = joblib.load('trained_models/rfc_' + tier + '.joblib')

xgboost = xgb.XGBClassifier()
xgboost.load_model('trained_models/xgb_' + tier + '.json')

# Test dataset
print(summoner_names)
if manual_auto == 'm':
    x_curr = all_summoners.drop(columns=['championName'])
    x_curr_scaled = scaler.transform(x_curr)

    ## Random Forest
    print('Random Forest')
    rfc_result = rfc.predict(x_curr_scaled)
    rfc_prob = rfc.predict_proba(x_curr_scaled)
    rfc_champion = pd.DataFrame({'championName':all_summoners['championName'], 'win_prob':[round(prob[1]*100, 2) for prob in rfc_prob]}).sort_values('win_prob', ascending=False)
    print(rfc_champion.head())

    ## XGBoost
    print('XGBoost')
    xgb_result = xgboost.predict(x_curr_scaled)
    xgb_prob = xgboost.predict_proba(x_curr_scaled)
    xgb_champion = pd.DataFrame({'championName':all_summoners['championName'], 'win_prob':[round(prob[1]*100, 2) for prob in xgb_prob]}).sort_values('win_prob', ascending=False)
    print(xgb_champion.head())

    ## Average
    average_champion = pd.concat([rfc_champion, xgb_champion]).groupby('championName').mean().sort_values('win_prob', ascending=False)
    print(average_champion.head())

elif manual_auto == 'a':
    x_curr_auto = summoner_all_comb.drop(list(summoner_all_comb.filter(regex = 'championName')), axis=1)
    x_curr_auto_scaled = scaler.transform(x_curr_auto)

    # Fit and predict
    ## Random Forest
    print('Random Forest')
    rfc_result_auto = rfc.predict(x_curr_auto_scaled)
    rfc_prob_auto = rfc.predict_proba(x_curr_auto_scaled)
    rfc_champion_auto = summoner_all_comb.loc[:, ['championName_TOP', 'championName_JUNGLE', 'championName_MIDDLE', 'championName_BOTTOM', 'championName_UTILITY']]
    rfc_champion_auto.loc[:, 'win_prob'] = [round(prob[1]*100, 2) for prob in rfc_prob_auto]
    rfc_champion_auto = rfc_champion_auto.sort_values('win_prob', ascending = False)
    print(rfc_champion_auto.head(10))

    ## XGBoost
    print('XGBoost')
    xgb_result_auto = xgboost.predict(x_curr_auto_scaled)
    xgb_prob_auto = xgboost.predict_proba(x_curr_auto_scaled)
    xgb_champion_auto = summoner_all_comb.loc[:, ['championName_TOP', 'championName_JUNGLE', 'championName_MIDDLE', 'championName_BOTTOM', 'championName_UTILITY']]
    xgb_champion_auto.loc[:, 'win_prob'] = [round(prob[1]*100, 2) for prob in xgb_prob_auto]
    xgb_champion_auto = xgb_champion_auto.sort_values('win_prob', ascending = False)
    print(xgb_champion_auto.head(10))

    #auto_prob = summoner_all_comb.loc[:,['championName_TOP', 'championName_JUNGLE', 'championName_MIDDLE', 'championName_BOTTOM', 'championName_UTILITY', 'championNames']]
    #auto_prob['win_prob_rfc'] = pd.Series([x[0] for x in rfc_prob_auto])
    #auto_prob['win_prob_xgb'] = pd.Series([x[0] for x in xgb_prob_auto])
    
    #auto_prob['win_prob_rfc_avg'] = df = auto_prob.groupby('championName_' + summoner_names[my_summoner_name])['win_prob_rfc'].transform('mean')
    #auto_prob['win_prob_xgb_avg'] = df = auto_prob.groupby('championName_' + summoner_names[my_summoner_name])['win_prob_xgb'].transform('mean')
    #auto_prob['win_prob_overall_avg'] = auto_prob[['win_prob_rfc_avg', 'win_prob_xgb_avg']].mean(axis=1)

    #print('Combined')
    #print(my_summoner_name + ': champion_' + str(list(summoner_names).index(my_summoner_name)+1))
    #print(auto_prob[['championNames', 'win_prob_rfc_avg', 'win_prob_xgb_avg', 'win_prob_overall_avg']].sort_values('win_prob_overall_avg', ascending=False).head())