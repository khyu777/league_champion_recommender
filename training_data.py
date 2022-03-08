from riotwatcher import LolWatcher, ApiError
import pandas as pd
import numpy as np
from collections import defaultdict
import time
from tqdm import tqdm
from datetime import datetime
from constants import ACCESS_TOKEN

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

champs = pd.DataFrame.from_dict(champ['data'], orient='index')
champs = pd.DataFrame(champs.stats.values.tolist(), index=champs['id'])

champ_stats = {}
for champion in champ['data']:
    champ_stats[champion] = champ['data'][champion]['stats']

champ_stats_df = pd.DataFrame.from_dict(champ_stats, orient = 'index')
champ_stats_df.index = champ_stats_df.index.str.lower()
champ_stats_df.head()

# Get match information from challenger queue
## get summoner ids from challenger queue
league_queue = input('Please enter the leagues separated by commas: ').lower()
league_queue_list = league_queue.split(sep=',')
other_leagues = ['bronze', 'silver', 'gold', 'platinum', 'diamond']
summoner_list = []
for league in league_queue_list:
    if league == 'challenger':
        summoner_list_challenger = [summoner['summonerId'] for summoner in lol_watcher.league.challenger_by_queue(my_region, 'RANKED_SOLO_5x5')['entries']]
        summoner_list += summoner_list_challenger
    elif league == 'grandmaster':
        summoner_list_gm = [summoner['summonerId'] for summoner in lol_watcher.league.grandmaster_by_queue(my_region, 'RANKED_SOLO_5x5')['entries']]
        summoner_list += summoner_list_gm
    elif league in other_leagues:
        for div in ['I', 'II', 'III', 'IV']:
            summoner_list_oth = [summoner['summonerId'] for summoner in lol_watcher.league.entries(my_region, 'RANKED_SOLO_5x5', league.upper(), div)]
            summoner_list += summoner_list_oth

## get puuid for each summoner
summoner_list_puuid = []
for summoner_id in tqdm(summoner_list, bar_format='{l_bar}{bar:20}{r_bar}{bar:-20b}'):
    try:
        puuid = lol_watcher.summoner.by_id(my_region, summoner_id)['puuid']
        summoner_list_puuid.append(puuid)
        time.sleep(1.2)
    except ApiError as err:
        print(err.response.status_code)
        if err.response.status_code == 429:
            print('waiting...')
            time.sleep(60)
        elif err.response.status_code == 403:
            print('Invalid path or invalid API')
            ACCESS_TOKEN = input('Enter new API token if expired: ')
            lol_watcher = LolWatcher(ACCESS_TOKEN)
        else:
            raise

## get match list
matches = []
americas = ['br1', 'la1', 'la2', 'na1']
asia = ['jp1', 'kr', 'oc1', 'tr1', 'ru']
europe = ['eun1', 'euw1']
if my_region in americas:
    region = 'americas'
elif my_region in asia:
    region = 'asia'
elif my_region in europe:
    region = 'europe'
for puuid in tqdm(summoner_list_puuid, bar_format='{l_bar}{bar:20}{r_bar}{bar:-20b}'):
    while True:
        try:
            matches_by_puuid = lol_watcher.match.matchlist_by_puuid(region, puuid, count = 5)
            time.sleep(1.2)
        except ApiError as err:
            print(err.response.status_code)
            if err.response.status_code == 429:
                print('Waiting...')
                time.sleep(120)
            elif err.response.status_code == 403:
                print('Invalid path or invalid API')
                ACCESS_TOKEN = input('Enter new API token if expired: ')
                lol_watcher = LolWatcher(ACCESS_TOKEN)
        else:
            break
    for match in matches_by_puuid:
        matches.append(match)
matches = list(set(matches))

## get match information for matches in the list
matches_info = []
for match in tqdm(matches, bar_format='{l_bar}{bar:20}{r_bar}{bar:-20b}'):
    while True:
        try:
            match_info = lol_watcher.match.by_id(region, match)
            time.sleep(1.2)
        except ApiError as err:
            #print(err.response.status_code)
            if err.response.status_code == 429:
                print('Waiting...')
                time.sleep(60)
            elif err.response.status_code == 403:
                print('Invalid path or invalid API')
                ACCESS_TOKEN = input('Enter new API token if expired: ')
                lol_watcher = LolWatcher(ACCESS_TOKEN)
        else:
            break
    match_participants = defaultdict(list)
    if match_info['info']['gameType'] == 'MATCHED_GAME':
        for participant in match_info['info']['participants']:
            try:
                del participant['challenges']
            except KeyError:
                pass
            try:
                del participant['championId']
            except KeyError:
                pass
            if participant['teamPosition'] != '':
                for key, value in participant.items():
                    match_participants[key].append(value)
        df = pd.DataFrame(match_participants)
        if not df.empty:
            df['championName'] = df['championName'].str.lower()
            df = pd.merge(df, champ_stats_df.reset_index().rename(columns = {'index':'championName'}), 'left', on = 'championName')
            df.drop(df.filter(regex='^armor|^attack|championTransform|consumablesPurchased|damageSelfMitigated|detectorWardsPlaced|^firstBlood|gameEnded|^hp|^item|largestCriticalStrike|movespeed|^mp|^nexus|^objective|participantId|pentaKills|physicalDamageTaken|profileIcon|^spell|^summoner[1-2]|summonerLevel|summonerId|teamId|teamEarly|^time|totalDamageShielded|totalHealsOnTeammates|totalMinionsKilled|totalTimeCC|totalUnitsHealed|^trueDamage|visionWards|^wards').columns, axis=1, inplace=True)
            df = df.pivot(index = 'win', columns = 'teamPosition').reset_index().select_dtypes(include=[np.number, 'bool'])
            matches_info.append(df)

## convert to dataframe
matches_info_df = pd.concat(matches_info).dropna()
matches_info_df.columns = ["_".join(map(str,a)) for a in matches_info_df.columns.to_flat_index()]
matches_info_df.head(10)

## save to csv
matches_info_df.to_csv(f'dataset/training_dataset_{"_".join(league_queue_list)}_{datetime.now().strftime("%m%d%y_%H%S")}_{my_region}.csv', index = False)