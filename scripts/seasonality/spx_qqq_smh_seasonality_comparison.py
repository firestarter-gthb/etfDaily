"""
Seasonality Analysis & Comparison: SPX vs QQQ vs SMH
=====================================================
Uses the established SPX seasonality methodology:
1. Start of Month (1e-tot-1e / SOM)
2. Mid-Month (15e-tot-15e / 15th-to-15th)
3. OpEx-tot-OpEx (3rd Friday to 3rd Friday)
4. End of Month (EOM / Calendar Month)

Compares:
- All Years (2006 - 2026 for consistent multi-asset history)
- Midterm Years (Year % 4 == 2: 2006, 2010, 2014, 2018, 2022, 2026)
- Full Presidential Cycle (4 cycle years)
- Relative Outperformance & Volatility profiles
"""
from pathlib import Path
import pandas as pd
import numpy as np
import datetime
import calendar
import warnings
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

warnings.filterwarnings("ignore")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
FIGURES_DIR = BASE_DIR / "reports" / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

def load_data(ticker, filepath):
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
        s = s[~s.index.duplicated(keep='first')]
        return s.sort_index()
    
    import yfinance as yf
    raw = yf.download(ticker, period='max', progress=False)
    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = raw.columns.droplevel(1)
    col = 'Adj Close' if 'Adj Close' in raw.columns else 'Close'
    s = pd.to_numeric(raw[col], errors='coerce').dropna()
    return s.sort_index()

# 1. Load Data
spx_series = load_data('^GSPC', 'data/indices/SPX.csv')
qqq_series = load_data('QQQ', 'data/indices/QQQ.csv')
smh_series = load_data('SMH', 'data/sectors/SMH_Semiconductors.csv')

assets = {
    'SPX': spx_series,
    'QQQ': qqq_series,
    'SMH': smh_series
}

def get_3rd_friday(year, month):
    d = datetime.date(year, month, 1)
    while d.weekday() != 4:
        d += datetime.timedelta(days=1)
    d += datetime.timedelta(days=14)
    return pd.Timestamp(d)

def compute_all_windows(series, start_year=2006):
    df_filtered = series[series.index >= f"{start_year-1}-12-01"].copy()
    max_data_date = df_filtered.index.max()
    
    # 1. Start of Month (SOM / 1e-tot-1e)
    som_prices = df_filtered.groupby([df_filtered.index.year, df_filtered.index.month]).first()
    som_ret = som_prices.pct_change().dropna()
    som_ret.index = pd.MultiIndex.from_tuples(
        [(y, m-1) if m > 1 else (y-1, 12) for y, m in som_ret.index],
        names=['Year', 'Month']
    )
    som_ret = som_ret[som_ret.index.get_level_values('Year') >= start_year]
    
    # 2. Mid-Month (15e-tot-15e)
    df_15 = df_filtered[df_filtered.index.day >= 15].copy()
    mid_prices = df_15.groupby([df_15.index.year, df_15.index.month]).first()
    mid_ret = mid_prices.pct_change().dropna()
    mid_ret.index = pd.MultiIndex.from_tuples(
        [(y, m-1) if m > 1 else (y-1, 12) for y, m in mid_ret.index],
        names=['Year', 'Month']
    )
    mid_ret = mid_ret[mid_ret.index.get_level_values('Year') >= start_year]
    
    # 3. End of Month (EOM / Kalender)
    eom_prices = df_filtered.groupby([df_filtered.index.year, df_filtered.index.month]).last()
    eom_ret = eom_prices.pct_change().dropna()
    eom_ret.index.names = ['Year', 'Month']
    eom_ret = eom_ret[eom_ret.index.get_level_values('Year') >= start_year]
    
    # 4. OpEx to OpEx (3rd Friday to 3rd Friday)
    min_y = df_filtered.index.min().year
    max_y = df_filtered.index.max().year
    opex_rows = []
    for y in range(min_y, max_y + 1):
        for m in range(1, 13):
            target = get_3rd_friday(y, m)
            if target > max_data_date:
                continue
            valid = df_filtered.index[df_filtered.index <= target]
            if len(valid) > 0 and valid[-1] >= df_filtered.index[0]:
                opex_rows.append({'Year': y, 'Month': m, 'Price': df_filtered.loc[valid[-1]]})
    
    df_opex = pd.DataFrame(opex_rows)
    df_opex['Return'] = df_opex['Price'].pct_change()
    df_opex = df_opex.dropna(subset=['Return'])
    df_opex = df_opex[df_opex['Year'] >= start_year]
    df_opex.set_index(['Year', 'Month'], inplace=True)
    opex_ret = df_opex['Return']
    
    return {
        '1e-tot-1e': som_ret,
        '15e-tot-15e': mid_ret,
        'OpEx-tot-OpEx': opex_ret,
        'Kalender (EOM)': eom_ret
    }

def aggregate_stats(ret_series, filter_func=None):
    s = ret_series.copy()
    if filter_func is not None:
        years = s.index.get_level_values('Year')
        s = s[filter_func(years)]
    
    rows = []
    for m in range(1, 13):
        m_vals = s[s.index.get_level_values('Month') == m] * 100
        if len(m_vals) == 0:
            rows.append({
                'Maand': MONTHS[m-1], 'N': 0, 'WinRate': np.nan,
                'AvgRet': np.nan, 'MedianRet': np.nan, 'StdDev': np.nan,
                'Best': np.nan, 'Worst': np.nan
            })
            continue
        wr = (m_vals > 0).mean() * 100
        avg = m_vals.mean()
        med = m_vals.median()
        sd = m_vals.std()
        best = m_vals.max()
        worst = m_vals.min()
        rows.append({
            'Maand': MONTHS[m-1],
            'N': len(m_vals),
            'WinRate': wr,
            'AvgRet': avg,
            'MedianRet': med,
            'StdDev': sd,
            'Best': best,
            'Worst': worst
        })
    return pd.DataFrame(rows).set_index('Maand')

returns_dict = {ticker: compute_all_windows(series, start_year=2006) for ticker, series in assets.items()}

print("=" * 90)
print(" VERGELIJKING SEASONALITY: SPX vs QQQ vs SMH (2006 - 2026)")
print("=" * 90)

# PART 1: ALL YEARS - OpEx to OpEx Comparison
print("\n>>> DEEL 1: ALGEMENE SEASONALITY (ALLE JAREN: 2006 - 2026) - OPEX-TOT-OPEX <<<")
opex_all = {t: aggregate_stats(returns_dict[t]['OpEx-tot-OpEx']) for t in ['SPX', 'QQQ', 'SMH']}
comp_opex_all = pd.DataFrame({
    'SPX_WR%': opex_all['SPX']['WinRate'],
    'SPX_Avg%': opex_all['SPX']['AvgRet'],
    'QQQ_WR%': opex_all['QQQ']['WinRate'],
    'QQQ_Avg%': opex_all['QQQ']['AvgRet'],
    'SMH_WR%': opex_all['SMH']['WinRate'],
    'SMH_Avg%': opex_all['SMH']['AvgRet'],
    'Alpha_QQQ_SPX': opex_all['QQQ']['AvgRet'] - opex_all['SPX']['AvgRet'],
    'Alpha_SMH_SPX': opex_all['SMH']['AvgRet'] - opex_all['SPX']['AvgRet']
})
print(comp_opex_all.round(2).to_string())

# PART 2: ALL YEARS - Calendar (EOM) Comparison
print("\n>>> DEEL 2: ALGEMENE SEASONALITY (ALLE JAREN: 2006 - 2026) - KALENDER (EOM) <<<")
eom_all = {t: aggregate_stats(returns_dict[t]['Kalender (EOM)']) for t in ['SPX', 'QQQ', 'SMH']}
comp_eom_all = pd.DataFrame({
    'SPX_WR%': eom_all['SPX']['WinRate'],
    'SPX_Avg%': eom_all['SPX']['AvgRet'],
    'QQQ_WR%': eom_all['QQQ']['WinRate'],
    'QQQ_Avg%': eom_all['QQQ']['AvgRet'],
    'SMH_WR%': eom_all['SMH']['WinRate'],
    'SMH_Avg%': eom_all['SMH']['AvgRet'],
    'Alpha_SMH_SPX': eom_all['SMH']['AvgRet'] - eom_all['SPX']['AvgRet']
})
print(comp_eom_all.round(2).to_string())

# PART 3: MIDTERM YEARS ONLY
print("\n>>> DEEL 3: MIDTERM JAREN (2006, 2010, 2014, 2018, 2022, 2026) <<<")
midterm_filter = lambda y: y % 4 == 2

for window in ['OpEx-tot-OpEx', '15e-tot-15e', '1e-tot-1e', 'Kalender (EOM)']:
    print(f"\n--- Venster: {window} (Midterm Jaren) ---")
    st_spx = aggregate_stats(returns_dict['SPX'][window], midterm_filter)
    st_qqq = aggregate_stats(returns_dict['QQQ'][window], midterm_filter)
    st_smh = aggregate_stats(returns_dict['SMH'][window], midterm_filter)
    
    df_window = pd.DataFrame({
        'SPX_WR%': st_spx['WinRate'],
        'SPX_Avg%': st_spx['AvgRet'],
        'QQQ_WR%': st_qqq['WinRate'],
        'QQQ_Avg%': st_qqq['AvgRet'],
        'SMH_WR%': st_smh['WinRate'],
        'SMH_Avg%': st_smh['AvgRet'],
        'SMH_vs_SPX': st_smh['AvgRet'] - st_spx['AvgRet']
    })
    print(df_window.round(2).to_string())

# Plotting figures
fig, axes = plt.subplots(2, 2, figsize=(18, 12))
fig.suptitle("Seasonality Vergelijking: S&P 500 (SPX) vs Nasdaq 100 (QQQ) vs Semiconductors (SMH)\n(Periode: 2006 - 2026)",
             fontsize=14, fontweight="bold")

x = np.arange(12)
width = 0.26

# Plot 1: All Years - OpEx-to-OpEx
ax = axes[0, 0]
ax.bar(x - width, opex_all['SPX']['AvgRet'], width, label='SPX', color='#2c3e50', alpha=0.9)
ax.bar(x, opex_all['QQQ']['AvgRet'], width, label='QQQ', color='#2980b9', alpha=0.9)
ax.bar(x + width, opex_all['SMH']['AvgRet'], width, label='SMH', color='#e67e22', alpha=0.9)
ax.axhline(0, color='black', linewidth=0.8)
ax.set_xticks(x)
ax.set_xticklabels(MONTHS)
ax.set_ylabel("Gem. Rendement (%)")
ax.set_title("Alle Jaren: OpEx-tot-OpEx Gemiddeld Rendement", fontweight='bold')
ax.legend()
ax.grid(axis='y', alpha=0.3)

# Plot 2: All Years - Win Rate (OpEx)
ax = axes[0, 1]
ax.bar(x - width, opex_all['SPX']['WinRate'], width, label='SPX', color='#2c3e50', alpha=0.9)
ax.bar(x, opex_all['QQQ']['WinRate'], width, label='QQQ', color='#2980b9', alpha=0.9)
ax.bar(x + width, opex_all['SMH']['WinRate'], width, label='SMH', color='#e67e22', alpha=0.9)
ax.axhline(50, color='red', linestyle='--', linewidth=0.8, label='50% Win Rate')
ax.set_xticks(x)
ax.set_xticklabels(MONTHS)
ax.set_ylabel("Winstkans (%)")
ax.set_title("Alle Jaren: OpEx-tot-OpEx Winstkans (%)", fontweight='bold')
ax.legend()
ax.grid(axis='y', alpha=0.3)

# Plot 3: Midterm Years - OpEx-to-OpEx
st_spx_mid = aggregate_stats(returns_dict['SPX']['OpEx-tot-OpEx'], midterm_filter)
st_qqq_mid = aggregate_stats(returns_dict['QQQ']['OpEx-tot-OpEx'], midterm_filter)
st_smh_mid = aggregate_stats(returns_dict['SMH']['OpEx-tot-OpEx'], midterm_filter)

ax = axes[1, 0]
ax.bar(x - width, st_spx_mid['AvgRet'], width, label='SPX', color='#2c3e50', alpha=0.9)
ax.bar(x, st_qqq_mid['AvgRet'], width, label='QQQ', color='#2980b9', alpha=0.9)
ax.bar(x + width, st_smh_mid['AvgRet'], width, label='SMH', color='#e67e22', alpha=0.9)
ax.axhline(0, color='black', linewidth=0.8)
ax.set_xticks(x)
ax.set_xticklabels(MONTHS)
ax.set_ylabel("Gem. Rendement (%)")
ax.set_title("Midterm Jaren: OpEx-tot-OpEx Gemiddeld Rendement", fontweight='bold')
ax.legend()
ax.grid(axis='y', alpha=0.3)

# Plot 4: Midterm Years - 15th-to-15th (Mid-Month)
st_spx_15 = aggregate_stats(returns_dict['SPX']['15e-tot-15e'], midterm_filter)
st_qqq_15 = aggregate_stats(returns_dict['QQQ']['15e-tot-15e'], midterm_filter)
st_smh_15 = aggregate_stats(returns_dict['SMH']['15e-tot-15e'], midterm_filter)

ax = axes[1, 1]
ax.bar(x - width, st_spx_15['AvgRet'], width, label='SPX', color='#2c3e50', alpha=0.9)
ax.bar(x, st_qqq_15['AvgRet'], width, label='QQQ', color='#2980b9', alpha=0.9)
ax.bar(x + width, st_smh_15['AvgRet'], width, label='SMH', color='#e67e22', alpha=0.9)
ax.axhline(0, color='black', linewidth=0.8)
ax.set_xticks(x)
ax.set_xticklabels(MONTHS)
ax.set_ylabel("Gem. Rendement (%)")
ax.set_title("Midterm Jaren: 15e-tot-15e Gemiddeld Rendement", fontweight='bold')
ax.legend()
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
chart_path = FIGURES_DIR / "seasonality_spx_qqq_smh_comparison.png"
plt.savefig(chart_path, dpi=150, bbox_inches="tight")
plt.close()
print(f"\nGrafiek opgeslagen: {chart_path}")
