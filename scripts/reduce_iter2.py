import multiprocessing as mp
import pandas as pd
import numpy as np
import glob
from datetime import date, datetime, time, timedelta
from collections import defaultdict
import os

""" reduciremos los dias que no tengan medicion durante la noche """

""" buscaremos dias con menos de 32 mediciones en el intervalo de 20 hrs y 10 hrs del dia siguiente """


def read_data(path):
    dfs = []
    dict_meta = {"region": [], "estacion": [], "codigo": []}
    for file in glob.glob(path + "/*/*"):
        print(file + " " * 30, end="\r")
        file = file.replace("\\", "/")
        dict_meta["region"].append(file.split("/")[-2])
        dict_meta["estacion"].append(file.split("/")[-1].split(".")[0])
        df = pd.read_csv(file)
        dict_meta["codigo"].append(df["Codigo"][0])
        dfs.append(df)
    print(file + " " * 30)
    print("concatenate and resort ...", end="")
    df = pd.concat(dfs, ignore_index=True)
    df = df.sort_values(by=['Codigo', 'Fecha', 'Hora'])
    df = df.drop_duplicates(subset=['Codigo', 'Fecha', 'Hora'])
    df = df.reset_index(drop=True)
    print("done")
    return df.values


def worker_datetime(data, ini, end, res_q):
    print("starting worker range [{}, {}]... ".format(ini, end), end="")
    ddtt = []
    displaced_date = []
    deltatime = timedelta(hours=14)
    c = 0
    for i in range(end - ini):
        # if i % 1000 == 0:
        #     print(i, end='\r')
        d = data[i][1]
        t = data[i][2]
        if " " in d:
            d = d.split(" ")[0]
            datm = datetime.strptime(d + " " + t, '%Y-%m-%d %H:%M:%S')
        elif "-" in d:
            datm = datetime.strptime(d + " " + t, '%Y-%m-%d %H:%M:%S')
        else:
            datm = datetime.strptime(d + " " + t, '%d/%m/%Y %H:%M:%S')

        #         data[i][10] = (datm + deltatime).__str__()
        #         data[i][11] = datm

        displaced_date.append((datm + deltatime).date().__str__())
        ddtt.append(datm + deltatime)
        c += 1
    res_q.put((ini, end, displaced_date, ddtt))
    print("done")


def run_datetime(data, N):
    # obtenemos los indices de los subrangos
    print("obteniendo sub rangos ... ")
    r = data.shape[0] // N
    idxs = np.arange(N + 1) * r

    # lanzamos los workers
    m = mp.Manager()
    res_q = m.Queue()
    print("starting workers ....")
    jobs = []
    for i in range(len(idxs) - 1):
        ini = idxs[i]
        end = idxs[i + 1]
        print("launching worker for [{},{}]".format(ini, end))
        jobs.append(mp.Process(target=worker_datetime, args=(data[ini:end], ini, end, res_q)))
        jobs[-1].start()
    print("waiting workers ...")
    for p in jobs:
        p.join()
    return res_q


def get_data(n, res_q):
    arr = np.full((n, 2), None)
    qsize = res_q.qsize()
    while qsize > 0:
        ini, end, displaced, ddtt = res_q.get()
        arr[ini:end,0] = ddtt
        arr[ini:end,1] = displaced
        qsize -= 1
    return arr


path = "../data/cleared"
data = read_data(path)
res_q = run_datetime(data, 8)
print("DONE")
arr = get_data(data.shape[0], res_q)
data_final = np.append(data, arr, axis=1)
np.save("../data/cleared2/datetime2.npy", data_final)