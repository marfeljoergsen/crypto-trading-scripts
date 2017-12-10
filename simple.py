#!/usr/bin/env python
# ---

# Modified version of: https://blog.patricktriest.com/analyzing-cryptocurrencies-python/

# =============================================================
# Run "jupyter notebook" from shell to get the correct graphs.
# =============================================================

import numpy as np
#import pandas as pd
from lib import crypto_trading_lib as ctl
#import pdb
from plot_settings import *
import time # plotly needs time to switch/open new browser tab
#---
dataDir = 'data/'



# Step 2.2 - Pull Kraken Exchange Pricing Data
# --------------------------------------------
# Pull Kraken BTC price exchange data
btc_usd_price_kraken = ctl.get_quandl_data('BCHARTS/KRAKENUSD', dataDir)

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

btc_usd_datasets = ctl.merge_dfs_on_column( \
    list(exchange_data.values()), \
    list(exchange_data.keys()), 'Weighted Price' )
#print("btc_usd_datasets = ")
#print( btc_usd_datasets.tail() )


# Step 2.5 - Visualize The Pricing Datasets
# -----------------------------------------
# For this, we'll define a helper function to provide a single-line
# command to generate a graph from the dataframe.


# We can now easily generate a graph for the Bitcoin pricing data.
# # Plot all of the BTC exchange prices
#ctl.df_scatter(btc_usd_datasets, 'Bitcoin Price (USD) By Exchange') # NB: NEED TO REMOVE 0-VALUES


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

if usePlotly:
    layout = go.Layout( title='Avg BTC price in USD', xaxis=dict(type='date'),
                        yaxis=dict( title='avg_btc_price_usd') )
    trace_arr = []
    btc_trace = go.Scatter(x=btc_usd_datasets['avg_btc_price_usd'].index,
                           y=btc_usd_datasets['avg_btc_price_usd'],
                           name='avg_btc_price_usd')
    trace_arr.append(btc_trace)
    fig = go.Figure(data=trace_arr, layout=layout)
    if useJupyterNotebook:
        py.iplot(fig)
    else:
        py.plot(fig)
    print("Waiting " + str(plotlyDelay) +
          " seconds for browser to open up figure: avg_btc_price_usd...")
    time.sleep(plotlyDelay)

else:
    plt.plot( btc_usd_datasets.index.to_pydatetime(), btc_usd_datasets['avg_btc_price_usd'] )
    plt.grid(True)
    plt.legend()
    plt.show()
    #pdb.set_trace()


# EUR/USD (BUNDESBANK/BBEX3_D_USD_EUR_BB_AC_000): https://www.quandl.com/data/BUNDESBANK/BBEX3_D_USD_EUR_BB_AC_000-Euro-foreign-exchange-reference-rate-of-the-ECB-EUR-1-USD-United-States
eur_usd_price = ctl.get_quandl_data('BUNDESBANK/BBEX3_D_USD_EUR_BB_AC_000', dataDir)
#eur_usd_price = ctl.get_crypto_data
#ctl.df_scatter(eur_usd_price, 'Price for 1 EUR in USD')


# EUR/DKK (ECB/EURDKK): https://www.quandl.com/data/ECB/EURDKK-EUR-vs-DKK-Foreign-Exchange-Reference-Rate
eur_in_dkk_price = ctl.get_quandl_data('ECB/EURDKK', dataDir)
#eur_in_dkk_price = ctl.get_crypto_data
#ctl.df_scatter(eur_in_dkk_price, 'Price for 1 EUR in DKK')


# Multiplication - to get 1 USD in DKK - historic rates
# =====================================================
print("Converting to DKK")

#usd_in_dkk_price = eur_usd_price * eur_in_dkk_price
usd_in_dkk_price = eur_in_dkk_price / eur_usd_price
if False:
    ctl.df_scatter(usd_in_dkk_price, 'Price for 1 USD in DKK')
#usd_in_dkk_price=usd_in_dkk_price.asfreq('D')

# import IPython; IPython.terminal.debugger.TerminalPdb().set_trace()
btc_in_dkk_price = usd_in_dkk_price.multiply(btc_usd_price_kraken['Weighted Price'], axis='index') # maybe: .dropna()
# ctl.df_scatter(btc_in_dkk_price, 'Bitcoin Price (in DKK)')


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

if True: # write to Excel
    btc_in_dkk_price.to_excel('btc_in_dkk_price.xls')

if True:
    print("Fraction of valid vs invalid values in btc_in_dkk_price: " + str( btc_in_dkk_price['Value'].count() / len(btc_in_dkk_price)) )
    print("Number of NaN's: " + str( btc_in_dkk_price['Value'].isnull().sum() ))

titl = "Historical price for 1 BTC in DKK"
if usePlotly:
    layout = go.Layout( title=titl, xaxis=dict(type='date') )
    btc_trace_arr = []
    btc_trace_arr.append( go.Scatter(x=btc_in_dkk_price.index, y=btc_in_dkk_price['Value']) )
    fig = go.Figure(data=btc_trace_arr, layout=layout)
    if useJupyterNotebook:
        py.iplot(fig)
    else:
        py.plot(fig)
    print("Waiting " + str(plotlyDelay) +
          " seconds for browser to open up figure: btc_in_dkk_price...")
    time.sleep(plotlyDelay)

else:
    #plt.plot( btc_in_dkk_price.index, btc_in_dkk_price )
    plt.plot( btc_in_dkk_price.index.to_pydatetime(), btc_in_dkk_price )
    plt.title(titl)
    plt.grid(True)
    plt.legend()
    plt.show()

# plt.close('all') # Clean up - strictly not required
