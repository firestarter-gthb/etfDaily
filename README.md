# ETF & Global Macro Daily Analysis Engine (`etfDaily`)

Een uitgebreide repository voor **dagelijkse marktanalyses, multi-asset en landen-ETF momentum ranking, pensioenallocatiestrategieën, seizoens- en presidentscyclus analyses en trading exit optimalisaties**.

---

## 📁 Repository Structuur

```text
etfDaily/
├── data/
│   ├── countries/              # 36 UCITS Country & Region ETF CSVs (1M - 20+ jaar historie)
│   ├── indices/                # 17 Global Indices, Commodities & Treasury Bond CSVs
│   ├── sectors/                # 19 S&P 500 Select Sector & Industry ETF CSVs
│   └── daily/                  # Dagelijkse 1D data van SPY, SPX, AAPL, GDAXI, TRIN
├── scripts/
│   ├── data_download/          # Scripts om data automatisch via yfinance te downloaden/updaten
│   │   ├── download_country_etfs.py
│   │   ├── download_indices_data.py
│   │   └── download_sector_etfs.py
│   ├── momentum/               # Landen & Sector ETF momentum & correlatie analyses
│   │   ├── country_momentum.py
│   │   ├── country_correlation.py
│   │   ├── compare_alt_etfs.py
│   │   ├── compare_us_indices.py
│   │   └── momentum_allocation_backtest.py
│   ├── pension/                # Pensioenopbouw & Lifecycle backtests (MSCI World, Momentum)
│   │   ├── msci_pension_strategy.py
│   │   └── pension_cycle_backtest.py
│   ├── seasonality/            # Seizoenspatronen, OpEx cycli & US Presidentscyclus
│   │   ├── presidential_cycle_analysis.py
│   │   ├── annual_seasonality.py
│   │   ├── annual_seasonality_opex.py
│   │   ├── compare_seasonality.py
│   │   ├── shifted_seasonality.py
│   │   ├── verify_seasonality.py
│   │   ├── verify_presidential_zones.py
│   │   ├── smh_seasonality.py
│   │   ├── smh_opex_seasonality.py
│   │   ├── spx_monthly_seasonality.py
│   │   └── spx_midmonth_seasonality.py
│   └── trading/                # Dagelijkse setups, trade analyzers en exit evaluaties
│       ├── sniper_trade_analyzer.py
│       ├── test_smart_exits.py
│       └── test_opex_vs_cal.py
├── reports/
│   ├── research/               # Volledige onderzoeksrapporten, artikelen & infographics (Markdown)
│   │   ├── global_momentum_ranking.md
│   │   ├── msci_pension_analysis.md
│   │   ├── presidential_cycle_seasonality.md
│   │   ├── presidential_cycle_article.md
│   │   ├── presidential_cycle_infographic.md
│   │   ├── annual_seasonality_infographic.md
│   │   ├── comparison_seasonality_results.md
│   │   ├── shifted_seasonality_results.md
│   │   ├── zone_verification_report.md
│   │   ├── smh_options_strategy.md
│   │   ├── spx_midterm_seasonality.md
│   │   └── spx_monthly_seasonality.md
│   └── figures/                # Gegenereerde grafieken, visualisaties & zip-pakketten
│       ├── alternative_etfs.png
│       ├── equity_curve.png
│       ├── pension_backtest.png
│       ├── us_indices_long_term.png
│       ├── presidential_cycle_zones_*.jpg
│       ├── annual_seasonality_chart_*.jpg
│       └── seasonality_comparison_*.jpg
├── requirements.txt            # Python dependencies
├── .gitignore
└── README.md
```

---

## 📊 Belangrijkste Onderzoeksmodules

### 1. Global Country ETF Momentum Ranking (`scripts/momentum/`)
- **Doel**: Systematische evaluatie van 36 wereldwijde landen- en regio-ETFs op basis van 1M, 3M, 6M en 12M momentum.
- **Uitvoering**:
  ```bash
  python scripts/momentum/country_momentum.py
  python scripts/momentum/country_correlation.py
  ```

### 2. MSCI World & Pensioen Allocatie (`scripts/pension/`)
- **Doel**: Simulatie en optimalisatie van lange-termijn pensioenopbouw met dynamische allocatie (wereldwijde spreiding vs. momentum tilt).
- **Uitvoering**:
  ```bash
  python scripts/pension/msci_pension_strategy.py
  python scripts/pension/pension_cycle_backtest.py
  ```

### 3. Presidentscyclus & Seizoenspatronen (`scripts/seasonality/`)
- **Doel**: Statistische validatie van 4-jarige Amerikaanse presidentscycli, maandelijkse seizoenspatronen (SPY, QQQ, SMH) en de verschuiving naar OpEx-tot-OpEx cycli.
- **Uitvoering**:
  ```bash
  python scripts/seasonality/presidential_cycle_analysis.py
  python scripts/seasonality/smh_seasonality.py
  python scripts/seasonality/annual_seasonality.py
  python scripts/seasonality/compare_seasonality.py
  ```

### 4. Sniper Trade Analysis & Smart Exits (`scripts/trading/`)
- **Doel**: Analyseren van dagelijkse niveaus, trailing stop optimalisaties en vergelijken van holding-periodes.
- **Uitvoering**:
  ```bash
  python scripts/trading/sniper_trade_analyzer.py
  python scripts/trading/test_smart_exits.py
  ```

---

## 🚀 Data Updates

Om de datasets voor landen-ETFs, sector-ETFs en indices bij te werken naar de meest recente koersen:
```bash
python scripts/data_download/download_country_etfs.py
python scripts/data_download/download_indices_data.py
python scripts/data_download/download_sector_etfs.py
```

---

## ⚙️ Installatie

Installeer de benodigde packages:
```bash
pip install -r requirements.txt
```
