# coding: utf-8
# pylint: disable = invalid-name, C0111
import feedback
import lightgbm as lgb
import numpy as np


# load or create your dataset
print('Load data...')
X_train, y_train = feedback.load_experiment_record(sample_rate=250, trunc=None)
X_train = np.array(X_train)
y_train = np.array(y_train)
lgb_train = lgb.Dataset(X_train, y_train)

X_test, y_test = feedback.load_experiment_record(sample_rate=2, trunc=1000)
X_test = np.array(X_test)
y_test = np.array(y_test)
lgb_eval = lgb.Dataset(X_test, y_test, reference=lgb_train)

# specify your configurations as a dict
params = {
    'task': 'train',
    'boosting_type': 'gbdt',
    'objective': 'mape',
    'metric': {'mape', 'l1'},
    'num_leaves': 20,
    'learning_rate': 0.09,
    'feature_fraction': 0.9,
    'bagging_fraction': 0.8,
    'bagging_freq': 5,
    "lambda_l1":0.0001,
    'verbose': 0
}

print('Start training...')
# train
gbm = lgb.train(params,
                lgb_train,
                num_boost_round=100,
                valid_sets=lgb_eval,
                early_stopping_rounds=100)

print('Save model...')
# save model to file
gbm.save_model('gdm-model.txt')

print('Start predicting...')
# predict
y_pred = gbm.predict(X_test, num_iteration=gbm.best_iteration)
# eval
print(len(X_train))
print('The max error of prediction is:', np.max(
    np.abs((y_pred - y_test) / y_test)))
