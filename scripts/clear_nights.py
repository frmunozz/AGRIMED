import pandas as pd
import numpy as np
import glob
from datetime import date, datetime, time, timedelta
from collections import defaultdict
import os



def count_night_data(sub_sub_data):
	c = 0
	ddtt = sub_sub_data[0][10]
	day = str(ddtt.date())
	start = datetime.strptime(day + " 10:00:00", '%Y-%m-%d %H:%M:%S')
	end = start + timedelta(hours=14)
	for i, row in enumerate(sub_sub_data):
		if start <= row[10] <= end:
			c += 1
	return c


def find_min_temp_all_day(sub_sub_data):
	temps = sub_sub_data[:,3]
	idx = np.argmin(temps)
	return idx

def find_min_temp_night(sub_sub_data):
	day = sub_sub_data[0][11]
	start_night = datetime.strptime(day + " 10:00:00", '%Y-%m-%d %H:%M:%S')
	end_night = start_night + timedelta(hours=14)
	ini = 0
	while sub_sub_data[ini][10] < start_night:
		ini += 1
	end = len(sub_sub_data) - 1
	temps = sub_sub_data[ini:end,3]
	return ini + np.argmin(temps)


def clear_bad_days(data):
	last_code = data[0][0]
	last_day = data[0][11]
	good_data = np.full(data.shape, None)
	min_temps_idxs = []
	min_temps_night_idxs = []
	pointer = 0
	i = 0
	bads = []
	for j, row in enumerate(data):
		if j % 5000 == 0:
			print("processing row number: ", j, end='\r')
		if row[0] != last_code:
			count = count_night_data(data[i:j])
			if count <= 34:
				bads.append((i, j, count))
			else:
				good_data[pointer:pointer + (j-i)] = data[i:j]
				pointer += (j-i)
				min_temps_idxs.append(i + find_min_temp_all_day(data[i:j]))
				min_temps_night_idxs.append(i + find_min_temp_night(data[i:j]))

			i = j
			last_code = row[0]
			last_day = row[11]
		else:
			if last_day != row[11]:
				count = count_night_data(data[i:j])
				if count <= 34:
					bads.append((i, j, count))
				else:
					good_data[pointer:pointer + (j-i)] = data[i:j]
					pointer += (j-i)
					min_temps_idxs.append(i + find_min_temp_all_day(data[i:j]))
					min_temps_night_idxs.append(i + find_min_temp_night(data[i:j]))

				i = j
				last_day = row[11]
	# luego, generamos un array de solo temperaturas minimas
	print("processing row number: ", j)
	print("obteniendo datos de temperaturas minimas de todo el dia ...")
	min_temps = np.full((len(min_temps_idxs), data.shape[1]), None)
	for k, idx in enumerate(min_temps_idxs):
		if k % 1000 == 0:
			print("processing day: ", k, end='\r')
		min_temps[k] = data[idx]
	print("processing day: ", k+1, " DONE")
	print("obtenemos datos de temperaturas minimas considerando solo noche ...")
	min_temps_night = np.full((len(min_temps_night_idxs), data.shape[1]), None)
	for k, idx in enumerate(min_temps_night_idxs):
		if k % 1000 == 0:
			print("processing day: ", k, end='\r')
		min_temps_night[k] = data[idx]
	return bads, good_data, pointer, min_temps, min_temps_idxs, min_temps_night




print("cargamos datos")
data = np.load("../data/cleared2/datetime2.npy", allow_pickle=True)
bads, good_data, p, min_temps, min_temps_idxs, min_temps_night = clear_bad_days(data)
goods = good_data[:p]
np.save("../data/cleared2/dataset.npy", goods)
np.save("../data/cleared2/bad_days_slices.npy", bads)
np.save("../data/cleared2/min_temps.npy", min_temps)
np.save("../data/cleared2/min_temps_night.npy", min_temps_night)