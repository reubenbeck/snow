# -*- coding: utf-8 -*-
#%%
#from line_profiler import LineProfiler
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
path = r"D:\\Users\\Reuben\\Internship\\Data_v1"

#This finds all the .nc extension files within a folder with all the data
#recrusive=True means that all subdirectories are also considered.
files = glob.glob(path + "\**\*.nc", recursive=True)

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
    files = glob.glob(path + "\**\*.nc", recursive=True)
    
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
    
    files = glob.glob(path + "\**\*.nc", recursive=True)
    filenames = list(map(lambda x: get_filename(x), files))
    dates = list(map(lambda x: get_date(x), filenames))

    dates_dict = {'dates': dates}


    df = pd.DataFrame(dates_dict)

    #format from Panda Dataframe to a DateTime dataframe so particular dates can 
    #now be selected. Format '%Y%m%d' translates to the format YYYYMMDD
    
    df['dates'] = pd.to_datetime(df['dates'], format='%Y%m%d')
    
    return df

def Data_from_month(particular_month, date_dataframe, files):
    """
    Given a paricular month, e.g March = 3, this function will return all the filenames
    from this given month

    Input
    ----------
    particular_month : Particular month from the Snow data that is wanted. 
        Need to be written as an integer. For March this means it will be 3.
        Write in the format 'YYYY-MM-DD' and is the day/month has a leading zero (e.g 01) -> write as 1.

    date_dataframe: This is the pandas dataframe that contains all the dates.
    
    files: Dataframe with all the files in.

    Returns
    -------
    Panda Dataframe with data only from the specific month that is specified.
    """
    
    mask = date_dataframe['dates'].dt.month==particular_month
    month_index = date_dataframe[mask].index.values
    
    files_with_given_month = files.iloc[month_index]
    
    files_list = files_with_given_month.values.tolist()
    files_string = list(map(lambda x: list_to_strings(x), files_list))
    
    return files_string

def Data_from_range(start_date, end_date, dataframe, path):
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
    
    #Only data from between start and end date are shown
    mask = (dataframe['dates'] > start_date) & (dataframe['dates'] <= end_date)
    df_date_indexes = dataframe[mask].index.values
    
    df_filename = get_filenames(path)
    
    files_needed = df_filename.iloc[df_date_indexes]
    
    files_needed_list = files_needed.values.tolist()

    files_needed_string_list = list(map(lambda x: list_to_strings(x), files_needed_list))
    
    return files_needed_string_list


def Data_from_range1(start_date, end_date, path):
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


def create_colourmap():
    """
    A function to create the colorbar for the SWE values. THe colorbar goes from blue to white
    for the values of the snow water equivalent going from 0 to 500mm respectively.

    The flag values are colored as the following:
        - No Data/ No Snow = Light Green
        - Mountains (where snow cannot be retrieved) = Yellow
        - Water = Light Blue
        - Glaciers/Ice = Grey

    Input
    ----------

    Returns
    -------
    A colorbar which contains the features that are mentioned above.

    """
    

    colours_flag_values = cm.get_cmap('Set2_r', 30)
    colors_snow = cm.get_cmap('Blues_r', 500)
    
    #for the linspace, this corresponds to the length of the colorbars and for the
    #colors_flag_values ([-30,-20,-10,0]) and colors_snow (0-500mm) to work then the ratio of the two 
    #color bars have to work. 31 is chosen instead of 30 for the flag colours because if they meet at 0
    #the colors is shown for snow but it should be where there is no snow.
    newcolours = np.vstack((colours_flag_values(np.linspace(0,1,31)), colors_snow(np.linspace(0,1,500))))
    newcmp = ListedColormap(newcolours, name='BinaryBlue_r')
    
    return newcmp


def plot_values_from_range(start_date, end_date, path):
    """
    A function to create a plot of SWE data given a start and end date. The colorbar goes from blue to white
    for the values of the snow water equivalent going from 0 to 500mm respectively.

    The flag values are colored as the following:
        - No Data/ No Snow = Light Green
        - Mountains (where snow cannot be retrieved) = Yellow
        - Water = Light Blue
        - Glaciers/Ice = Grey

    Input
    ----------

    start_date: String which contain the start date in the format 'YYYY-MM-DD'

    end_date: String which contain the start date in the format 'YYYY-MM-DD'

    path: directory for the folder of where the snow data is stored.

    Returns
    -------
    A pcolormesh of the SWE data.

    """
    
    files_from_range = Data_from_range1(start_date, end_date, path)
    
    
    #this try block is to stop the code plotting empty graphs where there was not data
    ds = xr.open_mfdataset(files_from_range)


    swe_northernhemisphere = ds.sel(lon=slice(-180,180),lat=slice(20,80))

    #resample the data in monthly intervals and calculates the mean for each month.
    swe_monthly_values = swe_northernhemisphere.swe.resample(time='m').mean()
    swe_colorbar = create_colourmap()

    for month_values in swe_monthly_values:

        #retrieves the date in the format "YYYY-MM-DD"
        date = month_values.coords['time'].dt.strftime('%Y-%m-%d').values

        #Creates map projection to show the globe from the northern hemisphere
        map_projection = ccrs.Orthographic(0, 90)
        fig = plt.figure(figsize=(15,10))
    
        ax = fig.add_subplot(111, projection=map_projection)
        #ax.add_feature(cartopy.feature.OCEAN, zorder=0)
        ax.coastlines()
        ax.set_global()
        im = month_values.plot.pcolormesh(x='lon', 
                                        y='lat',
                                        cmap = swe_colorbar,
                                        vmin=-30,
                                        vmax=500,
                                        transform=ccrs.PlateCarree(),
                                        ax = ax,
                                        cbar_kwargs={'label': "Snow Water Equivalent (mm)"}
                                        )
    
    
        ax.set_title("Northern Hemisphere Monthly SWE", fontsize=40, fontstyle='italic')
        ax.text(s=date, x=-0, y=4500000, fontsize=30, ha='center')
        fig.savefig('D:\\Users\\Reuben\\Internship\\Monthly_Plots\\' + str(date)+'.jpg', bbox_inches='tight')
        #ax.suptitle(date)
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
        plt.rcParams['font.monospace'] = 'Ubuntu Mono'
        #plt.show slows done the code quite a lot
        plt.show()
        
    return "All Done"

#plot_values_from_range('2014-3-1','2018-12-31',path)


# %%
