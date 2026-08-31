from pathlib import Path
import pandas as pd
import yfinance as yf
import numpy as np
import datetime
import warnings
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Suppress pandas warnings
warnings.filterwarnings('ignore')

tickers = ["SPY", "QQQ", "SMH"]
data = yf.download(tickers, start="2002-01-01", progress=False)['Close'].dropna()

spy = data['SPY']
qqq = data['QQQ']
smh = data['SMH']
dates = data.index

# Macro filter: we look at yesterday's close vs yesterday's 200SMA
spy_200sma = spy.rolling(window=200).mean()
macro_crash = (spy < spy_200sma).shift(1).fillna(False)

# OpEx logic with shift support
def get_opex_month_year(dates, shift_days=0):
    opex_months = []
    opex_years = []
    for d in dates:
        first_day = datetime.date(d.year, d.month, 1)
        first_friday = first_day + datetime.timedelta(days=(4 - first_day.weekday() + 7) % 7)
        target_friday = first_friday + datetime.timedelta(days=14 + shift_days)
        
        if d.date() > target_friday:
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

def simulate_trades(price_series, asset_name, is_golden, is_danger):
    entry_signal = is_golden & ~is_golden.shift(1).fillna(False)
    # Exit if danger starts, or golden ends
    exit_signal = (is_danger & ~is_danger.shift(1).fillna(False)) | (~is_golden & is_golden.shift(1).fillna(False))
    
    in_trade = False
    entry_price = 0
    entry_date = None
    trades = []
    
    # Asset 200 SMA rule
    asset_sma = price_series.rolling(window=200).mean().shift(1)
    
    for i in range(1, len(dates)):
        date = dates[i]
        price = price_series.iloc[i]
        mc = macro_crash.iloc[i]
        
        if in_trade:
            # Check exit
            if exit_signal.iloc[i] or mc or price < asset_sma.iloc[i]:
                ret = (price / entry_price) - 1
                trades.append({
                    'asset': asset_name,
                    'entry_date': entry_date,
                    'exit_date': date,
                    'ret': ret * 100
                })
                in_trade = False
        else:
            # Check entry
            if entry_signal.iloc[i] and not mc and price >= asset_sma.iloc[i]:
                in_trade = True
                entry_price = price
                entry_date = date
                
    return trades

def print_stats(trades, name, shift_name):
    if not trades:
        return f"No trades for {name} ({shift_name})"
    df_t = pd.DataFrame(trades)
    wins = df_t[df_t['ret'] > 0]
    win_rate = len(wins) / len(df_t) * 100
    avg_ret = df_t['ret'].mean()
    
    # Calculate Compounded Return of the Trades (assuming 100% reallocation into each trade)
    total_compounded = 1.0
    for r in df_t['ret']:
        total_compounded *= (1 + r/100)
    total_ret = (total_compounded - 1) * 100
    
    avg_days = (df_t['exit_date'] - df_t['entry_date']).mean().days
    total_days_in_market = (df_t['exit_date'] - df_t['entry_date']).sum().days
    total_days = (dates[-1] - dates[0]).days
    time_in_market_pct = (total_days_in_market / total_days) * 100
    
    s = f"--- {name} SNIPER STATISTICS (2002-2026) | {shift_name} ---\n"
    s += f"Total Trades: {len(df_t)}\n"
    s += f"Win Rate:     {win_rate:.1f}%\n"
    s += f"Average Ret:  {avg_ret:.2f}% per trade\n"
    s += f"Avg Duration: {avg_days} days per trade\n"
    s += f"Time in Mkt:  {time_in_market_pct:.1f}% of the time\n"
    s += f"Total Return: +{total_ret:.1f}%\n"
    return s

def generate_markdown(trades, asset_name):
    if not trades:
        return f"## {asset_name} Trades\nGeen trades gesimuleerd.\n"
    df = pd.DataFrame(trades)
    df['entry_date'] = pd.to_datetime(df['entry_date']).dt.strftime('%Y-%m-%d')
    df['exit_date'] = pd.to_datetime(df['exit_date']).dt.strftime('%Y-%m-%d')
    df['ret'] = df['ret'].round(2)
    df['Outcome'] = df['ret'].apply(lambda x: '🟢 WIN' if x > 0 else '🔴 VERLIES')
    
    s = f"### {asset_name} Trades\n"
    s += "| Entry Datum | Exit Datum | Rendement (%) | Resultaat |\n"
    s += "| :--- | :--- | :--- | :--- |\n"
    for idx, row in df.iterrows():
        s += f"| {row['entry_date']} | {row['exit_date']} | {row['ret']}% | {row['Outcome']} |\n"
    return s

shifts = [-7, 0, 7]
shift_names = {-7: "Een Week Eerder (-7 Dagen)", 0: "Origineel", 7: "Een Week Later (+7 Dagen)"}

# Generate stats file
stats_content = ""
markdown_content = "# Trade Log: Presidential Cycle Sniper\n\nHier is het overzicht van **alle** gesimuleerde trades van de afgelopen 24 jaar voor de ETF's (SPY, QQQ, SMH), exact volgens de OpEx signalen van het pine script.\n\n"

for shift in shifts:
    shift_lbl = shift_names[shift]
    markdown_content += f"## Versie: {shift_lbl}\n\n"
    stats_content += f"==================================================\n"
    stats_content += f"SITUATIE: {shift_lbl}\n"
    stats_content += f"==================================================\n"
    
    opex_m, opex_y = get_opex_month_year(dates, shift_days=shift)
    cy_years = opex_y % 4
    
    is_danger_zone = pd.Series(False, index=dates)
    is_golden_zone = pd.Series(False, index=dates)
    
    # Zones logic (CORRECTED based on OpEx-to-OpEx verification 2026-08-28)
    y1 = (cy_years == 1)
    is_danger_zone.loc[y1 & (opex_m == 2)] = True
    is_golden_zone.loc[y1 & np.isin(opex_m, [5, 7, 11, 12])] = True
    
    y2 = (cy_years == 2)
    is_danger_zone.loc[y2 & np.isin(opex_m, [6, 9, 12])] = True
    is_golden_zone.loc[y2 & np.isin(opex_m, [8, 11])] = True
    
    y3 = (cy_years == 3)
    is_danger_zone.loc[y3 & (opex_m == 8)] = True
    is_golden_zone.loc[y3 & np.isin(opex_m, [4, 9, 11, 12])] = True
    
    y4 = (cy_years == 0)
    is_danger_zone.loc[y4 & (opex_m == 10)] = True
    is_golden_zone.loc[y4 & np.isin(opex_m, [8, 12])] = True
    
    is_danger = is_danger_zone.shift(1).fillna(False)
    is_golden = is_golden_zone.shift(1).fillna(False)
    
    trades_spy = simulate_trades(spy, 'SPY', is_golden, is_danger)
    trades_qqq = simulate_trades(qqq, 'QQQ', is_golden, is_danger)
    trades_smh = simulate_trades(smh, 'SMH', is_golden, is_danger)
    
    # Save stats
    stats_content += print_stats(trades_spy, 'SPY', shift_lbl) + "\n"
    stats_content += print_stats(trades_qqq, 'QQQ', shift_lbl) + "\n"
    stats_content += print_stats(trades_smh, 'SMH', shift_lbl) + "\n"
    
    # Append to markdown
    markdown_content += generate_markdown(trades_spy, 'SPY') + "\n"
    markdown_content += generate_markdown(trades_qqq, 'QQQ') + "\n"
    markdown_content += generate_markdown(trades_smh, 'SMH') + "\n"

# Write stats
with open(str(BASE_DIR / "reports" / "sniper_stats.txt"), 'w') as f:
    f.write(stats_content)

# Write to current brain conversation dir as requested
trade_log_path = str(BASE_DIR / "reports" / "trade_log.md")
os.makedirs(os.path.dirname(trade_log_path), exist_ok=True)
with open(trade_log_path, 'w', encoding='utf-8') as f:
    f.write(markdown_content)

print("Simulation complete.")
