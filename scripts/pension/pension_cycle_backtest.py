from pathlib import Path
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent

# We use SPY as the core "MSCI World" proxy for the 25 year backtest,
# since true global ETFs don't have enough history. SPY matches global trend 99%.
tickers = ["SPY", "QQQ", "SMH"]
data = yf.download(tickers, start="2002-01-01", progress=False)

df = data['Adj Close' if 'Adj Close' in data.columns else 'Close'].copy()
df = df.dropna()

returns = df.pct_change().dropna()
dates = returns.index

# Add macro crash indicator (SPY < 200 SMA)
spy_200sma = df['SPY'].rolling(window=200).mean()
macro_crash = df['SPY'] < spy_200sma
macro_crash = macro_crash.shift(1).fillna(False)

years = dates.year
months = dates.month
days = dates.day
cycle_years = years % 4

is_danger_zone = pd.Series(False, index=dates)
is_golden_zone = pd.Series(False, index=dates)

# Jaar 1 (Post-Election)
y1 = (cycle_years == 1)
is_danger_zone.loc[y1 & (months == 2)] = True
is_golden_zone.loc[y1 & (months.isin([4, 5, 7, 11, 12]))] = True

# Jaar 2 (Midterm)
y2 = (cycle_years == 2)
is_danger_zone.loc[y2 & (months.isin([6, 8, 9, 12]))] = True
is_golden_zone.loc[y2 & ((months == 11) | ((months == 10) & (days >= 15)))] = True

# Jaar 3 (Pre-Election)
y3 = (cycle_years == 3)
is_danger_zone.loc[y3 & (months.isin([8, 9]))] = True
is_golden_zone.loc[y3 & (months.isin([4, 10, 11, 12]))] = True

# Jaar 4 (Election)
y4 = (cycle_years == 0)
is_danger_zone.loc[y4 & (months == 10)] = True
is_golden_zone.loc[y4 & (months.isin([8, 11, 12]))] = True

# Shift zones to prevent lookahead bias (trade next day)
is_danger = is_danger_zone.shift(1).fillna(False)
is_golden = is_golden_zone.shift(1).fillna(False)

golden_mask = is_golden & ~macro_crash
danger_mask = is_danger | macro_crash

# Scenario 1: Buy & Hold SPY
s1_ret = returns['SPY']

# Scenario 2: Turbo Boost (100% SPY -> 50/50 QQQ/SMH in Golden)
s2_ret = returns['SPY'].copy()
s2_ret[golden_mask] = (returns['QQQ'][golden_mask] + returns['SMH'][golden_mask]) / 2

# Scenario 3: Risk Averse (100% SPY -> Cash in Danger)
s3_ret = returns['SPY'].copy()
s3_ret[danger_mask] = 0.0

# Scenario 4: The Ultimate Presidential Pension (Mix)
s4_ret = returns['SPY'].copy()
s4_ret[golden_mask] = (returns['QQQ'][golden_mask] + returns['SMH'][golden_mask]) / 2
s4_ret[danger_mask] = 0.0

def get_metrics(ret_series):
    cum = (1 + ret_series).cumprod()
    total_ret = (cum.iloc[-1] - 1) * 100
    years_count = len(ret_series) / 252
    cagr = ((cum.iloc[-1]) ** (1 / years_count) - 1) * 100
    roll_max = cum.cummax()
    drawdown = (cum / roll_max - 1) * 100
    max_dd = drawdown.min()
    return cum, total_ret, cagr, max_dd

c1, t1, cagr1, dd1 = get_metrics(s1_ret)
c2, t2, cagr2, dd2 = get_metrics(s2_ret)
c3, t3, cagr3, dd3 = get_metrics(s3_ret)
c4, t4, cagr4, dd4 = get_metrics(s4_ret)

with open(r'C:\Users\ROB5293\antigravity\etfDaily\scripts\pension_results.txt', 'w') as f:
    f.write(f"S1|{t1:.1f}|{cagr1:.1f}|{dd1:.1f}\n")
    f.write(f"S2|{t2:.1f}|{cagr2:.1f}|{dd2:.1f}\n")
    f.write(f"S3|{t3:.1f}|{cagr3:.1f}|{dd3:.1f}\n")
    f.write(f"S4|{t4:.1f}|{cagr4:.1f}|{dd4:.1f}\n")

plt.figure(figsize=(12, 6))
plt.plot(c1.index, c1.values * 100, label='S1: Buy & Hold (Baseline)', color='gray')
plt.plot(c2.index, c2.values * 100, label='S2: Turbo Boost', color='blue')
plt.plot(c3.index, c3.values * 100, label='S3: Risk Averse', color='orange')
plt.plot(c4.index, c4.values * 100, label='S4: Ultimate Presidential', color='green', linewidth=2)
plt.title("Pension Allocation Strategy (2002 - 2026)")
plt.ylabel("Portfolio Value (100 = Start) - LOG SCALE")
plt.yscale('log')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig(str(BASE_DIR / "reports" / "figures\pension_backtest.png")
print("Done")
