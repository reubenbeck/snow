#%%
import urllib.request
import requests 
import numpy as np

def bulk_download(version, start_year, end_year, start_month, end_month, path_name):
    """
    Downloads the ESA Snow CCI onto a local machine with the directory of where this python file is located.

    Input
    ---------
    version: Must be written as either v1.0 or v2.0. THis is to select the version of the data you want.

    start_year: Starting year from which the Snow data will be downloaded from. Must be between a year 1979 and 2018/2020 (v1.0/v2.0)

    end_year: Ending year from which the Snow data will be downloaded to. Must be between a year 1979 and 2018/2020 (v1.0/v2.0)

    start_month: Starting month from which the Snow data will be downloaded from. Must be a month between 1 and 12.

    end_month: Ending month from which the Snow data will be downloaded to. Must be a month between 1 and 12.

    path_name: String for the path of the folder which you would like the data to be downloaded to.

    Returns:
    ----------
    Downloads the daily ESA Snow CCI onto a local machine.
    
    Notes
    -----------
    Make sure that the index of all the files is open in a browser so that the files can be downloaded.
    """

    
    #to get a python array of years from 1979-2020
    years = np.arange(start_year ,end_year + 1)


    #to get python array of months from 01-12
    #the code below with rjust allows for the leading 0 to be allowed
    #so it is written as 01 not 1

    a = np.arange(start_month , end_month + 1)
    months =[]
    for num in a:
        months.append((str(num).rjust(2, '0')))

    b = np.arange(1,32)
    days = []

    for num in b:
        days.append((str(num).rjust(2, '0')))


    #make sure that the index of the files is open in browser so it can download
    #the if block is because from 1987-10-01 onwards the url changes from SSMR-NIMBUS to SSMI-DMSP
    #this is needed so that the right url is downloaded
    for year in years:
            for month in months:
                for day in days:
                    if year == 1987 and int(month) == 10:
                        url = 'https://dap.ceda.ac.uk/neodc/esacci/snow/data/swe/MERGED/' + str(version) + '/' + str(year)+'/'+ str(month) +'/' + str(year) + str(month) + str(day) +'-ESACCI-L3C_SNOW-SWE-SSMI-DMSP-fv2.0.nc'
                    elif year == 1987 and int(month) == 11:
                        url = 'https://dap.ceda.ac.uk/neodc/esacci/snow/data/swe/MERGED/' + str(version) + '/' + str(year)+'/'+ str(month) +'/' + str(year) + str(month) + str(day) +'-ESACCI-L3C_SNOW-SWE-SSMI-DMSP-fv2.0.nc'
                    elif year == 1987 and int(month) == 12:
                        url = 'https://dap.ceda.ac.uk/neodc/esacci/snow/data/swe/MERGED/' + str(version) + '/'  + str(year)+'/'+ str(month) +'/' + str(year) + str(month) + str(day) +'-ESACCI-L3C_SNOW-SWE-SSMI-DMSP-fv2.0.nc'
                    elif 1987 < year < 2009:
                        url = 'https://dap.ceda.ac.uk/neodc/esacci/snow/data/swe/MERGED/' + str(version) + '/' + str(year)+'/'+ str(month) +'/' + str(year) + str(month) + str(day) +'-ESACCI-L3C_SNOW-SWE-SSMI-DMSP-fv2.0.nc'
                    elif year > 2008:
                        url = 'https://dap.ceda.ac.uk/neodc/esacci/snow/data/swe/MERGED/' + str(version) + '/' + str(year)+'/'+ str(month) +'/' + str(year) + str(month) + str(day) +'-ESACCI-L3C_SNOW-SWE-SSMIS-DMSP-fv2.0.nc'
                    else:
                        url = 'https://dap.ceda.ac.uk/neodc/esacci/snow/data/swe/MERGED/' + str(version) + '/'+ str(year)+'/'+ str(month) +'/' + str(year) + str(month) + str(day) +'-ESACCI-L3C_SNOW-SWE-SMMR-NIMBUS7-fv2.0.nc'

                    file_path = str(path_name) + str(year) + str(month) + str(day) + '.nc'
                    r = requests.get(url, allow_redirects=True)
                    if r.status_code == 404:
                        continue

                    # Download the file from `url` and save it locally under `file_name`:
                    urllib.request.urlretrieve(url, file_path)

    return
    
                
    
            


# %%
