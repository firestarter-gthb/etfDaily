from pathlib import Path
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Configuration
TOP_N = 5
MOMENTUM_LOOKBACK = 12 # 12 months for standard Dual Momentum
TREND_LOOKBACK = 10 # 10-month SMA for absolute momentum
START_YEAR = 2008 # Start of backtest

tickers = {
    "Zuid-Korea": "EWY", "Taiwan": "EWT", "Colombia": "GXG", "Griekenland": "GREK", "Polen": "EPOL",
    "Singapore": "EWS", "Zweden": "EWD", "Noorwegen": "ENOR", "Canada": "EWC", "Italië": "EWI",
    "Thailand": "THD", "Zuid-Afrika": "EZA", "Spanje": "EWP", "Denemarken": "EDEN", "Zwitserland": "EWL",
    "USA": "SPY", "Japan": "EWJ", "Wereld Benchmark": "URTH", "Europa 600": "EZU", "Israël": "EIS",
    "Mexico": "EWW", "VK": "EWU", "Australië": "EWA", "Brazilië": "EWZ", "Turkije": "TUR",
    "Argentinië": "ARGT", "Maleisië": "EWM", "Duitsland": "EWG", "Frankrijk": "EWQ", "Saudi-Arabië": "KSA",
    "Verenigde Arabische Emiraten": "UAE", "India": "INDA", "Vietnam": "VNM", "China": "MCHI", "Indonesië": "EIDO",
    "Nasdaq 100": "QQQ", "Dow Jones": "DIA"
}

print("Downloading data...")
data = yf.download(list(tickers.values()), start=f"{START_YEAR-1}-01-01", progress=False)
adj_close = data['Adj Close'] if 'Adj Close' in data.columns else data['Close']
adj_close = adj_close.rename(columns={v: k for k, v in tickers.items()})

# Resample to end of month
monthly = adj_close.resample('ME').last()

# Calculate momentum (12-month return)
momentum = monthly.pct_change(MOMENTUM_LOOKBACK)

# Calculate volatility (12-month standard deviation of monthly returns)
volatility = monthly.pct_change(1).rolling(MOMENTUM_LOOKBACK).std()
vol_adj_momentum = momentum / volatility

# Calculate absolute trend (SPY > 10-month SMA)
spy_sma10 = monthly['USA'].rolling(window=TREND_LOOKBACK).mean()
trend_is_positive = monthly['USA'] > spy_sma10

# Calculate 1-month forward returns for all countries (what we actually earn next month)
forward_returns = monthly.pct_change(1).shift(-1)

# Backtest loop
portfolio_returns = []
dates = []

# Exclude Benchmarks from being selected as "Countries"
country_universe = [c for c in tickers.keys() if c not in ["Wereld Benchmark", "Europa 600", "Nasdaq 100", "Dow Jones"]]

# Start backtest after enough lookback data
start_idx = max(MOMENTUM_LOOKBACK, TREND_LOOKBACK)

for i in range(start_idx, len(monthly) - 1): # -1 because we need forward returns
    date = monthly.index[i]
    
    if trend_is_positive.iloc[i]:
        current_mom = vol_adj_momentum[country_universe].iloc[i].dropna()
        if len(current_mom) >= TOP_N:
            top_n = current_mom.nlargest(TOP_N).index.tolist()
            next_month_return = forward_returns[top_n].iloc[i].mean()
        else:
            next_month_return = 0.0
    else:
        next_month_return = 0.0
        
    portfolio_returns.append(next_month_return)
    dates.append(monthly.index[i+1]) # The return applies to the next month

# Create DataFrame
bt_df = pd.DataFrame(index=dates)
bt_df['Dual Momentum'] = portfolio_returns

# Add Benchmarks
bt_df['S&P 500'] = forward_returns['USA'].loc[dates]
bt_df['MSCI World'] = forward_returns['Wereld Benchmark'].loc[dates]
bt_df['Nasdaq 100'] = forward_returns['Nasdaq 100'].loc[dates]
bt_df['Dow Jones'] = forward_returns['Dow Jones'].loc[dates]

# Drop NAs
bt_df.dropna(inplace=True)

# Calculate Equity Curve
equity_curve = (1 + bt_df).cumprod()
equity_curve = equity_curve / equity_curve.iloc[0] * 100 # Base 100

# Plot
plt.figure(figsize=(12, 6))
plt.plot(equity_curve.index, equity_curve['Nasdaq 100'], label='Nasdaq 100 (QQQ)', alpha=0.9, color='purple')
plt.plot(equity_curve.index, equity_curve['Dual Momentum'], label='Global Dual Momentum (Top 5)', linewidth=2, color='red')
plt.plot(equity_curve.index, equity_curve['S&P 500'], label='S&P 500 (Buy & Hold)', alpha=0.7, color='blue')
plt.plot(equity_curve.index, equity_curve['Dow Jones'], label='Dow Jones (DIA)', alpha=0.7, color='green')
plt.plot(equity_curve.index, equity_curve['MSCI World'], label='MSCI World (Buy & Hold)', alpha=0.7, color='orange')
plt.yscale('log')
plt.title('Global Dual Momentum vs Major Indices (Log Scale)')
plt.ylabel('Equity (Base 100)')
plt.legend()
plt.grid(True, which="both", ls="-", alpha=0.2)
plt.tight_layout()
plt.savefig(str(BASE_DIR / "reports" / "figures" / "equity_curve.png"))

# Metrics
def calc_metrics(returns):
    cum_ret = (1 + returns).cumprod() - 1
    total_ret = cum_ret.iloc[-1]
    
    # Annualized Return
    years = len(returns) / 12
    ann_ret = (1 + total_ret) ** (1 / years) - 1
    
    # Max Drawdown
    roll_max = (1 + returns).cumprod().cummax()
    drawdown = (1 + returns).cumprod() / roll_max - 1
    max_dd = drawdown.min()
    
    # Sharpe Ratio (assuming 0% risk free rate)
    ann_vol = returns.std() * np.sqrt(12)
    sharpe = ann_ret / ann_vol if ann_vol > 0 else 0
    
    return {
        "Total Return": f"{total_ret*100:.1f}%",
        "Ann. Return": f"{ann_ret*100:.1f}%",
        "Max Drawdown": f"{max_dd*100:.1f}%",
        "Sharpe Ratio": f"{sharpe:.2f}"
    }

metrics = pd.DataFrame({
    'Dual Momentum': calc_metrics(bt_df['Dual Momentum']),
    'S&P 500': calc_metrics(bt_df['S&P 500']),
    'MSCI World': calc_metrics(bt_df['MSCI World']),
    'Nasdaq 100': calc_metrics(bt_df['Nasdaq 100']),
    'Dow Jones': calc_metrics(bt_df['Dow Jones'])
})

# Reorder columns by Total Return
def get_num(s):
    return float(s.replace('%', ''))
order = metrics.T['Total Return'].apply(get_num).sort_values(ascending=False).index
metrics = metrics[order]

print("\n--- BACKTEST METRICS (Sorted by Total Return) ---")
print(metrics.T.to_string())
