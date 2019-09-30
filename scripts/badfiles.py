import pandas as pd
import glob
import numpy as np


headers = ['Codigo', 'Fecha', 'Hora', 'Temperatura', 'Humedad',
           'Direccion de Viento', 'Velocidad de Viento', 'Precipitacion',
           'Radiacion Solar', 'Presion Atmosferica']


class BadFiles(object):

    def __init__(self, raw_folder):
        self.raw_folder = raw_folder
        self.curr_file = None
        self.curr_error = None
        self.files = []
        self.errors = []
        self.counter = 0
        self.counter_bads = 0
        self.bad_station = False

    def _update(self):
        self.files.append(self.curr_file)
        self.errors.append(self.curr_error)
        self.counter_bads += 1

    def bad_header(self, df):
        res = any([name not in headers for name in df.columns]) or len(headers) != len(df.columns)
        if res:
            self.curr_error = "ERROR.badHeader"
            self._update()
        return res

    def has_nan(self, df):
        res = df.isnull().any().any()
        if res:
            self.curr_error = "ERROR.NaN"
            self._update()
        return res

    def has_bad_data(self, df):
        error_type = None
        if not df[df['Velocidad de Viento'] < 0].empty:
            error_type = "INCONSISTENCY.NegVel"
        elif not df[df["Direccion de Viento"] < 0].empty:
            error_type = "INCONSISTENCY.NegDir"
        elif not df[df["Precipitacion"] < 0].empty:
            error_type = "INCONSISTENCY.Neg.Precip"
        elif not df[df["Radiacion Solar"] < 0].empty:
            error_type = "INCONSISTENCY.NegRad"
        elif not df[df["Humedad"] < 0].empty:
            error_type = "INCONSISTENCY.NegHum"
        elif not df[df["Presion Atmosferica"] <= 0].empty:
            error_type = "INCONSISTENCY.ZeroOrNegPAtm"

        if error_type is not None:
            self.curr_error = error_type
            self._update()
            return True
        return False

    def is_empty(self, df):
        res = len(df) <= 1
        if res:
            self.curr_error = "ERROR.NoResultFile"
            self._update()
        return res

    def open_file(self):
        df = None
        if ".csv" in self.curr_file:
            df = pd.read_csv(self.curr_file, sep='\t', lineterminator='\r', decimal=",")
        else:
            try:
                df = pd.read_excel(self.curr_file)
            except:
                self.curr_error = "ERROR.file"
                self._update()
        return df

    def check_errors(self, df):
        if df is not None:
            if self.bad_header(df):
                return True
            elif self.is_empty(df):
                return True
            elif self.has_nan(df):
                return True
            elif self.has_bad_data(df):
                return True
        else:
            return True
        return False

    def check_excel(self, file):
        self.counter += 1
        file = file.replace("\\", "/")
        self.curr_file = file
        self.curr_error = None
        df = self.open_file()
        res = self.check_errors(df)
        if res:
            print("%s.%s" % (self.curr_error, self.curr_file))
            self.bad_station = res

        self.curr_file = None
        self.curr_error = None
        return df

    def check_region(self, path):
        path = path.replace("\\", "/")
        print(":::::: %s ::::::" % path.split("/")[-1])
        for folder in glob.glob(path + "/*"):
            dfs = []
            files = []
            for file in glob.glob(folder + "/*"):
                dfs.append(self.check_excel(file))
                files.append(file)

            if not self.bad_station:
                if self.check_not_unique_code(dfs):
                    for file in files:
                        if file not in self.files:
                            self.files.append(file)
                            self.errors.append(self.curr_error)
                    print("%s.%s" % (self.curr_error, folder))

            self.bad_station = False

    def check_all(self):
        for path in glob.glob(self.raw_folder + "/*"):
            if all(x not in path for x in ["FDF semestre 2 2010", "DE MALLANES Y LA ANTARTIDA"]):
                self.check_region(path)

    def recheck_all(self):
        for path in glob.glob(self.raw_folder + "/*"):
            self.recheck_region(path)

    def recheck_region(self, path):
        path = path.replace("\\", "/")
        for station in glob.glob(path + "/*.csv"):
            df = self.recheck_csv(station)
            if not self.bad_station:
                if self.check_not_unique_code([df]):
                    if station not in self.files:
                        self.files.append(station)
                        self.errors.append(self.curr_error)
                    print("%s.%s" % (self.curr_error, station))
            self.bad_station = False

    def recheck_csv(self, file):
        self.counter += 1
        file = file.replace("\\", "/")
        self.curr_file = file
        self.curr_error = None
        df = pd.read_csv(file)
        res = self.check_errors(df)
        if res:
            print("%s.%s" % (self.curr_error, self.curr_file))
            self.bad_station = res

        self.curr_file = None
        self.curr_error = None
        return df

    def check_not_unique_code(self, dfs):
        codigo = None
        res = False
        for df in dfs:
            df_code = np.unique(list(df['Codigo']))
            if len(df_code) == 1:
                if codigo is None:
                    codigo = df_code[0]
                else:
                    if codigo != df_code[0]:
                        res = True
            else:
                res = True

        if res:
            self.curr_error = "ERROR.notUniqueCodeInStation"

        return res

    def save(self, path):
        np.save(path + "/bad_files", self.files)
        np.save(path + "/errors", self.errors)


