#AGRIMED/scripts/carga_datos.py
import pandas as pd
import numpy as np
from datetime import time, date, datetime

# cargar datos y curvas de tiempo gracias al codigo de Francisco modificado
def process(df):
    print("-> drop repeated, before len: ", len(df))
    df = df.drop(df[df.duplicated(['Codigo', 'Fecha', 'Hora'])].index)
    print("-> after len: ", len(df))
    df = df.sort_values(by =['Codigo', 'Fecha', 'Hora'])
    df = df.reset_index(drop=True)
    return df

meses = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril", 
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre"
}

def is_summer(d):
    ini = datetime(day=21, month=12, year=2009)
    last_day = datetime(day=31, month=12, year=2009)
    first_day = datetime(day=1, month=1, year=2010)
    end = datetime(day=20, month=3, year=2010)
    return ini <= d <= last_day or first_day <= d < end

def is_fall(d):
    ini = datetime(day=20, month=3, year=2010)
    end = datetime(day=21, month=6, year=2010)
    return ini <= d < end

def is_winter(d):
    ini = datetime(day=21, month=6, year=2010)
    last_day = datetime(day=30, month=6, year=2010)
    first_day = datetime(day=1, month=7, year=2009)
    end = datetime(day=22, month=9, year=2009)
    return ini <= d <= last_day or first_day <= d < end

def is_spring(d):
    ini = datetime(day=22, month=9, year=2009)
    end = datetime(day=21, month=12, year=2009)
    return ini <= d < end

def read_year(file1, file2):
    df1 = pd.read_excel(file1)
    df2 = pd.read_excel(file2)
#     df3 = pd.read_excel(file3)
    df = pd.concat([df1, df2], ignore_index=True)
    df = process(df)
    df.columns = ["Codigo", "Fecha", "Hora", "Temp.", "Hum.", "Dir.Viento", "Vel.Viento", "Precip.", "Rad.Sol", "P.Atm"]
    
    season = []
    for v in df["Fecha"]:
        d = v.to_pydatetime()
        if is_summer(d):
            season.append("Verano")
        elif is_fall(d):
            season.append("Otoño")
        elif is_winter(d):
            season.append("Invierno")
        elif is_spring(d):
            season.append("Primavera")
        else:
            raise ValueError("Fallo")
            
    df["Estacion"] = season
    df["Hora"] = [round(x.hour * 60 + x.minute) for x in df["Hora"]]
    df["Mes"] = [meses.get(int(x.month), "None") for x in df["Fecha"]]
    df["Dia"] = [x.date() for x in df["Fecha"]]
    df = df.drop(["Codigo", "Fecha"], axis=1)
    print(df.count())
    df.head()
    return df


def encontrar_dias(df, hora_inicio, hora_final):
    """
    Input:
        (dataframe, hora_inicio, hora_final)
    Return:
        Diccionario con las fechas de los dias tomados, cada fecha contiene las series de tiempo
        correspondientes

    Esta funcion entrega un diccionario con los dias como clave y un dataframe dentro de este con
    las distintas variables como:
        - temperatura
        - humedad
        - rad.Solar
        - etc
    
    El dia contiene la información entre ciertas horas de interés
    """
    
    dias = {}
    inicio = df['Dia'][0]
    index2add = []
    
    ordinal = False
    if hora_final > hora_inicio: ordinal = True
    
    for idx, hora in enumerate(df['Hora']):
        if ordinal and (hora < hora_final and hora >= hora_inicio):
            index2add.append(idx)
        if not(ordinal) and (hora < hora_final or hora >= hora_inicio):
            index2add.append(idx)
        elif hora == hora_final:
            aux_df = df.loc[index2add]
            aux_df['Hora'] = [round(x.hour * 60 + x.minute) for x in aux_df['Hora']]
            dias[df['Dia'][idx]] = aux_df
            index2add = []
    
    return dias
