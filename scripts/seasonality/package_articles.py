from pathlib import Path
import os
import shutil
import zipfile

BASE_DIR = Path(__file__).resolve().parent.parent.parent
FIGURES_DIR = BASE_DIR / "reports" / "figures"
TARGET_DIR = Path(r"C:\Users\ROB5293\antigravity\datasente")
TEMP_PACKAGE_DIR = BASE_DIR / "reports" / "presidential_cycle_package"

TARGET_DIR.mkdir(parents=True, exist_ok=True)
TEMP_PACKAGE_DIR.mkdir(parents=True, exist_ok=True)

# 1. Dutch Article Content
article_nl = """# De 4-Jarige Presidentscyclus: Seizoenspatronen & OpEx Handelsstrategie

*Een data-gedreven analyse van de S&P 500 (SPY 1993 – 2026)*

---

## 1. Introductie

De financiële markten bewegen niet in een vacuüm; politieke en monetaire beleidscycli spelen een doorslaggevende rol in het gedrag van beleggers. Een van de meest gedocumenteerde en krachtige macro-patronen is de **4-jarige Amerikaanse Presidentscyclus** (oorspronkelijk ontdekt door Yale Hirsch). 

De theorie stelt dat zittende overheden in de eerste twee jaar van hun ambtstermijn vaak pijnlijke beleidsmaatregelen nemen (wanneer het electoraal het minst schaadt), terwijl in de laatste twee jaar de economie juist fiscaal en monetair wordt gestimuleerd in aanloop naar de volgende verkiezingen.

In dit onderzoek gaan we een stap verder dan traditionele kalendermaanden. We hebben geanalyseerd of het handelen van **expiratie tot expiratie (OpEx: 3e vrijdag tot 3e vrijdag)** een zuiverder en krachtiger signaal geeft dan de traditionele kalendermaand (1e tot 1e van de maand).

---

## 2. De Vier Fasen van de Cyclus

De 4-jarige cyclus wordt opgedeeld in vier unieke seizoensprofielen:

```
Jaar 1: Post-Election (bijv. 2021, 2025, 2029)  -->  Consolidatie & selectieve kracht
Jaar 2: Midterm        (bijv. 2022, 2026, 2030)  -->  Zomerdip & krachtige November-rally
Jaar 3: Pre-Election   (bijv. 2023, 2027, 2031)  -->  Historisch het sterkste beursjaar
Jaar 4: Election Year  (bijv. 2020, 2024, 2028)  -->  Krachtig voorjaar, volatiele herfst
```

### Jaar 1 — Post-Election (bijv. 2025)
Nieuwe regeringen voeren vaak vroeg hervormingen door. De markt kent een sterke lente en vroege zomer:
- **Mei (+4.44% gemiddeld, 78% Win Rate)** en **Juli (+2.58%, 89% WR)** zijn uitgesproken winnaars.
- **Maart (-1.38%)** is de enige structureel zwakke maand in deze cyclus.

### Jaar 2 — Midterm (bijv. 2026)
Midterm-jaren staan bekend om hun uitgesproken seizoensvallei in de zomer, gevolgd door een spectaculaire opluchtingsrally:
- **Zomerdip**: Mei (-1.85%), Juni (-0.57%) en Juli (-0.72%) zijn zwak.
- **September (-1.08%)**: De periode van medio augustus tot medio september is berucht riskant.
- **November (+4.04%, 75% WR)**: Zodra de stembussen sluiten en de politieke verhoudingen helder zijn, start de befaamde *Midterm Relief Rally*.
- **Maart (+2.08%, 89% WR)** en **Augustus (+2.63%, 78% WR)** bieden uitstekende tussentijdse long kansen.

### Jaar 3 — Pre-Election (bijv. 2027)
Historisch gezien met afstand het meest winstgevende jaar voor aandelenbeleggers:
- **Januari t/m Juli** vormt een vrijwel ononderbroken stierenmarkt.
- **Juli springt eruit**: een verbluffende **100% Win Rate** over de gehele dataset!
- **Het Gevaar**: **Augustus (-4.68%, 25% WR)** is de zwaarste daling van de hele 4-jarige cyclus.
- **September (+3.52%)** herstelt direct krachtig na de augustus-verkoopgolf.

### Jaar 4 — Election Year (bijv. 2024, 2028)
- **Februari (+1.52%)**, **April (+3.53%)** en **Juni (+2.13%)** presteren uitstekend.
- **Oktober (-2.56%)**: Onzekerheid over de verkiezingsuitslag leidt steevast tot verhoogde volatiliteit.
- **December (+3.30%, 88% WR)**: Na de verkiezingsuitslag volgt een krachtige eindejaarsrally.

---

## 3. Kalendermaand vs. OpEx-tot-OpEx: Wat Werkt Beter?

Een cruciale ontdekking uit onze data is dat **handelen van Expiratie tot Expiratie (3e vrijdag tot 3e vrijdag)** in **3 van de 4 cyclusjaren superieur** is aan de standaard kalendermaand:

| Cyclus | Sterke Signalen (Kalender) | Sterke Signalen (OpEx) | Winnaar |
| :--- | :---: | :---: | :---: |
| **Post-Election** | 6 | 6 | Gelijk |
| **Midterm** | 3 | 5 | **OpEx (+)** |
| **Pre-Election** | 8 | 10 | **OpEx (+)** |
| **Election Year** | 3 | 7 | **OpEx (+)** |

**Waarom wint OpEx?**  
Institutionele stromen, optieherpositionering en dealer gamma-afwikkeling clusteren rond de 3e vrijdag van de maand. Door de expiratie als ankerpunt te nemen, worden seizoensverschuivingen niet kunstmatig doormidden geknipt.

---

## 4. De OpEx Seizoenskalender (Infographic)

In onderstaand overzicht is elke cyclusmaand geclassificeerd van expiratie tot expiratie:
- 🟢 **Donkergroen (Sterk Positief)**: Gemiddeld rendement > +1.8%
- 🟩 **Lichtgroen (Positief)**: Gemiddeld rendement > +0.4%
- ⬛ **Grijs (Neutraal)**: Rendement tussen -0.4% en +0.4%
- 🟥 **Lichtrood (Negatief)**: Gemiddeld rendement < -0.4%
- 🔴 **Donkerrood (Sterk Negatief)**: Gemiddeld rendement < -1.5%

![Presidential Cycle OpEx Seasonality Calendar](presidential_cycle_opex_calendar.png)

---

## 5. Praktische Conclusies voor Beleggers & Traders

1. **Ken je macro-positie**: Weet altijd in welk cyclusjaar (1 t/m 4) we zitten. Dit frame dicteert of je agressief kunt bijkopen of juist risico moet afbouwen.
2. **Gebruik de 3e vrijdag als navigatiepunt**: Schakel niet om op de 1e van de maand, maar plan executies rond de maandelijkse optie-expiratiedatum.
3. **Vermijd de rode zones**:
   - Midterm September (3e vr aug -> 3e vr sep)
   - Pre-Election Augustus (3e vr jul -> 3e vr aug)
   - Election Oktober (3e vr sep -> 3e vr okt)
4. **Benut de gouden kansen**:
   - Pre-Election Juli (100% historische winstkans)
   - Midterm November (gemiddeld +4.04% na de verkiezingen)
   - Election December (+3.30% jaarafsluiting)

---
*Disclaimer: Deze analyse is uitsluitend bedoeld voor educatieve en informatieve doeleinden en vormt geen financieel advies. Resultaten uit het verleden bieden geen garantie voor de toekomst.*
"""

# 2. English Article Content
article_en = """# The 4-Year Presidential Election Cycle: S&P 500 Seasonality & OpEx Trading Strategy

*A data-driven empirical study on the S&P 500 (SPY 1993 – 2026)*

---

## 1. Introduction

Financial markets do not operate in a vacuum. Political incentives, fiscal stimulus schedules, and election timelines exert a massive structural force on equity performance. The **4-Year Presidential Election Cycle Theory** (first popularized by Yale Hirsch) is one of the most reliable and statistically validated macro-patterns in market history.

The fundamental rationale is straightforward: newly elected administrations tend to front-load unpopular economic policies during the first two years of their term when political capital is highest. Conversely, in the final two years leading up to the election, policy pivots toward economic stimulus to foster voter optimism.

In this research, we take this analysis one step further. Rather than using traditional calendar months, we evaluated whether measuring performance from **Options Expiration to Options Expiration (OpEx: 3rd Friday to 3rd Friday)** yields cleaner, more reliable trading signals.

---

## 2. The Four Stages of the Cycle

The 4-year cycle is divided into four distinct market phases:

```
Year 1: Post-Election  (e.g., 2021, 2025, 2029)  -->  Policy recalibration & selective strength
Year 2: Midterm        (e.g., 2022, 2026, 2030)  -->  Summer drawdown & massive Nov relief rally
Year 3: Pre-Election   (e.g., 2023, 2027, 2031)  -->  Historically the strongest year of the cycle
Year 4: Election Year  (e.g., 2020, 2024, 2028)  -->  Strong spring, pre-election autumn turbulence
```

### Year 1 — Post-Election (e.g., 2025)
Administrations implement reforms early. The equity market demonstrates remarkable momentum through spring and early summer:
- **May (+4.44% average return, 78% Win Rate)** and **July (+2.58%, 89% WR)** are standout performers.
- **March (-1.38%)** represents the only persistent weak spot in this cycle.

### Year 2 — Midterm (e.g., 2026)
Midterm years are infamous for policy uncertainty and pre-election gridlock, leading into a steep summer dip followed by a classic relief rally:
- **Summer Valley**: May (-1.85%), June (-0.57%), and July (-0.72%) are consistently sluggish.
- **September (-1.08%)**: The window from 3rd Friday August to 3rd Friday September is notoriously turbulent.
- **November (+4.04%, 75% WR)**: As election results settle, the *Midterm Relief Rally* generates explosive returns.
- **March (+2.08%, 89% WR)** and **August (+2.63%, 78% WR)** provide excellent early tactical long opportunities.

### Year 3 — Pre-Election (e.g., 2027)
By a wide margin, Year 3 is the most bullish phase in the four-year presidential cycle:
- **January through July** delivers nearly uninterrupted upside momentum.
- **July stands apart**: an astonishing **100% Win Rate** across the entire 33-year SPY dataset!
- **The Red Flag**: **August (-4.68%, 25% WR)** registers the deepest average drawdown in the entire 4-year matrix.
- **September (+3.52%)** rebounds aggressively following the August dip.

### Year 4 — Election Year (e.g., 2024, 2028)
- **February (+1.52%)**, **April (+3.53%)**, and **June (+2.13%)** display robust strength.
- **October (-2.56%)**: Political jitters and election-hedging drive sharp pre-election pullbacks.
- **December (+3.30%, 88% WR)**: Certainty returns post-election, triggering an aggressive year-end rally.

---

## 3. Calendar Month vs. OpEx-to-OpEx: Which Generates Better Signals?

A pivotal finding in our research is that measuring returns from **Options Expiration to Options Expiration (3rd Friday to 3rd Friday)** outperforms the conventional calendar-month framework in **3 out of 4 cycle years**:

| Cycle Phase | Strong Signals (Calendar) | Strong Signals (OpEx) | Winner |
| :--- | :---: | :---: | :---: |
| **Post-Election** | 6 | 6 | Tie |
| **Midterm** | 3 | 5 | **OpEx (+)** |
| **Pre-Election** | 8 | 10 | **OpEx (+)** |
| **Election Year** | 3 | 7 | **OpEx (+)** |

**Why OpEx Outperforms:**  
Institutional rebalancing, dealer gamma exposures, and derivatives settlement cluster around the 3rd Friday of each month. Anchoring seasonal analysis to OpEx dates mirrors institutional capital flows much more accurately than arbitrary 1st-of-the-month cutoffs.

---

## 4. OpEx Seasonality Heatmap (Infographic)

Below is the complete matrix mapping all 48 cycle months classified by OpEx-to-OpEx performance:
- 🟢 **Dark Green (Strong Positive)**: Average return > +1.8%
- 🟩 **Light Green (Positive)**: Average return > +0.4%
- ⬛ **Gray (Neutral)**: Return between -0.4% and +0.4%
- 🟥 **Light Red (Negative)**: Average return < -0.4%
- 🔴 **Dark Red (Strong Negative)**: Average return < -1.5%

![Presidential Cycle OpEx Seasonality Calendar](presidential_cycle_opex_calendar.png)

---

## 5. Key Actionable Rules for Traders & Investors

1. **Always contextualize the cycle year (1 to 4)**: This single macro parameter determines whether to buy dips aggressively or deploy defensive hedging.
2. **Anchor execution to the 3rd Friday**: Align key portfolio rebalancing and trade entries around monthly options expiration dates.
3. **Avoid the major danger zones**:
   - Midterm September (mid-Aug to mid-Sep)
   - Pre-Election August (mid-Jul to mid-Aug)
   - Election October (mid-Sep to mid-Oct)
4. **Capitalize on high-conviction seasonal setups**:
   - Pre-Election July (100% historical win rate)
   - Midterm November (+4.04% post-election relief)
   - Election December (+3.30% year-end continuation)

---
*Disclaimer: This analysis is for educational and informational purposes only and does not constitute financial advice. Past performance is no guarantee of future results.*
"""

# Write markdown files to temp package dir
(TEMP_PACKAGE_DIR / "presidential_cycle_article_NL.md").write_text(article_nl, encoding="utf-8")
(TEMP_PACKAGE_DIR / "presidential_cycle_article_EN.md").write_text(article_en, encoding="utf-8")

# Copy the generated figures into temp package dir
figures = [
    "presidential_cycle_opex_calendar.png",
    "presidential_cycle_bar_comparison.png",
    "presidential_cycle_seasonality_comparison.png"
]

for fig in figures:
    src = FIGURES_DIR / fig
    if src.exists():
        shutil.copy2(src, TEMP_PACKAGE_DIR / fig)
        print(f"Copied {fig} to package directory.")

# Create the ZIP archive directly in TARGET_DIR
zip_output_path = TARGET_DIR / "presidential_cycle_articles_and_figures.zip"

with zipfile.ZipFile(zip_output_path, "w", zipfile.ZIP_DEFLATED) as zf:
    for file in TEMP_PACKAGE_DIR.iterdir():
        if file.is_file():
            zf.write(file, arcname=file.name)
            print(f"Added {file.name} to zip archive.")

print(f"\nSuccessfully created ZIP file at: {zip_output_path}")
print(f"ZIP Size: {zip_output_path.stat().st_size / 1024:.1f} KB")
