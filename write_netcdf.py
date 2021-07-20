"""
Write Brazilian river discharge data in CSV format to a NetCDF file. 

Creates an "orthogonal" set of time series. This allows for efficient data storage, as each time series shares a single date/time variable. 
Each time series begins and ends on the same date. In the CSV files I created with the script convert_vazoes_2_csv.py, I chose to use 
the date range 1970-01-01 to 2019-12-31.

Written for Python 3.9.2

Created by Matthew Heberger, matthew.heberger@obspm.fr
Last updated: 2021-07-13

MIT License

"""

import numpy as np
import datetime
import os
from netCDF4 import Dataset
import pandas as pd

# Read information about our gages (lat, lon) from the gageinfo file
# into a lookup table
datafile = 'cabra-gageinfo.csv'
lookup = pd.read_csv(datafile, index_col=0)

#Folder where you want your output to go
csv_folder = 'csv/'

files = os.listdir(csv_folder)
n = len(files)
i = 0  # counter to keep track of which file we are currently processing (just to give some status output to monitor the script) 



#Create file
ncfile = Dataset('Brazil_Discharge.nc', mode='w', format='NETCDF4')

#Add some basic metadata
ncfile.title = "Brazil River Discharge"
ncfile.subtitle = 'Measured, 1970 - 2019'
ncfile.institution = "Paris Observatory, LERMA"
ncfile.source = "Brazil Hidroweb, https://www.snirh.gov.br/hidroweb/"
ncfile.summary = ('Created by Matthew Heberger')
ncfile.license = ('This work is licensed under the MIT License, https://opensource.org/licenses/MIT')
ncfile.featureType = 'timeSeries' 
ncfile.Conventions = 'H.2.1.' #http://cfconventions.org/cf-conventions/v1.6.0/cf-conventions.html#_orthogonal_multidimensional_array_representation_of_time_series
ncfile.history = '{0} creation of Brazil discharge NetCDF file.'.format(datetime.datetime.now().strftime("%Y-%m-%d"))

#Set up the variables in the file

#STATION and time are the only "Dimensions" - everything else is a variable
ncfile.createDimension('station', n)
ncfile.createDimension('date', None) #None means there is no limit. In reality, we have from 1970 to 2019, or 18,628 days

#STATION - we assign the Gage ID, e.g. "10100000" to each time series
stationid = ncfile.createVariable(varname='station', datatype='S8', dimensions=('station', )) 
stationid._Encoding = 'ascii'
stationid.cf_role = 'profile_id'
stationid.long_name = 'Station identifier'

#DATE - this variable is shared for every variable (that's what makes this "orthogonal" - and allows us to store the data efficiently
# However, it does not have to be like this. Each variable can have it's own associated time variable.
# For more information, see: http://cfconventions.org/cf-conventions/v1.6.0/cf-conventions.html#representations-features

date = ncfile.createVariable(varname='date', datatype=np.float32, dimensions=('date',)) #i4 is a 32-bit integer
date.units = 'Days since 1970-01-01'


# LAT and LON - not strictly needed - the station ID is the "primary key" to look up information about each of the gages,
# like its name, river, basin, region, etc. and the lat, lng could be readily looked up using the station ID.
# However, it seems like it is good practice, almost expected, to include lat, lng in any NetCDF file.

lon = ncfile.createVariable('lon', np.float64, ('station',))
lon.standard_name = 'longitude'

lat = ncfile.createVariable('lat', np.float64, ('station',))
lat.standard_name = 'latitude'


#DISCHARGE
discharge = ncfile.createVariable(varname='discharge', datatype=np.float32, dimensions=('station', 'date'), fill_value=-999)
discharge.long_name = 'River Discharge'
discharge.units = 'm³/s'


#iterate over all of the files in the folder
os.chdir(csv_folder)

for fname in files:
    
    #The files I created earlier are named after the Gage ID number, e.g. 10100000.csv
    #To get the Gage ID as a string, just lop the ".csv" off of the end of the file name.
    gage = fname[:-4]
    stationid[i] = gage
    intGage = int(gage)
    lat[i] = lookup.loc[intGage].latitude
    lon[i] = lookup.loc[intGage].longitude
    
    print("Saving %s of %s, gage: %s " % (i, n, gage))
    
    df = pd.read_csv(fname, index_col=0, parse_dates=['Date'])
    
    #I *think* we only have to add the date variable once; it is the same every time. 
    if i == 1:
        #Get the dates from the CSV, and convert them to integers, and insert them in .nc file
        listDates = df.index.tolist()
        day1 = datetime.date(1970, 1, 1)
        delta = [d.date() - day1 for d in listDates]
        intDays = [d.days for d in delta]
        date[:] = intDays

    #Write the discharge data to the file
    discharge[i,:] = df.Q
    
    i = i + 1
    
    #Is there a way to save or commit without closing?? 

ncfile.close()
