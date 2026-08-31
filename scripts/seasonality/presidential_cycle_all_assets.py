"""
Full Presidential Cycle Seasonality: SPX vs QQQ vs SMH
======================================================
Comprehensive 4-Year Presidential Cycle comparison across all measurement windows:
1. OpEx-tot-OpEx (3rd Friday to 3rd Friday)
2. Kalendermaand (EOM-to-EOM)
3. 15e-tot-15e (Mid-Month)
4. 1e-tot-1e (SOM-to-SOM)

Cycle Definitions:
- Year 1 (jaar % 4 == 1): Post-Election  (2001, 2005, 2009, 2013, 2017, 2021, 2025)
- Year 2 (jaar % 4 == 2): Midterm        (2002, 2006, 2010, 2014, 2018, 2022, 2026)
- Year 3 (jaar % 4 == 3): Pre-Election   (2003, 2007, 2011, 2015, 2019, 2023)
- Year 0 (jaar % 4 == 0): Election Year  (2004, 2008, 2012, 2016, 2020, 2024)
"""
from pathlib import Path
import pandas as pd
import numpy as np
import datetime
import calendar
import warnings
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.colors import LinearSegmentedColormap

warnings.filterwarnings("ignore")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
FIGURES_DIR = BASE_DIR / "reports" / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

CYCLE_CONFIG = [
    (1, "Post-Election (Jaar 1)", "2001, 2005, 2009, 2013, 2017, 2021, 2025"),
    (2, "Midterm (Jaar 2)",       "2002, 2006, 2010, 2014, 2018, 2022, 2026"),
    (3, "Pre-Election (Jaar 3)",  "2003, 2007, 2011, 2015, 2019, 2023"),
    (0, "Election Year (Jaar 4)", "2004, 2008, 2012, 2016, 2020, 2024")
]

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

def compute_all_windows(series, start_year=2001):
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

returns_dict = {ticker: compute_all_windows(series, start_year=2001) for ticker, series in assets.items()}

# Generate detailed text output for each cycle phase
for key, title, years_str in CYCLE_CONFIG:
    filt = lambda y, k=key: y % 4 == k
    print("=" * 95)
    print(f" {title.upper()} — ({years_str})")
    print("=" * 95)
    
    # 1. OpEx-tot-OpEx
    print("\n--- OPEX-TOT-OPEX (3e Vrijdag tot 3e Vrijdag) ---")
    st_spx_op = aggregate_stats(returns_dict['SPX']['OpEx-tot-OpEx'], filt)
    st_qqq_op = aggregate_stats(returns_dict['QQQ']['OpEx-tot-OpEx'], filt)
    st_smh_op = aggregate_stats(returns_dict['SMH']['OpEx-tot-OpEx'], filt)
    
    df_op = pd.DataFrame({
        'N': st_spx_op['N'],
        'SPX_WR%': st_spx_op['WinRate'], 'SPX_Avg%': st_spx_op['AvgRet'],
        'QQQ_WR%': st_qqq_op['WinRate'], 'QQQ_Avg%': st_qqq_op['AvgRet'],
        'SMH_WR%': st_smh_op['WinRate'], 'SMH_Avg%': st_smh_op['AvgRet'],
        'Alpha_SMH_SPX': st_smh_op['AvgRet'] - st_spx_op['AvgRet'],
        'Alpha_QQQ_SPX': st_qqq_op['AvgRet'] - st_spx_op['AvgRet']
    })
    print(df_op.round(2).to_string())
    
    # 2. Kalender (EOM-tot-EOM)
    print("\n--- KALENDER (EOM-tot-EOM) ---")
    st_spx_eom = aggregate_stats(returns_dict['SPX']['Kalender (EOM)'], filt)
    st_qqq_eom = aggregate_stats(returns_dict['QQQ']['Kalender (EOM)'], filt)
    st_smh_eom = aggregate_stats(returns_dict['SMH']['Kalender (EOM)'], filt)
    
    df_eom = pd.DataFrame({
        'N': st_spx_eom['N'],
        'SPX_WR%': st_spx_eom['WinRate'], 'SPX_Avg%': st_spx_eom['AvgRet'],
        'QQQ_WR%': st_qqq_eom['WinRate'], 'QQQ_Avg%': st_qqq_eom['AvgRet'],
        'SMH_WR%': st_smh_eom['WinRate'], 'SMH_Avg%': st_smh_eom['AvgRet'],
        'Alpha_SMH_SPX': st_smh_eom['AvgRet'] - st_spx_eom['AvgRet']
    })
    print(df_eom.round(2).to_string())
    print("\n")

# =========================================================================
# VISUALISATIES MAKEN
# =========================================================================
# Figure 1: 4-Row Bar Chart (1 row per cycle year, comparing SPX, QQQ, SMH for OpEx)
fig, axes = plt.subplots(4, 1, figsize=(16, 22), sharex=True)
fig.suptitle("Presidential Cycle Seasonality Vergelijking: SPX vs QQQ vs SMH (OpEx-tot-OpEx)\n(2001 - 2026)",
             fontsize=15, fontweight="bold", y=0.99)

x = np.arange(12)
bar_w = 0.27

for idx, (key, title, years_str) in enumerate(CYCLE_CONFIG):
    ax = axes[idx]
    filt = lambda y, k=key: y % 4 == k
    
    s_spx = aggregate_stats(returns_dict['SPX']['OpEx-tot-OpEx'], filt)['AvgRet']
    s_qqq = aggregate_stats(returns_dict['QQQ']['OpEx-tot-OpEx'], filt)['AvgRet']
    s_smh = aggregate_stats(returns_dict['SMH']['OpEx-tot-OpEx'], filt)['AvgRet']
    
    bars1 = ax.bar(x - bar_w, s_spx, bar_w, label='SPX (S&P 500)', color='#1f3c88', alpha=0.9)
    bars2 = ax.bar(x,         s_qqq, bar_w, label='QQQ (Nasdaq 100)', color='#07b1ca', alpha=0.9)
    bars3 = ax.bar(x + bar_w, s_smh, bar_w, label='SMH (Semiconductors)', color='#f2711c', alpha=0.9)
    
    ax.axhline(0, color='black', linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(MONTHS, fontsize=10, fontweight='bold')
    ax.set_ylabel("Gem. Rendement (%)", fontsize=10)
    ax.set_title(f"{title}  ·  [{years_str}]", fontsize=12, fontweight='bold', pad=8)
    ax.grid(axis='y', alpha=0.3)
    ax.legend(loc='upper left', framealpha=0.9, fontsize=9)
    
    # Annotate bar values
    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            h = bar.get_height()
            if not np.isnan(h) and abs(h) > 0.05:
                va = 'bottom' if h >= 0 else 'top'
                y_pos = h + (0.15 if h >= 0 else -0.35)
                ax.text(bar.get_x() + bar.get_width()/2, y_pos, f"{h:+.1f}",
                        ha='center', va=va, fontsize=6.5, color='black')

plt.tight_layout(rect=[0, 0, 1, 0.98])
fig_path1 = FIGURES_DIR / "presidential_cycle_spx_qqq_smh_opex.png"
plt.savefig(fig_path1, dpi=150, bbox_inches="tight")
plt.close()
print(f"Grafiek 1 opgeslagen: {fig_path1}")

# Figure 2: Heatmap per asset across the 4 cycle phases
fig, axes = plt.subplots(3, 4, figsize=(22, 14))
fig.suptitle("Presidential Cycle Heatmaps: Gemiddeld Rendement (%) & Win Rate (%)\nSPX vs QQQ vs SMH (OpEx-tot-OpEx)",
             fontsize=15, fontweight="bold", y=0.99)

cmap = LinearSegmentedColormap.from_list("rdgrn", ["#c0392b", "#f8f9fa", "#27ae60"])

ticker_list = ['SPX', 'QQQ', 'SMH']

for row_idx, ticker in enumerate(ticker_list):
    for col_idx, (key, title, _) in enumerate(CYCLE_CONFIG):
        ax = axes[row_idx, col_idx]
        filt = lambda y, k=key: y % 4 == k
        st = aggregate_stats(returns_dict[ticker]['OpEx-tot-OpEx'], filt)
        
        avg_vals = st['AvgRet'].values.reshape(1, -1)
        vmax = 6.0
        im = ax.imshow(avg_vals, cmap=cmap, aspect='auto', vmin=-vmax, vmax=vmax)
        
        for m_idx, m_name in enumerate(MONTHS):
            avg_v = st.loc[m_name, 'AvgRet']
            wr_v = st.loc[m_name, 'WinRate']
            n_v = int(st.loc[m_name, 'N'])
            if not np.isnan(avg_v):
                sign = "+" if avg_v >= 0 else ""
                txt_col = "white" if abs(avg_v) > 3.2 else "black"
                ax.text(m_idx, 0, f"{sign}{avg_v:.1f}%\n{wr_v:.0f}% WR\n(N={n_v})",
                        ha='center', va='center', fontsize=7.5, color=txt_col, fontweight='bold')
                
        ax.set_xticks(range(12))
        ax.set_xticklabels(MONTHS, fontsize=8)
        ax.set_yticks([])
        ax.set_title(f"{ticker} — {title.split(' ')[0]}", fontsize=10, fontweight='bold')

plt.tight_layout(rect=[0, 0, 1, 0.97])
fig_path2 = FIGURES_DIR / "presidential_cycle_heatmap_matrix.png"
plt.savefig(fig_path2, dpi=150, bbox_inches="tight")
plt.close()
print(f"Grafiek 2 opgeslagen: {fig_path2}")
