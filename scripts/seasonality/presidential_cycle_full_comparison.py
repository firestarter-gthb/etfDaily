"""
Presidential Cycle Seasonality: Calendar (EOM→EOM) vs OpEx (3rd Friday→3rd Friday)
=====================================================================================
Doel: Bepaal welke meetmethode (1e-tot-1e of expiratie-tot-expiratie) een beter
      signaal geeft voor elk van de 4 presidentscyclusjaren.

Presidentiële cyclus:
  jaar % 4 == 1 → Post-Election  (2021, 2025, ...)
  jaar % 4 == 2 → Midterm        (2022, 2026, ...)
  jaar % 4 == 3 → Pre-Election   (2023, 2027, ...)
  jaar % 4 == 0 → Election       (2020, 2024, ...)
"""
from pathlib import Path
import pandas as pd
import numpy as np
import datetime
import calendar
import warnings
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.colors import LinearSegmentedColormap

warnings.filterwarnings("ignore")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
FIGURES_DIR = BASE_DIR / "reports" / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# ── 1. Data downloaden ──────────────────────────────────────────────────────
print("Downloading SPY data (max history)...")
raw = yf.download("SPY", period="max", progress=False)
if isinstance(raw.columns, pd.MultiIndex):
    raw.columns = raw.columns.droplevel(1)
raw.index = pd.to_datetime(raw.index)
price_col = "Adj Close" if "Adj Close" in raw.columns else "Close"
spy = raw[price_col].dropna()
print(f"SPY data: {spy.index[0].date()} → {spy.index[-1].date()} ({len(spy)} trading days)\n")

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

CYCLE_LABELS = {
    1: "Post-Election",
    2: "Midterm",
    3: "Pre-Election",
    0: "Election"
}
CYCLE_ORDER = [1, 2, 3, 0]

def get_stats(series):
    """Bereken win-rate en gemiddeld rendement (%)."""
    s = series.dropna()
    if len(s) == 0:
        return np.nan, np.nan, 0
    win = (s > 0).mean() * 100
    avg = s.mean() * 100
    return win, avg, len(s)

# ── 2. METHODE A: Calendar / EOM→EOM ───────────────────────────────────────
monthly_eom = spy.resample("ME").last()
eom_ret = monthly_eom.pct_change().dropna()

eom_df = pd.DataFrame({
    "Return": eom_ret,
    "Month":  eom_ret.index.month,
    "Year":   eom_ret.index.year,
})
eom_df["CycleKey"] = eom_df["Year"] % 4

# ── 3. METHODE B: OpEx / 3rd Friday→3rd Friday ──────────────────────────────
def get_3rd_friday(year, month):
    d = datetime.date(year, month, 1)
    while d.weekday() != 4:           # zoek eerste vrijdag
        d += datetime.timedelta(days=1)
    d += datetime.timedelta(days=14)  # + 2 weken = 3e vrijdag
    return pd.Timestamp(d)

min_y = spy.index.min().year
max_y = spy.index.max().year
max_date = spy.index.max()

opex_rows = []
for y in range(min_y, max_y + 1):
    for m in range(1, 13):
        target = get_3rd_friday(y, m)
        if target > max_date:
            continue
        valid = spy.index[spy.index <= target]
        if len(valid) == 0:
            continue
        actual = valid[-1]
        opex_rows.append({"Year": y, "Month": m, "Price": spy.loc[actual]})

opex_df_raw = pd.DataFrame(opex_rows)
opex_df_raw["Return"] = opex_df_raw["Price"].pct_change()
opex_df_raw = opex_df_raw.dropna(subset=["Return"])
opex_df_raw["CycleKey"] = opex_df_raw["Year"] % 4

# ── 4. Statistieken per cyclus × maand voor beide methoden ──────────────────
def build_stats_table(df, method_name):
    """Bouw een dict: {cycle_key: DataFrame met statistieken per maand}."""
    result = {}
    for key in CYCLE_ORDER:
        subset = df[df["CycleKey"] == key]
        rows = []
        for m in range(1, 13):
            m_data = subset[subset["Month"] == m]["Return"]
            win, avg, n = get_stats(m_data)
            rows.append({
                "Maand": MONTHS[m - 1],
                f"WR%":  win,
                f"Avg%": avg,
                "N":     n
            })
        result[key] = pd.DataFrame(rows).set_index("Maand")
    return result

eom_stats  = build_stats_table(eom_df,      "EOM")
opex_stats = build_stats_table(opex_df_raw, "OpEx")

# ── 5. Console output ────────────────────────────────────────────────────────
def fmt_win(v):
    if np.isnan(v): return "  N/A"
    return f"{v:5.1f}%"

def fmt_avg(v):
    if np.isnan(v): return "   N/A"
    sign = "+" if v >= 0 else ""
    return f"{sign}{v:5.2f}%"

header = (
    f"\n{'':12}"
    f"{'── CALENDAR (EOM→EOM) ──':^26}"
    f"   "
    f"{'── OPEX (3rd Fri→3rd Fri) ──':^26}"
    f"   VERSCHIL"
)
subheader = (
    f"{'Maand':<6} {'WR%':>6} {'Avg%':>7} {'N':>3}"
    f"   "
    f"{'WR%':>6} {'Avg%':>7} {'N':>3}"
    f"   {'ΔAvg':>7}"
)

for key in CYCLE_ORDER:
    label = CYCLE_LABELS[key]
    years = [y for y in range(spy.index.year.min(), spy.index.year.max() + 1) if y % 4 == key]
    print("=" * 72)
    print(f"  {label.upper()} JAREN ({', '.join(map(str, years))})")
    print("=" * 72)
    print(header)
    print("-" * 72)
    print(subheader)
    print("-" * 72)

    e = eom_stats[key]
    o = opex_stats[key]

    for m_name in MONTHS:
        wr_e  = e.loc[m_name, "WR%"]  if m_name in e.index  else np.nan
        avg_e = e.loc[m_name, "Avg%"] if m_name in e.index  else np.nan
        n_e   = int(e.loc[m_name, "N"])  if m_name in e.index  else 0

        wr_o  = o.loc[m_name, "WR%"]  if m_name in o.index  else np.nan
        avg_o = o.loc[m_name, "Avg%"] if m_name in o.index  else np.nan
        n_o   = int(o.loc[m_name, "N"])  if m_name in o.index  else 0

        delta = (avg_o - avg_e) if not (np.isnan(avg_o) or np.isnan(avg_e)) else np.nan

        # Visueel markeren: sterk positief (★) of sterk negatief (✗)
        e_mark = " ★" if (not np.isnan(avg_e) and avg_e > 1.5)  else (" ✗" if (not np.isnan(avg_e) and avg_e < -1.0) else "  ")
        o_mark = " ★" if (not np.isnan(avg_o) and avg_o > 1.5)  else (" ✗" if (not np.isnan(avg_o) and avg_o < -1.0) else "  ")

        delta_str = f"{'+' if delta >=0 else ''}{delta:.2f}%" if not np.isnan(delta) else "   N/A"

        print(
            f"{m_name:<6} {fmt_win(wr_e):>6} {fmt_avg(avg_e):>7}{e_mark} {n_e:>2}"
            f"   "
            f"{fmt_win(wr_o):>6} {fmt_avg(avg_o):>7}{o_mark} {n_o:>2}"
            f"   {delta_str:>7}"
        )
    print()

# ── 6. Samenvatting: welke methode wint? ────────────────────────────────────
print("=" * 72)
print("  SAMENVATTING: WELKE METHODE GEEFT HET STERKSTE SIGNAAL?")
print("=" * 72)
print(f"\n  ★ = gemiddeld rendement > +1.5%  |  ✗ = gemiddeld rendement < -1.0%\n")

for key in CYCLE_ORDER:
    label = CYCLE_LABELS[key]
    e = eom_stats[key]
    o = opex_stats[key]

    strong_e   = (e["Avg%"] >  1.5).sum() + (e["Avg%"] < -1.0).sum()
    strong_o   = (o["Avg%"] >  1.5).sum() + (o["Avg%"] < -1.0).sum()
    winner     = "OPEX" if strong_o > strong_e else ("CALENDAR" if strong_e > strong_o else "GELIJK")
    avg_diff   = (o["Avg%"] - e["Avg%"]).mean()

    print(f"  {label:<18} → Sterke maanden: Calendar={strong_e}  OpEx={strong_o}  "
          f"│ Gem. ΔAvg={avg_diff:+.3f}%  │ Voorkeur: {winner}")

print()

# ── 7. Heatmap visualisatie ──────────────────────────────────────────────────
print("\nGenerating heatmap charts...")

fig, axes = plt.subplots(4, 2, figsize=(18, 22))
fig.suptitle(
    "S&P 500 (SPY) — Presidential Cycle Seasonality\nCalendar (EOM→EOM) vs OpEx (3rd Friday→3rd Friday)",
    fontsize=15, fontweight="bold", y=0.98
)

# Custom colormap: rood → wit → groen
cmap = LinearSegmentedColormap.from_list(
    "rdgrn", ["#c0392b", "#f5f5f5", "#27ae60"]
)

for row_idx, key in enumerate(CYCLE_ORDER):
    label = CYCLE_LABELS[key]
    e = eom_stats[key]
    o = opex_stats[key]

    for col_idx, (stats, method) in enumerate([(e, "Calendar  (EOM→EOM)"), (o, "OpEx  (3rd Fri→3rd Fri)")]):
        ax = axes[row_idx][col_idx]

        avg_vals = stats["Avg%"].values.reshape(1, -1)
        wr_vals  = stats["WR%"].values

        vmax = max(abs(np.nanmin(avg_vals)), abs(np.nanmax(avg_vals)), 1.0)
        im = ax.imshow(avg_vals, cmap=cmap, aspect="auto",
                       vmin=-vmax, vmax=vmax)

        # Labels in elke cel
        for m_idx, m_name in enumerate(MONTHS):
            avg_v = stats.loc[m_name, "Avg%"] if m_name in stats.index else np.nan
            wr_v  = stats.loc[m_name, "WR%"]  if m_name in stats.index else np.nan
            n_v   = int(stats.loc[m_name, "N"]) if m_name in stats.index else 0

            if not np.isnan(avg_v):
                sign = "+" if avg_v >= 0 else ""
                txt_color = "white" if abs(avg_v) > vmax * 0.55 else "black"
                ax.text(m_idx, 0, f"{sign}{avg_v:.2f}%\n{wr_v:.0f}% WR\nN={n_v}",
                        ha="center", va="center", fontsize=7.5,
                        color=txt_color, fontweight="bold")

        ax.set_xticks(range(12))
        ax.set_xticklabels(MONTHS, fontsize=8)
        ax.set_yticks([])
        ax.set_title(f"{label}  ·  {method}", fontsize=9, fontweight="bold", pad=6)

        # Kleurenlegenda
        plt.colorbar(im, ax=ax, orientation="vertical", shrink=0.8,
                     label="Gem. Rendement (%)")

plt.tight_layout(rect=[0, 0, 1, 0.97])
fig_path = FIGURES_DIR / "presidential_cycle_seasonality_comparison.png"
plt.savefig(fig_path, dpi=150, bbox_inches="tight")
plt.close()
print(f"Chart saved: {fig_path}\n")

# ── 8. Bar-chart: gemiddeld maandrendement per cyclus, beide methoden ────────
fig2, axes2 = plt.subplots(4, 1, figsize=(16, 20))
fig2.suptitle(
    "Gemiddeld Maandrendement SPY — Presidential Cycle\nCalendar vs OpEx (per cyclusjaar)",
    fontsize=14, fontweight="bold"
)

bar_width = 0.38
x = np.arange(12)

for row_idx, key in enumerate(CYCLE_ORDER):
    label = CYCLE_LABELS[key]
    ax    = axes2[row_idx]
    e = eom_stats[key]
    o = opex_stats[key]

    avg_e = [e.loc[m, "Avg%"] if m in e.index else 0 for m in MONTHS]
    avg_o = [o.loc[m, "Avg%"] if m in o.index else 0 for m in MONTHS]

    colors_e = ["#27ae60" if v >= 0 else "#c0392b" for v in avg_e]
    colors_o = ["#2980b9" if v >= 0 else "#e67e22" for v in avg_o]

    bars_e = ax.bar(x - bar_width/2, avg_e, bar_width,
                    color=colors_e, alpha=0.85, label="Calendar (EOM→EOM)", edgecolor="white", linewidth=0.4)
    bars_o = ax.bar(x + bar_width/2, avg_o, bar_width,
                    color=colors_o, alpha=0.85, label="OpEx (3rd Fri→3rd Fri)", edgecolor="white", linewidth=0.4)

    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(MONTHS, fontsize=9)
    ax.set_ylabel("Gem. Rendement (%)", fontsize=8)
    ax.set_title(f"{label} (jaar % 4 = {key})", fontsize=10, fontweight="bold")
    ax.legend(fontsize=8, loc="upper left")
    ax.grid(axis="y", alpha=0.3)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:+.1f}%"))

    # Waarden boven de staven
    for bar in bars_e:
        h = bar.get_height()
        if abs(h) > 0.01:
            ax.text(bar.get_x() + bar.get_width()/2, h + (0.05 if h >= 0 else -0.15),
                    f"{h:+.2f}", ha="center", fontsize=6, color="black")
    for bar in bars_o:
        h = bar.get_height()
        if abs(h) > 0.01:
            ax.text(bar.get_x() + bar.get_width()/2, h + (0.05 if h >= 0 else -0.15),
                    f"{h:+.2f}", ha="center", fontsize=6, color="black")

plt.tight_layout()
fig2_path = FIGURES_DIR / "presidential_cycle_bar_comparison.png"
plt.savefig(fig2_path, dpi=150, bbox_inches="tight")
plt.close()
print(f"Bar chart saved: {fig2_path}\n")

print("Klaar! Beide grafieken staan in reports/figures/")
