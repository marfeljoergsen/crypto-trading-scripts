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

altcoin_data = {} # dict
for altcoin in altcoins:
    coinpair = 'BTC_{}'.format(altcoin)
    crypto_price_df = ctl.get_crypto_data(coinpair, dataDir)
    altcoin_data[altcoin] = crypto_price_df # adding Pandas DF to dict


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

if True:
    btc_in_dkk_price.replace(0, np.nan, inplace=True) # Convert 0's to NaN's
    btc_in_dkk_price.interpolate() # interpolate to remove NaN's
if  False: #True:
    plt.plot( btc_in_dkk_price.index, btc_in_dkk_price )
    plt.title("Historical price for 1 BTC in DKK")
    plt.grid(True)
    plt.legend()
    plt.show()


# Calculate the historical FIAT-currency values for each altcoin.
if False:
    FIAT_curr = 'USD'
    for altcoin in altcoin_data.keys():
        altcoin_data[altcoin]['price'] = \
            altcoin_data[altcoin]['weightedAverage'] * btc_usd_datasets['avg_btc_price_usd']
    # Create a combined dataframe of the price for each cryptocurrency, into single dataframe
    combined_df = ctl.merge_dfs_on_column( list(altcoin_data.values()), list(altcoin_data.keys()), 'price' )
    combined_df['BTC'] = btc_usd_datasets['avg_btc_price_usd'] # Add BTC price to the dataframe
else:
    FIAT_curr = 'DKK'
    for altcoin in altcoin_data.keys():
        altcoin_data[altcoin]['price'] = \
            altcoin_data[altcoin]['weightedAverage'] * btc_usd_datasets['avg_btc_price_usd']
        altcoin_data[altcoin]['price'] = altcoin_data[altcoin]['price'] * usd_in_dkk_price['Value']
    # Create a combined dataframe of the price for each cryptocurrency, into single dataframe
    combined_df = ctl.merge_dfs_on_column( list(altcoin_data.values()), list(altcoin_data.keys()), 'price' )
    combined_df['BTC'] = btc_usd_datasets['avg_btc_price_usd'] * usd_in_dkk_price['Value']

# Chart all of the altocoin prices
if True: # False:
    ctl.df_scatter(combined_df, 'Cryptocurrency Prices (' + FIAT_curr + ')', seperate_y_axis=False, \
            y_axis_label='Coin Value (' + FIAT_curr + ')', scale='log')
    ctl.df_scatter(combined_df, 'Cryptocurrency Prices (' + FIAT_curr + ')', seperate_y_axis=False, \
            y_axis_label='Coin Value (' + FIAT_curr + ')')
# Note that we're using a logarithmic y-axis scale in order to compare
# all of the currencies on the same plot. You are welcome to try out
# different parameters values here (such as scale='linear') to get
# different perspectives on the data.

plt.close('all') # Clean up - strictly not required
