# NOT DONE...


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
