# Verificatie: Presidential Cycle Zones (OpEx-to-OpEx)

Dit rapport controleert of de zone-toewijzingen (Golden / Danger / Neutral) in het Sniper-systeem overeenkomen met de daadwerkelijke historische OpEx-to-OpEx rendementen van **SPY** over de periode 2001-2026.

---

## Samenvatting: 5 Potentiele Misclassificaties Gevonden

> [!WARNING]
> De verificatie heeft **5 zones** geidentificeerd die niet consistent zijn met de onderliggende data. Dit zijn zones die als GOLDEN zijn gemarkeerd maar negatieve rendementen laten zien, of als DANGER zijn gemarkeerd maar juist sterk positief zijn.

| # | Jaar | Maand | Huidige Zone | Gem. Rendement | Win Rate | Probleem |
|:--|:-----|:------|:------------|:--------------|:---------|:---------|
| 1 | **Jaar 1 (Post-Election)** | April | GOLDEN | +2.47% | **43%** | WR < 50% ondanks positief gemiddelde. Gemiddelde wordt opgeblazen door 2 uitschieters (+8.3%, +13.5%) |
| 2 | **Jaar 2 (Midterm)** | Augustus | DANGER | **+4.26%** | **86%** | Sterk positief met 86% WR! Helemaal geen Danger |
| 3 | **Jaar 3 (Pre-Election)** | September | DANGER | **+3.90%** | **83%** | Sterk positief met 83% WR! Niet consistent met Danger |
| 4 | **Jaar 3 (Pre-Election)** | Oktober | GOLDEN | -0.01% | **50%** | Negatief/neutraal gemiddelde met coin-flip WR |
| 5 | **Jaar 4 (Election)** | November | GOLDEN | **-1.52%** | 67% | Negatief gemiddelde! Wordt gedomineerd door 2008 (-14.7%) |

---

## Detailanalyse per Misclassificatie

### 1. Jaar 1 April: GOLDEN -> Beter NEUTRAL
Individuele OpEx-rendementen: `+8.3, -3.7, +13.5, -0.2, -1.0, +7.1, -6.7`

Het gemiddelde is +2.47% maar de win rate is slechts 43% (3 van 7 winstgevend). De hoge gemiddelde wordt volledig gedreven door 2 extreme uitschieters (2009: +8.3%, 2013: +13.5%). In de meeste jaren verliest de maand. **Aanbeveling: Downgrade naar NEUTRAL.**

---

### 2. Jaar 2 Augustus: DANGER -> Beter GOLDEN!
Individuele OpEx-rendementen: `+10.0, +5.4, +0.8, -1.0, +1.9, +9.6, +3.0`

Dit is de **meest flagrante misclassificatie**. Augustus in een midterm-jaar is met +4.26% gemiddeld rendement en 86% win rate een van de sterkste maanden in de hele cyclus! Slechts 1 van de 7 observaties was negatief (-1.0% in 2014). **Aanbeveling: Upgrade naar GOLDEN.**

> [!IMPORTANT]
> Dit is opmerkelijk: de zones zijn vermoedelijk oorspronkelijk op **kalenderbasis** bepaald (waarin augustus inderdaad zwak is in midterm-jaren). Maar op **OpEx-basis** verschuift de zwakte naar later, waardoor OpEx-augustus juist sterk wordt. De zone-definities zijn dus niet gesynchroniseerd met de OpEx-meetmethode!

---

### 3. Jaar 3 September: DANGER -> Beter GOLDEN!
Individuele OpEx-rendementen: `+4.5, +5.5, +8.4, -0.7, +3.7, +1.9`

Zelfde probleem als #2. Op **kalenderbasis** is september in pre-election jaren historisch negatief, maar op **OpEx-basis** (mid-aug tot mid-sep) is het juist extreem sterk: +3.90% gemiddeld met 83% win rate. **Aanbeveling: Upgrade naar GOLDEN.**

---

### 4. Jaar 3 Oktober: GOLDEN -> Beter NEUTRAL
Individuele OpEx-rendementen: `+0.6, -1.5, +2.0, +4.0, -0.1, -5.0`

Gemiddelde is -0.01% met een 50% win rate. Dit is statistisch neutraal. De positieve maanden cancelen de negatieve precies uit. **Aanbeveling: Downgrade naar NEUTRAL.**

---

### 5. Jaar 4 November: GOLDEN -> Beter NEUTRAL
Individuele OpEx-rendementen: `+5.8, -14.7, -4.9, +2.1, +2.3, +0.2`

Het gemiddelde is -1.52%, volledig gedomineerd door de crash van 2008 (-14.7%). Zelfs als we 2008 als outlier uitsluiten, is het gemiddelde slechts +1.10%, wat eerder neutraal is. **Aanbeveling: Downgrade naar NEUTRAL.**

---

## Zones die WEL correct zijn

De volgende zones zijn consistent met de data en behoeven geen aanpassing:

| Jaar | Zone | Sterke bevestiging |
|:-----|:-----|:-------------------|
| Jaar 1 | Mei GOLDEN | +4.53%, 86% WR |
| Jaar 1 | Juli GOLDEN | +2.96%, 86% WR |
| Jaar 1 | Nov GOLDEN | +2.98%, 86% WR |
| Jaar 1 | Dec GOLDEN | +1.56%, 86% WR |
| Jaar 2 | Nov GOLDEN | +3.75%, 83% WR |
| Jaar 2 | Aug DANGER -> Moet GOLDEN worden (zie boven) |
| Jaar 3 | Apr GOLDEN | +3.02%, 67% WR |
| Jaar 3 | Aug DANGER | -5.54%, 17% WR (heel sterk bevestigd!) |
| Jaar 3 | Dec GOLDEN | +1.91%, 83% WR |
| Jaar 4 | Aug GOLDEN | +2.51%, 83% WR |
| Jaar 4 | Dec GOLDEN | +4.78%, 100% WR (perfecte score!) |
| Jaar 4 | Okt DANGER | -3.35%, 50% WR |

---

## Aanbevolen Gecorrigeerde Zone-definitie

Als je de bovenstaande correcties doorvoert, wordt de zone-tabel:

### Jaar 1: Post-Election
- DANGER: Februari
- GOLDEN: Mei, Juli, November, December
- NEUTRAL: Januari, Maart, **April** (was Golden), Juni, Augustus, September, Oktober

### Jaar 2: Midterm
- DANGER: Juni, September, December (Augustus verwijderd!)
- GOLDEN: **Augustus** (was Danger), November
- NEUTRAL: Januari, Februari, Maart, April, Mei, Juli, Oktober

### Jaar 3: Pre-Election
- DANGER: Augustus (September verwijderd!)
- GOLDEN: April, **September** (was Danger), November, December (Oktober verwijderd!)
- NEUTRAL: Januari, Februari, Maart, Mei, Juni, Juli, **Oktober** (was Golden)

### Jaar 4: Election
- DANGER: Oktober
- GOLDEN: Augustus, December (**November verwijderd!**)
- NEUTRAL: Januari, Februari, Maart, April, Mei, Juni, Juli, September, **November** (was Golden)

---

## Root Cause

> [!CAUTION]
> De kernoorzaak van de misclassificaties is dat de zone-definities oorspronkelijk zijn bepaald op **kalenderbasis** (1e tot 1e), maar het trading-systeem werkt op **OpEx-to-OpEx basis** (3e vrijdag tot 3e vrijdag). Door de ~2 weken verschuiving verschuiven zwakte- en sterkte-periodes, waardoor sommige zones niet meer kloppen.

Wil je dat ik de zone-definities in het script en de infographic bijwerk met de gecorrigeerde waarden?
