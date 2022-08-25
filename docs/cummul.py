#%%
import pandas as pd

northern_hemisphere_csv = pd.read_csv('D:\\Users\\Reuben\\Internship\\Northern_hemisphere_snow_masses_gt.csv')
#print(northern_hemisphere_csv)

start_year = 1993
end_year = 2017

#get data between 1994-2017
df = northern_hemisphere_csv[northern_hemisphere_csv['year'].between(start_year, end_year)]

print(df.loc[df['year'] == 1993]['snow mass'].values[0])

df['snow loss'] = df['snow mass'] - df.loc[df['year'] == 1993]['snow mass'].values[0]
df['cummul'] = df['snow loss'].cumsum()

cummul_1994_2017 = df[['year', 'cummul']] 
print(cummul_1994_2017)
pd.DataFrame(cummul_1994_2017).to_csv('D:\\Users\\Reuben\\Internship\\1994_2017_cummul_all_ice_snow.csv')
#print(df)


# %%
