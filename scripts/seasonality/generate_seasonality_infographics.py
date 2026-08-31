"""
Generate Premium Infographics for Presidential Cycle Seasonality: SPX vs QQQ vs SMH
====================================================================================
Creates 4 high-resolution visual charts:
1. presidential_cycle_4phases_comparison.png (Side-by-side bar chart per cycle phase)
2. presidential_cycle_heatmap_matrix.png (3x4 Heatmap matrix with stats in each cell)
3. presidential_cycle_cumulative_trajectory.png (48-month composite Presidential Cycle trajectory)
4. smh_alpha_by_cycle_phase.png (Monthly Alpha/Spread of SMH vs SPX across all 4 phases)
"""
from pathlib import Path
import pandas as pd
import numpy as np
import datetime
import calendar
import warnings
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap

warnings.filterwarnings("ignore")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
FIGURES_DIR = BASE_DIR / "reports" / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

CYCLE_CONFIG = [
    (1, "Post-Election (Jaar 1)", "2001 · 2005 · 2009 · 2013 · 2017 · 2021 · 2025", "#2ecc71"),
    (2, "Midterm Year (Jaar 2)",   "2002 · 2006 · 2010 · 2014 · 2018 · 2022 · 2026", "#e74c3c"),
    (3, "Pre-Election (Jaar 3)",  "2003 · 2007 · 2011 · 2015 · 2019 · 2023",        "#3498db"),
    (0, "Election Year (Jaar 4)", "2004 · 2008 · 2012 · 2016 · 2020 · 2024",        "#9b59b6")
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

def compute_opex_returns(series, start_year=2001):
    df_filtered = series[series.index >= f"{start_year-1}-12-01"].copy()
    max_data_date = df_filtered.index.max()
    min_y = df_filtered.index.min().year
    max_y = df_filtered.index.max().year
    
    rows = []
    for y in range(min_y, max_y + 1):
        for m in range(1, 13):
            target = get_3rd_friday(y, m)
            if target > max_data_date:
                continue
            valid = df_filtered.index[df_filtered.index <= target]
            if len(valid) > 0 and valid[-1] >= df_filtered.index[0]:
                rows.append({'Year': y, 'Month': m, 'Price': df_filtered.loc[valid[-1]]})
    
    df_op = pd.DataFrame(rows)
    df_op['Return'] = df_op['Price'].pct_change()
    df_op = df_op.dropna(subset=['Return'])
    df_op = df_op[df_op['Year'] >= start_year]
    df_op['CycleKey'] = df_op['Year'] % 4
    return df_op

opex_dfs = {t: compute_opex_returns(s, start_year=2001) for t, s in assets.items()}

def get_stats(df, cycle_key):
    sub = df[df['CycleKey'] == cycle_key]
    rows = []
    for m in range(1, 13):
        m_data = sub[sub['Month'] == m]['Return'] * 100
        if len(m_data) == 0:
            rows.append({'Month': m, 'N': 0, 'WinRate': np.nan, 'AvgRet': np.nan, 'StdDev': np.nan})
            continue
        wr = (m_data > 0).mean() * 100
        avg = m_data.mean()
        sd = m_data.std()
        rows.append({'Month': m, 'N': len(m_data), 'WinRate': wr, 'AvgRet': avg, 'StdDev': sd})
    return pd.DataFrame(rows).set_index('Month')

# =========================================================================
# 1. FIGUUR 1: 4-FASEN VERGELIJKING (BAR CHARTS MET DETAILS)
# =========================================================================
print("Generating Chart 1: 4-Phases Bar Comparison...")
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
fig, axes = plt.subplots(4, 1, figsize=(17, 24), sharex=True)
fig.patch.set_facecolor('#fcfcfc')
fig.suptitle("Presidentiële Cyclus Seizoenspatronen (2001 – 2026)\nSPX (S&P 500) vs QQQ (Nasdaq 100) vs SMH (Semiconductors) — OpEx-tot-OpEx",
             fontsize=16, fontweight="bold", y=0.99, color='#111111')

x = np.arange(12)
bar_w = 0.26

color_spx = '#1e3799'
color_qqq = '#00a8ff'
color_smh = '#e67e22'

for idx, (ckey, ctitle, cyears, cbadge) in enumerate(CYCLE_CONFIG):
    ax = axes[idx]
    ax.set_facecolor('#ffffff')
    
    st_spx = get_stats(opex_dfs['SPX'], ckey)
    st_qqq = get_stats(opex_dfs['QQQ'], ckey)
    st_smh = get_stats(opex_dfs['SMH'], ckey)
    
    b1 = ax.bar(x - bar_w, st_spx['AvgRet'], bar_w, label='SPX (S&P 500)', color=color_spx, alpha=0.92, edgecolor='none')
    b2 = ax.bar(x,         st_qqq['AvgRet'], bar_w, label='QQQ (Nasdaq 100)', color=color_qqq, alpha=0.92, edgecolor='none')
    b3 = ax.bar(x + bar_w, st_smh['AvgRet'], bar_w, label='SMH (Semiconductors)', color=color_smh, alpha=0.95, edgecolor='none')
    
    ax.axhline(0, color='#2c3e50', linewidth=0.9)
    ax.set_xticks(x)
    ax.set_xticklabels(MONTHS, fontsize=11, fontweight='bold')
    ax.set_ylabel("Gemiddeld Rendement (%)", fontsize=10, fontweight='bold')
    ax.set_title(f"{ctitle}  ·  [{cyears}]", fontsize=12, fontweight='bold', pad=10, loc='left', color='#2c3e50')
    ax.grid(axis='y', linestyle='--', alpha=0.5)
    ax.legend(loc='upper left', framealpha=0.95, fontsize=9.5)
    
    # Annotate returns and win rates
    for m_i in range(12):
        v_spx, wr_spx = st_spx.loc[m_i+1, 'AvgRet'], st_spx.loc[m_i+1, 'WinRate']
        v_qqq, wr_qqq = st_qqq.loc[m_i+1, 'AvgRet'], st_qqq.loc[m_i+1, 'WinRate']
        v_smh, wr_smh = st_smh.loc[m_i+1, 'AvgRet'], st_smh.loc[m_i+1, 'WinRate']
        
        for bar, val, wr in [(b1[m_i], v_spx, wr_spx), (b2[m_i], v_qqq, wr_qqq), (b3[m_i], v_smh, wr_smh)]:
            if not np.isnan(val) and abs(val) > 0.05:
                y_pos = val + (0.2 if val >= 0 else -0.55)
                va = 'bottom' if val >= 0 else 'top'
                ax.text(bar.get_x() + bar.get_width()/2, y_pos, f"{val:+.1f}%\n({wr:.0f}%)",
                        ha='center', va=va, fontsize=6.2, fontweight='bold', color='#111111')

plt.tight_layout(rect=[0, 0, 1, 0.98])
p1 = FIGURES_DIR / "presidential_cycle_4phases_comparison.png"
plt.savefig(p1, dpi=180, bbox_inches="tight")
plt.close()
print(f"Chart 1 saved to: {p1}")

# =========================================================================
# 2. FIGUUR 2: 3x4 HEATMAP MATRIX
# =========================================================================
print("Generating Chart 2: 3x4 Heatmap Matrix...")
fig, axes = plt.subplots(3, 4, figsize=(22, 13))
fig.patch.set_facecolor('#fcfcfc')
fig.suptitle("Presidentiële Cyclus Seizoens-Matrix: SPX vs QQQ vs SMH (OpEx-tot-OpEx)\nGemiddeld Rendement (%) en Winstkans (%) per Cyclusfase (2001 – 2026)",
             fontsize=16, fontweight="bold", y=0.99)

cmap = LinearSegmentedColormap.from_list("rdgrn", ["#c0392b", "#f9f9f9", "#27ae60"])

ticker_list = [('SPX', 'S&P 500 (SPX)'), ('QQQ', 'Nasdaq 100 (QQQ)'), ('SMH', 'Semiconductors (SMH)')]

for row_idx, (t_sym, t_name) in enumerate(ticker_list):
    for col_idx, (ckey, ctitle, cyears, _) in enumerate(CYCLE_CONFIG):
        ax = axes[row_idx, col_idx]
        st = get_stats(opex_dfs[t_sym], ckey)
        
        avg_vals = st['AvgRet'].values.reshape(1, -1)
        vmax = 7.0
        im = ax.imshow(avg_vals, cmap=cmap, aspect='auto', vmin=-vmax, vmax=vmax)
        
        for m_idx, m_name in enumerate(MONTHS):
            avg_v = st.loc[m_idx+1, 'AvgRet']
            wr_v = st.loc[m_idx+1, 'WinRate']
            n_v = int(st.loc[m_idx+1, 'N'])
            if not np.isnan(avg_v):
                sign = "+" if avg_v >= 0 else ""
                txt_col = "white" if abs(avg_v) > 3.4 else "#111111"
                ax.text(m_idx, 0, f"{sign}{avg_v:.1f}%\n{wr_v:.0f}% WR\n(N={n_v})",
                        ha='center', va='center', fontsize=7.2, color=txt_col, fontweight='bold')
                
        ax.set_xticks(range(12))
        ax.set_xticklabels(MONTHS, fontsize=8, fontweight='bold')
        ax.set_yticks([])
        phase_short = ctitle.split(' ')[0]
        ax.set_title(f"{t_sym} · {phase_short}", fontsize=11, fontweight='bold', pad=6, color='#2c3e50')
        if col_idx == 0:
            ax.set_ylabel(t_sym, fontsize=12, fontweight='bold', labelpad=10)

plt.tight_layout(rect=[0, 0, 1, 0.97])
p2 = FIGURES_DIR / "presidential_cycle_heatmap_matrix_full.png"
plt.savefig(p2, dpi=180, bbox_inches="tight")
plt.close()
print(f"Chart 2 saved to: {p2}")

# =========================================================================
# 3. FIGUUR 3: CUMULATIEVE 48-MAANDEN PRESIDENTIAL CYCLE TRAJECTORY
# =========================================================================
print("Generating Chart 3: Cumulative 48-Month Trajectory...")
fig, ax = plt.subplots(figsize=(18, 9))
fig.patch.set_facecolor('#fcfcfc')
ax.set_facecolor('#ffffff')

# Build the 48-month composite cycle for each asset (starting at 100)
# Month 1 = Post-Election Jan ... Month 48 = Election Dec
cycle_months_labels = []
for ckey, ctitle, _, _ in CYCLE_CONFIG:
    p_name = ctitle.split(' ')[0]
    for m in MONTHS:
        cycle_months_labels.append(f"{p_name}\n{m}")

trajectories = {}
for t in ['SPX', 'QQQ', 'SMH']:
    monthly_series = []
    for ckey, _, _, _ in CYCLE_CONFIG:
        st = get_stats(opex_dfs[t], ckey)
        monthly_series.extend(st['AvgRet'].values / 100.0)
    
    # Cumulative return starting at $10,000
    cum = [10000.0]
    for r in monthly_series:
        cum.append(cum[-1] * (1.0 + r))
    trajectories[t] = cum

x_axis = np.arange(49)

ax.plot(x_axis, trajectories['SPX'], label='SPX (S&P 500)', color='#1e3799', linewidth=2.8, alpha=0.95)
ax.plot(x_axis, trajectories['QQQ'], label='QQQ (Nasdaq 100)', color='#00a8ff', linewidth=3.0, alpha=0.95)
ax.plot(x_axis, trajectories['SMH'], label='SMH (Semiconductors)', color='#e67e22', linewidth=3.2, alpha=0.95)

# Highlight cycle boundaries
for boundary in [12, 24, 36]:
    ax.axvline(boundary, color='#7f8c8d', linestyle='--', linewidth=1.2, alpha=0.7)

# Background phase shadings
ax.axvspan(0, 12, color='#2ecc71', alpha=0.06, label='Jaar 1: Post-Election')
ax.axvspan(12, 24, color='#e74c3c', alpha=0.06, label='Jaar 2: Midterm')
ax.axvspan(24, 36, color='#3498db', alpha=0.06, label='Jaar 3: Pre-Election')
ax.axvspan(36, 48, color='#9b59b6', alpha=0.06, label='Jaar 4: Election Year')

# Annotations of key turning points
ax.annotate('Midterm Bodem & Breakout\n(Nov: SMH +10.3%)', xy=(23, trajectories['SMH'][23]), xytext=(17, trajectories['SMH'][23] + 2500),
            arrowprops=dict(facecolor='#e67e22', arrowstyle='->', lw=2),
            fontsize=10, fontweight='bold', color='#c0392b',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#fff0f0', edgecolor='#e74c3c'))

ax.annotate('Pre-Election Boom\n(Sep: SMH +8.0%, QQQ +7.1%)', xy=(33, trajectories['SMH'][33]), xytext=(28, trajectories['SMH'][33] + 3000),
            arrowprops=dict(facecolor='#00a8ff', arrowstyle='->', lw=2),
            fontsize=10, fontweight='bold', color='#2980b9',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#eef7fd', edgecolor='#3498db'))

ax.annotate('Election Relief Rally\n(Dec: QQQ +5.6%, SMH +5.3%)', xy=(48, trajectories['SMH'][48]), xytext=(40, trajectories['SMH'][48] + 2000),
            arrowprops=dict(facecolor='#27ae60', arrowstyle='->', lw=2),
            fontsize=10, fontweight='bold', color='#27ae60',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#eafaf1', edgecolor='#2ecc71'))

ax.set_xticks(np.arange(0, 49, 2))
tick_labels = ['Start'] + [cycle_months_labels[i] for i in range(1, 48, 2)]
ax.set_xticklabels(tick_labels, fontsize=8, fontweight='bold')
ax.set_ylabel("Geaccumuleerde Waarde ($ van $10.000 Start)", fontsize=11, fontweight='bold')
ax.set_title("Geaccumuleerde 48-Maanden Cyclus: SPX vs QQQ vs SMH (OpEx-tot-OpEx)\nVerloop van een gemiddelde 4-jarige Presidentiële Termijn",
             fontsize=14, fontweight="bold", pad=12, color='#2c3e50')
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"${y:,.0f}"))
ax.grid(True, linestyle='--', alpha=0.5)
ax.legend(loc='upper left', framealpha=0.95, fontsize=10.5)

plt.tight_layout()
p3 = FIGURES_DIR / "presidential_cycle_cumulative_trajectory.png"
plt.savefig(p3, dpi=180, bbox_inches="tight")
plt.close()
print(f"Chart 3 saved to: {p3}")

# =========================================================================
# 4. FIGUUR 4: SMH ALPHA MATRIX T.O.V. SPX
# =========================================================================
print("Generating Chart 4: SMH Alpha / Spread...")
fig, ax = plt.subplots(figsize=(16, 7))
fig.patch.set_facecolor('#fcfcfc')
ax.set_facecolor('#ffffff')

alpha_data = []
for ckey, _, _, _ in CYCLE_CONFIG:
    st_spx = get_stats(opex_dfs['SPX'], ckey)
    st_smh = get_stats(opex_dfs['SMH'], ckey)
    alpha = st_smh['AvgRet'] - st_spx['AvgRet']
    alpha_data.append(alpha.values)

alpha_matrix = np.array(alpha_data)

cmap_alpha = LinearSegmentedColormap.from_list("alpha_cmap", ["#e74c3c", "#f7f7f7", "#27ae60"])
vmax_a = 6.5

im = ax.imshow(alpha_matrix, cmap=cmap_alpha, aspect='auto', vmin=-vmax_a, vmax=vmax_a)

for r_i in range(4):
    for c_i in range(12):
        val = alpha_matrix[r_i, c_i]
        if not np.isnan(val):
            sign = "+" if val >= 0 else ""
            txt_col = "white" if abs(val) > 3.0 else "#111111"
            ax.text(c_i, r_i, f"{sign}{val:.2f}%", ha='center', va='center', fontsize=9.5, fontweight='bold', color=txt_col)

ax.set_xticks(range(12))
ax.set_xticklabels(MONTHS, fontsize=11, fontweight='bold')
ax.set_yticks(range(4))
ax.set_yticklabels([f"{title.split(' ')[0]} ({title.split(' ')[1]})" for _, title, _, _ in CYCLE_CONFIG], fontsize=11, fontweight='bold')
ax.set_title("SMH Alpha Spread t.o.v. S&P 500 (OpEx-tot-OpEx)\nGroen = SMH Outperformance  |  Rood = SMH Underperformance",
             fontsize=14, fontweight="bold", pad=12, color='#2c3e50')

cbar = plt.colorbar(im, ax=ax, orientation='horizontal', shrink=0.6, pad=0.15)
cbar.set_label("Alpha Spread: Rendement SMH min Rendement SPX (%)", fontsize=10, fontweight='bold')

plt.tight_layout()
p4 = FIGURES_DIR / "smh_alpha_by_cycle_phase.png"
plt.savefig(p4, dpi=180, bbox_inches="tight")
plt.close()
print(f"Chart 4 saved to: {p4}")

print("\nAlle 4 afbeeldingen succesvol gegenereerd in reports/figures/!")
