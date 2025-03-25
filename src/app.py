#!/usr/bin/env python3
import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import numpy as np

# Sample data generation (replace these with your actual data)
npz='../npz/sst_yearly_mean_1982_2023.npz'
C=np.load(npz)
lon=C['lon']
lat=C['lat']
sst=C['sst_yearly']
warming=np.load('../npz/warming.npz')['slopes']; warming[warming==0]=np.nan
years = np.arange(1982, 2023)

# Initialize Dash app
app = dash.Dash(__name__)
server = app.server

# Layout
app.layout = html.Div([
    html.H1("Global Warming Dashboard", style={'textAlign': 'center'}),

    html.Div([
    # Colormap selection input box
    html.Label("Enter Colormap:", style={'fontSize': '20px'}),
    dcc.Input(id='colormap-input', type='text', value='RdBu_r', style={'fontSize': '20px','width': '150px'}),

    # zmin and zmax input fields
    html.Label("zmin:", style={'fontSize': '20px'}),
    dcc.Input(id='zmin-input', type='number', value=-0.05, style={'fontSize': '15px','width': '70px'}),

    html.Label("zmax:", style={'fontSize': '20px'}),
    dcc.Input(id='zmax-input', type='number', value=0.05, style={'fontSize': '15px','width': '70px'}),
    
    html.Label(u"Δdlon:", style={'fontSize': '20px'}),
    dcc.Input(id='dlon-input', type='number', value=5, style={'fontSize': '15px','width': '70px'}),
    
    html.Label(u"Δlat:", style={'fontSize': '20px'}),
    dcc.Input(id='dlat-input', type='number', value=5, style={'fontSize': '15px','width': '70px'}),
    ], style={'display': 'flex', 'justifyContent': 'center'}),
    
    html.Div([
    dcc.Graph(id='global-plot', style={'height': '40vw', 'width': '60vw'}),
    dcc.Graph(id='time-series-plot', style={'height': '30vw', 'width': '60vw'})
], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'})
    
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
    fig = go.Figure(data=go.Heatmap(z=warming, x=lon, y=lat, colorscale=colormap, zmin=zmin, zmax=zmax))
    fig.update_layout(title={'text':'Global Warming Map','font': {'size': 20},'x': 0.5,  # Center the title
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
    
    sst_time_series = sst[:, max([0,lat_idx-int(dlat*2)]):min([lat_idx+1+int(dlat*2),len(lat)]), max([0,lon_idx-int(dlon*2)]):min([lon_idx+1+int(dlon*2),len(lon)])]
    sst_time_series=sst_time_series.mean(axis=(1,2))
    fig2 = go.Figure(data=go.Scatter(x=years, y=sst_time_series, mode='lines+markers',
                                     line=dict(color='black'),
                                     marker=dict(size=20)))
    fig2.update_layout(title={'text':f'SST Time Series at ({clicked_x:.2f}, {clicked_y:.2f}) with Δlon={dlon:.1f} and Δlat={dlat:.1f}',
                              'font': {'size': 20},'x': 0.5,  # Center the title
                              'xanchor': 'center'},
                       xaxis_title='Year',
                       yaxis_title='SST (\u00b0C)')

    return fig2

if __name__ == '__main__':
    app.run()
    
#after run the script; open your internet browser and go to: http://127.0.0.1:8050
