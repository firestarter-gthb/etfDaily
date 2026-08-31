from pathlib import Path
import pandas as pd
import numpy as np
import warnings

BASE_DIR = Path(__file__).resolve().parent.parent
warnings.filterwarnings('ignore')

# Load data
file_path = str(BASE_DIR\data\indices\MSCI_World.csv"
# The CSV has 3 header rows (Price..., Ticker..., Date...)
# We can skip the Ticker and Date rows (indices 1 and 2)
df = pd.read_csv(file_path, skiprows=[1, 2], index_col=0, parse_dates=True)
df.index.name = 'Date'

# Flatten columns if multi-index (yfinance new format)
if isinstance(df.columns, pd.MultiIndex):
    # Take the first level if multi-index
    df.columns = df.columns.get_level_values(0)

# Identify the price column
price_col = 'Adj Close' if 'Adj Close' in df.columns else 'Close'

# Check if price_col exists, if not, maybe it's named differently
if price_col not in df.columns:
    print(f"Available columns: {df.columns}")
    price_col = df.columns[0] # Fallback to first column

# Ensure price is numeric
df[price_col] = pd.to_numeric(df[price_col], errors='coerce')
df.dropna(subset=[price_col], inplace=True)

# Calculate MAs
df['SMA_5'] = df[price_col].rolling(window=5).mean()
df['SMA_50'] = df[price_col].rolling(window=50).mean()
df['SMA_100'] = df[price_col].rolling(window=100).mean()
df['SMA_200'] = df[price_col].rolling(window=200).mean()

# Calculate daily returns
df['Daily_Return'] = df[price_col].pct_change()

# Define positions (shifted by 1 to prevent look-ahead bias)
# If signal is True today, we hold the position tomorrow
df['Pos_BnH'] = 1
df['Pos_SMA_5'] = (df[price_col] > df['SMA_5']).astype(int).shift(1)
df['Pos_SMA_100'] = (df[price_col] > df['SMA_100']).astype(int).shift(1)
df['Pos_SMA_200'] = (df[price_col] > df['SMA_200']).astype(int).shift(1)
df['Pos_Golden_Cross'] = (df['SMA_50'] > df['SMA_200']).astype(int).shift(1)

# Drop NaNs to have a fair comparison from the point where 200 SMA is available
df_test = df.dropna(subset=['SMA_200'])

strategies = {
    'Buy and Hold': 'Pos_BnH',
    'Price > 5 MA': 'Pos_SMA_5',
    'Price > 100 MA': 'Pos_SMA_100',
    'Price > 200 MA': 'Pos_SMA_200',
    'Golden Cross (50>200 MA)': 'Pos_Golden_Cross'
}

results = []

years = (df_test.index[-1] - df_test.index[0]).days / 365.25

for name, pos_col in strategies.items():
    strat_returns = df_test['Daily_Return'] * df_test[pos_col]
    
    # Cumulative return
    cum_returns = (1 + strat_returns).cumprod()
    total_return = cum_returns.iloc[-1] - 1
    
    # CAGR
    cagr = (cum_returns.iloc[-1] ** (1 / years)) - 1
    
    # Max Drawdown
    roll_max = cum_returns.cummax()
    drawdown = (cum_returns - roll_max) / roll_max
    max_dd = drawdown.min()
    
    # Sharpe Ratio (annualized)
    sharpe = np.sqrt(252) * strat_returns.mean() / strat_returns.std()
    
    results.append({
        'Strategy': name,
        'Total Return': f"{total_return*100:.2f}%",
        'CAGR': f"{cagr*100:.2f}%",
        'Max Drawdown': f"{max_dd*100:.2f}%",
        'Sharpe Ratio': f"{sharpe:.2f}"
    })

results_df = pd.DataFrame(results)
print(f"Data period: {df_test.index[0].date()} to {df_test.index[-1].date()} ({years:.1f} years)\n")
print(results_df.to_string(index=False))
