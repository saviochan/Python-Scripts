"""
Written by Qiaoling Cui, July 2020.
Note 'path' name, 'time', 'frame_shift' and 'pix_per_mm' values to be replaced each time
when analyzing a new SimBA 'xlsx' file!
"""
import numpy as np
import pandas as pd

# path name to be replaced each time when analyzing a new file, keep .xlsx!
# if code is in the same folder as data files (recommended), just put "filename.xlsx";
# otherwise need to put the full directory such as r"C:\Users\QIAOLING\Desktop\file\filename.xlsx".
path = "PV-ChR2_8007_Trial403.xlsx"

# fill in time (min) for when to start (inclusive) and stop (exclusive) for first bulk of trials,
# when to start (inclusive) and stop (exclusive) for second bulk of trials.
# if just have one bulk of trials, fill in first two with start and stop time, fill in the rest two with zeros!
time = [5,25,0,0]

# note the stim start frame is a bit variable from videos to videos, generally around 5 frames earlier than exact min
frame_shift = 4

pix_per_mm = 2.364285714

df = pd.read_excel(path)

# calculate distance (in cm) between each body parts and body center or between nose and tailbase

df['Ear_left_center_dist'] = np.sqrt((df.Ear_left_x - df.Center_x)**2 + (df.Ear_left_y - df.Center_y)**2)/pix_per_mm/10

df['Ear_right_center_dist'] = np.sqrt((df.Ear_right_x - df.Center_x)**2 + (df.Ear_right_y - df.Center_y)**2)/pix_per_mm/10

df['Nose_center_dist'] = np.sqrt((df.Nose_x - df.Center_x)**2 + (df.Nose_y - df.Center_y)**2)/pix_per_mm/10

df['Lat_left_center_dist'] = np.sqrt((df.Lat_left_x - df.Center_x)**2 + (df.Lat_left_y - df.Center_y)**2)/pix_per_mm/10

df['Lat_right_center_dist'] = np.sqrt((df.Lat_right_x - df.Center_x)**2 + (df.Lat_right_y - df.Center_y)**2)/pix_per_mm/10

df['Tailbase_center_dist'] = np.sqrt((df.Tail_base_x - df.Center_x)**2 + (df.Tail_base_y - df.Center_y)**2)/pix_per_mm/10

df['Tailend_center_dist'] = np.sqrt((df.Tail_end_x - df.Center_x)**2 + (df.Tail_end_y - df.Center_y)**2)/pix_per_mm/10

df['Nose_tailbase_dist'] = np.sqrt((df.Nose_x - df.Tail_base_x)**2 + (df.Nose_y - df.Tail_base_y)**2)/pix_per_mm/10

# calculate when to grab data
# convert time(min) to the index number to find the data values, start from 250 frames before 'light' period (-250)
start1 = time[0] * 60 * 10 - frame_shift - 250
stop1 = time[1] * 60 * 10 - frame_shift - 250
start2 = time[2] * 60 * 10 - frame_shift - 250
stop2 = time[3] * 60 * 10 - frame_shift - 250

# connect the separate bulks of trials if any

df_ear_left_center = pd.concat([df['Ear_left_center_dist'][start1:stop1], df['Ear_left_center_dist'][start2:stop2]])
df_ear_left_center.dropna(inplace=True)

df_ear_right_center = pd.concat([df['Ear_right_center_dist'][start1:stop1], df['Ear_right_center_dist'][start2:stop2]])
df_ear_right_center.dropna(inplace=True)

df_nose_center = pd.concat([df['Nose_center_dist'][start1:stop1], df['Nose_center_dist'][start2:stop2]])
df_nose_center.dropna(inplace=True)

df_lat_left_center = pd.concat([df['Lat_left_center_dist'][start1:stop1], df['Lat_left_center_dist'][start2:stop2]])
df_lat_left_center.dropna(inplace=True)

df_lat_right_center = pd.concat([df['Lat_right_center_dist'][start1:stop1], df['Lat_right_center_dist'][start2:stop2]])
df_lat_right_center.dropna(inplace=True)

df_tailbase_center = pd.concat([df['Tailbase_center_dist'][start1:stop1], df['Tailbase_center_dist'][start2:stop2]])
df_tailbase_center.dropna(inplace=True)

df_tailend_center = pd.concat([df['Tailend_center_dist'][start1:stop1], df['Tailend_center_dist'][start2:stop2]])
df_tailend_center.dropna(inplace=True)

df_nose_tailbase = pd.concat([df['Nose_tailbase_dist'][start1:stop1], df['Nose_tailbase_dist'][start2:stop2]])
df_nose_tailbase.dropna(inplace=True)

# separate the dist data per trial (by converting the data to array and reshape the array to 2d array)
# count the number of trials first (to determine number of rows for 2d array, also used later)
n = time[1]-time[0]+time[3]-time[2]
from pandas import DataFrame
df_ear_left_center = DataFrame(df_ear_left_center.values.reshape(n,600)).transpose()
df_ear_right_center = DataFrame(df_ear_right_center.values.reshape(n,600)).transpose()
df_nose_center = DataFrame(df_nose_center.values.reshape(n,600)).transpose()
df_lat_left_center = DataFrame(df_lat_left_center.values.reshape(n,600)).transpose()
df_lat_right_center = DataFrame(df_lat_right_center.values.reshape(n,600)).transpose()
df_tailbase_center = DataFrame(df_tailbase_center.values.reshape(n,600)).transpose()
df_tailend_center = DataFrame(df_tailend_center.values.reshape(n,600)).transpose()
df_nose_tailbase = DataFrame(df_nose_tailbase.values.reshape(n,600)).transpose()

# calculate row mean (across trials) for each dist dataframe
df['Ear_left_center'] = df_ear_left_center.mean(axis=1)
df['Ear_right_center'] = df_ear_right_center.mean(axis=1)
df['Nose_center'] = df_nose_center.mean(axis=1)
df['Lat_left_center'] = df_lat_left_center.mean(axis=1)
df['Lat_right_center'] = df_lat_right_center.mean(axis=1)
df['Tailbase_center'] = df_tailbase_center.mean(axis=1)
df['Tailend_center'] = df_tailend_center.mean(axis=1)
df['Nose_tailbase'] = df_nose_tailbase.mean(axis=1)

# concatenate all distance dataframes into one dataframe and save the dataframe to current excel

from openpyxl import load_workbook
book = load_workbook(path)
writer = pd.ExcelWriter(path, engine = 'openpyxl')
writer.book = book

group_names = ['Ear_left_center_dist','Ear_right_center_dist','Nose_center_dist','Lat_left_center_dist', \
'Lat_right_center_dist','Tailbase_center_dist','Tailend_center_dist','Nose_tailbase_dist']

df_dist = pd.concat([df_ear_left_center,df_ear_right_center,df_nose_center,df_lat_left_center, \
df_lat_right_center,df_tailbase_center,df_tailend_center,df_nose_tailbase],axis=1,keys = group_names)

# create a dataframe including mean for each dist dataframe
df_dist_mean = DataFrame(df, columns=['Ear_left_center','Ear_right_center','Nose_center','Lat_left_center', \
'Lat_right_center','Tailbase_center','Tailend_center','Nose_tailbase']).dropna()

# average per 10 data points for each trial
df_dist = df_dist.groupby(np.arange(len(df_dist))//10).mean()
df_dist_mean = df_dist_mean.groupby(np.arange(len(df_dist_mean))//10).mean()

df_dist.to_excel(writer, sheet_name = 'Dist (cm)')
df_dist_mean.to_excel(writer, sheet_name = 'Mean dist (cm)')

writer.save()
writer.close()
