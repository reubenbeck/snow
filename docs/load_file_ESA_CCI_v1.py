#%%
from operator import index
from matplotlib.pyplot import grid, pcolor
import netCDF4 as nc
import glob
import os
import pandas as pd
import xarray as xr
import numpy as np
import matplotlib.pylab as plt
from tqdm.auto import tqdm, trange
from scipy import interpolate

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
    return ds.sel(lat=slice(-80,100),lon=slice(-15,180))

def north_america_above_40_lat(ds):
    return ds.sel(lat=slice(-80,100),lon=slice(-180,-15))

def eurasia(ds):
    min_lon = -10
    min_lat = 40
    max_lon = 170
    max_lat = 90

    mask_lon = (ds.lon >= min_lon) & (ds.lon <= max_lon)
    mask_lat = (ds.lat >= min_lat) & (ds.lat <= max_lat)

    return ds.where(mask_lon & mask_lat, drop=True)

def north_america(ds):
    min_lon = -170
    min_lat = 40
    max_lon = -10
    max_lat = 90

    mask_lon = (ds.lon >= min_lon) & (ds.lon <= max_lon)
    mask_lat = (ds.lat >= min_lat) & (ds.lat <= max_lat)

    return ds.where(mask_lon & mask_lat, drop=True)

def north_hemisphere(ds):
    min_lon = -180
    min_lat = 40
    max_lon = 180
    max_lat = 90

    mask_lon = (ds.lon >= min_lon) & (ds.lon <= max_lon)
    mask_lat = (ds.lat >= min_lat) & (ds.lat <= max_lat)

    return ds.where(mask_lon & mask_lat, drop=True)

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

def get_snow_depths(data):
    #flag values are below 0 (0 is a flag value too). So all snow values are > 0.
    #swe > 5 because depths less than 0.05m cannot be relilably retrieved because of the
    #brightness temperature difference between two frequencies falls below 2K detection temperature
    mask_swe_1 = data>0
    mask_swe_2 = data<1000
    return data.where(mask_swe_1 & mask_swe_2)

def get_area(snow_depths):

    #calculates the number of grid cells that are snow_covered over the whole time series
    #Getting 0 --> nan and 1 --> non_nan value (therefore snow-covered) and then counts all the ones.
    number_of_grid_cells = np.count_nonzero(~np.isnan(snow_depths))

    #0.25 degree spatial_resoltion - 25.75km as specified in Table 4.2 - https://climate.esa.int/media/documents/Snow_cci_D1.1_URD_v4.0.pdf
    lat_length = 25750
    lon_length = 25750
    grid_area = lat_length * lon_length
    
    return number_of_grid_cells * grid_area

def get_total_area(swe_values, swe_mask):
    #area dataArray

    #apply the area_grid function to the data to calculate the area for each grid cell
    #takes into account of the curvature of the globe.
    da_area = area_grid(swe_values['lat'], swe_values['lon'])

    truth_false_array = ~np.isnan(swe_mask)
    zeroes_ones = np.multiply(truth_false_array, 1)

    swe_values = da_area*zeroes_ones

    #sums it all up
    areas = swe_values.sum(['lat', 'lon'])

    total_area = np.sum(areas)

    return total_area.values

def get_mean(snow_depths, ds):
    #creating weights: the cosine of the latitude is proportional to the grid cell area.
    
    weights = np.cos(np.deg2rad(ds.lat))

    snow_weighted = snow_depths.weighted(weights)

    snow_weighted_mean = snow_weighted.mean(("lon", "lat"))

    mean = snow_weighted_mean.mean()

    return mean

def get_mean_without_weights(snow_depths):
    return snow_depths.mean()

def get_mean_using_area_weighted(ds):
    # area dataArray
    da_area = area_grid(ds['latitude'], ds['longitude'])

    # total area
    total_area = da_area.sum(['latitude','longitude'])

    # temperature weighted by grid-cell area
    temp_weighted = (ds['temperature']*da_area) / total_area

    # area-weighted mean temperature
    temp_weighted_mean = temp_weighted.sum(['latitude','longitude'])

    return temp_weighted_mean


def get_snow_mass(mean, total_area):

    #swe is in mm so need to convert to m
    mean_snow_depth_in_metres = mean/1000

    volume_of_snow = mean_snow_depth_in_metres * total_area
    #using static density of 240 kgm^-3. Whilst this is not 100% accurate, for long-term climate analysis it is sufficient.
    #This is defined in Product User uide for this SWE product.

    #Whilst 240 is quoted in the paper to use a static denisty, the value of 625 is used in the source code
    #fixed problems!
    mass_of_snow = volume_of_snow * 240
    mass_in_tonnes = mass_of_snow / 1000
    mass_in_Gt = mass_in_tonnes * 1e-9

    return mass_in_Gt

def get_number_of_grid_cells(snow_depths):

    #calculates the number of grid cells that are snow_covered over the whole time series
    #Getting 0 --> nan and 1 --> non_nan value (therefore snow-covered) and then counts all the ones.
    number_of_grid_cells = np.count_nonzero(~np.isnan(snow_depths))
    
    return number_of_grid_cells

def area_weighted_swe_values(swe_values, swe_mask):

    #area dataArray

    #apply the area_grid function to the data to calculate the area for each grid cell
    #takes into account of the curvature of the globe.
    da_area = area_grid(swe_values['lat'], swe_values['lon'])

    truth_false_array = ~np.isnan(swe_mask)
    zeroes_ones = np.multiply(truth_false_array, 1)

    swe_values = da_area*zeroes_ones

    #print(swe_values.shape, swe_values)
    #print(da_area.shape, da_area)
    snow_masses = swe_values * swe_mask
    
    
    snow_masses_gt = np.sum(snow_masses)/1e12

    return snow_masses_gt


#define all the dates (needed for Data_from_range)
df = get_dates(path, files)

#create dataframe and dictionary
panda_dataframe = pd.DataFrame(columns={'year', 'snow mass'})
march_yearly_snow_masses = {}


for year in range(1979, 1980):

    filenames = Data_from_range(str(year) + '-1-1', str(year) + '-12-12',df, path, files)

    data = xr.open_mfdataset(filenames,preprocess=eurasia,parallel=True, chunks={'time':7})

    #print(data)


    #calculates the total area of the swe data
    #total_area = get_total_area(data)


    #calulcates swe.mean()
    #mean_snow_depths = get_mean_without_weights(snow_depths)
    #print(mean_snow_depths.values)


    #snow_mass = get_snow_mass(mean_snow_depths, total_area)
    #print(snow_mass.values)
    #snow_mass = get_snow_mass_actual(snow_depths, mean_snow_depths, total_area)
    #print("{:e}".format(156.25e3 * get_number_of_grid_cells(snow_depths)))

    if 1979 <= year <= 1987:
        
        #for bi-daily data interpolate missing days using linear interpolation (as paper quoted)
        #swe_daily_values = data.swe.resample(time='D').asfreq()
        #swe_daily_values_snow = swe_daily_values.where(swe_daily_values>0)
        #print(swe_daily_values_snow.values)
        #swe_daily_values_snow = swe_daily_values_snow.interpolate_na(dim=('time'))
        #swe_daily_values_snow = swe_daily_values_snow.interpolate_na(dim=('lon'))
        #print(swe_daily_values_snow.values[2])
        

        #combine all daily date into monthly data
        swe_monthly_values = data.swe.resample(time='M').mean()

        #get 5 < swe (mm) < 500
        snow_depths_smmr = get_snow_depths(swe_monthly_values)


        total_area = get_total_area(swe_monthly_values, snow_depths_smmr)
        #("{:e}".format(total_area))

        mean_snow_depths = area_weighted_swe_values(swe_monthly_values, snow_depths_smmr)
        print(mean_snow_depths.values)
        
    else:
        #number_of_grid_cells = get_number_of_grid_cells(snow_depths)
        swe_monthly_values = data.swe.resample(time='M').mean()
        snow_depths = get_snow_depths(swe_monthly_values)
        total_area = get_total_area(swe_monthly_values, snow_depths)
        mean_snow_depths = area_weighted_swe_values(swe_monthly_values, snow_depths)
        print(mean_snow_depths.values)

    #paper method
    #snow_mass = 156.25e3 * number_of_grid_cells * mean_snow_depths.values/1e10
    snow_mass = total_area * mean_snow_depths/1e12
    #print(snow_mass.values)

    march_yearly_snow_masses.setdefault('year', []).append(str(year))

    march_yearly_snow_masses.setdefault('snow mass', []).append(snow_mass.values.astype(int))

swe_data_pandas = pd.DataFrame(march_yearly_snow_masses)
swe_data_pandas['5 year moving average'] = swe_data_pandas['snow mass'].rolling(5).mean()
average_swe = swe_data_pandas['snow mass'].mean()
print(average_swe)

fig = plt.figure(figsize=(15,10), edgecolor="Blue")
ax = fig.add_subplot(111)

snow_masses = swe_data_pandas.plot(x='year', y='snow mass', kind='scatter', ax = ax)
five_year_moving_average = swe_data_pandas.plot(x='year', y='5 year moving average', ax= ax)

plt.xticks(rotation=90)
#plt.ylim([500, 1500])
    
# %%

#%%
EU_area = 4.178e13
NA_area = 3.071e13
NH_area = 1.26377028e14

total = EU_area + NA_area
diff = NH_area - total
print(total, diff)

EU_mass = 1308
NA_mass = 882.3
NH_mass = 2786

total_mass = EU_mass + NA_mass
diff = NH_mass - total_mass

print(total_mass, diff)
# %%
