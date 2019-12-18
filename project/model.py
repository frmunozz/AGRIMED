from .lstm.lstm_conv2 import load_model, predict
from sklearn.externals import joblib
import numpy as np
import pandas as pd
import datetime
from keras.models import model_from_json
import matplotlib.pyplot as plt


class Predictor:
    def __init__(self, bc_model_path=None, lstm_model_path=None):
        self.bc_path = bc_model_path
        self.lstm_path = lstm_model_path
        self.classifier = self.load_binary_classifier()
        self.lstm = self.load_lstm_predictor()

    def plot_curve(self, pred):
        minutes = np.arange(50) * 15
        plt.plot(minutes, pred, "--")
        plt.title("Curva de temperatura predicha")
        plt.xlabel("Hora de la prediccion (en minutos, iniciando desde las 20 hrs)")
        plt.ylabel("Temperatura")
        plt.show()

    def save_curve(self, ddtt, pred):
        # import pdb
        # pdb.set_trace()
        times = []
        time20 = datetime.datetime.strptime(str(ddtt.date()) + " " + str(datetime.time(hour=20)),
                                            "%Y-%m-%d %H:%M:%S")
        for i in range(50):
            deltat = datetime.timedelta(minutes=15 * i)
            times.append(time20 + deltat)
        df_dict = {"datetime": times,
                   "temp": pred}
        df = pd.DataFrame(df_dict)
        df.to_csv("pred_%s.csv" % str(ddtt.date()))


    def load_binary_classifier(self):
        json_file = open(self.bc_path + 'model.json', 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        loaded_model = model_from_json(loaded_model_json)
        # load weights into new model
        loaded_model.load_weights(self.bc_path + "model.h5")
        return loaded_model

    def load_lstm_predictor(self):
        lstm = load_model(path=self.lstm_path)
        return lstm

    def predict_classifier(self, input_, threshold=0.5):
        # import pdb
        # pdb.set_trace()
        # load scaler
        scaler = joblib.load(self.bc_path + "scaler.save")
        input_scaled = scaler.transform(np.array([input_]))

        pred_prob = self.classifier.predict(input_scaled)

        return pred_prob[0][1] > threshold, pred_prob[0]

    def predict_curve(self, input_, device="cpu"):
        # import pdb
        # pdb.set_trace()
        pred = predict(input_, self.lstm, device="cpu")
        return pred


class DataHandler:
    def __init__(self, dataframe):
        self.df = dataframe

    def check_columns(self):
        cols = ["Codigo", "Fecha", "Hora", "Temperatura", "Humedad", "Velocidad de Viento",
                "Precipitacion", "Radiacion Solar", "Presion Atmosferica"]
        return all([x in self.df.columns for x in cols])

    def check_date(self, ddtt):
        if isinstance(self.df["Fecha"][0], str):
            return any(self.df["Fecha"] == str(ddtt.date()))
        else:
            return any(self.df["Fecha"] == ddtt)

    def check_time(self, ddtt, hour=20):
        ddtt2 = datetime.time(hour=hour)
        if isinstance(self.df["Fecha"][0], str):
            df_hour = self.df[self.df["Fecha"] == str(ddtt.date())]
            return any(df_hour["Hora"] == str(ddtt2))
        else:
            df_hour = self.df[self.df["Fecha"] == ddtt]
            return any(df_hour["Hora"] == ddtt2)

    def prepare_for_lst(self, ddtt):
        ddtt = pd.Timestamp(ddtt)
        if self.check_date(ddtt) and self.check_time(ddtt, hour=20):
            if isinstance(self.df["Fecha"][0], str):
                df2 = self.df[self.df["Fecha"] == str(ddtt.date())]
            else:
                df2 = self.df[self.df["Fecha"] == ddtt]

            if isinstance(df2["Hora"].iloc[0], str):
                time20 = df2[df2["Hora"] == str(datetime.time(hour=20))]
            else:
                time20 = df2[df2["Hora"] == datetime.time(hour=20)]

            idx = time20.index[0]
            df3 = df2[df2.index <= idx]
            df3 = df3[df3.index > idx - 50]
            ddtt_col = []
            for i in range(len(df3)):
                line = df3.iloc[i]
                dd = line["Fecha"]
                if not isinstance(dd, str):
                    dd = str(dd.date())
                tt = line["Hora"]
                if not isinstance(tt, str):
                    tt = str(tt)
                ddtt_col.append(datetime.datetime.strptime(dd + " " + tt, "%Y-%m-%d %H:%M:%S"))
            df4 = pd.DataFrame(df3.values, columns=df3.columns)
            df4["Tiempo"] = ddtt_col
            df4 = df4.drop(['Codigo', 'Fecha', 'Hora', 'Direccion de Viento'], axis=1)
            return df4


    def prepare_for_classifier(self, ddtt, asnm):
        # import pdb
        # pdb.set_trace()
        ddtt = pd.Timestamp(ddtt)
        # ["asnm", "T_14", "Hum_14", "VVin_14", "Prec_14", "RadSol_14", "PATM_14", ...20...]
        data = [asnm]
        if self.check_date(ddtt) and self.check_time(ddtt, hour=20) and self.check_time(ddtt, hour=14):
            if isinstance(self.df["Fecha"][0], str):
                df2 = self.df[self.df["Fecha"] == str(ddtt.date())]
            else:
                df2 = self.df[self.df["Fecha"] == ddtt]

            if isinstance(df2["Hora"].iloc[0], str):
                time14 = df2[df2["Hora"] == str(datetime.time(hour=14))].iloc[0]
                time20 = df2[df2["Hora"] == str(datetime.time(hour=20))].iloc[0]
            else:
                time14 = df2[df2["Hora"] == datetime.time(hour=14)].iloc[0]
                time20 = df2[df2["Hora"] == datetime.time(hour=20)].iloc[0]
            for dftime in [time14, time20]:
                data.append(dftime["Temperatura"])
                data.append(dftime["Humedad"])
                data.append(dftime["Velocidad de Viento"])
                data.append(dftime["Precipitacion"])
                data.append(dftime["Radiacion Solar"])
                data.append(dftime["Presion Atmosferica"])

            return data
        else:
            return None
