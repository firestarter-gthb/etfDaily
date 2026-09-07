"""
Seasonal Confluence Infographic — Methode 2: Samenloop van Cycli
=================================================================
Visualizes the combination of the 24 OpEx periods and the 4-year Presidential cycle:
- Decision Engine / Traffic Light Model (Dubbel Groen, Divergentie, Dubbel Rood)
- Empirical 24-period Confluence Pulse for Midterm Years (like 2026)
- Position sizing & Option Strategy Allocation Guide
"""
from pathlib import Path
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

# ── 1. Load Data ─────────────────────────────────────────────────────────────
print("Loading SPY data...")
raw = yf.download("SPY", start="1993-01-01", progress=False)
if isinstance(raw.columns, pd.MultiIndex):
    raw.columns = raw.columns.droplevel(1)
price = (raw["Adj Close"] if "Adj Close" in raw.columns else raw["Close"]).dropna()
max_date = price.index.max()

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
        r_1h = (sub.iloc[mid_idx] / sub.iloc[0] - 1) * 100
        r_2h = (sub.iloc[-1] / sub.iloc[mid_idx] - 1) * 100
        records.append({
            "Year": y, "Month": m, "CycleKey": y % 4,
            "r_1h": r_1h, "r_2h": r_2h
        })

df = pd.DataFrame(records)

# ── 2. Color Palette & Dark Theme ─────────────────────────────────────────────
BG = "#0d1117"
PANEL = "#161b22"
HEADER_BG = "#21262d"
BORDER = "#30363d"
ACCENT = "#00d2ff"
GREEN_A_PLUS = "#00e676"  # Strong Green
GREEN_LIGHT  = "#69f0ae"
YELLOW_WARN  = "#ffd600"  # Divergence
RED_DANGER   = "#ff1744"  # Strong Red
RED_LIGHT    = "#ff8a80"

fig = plt.figure(figsize=(16, 12), facecolor=BG)
gs = fig.add_gridspec(2, 1, height_ratios=[1.15, 1.25], hspace=0.22)

# ── 3. Panel 1: The 4-State Confluence Decision Engine ────────────────────────
ax1 = fig.add_subplot(gs[0])
ax1.set_facecolor(BG)
ax1.axis("off")

w1 = 16.0
h1 = 6.2
ax1.set_xlim(0, w1)
ax1.set_ylim(0, h1)

# Header Title Box
ax1.add_patch(FancyBboxPatch(
    (0.4, h1 - 1.15), w1 - 0.8, 0.98,
    boxstyle="round,pad=0.03", fc=HEADER_BG, ec=ACCENT, lw=1.6, zorder=2
))
ax1.text(w1 / 2, h1 - 0.50,
         "Seasonal Confluence Model — Methode 2: Samenloop van Cycli",
         ha="center", va="center", fontsize=15.5, fontweight="bold", color="white", zorder=3)
ax1.text(w1 / 2, h1 - 0.85,
         "Het Stoplicht-Beslismodel: Combinatie van Jaarlijkse 24 OpEx-Perioden en het 4-Jarige Presidentscyclus Regime",
         ha="center", va="center", fontsize=9.2, color="#8b949e", zorder=3)

# 4 Decision Cards
card_w = 3.65
card_h = 4.3
card_y = 0.4
card_xs = [0.4 + i * 3.82 for i in range(4)]

cards_meta = [
    {
        "status": "A+ SETUP: DUBBEL GROEN",
        "tag": "Maximal Bullish Confluence",
        "color": GREEN_A_PLUS,
        "border": "#00c853",
        "bg": "rgba(0, 230, 118, 0.08)",
        "signal": "Positiegrootte: 100% – 125%",
        "jaar": "POSITIEF (Score ≥ +0.5%)",
        "pres": "POSITIEF (Macro-wind mee)",
        "strat": "Optiestrategie:\n• Bull Put Spreads (30-45 DTE)\n• Long Calls / Diagonal Spreads\n• Agressief Dip-Buying",
        "examples": "Praktijkvoorbeelden:\n• Midterm Nov (+4.04% na verkiezing)\n• Dec 1H (+1.51%, 79% WR)\n• Pre-Election Juli (100% WR)"
    },
    {
        "status": "DIVERGENTIE TYPE 1",
        "tag": "Jaar Groen · Cyclus Rood",
        "color": YELLOW_WARN,
        "border": "#fbc02d",
        "bg": "rgba(255, 214, 0, 0.07)",
        "signal": "Positiegrootte: 25% – 50%",
        "jaar": "POSITIEF (Normaal Seizoenssterk)",
        "pres": "NEGATIEF (Macro-tegenwind)",
        "strat": "Optiestrategie:\n• Covered Calls (Winstneming)\n• Iron Condors (Delta-neutraal)\n• Halveer hefboom / Wachten",
        "examples": "Praktijkvoorbeelden:\n• Midterm Mei/Juni (Jaarcyclus is\n  normaal groen, maar Midterm daalt)"
    },
    {
        "status": "DIVERGENTIE TYPE 2",
        "tag": "Jaar Rood · Cyclus Groen",
        "color": "#40c4ff",
        "border": "#00b0ff",
        "bg": "rgba(0, 176, 255, 0.07)",
        "signal": "Positiegrootte: 25% – 50%",
        "jaar": "NEGATIEF (Normaal Zwakke Periode)",
        "pres": "POSITIEF (Cyclus-injectie)",
        "strat": "Optiestrategie:\n• Selectieve Alpha Plays\n• Strakke trailing stop-losses\n• Kleine Call Spreads",
        "examples": "Praktijkvoorbeelden:\n• Pre-Election September\n  (Herstelt direct na de augustusdip,\n  tegen de normale beurstrend in)"
    },
    {
        "status": "GEVAARZONE: DUBBEL ROOD",
        "tag": "Maximal Defensive Confluence",
        "color": RED_DANGER,
        "border": "#d50000",
        "bg": "rgba(255, 23, 68, 0.09)",
        "signal": "Positiegrootte: 0% Long / Hedges",
        "jaar": "NEGATIEF (Historische Daling)",
        "pres": "NEGATIEF (Macro-vallei)",
        "strat": "Optiestrategie:\n• 100% Cash / Geen Longs\n• Long Puts & Bear Call Spreads\n• VIX Call Spreads / Hedges",
        "examples": "Praktijkvoorbeelden:\n• Midterm Oktober 1H (-1.45%)\n• Pre-Election Augustus (-4.68%)\n• September Flash-Crash Vensters"
    }
]

for i, c in enumerate(cards_meta):
    cx = card_xs[i]
    ax1.add_patch(FancyBboxPatch(
        (cx, card_y), card_w, card_h,
        boxstyle="round,pad=0.04", fc=PANEL, ec=c["border"], lw=1.5, zorder=2
    ))
    
    # Card Header Pill
    ax1.add_patch(FancyBboxPatch(
        (cx + 0.15, card_y + card_h - 0.70), card_w - 0.3, 0.52,
        boxstyle="round,pad=0.03", fc=HEADER_BG, ec=c["color"], lw=1.0, zorder=3
    ))
    ax1.text(cx + card_w / 2, card_y + card_h - 0.35, c["status"],
             ha="center", va="center", fontsize=9.5, fontweight="bold", color=c["color"], zorder=4)
    ax1.text(cx + card_w / 2, card_y + card_h - 0.56, c["tag"],
             ha="center", va="center", fontsize=7.2, color="#8b949e", zorder=4)
    
    # Allocation Badge
    ax1.text(cx + card_w / 2, card_y + card_h - 1.05, c["signal"],
             ha="center", va="center", fontsize=8.8, fontweight="bold", color="white",
             bbox=dict(boxstyle="round,pad=0.25", fc=HEADER_BG, ec=BORDER, lw=0.8), zorder=4)
    
    # Inputs (Jaar vs Cyclus)
    ax1.text(cx + 0.2, card_y + card_h - 1.50, f"Jaarcyclus :  {c['jaar']}",
             ha="left", va="center", fontsize=7.8, color="#c9d1d9", zorder=4)
    ax1.text(cx + 0.2, card_y + card_h - 1.82, f"Presidents : {c['pres']}",
             ha="left", va="center", fontsize=7.8, color="#c9d1d9", zorder=4)
    
    # Divider line
    ax1.plot([cx + 0.2, cx + card_w - 0.2], [card_y + card_h - 2.05, card_y + card_h - 2.05],
             color=BORDER, lw=0.8, zorder=3)
    
    # Strategy
    ax1.text(cx + 0.2, card_y + card_h - 2.75, c["strat"],
             ha="left", va="center", fontsize=7.6, color="#e6edf3", zorder=4, multialignment="left")
    
    # Divider line
    ax1.plot([cx + 0.2, cx + card_w - 0.2], [card_y + card_h - 3.35, card_y + card_h - 3.35],
             color=BORDER, lw=0.8, zorder=3)
    
    # Examples
    ax1.text(cx + 0.2, card_y + card_h - 3.85, c["examples"],
             ha="left", va="center", fontsize=7.2, color="#8b949e", zorder=4, multialignment="left")

# ── 4. Panel 2: Live Confluence Roadmap for Midterm Year (2026) ───────────────
ax2 = fig.add_subplot(gs[1])
ax2.set_facecolor(PANEL)

labels = []
base_returns = []
midterm_returns = []
confluence_colors = []
confluence_tags = []

# Midterm is CycleKey == 2
for m in range(1, 13):
    m_name = MONTHS[m - 1]
    
    # 1H
    b1 = df[df["Month"] == m]["r_1h"].mean()
    m1 = df[(df["Month"] == m) & (df["CycleKey"] == 2)]["r_1h"].mean()
    labels.append(f"{m_name}\n1H")
    base_returns.append(b1)
    midterm_returns.append(m1)
    
    # Confluence logic for 1H
    if b1 > 0.4 and m1 > 0.4:
        confluence_colors.append(GREEN_A_PLUS)
        confluence_tags.append("🟢🟢 A+")
    elif b1 < -0.3 and m1 < -0.3:
        confluence_colors.append(RED_DANGER)
        confluence_tags.append("🔴🔴 Gevaar")
    elif (b1 > 0 and m1 < 0) or (b1 < 0 and m1 > 0):
        confluence_colors.append(YELLOW_WARN)
        confluence_tags.append("🟡 Conflict")
    else:
        confluence_colors.append("#78909c")
        confluence_tags.append("⚪ Neutraal")
        
    # 2H
    b2 = df[df["Month"] == m]["r_2h"].mean()
    m2 = df[(df["Month"] == m) & (df["CycleKey"] == 2)]["r_2h"].mean()
    labels.append(f"{m_name}\n2H")
    base_returns.append(b2)
    midterm_returns.append(m2)
    
    # Confluence logic for 2H
    if b2 > 0.4 and m2 > 0.4:
        confluence_colors.append(GREEN_A_PLUS)
        confluence_tags.append("🟢🟢 A+")
    elif b2 < -0.3 and m2 < -0.3:
        confluence_colors.append(RED_DANGER)
        confluence_tags.append("🔴🔴 Gevaar")
    elif (b2 > 0 and m2 < 0) or (b2 < 0 and m2 > 0):
        confluence_colors.append(YELLOW_WARN)
        confluence_tags.append("🟡 Conflict")
    else:
        confluence_colors.append("#78909c")
        confluence_tags.append("⚪ Neutraal")

x = np.arange(24)
bar_width = 0.38

# Side-by-side bars: Annual Base vs Midterm specific
b_bars = ax2.bar(x - bar_width/2, base_returns, width=bar_width, color="#455a64", label="Jaarlijkse Cyclus Baseline (33 jr)", zorder=3)
m_bars = ax2.bar(x + bar_width/2, midterm_returns, width=bar_width, color=confluence_colors, label="Midterm Jaar Cyclus (Regime 2026)", zorder=3)

ax2.axhline(0, color="#8b949e", lw=1.0, zorder=2)

# Add confluence tag badges above/below bars
for i in range(24):
    max_h = max(base_returns[i], midterm_returns[i])
    min_h = min(base_returns[i], midterm_returns[i])
    
    # Confluence label
    if max_h >= 0:
        badge_y = max(max_h, 0) + 0.35
    else:
        badge_y = min_h - 0.45
        
    # Format midterm value
    sign = "+" if midterm_returns[i] >= 0 else ""
    ax2.text(x[i] + bar_width/2, midterm_returns[i] + (0.12 if midterm_returns[i] >= 0 else -0.22),
             f"{sign}{midterm_returns[i]:.1f}%", ha="center", fontsize=6.8, fontweight="bold",
             color="white", zorder=5)

# Formatting Panel 2
ax2.set_xticks(x)
ax2.set_xticklabels(labels, fontsize=7.8, fontweight="bold", color="#c9d1d9")
ax2.set_ylabel("Gemiddeld Rendement per Periode (%)", color="#c9d1d9", fontsize=9.5, fontweight="bold")
ax2.set_title("Praktijktoepassing: Confluence Roadmap voor Midterm-Jaren (zoals 2026)",
              fontsize=11.5, fontweight="bold", color="white", pad=12)
ax2.tick_params(colors="#8b949e", labelsize=8)
ax2.grid(True, axis="y", color="#30363d", ls="--", lw=0.6, alpha=0.7, zorder=1)
ax2.set_xlim(-0.7, 23.7)
ax2.set_ylim(-2.8, 3.8)

# Specific Callout Annotations for Midterm Dynamics
ax2.annotate("[A+ DUBBEL GROEN]\nNieuwjaars Inflows\n(+1.73%)", xy=(0, 1.73), xytext=(0.5, 3.0),
             arrowprops=dict(facecolor=GREEN_A_PLUS, shrink=0.08, width=1, headwidth=4),
             ha="center", fontsize=7.0, fontweight="bold", color=GREEN_A_PLUS,
             bbox=dict(boxstyle="round,pad=0.25", fc="#161b22", ec=GREEN_A_PLUS, lw=0.9))

ax2.annotate("[DIVERGENTIE]\nJaar Groen, Midterm Rood\n(-1.19% Sell-in-May)", xy=(9, -1.19), xytext=(9, -2.05),
             arrowprops=dict(facecolor=YELLOW_WARN, shrink=0.08, width=1, headwidth=4),
             ha="center", fontsize=7.0, fontweight="bold", color=YELLOW_WARN,
             bbox=dict(boxstyle="round,pad=0.25", fc="#161b22", ec=YELLOW_WARN, lw=0.9))

ax2.annotate("[DUBBEL ROOD: GEVAAR]\nSeizoensvallei & Pre-Election Dip\n(Base -0.88% | Midterm -1.45%)", xy=(18, -1.45), xytext=(17.5, -2.25),
             arrowprops=dict(facecolor=RED_DANGER, shrink=0.08, width=1, headwidth=4),
             ha="center", fontsize=7.0, fontweight="bold", color=RED_DANGER,
             bbox=dict(boxstyle="round,pad=0.25", fc="#161b22", ec=RED_DANGER, lw=0.9))

ax2.annotate("[A+ DUBBEL GROEN]\nDe Grote Midterm Bodem\n(+1.72% Reversal)", xy=(19, 1.72), xytext=(18.2, 2.75),
             arrowprops=dict(facecolor=GREEN_A_PLUS, shrink=0.08, width=1, headwidth=4),
             ha="center", fontsize=7.0, fontweight="bold", color=GREEN_A_PLUS,
             bbox=dict(boxstyle="round,pad=0.25", fc="#161b22", ec=GREEN_A_PLUS, lw=0.9))

ax2.annotate("[A+ DUBBEL GROEN]\nPost-Election Reliefrally\n(+2.35% explosie)", xy=(21, 2.35), xytext=(22.0, 3.25),
             arrowprops=dict(facecolor=GREEN_A_PLUS, shrink=0.08, width=1, headwidth=4),
             ha="center", fontsize=7.0, fontweight="bold", color=GREEN_A_PLUS,
             bbox=dict(boxstyle="round,pad=0.25", fc="#161b22", ec=GREEN_A_PLUS, lw=0.9))

# Legend for bottom panel
ax2.legend(loc="upper left", bbox_to_anchor=(0.14, 0.98), framealpha=0.85, facecolor=HEADER_BG, edgecolor=BORDER, fontsize=8.2, labelcolor="white")

for spine in ["top", "right", "left", "bottom"]:
    ax2.spines[spine].set_color(BORDER)

plt.tight_layout()

# ── 5. Save to Targets ────────────────────────────────────────────────────────
fig_out1 = FIGURES_DIR / "seasonal_confluence_method2.png"
fig.savefig(fig_out1, dpi=200, facecolor=BG)
print(f"Saved figure: {fig_out1}")

fig_out_pkg = PACKAGE_DIR / "seasonal_confluence_method2.png"
shutil.copy2(fig_out1, fig_out_pkg)

fig_out_ds1 = DATASENTE_DIR / "seasonal_confluence_method2.png"
fig_out_ds2 = DATASENTE_IMG_DIR / "seasonal_confluence_method2.png"
shutil.copy2(fig_out1, fig_out_ds1)
shutil.copy2(fig_out1, fig_out_ds2)

# Copy to conversation artifact directory
artifact_img = Path(r"C:\Users\ROB5293\.gemini\antigravity-ide\brain\dd99d209-d1e7-41fa-a165-17bc8389f138\seasonal_confluence_method2.png")
shutil.copy2(fig_out1, artifact_img)
print("Copied to conversation artifacts and DataSente.")
