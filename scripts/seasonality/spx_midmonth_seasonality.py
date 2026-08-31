from pathlib import Path
import pandas as pd
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent

file_path = str(BASE_DIR\data\indices\SPX.csv"

# Read the CSV, handling the yfinance multi-header format
try:
    df = pd.read_csv(file_path, skiprows=[1, 2], index_col=0, parse_dates=True)
except Exception:
    df = pd.read_csv(file_path, index_col=0, parse_dates=True)

df.index = pd.to_datetime(df.index)

# Flatten columns if multi-index
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

price_col = 'Adj Close' if 'Adj Close' in df.columns else 'Close'

if price_col not in df.columns:
    price_col = df.columns[0]
    
df[price_col] = pd.to_numeric(df[price_col], errors='coerce')
df.dropna(subset=[price_col], inplace=True)

# 1. 15th to 15th Returns
# Get all dates that are on or after the 15th
df_15th = df[df.index.day >= 15].copy()
# Group by year and month, and pick the first observation (which will be the 15th, or the first trading day after)
df_15th_monthly = df_15th.groupby([df_15th.index.year, df_15th.index.month]).first()
mid_month_returns = df_15th_monthly[price_col].pct_change().dropna()

# 2. Standard Monthly Returns (End of Month to End of Month)
# Pick the last observation of each month
df_eom = df.groupby([df.index.year, df.index.month]).last()
eom_returns = df_eom[price_col].pct_change().dropna()

# 3. 1st to 1st Returns (Start of month to start of month)
df_1st = df.groupby([df.index.year, df.index.month]).first()
som_returns = df_1st[price_col].pct_change().dropna()

def analyze_returns(returns, name):
    win_rate = (returns > 0).mean() * 100
    avg_return = returns.mean() * 100
    median_return = returns.median() * 100
    best = returns.max() * 100
    worst = returns.min() * 100
    annualized_vol = returns.std() * np.sqrt(12) * 100
    total_months = len(returns)
    
    return {
        'Period': name,
        'Win Rate': f"{win_rate:.1f}%",
        'Avg Return': f"{avg_return:.2f}%",
        'Median Return': f"{median_return:.2f}%",
        'Best': f"{best:.2f}%",
        'Worst': f"{worst:.2f}%",
        'Ann. Volatility': f"{annualized_vol:.2f}%",
        'N Months': total_months
    }

print(f"Data period: {df.index[0].date()} to {df.index[-1].date()} ({len(df)} days)")
print("\n--- All Time Performance ---")
res_all = [
    analyze_returns(som_returns, "1st to 1st (Start of Month)"),
    analyze_returns(mid_month_returns, "15th to 15th (Mid-Month)"),
    analyze_returns(eom_returns, "EOM to EOM (End of Month)")
]
print(pd.DataFrame(res_all).to_string(index=False))

print("\n--- Modern Era (Since 1990) ---")
recent_year = 1990
res_recent = [
    analyze_returns(som_returns[som_returns.index.get_level_values(0) >= recent_year], "1st to 1st"),
    analyze_returns(mid_month_returns[mid_month_returns.index.get_level_values(0) >= recent_year], "15th to 15th"),
    analyze_returns(eom_returns[eom_returns.index.get_level_values(0) >= recent_year], "EOM to EOM")
]
print(pd.DataFrame(res_recent).to_string(index=False))
