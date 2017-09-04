#!/usr/bin/env python
# ---

# Modified version of: https://blog.patricktriest.com/analyzing-cryptocurrencies-python/

# =============================================================
# Run "jupyter notebook" from shell to get the correct graphs.
# =============================================================

import os
import numpy as np
import pandas as pd
import pickle
import quandl
from datetime import datetime

#---
usePlotly = True # for jupyter notebook (plotly)
usePlotly = False # for normal python (matplotlib)
#---
#useJupyterNotebook = True # (use py.iplot - shows directly in Jupyter NTB)
useJupyterNotebook = False # (use py.plot - opens webpage in your browser)
#---
dataDir = 'data/'


if usePlotly:
    import plotly.offline as py
    import plotly.graph_objs as go
    import plotly.figure_factory as ff
    py.init_notebook_mode(connected=True)
else:
    import matplotlib.pyplot as plt

import pdb


# Step 2 - Retrieve Bitcoin Pricing Data
# --------------------------------------
# To assist with this data retrieval we'll define a function to
# download and cache datasets from Quandl.
def get_quandl_data(quandl_id):
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

# Step 2.2 - Pull Kraken Exchange Pricing Data
# --------------------------------------------
# Pull Kraken BTC price exchange data
btc_usd_price_kraken = get_quandl_data('BCHARTS/KRAKENUSD')

# We can inspect the first 5 rows of the dataframe using the head() method.
btc_usd_price_kraken.head()

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
    btc_exchange_df = get_quandl_data(exchange_code)
    exchange_data[exchange] = btc_exchange_df

# Step 2.4 - Merge All Of The Pricing Data Into A Single Dataframe
# ----------------------------------------------------------------

# Next, we will define a simple function to merge a common column of
# each dataframe into a new combined dataframe.

def merge_dfs_on_column(dataframes, labels, col):
    '''Merge a single column of each dataframe into a new combined dataframe'''
    series_dict = {}
    for index in range(len(dataframes)):
        series_dict[labels[index]] = dataframes[index][col]
    return pd.DataFrame(series_dict)

# Now we will merge all of the dataframes together on their "Weighted
# Price" column (merge the BTC price dataseries' into a single dataframe)

btc_usd_datasets = merge_dfs_on_column( list(exchange_data.values()), list(exchange_data.keys()), 'Weighted Price' )
print("btc_usd_datasets = ")
print( btc_usd_datasets.tail() )

# Step 2.5 - Visualize The Pricing Datasets
# -----------------------------------------
# For this, we'll define a helper function to provide a single-line
# command to generate a graph from the dataframe.

def df_scatter(df, title, seperate_y_axis=False, y_axis_label='', scale='linear', initial_hide=False):
    '''Generate a scatter plot of the entire dataframe'''
    label_arr = list(df)
    series_arr = list(map(lambda col: df[col], label_arr))

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
    if usePlotly:
        for index, series in enumerate(series_arr):
            trace = go.Scatter(
                x=series.index,
                y=series,
                name=label_arr[index],
                visible=visibility
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

    else:
        # Use Matplotlib instead of plotly:
        for index, series in enumerate(series_arr):
            trace = { "x" : series.index, "y" : series, "name" : label_arr[index] }
            trace_arr.append(trace)

        for i in range(len(trace_arr)):
            plt.plot(trace_arr[i]["x"],  trace_arr[i]["y"],  label = 'id %s'%trace_arr[i]["name"])
        if scale=='log':
            plt.yscale('log')
        plt.grid(True)
        plt.legend()
        plt.title(title)
        plt.show()

    #pdb.set_trace()

# We can now easily generate a graph for the Bitcoin pricing data.
# # Plot all of the BTC exchange prices
df_scatter(btc_usd_datasets, 'Bitcoin Price (USD) By Exchange')


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
df_scatter(btc_usd_datasets, 'Bitcoin Price (USD) By Exchange')

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



# Step 3 - Retrieve Altcoin Pricing Data
# --------------------------------------
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

base_polo_url = 'https://poloniex.com/public?command=returnChartData&currencyPair={}&start={}&end={}&period={}'
start_date = datetime.strptime('2015-01-01', '%Y-%m-%d') # get data from the start of 2015
#start_date = datetime.strptime('2017-07-01', '%Y-%m-%d')
end_date = datetime.now() # up until today
pediod = 86400 # pull daily data (86,400 seconds per day)

def get_crypto_data(poloniex_pair):
    '''Retrieve cryptocurrency data from poloniex'''
    json_url = base_polo_url.format(poloniex_pair, start_date.timestamp(), end_date.timestamp(), pediod)
    data_df = get_json_data(json_url, dataDir + poloniex_pair)
    data_df = data_df.set_index('date')
    return data_df


# Step 3.2 - Download Trading Data From Poloniex
# ----------------------------------------------
# We'll download exchange data for nine of the top cryptocurrencies -
# Ethereum, Litecoin, Ripple, Ethereum Classic, Stellar, Dashcoin,
# Siacoin, Monero, and NEM.

altcoins = ['ETH','LTC','XRP','ETC','STR','DASH','SC','XMR','XEM']
print("Downloading data for these altcoins: ",  altcoins)

altcoin_data = {}
for altcoin in altcoins:
    coinpair = 'BTC_{}'.format(altcoin)
    crypto_price_df = get_crypto_data(coinpair)
    altcoin_data[altcoin] = crypto_price_df

print("We can preview the last few rows of the Ethereum price table to make sure it looks ok:")
print( altcoin_data['ETH'].tail() )


# Step 3.3 - Convert Prices to USD
# --------------------------------
# Now we can combine this BTC-altcoin exchange rate data with our
# Bitcoin pricing index to directly calculate the historical USD
# values for each altcoin.

print(" ")
print("Need to change this line into something with DKK: ")
print("altcoin_data[altcoin]['price_usd'] =  altcoin_data[altcoin]['weightedAverage'] * btc_usd_datasets['avg_btc_price_usd']")

for altcoin in altcoin_data.keys():
    altcoin_data[altcoin]['price_usd'] =  altcoin_data[altcoin]['weightedAverage'] * btc_usd_datasets['avg_btc_price_usd']


# Here, we've created a new column in each altcoin dataframe with the
# USD prices for that coin. Next, we can re-use our
# merge_dfs_on_column function from earlier to create a combined
# dataframe of the USD price for each cryptocurrency.

# Merge USD price of each altcoin into single dataframe
combined_df = merge_dfs_on_column( list(altcoin_data.values()), list(altcoin_data.keys()), 'price_usd' )

# Easy. Now let's also add the Bitcoin prices as a final column to the
# combined dataframe ==> Add BTC price to the dataframe
combined_df['BTC'] = btc_usd_datasets['avg_btc_price_usd']

# Now we should have a single dataframe containing daily USD prices
# for the ten cryptocurrencies that we're examining.

# Let's reuse our df_scatter function from earlier to chart all of the
# cryptocurrency prices against each other.

# Chart all of the altocoin prices
df_scatter(combined_df, 'Cryptocurrency Prices (USD)', seperate_y_axis=False, y_axis_label='Coin Value (USD)', scale='log')
df_scatter(combined_df, 'Cryptocurrency Prices (USD)', seperate_y_axis=False, y_axis_label='Coin Value (USD)')

# Note that we're using a logarithmic y-axis scale in order to compare
# all of the currencies on the same plot. You are welcome to try out
# different parameters values here (such as scale='linear') to get
# different perspectives on the data.


# Step 3.4 - Perform Correlation Analysis
# ---------------------------------------

# You might notice is that the cryptocurrency exchange rates, despite
# their wildly different values and volatility, look slightly
# correlated. Especially since the spike in April 2017, even many of
# the smaller fluctuations appear to be occurring in sync across the
# entire market.

# A visually-derived hunch is not much better than a guess until we
# have the stats to back it up.

# We can test our correlation hypothesis using the Pandas corr()
# method, which computes a Pearson correlation coefficient for each
# column in the dataframe against each other column.

# Computing correlations directly on a non-stationary time series
# (such as raw pricing data) can give biased correlation values. We
# will work around this by first applying the pct_change() method,
# which will convert each cell in the dataframe from an absolute price
# value to a daily return percentage.

# To help visualize these results, we'll create one more helper
# visualization function.

def correlation_heatmap(df, title, absolute_bounds=True):
    '''Plot a correlation heatmap for the entire dataframe'''
    if usePlotly:
        heatmap = go.Heatmap(
            z=df.corr(method='pearson').as_matrix(),
            x=df.columns,
            y=df.columns,
            colorbar=dict(title='Pearson Coefficient'),
        )

        layout = go.Layout(title=title)

        if absolute_bounds:
            heatmap['zmax'] = 1.0
            heatmap['zmin'] = -1.0

        fig = go.Figure(data=[heatmap], layout=layout)

        if useJupyterNotebook:
            py.iplot(fig)
        else:
            py.plot(fig)

    else:
        z=df.corr(method='pearson').as_matrix()
        print("z=df.corr(method='pearson').as_matrix() =")
        print(z)
        x=df.columns.tolist()
        y=df.columns.tolist()
        title='Pearson Coefficient'
        # ----
        #fig, ax = plt.subplots()
        #fig, ax = plt.subplots(figsize=(x, y)
        fig, ax = plt.subplots(figsize= z.shape)
        ax.matshow( z )

        # put the major ticks at the middle of each cell, notice "reverse" use of dimension
        #ax.set_yticks(np.arange(z.shape[0])+0.5, minor=False) # array([ 0.5,  1.5,  2.5,  3.5,  4.5,  5.5,  6.5,  7.5,  8.5,  9.5])
        #ax.set_xticks(np.arange(z.shape[1])+0.5, minor=False) # array([ 0.5,  1.5,  2.5,  3.5,  4.5,  5.5,  6.5,  7.5,  8.5,  9.5])
        ax.set_xticklabels(x, minor=False)
        ax.set_yticklabels(y, minor=False)

        #plt.xticks(range(len(z.columns)), z.columns);
        #plt.yticks(range(len(z.columns)), z.columns);
        plt.show()
        #pdb.set_trace()


# First we'll calculate correlations for 2016.

# Calculate the pearson correlation coefficients for cryptocurrencies in 2016
combined_df_2016 = combined_df[combined_df.index.year == 2016]
combined_df_2016.pct_change().corr(method='pearson')

print("combined_df_2016.pct_change() =")
print(combined_df_2016.pct_change())

correlation_heatmap(combined_df_2016.pct_change(), "Cryptocurrency Correlations in 2016")

# These correlation coefficients are all over the place. Coefficients
# close to 1 or -1 mean that the series' are strongly correlated or
# inversely correlated respectively, and coefficients close to zero
# mean that the values are not correlated, and fluctuate independently
# of each other.

print(' ')

# Here, the dark red values represent strong correlations (note that
# each currency is, obviously, strongly correlated with itself), and
# the dark blue values represent strong inverse correlations. All of
# the light blue/orange/gray/tan colors in-between represent varying
# degrees of weak/non-existent correlations.

# What does this chart tell us? Essentially, it shows that there was
# little statistically significant linkage between how the prices of
# different cryptocurrencies fluctuated during 2016.

# Now, to test our hypothesis that the cryptocurrencies have become
# more correlated in recent months, let's repeat the same test using
# only the data from 2017.

combined_df_2017 = combined_df[combined_df.index.year == 2017]
combined_df_2017.pct_change().corr(method='pearson')

print("combined_df_2017.pct_change() =")
print(combined_df_2017.pct_change())

# These are somewhat more significant correlation coefficients. Strong
# enough to use as the sole basis for an investment? Certainly not.

# It is notable, however, that almost all of the cryptocurrencies have
# become more correlated with each other across the board.

correlation_heatmap(combined_df_2017.pct_change(), "Cryptocurrency Correlations in 2017")

# Why is this happening? Good question. I'm really not sure. The most
# immediate explanation that comes to mind is that hedge funds have
# recently begun publicly trading in crypto-currency
# markets[1][2]. These funds have vastly more capital to play with
# than the average trader, so if a fund is hedging their bets across
# multiple cryptocurrencies, and using similar trading strategies for
# each based on independent variables (say, the stock market), it
# could make sense that this trend of increasing correlations would
# emerge.
