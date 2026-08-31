from pathlib import Path
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent.parent.parent

tickers = {
    "Nasdaq 100 (QQQ)": "QQQ", 
    "S&P 500 (SPY)": "SPY", 
    "Dow Jones (DIA)": "DIA",
    "Russell 2000 (IWM)": "IWM",
    "Semiconductors (SMH)": "SMH",
    "Gold (GLD)": "GLD"
}

print("Downloading data...")
data = yf.download(list(tickers.values()), start="2005-01-01", progress=False)
adj_close = data['Adj Close'] if 'Adj Close' in data.columns else data['Close']
adj_close = adj_close.rename(columns={v: k for k, v in tickers.items()})

adj_close.dropna(inplace=True)

monthly = adj_close.resample('ME').last()
returns = monthly.pct_change().dropna()

equity_curve = (1 + returns).cumprod()
equity_curve = equity_curve / equity_curve.iloc[0] * 100

plt.figure(figsize=(12, 6))
for col in equity_curve.columns:
    plt.plot(equity_curve.index, equity_curve[col], label=col, linewidth=2)
plt.yscale('log')
plt.title(f'Alternative ETFs Performance ({equity_curve.index[0].year} - {equity_curve.index[-1].year})')
plt.ylabel('Equity (Base 100, Log Scale)')
plt.legend()
plt.grid(True, which="both", ls="-", alpha=0.2)
plt.tight_layout()
plt.savefig(str(BASE_DIR / "reports" / "figures" / "alternative_etfs.png"))

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
        "Total Return": f"{total_ret*100:.1f}%",
        "Ann. Return": f"{ann_ret*100:.1f}%",
        "Max Drawdown": f"{max_dd*100:.1f}%",
        "Sharpe Ratio": f"{sharpe:.2f}"
    }

metrics = pd.DataFrame({k: calc_metrics(returns[k]) for k in tickers.keys()})

def get_num(s):
    return float(s.replace('%', ''))
order = metrics.T['Total Return'].apply(get_num).sort_values(ascending=False).index
metrics = metrics[order]

print("\n--- ALTERNATIVE ETF METRICS (2005 - 2026) ---")
print(metrics.T.to_string())
