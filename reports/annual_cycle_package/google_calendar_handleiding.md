# Handleiding: Google Calendar (iCal) Import voor SPY Seizoensmatigheid & Optiestrategieën

Met de bijgeleverde agenda-bestanden kun je in één klik alle **24 twee-wekelijkse OpEx-perioden** toevoegen aan je Google Agenda (of Apple Calendar / Outlook).

Elke periode staat direct als doorlopend balk-evenement op je kalender, inclusief:
- **Kleur/Emoji-badge** in de titel (bv. `🟢🟢 SPY [A+ BULL]`, `🔴🔴🚨 SPY [CAPITULATIE BODEM]`, `👑 SPY [KROONJUWEEL]`)
- **Beide cycli direct zichtbaar**: Zowel het historisch rendement van de Jaarlijkse Cyclus als de Presidentiële Cyclus (Midterm 2026)
- **Volledig Optie Playbook in de beschrijving**: Primaire strategie, strikes, delta's, exit regels en de vooruitblik op de volgende periode!

---

## Beschikbare Agendabestanden

De bestanden zijn opgeslagen in de volgende mappen:
1. **`reports/presidential_cycle_package/`**
2. **`reports/annual_cycle_package/`**
3. **`C:\Users\ROB5293\antigravity\datasente\`**

| Bestand | Formaat | Inhoud |
| :--- | :--- | :--- |
| **`spy_seasonality_options_2026.ics`** | iCalendar (`.ics`) | **Aanbevolen.** 24 perioden voor 2026 (Midterm Jaar) met volledige rijke opmaak. |
| **`spy_seasonality_options_2026_2027.ics`** | iCalendar (`.ics`) | 48 perioden: 2026 (Midterm) + 2027 (Pre-Election Jaar 3). |
| **`spy_seasonality_options_2026_google_calendar.csv`** | Google CSV | Alternatief importbestand via CSV voor Google Agenda. |

---

## Stap-voor-stap Importinstructie voor Google Calendar

### Optie A: Importeren in een aparte agenda (Sterk Aanbevolen! ⭐)
*Door een aparte agenda aan te maken, kun je de seizoensbalken met één vinkje aan- en uitzetten op je scherm.*

1. **Maak een nieuwe agenda aan**:
   - Ga op je computer naar [calendar.google.com](https://calendar.google.com).
   - Kijk in de linker zijbalk bij **Andere agenda's** en klik op het plus-icoon (**+**).
   - Kies **Nieuwe agenda maken**.
   - Naam: `SPY Seizoensmatigheid & Opties`.
   - Beschrijving: `24 OpEx Perioden - Jaarlijkse cyclus, Presidentiële cyclus en Optie Playbook`.
   - Klik op **Agenda maken**.

2. **Importeer het bestand**:
   - Klik linksboven of rechtsboven op **Instellingen** (⚙️) $\rightarrow$ **Instellingen**.
   - Klik in het linkermenu op **Importeren en exporteren**.
   - Klik op het vak **Selecteer bestand op je computer**.
   - Blader naar:
     `C:\Users\ROB5293\antigravity\etfDaily\reports\presidential_cycle_package\spy_seasonality_options_2026.ics`
   - Selecteer bij **Toevoegen aan agenda** de zojuist aangemaakte agenda (`SPY Seizoensmatigheid & Opties`).
   - Klik op de blauwe knop **Importeren**.

3. **Klaar!**
   - Google Agenda toont nu: *"24 van de 24 afspraken geïmporteerd"*.
   - Je ziet nu direct alle 24 perioden overzichtelijk verdeeld over het hele jaar.

---

### Optie B: Importeren op smartphone (Android / iPhone)
- Als je stap A op de desktop uitvoert, synchroniseert Google Calendar dit **automatisch** binnen enkele seconden naar de Google Agenda app op je Android of iPhone!
- Je kunt op je telefoon op elk evenement tikken om direct het volledige handelsplan van die week te lezen.

---

## Hoe ziet een agenda-evenement eruit?

### Titel in je Google Agenda:
```text
👑 SPY [KROONJUWEEL A++ (100% WIN RATE)] Nov 2H | +0.92% / +2.35%
```

### Inhoud van de beschrijving wanneer je het evenement opent:
```text
=== SPY SEIZOENSMATIGHEID & OPTIE STRATEGIE ===
PERIODE: November 2H (Pre-OpEx) 2026 (03-Nov t/m 20-Nov-2026)
STATUS / SIGNAAL: KROONJUWEEL A++ (100% WIN RATE)

--- 1. JAARLIJKSE CYCLUS (1993-2026 / 34 JAAR) ---
• Gemiddeld Rendement: +0.92%
• Mediaan: +0.98%
• Win Rate: 70.0% (34 cycli)
• Volatiliteit (StdDev): 1.84%

--- 2. PRESIDENTIELE CYCLUS (Midterm Year (Jaar 2)) ---
• Gemiddeld Rendement: +2.35%
• Mediaan: +2.18%
• Win Rate: 100.0% (8 vergelijkbare jaren - 8 uit 8 positief!)
• Confluence Oordeel: HET ULTIEME SEIZOENSJUWEEL: Midterm +2.35% MET EEN PERFECTE 100.0% HISTORISCHE WIN RATE!

--- 3. AANBEVOLEN OPTIE STRATEGIE & PLAYBOOK ---
🎯 Primaire Strategie: Maximale Bullish Exposure: Deep ITM Call LEAPS, Bull Call Spreads, Synthetic Longs.
🔄 Alternatieve Setup: Agressief verkopen van OTM Puts (30 Delta) om royale premie op te strijken.
📊 IV & Regime: Historisch gunstig; gestage Thanksgiving opwaartse stroom.
📐 Strike Keuze & Delta: Koop 65-Delta Long Calls, verkoop 25-Delta Calls; of naked long calls.
🛡️ Exit & Risicobeheer: Winst nemen vóór de eerste week van december.

--- 4. VOORUITBLIK VOLGENDE PERIODE ---
👉 Dec 1H: Start van de Santa Claus Rally (+1.51% Jaarlijks, 79% WR).
```

---

## Automatisch updaten & andere jaren genereren

Wil je in de toekomst de agenda voor **2027**, **2028** of een ander jaar genereren?
Voer eenvoudig het script uit in PowerShell:
```powershell
python scripts/seasonality/generate_google_calendar_opex.py
```
Dit genereert direct verse bestanden op basis van de meest actuele SPY koersen!
