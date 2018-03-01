# coding: utf-8
# pylint: disable = invalid-name, C0111
import feedback
import lightgbm as lgb
import numpy as np


# load or create your dataset
print('Load data...')
X_train, y_train = feedback.load_experiment_record(sample_rate=200, trunc=None)
X_train = np.array(X_train)
y_train = np.array(y_train)
lgb_train = lgb.Dataset(X_train, y_train)

X_test, y_test = feedback.load_experiment_record(sample_rate=1, trunc=700)
X_test = np.array(X_test)
y_test = np.array(y_test)
lgb_eval = lgb.Dataset(X_test, y_test, reference=lgb_train)

# specify your configurations as a dict
params = {
    'task': 'train',
    'boosting_type': 'dart',
    'objective': 'mape',
    'metric': {'mape'},
    'num_leaves': 50,
    'learning_rate': 0.09,
    'feature_fraction': 1,
    'bagging_fraction': 1,
    'bagging_freq': 20,
    'verbose': 0
}

print('Start training...')
# trainfeature_fraction
gbm = lgb.train(params,
                lgb_train,
                num_boost_round=150,
                valid_sets=lgb_eval,
                early_stopping_rounds=200)

print('Save model...')
# save model to file
gbm.save_model('gdm-model.txt')

print('Start predicting...')
# predict
y_pred = gbm.predict(X_test, num_iteration=gbm.best_iteration)
# eval
print(len(X_train))
err_mask = np.abs((y_pred - y_test) / y_test) > 0.5
print('The number of error (>50%) of prediction is:', np.sum(err_mask))
# print(np.array([(y_test)[err_mask],(y_pred)[err_mask]]).transpose())
