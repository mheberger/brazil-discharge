"""
Creates a series of time series plots or *hydrographs* for the Brazil discharge data
and saves the plots to JPG files.
Each plot shows the hydrograph for a single gage.

"""
import os
import matplotlib.pyplot as plt
import matplotlib.ticker
import numpy as np
import pandas as pd
import datetime


#Make the figure window - just do this once and reuse to be efficient. 
#Make the figure window 
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13,4), gridspec_kw = {'width_ratios':[4, 1]})

#Get rid of some excess whitespace at the edges of the figure window
fig.tight_layout()

in_folder = 'C:/Data/Discharge/Observed/Brazil/csv/'
out_folder ='C:/Data/Discharge/Observed/Brazil/plots/'

files = os.listdir(in_folder)
n = len(files)
i = 0  # counter to keep track of which file we are currently processing (just to give some status output to monitor the script) 

#iterate over all of the files in the folder
os.chdir(in_folder)
for fname in files:
    i = i + 1
    #The files I created earlier are named after the Gage ID number, e.g. 10100000.csv
    #To get the Gage ID as a string, just lop the ".csv" off of the end of the file name.
    gage = fname[:-4]

    print("Plotting %s of %s, gage: %s " % (i, n, gage))
    
    df = pd.read_csv(fname, index_col=0, parse_dates=['Date'])
    
    # Filter the Pandas table (dataframe) to include only dates after 2000,
    # as that is our period of interest (Change to show data as far back as 1931 for some gages)
    df = df.loc['2000-01-01':'2019-12-31']
    
    #Create another column of data to plot, as I want to show the missing data very prominently.
    df['missing'] = df['Q'].interpolate(method='linear')
    
    #Now delete any non-interpolated 
    df.loc[pd.notna(df.Q), 'missing'] = np.nan
    
    #Make the time series plot
    ax1.plot(df.index, df.Q)
    ax1.plot(df.index, df.missing, linewidth=3, color='r')
    
    ax1.set_ylabel('Discharge, m³/s')
    ax1.set_ylim(bottom=0)
    ylims = ax1.get_ylim()
    ax1.yaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
    ax1.set_title("Station " + gage)
    
    #Make the bar chart of monthly average flows. 
    df['mo'] = df.index.month
    m = df.groupby('mo')['Q'].mean()
                         
    ax2.bar(m.index,m)
    ax2.set_xticks(m.index)
    #ax2.set_ylim(my_ylims) #I had the idea to make the two plots have the same y axis, but it wasn't nice looking
    ax2.set_title("Monthly Averages")
    ax2.yaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
     
    #Save the figure with the gage ID as the filename
    
    fname = out_folder + 'TS_' + gage + '.jpg'
    fig.savefig(fname, dpi=75)
    
    #Clear the axes to prepare for the next plots
    ax1.clear()
    ax2.clear()
