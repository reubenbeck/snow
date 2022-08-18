#%%
from matplotlib.pyplot import grid, pcolor
import netCDF4 as nc
import glob
import os
import pandas as pd
import xarray as xr
import numpy as np
import matplotlib.pylab as plt

path = r'D:\\Users\\Reuben\\Internship\\ESA_CCI_v1_March_Daily_Data'
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

def earth_radius(lat):
    '''
    calculate radius of Earth assuming oblate spheroid
    defined by WGS84
    
    Input
    ---------
    lat: vector or latitudes in degrees  
    
    Output
    ----------
    r: vector of radius in meters
    
    Notes
    -----------
    WGS84: https://earth-info.nga.mil/GandG/publications/tr8350.2/tr8350.2-a/Chapter%203.pdf
    '''
    from numpy import deg2rad, sin, cos

    # define oblate spheroid from WGS84
    a = 6378137
    b = 6356752.3142
    e2 = 1 - (b**2/a**2)
    
    # convert from geodecic to geocentric
    # see equation 3-110 in WGS84
    lat = deg2rad(lat)
    lat_gc = np.arctan( (1-e2)*np.tan(lat) )

    # radius equation
    # see equation 3-107 in WGS84
    r = (
        (a * (1 - e2)**0.5) 
         / (1 - (e2 * np.cos(lat_gc)**2))**0.5 
        )

    return r

def area_grid(lat, lon):
    """
    Calculate the area of each grid cell
    Area is in square meters
    
    Input
    -----------
    lat: vector of latitude in degrees
    lon: vector of longitude in degrees
    
    Output
    -----------
    area: grid-cell area in square-meters with dimensions, [lat,lon]
    
    Notes
    -----------
    Based on the function in
    https://github.com/chadagreene/CDT/blob/master/cdt/cdtarea.m
    """
    from numpy import meshgrid, deg2rad, gradient, cos
    from xarray import DataArray

    xlon, ylat = meshgrid(lon, lat)
    R = earth_radius(ylat)

    dlat = deg2rad(gradient(ylat, axis=0))
    dlon = deg2rad(gradient(xlon, axis=1))

    dy = dlat * R
    dx = dlon * R * cos(deg2rad(ylat))

    area = dy * dx

    xda = DataArray(
        area,
        dims=["lat", "lon"],
        coords={"lat": lat, "lon": lon},
        attrs={
            "long_name": "area_per_pixel",
            "description": "area per pixel",
            "units": "m^2",
        },
    )
    return xda

#get all the dates needed
df = get_dates(path, files)

filenames = Data_from_range('1980-1-1', '2018-12-12', df, path, files)

data = xr.open_mfdataset(filenames)

swe_mask = data.swe>5
swe_mask2 = data.swe<500
data_needed = data.swe.where(swe_mask & swe_mask2)
#print(data_needed.values)

truth_false_array = ~np.isnan(data_needed)
#print(truth_for_swe_false_for_else.values)

zeroes_ones = np.multiply(truth_false_array, 1)
#print(zeroes_ones.values)

def get_area(ds):
    #area dataArray
    snow_values = ds.where(ds.swe>0)

    #apply the area_grid function to the data to calculate the area for each grid cell
    #takes into account of the curvature of the globe.
    da_area = area_grid(snow_values['lat'], snow_values['lon'])

    total_area = da_area.sum(['lat', 'lon'])

    return da_area, total_area

def get_number_of_grid_cells(snow_depths):

    #calculates the number of grid cells that are snow_covered over the whole time series
    #Getting 0 --> nan and 1 --> non_nan value (therefore snow-covered) and then counts all the ones.
    number_of_grid_cells = np.count_nonzero(~np.isnan(snow_depths))
    
    return number_of_grid_cells

number_of_grid_cells = get_number_of_grid_cells(data_needed)
print(number_of_grid_cells)
mean_swe = data_needed.mean().values
print(mean_swe)

snow_mass_try_again = 156.25e3 * number_of_grid_cells * mean_swe/1e10
print(snow_mass_try_again)


lat_lon_of_swe = zeroes_ones * get_area(data)[0]



snow_mass_gt_v1 = mean_swe/get_area(data)[1]
print(snow_mass_gt_v1)

swe_values = zeroes_ones * data_needed

snow_mass_kg = np.reciprocal(lat_lon_of_swe, where= lat_lon_of_swe != 0) * swe_values
#print(snow_mass_kg.values)
print(np.nansum(snow_mass_kg.values))


snow_mass_kg_v1 = (lat_lon_of_swe*swe_values)
snow_mass_gt = (np.nansum(np.reciprocal(lat_lon_of_swe, where= lat_lon_of_swe != 0)*swe_values))/1e12
print(snow_mass_gt)
# %%
