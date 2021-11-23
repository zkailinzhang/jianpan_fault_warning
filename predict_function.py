from statsmodels.tsa.api import VAR
from scipy.signal._savitzky_golay import savgol_filter
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import numpy as np
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import tensorflow as tf
import warnings
warnings.filterwarnings("ignore")


class VarFunction:
    def __init__(self):
        self.model = None
        self.maxlags = 3
        self.steps = 1
        self.predict_value = 0
        self.predict_value_dict = {}
        self.data = None

    def initialize(self, maxlags=10, steps=1):
        self.model = None
        self.maxlags = maxlags
        self.steps = steps
        self.predict_value = 0

    def forecast(self, var_list, data_dict):
        for i in var_list:
            data_fit = []
            location = 0
            for m in range(len(i)):
                data_fit.append(data_dict[i[m]].reshape(-1, 1))
            data_fit = tuple(data_fit)
            data_fit = np.concatenate(data_fit, axis=1)
            mm = MinMaxScaler()
            data = mm.fit_transform(data_fit)
            self.model = VAR(endog=data)
            model_fit = self.model.fit(maxlags=self.maxlags)
            self.predict_value = model_fit.forecast(model_fit.y, steps=self.steps)
            self.predict_value = mm.inverse_transform(self.predict_value)
            self.predict_value = self.predict_value.ravel()
            for key in i:
                self.predict_value_dict[key] = self.predict_value[location]
                location += 1

        return self.predict_value_dict


class LstmFunction:
    def __init__(self):
        self.model = None
        self.predict_value = 0

    def initialize(self):
        self.model = None
        self.predict_value = 0

    def build_model(self, input_shape, layers):
        self.model = tf.keras.models.Sequential()
        if layers == 1:
            self.model.add(tf.keras.layers.GRU(128, activation='relu', input_shape=input_shape, return_sequences=False))
        else:
            for i in range(layers):
                self.model.add(tf.keras.layers.GRU(64, activation='relu', return_sequences=True))
        # self.model.add(tf.keras.layers.GRU(32, activation='relu', return_sequences=True))
        # model = tf.keras.models.Sequential()
        # self.model.add(tf.keras.layers.RNN(tf.keras.layers.LSTMCell(128), input_shape=(200, 1), return_sequences=True))
        # self.model.add(tf.keras.layers.RNN(tf.keras.layers.LSTMCell(128), return_sequences=True))
        # self.model.add(tf.keras.layers.Dense(1))
        self.model.add(tf.keras.layers.Dropout(0.1))
        self.model.add(tf.keras.layers.Dense(1))
        self.model.compile(optimizer='adam', loss='mse')
        return self.model

    def fit(self, data_sequence):
        self.model.fit_generator(data_sequence, steps_per_epoch=1, epochs=200)
        return self.model

    def predict(self, model, data):
        self.predict_value = model.predict(data)
        return self.predict_value