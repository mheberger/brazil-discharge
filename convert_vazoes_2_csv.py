"""
Script to process daily river discharge data from from Brazil's Hidroweb site, http://www.snirh.gov.br/hidroweb/
(in files like vazoes_T_10100000.txt) and export it to CSV.
One .csv file will be created for each individual gage, which can then be easily processed. 

The output is a complete, evenly spaced daily time series
(Missing flow observations are a date with a blank in the CSV,
which other programs will usually interpret as Null or NaN.) 

Works on data from multiple gages (or station) as long as the files 
are all in the same directory.

The data files are a little unusual:
 * semicolon delimited
 * Each column contains data for a different day of the month
 * Some files contain both provisional or "raw" data as well as corrected "final" data which would result in duplicates if we don't check carefully.
 * Some files also contain an apparent bug where months are listed more than once. However, there is a telltale. The month is always shown as dd/mm/yyyy, e.g.: 01/03/2021. Duplicate data will have a day that is not 01 ... like 31/03/2021. This is weird, and I don't really understand the reason for it, but in my testing, it *seems* OK to delete any row with a day that is not 01. 

Written for Python 3.9

Created by Matthew Heberger, matthew.heberger@obspm.fr
Last updated: 2021-07-12

MIT License

"""

import pandas as pd
import numpy as np
import datetime
import os

# PARAMETERS: 
# Folder containing the text files of discharge date 
data_folder = 'C:/Data/Discharge/Observed/Brazil/data/'

#Folder where you want your output to go
output_folder = 'C:/Data/Discharge/Observed/Brazil/csv/'

#Define your time period of interest. Here is how many stations I found had data by decade
#as of July 2021 (list of stations that are >90% complete, following CABra, https://doi.org/10.5194/hess-25-3105-2021

"""
1930    2
1940    2
1950    3
1960   41
1970  113
1980  151
1990  153
2000  153
2010  151
2020   78
"""

start_date = '1970-01-01' 
end_date = '2020-12-31' #I found there is about 5-month lag in posting the daily flows. 


# BEGIN PROCESSING

# Get a list of all the files in the folder.
files = os.listdir(data_folder)
num_files = len(files)
i = 0  # counter to keep track of which file we are currently processing (just to give some status output to monitor the script) 

# Iterate over all of the files in the folder
os.chdir(data_folder)
for fname in files:
    i = i + 1
    
    gage = fname[9:17]
    
    print('Processing file %s of %s: gage %s' % (i, num_files, gage))
    
    # Tell Pandas which columns we want to import.
    cols = [1, 2] + list(range(16,47))

    # Read CSV file into a Pandas DataFrame (nice format for tabular data with different data types in different columns) 
    df = pd.read_csv(fname, sep=';', skiprows=13, index_col=False, usecols=cols, parse_dates=['Data'], dayfirst=True, decimal=',')

    # Create better column names from the Portugese names in the data files
    #(Consistencia -> QACode, Data -> Month, Vazao01 -> 01, Vazao02 -> 02, etc.
    df.columns = ['QACode', 'Month'] + [str(i).zfill(2) for i in list(range(1,32))]
    
    # Sort the rows to assist with removing occasional duplicate rows.
    df.sort_values(['Month', 'QACode'],  ascending = (True, False), inplace=True)
    df.drop_duplicates(['Month'], keep='first', inplace=True)
    df.drop(labels=['QACode'], axis=1, inplace=True) #We no longer need this column
    
    #HACKY bug fix: Get rid of weird duplicate rows that appear in a few of the data files.
    #These buggy rows seem to always have the month labeled with a day other than 1.
    #The way to do this is to create a column with the day, then delete any rows where Day <> 1
    df['Day'] = df['Month'].dt.day
    indices2delete = df[df['Day'] != 1].index
    df.drop(indices2delete , inplace=True)
    df.drop(labels=['Day'], axis=1)
    
    # The "melt" function is a quick way to 'lengthen' or 'unpivot' the database table.
    # or create many new rows from the data in columns.
    c = df.melt(id_vars=['Month'], var_name='Day', value_name = 'Q')

    # Sort the table in ascending chronological order.
    c = c.sort_values(['Month', 'Day'])

    # Create a new date column from the Month + Day
    # Incorrect dates like April 31 or Feb 30 will return 'None', which we will delete below
    c['isodate'] = c['Month'].astype(str).str.slice(0, 7) + '-' + c['Day']
    c['Date'] = pd.to_datetime(c['isodate'], errors='coerce')
    c = c.sort_values(['Date'])
    
    # Delete rows where Date is not valid 
    indices2delete = c[c['Date'].isnull()].index
    c.drop(indices2delete , inplace=True)

    #Delete columns that are no longer necessary
    c = c.drop(labels=['Month', 'Day'], axis=1)

    # "Normalize" the time series, i.e. fill in gaps where there are missing dates
    # First, make the Date column the Index for the Pandas table. 
    c.index = c['Date']
    new_index = pd.date_range(start=start_date, end=end_date, freq='D')
    c.index = pd.DatetimeIndex(c.index)
    c = c.reindex(new_index, fill_value = None)
    
    #Now we have two columns with duplicate date information, so drop one of them.
    c.drop(['isodate', 'Date'], axis=1, inplace=True)
    c.index.name = 'Date'

    #Export the table as a (now nicely formatted) CSV file
    fname = output_folder + gage + '.csv'
    c.to_csv(fname)
