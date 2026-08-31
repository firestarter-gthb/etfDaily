"""
Verification script for Annual Seasonality calculations.
Compares Calendar (EOM-to-EOM) vs OpEx (3rd Friday to 3rd Friday) returns.
Shows detailed breakdowns so we can manually verify the numbers.
"""
import pandas as pd
import yfinance as yf
import numpy as np
import datetime
import calendar
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# 1. Download data
# ============================================================
tickers = ["SPY", "QQQ", "SMH"]
data = yf.download(tickers, start="2002-01-01", progress=False)['Close'].dropna()
print(f"Data range: {data.index.min().date()} to {data.index.max().date()}")
print(f"Total trading days: {len(data)}")
print()

# ============================================================
# 2. CALENDAR-BASED SEASONALITY (EOM-to-EOM)
# ============================================================
print("=" * 80)
print("PART 1: CALENDAR-BASED SEASONALITY (End-of-Month to End-of-Month)")
print("=" * 80)

cal_results = {}
for ticker in tickers:
    price_series = data[ticker]
    monthly_prices = price_series.resample('ME').last()
    monthly_returns = monthly_prices.pct_change().dropna() * 100
    
    df_ret = pd.DataFrame({'Return': monthly_returns})
    df_ret['Month'] = df_ret.index.month
    df_ret['Year'] = df_ret.index.year
    
    print(f"\n--- {ticker} Calendar Returns (sample: last 3 years) ---")
    recent = df_ret[df_ret['Year'] >= 2024].copy()
    recent['MonthName'] = recent['Month'].apply(lambda m: calendar.month_abbr[m])
    print(recent[['Year', 'MonthName', 'Return']].to_string(index=False))
    
    month_stats = []
    for m in range(1, 13):
        m_data = df_ret[df_ret['Month'] == m]['Return']
        n_obs = len(m_data)
        win_rate = (m_data > 0).mean() * 100
        avg_ret = m_data.mean()
        month_stats.append({
            'Month': calendar.month_abbr[m],
            'N': n_obs,
            'WinRate': round(win_rate, 1),
            'AvgRet': round(avg_ret, 2)
        })
    cal_results[ticker] = pd.DataFrame(month_stats).set_index('Month')

print("\n\n--- CALENDAR SEASONALITY SUMMARY ---")
for ticker in tickers:
    print(f"\n{ticker}:")
    print(cal_results[ticker].to_string())


# ============================================================
# 3. OPEX-BASED SEASONALITY (3rd Friday to 3rd Friday)
# ============================================================
print("\n\n" + "=" * 80)
print("PART 2: OPEX-BASED SEASONALITY (3rd Friday to 3rd Friday)")
print("=" * 80)

def get_3rd_friday(year, month):
    """Calculate the 3rd Friday of a given month/year."""
    d = datetime.date(year, month, 1)
    # Find first Friday
    while d.weekday() != 4:
        d += datetime.timedelta(days=1)
    # Add 2 weeks to get 3rd Friday
    d += datetime.timedelta(days=14)
    return pd.Timestamp(d)

# First, let's verify the 3rd Friday calculation for a few known dates
print("\n--- Verification of 3rd Friday calculation ---")
test_cases = [
    (2024, 1, "Jan 2024 -> should be Jan 19"),
    (2024, 3, "Mar 2024 -> should be Mar 15"),
    (2024, 6, "Jun 2024 -> should be Jun 21"),
    (2024, 9, "Sep 2024 -> should be Sep 20"),
    (2024, 12, "Dec 2024 -> should be Dec 20"),
    (2025, 8, "Aug 2025 -> should be Aug 15"),
    (2026, 1, "Jan 2026 -> should be Jan 16"),
]
for y, m, desc in test_cases:
    f3 = get_3rd_friday(y, m)
    dow = f3.strftime('%A')
    print(f"  {desc} => Calculated: {f3.date()} ({dow})")

opex_results = {}
for ticker in tickers:
    price_series = data[ticker]
    min_year = price_series.index.min().year
    max_year = price_series.index.max().year
    
    opex_prices = []
    for y in range(min_year, max_year + 1):
        for m in range(1, 13):
            target_opex = get_3rd_friday(y, m)
            # Find the closest trading day on or before the 3rd Friday
            valid = price_series.index[price_series.index <= target_opex]
            if len(valid) > 0 and valid[-1] >= price_series.index[0]:
                actual_date = valid[-1]
                opex_prices.append({
                    'Year': y,
                    'Month': m,
                    'TargetOpEx': target_opex.date(),
                    'ActualDate': actual_date.date(),
                    'Price': price_series.loc[actual_date]
                })
    
    df_opex = pd.DataFrame(opex_prices)
    
    # Show the actual dates being used (sample)
    print(f"\n--- {ticker} OpEx Anchor Dates (sample: 2024-2026) ---")
    recent = df_opex[df_opex['Year'] >= 2024].copy()
    recent['MonthName'] = recent['Month'].apply(lambda m: calendar.month_abbr[m])
    print(recent[['Year', 'MonthName', 'TargetOpEx', 'ActualDate', 'Price']].to_string(index=False))
    
    # Calculate returns: return for "month M" = price at OpEx(M) / price at OpEx(M-1) - 1
    # shift(-1) means: for row M, the return is from OpEx(M) to OpEx(M+1)
    # But we want: for "month M", the return from OpEx(M-1) to OpEx(M)
    # So we should use regular pct_change() and assign the return to the current month
    df_opex['Return'] = df_opex['Price'].pct_change() * 100
    df_opex = df_opex.dropna(subset=['Return'])
    
    # Show returns for recent years
    print(f"\n--- {ticker} OpEx Returns (sample: 2024-2026) ---")
    recent_ret = df_opex[df_opex['Year'] >= 2024].copy()
    recent_ret['MonthName'] = recent_ret['Month'].apply(lambda m: calendar.month_abbr[m])
    print(recent_ret[['Year', 'MonthName', 'ActualDate', 'Price', 'Return']].to_string(index=False))
    
    month_stats = []
    for m in range(1, 13):
        m_data = df_opex[df_opex['Month'] == m]['Return']
        n_obs = len(m_data)
        win_rate = (m_data > 0).mean() * 100
        avg_ret = m_data.mean()
        month_stats.append({
            'Month': calendar.month_abbr[m],
            'N': n_obs,
            'WinRate': round(win_rate, 1),
            'AvgRet': round(avg_ret, 2)
        })
    opex_results[ticker] = pd.DataFrame(month_stats).set_index('Month')

print("\n\n--- OPEX SEASONALITY SUMMARY ---")
for ticker in tickers:
    print(f"\n{ticker}:")
    print(opex_results[ticker].to_string())

# ============================================================
# 4. SIDE-BY-SIDE COMPARISON
# ============================================================
print("\n\n" + "=" * 80)
print("PART 3: SIDE-BY-SIDE COMPARISON")
print("=" * 80)

for ticker in tickers:
    print(f"\n--- {ticker} ---")
    comp = pd.DataFrame({
        'Cal_N': cal_results[ticker]['N'],
        'Cal_WR': cal_results[ticker]['WinRate'],
        'Cal_Ret': cal_results[ticker]['AvgRet'],
        'OpEx_N': opex_results[ticker]['N'],
        'OpEx_WR': opex_results[ticker]['WinRate'],
        'OpEx_Ret': opex_results[ticker]['AvgRet'],
        'Diff_Ret': opex_results[ticker]['AvgRet'] - cal_results[ticker]['AvgRet']
    })
    print(comp.to_string())

# ============================================================
# 5. SANITY CHECK: Verify the OpEx return interpretation
# ============================================================
print("\n\n" + "=" * 80)
print("PART 4: SANITY CHECK - What does 'OpEx Month X' actually measure?")
print("=" * 80)
print("""
IMPORTANT: The OpEx return for 'Month M' represents:
  - The return from the 3rd Friday of month (M-1) to the 3rd Friday of month M.
  
For example, 'OpEx August' = return from 3rd Friday of JULY to 3rd Friday of AUGUST.

This means:
  - OpEx January  = Dec OpEx -> Jan OpEx  (mid-Dec to mid-Jan)
  - OpEx February = Jan OpEx -> Feb OpEx  (mid-Jan to mid-Feb)
  - OpEx August   = Jul OpEx -> Aug OpEx  (mid-Jul to mid-Aug)
  - OpEx September = Aug OpEx -> Sep OpEx (mid-Aug to mid-Sep)
  - OpEx October  = Sep OpEx -> Oct OpEx  (mid-Sep to mid-Oct)
""")

# Show a concrete example
ticker = 'SPY'
price_series = data[ticker]
print(f"Concrete Example for {ticker} in 2024:")
for m in range(7, 11):  # Jul-Oct
    f3 = get_3rd_friday(2024, m)
    valid = price_series.index[price_series.index <= f3]
    actual = valid[-1]
    price = price_series.loc[actual]
    print(f"  3rd Friday {calendar.month_abbr[m]} 2024: target={f3.date()}, actual={actual.date()}, price={price:.2f}")

# Calculate returns manually
for m in range(8, 11):
    f3_prev = get_3rd_friday(2024, m-1)
    f3_curr = get_3rd_friday(2024, m)
    valid_prev = price_series.index[price_series.index <= f3_prev]
    valid_curr = price_series.index[price_series.index <= f3_curr]
    p_prev = price_series.loc[valid_prev[-1]]
    p_curr = price_series.loc[valid_curr[-1]]
    ret = (p_curr / p_prev - 1) * 100
    print(f"  OpEx {calendar.month_abbr[m]} 2024 return = ({p_curr:.2f} / {p_prev:.2f} - 1) = {ret:.2f}%")
    print(f"    This measures: {valid_prev[-1].date()} to {valid_curr[-1].date()}")
