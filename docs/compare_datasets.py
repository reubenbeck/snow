#%%
from re import S
import cartopy
import cartopy.crs as ccrs
import glob
import os
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib import cm
from matplotlib.colors import ListedColormap
import xarray as xr
import numpy as np

#change this to folder where the data is stored on local/global machine
path_globsnow = r'D:\\Users\\Reuben\\Internship\\GlobSnow_daily_swe'
path_esacci = r"D:\\Users\\Reuben\\Internship\\Data_v1"

def get_filename(x):
    filename = os.path.basename(x)
    return filename

def get_date_globsnow(x):
    #globsnow needs . to get date
    date = x.split(".")[0]
    return date

def get_date_esaci(x):
    #esacci needs hyphen to get date
    date = x.split("_")[0]
    return date

def list_to_strings(x):
    return x[0]

def get_filenames(path):
    #This finds all the .nc extension files within a folder with all the data
    #recrusive=True means that all subdirectories are also considered.
    files = glob.glob(path + "\**\*.nc", recursive=True)
    
    #creates dictionary
    filenames_dict = {'filenames': files}
    
    #creates panda dataframe from dictionary
    df_filename = pd.DataFrame(filenames_dict)
    
    return df_filename

def get_dates_globsnow(path):
    
    files = glob.glob(path + "\**\*.nc", recursive=True)
    filenames = list(map(lambda x: get_filename(x), files))
    dates = list(map(lambda x: get_date_globsnow(x), filenames))

    dates_dict = {'dates': dates}


    df = pd.DataFrame(dates_dict)

    #format from Panda Dataframe to a DateTime dataframe so particular dates can 
    #now be selected. Format '%Y%m%d' translates to the format YYYYMMDD
    
    df['dates'] = pd.to_datetime(df['dates'], format='%Y%m%d')
    
    return df

def get_dates_esacci(path):
    
    files = glob.glob(path + "\**\*.nc", recursive=True)
    filenames = list(map(lambda x: get_filename(x), files))
    dates = list(map(lambda x: get_dates_esacci(x), filenames))

    dates_dict = {'dates': dates}


    df = pd.DataFrame(dates_dict)

    #format from Panda Dataframe to a DateTime dataframe so particular dates can 
    #now be selected. Format '%Y%m%d' translates to the format YYYYMMDD
    
    df['dates'] = pd.to_datetime(df['dates'], format='%Y%m%d')
    
    return df

def Data_from_range_globsnow(start_date, end_date, path):
    """
    From selected start and end date, the Panda Datetime
    Dataframe will only include the data between these dates.

    Input
    ----------
    start_date : String
        Write in the format 'YYYY-MM-DD' and is the day/month has a leading zero (e.g 01) -> write as 1.

    end_date : String
        Write in the format 'YYYY-MM-DD' and is the day/month has a leading zero (e.g 01) -> write as 1.

    dataframe: Panda Dataframe of all the dates
        

    Returns
    -------
    Panda Dataframe with data only between the two dates given.

    """

    dates_dataframe = get_dates_globsnow(path)
    
    #Only data from between start and end date are shown
    mask = (dates_dataframe['dates'] > start_date) & (dates_dataframe['dates'] <= end_date)

    #gets the values for the sliced data
    df_date_indexes = dates_dataframe[mask].index.values
    
    #retrieves all the filenames
    df_filename = get_filenames(path)
    
    #gets only the files wanted from the parameters: start_date, end_date
    files_needed = df_filename.iloc[df_date_indexes]
    
    #From the files wanted, gets the values and then creates a list from their values
    files_needed_list = files_needed.values.tolist()

    #String format is needed to pass through the function mfdataset (to read all the files)
    files_needed_string_list = list(map(lambda x: list_to_strings(x), files_needed_list))
    
    return files_needed_string_list

def Data_from_range_esacci(start_date, end_date, path):
    """
    From selected start and end date, the Panda Datetime
    Dataframe will only include the data between these dates.

    Input
    ----------
    start_date : String
        Write in the format 'YYYY-MM-DD' and is the day/month has a leading zero (e.g 01) -> write as 1.

    end_date : String
        Write in the format 'YYYY-MM-DD' and is the day/month has a leading zero (e.g 01) -> write as 1.

    dataframe: Panda Dataframe of all the dates
        

    Returns
    -------
    Panda Dataframe with data only between the two dates given.

    """

    dates_dataframe = get_dates_esacci(path)
    
    #Only data from between start and end date are shown
    mask = (dates_dataframe['dates'] > start_date) & (dates_dataframe['dates'] <= end_date)

    #gets the values for the sliced data
    df_date_indexes = dates_dataframe[mask].index.values
    
    #retrieves all the filenames
    df_filename = get_filenames(path)
    
    #gets only the files wanted from the parameters: start_date, end_date
    files_needed = df_filename.iloc[df_date_indexes]
    
    #From the files wanted, gets the values and then creates a list from their values
    files_needed_list = files_needed.values.tolist()

    #String format is needed to pass through the function mfdataset (to read all the files)
    files_needed_string_list = list(map(lambda x: list_to_strings(x), files_needed_list))
    
    return files_needed_string_list


def compare_datasets(start_year, end_year, start_month, end_month, path_globsnow, path_esacci):
    monthly_swe = {}
    for year in range(start_year, end_year + 1):
        for month in range(start_month, end_month + 1):

            filenames_globsnow = Data_from_range_globsnow(str(year) + '-' + str(month) + '-1', str(year) + '-' + str(month) + '-31', path_globsnow)
            print(filenames_globsnow)
            filesnames_esacci = Data_from_range_esacci(str(year) + '-' + str(month) + '-1', str(year) + '-' + str(month) + '-31', path_esacci)

            try:
                data_globsnow = xr.open_mfdataset(filenames_globsnow, combine='nested', concat_dim='time', parallel=True, chunks={'time':10})
                data_globsnow['time'] = data_globsnow['dates'].values
                data_globsnow.swe.transpose('x', 'y', 'time')
            except OSError:
                monthly_swe.setdefault('year-month', []).append(str(year)+ '-' + str(month))
                monthly_swe.setdefault('GlobSnow SWE', []).append(0)
                continue
            
            try:
                data_esacci = xr.open_mfdataset(filesnames_esacci)
            except OSError:
                monthly_swe.setdefault('year-month', []).append(str(year)+ '-' + str(month))
                monthly_swe.setdefault('EsaCCI SWE', []).append(0)
            
            #globsnow is already given in monthly swe
            monthly_swe_value_globsnow = data_globsnow.mean().values
            print(monthly_swe_value_globsnow)

            monthly_swe_value_esacci = data_esacci.groupby('time.month').mean().values
            print(monthly_swe_value_esacci)

            monthly_swe.setdefault('year-month', []).append(str(year)+ '-' + str(month))
            monthly_swe.setdefault('GlobSnow SWE', []).append(monthly_swe_value_globsnow)
            monthly_swe.setdefault('year-month', []).append(str(year)+ '-' + str(month))
            monthly_swe.setdefault('EsaCCI SWE', []).append(monthly_swe_value_esacci)
    
    return







# %%
