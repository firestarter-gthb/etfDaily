# The Presidential Cycle: 24 Expiration Periods per Cycle Year (96-Period Macro Pulse)

*An empirical quantitative analysis of the S&P 500 (SPY 1993 – 2026) across 4 cycle years, 12 monthly option expirations, and 96 seasonal micro-periods*

---

## 1. Introduction: Why Split Presidential Cycles into OpEx Halves?

Yale Hirsch's classic **4-Year Presidential Cycle** is widely recognized as one of the most reliable macroeconomic patterns in modern market history:
- **Year 1 (Post-Election)**: New governance, early regulatory adjustments, selective strength and consolidation.
- **Year 2 (Midterm — *Current Year: 2026!*)**: Legislative gridlock, an infamous summer doldrum, followed by a relief rally once ballots are cast.
- **Year 3 (Pre-Election)**: Pre-election fiscal and monetary tailwinds; historically the most profitable year of the cycle.
- **Year 4 (Election Year)**: Campaign-driven autumn volatility, preceded by a strong spring and followed by a post-election surge.

However, conventional seasonal studies exclusively track calendar months (1st to 30th/31st). This masks vital inflection points. Institutional liquidity, dealer gamma repositioning, and derivatives roll dynamics cluster around **monthly option expiration (OpEx: the 3rd Friday of each month)**.

Following the quantitative methodology established in our [Annual Cycle Analysis](file:///c:/Users/ROB5293/antigravity/etfDaily/reports/annual_cycle_package/annual_cycle_24periods_article_EN.md), we split each monthly expiration cycle (3rd Friday to 3rd Friday) into two equal trading-day halves (~10 days each):
1. **1H (Post-OpEx / First Half)**: From the prior month's 3rd Friday to mid-cycle (trading day 1 through ~10).
2. **2H (Pre-OpEx / Second Half)**: From mid-cycle into the new 3rd Friday (trading day ~11 through ~20).
3. **Full (Complete OpEx Cycle)**: The full 3rd Friday to 3rd Friday cycle.

Across 4 cycle years, this yields **24 periods per cycle year** and an unprecedented **96-period chronological macro pulse**.

---

## 2. Master Calendar Matrix (Infographic)

The visual matrix below presents all 4 presidential cycle years, broken down into 1H, 2H, and Full cycles over 33 years of market data (SPY 1993–2026):

![S&P 500 Presidential Cycle 24 Expiration Periods](presidential_cycle_opex_calendar.png)

---

## 3. 96-Period Macro Pulse & 2026 Midterm Deep Dive

The chart below displays the continuous 4-year cycle (top panel: 96 periods with cumulative trajectory) alongside a granular deep dive into the 24 periods of the current **Midterm Year (2026)** (bottom panel):

![96-Period Presidential Cycle Pulse & Midterm Focus](presidential_cycle_96periods_pulse.png)

---

## 4. Key Discoveries from the 96-Period Breakdown

### 1. The Midterm Autumn Anatomy (The 2026 Playbook)
While general consensus warns of "a weak autumn in midterm years", the split OpEx data uncovers the exact anatomy of the turning point:
- **September 1H (-1.42%, 50% Win Rate)** takes the initial hit post-Labor Day.
- **September 2H (+0.33%, 62% WR — *Current Window in 2026!*)** stabilizes ahead of expiration.
- **October 1H (-1.45%, 25% WR)** represents the **true capitulation bottom** (only 2 out of 8 historical years closed in positive territory).
- **October 2H (+1.72%, 62% WR)** establishes the **structural bottom and early reversal**.
- **November 2H (+2.35%, 100% Win Rate)**: The crown jewel of midterm seasonality. In every single observed midterm year in the 33-year history of SPY, the market rallied into Thanksgiving post-election!

### 2. The Pre-Election August Trap
Pre-Election years are widely known as the strongest year of the cycle (+2.84% in Jan, +2.78% in Apr, +2.13% in Jul). However, investors unaware of the micro-structure face a punishing drawdown in **August 1H**:
- Average return: **-2.72%**
- Win rate: **only 12% (1 in 8 years positive)**!
- Followed by a sharp V-shaped recovery in **September 1H (+2.02%, 75% WR)** and an explosive **November 1H (+2.74%, 100% WR)**.

### 3. The 100% Win Rate Elite Club
By segmenting cycles into 1H and 2H, 5 periods emerge with an immaculate **100% historical Win Rate**:
1. **Midterm Jan 1H**: +1.73% (9 of 9 years positive)
2. **Midterm Nov 2H**: +2.35% (8 of 8 years positive)
3. **Pre-Election May 1H**: +1.85% (8 of 8 years positive)
4. **Pre-Election Nov 1H**: +2.74% (8 of 8 years positive)
5. **Election Apr 1H**: +3.05% (8 of 8 years positive)

---

## 5. Summary of Package Files

- **Infographics**:
  - [`presidential_cycle_opex_calendar.png`](file:///c:/Users/ROB5293/antigravity/etfDaily/reports/presidential_cycle_package/presidential_cycle_opex_calendar.png): Master 4-year calendar matrix (12 months × 1H, 2H, Full).
  - [`presidential_cycle_96periods_pulse.png`](file:///c:/Users/ROB5293/antigravity/etfDaily/reports/presidential_cycle_package/presidential_cycle_96periods_pulse.png): Sequential 96-period pulse with cumulative curve and 2026 Midterm focus.
- **Data**:
  - [`presidential_cycle_24periods_stats.json`](file:///c:/Users/ROB5293/antigravity/etfDaily/reports/presidential_cycle_package/presidential_cycle_24periods_stats.json): Complete dataset containing means, medians, win rates, and standard deviations.
- **Python Pipeline**:
  - [`presidential_cycle_24periods_opex.py`](file:///c:/Users/ROB5293/antigravity/etfDaily/scripts/seasonality/presidential_cycle_24periods_opex.py): Production-ready script to regenerate all data and charts.
