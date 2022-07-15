#%%
import datetime
import glob
import os
import pandas as pd
import numpy as np
import xarray as xr

path = r'D:/Users/Reuben/Internship/Data'
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

def get_dates(path, files):
    
    #loops through all the files and gets their filenames - uses numpy mapping
    filenames = list(map(lambda x: get_filename(x), files))

    #loops through all the filenames and retrieves their dates
    dates = list(map(lambda x: get_date(x), filenames))
    dates_dict = {'dates': dates}

    df = pd.DataFrame(dates_dict)

    #format from Panda Dataframe to a DateTime dataframe so particular dates can 
    #now be selected. Format '%Y%m%d' translates to the format YYYYMMDD
    
    df['dates'] = pd.to_datetime(df['dates'], format='%Y%m%d')
    
    return df

def Data_from_range(start_date, end_date, dataframe, path, files):
    """
    From selected start and end date, the Panda Datetime
    Dataframe will only include the data between these dates.

    Parameters
    ----------
    start_date : String
        Write in the format 'YYYY-MM-DD' and is the day/month has a leading zero (e.g 01) -> write as 1.
    end_date : String
        Write in the format 'YYYY-MM-DD' and is the day/month has a leading zero (e.g 01) -> write as 1.
    dataframe: Panda Dataframe of all the dates
        

    Returns
    -------
    Panda Dataframe with data from between the two dates.

    """
    
    #Only data from between start and end date are shown
    mask = (dataframe['dates'] > start_date) & (dataframe['dates'] <= end_date)
    #gets the values for the sliced data
    df_date_indexes = dataframe[mask].index.values
    
    #retrieves all the filesnames
    df_filename = get_filenames(path)
    
    #gets only the files wanted from the parameters: start_date, end_date
    files_needed = df_filename.iloc[df_date_indexes]
    
    #From the files wanted, gets the values and then creates a list from their values
    files_needed_list = files_needed.values.tolist()

    #String format is needed to pass through the function mfdataset (to read all the files)
    files_needed_string_list = list(map(lambda x: list_to_strings(x), files_needed_list))
    
    return files_needed_string_list

df = get_dates(path, files)

Data_from_range('1979-1-1', '1979-2-28', df, path, files)

#this is needed to create a list with a leading zero: 1 -> 01
a = np.arange(1,13)
months =[]
for num in a:
    months.append((str(num).rjust(2, '0')))

def last_day_of_month(any_day):
    # The day 28 exists in every month. 4 days later, it's always next month
    next_month = any_day.replace(day=28) + datetime.timedelta(days=4)
    # subtracting the number of the current day brings us back one month
    return next_month - datetime.timedelta(days=next_month.day)

def datetime_to_dates(x):
    return str(x.date())


end_dates = []
for year in range(1979, 2021):
    for month in range(1,13):
        end_dates.append(last_day_of_month(datetime.date(year, month,1)).strftime('%Y-%m-%d'))


monthly_data = []
for year in range(1979,2021):
    for month, end_date in zip(months, end_dates):
        print(str(year) + '-' + str(month) +'-1', end_date)
        monthly_data.append(Data_from_range(str(year) + '-' + str(month) +'-1', end_date, df, path, files))

for data in monthly_data:
    print(data)
    dataframe = xr.open_mfdataset(data)
    swe_northernhemisphere = dataframe.sel(lon=slice(-180,180),lat=slice(20,80))
    swe_monthly_value = swe_northernhemisphere.swe.resample(time='m').mean()
    swe_monthly_value.to_netcdf()
        
# %%
