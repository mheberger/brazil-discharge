""" 
# Script to download river discharge data from Brazil's Hidroweb, https://www.snirh.gov.br/hidroweb/

Their server requires for you to establish a session, and they write a cookie to your browser,
which you then need to send in the header of your request.

This script uses the Python library *requests* which takes care of sessions quite easily

This script expects a text file with a list of gages on each line, e.g.:

10100000
10200000
10500000
11400000

The requests themselves are really simple. You request a URL like
https://www.snirh.gov.br/hidroweb/rest/api/documento/convencionais?tipo=2&documentos=10100000
and also send the right cookies in a header, and the server returns a zip file with lots of data in it.
(Can include a rating curve, water quality data, all kinds of stuff in addition to flow.)

Next, you can manually extract the files. Archive or delete the files you don't want,
and keep the files labeled vazoes...these are the ones with flow data in them. 

Matthew Heberger, matthew.heberger@obspm.fr
Updated: 2021-07-12

MIT License

"""
import os
import requests
import time
import requests

print(os.getcwd())

# PARAMETERS
#Location of your list of gages
gagesfile = 'gagelist.txt'

#Where to save the files. These are going to be a bunch of .zip files
out_path =  'data/'

# I'm not sure whether this is necessary, but if you hit some servers with too many requests in too short a time, 
#they will block your IP address. One way around this is to add a little pause in between requests. 
delay = 2.5 #seconds

# BEGIN PROCESSING

# First, read in the list of gages or stations from the text file
gagelist = open(gagesfile, 'r')
gages = gagelist.read().splitlines()
gagelist.close()
n = len(gages)
i = 0

#Create a list to store the gages for which download failed, so we can easily try again later.
failed_gages = []

# Alternatively, you could just grab data from a few gages, in a Python List ()
#gages = ['14250000', '10100000']

#This creates the web session and let us download files
s = requests.session()
r = s.get('https://www.snirh.gov.br/hidroweb/serieshistoricas')
base_url = 'https://www.snirh.gov.br/hidroweb/rest/api/documento/convencionais?tipo=2&documentos='

for gage in gages:       
    url = base_url + gage
    i = i + 1
    print('Trying %s, gage %s of %s' % (gage, i, n))
    
    #For some reason, I distrust filenames that are also numbers, so I put a character f at the beginning.
    # I think this comes from many years of using ESRI software, and is probably nonsensical in 2021
    outfile = out_path + 'f' + gage + '.zip'   
    
    #Create a new 'request' as part of the existing 'session' 
    r = s.get(url, stream=True)
    
    #These next three lines save the zip file returned by the server
    with open(outfile, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=128):
            fd.write(chunk)
    
    #Write the status to stdout. (Might be nicer to save the status a text file...) 
    if r.status_code == requests.codes.ok:
        print(gage + '\tDownloaded')
    else:
        print(gage + "\t FAILED, Error Code " + str(r.status_code))
        time.sleep(delay) #Add a short pause after any failure... not sure if this is really necessary. 
        failed_gages.append(gage)
        
    #Add a short pause between requests. 
    time.sleep(delay) 
        
#Output the list of failed gages
f = open('failed.txt', 'w')
f.write('\n'.join(failed_gages))
f.close()

# It's done... you may wish to play a little beep here. This one worked for me. 
import sys
sys.stdout.write('\a')
