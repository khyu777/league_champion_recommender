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

joblib.dump(scaler, 'trained_models/scaler.joblib')
joblib.dump(logit, 'trained_models/logit.joblib')
joblib.dump(rfc, 'trained_models/rfc.joblib')
xgboost.save_model('trained_models/xgb.json')