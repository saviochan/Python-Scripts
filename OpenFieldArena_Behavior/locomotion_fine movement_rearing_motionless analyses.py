"""
Written by Qiaoling Cui, July 2020.
Note 'path' name, 'time', 'frame_shift' and 'pixel_per_mm' values to be replaced each time
when analyzing a new SimBA 'xlsx' file!
"""
import numpy as np
import pandas as pd

# path name to be replaced each time when analyzing a new file, keep .xlsx!
# if code is in the same folder as data files (recommended), just put "filename.xlsx";
# otherwise need to put the full directory such as r"C:\Users\QIAOLING\Desktop\file\filename.xlsx".
path = "STN-ACR2_Trial348_3761.xlsx"

# fill in time (min) for when to start (inclusive) and stop (exclusive) for first bulk of trials,
# when to start (inclusive) and stop (exclusive) for second bulk of trials.
# if just have one bulk of trials, fill in first two with start and stop time, fill in the rest two with zeros!
time = [5,15,0,0]

# note the stim start frame is a bit variable from videos to videos, generally around 5 frames earlier than exact min
frame_shift = 4

pixel_per_mm = 2.521428571

df = pd.read_excel(path)

# define a function to calculate distance moved for a body part between two successive frames
import math
get_dist = lambda x1,y1,x2,y2: math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

# calculate distance moved (in pixels) for ears, body center, laterals, and tailbase across all frames

r = len(df.index)-1

ear_left_dist_moved = [get_dist(df['Ear_left_x'][i],df['Ear_left_y'][i],df['Ear_left_x'][i+1], \
df['Ear_left_y'][i+1]) for i in range(r)]

ear_right_dist_moved = [get_dist(df['Ear_right_x'][i],df['Ear_right_y'][i],df['Ear_right_x'][i+1], \
df['Ear_right_y'][i+1]) for i in range(r)]

center_dist_moved = [get_dist(df['Center_x'][i],df['Center_y'][i],df['Center_x'][i+1], \
df['Center_y'][i+1]) for i in range(r)]

lat_left_dist_moved = [get_dist(df['Lat_left_x'][i],df['Lat_left_y'][i],df['Lat_left_x'][i+1], \
df['Lat_left_y'][i+1]) for i in range(r)]

lat_right_dist_moved = [get_dist(df['Lat_right_x'][i],df['Lat_right_y'][i],df['Lat_right_x'][i+1], \
df['Lat_right_y'][i+1]) for i in range(r)]

tailbase_dist_moved = [get_dist(df['Tail_base_x'][i],df['Tail_base_y'][i],df['Tail_base_x'][i+1], \
df['Tail_base_y'][i+1]) for i in range(r)]

# put dist_moved and ratio to columns of dataframe
# (shift one cell down for dist_moved to match the rows,
# leaving first and last cells as 'NaN' but last cells wouldn't be used)
df['Ear_left_dist_moved'] = pd.Series(ear_left_dist_moved).shift(periods=1)
df['Ear_right_dist_moved'] = pd.Series(ear_right_dist_moved).shift(periods=1)
df['Center_dist_moved'] = pd.Series(center_dist_moved).shift(periods=1)
df['Lat_left_dist_moved'] = pd.Series(lat_left_dist_moved).shift(periods=1)
df['Lat_right_dist_moved'] = pd.Series(lat_right_dist_moved).shift(periods=1)
df['Tailbase_dist_moved'] = pd.Series(tailbase_dist_moved).shift(periods=1)
df['Ratio'] = df['Mouse_nose_to_tail']/df['Mouse_width']

# calculate when to grab data
# convert time(min) to the index number to find the data values, start from 250 frames before 'light' period (-250)
start1 = time[0] * 60 * 10 - frame_shift - 250
stop1 = time[1] * 60 * 10 - frame_shift - 250
start2 = time[2] * 60 * 10 - frame_shift - 250
stop2 = time[3] * 60 * 10 - frame_shift - 250
# stop frame (exclusive) of 5min pre trial period (baseline, bsln)
stop_bsln = 5 * 60 * 10 - frame_shift

# connect the separate bulks of trials if any

df_ear_left = pd.concat([df['Ear_left_dist_moved'][start1:stop1], df['Ear_left_dist_moved'][start2:stop2]])
df_ear_left.dropna(inplace=True)

df_ear_right = pd.concat([df['Ear_right_dist_moved'][start1:stop1], df['Ear_right_dist_moved'][start2:stop2]])
df_ear_right.dropna(inplace=True)

df_center = pd.concat([df['Center_dist_moved'][start1:stop1], df['Center_dist_moved'][start2:stop2]])
df_center.dropna(inplace=True)

df_lat_left = pd.concat([df['Lat_left_dist_moved'][start1:stop1], df['Lat_left_dist_moved'][start2:stop2]])
df_lat_left.dropna(inplace=True)

df_lat_right = pd.concat([df['Lat_right_dist_moved'][start1:stop1], df['Lat_right_dist_moved'][start2:stop2]])
df_lat_right.dropna(inplace=True)

df_tailbase = pd.concat([df['Tailbase_dist_moved'][start1:stop1], df['Tailbase_dist_moved'][start2:stop2]])
df_tailbase.dropna(inplace=True)

df_rearing = pd.concat([df['Rearing'][start1:stop1], df['Rearing'][start2:stop2]])
df_rearing.dropna(inplace=True)

df_ratio = pd.concat([df['Ratio'][start1:stop1], df['Ratio'][start2:stop2]])
df_ratio.dropna(inplace=True)

df_angle = pd.concat([df['Mouse_angle'][start1:stop1], df['Mouse_angle'][start2:stop2]])
df_angle.dropna(inplace=True)

########## FOR STIM TRIALS ##########
###### CALCULATE LOCOMOTION ######

# set dist_moved values of body center above the threshold and exclude rearing to calculate locomotion data
# (Boolean True), use 'pixels/mm' value from video_info csv file divided by 2 as the threshold value,
# i.e., above 0.5 mm movement per adjacent frames (0.5 cm/s)
thres = pixel_per_mm/2
df_locomotion = (df_center > thres) & (df_rearing == 0)

# separate the locomotion data per trial (by converting the data to array and reshape the array to 2d array)
# count the number of trials first (to determine number of rows for 2d array, also used later)
n = time[1]-time[0]+time[3]-time[2]
locomotion_arr = np.array(df_locomotion).reshape(n,600)

# sample data for pre, stim, and post periods
locomotion_pre = locomotion_arr[:,150:250]
locomotion_stim = locomotion_arr[:,250:350]
locomotion_post = locomotion_arr[:,350:450]

# count the number of locomotion bouts and the number of time points in each bout (consecutive True values
# as a bout, key), per row in the array

import itertools
count_locomotion_pre = lambda locomotion_pre: [sum(1 for _ in group) for key, group in \
itertools.groupby(locomotion_pre) if key]
count_locomotion_stim = lambda locomotion_stim: [sum(1 for _ in group) for key, group in \
itertools.groupby(locomotion_stim) if key]
count_locomotion_post = lambda locomotion_post: [sum(1 for _ in group) for key, group in \
itertools.groupby(locomotion_post) if key]

locomotion_count_pre = [count_locomotion_pre(locomotion_pre[i]) for i in range(n)]
locomotion_count_stim = [count_locomotion_stim(locomotion_stim[i]) for i in range(n)]
locomotion_count_post = [count_locomotion_post(locomotion_post[i]) for i in range(n)]

# convert the number of time points in each bout to duration, as each time point (i) is for 0.1s
locomotion_dur_pre = [[i/10.0 for i in lst] for lst in locomotion_count_pre]
locomotion_dur_stim = [[i/10.0 for i in lst] for lst in locomotion_count_stim]
locomotion_dur_post = [[i/10.0 for i in lst] for lst in locomotion_count_post]

# filter trials wothout numbers (empty sublists)
locomotion_dur_pre = list(filter(None, locomotion_dur_pre))
locomotion_dur_stim = list(filter(None, locomotion_dur_stim))
locomotion_dur_post = list(filter(None, locomotion_dur_post))

# calculate mean bout duration values for each trial (sublist)
from statistics import mean
locomotion_dur_pre_avgs = [mean(lst) for lst in locomotion_dur_pre]
locomotion_dur_stim_avgs = [mean(lst) for lst in locomotion_dur_stim]
locomotion_dur_post_avgs = [mean(lst) for lst in locomotion_dur_post]

# put mean bout duration values to columns of data frame
df['Locomotion_dur_pre'] = pd.Series(locomotion_dur_pre_avgs)
df['Locomotion_dur_stim'] = pd.Series(locomotion_dur_stim_avgs)
df['Locomotion_dur_post'] = pd.Series(locomotion_dur_post_avgs)

# calculate % time spent locomotion
percent_time_locomotion_pre = sum([sum(lst) for lst in locomotion_dur_pre])/n/10*100
percent_time_locomotion_stim = sum([sum(lst) for lst in locomotion_dur_stim])/n/10*100
percent_time_locomotion_post = sum([sum(lst) for lst in locomotion_dur_post])/n/10*100

# put % time locomotion to columns of data frame
df['Percent_time_locomotion_pre'] = pd.Series(percent_time_locomotion_pre)
df['Percent_time_locomotion_stim'] = pd.Series(percent_time_locomotion_stim)
df['Percent_time_locomotion_post'] = pd.Series(percent_time_locomotion_post)

# calculate frequency for locomotion bouts (per 10 s)
locomotion_freq_pre = sum([len(lst) for lst in locomotion_dur_pre])/n
locomotion_freq_stim = sum([len(lst) for lst in locomotion_dur_stim])/n
locomotion_freq_post = sum([len(lst) for lst in locomotion_dur_post])/n

# put frequency to columns of data frame
df['Locomotion_freq_pre'] = pd.Series(locomotion_freq_pre)
df['Locomotion_freq_stim'] = pd.Series(locomotion_freq_stim)
df['Locomotion_freq_post'] = pd.Series(locomotion_freq_post)

###### CALCULATE FINE MOVEMENT ######

df_fine_movement = ((df_ear_left > thres) | (df_ear_right > thres) | (df_tailbase > thres) \
| (df_lat_left > thres) | (df_lat_right > thres)) & (df_center <= thres) & (df_rearing == 0)

# separate the fine_movement data per trial
fine_movement_arr = np.array(df_fine_movement).reshape(n,600)

# sample data for pre, stim, and post periods
fine_movement_pre = fine_movement_arr[:,150:250]
fine_movement_stim = fine_movement_arr[:,250:350]
fine_movement_post = fine_movement_arr[:,350:450]

# count the number of fine_movement bouts and the number of time points in each bout

count_fine_movement_pre = lambda fine_movement_pre: [sum(1 for _ in group) for key, group in \
itertools.groupby(fine_movement_pre) if key]
count_fine_movement_stim = lambda fine_movement_stim: [sum(1 for _ in group) for key, group in \
itertools.groupby(fine_movement_stim) if key]
count_fine_movement_post = lambda fine_movement_post: [sum(1 for _ in group) for key, group in \
itertools.groupby(fine_movement_post) if key]

fine_movement_count_pre = [count_fine_movement_pre(fine_movement_pre[i]) for i in range(n)]
fine_movement_count_stim = [count_fine_movement_stim(fine_movement_stim[i]) for i in range(n)]
fine_movement_count_post = [count_fine_movement_post(fine_movement_post[i]) for i in range(n)]

# convert the number of time points in each bout to duration
fine_movement_dur_pre = [[i/10.0 for i in lst] for lst in fine_movement_count_pre]
fine_movement_dur_stim = [[i/10.0 for i in lst] for lst in fine_movement_count_stim]
fine_movement_dur_post = [[i/10.0 for i in lst] for lst in fine_movement_count_post]

# filter trials without numbers (empty sublists)
fine_movement_dur_pre = list(filter(None, fine_movement_dur_pre))
fine_movement_dur_stim = list(filter(None, fine_movement_dur_stim))
fine_movement_dur_post = list(filter(None, fine_movement_dur_post))

# calculate mean bout duration values for each trial (sublist)
fine_movement_dur_pre_avgs = [mean(lst) for lst in fine_movement_dur_pre]
fine_movement_dur_stim_avgs = [mean(lst) for lst in fine_movement_dur_stim]
fine_movement_dur_post_avgs = [mean(lst) for lst in fine_movement_dur_post]

# put mean bout duration values to columns of data frame
df['Fine_movement_dur_pre'] = pd.Series(fine_movement_dur_pre_avgs)
df['Fine_movement_dur_stim'] = pd.Series(fine_movement_dur_stim_avgs)
df['Fine_movement_dur_post'] = pd.Series(fine_movement_dur_post_avgs)

# calculate % time spent fine_movement
percent_time_fine_movement_pre = sum([sum(lst) for lst in fine_movement_dur_pre])/n/10*100
percent_time_fine_movement_stim = sum([sum(lst) for lst in fine_movement_dur_stim])/n/10*100
percent_time_fine_movement_post = sum([sum(lst) for lst in fine_movement_dur_post])/n/10*100

# put % time fine_movement to columns of data frame
df['Percent_time_fine_movement_pre'] = pd.Series(percent_time_fine_movement_pre)
df['Percent_time_fine_movement_stim'] = pd.Series(percent_time_fine_movement_stim)
df['Percent_time_fine_movement_post'] = pd.Series(percent_time_fine_movement_post)

# calculate frequency for fine_movement bouts (per 10 s)
fine_movement_freq_pre = sum([len(lst) for lst in fine_movement_dur_pre])/n
fine_movement_freq_stim = sum([len(lst) for lst in fine_movement_dur_stim])/n
fine_movement_freq_post = sum([len(lst) for lst in fine_movement_dur_post])/n

# put frequency to columns of data frame
df['Fine_movement_freq_pre'] = pd.Series(fine_movement_freq_pre)
df['Fine_movement_freq_stim'] = pd.Series(fine_movement_freq_stim)
df['Fine_movement_freq_post'] = pd.Series(fine_movement_freq_post)

###### CALCULATE REARING ######

# separate the rearing data per trial
rearing_arr = np.array(df_rearing == 1).reshape(n,600)

# sample data for pre, stim, and post periods
rearing_pre = rearing_arr[:,150:250]
rearing_stim = rearing_arr[:,250:350]
rearing_post = rearing_arr[:,350:450]

# count the number of rearing bouts and the number of time points in each bout

count_rearing_pre = lambda rearing_pre: [sum(1 for _ in group) for key, group in \
itertools.groupby(rearing_pre) if key]
count_rearing_stim = lambda rearing_stim: [sum(1 for _ in group) for key, group in \
itertools.groupby(rearing_stim) if key]
count_rearing_post = lambda rearing_post: [sum(1 for _ in group) for key, group in \
itertools.groupby(rearing_post) if key]

rearing_count_pre = [count_rearing_pre(rearing_pre[i]) for i in range(n)]
rearing_count_stim = [count_rearing_stim(rearing_stim[i]) for i in range(n)]
rearing_count_post = [count_rearing_post(rearing_post[i]) for i in range(n)]

# convert the number of time points in each bout to duration
rearing_dur_pre = [[i/10.0 for i in lst] for lst in rearing_count_pre]
rearing_dur_stim = [[i/10.0 for i in lst] for lst in rearing_count_stim]
rearing_dur_post = [[i/10.0 for i in lst] for lst in rearing_count_post]

# filter trials without numbers (empty sublists)
rearing_dur_pre = list(filter(None, rearing_dur_pre))
rearing_dur_stim = list(filter(None, rearing_dur_stim))
rearing_dur_post = list(filter(None, rearing_dur_post))

# calculate mean bout duration values for each trial (sublist)
rearing_dur_pre_avgs = [mean(lst) for lst in rearing_dur_pre]
rearing_dur_stim_avgs = [mean(lst) for lst in rearing_dur_stim]
rearing_dur_post_avgs = [mean(lst) for lst in rearing_dur_post]

# put mean bout duration values to columns of data frame
df['Rearing_dur_pre'] = pd.Series(rearing_dur_pre_avgs)
df['Rearing_dur_stim'] = pd.Series(rearing_dur_stim_avgs)
df['Rearing_dur_post'] = pd.Series(rearing_dur_post_avgs)

# calculate % time spent rearing
percent_time_rearing_pre = sum([sum(lst) for lst in rearing_dur_pre])/n/10*100
percent_time_rearing_stim = sum([sum(lst) for lst in rearing_dur_stim])/n/10*100
percent_time_rearing_post = sum([sum(lst) for lst in rearing_dur_post])/n/10*100

# put % time rearing to columns of data frame
df['Percent_time_rearing_pre'] = pd.Series(percent_time_rearing_pre)
df['Percent_time_rearing_stim'] = pd.Series(percent_time_rearing_stim)
df['Percent_time_rearing_post'] = pd.Series(percent_time_rearing_post)

# calculate frequency for rearing bouts (per 10 s)
rearing_freq_pre = sum([len(lst) for lst in rearing_dur_pre])/n
rearing_freq_stim = sum([len(lst) for lst in rearing_dur_stim])/n
rearing_freq_post = sum([len(lst) for lst in rearing_dur_post])/n

# put frequency to columns of data frame
df['Rearing_freq_pre'] = pd.Series(rearing_freq_pre)
df['Rearing_freq_stim'] = pd.Series(rearing_freq_stim)
df['Rearing_freq_post'] = pd.Series(rearing_freq_post)

###### CALCULATE MOTIONLESS ######

df_motionless = (df_ear_left <= thres) & (df_ear_right <= thres) & (df_center <= thres) \
& (df_lat_left <= thres) & (df_lat_right <= thres) & (df_tailbase <= thres) & (df_rearing == 0)

# separate the motionless data per trial
motionless_arr = np.array(df_motionless).reshape(n,600)

# sample data for pre, stim, and post periods
motionless_pre = motionless_arr[:,150:250]
motionless_stim = motionless_arr[:,250:350]
motionless_post = motionless_arr[:,350:450]

# count the number of motionless bouts and the number of time points in each bout

count_motionless_pre = lambda motionless_pre: [sum(1 for _ in group) for key, group in \
itertools.groupby(motionless_pre) if key]
count_motionless_stim = lambda motionless_stim: [sum(1 for _ in group) for key, group in \
itertools.groupby(motionless_stim) if key]
count_motionless_post = lambda motionless_post: [sum(1 for _ in group) for key, group in \
itertools.groupby(motionless_post) if key]

motionless_count_pre = [count_motionless_pre(motionless_pre[i]) for i in range(n)]
motionless_count_stim = [count_motionless_stim(motionless_stim[i]) for i in range(n)]
motionless_count_post = [count_motionless_post(motionless_post[i]) for i in range(n)]

# convert the number of time points in each bout to duration
motionless_dur_pre = [[i/10.0 for i in lst] for lst in motionless_count_pre]
motionless_dur_stim = [[i/10.0 for i in lst] for lst in motionless_count_stim]
motionless_dur_post = [[i/10.0 for i in lst] for lst in motionless_count_post]

# filter trials without numbers (empty sublists)
motionless_dur_pre = list(filter(None, motionless_dur_pre))
motionless_dur_stim = list(filter(None, motionless_dur_stim))
motionless_dur_post = list(filter(None, motionless_dur_post))

# calculate mean bout duration values for each trial (sublist)
motionless_dur_pre_avgs = [mean(lst) for lst in motionless_dur_pre]
motionless_dur_stim_avgs = [mean(lst) for lst in motionless_dur_stim]
motionless_dur_post_avgs = [mean(lst) for lst in motionless_dur_post]

# put mean bout duration values to columns of data frame
df['Motionless_dur_pre'] = pd.Series(motionless_dur_pre_avgs)
df['Motionless_dur_stim'] = pd.Series(motionless_dur_stim_avgs)
df['Motionless_dur_post'] = pd.Series(motionless_dur_post_avgs)

# calculate % time spent motionless
percent_time_motionless_pre = sum([sum(lst) for lst in motionless_dur_pre])/n/10*100
percent_time_motionless_stim = sum([sum(lst) for lst in motionless_dur_stim])/n/10*100
percent_time_motionless_post = sum([sum(lst) for lst in motionless_dur_post])/n/10*100

# put % time motionless to columns of data frame
df['Percent_time_motionless_pre'] = pd.Series(percent_time_motionless_pre)
df['Percent_time_motionless_stim'] = pd.Series(percent_time_motionless_stim)
df['Percent_time_motionless_post'] = pd.Series(percent_time_motionless_post)

# calculate frequency for motionless bouts (per 10 s)
motionless_freq_pre = sum([len(lst) for lst in motionless_dur_pre])/n
motionless_freq_stim = sum([len(lst) for lst in motionless_dur_stim])/n
motionless_freq_post = sum([len(lst) for lst in motionless_dur_post])/n

# put frequency to columns of data frame
df['Motionless_freq_pre'] = pd.Series(motionless_freq_pre)
df['Motionless_freq_stim'] = pd.Series(motionless_freq_stim)
df['Motionless_freq_post'] = pd.Series(motionless_freq_post)

###### RATIO OF MOUSE LENGTH VS WIDTH, MOUSE ANGLE, CENTER SPEED ######

# separate the ratio data per trial
ratio_arr = np.array(df_ratio).reshape(n,600)

# separate the angle data per trial
angle_arr = np.array(df_angle).reshape(n,600)

# separate the body center speed data per trial
center_arr = np.array(df_center/pixel_per_mm).reshape(n,600)

###### CALCULATE BEHAVIOR SWITCHES ######

# convert arr to df and int type, to remove 0s and replace 1s to letters, then combine df

from pandas import DataFrame

df_locomotion_l = DataFrame(locomotion_arr).astype(int).replace(0,np.nan).replace(1,'l')
df_fine_movement_l = DataFrame(fine_movement_arr).astype(int).replace(0,np.nan).replace(1,'f')
df_rearing_l = DataFrame(rearing_arr).astype(int).replace(0,np.nan).replace(1,'r')
df_motionless_l = DataFrame(motionless_arr).astype(int).replace(0,np.nan).replace(1,'m')

df_behaviors_l = df_locomotion_l.fillna(df_fine_movement_l).fillna(df_rearing_l).fillna(df_motionless_l)

# convert df back to arr for counting behavior switches
behaviors_l_arr = np.array(df_behaviors_l)

# sample data for pre, stim, and post periods
behavior_pre = behaviors_l_arr[:,150:250]
behavior_stim = behaviors_l_arr[:,250:350]
behavior_post = behaviors_l_arr[:,350:450]

# make tuple for each neighbour pairs of data for each trial
behavior_pre_tup = [list(zip(lst[::1],lst[1::1])) for lst in behavior_pre]
behavior_stim_tup = [list(zip(lst[::1],lst[1::1])) for lst in behavior_stim]
behavior_post_tup = [list(zip(lst[::1],lst[1::1])) for lst in behavior_post]

# count occurences of each possible behavior switch (type of pair), e.g. ('l','m') (locomotion to motionless switch)
import collections
switch_occurrences_pre = [collections.Counter(lst) for lst in behavior_pre_tup]
switch_occurrences_stim = [collections.Counter(lst) for lst in behavior_stim_tup]
switch_occurrences_post = [collections.Counter(lst) for lst in behavior_post_tup]

########## FOR PRE TRIALS ##########
###### CALCULATE LOCOMOTION ######

# set dist_moved values of body center above the threshold and exclude rearing to calculate locomotion data
df_locomotion_bsln = (df['Center_dist_moved'][1:stop_bsln] > thres) & (df['Rearing'][1:stop_bsln] == 0)

# count the number of locomotion bouts and the number of time points in each bout
locomotion_count_bsln = [sum(1 for _ in group) for key, group in itertools.groupby(df_locomotion_bsln) if key]

# convert the number of time points in each bout to duration, and convert list to Series for concatenation later
locomotion_dur_bsln = [i/10.0 for i in locomotion_count_bsln]
locomotion_dur_bsln = pd.Series(locomotion_dur_bsln)

# calculate % time spent locomotion
percent_time_locomotion_bsln = sum(locomotion_count_bsln)/(stop_bsln-1)*100

# put % time locomotion to columns of data frame
df['Percent_time_locomotion_bsln'] = pd.Series(percent_time_locomotion_bsln)

# calculate frequency for locomotion bouts (per 10 s, i.e., 100 frames, to be consistent with stim trials)
locomotion_freq_bsln = len(locomotion_dur_bsln)/((stop_bsln-1)/100)

# put frequency to columns of data frame
df['Locomotion_freq_bsln'] = pd.Series(locomotion_freq_bsln)

###### CALCULATE FINE MOVEMENT ######

df_fine_movement_bsln = ((df['Ear_left_dist_moved'][1:stop_bsln] > thres) | (df['Ear_right_dist_moved'][1:stop_bsln] \
> thres) | (df['Tailbase_dist_moved'][1:stop_bsln] > thres) | (df['Lat_left_dist_moved'][1:stop_bsln] > thres) \
| (df['Lat_right_dist_moved'][1:stop_bsln] > thres)) & (df['Center_dist_moved'][1:stop_bsln] <= thres) \
& (df['Rearing'][1:stop_bsln] == 0)

# count the number of fine_movement bouts and the number of time points in each bout
fine_movement_count_bsln = [sum(1 for _ in group) for key, group in itertools.groupby(df_fine_movement_bsln) if key]

# convert the number of time points in each bout to duration
fine_movement_dur_bsln = [i/10.0 for i in fine_movement_count_bsln]
fine_movement_dur_bsln = pd.Series(fine_movement_dur_bsln)

# calculate % time spent fine_movement
percent_time_fine_movement_bsln = sum(fine_movement_count_bsln)/(stop_bsln-1)*100

# put % time fine_movement to columns of data frame
df['Percent_time_fine_movement_bsln'] = pd.Series(percent_time_fine_movement_bsln)

# calculate frequency for fine_movement bouts (per 10 s, i.e., 100 frames, to be consistent with stim trials)
fine_movement_freq_bsln = len(fine_movement_dur_bsln)/((stop_bsln-1)/100)

# put frequency to columns of data frame
df['Fine_movement_freq_bsln'] = pd.Series(fine_movement_freq_bsln)

###### CALCULATE REARING ######

df_rearing_bsln = df['Rearing'][1:stop_bsln] == 1

# count the number of rearing bouts and the number of time points in each bout
rearing_count_bsln = [sum(1 for _ in group) for key, group in itertools.groupby(df_rearing_bsln) if key]

# convert the number of time points in each bout to duration
rearing_dur_bsln = [i/10.0 for i in rearing_count_bsln]
rearing_dur_bsln = pd.Series(rearing_dur_bsln)

# calculate % time spent rearing
percent_time_rearing_bsln = sum(rearing_count_bsln)/(stop_bsln-1)*100

# put % time rearing to columns of data frame
df['Percent_time_rearing_bsln'] = pd.Series(percent_time_rearing_bsln)

# calculate frequency for rearing bouts (per 10 s, i.e., 100 frames, to be consistent with stim trials)
rearing_freq_bsln = len(rearing_dur_bsln)/((stop_bsln-1)/100)

# put frequency to columns of data frame
df['Rearing_freq_bsln'] = pd.Series(rearing_freq_bsln)

###### CALCULATE MOTIONLESS ######

df_motionless_bsln = (df['Ear_left_dist_moved'][1:stop_bsln] <= thres) & (df['Ear_right_dist_moved'][1:stop_bsln] \
<= thres) & (df['Center_dist_moved'][1:stop_bsln] <= thres) & (df['Lat_left_dist_moved'][1:stop_bsln] <= thres) \
& (df['Lat_right_dist_moved'][1:stop_bsln] <= thres) & (df['Tailbase_dist_moved'][1:stop_bsln] <= thres) \
& (df['Rearing'][1:stop_bsln] == 0)

# count the number of motionless bouts and the number of time points in each bout
motionless_count_bsln = [sum(1 for _ in group) for key, group in itertools.groupby(df_motionless_bsln) if key]

# convert the number of time points in each bout to duration
motionless_dur_bsln = [i/10.0 for i in motionless_count_bsln]
motionless_dur_bsln = pd.Series(motionless_dur_bsln)

# calculate % time spent motionless
percent_time_motionless_bsln = sum(motionless_count_bsln)/(stop_bsln-1)*100

# put % time rearing to columns of data frame
df['Percent_time_motionless_bsln'] = pd.Series(percent_time_motionless_bsln)

# calculate frequency for motionless bouts (per 10 s, i.e., 100 frames, to be consistent with stim trials)
motionless_freq_bsln = len(motionless_dur_bsln)/((stop_bsln-1)/100)

# put frequency to columns of data frame
df['Motionless_freq_bsln'] = pd.Series(motionless_freq_bsln)

###### RATIO OF MOUSE LENGTH VS WIDTH, MOUSE ANGLE, CENTER SPEED ######

# get ratio data pre trial
df_ratio_bsln = df['Ratio'][1:stop_bsln]

# get the angle data pre trial
df_angle_bsln = df['Mouse_angle'][1:stop_bsln]

# get the body center speed data pre trial
df_center_bsln = df['Center_dist_moved'][1:stop_bsln]/pixel_per_mm

###### CALCULATE BEHAVIOR SWITCHES ######

# convert df of booleans to int type, to remove 0s and replace 1s to letters, then combine df

df_locomotion_bsln_l = df_locomotion_bsln.astype(int).replace(0,np.nan).replace(1,'l')
df_fine_movement_bsln_l = df_fine_movement_bsln.astype(int).replace(0,np.nan).replace(1,'f')
df_rearing_bsln_l = df_rearing_bsln.astype(int).replace(0,np.nan).replace(1,'r')
df_motionless_bsln_l = df_motionless_bsln.astype(int).replace(0,np.nan).replace(1,'m')

df_behaviors_bsln_l = df_locomotion_bsln_l.fillna(df_fine_movement_bsln_l).fillna(df_rearing_bsln_l \
).fillna(df_motionless_bsln_l)

# make tuple for each neighbour pairs of data for pre trial (starting from 1 as no data for first cell)
behavior_bsln_tup = [list(zip(df_behaviors_bsln_l[1::1],df_behaviors_bsln_l[2::1]))]

# count occurences of each possible behavior switch (type of pair)
switch_occurrences_bsln = [collections.Counter(lst) for lst in behavior_bsln_tup]

########## put together all data into data frames and save data frames to current excel ##########

from openpyxl import load_workbook
book = load_workbook(path)
writer = pd.ExcelWriter(path, engine = 'openpyxl')
writer.book = book

# put each behavior array from trials into a data frame
df_locomotion = DataFrame(locomotion_arr).transpose()
df_fine_movement = DataFrame(fine_movement_arr).transpose()
df_rearing = DataFrame(rearing_arr).transpose()
df_motionless = DataFrame(motionless_arr).transpose()
# calculate row mean (across trials) for each behavior dataframe, i.e. mean behavior freq
df['Locomotion_mean'] = df_locomotion.mean(axis=1)
df['Fine_movement_mean'] = df_fine_movement.mean(axis=1)
df['Rearing_mean'] = df_rearing.mean(axis=1)
df['Motionless_mean'] = df_motionless.mean(axis=1)

# put ratio, angle, and body center speed arrays from trials into a data frame
df_ratio = DataFrame(ratio_arr).transpose()
df_angle = DataFrame(angle_arr).transpose()
df_center = DataFrame(center_arr).transpose()
# calculate row mean (across trials) for each ratio/angle/center speed dataframe
df['Ratio_mean'] = df_ratio.mean(axis=1)
df['Angle_mean'] = df_angle.mean(axis=1)
df['Center_mean'] = df_center.mean(axis=1)

# put behavior switch array from trials or pre trial into a data frame
switch_pre = DataFrame(switch_occurrences_pre)
switch_stim = DataFrame(switch_occurrences_stim)
switch_post = DataFrame(switch_occurrences_post)
switch_bsln = DataFrame(switch_occurrences_bsln)

# concatenate dataframes of all behaviors from trials or pre trial
group_name1 = ['Locomotion','Fine_movement','Rearing','Motionless']
df_behaviors = pd.concat([df_locomotion,df_fine_movement,df_rearing,df_motionless], \
axis=1, keys = group_name1).astype(int).replace(0,'-')
df_behaviors_bsln = pd.concat([df_locomotion_bsln,df_fine_movement_bsln,df_rearing_bsln,df_motionless_bsln], \
axis=1, keys = group_name1).astype(int).replace(0,'-')
# create a dataframe including all mean behavior freq
df_behaviors_mean = DataFrame(df, columns=['Locomotion_mean','Fine_movement_mean','Rearing_mean', \
'Motionless_mean']).dropna()
# average per 10 data points for each mean behavior freq
df_behaviors_mean_10 = df_behaviors_mean.groupby(np.arange(len(df_behaviors_mean))//10).mean()

# concatenate dataframes of ratio, angle, and body center speed from trials or pre trial
group_name2 = ['Ratio','Angle','Center_speed']
df_ratio_angle_center = pd.concat([df_ratio,df_angle,df_center], axis=1, keys = group_name2)
df_ratio_angle_center_bsln = pd.concat([df_ratio_bsln,df_angle_bsln,df_center_bsln], axis=1, \
keys = group_name2)
# create a dataframe including mean for each ratio/angle/center speed columns
df_ratio_angle_center_mean = DataFrame(df, columns=['Ratio_mean','Angle_mean','Center_mean']).dropna()
# average per 10 data points for each trial or pre trial
df_ratio_angle_center = df_ratio_angle_center.groupby(np.arange(len(df_ratio_angle_center))//10).mean()
df_ratio_angle_center_bsln = df_ratio_angle_center_bsln.groupby(np.arange(len(df_ratio_angle_center_bsln \
))//10).mean()
df_ratio_angle_center_mean = df_ratio_angle_center_mean.groupby(np.arange(len(df_ratio_angle_center_mean \
))//10).mean()

# concatenate dataframes of behavior switches from each period of trials and pre trial
df_switch = pd.concat([switch_pre,switch_stim,switch_post,switch_bsln], axis=0, keys = ['Switch_pre',\
'Switch_stim','Switch_post','Switch_bsln'])

# create a dataframe for dur of each type of behaviors for pre, stim and post periods from trials
df_dur = DataFrame(df, columns=['Locomotion_dur_pre','Locomotion_dur_stim','Locomotion_dur_post', \
'Fine_movement_dur_pre','Fine_movement_dur_stim','Fine_movement_dur_post', \
'Rearing_dur_pre','Rearing_dur_stim','Rearing_dur_post', \
'Motionless_dur_pre','Motionless_dur_stim','Motionless_dur_post'])

# concatenate dataframes of duration from pre trial
df_dur_bsln = pd.concat([locomotion_dur_bsln,fine_movement_dur_bsln,rearing_dur_bsln,motionless_dur_bsln], \
axis=1,keys = group_name1)

# create a dataframe including freq and percent_time of each type of behaviors for pre, stim and post periods
df_freq_percent_time = DataFrame(df, columns=['Locomotion_freq_pre','Locomotion_freq_stim','Locomotion_freq_post', \
'Percent_time_locomotion_pre','Percent_time_locomotion_stim','Percent_time_locomotion_post', \
'Fine_movement_freq_pre','Fine_movement_freq_stim','Fine_movement_freq_post', \
'Percent_time_fine_movement_pre','Percent_time_fine_movement_stim','Percent_time_fine_movement_post', \
'Rearing_freq_pre','Rearing_freq_stim','Rearing_freq_post', \
'Percent_time_rearing_pre','Percent_time_rearing_stim','Percent_time_rearing_post', \
'Motionless_freq_pre','Motionless_freq_stim','Motionless_freq_post', \
'Percent_time_motionless_pre','Percent_time_motionless_stim','Percent_time_motionless_post'])

# create a dataframe including freq and percent_time of each type of behaviors for pre trials
df_freq_percent_time_bsln = DataFrame(df, columns=['Locomotion_freq_bsln','Percent_time_locomotion_bsln',\
'Fine_movement_freq_bsln','Percent_time_fine_movement_bsln','Rearing_freq_bsln','Percent_time_rearing_bsln',\
'Motionless_freq_bsln','Percent_time_motionless_bsln'])

# save dataframes into excel
df_behaviors.to_excel(writer, sheet_name = 'Behaviors_trials')
df_behaviors_mean.to_excel(writer, sheet_name = 'Mean_behaviors_trials')
df_behaviors_mean_10.to_excel(writer, sheet_name = 'Mean_behaviors_trials_10')
df_behaviors_bsln.to_excel(writer, sheet_name = 'Behaviors_bsln')
df_ratio_angle_center.to_excel(writer, sheet_name = 'L_W_ratio_angle_Vcenter_trials')
df_ratio_angle_center_mean.to_excel(writer, sheet_name = 'Mean_ratio_angle_Vcenter')
df_ratio_angle_center_bsln.to_excel(writer, sheet_name = 'L_W_ratio_angle_Vcenter_bsln')
df_switch.to_excel(writer, sheet_name = 'Behavior_switch_all')
df_freq_percent_time.to_excel(writer, sheet_name = 'Freq_percent_time_trials', index=False)
df_freq_percent_time_bsln.to_excel(writer, sheet_name = 'Freq_percent_time_bsln', index=False)

# save some statistics to excel
df_dur.describe().to_excel(writer, sheet_name = 'Statistics_dur_trials')
df_dur_bsln.describe().to_excel(writer, sheet_name = 'Statistics_dur_bsln')

writer.save()
writer.close()
