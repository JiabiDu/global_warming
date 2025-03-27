#!/usr/bin/env python3
import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import numpy as np
import os

# Sample data generation (replace these with your actual data)
npz='npz/sst_yearly_mean_1982_2023.npz'
C=np.load(npz)
lon=C['lon']
lat=C['lat']
sst=C['sst_yearly']
D=np.load('npz/warming.npz'); warming=D['slopes']; warming[warming==0]=np.nan
wlon,wlat=D['lon'],D['lat']
years = np.arange(1982, 2023)

# Initialize Dash app
app = dash.Dash(__name__)
server = app.server

# Layout
app.layout = html.Div([
    html.H1("Global Warming Dashboard  (developed by TAMUG)", style={'textAlign': 'center'}),

    html.Div([
    # Colormap selection input box
    html.Label("Enter Colormap:", style={'fontSize': '20px'}),
    dcc.Input(id='colormap-input', type='text', value='RdBu_r', style={'fontSize': '20px','width': '100px'}),

    # zmin and zmax input fields
    html.Label("zmin:", style={'fontSize': '20px'}),
    dcc.Input(id='zmin-input', type='number', value=-0.05, step=0.01, style={'fontSize': '15px','width': '70px'}),

    html.Label("zmax:", style={'fontSize': '20px'}),
    dcc.Input(id='zmax-input', type='number', value=0.05, step=0.01, style={'fontSize': '15px','width': '70px'}),
    
    html.Label(u"Δlon:", style={'fontSize': '20px'}),
    dcc.Input(id='dlon-input', type='number', value=5, style={'fontSize': '15px','width': '70px'}),
    
    html.Label(u"Δlat:", style={'fontSize': '20px'}),
    dcc.Input(id='dlat-input', type='number', value=5, style={'fontSize': '15px','width': '70px'}),
    ], style={'display': 'flex', 'justifyContent': 'center'}),
    
    html.Div([
    dcc.Graph(id='global-plot', style={'height': '40vw', 'width': '50vw'}),
    dcc.Graph(id='time-series-plot', style={'height': '40vw', 'width': '50vw'})
], style={'display': 'flex', 'flexDirection': 'row', 'alignItems': 'center'})
    
    # Global Warming Plot
    #dcc.Graph(id='global-plot', style={'width': '60vw', 'height': '40vw','display': 'flex', 'justifyContent': 'center'}),

    # Time Series Plot
    #dcc.Graph(id='time-series-plot',style={'width': '60vw', 'height': '30vw','display': 'flex', 'justifyContent': 'center'}),
])

@app.callback(
    Output('global-plot', 'figure'),
    [
        Input('colormap-input', 'value'),
        Input('zmin-input', 'value'),
        Input('zmax-input', 'value')
    ]
)

# if receiving any inputs in any of the three inputs, update the plot. 
def update_global_plot(colormap, zmin, zmax):
    fig = go.Figure(data=go.Heatmap(z=warming, x=wlon, y=wlat, colorscale=colormap, zmin=zmin, zmax=zmax))
    fig.update_layout(title={'text':'Global Warming (\u00b0C/yr)','font': {'size': 20},'x': 0.5,'y':0.9,  # Center the title
    'xanchor': 'center'}, xaxis_title='Longitude', yaxis_title='Latitude')
    return fig

@app.callback(
    Output('time-series-plot', 'figure'),
    [Input('global-plot', 'clickData'),Input('dlon-input', 'value'),Input('dlat-input', 'value')]
)
#if receiving any input (i.e., clicking the map), call function below to update time-series-plot
def update_time_series(clickData,dlon,dlat):
    if clickData is None:
        return go.Figure(layout={'title': 'Click a grid point to view SST time series'})

    clicked_x = clickData['points'][0]['x']
    clicked_y = clickData['points'][0]['y']

    lon_idx = np.abs(lon - clicked_x).argmin()
    lat_idx = np.abs(lat - clicked_y).argmin()
    
    sst_time_series = sst[:, max([0,lat_idx-int(dlat/2)]):min([lat_idx+1+int(dlat/2),len(lat)]), max([0,lon_idx-int(dlon/2)]):min([lon_idx+1+int(dlon/2),len(lon)])]
    sst_time_series=np.nanmean(sst_time_series,axis=(1,2))
    fig2 = go.Figure(data=go.Scatter(x=years, y=sst_time_series, mode='lines+markers',
                                     line=dict(color='black'),
                                     marker=dict(size=20)))
    fig2.update_layout(title={'text':f'SST at ({clicked_x:.1f}, {clicked_y:.1f}) avg over Δlon={dlon:.1f} and Δlat={dlat:.1f}',
                              'font': {'size': 20},'x': 0.5, 'y':0.9,  # Center the title
                              'xanchor': 'center'},
                       xaxis_title='Year',
                       yaxis_title='SST (\u00b0C)')

    return fig2

if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
    #app.run(host='0.0.0.0',port=10000)
    #app.run()
    
#after run the script; open your internet browser and go to: http://127.0.0.1:8050
