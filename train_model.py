from sklearn.linear_model import LogisticRegression
from sklearn import preprocessing
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import xgboost as xgb
import os
import glob
import pandas as pd
import joblib

# Import training dataset
path = os.getcwd() + '\\dataset'
tier = input('Tier? ').lower()
tier = '_'.join(tier.split(sep=', '))
filenames = [i for i in glob.glob(os.path.join(path, '*' + tier + '*.csv'))]
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

rfc = RandomForestClassifier()
rfc.fit(x_train_scaled, y_train)

print(f'Random Forest Score (Train): {round(rfc.score(x_train_scaled, y_train), 4)}')
print(f'Random Forest Score (Test): {round(rfc.score(x_test_scaled, y_test), 4)}')

xgboost = xgb.XGBClassifier(use_label_encoder=False, eval_metric = 'logloss')
xgboost.fit(x_train_scaled, y_train)

print(f'XGB Score (Train): {round(xgboost.score(x_train_scaled, y_train), 4)}')
print(f'XGB Score (Test): {round(xgboost.score(x_test_scaled, y_test), 4)}')

joblib.dump(scaler, 'trained_models/scaler_' + tier + '.joblib')
joblib.dump(rfc, 'trained_models/rfc_' + tier + '.joblib')
xgboost.save_model('trained_models/xgb_' + tier + '.json')