#%%
import chunk
from matplotlib.pyplot import grid, pcolor
import netCDF4 as nc
import glob
import os
import pandas as pd
import xarray as xr
import numpy as np

path = r'D:\\Users\\Reuben\\Internship\\March Monthly Data'
files = glob.glob(path + "/*.nc")


#These functions are needed so that the numpy mapping (map(lambda x: ....)) works
#Its basically like looping but it vectorises the input to the output.
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


#define the regions named with a lat and lon slice. This is from the Patterns and trends of Northern Hemisphere
#snow mass from 1980 to 2018 paper 

def region_europe(ds):
    return ds.sel(lat=slice(50,65), lon=slice(15,35))

def region_east_siberia(ds):
    return ds.sel(lat=slice(65,73),lon=slice(145,175))

def region_Siberia(ds):
    return ds.sel(lat=slice(55,70),lon=slice(65,115))

def region_prairie(ds):
    return ds.sel(lat=slice(40,50),lon=slice(-110,-95))

def region_hudson_bay_area(ds):
    return ds.sel(lat=slice(50,65),lon=slice(-100,-70))

def eurasia_above_40_lat(ds):
    return ds.sel(lat=slice(40,80),lon=slice(-20,180))

df = get_dates(path, files)

filenames = Data_from_range('1995-1-1','1995-12-12',df, path, files)

#preprocess allows the data to be sliced/manipulated upon opening the files (to reduce memory issues)
data_1979 = xr.open_mfdataset(filenames, preprocess=eurasia_above_40_lat, parallel=True, chunks={'time':7})


snow_values = data_1979.swe.where(data_1979.swe>0)
snow_values.plot.hist()

#calculates the number of grid cells that are snow_covered over the whole time series
#Getting 0 --> nan and 1 --> non_nan value (therefore snow-covered) and then counts all the ones.
number_of_grid_cells = np.count_nonzero(~np.isnan(snow_values))

#using spatial resolution in lon and lat at 0.1 degrees = 11.1km
grid_area = 1.11e7

total_area = number_of_grid_cells * grid_area


mean = snow_values.mean(skipna=True)
mean_in_metres = mean/1000
volume_of_snow = total_area * mean_in_metres

#using static density (from paper) of 240 kgm^-3. Whilst this is not 100% accurate, for long-term climate analysis it is sufficient.
mass_of_snow = volume_of_snow * 240

mass_in_tonnes = mass_of_snow / 1000
mass_in_Gt = mass_in_tonnes * 1e-9
print(mass_in_Gt.values)
# %%
