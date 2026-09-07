"""
Annual Cycle OpEx Seasonality (24 Periods Analysis)
===================================================
Empirical analysis of the S&P 500 (SPY 1993-2026) across 12 monthly expiration cycles,
each split into 1H (Post-OpEx / First Half) and 2H (Pre-OpEx / Second Half) = 24 periods.
Generates premium dark infographic and exports structured data.
"""
from pathlib import Path
import json
import shutil
import pandas as pd
import numpy as np
import datetime
import warnings
import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

warnings.filterwarnings("ignore")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
FIGURES_DIR = BASE_DIR / "reports" / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)
PACKAGE_DIR = BASE_DIR / "reports" / "annual_cycle_package"
PACKAGE_DIR.mkdir(parents=True, exist_ok=True)
DATASENTE_DIR = Path(r"C:\Users\ROB5293\antigravity\datasente")
DATASENTE_IMG_DIR = DATASENTE_DIR / "img"
DATASENTE_IMG_DIR.mkdir(parents=True, exist_ok=True)

# ── 1. Data ─────────────────────────────────────────────────────────────────
print("Loading SPY data...")
raw = yf.download("SPY", start="1993-01-01", progress=False)
if isinstance(raw.columns, pd.MultiIndex):
    raw.columns = raw.columns.droplevel(1)
price = (raw["Adj Close"] if "Adj Close" in raw.columns else raw["Close"]).dropna()
max_date = price.index.max()
print(f"Data range: {price.index[0].date()} to {max_date.date()} ({len(price)} trading days)\n")

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

MONTHS_NL = ["Januari", "Februari", "Maart", "April", "Mei", "Juni",
             "Juli", "Augustus", "September", "Oktober", "November", "December"]

def get_3rd_friday(year, month):
    d = datetime.date(year, month, 1)
    while d.weekday() != 4:
        d += datetime.timedelta(days=1)
    d += datetime.timedelta(days=14)
    return pd.Timestamp(d)

# ── 2. OpEx Periods Calculation ─────────────────────────────────────────────
records = []
min_y = price.index.min().year
max_y = price.index.max().year

for y in range(min_y, max_y + 1):
    for m in range(1, 13):
        prev_opex = get_3rd_friday(y - 1, 12) if m == 1 else get_3rd_friday(y, m - 1)
        curr_opex = get_3rd_friday(y, m)
        
        if curr_opex > max_date:
            continue
            
        vp = price.index[price.index <= prev_opex]
        vc = price.index[price.index <= curr_opex]
        if len(vp) == 0 or len(vc) == 0:
            continue
            
        sub = price.loc[vp[-1]:vc[-1]]
        if len(sub) < 10:
            continue
            
        k = len(sub) - 1 # total steps
        mid_idx = k // 2 # 50/50 trading day midpoint
        
        p0 = sub.iloc[0]
        pmid = sub.iloc[mid_idx]
        pend = sub.iloc[-1]
        
        r_1h = (pmid / p0 - 1) * 100
        r_2h = (pend / pmid - 1) * 100
        r_full = (pend / p0 - 1) * 100
        
        records.append({
            "Year": y,
            "Month": m,
            "Month_Name": MONTHS[m - 1],
            "Ret_1H": r_1h,
            "Ret_2H": r_2h,
            "Ret_Full": r_full,
            "Days_1H": mid_idx,
            "Days_2H": k - mid_idx,
            "Total_Days": k,
            "Start_Date": sub.index[0],
            "Mid_Date": sub.index[mid_idx],
            "End_Date": sub.index[-1]
        })

df_opex = pd.DataFrame(records)

# ── 3. Statistical Aggregations ──────────────────────────────────────────────
stats_1h = {}
stats_2h = {}
stats_full = {}

for m in range(1, 13):
    m_name = MONTHS[m - 1]
    sub = df_opex[df_opex["Month"] == m]
    n = len(sub)
    
    # 1H stats
    s1 = sub["Ret_1H"]
    stats_1h[m_name] = {
        "avg": float(s1.mean()),
        "median": float(s1.median()),
        "wr": float((s1 > 0).mean() * 100),
        "n": int(n),
        "std": float(s1.std()),
        "best": float(s1.max()),
        "worst": float(s1.min())
    }
    
    # 2H stats
    s2 = sub["Ret_2H"]
    stats_2h[m_name] = {
        "avg": float(s2.mean()),
        "median": float(s2.median()),
        "wr": float((s2 > 0).mean() * 100),
        "n": int(n),
        "std": float(s2.std()),
        "best": float(s2.max()),
        "worst": float(s2.min())
    }
    
    # Full OpEx stats
    sf = sub["Ret_Full"]
    stats_full[m_name] = {
        "avg": float(sf.mean()),
        "median": float(sf.median()),
        "wr": float((sf > 0).mean() * 100),
        "n": int(n),
        "std": float(sf.std()),
        "best": float(sf.max()),
        "worst": float(sf.min())
    }

# ── 4. Classification ─────────────────────────────────────────────────────────
def classify(avg, wr):
    if np.isnan(avg):
        return "neutral", "N/A"
    score = avg
    if wr < 45 and avg > 0:
        score -= 0.5
    if wr > 70 and avg < 0:
        score += 0.5
    if wr >= 70 and avg > 0.8:
        score += 0.4
    if wr <= 45 and avg < 0:
        score -= 0.4

    if score >= 1.2:
        return "strong_green", "Sterk +"
    elif score >= 0.3:
        return "green", "Positief"
    elif score > -0.3:
        return "neutral", "Neutraal"
    elif score > -1.0:
        return "red", "Negatief"
    else:
        return "strong_red", "Sterk -"

COLORS = {
    "strong_green": "#00c853",
    "green": "#69f0ae",
    "neutral": "#455a64",
    "red": "#ef9a9a",
    "strong_red": "#e53935",
}

TEXT_ON = {
    "strong_green": "white",
    "green": "#1a2a1a",
    "neutral": "#cfd8dc",
    "red": "#2a0a0a",
    "strong_red": "white",
}

BG = "#0d1117"
PANEL = "#161b22"
HEADER_BG = "#21262d"
ACCENT = "#58a6ff"
BORDER = "#30363d"

# ── 5. Generate Dual-Panel Infographic ────────────────────────────────────────
# Total figure layout
fig = plt.figure(figsize=(15.5, 11.5), facecolor=BG)

# We use two subplots (Axes)
# Top: Matrix calendar (12 cols x 3 rows: 1H, 2H, Full)
# Bottom: 24-Period chronological bar chart with cumulative trajectory
gs = fig.add_gridspec(2, 1, height_ratios=[1.25, 1.0], hspace=0.28)

ax1 = fig.add_subplot(gs[0])
ax1.set_facecolor(BG)
ax1.axis("off")

# Title Banner
ax1_w = 15.5
ax1_h = 6.2
ax1.set_xlim(0, ax1_w)
ax1.set_ylim(0, ax1_h)

ax1.add_patch(FancyBboxPatch(
    (0.3, ax1_h - 1.15), ax1_w - 0.6, 1.0,
    boxstyle="round,pad=0.04", fc=HEADER_BG, ec=ACCENT, lw=1.5, zorder=2
))
ax1.text(ax1_w / 2, ax1_h - 0.48,
         "S&P 500 Jaarlijkse Cyclus — 24 Expiratie Perioden (OpEx Seasonality)",
         ha="center", va="center", fontsize=15, fontweight="bold",
         color="white", zorder=3)
ax1.text(ax1_w / 2, ax1_h - 0.84,
         "12 Expiratie-cycli (3e vrijdag → 3e vrijdag) gesplitst in 1e Helft (Post-OpEx) & 2e Helft (Pre-OpEx)  |  SPY 1993–2026 (33 jaar)",
         ha="center", va="center", fontsize=8.5, color="#8b949e", zorder=3)

# Grid Layout for Matrix
n_cols = 12
cell_w = 0.98
cell_h = 1.08
margin_l = 2.4
margin_t = 1.7

# Month headers
header_y = ax1_h - margin_t + 0.12
for m_idx, m_name in enumerate(MONTHS):
    cx = margin_l + m_idx * cell_w + cell_w / 2
    ax1.add_patch(FancyBboxPatch(
        (margin_l + m_idx * cell_w + 0.03, header_y - 0.24),
        cell_w - 0.06, 0.34,
        boxstyle="round,pad=0.03", fc=HEADER_BG, ec=BORDER, lw=0.8, zorder=2
    ))
    ax1.text(cx, header_y - 0.07, m_name,
             ha="center", va="center", fontsize=9.5, fontweight="bold",
             color=ACCENT, zorder=3)

ROW_LABELS = [
    ("1e Helft (1H)", "Post-OpEx (~10 dgn)\nExpiratie → Medio"),
    ("2e Helft (2H)", "Pre-OpEx (~10 dgn)\nMedio → Expiratie"),
    ("Volledig (OpEx)", "3e Vrijdag → 3e Vrijdag\nComplete Cyclus")
]
ROW_DATA = [stats_1h, stats_2h, stats_full]

for r_idx, (r_title, r_sub) in enumerate(ROW_LABELS):
    row_y = ax1_h - margin_t - (r_idx + 1) * cell_h + 0.15
    
    # Left row label
    ax1.add_patch(FancyBboxPatch(
        (0.3, row_y + 0.05), margin_l - 0.45, cell_h - 0.10,
        boxstyle="round,pad=0.04", fc=HEADER_BG, ec=BORDER, lw=0.8, zorder=2
    ))
    ax1.text(margin_l / 2 + 0.05, row_y + cell_h / 2 + 0.14, r_title,
             ha="center", va="center", fontsize=9, fontweight="bold", color="white", zorder=3)
    ax1.text(margin_l / 2 + 0.05, row_y + cell_h / 2 - 0.18, r_sub,
             ha="center", va="center", fontsize=6.8, color="#8b949e", multialignment="center", zorder=3)
    
    # Cells for each month
    current_stat_dict = ROW_DATA[r_idx]
    for m_idx, m_name in enumerate(MONTHS):
        s = current_stat_dict[m_name]
        avg = s["avg"]
        wr = s["wr"]
        n = s["n"]
        cls, lbl = classify(avg, wr)
        fc = COLORS[cls]
        tc = TEXT_ON[cls]
        
        cx = margin_l + m_idx * cell_w
        pad = 0.04
        
        ax1.add_patch(FancyBboxPatch(
            (cx + pad, row_y + pad),
            cell_w - 2 * pad, cell_h - 2 * pad,
            boxstyle="round,pad=0.05", fc=fc, ec="#0d1117", lw=1.2, zorder=2
        ))
        
        mid_x = cx + cell_w / 2
        mid_y = row_y + cell_h / 2
        
        sign = "+" if avg >= 0 else ""
        ax1.text(mid_x, mid_y + 0.20, f"{sign}{avg:.2f}%",
                 ha="center", va="center", fontsize=9.2, fontweight="bold",
                 color=tc, zorder=3)
        ax1.text(mid_x, mid_y - 0.07, f"{wr:.0f}% WR",
                 ha="center", va="center", fontsize=7.2,
                 color=tc, alpha=0.9, zorder=3)
        ax1.text(mid_x, mid_y - 0.28, f"n={n}",
                 ha="center", va="center", fontsize=5.8,
                 color=tc, alpha=0.65, zorder=3)

# Panel 1 Legend
leg_y = 0.25
leg_items = [
    ("strong_green", "Sterk Positief (Score ≥ +1.2%)"),
    ("green",        "Positief (Score ≥ +0.3%)"),
    ("neutral",      "Neutraal (-0.3% tot +0.3%)"),
    ("red",          "Negatief (Score < -0.3%)"),
    ("strong_red",   "Sterk Negatief (Score < -1.0%)"),
]
leg_x_start = 1.2
for i, (cls, txt) in enumerate(leg_items):
    lx = leg_x_start + i * 2.7
    ax1.add_patch(FancyBboxPatch(
        (lx, leg_y - 0.12), 0.28, 0.24,
        boxstyle="round,pad=0.03", fc=COLORS[cls], ec="none", zorder=2
    ))
    ax1.text(lx + 0.38, leg_y, txt,
             ha="left", va="center", fontsize=7.2, color="#c9d1d9", zorder=3)

# ── 6. Panel 2: 24 Periods Sequential Chronological Pulse Bar Chart ──────────
ax2 = fig.add_subplot(gs[1])
ax2.set_facecolor(PANEL)

periods_labels = []
periods_returns = []
periods_winrates = []
periods_colors = []

# Chronological order of 24 periods: Jan 1H, Jan 2H, Feb 1H, ..., Dec 2H
for m_idx, m_name in enumerate(MONTHS):
    # 1H
    s1 = stats_1h[m_name]
    c1, _ = classify(s1["avg"], s1["wr"])
    periods_labels.append(f"{m_name}\n1H")
    periods_returns.append(s1["avg"])
    periods_winrates.append(s1["wr"])
    periods_colors.append(COLORS[c1])
    
    # 2H
    s2 = stats_2h[m_name]
    c2, _ = classify(s2["avg"], s2["wr"])
    periods_labels.append(f"{m_name}\n2H")
    periods_returns.append(s2["avg"])
    periods_winrates.append(s2["wr"])
    periods_colors.append(COLORS[c2])

x = np.arange(24)
bars = ax2.bar(x, periods_returns, color=periods_colors, width=0.68, edgecolor="#0d1117", lw=1.2, zorder=3)

# Add zero line
ax2.axhline(0, color="#8b949e", lw=1.0, ls="-", zorder=2)

# Value annotations on top/bottom of bars
for i, b in enumerate(bars):
    h = b.get_height()
    va = "bottom" if h >= 0 else "top"
    offset = 0.08 if h >= 0 else -0.08
    sign = "+" if h >= 0 else ""
    ax2.text(b.get_x() + b.get_width() / 2, h + offset,
             f"{sign}{h:.2f}%\n({periods_winrates[i]:.0f}%)",
             ha="center", va=va, fontsize=6.8, fontweight="bold",
             color="#e6edf3", zorder=4)

# Cumulative line overlay on twin axis
ax2_twin = ax2.twinx()
cum_curve = np.cumsum(periods_returns)
ax2_twin.plot(x, cum_curve, color=ACCENT, lw=2.2, marker="o", markersize=4, label="Cumulatief Rendement (%)", zorder=5)
ax2_twin.set_ylabel("Cumulatief Seizoensverloop (%)", color=ACCENT, fontsize=9, fontweight="bold")
ax2_twin.tick_params(colors=ACCENT, labelsize=8)
ax2_twin.grid(False)

# Formatting Panel 2
ax2.set_xticks(x)
ax2.set_xticklabels(periods_labels, fontsize=7.8, fontweight="bold", color="#c9d1d9")
ax2.set_ylabel("Gemiddeld Rendement per Periode (%)", color="#c9d1d9", fontsize=9, fontweight="bold")
ax2.set_title("De 24-Perioden Seizoenspuls: Gemiddeld Rendement (Bars) & Cumulatieve Curve (Blauw)",
              fontsize=10.5, fontweight="bold", color="white", pad=12)
ax2.tick_params(colors="#8b949e", labelsize=8)
ax2.grid(True, axis="y", color="#30363d", ls="--", lw=0.6, alpha=0.7, zorder=1)
ax2.set_xlim(-0.7, 23.7)

# Adjust y limits for aesthetic breathing room
y_min = min(periods_returns) - 0.85
y_max = max(periods_returns) + 0.75
ax2.set_ylim(y_min, y_max)

# Annotate Key Inflection Zones
ax2.annotate("Gouden Start\n(+1.28%, 76% WR)", xy=(0, 1.28), xytext=(0, 1.95),
             arrowprops=dict(facecolor="#00c853", shrink=0.08, width=1, headwidth=4),
             ha="center", fontsize=6.5, fontweight="bold", color="#69f0ae",
             bbox=dict(boxstyle="round,pad=0.2", fc="#161b22", ec="#00c853", lw=0.8))

ax2.annotate("Tax Day Rally\n(+1.08%, 62% WR)", xy=(7, 1.08), xytext=(7, 1.75),
             arrowprops=dict(facecolor="#00c853", shrink=0.08, width=1, headwidth=4),
             ha="center", fontsize=6.5, fontweight="bold", color="#69f0ae",
             bbox=dict(boxstyle="round,pad=0.2", fc="#161b22", ec="#00c853", lw=0.8))

ax2.annotate("Gevaarzone Najaar\n(-0.88%, 42% WR)", xy=(18, -0.88), xytext=(18, -1.65),
             arrowprops=dict(facecolor="#e53935", shrink=0.08, width=1, headwidth=4),
             ha="center", fontsize=6.5, fontweight="bold", color="#ef9a9a",
             bbox=dict(boxstyle="round,pad=0.2", fc="#161b22", ec="#e53935", lw=0.8))

ax2.annotate("Bodem & Reversal\n(+0.62%, 58% WR)", xy=(19, 0.62), xytext=(19, 1.35),
             arrowprops=dict(facecolor="#69f0ae", shrink=0.08, width=1, headwidth=4),
             ha="center", fontsize=6.5, fontweight="bold", color="#69f0ae",
             bbox=dict(boxstyle="round,pad=0.2", fc="#161b22", ec="#69f0ae", lw=0.8))

ax2.annotate("Eindejaarsrally\n(+1.51%, 79% WR)", xy=(22, 1.51), xytext=(22, 2.15),
             arrowprops=dict(facecolor="#00c853", shrink=0.08, width=1, headwidth=4),
             ha="center", fontsize=6.5, fontweight="bold", color="#69f0ae",
             bbox=dict(boxstyle="round,pad=0.2", fc="#161b22", ec="#00c853", lw=0.8))

for spine in ["top", "right", "left", "bottom"]:
    ax2.spines[spine].set_color(BORDER)
    ax2_twin.spines[spine].set_color(BORDER)

plt.tight_layout()

# ── 7. Save to Targets ───────────────────────────────────────────────────────
fig_file1 = FIGURES_DIR / "annual_cycle_opex_calendar.png"
fig.savefig(fig_file1, dpi=200, facecolor=BG)
print(f"Saved figure: {fig_file1}")

fig_file_pkg = PACKAGE_DIR / "annual_cycle_opex_calendar.png"
shutil.copy2(fig_file1, fig_file_pkg)

fig_file_ds1 = DATASENTE_DIR / "annual_cycle_opex_calendar.png"
fig_file_ds2 = DATASENTE_IMG_DIR / "annual_cycle_opex_calendar.png"
shutil.copy2(fig_file1, fig_file_ds1)
shutil.copy2(fig_file1, fig_file_ds2)

# Copy to conversation artifacts
artifact_img = Path(r"C:\Users\ROB5293\.gemini\antigravity-ide\brain\dd99d209-d1e7-41fa-a165-17bc8389f138\annual_cycle_opex_calendar.png")
shutil.copy2(fig_file1, artifact_img)
print("Copied figure to conversation artifact directory.")
print(f"Copied figure to DataSente website directories.")

# ── 8. Export Data JSON ──────────────────────────────────────────────────────
output_json = {
    "generated_at": datetime.datetime.now().isoformat(),
    "dataset": "SPY 1993-2026",
    "months": MONTHS,
    "stats_1h": stats_1h,
    "stats_2h": stats_2h,
    "stats_full": stats_full,
    "periods_24": [
        {
            "index": i + 1,
            "period": periods_labels[i].replace("\n", " "),
            "month": MONTHS[i // 2],
            "half": "1H" if i % 2 == 0 else "2H",
            "avg_return": periods_returns[i],
            "win_rate": periods_winrates[i],
            "classification": classify(periods_returns[i], periods_winrates[i])[1]
        }
        for i in range(24)
    ]
}

json_path = PACKAGE_DIR / "annual_cycle_24periods_stats.json"
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(output_json, f, indent=2)
print(f"Saved stats JSON: {json_path}")
print("Done!")
