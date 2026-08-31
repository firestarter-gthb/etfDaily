"""
Quantitative Research: Impact of Past 1-3 Month Seasonality Divergence on Current Month Returns
==============================================================================================
Hypothesis testing: Does outperforming or underperforming seasonal benchmarks over the past 
1 to 3 months (Seasonal Divergence / Alpha) lead to Mean Reversion or Trend Continuation in the current month?

Assets Tested:
1. SPX (S&P 500 Index: 1950 - 2026)
2. QQQ / Nasdaq (1971 - 2026)
3. SMH (Semiconductors: 2000 - 2026)
4. Bitcoin (BTC-USD: 2014 - 2026)
"""
from pathlib import Path
import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.colors import LinearSegmentedColormap
import warnings

warnings.filterwarnings("ignore")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
FIGURES_DIR = BASE_DIR / "reports" / "figures"
REPORTS_DIR = BASE_DIR / "reports" / "research"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# Helper to load monthly series
def load_monthly_series(filepath, ticker_symbol, start_year=1950):
    full_path = BASE_DIR / filepath
    if full_path.exists():
        try:
            df = pd.read_csv(full_path, skiprows=[1, 2], index_col=0, parse_dates=True)
        except Exception:
            df = pd.read_csv(full_path, index_col=0, parse_dates=True)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df.index = pd.to_datetime(df.index)
        col = 'Adj Close' if 'Adj Close' in df.columns else ('Close' if 'Close' in df.columns else df.columns[0])
        s = pd.to_numeric(df[col], errors='coerce').dropna()
        s = s[~s.index.duplicated(keep='first')].sort_index()
    else:
        import yfinance as yf
        raw = yf.download(ticker_symbol, period='max', progress=False)
        if isinstance(raw.columns, pd.MultiIndex):
            raw.columns = raw.columns.droplevel(1)
        col = 'Adj Close' if 'Adj Close' in raw.columns else 'Close'
        s = pd.to_numeric(raw[col], errors='coerce').dropna().sort_index()

    # Filter start year
    s = s[s.index >= f"{start_year-1}-12-01"]
    
    # Calculate End of Month monthly returns
    monthly_prices = s.groupby([s.index.year, s.index.month]).last()
    monthly_rets = monthly_prices.pct_change().dropna()
    
    # Build a clean dataframe with date index as Year-Month
    df_m = pd.DataFrame({
        'Year': [y for y, m in monthly_rets.index],
        'Month': [m for y, m in monthly_rets.index],
        'Return': monthly_rets.values * 100.0
    })
    df_m['Date'] = pd.to_datetime(df_m.apply(lambda r: f"{int(r.Year)}-{int(r.Month):02d}-01", axis=1))
    df_m.sort_values('Date', inplace=True)
    df_m.reset_index(drop=True, inplace=True)
    return df_m

# Load Datasets
datasets = {
    'SPX (S&P 500)': ('data/indices/SPX.csv', '^GSPC', 1950),
    'Nasdaq / QQQ': ('data/indices/Nasdaq.csv', '^IXIC', 1971),
    'SMH (Semiconductors)': ('data/sectors/SMH_Semiconductors.csv', 'SMH', 2000),
    'Bitcoin': ('data/crypto/Bitcoin.csv', 'BTC-USD', 2014)
}

def analyze_seasonality_divergence(df_m, asset_name):
    """
    Computes expanding/historical seasonality baseline, calculates divergence (excess return vs seasonality),
    and tests predictive power of 1M, 2M, 3M past divergence on current month return and divergence.
    """
    df = df_m.copy()
    
    # Calculate baseline seasonality per calendar month (historical average)
    # Using all-sample average and expanding window to ensure robustness
    month_means = df.groupby('Month')['Return'].mean()
    df['Seasonal_Mean'] = df['Month'].map(month_means)
    
    # Seasonal Divergence in month t (Alpha over seasonal benchmark)
    df['Divergence'] = df['Return'] - df['Seasonal_Mean']
    
    # Lags for lookback: 1 month, 2 months, 3 months
    # Past 1M Divergence
    df['Div_Lag1'] = df['Divergence'].shift(1)
    df['Ret_Lag1'] = df['Return'].shift(1)
    
    # Past 2M Cumulative Divergence: (D_{t-1} + D_{t-2})
    df['Div_Lag2_Sum'] = df['Divergence'].shift(1) + df['Divergence'].shift(2)
    df['Ret_Lag2_Sum'] = df['Return'].shift(1) + df['Return'].shift(2)
    
    # Past 3M Cumulative Divergence: (D_{t-1} + D_{t-2} + D_{t-3})
    df['Div_Lag3_Sum'] = df['Divergence'].shift(1) + df['Divergence'].shift(2) + df['Divergence'].shift(3)
    df['Ret_Lag3_Sum'] = df['Return'].shift(1) + df['Return'].shift(2) + df['Return'].shift(3)
    
    df_clean = df.dropna().copy()
    
    # 3-Month Divergence Regimes:
    # Regime 1: Strong Overperformance (> +5% or Top Tercile)
    # Regime 2: Neutral / In-Line (-5% to +5% or Middle Tercile)
    # Regime 3: Strong Underperformance (< -5% or Bottom Tercile)
    tercile_3m = pd.qcut(df_clean['Div_Lag3_Sum'], q=3, labels=['Underperforming (Bottom 33%)', 'Neutral (Middle 33%)', 'Overperforming (Top 33%)'])
    df_clean['Regime_3M_Tercile'] = tercile_3m
    
    # Fixed threshold regimes:
    # Overperforming (> +3%), Neutral (-3% to +3%), Underperforming (< -3%) for SPX
    # For high vol assets (Bitcoin, SMH), threshold scales
    threshold_3m = 4.0 if 'Bitcoin' not in asset_name else 15.0
    
    def classify_threshold(val, thresh):
        if val > thresh:
            return f"Overperformance (>+{thresh}%)"
        elif val < -thresh:
            return f"Underperformance (<-{thresh}%)"
        else:
            return f"In-Line (±{thresh}%)"
            
    df_clean['Regime_3M_Fixed'] = df_clean['Div_Lag3_Sum'].apply(lambda x: classify_threshold(x, threshold_3m))
    
    # Statistics per Tercile
    stats_tercile = []
    for reg in ['Underperforming (Bottom 33%)', 'Neutral (Middle 33%)', 'Overperforming (Top 33%)']:
        sub = df_clean[df_clean['Regime_3M_Tercile'] == reg]
        n = len(sub)
        avg_ret = sub['Return'].mean()
        med_ret = sub['Return'].median()
        win_rate = (sub['Return'] > 0).mean() * 100
        avg_div = sub['Divergence'].mean()
        div_win_rate = (sub['Divergence'] > 0).mean() * 100
        std_ret = sub['Return'].std()
        sharpe = (avg_ret / std_ret) if std_ret > 0 else np.nan
        
        stats_tercile.append({
            'Regime': reg,
            'N': n,
            'Avg Return (%)': avg_ret,
            'Median Return (%)': med_ret,
            'Win Rate (%)': win_rate,
            'Avg Seasonal Alpha (%)': avg_div,
            'Alpha Win Rate (%)': div_win_rate,
            'Std Dev (%)': std_ret,
            'Sharpe (Mo)': sharpe
        })
        
    df_stats_tercile = pd.DataFrame(stats_tercile).set_index('Regime')
    
    # Linear Regression & Correlation
    # Correlation between Div_Lag3_Sum and current Return
    corr_ret_div3, p_ret_div3 = stats.pearsonr(df_clean['Div_Lag3_Sum'], df_clean['Return'])
    corr_div_div3, p_div_div3 = stats.pearsonr(df_clean['Div_Lag3_Sum'], df_clean['Divergence'])
    
    # 1M and 2M correlation
    corr_ret_div1, p_ret_div1 = stats.pearsonr(df_clean['Div_Lag1'], df_clean['Return'])
    corr_div_div1, p_div_div1 = stats.pearsonr(df_clean['Div_Lag1'], df_clean['Divergence'])
    
    correlations = {
        '1M Div -> Next Ret Corr': (corr_ret_div1, p_ret_div1),
        '1M Div -> Next Div Corr': (corr_div_div1, p_div_div1),
        '3M Div -> Next Ret Corr': (corr_ret_div3, p_ret_div3),
        '3M Div -> Next Div Corr': (corr_div_div3, p_div_div3)
    }
    
    return df_clean, df_stats_tercile, correlations

print("Running Quantitative Divergence Analysis across all assets...\n")

all_results = {}
for asset_label, (fpath, symbol, s_yr) in datasets.items():
    df_m = load_monthly_series(fpath, symbol, s_yr)
    df_clean, stats_tercile, corrs = analyze_seasonality_divergence(df_m, asset_label)
    all_results[asset_label] = {
        'data': df_clean,
        'stats': stats_tercile,
        'corrs': corrs
    }
    print(f"=== {asset_label} (N = {len(df_clean)} months) ===")
    print(stats_tercile.round(2).to_string())
    print("\nCorrelations:")
    for k, (c, p) in corrs.items():
        sig = "***" if p < 0.01 else ("**" if p < 0.05 else ("*" if p < 0.1 else " (ns)"))
        print(f"  {k}: r = {c:+.4f} (p = {p:.4f}){sig}")
    print("\n" + "="*80 + "\n")

# =========================================================================
# COMBINED SUMMARY TABLE & STATISTICAL COMPARISON
# =========================================================================
summary_rows = []
for asset, res in all_results.items():
    st = res['stats']
    under = st.loc['Underperforming (Bottom 33%)']
    over = st.loc['Overperforming (Top 33%)']
    neutral = st.loc['Neutral (Middle 33%)']
    
    diff_ret = over['Avg Return (%)'] - under['Avg Return (%)']
    diff_wr = over['Win Rate (%)'] - under['Win Rate (%)']
    diff_alpha = over['Avg Seasonal Alpha (%)'] - under['Avg Seasonal Alpha (%)']
    
    summary_rows.append({
        'Asset': asset,
        'N (Months)': int(under['N'] + neutral['N'] + over['N']),
        'Underperform 3M: Ret%': under['Avg Return (%)'],
        'Underperform 3M: WR%': under['Win Rate (%)'],
        'Overperform 3M: Ret%': over['Avg Return (%)'],
        'Overperform 3M: WR%': over['Win Rate (%)'],
        'Spread (Over - Under Ret)': diff_ret,
        'Spread (Over - Under WR)': diff_wr,
        '3M Div -> Next Ret Corr': res['corrs']['3M Div -> Next Ret Corr'][0],
        'p-value': res['corrs']['3M Div -> Next Ret Corr'][1]
    })

summary_df = pd.DataFrame(summary_rows).set_index('Asset')
print("=== ONDERZOEKS CONCLUSIE SAMENVATTING (3M SEASONAL ALPHA REGIMES) ===")
print(summary_df.round(2).to_string())

# =========================================================================
# COMPREHENSIVE VISUALIZATION
# =========================================================================
fig = plt.figure(figsize=(20, 16))
gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.32, wspace=0.22)
fig.suptitle("Impact van 3-Maands Seizoens-Divergence op de Volgende Maand\n(Onderzoek naar Trend-Continuation vs. Mean-Reversion)", 
             fontsize=16, fontweight="bold", y=0.98)

colors = ['#c0392b', '#7f8c8d', '#27ae60']

for idx, (asset_label, res) in enumerate(all_results.items()):
    ax = fig.add_subplot(gs[idx // 2, idx % 2])
    st = res['stats']
    
    regimes = ['Underperforming\n(Bottom 33%)', 'Neutral\n(Middle 33%)', 'Overperforming\n(Top 33%)']
    avg_rets = st['Avg Return (%)'].values
    win_rates = st['Win Rate (%)'].values
    alphas = st['Avg Seasonal Alpha (%)'].values
    n_counts = st['N'].values
    
    x = np.arange(len(regimes))
    bar_w = 0.38
    
    bars1 = ax.bar(x - bar_w/2, avg_rets, bar_w, label='Gem. Rendement (%)', color=colors, alpha=0.85, edgecolor='black', linewidth=0.8)
    
    ax2 = ax.twinx()
    line1 = ax2.plot(x, win_rates, color='#1f3c88', marker='o', linewidth=2.5, markersize=8, label='Win Rate (%)', linestyle='--')
    ax2.set_ylabel("Win Rate (% Positieve Maanden)", color='#1f3c88', fontsize=10, fontweight='bold')
    ax2.tick_params(axis='y', labelcolor='#1f3c88')
    ax2.set_ylim(max(20, min(win_rates) - 15), min(100, max(win_rates) + 15))
    
    ax.axhline(0, color='black', linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(regimes, fontsize=10, fontweight='bold')
    ax.set_ylabel("Volgende Maand Gem. Rendement (%)", fontsize=10, fontweight='bold')
    
    # Correlation text
    c_val, p_val = res['corrs']['3M Div -> Next Ret Corr']
    sig_str = "Statistisch Significant" if p_val < 0.05 else "Niet Significant"
    ax.set_title(f"{asset_label}\nCorrelatie: r = {c_val:+.3f} (p = {p_val:.3f} · {sig_str})", fontsize=11, fontweight='bold', pad=10)
    
    # Annotate bars
    for i, bar in enumerate(bars1):
        h = bar.get_height()
        va = 'bottom' if h >= 0 else 'top'
        y_pos = h + (0.1 if h >= 0 else -0.2)
        ax.text(bar.get_x() + bar.get_width()/2, y_pos, f"{h:+.2f}%\n(N={n_counts[i]})",
                ha='center', va=va, fontsize=9, fontweight='bold', color='black')
        
    for i, wr in enumerate(win_rates):
        ax2.text(x[i], wr + 1.5, f"{wr:.1f}%", ha='center', va='bottom', fontsize=9, fontweight='bold', color='#1f3c88')
        
    ax.grid(axis='y', alpha=0.3)

chart_path = FIGURES_DIR / "seasonality_divergence_impact.png"
plt.savefig(chart_path, dpi=150, bbox_inches="tight")
plt.close()
print(f"\nGrafiek opgeslagen naar: {chart_path}")

# =========================================================================
# FIGURE 2: SCATTER PLOT & REGRESSION: 3M DIVERGENCE VS NEXT MONTH RETURN
# =========================================================================
fig2, axes = plt.subplots(2, 2, figsize=(18, 14))
fig2.suptitle("Scatter & Regressie: Vorige 3-Maanden Seasonal Alpha vs. Volgende Maand Rendement",
              fontsize=15, fontweight="bold", y=0.98)

for idx, (asset_label, res) in enumerate(all_results.items()):
    ax = axes[idx // 2, idx % 2]
    df_clean = res['data']
    
    x = df_clean['Div_Lag3_Sum']
    y = df_clean['Return']
    
    # Scatter points
    ax.scatter(x, y, alpha=0.45, color='#2980b9', edgecolors='none', s=35)
    
    # Linear trendline
    m, b = np.polyfit(x, y, 1)
    x_vals = np.linspace(x.min(), x.max(), 100)
    ax.plot(x_vals, m * x_vals + b, color='#c0392b', linewidth=2.5, 
            label=f'Trendlijn: y = {m:+.3f}x + {b:.2f}')
    
    ax.axhline(0, color='black', linewidth=0.8, linestyle=':')
    ax.axvline(0, color='black', linewidth=0.8, linestyle=':')
    
    c_val, p_val = res['corrs']['3M Div -> Next Ret Corr']
    ax.set_title(f"{asset_label} (N = {len(df_clean)})\nr = {c_val:+.3f}, p = {p_val:.4f}", fontsize=11, fontweight='bold')
    ax.set_xlabel("Cumulatieve Seasonal Divergence Afgelopen 3 Maanden (%)", fontsize=10)
    ax.set_ylabel("Rendement Volgende Maand (%)", fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper left', fontsize=9)

chart2_path = FIGURES_DIR / "seasonality_divergence_scatter.png"
plt.savefig(chart2_path, dpi=150, bbox_inches="tight")
plt.close()
print(f"Scatter grafiek opgeslagen naar: {chart2_path}")

# =========================================================================
# FIGURE 3: LOOKBACK COMPARISON (1-Month vs 2-Month vs 3-Month vs 6-Month)
# =========================================================================
# Test multi-lag predictive structure on SPX and QQQ
def test_lags(df_m, asset_name):
    df = df_m.copy()
    month_means = df.groupby('Month')['Return'].mean()
    df['Divergence'] = df['Return'] - df['Month'].map(month_means)
    
    lags = [1, 2, 3, 6, 12]
    res_lags = []
    for l in lags:
        df[f'Div_Lag_{l}'] = df['Divergence'].shift(1).rolling(l).sum()
        df_sub = df.dropna(subset=[f'Div_Lag_{l}', 'Return', 'Divergence'])
        
        c_ret, p_ret = stats.pearsonr(df_sub[f'Div_Lag_{l}'], df_sub['Return'])
        c_div, p_div = stats.pearsonr(df_sub[f'Div_Lag_{l}'], df_sub['Divergence'])
        
        # Split into top 33% and bottom 33%
        terc = pd.qcut(df_sub[f'Div_Lag_{l}'], q=3, labels=['Under', 'Neutral', 'Over'])
        ret_over = df_sub[terc == 'Over']['Return'].mean()
        ret_under = df_sub[terc == 'Under']['Return'].mean()
        wr_over = (df_sub[terc == 'Over']['Return'] > 0).mean() * 100
        wr_under = (df_sub[terc == 'Under']['Return'] > 0).mean() * 100
        
        res_lags.append({
            'Lookback Window': f"{l} Maand{'en' if l > 1 else ''}",
            'Corr -> Return': c_ret,
            'p-value': p_ret,
            'Overperf Return (%)': ret_over,
            'Underperf Return (%)': ret_under,
            'Spread Return (%)': ret_over - ret_under,
            'Overperf WinRate (%)': wr_over,
            'Underperf WinRate (%)': wr_under,
            'Spread WinRate (%)': wr_over - wr_under
        })
    return pd.DataFrame(res_lags).set_index('Lookback Window')

print("\n=== SPX MULTI-LOOKBACK WINDOW TEST ===")
spx_lags = test_lags(load_monthly_series('data/indices/SPX.csv', '^GSPC', 1950), 'SPX')
print(spx_lags.round(2).to_string())

print("\n=== NASDAQ MULTI-LOOKBACK WINDOW TEST ===")
nasdaq_lags = test_lags(load_monthly_series('data/indices/Nasdaq.csv', '^IXIC', 1971), 'Nasdaq')
print(nasdaq_lags.round(2).to_string())

print("\n=== BITCOIN MULTI-LOOKBACK WINDOW TEST ===")
btc_lags = test_lags(load_monthly_series('data/crypto/Bitcoin.csv', 'BTC-USD', 2014), 'Bitcoin')
print(btc_lags.round(2).to_string())
