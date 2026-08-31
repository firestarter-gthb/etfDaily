"""
Shifted OpEx Seasonality Comparison: -7 Days vs Original OpEx vs +7 Days
========================================================================
Analyzes 3 expiration-anchored timing situations across the 4-year Presidential Cycle:
1. -7 Dagen (1 week vóór OpEx / 2e vrijdag)
2. Origineel (OpEx / 3e vrijdag)
3. +7 Dagen (1 week ná OpEx / 4e vrijdag)

For SPX, QQQ, and SMH (2001 - 2026).
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

SHIFTS = [-7, 0, 7]
SHIFT_LABELS = {
    -7: "-7 Dagen (Week Vóór OpEx)",
     0: "Origineel (OpEx)",
     7: "+7 Dagen (Week Ná OpEx)"
}
SHIFT_SHORT = {-7: "-7d", 0: "OpEx", 7: "+7d"}

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

spx = load_data('^GSPC', 'data/indices/SPX.csv')
qqq = load_data('QQQ', 'data/indices/QQQ.csv')
smh = load_data('SMH', 'data/sectors/SMH_Semiconductors.csv')

assets = {'SPX': spx, 'QQQ': qqq, 'SMH': smh}

def get_3rd_friday(year, month):
    d = datetime.date(year, month, 1)
    while d.weekday() != 4:
        d += datetime.timedelta(days=1)
    d += datetime.timedelta(days=14)
    return pd.Timestamp(d)

def compute_shifted_returns(series, shift_days, start_year=2001):
    df_filtered = series[series.index >= f"{start_year-1}-12-01"].copy()
    max_data_date = df_filtered.index.max()
    min_y = df_filtered.index.min().year
    max_y = df_filtered.index.max().year
    
    rows = []
    for y in range(min_y, max_y + 1):
        for m in range(1, 13):
            target = get_3rd_friday(y, m) + datetime.timedelta(days=shift_days)
            if target > max_data_date:
                continue
            valid = df_filtered.index[df_filtered.index <= target]
            if len(valid) > 0 and valid[-1] >= df_filtered.index[0]:
                rows.append({'Year': y, 'Month': m, 'Price': df_filtered.loc[valid[-1]]})
    
    df_res = pd.DataFrame(rows)
    df_res['Return'] = df_res['Price'].pct_change()
    df_res = df_res.dropna(subset=['Return'])
    df_res = df_res[df_res['Year'] >= start_year]
    df_res['CycleKey'] = df_res['Year'] % 4
    return df_res

# Compute dataset for all (Asset, Shift) combinations
all_data = {}
for t_name, series in assets.items():
    all_data[t_name] = {}
    for s_val in SHIFTS:
        all_data[t_name][s_val] = compute_shifted_returns(series, s_val, start_year=2001)

def get_stats_table(df, filter_func=None):
    sub = df.copy()
    if filter_func is not None:
        sub = sub[filter_func(sub['Year'])]
    rows = []
    for m in range(1, 13):
        m_vals = sub[sub['Month'] == m]['Return'] * 100
        if len(m_vals) == 0:
            rows.append({'Month': m, 'N': 0, 'WinRate': np.nan, 'AvgRet': np.nan, 'StdDev': np.nan})
            continue
        rows.append({
            'Month': m,
            'N': len(m_vals),
            'WinRate': (m_vals > 0).mean() * 100,
            'AvgRet': m_vals.mean(),
            'StdDev': m_vals.std()
        })
    return pd.DataFrame(rows).set_index('Month')

# =========================================================================
# PRINT DETAILED COMPARISONS
# =========================================================================
print("=" * 100)
print(" VERGELIJKING: -7 DAGEN vs ORIGINEEL OPEX vs +7 DAGEN (2001 - 2026)")
print("==================================================================")

# 1. OVERALL COMPARISON (ALLE JAREN)
print("\n>>> 1. ALGEMENE SEASONALITY (ALLE JAREN) — GEMIDDELD RENDEMENT PER MAAND (%) <<<")
for t_name in ['SPX', 'QQQ', 'SMH']:
    print(f"\n--- {t_name} (Alle Jaren) ---")
    st_minus7 = get_stats_table(all_data[t_name][-7])
    st_orig   = get_stats_table(all_data[t_name][0])
    st_plus7  = get_stats_table(all_data[t_name][7])
    
    df_comp = pd.DataFrame({
        'Maand': MONTHS,
        '-7d Win%': st_minus7['WinRate'].values,
        '-7d Gem%': st_minus7['AvgRet'].values,
        'OpEx Win%': st_orig['WinRate'].values,
        'OpEx Gem%': st_orig['AvgRet'].values,
        '+7d Win%': st_plus7['WinRate'].values,
        '+7d Gem%': st_plus7['AvgRet'].values,
    }).set_index('Maand')
    print(df_comp.round(2).to_string())

# 2. COMPARISON PER PRESIDENTIAL CYCLE PHASE
for ckey, ctitle, cyears in CYCLE_CONFIG:
    print("\n" + "=" * 100)
    print(f" {ctitle.upper()} ({cyears})")
    print("=" * 100)
    filt = lambda y, k=ckey: y % 4 == k
    
    for t_name in ['SPX', 'QQQ', 'SMH']:
        print(f"\n--- {t_name} — {ctitle} ---")
        st_m7 = get_stats_table(all_data[t_name][-7], filt)
        st_0  = get_stats_table(all_data[t_name][0], filt)
        st_p7 = get_stats_table(all_data[t_name][7], filt)
        
        df_c = pd.DataFrame({
            'Maand': MONTHS,
            '-7d Win%': st_m7['WinRate'].values,
            '-7d Gem%': st_m7['AvgRet'].values,
            'OpEx Win%': st_0['WinRate'].values,
            'OpEx Gem%': st_0['AvgRet'].values,
            '+7d Win%': st_p7['WinRate'].values,
            '+7d Gem%': st_p7['AvgRet'].values,
        }).set_index('Maand')
        print(df_c.round(2).to_string())

# 3. OVERALL AGGREGATED COMPARISON (Mean Win Rate & Mean Return across all months)
print("\n" + "=" * 100)
print(" TOTALE AGGREGATIE (Gemiddelde over alle 12 maanden)")
print("=" * 100)
agg_rows = []
for t_name in ['SPX', 'QQQ', 'SMH']:
    for s_val in SHIFTS:
        st = get_stats_table(all_data[t_name][s_val])
        agg_rows.append({
            'Asset': t_name,
            'Situatie': SHIFT_LABELS[s_val],
            'Gem. Win Rate (%)': st['WinRate'].mean(),
            'Gem. Maandrendement (%)': st['AvgRet'].mean(),
            'Beste Maand': MONTHS[st['AvgRet'].idxmax() - 1] + f" ({st['AvgRet'].max():+.2f}%)",
            'Slechtste Maand': MONTHS[st['AvgRet'].idxmin() - 1] + f" ({st['AvgRet'].min():+.2f}%)"
        })
print(pd.DataFrame(agg_rows).to_string(index=False))

# =========================================================================
# GENERATE VISUAL CHARTS
# =========================================================================
print("\nGenerating visual comparison charts...")

# FIGUUR 1: 3-Panel Side-by-Side Bar Chart for All Years (SPX, QQQ, SMH across -7d, OpEx, +7d)
fig, axes = plt.subplots(3, 1, figsize=(18, 18), sharex=True)
fig.patch.set_facecolor('#fcfcfc')
fig.suptitle("OpEx Timing Vergelijking: Week Vóór OpEx (-7d) vs Origineel OpEx vs Week Ná OpEx (+7d)\n(Alle Jaren 2001 – 2026)",
             fontsize=15, fontweight="bold", y=0.99, color='#111111')

x = np.arange(12)
bar_w = 0.27

colors_shifts = {
    -7: '#3498db',  # Blauw (Week Vóór OpEx)
     0: '#2ecc71',  # Groen (Origineel OpEx)
     7: '#e67e22'   # Oranje (Week Ná OpEx)
}

for idx, (t_sym, t_title) in enumerate([('SPX', 'S&P 500 (SPX)'), ('QQQ', 'Nasdaq 100 (QQQ)'), ('SMH', 'Semiconductors (SMH)')]):
    ax = axes[idx]
    ax.set_facecolor('#ffffff')
    
    st_m7 = get_stats_table(all_data[t_sym][-7])
    st_0  = get_stats_table(all_data[t_sym][0])
    st_p7 = get_stats_table(all_data[t_sym][7])
    
    b1 = ax.bar(x - bar_w, st_m7['AvgRet'], bar_w, label='-7 Dagen (Week Vóór OpEx)', color=colors_shifts[-7], alpha=0.9)
    b2 = ax.bar(x,         st_0['AvgRet'],  bar_w, label='Origineel (OpEx - 3e Vrijdag)', color=colors_shifts[0], alpha=0.9)
    b3 = ax.bar(x + bar_w, st_p7['AvgRet'], bar_w, label='+7 Dagen (Week Ná OpEx)', color=colors_shifts[7], alpha=0.9)
    
    ax.axhline(0, color='#2c3e50', linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(MONTHS, fontsize=11, fontweight='bold')
    ax.set_ylabel("Gem. Rendement (%)", fontsize=10, fontweight='bold')
    ax.set_title(f"{t_title}", fontsize=13, fontweight='bold', pad=8, loc='left', color='#2c3e50')
    ax.grid(axis='y', linestyle='--', alpha=0.4)
    ax.legend(loc='upper left', framealpha=0.95, fontsize=9.5)
    
    for m_i in range(12):
        v1, v2, v3 = st_m7.loc[m_i+1, 'AvgRet'], st_0.loc[m_i+1, 'AvgRet'], st_p7.loc[m_i+1, 'AvgRet']
        for bar, val in [(b1[m_i], v1), (b2[m_i], v2), (b3[m_i], v3)]:
            if not np.isnan(val) and abs(val) > 0.1:
                y_pos = val + (0.18 if val >= 0 else -0.45)
                va = 'bottom' if val >= 0 else 'top'
                ax.text(bar.get_x() + bar.get_width()/2, y_pos, f"{val:+.1f}%",
                        ha='center', va=va, fontsize=6.5, fontweight='bold', color='#111111')

plt.tight_layout(rect=[0, 0, 1, 0.98])
p1 = FIGURES_DIR / "shifted_opex_comparison_all_years.png"
plt.savefig(p1, dpi=180, bbox_inches="tight")
plt.close()
print(f"Grafiek 1 opgeslagen: {p1}")

# FIGUUR 2: 4-Panel Grid for Midterm & Presidential Cycle with Shifts
fig, axes = plt.subplots(4, 3, figsize=(22, 18))
fig.patch.set_facecolor('#fcfcfc')
fig.suptitle("Presidential Cycle Shift Matrix: Gemiddeld Rendement (%) voor -7d, OpEx en +7d\nSPX, QQQ en SMH over alle 4 Cyclusjaren (2001 – 2026)",
             fontsize=16, fontweight="bold", y=0.99)

for row_idx, (ckey, ctitle, _) in enumerate(CYCLE_CONFIG):
    filt = lambda y, k=ckey: y % 4 == k
    phase_short = ctitle.split(' ')[0]
    
    for col_idx, t_sym in enumerate(['SPX', 'QQQ', 'SMH']):
        ax = axes[row_idx, col_idx]
        ax.set_facecolor('#ffffff')
        
        st_m7 = get_stats_table(all_data[t_sym][-7], filt)
        st_0  = get_stats_table(all_data[t_sym][0], filt)
        st_p7 = get_stats_table(all_data[t_sym][7], filt)
        
        ax.plot(x, st_m7['AvgRet'], marker='o', label='-7d (Vóór OpEx)', color='#3498db', linewidth=2.0, alpha=0.85)
        ax.plot(x, st_0['AvgRet'],  marker='s', label='OpEx (Origineel)', color='#2ecc71', linewidth=2.6, alpha=0.95)
        ax.plot(x, st_p7['AvgRet'], marker='^', label='+7d (Ná OpEx)', color='#e67e22', linewidth=2.0, alpha=0.85)
        
        ax.axhline(0, color='#7f8c8d', linestyle='--', linewidth=0.8)
        ax.set_xticks(x)
        ax.set_xticklabels(MONTHS, fontsize=8, fontweight='bold')
        ax.set_title(f"{t_sym} · {phase_short}", fontsize=11, fontweight='bold', color='#2c3e50')
        ax.grid(True, linestyle=':', alpha=0.4)
        if col_idx == 0:
            ax.set_ylabel(f"{phase_short}\nGem. Rend. (%)", fontsize=10, fontweight='bold')
        if row_idx == 0 and col_idx == 0:
            ax.legend(loc='upper left', fontsize=8, framealpha=0.9)

plt.tight_layout(rect=[0, 0, 1, 0.97])
p2 = FIGURES_DIR / "shifted_opex_presidential_matrix.png"
plt.savefig(p2, dpi=180, bbox_inches="tight")
plt.close()
print(f"Grafiek 2 opgeslagen: {p2}")

print("\nKlaar! Beide grafieken zijn opgeslagen in reports/figures/.")
