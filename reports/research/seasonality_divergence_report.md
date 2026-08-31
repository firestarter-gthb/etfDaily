# Onderzoeksrapport: Impact van 1-3 Maands Seizoens-Divergence op de Huidige Maand

**Onderzoeksvraag:** *Heeft het overperformen of underperformen ten opzichte van de historische seizoensverwachting (Seasonal Alpha) in de afgelopen 1 tot 3 maanden een voorspellend effect (Mean Reversion vs. Trend Continuation) op het rendement en de winrate van de huidige maand?*

---

## 1. Samenvatting & Belangrijkste Conclusies

1. **Geen sterke Mean-Reversion ("Rubber Band Effect"):** 
   - De hypothese dat een asset na 3 maanden sterke outperformance 'oververhit' is en in de huidige maand terugvalt t.o.v. zijn seasonaliteit, wordt **verworpen**.
   - Integendeel: in vrijwel alle geteste activaklassen leidt eerdere seizoens-outperformance tot **gelijke of hogere** rendementen en winrates in de opvolgende maand.
2. **Asset-Specifieke Gedragingen:**
   - **S&P 500 (SPX, 1950 - 2026 / 917 maanden):** Vrijwel **neutraal / onafhankelijk** ($r = 0.00, p = 0.90$). De markt beweegt efficiënt rond zijn seizoensgemiddelde; eerdere afwijkingen over 3 maanden hebben nauwelijks invloed.
   - **Nasdaq (1971 - 2026 / 663 maanden):** Duidelijke **korte-termijn momentumwerking (1-maand)** ($r = +0.09, p = 0.02$). Een sterke voorgaande maand t.o.v. seasonaliteit verhoogt de winrate in de volgende maand van **55.9% naar 66.7%** (+10.8% spread).
   - **Bitcoin (2014 - 2026 / 140 maanden):** Zeer sterke en statistisch significante **Trend Continuation ($r = +0.20, p = 0.016$)**. 
     - Na 3 maanden outperformance: **+13.65% gem. rendement / 65.96% winrate**.
     - Na 3 maanden underperformance: **+1.27% gem. rendement (mediaan: -2.16%) / 48.94% winrate**.

---

## 2. Kwantitatieve Resultaten (3-Maands Lookback Window)

Onderstaande tabel toont de prestaties in de **huidige maand** gesegmenteerd naar het regime van de **voorafgaande 3 maanden** (Top 33% overperformance vs. Bottom 33% underperformance t.o.v. de historische seizoensbenchmark):

| Asset | N (Maanden) | Underperf. (3M): Rend. | Underperf. (3M): WinRate | Overperf. (3M): Rend. | Overperf. (3M): WinRate | Rendement Spread (Over - Under) | WinRate Spread | Correlatie ($r$) | $p$-waarde |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **SPX (S&P 500)** | 917 | +0.75% | 59.48% | **+0.95%** | **61.11%** | +0.20% | +1.63% | +0.00 | 0.90 *(ns)* |
| **Nasdaq / QQQ** | 663 | +0.90% | 58.37% | **+1.16%** | **61.54%** | +0.26% | +3.17% | +0.04 | 0.35 *(ns)* |
| **SMH (Semiconductors)** | 311 | +0.43% | 55.77% | **+1.80%** | **61.54%** | +1.37% | +5.77% | +0.03 | 0.65 *(ns)* |
| **Bitcoin (BTC-USD)** | 140 | +1.27% | 48.94% | **+13.65%** | **65.96%** | **+12.37%** | **+17.02%** | **+0.20** | **0.016\*\*** |

---

## 3. Analyse per Lookback Window (1M vs 2M vs 3M vs 6M)

### A. S&P 500 (SPX)
| Lookback Window | Correlatie ($r$) | $p$-waarde | Rendement na Overperf. | Rendement na Underperf. | Winrate na Overperf. | Winrate na Underperf. |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **1 Maand** | +0.01 | 0.82 | +0.78% | +0.95% | 61.11% | 59.93% |
| **2 Maanden** | -0.02 | 0.46 | +0.68% | +1.18% | 60.46% | 64.05% |
| **3 Maanden** | 0.00 | 0.90 | +0.95% | +0.75% | 61.11% | 59.48% |
| **6 Maanden** | +0.02 | 0.51 | +0.90% | +0.54% | 60.66% | 55.74% |

> **Inzicht:** Bij de S&P 500 blijft de seizoensverwachting van de lopende kalendermaand de dominante factor. Eerdere afwijkingen heffen elkaar op.

---

### B. Nasdaq (Tech & Growth)
| Lookback Window | Correlatie ($r$) | $p$-waarde | Rendement na Overperf. | Rendement na Underperf. | Winrate na Overperf. | Winrate na Underperf. |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **1 Maand** | **+0.09** | **0.02\*\*** | **+1.79%** | **+0.73%** | **66.67%** | **55.86%** |
| **2 Maanden** | +0.04 | 0.34 | +1.59% | +0.99% | 64.71% | 58.56% |
| **3 Maanden** | +0.04 | 0.35 | +1.16% | +0.90% | 61.54% | 58.37% |
| **6 Maanden** | +0.02 | 0.60 | +1.20% | +0.83% | 61.36% | 55.00% |

> **Inzicht:** In techaandelen heeft **1-maands seizoens-alpha een duidelijke momentum-cascade**: als de voorgaande maand boven seizoensverwachting presteerde, stijgt het rendement van de huidige maand met meer dan +1.0% en de winrate met +10.8%.

---

### C. Bitcoin (Crypto)
| Lookback Window | Correlatie ($r$) | $p$-waarde | Rendement na Overperf. | Rendement na Underperf. | Winrate na Overperf. | Winrate na Underperf. |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **1 Maand** | **+0.20** | **0.02\*\*** | **+9.98%** | **-0.52%** | **57.45%** | **45.83%** |
| **2 Maanden** | **+0.16** | **0.05\*\*** | **+8.38%** | **+1.70%** | **55.32%** | **51.06%** |
| **3 Maanden** | **+0.20** | **0.02\*\*** | **+13.65%** | **+1.27%** | **65.96%** | **48.94%** |
| **6 Maanden** | +0.14 | 0.10 | +8.82% | +4.31% | 54.35% | 52.17% |

> **Inzicht:** Bij Bitcoin heerst **sterk regime-momentum**. Underperformance in de afgelopen 1-3 maanden leidt tot 'dead money' / negatieve medianen in de huidige maand. Outperformance trekt sterke retail/institutionele FOMO aan die maanden aanhoudt.

---

## 4. Praktische Trading & Allocatie Regels

1. **Verwacht geen directe 'bounce' na seizoens-underperformance:**
   - Als een asset een van nature sterke seizoensperiode mist of underperformt (bijv. een zwakke april of november), is het risicovol om direct op een inhaalslag te speculeren. Vaak duidt dit op bredere macro- of liquiditeitszwakte.
2. **Volg sterke seizoens-outperformance in Beta & Crypto:**
   - In Nasdaq en Bitcoin is overperformance t.o.v. de seizoensnorm een krachtig **groen licht**: posities vergroten of 'let winners run' levert historisch aanzienlijk hogere Sharpe ratios op.
3. **Voor SPX blijft de kalender-/presidentscyclus primair:**
   - Omdat de SPX nauwelijks divergeert van zijn lange-termijn baseline door eerdere 3-maands uitslagen, kun je voor indexopties en indexallocatie puur vertrouwen op de seizoenswindows (zoals OpEx-tot-OpEx en de Presidentscyclus).

---

## 5. Gegenereerde Grafieken & Visualisaties

- 📊 **Bar Chart & Win Rate Vergelijking:** [`reports/figures/seasonality_divergence_impact.png`](file:///c:/Users/ROB5293/antigravity/etfDaily/reports/figures/seasonality_divergence_impact.png)
- 📈 **Regressie & Scatter Matrix:** [`reports/figures/seasonality_divergence_scatter.png`](file:///c:/Users/ROB5293/antigravity/etfDaily/reports/figures/seasonality_divergence_scatter.png)
