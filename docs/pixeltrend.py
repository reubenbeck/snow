#%%
import glob
import os
import pandas as pd
import numpy as np
import xarray as xr
import cartopy.crs as ccrs
import matplotlib.pyplot as plt

path = r'D:\\Users\\Reuben\\Internship\\ESA_CCI_v1_March_Daily_Data'
files = glob.glob(path + "/**/*.nc", recursive=True)

#read in and open up files using Xarray
data = xr.open_mfdataset(files)

#Do some data reducton by resampling the data into yearly data.
#This will just the mean for the March data since only the March Snow Data
#is read in.
march_annual_swe = data.groupby('time.year').mean()


lat = march_annual_swe.swe['lat'].values
lon = march_annual_swe.swe['lon'].values

#Compute the temporal trend in SWE at each pixel.

#Create a 3-dimensional numpy array from xarray, to be used for
#the x coordinate in the regression calculation.

#vals has the dimensions (TIME, LAT, LON)
vals = march_annual_swe['swe'].values
years = march_annual_swe.year.values

#Reshape to an array with as many rows as years and
#as many columns as there are pixels
vals2 = vals.reshape(len(years), -1)

#Do a first-degree polyfit
regressions = np.polyfit(years, vals2, 1)

#Get the coefficients back
trends = regressions[0,:].reshape(vals.shape[1], vals.shape[2])

#Coeffients * 10 to get the decal trend
decadal_trend = trends*10

#create xarray dataset and add coordinates to this dataset, lat and lon
keys = ['lat', 'lon']
array_of_coords = [lat, lon]
array_of_coords_array = np.array(array_of_coords)
lat_lon_coords = dict(zip(keys, array_of_coords_array.T))
pixel_trend_datarray = xr.DataArray(decadal_trend, coords=lat_lon_coords)
print(pixel_trend_datarray)

#plot onto globe
map_projection = ccrs.Orthographic(0, 90)
fig = plt.figure(figsize=(15,10))

ax = fig.add_subplot(111, projection=map_projection)
#ax.add_feature(cartopy.feature.OCEAN, zorder=0)
ax.coastlines()
ax.set_global()
xr.plot.pcolormesh(pixel_trend_datarray, 
                    x='lon', 
                    y='lat',
                    cmap = 'seismic_r',
                    transform=ccrs.PlateCarree(),
                    ax = ax,
                    cbar_kwargs={'label': " SWE trend (mm/decade)"}
                    )


ax.set_title("Distribution and decadal trend for mean March hemispheric snow", fontsize=40, fontstyle='italic')
#ax.text(s=date, x=-0, y=4500000, fontsize=30, ha='center')
#fig.savefig('D:\\Users\\Reuben\\Internship\\Monthly_Plots\\' + str(date)+'.jpg', bbox_inches='tight')
#ax.suptitle(date)
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.monospace'] = 'Ubuntu Mono'
#plt.show slows done the code quite a lot
plt.show()









# %%
