from pathlib import Path
import pandas as pd
import yfinance as yf
import numpy as np
import datetime

BASE_DIR = Path(__file__).resolve().parent.parent

# Download data
tickers = ["SPY", "QQQ", "SMH"]
data = yf.download(tickers, start="2002-01-01", progress=False)['Close'].dropna()
returns = data.pct_change().dropna()
dates = returns.index

spy_200sma = data['SPY'].rolling(window=200).mean()
macro_crash = (data['SPY'] < spy_200sma).shift(1).fillna(False)

# Helper for OpEx month
def get_opex_month_year(dates):
    # OpEx is 3rd Friday.
    # We define the "OpEx Month X" as the period ending on the 3rd Friday of Month X.
    # So if today is after the 3rd Friday of Sept, we are in OpEx Month 10 (October).
    opex_months = []
    opex_years = []
    for d in dates:
        # Find 3rd Friday of the current calendar month
        first_day = datetime.date(d.year, d.month, 1)
        first_friday = first_day + datetime.timedelta(days=(4 - first_day.weekday() + 7) % 7)
        third_friday = first_friday + datetime.timedelta(days=14)
        
        if d.date() > third_friday:
            # We are in the next OpEx month
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

cal_months = dates.month
cal_years = dates.year
opex_months, opex_years = get_opex_month_year(dates)

def backtest_s4(months, years, is_opex_mode=False):
    cycle_years = years % 4
    
    is_danger_zone = pd.Series(False, index=dates)
    is_golden_zone = pd.Series(False, index=dates)
    
    y1 = (cycle_years == 1)
    is_danger_zone.loc[y1 & (months == 2)] = True
    is_golden_zone.loc[y1 & np.isin(months, [4, 5, 7, 11, 12])] = True
    
    y2 = (cycle_years == 2)
    is_danger_zone.loc[y2 & np.isin(months, [6, 8, 9, 12])] = True
    
    if not is_opex_mode:
        days = dates.day
        is_golden_zone.loc[y2 & ((months == 11) | ((months == 10) & (days >= 15)))] = True
    else:
        # If OpEx mode, OpEx October starts right after the 3rd Friday of September (so we use month 10)
        # Wait, if we want Midterm to start mid-October (like Oct 15), then in OpEx terms it should start on Month 11 (after Oct OpEx)
        is_golden_zone.loc[y2 & np.isin(months, [11])] = True
    
    y3 = (cycle_years == 3)
    is_danger_zone.loc[y3 & np.isin(months, [8, 9])] = True
    is_golden_zone.loc[y3 & np.isin(months, [4, 10, 11, 12])] = True
    
    y4 = (cycle_years == 0)
    is_danger_zone.loc[y4 & (months == 10)] = True
    is_golden_zone.loc[y4 & np.isin(months, [8, 11, 12])] = True
    
    is_danger = is_danger_zone.shift(1).fillna(False)
    is_golden = is_golden_zone.shift(1).fillna(False)
    
    golden_mask = is_golden & ~macro_crash
    danger_mask = is_danger | macro_crash
    
    s4_ret = returns['SPY'].copy()
    s4_ret[golden_mask] = (returns['QQQ'][golden_mask] + returns['SMH'][golden_mask]) / 2
    s4_ret[danger_mask] = 0.0
    
    cum = (1 + s4_ret).cumprod()
    total_ret = (cum.iloc[-1] - 1) * 100
    return total_ret

ret_cal = backtest_s4(cal_months, cal_years, is_opex_mode=False)
ret_opex = backtest_s4(opex_months, opex_years, is_opex_mode=True)

with open(r'C:\Users\ROB5293\antigravity\etfDaily\scripts\opex_vs_cal.txt', 'w') as f:
    f.write(f"Calendar Total Return: {ret_cal:.1f}%\n")
    f.write(f"OpEx Total Return: {ret_opex:.1f}%\n")
