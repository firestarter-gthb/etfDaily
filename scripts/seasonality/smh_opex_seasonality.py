import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import calendar

print("Downloading SMH data...")
data = yf.download("SMH", period="max", progress=False)
df = data.copy()
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.droplevel(1)
df.index = pd.to_datetime(df.index)
close_col = 'Adj Close' if 'Adj Close' in df.columns else 'Close'

# Find 3rd Friday of every month
def get_3rd_friday(year, month):
    d = datetime(year, month, 1)
    while d.weekday() != 4:
        d += timedelta(days=1)
    d += timedelta(days=14)
    return pd.Timestamp(d)

min_year = df.index.min().year
max_year = df.index.max().year

opex_dates = []
for y in range(min_year, max_year + 1):
    for m in range(1, 13):
        try:
            opex = get_3rd_friday(y, m)
            # Find the closest trading day on or before OpEx
            valid_dates = df.index[df.index <= opex]
            if len(valid_dates) > 0:
                actual_opex = valid_dates[-1]
                # Ensure the found date is actually in the correct month/year context
                if actual_opex >= df.index[0]:
                    opex_dates.append({
                        'Year': y,
                        'StartMonth': m,
                        'Date': actual_opex,
                        'Price': df.loc[actual_opex, close_col]
                    })
        except ValueError:
            pass

opex_df = pd.DataFrame(opex_dates)
# Calculate return to NEXT opex
opex_df['Return'] = opex_df['Price'].pct_change().shift(-1)
opex_df = opex_df.dropna()

midterm_years = [2002, 2006, 2010, 2014, 2018, 2022, 2026]

print("\n--- MIDTERM OPEX TO OPEX (e.g. 'Oct' = Oct OpEx to Nov OpEx) ---")
print("START_MONTH | WIN_RATE | AVG_RETURN")

for m in range(1, 13):
    m_data = opex_df[(opex_df['StartMonth'] == m) & (opex_df['Year'].isin(midterm_years))]
    if len(m_data) > 0:
        win = (m_data['Return'] > 0).mean() * 100
        avg = m_data['Return'].mean() * 100
        print(f"{calendar.month_abbr[m]:<11} | {win:>7.1f}% | {avg:>9.2f}%")
