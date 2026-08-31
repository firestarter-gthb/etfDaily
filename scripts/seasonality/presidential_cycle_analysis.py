from pathlib import Path
import pandas as pd
import yfinance as yf
import calendar

BASE_DIR = Path(__file__).resolve().parent.parent

print("Downloading SPY data...")
data = yf.download("SPY", period="max", progress=False)
df = data.copy()
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.droplevel(1)
df.index = pd.to_datetime(df.index)

monthly = df['Adj Close' if 'Adj Close' in df.columns else 'Close'].resample('ME').last()
ret = monthly.pct_change().dropna()

df_ret = pd.DataFrame({'Return': ret})
df_ret['Month'] = df_ret.index.month
df_ret['Year'] = df_ret.index.year

def get_cycle_year(y):
    mod = y % 4
    if mod == 1: return "1. Post-Election"
    elif mod == 2: return "2. Midterm"
    elif mod == 3: return "3. Pre-Election"
    else: return "4. Election"

df_ret['Cycle'] = df_ret['Year'].apply(get_cycle_year)

def get_stats(series):
    if len(series) == 0: return 0, 0
    win = (series > 0).mean() * 100
    avg = series.mean() * 100
    return win, avg

cycles = ["1. Post-Election", "2. Midterm", "3. Pre-Election", "4. Election"]
results = {}

for c in cycles:
    c_data = df_ret[df_ret['Cycle'] == c]
    month_stats = []
    for m in range(1, 13):
        m_data = c_data[c_data['Month'] == m]['Return']
        w, a = get_stats(m_data)
        month_stats.append(f"| {calendar.month_abbr[m]} | {w:.1f}% | {a:.2f}% |")
    results[c] = month_stats

output_path = str(BASE_DIR / "reports" / "cycle_results.txt")
with open(output_path, 'w') as f:
    for c in cycles:
        f.write(f"### {c}\n")
        f.write("| Month | Win % | Avg Ret |\n")
        f.write("| :--- | :--- | :--- |\n")
        for line in results[c]:
            f.write(line + "\n")
        f.write("\n")
print("Done")
