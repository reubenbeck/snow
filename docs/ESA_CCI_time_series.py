#%%
from cmath import nan
import netCDF4 as nc
import glob
import os
import pandas as pd
import xarray as xr
import numpy as np
import matplotlib.pylab as plt
from tqdm.auto import tqdm, trange
from scipy import interpolate

#path to where all the netcdf4 files are
path = r'D:\\Users\\Reuben\\Internship\\ESA_CCI_v1_March_Daily_Data'
files = glob.glob(path + "/*.nc")



#These functions are needed so that the numpy mapping (map(lambda x: ....)) works
#Its basically like looping but it vectorises the input to the output.
def get_filename(x):
    """
    Retrieves the filename. For example, '
    From:
    'D:\\\\Users\\\\Reuben\\\\Internship\\\\ESA_CCI_v1_March_Daily_Data\\20180331-ESACCI-L3C_SNOW-SWE-SSMIS-DMSP-fv1.0.nc'
    
    this function gets:
    '20180331-ESACCI-L3C_SNOW-SWE-SSMIS-DMSP-fv1.0.nc'

    Input
    ---------
    x: Passing parameter for numpy mapping. In this case x
        will be each file of the snow data.
    Output
    ----------
    filename: filename for a given file
    
    Notes
    -----------

    """
    filename = os.path.basename(x)
    return filename

def get_date(x):
    """
    Retrieves the filename. For example, '
    From:
    '20180331-ESACCI-L3C_SNOW-SWE-SSMIS-DMSP-fv1.0.nc'
    
    this function gets:
    '20180331'

    Input
    ---------
    x: Passing parameter for numpy mapping. In this case x
        will the basename for each file. 
    Output
    ----------
    Data: date given in YYYYMMDD
    
    Notes
    -----------

    """
    date = x.split("-")[0]
    return date

def list_to_strings(x):
    """
    Creates a list of strings. Each string is a directory 
    to the file that needs to be opened.
    
    Goes from:

    [['file-1'],['file-2'], ... ['file-n']]
    
    to:

    ['file-1', 'file-2', ... 'file-n']

    Input
    ---------
    x: Passing parameter for numpy mapping. In this case x
        is each file directory for the snow data.
    Output
    ----------
    filename: String of the filename.
    
    Notes
    -----------

    """
    return x[0]

def get_filenames(path):
    """
    Create a panda's dataframe which has one column: filenames.
    These are all the paths for the snow data on your local machine.
    
    Input
    ---------
    path: Directory to the folder/folders where all the data is located.

    Output
    ----------
    Panda Dataframe: Dataframe containing a list of all the files.
    
    Notes
    -----------

    """
    
    #This finds all the .nc extension files within a folder with all the data
    #recrusive=True means that all subdirectories are also considered.
    files = glob.glob(path + "/**/*.nc", recursive=True)
    
    #creates dictionary
    filenames_dict = {'filenames': files}
    
    #creates panda dataframe from dictionary
    df_filename = pd.DataFrame(filenames_dict)
    
    return df_filename

def get_dates(path):
    """
    Returns a pandas dataframe identical in length to the filenames dataframe.
    It has one column: dates. This corresponds to the dates in filename.
    
    Example:
    
                                                                                                               dates
    0   D:\\Users\\Reuben\\Internship\\ESA_CCI_v1_March_Daily_Data\\20180331-ESACCI-L3C_SNOW-SWE-SSMIS-DMSP-fv1.0.nc
    ...
            dates
    0   1979-03-01
    ...

    Input
    ---------
    path: Directory to all the snow data on local machine. 
    
    Output
    ----------
    Pandas Dataframe: Dataframe containing all the dates
    
    Notes
    -----------

    """
    files = glob.glob(path + "/**/*.nc", recursive=True)
    
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

def Data_from_range(start_date, end_date, path):
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

    dates_dataframe = get_dates(path)
    
    #Only data from between start and end date are shown
    mask = (dates_dataframe['dates'] >= start_date) & (dates_dataframe['dates'] <= end_date)

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

print(Data_from_range('1979-3-1', '1979-3-31', path))

#define the regions named with a lat and lon slice. This is from the Patterns and trends of Northern Hemisphere
#snow mass from 1980 to 2018 paper 

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

def northern_hemisphere(ds):
    min_lon = -170
    min_lat = 40
    max_lon = 170
    max_lat = 90

    mask_lon = (ds.lon >= min_lon) & (ds.lon <= max_lon)
    mask_lat = (ds.lat >= min_lat) & (ds.lat <= max_lat)

    return ds.where(mask_lon & mask_lat, drop=True)

#all the data as sliced by the GlobSnow Product.
#From paper, Patterns and Trends of Northern Hemisphere Snow Mass from 1980 to 2018

def ease_grid_globsnow(ds):
    min_lon = -180
    min_lat = 35
    max_lon = 180
    max_lat = 85

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

    #v1 of the data
    #multiplied by 1.28 for north_america
    #mutliplied by 1.1 for eurasia
    #multiplied by 1.34 for north hemisphere (ease_grid_north_hemisphere)

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
    """
    Returns the snow values from the data between 5 and 500 mm.
    
    Input
    -----------
    data: NetCDF4 files of all the snow data
    
    Output
    -----------
    Snow_data: Snow values between the values of 5 and 500mm
    
    Notes
    -----------
    """

    #flag values are below 0 (0 is a flag value too). So all snow values are > 0.

    #swe > 5 because depths less than 0.05m cannot be relilably retrieved because of the
    #brightness temperature difference between two frequencies falls below 2K detection temperature

    mask_swe_1 = data>5
    mask_swe_2 = data<500
    return data.where(mask_swe_1 & mask_swe_2)

def get_total_area(data):
    """
    Calcualtes the total area of a gridded data set given the coordinates: lat and lon.
    A meshgrid is created from the function, area_grid, which works out the area for each pixel.
    
    Input
    -----------
    data: NetCDF4 files of all the data
    
    Output
    -----------
    total_area: Sum of all the pixel areas.
    
    Notes
    -----------

    """

    data_swe = data.swe

    area = area_grid(data_swe['lat'], data_swe['lon'])

    total_area = np.sum(area)

    return total_area.values.item()

def get_daily_snow_masses_gt(x):
    """
    For each datarray of the SWE product, the snow mass is returned.
    This is done through the following steps:
        - creates a snow mask that gets values beteen 5mm and 500mm
        - for each pixel in the data, area_grid calculates the area of that pixel
        - Masking is used to get the areas of pixels which snow data is present
        - calculates the snow mass by multiply each pixel area by the SWE value
        - sum it all up (total mass) --> divide by 1e12 to get Gigatonnes
    
    Input
    -----------
    x: Passing parameter for numpy mapping. In this case x
        is each Datarray containing the swe data. This is a 2D grid (x = lat, y = lon)
    
    Output
    -----------
    Snow Mass: If data doesn't exist (due to SMMR bi-daily Data) wil return NaN. Otherwise
        it returns the Snow Mass in Gigatonnes.
    
    Notes
    -----------

    """
    #x is the data array. This is used so that all the days can be iterated over through numpy mapping

    #gets values betweeen 5mm and 500mm
    snow_mask = get_snow_depths(x)

    da_area = area_grid(x['lat'], x['lon'])

    #~np.isnan gets all the non-NaN values which in this case is all the snow data
    truth_false_array = ~np.isnan(snow_mask)

    #Multiply previous array by 1 to convert from False --> 0 and True --> 1
    zeroes_ones = np.multiply(truth_false_array, 1)

    #Array which gives the area for each pixel where the snow data is present
    area_values_where_snow_is_present = da_area * zeroes_ones

    #calcualtes snow masses
    snow_masses_array = area_values_where_snow_is_present * snow_mask

    #Sums all pixels (snow mass) to get total mass and then convert to Gigatonnes.
    snow_masses_gt = np.sum(snow_masses_array)/1e12

    #If no data is present return nan
    #Else return the snow mass in Gigatonnes
    if snow_masses_gt == 0:
        return nan
    else:
        return snow_masses_gt.values.item()


#the total area for the ease-grid glob snow (721 x 721) with 0.25 degree resolution
#721 x721 corresponds to
#lat: 35 degree north to 85 degree
#lon: 180 degree west to 180 degree west 
#total_area = 3.249006e+14

#using the area_grid forumla and slicing the data as the same for the globsnow data
#the total area that was given was 1.075677e14

def get_snow_masses(data):
    """
    Interpolates for the missing snow values. This is key for the data from the SMMR sensor that is
    deactivated every other day. Monthly Snow masses are returned.

    Input
    -----------
    data: Data Array for the snow. For monthly snow masses to be returned this array needs to only contain one month of data.
        in this case it will be March
    
    Output
    -----------
    monthly_snow_mass: March Monthly Snow Mass, given in Gigatonnes.
    
    Notes
    -----------
    """
    #accounts for the missing bi-daily data from the smmr satellite
    swe_daily_values_smmr = data.swe.resample(time='D').asfreq()

    list_of_swe_datarrays = []
    
    #this gets the number of days in a given month and then creates
    #a list of all the Snow water Equivalent Datarrays for each day.
    for i in range(swe_daily_values_smmr.shape[0]):
        list_of_swe_datarrays.append(swe_daily_values_smmr[i, :, :])


    #uses numpy mapping to apply function: get_daily_snow_masses_gt() to every element of the smmr data arrays

    snow_masses = np.array(list(map(lambda x: get_daily_snow_masses_gt(x), list_of_swe_datarrays)))

    #any snow masses that are missing, mainly due to the bi_daily data from 1979-1988 will be interpolated
    interp_masses_daily = pd.Series(snow_masses).interpolate(method='linear')

    monthly_snow_mass = interp_masses_daily.mean()

    return monthly_snow_mass

def create_plot(dict_of_snow_masses):
    """
    Creates a time_series plot of the March Yearly snow masses and includes a 5 year rolling average.


    Input
    -----------
    dict_of_snow_masses: Dictionary of snow masses. Dictionary is of the form:
        year: snow mass
    
    Output
    -----------
    plot: Time Series for March snow mass
    
    Notes
    -----------
    """
    swe_data_pandas = pd.DataFrame(dict_of_snow_masses)

    #creates 5 year rolling average
    swe_data_pandas['5 year moving average'] = swe_data_pandas['snow mass'].rolling(5).mean()
    average_swe = swe_data_pandas['snow mass'].mean()
    print(swe_data_pandas)
    print(average_swe)

    fig = plt.figure(figsize=(15,10), edgecolor="Blue")
    ax = fig.add_subplot(111)

    #plots monthly march snow masses and 5 year rolling average
    snow_masses = swe_data_pandas.plot(x='year', y='snow mass', kind='scatter', ax = ax)
    five_year_moving_average = swe_data_pandas.plot(x='year', y='5 year moving average', ax= ax)

    #so the years can be seen clearly
    plt.xticks(rotation=90)
    #plt.ylim([500, 1500])

    return 
        

def snow_time_series_annually(start_year, end_year, region):
    """
    Creates a time_series plot of the March Yearly snow masses and includes a 5 year rolling average.
    Data can be sliced to give a particular region for anaylsis. Includes linear interpolation for any missing data present.

    Input
    -----------
    start_year: Starting year for the data to be opened from. (any year between 1979 and 2018)

    End_year: End year for the data to be opened to. (any year between 1979 and 2018.)

    region: selecting region of interest:
        - eurasia, north_america, northern_hemisphere or ease_grid_globsnow
        - type None if want all the data to be anaylsed
    Output
    -----------
    plot: Time Series for March snow mass
    
    Notes
    -----------
    
    """

    #creates dictionary for snow masses to be appended to
    march_yearly_snow_masses = {}

    for year in range(start_year, end_year + 1):


        #gets a list of all the filenames
        filenames = Data_from_range(str(year) + '-1-1', str(year) + '-12-12',path)
        print(filenames)

        #opens each file and creates a data array using xarray
        #preproces applies a function to each file before it is saved to the array:
            #in this case the preprocess functions slice the array to consider a region of the northen hemisphere
        data = xr.open_mfdataset(filenames,preprocess=region,parallel=True, chunks={'time':7})
        march_yearly_snow_masses.setdefault('year', []).append(str(year))

        monthly_snow_masses = get_snow_masses(data)
        march_yearly_snow_masses.setdefault('snow mass', []).append(monthly_snow_masses)
        print(monthly_snow_masses)

        #csv_snow_masses = pd.DataFrame(march_yearly_snow_masses).to_csv('D:\\Users\\Reuben\\Internship\\Northern_hemisphere_snow_masses_gt.csv')
             
    create_plot(march_yearly_snow_masses)
    
    return


# %%
