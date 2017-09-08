#!/usr/bin/env python
# ---

# Modified version of: https://blog.patricktriest.com/analyzing-cryptocurrencies-python/

# =============================================================
# Run "jupyter notebook" from shell to get the correct graphs.
# =============================================================

import numpy as np
#import pandas as pd
from lib import crypto_trading_lib as ctl
import sys
sys.path.insert(0, './lib')
from plot_settings import *
#import pdb

#---
dataDir = 'data/'



# Step 2.2 - Pull Kraken Exchange Pricing Data
# --------------------------------------------
# Pull Kraken BTC price exchange data
# ("Quandl Code ID" search e.g.: https://www.quandl.com/search?query= )
btc_usd_price_kraken = ctl.get_quandl_data('BCHARTS/KRAKENUSD', dataDir)

# Pull pricing data for 3 more BTC exchanges
exchanges = ['COINBASE','BITSTAMP','ITBIT']

# Storing Pandas DF in dict (data from KRAKEN + other exchanges):
exchange_data = {} # dict
exchange_data['KRAKEN'] = btc_usd_price_kraken # Pandas DF
for exchange in exchanges:
    exchange_code = 'BCHARTS/{}USD'.format(exchange)
    btc_exchange_df = ctl.get_quandl_data(exchange_code, dataDir) # Pandas DF
    exchange_data[exchange] = btc_exchange_df

# Now we will merge all of the dataframes together on their "Weighted
# Price" column (merge the BTC price dataseries' into a single dataframe)
btc_usd_datasets = ctl.merge_dfs_on_column( # def merge_dfs_on_column(dataframes, labels, col):
        list(exchange_data.values()), list(exchange_data.keys()), 'Weighted Price' )

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

altcoins = ['ETH','LTC','XRP','ETC','STR','DASH','SC','XMR','XEM']
print("Downloading data for these altcoins: ",  altcoins)

altcoin_data = {}
for altcoin in altcoins:
    coinpair = 'BTC_{}'.format(altcoin)
    crypto_price_df = ctl.get_crypto_data(coinpair, dataDir)
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
    if False:
        test1 = altcoin_data[altcoin]['weightedAverage']
        test2 = btc_usd_datasets['avg_btc_price_usd']
        df1aligned, df2aligned = test1.align(test2)
    #if altcoin_data[altcoin]['weightedAverage'].shape != btc_usd_datasets['avg_btc_price_usd'].shape
    altcoin_data[altcoin]['price_usd'] = \
        altcoin_data[altcoin]['weightedAverage'] * \
        btc_usd_datasets['avg_btc_price_usd']


# Here, we've created a new column in each altcoin dataframe with the
# USD prices for that coin. Next, we can re-use our
# merge_dfs_on_column function from earlier to create a combined
# dataframe of the USD price for each cryptocurrency.

# Merge USD price of each altcoin into single dataframe
combined_df = ctl.merge_dfs_on_column( list(altcoin_data.values()), list(altcoin_data.keys()), 'price_usd' )

# Easy. Now let's also add the Bitcoin prices as a final column to the
# combined dataframe ==> Add BTC price to the dataframe
combined_df['BTC'] = btc_usd_datasets['avg_btc_price_usd']

# Now we should have a single dataframe containing daily USD prices
# for the ten cryptocurrencies that we're examining.

# Let's reuse our ctl.df_scatter function from earlier to chart all of the
# cryptocurrency prices against each other.

# Chart all of the altocoin prices
if False:
    ctl.df_scatter(combined_df, 'Cryptocurrency Prices (USD)', seperate_y_axis=False, y_axis_label='Coin Value (USD)', scale='log')
    ctl.df_scatter(combined_df, 'Cryptocurrency Prices (USD)', seperate_y_axis=False, y_axis_label='Coin Value (USD)')
# Note that we're using a logarithmic y-axis scale in order to compare
# all of the currencies on the same plot. You are welcome to try out
# different parameters values here (such as scale='linear') to get
# different perspectives on the data.


plt.close('all') # Clean up - strictly not required
print("Converting to DKK")

# EUR/USD (BUNDESBANK/BBEX3_D_USD_EUR_BB_AC_000): https://www.quandl.com/data/BUNDESBANK/BBEX3_D_USD_EUR_BB_AC_000-Euro-foreign-exchange-reference-rate-of-the-ECB-EUR-1-USD-United-States
eur_usd_price = ctl.get_quandl_data('BUNDESBANK/BBEX3_D_USD_EUR_BB_AC_000', dataDir)
#eur_usd_price = ctl.get_crypto_data
#ctl.df_scatter(eur_usd_price, 'Price for 1 EUR in USD')

# EUR/DKK (ECB/EURDKK): https://www.quandl.com/data/ECB/EURDKK-EUR-vs-DKK-Foreign-Exchange-Reference-Rate
eur_in_dkk_price = ctl.get_quandl_data('ECB/EURDKK', dataDir)
#eur_in_dkk_price = ctl.get_crypto_data
#ctl.df_scatter(eur_in_dkk_price, 'Price for 1 EUR in DKK')

#usd_in_dkk_price = eur_usd_price * eur_in_dkk_price
usd_in_dkk_price = eur_in_dkk_price / eur_usd_price
if False:
    ctl.df_scatter(usd_in_dkk_price, 'Price for 1 USD in DKK')
#usd_in_dkk_price=usd_in_dkk_price.asfreq('D')

# import IPython; IPython.terminal.debugger.TerminalPdb().set_trace()
if False:
    btc_in_dkk_price = usd_in_dkk_price.multiply(btc_usd_price_kraken['Weighted Price'], axis='index')
    ctl.df_scatter(btc_in_dkk_price, 'Cryptocurrency Prices (DKK)', \
        seperate_y_axis=False, y_axis_label='Coin Value (USD)', scale='log')
    ctl.df_scatter(btc_in_dkk_price, 'Cryptocurrency Prices (DKK)', \
        seperate_y_axis=False, y_axis_label='Coin Value (USD)')
    
#btc_in_dkk_price = usd_in_dkk_price.multiply(btc_usd_price_kraken['Weighted Price'], axis='index')
#combined_df
#combined_df_DKK = usd_in_dkk_price.multiply(combined_df,  axis='index')
#combined_df_DKK = combined_df.multiply( usd_in_dkk_price, axis='index')
#combined_df.index.name = 'Date'
#usd_in_dkk_price = usd_in_dkk_price.asfreq = 'D'
#intersect = pd.merge(combined_df, usd_in_dkk_price, how='inner')
intersect = combined_df.merge( usd_in_dkk_price ).dropna()
combined_df_DKK = (combined_df * usd_in_dkk_price).dropna()
combined_df_DKK = combined_df[combined_df.columns].multiply( usd_in_dkk_price, axis=0).dropna()
combined_df_DKK = combined_df.multiply( usd_in_dkk_price, axis='index').dropna()
ctl.df_scatter(combined_df_DKK, 'Cryptocurrency Prices (DKK)', seperate_y_axis=False, y_axis_label='Coin Value (DKK)', scale='log')
ctl.df_scatter(combined_df_DKK, 'Cryptocurrency Prices (DKK)', seperate_y_axis=False, y_axis_label='Coin Value (DKK)')


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
