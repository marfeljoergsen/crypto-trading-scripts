
import pyfolio as pf
#get_ipython().run_line_magic('matplotlib', 'inline')

# silence warnings
#import warnings
#warnings.filterwarnings('ignore')

stock_rets = pf.utils.get_symbol_rets('FB')

# ## Create a returns tear sheet for the single stock
# This will show charts and analysis about returns of the single stock.
pf.create_returns_tear_sheet(stock_rets, live_start_date='2015-12-1')

