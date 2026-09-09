"""
Generate TradingView Pine Script v5 Indicator for 24 OpEx Periods Seasonality & Options Confluence
==================================================================================================
Embeds:
  - 24 Two-Week OpEx Periods (1H Post-OpEx & 2H Pre-OpEx)
  - Accurate 3rd Friday OpEx & Midpoint computation in Pine Script v5
  - Annual Cycle Stats (1993-2026)
  - 4-Year Presidential Cycle Stats (Post-Election, Midterm, Pre-Election, Election)
  - Confluence classification and Option Playbook (Primary Strategy, Delta/Strikes, Risk Rules)
  - Modern Dashboard Info-Table on chart
  - Color-coded Background Tinting
  - Period-Transition Chart Markers
  - Real-time Alerts with full Dutch strategy description, returns and win rates!
"""

import json
from pathlib import Path
from utils import distribute

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ANN_FILE = BASE_DIR / "reports" / "annual_cycle_package" / "annual_cycle_24periods_stats.json"
PRES_FILE = BASE_DIR / "reports" / "presidential_cycle_package" / "presidential_cycle_24periods_stats.json"
PINE_DIR = BASE_DIR / "tradingview"
PINE_DIR.mkdir(parents=True, exist_ok=True)
PRES_PKG_DIR = BASE_DIR / "reports" / "presidential_cycle_package"
DATASENTE_DIR = Path(r"C:\Users\ROB5293\antigravity\datasente")

with open(ANN_FILE, "r", encoding="utf-8") as f:
    ann_data = json.load(f)

with open(PRES_FILE, "r", encoding="utf-8") as f:
    pres_data = json.load(f)

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MONTHS_NL = {
    "Jan": "Januari", "Feb": "Februari", "Mar": "Maart", "Apr": "April",
    "May": "Mei", "Jun": "Juni", "Jul": "Juli", "Aug": "Augustus",
    "Sep": "September", "Oct": "Oktober", "Nov": "November", "Dec": "December"
}

# Import strategy playbook dictionary from generate_google_calendar_opex
import sys
sys.path.append(str(BASE_DIR / "scripts" / "seasonality"))
from generate_google_calendar_opex import STRATEGY_PLAYBOOK

def build_pinescript():
    period_names = []
    period_full_names = []
    ann_rets = []
    ann_wrs = []
    mid_rets = []
    mid_wrs = []
    pre_rets = []
    pre_wrs = []
    post_rets = []
    post_wrs = []
    elec_rets = []
    elec_wrs = []
    badges = []
    emojis = []
    primaries = []
    confluences = []
    strike_rules = []
    exit_rules = []
    regimes = []

    for m in MONTHS:
        for h in ["1H", "2H"]:
            key = f"{m}_{h}"
            p_name = f"{m} {h}"
            h_label = "Post-OpEx" if h == "1H" else "Pre-OpEx"
            p_full = f"{MONTHS_NL[m]} {h} ({h_label})"
            
            period_names.append(p_name)
            period_full_names.append(p_full)
            
            # Annual
            a_stat = ann_data["stats_1h"][m] if h == "1H" else ann_data["stats_2h"][m]
            ann_rets.append(f"{a_stat['avg']:.2f}")
            ann_wrs.append(f"{a_stat['wr']:.1f}")
            
            # Midterm (Key 2)
            m_stat = pres_data["cycles"]["Midterm"]["stats_1h"][m] if h == "1H" else pres_data["cycles"]["Midterm"]["stats_2h"][m]
            mid_rets.append(f"{m_stat['avg']:.2f}")
            mid_wrs.append(f"{m_stat['wr']:.1f}")
            
            # Pre-Election (Key 3)
            pr_stat = pres_data["cycles"]["Pre-Election"]["stats_1h"][m] if h == "1H" else pres_data["cycles"]["Pre-Election"]["stats_2h"][m]
            pre_rets.append(f"{pr_stat['avg']:.2f}")
            pre_wrs.append(f"{pr_stat['wr']:.1f}")
            
            # Post-Election (Key 1)
            po_stat = pres_data["cycles"]["Post-Election"]["stats_1h"][m] if h == "1H" else pres_data["cycles"]["Post-Election"]["stats_2h"][m]
            post_rets.append(f"{po_stat['avg']:.2f}")
            post_wrs.append(f"{po_stat['wr']:.1f}")
            
            # Election (Key 0)
            el_stat = pres_data["cycles"]["Election Year"]["stats_1h"][m] if h == "1H" else pres_data["cycles"]["Election Year"]["stats_2h"][m]
            elec_rets.append(f"{el_stat['avg']:.2f}")
            elec_wrs.append(f"{el_stat['wr']:.1f}")
            
            # Strategy: use `context` (qualitative-only field, fix #6 compatibility)
            strat = STRATEGY_PLAYBOOK[key]
            badges.append(strat["badge"])
            emojis.append(strat["emoji"])
            primaries.append(strat["primary"].replace('"', "'"))
            confluences.append(strat["context"].replace('"', "'"))  # context is editorial-only; no hardcoded numbers
            strike_rules.append(strat["strike_rules"].replace('"', "'"))
            exit_rules.append(strat["exit_rules"].replace('"', "'"))
            # NOTE: regime is no longer precomputed here. It is computed dynamically in Pine Script
            # from the ACTUAL selected cycle's p_pres_ret / p_pres_wr, fixing Bug #1.

    def to_pine_str_array(arr):
        return 'array.new_string(' + str(len(arr)) + ', "")\n'

    pine = f"""//@version=5
indicator("SPY Seasonality & Options Confluence [24 OpEx Periods]", "SPY OpEx Seasonality", overlay=true, max_labels_count=500, max_boxes_count=500)

// =============================================================================
// INPUTS & CONFIGURATION
// =============================================================================
grp_display = "Visualisatie Instellingen"
show_table  = input.bool(true, "Toon Dashboard Tabel", group=grp_display)
table_pos   = input.string("Boven Rechts", "Tabel Positie", options=["Boven Rechts", "Onder Rechts", "Boven Links", "Onder Links"], group=grp_display)
table_size  = input.string("Normaal", "Tabel Grootte", options=["Klein", "Normaal", "Groot"], group=grp_display)
show_bg     = input.bool(true, "Achtergrondkleur per Periode Signaal", group=grp_display)
show_labels = input.bool(true, "Toon Periode Labels op Grafiek", group=grp_display)

grp_cycle   = "Presidentiële Cyclus Selectie"
cycle_mode  = input.string("Auto (Gebaseerd op Huidig Jaar)", "Cyclus Modus", 
              options=["Auto (Gebaseerd op Huidig Jaar)", "Midterm (Jaar 2 - bijv. 2026)", "Pre-Election (Jaar 3 - bijv. 2027)", "Election (Jaar 4 - bijv. 2028)", "Post-Election (Jaar 1 - bijv. 2025)"], 
              group=grp_cycle)

grp_alerts  = "Alerts & Meldingen"
alert_on_change = input.bool(true, "Trigger Alert bij Overgang naar Nieuwe Periode", group=grp_alerts)

// =============================================================================
// OPEX & 24-PERIOD TIME COMPUTATION (PINE SCRIPT v5)
// =============================================================================
// Berekening van de 3e vrijdag (Monthly OpEx)
f_get_3rd_friday_day(y, m) =>
    // Day of week van de 1e van de maand (1=Sun, 2=Mon, ..., 6=Fri, 7=Sat)
    ts_1st = timestamp(y, m, 1, 0, 0, 0)
    dow_1st = dayofweek(ts_1st)
    days_to_fri = (6 - dow_1st + 7) % 7
    first_fri_day = 1 + days_to_fri
    first_fri_day + 14

curr_y = year(time)
curr_m = month(time)
curr_d = dayofmonth(time)

// Bepaal de 3e vrijdag van de huidige maand
opex_day_curr_m = f_get_3rd_friday_day(curr_y, curr_m)
ts_curr_m_opex_end = timestamp(curr_y, curr_m, opex_day_curr_m, 23, 59, 59)

// Als de huidige bar voorbij de OpEx van deze maand is, vallen we in de cyclus van volgende maand
target_y = time <= ts_curr_m_opex_end ? curr_y : (curr_m == 12 ? curr_y + 1 : curr_y)
target_m = time <= ts_curr_m_opex_end ? curr_m : (curr_m == 12 ? 1 : curr_m + 1)
prev_y   = time <= ts_curr_m_opex_end ? (curr_m == 1 ? curr_y - 1 : curr_y) : curr_y
prev_m   = time <= ts_curr_m_opex_end ? (curr_m == 1 ? 12 : curr_m - 1) : curr_m

// Bereken exacte OpEx timestamps van de actieve cyclus
prev_opex_day = f_get_3rd_friday_day(prev_y, prev_m)
curr_opex_day = f_get_3rd_friday_day(target_y, target_m)

ts_prev_opex_end = timestamp(prev_y, prev_m, prev_opex_day, 23, 59, 59)
ts_curr_opex_end = timestamp(target_y, target_m, curr_opex_day, 23, 59, 59)

// Middelpunt van de 4 of 5 wekelijkse cyclus
ts_cycle_mid = ts_prev_opex_end + int((ts_curr_opex_end - ts_prev_opex_end) / 2)

// Bepaal 1H (Post-OpEx) of 2H (Pre-OpEx)
is_1h = time <= ts_cycle_mid
half_str = is_1h ? "1H" : "2H"
half_name = is_1h ? "Post-OpEx" : "Pre-OpEx"

// Periode Index van 0 t/m 23
period_idx = (target_m - 1) * 2 + (is_1h ? 0 : 1)

// Bepaal Presidentiële Cyclus Key (1=Post-Election, 2=Midterm, 3=Pre-Election, 0=Election)
// Ternaire expressie: geen var-state nodig, wordt elke bar vers berekend.
cycle_key = cycle_mode == "Midterm (Jaar 2 - bijv. 2026)"    ? 2 :
            cycle_mode == "Pre-Election (Jaar 3 - bijv. 2027)" ? 3 :
            cycle_mode == "Election (Jaar 4 - bijv. 2028)"      ? 0 :
            cycle_mode == "Post-Election (Jaar 1 - bijv. 2025)" ? 1 :
            curr_y % 4  // Auto: jaren deelbaar door 4 = Election, +1 = Post, +2 = Midterm, +3 = Pre

cycle_label = cycle_key == 2 ? "Midterm (Jaar 2)" : cycle_key == 3 ? "Pre-Election (Jaar 3)" : cycle_key == 0 ? "Election (Jaar 4)" : "Post-Election (Jaar 1)"

// =============================================================================
// STATISTISCHE DATA ARRAYS (SPY 1993-2026 / 402 OPEX CYCLI)
// =============================================================================
var string[] a_names        = array.new_string(24)
var string[] a_full_names   = array.new_string(24)
var float[]  a_ann_ret      = array.new_float(24)
var float[]  a_ann_wr       = array.new_float(24)
var float[]  a_mid_ret      = array.new_float(24)
var float[]  a_mid_wr       = array.new_float(24)
var float[]  a_pre_ret      = array.new_float(24)
var float[]  a_pre_wr       = array.new_float(24)
var float[]  a_post_ret     = array.new_float(24)
var float[]  a_post_wr      = array.new_float(24)
var float[]  a_elec_ret     = array.new_float(24)
var float[]  a_elec_wr      = array.new_float(24)
var string[] a_badges       = array.new_string(24)
var string[] a_emojis       = array.new_string(24)
var string[] a_primaries    = array.new_string(24)
var string[] a_confluences  = array.new_string(24)
var string[] a_strikes      = array.new_string(24)
var string[] a_exits        = array.new_string(24)
// NOTE: a_regimes is intentionally omitted — regime is computed dynamically from p_pres_ret/p_pres_wr
//       so that switching cycle_mode on-the-fly reflects the correct signal (fix Bug #1).

if barstate.isfirst
"""

    # Populate array assignments in Pine Script
    for i in range(24):
        pine += f'    array.set(a_names, {i}, "{period_names[i]}")\n'
        pine += f'    array.set(a_full_names, {i}, "{period_full_names[i]}")\n'
        pine += f'    array.set(a_ann_ret, {i}, {ann_rets[i]})\n'
        pine += f'    array.set(a_ann_wr, {i}, {ann_wrs[i]})\n'
        pine += f'    array.set(a_mid_ret, {i}, {mid_rets[i]})\n'
        pine += f'    array.set(a_mid_wr, {i}, {mid_wrs[i]})\n'
        pine += f'    array.set(a_pre_ret, {i}, {pre_rets[i]})\n'
        pine += f'    array.set(a_pre_wr, {i}, {pre_wrs[i]})\n'
        pine += f'    array.set(a_post_ret, {i}, {post_rets[i]})\n'
        pine += f'    array.set(a_post_wr, {i}, {post_wrs[i]})\n'
        pine += f'    array.set(a_elec_ret, {i}, {elec_rets[i]})\n'
        pine += f'    array.set(a_elec_wr, {i}, {elec_wrs[i]})\n'
        pine += f'    array.set(a_badges, {i}, "{badges[i]}")\n'
        pine += f'    array.set(a_emojis, {i}, "{emojis[i]}")\n'
        pine += f'    array.set(a_primaries, {i}, "{primaries[i]}")\n'
        pine += f'    array.set(a_confluences, {i}, "{confluences[i]}")\n'
        pine += f'    array.set(a_strikes, {i}, "{strike_rules[i]}")\n'
        pine += f'    array.set(a_exits, {i}, "{exit_rules[i]}")\n'
        # a_regimes intentionally omitted: regime is computed live in Pine from actual cycle stats

    pine += """
// =============================================================================
// CURRENT PERIOD STATS SELECTION
// =============================================================================
p_name       = array.get(a_names, period_idx)
p_full_name  = array.get(a_full_names, period_idx)
p_ann_ret    = array.get(a_ann_ret, period_idx)
p_ann_wr     = array.get(a_ann_wr, period_idx)
p_badge      = array.get(a_badges, period_idx)
p_emoji      = array.get(a_emojis, period_idx)
p_primary    = array.get(a_primaries, period_idx)
p_confluence = array.get(a_confluences, period_idx)
p_strike     = array.get(a_strikes, period_idx)
p_exit       = array.get(a_exits, period_idx)
// NOTE: p_regime is NOT read from a static array anymore (see dyn_regime below)

// Select Presidential Return & Win Rate based on active cycle
float p_pres_ret = na
float p_pres_wr  = na
if cycle_key == 2
    p_pres_ret := array.get(a_mid_ret, period_idx)
    p_pres_wr  := array.get(a_mid_wr, period_idx)
else if cycle_key == 3
    p_pres_ret := array.get(a_pre_ret, period_idx)
    p_pres_wr  := array.get(a_pre_wr, period_idx)
else if cycle_key == 0
    p_pres_ret := array.get(a_elec_ret, period_idx)
    p_pres_wr  := array.get(a_elec_wr, period_idx)
else
    p_pres_ret := array.get(a_post_ret, period_idx)
    p_pres_wr  := array.get(a_post_wr, period_idx)

// =============================================================================
// DYNAMIC REGIME (fix Bug #1): computed from the ACTIVE cycle's actual stats.
// This ensures the signal, background, and alert reflect the cycle currently
// selected by the user (Midterm / Pre-Election / Election / Post-Election),
// not a hardcoded Midterm-only precomputed array.
// =============================================================================
dyn_regime = p_pres_wr >= 95.0 ? 2 :
             (p_pres_ret >= 1.5 and p_pres_wr >= 70.0) ? 2 :
             (p_pres_ret >= 0.3 and p_pres_wr >= 55.0) ? 1 :
             (p_pres_ret <= -1.0 and p_pres_wr <= 38.0) ? -2 :
             (p_pres_ret < -0.3 or p_pres_wr < 44.0) ? -1 : 0

// Confluence Signaal: afgeleid van dyn_regime (gebaseerd op actief geselecteerde cyclus)
// conf_score (dode variabele) is verwijderd
string conf_sentiment = ""
color conf_color = color.gray
if dyn_regime == 2
    conf_sentiment := "A++ MAX BULL"
    conf_color := color.green
else if dyn_regime == 1
    conf_sentiment := "BULLISH DRIFT"
    conf_color := #00e676
else if dyn_regime == -2
    conf_sentiment := "DUBBEL RISICO / BODEM"
    conf_color := #ff1744
else if dyn_regime == -1
    conf_sentiment := "BEARISH DRUK"
    conf_color := #ff5252
else
    conf_sentiment := "NEUTRAAL / CHOP"
    conf_color := #ffd600

// =============================================================================
// CHART VISUALIZATIONS: BACKGROUND TINT & PERIOD LABELS
// =============================================================================
// Background color tinting based on dyn_regime
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

bgcolor(bg_col, title="Periode Sentiment Achtergrond")

// Periode Overgang Detectie
is_new_period = ta.change(period_idx) != 0

// Plot Period Marker Label on Chart
if show_labels and is_new_period
    label_text = p_emoji + " " + p_name + "\\n" + str.tostring(p_pres_ret, "+0.00") + "% (" + str.tostring(p_pres_wr, "0") + "% WR)"
    label_col = dyn_regime > 0 ? #00c853 : (dyn_regime < 0 ? #d50000 : #ffab00)
    yloc_pos = dyn_regime >= 0 ? yloc.belowbar : yloc.abovebar
    label_style = dyn_regime >= 0 ? label.style_label_up : label.style_label_down
    label.new(bar_index, yloc_pos == yloc.belowbar ? low : high, text=label_text, yloc=yloc_pos, 
              color=label_col, textcolor=color.white, style=label_style, size=size.small)

// =============================================================================
// DASHBOARD INFO TABLE
// =============================================================================
var table info_table = na
t_pos = table_pos == "Boven Rechts" ? position.top_right : 
        table_pos == "Onder Rechts" ? position.bottom_right : 
        table_pos == "Boven Links" ? position.top_left : position.bottom_left

t_size = table_size == "Klein" ? size.small : (table_size == "Groot" ? size.large : size.normal)

if show_table and barstate.islast
    info_table := table.new(t_pos, 2, 8, bgcolor=#0d1117, border_color=#30363d, border_width=1)
    
    // Header
    table.cell(info_table, 0, 0, "SPY OPEX SEIZOENSMATIGHEID", bgcolor=#161b22, text_color=#58a6ff, text_size=t_size, text_halign=text.halign_left)
    table.cell(info_table, 1, 0, cycle_label, bgcolor=#161b22, text_color=#e6edf3, text_size=t_size, text_halign=text.halign_right)
    
    // Row 1: Periode & Signaal
    table.cell(info_table, 0, 1, "Actieve Periode:", text_color=#8b949e, text_size=t_size, text_halign=text.halign_left)
    table.cell(info_table, 1, 1, p_emoji + " " + p_full_name, text_color=#ffffff, text_size=t_size, text_halign=text.halign_right)
    
    // Row 2: Confluence Signaal
    table.cell(info_table, 0, 2, "Confluence Signaal:", text_color=#8b949e, text_size=t_size, text_halign=text.halign_left)
    table.cell(info_table, 1, 2, conf_sentiment, text_color=conf_color, text_size=t_size, text_halign=text.halign_right)
    
    // Row 3: Jaarlijkse Cyclus
    ann_str = str.tostring(p_ann_ret, "+0.00") + "% (WR " + str.tostring(p_ann_wr, "0.0") + "%)"
    table.cell(info_table, 0, 3, "Jaarlijkse Cyclus (34j):", text_color=#8b949e, text_size=t_size, text_halign=text.halign_left)
    table.cell(info_table, 1, 3, ann_str, text_color=p_ann_ret >= 0 ? #3fb950 : #f85149, text_size=t_size, text_halign=text.halign_right)
    
    // Row 4: Presidentiële Cyclus
    pres_str = str.tostring(p_pres_ret, "+0.00") + "% (WR " + str.tostring(p_pres_wr, "0.0") + "%)"
    table.cell(info_table, 0, 4, "Presidentieel (" + cycle_label + "):", text_color=#8b949e, text_size=t_size, text_halign=text.halign_left)
    table.cell(info_table, 1, 4, pres_str, text_color=p_pres_ret >= 0 ? #3fb950 : #f85149, text_size=t_size, text_halign=text.halign_right)
    
    // Row 5: Primaire Optiestrategie
    table.cell(info_table, 0, 5, "Beste Optiestrategie:", text_color=#8b949e, text_size=t_size, text_halign=text.halign_left)
    table.cell(info_table, 1, 5, p_primary, text_color=#e3b341, text_size=t_size, text_halign=text.halign_right)
    
    // Row 6: Strike Regels
    table.cell(info_table, 0, 6, "Strike Keuze & Delta:", text_color=#8b949e, text_size=t_size, text_halign=text.halign_left)
    table.cell(info_table, 1, 6, p_strike, text_color=#79c0ff, text_size=t_size, text_halign=text.halign_right)
    
    // Row 7: Exit Regels
    table.cell(info_table, 0, 7, "Exit & Risicobeheer:", text_color=#8b949e, text_size=t_size, text_halign=text.halign_left)
    table.cell(info_table, 1, 7, p_exit, text_color=#ffa657, text_size=t_size, text_halign=text.halign_right)

// =============================================================================
// ALERTS ENGINE
// =============================================================================
// Bouw gedetailleerde alert boodschap in het Nederlands
alert_msg = "🚨 SPY OpEx Seizoensperiode Update!\\n" + 
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\\n" + 
            "📅 PERIODE: " + p_emoji + " " + p_full_name + " | " + cycle_label + "\\n" + 
            "🚦 SIGNAAL: " + conf_sentiment + "\\n\\n" + 
            "📊 KWANTITATIEVE KANSEN:\\n" + 
            "• Jaarlijkse Cyclus (34 jaar): Gem. " + str.tostring(p_ann_ret, "+0.00") + "% | Kans: " + str.tostring(p_ann_wr, "0.0") + "% Win Rate\\n" + 
            "• Presidentiële Cyclus (" + cycle_label + "): Gem. " + str.tostring(p_pres_ret, "+0.00") + "% | Kans: " + str.tostring(p_pres_wr, "0.0") + "% Win Rate\\n" + 
            "• Confluence Oordeel: " + p_confluence + "\\n\\n" + 
            "🎯 AANBEVOLEN OPTIE STRATEGIE & PLAYBOOK:\\n" + 
            "• Primaire Strategie: " + p_primary + "\\n" + 
            "• Strike Keuze: " + p_strike + "\\n" + 
            "• Exit & Risicobeheer: " + p_exit + "\\n" + 
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

// Real-time alert trigger bij sluiten van bar bij periode-overgang
if alert_on_change and is_new_period
    alert(alert_msg, alert.freq_once_per_bar_close)

// TradingView Alert Condition voor UI configuratie
alertcondition(is_new_period, title="SPY Nieuwe OpEx Periode Alert", message="{{plot_0}}")
"""

    return pine

def main():
    print("Generating TradingView Pine Script Indicator...")
    pine_code = build_pinescript()

    # Primary output location
    pine_file_primary = PINE_DIR / "spy_seasonality_options_confluence.pine"
    with open(pine_file_primary, "w", encoding="utf-8") as f:
        f.write(pine_code)

    # Distribute to presidential_cycle_package and datasente (fix #7: single distribute() call)
    distribute(
        source_files=[pine_file_primary],
        extra_dirs=[PRES_PKG_DIR, DATASENTE_DIR]
    )

    print(f"Saved: {pine_file_primary} ({len(pine_code.splitlines())} lines)")
    print("Pine Script indicator generated and distributed successfully!")

if __name__ == "__main__":
    main()
