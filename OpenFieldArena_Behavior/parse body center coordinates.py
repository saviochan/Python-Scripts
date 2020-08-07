"""
Written by Qiaoling Cui, July 2020.
Note 'path' name, 'time', 'frame_shift' and 'pixel_per_mm' values to be replaced each time
when analyzing a new SimBA 'xlsx' file!
"""
import numpy as np
import pandas as pd
from pandas import DataFrame

# path name to be replaced each time when analyzing a new file, keep .xlsx!
# if code is in the same folder as data files (recommended), just put "filename.xlsx";
# otherwise need to put the full directory such as r"C:\Users\QIAOLING\Desktop\file\filename.xlsx".
path = "DMS_dSPN_ChR2_trial_451.xlsx"

# fill in time (min) for when to start (inclusive) and stop (exclusive) for first bulk of trials,
# when to start (inclusive) and stop (exclusive) for second bulk of trials.
# if just have one bulk of trials, fill in first two with start and stop time, fill in the rest two with zeros!
time = [11,25,0,0]

# note the stim start frame is a bit variable from videos to videos, generally around 5 frames earlier than exact min
frame_shift = 6

pixel_per_mm = 2.632142857

df = pd.read_excel(path)

# calculate when to grab data
# convert time(min) to the index number to find the data values, start from 250 frames before 'light' period (-250)
start1 = time[0] * 60 * 10 - frame_shift - 250
stop1 = time[1] * 60 * 10 - frame_shift - 250
start2 = time[2] * 60 * 10 - frame_shift - 250
stop2 = time[3] * 60 * 10 - frame_shift - 250

# connect the separate bulks of trials if any

df_center_x = pd.concat([df['Center_x'][start1:stop1], df['Center_x'][start2:stop2]])
df_center_x.dropna(inplace=True)
min_x = df_center_x.min()
df_center_x = df_center_x - min_x

df_center_y = pd.concat([df['Center_y'][start1:stop1], df['Center_y'][start2:stop2]])
df_center_y.dropna(inplace=True)
min_y = df_center_y.min()
df_center_y = df_center_y - min_y

###### GET CENTER COORDINATES FOR STIM TRIALS ######

# separate the coordinates data per trial (by converting the data to array and reshape the array to 2d array)
# count the number of trials first (to determine number of rows for 2d array, also used later)
n = time[1]-time[0]+time[3]-time[2]
center_x_arr = np.array(df_center_x).reshape(n,600)
center_y_arr = np.array(df_center_y).reshape(n,600)

# sample data for pre, stim, and post periods
center_x_pre = center_x_arr[:,150:250]
center_x_light = center_x_arr[:,250:350]
center_x_post = center_x_arr[:,350:450]
center_y_pre = center_y_arr[:,150:250]
center_y_light = center_y_arr[:,250:350]
center_y_post = center_y_arr[:,350:450]

# concatenate the coordinates data (pre/stim/post) from each trial to 1d array (by flattening 2d array),
# then put the 1d array to a column of the dataframe (pd.Series)
df['x_pre'] = pd.Series(center_x_pre.flatten())
df['x_light'] = pd.Series(center_x_light.flatten())
df['x_post'] = pd.Series(center_x_post.flatten())
df['y_pre'] = pd.Series(center_y_pre.flatten())
df['y_light'] = pd.Series(center_y_light.flatten())
df['y_post'] = pd.Series(center_y_post.flatten())

########## put together all data into data frames and save data frames to current excel ##########

from openpyxl import load_workbook
book = load_workbook(path)
writer = pd.ExcelWriter(path, engine = 'openpyxl')
writer.book = book

# create a dataframe including coordinates for pre/light/post periods
df_coordinates = DataFrame(df, columns=['x_pre','y_pre','x_light','y_light','x_post','y_post'])/pixel_per_mm

# save dataframes into excel
df_coordinates.to_excel(writer, sheet_name = 'Center_coordinates (mm)', index=False)

writer.save()
writer.close()
