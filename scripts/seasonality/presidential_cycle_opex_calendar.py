"""
Presidential Cycle OpEx Calendar — Premium Infographic
=======================================================
4-jarige presidentscyclus, OpEx-tot-OpEx classificatie:
  Sterk Groen  : avg > +1.5%
  Groen        : avg > +0.3%
  Neutraal     : -0.3% tot +0.3%
  Rood         : avg < -0.3%
  Sterk Rood   : avg < -1.5%
  (win-rate <45% verlaagt één klasse)
"""
from pathlib import Path
import pandas as pd
import numpy as np
import datetime
import warnings
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch

warnings.filterwarnings("ignore")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
FIGURES_DIR = BASE_DIR / "reports" / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# ── 1. Data ─────────────────────────────────────────────────────────────────
print("Downloading SPY data...")
raw = yf.download("SPY", period="max", progress=False)
if isinstance(raw.columns, pd.MultiIndex):
    raw.columns = raw.columns.droplevel(1)
raw.index = pd.to_datetime(raw.index)
price_col = "Adj Close" if "Adj Close" in raw.columns else "Close"
spy = raw[price_col].dropna()
max_date = spy.index.max()
print(f"  {spy.index[0].date()} to {max_date.date()} — {len(spy)} trading days\n")

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

CYCLE_LABELS = {1: "Post-Election", 2: "Midterm", 3: "Pre-Election", 0: "Election Year"}
CYCLE_SUBTITLE = {
    1: "2021 · 2025 · 2029",
    2: "2022 · 2026 · 2030",
    3: "2023 · 2027 · 2031",
    0: "2020 · 2024 · 2028",
}
CYCLE_ORDER = [1, 2, 3, 0]

# ── 2. OpEx berekening ───────────────────────────────────────────────────────
def get_3rd_friday(year, month):
    d = datetime.date(year, month, 1)
    while d.weekday() != 4:
        d += datetime.timedelta(days=1)
    d += datetime.timedelta(days=14)
    return pd.Timestamp(d)

opex_rows = []
for y in range(spy.index.min().year, spy.index.max().year + 1):
    for m in range(1, 13):
        target = get_3rd_friday(y, m)
        if target > max_date:
            continue
        valid = spy.index[spy.index <= target]
        if len(valid) == 0:
            continue
        opex_rows.append({"Year": y, "Month": m, "Price": spy.loc[valid[-1]]})

opex_df = pd.DataFrame(opex_rows)
opex_df["Return"] = opex_df["Price"].pct_change()
opex_df = opex_df.dropna(subset=["Return"])
opex_df["CycleKey"] = opex_df["Year"] % 4

# ── 3. Statistieken ──────────────────────────────────────────────────────────
stats = {}
for key in CYCLE_ORDER:
    sub = opex_df[opex_df["CycleKey"] == key]
    month_stats = {}
    for m_idx, m_name in enumerate(MONTHS):
        m_num = m_idx + 1
        m_data = sub[sub["Month"] == m_num]["Return"] * 100
        if len(m_data) == 0:
            month_stats[m_name] = {"avg": np.nan, "wr": np.nan, "n": 0}
        else:
            month_stats[m_name] = {
                "avg": m_data.mean(),
                "wr":  (m_data > 0).mean() * 100,
                "n":   len(m_data),
            }
    stats[key] = month_stats

# ── 4. Classificatie ─────────────────────────────────────────────────────────
def classify(avg, wr):
    """Geeft terug: kleur-string en label."""
    if np.isnan(avg):
        return "neutral", "N/A"

    score = avg
    # Win-rate correctie
    if wr < 42 and avg > 0:
        score -= 0.6
    if wr > 72 and avg < 0:
        score += 0.6

    if   score >  1.8: return "strong_green",  "Sterk +"
    elif score >  0.4: return "green",          "Positief"
    elif score > -0.4: return "neutral",        "Neutraal"
    elif score > -1.5: return "red",            "Negatief"
    else:              return "strong_red",     "Sterk -"

# ── 5. Kleurenpalet (dark premium) ───────────────────────────────────────────
COLORS = {
    "strong_green" : "#00c853",   # helder groen
    "green"        : "#69f0ae",   # licht groen
    "neutral"      : "#455a64",   # blauw-grijs
    "red"          : "#ef9a9a",   # licht rood
    "strong_red"   : "#e53935",   # helder rood
}
TEXT_ON = {
    "strong_green" : "white",
    "green"        : "#1a2a1a",
    "neutral"      : "#cfd8dc",
    "red"          : "#2a0a0a",
    "strong_red"   : "white",
}

BG    = "#0d1117"
PANEL = "#161b22"
HEADER_BG = "#21262d"
ACCENT = "#58a6ff"

# ── 6. Layout ────────────────────────────────────────────────────────────────
n_cycles = 4
n_months = 12
cell_w   = 1.0
cell_h   = 1.35
margin_l = 2.4    # ruimte voor cycle-label links
margin_t = 1.7    # header boven
margin_b = 1.2    # legenda onder

total_w = margin_l + n_months * cell_w + 0.3
total_h = margin_t + n_cycles * cell_h + margin_b

fig, ax = plt.subplots(figsize=(total_w, total_h), facecolor=BG)
ax.set_facecolor(BG)
ax.set_xlim(0, total_w)
ax.set_ylim(0, total_h)
ax.axis("off")

# ── 7. Titelbalk ─────────────────────────────────────────────────────────────
ax.add_patch(FancyBboxPatch(
    (0.15, total_h - 1.35), total_w - 0.3, 1.2,
    boxstyle="round,pad=0.05", fc=HEADER_BG, ec=ACCENT, lw=1.5, zorder=2
))
ax.text(total_w / 2, total_h - 0.55,
        "S&P 500 Presidential Cycle — OpEx Seasonality Calendar",
        ha="center", va="center", fontsize=14, fontweight="bold",
        color="white", zorder=3)
ax.text(total_w / 2, total_h - 0.97,
        "Classificatie op basis van OpEx-tot-OpEx rendement (3e vrijdag → 3e vrijdag)  |  SPY 1993–2026",
        ha="center", va="center", fontsize=8, color="#8b949e", zorder=3)

# ── 8. Maand-headers ─────────────────────────────────────────────────────────
header_y = total_h - margin_t + 0.08
for m_idx, m_name in enumerate(MONTHS):
    cx = margin_l + m_idx * cell_w + cell_w / 2
    ax.add_patch(FancyBboxPatch(
        (margin_l + m_idx * cell_w + 0.04, header_y - 0.28),
        cell_w - 0.08, 0.38,
        boxstyle="round,pad=0.04", fc=HEADER_BG, ec="#30363d", lw=0.8, zorder=2
    ))
    ax.text(cx, header_y - 0.08, m_name,
            ha="center", va="center", fontsize=9.5, fontweight="bold",
            color=ACCENT, zorder=3)

# ── 9. Cellen tekenen ────────────────────────────────────────────────────────
for row_idx, key in enumerate(CYCLE_ORDER):
    row_y = total_h - margin_t - (row_idx + 1) * cell_h

    # Links: cycle-label
    label_cx = margin_l / 2
    label_cy = row_y + cell_h / 2

    ax.add_patch(FancyBboxPatch(
        (0.1, row_y + 0.06), margin_l - 0.25, cell_h - 0.12,
        boxstyle="round,pad=0.06", fc=HEADER_BG, ec="#30363d", lw=0.8, zorder=2
    ))
    ax.text(label_cx, label_cy + 0.18, CYCLE_LABELS[key],
            ha="center", va="center", fontsize=9, fontweight="bold",
            color="white", zorder=3)
    ax.text(label_cx, label_cy - 0.18, CYCLE_SUBTITLE[key],
            ha="center", va="center", fontsize=6.5,
            color="#8b949e", zorder=3)

    # Jaar-indicator (welk jaar in cyclus zijn we)
    cycle_year_num = {1: "Jaar 1", 2: "Jaar 2", 3: "Jaar 3", 0: "Jaar 4"}
    ax.text(label_cx, row_y + 0.1, cycle_year_num[key],
            ha="center", va="center", fontsize=6,
            color=ACCENT, alpha=0.7, zorder=3)

    for m_idx, m_name in enumerate(MONTHS):
        s = stats[key][m_name]
        avg = s["avg"]
        wr  = s["wr"]
        n   = s["n"]
        cls, lbl = classify(avg, wr)
        fc = COLORS[cls]
        tc = TEXT_ON[cls]

        cx = margin_l + m_idx * cell_w
        pad = 0.06

        # Cel achtergrond
        ax.add_patch(FancyBboxPatch(
            (cx + pad, row_y + pad),
            cell_w - 2*pad, cell_h - 2*pad,
            boxstyle="round,pad=0.07",
            fc=fc, ec="#0d1117", lw=1.2, zorder=2
        ))

        mid_x = cx + cell_w / 2
        mid_y = row_y + cell_h / 2

        # Gemiddeld rendement (groot)
        sign = "+" if not np.isnan(avg) and avg >= 0 else ""
        avg_txt = f"{sign}{avg:.2f}%" if not np.isnan(avg) else "N/A"
        ax.text(mid_x, mid_y + 0.22, avg_txt,
                ha="center", va="center", fontsize=9.5, fontweight="bold",
                color=tc, zorder=3)

        # Win rate
        wr_txt = f"{wr:.0f}% WR" if not np.isnan(wr) else ""
        ax.text(mid_x, mid_y - 0.08, wr_txt,
                ha="center", va="center", fontsize=7,
                color=tc, alpha=0.85, zorder=3)

        # N observaties
        ax.text(mid_x, mid_y - 0.32, f"n={n}",
                ha="center", va="center", fontsize=5.5,
                color=tc, alpha=0.6, zorder=3)

# ── 10. Legenda ──────────────────────────────────────────────────────────────
leg_y  = margin_b * 0.55
leg_items = [
    ("strong_green", "Sterk Positief  avg > +1.8%"),
    ("green",        "Positief  avg > +0.4%"),
    ("neutral",      "Neutraal  -0.4% tot +0.4%"),
    ("red",          "Negatief  avg < -0.4%"),
    ("strong_red",   "Sterk Negatief  avg < -1.5%"),
]
n_items   = len(leg_items)
box_w     = 0.38
box_h     = 0.28
spacing   = (total_w - 0.8) / n_items
start_x   = 0.4

for i, (cls, label) in enumerate(leg_items):
    bx = start_x + i * spacing
    ax.add_patch(FancyBboxPatch(
        (bx, leg_y - box_h/2), box_w, box_h,
        boxstyle="round,pad=0.04", fc=COLORS[cls], ec="#30363d", lw=0.8, zorder=2
    ))
    ax.text(bx + box_w + 0.12, leg_y, label,
            va="center", fontsize=7, color="#c9d1d9", zorder=3)

ax.text(total_w/2, 0.25,
        "Gemiddeld rendement op basis van historische OpEx-cycli  |  Win Rate = % maanden positief gesloten",
        ha="center", va="center", fontsize=6.5, color="#6e7681", zorder=3)

# ── 11. Huidige positie markeren (2026 = Midterm jaar 2) ────────────────────
current_year = 2026
current_month_idx = 7  # Aug 2026 is volgende OpEx maand (huidige positie)
current_cycle = current_year % 4  # = 2 = Midterm = row 1

row_idx_current = CYCLE_ORDER.index(current_cycle)
row_y_current = total_h - margin_t - (row_idx_current + 1) * cell_h
cx_current = margin_l + current_month_idx * cell_w
pad = 0.06

# Gouden rand om huidige maand
ax.add_patch(FancyBboxPatch(
    (cx_current + pad - 0.04, row_y_current + pad - 0.04),
    cell_w - 2*pad + 0.08, cell_h - 2*pad + 0.08,
    boxstyle="round,pad=0.07",
    fc="none", ec="#ffd700", lw=2.5, zorder=4
))
ax.text(cx_current + cell_w/2, row_y_current + cell_h - 0.09,
        "NU", ha="center", va="center", fontsize=6, fontweight="bold",
        color="#ffd700", zorder=5)

plt.tight_layout(pad=0.2)
fig_path = FIGURES_DIR / "presidential_cycle_opex_calendar.png"
plt.savefig(fig_path, dpi=180, bbox_inches="tight", facecolor=BG)
plt.close()
print(f"Infographic opgeslagen: {fig_path}")
