# ETF Daily — Global Macro & Seasonality Analysis Engine

> **Systematische marktanalyse** voor ETF-momentum, pensioenallocatie, Amerikaanse seizoenspatronen en de 4-jarige presidentscyclus, volledig uitgewerkt naar **24 half-maandelijkse OpEx-perioden** met bijbehorend optie-strategie playbook.

---

## Inhoudsopgave

1. [Overzicht](#overzicht)
2. [Repository structuur](#repository-structuur)
3. [Seizoensmatigheid & Presidentscyclus Suite](#seizoensmatigheid--presidentscyclus-suite)
4. [Momentum & Landen ETF Ranking](#momentum--landen-etf-ranking)
5. [Pensioenallocatie & Backtests](#pensioenallocatie--backtests)
6. [TradingView Pine Script Indicator](#tradingview-pine-script-indicator)
7. [Google Calendar Integratie](#google-calendar-integratie)
8. [Data Updates](#data-updates)
9. [Installatie](#installatie)
10. [Kernbevindingen](#kernbevindingen)

---

## Overzicht

`etfDaily` is een kwantitatieve analyse-engine voor systematische beursinzichten. De repository combineert **34 jaar SPY data (1993–2026)** met de **4-jarige Amerikaanse Presidentscyclus** om tactische optie-strategieën te genereren per twee-wekelijkse OpEx-periode.

### Wat maakt dit uniek?

- **24-periode methodologie**: Elke kalendermaand is gesplitst in een **1H (Post-OpEx, ~10 handelsdagen)** en een **2H (Pre-OpEx, ~10 handelsdagen)** periode, gebaseerd op de daadwerkelijke 3e vrijdag van de maand als snijpunt.
- **Dubbele cyclus-analyse**: Elke periode is getoetst aan zowel de *Jaarlijkse Cyclus* (alle 34 jaar) als de *4-jarige Presidentscyclus* (Post-Election, Midterm, Pre-Election, Election Year).
- **Confluence-signalen**: Beide cycli worden gecombineerd tot een stoplicht-systeem (A+ Bull t/m Dubbel Risico) met bijbehorend optie-strategie playbook.
- **End-to-end tooling**: Van Python-analyse naar Google Calendar export, TradingView Pine Script indicator en Nederlandse handleidingen.

---

## Repository structuur

```text
etfDaily/
├── data/
│   ├── countries/              # 36 UCITS landen- & regio-ETF CSVs (tot 20+ jaar)
│   ├── crypto/                 # Dagelijkse Bitcoin, Ethereum, Solana CSVs
│   ├── indices/                # 18 wereldwijde indices, grondstoffen & obligaties
│   ├── sectors/                # 19 S&P 500 sector- & industrie-ETF CSVs
│   └── daily/                  # 1D data SPY, SPX, AAPL, GDAXI, TRIN
│
├── scripts/
│   ├── data_download/          # yfinance downloaders voor alle datasets
│   ├── momentum/               # Landen- & sector-ETF momentum, correlatie, backtest
│   ├── pension/                # Pensioenopbouw & lifecycle backtests
│   ├── seasonality/            # ⭐ Hoofdmodule – zie sectie hieronder
│   ├── trading/                # Dagelijkse setups, trailing stop & exit optimalisaties
│   └── experiments/            # Chronos-2 tijdreeksforecast experimenten
│
├── reports/
│   ├── annual_cycle_package/   # Jaarlijkse cyclus artikelen, stats JSON & kalenderfiles
│   ├── presidential_cycle_package/ # Presidentscyclus artikelen, stats JSON & assets
│   ├── figures/                # Alle gegenereerde grafieken & infographics
│   └── research/               # Vrije onderzoeksrapporten (markdown)
│
├── tradingview/
│   ├── spy_seasonality_options_confluence.pine  # TradingView v5 indicator
│   └── tradingview_indicator_handleiding.md     # Installatie & gebruikshandleiding
│
├── requirements.txt
└── README.md
```

---

## Seizoensmatigheid & Presidentscyclus Suite

> **Locatie**: `scripts/seasonality/`

De kern van de repository. Alle scripts draaien autonoom en schrijven hun output naar de corresponderende `reports/`-mappen.

### Pipeline volgorde

```bash
# Stap 1: Bereken de 24-periode jaarlijkse statistieken
python scripts/seasonality/annual_cycle_24periods_opex.py

# Stap 2: Bereken de 24-periode presidentscyclus statistieken (4 cyclusjaren × 24 perioden = 96)
python scripts/seasonality/presidential_cycle_24periods_opex.py

# Stap 3: Gecombineerde vergelijkingsvisualisatie (Jaarlijks vs. Midterm vs. Pre-Election)
python scripts/seasonality/combined_annual_presidential_cycle.py

# Stap 4: Genereer Google Calendar (.ics + .csv)
python scripts/seasonality/generate_google_calendar_opex.py

# Stap 5: Genereer TradingView Pine Script indicator
python scripts/seasonality/generate_pinescript_indicator.py
```

### Beschrijving per script

| Script | Doel | Output |
|---|---|---|
| `annual_cycle_24periods_opex.py` | SPY seizoenspatronen (1993–2026) per 24 OpEx-perioden | `annual_cycle_24periods_stats.json` + kalendermatrix |
| `presidential_cycle_24periods_opex.py` | 4-jarige presidentscyclus × 24 perioden = 96 statistieken | `presidential_cycle_24periods_stats.json` + 3 visualisaties |
| `combined_annual_presidential_cycle.py` | Confluentiematrix: Jaarlijks vs. Midterm vs. Pre-Election | `combined_annual_presidential_cycle.png` |
| `generate_google_calendar_opex.py` | iCal + CSV export met volledig optie-playbook per periode | `.ics` & `.csv` bestanden |
| `generate_pinescript_indicator.py` | TradingView v5 indicator met live dashboard & alerts | `spy_seasonality_options_confluence.pine` |
| `utils.py` | Gedeeld hulpprogramma: `distribute()` voor file-distributie | — |

### Methodologie

**Periode-definitie**:
- `1H (Post-OpEx)`: Dag na de 3e vrijdag van maand M−1 t/m het middelpunt van de cyclus
- `2H (Pre-OpEx)`: Dag na het middelpunt t/m de 3e vrijdag van maand M
- Middelpunt = `(ts_prev_opex_end + ts_curr_opex_end) / 2`

**Presidentscyclus sleutels**:

| Sleutel | Jaar | Voorbeeld |
|---|---|---|
| `0` | Election Year | 2024, 2028 |
| `1` | Post-Election | 2025, 2029 |
| `2` | Midterm | 2026, 2030 |
| `3` | Pre-Election | 2027, 2031 |

### Gegenereerde visualisaties

| Bestand | Beschrijving |
|---|---|
| `presidential_cycle_opex_calendar.png` | 12-maands kalendermatrix met 1H/2H/Volledig per cyclusjaar |
| `presidential_cycle_96periods_pulse.png` | 4-jarige vermogenscurve + Midterm deep-dive |
| `combined_annual_presidential_cycle.png` | Vergelijkingsmatrix + stoplicht confluentiebalk |

---

## Momentum & Landen ETF Ranking

> **Locatie**: `scripts/momentum/`

```bash
python scripts/momentum/country_momentum.py      # 36 landen-ETFs: 1M/3M/6M/12M momentum ranking
python scripts/momentum/country_correlation.py   # Correlatiematrix & clustering
python scripts/momentum/compare_us_indices.py    # SPY / QQQ / SMH vergelijking
python scripts/momentum/momentum_allocation_backtest.py  # Momentum-gebaseerde allocatie backtest
```

---

## Pensioenallocatie & Backtests

> **Locatie**: `scripts/pension/`

```bash
python scripts/pension/msci_pension_strategy.py     # MSCI World lifecycle-strategie simulatie
python scripts/pension/pension_cycle_backtest.py    # Presidentscyclus × pensioen-timing backtest
```

---

## TradingView Pine Script Indicator

> **Bestand**: `tradingview/spy_seasonality_options_confluence.pine`
> **Handleiding**: `tradingview/tradingview_indicator_handleiding.md`

Een volledige TradingView Pine Script v5 indicator die real-time aangeeft in welke van de 24 OpEx-perioden de markt zich bevindt.

### Functies

| Feature | Beschrijving |
|---|---|
| **Live Dashboard** | Periode, cyclus, gemiddeld rendement, win rate (jaarlijks + presidentieel) |
| **Dynamisch regime** | `dyn_regime` berekend uit werkelijke geselecteerde-cyclus statistieken — niet hardcoded |
| **Achtergrondkleuring** | Groen → Bullish, Rood → Bearish, Geel → Neutraal per periode |
| **Periode-labels** | Automatische markers op de grafiek bij elke periode-overgang |
| **Dutch alerts** | Volledige Nederlandstalige push-notificaties met kwantitatieve kansen en het complete handelsplan |
| **Cyclus selectie** | Dropdown: Auto / Midterm / Pre-Election / Election / Post-Election |

### Installatie (4 stappen)

1. Genereer de indicator: `python scripts/seasonality/generate_pinescript_indicator.py`
2. Open TradingView → **Pine Editor** → plak de inhoud van `spy_seasonality_options_confluence.pine`
3. Klik **Add to chart**
4. Stel alerts in via **Alerts** → `SPY Nieuwe OpEx Periode Alert`

---

## Google Calendar Integratie

> **Handleiding**: `reports/annual_cycle_package/google_calendar_handleiding.md`

```bash
python scripts/seasonality/generate_google_calendar_opex.py
```

Genereert vier bestanden:

| Bestand | Beschrijving |
|---|---|
| `spy_seasonality_options_2026.ics` | Midterm 2026 — 24 events voor iCal / Apple Calendar / Outlook |
| `spy_seasonality_options_2026_google_calendar.csv` | Google Calendar CSV importformaat |
| `spy_seasonality_options_2026_2027.ics` | 2-jaar pakket Midterm 2026 + Pre-Election 2027 |
| `spy_seasonality_options_2026_2027_google_calendar.csv` | 2-jaar Google Calendar CSV |

Elk agenda-event bevat: signaal-badge, jaarlijkse & presidentiële statistieken, primaire optiestrategie, strike-keuze & delta, exit-criteria en een preview van de volgende periode.

**Google Calendar importeren**:
1. Ga naar [calendar.google.com](https://calendar.google.com) → ⚙️ → **Instellingen**
2. **Importeren** → selecteer het `.ics` of `.csv` bestand

---

## Data Updates

Houd alle datasets bijgewerkt naar de meest recente koersen:

```bash
python scripts/data_download/download_country_etfs.py   # 36 landen-ETFs
python scripts/data_download/download_indices_data.py   # Indices, obligaties, grondstoffen
python scripts/data_download/download_sector_etfs.py    # S&P 500 sector-ETFs
python scripts/data_download/download_crypto_data.py    # Bitcoin, Ethereum, Solana
```

---

## Installatie

```bash
# Clone de repository
git clone https://github.com/firestarter-gthb/etfDaily.git
cd etfDaily

# Installeer dependencies
pip install -r requirements.txt
```

**Python versie**: 3.9+

**Kernpakketten** (zie `requirements.txt`):

| Pakket | Gebruik |
|---|---|
| `pandas` / `numpy` | Data-manipulatie & statistieken |
| `matplotlib` / `seaborn` | Visualisaties & infographics |
| `yfinance` | Historische marktdata ophalen |
| `scipy` | Statistische toetsen |

---

## Kernbevindingen

De meest opmerkelijke kwantitatieve uitkomsten uit de 24-periode analyse (SPY 1993–2026):

### Midterm 2026 — Sleutelperioden

| Periode | Gem. Rendement | Win Rate | Signaal |
|---|:---:|:---:|---|
| **Januari 1H** | +1.73% | **100%** | A+ Bull — 9/9 Midterm-jaren positief |
| **Maart 2H** | +1.49% | 78% | Krachtig kwartaaleinde herstel |
| **Augustus 1H** | +1.29% | 78% | Opvallende Midterm veerkracht |
| **Oktober 1H** | −1.45% | **25%** | ⚠️ Diepste capitulatiedip van de 4-jarige cyclus |
| **Oktober 2H** | +1.72% | 62% | Het grote draaipunt — smart money stapt in |
| **November 2H** | +2.35% | **100%** | 👑 Kroonjuweel — 8/8 Midterm-jaren positief |
| **December 1H** | +1.51% | **79%** | Hoogste jaarlijkse win rate van alle 24 perioden |

### Pre-Election 2027 — Waarschuwingen

| Periode | Gem. Rendement | Win Rate | Signaal |
|---|:---:|:---:|---|
| **Augustus 1H** | −2.72% | **12%** | 🚨 Zwaarste uitverkoop van de gehele 4-jarige cyclus |
| **November 1H** | +2.74% | **100%** | Buitengewone herfstrally na de najaarsdip |

### Election Year 2028 — Uitschieters

| Periode | Gem. Rendement | Win Rate | Signaal |
|---|:---:|:---:|---|
| **April 1H** | +3.05% | **100%** | Krachtigste 1e helft van de gehele 4-jarige cyclus |

---

## Bijdragen & Licentie

Dit is een persoonlijk kwantitatief onderzoeksproject. Bevindingen zijn gebaseerd op historische data en zijn **geen beleggingsadvies**.

> *"The market is a device for transferring money from the impatient to the patient."* — Warren Buffett

---

*Gegenereerd door de ETF Daily Seasonality Engine | SPY 1993–2026 | 402 volledige OpEx-cycli*
