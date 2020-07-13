# -*- coding: utf-8 -*-
"""
Version 1.1
Created on 141006
@author: Jason
USAGE: This script detects and filters peaks from .csv files in a column-wise manner. This is currently set up to detect GCaMP3-based calcium transients in non-background subtracted images. If you background subtract, increase the alpha value accordingly.
NOTE: Go to Preferences > Run > and select "Execute in a new dedicated Python interpreter" to avoid issues with the GUI window.
"""

import math
import numpy as np
import scipy as sp
import scipy.stats
import csv
import Tkinter, tkFileDialog
from pandas import *
import glob

def mean_confidence_interval(data, confidence=0.05):
    a = 1.0*np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * sp.stats.t._ppf((1+confidence)/2., n-1)
    return m+h

def findEvents(array):
    silent = True
    difference = [] #creates an array to hold difference values
    raw_events = [] #creates an array to hold the significant value
    event_start = [] #creates an array to hold the event start times
    event_end = []
    baselines = []
    baseline_averages = [] #make an array to hold values to average for baseline
    return_averages = [] #make an array to hold values to average for return
    #FIND DIFFERENCES
    for i in range(0,((len(array))-(t+10))):
        difference.append(array[(i+t)] - array[i])
    #FIND DIFFERENCES ABOVE THRESHOLD
    for a in range(10,(len(difference)-1)):
        if difference[a] > alpha:
            raw_events.append(a)
            silent = False
    #CALL CELL SILENT IF NO EVENTS WERE FOUND
    if silent == True:
        del event_start
        event_start = 'silent'
        event_end = 'silent'
        baselines = 'silent'
    #IF EVENTS WERE FOUND, FIND THEIR BEGINNING
    if silent == False:
        event_start.append(raw_events[0]+t-2) #adds the first identified peak
        for b in range(1,len(raw_events)-(t*2)):
            if raw_events[b] - raw_events[b-1] > 1:
                event_start.append(raw_events[b]+t-2)
        #ASSUME THAT NO PEAKS HAVE AN END
        for a in range(0,len(event_start)):
            event_end.append('no end')
        #FIND THE ENDS
        for a in range(0,len(event_start)):
            x = event_start[a]
            while event_end[a] == 'no end':
                baseline_averages = []
                #if event_end[a] == 'no end':
                if len(array[:x]) <= baseline_length+1:
                    baseline_averages.append(array[:x])
                if len(array[:x]) > baseline_length+1:
                    for b in range(0,baseline_length):
                        baseline_averages.append(array[(x-b)])
                for c in range(t,len(array[x:])):
                    bval = np.mean(baseline_averages)+scipy.stats.sem(baseline_averages)
                    if event_end[a] == 'no end':
                        if array[event_start[a]+c] <= bval:
                            return_averages = []
                            if len(array[(x+c):]) < baseline_length+1:
                                return_averages.append(array[(x+c):])
                            if len(array[(x+c):]) > baseline_length+1:
                                for b in range(0,baseline_length+1):
                                    return_averages.append(array[(x+b+c)])
                            baselines.append(np.mean(baseline_averages))
                            event_end[a] = x+c
                if event_end[a] == 'no end':
                    del baseline_averages[:]
                    x = x+1
        for a in range(0,len(event_end)):            
            if event_end[a]+5 >= len(array):
                for value in range(0,(len(array)-event_end[a])):
                    minarray = []
                    minarray.append(event_end[a]+value)
                offset = np.argmin(minarray)
                event_end[a] = event_end[a]+offset
            if event_end[a]+5 < len(array):
                for value in range(0,5):
                    minarray = []
                    minarray.append(event_end[a]+value)
                offset = np.argmin(minarray)
                event_end[a] = event_end[a]+offset
    return event_start, event_end, baselines


def findMaxima(array, event_start, event_end):
    maxima = [] #create an array to hold the max values
    duration = [] #create an array to hold the duration
    peak_time = []
    for a in range (0,len(event_start)):
        maxima.append(max(array[(event_start[a]):event_end[a]]))
        peak_time.append(np.argmax(array[(event_start[a]):event_end[a]])+1)
        duration.append(event_end[a]-event_start[a])
    return maxima, peak_time, duration

def filterEvents(event_starts, event_ends, maxima, event_baselines, duration, peak_time):
    filtered_event_starts = [] #create arrays to hold filtered values
    filtered_event_ends = []
    filtered_maxima = []
    filtered_event_baselines = []
    filtered_duration = []
    filtered_peak_time = []
    if event_starts == 'silent':
        filtered_event_starts.append('silent')
        filtered_event_ends.append('silent')
        filtered_maxima.append('silent')
        filtered_event_baselines.append('silent')
        filtered_duration.append('silent')
        filtered_peak_time.append('silent')
    else:
        for a in range (0,len(event_starts)):
            if (maxima[a]-event_baselines[a]) > 0.05 and duration[a] < time:
                filtered_event_starts.append(event_starts[a])
                filtered_event_ends.append(event_ends[a])
                filtered_maxima.append(maxima[a])
                filtered_event_baselines.append(event_baselines[a])
                filtered_duration.append(duration[a])
                filtered_peak_time.append(peak_time[a])
    if len(filtered_event_starts) == 0:
            filtered_event_starts.append('silent')
            filtered_event_ends.append('silent')
            filtered_maxima.append('silent')
            filtered_event_baselines.append('silent')
            filtered_duration.append('silent')
            filtered_peak_time.append('silent')            
    return filtered_event_starts, filtered_event_ends, filtered_maxima, filtered_event_baselines, filtered_duration, filtered_peak_time

def separateComplex(dirname):
    csvFiles = glob.glob(dirname+"/*.csv")
    for x in range(0,(len(csvFiles))):
        dataset = read_csv(csvFiles[x])
        

#DETERMINE THE DIFFERENCE IN TIME POINTS YOU WOULD LIKE TO LOOK AT. 
t = 5 #units are determined by your sampling factor

#SPECIFY CRITICAL VALUE FOR EVENT DETECTION
alpha = 0.05 #scale this with the size of your events

#SPECIFY CUTOFF TIME FOR EVENTS
time = 90 #this is the maximum cutoff for an event

#SPECIFY NUMBER OF TIME POINTS TO AVERAGE FOR BASELINE
baseline_length = 5 #longer baseline can be more accurate, unless there is a lot of activity

#SPECIFY SAVE DIRECTORY
root = Tkinter.Tk()
root.withdraw()
dirname = tkFileDialog.askdirectory(parent=root,initialdir="/",title='Please select a directory to save the calcium analysis files')
if len(dirname) > 0:
    print "You chose %s" % dirname

#SPECIFY DATASET TO OPEN
root = Tkinter.Tk()
root.withdraw()
filename = tkFileDialog.askopenfile(parent=root,mode='rb',title='Choose a .csv file to open') #make sure this is a .csv file or adjust accordingly
dataset = read_csv(filename)
points = len(dataset.index)
cells = len(dataset.columns)

#NAME ARRAY TO BE ANALYZED
for a in range(0,cells):
    calcium = dataset[dataset.columns[a]]
    
#FIND EVENTS BASED ON CRITICAL VALUE
    event_starts, event_ends, event_baselines = findEvents(calcium)

#FIND GLOBAL MAXIMUM FOR EACH PEAK
    if event_starts != 'silent':
        maxima, peak_time, duration = findMaxima(calcium, event_starts, event_ends)
    else:
        maxima = 'silent'
        peak_time = 'silent'
        duration = 'silent'

#FILTER EVENTS
    filtered_event_starts, filtered_event_ends, filtered_maxima, filtered_event_baselines, filtered_duration, filtered_peak_time = filterEvents(event_starts, event_ends, maxima, event_baselines, duration, peak_time)

#ORGANIZE DATA INTO A TABLE AND EXPORT AS CSV
    header = []
    for i in range(1,(len(filtered_event_starts)+1)):
        header.append(i)
    header.insert(0,'Peak')
    if filtered_event_starts != 'silent':
        filtered_event_starts.insert(0, 'event start time (s)')
        filtered_event_ends.insert(0, 'event end time (s)')
        filtered_duration.insert(0, 'event duration (s)')
        filtered_event_baselines.insert(0, 'event baseline (dF/F')
        filtered_maxima.insert(0, 'event max dF/f')
        filtered_peak_time.insert(0, 'time of peak (s)')
    data = [header, filtered_event_starts, filtered_event_ends, filtered_duration, filtered_event_baselines, filtered_maxima, filtered_peak_time]
    if a < 9:
        x = 'cell 0'+str(a+1)
    if a > 8:
        x = 'cell '+str(a+1)
    csvfile = dirname+"/"+x+".csv"
    with open(csvfile, "w") as output:
        writer = csv.writer(output, lineterminator='\n')
        writer.writerows(data)

#CREATE ONE SPREADSHEET WITH SIMPLE AND COMPLEX PEAKS FOR EACH CELL
separateComplex(dirname)

print "Finished"