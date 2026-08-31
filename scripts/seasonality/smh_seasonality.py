import pandas as pd
import numpy as np
import yfinance as yf
import calendar

print("Downloading SMH data...")
data = yf.download("SMH", period="max", progress=False)
df = data.copy()
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.droplevel(1)
df.index = pd.to_datetime(df.index)
close_col = 'Adj Close' if 'Adj Close' in df.columns else 'Close'

# Monthly (1st to 1st)
monthly = df[close_col].resample('ME').last()
monthly_ret = monthly.pct_change().dropna()

df_monthly = pd.DataFrame({'Return': monthly_ret})
df_monthly['Month'] = df_monthly.index.month
df_monthly['Year'] = df_monthly.index.year

midterm_years = [2002, 2006, 2010, 2014, 2018, 2022, 2026]

# Function to calc stats
def get_stats(data_series):
    if len(data_series) == 0:
        return 0, 0
    win = (data_series > 0).mean() * 100
    avg = data_series.mean() * 100
    return win, avg

print("MONTH | ALL_WIN | ALL_AVG | MIDTERM_WIN | MIDTERM_AVG")
for m in range(1, 13):
    m_data = df_monthly[df_monthly['Month'] == m]
    all_w, all_a = get_stats(m_data['Return'])
    
    mid_data = m_data[m_data['Year'].isin(midterm_years)]
    mid_w, mid_a = get_stats(mid_data['Return'])
    
    print(f"{calendar.month_abbr[m]:<5} | {all_w:>6.1f}% | {all_a:>6.2f}% | {mid_w:>10.1f}% | {mid_a:>10.2f}%")

print("\n--- MIDTERM 15th to 15th (Mid-Month) ---")
# Find the closest trading day to the 15th of each month
df['Day'] = df.index.day
df['Month'] = df.index.month
df['Year'] = df.index.year

mid_month_prices = []
for year in df['Year'].unique():
    for month in range(1, 13):
        mask = (df['Year'] == year) & (df['Month'] == month)
        if mask.any():
            month_data = df[mask].copy()
            month_data['dist'] = abs(month_data['Day'] - 15)
            closest = month_data.sort_values('dist').iloc[0]
            mid_month_prices.append({'Date': closest.name, 'Price': closest[close_col]})

mid_df = pd.DataFrame(mid_month_prices).set_index('Date')
mid_ret = mid_df['Price'].pct_change().dropna()

mid_ret_df = pd.DataFrame({'Return': mid_ret})
mid_ret_df['StartMonth'] = mid_ret_df.index.month
mid_ret_df['Year'] = mid_ret_df.index.year

print("START_MONTH | MIDTERM_15_WIN | MIDTERM_15_AVG")
for m in range(1, 13):
    m_data = mid_ret_df[(mid_ret_df['StartMonth'] == m) & (mid_ret_df['Year'].isin(midterm_years))]
    w, a = get_stats(m_data['Return'])
    print(f"{calendar.month_abbr[m]:<11} | {w:>13.1f}% | {a:>13.2f}%")
