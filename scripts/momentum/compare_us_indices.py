from pathlib import Path
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent.parent.parent

tickers = {"Nasdaq 100 (QQQ)": "QQQ", "S&P 500 (SPY)": "SPY", "Dow Jones (DIA)": "DIA"}

print("Downloading data...")
data = yf.download(list(tickers.values()), period="max", progress=False)
adj_close = data['Adj Close'] if 'Adj Close' in data.columns else data['Close']
adj_close = adj_close.rename(columns={v: k for k, v in tickers.items()})

# Drop NA so we start when all 3 exist (approx March 1999)
adj_close.dropna(inplace=True)

# Monthly returns
monthly = adj_close.resample('ME').last()
returns = monthly.pct_change().dropna()

# Equity curve
equity_curve = (1 + returns).cumprod()
equity_curve = equity_curve / equity_curve.iloc[0] * 100

plt.figure(figsize=(12, 6))
plt.plot(equity_curve.index, equity_curve['Nasdaq 100 (QQQ)'], label='Nasdaq 100 (QQQ)', color='purple', linewidth=2)
plt.plot(equity_curve.index, equity_curve['S&P 500 (SPY)'], label='S&P 500 (SPY)', color='blue', linewidth=2)
plt.plot(equity_curve.index, equity_curve['Dow Jones (DIA)'], label='Dow Jones (DIA)', color='green', linewidth=2)
plt.yscale('log')
plt.title(f'US Indices Long-Term Performance ({equity_curve.index[0].year} - {equity_curve.index[-1].year})')
plt.ylabel('Equity (Base 100, Log Scale)')
plt.legend()
plt.grid(True, which="both", ls="-", alpha=0.2)
plt.tight_layout()
plt.savefig(str(BASE_DIR / "reports" / "figures" / "us_indices_long_term.png"))

def calc_metrics(ret):
    cum_ret = (1 + ret).cumprod() - 1
    total_ret = cum_ret.iloc[-1]
    
    years = len(ret) / 12
    ann_ret = (1 + total_ret) ** (1 / years) - 1
    
    roll_max = (1 + ret).cumprod().cummax()
    drawdown = (1 + ret).cumprod() / roll_max - 1
    max_dd = drawdown.min()
    
    ann_vol = ret.std() * np.sqrt(12)
    sharpe = ann_ret / ann_vol if ann_vol > 0 else 0
    
    return {
        "Start": ret.index[0].strftime('%Y-%m'),
        "Total Return": f"{total_ret*100:.1f}%",
        "Ann. Return": f"{ann_ret*100:.1f}%",
        "Max Drawdown": f"{max_dd*100:.1f}%",
        "Sharpe Ratio": f"{sharpe:.2f}"
    }

metrics = pd.DataFrame({
    'Nasdaq 100 (QQQ)': calc_metrics(returns['Nasdaq 100 (QQQ)']),
    'S&P 500 (SPY)': calc_metrics(returns['S&P 500 (SPY)']),
    'Dow Jones (DIA)': calc_metrics(returns['Dow Jones (DIA)'])
})

def get_num(s):
    return float(s.replace('%', ''))
order = metrics.T['Total Return'].apply(get_num).sort_values(ascending=False).index
metrics = metrics[order]

print("\n--- LONG TERM METRICS ---")
print(metrics.T.to_string())
