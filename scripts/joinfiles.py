import pandas as pd
import glob
import os


class JoinFiles(object):

    def __init__(self, raw_path, new_path):
        self.raw_path = raw_path
        self.new_path = new_path
        self.region = None

    def get_region(self, path_path):
        return path_path.split("/")[-1]

    def get_station(self, folder_path):
        return folder_path.split("/")[-1]

    def join_station(self, folder):
        dfs = []
        outdir = "{}/{}".format(self.new_path, self.region)
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        station = self.get_station(folder)
        outfile = "{}/{}.csv".format(outdir, station)
        print("creating:", outfile)
        for file in glob.glob(folder + "/*"):
            file = file.replace("\\", "/")
            if ".csv" in file:
                df = pd.read_csv(file, sep='\t', lineterminator='\r')
            else:
                df = pd.read_excel(file)
            dfs.append(df)
            final_df = pd.concat(dfs, ignore_index=True)
            final_df = final_df.sort_values(by=['Codigo', 'Fecha', 'Hora'])
            final_df = final_df.reset_index(drop=True)
            final_df.to_csv(outfile)

    def process_region(self, path):
        path = path.replace("\\", "/")
        self.region = self.get_region(path)
        print(":::::: %s ::::::" % self.region)
        for folder in glob.glob(path + "/*"):
            folder = folder.replace("\\", "/")
            self.join_station(folder)

    def process_all(self):
        for path in glob.glob(self.raw_path + "/*"):
            if all(x not in path for x in ["FDF semestre 2 2010", "DE MALLANES Y LA ANTARTIDA"]):
                self.process_region(path)