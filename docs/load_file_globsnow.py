#%%
from math import comb
from matplotlib.pyplot import grid, pcolor
import netCDF4 as nc
import glob
import os
import pandas as pd
import xarray as xr
import numpy as np
import matplotlib.pylab as plt
import rioxarray as rio
from pyproj import Proj, Transformer
import cartopy.crs as ccrs

path = r'D:\\Users\\Reuben\\Internship\\Snow\\snow\\docs\\GlobSnowMarchDailyData'
files = glob.glob(path + "/*.nc")


#These functions are needed so that the numpy mapping (map(lambda x: ....)) works
#Its basically like looping but it vectorises the input to the output.
def get_filename(x):
    filename = os.path.basename(x)
    return filename

#change the file basename from 19790301.nc to 19790301 (just the date)
def get_date(x):
    date = x.split(".")[0]
    return date

def list_to_strings(x):
    return x[0]

def get_filenames(path):
    
    #This finds all the .nc extension files within a folder with all the data
    #recrusive=True means that all subdirectories are also considered.
    files = glob.glob(path + "/*.nc")
    
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
#function to go from lat, lon to x, y

def lat_lon_to_x_y(lat, lon):
    transformer = Transformer.from_crs("epsg:4326", "epsg:3408")
    x, y = transformer.transform(lat, lon)
    return x, y

#define the regions named with a lat and lon slice. This is from the Patterns and trends of Northern Hemisphere
#snow mass from 1980 to 2018 paper 
def eurasia_above_40_lat_xy(ds):
    y1, x1 = lat_lon_to_x_y(40, -20)
    y2, x2 = lat_lon_to_x_y(80, 180)
    return ds.sel(x=slice(x1,x2), y=slice(y1,y2))

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
    return ds.sel(lat=slice(40,90),lon=slice(-10,170))

def north_america_above_40_lat(ds):
    return ds.sel(lat=slice(40,80),lon=slice(-170,-40))

df = get_dates(path, files)

def get_snow_depths(data):
    #flag values are below 0 (0 is a flag value too). So all snow values are > 0.
    return data.swe.where(data.swe>0)

def get_area(snow_depths):

    #calculates the number of grid cells that are snow_covered over the whole time series
    #Getting 0 --> nan and 1 --> non_nan value (therefore snow-covered) and then counts all the ones.
    number_of_grid_cells = np.count_nonzero(~np.isnan(snow_depths))
    grid_area = 1.11e7
    
    return number_of_grid_cells * grid_area

def get_mean(snow_depths):
    return snow_depths.mean(skipna=True)

def get_snow_mass(mean, total_area):

    #swe is in mm so need to convert to m
    mean_snow_depth_in_metres = mean/1000
    volume_of_snow = mean_snow_depth_in_metres * total_area

    #using static density of 240 kgm^-3. Whilst this is not 100% accurate, for long-term climate analysis it is sufficient.
    #This is defined in Product User uide for this SWE product.
    mass_of_snow = volume_of_snow * 240
    mass_in_tonnes = mass_of_snow / 1000
    mass_in_Gt = mass_in_tonnes * 1e-9

    return mass_in_Gt

def get_number_of_grid_cells(snow_depths):

    #calculates the number of grid cells that are snow_covered over the whole time series
    #Getting 0 --> nan and 1 --> non_nan value (therefore snow-covered) and then counts all the ones.
    number_of_grid_cells = np.count_nonzero(~np.isnan(snow_depths))
    
    return number_of_grid_cells


def get_snow_depths(data):
    #flag values are below 0 (0 is a flag value too). So all snow values are > 0.
    #swe > 5 because depths less than 0.05m cannot be relilably retrieved because of the
    #brightness temperature difference between two frequencies falls below 2K detection temperature
    return data.swe.where(data.swe>5)


dataframe = get_dates(path, files)
filenames_test = Data_from_range('1979-1-1', '1980-12-31', dataframe, path, files)
ds = xr.open_mfdataset(files, combine='nested', concat_dim='time', parallel=True, chunks={'time':10})
ds['time'] = dataframe['dates'].values
ds.swe.transpose('x', 'y', 'time')

def area_weighted_swe_values(swe_values):


    #area dataArray

    swe_values.resample(time='M').mean()
    #print(swe_values)


    mean_swe = swe_values.mean()

    area = 6.25e8 * get_number_of_grid_cells(swe_values)
    grid_cell_size = 25000
    total_area = grid_cell_size**2 * 721 * 721
    print("{:e}".format(total_area))
    print(get_number_of_grid_cells(swe_values))
    
    snow_masses_gt = 625e3 * get_number_of_grid_cells(swe_values) * mean_swe/1e10

    return snow_masses_gt, mean_swe, area


panda_dataframe = pd.DataFrame(columns={'year', 'snow mass', 'mean swe', 'total area'})
march_yearly_snow_masses = {}

for year in range(1979,2019):

    data = ds.sel(time=slice(str(year) + '-01-01', str(year) + '-12-31'))

    snow_depths = get_snow_depths(data)

    snow_mass, mean_swe, total_area = area_weighted_swe_values(snow_depths)


    march_yearly_snow_masses.setdefault('year', []).append(str(year))
    march_yearly_snow_masses.setdefault('snow mass', []).append(snow_mass.values)
    march_yearly_snow_masses.setdefault('mean swe', []).append(mean_swe.values.astype(int))
    march_yearly_snow_masses.setdefault('total area', []).append(total_area)

swe_data_pandas = pd.DataFrame(march_yearly_snow_masses)
swe_data_pandas['5 year moving average'] = swe_data_pandas['snow mass'].rolling(5).mean()
average_swe = swe_data_pandas['snow mass'].mean()
print(swe_data_pandas)
print(average_swe)

fig = plt.figure(figsize=(15,10), edgecolor="Blue")
ax = fig.add_subplot(111)

snow_masses = swe_data_pandas.plot(x='year', y='snow mass', kind='scatter', ax = ax)
five_year_moving_average = swe_data_pandas.plot(x='year', y='5 year moving average', ax= ax)

plt.xticks(rotation=90)

#print(ds)
#print(ds.crs)
#print(ds.crs.attrs)
#print(ds.swe)
#print(ds.swe.attrs)
#print(ds.crs.attrs['spatial_ref'])

map_projection = ccrs.PlateCarree()
#fig = plt.figure(figsize=(15,10))

#ax = fig.add_subplot(111, transform=map_projection)
#ax = plt.axes(projection=ccrs.PlateCarree())
#ax.add_feature(ccrs.feature.OCEAN, zorder=0)
#ax.coastlines()
#ax.set_global()
#im = ds.swe[0].plot.pcolormesh(ax=ax, transform=ccrs.PlateCarree())

#ax.set_title('Glob Snow v3 March Monthly SWE 0.25 grid')
# %%
