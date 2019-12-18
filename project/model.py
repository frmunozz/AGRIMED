# from .lstm.lstm_conv2 import load_model, predict
from .classifier.regressor import Regressor
import numpy as np
import pandas as pd
import datetime


class Predictor:
    def __init__(self, bc_model_path=None, lstm_model_path=None):
        self.bc_path = bc_model_path
        self.lstm_path = lstm_model_path
        self.classifier = self.load_binary_classifier()
        # self.lstm = self.load_lstm_predictor()

    def load_binary_classifier(self):
        reg = Regressor()
        reg.load("class_binario_win", path=self.bc_path)
        return reg

    # def load_lstm_predictor(self):
    #     lstm = load_model(path=self.lstm_path)
    #     return lstm

    def predict_classifier(self, input, threshold=0.5):
        pred_prob = self.classifier.predict(input)
        return pred_prob[1] > threshold, pred_prob

    # def predict_curve(self, input, device="cpu"):
    #     return predict(input, self.lstm, device="cpu")


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

    def prepare_for_lst(self):
        pass

    def prepare_for_classifier(self, ddtt, asnm, lat):
        import pdb
        pdb.set_trace()
        ddtt = pd.Timestamp(ddtt)
        # ["lat", "asnm", "T_14", "Hum_14", "VVin_14", "Prec_14", "RadSol_14", "PATM_14", ...20...]
        data = [lat, asnm]
        if self.check_date(ddtt) and self.check_time(ddtt, hour=20) and self.check_time(ddtt, hour=14):
            if isinstance(self.df["Fecha"], str):
                df2 = self.df[self.df["Fecha"] == str(ddtt.date())]
            else:
                df2 = self.df[self.df["Fecha"] == ddtt]

            if isinstance(df2["Hora"], str):
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
