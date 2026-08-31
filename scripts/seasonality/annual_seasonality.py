import pandas as pd
import yfinance as yf
import calendar

tickers = ["SPY", "QQQ", "SMH"]
data = yf.download(tickers, start="2002-01-01", progress=False)['Close'].dropna()

results = {}

for ticker in tickers:
    price_series = data[ticker]
    # Resample to monthly closes
    monthly_prices = price_series.resample('ME').last()
    # Calculate monthly returns
    monthly_returns = monthly_prices.pct_change().dropna()
    
    df_ret = pd.DataFrame({'Return': monthly_returns * 100})
    df_ret['Month'] = df_ret.index.month
    
    # Calculate average return and win rate for each month
    month_stats = []
    for m in range(1, 13):
        m_rets = df_ret[df_ret['Month'] == m]['Return']
        win_rate = (m_rets > 0).mean() * 100
        avg_ret = m_rets.mean()
        month_stats.append({
            'Month': calendar.month_abbr[m],
            'WinRate': round(win_rate, 1),
            'AvgRet': round(avg_ret, 2)
        })
    results[ticker] = pd.DataFrame(month_stats).set_index('Month')

for ticker in tickers:
    print(f"\n=== GENERAL SEASONALITY FOR {ticker} (2002-2026) ===")
    print(results[ticker].to_string())
