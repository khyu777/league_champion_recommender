from riotwatcher import LolWatcher, ApiError
import pandas as pd
import time
from tqdm import tqdm
from constants import ACCESS_TOKEN
import os
import glob

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
champ_stats_df.index.str.lower()
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
    summoner_name = input('Summoner Name: ')
    summoner_id = lol_watcher.summoner.by_name(my_region, summoner_name)['id']
    summoners = lol_watcher.spectator.by_summoner(my_region, summoner_id)['participants']
    team_choice = input('Ally/Enemy team? (A/E) ')
    teamIds = [100, 200]
    curr_teamIds = {summoner['summonerName']:summoner['teamId'] for summoner in summoners}
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
            if player['puuid'] == id:
                player['summonerName'] = name
                player_stats.append(player)

player_stats_df = pd.DataFrame(player_stats)
player_stats_df['championName'] = player_stats_df['championName'].str.lower()

player_stats_df_summary = player_stats_df.groupby(['summonerName', 'championName']).mean()
player_stats_df_summary.drop(columns=['championId'], inplace=True)
player_stats_df_count = player_stats_df.groupby(['summonerName', 'championName']).size()
player_stats_df_summary = player_stats_df_summary.join(pd.DataFrame(player_stats_df_count, columns = ['count']))
player_stats_df_summary.reset_index(level = 0, inplace=True)

# Combine player stat and champion base stat
player_combined = player_stats_df_summary.join(champ_stats_df)
player_combined = player_combined.reset_index().rename(columns={'index':'championName'})
player_combined.summonerName.unique()

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
elif analysis_type == 'n':
    champion_selection = [champ_keys[champId].lower() for champId in curr_champIds]

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

current_team = pd.DataFrame(
    {'summonerName': [value for key, value in summoner_ids.items()], 'championName':champion_selection}
)
current_team_stats = pd.merge(current_team, player_combined, 'left', on = ['summonerName', 'championName']).fillna(0)

current_team_stats['kda'] = round((current_team_stats['kills'] + current_team_stats['deaths']) / current_team_stats['deaths'], 2)

print(current_team_stats[['summonerName', 'championName', 'kda']])

current_team_out = current_team_stats.drop(columns=['summonerName', 'championName', 'win', 'count', 'kda']).stack()
current_team_out.index = current_team_out.index.map('{0[1]}_{0[0]}'.format)
current_team_out = current_team_out.to_frame().T
current_team_out = current_team_out.reindex(sorted(current_team_out.columns), axis=1)

from sklearn.linear_model import LogisticRegression
from sklearn import preprocessing
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import xgboost as xgb

# Import training dataset
path = os.getcwd() + '\\dataset'
filenames = [i for i in glob.glob(os.path.join(path, '*.csv'))]
training_dataset = pd.concat([pd.read_csv(f) for f in filenames])

## split into train/test
x_train, x_test, y_train, y_test = train_test_split(
    training_dataset.reindex(sorted(training_dataset.columns), axis=1).drop(columns = 'win_'),
    training_dataset['win_'],
    random_state=42
)

scaler = preprocessing.StandardScaler()
x_train_scaled = scaler.fit_transform(x_train)
x_test_scaled = scaler.transform(x_test)

logit = LogisticRegression(max_iter=50000)
logit.fit(x_train_scaled, y_train)

print(f'Logit Score (Train): {round(logit.score(x_train_scaled, y_train), 4)}')
print(f'Logit Score (Test): {round(logit.score(x_test_scaled, y_test), 4)}')

rfc = RandomForestClassifier()
rfc.fit(x_train_scaled, y_train)

print(f'Random Forest Score (Train): {round(rfc.score(x_train_scaled, y_train), 4)}')
print(f'Random Forest Score (Test): {round(rfc.score(x_test_scaled, y_test), 4)}')

xgboost = xgb.XGBClassifier(use_label_encoder=False, eval_metric = 'logloss')
xgboost.fit(x_train_scaled, y_train)

print(f'XGB Score (Train): {round(xgboost.score(x_train_scaled, y_train), 4)}')
print(f'XGB Score (Test): {round(xgboost.score(x_test_scaled, y_test), 4)}')

# Test dataset
x_curr = current_team_out.reindex(sorted(current_team_out.columns), axis=1)
x_curr_scaled = scaler.transform(x_curr)

# Fit and predict
## Logistic Regression
logit_result = logit.predict(x_curr_scaled)
logit_prob = logit.predict_proba(x_curr_scaled)
if logit_result:
    print(f'Logistic Regression result: Win ({round(logit_prob[0][1] * 100, 2)}%)')
else:
    print(f'Logistic Regression result: Lose ({round(logit_prob[0][0] * 100, 2)}%)')

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

avg_result = (logit_prob + rf_prob + xgb_prob) / 3
if avg_result[0][0] > 0.5:
    print(f'Average result: Lose ({round(avg_result[0][0], 2) * 100}%)')
else:
    print(f'Average result: Win ({round(avg_result[0][1], 2) * 100}%)')