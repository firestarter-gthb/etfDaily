"""
Generate TradingView Pine Script v5 ETF Entry/Exit Strategy
===========================================================
Based on the 24 two-week OpEx periods from the SPY Seasonality Suite.

The generated strategy:
- Detects the current OpEx half-period (1H / 2H) in real time
- Computes a dynamic regime (dyn_regime) from the selected presidential cycle's actual stats
- Enters LONG at the start of bullish periods (regime >= threshold)
- Closes LONG at the start of non-bullish periods
- Optionally enters SHORT during bearish periods
- Sends full Dutch-language alerts on every signal transition
- Displays an entry/exit dashboard and background tinting

Output: tradingview/spy_opex_etf_strategy.pine
"""

import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ANN_FILE  = BASE_DIR / "reports" / "annual_cycle_package"    / "annual_cycle_24periods_stats.json"
PRES_FILE = BASE_DIR / "reports" / "presidential_cycle_package" / "presidential_cycle_24periods_stats.json"
PINE_DIR  = BASE_DIR / "tradingview"
PRES_PKG_DIR = BASE_DIR / "reports" / "presidential_cycle_package"
DATASENTE_DIR = Path(r"C:\Users\ROB5293\antigravity\datasente")

sys.path.insert(0, str(Path(__file__).parent))
from generate_google_calendar_opex import STRATEGY_PLAYBOOK
from utils import distribute

with open(ANN_FILE,  "r", encoding="utf-8") as f:
    ann_data = json.load(f)
with open(PRES_FILE, "r", encoding="utf-8") as f:
    pres_data = json.load(f)

MONTHS    = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
MONTHS_NL = {
    "Jan":"Januari","Feb":"Februari","Mar":"Maart","Apr":"April",
    "May":"Mei","Jun":"Juni","Jul":"Juli","Aug":"Augustus",
    "Sep":"September","Oct":"Oktober","Nov":"November","Dec":"December"
}

# ---------------------------------------------------------------------------
# Build period data arrays (shared with indicator generator)
# ---------------------------------------------------------------------------

def build_arrays():
    names, full_names = [], []
    ann_rets, ann_wrs  = [], []
    mid_rets, mid_wrs  = [], []
    pre_rets, pre_wrs  = [], []
    post_rets, post_wrs = [], []
    elec_rets, elec_wrs = [], []
    badges, emojis, primaries, confluences, strikes, exits = [], [], [], [], [], []

    for m in MONTHS:
        for h in ["1H", "2H"]:
            key     = f"{m}_{h}"
            h_label = "Post-OpEx" if h == "1H" else "Pre-OpEx"
            s_key   = "stats_1h"  if h == "1H" else "stats_2h"

            names.append(f"{m} {h}")
            full_names.append(f"{MONTHS_NL[m]} {h} ({h_label})")

            a = ann_data[s_key][m]
            ann_rets.append(f"{a['avg']:.2f}")
            ann_wrs.append(f"{a['wr']:.1f}")

            for cycle, r_list, w_list in [
                ("Midterm",      mid_rets,  mid_wrs),
                ("Pre-Election", pre_rets,  pre_wrs),
                ("Post-Election",post_rets, post_wrs),
                ("Election Year",elec_rets, elec_wrs),
            ]:
                p = pres_data["cycles"][cycle][s_key][m]
                r_list.append(f"{p['avg']:.2f}")
                w_list.append(f"{p['wr']:.1f}")

            strat = STRATEGY_PLAYBOOK[key]
            badges.append(strat["badge"])
            emojis.append(strat["emoji"])
            primaries.append(strat["primary"].replace('"', "'"))
            confluences.append(strat["context"].replace('"', "'"))
            strikes.append(strat["strike_rules"].replace('"', "'"))
            exits.append(strat["exit_rules"].replace('"', "'"))

    return (names, full_names,
            ann_rets, ann_wrs,
            mid_rets, mid_wrs,
            pre_rets, pre_wrs,
            post_rets, post_wrs,
            elec_rets, elec_wrs,
            badges, emojis, primaries, confluences, strikes, exits)

# ---------------------------------------------------------------------------
# Pine Script template
# ---------------------------------------------------------------------------

def build_pine(arrays):
    (names, full_names,
     ann_rets, ann_wrs,
     mid_rets, mid_wrs,
     pre_rets, pre_wrs,
     post_rets, post_wrs,
     elec_rets, elec_wrs,
     badges, emojis, primaries, confluences, strikes, exits) = arrays

    pine = """//@version=5
strategy("SPY OpEx 24-Period ETF Cycle Strategy [2-Wekelijks]",
         shorttitle="OpEx ETF Strategy",
         overlay=true,
         default_qty_type=strategy.percent_of_equity,
         default_qty_value=100,
         initial_capital=10000,
         commission_type=strategy.commission.percent,
         commission_value=0.05,
         slippage=2,
         calc_on_order_fills=false,
         process_orders_on_close=false,
         max_labels_count=500)

// =============================================================================
// INPUTS & CONFIGURATION
// =============================================================================
grp_strat   = "Strategie Instellingen"
long_regime = input.int(1, "Min. Regime voor Long Entry (1=Bull, 2=A+ Bull)",
              minval=1, maxval=2, group=grp_strat,
              tooltip="1 = Ga long bij bullish en A+ bullish perioden. 2 = Alleen de sterkste A+ perioden.")
allow_short  = input.bool(false, "Ook Short bij Bearish Perioden", group=grp_strat)
short_regime = input.int(-1, "Max. Regime voor Short Entry (-1=Bear, -2=Dubbel Risico)",
               minval=-2, maxval=-1, group=grp_strat)
use_stop     = input.bool(true, "Gebruik Vaste Stop Loss", group=grp_strat)
stop_pct     = input.float(4.0, "Stop Loss % (van Entry Prijs)", minval=0.5, maxval=20.0, step=0.5,
               group=grp_strat) / 100.0

grp_cycle = "Presidentiëlle Cyclus"
cycle_mode = input.string("Auto (Gebaseerd op Huidig Jaar)", "Cyclus Modus",
             options=["Auto (Gebaseerd op Huidig Jaar)",
                      "Midterm (Jaar 2 - bijv. 2026)",
                      "Pre-Election (Jaar 3 - bijv. 2027)",
                      "Election (Jaar 4 - bijv. 2028)",
                      "Post-Election (Jaar 1 - bijv. 2025)"],
             group=grp_cycle)

grp_display = "Visualisatie"
show_table   = input.bool(true,  "Toon Live Dashboard",       group=grp_display)
show_labels  = input.bool(true,  "Toon Periode Labels",       group=grp_display)
show_signals = input.bool(true,  "Toon Entry/Exit Pijlen",    group=grp_display)
show_bg      = input.bool(true,  "Achtergrondkleur per Signaal", group=grp_display)

// =============================================================================
// OPEX TIME COMPUTATION (Pine Script v5)
// =============================================================================
f_get_3rd_friday_day(y, m) =>
    ts_1st   = timestamp(y, m, 1, 0, 0, 0)
    dow_1st  = dayofweek(ts_1st)
    days_fri = (6 - dow_1st + 7) % 7
    1 + days_fri + 14

curr_y = year(time)
curr_m = month(time)

opex_day_curr_m    = f_get_3rd_friday_day(curr_y, curr_m)
ts_curr_m_opex_end = timestamp(curr_y, curr_m, opex_day_curr_m, 23, 59, 59)

target_y = time <= ts_curr_m_opex_end ? curr_y : (curr_m == 12 ? curr_y + 1 : curr_y)
target_m = time <= ts_curr_m_opex_end ? curr_m : (curr_m == 12 ? 1 : curr_m + 1)
prev_y   = time <= ts_curr_m_opex_end ? (curr_m == 1 ? curr_y - 1 : curr_y) : curr_y
prev_m   = time <= ts_curr_m_opex_end ? (curr_m == 1 ? 12 : curr_m - 1) : curr_m

prev_opex_day = f_get_3rd_friday_day(prev_y, prev_m)
curr_opex_day = f_get_3rd_friday_day(target_y, target_m)

ts_prev_opex_end = timestamp(prev_y, prev_m, prev_opex_day, 23, 59, 59)
ts_curr_opex_end = timestamp(target_y, target_m, curr_opex_day, 23, 59, 59)
ts_cycle_mid     = ts_prev_opex_end + int((ts_curr_opex_end - ts_prev_opex_end) / 2)

is_1h      = time <= ts_cycle_mid
period_idx = (target_m - 1) * 2 + (is_1h ? 0 : 1)

// Presidential cycle key (ternary, computed each bar)
cycle_key = cycle_mode == "Midterm (Jaar 2 - bijv. 2026)"    ? 2 :
            cycle_mode == "Pre-Election (Jaar 3 - bijv. 2027)" ? 3 :
            cycle_mode == "Election (Jaar 4 - bijv. 2028)"      ? 0 :
            cycle_mode == "Post-Election (Jaar 1 - bijv. 2025)" ? 1 :
            curr_y % 4   // Auto: deelbaar door 4 = Election, +1=Post, +2=Midterm, +3=Pre

cycle_label = cycle_key == 2 ? "Midterm (Jaar 2)" :
              cycle_key == 3 ? "Pre-Election (Jaar 3)" :
              cycle_key == 0 ? "Election (Jaar 4)" : "Post-Election (Jaar 1)"

// =============================================================================
// STATISTICAL DATA ARRAYS (SPY 1993-2026)
// =============================================================================
var string[] a_names       = array.new_string(24)
var string[] a_full_names  = array.new_string(24)
var float[]  a_ann_ret     = array.new_float(24)
var float[]  a_ann_wr      = array.new_float(24)
var float[]  a_mid_ret     = array.new_float(24)
var float[]  a_mid_wr      = array.new_float(24)
var float[]  a_pre_ret     = array.new_float(24)
var float[]  a_pre_wr      = array.new_float(24)
var float[]  a_post_ret    = array.new_float(24)
var float[]  a_post_wr     = array.new_float(24)
var float[]  a_elec_ret    = array.new_float(24)
var float[]  a_elec_wr     = array.new_float(24)
var string[] a_badges      = array.new_string(24)
var string[] a_emojis      = array.new_string(24)
var string[] a_primaries   = array.new_string(24)
var string[] a_strikes     = array.new_string(24)
var string[] a_exits       = array.new_string(24)

if barstate.isfirst
"""

    for i in range(24):
        pine += f'    array.set(a_names,      {i}, "{names[i]}")\n'
        pine += f'    array.set(a_full_names,  {i}, "{full_names[i]}")\n'
        pine += f'    array.set(a_ann_ret,     {i}, {ann_rets[i]})\n'
        pine += f'    array.set(a_ann_wr,      {i}, {ann_wrs[i]})\n'
        pine += f'    array.set(a_mid_ret,     {i}, {mid_rets[i]})\n'
        pine += f'    array.set(a_mid_wr,      {i}, {mid_wrs[i]})\n'
        pine += f'    array.set(a_pre_ret,     {i}, {pre_rets[i]})\n'
        pine += f'    array.set(a_pre_wr,      {i}, {pre_wrs[i]})\n'
        pine += f'    array.set(a_post_ret,    {i}, {post_rets[i]})\n'
        pine += f'    array.set(a_post_wr,     {i}, {post_wrs[i]})\n'
        pine += f'    array.set(a_elec_ret,    {i}, {elec_rets[i]})\n'
        pine += f'    array.set(a_elec_wr,     {i}, {elec_wrs[i]})\n'
        pine += f'    array.set(a_badges,      {i}, "{badges[i]}")\n'
        pine += f'    array.set(a_emojis,      {i}, "{emojis[i]}")\n'
        pine += f'    array.set(a_primaries,   {i}, "{primaries[i]}")\n'
        pine += f'    array.set(a_strikes,     {i}, "{strikes[i]}")\n'
        pine += f'    array.set(a_exits,       {i}, "{exits[i]}")\n'

    pine += """
// =============================================================================
// CURRENT PERIOD SELECTION
// =============================================================================
p_name      = array.get(a_names,     period_idx)
p_full_name = array.get(a_full_names, period_idx)
p_ann_ret   = array.get(a_ann_ret,   period_idx)
p_ann_wr    = array.get(a_ann_wr,    period_idx)
p_emoji     = array.get(a_emojis,    period_idx)
p_badge     = array.get(a_badges,    period_idx)
p_primary   = array.get(a_primaries, period_idx)
p_strike    = array.get(a_strikes,   period_idx)
p_exit_rule = array.get(a_exits,     period_idx)

// Select presidential cycle stats for active cycle
float p_pres_ret = na
float p_pres_wr  = na
if cycle_key == 2
    p_pres_ret := array.get(a_mid_ret,  period_idx)
    p_pres_wr  := array.get(a_mid_wr,   period_idx)
else if cycle_key == 3
    p_pres_ret := array.get(a_pre_ret,  period_idx)
    p_pres_wr  := array.get(a_pre_wr,   period_idx)
else if cycle_key == 0
    p_pres_ret := array.get(a_elec_ret, period_idx)
    p_pres_wr  := array.get(a_elec_wr,  period_idx)
else
    p_pres_ret := array.get(a_post_ret, period_idx)
    p_pres_wr  := array.get(a_post_wr,  period_idx)

// Dynamic regime (computed from ACTIVE cycle stats — not hardcoded)
dyn_regime = p_pres_wr >= 95.0 ? 2 :
             (p_pres_ret >= 1.5 and p_pres_wr >= 70.0) ? 2 :
             (p_pres_ret >= 0.3 and p_pres_wr >= 55.0) ? 1 :
             (p_pres_ret <= -1.0 and p_pres_wr <= 38.0) ? -2 :
             (p_pres_ret < -0.3 or p_pres_wr < 44.0) ? -1 : 0

// =============================================================================
// STRATEGY SIGNALS
// =============================================================================
is_new_period = ta.change(period_idx) != 0

long_entry  = is_new_period and dyn_regime >= long_regime
long_exit   = is_new_period and dyn_regime < long_regime and strategy.position_size > 0
short_entry = allow_short and is_new_period and dyn_regime <= short_regime and strategy.position_size >= 0
short_exit  = allow_short and is_new_period and dyn_regime > short_regime and strategy.position_size < 0

// Build rich Dutch alert messages
entry_msg = "KOOP SIGNAAL - OpEx ETF Strategie\\n" +
            "Periode: " + p_full_name + " | " + cycle_label + "\\n" +
            "Jaarlijks: " + str.tostring(p_ann_ret, "+0.00") + "% (" + str.tostring(p_ann_wr, "0") + "% WR) | " +
            cycle_label + ": " + str.tostring(p_pres_ret, "+0.00") + "% (" + str.tostring(p_pres_wr, "0") + "% WR)\\n" +
            "Regime: " + str.tostring(dyn_regime, "0") + " | Badge: " + p_badge + "\\n" +
            "Optie Strategie: " + p_primary + "\\n" +
            "Strike & Delta: " + p_strike + "\\n" +
            "Exit Regel: " + p_exit_rule

exit_msg = "SLUIT SIGNAAL - OpEx ETF Strategie\\n" +
           "Nieuwe periode: " + p_full_name + " | " + cycle_label + "\\n" +
           "Jaarlijks: " + str.tostring(p_ann_ret, "+0.00") + "% (" + str.tostring(p_ann_wr, "0") + "% WR) | " +
           cycle_label + ": " + str.tostring(p_pres_ret, "+0.00") + "% (" + str.tostring(p_pres_wr, "0") + "% WR)\\n" +
           "Regime: " + str.tostring(dyn_regime, "0") + " — Nieuwe periode is NIET bullish. Sluit positie."

short_msg = "SHORT SIGNAAL - OpEx ETF Strategie\\n" +
            "Bearish periode: " + p_full_name + " | " + cycle_label + "\\n" +
            "Jaarlijks: " + str.tostring(p_ann_ret, "+0.00") + "% (" + str.tostring(p_ann_wr, "0") + "% WR) | " +
            cycle_label + ": " + str.tostring(p_pres_ret, "+0.00") + "% (" + str.tostring(p_pres_wr, "0") + "% WR)\\n" +
            "Regime: " + str.tostring(dyn_regime, "0") + " — Bearish. Overweeg short positie."

// Execute strategy orders
if long_entry
    strategy.entry("Long", strategy.long, comment=p_name, alert_message=entry_msg)
    if use_stop
        strategy.exit("Long SL", from_entry="Long",
                      stop=strategy.position_avg_price * (1.0 - stop_pct),
                      comment="Stop " + str.tostring(stop_pct * 100, "0.0") + "%")

if long_exit
    strategy.close("Long", comment="Sluit: " + p_name, alert_message=exit_msg)

if short_entry
    strategy.entry("Short", strategy.short, comment=p_name + " SHORT", alert_message=short_msg)
    if use_stop
        strategy.exit("Short SL", from_entry="Short",
                      stop=strategy.position_avg_price * (1.0 + stop_pct),
                      comment="Short Stop")

if short_exit
    strategy.close("Short", comment="Sluit Short: " + p_name, alert_message=exit_msg)

// =============================================================================
// VISUAL: BACKGROUND TINTING
// =============================================================================
color bg_col = na
if show_bg
    if dyn_regime == 2
        bg_col := color.new(#00e676, 90)
    else if dyn_regime == 1
        bg_col := color.new(#69f0ae, 93)
    else if dyn_regime == -2
        bg_col := color.new(#ff1744, 88)
    else if dyn_regime == -1
        bg_col := color.new(#ff8a80, 93)
    else
        bg_col := color.new(#ffd600, 95)
bgcolor(bg_col, title="Periode Regime Achtergrond")

// =============================================================================
// VISUAL: ENTRY / EXIT ARROWS & PERIOD LABELS
// =============================================================================
if show_signals
    if long_entry
        label.new(bar_index, low,
                  text="KOOP\\n" + p_name + "\\n" + str.tostring(p_pres_ret, "+0.00") + "%",
                  yloc=yloc.belowbar, color=#00c853, textcolor=color.white,
                  style=label.style_label_up, size=size.small)
    if long_exit
        label.new(bar_index, high,
                  text="SLUIT\\n" + p_name,
                  yloc=yloc.abovebar, color=#d50000, textcolor=color.white,
                  style=label.style_label_down, size=size.small)
    if short_entry
        label.new(bar_index, high,
                  text="SHORT\\n" + p_name + "\\n" + str.tostring(p_pres_ret, "+0.00") + "%",
                  yloc=yloc.abovebar, color=#6200ea, textcolor=color.white,
                  style=label.style_label_down, size=size.small)

if show_labels and is_new_period and not long_entry and not long_exit and not short_entry
    label.new(bar_index, dyn_regime >= 0 ? low : high,
              text=p_emoji + " " + p_name,
              yloc=dyn_regime >= 0 ? yloc.belowbar : yloc.abovebar,
              color=dyn_regime > 0 ? #1b5e20 : (dyn_regime < 0 ? #b71c1c : #f57f17),
              textcolor=color.white,
              style=dyn_regime >= 0 ? label.style_label_up : label.style_label_down,
              size=size.tiny)

// =============================================================================
// DASHBOARD TABLE
// =============================================================================
var table dash = na
if show_table and barstate.islast
    dash := table.new(position.top_right, 2, 9,
                      bgcolor=#0d1117, border_color=#30363d, border_width=1)

    // Header
    table.cell(dash, 0, 0, "OpEx ETF STRATEGIE", bgcolor=#161b22, text_color=#58a6ff,
               text_halign=text.halign_left, text_size=size.small)
    table.cell(dash, 1, 0, cycle_label, bgcolor=#161b22, text_color=#e6edf3,
               text_halign=text.halign_right, text_size=size.small)

    // Periode
    table.cell(dash, 0, 1, "Actieve Periode:", text_color=#8b949e, text_halign=text.halign_left, text_size=size.small)
    table.cell(dash, 1, 1, p_emoji + " " + p_full_name, text_color=#ffffff,
               text_halign=text.halign_right, text_size=size.small)

    // Regime
    regime_str = dyn_regime == 2 ? "A++ MAX BULL" : dyn_regime == 1 ? "BULLISH" :
                 dyn_regime == -2 ? "DUBBEL RISICO" : dyn_regime == -1 ? "BEARISH" : "NEUTRAAL"
    regime_col = dyn_regime >= 1 ? #3fb950 : (dyn_regime <= -1 ? #f85149 : #e3b341)
    table.cell(dash, 0, 2, "Regime Signaal:", text_color=#8b949e, text_halign=text.halign_left, text_size=size.small)
    table.cell(dash, 1, 2, regime_str, text_color=regime_col, text_halign=text.halign_right, text_size=size.small)

    // Positie
    pos_str = strategy.position_size > 0 ? "LONG (" + str.tostring(strategy.position_avg_price, format.mintick) + ")" :
              strategy.position_size < 0 ? "SHORT" : "CASH / FLAT"
    pos_col = strategy.position_size > 0 ? #3fb950 : (strategy.position_size < 0 ? #f85149 : #8b949e)
    table.cell(dash, 0, 3, "Positie Status:", text_color=#8b949e, text_halign=text.halign_left, text_size=size.small)
    table.cell(dash, 1, 3, pos_str, text_color=pos_col, text_halign=text.halign_right, text_size=size.small)

    // Open P&L
    pnl_pct = strategy.position_size != 0 ? (close - strategy.position_avg_price) / strategy.position_avg_price * 100 : 0.0
    table.cell(dash, 0, 4, "Open P&L:", text_color=#8b949e, text_halign=text.halign_left, text_size=size.small)
    table.cell(dash, 1, 4, str.tostring(pnl_pct, "+0.00") + "%",
               text_color=pnl_pct >= 0 ? #3fb950 : #f85149, text_halign=text.halign_right, text_size=size.small)

    // Jaarlijkse Cyclus
    table.cell(dash, 0, 5, "Jaarlijkse Cyclus (34j):", text_color=#8b949e, text_halign=text.halign_left, text_size=size.small)
    table.cell(dash, 1, 5, str.tostring(p_ann_ret, "+0.00") + "% (WR " + str.tostring(p_ann_wr, "0.0") + "%)",
               text_color=p_ann_ret >= 0 ? #3fb950 : #f85149, text_halign=text.halign_right, text_size=size.small)

    // Presidentiële Cyclus
    table.cell(dash, 0, 6, cycle_label + ":", text_color=#8b949e, text_halign=text.halign_left, text_size=size.small)
    table.cell(dash, 1, 6, str.tostring(p_pres_ret, "+0.00") + "% (WR " + str.tostring(p_pres_wr, "0.0") + "%)",
               text_color=p_pres_ret >= 0 ? #3fb950 : #f85149, text_halign=text.halign_right, text_size=size.small)

    // Strategie
    table.cell(dash, 0, 7, "Aanbevolen Strategie:", text_color=#8b949e, text_halign=text.halign_left, text_size=size.small)
    table.cell(dash, 1, 7, p_primary, text_color=#e3b341, text_halign=text.halign_right, text_size=size.small)

    // Stop Loss info
    sl_str = use_stop and strategy.position_size != 0 ?
             str.tostring(strategy.position_avg_price * (1.0 - stop_pct), format.mintick) + " (-" + str.tostring(stop_pct * 100, "0.0") + "%)" :
             "Niet actief"
    table.cell(dash, 0, 8, "Stop Loss Niveau:", text_color=#8b949e, text_halign=text.halign_left, text_size=size.small)
    table.cell(dash, 1, 8, sl_str, text_color=#79c0ff, text_halign=text.halign_right, text_size=size.small)

// =============================================================================
// ALERT CONDITIONS (for TradingView alert setup UI)
// =============================================================================
alertcondition(long_entry,
    title="KOOP Signaal — OpEx Bullish Periode",
    message="KOOP | {{ticker}} | Nieuwe bullish OpEx periode | {{interval}} | Prijs: {{close}}")

alertcondition(long_exit,
    title="SLUIT LONG Signaal — OpEx Periode Niet Bullish",
    message="SLUIT LONG | {{ticker}} | Nieuwe niet-bullish periode | {{interval}} | Prijs: {{close}}")

alertcondition(short_entry,
    title="SHORT Signaal — OpEx Bearish Periode",
    message="SHORT | {{ticker}} | Nieuwe bearish OpEx periode | {{interval}} | Prijs: {{close}}")

alertcondition(long_entry or long_exit or short_entry or short_exit,
    title="Alle OpEx Strategie Signalen",
    message="OpEx Strategie Signaal | {{ticker}} | {{interval}} | Prijs: {{close}}")
"""

    return pine


def main():
    print("Generating TradingView Pine Script v5 ETF Strategy...")
    arrays = build_arrays()
    pine   = build_pine(arrays)

    out_file = PINE_DIR / "spy_opex_etf_strategy.pine"
    PINE_DIR.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(pine)

    distribute([out_file], [PRES_PKG_DIR, DATASENTE_DIR])
    print(f"Saved: {out_file} ({len(pine.splitlines())} regels)")
    print("Pine Script ETF strategy gegenereerd en gedistribueerd!")


if __name__ == "__main__":
    main()
