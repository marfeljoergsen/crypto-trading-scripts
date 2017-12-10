#!/usr/bin/env python
# ---

# Modified version of: https://blog.patricktriest.com/analyzing-cryptocurrencies-python/
import numpy as np
import pandas as pd
from lib import crypto_trading_lib as ctl
import sys
sys.path.insert(0, './lib')
from plot_settings import *
import time # plotly needs time to switch/open new browser tab
from datetime import datetime
#import pdb

# =============================================================
# Run "jupyter notebook" from shell to get the correct graphs.
# =============================================================


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
        titleStr='Pearson Coefficient: ' + title
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
        plt.title(titleStr)
        plt.show()
        #pdb.set_trace()


# ---
dataDir = 'data/'
altcoinsFile = 'altcoins.txt'
start_date = datetime.strptime('2016-01-01', '%Y-%m-%d')  # get data from the start of 2015
# start_date = datetime.strptime('2017-07-01', '%Y-%m-%d')
# ---


# Step 2.2 - Pull Kraken Exchange Pricing Data
# --------------------------------------------
# Pull Kraken BTC price exchange data
# ("Quandl Code ID" search e.g.: https://www.quandl.com/search?query= )
btc_usd_price_kraken = ctl.get_quandl_data('BCHARTS/KRAKENUSD', dataDir)

# Pull pricing data for 3 more BTC exchanges
exchanges = ['COINBASE', 'BITSTAMP', 'ITBIT']

# Storing Pandas DF in dict (data from KRAKEN + other exchanges):
exchange_data = {}  # dict
exchange_data['KRAKEN'] = btc_usd_price_kraken  # Pandas DF
for exchange in exchanges:
    exchange_code = 'BCHARTS/{}USD'.format(exchange)
    btc_exchange_df = ctl.get_quandl_data(exchange_code, dataDir)  # Pandas DF
    exchange_data[exchange] = btc_exchange_df

# Now we will merge all of the dataframes together on their "Weighted
# Price" column (merge the BTC price dataseries' into a single dataframe)
btc_usd_datasets = ctl.merge_dfs_on_column(  # def merge_dfs_on_column(dataframes, labels, col):
    list(exchange_data.values()), list(exchange_data.keys()), 'Weighted Price')

# Remove "0" values
btc_usd_datasets.replace(0, np.nan, inplace=True)

# We can now calculate a new column, containing the average daily
# Bitcoin price across all of the exchanges.
btc_usd_datasets['avg_btc_price_usd'] = btc_usd_datasets.mean(axis=1)

# Step 3 - Retrieve Altcoin Pricing Data
# --------------------------------------

# Step 3.2 - Download Trading Data From Poloniex
# ----------------------------------------------
# We'll download exchange data for nine of the top cryptocurrencies -
# Ethereum, Litecoin, Ripple, Ethereum Classic, Stellar, Dashcoin,
# Siacoin, Monero, and NEM.

if False:
    altcoins = ['ETH', 'LTC', 'XRP', 'ETC', 'STR', 'DASH', 'SC', 'XMR', 'XEM']
else:
    with open(altcoinsFile) as f:
        altcoins = f.read().splitlines()
print("Downloading data for these altcoins: ", altcoins)

altcoin_data = {}  # dict
for altcoin in altcoins:
    coinpair = 'BTC_{}'.format(altcoin)
    crypto_price_df = ctl.get_crypto_data(coinpair, start_date, dataDir)
    altcoin_data[altcoin] = crypto_price_df  # adding Pandas DF to dict

if not usePlotly:
    plt.close('all')

print("Converting to DKK")
eur_usd_price = ctl.get_quandl_data('BUNDESBANK/BBEX3_D_USD_EUR_BB_AC_000', dataDir)
eur_in_dkk_price = ctl.get_quandl_data('ECB/EURDKK', dataDir)
usd_in_dkk_price = eur_in_dkk_price / eur_usd_price

if False:
    ctl.df_scatter(usd_in_dkk_price, 'Price for 1 USD in DKK')
if False:
    plt.plot(usd_in_dkk_price.index, usd_in_dkk_price)
    plt.title("1 USD in DKK")
    plt.grid(True)
    plt.legend()
    plt.show()

btc_in_dkk_price = usd_in_dkk_price.multiply(btc_usd_price_kraken['Weighted Price'], axis='index')  # maybe: .dropna()

if False:  # True:
    titl = "Historical price for 1 BTC in DKK"
    if usePlotly:
        layout = go.Layout(title=titl, xaxis=dict(type='date'),
                           yaxis=dict(title='1 BTC Price in DKK'))
        trace_arr = []
        btc_trace = go.Scatter(x=btc_in_dkk_price.index,
                               y=btc_in_dkk_price['Value'], name='1 BTC price converted to DKK')
        trace_arr.append(btc_trace)
        fig = go.Figure(data=trace_arr, layout=layout)
        if useJupyterNotebook:
            py.iplot(fig)
        else:
            py.plot(fig)
        print("Waiting " + str(plotlyDelay) +
              " seconds for browser to open up figure: " + titl)
        time.sleep(plotlyDelay)

    else:
        plt.plot(btc_in_dkk_price.index, btc_in_dkk_price)
        plt.title(titl)
        plt.grid(True)
        plt.legend()
        plt.show()

if True:  # Print stats
    print("=" * 50)
    print("btc_in_dkk_price.first_valid_index() = " + str(btc_in_dkk_price.first_valid_index()))
    print("btc_in_dkk_price.last_valid_index() = " + str(btc_in_dkk_price.last_valid_index()))
    print("Fraction of valid vs invalid values in btc_in_dkk_price: " + str(
        btc_in_dkk_price['Value'].count() / len(btc_in_dkk_price)))
    print("Number of NaN's: " + str(btc_in_dkk_price['Value'].isnull().sum()))
    print("Number of 0's: " + str(sum(btc_in_dkk_price['Value'] == 0)))

if True:  # remove invalid indices:
    btc_in_dkk_price = btc_in_dkk_price[btc_in_dkk_price['Value'].notnull()]  # remove unused indices
    print("Number of 0'values (to be replaced with NaN): " + str(np.sum(btc_in_dkk_price['Value'] == 0)))
    btc_in_dkk_price.replace(0, np.nan, inplace=True)  # replace 0 with NaN
    print("Number of 0'values: " + str(np.sum(btc_in_dkk_price['Value'] == 0)))

if True:  # Remove NaN-values:
    print("  *** WARNING: Removing NaN-values by interpolation! ***")
    print("Number of NaN values: " + str(np.sum(np.isnan(btc_in_dkk_price['Value']))))
    btc_in_dkk_price = btc_in_dkk_price.interpolate()  # interpolate to remove NaN's
    print("Number of NaN values: " + str(np.sum(np.isnan(btc_in_dkk_price['Value']))))

if True:  # Print stats again
    print("Fraction of valid vs invalid values in btc_in_dkk_price: " + str(
        btc_in_dkk_price['Value'].count() / len(btc_in_dkk_price)))
    print("Number of NaN's: " + str(btc_in_dkk_price['Value'].isnull().sum()))
    print("Number of 0'values: " + str(np.sum(btc_in_dkk_price['Value'] == 0)))

if False:  # True: # write to Excel
    btc_in_dkk_price.to_excel('btc_in_dkk_price.xls')

# Calculate the historical FIAT-currency values for each altcoin.
if False:
    FIAT_curr = 'USD'
    for altcoin in altcoin_data.keys():
        altcoin_data[altcoin]['price'] = \
            altcoin_data[altcoin]['weightedAverage'] * btc_usd_datasets['avg_btc_price_usd']
        if False:  # True: # Drop NaN!
            altcoin_data[altcoin]['price'] = altcoin_data[altcoin]['price'].dropna()
    # Create a combined dataframe of the price for each cryptocurrency, into single dataframe
    combined_df = ctl.merge_dfs_on_column(list(altcoin_data.values()), list(altcoin_data.keys()), 'price')
    combined_df['BTC'] = btc_usd_datasets['avg_btc_price_usd']  # Add BTC price to the dataframe
else:
    FIAT_curr = 'DKK'
    for altcoin in altcoin_data.keys():
        altcoin_data[altcoin]['price'] = \
            altcoin_data[altcoin]['weightedAverage'] * btc_usd_datasets['avg_btc_price_usd']
        altcoin_data[altcoin]['price'] = altcoin_data[altcoin]['price'] * usd_in_dkk_price['Value']
        if False:  # True: # Drop NaN!
            altcoin_data[altcoin]['price'] = altcoin_data[altcoin]['price'].dropna()
    # Create a combined dataframe of the price for each cryptocurrency, into single dataframe
    combined_df = ctl.merge_dfs_on_column(list(altcoin_data.values()), list(altcoin_data.keys()), 'price')
    BTCinDKK = btc_usd_datasets['avg_btc_price_usd'] * usd_in_dkk_price['Value']
    combined_df['BTC'] = BTCinDKK

    if True:  # chop useless dates
        print("Removing early ticker info from before: " + str(start_date))
        BTCinDKK = BTCinDKK[BTCinDKK.index >= start_date]

    if True:  # Write to Excel
        excelOutputFile = 'CryptoData.xlsx'
        print("Writing to Excel file: " + excelOutputFile)
        with pd.ExcelWriter(excelOutputFile) as writer:
            BTCinDKK.to_excel(writer, "BTC")  # Write BTC as first sheet
            for altcoin in altcoin_data.keys():
                altcoin_data[altcoin]['price'].to_excel(writer, altcoin)  # Write to following sheets

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
