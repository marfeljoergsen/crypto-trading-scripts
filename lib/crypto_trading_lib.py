import pickle
from datetime import datetime
import pandas as pd
import quandl
import sys
from plot_settings import *
import time # plotly needs time to switch/open new browser tab

start_date = datetime.strptime('2015-01-01', '%Y-%m-%d') # get data from the start of 2015
#start_date = datetime.strptime('2017-07-01', '%Y-%m-%d')
end_date = datetime.now() # up until today
pediod = 86400 # pull daily data (86,400 seconds per day)

# =================================
#usePlotly = True # for jupyter notebook (plotly)
#usePlotly = False # for normal python (matplotlib)
##---
##useJupyterNotebook = True # (use py.iplot - shows directly in Jupyter NTB)
#useJupyterNotebook = False # (use py.plot - opens webpage in your browser)
#if usePlotly:
#    import plotly.offline as py
#    import plotly.graph_objs as go
#    import plotly.figure_factory as ff
#    py.init_notebook_mode(connected=True)
#else:
#    import matplotlib.pyplot as plt
## =================================


# Step 2 - Retrieve Bitcoin Pricing Data
# --------------------------------------
# To assist with this data retrieval we'll define a function to
# download and cache datasets from Quandl.
# ("Quandl Code ID" search e.g.: https://www.quandl.com/search?query= )
def get_quandl_data(quandl_id, dataDir):
    '''Download and cache Quandl dataseries'''
    cache_path = dataDir + '{}.pkl'.format(quandl_id).replace('/','-')
    try:
        f = open(cache_path, 'rb')
        df = pickle.load(f)
        print('Loaded {} from cache'.format(quandl_id))
    except (OSError, IOError) as e:
        print('Downloading {} from Quandl'.format(quandl_id))
        df = quandl.get(quandl_id, returns="pandas")
        df.to_pickle(cache_path)
        print('Cached {} at {}'.format(quandl_id, cache_path))
    return df

# We're using pickle to serialize and save the downloaded data as a
# file, which will prevent our script from re-downloading the same
# data each time we run the script. The function will return the data
# as a Pandas dataframe.



# Step 2.4 - Merge All Of The Pricing Data Into A Single Dataframe
# ----------------------------------------------------------------

# Next, we will define a simple function to merge a common column of
# each dataframe into a new combined dataframe.

def merge_dfs_on_column(dataframes, labels, col):
    '''Merge a single column of each dataframe into a new combined dataframe'''
    series_dict = {}
    for index in range(len(dataframes)):
        series_dict[labels[index]] = dataframes[index][col]
    return pd.DataFrame(series_dict) # convert dict to Pandas DF



def df_scatter(df, title, seperate_y_axis=False, y_axis_label='',
               scale='linear', initial_hide=False, connGaps=False):
    '''Generate a scatter plot of the entire dataframe'''

    global usePlotly, useJupyterNotebook

    label_arr = list(df) # = ['DASH', 'ETC', 'ETH', 'LTC', 'SC', 'STR', 'XEM', 'XMR', 'XRP', 'BTC']
    series_arr = list(map(lambda col: df[col], label_arr)) # list of map(function, iterable, ...)

    if usePlotly:
        layout = go.Layout(
            title=title,
            legend=dict(orientation="h"),
            xaxis=dict(type='date'),
            yaxis=dict(
                title=y_axis_label,
                showticklabels= not seperate_y_axis,
                type=scale
            )
        )

        y_axis_config = dict(
            overlaying='y',
            showticklabels=False,
            type=scale )

        visibility = 'visible'
        if initial_hide:
            visibility = 'legendonly'

        # Form Trace For Each Series
        trace_arr = []
        for index, series in enumerate(series_arr):
            trace = go.Scatter(
                x=series.index,
                y=series,
                name=label_arr[index],
                visible=visibility,
                connectgaps = connGaps
            )
            # Add seperate axis for the series
            if seperate_y_axis:
                trace['yaxis'] = 'y{}'.format(index + 1)
                layout['yaxis{}'.format(index + 1)] = y_axis_config
            trace_arr.append(trace)

        fig = go.Figure(data=trace_arr, layout=layout)
        if useJupyterNotebook:
            py.iplot(fig)
        else:
            py.plot(fig)
        print("Waiting " + str(plotlyDelay) +
              " second(s) for browser to open figure: " + layout.title)
        time.sleep(plotlyDelay)
    else:
        # Use Matplotlib instead of plotly:
        for index, series in enumerate(series_arr): # series_arr = list(map(lambda col: df[col], label_arr)),
            # where label_arr = ['DASH', 'ETC', 'ETH', 'LTC', 'SC', 'STR', 'XEM', 'XMR', 'XRP', 'BTC']
            trace = { "x" : series.index, "y" : series, "name" : label_arr[index] }
            trace_arr.append(trace)

        for i in range(len(trace_arr)):
            plt.plot(trace_arr[i]["x"],  trace_arr[i]["y"],  label = '%s'%trace_arr[i]["name"])
        if scale=='log':
            plt.yscale('log')
        plt.grid(True)
        plt.legend()
        plt.title(title)
        plt.show()

    #pdb.set_trace()


# Step 3.1 - Define Poloniex API Helper Functions

# For retrieving data on cryptocurrencies we'll be using the Poloniex
# API. To assist in the altcoin data retrieval, we'll define two
# helper functions to download and cache JSON data from this
# API. First, we'll define get_json_data, which will download and
# cache JSON data from a provided URL.

def get_json_data(json_url, cache_path):
    '''Download and cache JSON data, return as a dataframe.'''
    try:
        f = open(cache_path, 'rb')
        df = pickle.load(f)
        print('Loaded {} from cache'.format(json_url))
    except (OSError, IOError) as e:
        print('Downloading {}'.format(json_url))
        df = pd.read_json(json_url)
        df.to_pickle(cache_path)
        print('Cached {} at {}'.format(json_url, cache_path))
    return df

# Next, we'll define a function that will generate Poloniex API HTTP
# requests, and will subsequently call our new get_json_data function
# to save the resulting data.


def get_crypto_data(poloniex_pair, dataDir):
    '''Retrieve cryptocurrency data from poloniex'''
    base_polo_url = 'https://poloniex.com/public?command=returnChartData&currencyPair={}&start={}&end={}&period={}'
    json_url = base_polo_url.format(poloniex_pair, start_date.timestamp(), end_date.timestamp(), pediod)
    data_df = get_json_data(json_url, dataDir + poloniex_pair)
    data_df = data_df.set_index('date')
    return data_df
