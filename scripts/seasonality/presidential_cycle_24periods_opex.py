"""
Presidential Cycle OpEx Seasonality (Split Expiration Months / 1H & 2H)
=======================================================================
Empirical analysis of the S&P 500 (SPY 1993-2026) across the 4-year Presidential Cycle,
with each of the 12 monthly expiration cycles split into:
  - 1H: Post-OpEx (3rd Friday to mid-cycle / ~10 trading days)
  - 2H: Pre-OpEx (mid-cycle to new 3rd Friday / ~10 trading days)
  - Full: Complete OpEx cycle (3rd Friday to 3rd Friday)

Total of 24 periods per cycle year, and 96 periods across the full 4-year term.
Generates:
  1. Master Calendar Matrix (presidential_cycle_opex_calendar.png)
  2. 96-Period Macro Pulse & 2026 Midterm Deep Dive (presidential_cycle_96periods_pulse.png)
  3. Structured JSON dataset (presidential_cycle_24periods_stats.json)
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
PACKAGE_DIR = BASE_DIR / "reports" / "presidential_cycle_package"
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

CYCLE_CONFIG = [
    (1, "Post-Election", "Jaar 1", "2001, 2005, 2009, 2013, 2017, 2021, 2025"),
    (2, "Midterm",       "Jaar 2 (NU: 2026)", "2002, 2006, 2010, 2014, 2018, 2022, 2026"),
    (3, "Pre-Election",  "Jaar 3", "2003, 2007, 2011, 2015, 2019, 2023"),
    (0, "Election Year", "Jaar 4", "2000, 2004, 2008, 2012, 2016, 2020, 2024")
]
CYCLE_KEYS = [1, 2, 3, 0]

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
            "CycleKey": y % 4,
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
print(f"Total OpEx cycle records calculated: {len(df_opex)}")

# ── 3. Statistical Aggregations ──────────────────────────────────────────────
cycle_stats = {}

for key, name, year_lbl, sample_years in CYCLE_CONFIG:
    sub_c = df_opex[df_opex["CycleKey"] == key]
    n_years = sub_c["Year"].nunique()
    
    c_dict = {
        "name": name,
        "label": year_lbl,
        "sample_years": sample_years,
        "n_years": n_years,
        "1H": {},
        "2H": {},
        "Full": {}
    }
    
    for m in range(1, 13):
        m_name = MONTHS[m - 1]
        sub_m = sub_c[sub_c["Month"] == m]
        n_obs = len(sub_m)
        
        for part, col in [("1H", "Ret_1H"), ("2H", "Ret_2H"), ("Full", "Ret_Full")]:
            s = sub_m[col]
            if len(s) > 0:
                c_dict[part][m_name] = {
                    "avg": float(s.mean()),
                    "median": float(s.median()),
                    "wr": float((s > 0).mean() * 100),
                    "n": int(n_obs),
                    "std": float(s.std()) if len(s) > 1 else 0.0,
                    "best": float(s.max()),
                    "worst": float(s.min())
                }
            else:
                c_dict[part][m_name] = {
                    "avg": 0.0, "median": 0.0, "wr": 0.0, "n": 0, "std": 0.0, "best": 0.0, "worst": 0.0
                }
                
    cycle_stats[key] = c_dict

# ── 4. Classification ─────────────────────────────────────────────────────────
def classify(avg, wr):
    if np.isnan(avg):
        return "neutral", "N/A"
    score = avg
    if wr < 42 and avg > 0:
        score -= 0.6
    if wr > 72 and avg < 0:
        score += 0.6
    if wr >= 72 and avg > 1.0:
        score += 0.5
    if wr <= 40 and avg < 0:
        score -= 0.5

    if score >= 1.5:
        return "strong_green", "Sterk +"
    elif score >= 0.35:
        return "green", "Positief"
    elif score > -0.35:
        return "neutral", "Neutraal"
    elif score > -1.2:
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
GOLD = "#ffd700"

# ═════════════════════════════════════════════════════════════════════════════
# FIGURE 1: MASTER CALENDAR MATRIX (4 Cycle Years x [1H, 2H, Full])
# ═════════════════════════════════════════════════════════════════════════════
print("Generating Master Calendar Matrix...")

cell_w = 1.05
cell_h = 0.88
margin_l = 3.65
margin_t = 1.8
margin_b = 1.2

total_w = margin_l + 12 * cell_w + 0.35
total_h = 14.8

fig, ax = plt.subplots(figsize=(total_w, total_h), facecolor=BG)
ax.set_facecolor(BG)
ax.set_xlim(0, total_w)
ax.set_ylim(0, total_h)
ax.axis("off")

# Title Banner
banner_h = 1.2
ax.add_patch(FancyBboxPatch(
    (0.3, total_h - banner_h - 0.2), total_w - 0.6, banner_h,
    boxstyle="round,pad=0.04", fc=HEADER_BG, ec=ACCENT, lw=1.6, zorder=2
))
ax.text(total_w / 2, total_h - 0.55,
        "S&P 500 Presidentscyclus — 24 Expiratie Perioden per Cyclusjaar",
        ha="center", va="center", fontsize=15, fontweight="bold",
        color="white", zorder=3)
ax.text(total_w / 2, total_h - 0.98,
        "Elk van de 4 cyclusjaren gesplitst in 1H (Post-OpEx / ~10 dgn) & 2H (Pre-OpEx / ~10 dgn)  |  SPY 1993–2026 (33 jaar)",
        ha="center", va="center", fontsize=8.6, color="#8b949e", zorder=3)

# Month Headers
header_y = total_h - margin_t + 0.08
for m_idx, m_name in enumerate(MONTHS):
    cx = margin_l + m_idx * cell_w + cell_w / 2
    ax.add_patch(FancyBboxPatch(
        (margin_l + m_idx * cell_w + 0.03, header_y - 0.28),
        cell_w - 0.06, 0.36,
        boxstyle="round,pad=0.03", fc=HEADER_BG, ec=BORDER, lw=0.8, zorder=2
    ))
    ax.text(cx, header_y - 0.10, m_name,
            ha="center", va="center", fontsize=9.6, fontweight="bold",
            color=ACCENT, zorder=3)

# Grid Layout: 4 Cycle Groups
current_y_cursor = total_h - margin_t - 0.1

for c_idx, (key, name, year_lbl, sample_years) in enumerate(CYCLE_CONFIG):
    c_data = cycle_stats[key]
    n_years = c_data["n_years"]
    
    group_top_y = current_y_cursor
    group_h = 3 * cell_h + 0.15
    
    is_midterm = (key == 2)
    border_color = GOLD if is_midterm else BORDER
    border_lw = 2.0 if is_midterm else 0.8
    card_bg = "#1a1f26" if is_midterm else HEADER_BG
    
    # Left Year Main Card (x: 0.25 to 2.25)
    card_w = 1.95
    ax.add_patch(FancyBboxPatch(
        (0.25, group_top_y - group_h + 0.05), card_w, group_h - 0.10,
        boxstyle="round,pad=0.05", fc=card_bg, ec=border_color, lw=border_lw, zorder=2
    ))
    
    mid_card_x = 0.25 + card_w / 2
    ax.text(mid_card_x, group_top_y - 0.55, f"{name}",
            ha="center", va="center", fontsize=10.0, fontweight="bold",
            color=GOLD if is_midterm else "white", zorder=3)
    ax.text(mid_card_x, group_top_y - 0.95, f"({year_lbl})",
            ha="center", va="center", fontsize=7.8, fontweight="bold",
            color=GOLD if is_midterm else ACCENT, zorder=3)
    ax.text(mid_card_x, group_top_y - 1.40, f"{n_years} cycli in dataset",
            ha="center", va="center", fontsize=6.8, color="#c9d1d9", zorder=3)
    ax.text(mid_card_x, group_top_y - 1.70, f"{sample_years[:22]}...",
            ha="center", va="center", fontsize=5.8, color="#8b949e", zorder=3)
    
    # Sub-row indicators card/pills (x: 2.30 to 3.52)
    sub_labels = [
        ("1H (Post-OpEx)", "Dag 1→10"),
        ("2H (Pre-OpEx)", "Dag 11→20"),
        ("Volledig", "3e Vr → 3e Vr")
    ]
    
    pill_x = 2.30
    pill_w = 1.22
    
    for r_idx, part in enumerate(["1H", "2H", "Full"]):
        row_y = group_top_y - (r_idx + 1) * cell_h + 0.05
        sub_t, sub_s = sub_labels[r_idx]
        
        pill_fc = "#22272e" if part != "Full" else "#1c2c3e"
        pill_ec = BORDER if part != "Full" else "#388bfd"
        ax.add_patch(FancyBboxPatch(
            (pill_x, row_y + 0.04), pill_w, cell_h - 0.08,
            boxstyle="round,pad=0.03", fc=pill_fc, ec=pill_ec, lw=0.8, zorder=2
        ))
        
        ax.text(pill_x + pill_w / 2, row_y + cell_h / 2 + 0.12, sub_t,
                ha="center", va="center", fontsize=7.2, fontweight="bold",
                color=ACCENT if part == "Full" else "white", zorder=3)
        ax.text(pill_x + pill_w / 2, row_y + cell_h / 2 - 0.14, sub_s,
                ha="center", va="center", fontsize=5.8, color="#8b949e", zorder=3)
        
        # Draw cells for each month
        part_dict = c_data[part]
        for m_idx, m_name in enumerate(MONTHS):
            s = part_dict[m_name]
            avg = s["avg"]
            wr = s["wr"]
            n = s["n"]
            cls, lbl = classify(avg, wr)
            fc = COLORS[cls]
            tc = TEXT_ON[cls]
            
            cx = margin_l + m_idx * cell_w
            pad_x = 0.035
            pad_y = 0.035
            
            # Highlight current active window (Midterm 2026, Sept 2H)
            is_current_cell = (key == 2 and m_idx == 8 and part == "2H")
            
            ax.add_patch(FancyBboxPatch(
                (cx + pad_x, row_y + pad_y),
                cell_w - 2 * pad_x, cell_h - 2 * pad_y,
                boxstyle="round,pad=0.04", fc=fc, ec=GOLD if is_current_cell else "#0d1117",
                lw=2.5 if is_current_cell else 1.0, zorder=4 if is_current_cell else 2
            ))
            
            mid_x = cx + cell_w / 2
            mid_y = row_y + cell_h / 2
            
            sign = "+" if avg >= 0 else ""
            ax.text(mid_x, mid_y + 0.17, f"{sign}{avg:.2f}%",
                     ha="center", va="center", fontsize=8.4, fontweight="bold",
                     color=tc, zorder=5)
            ax.text(mid_x, mid_y - 0.06, f"{wr:.0f}% WR",
                     ha="center", va="center", fontsize=6.8,
                     color=tc, alpha=0.9, zorder=5)
            ax.text(mid_x, mid_y - 0.24, f"n={n}",
                     ha="center", va="center", fontsize=5.5,
                     color=tc, alpha=0.65, zorder=5)
            
            if is_current_cell:
                ax.text(mid_x, row_y + cell_h - 0.09, "★ NU (2026)",
                        ha="center", va="center", fontsize=6.2, fontweight="bold",
                        color=GOLD, zorder=6)

    current_y_cursor -= (group_h + 0.18)

# Legend
leg_y = margin_b * 0.55
leg_items = [
    ("strong_green", "Sterk Positief (Score ≥ +1.5%)"),
    ("green",        "Positief (Score ≥ +0.35%)"),
    ("neutral",      "Neutraal (-0.35% tot +0.35%)"),
    ("red",          "Negatief (Score < -0.35%)"),
    ("strong_red",   "Sterk Negatief (Score < -1.2%)"),
]
leg_x_start = 1.0
spacing = (total_w - 2.0) / len(leg_items)
for i, (cls, txt) in enumerate(leg_items):
    lx = leg_x_start + i * spacing
    ax.add_patch(FancyBboxPatch(
        (lx, leg_y - 0.12), 0.32, 0.24,
        boxstyle="round,pad=0.03", fc=COLORS[cls], ec="none", zorder=2
    ))
    ax.text(lx + 0.42, leg_y, txt,
            ha="left", va="center", fontsize=7.2, color="#c9d1d9", zorder=3)

ax.text(total_w / 2, 0.22,
        "1H = Post-OpEx (3e vrijdag vorige maand → halverwege)  |  2H = Pre-OpEx (halverwege → 3e vrijdag)  |  Volledig = Complete OpEx-cyclus",
        ha="center", va="center", fontsize=6.8, color="#6e7681", zorder=3)

plt.tight_layout()
cal_path = FIGURES_DIR / "presidential_cycle_opex_calendar.png"
fig.savefig(cal_path, dpi=200, facecolor=BG)
plt.close()
print(f"Saved calendar: {cal_path}")

# ═════════════════════════════════════════════════════════════════════════════
# FIGURE 2: 96-PERIOD MACRO PULSE & 2026 MIDTERM DEEP DIVE
# ═════════════════════════════════════════════════════════════════════════════
print("Generating 96-Period Macro Pulse & Midterm Deep Dive...")

fig2 = plt.figure(figsize=(16.5, 12.2), facecolor=BG)
gs = fig2.add_gridspec(2, 1, height_ratios=[1.15, 1.0], hspace=0.36)

# Subplot 1: Complete 96-Period Sequential 4-Year Macro Cycle
ax_macro = fig2.add_subplot(gs[0])
ax_macro.set_facecolor(PANEL)

macro_labels = []
macro_returns = []
macro_winrates = []
macro_colors = []

for key, name, year_lbl, _ in CYCLE_CONFIG:
    c_data = cycle_stats[key]
    for m_idx, m_name in enumerate(MONTHS):
        for part in ["1H", "2H"]:
            s = c_data[part][m_name]
            avg = s["avg"]
            wr = s["wr"]
            cls, _ = classify(avg, wr)
            macro_labels.append(f"{m_name} {part}")
            macro_returns.append(avg)
            macro_winrates.append(wr)
            macro_colors.append(COLORS[cls])

x96 = np.arange(96)
bars96 = ax_macro.bar(x96, macro_returns, color=macro_colors, width=0.72, edgecolor="#0d1117", lw=0.6, zorder=3)
ax_macro.axhline(0, color="#8b949e", lw=1.0, ls="-", zorder=2)

ax_macro_twin = ax_macro.twinx()
cum96 = np.cumsum(macro_returns)
ax_macro_twin.plot(x96, cum96, color=ACCENT, lw=2.4, label="Cumulatief Rendement (%)", zorder=5)
ax_macro_twin.set_ylabel("Cumulatief 4-Jaars Rendement (%)", color=ACCENT, fontsize=9.5, fontweight="bold")
ax_macro_twin.tick_params(colors=ACCENT, labelsize=8)
ax_macro_twin.grid(False)

# Separators between the 4 cycle years
cycle_divs = [24, 48, 72]
cycle_names_headers = ["Jaar 1: Post-Election", "Jaar 2: Midterm (2026)", "Jaar 3: Pre-Election", "Jaar 4: Election Year"]
for i, div in enumerate(cycle_divs):
    ax_macro.axvline(div - 0.5, color="#58a6ff", lw=1.2, ls="--", alpha=0.6, zorder=2)

for i in range(4):
    ax_macro.text(i * 24 + 12, 4.85, cycle_names_headers[i],
                  ha="center", va="center", fontsize=9.5, fontweight="bold",
                  color=GOLD if i == 1 else "white",
                  bbox=dict(boxstyle="round,pad=0.25", fc=HEADER_BG, ec=GOLD if i == 1 else BORDER, lw=1.0),
                  zorder=7)

ax_macro.set_title("De 96-Perioden Presidentscyclus: S&P 500 OpEx Micro-Puls over de Volledige 4-Jarige Termijn",
                   fontsize=12, fontweight="bold", color="white", pad=16)
ax_macro.set_ylabel("Gemiddeld Rendement per Periode (%)", color="#c9d1d9", fontsize=9, fontweight="bold")
ax_macro.tick_params(colors="#8b949e", labelsize=7.5)
ax_macro.grid(True, axis="y", color="#30363d", ls="--", lw=0.6, alpha=0.7, zorder=1)
ax_macro.set_xlim(-0.8, 95.8)
ax_macro.set_ylim(-4.2, 5.5)

# Custom tick marks showing each year's start and mid-point
tick_pos = [0, 12, 24, 36, 48, 60, 72, 84]
tick_lbl = ["J1 Jan", "J1 Jul", "J2 Jan (Mid)", "J2 Jul", "J3 Jan (Pre)", "J3 Jul", "J4 Jan (Elec)", "J4 Jul"]
ax_macro.set_xticks(tick_pos)
ax_macro.set_xticklabels(tick_lbl, fontsize=8, fontweight="bold", color="#c9d1d9")

# Annotate macro turning points with clean offsets
ax_macro.annotate("Midterm Nov 2H\n(+2.35%, 100% WR)", xy=(45, 2.35), xytext=(45, 3.4),
                  arrowprops=dict(facecolor=GOLD, shrink=0.08, width=1, headwidth=4),
                  ha="center", fontsize=6.5, fontweight="bold", color=GOLD,
                  bbox=dict(boxstyle="round,pad=0.2", fc="#161b22", ec=GOLD, lw=0.9))

ax_macro.annotate("Pre-Elec Aug 1H\n(-2.72%, 12% WR)", xy=(62, -2.72), xytext=(62, -3.6),
                  arrowprops=dict(facecolor="#e53935", shrink=0.08, width=1, headwidth=4),
                  ha="center", fontsize=6.5, fontweight="bold", color="#ef9a9a",
                  bbox=dict(boxstyle="round,pad=0.2", fc="#161b22", ec="#e53935", lw=0.9))

ax_macro.annotate("Pre-Elec Nov 1H\n(+2.74%, 100% WR)", xy=(68, 2.74), xytext=(68, 3.4),
                  arrowprops=dict(facecolor="#00c853", shrink=0.08, width=1, headwidth=4),
                  ha="center", fontsize=6.5, fontweight="bold", color="#69f0ae",
                  bbox=dict(boxstyle="round,pad=0.2", fc="#161b22", ec="#00c853", lw=0.9))

ax_macro.annotate("Election Apr 1H\n(+3.05%, 100% WR)", xy=(78, 3.05), xytext=(78, 3.6),
                  arrowprops=dict(facecolor="#00c853", shrink=0.08, width=1, headwidth=4),
                  ha="center", fontsize=6.5, fontweight="bold", color="#69f0ae",
                  bbox=dict(boxstyle="round,pad=0.2", fc="#161b22", ec="#00c853", lw=0.9))

# Subplot 2: 24 Periods Midterm Year Deep Dive (2026 Focus)
ax_mid = fig2.add_subplot(gs[1])
ax_mid.set_facecolor(PANEL)

mid_labels = []
mid_returns = []
mid_winrates = []
mid_colors = []

mid_data = cycle_stats[2] # Midterm
for m_idx, m_name in enumerate(MONTHS):
    for part in ["1H", "2H"]:
        s = mid_data[part][m_name]
        cls, _ = classify(s["avg"], s["wr"])
        mid_labels.append(f"{m_name}\n{part}")
        mid_returns.append(s["avg"])
        mid_winrates.append(s["wr"])
        mid_colors.append(COLORS[cls])

x24 = np.arange(24)
bars24 = ax_mid.bar(x24, mid_returns, color=mid_colors, width=0.68, edgecolor="#0d1117", lw=1.2, zorder=3)
ax_mid.axhline(0, color="#8b949e", lw=1.0, ls="-", zorder=2)

for i, b in enumerate(bars24):
    h = b.get_height()
    va = "bottom" if h >= 0 else "top"
    offset = 0.08 if h >= 0 else -0.08
    sign = "+" if h >= 0 else ""
    ax_mid.text(b.get_x() + b.get_width() / 2, h + offset,
                f"{sign}{h:.2f}%\n({mid_winrates[i]:.0f}%)",
                ha="center", va=va, fontsize=6.6, fontweight="bold",
                color="#e6edf3", zorder=4)

ax_mid_twin = ax_mid.twinx()
cum24 = np.cumsum(mid_returns)
ax_mid_twin.plot(x24, cum24, color=GOLD, lw=2.4, marker="o", markersize=4, label="Cumulatief Midterm (%)", zorder=5)
ax_mid_twin.set_ylabel("Cumulatief Midterm Koersverloop (%)", color=GOLD, fontsize=9, fontweight="bold")
ax_mid_twin.tick_params(colors=GOLD, labelsize=8)
ax_mid_twin.grid(False)

ax_mid.set_xticks(x24)
ax_mid.set_xticklabels(mid_labels, fontsize=7.8, fontweight="bold", color="#c9d1d9")
ax_mid.set_ylabel("Gemiddeld Rendement per Periode (%)", color="#c9d1d9", fontsize=9, fontweight="bold")
ax_mid.set_title("Midterm Jaar Focus (2026): 24 Expiratie-Perioden — Van de Zomerdip naar de November 100% Win Rate Rally",
                 fontsize=10.5, fontweight="bold", color=GOLD, pad=12)
ax_mid.tick_params(colors="#8b949e", labelsize=8)
ax_mid.grid(True, axis="y", color="#30363d", ls="--", lw=0.6, alpha=0.7, zorder=1)
ax_mid.set_xlim(-0.7, 23.7)
ax_mid.set_ylim(min(mid_returns) - 0.9, max(mid_returns) + 1.55)

# Annotations for Midterm 2026 key inflection points
ax_mid.annotate("Gouden Nieuwjaarsstart\n(+1.73%, 100% WR)", xy=(0, 1.73), xytext=(0, 2.5),
                arrowprops=dict(facecolor="#00c853", shrink=0.08, width=1, headwidth=4),
                ha="center", fontsize=6.5, fontweight="bold", color="#69f0ae",
                bbox=dict(boxstyle="round,pad=0.2", fc="#161b22", ec="#00c853", lw=0.8))

ax_mid.annotate("De Najaarsdip\n(-1.45%, 25% WR)", xy=(18, -1.45), xytext=(18, -2.25),
                arrowprops=dict(facecolor="#e53935", shrink=0.08, width=1, headwidth=4),
                ha="center", fontsize=6.5, fontweight="bold", color="#ef9a9a",
                bbox=dict(boxstyle="round,pad=0.2", fc="#161b22", ec="#e53935", lw=0.8))

ax_mid.annotate("De Ommekeer\n(+1.72%, 62% WR)", xy=(19, 1.72), xytext=(19, 2.45),
                arrowprops=dict(facecolor="#69f0ae", shrink=0.08, width=1, headwidth=4),
                ha="center", fontsize=6.5, fontweight="bold", color="#69f0ae",
                bbox=dict(boxstyle="round,pad=0.2", fc="#161b22", ec="#69f0ae", lw=0.8))

ax_mid.annotate("De Verkiezingsexplosie\n(+2.35%, 100% Win Rate!)", xy=(21, 2.35), xytext=(21, 3.25),
                arrowprops=dict(facecolor=GOLD, shrink=0.08, width=1, headwidth=4),
                ha="center", fontsize=6.8, fontweight="bold", color=GOLD,
                bbox=dict(boxstyle="round,pad=0.25", fc="#161b22", ec=GOLD, lw=1.0),
                zorder=8)

for s_ax in [ax_macro, ax_macro_twin, ax_mid, ax_mid_twin]:
    for spine in ["top", "right", "left", "bottom"]:
        s_ax.spines[spine].set_color(BORDER)

plt.tight_layout()
pulse_path = FIGURES_DIR / "presidential_cycle_96periods_pulse.png"
fig2.savefig(pulse_path, dpi=200, facecolor=BG)
plt.close()
print(f"Saved macro pulse: {pulse_path}")

# ── 5. Copy Figures to Target Folders ─────────────────────────────────────────
for f_src in [cal_path, pulse_path]:
    shutil.copy2(f_src, PACKAGE_DIR / f_src.name)
    shutil.copy2(f_src, DATASENTE_DIR / f_src.name)
    shutil.copy2(f_src, DATASENTE_IMG_DIR / f_src.name)
    artifact_path = Path(r"C:\Users\ROB5293\.gemini\antigravity-ide\brain\3809dc40-c017-47fc-bc95-09b8200d75c4") / f_src.name
    shutil.copy2(f_src, artifact_path)

print("Copied figures to package, DataSente and conversation artifact directory.")

# ── 6. Export JSON Dataset ───────────────────────────────────────────────────
export_data = {
    "generated_at": datetime.datetime.now().isoformat(),
    "dataset": "SPY 1993-2026",
    "months": MONTHS,
    "cycles": {}
}

for key, name, year_lbl, sample_years in CYCLE_CONFIG:
    c_data = cycle_stats[key]
    periods_list = []
    for m_idx, m_name in enumerate(MONTHS):
        for part in ["1H", "2H"]:
            s = c_data[part][m_name]
            cls, lbl = classify(s["avg"], s["wr"])
            periods_list.append({
                "period": f"{m_name} {part}",
                "month": m_name,
                "half": part,
                "avg_return": s["avg"],
                "median": s["median"],
                "win_rate": s["wr"],
                "n": s["n"],
                "std": s["std"],
                "classification": lbl
            })
            
    export_data["cycles"][name] = {
        "cycle_key": key,
        "label": year_lbl,
        "sample_years": sample_years,
        "n_years": c_data["n_years"],
        "stats_1h": c_data["1H"],
        "stats_2h": c_data["2H"],
        "stats_full": c_data["Full"],
        "periods_24": periods_list
    }

json_path = PACKAGE_DIR / "presidential_cycle_24periods_stats.json"
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(export_data, f, indent=2)

print(f"Saved JSON data: {json_path}")
print("Presidential Cycle 24-Period OpEx analysis completed successfully!")
