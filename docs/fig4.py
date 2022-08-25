#%%
import plotly.express as px 
import plotly.graph_objects as go
import pandas as pd 
import numpy as np 

# Get some data
df = pd.read_csv('D:\\Users\\Reuben\\Internship\\1994_2017_cummul_ice.csv')
print(df)
pd.options.plotting.backend = "plotly"
#df.plot()
# Plot 
fig = go.Figure()
fig.add_trace(go.Scatter(x=df['Year'], y=df['Antarctic Sea Ice'], name='Antarctica Sea Ice', fill='tonexty', line=dict(color="#33fff7")))
fig.add_trace(go.Scatter(x=df['Year'], y=df['Artic Sea Ice'], name='Artic Sea Ice', fill='tonexty', line=dict(color="#33d8ff")))
fig.add_trace(go.Scatter(x=df['Year'], y=df['Ice Shelf Calving'], name='Ice Shelf Calving', fill='tonexty', line=dict(color="#339cff")))
fig.add_trace(go.Scatter(x=df['Year'], y=df['Ice Shelf Thinning'], name='Ice Shelf Thinning', fill='tonexty', line=dict(color="#334dff")))
fig.add_trace(go.Scatter(x=df['Year'], y=df['Antarctica'], name='Antarctica', fill='tonexty', line=dict(color="#c633ff")))
fig.add_trace(go.Scatter(x=df['Year'], y=df['Greenland'], name='Greenland', fill='tonexty', line=dict(color="#aa33ff")))
fig.add_trace(go.Scatter(x=df['Year'], y=df['Glacier'], name='Glacier', fill='tonexty', line=dict(color="#9033ff")))
fig.add_trace(go.Scatter(x=df['Year'], y=df['Snow'], name='Snow', fill='tonexty', line=dict(color="#ff3382")))

fig.update_layout(
    title="Global ice mass change between 1994 and 2017",
    xaxis_title="Year",
    yaxis_title="Mass Change (Gt)",
    legend_title="Types of Ice + Snow",
    #font=dict(
        #family="Courier New, monospace",
        #size=18,
        #color="RebeccaPurple"
    )
#)

fig.show()


# Show plot 
fig.show()
# %%
