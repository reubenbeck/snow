#%%
from shutil import copyfile
import glob
import os
import pandas as pd
import numpy as np
import xarray as xr

path = r'D:/Users/Reuben/Internship/Data'
files = glob.glob(path + "/**/*.nc", recursive=True)

#This finds all the .nc extension files within a folder with all the data
#recrusive=True means that all subdirectories are also considered.
files = glob.glob(path + "/**/*.nc", recursive=True)

def get_filename(x):
    filename = os.path.basename(x)
    return filename

def get_date(x):
    date = x.split("-")[0]
    return date

def list_to_strings(x):
    return x[0]

def get_filenames(path):
    
    #This finds all the .nc extension files within a folder with all the data
    #recrusive=True means that all subdirectories are also considered.
    files = glob.glob(path + "/**/*.nc", recursive=True)
    
    #creates dictionary
    filenames_dict = {'filenames': files}
    
    #creates panda dataframe from dictionary
    df_filename = pd.DataFrame(filenames_dict)
    
    return df_filename

def get_dates(path):
    
    files = glob.glob(path + "/**/*.nc", recursive=True)
    filenames = list(map(lambda x: get_filename(x), files))
    dates = list(map(lambda x: get_date(x), filenames))

    dates_dict = {'dates': dates}


    df = pd.DataFrame(dates_dict)

    #format from Panda Dataframe to a DateTime dataframe so particular dates can 
    #now be selected. Format '%Y%m%d' translates to the format YYYYMMDD
    
    df['dates'] = pd.to_datetime(df['dates'], format='%Y%m%d')
    
    return df

def Data_from_month(particular_month, dataframe, path):
    
    mask = dataframe['dates'].dt.month==particular_month
    month_index = dataframe[mask].index.values
    filenames = get_filenames(path)
    files_with_given_month = filenames.iloc[month_index]
    
    files_list = files_with_given_month.values.tolist()
    files_string = list(map(lambda x: list_to_strings(x), files_list))
    
    return files_string




def copy_files(particular_month, path_data, path_download_to):
    """
    From a given month, e.g March, this data will be re-downloaded
    to another folder. Useful to analyse Snow Data just for a particular month.

    Input
    ---------
    particular_month: Integer for the month you would like to download. Jan = 1, Feb = 2 ect.

    path_data: This is the path_ for which all the Snow Data is stored. Make sure to include r in front of the string for the path.
        E.g: r'D:/Users/Reuben/Internship/Data'

    path_download_to: This path for the directory which you would like the data to be copied to. Make sure it is a String.

    Output
    ----------
    filename: filename for a given file
    
    Notes
    -----------

    """

    dataframe = get_dates(path_data)

    fileList = Data_from_month(particular_month, dataframe, path_data)

    for item in fileList:
        filename = os.path.basename(item)
        copyfile(item, os.path.join(path_download_to, filename))

    return

# %%
