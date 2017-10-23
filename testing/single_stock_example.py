
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import pyfolio as pf
import empyrical as ep # Common financial risk and performance metrics. Used by zipline and pyfolio. http://quantopian.github.io/empyrical
from pyfolio.utils import (APPROX_BDAYS_PER_MONTH,
                    MM_DISPLAY_UNIT)
import pandas as pd
from collections import OrderedDict

# INSPIRATION FROM: /usr/lib/python3.6/site-packages/pyfolio

#get_ipython().run_line_magic('matplotlib', 'inline')

# silence warnings
#import warnings
#warnings.filterwarnings('ignore')

STAT_FUNCS_PCT = [
    'Annual return',
    'Cumulative returns',
    'Annual volatility',
    'Max drawdown',
    'Daily value at risk',
    'Daily turnover'
]


def show_perf_stats(returns, factor_returns, positions=None,
                    transactions=None, live_start_date=None,
                    bootstrap=False):
    """
    Prints some performance metrics of the strategy.

    - Shows amount of time the strategy has been run in backtest and
      out-of-sample (in live trading).

    - Shows Omega ratio, max drawdown, Calmar ratio, annual return,
      stability, Sharpe ratio, annual volatility, alpha, and beta.

    Parameters
    ----------
    returns : pd.Series
        Daily returns of the strategy, noncumulative.
         - See full explanation in tears.create_full_tear_sheet.
    factor_returns : pd.Series
        Daily noncumulative returns of the benchmark.
         - This is in the same style as returns.
    positions : pd.DataFrame
        Daily net position values.
         - See full explanation in create_full_tear_sheet.
    live_start_date : datetime, optional
        The point in time when the strategy began live trading, after
        its backtest period.
    bootstrap : boolean (optional)
        Whether to perform bootstrap analysis for the performance
        metrics.
         - For more information, see timeseries.perf_stats_bootstrap
    """

    if bootstrap:
        perf_func = pf.timeseries.perf_stats_bootstrap
    else:
        perf_func = pf.timeseries.perf_stats

    perf_stats_all = perf_func(
        returns,
        factor_returns=factor_returns,
        positions=positions,
        transactions=transactions)

    if live_start_date is not None:
        live_start_date = ep.utils.get_utc_timestamp(live_start_date)
        returns_is = returns[returns.index < live_start_date]
        returns_oos = returns[returns.index >= live_start_date]

        positions_is = None
        positions_oos = None
        transactions_is = None
        transactions_oos = None

        if positions is not None:
            positions_is = positions[positions.index < live_start_date]
            positions_oos = positions[positions.index >= live_start_date]
            if transactions is not None:
                transactions_is = transactions[(transactions.index <
                                                live_start_date)]
                transactions_oos = transactions[(transactions.index >
                                                 live_start_date)]

        perf_stats_is = perf_func(
            returns_is,
            factor_returns=factor_returns,
            positions=positions_is,
            transactions=transactions_is)

        perf_stats_oos = perf_func(
            returns_oos,
            factor_returns=factor_returns,
            positions=positions_oos,
            transactions=transactions_oos)

        print('In-sample months: ' +
              str(int(len(returns_is) / APPROX_BDAYS_PER_MONTH)))
        print('Out-of-sample months: ' +
              str(int(len(returns_oos) / APPROX_BDAYS_PER_MONTH)))

        perf_stats = pd.concat(OrderedDict([
            ('In-sample', perf_stats_is),
            ('Out-of-sample', perf_stats_oos),
            ('All', perf_stats_all),
        ]), axis=1)
    else:
        print('Backtest months: ' +
              str(int(len(returns) / APPROX_BDAYS_PER_MONTH)))
        perf_stats = pd.DataFrame(perf_stats_all, columns=['Backtest'])

    for column in perf_stats.columns:
        for stat, value in perf_stats[column].iteritems():
            if stat in STAT_FUNCS_PCT:
                perf_stats.loc[stat, column] = str(np.round(value * 100,
                                                            1)) + '%'

    pf.utils.print_table(perf_stats, fmt='{0:.2f}')


def create_returns_tear_sheet(returns, positions=None,
                              transactions=None,
                              live_start_date=None,
                              cone_std=(1.0, 1.5, 2.0),
                              benchmark_rets=None,
                              bootstrap=False,
                              return_fig=False):
    """
    Generate a number of plots for analyzing a strategy's returns.

    - Fetches benchmarks, then creates the plots on a single figure.
    - Plots: rolling returns (with cone), rolling beta, rolling sharpe,
        rolling Fama-French risk factors, drawdowns, underwater plot, monthly
        and annual return plots, daily similarity plots,
        and return quantile box plot.
    - Will also print the start and end dates of the strategy,
        performance statistics, drawdown periods, and the return range.

    Parameters
    ----------
    returns : pd.Series
        Daily returns of the strategy, noncumulative.
         - See full explanation in create_full_tear_sheet.
    positions : pd.DataFrame, optional
        Daily net position values.
         - See full explanation in create_full_tear_sheet.
    live_start_date : datetime, optional
        The point in time when the strategy began live trading,
        after its backtest period.
    cone_std : float, or tuple, optional
        If float, The standard deviation to use for the cone plots.
        If tuple, Tuple of standard deviation values to use for the cone plots
         - The cone is a normal distribution with this standard deviation
             centered around a linear regression.
    benchmark_rets : pd.Series, optional
        Daily noncumulative returns of the benchmark.
         - This is in the same style as returns.
    bootstrap : boolean (optional)
        Whether to perform bootstrap analysis for the performance
        metrics. Takes a few minutes longer.
    return_fig : boolean, optional
        If True, returns the figure that was plotted on.
    set_context : boolean, optional
        If True, set default plotting style context.
    """

    #myDebug = True # THIS DOES NOT WORK!
    myDebug = False # THIS DOES NOT WORK!

    if benchmark_rets is None:
        benchmark_rets = pf.utils.get_symbol_rets('SPY')

    returns = returns[returns.index > benchmark_rets.index[0]]

    print("Entire data start date: %s" % returns.index[0].strftime('%Y-%m-%d'))
    print("Entire data end date: %s" % returns.index[-1].strftime('%Y-%m-%d'))

    show_perf_stats(returns, benchmark_rets,
                             positions=positions,
                             transactions=transactions,
                             bootstrap=bootstrap,
                             live_start_date=live_start_date)

    if myDebug:
        plt.show()

    print("PLEASE WAIT NOW - BE PATIENT - THIS CAN TAKE A WHILE!!!")
    pf.plotting.show_worst_drawdown_periods(returns)

    if myDebug:
        plt.show()

    # If the strategy's history is longer than the benchmark's, limit strategy
    if returns.index[0] < benchmark_rets.index[0]:
        returns = returns[returns.index > benchmark_rets.index[0]]

    vertical_sections = 13

    if live_start_date is not None:
        vertical_sections += 1
        live_start_date = ep.utils.get_utc_timestamp(live_start_date)

    if bootstrap:
        vertical_sections += 1

    fig = plt.figure(figsize=(14, vertical_sections * 6))
    gs = gridspec.GridSpec(vertical_sections, 3, wspace=0.5, hspace=0.5)
    ax_rolling_returns = plt.subplot(gs[:2, :])

    i = 2
    ax_rolling_returns_vol_match = plt.subplot(gs[i, :],
                                               sharex=ax_rolling_returns)
    i += 1
    ax_rolling_returns_log = plt.subplot(gs[i, :],
                                         sharex=ax_rolling_returns)
    i += 1
    ax_returns = plt.subplot(gs[i, :],
                             sharex=ax_rolling_returns)
    i += 1
    ax_rolling_beta = plt.subplot(gs[i, :], sharex=ax_rolling_returns)
    i += 1
    ax_rolling_volatility = plt.subplot(gs[i, :], sharex=ax_rolling_returns)
    i += 1
    ax_rolling_sharpe = plt.subplot(gs[i, :], sharex=ax_rolling_returns)
    i += 1
    ax_rolling_risk = plt.subplot(gs[i, :], sharex=ax_rolling_returns)
    i += 1
    ax_drawdown = plt.subplot(gs[i, :], sharex=ax_rolling_returns)
    i += 1
    ax_underwater = plt.subplot(gs[i, :], sharex=ax_rolling_returns)
    i += 1
    ax_monthly_heatmap = plt.subplot(gs[i, 0])
    ax_annual_returns = plt.subplot(gs[i, 1])
    ax_monthly_dist = plt.subplot(gs[i, 2])
    i += 1
    ax_return_quantiles = plt.subplot(gs[i, :])
    i += 1

    pf.plotting.plot_rolling_returns(
        returns,
        factor_returns=benchmark_rets,
        live_start_date=live_start_date,
        cone_std=cone_std,
        ax=ax_rolling_returns)
    ax_rolling_returns.set_title(
        'Cumulative returns')

    pf.plotting.plot_rolling_returns(
        returns,
        factor_returns=benchmark_rets,
        live_start_date=live_start_date,
        cone_std=None,
        volatility_match=True,
        legend_loc=None,
        ax=ax_rolling_returns_vol_match)
    ax_rolling_returns_vol_match.set_title(
        'Cumulative returns volatility matched to benchmark')

    pf.plotting.plot_rolling_returns(
        returns,
        factor_returns=benchmark_rets,
        logy=True,
        live_start_date=live_start_date,
        cone_std=cone_std,
        ax=ax_rolling_returns_log)
    ax_rolling_returns_log.set_title(
        'Cumulative returns on logarithmic scale')

    pf.plotting.plot_returns(
        returns,
        live_start_date=live_start_date,
        ax=ax_returns,
    )
    ax_returns.set_title(
        'Returns')

    if myDebug:
        plt.show()


    pf.plotting.plot_rolling_beta(
        returns, benchmark_rets, ax=ax_rolling_beta)

    if myDebug:
        plt.show()

    pf.plotting.plot_rolling_volatility(
        returns, factor_returns=benchmark_rets, ax=ax_rolling_volatility)

    if myDebug:
        plt.show()

    pf.plotting.plot_rolling_sharpe(
        returns, ax=ax_rolling_sharpe)

    if myDebug:
        plt.show()

    pf.plotting.plot_rolling_fama_french(
        returns, ax=ax_rolling_risk)

    if myDebug:
        plt.show()

    # Drawdowns
    pf.plotting.plot_drawdown_periods(
        returns, top=5, ax=ax_drawdown)

    if myDebug:
        plt.show()

    pf.plotting.plot_drawdown_underwater(
        returns=returns, ax=ax_underwater)

    if myDebug:
        plt.show()

    pf.plotting.plot_monthly_returns_heatmap(returns, ax=ax_monthly_heatmap)
    pf.plotting.plot_annual_returns(returns, ax=ax_annual_returns)
    pf.plotting.plot_monthly_returns_dist(returns, ax=ax_monthly_dist)

    if myDebug:
        plt.show()

    pf.plotting.plot_return_quantiles(
        returns,
        live_start_date=live_start_date,
        ax=ax_return_quantiles)

    if myDebug:
        plt.show()

    if bootstrap:
        ax_bootstrap = plt.subplot(gs[i, :])
        pf.plotting.plot_perf_stats(returns, benchmark_rets,
                                 ax=ax_bootstrap)

    for ax in fig.axes:
        plt.setp(ax.get_xticklabels(), visible=True)

    plt.show()
    if return_fig:
        return fig


# t = np.arange(0.0, 2.0, 0.01)
# s = 1 + np.sin(2 * np.pi * t)
# plt.plot(t, s)
#
# plt.xlabel('time (s)')
# plt.ylabel('voltage (mV)')
# plt.title('About as simple as it gets, folks')
# plt.grid(True)
# # plt.savefig("test.png")
# plt.show()

print("Executing: stock_rets = pf.utils.get_symbol_rets('FB')")
stock_rets = pf.utils.get_symbol_rets('FB')
#plt.show()

# pf.timeseries.cum_returns(stock_rets).plot()

# ## Create a returns tear sheet for the single stock
# This will show charts and analysis about returns of the single stock.
print("Please wait: pf.create_returns_tear_sheet(stock_rets, live_start_date='2015-12-1') - WAIT PLEASE!")
create_returns_tear_sheet(stock_rets, live_start_date='2015-12-1')

print("done")
