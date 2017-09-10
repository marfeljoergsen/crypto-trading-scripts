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
import time # plotly needs time to switch/open new browser tab
#import pdb

#---
dataDir = 'data/'
altcoinsFile = 'altcoins.txt'

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

if False:
    altcoins = ['ETH','LTC','XRP','ETC','STR','DASH','SC','XMR','XEM']
else:
    with open(altcoinsFile) as f:
        altcoins = f.read().splitlines()
print("Downloading data for these altcoins: ",  altcoins)

altcoin_data = {} # dict
for altcoin in altcoins:
    coinpair = 'BTC_{}'.format(altcoin)
    crypto_price_df = ctl.get_crypto_data(coinpair, dataDir)
    altcoin_data[altcoin] = crypto_price_df # adding Pandas DF to dict


if not usePlotly:
    plt.close('all')

print("Converting to DKK")
eur_usd_price = ctl.get_quandl_data('BUNDESBANK/BBEX3_D_USD_EUR_BB_AC_000', dataDir)
eur_in_dkk_price = ctl.get_quandl_data('ECB/EURDKK', dataDir)
usd_in_dkk_price = eur_in_dkk_price / eur_usd_price

if False:
    ctl.df_scatter(usd_in_dkk_price, 'Price for 1 USD in DKK')
if False:
    plt.plot( usd_in_dkk_price.index, usd_in_dkk_price )
    plt.title("1 USD in DKK")
    plt.grid(True)
    plt.legend()
    plt.show()

btc_in_dkk_price = usd_in_dkk_price.multiply(btc_usd_price_kraken['Weighted Price'], axis='index') # maybe: .dropna()

if False: # True:
    titl = "Historical price for 1 BTC in DKK"
    if usePlotly:
        layout = go.Layout( title=titl, xaxis=dict(type='date'),
                            yaxis=dict( title='1 BTC Price in DKK') )
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
              " seconds for browser to open up figure: " + titl )
        time.sleep(plotlyDelay)

    else:
        plt.plot( btc_in_dkk_price.index, btc_in_dkk_price )
        plt.title(titl)
        plt.grid(True)
        plt.legend()
        plt.show()

if True: # Print stats
    print("="*50)
    print("btc_in_dkk_price.first_valid_index() = " + str(btc_in_dkk_price.first_valid_index()))
    print("btc_in_dkk_price.last_valid_index() = " + str(btc_in_dkk_price.last_valid_index()))
    print("Fraction of valid vs invalid values in btc_in_dkk_price: " + str( btc_in_dkk_price['Value'].count() / len(btc_in_dkk_price)) )
    print("Number of NaN's: " + str( btc_in_dkk_price['Value'].isnull().sum() ))
    print("Number of 0's: " + str( sum(btc_in_dkk_price['Value'] == 0 )))

if True: # remove invalid indices:
    btc_in_dkk_price = btc_in_dkk_price[ btc_in_dkk_price['Value'].notnull() ] # remove unused indices
    print("Number of 0'values (to be replaced with NaN): " + str(np.sum( btc_in_dkk_price['Value']==0 )) )
    btc_in_dkk_price.replace(0, np.nan, inplace=True) # replace 0 with NaN
    print("Number of 0'values: " + str(np.sum( btc_in_dkk_price['Value']==0 )) )

if True: # Remove NaN-values:
    print("  *** WARNING: Removing NaN-values by interpolation! ***")
    print("Number of NaN values: " + str(np.sum( np.isnan( btc_in_dkk_price['Value'] )) ) )
    btc_in_dkk_price = btc_in_dkk_price.interpolate() # interpolate to remove NaN's
    print("Number of NaN values: " + str(np.sum( np.isnan( btc_in_dkk_price['Value'] )) ) )

if True: # Print stats again
    print("Fraction of valid vs invalid values in btc_in_dkk_price: " + str( btc_in_dkk_price['Value'].count() / len(btc_in_dkk_price)) )
    print("Number of NaN's: " + str( btc_in_dkk_price['Value'].isnull().sum() ))
    print("Number of 0'values: " + str(np.sum( btc_in_dkk_price['Value']==0 )) )

if False: #True: # write to Excel
    btc_in_dkk_price.to_excel('btc_in_dkk_price.xls')


# Calculate the historical FIAT-currency values for each altcoin.
if False:
    FIAT_curr = 'USD'
    for altcoin in altcoin_data.keys():
        altcoin_data[altcoin]['price'] = \
            altcoin_data[altcoin]['weightedAverage'] * btc_usd_datasets['avg_btc_price_usd']
        if False: # True: # Drop NaN!
            altcoin_data[altcoin]['price'] = altcoin_data[altcoin]['price'].dropna()
    # Create a combined dataframe of the price for each cryptocurrency, into single dataframe
    combined_df = ctl.merge_dfs_on_column( list(altcoin_data.values()), list(altcoin_data.keys()), 'price' )
    combined_df['BTC'] = btc_usd_datasets['avg_btc_price_usd'] # Add BTC price to the dataframe
else:
    FIAT_curr = 'DKK'
    for altcoin in altcoin_data.keys():
        altcoin_data[altcoin]['price'] = \
            altcoin_data[altcoin]['weightedAverage'] * btc_usd_datasets['avg_btc_price_usd']
        altcoin_data[altcoin]['price'] = altcoin_data[altcoin]['price'] * usd_in_dkk_price['Value']
        if False: #True: # Drop NaN!
            altcoin_data[altcoin]['price'] = altcoin_data[altcoin]['price'].dropna()
    # Create a combined dataframe of the price for each cryptocurrency, into single dataframe
    combined_df = ctl.merge_dfs_on_column( list(altcoin_data.values()), list(altcoin_data.keys()), 'price' )
    combined_df['BTC'] = btc_usd_datasets['avg_btc_price_usd'] * usd_in_dkk_price['Value']


# Chart all of the altocoin prices
if True: # False:
    ctl.df_scatter(combined_df, 'Cryptocurrency Prices - y-LOG (' + FIAT_curr + ')', seperate_y_axis=False, \
                   y_axis_label='Coin Value (' + FIAT_curr + ')', scale='log', connGaps=True)
    ctl.df_scatter(combined_df, 'Cryptocurrency Prices - y-Linear (' + FIAT_curr + ')', seperate_y_axis=False, \
                   y_axis_label='Coin Value (' + FIAT_curr + ')', connGaps=True)
# Note that we're using a logarithmic y-axis scale in order to compare
# all of the currencies on the same plot. You are welcome to try out
# different parameters values here (such as scale='linear') to get
# different perspectives on the data.
