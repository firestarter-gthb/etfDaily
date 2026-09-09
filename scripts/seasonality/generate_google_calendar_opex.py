"""
Generate Google Calendar (iCal .ics & Google CSV) for 24-Period OpEx Seasonality & Option Strategies
====================================================================================================
Integrates:
  1. 24 Two-Week OpEx Periods (1H Post-OpEx & 2H Pre-OpEx)
  2. Annual Cycle SPY Empirical Stats (1993-2026)
  3. 4-Year Presidential Cycle Stats (Midterm Year 2026 & Pre-Election Year 2027)
  4. Confluence Signal Classification (A+ Bull, Bull, Neutraal/Divergentie, Bear, Dubbel Risico)
  5. Actionable Option Playbook per period (Primary Strategy, Alternative, Delta/Strikes, Risk Rules)

Outputs:
  - spy_seasonality_options_2026.ics (iCal format for Google Calendar / Apple Calendar / Outlook)
  - spy_seasonality_options_2026_google_calendar.csv (CSV format for Google Calendar)
  - spy_seasonality_options_2026_2027.ics (2-Year calendar for 2026 Midterm + 2027 Pre-Election)
  - spy_seasonality_options_2026_2027_google_calendar.csv
"""

import json
import datetime
from pathlib import Path
from utils import distribute

BASE_DIR = Path(__file__).resolve().parent.parent.parent
PRES_PKG_DIR = BASE_DIR / "reports" / "presidential_cycle_package"
ANN_PKG_DIR = BASE_DIR / "reports" / "annual_cycle_package"
DATASENTE_DIR = Path(r"C:\Users\ROB5293\antigravity\datasente")

# Load existing computed statistical JSON files
with open(ANN_PKG_DIR / "annual_cycle_24periods_stats.json", "r", encoding="utf-8") as f:
    annual_data = json.load(f)

with open(PRES_PKG_DIR / "presidential_cycle_24periods_stats.json", "r", encoding="utf-8") as f:
    pres_data = json.load(f)

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MONTHS_NL = {
    "Jan": "Januari", "Feb": "Februari", "Mar": "Maart", "Apr": "April",
    "May": "Mei", "Jun": "Juni", "Jul": "Juli", "Aug": "Augustus",
    "Sep": "September", "Oct": "Oktober", "Nov": "November", "Dec": "December"
}

CYCLE_NAMES = {
    0: "Election Year (Jaar 4)",
    1: "Post-Election Year (Jaar 1)",
    2: "Midterm Year (Jaar 2)",
    3: "Pre-Election Year (Jaar 3)"
}

# =============================================================================
# 24-Period Option Strategy Playbook
# NOTE: `context` is intentionally qualitative only — no hardcoded numbers.
# All percentages / win-rates are injected at runtime by build_confluence_text().
# =============================================================================
STRATEGY_PLAYBOOK = {
    "Jan_1H": {
        "badge": "A+ BULL CONFLUENCE",
        "emoji": "🟢🟢",
        "context": "Twee ongekend sterke cycli bevestigen elkaar. Maximale institutionele instroom in het nieuwe beursjaar.",
        "primary": "Bull Call Debit Spread (+0.60 Delta Long Call / -0.30 Delta Short Call) of Bull Put Credit Spread (20 Delta).",
        "alternative": "Long SPY Calls / Call LEAPS toevoegen voor het nieuwe beursjaar.",
        "iv_regime": "Matig tot dalend (post-holiday implied volatility crush).",
        "strike_rules": "Long Call net ITM/ATM, Short Call op 3-4% OTM weerstand. Target 30-45 DTE of OpEx.",
        "exit_rules": "Winst nemen bij 50-60% max profit. Stop loss bij sluiting onder de 21-daagse EMA.",
        "next_preview": "Jan 2H: Consolidatie en winstnemingen in aanloop naar tech earnings."
    },
    "Jan_2H": {
        "badge": "NEUTRAAL / PRE-EARNINGS",
        "emoji": "🟡",
        "context": "Adempauze vóór het Big Tech-kwartaalcijferseizoen. De eerste earnings-resultaten bepalen de richting.",
        "primary": "Iron Condor (16-Delta Puts / 16-Delta Calls) of Call Diagonal Spread.",
        "alternative": "Cash-Secured Put op favoriete dips.",
        "iv_regime": "Stijgend in aanloop naar Big Tech earnings.",
        "strike_rules": "Wings 5 tot 10 punten breed. Verkoop premie buiten de verwachte weekly move.",
        "exit_rules": "Sluiten vóór Big Tech earnings en vóór OpEx Friday.",
        "next_preview": "Feb 1H: Vroege februari rebound (+0.85%, 67% WR Jaarlijks)."
    },
    "Feb_1H": {
        "badge": "GEMATIGD BULLISH / DIVERGENTIE",
        "emoji": "🟢🟡",
        "context": "Jaarlijks solide herstel, maar Midterm-jaren tonen hier vroege terughoudendheid. Divergentie bewaken.",
        "primary": "Bull Put Credit Spread (15-20 Delta) of OTM Call Spread.",
        "alternative": "Covered Call op bestaande long aandelen.",
        "iv_regime": "Post-earnings IV crush benutten.",
        "strike_rules": "Short Put onder recente swing low; Long Put ter bescherming 5 punten lager.",
        "exit_rules": "Winst nemen bij 50% max winst vóór 8 februari om niet verrast te worden door Feb 2H.",
        "next_preview": "Feb 2H: Let op voor de traditionele late-februari consolidatie."
    },
    "Feb_2H": {
        "badge": "NEUTRAAL / CONSOLIDATIE",
        "emoji": "🟡",
        "context": "Besluiteloze markt door late earnings en macrocijfers. Consolidatie binnen een range is de meest voorkomende uitkomst.",
        "primary": "Iron Condor of Short Strangles met ruime strikes.",
        "alternative": "Bear Call Credit Spread bij zwak momentum.",
        "iv_regime": "Licht verhoogde chop.",
        "strike_rules": "Verkoop 15-Delta strikes aan weerszijden van de range.",
        "exit_rules": "Sluiten bij 50% winst of op OpEx Friday.",
        "next_preview": "Mar 1H: ⚠️ Maart start historisch stroef en volatiel."
    },
    "Mar_1H": {
        "badge": "VOLATILITEIT / STROEF",
        "emoji": "🔴🟡",
        "context": "De vroege maartstart is historisch stroef en volatiel. Geduld loont beter dan agressie.",
        "primary": "Long Volatiliteit / Strangle of Bear Call Credit Spread.",
        "alternative": "Cash positie aanhouden / wachten op de befaamde Mar 2H bodem.",
        "iv_regime": "Hoog en schommelend.",
        "strike_rules": "Verkoop pas puts als SPY oversold raakt op de RSI(14) < 35.",
        "exit_rules": "Geen agressieve naked long calls aanhouden.",
        "next_preview": "Mar 2H: 🚀 STERK HERSTEL! Quarter-end window dressing (+1.49% Midterm, 78% WR)."
    },
    "Mar_2H": {
        "badge": "STERK HERSTEL (KWARTAALEINDE)",
        "emoji": "🟢🟢",
        "context": "Institutionele kwartaalherbalancering (window dressing) drijft een betrouwbare opwaartse beweging richting Q1-einde.",
        "primary": "Bull Call Debit Spread (+0.55 Delta / -0.25 Delta) of ATM Long Calls.",
        "alternative": "Bull Put Credit Spread (25-30 Delta agressief verkopen).",
        "iv_regime": "IV crush aan het einde van het kwartaal.",
        "strike_rules": "Target de bovenkant van de kwartaalrange.",
        "exit_rules": "Sluiten op of rond de laatste handelsdag van maart.",
        "next_preview": "Apr 1H: April seasonality instroom en tax refund liquiditeit (+0.87% Jaarlijks)."
    },
    "Apr_1H": {
        "badge": "APRIL DRIFT / GEMENGD",
        "emoji": "🟢🟡",
        "context": "Start Q1-kwartaalcijfers gecombineerd met tax refund liquiditeit. Resultaten zijn bepalend voor de richting.",
        "primary": "Bull Put Credit Spread (20 Delta) of Long Call Diagonal.",
        "alternative": "Synthetic Long (Long ATM Call gefinancierd door Short OTM Put).",
        "iv_regime": "Laag tot gemiddeld; gunstig voor debit structuren.",
        "strike_rules": "Short Put onder steunniveau van eind maart.",
        "exit_rules": "Winst nemen vóór grote tech-rapportages in week 2.",
        "next_preview": "Apr 2H: 🟢 Sterke pre-OpEx rally in april (+1.08% Jaarlijks, +0.77% Midterm)."
    },
    "Apr_2H": {
        "badge": "BULLISH PRE-OPEX RALLY",
        "emoji": "🟢",
        "context": "Betrouwbare pre-OpEx drift door tax refund piek en positieve kwartaalcijfers-impuls. Pre-earnings instroom.",
        "primary": "Bull Call Debit Spread (+0.60 Delta / -0.30 Delta) of Bull Put Spread.",
        "alternative": "Calendar Call Spread rond megacap rapportages.",
        "iv_regime": "Hoog rond earnings, snelle crush na publicatie.",
        "strike_rules": "Target resistance van 52-week highs.",
        "exit_rules": "Sluiten bij 50-60% max profit vóór de start van mei.",
        "next_preview": "May 1H: Laatste opwaartse stoot vóór de beruchte 'Sell in May'."
    },
    "May_1H": {
        "badge": "VROEGE MEI DRIFT",
        "emoji": "🟢🟡",
        "context": "Vroeg-mei-momentum bestaat, maar de klok tikt naar de seizoensmatige Sell in May-periode. Kortlopend blijven.",
        "primary": "Bull Put Credit Spread (15-20 Delta) of Short-term Call Debit Spread.",
        "alternative": "Covered Call verkoop op piekniveaus.",
        "iv_regime": "Dalend post-earnings.",
        "strike_rules": "Gebruik strakke looptijden (7-14 DTE) om niet vast te zitten in Mei 2H.",
        "exit_rules": "Winst nemen rond 10 mei. GEEN nieuwe lange posities openen na 12 mei!",
        "next_preview": "May 2H: ⚠️ SELL IN MAY KICK-OFF! Midterm gemiddeld -1.19% (44% WR)."
    },
    "May_2H": {
        "badge": "SELL IN MAY (MIDTERM SELL-OFF)",
        "emoji": "🔴",
        "context": "De seizoensmatige zomerdip-kick-off. Politieke onzekerheid in Midterm-jaren versterkt de correctie structureel.",
        "primary": "Bear Call Credit Spread (15-20 Delta short call) of Collar op aandelenbezit.",
        "alternative": "Long Put Hedges (30-45 DTE).",
        "iv_regime": "Lage IV maakt put protectie relatief goedkoop!",
        "strike_rules": "Short Calls boven de mei-top.",
        "exit_rules": "Bescherm kapitaal; winst nemen bij elke diepe dip.",
        "next_preview": "Jun 1H: 🟢 Vroege juni herstelinflow (+1.04% Jaarlijks)."
    },
    "Jun_1H": {
        "badge": "ZOMERINSTROOM",
        "emoji": "🟢",
        "context": "Tijdelijke herstelgolf na de mei-zwakte biedt een korte maar betrouwbare adempauze.",
        "primary": "Bull Put Credit Spread (20 Delta) of Call Debit Spread.",
        "alternative": "Iron Condor met bullish bias.",
        "iv_regime": "Stabiel zomers regime.",
        "strike_rules": "Short Put onder late-mei swing lows.",
        "exit_rules": "Winst verzilveren vóór medio juni.",
        "next_preview": "Jun 2H: ⚠️ Pre-OpEx zomerzwakte en Quadruple Witching."
    },
    "Jun_2H": {
        "badge": "ZOMERZWAKTE / PRE-OPEX",
        "emoji": "🔴",
        "context": "Quadruple Witching herbalancering en zomerliquiditeitsdruk creëren substantiële verkoopdruk in Midterm-jaren.",
        "primary": "Bear Call Credit Spread of Delta Neutral Iron Butterfly.",
        "alternative": "Protective Puts ter bescherming van Q2 winsten.",
        "iv_regime": "Stijgende hedging activiteit rond Quad Witching.",
        "strike_rules": "Verkoop calls boven weerstand.",
        "exit_rules": "Posities sluiten op OpEx Friday.",
        "next_preview": "Jul 1H: 🚀 Vroeg Juli instroom van pensioengelden."
    },
    "Jul_1H": {
        "badge": "JULI LIQUIDITEITSINSTROOM",
        "emoji": "🟢",
        "context": "Nieuwe Q3-pensioenallocaties stuwen vroeg-juli institutioneel hoger.",
        "primary": "Bull Put Credit Spread (15 Delta) of Call Debit Spread.",
        "alternative": "Covered Strangle.",
        "iv_regime": "Laag zomers regime.",
        "strike_rules": "Koop 50-Delta Call, verkoop 25-Delta Call.",
        "exit_rules": "Winst nemen vóór midden juli.",
        "next_preview": "Jul 2H: Zomertop vorming en start Q2 cijfers."
    },
    "Jul_2H": {
        "badge": "ZOMERTOP / CONSOLIDATIE",
        "emoji": "🟡",
        "context": "Zomertop-vorming. Earnings-divergentie tussen Big Tech-winnaars en zwakkere marktdelen.",
        "primary": "Delta Neutral Iron Condor of Call Credit Spread.",
        "alternative": "Collars ter bescherming van de July 1H winsten.",
        "iv_regime": "Earnings IV crush actief.",
        "strike_rules": "Ruime strikes (10-15 Delta) vanwege 'summer chop'.",
        "exit_rules": "Geen overnight exposure meenemen naar Augustus.",
        "next_preview": "Aug 1H: Midterm toont historisch kracht (+1.29%, 78% WR)."
    },
    "Aug_1H": {
        "badge": "MIDTERM AUGUSTUS VEERKRACHT",
        "emoji": "🟢",
        "context": "Opvallend patroon: Midterm-jaren tonen hier veerkracht terwijl Pre-Election-jaren juist hard instorten.",
        "primary": "Bull Put Credit Spread (20 Delta) of Bull Call Spread.",
        "alternative": "Long Volatiliteit / VIX Calls als macro-verzekering.",
        "iv_regime": "Lage volumes kunnen uitslagen vergroten.",
        "strike_rules": "Short Put onder steunniveau van eind juli.",
        "exit_rules": "Winst veiligstellen bij 50% max profit.",
        "next_preview": "Aug 2H: Jackson Hole centrale bankiers conferentie."
    },
    "Aug_2H": {
        "badge": "JACKSON HOLE DRIFT",
        "emoji": "🟢🟡",
        "context": "Fed Jackson Hole-symposium en afnemende vakantieliquiditeit bepalen het koersverloop.",
        "primary": "Iron Condor of Bull Put Spread (15 Delta).",
        "alternative": "Calendar Spreads.",
        "iv_regime": "IV daalt na speeches centrale bankiers.",
        "strike_rules": "16-Delta limits, focus op theta decay.",
        "exit_rules": "Sluiten vóór het begin van gevreesd September!",
        "next_preview": "Sep 1H: ⚠️ Start van de beruchtste beursmaand van het jaar (-1.42% Midterm)."
    },
    "Sep_1H": {
        "badge": "SEPTEMBER KATER (RISICO)",
        "emoji": "🔴",
        "context": "Wall Street keert terug van vakantie en verlaagt risico. De september-kater slaat planmatig toe.",
        "primary": "Bear Put Debit Spread of Cash verhogen.",
        "alternative": "Long Puts als downside hedge.",
        "iv_regime": "Stijgende volatiliteit.",
        "strike_rules": "ATM/OTM Put spreads met 21-30 DTE.",
        "exit_rules": "Neem snelle deelwinsten bij marktcorrecties.",
        "next_preview": "Sep 2H: Pre-OpEx stabilisatie vóór de beruchte Oktober bodem."
    },
    "Sep_2H": {
        "badge": "PRE-OPEX STABILISATIE ★ HUIDIG",
        "emoji": "🟢🟡★",
        "context": "Tijdelijke stabilisatie vóór de beruchte Oktober 1H. Rust voor de storm — posities sluiten is het devies.",
        "primary": "Iron Condor (Delta-Neutraal) of lichte Bull Put Spread (15 Delta).",
        "alternative": "Short Strangle met ruime marges om theta te verzamelen.",
        "iv_regime": "Stabiel tot licht stijgend richting oktober.",
        "strike_rules": "Call spread op recente weerstand, Put spread ruim onder september support.",
        "exit_rules": "ALLES SLUITEN OP OPEX FRIDAY! Neem geen long exposure mee naar Oktober 1H!",
        "next_preview": "🚨 OKTOBER 1H: DE GEVAARLIJKSTE PERIODE VAN HET JAAR (-1.45%, 25% WR)!"
    },
    "Oct_1H": {
        "badge": "CAPITULATIE BODEM (MAX DUBBEL RISICO)",
        "emoji": "🔴🔴🚨",
        "context": "De diepste capitulatiedip van de gehele 4-jarige cyclus. Paniek, politiek en liquidaties komen samen op hun historisch hoogtepunt.",
        "primary": "Agressieve Hedges: Bear Put Debit Spreads, Long Puts of Long VIX Calls.",
        "alternative": "100% Cash voor risk-averse handelaren; bereid buy-the-dip orders voor.",
        "iv_regime": "Piek in implied volatility en marktpaniek.",
        "strike_rules": "Koop 50-Delta Puts zodra support breekt. Wacht met calls tot extreme capitulatie (VIX > 25-30).",
        "exit_rules": "Hedges agressief verzilveren rond OpEx Friday wanneer paniek maximaal is.",
        "next_preview": "🚀 OKTOBER 2H: DE GROTE TURNAROUND! Het startschot voor de mega eindejaarsrally (+1.72%, 62% WR)!"
    },
    "Oct_2H": {
        "badge": "DE GROTE PIVOT / TURNAROUND",
        "emoji": "🟢🟢🚀",
        "context": "Het startschot van de mega-eindejaarsrally. Smart money bouwt posities op na de capitulatie — turnaround is ingezet.",
        "primary": "Bull Call Debit Spread (+0.60 Delta / -0.30 Delta) of Risk Reversal (Sell OTM Put, Koop ATM Call).",
        "alternative": "Agressieve Bull Put Spreads op oversold niveaus.",
        "iv_regime": "IV crush begint na de capitulatiedip; ideaal voor debit spreads.",
        "strike_rules": "Koop ATM Calls met 45-60 DTE gericht op de eindejaarsrally.",
        "exit_rules": "Laat winnaars lopen; rol opwaarts door naar November.",
        "next_preview": "Nov 1H: Post-Election Relief Rally (+1.63% Midterm, 62% WR)!"
    },
    "Nov_1H": {
        "badge": "POST-ELECTION RELIEF RALLY",
        "emoji": "🟢🟢",
        "context": "Het sluiten van de stembussen verwijdert politieke onzekerheid in één klap. Election Relief Rally explodeert.",
        "primary": "Bull Call Debit Spread of ATM Long Calls.",
        "alternative": "Bull Put Credit Spread (20 Delta).",
        "iv_regime": "Sterke daling van de 'Election Volatility' (IV crush).",
        "strike_rules": "Verkoop out-of-the-money calls 3-5% boven de markt.",
        "exit_rules": "Winst vasthouden richting Thanksgiving.",
        "next_preview": "👑 NOVEMBER 2H: HET KROONJUWEEL! 100% WIN RATE IN MIDTERM JAREN (+2.35%)!"
    },
    "Nov_2H": {
        "badge": "KROONJUWEEL A++ (100% WIN RATE)",
        "emoji": "🟢🟢🟢👑",
        "context": "Het historisch perfecte seizoensjuweel. Thanksgiving-liquiditeit en post-election euforie versterken elkaar maximaal.",
        "primary": "Maximale Bullish Exposure: Deep ITM Call LEAPS, Bull Call Spreads, Synthetic Longs.",
        "alternative": "Agressief verkopen van OTM Puts (30 Delta) om royale premie op te strijken.",
        "iv_regime": "Historisch gunstig; gestage Thanksgiving opwaartse stroom.",
        "strike_rules": "Koop 65-Delta Long Calls, verkoop 25-Delta Calls; of naked long calls.",
        "exit_rules": "Winst nemen vóór de eerste week van december.",
        "next_preview": "Dec 1H: Start van de Santa Claus Rally (+1.51% Jaarlijks, 79% WR)."
    },
    "Dec_1H": {
        "badge": "SANTA RALLY KICK-OFF",
        "emoji": "🟢",
        "context": "Gestage Santa Claus-drift met historisch de hoogste jaarlijkse win rate van alle 24 perioden.",
        "primary": "Bull Put Credit Spread (15-20 Delta) of Covered Calls.",
        "alternative": "Iron Condor met bullish skew.",
        "iv_regime": "Lage volatiliteit; sterke theta decay.",
        "strike_rules": "Short Put ruim onder de november low.",
        "exit_rules": "50% winst target voor OpEx Friday.",
        "next_preview": "Dec 2H: Eindejaars window dressing en rollover naar Jan 1H."
    },
    "Dec_2H": {
        "badge": "WINDOW DRESSING / DIVERGENTIE",
        "emoji": "🟡🔴",
        "context": "Jaareinde-winstnemingen en herbalancering sluiten het beursjaar af. Rustige afsluiting na de november-explosie.",
        "primary": "Iron Condor (Theta Melken) of Long Call rollen naar Januari.",
        "alternative": "Cash opbouwen voor de Jan 1H A+ setup.",
        "iv_regime": "Zeer lage holiday volumes.",
        "strike_rules": "Ver OTM strikes (10 Delta) om holiday theta te incasseren.",
        "exit_rules": "Posities sluiten vóór 31 december; nieuw handelsplan klaarzetten!",
        "next_preview": "Jan 1H: Het nieuwe jaar start met A+ Bull Confluence (+1.28% tot +1.73%)!"
    }
}


def build_confluence_text(ann_stat: dict, pres_stat: dict, context: str, cycle_label: str) -> str:
    """
    Generate the full confluence description from live JSON statistics.
    Combines a dynamically computed data header with the editorial context from the playbook.
    This ensures the text is always in sync with the actual computed stats — no hardcoded numbers.
    """
    ann_avg  = ann_stat["avg"]
    ann_wr   = ann_stat["wr"]
    ann_n    = ann_stat["n"]
    pres_avg = pres_stat["avg"]
    pres_wr  = pres_stat["wr"]
    pres_n   = pres_stat["n"]

    # Signal prefix derived from the data itself
    if pres_wr >= 95.0 and pres_avg > 1.0:
        prefix = "A+ CONFLUENCE"
    elif pres_wr <= 30.0 and pres_avg < -0.5:
        prefix = "DUBBEL RISICO"
    elif pres_avg > 0.8 and ann_avg > 0.5:
        prefix = "BULLISH CONFLUENCE"
    elif pres_avg < -0.5 or ann_avg < -0.5:
        prefix = "BEARISH DRUK"
    else:
        prefix = "NEUTRAAL"

    return (
        f"[{prefix}] "
        f"Jaarlijks: {ann_avg:+.2f}% ({ann_wr:.0f}% WR, {ann_n}j) | "
        f"{cycle_label}: {pres_avg:+.2f}% ({pres_wr:.0f}% WR, {pres_n} vergelijkbare jaren). "
        f"{context}"
    )


def get_3rd_friday(year, month):
    d = datetime.date(year, month, 1)
    while d.weekday() != 4:
        d += datetime.timedelta(days=1)
    d += datetime.timedelta(days=14)
    return d

def compute_calendar_periods(year):
    periods = []
    cycle_key = year % 4
    cycle_name = CYCLE_NAMES[cycle_key]

    for m in range(1, 13):
        m_code = MONTHS[m - 1]
        m_nl = MONTHS_NL[m_code]
        
        prev_opex = get_3rd_friday(year - 1, 12) if m == 1 else get_3rd_friday(year, m - 1)
        curr_opex = get_3rd_friday(year, m)
        
        total_days = (curr_opex - prev_opex).days
        mid_date = prev_opex + datetime.timedelta(days=total_days // 2)
        
        # 1H Post-OpEx: Saturday after prev OpEx to midpoint Friday
        p1_start = prev_opex + datetime.timedelta(days=1)
        p1_end = mid_date
        
        # 2H Pre-OpEx: Saturday after midpoint to Friday OpEx
        p2_start = mid_date + datetime.timedelta(days=1)
        p2_end = curr_opex
        
        ann_1h = annual_data["stats_1h"][m_code]
        ann_2h = annual_data["stats_2h"][m_code]
        
        pres_cycle_label = "Midterm" if cycle_key == 2 else ("Pre-Election" if cycle_key == 3 else ("Election" if cycle_key == 0 else "Post-Election"))
        pres_stats = pres_data["cycles"][pres_cycle_label]
        pres_1h = pres_stats["stats_1h"][m_code]
        pres_2h = pres_stats["stats_2h"][m_code]
        
        strat_1h = STRATEGY_PLAYBOOK[f"{m_code}_1H"]
        strat_2h = STRATEGY_PLAYBOOK[f"{m_code}_2H"]

        # Build confluence text dynamically from live stats (fix #6)
        confluence_1h = build_confluence_text(ann_1h, pres_1h, strat_1h["context"], pres_cycle_label)
        confluence_2h = build_confluence_text(ann_2h, pres_2h, strat_2h["context"], pres_cycle_label)

        periods.append({
            "year": year,
            "month": m,
            "month_code": m_code,
            "month_nl": m_nl,
            "half": "1H",
            "half_name": "1H (Post-OpEx)",
            "start_date": p1_start,
            "end_date": p1_end,
            "dtend_exclusive": p1_end + datetime.timedelta(days=1),
            "cycle_key": cycle_key,
            "cycle_name": cycle_name,
            "pres_cycle_label": pres_cycle_label,
            "ann_stats": ann_1h,
            "pres_stats": pres_1h,
            "confluence": confluence_1h,   # dynamic — always in sync with JSON data
            "strat": strat_1h
        })

        periods.append({
            "year": year,
            "month": m,
            "month_code": m_code,
            "month_nl": m_nl,
            "half": "2H",
            "half_name": "2H (Pre-OpEx)",
            "start_date": p2_start,
            "end_date": p2_end,
            "dtend_exclusive": p2_end + datetime.timedelta(days=1),
            "cycle_key": cycle_key,
            "cycle_name": cycle_name,
            "pres_cycle_label": pres_cycle_label,
            "ann_stats": ann_2h,
            "pres_stats": pres_2h,
            "confluence": confluence_2h,   # dynamic — always in sync with JSON data
            "strat": strat_2h
        })
        
    return periods

def generate_ics_content(periods, cal_name="SPY Seasonality & Opties"):
    now_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//ETF Daily//SPY Seasonality & Options Calendar//NL",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:{cal_name}",
        "X-WR-TIMEZONE:Europe/Amsterdam",
        "X-WR-CALDESC:24 Twee-Wekelijkse OpEx Perioden met Jaarlijkse Cyclus, Presidentiele Cyclus en Optie Strategieen per periode",
    ]
    
    for p in periods:
        uid = f"spy-{p['year']}-{p['month']:02d}-{p['half']}@etfdaily.seasonality"
        dtstart = p["start_date"].strftime("%Y%m%d")
        dtend = p["dtend_exclusive"].strftime("%Y%m%d")
        
        badge = p["strat"]["badge"]
        emoji = p["strat"]["emoji"]
        title = f"{emoji} SPY [{badge}] {p['month_code']} {p['half']} | {p['ann_stats']['avg']:+.2f}% / {p['pres_stats']['avg']:+.2f}%"
        
        desc_lines = [
            f"=== SPY SEIZOENSMATIGHEID & OPTIE STRATEGIE ===",
            f"PERIODE: {p['month_nl']} {p['half_name']} {p['year']} ({p['start_date'].strftime('%d-%b')} t/m {p['end_date'].strftime('%d-%b-%Y')})",
            f"STATUS / SIGNAAL: {p['strat']['badge']}",
            f"",
            f"--- 1. JAARLIJKSE CYCLUS (1993-2026 / 34 JAAR) ---",
            f"• Gemiddeld Rendement: {p['ann_stats']['avg']:+.2f}%",
            f"• Mediaan: {p['ann_stats']['median']:+.2f}%",
            f"• Win Rate: {p['ann_stats']['wr']:.1f}% ({p['ann_stats']['n']} cycli)",
            f"• Volatiliteit (StdDev): {p['ann_stats']['std']:.2f}%",
            f"",
            f"--- 2. PRESIDENTIELE CYCLUS ({p['cycle_name']}) ---",
            f"• Gemiddeld Rendement: {p['pres_stats']['avg']:+.2f}%",
            f"• Mediaan: {p['pres_stats']['median']:+.2f}%",
            f"• Win Rate: {p['pres_stats']['wr']:.1f}% ({p['pres_stats']['n']} vergelijkbare jaren)",
            f"• Confluence Oordeel: {p['confluence']}",
            f"",
            f"--- 3. AANBEVOLEN OPTIE STRATEGIE & PLAYBOOK ---",
            f"🎯 Primaire Strategie: {p['strat']['primary']}",
            f"🔄 Alternatieve Setup: {p['strat']['alternative']}",
            f"📊 IV & Regime: {p['strat']['iv_regime']}",
            f"📐 Strike Keuze & Delta: {p['strat']['strike_rules']}",
            f"🛡️ Exit & Risicobeheer: {p['strat']['exit_rules']}",
            f"",
            f"--- 4. VOORUITBLIK VOLGENDE PERIODE ---",
            f"👉 {p['strat']['next_preview']}",
            f"",
            f"Bron: ETF Daily Seasonality Engine & S&P 500 Historical OpEx Database"
        ]
        
        raw_desc = "\\n".join([line.replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;") for line in desc_lines])
        
        lines.append("BEGIN:VEVENT")
        lines.append(f"UID:{uid}")
        lines.append(f"DTSTAMP:{now_str}")
        lines.append(f"DTSTART;VALUE=DATE:{dtstart}")
        lines.append(f"DTEND;VALUE=DATE:{dtend}")
        lines.append(f"SUMMARY:{title.replace(',', ' -')}")
        lines.append(f"DESCRIPTION:{raw_desc}")
        lines.append("STATUS:CONFIRMED")
        lines.append("TRANSP:TRANSPARENT")
        lines.append("CATEGORIES:Trading,Seasonality,Options")
        lines.append("END:VEVENT")
        
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines)

def generate_csv_content(periods):
    header = ["Subject", "Start Date", "Start Time", "End Date", "End Time", "All Day Event", "Description", "Location", "Private"]
    rows = [",".join(header)]
    
    for p in periods:
        badge = p["strat"]["badge"]
        emoji = p["strat"]["emoji"]
        subject = f"{emoji} SPY [{badge}] {p['month_code']} {p['half']} | Ann: {p['ann_stats']['avg']:+.2f}% | Pres: {p['pres_stats']['avg']:+.2f}%"
        start_date_str = p["start_date"].strftime("%m/%d/%Y")
        end_date_str = p["end_date"].strftime("%m/%d/%Y")
        
        desc_text = (
            f"Periode: {p['month_nl']} {p['half_name']} {p['year']}\n"
            f"Signaal: {p['strat']['badge']}\n\n"
            f"JAARLIJKSE CYCLUS: Avg {p['ann_stats']['avg']:+.2f}% | WR {p['ann_stats']['wr']:.1f}%\n"
            f"PRESIDENTIELE CYCLUS ({p['cycle_name']}): Avg {p['pres_stats']['avg']:+.2f}% | WR {p['pres_stats']['wr']:.1f}%\n\n"
            f"PRIMAIRE OPTIE STRATEGIE:\n{p['strat']['primary']}\n\n"
            f"ALTERNATIEF:\n{p['strat']['alternative']}\n\n"
            f"STRIKE REGELS:\n{p['strat']['strike_rules']}\n\n"
            f"EXIT CRITERIA:\n{p['strat']['exit_rules']}\n\n"
            f"VOLGENDE PERIODE:\n{p['strat']['next_preview']}"
        )
        escaped_subject = '"' + subject.replace('"', '""') + '"'
        escaped_desc = '"' + desc_text.replace('"', '""') + '"'
        
        row = f"{escaped_subject},{start_date_str},,{end_date_str},,True,{escaped_desc},Options Desk,False"
        rows.append(row)
        
    return "\n".join(rows)

def main():
    print("Generating Google Calendar Seasonality & Options packages...")
    
    # 1. Generate for 2026 (Midterm Year)
    periods_2026 = compute_calendar_periods(2026)
    ics_2026 = generate_ics_content(periods_2026, cal_name="SPY Seasonality & Opties (Midterm 2026)")
    csv_2026 = generate_csv_content(periods_2026)
    
    # 2. Generate for 2026 + 2027 (Midterm + Pre-Election Year 2-year package)
    periods_2027 = compute_calendar_periods(2027)
    periods_combined = periods_2026 + periods_2027
    ics_combined = generate_ics_content(periods_combined, cal_name="SPY Seasonality & Opties (2026-2027)")
    csv_combined = generate_csv_content(periods_combined)
    
    # File targets in presidential package
    ics_file_2026 = PRES_PKG_DIR / "spy_seasonality_options_2026.ics"
    csv_file_2026 = PRES_PKG_DIR / "spy_seasonality_options_2026_google_calendar.csv"
    ics_file_comb = PRES_PKG_DIR / "spy_seasonality_options_2026_2027.ics"
    csv_file_comb = PRES_PKG_DIR / "spy_seasonality_options_2026_2027_google_calendar.csv"
    
    with open(ics_file_2026, "w", encoding="utf-8") as f:
        f.write(ics_2026)
    with open(csv_file_2026, "w", encoding="utf-8") as f:
        f.write(csv_2026)
    with open(ics_file_comb, "w", encoding="utf-8") as f:
        f.write(ics_combined)
    with open(csv_file_comb, "w", encoding="utf-8") as f:
        f.write(csv_combined)
        
    print(f"Saved: {ics_file_2026} ({len(periods_2026)} events)")
    print(f"Saved: {csv_file_2026}")
    print(f"Saved: {ics_file_comb} ({len(periods_combined)} events)")
    print(f"Saved: {csv_file_comb}")

    # Distribute to annual_cycle_package and datasente (fix #7: single distribute() call)
    distribute(
        source_files=[ics_file_2026, csv_file_2026, ics_file_comb, csv_file_comb],
        extra_dirs=[ANN_PKG_DIR, DATASENTE_DIR]
    )
    print("All calendar files synced to annual_cycle_package and datasente!")

if __name__ == "__main__":
    main()
