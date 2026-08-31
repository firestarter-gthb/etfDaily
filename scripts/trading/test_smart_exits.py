import pandas as pd
import yfinance as yf
import numpy as np
import datetime
import warnings
warnings.filterwarnings('ignore')

tickers = ["SPY", "QQQ", "SMH"]
data = yf.download(tickers, start="2002-01-01", progress=False)['Close'].dropna()
qqq = data['QQQ']

# Calculate RSI
delta = qqq.diff()
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
rs = gain / loss
rsi = 100 - (100 / (1 + rs))

# Macro filter
spy = data['SPY']
spy_200sma = spy.rolling(window=200).mean()
macro_crash = (spy < spy_200sma).shift(1).fillna(False)

def get_opex_month_year(dates):
    opex_months = []
    opex_years = []
    for d in dates:
        first_day = datetime.date(d.year, d.month, 1)
        first_friday = first_day + datetime.timedelta(days=(4 - first_day.weekday() + 7) % 7)
        third_friday = first_friday + datetime.timedelta(days=14)
        if d.date() > third_friday:
            next_m = d.month + 1
            next_y = d.year
            if next_m > 12:
                next_m = 1
                next_y += 1
            opex_months.append(next_m)
            opex_years.append(next_y)
        else:
            opex_months.append(d.month)
            opex_years.append(d.year)
    return np.array(opex_months), np.array(opex_years)

dates = data.index
opex_months, opex_years = get_opex_month_year(dates)
cycle_years = opex_years % 4

is_danger_zone = pd.Series(False, index=dates)
is_golden_zone = pd.Series(False, index=dates)

y1 = (cycle_years == 1)
is_danger_zone.loc[y1 & (opex_months == 2)] = True
is_golden_zone.loc[y1 & np.isin(opex_months, [4, 5, 7, 11, 12])] = True
y2 = (cycle_years == 2)
is_danger_zone.loc[y2 & np.isin(opex_months, [6, 8, 9, 12])] = True
is_golden_zone.loc[y2 & (opex_months == 11)] = True
y3 = (cycle_years == 3)
is_danger_zone.loc[y3 & np.isin(opex_months, [8, 9])] = True
is_golden_zone.loc[y3 & np.isin(opex_months, [4, 10, 11, 12])] = True
y4 = (cycle_years == 0)
is_danger_zone.loc[y4 & (opex_months == 10)] = True
is_golden_zone.loc[y4 & np.isin(opex_months, [8, 11, 12])] = True

is_danger = is_danger_zone.shift(1).fillna(False)
is_golden = is_golden_zone.shift(1).fillna(False)
entry_signal = is_golden & ~is_golden.shift(1).fillna(False)
calendar_exit_signal = (is_danger & ~is_danger.shift(1).fillna(False)) | (~is_golden & is_golden.shift(1).fillna(False))
asset_sma = qqq.rolling(window=200).mean().shift(1)
rsi_shift = rsi.shift(1)

def sim(use_rsi=False, rsi_level=70):
    in_trade = False
    entry_price = 0
    trades = []
    
    for i in range(1, len(dates)):
        price = qqq.iloc[i]
        mc = macro_crash.iloc[i]
        
        if in_trade:
            # Check exit
            do_exit = calendar_exit_signal.iloc[i] or mc or price < asset_sma.iloc[i]
            if use_rsi and rsi_shift.iloc[i] >= rsi_level:
                do_exit = True
                
            if do_exit:
                ret = (price / entry_price) - 1
                trades.append(ret)
                in_trade = False
        else:
            if entry_signal.iloc[i] and not mc and price >= asset_sma.iloc[i]:
                in_trade = True
                entry_price = price
    return trades

trades_base = sim(False)
trades_rsi75 = sim(True, 75)
trades_rsi70 = sim(True, 70)

def get_stats(trades):
    if not trades: return 0, 0
    w = sum(1 for r in trades if r > 0)
    return (w / len(trades) * 100), np.mean(trades) * 100

print(f"Base: Win Rate {get_stats(trades_base)[0]:.1f}%, Avg {get_stats(trades_base)[1]:.2f}%")
print(f"RSI 75: Win Rate {get_stats(trades_rsi75)[0]:.1f}%, Avg {get_stats(trades_rsi75)[1]:.2f}%")
print(f"RSI 70: Win Rate {get_stats(trades_rsi70)[0]:.1f}%, Avg {get_stats(trades_rsi70)[1]:.2f}%")
