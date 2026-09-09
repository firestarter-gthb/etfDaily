"""
Master Dashboard: Combined Annual & Presidential OpEx Cycle Seasonality
======================================================================
Integrates the 24 OpEx periods of the Annual Cycle with the 4-year Presidential Cycle:
  1. Top Panel: Master Confluence Matrix Calendar (Annual Baseline vs Midterm 2026 vs Pre-Election vs Confluence Signal)
  2. Bottom Panel: 24-Period Multi-Curve Confluence Trajectory (Annual Baseline vs Midterm vs Pre-Election vs Election)
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
ANNUAL_PACKAGE_DIR = BASE_DIR / "reports" / "annual_cycle_package"
ANNUAL_PACKAGE_DIR.mkdir(parents=True, exist_ok=True)
DATASENTE_DIR = Path(r"C:\Users\ROB5293\antigravity\datasente")
DATASENTE_IMG_DIR = DATASENTE_DIR / "img"
DATASENTE_IMG_DIR.mkdir(parents=True, exist_ok=True)

# ── 1. Data Download & Processing ────────────────────────────────────────────
print("Loading SPY data...")
raw = yf.download("SPY", start="1993-01-01", progress=False)
if isinstance(raw.columns, pd.MultiIndex):
    raw.columns = raw.columns.droplevel(1)
price = (raw["Adj Close"] if "Adj Close" in raw.columns else raw["Close"]).dropna()
max_date = price.index.max()
print(f"Data range: {price.index[0].date()} to {max_date.date()} ({len(price)} trading days)\n")

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

def get_3rd_friday(year, month):
    d = datetime.date(year, month, 1)
    while d.weekday() != 4:
        d += datetime.timedelta(days=1)
    d += datetime.timedelta(days=14)
    return pd.Timestamp(d)

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
        k = len(sub) - 1
        mid_idx = k // 2
        p0 = sub.iloc[0]
        pmid = sub.iloc[mid_idx]
        pend = sub.iloc[-1]
        
        records.append({
            "Year": y,
            "CycleKey": y % 4, # 1: Post-Election, 2: Midterm, 3: Pre-Election, 0: Election
            "Month": m,
            "Ret_1H": (pmid / p0 - 1) * 100,
            "Ret_2H": (pend / pmid - 1) * 100,
            "Ret_Full": (pend / p0 - 1) * 100
        })

df = pd.DataFrame(records)
print(f"Total OpEx cycle observations: {len(df)}")

# ── 2. Color Palette & Classification ─────────────────────────────────────────
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
    "green":        "#69f0ae",
    "neutral":      "#455a64",
    "red":          "#ef9a9a",
    "strong_red":   "#e53935",
}

TEXT_ON = {
    "strong_green": "white",
    "green":        "#1a2a1a",
    "neutral":      "#cfd8dc",
    "red":          "#2a0a0a",
    "strong_red":   "white",
}

BG = "#0d1117"
PANEL = "#161b22"
HEADER_BG = "#21262d"
ACCENT = "#58a6ff"
BORDER = "#30363d"
GOLD = "#ffd700"
CYAN = "#00e5ff"
MAGENTA = "#e040fb"

# ── 3. Calculate Aggregations ────────────────────────────────────────────────
# Baseline Annual
ann_1h = {}
ann_2h = {}
ann_full = {}
for m in range(1, 13):
    sm = df[df["Month"] == m]
    ann_1h[m] = {"avg": sm["Ret_1H"].mean(), "wr": (sm["Ret_1H"] > 0).mean() * 100, "n": len(sm)}
    ann_2h[m] = {"avg": sm["Ret_2H"].mean(), "wr": (sm["Ret_2H"] > 0).mean() * 100, "n": len(sm)}
    ann_full[m] = {"avg": sm["Ret_Full"].mean(), "wr": (sm["Ret_Full"] > 0).mean() * 100, "n": len(sm)}

# Midterm (Key 2)
mid_1h = {}
mid_2h = {}
mid_full = {}
sm_all_mid = df[df["CycleKey"] == 2]
for m in range(1, 13):
    sm = sm_all_mid[sm_all_mid["Month"] == m]
    mid_1h[m] = {"avg": sm["Ret_1H"].mean(), "wr": (sm["Ret_1H"] > 0).mean() * 100, "n": len(sm)}
    mid_2h[m] = {"avg": sm["Ret_2H"].mean(), "wr": (sm["Ret_2H"] > 0).mean() * 100, "n": len(sm)}
    mid_full[m] = {"avg": sm["Ret_Full"].mean(), "wr": (sm["Ret_Full"] > 0).mean() * 100, "n": len(sm)}

# Pre-Election (Key 3)
pre_1h = {}
pre_2h = {}
sm_all_pre = df[df["CycleKey"] == 3]
for m in range(1, 13):
    sm = sm_all_pre[sm_all_pre["Month"] == m]
    pre_1h[m] = {"avg": sm["Ret_1H"].mean(), "wr": (sm["Ret_1H"] > 0).mean() * 100, "n": len(sm)}
    pre_2h[m] = {"avg": sm["Ret_2H"].mean(), "wr": (sm["Ret_2H"] > 0).mean() * 100, "n": len(sm)}

# Election Year (Key 0)
elec_1h = {}
elec_2h = {}
sm_all_elec = df[df["CycleKey"] == 0]
for m in range(1, 13):
    sm = sm_all_elec[sm_all_elec["Month"] == m]
    elec_1h[m] = {"avg": sm["Ret_1H"].mean(), "wr": (sm["Ret_1H"] > 0).mean() * 100, "n": len(sm)}
    elec_2h[m] = {"avg": sm["Ret_2H"].mean(), "wr": (sm["Ret_2H"] > 0).mean() * 100, "n": len(sm)}

# Confluence Evaluation for Midterm (2026) vs Annual
confl_1h = {}
confl_2h = {}
for m in range(1, 13):
    # 1H
    b1, w1 = ann_1h[m]["avg"], ann_1h[m]["wr"]
    m1, mw1 = mid_1h[m]["avg"], mid_1h[m]["wr"]
    if b1 >= 0.5 and m1 >= 0.5 and w1 >= 60 and mw1 >= 60:
        c_tag = "A+ BULL\nSamenloop"
        c_color = "#00c853"
        c_tc = "white"
    elif b1 < -0.3 and m1 < -0.3 and w1 < 50 and mw1 < 50:
        c_tag = "DUBBEL RISICO\nGevaarzone"
        c_color = "#e53935"
        c_tc = "white"
    elif (b1 > 0.3 and m1 < -0.3) or (b1 < -0.3 and m1 > 0.3):
        c_tag = "DIVERGENTIE\nConflict"
        c_color = "#ffd600"
        c_tc = "#21262d"
    elif b1 > 0.2 and m1 > 0.2:
        c_tag = "POSITIEF\nBeide Groen"
        c_color = "#69f0ae"
        c_tc = "#1a2a1a"
    elif b1 < -0.1 and m1 < -0.1:
        c_tag = "ZWAK\nBeide Rood"
        c_color = "#ef9a9a"
        c_tc = "#2a0a0a"
    else:
        c_tag = "NEUTRAAL\nGeen Signaal"
        c_color = "#455a64"
        c_tc = "#cfd8dc"
    confl_1h[m] = {"tag": c_tag, "color": c_color, "tc": c_tc, "b_avg": b1, "m_avg": m1}

    # 2H
    b2, w2 = ann_2h[m]["avg"], ann_2h[m]["wr"]
    m2, mw2 = mid_2h[m]["avg"], mid_2h[m]["wr"]
    if b2 >= 0.5 and m2 >= 0.5 and w2 >= 60 and mw2 >= 60:
        c_tag = "A+ BULL\nSamenloop"
        c_color = "#00c853"
        c_tc = "white"
    elif b2 < -0.3 and m2 < -0.3 and w2 < 50 and mw2 < 50:
        c_tag = "DUBBEL RISICO\nGevaarzone"
        c_color = "#e53935"
        c_tc = "white"
    elif (b2 > 0.3 and m2 < -0.3) or (b2 < -0.3 and m2 > 0.3):
        c_tag = "DIVERGENTIE\nConflict"
        c_color = "#ffd600"
        c_tc = "#21262d"
    elif b2 > 0.2 and m2 > 0.2:
        c_tag = "POSITIEF\nBeide Groen"
        c_color = "#69f0ae"
        c_tc = "#1a2a1a"
    elif b2 < -0.1 and m2 < -0.1:
        c_tag = "ZWAK\nBeide Rood"
        c_color = "#ef9a9a"
        c_tc = "#2a0a0a"
    else:
        c_tag = "NEUTRAAL\nGeen Signaal"
        c_color = "#455a64"
        c_tc = "#cfd8dc"
    confl_2h[m] = {"tag": c_tag, "color": c_color, "tc": c_tc, "b_avg": b2, "m_avg": m2}


# ═════════════════════════════════════════════════════════════════════════════
# FIGURE: MASTER COMBINED DASHBOARD
# ═════════════════════════════════════════════════════════════════════════════
print("Rendering Master Combined Dashboard...")

fig = plt.figure(figsize=(17.2, 17.2), facecolor=BG)
gs = fig.add_gridspec(2, 1, height_ratios=[1.42, 1.0], hspace=0.25)

# ── TOP PANEL: MASTER MATRIX CALENDAR ─────────────────────────────────────────
ax_top = fig.add_subplot(gs[0])
ax_top.set_facecolor(BG)
ax_top.axis("off")

w_top = 17.2
h_top = 10.4
ax_top.set_xlim(0, w_top)
ax_top.set_ylim(0, h_top)

# Master Title Banner
banner_h = 1.05
ax_top.add_patch(FancyBboxPatch(
    (0.3, h_top - banner_h - 0.12), w_top - 0.6, banner_h,
    boxstyle="round,pad=0.03", fc=HEADER_BG, ec=ACCENT, lw=1.6, zorder=2
))
ax_top.text(w_top / 2, h_top - 0.44,
            "S&P 500 Seizoenscyclus Master Dashboard — Jaarlijkse vs. Presidentiële Cyclus",
            ha="center", va="center", fontsize=15.5, fontweight="bold",
            color="white", zorder=3)
ax_top.text(w_top / 2, h_top - 0.82,
            "24 Expiratie-Perioden per Regime (1H Post-OpEx & 2H Pre-OpEx)  |  Samenloop van Jaarcyclus (n=33) & Midterm 2026 (n=9)  |  SPY 1993–2026",
            ha="center", va="center", fontsize=8.6, color="#8b949e", zorder=3)

# Grid Layout
cell_w = 1.10
cell_h = 0.74
margin_l = 3.65
margin_t = 1.60

# Month Headers
header_y = h_top - margin_t + 0.08
for m_idx, m_name in enumerate(MONTHS):
    cx = margin_l + m_idx * cell_w + cell_w / 2
    ax_top.add_patch(FancyBboxPatch(
        (margin_l + m_idx * cell_w + 0.03, header_y - 0.28),
        cell_w - 0.06, 0.34,
        boxstyle="round,pad=0.03", fc=HEADER_BG, ec=BORDER, lw=0.8, zorder=2
    ))
    ax_top.text(cx, header_y - 0.11, m_name,
                ha="center", va="center", fontsize=9.6, fontweight="bold",
                color=ACCENT, zorder=3)

# We define 4 logical row blocks:
# Block 1: JAARLIJKSE CYCLUS (Baseline) [1H, 2H, Volledig] -> 3 rows
# Block 2: MIDTERM CYCLUS (2026 Focus) [1H, 2H, Volledig] -> 3 rows
# Block 3: CONFLUENTIE STOPLICHT [1H, 2H] -> 2 rows
# Block 4: PRE-ELECTION CYCLUS (2027) [1H, 2H] -> 2 rows

cursor_y = h_top - margin_t - 0.12

BLOCKS = [
    {
        "id": "ann",
        "title": "Jaarlijkse Cyclus",
        "sub": "Baseline (33 Jaar)",
        "desc": "Alle jaren 1993-2026",
        "color": "#388bfd",
        "border": "#1f6feb",
        "rows": [
            ("1H (Post-OpEx)", "Dag 1→10", ann_1h),
            ("2H (Pre-OpEx)", "Dag 11→20", ann_2h),
            ("Volledig", "3e Vr → 3e Vr", ann_full)
        ]
    },
    {
        "id": "mid",
        "title": "Midterm Cyclus",
        "sub": "Jaar 2 (NU: 2026)",
        "desc": "9 cycli (2002, 2006...)",
        "color": GOLD,
        "border": GOLD,
        "rows": [
            ("1H (Post-OpEx)", "Dag 1→10", mid_1h),
            ("2H (Pre-OpEx)", "Dag 11→20", mid_2h),
            ("Volledig", "3e Vr → 3e Vr", mid_full)
        ]
    },
    {
        "id": "confl",
        "title": "Confluentie Signaal",
        "sub": "Jaarlijks vs Midterm",
        "desc": "Stoplicht Handelsmodel",
        "color": "#00e676",
        "border": "#00c853",
        "is_confluence": True,
        "rows": [
            ("1H Confluentie", "Post-OpEx Samenloop", confl_1h),
            ("2H Confluentie", "Pre-OpEx Samenloop", confl_2h)
        ]
    },
    {
        "id": "pre",
        "title": "Pre-Election",
        "sub": "Jaar 3 (2027)",
        "desc": "8 cycli (2003, 2007...)",
        "color": "#a371f7",
        "border": "#8957e5",
        "rows": [
            ("1H (Post-OpEx)", "Dag 1→10", pre_1h),
            ("2H (Pre-OpEx)", "Dag 11→20", pre_2h)
        ]
    }
]

for b_idx, blk in enumerate(BLOCKS):
    n_rows = len(blk["rows"])
    blk_h = n_rows * cell_h + 0.10
    is_mid = (blk["id"] == "mid")
    is_confl = blk.get("is_confluence", False)
    
    # Left Main Card (x: 0.25 to 2.25)
    card_w = 1.95
    card_bg = "#1f242c" if is_mid else ("#16231d" if is_confl else HEADER_BG)
    ax_top.add_patch(FancyBboxPatch(
        (0.25, cursor_y - blk_h + 0.05), card_w, blk_h - 0.10,
        boxstyle="round,pad=0.05", fc=card_bg, ec=blk["border"], lw=1.8 if is_mid or is_confl else 0.8, zorder=2
    ))
    
    mid_cx = 0.25 + card_w / 2
    ax_top.text(mid_cx, cursor_y - 0.36, blk["title"],
                ha="center", va="center", fontsize=9.8, fontweight="bold",
                color=blk["color"], zorder=3)
    ax_top.text(mid_cx, cursor_y - 0.64, f"({blk['sub']})",
                ha="center", va="center", fontsize=7.4, fontweight="bold",
                color=blk["color"] if is_mid or is_confl else ACCENT, zorder=3)
    if n_rows > 2:
        ax_top.text(mid_cx, cursor_y - 0.95, blk["desc"],
                    ha="center", va="center", fontsize=6.2, color="#8b949e", zorder=3)
        
    # Sub-row Pills (x: 2.30 to 3.52)
    pill_x = 2.30
    pill_w = 1.22
    
    for r_idx, (r_title, r_sub, r_dict) in enumerate(blk["rows"]):
        row_y = cursor_y - (r_idx + 1) * cell_h + 0.04
        
        pill_fc = "#22272e" if "Volledig" not in r_title else "#1c2c3e"
        pill_ec = BORDER if "Volledig" not in r_title else "#388bfd"
        ax_top.add_patch(FancyBboxPatch(
            (pill_x, row_y + 0.03), pill_w, cell_h - 0.06,
            boxstyle="round,pad=0.03", fc=pill_fc, ec=pill_ec, lw=0.8, zorder=2
        ))
        
        ax_top.text(pill_x + pill_w / 2, row_y + cell_h / 2 + 0.10, r_title,
                    ha="center", va="center", fontsize=6.8, fontweight="bold",
                    color=blk["color"] if is_mid else ("#69f0ae" if is_confl else "white"), zorder=3)
        ax_top.text(pill_x + pill_w / 2, row_y + cell_h / 2 - 0.12, r_sub,
                    ha="center", va="center", fontsize=5.6, color="#8b949e", zorder=3)
        
        # Cells for 12 months
        for m_idx, m_name in enumerate(MONTHS):
            m_num = m_idx + 1
            cx = margin_l + m_idx * cell_w
            pad_x = 0.035
            pad_y = 0.03
            
            mid_x = cx + cell_w / 2
            mid_y = row_y + cell_h / 2
            
            if is_confl:
                # Confluence badge rendering
                item = r_dict[m_num]
                fc = item["color"]
                tc = item["tc"]
                tag = item["tag"]
                
                ax_top.add_patch(FancyBboxPatch(
                    (cx + pad_x, row_y + pad_y),
                    cell_w - 2 * pad_x, cell_h - 2 * pad_y,
                    boxstyle="round,pad=0.04", fc=fc, ec="#0d1117", lw=1.0, zorder=3
                ))
                
                # Split text: Title + Subtitle
                lines = tag.split("\n")
                ax_top.text(mid_x, mid_y + 0.12, lines[0],
                            ha="center", va="center", fontsize=6.8, fontweight="bold",
                            color=tc, zorder=4)
                ax_top.text(mid_x, mid_y - 0.14, lines[1] if len(lines) > 1 else "",
                            ha="center", va="center", fontsize=5.6, fontweight="bold",
                            color=tc, zorder=4)
            else:
                s = r_dict[m_num]
                avg = s["avg"]
                wr = s["wr"]
                n = s["n"]
                cls, _ = classify(avg, wr)
                fc = COLORS[cls]
                tc = TEXT_ON[cls]
                
                is_current_cell = (blk["id"] == "mid" and m_idx == 8 and r_idx == 1) # Midterm Sep 2H
                
                ax_top.add_patch(FancyBboxPatch(
                    (cx + pad_x, row_y + pad_y),
                    cell_w - 2 * pad_x, cell_h - 2 * pad_y,
                    boxstyle="round,pad=0.04", fc=fc, ec=GOLD if is_current_cell else "#0d1117",
                    lw=2.5 if is_current_cell else 1.0, zorder=4 if is_current_cell else 2
                ))
                
                sign = "+" if avg >= 0 else ""
                ax_top.text(mid_x, mid_y + 0.15, f"{sign}{avg:.2f}%",
                            ha="center", va="center", fontsize=8.0, fontweight="bold",
                            color=tc, zorder=5)
                ax_top.text(mid_x, mid_y - 0.07, f"{wr:.0f}% WR",
                            ha="center", va="center", fontsize=6.4,
                            color=tc, alpha=0.9, zorder=5)
                ax_top.text(mid_x, mid_y - 0.22, f"n={n}",
                            ha="center", va="center", fontsize=5.2,
                            color=tc, alpha=0.65, zorder=5)
                
                if is_current_cell:
                    ax_top.text(mid_x, row_y + cell_h - 0.08, "★ NU (2026)",
                                ha="center", va="center", fontsize=5.8, fontweight="bold",
                                color=GOLD, zorder=6)

    cursor_y -= (blk_h + 0.14)

# ── BOTTOM PANEL: 24-PERIOD CONFLUENCE TRAJECTORY ─────────────────────────────
ax_bot = fig.add_subplot(gs[1])
ax_bot.set_facecolor(PANEL)

p_labels = []
ann_curve = []
mid_curve = []
pre_curve = []
elec_curve = []

ann_bars = []
mid_bars = []

for m in range(1, 13):
    m_name = MONTHS[m - 1]
    # 1H
    p_labels.append(f"{m_name}\n1H")
    ann_bars.append(ann_1h[m]["avg"])
    mid_bars.append(mid_1h[m]["avg"])
    # 2H
    p_labels.append(f"{m_name}\n2H")
    ann_bars.append(ann_2h[m]["avg"])
    mid_bars.append(mid_2h[m]["avg"])

ann_cum = np.cumsum(ann_bars)
mid_cum = np.cumsum(mid_bars)

x24 = np.arange(24)
bar_w = 0.36

# Grouped bars: Annual vs Midterm
ax_bot.bar(x24 - bar_w/2, ann_bars, width=bar_w, color="#388bfd", label="Jaarlijks Gemiddelde (Alle Jaren)", alpha=0.85, zorder=3)
ax_bot.bar(x24 + bar_w/2, mid_bars, width=bar_w, color=GOLD, label="Midterm Regime (Huidig 2026)", alpha=0.95, zorder=3)

ax_bot.axhline(0, color="#8b949e", lw=1.0, ls="-", zorder=2)

# Twin Axis for Cumulative Curves
ax_twin = ax_bot.twinx()
ax_twin.plot(x24, ann_cum, color="#58a6ff", lw=2.6, marker="s", markersize=4, label="Cumulatief Jaarlijks (%)", zorder=5)
ax_twin.plot(x24, mid_cum, color=GOLD, lw=2.8, marker="o", markersize=4.5, label="Cumulatief Midterm 2026 (%)", zorder=6)

ax_twin.set_ylabel("Cumulatief Koersverloop (%)", color=GOLD, fontsize=9.5, fontweight="bold")
ax_twin.tick_params(colors=GOLD, labelsize=8)
ax_twin.grid(False)

# Labels & Styling
ax_bot.set_xticks(x24)
ax_bot.set_xticklabels(p_labels, fontsize=7.6, fontweight="bold", color="#c9d1d9")
ax_bot.set_ylabel("Rendement per Periode (%)", color="#c9d1d9", fontsize=9, fontweight="bold")
ax_bot.set_title("De 24-Perioden Confluentie-Puls: Jaarlijks Gemiddelde (Blauw) vs. Midterm Regime (Goud)",
                 fontsize=11.5, fontweight="bold", color="white", pad=12)
ax_bot.tick_params(colors="#8b949e", labelsize=8)
ax_bot.grid(True, axis="y", color="#30363d", ls="--", lw=0.6, alpha=0.7, zorder=1)
ax_bot.set_xlim(-0.8, 23.8)
ax_bot.set_ylim(-2.8, 4.4)

# Key Confluence Annotations
# Jan 1H (index 0): Both strong positive
ax_bot.annotate("A+ Confluentie Start\n(Jaar +1.28% | Mid +1.73%)", xy=(0, 1.73), xytext=(0, 2.9),
                arrowprops=dict(facecolor="#00c853", shrink=0.08, width=1, headwidth=4),
                ha="center", fontsize=6.5, fontweight="bold", color="#69f0ae",
                bbox=dict(boxstyle="round,pad=0.2", fc="#161b22", ec="#00c853", lw=0.8), zorder=7)

# Summer Divergence: May 2H / Jun 2H
ax_bot.annotate("Zomerdivergentie\nMidterm zakt in dal\n(Mei 2H: -1.19%)", xy=(9, -1.19), xytext=(9, -2.15),
                arrowprops=dict(facecolor="#ffd600", shrink=0.08, width=1, headwidth=4),
                ha="center", fontsize=6.5, fontweight="bold", color="#ffd600",
                bbox=dict(boxstyle="round,pad=0.2", fc="#161b22", ec="#ffd600", lw=0.8), zorder=7)

# Danger Oct 1H (index 18): Both negative
ax_bot.annotate("Dubbel Risico Zone\n(Jaar -0.88% | Mid -1.45%)", xy=(18, -1.45), xytext=(18, -2.15),
                arrowprops=dict(facecolor="#e53935", shrink=0.08, width=1, headwidth=4),
                ha="center", fontsize=6.5, fontweight="bold", color="#ef9a9a",
                bbox=dict(boxstyle="round,pad=0.2", fc="#161b22", ec="#e53935", lw=0.8), zorder=7)

# Oct 2H Reversal (index 19)
ax_bot.annotate("Vroege Ommekeer\nMidterm +1.72% (62% WR)", xy=(19, 1.72), xytext=(19, 2.7),
                arrowprops=dict(facecolor="#69f0ae", shrink=0.08, width=1, headwidth=4),
                ha="center", fontsize=6.5, fontweight="bold", color="#69f0ae",
                bbox=dict(boxstyle="round,pad=0.2", fc="#161b22", ec="#69f0ae", lw=0.8), zorder=7)

# November 2H Election Surge (index 21)
ax_bot.annotate("A+ Verkiezingsexplosie\nMidterm Nov 2H: +2.35%\n(100% Win Rate!)", xy=(21, 2.35), xytext=(21, 3.65),
                arrowprops=dict(facecolor=GOLD, shrink=0.08, width=1, headwidth=4),
                ha="center", fontsize=6.8, fontweight="bold", color=GOLD,
                bbox=dict(boxstyle="round,pad=0.25", fc="#161b22", ec=GOLD, lw=1.0), zorder=9)

# Legends for Bottom Panel
h1, l1 = ax_bot.get_legend_handles_labels()
h2, l2 = ax_twin.get_legend_handles_labels()
ax_bot.legend(h1 + h2, l1 + l2, loc="upper left", facecolor=HEADER_BG, edgecolor=BORDER, fontsize=7.5, ncol=2)

for s_ax in [ax_bot, ax_twin]:
    for spine in ["top", "right", "left", "bottom"]:
        s_ax.spines[spine].set_color(BORDER)

plt.tight_layout()

# Save combined figure
combined_path = FIGURES_DIR / "combined_annual_presidential_cycle.png"
fig.savefig(combined_path, dpi=200, facecolor=BG)
plt.close()
print(f"Saved combined master dashboard: {combined_path}")

# Copy to targets
for dest in [
    PACKAGE_DIR / "combined_annual_presidential_cycle.png",
    ANNUAL_PACKAGE_DIR / "combined_annual_presidential_cycle.png",
    DATASENTE_DIR / "combined_annual_presidential_cycle.png",
    DATASENTE_IMG_DIR / "combined_annual_presidential_cycle.png",
    Path(r"C:\Users\ROB5293\.gemini\antigravity-ide\brain\3809dc40-c017-47fc-bc95-09b8200d75c4") / "combined_annual_presidential_cycle.png"
]:
    shutil.copy2(combined_path, dest)

print("Copied master dashboard to all distribution folders.")
print("Done!")
