from riotwatcher import LolWatcher, ApiError
import pandas as pd
import numpy as np
from collections import defaultdict
import time
from tqdm import tqdm
from datetime import datetime
from constants import ACCESS_TOKEN

lol_watcher = LolWatcher(ACCESS_TOKEN)
my_region = 'na1'

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
summoner_list = [summoner['summonerId'] for summoner in lol_watcher.league.challenger_by_queue(my_region, 'RANKED_SOLO_5x5')['entries']]

## get puuid for each summoner
summoner_list_puuid = []
for summoner_id in tqdm(summoner_list[:1], bar_format='{l_bar}{bar:20}{r_bar}{bar:-20b}'):
    try:
        puuid = lol_watcher.summoner.by_id(my_region, summoner_id)['puuid']
        summoner_list_puuid.append(puuid)
        time.sleep(1.2)
    except ApiError as err:
        print(err.response.status_code)
        if err.response.status_code == 429:
            print('waiting...')
            time.sleep(60)
        elif err.response.status_code == 404:
            print('Summoner with that ridiculous name not found.')
        else:
            raise

## get match list
matches = []
for puuid in tqdm(summoner_list_puuid, bar_format='{l_bar}{bar:20}{r_bar}{bar:-20b}'):
    while True:
        try:
            matches_by_puuid = lol_watcher.match.matchlist_by_puuid('americas', puuid, count = 15)
            time.sleep(1.2)
        except ApiError as err:
            print(err.response.status_code)
            if err.response.status_code == 429:
                print('Waiting...')
                time.sleep(60)
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
            match_info = lol_watcher.match.by_id('americas', match)
            time.sleep(1.2)
        except ApiError as err:
            #print(err.response.status_code)
            if err.response.status_code == 429:
                print('Waiting...')
                time.sleep(60)
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
            for key, value in participant.items():
                match_participants[key].append(value)
        df = pd.DataFrame(match_participants)
        df.drop(df.filter(regex='^armor|^attack|championTransform|consumablesPurchased|damageSelfMitigated|detectorWardsPlaced|^firstBlood|gameEnded|^hp|^item|largestCriticalStrike|movespeed|^mp|^nexus|^objective|participantId|pentaKills|physicalDamageTaken|profileIcon|^spell|^summoner|^team|^time|totalDamageShielded|totalHealsOnTeammates|totalMinionsKilled|totalTimeCC|totalUnitsHealed|^trueDamage|visionWards|^wards').columns, axis=1, inplace=True)
        df['championName'] = df['championName'].str.lower()
        df = pd.merge(df, champ_stats_df.reset_index().rename(columns = {'index':'championName'}), 'left', on = 'championName')
        df['n'] = df.groupby('win').cumcount()
        df = df.pivot(index = 'win', columns = 'n').reset_index().select_dtypes(include=[np.number, 'bool'])
        matches_info.append(df)

## convert to dataframe
matches_info_df = pd.concat(matches_info).dropna()
matches_info_df.columns = ["_".join(map(str,a)) for a in matches_info_df.columns.to_flat_index()]
matches_info_df.head(10)

## save to csv
matches_info_df.to_csv(f'training_dataset_{datetime.now().strftime("%m%d%y_%H%S")}.csv', index = False)