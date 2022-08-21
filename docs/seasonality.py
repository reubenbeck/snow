#%%
from turtle import width
import plotly
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import seaborn as sns

df = pd.read_csv('D:\\Users\\Reuben\\Internship\\MonthlySnowMasses.csv')

df['March_rolling'] = df['March'].rolling(5).mean()
fig = go.Figure([go.Scatter(x=df['March-year-month'], y=df['March'],mode='markers'), go.Scatter(x=df['March-year-month'], y=df['March_rolling'])])
fig.show()

seasonality = df[['year-month', 'snow mass']].copy()
months = list(reversed([str(i) for i in list(range(1,13))])) + ['12']
months_test = list(np.arange(1,13))
year_months = list(seasonality['year-month'])

years = np.arange(1979,2019)

snow_masses = seasonality['snow mass'].values
#print(snow_masses)
snow_masses_yearly = [snow_masses[i:i+12] for i in range(0,len(snow_masses),12)]
#list_snow = list(seasonality[seasonality['year-month']==i]['snow mass']for i in year_months)

pal = list(sns.color_palette(palette='viridis', n_colors=len(years)).as_hex())

fig = go.Figure()
for snow_masses,year,colour in zip(snow_masses_yearly, years, pal):
    fig.add_trace(go.Scatterpolar(r = snow_masses, theta=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'June', 'July', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], fill= 'toself',
                                  name=str(year), marker = dict(color = colour)))

fig.update_layout(polar = dict(radialaxis = dict(visible = True, range=[0, 3700]),
                               angularaxis = dict(rotation=90, direction='clockwise')),
                  showlegend=True, width=650, height=650,
                  font = dict(size=14))

pal = list(sns.color_palette(palette='viridis', n_colors=len(years)).as_hex())


df = pd.DataFrame(dict(
    floating_and_grounded_ice_values = [166,111,129,155,329,40,0,266],
    floating_and_grounded_ice = ['Greenland','Antarctic','Ice Shelf Thinning','Ice Shelf Calving','Artic sea ice', 'Antarctic Sea Ice', 'Snow', 'Glaciers']))



fig = px.line_polar(df, r='floating_and_grounded_ice_values', theta='floating_and_grounded_ice', line_close=True)

fig.update_traces(fill='toself')

fig.show()

fig = go.Figure()
for snow_mass,p, year in zip(snow_masses_yearly, pal, years):
    fig.add_trace(go.Scatter(x = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'June', 'July', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                             y = snow_mass,
                             name = str(year),
                             line_color = p,
                             fill='tozeroy'))   #tozeroy 

fig.update_layout(width = 1000, height = 800)

fig.show()


print(seasonality)

# %%
