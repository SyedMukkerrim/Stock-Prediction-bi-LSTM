# -*- coding: utf-8 -*-
"""DM_Stock BiLSTM.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1_eRJLvTVC2XKqb0tcf1JNs3m8k29hBcG
"""

!git clone https://github.com/ArterioRodrigues/DM_Stock.git

from os import minor
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from keras.layers import LSTM, Dense, Dropout , Bidirectional , Dropout
from sklearn.model_selection import TimeSeriesSplit
from keras.callbacks import EarlyStopping
from keras.models import Sequential
from keras.utils.vis_utils import plot_model

df = pd.read_csv('/content/DM_Stock/CSV/MSFT_kaggle.csv', na_values=['null'], index_col='Date', parse_dates=True,infer_datetime_format=True)

plt.plot(pd.DataFrame(df['Close']), label='Close')
plt.title("The Closing Values of the DataSet Used")
plt.xlabel('Time Scale')
plt.ylabel('Values')
plt.legend()
plt.show()

df

#ground_truth
output_var = pd.DataFrame(df['Close'])
features = ['Open', 'High', 'Low', 'Volume']
scaler = MinMaxScaler(feature_range=(0,1))
feature_transform = scaler.fit_transform(df[features])
feature_transform = pd.DataFrame(columns=features, data=feature_transform, index=df.index)

feature_transform

timesplit = TimeSeriesSplit(n_splits=10)
for train_index, test_index in timesplit.split(feature_transform):
  X_train, X_test = feature_transform[:len(train_index)], feature_transform[len(train_index): ]
  y_train, y_test = output_var[:len(train_index)].values.ravel(), output_var[len(train_index): (len(train_index) + len(test_index))].values.ravel()



trainX = np.array(X_train)
testX = np.array(X_test)
X_train = trainX.reshape(X_train.shape[0], 1, X_train.shape[1])
X_test = testX.reshape(X_test.shape[0], 1, X_test.shape[1])

print(X_train.shape)
print(X_test.shape)

def build_model(dataset):
    scaler = MinMaxScaler()
    feature_transform = scaler.fit_transform(df[features])
    feature_transform = pd.DataFrame(columns=features, data=feature_transform, index=df.index)
    timesplit = TimeSeriesSplit(n_splits=10)
    for train_index, test_index in timesplit.split(feature_transform):
      X_train, X_test = feature_transform[:len(train_index)], feature_transform[len(train_index): ]
      y_train, y_test = output_var[:len(train_index)].values.ravel(), output_var[len(train_index): (len(train_index) + len(test_index))].values.ravel()
    trainX = np.array(X_train)
    testX = np.array(X_test)
    X_train = trainX.reshape(X_train.shape[0], 1, X_train.shape[1])
    X_test = testX.reshape(X_test.shape[0], 1, X_test.shape[1])
    bilstm = Sequential()
    bilstm.add(Bidirectional(LSTM(32, input_shape=(1, trainX.shape[1]), activation="selu")))
    bilstm.add(Dropout(0.4))
    bilstm.add(Dense(1))
    bilstm.compile(loss="mean_squared_error", optimizer="adam")

    earlyStop = EarlyStopping(
  monitor='loss',
  min_delta=0.01,
  patience=25,
  mode='min',
  verbose=1,
  restore_best_weights=True
)
    history=bilstm.fit(X_train, y_train, epochs=100, batch_size=8, verbose=1, shuffle=False, callbacks=[earlyStop])
    y_pred = bilstm.predict(X_test)


    return y_pred

#Building the biLSTM Model
bilstm = Sequential()
bilstm.add(Bidirectional(LSTM(128, input_shape=(1, trainX.shape[1]), activation="relu")))
bilstm.add(Dropout(0.4))
bilstm.add(Dense(1))

bilstm.compile(loss="mean_squared_error", optimizer="adam")

earlyStop = EarlyStopping(
  monitor='loss',
  min_delta=0.01,
  patience=25,
  mode='min',
  verbose=1,
  restore_best_weights=True
)

history=bilstm.fit(X_train, y_train, epochs=150, batch_size=8, verbose=1, shuffle=False, callbacks=[earlyStop])

#biLSTM Prediction
y_pred = bilstm.predict(X_test)

#Predicted vs True Adj Close Value – LSTM
plt.plot(y_test, label='True Value')
plt.plot(y_pred, label='BiLSTM Value')
plt.title("Prediction by BiLSTM")
plt.xlabel('Time Scale')
plt.ylabel('Scaled USD')
plt.legend()


pd.DataFrame(history.history).plot()
plt.show()

rmse = np.sqrt(np.mean( y_pred - y_test)**2)
print(rmse)

#!python -m pip uninstall matplotlib
#!pip install matplotlib==3.1.3

