"""
OpEx 24-Period Cycle Strategy — Performance Backtest
=====================================================
Backtests the 2-weekly OpEx seasonality entry/exit strategy against Buy-and-Hold
on four instruments: SPY (S&P 500), QQQ (Nasdaq 100), SMH (Semiconductors),
URTH (MSCI World ETF).

Strategy logic:
  - Invest (long) on the first day of a period where the annual cycle regime >= 1
    (avg return > 0.3% AND win rate > 55%)
  - Go to cash at the start of neutral/bearish periods (regime <= 0)
  - Regime thresholds are derived from annual_cycle_24periods_stats.json

Metrics reported per instrument:
  Total Return, CAGR, Sharpe, Sortino, Max Drawdown, Calmar,
  % Time in Market, # Trades, Win Rate per Trade, Avg Trade Return

Output:
  - reports/figures/opex_strategy_performance.png  (premium dark dashboard)
  - reports/figures/opex_strategy_results.csv      (metrics table)
"""

import json
import datetime
import warnings
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
import yfinance as yf

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR     = Path(__file__).resolve().parent.parent.parent
ANN_FILE     = BASE_DIR / "reports" / "annual_cycle_package" / "annual_cycle_24periods_stats.json"
FIGURES_DIR  = BASE_DIR / "reports" / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(Path(__file__).parent))
from utils import distribute

PRES_PKG_DIR  = BASE_DIR / "reports" / "presidential_cycle_package"
DATASENTE_DIR = Path(r"C:\Users\ROB5293\antigravity\datasente")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

INSTRUMENTS = {
    "SPY":  {"name": "S&P 500",       "full": "SPDR S&P 500 ETF (SPY)",          "start": "2000-01-01", "color": "#58a6ff"},
    "QQQ":  {"name": "Nasdaq 100",    "full": "Invesco QQQ Trust (QQQ)",          "start": "2000-01-01", "color": "#3fb950"},
    "SMH":  {"name": "Semiconductors","full": "VanEck Semiconductor ETF (SMH)",   "start": "2002-01-01", "color": "#ffd700"},
    "URTH": {"name": "MSCI World",    "full": "iShares MSCI World ETF (URTH)",    "start": "2012-01-01", "color": "#f78166"},
}

with open(ANN_FILE, "r", encoding="utf-8") as f:
    ann_data = json.load(f)

# ---------------------------------------------------------------------------
# Regime classification
# ---------------------------------------------------------------------------

def classify_regime(avg: float, wr: float) -> int:
    """
    Map (avg_return, win_rate) to an integer regime code:
      2  = A+ Bull       (wr >= 95% OR avg >= 1.5% AND wr >= 70%)
      1  = Bullish       (avg >= 0.3% AND wr >= 55%)
      0  = Neutral
     -1  = Bearish       (avg < -0.3% OR wr < 44%)
     -2  = Double Risk   (avg <= -1.0% AND wr <= 38%)
    """
    if wr >= 95.0 or (avg >= 1.5 and wr >= 70.0):
        return 2
    elif avg >= 0.3 and wr >= 55.0:
        return 1
    elif avg <= -1.0 and wr <= 38.0:
        return -2
    elif avg < -0.3 or wr < 44.0:
        return -1
    else:
        return 0


def build_regime_lookup() -> dict:
    """Build lookup {(month_index_0based, '1H'|'2H'): regime_code}."""
    lookup = {}
    for mi, m in enumerate(MONTHS):
        for half, sk in [("1H", "stats_1h"), ("2H", "stats_2h")]:
            stat = ann_data[sk][m]
            lookup[(mi, half)] = classify_regime(stat["avg"], stat["wr"])
    return lookup


# ---------------------------------------------------------------------------
# OpEx date computation
# ---------------------------------------------------------------------------

def get_3rd_friday(year: int, month: int) -> datetime.date:
    """Return the 3rd Friday of the given month."""
    d = datetime.date(year, month, 1)
    while d.weekday() != 4:          # 4 = Friday
        d += datetime.timedelta(days=1)
    return d + datetime.timedelta(weeks=2)


def build_opex_dates(start_year: int, end_year: int) -> list:
    """Generate sorted list of all 3rd-Friday dates from start_year-1 to end_year+1."""
    dates = []
    for y in range(start_year - 1, end_year + 2):
        for m in range(1, 13):
            dates.append(get_3rd_friday(y, m))
    return sorted(dates)


# ---------------------------------------------------------------------------
# Signal series construction
# ---------------------------------------------------------------------------

def build_signal_series(price_index: pd.DatetimeIndex,
                        regime_lookup: dict,
                        min_regime: int = 1) -> pd.Series:
    """
    For each trading day in price_index, determine:
      1  = invested (regime >= min_regime)
      0  = cash
    Uses a fast period-mapping approach: generate all opex dates once,
    then assign regime to every trading day that falls in each half-period.
    """
    start_year = price_index[0].year
    end_year   = price_index[-1].year
    opex_dates = build_opex_dates(start_year, end_year)

    # Map trading days to their regime via a date range approach
    # Build a date→regime dict first
    date_regime: dict[datetime.date, int] = {}

    for i in range(len(opex_dates) - 1):
        prev_opex = opex_dates[i]
        curr_opex = opex_dates[i + 1]

        # The target month is the one ending at curr_opex
        target_mi = curr_opex.month - 1   # 0-based

        total_days = (curr_opex - prev_opex).days
        midpoint   = prev_opex + datetime.timedelta(days=total_days // 2)

        # 1H: (prev_opex+1) … midpoint
        r1h = regime_lookup.get((target_mi, "1H"), 0)
        d = prev_opex + datetime.timedelta(days=1)
        while d <= midpoint:
            date_regime[d] = r1h
            d += datetime.timedelta(days=1)

        # 2H: (midpoint+1) … curr_opex
        r2h = regime_lookup.get((target_mi, "2H"), 0)
        d = midpoint + datetime.timedelta(days=1)
        while d <= curr_opex:
            date_regime[d] = r2h
            d += datetime.timedelta(days=1)

    # Map to the actual trading days and apply min_regime filter
    regime_series = pd.Series(
        {ts: date_regime.get(ts.date(), 0) for ts in price_index},
        name="regime"
    )
    signal = (regime_series >= min_regime).astype(int)
    return signal, regime_series


# ---------------------------------------------------------------------------
# Backtest engine
# ---------------------------------------------------------------------------

def run_backtest(prices: pd.Series,
                 signal: pd.Series,
                 min_regime: int = 1) -> tuple[pd.Series, pd.Series]:
    """
    Apply the OpEx cycle strategy.
    Signal is shifted by 1 day (enter/exit at next-day open/close).
    Returns (strategy_returns, buyhold_returns) as daily return series.
    """
    daily_ret = prices.pct_change()

    # Shift signal: decision on day D → execute on day D+1
    shifted = signal.shift(1).fillna(0)

    strat_ret = (daily_ret * shifted).rename("strategy")
    bnh_ret   = daily_ret.rename("buy_hold")

    return strat_ret, bnh_ret


def compute_metrics(returns: pd.Series, label: str, signal: pd.Series = None) -> dict:
    """Compute comprehensive performance metrics for a daily-return series."""
    r = returns.dropna()
    if len(r) == 0:
        return {}

    cum    = (1 + r).cumprod()
    total  = float(cum.iloc[-1] - 1)
    n_yrs  = len(r) / 252.0
    cagr   = float((1 + total) ** (1 / n_yrs) - 1) if n_yrs > 0 else 0.0

    mu, sigma = float(r.mean()), float(r.std())
    sharpe = (mu / sigma * np.sqrt(252)) if sigma > 0 else 0.0

    neg = r[r < 0]
    sortino = (mu / neg.std() * np.sqrt(252)) if len(neg) > 0 and neg.std() > 0 else 0.0

    roll_max = cum.cummax()
    dd       = (cum - roll_max) / roll_max
    max_dd   = float(dd.min())
    calmar   = cagr / abs(max_dd) if max_dd != 0 else 0.0

    # Trade-level analysis
    n_trades = win_rate = avg_trade = 0
    if signal is not None:
        sig_aligned = signal.reindex(r.index).fillna(0)
        in_market   = (sig_aligned.shift(1) > 0).astype(int)
        entries     = in_market.diff().clip(0)    # 1 = new entry

        # Compute per-trade returns by grouping consecutive in-market days
        trade_rets = []
        entry_date = None
        accum = 0.0

        for date, ret_val in r.items():
            if in_market.get(date, 0) == 1:
                if entry_date is None:
                    entry_date = date
                accum = (1 + accum) * (1 + ret_val) - 1
            else:
                if entry_date is not None:
                    trade_rets.append(accum)
                    entry_date = None
                    accum = 0.0

        if trade_rets:
            n_trades  = len(trade_rets)
            win_rate  = float(np.mean([t > 0 for t in trade_rets]))
            avg_trade = float(np.mean(trade_rets))

        time_in_market = float(in_market.mean())
    else:
        time_in_market = 1.0

    return {
        "label":          label,
        "total_return":   total,
        "cagr":           cagr,
        "sharpe":         sharpe,
        "sortino":        sortino,
        "max_drawdown":   max_dd,
        "calmar":         calmar,
        "n_years":        n_yrs,
        "n_trades":       n_trades,
        "win_rate":       win_rate,
        "avg_trade":      avg_trade,
        "time_in_market": time_in_market,
        "equity_curve":   cum,
    }


# ---------------------------------------------------------------------------
# Visualisation
# ---------------------------------------------------------------------------

DARK_BG    = "#0d1117"
DARK_PANEL = "#161b22"
DARK_GRID  = "#21262d"
BLUE       = "#58a6ff"
GREEN      = "#3fb950"
RED        = "#f85149"
GOLD       = "#ffd700"
MUTED      = "#8b949e"
WHITE      = "#e6edf3"


def format_pct(v: float) -> str:
    return f"{v:+.1f}%"


def format_x(v: float) -> str:
    return f"{v:.2f}×"


def draw_regime_calendar(ax, regime_lookup):
    """Draw the 24-period regime heatmap (months × halves)."""
    half_labels = ["1H", "2H"]
    month_abbrs = MONTHS
    grid = np.zeros((2, 12))
    for mi in range(12):
        for hi, h in enumerate(["1H", "2H"]):
            grid[hi, mi] = regime_lookup.get((mi, h), 0)

    cmap = LinearSegmentedColormap.from_list("regime",
        ["#b71c1c", "#f85149", "#ffd600", "#3fb950", "#00c853"], N=5)

    im = ax.imshow(grid, cmap=cmap, vmin=-2, vmax=2, aspect="auto")
    ax.set_xticks(range(12))
    ax.set_xticklabels(month_abbrs, color=WHITE, fontsize=7)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["2H\n(Pre-OpEx)", "1H\n(Post-OpEx)"], color=WHITE, fontsize=7)
    ax.set_title("Regime Kalender — 24 OpEx Perioden  (Groen=Long, Rood=Cash, Geel=Neutraal)",
                 color=BLUE, fontsize=8, pad=4)
    ax.tick_params(colors=MUTED, length=0)
    for spine in ax.spines.values():
        spine.set_edgecolor(DARK_GRID)

    # Add regime value text
    regime_names = {2: "A+", 1: "B", 0: "N", -1: "B-", -2: "D"}
    for hi in range(2):
        for mi in range(12):
            v = int(grid[hi, mi])
            ax.text(mi, hi, regime_names.get(v, "?"),
                    ha="center", va="center", fontsize=6,
                    color="white" if abs(v) >= 1 else "#333333", fontweight="bold")
    return im


def generate_visualization(all_metrics: dict, equity_curves: dict,
                           regime_lookup: dict):
    n_inst = len(INSTRUMENTS)
    fig = plt.figure(figsize=(20, 26), facecolor=DARK_BG)

    gs_main = gridspec.GridSpec(
        4, 1,
        hspace=0.45,
        top=0.95, bottom=0.04,
        left=0.06, right=0.97,
        height_ratios=[0.7, 2.5, 2.5, 1.6]
    )

    # ── Title block ──────────────────────────────────────────────────────────
    ax_title = fig.add_subplot(gs_main[0])
    ax_title.set_facecolor(DARK_BG)
    ax_title.axis("off")
    ax_title.text(0.5, 0.80, "OpEx 24-Period Cycle Strategy",
                  ha="center", va="center", fontsize=26, fontweight="bold",
                  color=WHITE, transform=ax_title.transAxes)
    ax_title.text(0.5, 0.45, "Performance Analyse vs Buy-and-Hold  ·  SPY, QQQ, SMH, MSCI World (URTH)",
                  ha="center", va="center", fontsize=13, color=MUTED,
                  transform=ax_title.transAxes)
    ax_title.text(0.5, 0.10,
                  "Strategie: Long in bullish OpEx-perioden (Regime ≥ 1)  ·  Cash in neutrale/bearish perioden  ·  Gebaseerd op SPY 1993–2026 statistieken",
                  ha="center", va="center", fontsize=9, color=GOLD,
                  transform=ax_title.transAxes)

    # ── Equity curves (2×2 grid) ─────────────────────────────────────────────
    gs_eq = gridspec.GridSpecFromSubplotSpec(
        2, 2, subplot_spec=gs_main[1], hspace=0.45, wspace=0.25
    )

    ticker_list = list(INSTRUMENTS.keys())
    for idx, ticker in enumerate(ticker_list):
        row, col = divmod(idx, 2)
        ax = fig.add_subplot(gs_eq[row, col])
        ax.set_facecolor(DARK_PANEL)

        info   = INSTRUMENTS[ticker]
        ec_s   = equity_curves.get(f"{ticker}_strategy")
        ec_b   = equity_curves.get(f"{ticker}_bnh")
        m_s    = all_metrics.get(f"{ticker}_strategy", {})
        m_b    = all_metrics.get(f"{ticker}_bnh", {})

        if ec_s is None or ec_b is None:
            ax.text(0.5, 0.5, "Data niet beschikbaar", ha="center", va="center",
                    color=MUTED, transform=ax.transAxes)
            continue

        c_inst = info["color"]
        ax.plot(ec_b.index, ec_b.values, color=MUTED, linewidth=1.2,
                alpha=0.6, label="Buy & Hold")
        ax.plot(ec_s.index, ec_s.values, color=c_inst, linewidth=2.0,
                label="OpEx Strategie")
        ax.fill_between(ec_s.index, ec_s.values, ec_b.values,
                        where=ec_s.values >= ec_b.values,
                        alpha=0.15, color=c_inst)
        ax.fill_between(ec_s.index, ec_s.values, ec_b.values,
                        where=ec_s.values < ec_b.values,
                        alpha=0.10, color=RED)

        # Drawdown shading
        roll_max = ec_s.cummax()
        dd = (ec_s - roll_max) / roll_max
        ax_dd = ax.twinx()
        ax_dd.fill_between(dd.index, dd.values, 0,
                           alpha=0.20, color=RED, linewidth=0)
        ax_dd.set_ylim(-1, 0.5)
        ax_dd.set_yticks([])
        ax_dd.spines["right"].set_visible(False)

        # Labels
        stot = m_s.get("total_return", 0)
        btot = m_b.get("total_return", 0)
        outperf = stot - btot

        ax.set_title(f"{info['full']}", color=WHITE, fontsize=9, pad=4)
        ax.set_xlabel("")
        ax.tick_params(colors=MUTED, labelsize=7)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.1f}×"))
        for sp in ax.spines.values():
            sp.set_edgecolor(DARK_GRID)
        ax.set_facecolor(DARK_PANEL)
        ax.grid(True, color=DARK_GRID, linewidth=0.5, alpha=0.7)

        # KPI badge inside chart
        badge_txt = (f"Strategie: {format_pct(stot * 100)}\n"
                     f"Buy&Hold:  {format_pct(btot * 100)}\n"
                     f"Outperf.:  {format_pct(outperf * 100)}")
        ax.text(0.02, 0.97, badge_txt, transform=ax.transAxes,
                fontsize=7.5, va="top", color=WHITE,
                bbox=dict(facecolor=DARK_BG, alpha=0.85, edgecolor=DARK_GRID, boxstyle="round,pad=0.4"))

        legend = ax.legend(loc="lower right", fontsize=7,
                           facecolor=DARK_BG, edgecolor=DARK_GRID,
                           labelcolor=WHITE, framealpha=0.9)

    # ── Metrics comparison table ──────────────────────────────────────────────
    gs_tbl = gridspec.GridSpecFromSubplotSpec(
        1, 1, subplot_spec=gs_main[2]
    )
    ax_tbl = fig.add_subplot(gs_tbl[0])
    ax_tbl.set_facecolor(DARK_BG)
    ax_tbl.axis("off")
    ax_tbl.set_title("Prestatiemetrieken — Strategie vs Buy-and-Hold",
                     color=BLUE, fontsize=12, pad=8, loc="left")

    col_labels = [
        "Instrument", "Type",
        "Totaal Return", "CAGR",
        "Sharpe", "Sortino",
        "Max Drawdown", "Calmar",
        "% In Markt", "# Trades", "Win Rate"
    ]

    rows = []
    row_colors = []
    for ticker in ticker_list:
        for suffix, label in [("_strategy", "Strategie"), ("_bnh", "Buy & Hold")]:
            key = f"{ticker}{suffix}"
            m   = all_metrics.get(key, {})
            if not m:
                continue
            is_strat = suffix == "_strategy"
            rows.append([
                INSTRUMENTS[ticker]["name"] if is_strat else "",
                label,
                f"{m.get('total_return', 0) * 100:+.1f}%",
                f"{m.get('cagr', 0) * 100:+.1f}%",
                f"{m.get('sharpe', 0):.2f}",
                f"{m.get('sortino', 0):.2f}",
                f"{m.get('max_drawdown', 0) * 100:.1f}%",
                f"{m.get('calmar', 0):.2f}",
                f"{m.get('time_in_market', 1.0) * 100:.0f}%",
                str(m.get("n_trades", "—")),
                f"{m.get('win_rate', 0) * 100:.0f}%" if is_strat else "—",
            ])
            bg_row = DARK_PANEL if is_strat else "#0f1923"
            row_colors.append([bg_row] * len(col_labels))

    if rows:
        tbl = ax_tbl.table(
            cellText=rows,
            colLabels=col_labels,
            cellLoc="center",
            loc="center",
            bbox=[0, 0, 1, 1],
        )
        tbl.auto_set_font_size(False)
        tbl.set_fontsize(8.5)

        # Header styling
        for j, _ in enumerate(col_labels):
            tbl[(0, j)].set_facecolor(BLUE)
            tbl[(0, j)].set_text_props(color="#0d1117", fontweight="bold")

        # Data row styling
        for i, row_data in enumerate(rows):
            is_strat = row_data[1] == "Strategie"
            for j in range(len(col_labels)):
                cell = tbl[(i + 1, j)]
                cell.set_facecolor(row_colors[i][j])
                cell.set_edgecolor(DARK_GRID)

                # Color code numeric cells
                txt = row_data[j]
                if j >= 2 and txt not in ("—",):
                    try:
                        val = float(txt.replace("%", "").replace("+", ""))
                        if j in (2, 3, 6):       # returns and drawdown columns
                            fc = GREEN if val > 0 else (RED if val < 0 else WHITE)
                        elif j in (4, 5, 7):      # ratios
                            fc = GREEN if val > 1 else (RED if val < 0 else WHITE)
                        else:
                            fc = WHITE
                        cell.set_text_props(color=fc)
                    except ValueError:
                        cell.set_text_props(color=WHITE)
                else:
                    col_clr = GOLD if is_strat else MUTED
                    cell.set_text_props(color=col_clr)

    # ── Regime calendar heatmap ───────────────────────────────────────────────
    gs_cal = gridspec.GridSpecFromSubplotSpec(
        1, 1, subplot_spec=gs_main[3]
    )
    ax_cal = fig.add_subplot(gs_cal[0])
    ax_cal.set_facecolor(DARK_BG)
    draw_regime_calendar(ax_cal, regime_lookup)

    # Legend for heatmap
    legend_items = [
        mpatches.Patch(color="#00c853", label="Regime +2  A+ Bull (Long)"),
        mpatches.Patch(color="#3fb950", label="Regime +1  Bullish (Long)"),
        mpatches.Patch(color="#ffd600", label="Regime  0  Neutraal (Cash)"),
        mpatches.Patch(color="#f85149", label="Regime -1  Bearish (Cash)"),
        mpatches.Patch(color="#b71c1c", label="Regime -2  Dubbel Risico (Cash)"),
    ]
    ax_cal.legend(handles=legend_items, loc="upper right", fontsize=7,
                  facecolor=DARK_BG, edgecolor=DARK_GRID, labelcolor=WHITE,
                  ncol=5, framealpha=0.9)

    # ── Footer ───────────────────────────────────────────────────────────────
    fig.text(0.5, 0.015,
             "ETF Daily Seasonality Engine  ·  Bron: SPY 1993–2026 / 402 OpEx-cycli  ·  Resultaten zijn historisch; geen beleggingsadvies",
             ha="center", fontsize=8, color=MUTED)

    out = FIGURES_DIR / "opex_strategy_performance.png"
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor=DARK_BG)
    plt.close(fig)
    print(f"Visualisatie opgeslagen: {out}")
    return out


# ---------------------------------------------------------------------------
# CSV results export
# ---------------------------------------------------------------------------

def save_csv(all_metrics: dict):
    rows = []
    for ticker in INSTRUMENTS:
        for suffix, label in [("_strategy", "Strategie"), ("_bnh", "Buy & Hold")]:
            m = all_metrics.get(f"{ticker}{suffix}", {})
            if not m:
                continue
            rows.append({
                "Instrument":      INSTRUMENTS[ticker]["name"],
                "Ticker":          ticker,
                "Type":            label,
                "Start":           INSTRUMENTS[ticker]["start"],
                "Jaren":           f"{m.get('n_years', 0):.1f}",
                "Totaal Return":   f"{m.get('total_return', 0) * 100:+.1f}%",
                "CAGR":            f"{m.get('cagr', 0) * 100:+.1f}%",
                "Sharpe":          f"{m.get('sharpe', 0):.2f}",
                "Sortino":         f"{m.get('sortino', 0):.2f}",
                "Max Drawdown":    f"{m.get('max_drawdown', 0) * 100:.1f}%",
                "Calmar":          f"{m.get('calmar', 0):.2f}",
                "% In Markt":      f"{m.get('time_in_market', 1.0) * 100:.0f}%",
                "Aantal Trades":   str(m.get("n_trades", "—")),
                "Win Rate Trades": f"{m.get('win_rate', 0) * 100:.0f}%" if label == "Strategie" else "—",
                "Gem. Trade Ret.": f"{m.get('avg_trade', 0) * 100:+.2f}%" if label == "Strategie" else "—",
            })
    df = pd.DataFrame(rows)
    out = FIGURES_DIR / "opex_strategy_results.csv"
    df.to_csv(out, index=False, encoding="utf-8-sig")
    print(f"CSV opgeslagen: {out}")
    return out


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def print_summary(all_metrics: dict):
    print("\n" + "=" * 90)
    print(f"{'INSTRUMENT':<22} {'TYPE':<14} {'CAGR':>7} {'SHARPE':>7} {'MAX DD':>8} {'IN MARKT':>9} {'TRADES':>7} {'WR':>6}")
    print("-" * 90)
    for ticker in INSTRUMENTS:
        for suffix, label in [("_strategy", "Strategie"), ("_bnh", "Buy&Hold")]:
            m = all_metrics.get(f"{ticker}{suffix}", {})
            if not m:
                continue
            print(
                f"  {INSTRUMENTS[ticker]['name']:<20} {label:<14}"
                f" {m.get('cagr', 0) * 100:>+6.1f}%"
                f" {m.get('sharpe', 0):>7.2f}"
                f" {m.get('max_drawdown', 0) * 100:>7.1f}%"
                f" {m.get('time_in_market', 1.0) * 100:>8.0f}%"
                f" {m.get('n_trades', 0):>7}"
                f" {m.get('win_rate', 0) * 100:>5.0f}%"
            )
        print()
    print("=" * 90)


def main():
    print("OpEx 24-Period Cycle Strategy — Performance Backtest")
    print("=" * 60)

    regime_lookup = build_regime_lookup()

    # Show regime classification for reference
    bull_periods = [(MONTHS[mi] + " " + h) for (mi, h), r in regime_lookup.items() if r >= 1]
    bear_periods = [(MONTHS[mi] + " " + h) for (mi, h), r in regime_lookup.items() if r <= -1]
    print(f"\nBullish perioden ({len(bull_periods)}/24): {', '.join(bull_periods)}")
    print(f"Bearish perioden ({len(bear_periods)}/24): {', '.join(bear_periods)}")
    print(f"Neutrale perioden: {24 - len(bull_periods) - len(bear_periods)}/24\n")

    all_metrics   = {}
    equity_curves = {}

    for ticker, info in INSTRUMENTS.items():
        print(f"[{ticker}] Downloaden & backtesten {info['full']} (vanaf {info['start']})...")

        try:
            raw = yf.download(ticker, start=info["start"], auto_adjust=True,
                              progress=False, threads=False)
            prices = raw["Close"].squeeze().dropna()
        except Exception as e:
            print(f"  ! Download mislukt: {e}")
            continue

        if len(prices) < 252:
            print(f"  ! Te weinig data ({len(prices)} bars), overgeslagen.")
            continue

        signal, regime_series = build_signal_series(prices.index, regime_lookup)
        strat_ret, bnh_ret    = run_backtest(prices, signal)

        # Align
        common = strat_ret.dropna().index.intersection(bnh_ret.dropna().index)
        strat_r = strat_ret.loc[common]
        bnh_r   = bnh_ret.loc[common]
        sig_c   = signal.reindex(common).fillna(0)

        m_s = compute_metrics(strat_r, f"{ticker} Strategie", signal=sig_c)
        m_b = compute_metrics(bnh_r,   f"{ticker} Buy & Hold")

        all_metrics[f"{ticker}_strategy"] = m_s
        all_metrics[f"{ticker}_bnh"]      = m_b

        equity_curves[f"{ticker}_strategy"] = m_s["equity_curve"]
        equity_curves[f"{ticker}_bnh"]      = m_b["equity_curve"]

        print(f"  Strategie  CAGR: {m_s.get('cagr', 0) * 100:+.1f}%  |  "
              f"Sharpe: {m_s.get('sharpe', 0):.2f}  |  "
              f"Max DD: {m_s.get('max_drawdown', 0) * 100:.1f}%  |  "
              f"In markt: {m_s.get('time_in_market', 1) * 100:.0f}%  |  "
              f"Trades: {m_s.get('n_trades', 0)}  |  WR: {m_s.get('win_rate', 0) * 100:.0f}%")
        print(f"  Buy&Hold   CAGR: {m_b.get('cagr', 0) * 100:+.1f}%  |  "
              f"Sharpe: {m_b.get('sharpe', 0):.2f}  |  "
              f"Max DD: {m_b.get('max_drawdown', 0) * 100:.1f}%")

    print_summary(all_metrics)

    # Generate visualization
    vis_file = generate_visualization(all_metrics, equity_curves, regime_lookup)
    csv_file = save_csv(all_metrics)

    # Distribute
    distribute([vis_file, csv_file], [PRES_PKG_DIR, DATASENTE_DIR])
    print("\nKlaar! Alle bestanden gedistribueerd.")


if __name__ == "__main__":
    main()
