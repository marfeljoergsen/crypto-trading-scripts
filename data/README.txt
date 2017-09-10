Place for downloaded - temporary files...

=========== QUANDL (file extension is ".pkl")  ===========
# ("Quandl Code ID" search e.g.: https://www.quandl.com/search?query= )
btc_usd_price_kraken = ctl.get_quandl_data('BCHARTS/KRAKENUSD', dataDir)
eur_usd_price = ctl.get_quandl_data('BUNDESBANK/BBEX3_D_USD_EUR_BB_AC_000', dataDir)


=========== Poloniex API (file extension is ".pkl")  ===========
crypto_price_df = ctl.get_crypto_data(coinpair, dataDir)
==>
    json_url = base_polo_url.format(poloniex_pair, start_date.timestamp(), end_date.timestamp(), pediod)
    data_df = get_json_data(json_url, dataDir + poloniex_pair)
    data_df = data_df.set_index('date')
