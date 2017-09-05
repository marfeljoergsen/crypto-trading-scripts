#!/usr/bin/env python
# ---

# Modified version of: https://blog.patricktriest.com/analyzing-cryptocurrencies-python/

# =============================================================
# Run "jupyter notebook" from shell to get the correct graphs.
# =============================================================

import os
import numpy as np
#import pandas as pd
from lib import crypto_trading_lib as ctl
#import pdb

#---
dataDir = 'data/'

# =================================
usePlotly = True # for jupyter notebook (plotly)
usePlotly = False # for normal python (matplotlib)
#---
#useJupyterNotebook = True # (use py.iplot - shows directly in Jupyter NTB)
useJupyterNotebook = False # (use py.plot - opens webpage in your browser)
if usePlotly:
    import plotly.offline as py
    import plotly.graph_objs as go
    import plotly.figure_factory as ff
    py.init_notebook_mode(connected=True)
else:
    import matplotlib.pyplot as plt
# =================================


# Step 2.2 - Pull Kraken Exchange Pricing Data
# --------------------------------------------
# Pull Kraken BTC price exchange data
btc_usd_price_kraken = ctl.get_quandl_data('BCHARTS/KRAKENUSD', dataDir)

# We can inspect the first 5 rows of the dataframe using the head() method.
print("We can inspect the first 5 rows of the dataframe using the head() method:")
print( btc_usd_price_kraken.head() )


# Chart the BTC pricing data
if usePlotly:
    btc_trace = go.Scatter(x=btc_usd_price_kraken.index, y=btc_usd_price_kraken['Weighted Price'])
    if useJupyterNotebook:
        py.iplot([btc_trace])
    else:
        py.plot([btc_trace])
else:
    btc_trace = plt.plot(btc_usd_price_kraken.index, btc_usd_price_kraken['Weighted Price'])
    plt.grid(True)
    plt.show()

#pdb.set_trace()
# Here, we're using Plotly for generating our visualizations. This is
# a less traditional choice than some of the more established Python
# data visualization libraries such as Matplotlib, but I think Plotly
# is a great choice since it produces fully-interactive charts using
# D3.js. These charts have attractive visual defaults, are easy to
# explore, and are very simple to embed in web pages.

# Step 2.3 - Pull Pricing Data From More BTC Exchanges
# ----------------------------------------------------

# First, we will download the data from each exchange into a
# dictionary of dataframes.

# Pull pricing data for 3 more BTC exchanges
exchanges = ['COINBASE','BITSTAMP','ITBIT']

exchange_data = {}

exchange_data['KRAKEN'] = btc_usd_price_kraken

for exchange in exchanges:
    exchange_code = 'BCHARTS/{}USD'.format(exchange)
    btc_exchange_df = ctl.get_quandl_data(exchange_code, dataDir)
    exchange_data[exchange] = btc_exchange_df


# Now we will merge all of the dataframes together on their "Weighted
# Price" column (merge the BTC price dataseries' into a single dataframe)

btc_usd_datasets = ctl.merge_dfs_on_column( list(exchange_data.values()), list(exchange_data.keys()), 'Weighted Price' )
print("btc_usd_datasets = ")
print( btc_usd_datasets.tail() )


# Step 2.5 - Visualize The Pricing Datasets
# -----------------------------------------
# For this, we'll define a helper function to provide a single-line
# command to generate a graph from the dataframe.


# We can now easily generate a graph for the Bitcoin pricing data.
# # Plot all of the BTC exchange prices
ctl.df_scatter(btc_usd_datasets, 'Bitcoin Price (USD) By Exchange')


# Step 2.6 - Clean and Aggregate the Pricing Data
# -----------------------------------------------
# We can see that, although the four series follow roughly the same
# path, there are various irregularities in each that we'll want to
# get rid of. Let's remove all of the zero values from the dataframe,
# since we know that the price of Bitcoin has never been equal to zero
# in the timeframe that we are examining.

# Remove "0" values
btc_usd_datasets.replace(0, np.nan, inplace=True)

# When we re-chart the dataframe, we'll see a much cleaner looking
# chart without the down-spikes:
ctl.df_scatter(btc_usd_datasets, 'Bitcoin Price (USD) By Exchange')

# We can now calculate a new column, containing the average daily
# Bitcoin price across all of the exchanges.
btc_usd_datasets['avg_btc_price_usd'] = btc_usd_datasets.mean(axis=1)

# This new column is our Bitcoin pricing index! Let's chart that
# column to make sure it looks ok.
if usePlotly:
    btc_trace = go.Scatter(x=btc_usd_datasets.index, y=btc_usd_datasets['avg_btc_price_usd'])
    if useJupyterNotebook:
        py.iplot([btc_trace])
    else:
        py.plot([btc_trace])
else:
    plt.plot( btc_usd_datasets.index, btc_usd_datasets['avg_btc_price_usd'] )
    plt.grid(True)
    plt.legend()
    plt.show()

    #pdb.set_trace()
