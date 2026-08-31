"""
CORRECTED OpEx-to-OpEx seasonality calculation.
Fixes:
1. Uses pct_change() (not shift(-1)) so returns are assigned to the correct month
2. Filters out future dates to avoid zero-return contamination
"""
import pandas as pd
import yfinance as yf
import numpy as np
import datetime
import calendar
import warnings
warnings.filterwarnings('ignore')

tickers = ["SPY", "QQQ", "SMH"]
data = yf.download(tickers, start="2002-01-01", progress=False)['Close'].dropna()
max_data_date = data.index.max()
print(f"Data range: {data.index.min().date()} to {max_data_date.date()}")

def get_3rd_friday(year, month):
    d = datetime.date(year, month, 1)
    while d.weekday() != 4:
        d += datetime.timedelta(days=1)
    d += datetime.timedelta(days=14)
    return pd.Timestamp(d)

# ============================================================
# CALENDAR-BASED (for comparison, unchanged)
# ============================================================
print("\n" + "=" * 70)
print("CALENDAR-BASED SEASONALITY (EOM to EOM)")
print("=" * 70)

for ticker in tickers:
    price_series = data[ticker]
    monthly_prices = price_series.resample('ME').last()
    monthly_returns = monthly_prices.pct_change().dropna() * 100
    df_ret = pd.DataFrame({'Return': monthly_returns})
    df_ret['Month'] = df_ret.index.month

    print(f"\n{ticker}:")
    print(f"{'Month':<6} {'N':>4} {'WinRate':>8} {'AvgRet':>8}")
    for m in range(1, 13):
        m_data = df_ret[df_ret['Month'] == m]['Return']
        n = len(m_data)
        wr = (m_data > 0).mean() * 100
        ar = m_data.mean()
        print(f"{calendar.month_abbr[m]:<6} {n:>4} {wr:>7.1f}% {ar:>7.2f}%")

# ============================================================
# OPEX-BASED (CORRECTED)
# ============================================================
print("\n" + "=" * 70)
print("OPEX-BASED SEASONALITY (3rd Friday to 3rd Friday) - CORRECTED")
print("=" * 70)

for ticker in tickers:
    price_series = data[ticker]
    min_year = price_series.index.min().year
    max_year = price_series.index.max().year

    opex_prices = []
    for y in range(min_year, max_year + 1):
        for m in range(1, 13):
            target_opex = get_3rd_friday(y, m)
            # CRITICAL: Skip if target OpEx is in the future
            if target_opex > max_data_date:
                continue
            valid = price_series.index[price_series.index <= target_opex]
            if len(valid) > 0:
                actual_date = valid[-1]
                opex_prices.append({
                    'Year': y,
                    'Month': m,
                    'Price': price_series.loc[actual_date]
                })

    df_opex = pd.DataFrame(opex_prices)
    # Return for month M = price at OpEx(M) / price at OpEx(M-1) - 1
    # This is correctly assigned by pct_change() to month M
    df_opex['Return'] = df_opex['Price'].pct_change() * 100
    df_opex = df_opex.dropna(subset=['Return'])

    print(f"\n{ticker}:")
    print(f"{'Month':<6} {'N':>4} {'WinRate':>8} {'AvgRet':>8}")
    for m in range(1, 13):
        m_data = df_opex[df_opex['Month'] == m]['Return']
        n = len(m_data)
        wr = (m_data > 0).mean() * 100
        ar = m_data.mean()
        print(f"{calendar.month_abbr[m]:<6} {n:>4} {wr:>7.1f}% {ar:>7.2f}%")

# ============================================================
# SIDE-BY-SIDE for easy comparison
# ============================================================
print("\n" + "=" * 70)
print("SIDE-BY-SIDE: Calendar vs OpEx (Corrected)")
print("=" * 70)

for ticker in tickers:
    price_series = data[ticker]
    
    # Calendar
    monthly_prices = price_series.resample('ME').last()
    monthly_returns = monthly_prices.pct_change().dropna() * 100
    df_cal = pd.DataFrame({'Return': monthly_returns})
    df_cal['Month'] = df_cal.index.month
    
    # OpEx
    min_year = price_series.index.min().year
    max_year = price_series.index.max().year
    opex_prices = []
    for y in range(min_year, max_year + 1):
        for m in range(1, 13):
            target_opex = get_3rd_friday(y, m)
            if target_opex > max_data_date:
                continue
            valid = price_series.index[price_series.index <= target_opex]
            if len(valid) > 0:
                opex_prices.append({'Year': y, 'Month': m, 'Price': price_series.loc[valid[-1]]})
    df_opex = pd.DataFrame(opex_prices)
    df_opex['Return'] = df_opex['Price'].pct_change() * 100
    df_opex = df_opex.dropna(subset=['Return'])
    
    print(f"\n{ticker}:")
    print(f"{'Month':<6} {'Cal_Ret':>8} {'OpEx_Ret':>9} {'Diff':>7}")
    for m in range(1, 13):
        cal_ret = df_cal[df_cal['Month'] == m]['Return'].mean()
        opex_ret = df_opex[df_opex['Month'] == m]['Return'].mean()
        diff = opex_ret - cal_ret
        print(f"{calendar.month_abbr[m]:<6} {cal_ret:>7.2f}% {opex_ret:>8.2f}% {diff:>+6.2f}%")
