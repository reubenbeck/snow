#%%
from shutil import copyfile
import glob
import os
import pandas as pd
import numpy as np
import xarray as xr

path = r'D:/Users/Reuben/Internship/Data'
files = glob.glob(path + "/**/*.nc", recursive=True)

path = r'D:/Users/Reuben/Internship/Data'


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

def Data_from_month(particular_month, dataframe, files, path):
    
    mask = dataframe['dates'].dt.month==particular_month
    month_index = dataframe[mask].index.values
    filenames = get_filenames(path)
    files_with_given_month = filenames.iloc[month_index]
    
    files_list = files_with_given_month.values.tolist()
    files_string = list(map(lambda x: list_to_strings(x), files_list))
    
    return files_string

dataframe = get_dates(path)

fileList = Data_from_month(3, dataframe, files, path)

for item in fileList:
    filename = os.path.basename(item)
    copyfile(item, os.path.join("D:\\Users\\Reuben\\Internship\\March Monthly Data", filename))


# %%
