# Performance Vergelijking: -7 Dagen vs Origineel vs +7 Dagen (Gecorrigeerd)

Hier is de vergelijking van de 3 situaties (gemiddeld over alle maanden) voor SPX (^GSPC), QQQ en SMH in midterm election years.
*(Noot: In de voorgaande berekening werden de resterende maanden van 2026 abusievelijk meegenomen met een rendement van 0%. Dit is nu gecorrigeerd, waardoor de daadwerkelijke percentages en winstkansen over de afgesloten maanden fractioneel hoger liggen.)*

## 1. Overall Aggregatie (Alle periodes gecombineerd per symbool)
Dit is de breedste blik: het gemiddelde van de "1e-tot-1e", "15e-tot-15e" en "OpEx-tot-OpEx" bij elkaar opgeteld per situatie.

| Symbool | Situatie | Gem. Winstkans (%) | Gem. Rendement per maand (%) |
| :--- | :--- | :--- | :--- |
| **QQQ** | -7 Dagen | 54.4% | 0.45% |
| | Origineel | 54.7% | 0.55% |
| | **+7 Dagen** | **55.5%** | **0.63%** |
| | | | |
| **SMH** | -7 Dagen | 52.5% | 0.67% |
| | Origineel | 52.7% | 0.84% |
| | **+7 Dagen** | **55.0%** | **0.94%** |
| | | | |
| **^GSPC (SPX)**| -7 Dagen | 61.9% | 0.34% |
| | Origineel | 60.7% | 0.42% |
| | **+7 Dagen** | **64.0%** | **0.49%** |

> [!TIP]
> **Hoofdconclusie:** Over de hele linie presteert de **+7 Dagen** situatie (een week later) het beste. Zowel de winstkans als het gemiddelde rendement ligt consequent hoger dan bij de originele timing of de vervroegde timing (-7 dagen) voor alle 3 de indexen. De eerdere conclusie blijft dus recht overeind!

---

## 2. Uitsplitsing per Specifieke Periode
Als we inzoomen op de exacte data (1e, 15e, of OpEx), zien we het volgende beeld over rendement:

### Gemiddeld Rendement per Maand (%)
| Symbool | Periode | -7 Dagen | Origineel | +7 Dagen | Winnaar Rendement |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **QQQ** | 15e-tot-15e | 0.47% | 0.58% | **0.70%** | +7 Dagen |
| | 1e-tot-1e | 0.27% | 0.38% | **0.47%** | +7 Dagen |
| | OpEx-tot-OpEx | 0.61% | 0.70% | **0.72%** | +7 Dagen |
| **SMH** | 15e-tot-15e | 0.61% | 0.85% | **0.94%** | +7 Dagen |
| | 1e-tot-1e | 0.51% | **0.71%** | 0.61% | Origineel |
| | OpEx-tot-OpEx | 0.89% | 0.95% | **1.28%** | +7 Dagen |
| **^GSPC** | 15e-tot-15e | 0.35% | 0.40% | **0.57%** | +7 Dagen |
| | 1e-tot-1e | 0.25% | 0.34% | **0.35%** | +7 Dagen |
| | OpEx-tot-OpEx | 0.42% | 0.53% | **0.55%** | +7 Dagen |


### Gemiddelde Winstkans (%)
| Symbool | Periode | -7 Dagen | Origineel | +7 Dagen | Winnaar Winstkans |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **QQQ** | 15e-tot-15e | 52.2% | 56.7% | **58.2%** | +7 Dagen |
| | 1e-tot-1e | **54.4%** | 47.8% | 52.2% | -7 Dagen |
| | OpEx-tot-OpEx | 56.7% | **59.7%** | 56.1% | Origineel |
| **SMH** | 15e-tot-15e | 47.8% | 50.7% | **58.2%** | +7 Dagen |
| | 1e-tot-1e | **55.9%** | 53.7% | 47.8% | -7 Dagen |
| | OpEx-tot-OpEx | 53.7% | 53.7% | **59.1%** | +7 Dagen |
| **^GSPC** | 15e-tot-15e | 62.7% | 59.7% | **64.2%** | +7 Dagen |
| | 1e-tot-1e | **63.2%** | 61.2% | 62.7% | -7 Dagen |
| | OpEx-tot-OpEx | 59.7% | 61.2% | **65.2%** | +7 Dagen |

## Conclusie
1. **Rendement (Yield):** De strategie van de trade **een week uitstellen (+7 Dagen)** levert bijna altijd het hoogste gemiddelde maandelijkse rendement op, met name bij *OpEx* (optie expiratie) en de *15e van de maand*. Enkel de start van de maand (1e-tot-1e) presteert voor SMH beter op de originele timing. (Voor SPX verslaat +7 dagen nu zelfs nèt de originele timing voor de 1e).
2. **Winstkans (Win Rate):** Wat betreft de winstkans zien we een vergelijkbare trend. "+7 Dagen" domineert bij de 15e en de OpEx. Bij de start van de maand (1e-tot-1e) zien we steevast dat de vroegste timing ("-7 Dagen") net iets vaker een winstgevende maand oplevert, hoewel het absolute totaalrendement nog steeds lager uitvalt.
3. **Slechtste Scenario:** De trade een week vervroegen ("-7 Dagen") is onmiskenbaar de minst aantrekkelijke optie qua totaalrendement. 

De algemene winnaar in alle scenario's qua performance blijft eenduidig: **Een week later (+7 Dagen)**.
