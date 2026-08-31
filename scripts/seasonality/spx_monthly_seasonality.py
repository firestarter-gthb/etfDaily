from pathlib import Path
import pandas as pd
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent

file_path = str(BASE_DIR\data\indices\SPX.csv"

# Read the CSV
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

# Filter for the last 20 years (from 2005-12-01 so we can get Jan 2006 complete returns)
df = df[df.index >= '2005-12-01']

# --- Helper functions ---

# 1. Start of Month (SOM) Returns
df_som = df.groupby([df.index.year, df.index.month]).first()
som_returns = df_som[price_col].pct_change().dropna()
som_returns.index = pd.MultiIndex.from_tuples(
    [(y, m-1) if m > 1 else (y-1, 12) for y, m in som_returns.index],
    names=['Year', 'Month']
)
som_returns = som_returns[som_returns.index.get_level_values('Year') >= 2006]

# 2. Mid-Month (15th to 15th) Returns
df_15th = df[df.index.day >= 15].copy()
df_15th = df_15th.groupby([df_15th.index.year, df_15th.index.month]).first()
mid_returns = df_15th[price_col].pct_change().dropna()
mid_returns.index = pd.MultiIndex.from_tuples(
    [(y, m-1) if m > 1 else (y-1, 12) for y, m in mid_returns.index],
    names=['Year', 'Month']
)
mid_returns = mid_returns[mid_returns.index.get_level_values('Year') >= 2006]

# 3. End of Month (EOM) Returns
df_eom = df.groupby([df.index.year, df.index.month]).last()
eom_returns = df_eom[price_col].pct_change().dropna()
eom_returns.index.names = ['Year', 'Month']
eom_returns = eom_returns[eom_returns.index.get_level_values('Year') >= 2006]

# 4. OpEx to OpEx (3rd Friday) Returns
third_fridays = pd.date_range(start=df.index.min(), end=df.index.max(), freq='WOM-3FRI')
valid_opex_dates = pd.DatetimeIndex([df.index[df.index <= d].max() for d in third_fridays]).dropna()
df_opex = df.loc[valid_opex_dates]
df_opex = df_opex[~df_opex.index.duplicated()]
opex_returns = df_opex[price_col].pct_change().dropna()
opex_years = opex_returns.index.year
opex_months = opex_returns.index.month
new_tuples = [(y, m-1) if m > 1 else (y-1, 12) for y, m in zip(opex_years, opex_months)]
opex_returns.index = pd.MultiIndex.from_tuples(new_tuples, names=['Year', 'Month'])
opex_returns = opex_returns[opex_returns.index.get_level_values('Year') >= 2006]

# --- FILTER FOR MIDTERM YEARS ---
som_returns = som_returns[som_returns.index.get_level_values('Year') % 4 == 2]
mid_returns = mid_returns[mid_returns.index.get_level_values('Year') % 4 == 2]
opex_returns = opex_returns[opex_returns.index.get_level_values('Year') % 4 == 2]

def agg_monthly(returns, name):
    res = []
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    for m in range(1, 13):
        m_rets = returns[returns.index.get_level_values('Month') == m]
        if len(m_rets) == 0: continue
        win_rate = (m_rets > 0).mean() * 100
        avg_ret = m_rets.mean() * 100
        res.append({
            'Maand': months[m-1],
            f'{name} Winstkans': f"{win_rate:.0f}%",
            f'{name} Gem. Rendement': f"{avg_ret:.2f}%"
        })
    return pd.DataFrame(res).set_index('Maand')

som_df = agg_monthly(som_returns, '1e-tot-1e')
mid_df = agg_monthly(mid_returns, '15e-tot-15e')
opex_df = agg_monthly(opex_returns, 'OpEx-tot-OpEx')

final_df = som_df.join(mid_df).join(opex_df)
print(final_df.to_string())
