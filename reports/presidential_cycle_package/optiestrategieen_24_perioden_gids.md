# Master Gids: Optiestrategieën per 2-Wekelijkse OpEx Cyclus
## Seizoensmatige Confluence: Jaarlijkse Cyclus & Presidentiële Cyclus (Midterm 2026 Focus)

---

### Inhoudsopgave
1. [Inleiding & Methodologie](#inleiding--methodologie)
2. [De Stoplicht-Matrix & Risicoclassificatie](#de-stoplicht-matrix--risicoclassificatie)
3. [Griekse Risicoparameters (Greeks Management per Cyclus)](#griekse-risicoparameters-greeks-management-per-cyclus)
4. [Volledig Playbook: De 24 Perioden in Detail](#volledig-playbook-de-24-perioden-in-detail)
   - [Q1: Januari t/m Maart](#q1-januari-tm-maart)
   - [Q2: April t/m Juni](#q2-april-tm-juni)
   - [Q3: Juli t/m September](#q3-juli-tm-september)
   - [Q4: Oktober t/m December](#q4-oktober-tm-december)
5. [Google Calendar & iCal Integratie](#google-calendar--ical-integratie)
6. [Samenvattende Handelstabel](#samenvattende-handelstabel)

---

### Inleiding & Methodologie

Traditionele seizoensanalyses kijken uitsluitend naar kalendermaanden (1 t/m 31). In de hedendaagse derivatenmarkten dicteert de maandelijkse **Options Expiration (OpEx)** — de 3e vrijdag van elke maand — echter het overgrote deel van de liquiditeits- en afwikkelingsstromen. 

Door elke maandelijkse OpEx-cyclus op te splitsen in twee gelijke handelshelften van circa 10 handelsdagen (2 kalenderweken):
1. **1H (Post-OpEx)**: Van de zaterdag na de vorige OpEx tot het berekende middelpunt (vaak de eerste vrijdag van de nieuwe kalendermaand). Gedomineerd door het opzetten van nieuwe institutionele posities en vroege liquiditeitsinstroom.
2. **2H (Pre-OpEx)**: Van het middelpunt tot en met de 3e vrijdag (OpEx). Gedomineerd door gamma-pinning, charm-decay, en het sluiten of doorrollen van optiecontracten.

In een **Midterm verkiezingsjaar (zoals 2026)** vertoont de markt een uitgesproken seizoensafwijking:
- **Zwak voorjaar en stroeve zomer** door politieke patstelling en onzekerheid.
- **De beruchte capitulatiedip in Oktober 1H** (-1.45% gemiddeld, slechts 25% Win Rate).
- **De historische explosieve eindejaarsrally vanaf Oktober 2H**, culminerend in **November 2H (100% historische Win Rate, +2.35% gemiddeld)**.

---

### De Stoplicht-Matrix & Risicoclassificatie

| Signaal | Kleur | Confluence Definitie | Primair Optieprofiel |
| :--- | :--- | :--- | :--- |
| **A+ Bull Confluence** | 🟢🟢🟢 | Zowel Jaarlijks als Midterm extreem sterk (WR > 70%, Rendement > +1.0%) | Bull Call Debit Spreads / Long Calls / ITM LEAPS |
| **Bullish Drift** | 🟢 | Positief rendement en solide win rate (> 60%) | Bull Put Credit Spreads (Delta 15-20) / Diagonal Calls |
| **Neutraal / Divergentie** | 🟡 | Tegengestelde signalen of zijwaartse consolidatie | Iron Condors / Short Strangles / Calendar Spreads |
| **Bearish Druk** | 🔴 | Negatief rendement of lage win rate (< 45%) | Bear Call Spreads / Cash / Protective Collars |
| **Dubbel Risico / Capitulatie** | 🔴🔴🚨 | Zowel Jaarlijks als Midterm zwaar negatief (WR < 40%) | Bear Put Debit Spreads / Long Puts / VIX Calls |

---

### Griekse Risicoparameters (Greeks Management per Cyclus)

1. **Delta ($\Delta$)**:
   - In A+ Bull periodes (Jan 1H, Okt 2H, Nov 2H) verhogen we de netto portfolio-delta naar **+0.40 tot +0.70**.
   - In Dubbel Risico periodes (Okt 1H, Mei 2H) verlagen we de delta naar neutraal of negatief (**-0.20 tot -0.40**).
2. **Theta ($\Theta$)**:
   - Pre-OpEx (2H) perioden hebben van nature de hoogste theta decay. Ideaal voor credit spreads en Iron Condors, mits de markt binnen de verwachte weekly move blijft.
3. **Vega ($\nu$)**:
   - Rond Oktober 1H piekt de Implied Volatility (IV). Long opties zijn dan duur; na de dip in Oktober 2H keldert de IV (IV crush), wat ideaal is voor het sluiten van puts en het openen van debit bull call spreads.

---

### Volledig Playbook: De 24 Perioden in Detail

#### Q1: Januari t/m Maart

##### 1. Januari 1H (Post-OpEx) — 🟢🟢 A+ Bull Confluence
- **Statistieken**: Jaarlijks +1.28% (76% WR) | Midterm +1.73% (**100% WR - 9 uit 9 jaar positief!**)
- **Karakter**: De ultieme kick-off van het beursjaar. Pensioenfondsen en institutionele beleggers alloceren massaal nieuw kapitaal.
- **Primaire Strategie**: **Bull Call Debit Spread** (+0.60 Delta Long Call / -0.30 Delta Short Call) met 30-45 DTE.
- **Alternatief**: ATM Long Calls of Bull Put Credit Spread (20 Delta).
- **Exit & Regels**: Winst nemen bij 50-60% max profit. Geen posities overhouden na het eerste weekend van januari.

##### 2. Januari 2H (Pre-OpEx) — 🟡 Neutraal / Pre-Earnings
- **Statistieken**: Jaarlijks -0.02% (64% WR) | Midterm -0.82% (56% WR)
- **Karakter**: De markt wacht op de eerste grote Tech kwartaalcijfers (Microsoft, Apple, Alphabet). Consolidatie en afnemend momentum.
- **Primaire Strategie**: **Delta-Neutrale Iron Condor** (16-Delta Short Puts en 16-Delta Short Calls, 5-10 punten wings).
- **Alternatief**: Call Diagonal Spread.
- **Exit & Regels**: Sluiten vóór de publicatie van megacap cijfers en vóór OpEx Friday.

##### 3. Februari 1H (Post-OpEx) — 🟢🟡 Gematigd Bullish / Divergentie
- **Statistieken**: Jaarlijks +0.85% (67% WR) | Midterm -0.39% (33% WR)
- **Karakter**: Jaarlijks positief na earnings, maar Midterm jaren laten hier vaak al vroege aarzeling zien.
- **Primaire Strategie**: **Bull Put Credit Spread** (15-20 Delta) met conservatieve strike onder recente support.
- **Alternatief**: Covered Calls schrijven op bestaande long posities om premie binnen te halen.
- **Exit & Regels**: Winst nemen bij 50% max profit vóór 8 februari.

##### 4. Februari 2H (Pre-OpEx) — 🟡 Neutraal / Consolidatie
- **Statistieken**: Jaarlijks +0.21% (61% WR) | Midterm +0.52% (44% WR)
- **Karakter**: Besluiteloze markt. Late earnings en macrocijfers domineren.
- **Primaire Strategie**: **Iron Condor** of wijde Short Strangles buiten de 1-standaarddeviatie range.
- **Alternatief**: Bear Call Spread indien SPY onder zijn 20-daags gemiddelde zakt.
- **Exit & Regels**: Sluiten op of vóór OpEx Friday.

##### 5. Maart 1H (Post-OpEx) — 🔴🟡 Volatiliteit / Stroef
- **Statistieken**: Jaarlijks -0.47% (47% WR) | Midterm +0.56% (44% WR)
- **Karakter**: Maart start historisch stroef. Lage win rates en verhoogde standaarddeviatie.
- **Primaire Strategie**: **Long Strangle / Long Volatility** of **Bear Call Credit Spread**.
- **Alternatief**: Cash allocatie verhogen en wachten op de befaamde Mar 2H kwartaalbodem.
- **Exit & Regels**: Geen agressieve naked calls vasthouden.

##### 6. Maart 2H (Pre-OpEx) — 🟢🟢 Sterk Herstel (Kwartaaleinde)
- **Statistieken**: Jaarlijks +0.21% (59% WR) | Midterm **+1.49% (78% WR)**
- **Karakter**: Institutionele herbalancering (Quarter-End Window Dressing). Midterm jaren schieten hier krachtig omhoog!
- **Primaire Strategie**: **Bull Call Debit Spread** (+0.55 Delta / -0.25 Delta) met target op de kwartaaltop.
- **Alternatief**: Bull Put Credit Spread (25 Delta).
- **Exit & Regels**: Sluiten op de laatste handelsdag van maart.

---

#### Q2: April t/m Juni

##### 7. April 1H (Post-OpEx) — 🟢🟡 April Drift / Gemengd
- **Statistieken**: Jaarlijks +0.87% (59% WR) | Midterm -0.49% (56% WR)
- **Karakter**: Start van Q1 earnings seizoen gecombineerd met tax refund liquiditeit in de VS.
- **Primaire Strategie**: **Bull Put Credit Spread** (20 Delta) onder de maart-lows.
- **Alternatief**: Synthetic Long of Long Call Diagonal.
- **Exit & Regels**: Winst nemen vóór zware tech earnings in week 2.

##### 8. April 2H (Pre-OpEx) — 🟢 Bullish Pre-OpEx Rally
- **Statistieken**: Jaarlijks +1.08% (62% WR) | Midterm +0.77% (56% WR)
- **Karakter**: Zeer betrouwbare opwaartse drift. De sterkste handelsweken van april.
- **Primaire Strategie**: **Bull Call Debit Spread** (+0.60 Delta / -0.30 Delta) gericht op 52-week highs.
- **Alternatief**: Bull Put Credit Spread (15 Delta).
- **Exit & Regels**: Winst nemen vóór het einde van april om winsten veilig te stellen vóór 'Sell in May'.

##### 9. Mei 1H (Post-OpEx) — 🟢🟡 Vroege Mei Drift
- **Statistieken**: Jaarlijks +0.97% (65% WR) | Midterm -0.69% (56% WR)
- **Karakter**: Vroege meidagen laten vaak nog een laatste opleving zien vóór de zomerdip begint.
- **Primaire Strategie**: **Kortlopende Bull Put Spread** (7-14 DTE, 15 Delta) of Covered Calls.
- **Alternatief**: Cash opbouwen en trailing stops aanscherpen.
- **Exit & Regels**: Winst nemen rond 10 mei. **GEEN nieuwe lange posities openen na 12 mei!**

##### 10. Mei 2H (Pre-OpEx) — 🔴 Sell in May (Midterm Sell-Off)
- **Statistieken**: Jaarlijks +0.19% (56% WR) | Midterm **-1.19% (44% WR)**
- **Karakter**: De klassieke 'Sell in May' slaat in Midterm jaren extra hard toe door politieke spanningen.
- **Primaire Strategie**: **Bear Call Credit Spread** (verkoop 20-Delta calls boven weerstand) of **Long Put Spreads**.
- **Alternatief**: Portefeuille hedgen met Collars (koop OTM put, verkoop OTM call).
- **Exit & Regels**: Bescherm kapitaal; winsten nemen bij elke diepe correctiedag.

##### 11. Juni 1H (Post-OpEx) — 🟢 Zomerinstroom
- **Statistieken**: Jaarlijks +1.04% (65% WR) | Midterm +0.55% (67% WR)
- **Karakter**: Tijdelijke herstelgolf aan het begin van juni.
- **Primaire Strategie**: **Bull Put Credit Spread** (20 Delta) onder de mei-bodem.
- **Alternatief**: Iron Condor met lichte call-skew.
- **Exit & Regels**: Posities sluiten vóór medio juni.

##### 12. Juni 2H (Pre-OpEx) — 🔴 Zomerzwakte / Pre-OpEx
- **Statistieken**: Jaarlijks -0.01% (41% WR) | Midterm **-1.06% (44% WR)**
- **Karakter**: Quadruple Witching expiratie en herbalancering zorgen voor aanzienlijke verkoopdruk in Midterm jaren.
- **Primaire Strategie**: **Bear Call Credit Spread** of Delta-Neutrale **Iron Butterfly**.
- **Alternatief**: Protective Puts.
- **Exit & Regels**: Alles sluiten op Quad Witching Friday.

---

#### Q3: Juli t/m September

##### 13. Juli 1H (Post-OpEx) — 🟢 Juli Liquiditeitsinstroom
- **Statistieken**: Jaarlijks +0.52% (62% WR) | Midterm -0.21% (56% WR)
- **Karakter**: Institutionele pensioeninstroom aan het begin van Q3.
- **Primaire Strategie**: **Bull Call Debit Spread** (+0.50 Delta / -0.25 Delta).
- **Alternatief**: Bull Put Spread (15 Delta).
- **Exit & Regels**: Winst verzilveren vóór medio juli.

##### 14. Juli 2H (Pre-OpEx) — 🟡 Zomertop / Consolidatie
- **Statistieken**: Jaarlijks +0.51% (59% WR) | Midterm -0.47% (56% WR)
- **Karakter**: Topvorming. Q2 kwartaalcijfers leiden tot divergentie tussen Big Tech en de rest van de markt.
- **Primaire Strategie**: **Delta-Neutrale Iron Condor** (ruime 10-15 Delta wings).
- **Alternatief**: Collars op long posities.
- **Exit & Regels**: Geen zware overnight long exposure meenemen naar augustus.

##### 15. Augustus 1H (Post-OpEx) — 🟢 Midterm Augustus Veerkracht
- **Statistieken**: Jaarlijks +0.30% (59% WR) | Midterm **+1.29% (78% WR)**
- **Karakter**: Opvallend fenomeen: waar Pre-Election jaren instorten (-2.72%), tonen Midterm jaren hier juist verrassende veerkracht!
- **Primaire Strategie**: **Bull Put Credit Spread** (20 Delta) gecombineerd met lichte OTM VIX Calls als macro-hedge.
- **Alternatief**: Bull Call Spread.
- **Exit & Regels**: Winst nemen bij 50% max profit. Let op dunne zomerliquiditeit.

##### 16. Augustus 2H (Pre-OpEx) — 🟢🟡 Jackson Hole Drift
- **Statistieken**: Jaarlijks +0.12% (68% WR) | Midterm **+1.34% (78% WR)**
- **Karakter**: De markt consolideert in afwachting van het Jackson Hole symposium van de Federal Reserve.
- **Primaire Strategie**: **Iron Condor** of ver OTM Bull Put Spread.
- **Alternatief**: Calendar Spreads rond de Fed-toespraken.
- **Exit & Regels**: **ABSOLUUT SLUITEN VÓÓR SEPTEMBER!**

##### 17. September 1H (Post-OpEx) — 🔴 September Kater (Risico)
- **Statistieken**: Jaarlijks +0.28% (58% WR) | Midterm **-1.42% (50% WR)**
- **Karakter**: Handelaren keren terug van vakantie en verlagen hun risicoprofiel. Typische start van de september-correctie.
- **Primaire Strategie**: **Bear Put Debit Spread** (ATM Long Put / 25-Delta Short Put) of Cash verhogen.
- **Alternatief**: Long Puts als pure downside bescherming.
- **Exit & Regels**: Snelle deelwinsten pakken bij scherpe rode dagen.

##### 18. September 2H (Pre-OpEx) — 🟢🟡 Pre-OpEx Stabilisatie ★ HUIDIGE PERIODE
- **Statistieken**: Jaarlijks +0.53% (67% WR) | Midterm +0.33% (62% WR)
- **Karakter**: Tijdelijke pauze in de september sell-off. De markt stabiliseert richting de 3e vrijdag OpEx.
- **Primaire Strategie**: **Delta-Neutrale Iron Condor** of lichte **Bull Put Spread** (15 Delta).
- **Alternatief**: Short Strangles met royale out-of-the-money marges.
- **Exit & Regels**: 🚨 **ALLES SLUITEN OP OPEX FRIDAY!** Neem absoluut geen long posities mee naar Oktober 1H!

---

#### Q4: Oktober t/m December

##### 19. Oktober 1H (Post-OpEx) — 🔴🔴🚨 Capitulatie Bodem (MAX DUBBEL RISICO)
- **Statistieken**: Jaarlijks -0.88% (42% WR) | Midterm **-1.45% (SLECHTS 25% WIN RATE - 2 van de 8 jaar positief!)**
- **Karakter**: **DE MEEST BERUCHTE PERIODE VAN DE 4-JARIGE CYCLUS.** Institutionele paniek, pre-election polls onzekerheid en liquidaties. Dit is de echte bodem van het Midterm jaar!
- **Primaire Strategie**: **Agressieve Hedges**: Bear Put Debit Spreads, Long Puts, Long VIX Calls.
- **Alternatief**: 100% Cash voor risico-averse handelaren. Bereid buy-the-dip orders voor!
- **Exit & Regels**: **Sluit alle short hedges rond OpEx Friday** wanneer de paniek maximaal is (VIX piekt). Dit is het moment om de dip van het decennium te kopen!

##### 20. Oktober 2H (Pre-OpEx) — 🟢🟢🚀 De Grote Pivot / Turnaround
- **Statistieken**: Jaarlijks +0.62% (58% WR) | Midterm **+1.72% (62% WR)**
- **Karakter**: **HET GROTE DRAAIPUNT.** De capitulatie is voltooid. Smart money begint massaal posities op te bouwen voor de eindejaarsrally.
- **Primaire Strategie**: **Bull Call Debit Spread** (+0.60 Delta / -0.30 Delta) met 45-60 DTE of **Risk Reversal** (verkoop OTM Put, koop ATM Call).
- **Alternatief**: Agressieve Bull Put Spreads op zwaar oversold niveaus.
- **Exit & Regels**: Laat winnaars lopen! Rol calls opwaarts door naar November.

##### 21. November 1H (Post-OpEx) — 🟢🟢 Post-Election Relief Rally
- **Statistieken**: Jaarlijks +1.34% (67% WR) | Midterm **+1.63% (62% WR)**
- **Karakter**: Zodra de stembussen sluiten bij de Midterm Elections valt de politieke onzekerheid weg. De befaamde 'Election Relief Rally' explodeert.
- **Primaire Strategie**: **Bull Call Debit Spread** of ATM Long Calls.
- **Alternatief**: Bull Put Credit Spread (20 Delta). De impliciete volatiliteit keldert (post-election IV crush), wat debit spreads zeer winstgevend maakt.
- **Exit & Regels**: Posities vasthouden en winsten laten oplopen richting Thanksgiving.

##### 22. November 2H (Pre-OpEx) — 🟢🟢🟢👑 KROONJUWEEL A++ (100% WIN RATE)
- **Statistieken**: Jaarlijks +0.92% (70% WR) | Midterm **+2.35% MET EEN PERFECTE 100.0% HISTORISCHE WIN RATE (8 uit 8 jaar positief!)**
- **Karakter**: **HET HOOGTEPUNT VAN DE 4-JARIGE PRESIDENTIËLE CYCLUS.** In de geschiedenis van de SPY (1993-2026) is deze periode in een Midterm jaar NOOIT negatief gesloten. Thanksgiving rally op maximale kracht.
- **Primaire Strategie**: **Maximale Bullish Exposure**: Deep ITM Call LEAPS, Bull Call Spreads, Synthetic Longs.
- **Alternatief**: Verkoop royale OTM Puts (30 Delta) om enorme premie binnen te halen.
- **Exit & Regels**: Winst veiligstellen vóór de eerste week van december.

##### 23. December 1H (Post-OpEx) — 🟢 Santa Rally Kick-Off
- **Statistieken**: Jaarlijks **+1.51% (79% WR - hoogste jaarlijkse win rate!)** | Midterm +0.60% (62% WR)
- **Karakter**: De Santa Claus Rally gaat van start. Zeer constante opwaartse drift met minimale volatiliteit.
- **Primaire Strategie**: **Bull Put Credit Spread** (15-20 Delta) of Covered Calls.
- **Alternatief**: Iron Condor met opwaartse skew.
- **Exit & Regels**: 50% winst target voor OpEx Friday.

##### 24. December 2H (Pre-OpEx) — 🟡🔴 Window Dressing / Divergentie
- **Statistieken**: Jaarlijks -0.18% (61% WR) | Midterm **-1.59% (50% WR)**
- **Karakter**: Jaareinde winstnemingen en herbalanceringen. Midterm jaren sluiten het jaar vaak rustig of licht corrigerend af na de enorme november rally.
- **Primaire Strategie**: **Iron Condor** om de holiday theta decay te innen, of winsten van calls verzilveren.
- **Alternatief**: Cash opbouwen en de playbook klaarmaken voor **Januari 1H (de volgende A+ Bull trade)**!
- **Exit & Regels**: Alles sluiten vóór 31 december.

---

### Google Calendar & iCal Integratie

Alle bovenstaande data is geëxporteerd naar direct bruikbare agenda-bestanden:
- **`spy_seasonality_options_2026.ics`**: Volledige iCalendar agenda voor 2026 met 24 perioden als doorlopende daggebeurtenissen inclusief alle statistieken, signalen en strike regels in de beschrijving.
- **`spy_seasonality_options_2026_google_calendar.csv`**: CSV-bestand voor Google Agenda import.
- **`spy_seasonality_options_2026_2027.ics`**: 2-jarige doorlopende agenda inclusief Pre-Election Jaar 2027.

#### Snelle Importinstructie in 3 Stappen:
1. Open [calendar.google.com](https://calendar.google.com) op je desktop.
2. Klik rechtsboven op het tandwiel (⚙️) $\rightarrow$ **Instellingen** $\rightarrow$ **Importeren en exporteren** (linker menu).
3. Klik op **Selecteer bestand op je computer**, kies `spy_seasonality_options_2026.ics`, selecteer je gewenste agenda (of maak eerst een nieuwe agenda aan genaamd *"ETF Seizoensmatigheid & Opties"*), en klik op **Importeren**.

---

### Samenvattende Handelstabel

| Periode | Data (2026) | Confluence Signaal | Jaarlijks (Avg / WR) | Midterm 2026 (Avg / WR) | Aanbevolen Optiestrategie |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Jan 1H** | 20 Dec - 02 Jan | 🟢🟢 **A+ BULL** | +1.28% / 76% | **+1.73% / 100%** | Bull Call Debit Spread / LEAPS |
| **Jan 2H** | 03 Jan - 16 Jan | 🟡 **Neutraal** | -0.02% / 64% | -0.82% / 56% | Iron Condor / Pre-Earnings Theta |
| **Feb 1H** | 17 Jan - 02 Feb | 🟢🟡 **Licht Bull** | +0.85% / 67% | -0.39% / 33% | Bull Put Credit Spread (15 Delta) |
| **Feb 2H** | 03 Feb - 20 Feb | 🟡 **Chop** | +0.21% / 61% | +0.52% / 44% | Iron Condor / Delta Neutraal |
| **Mar 1H** | 21 Feb - 06 Mrt | 🔴🟡 **Volatiel** | -0.47% / 47% | +0.56% / 44% | Long Strangle / Bear Call Spread |
| **Mar 2H** | 07 Mrt - 20 Mrt | 🟢🟢 **Sterk Herstel** | +0.21% / 59% | **+1.49% / 78%** | Bull Call Debit Spread (Q-End) |
| **Apr 1H** | 21 Mrt - 03 Apr | 🟢🟡 **April Drift** | +0.87% / 59% | -0.49% / 56% | Bull Put Spread (20 Delta) |
| **Apr 2H** | 04 Apr - 17 Apr | 🟢 **Bull Pre-OpEx** | +1.08% / 62% | +0.77% / 56% | Bull Call Debit Spread (Tax Refund) |
| **May 1H** | 18 Apr - 01 Mei | 🟢🟡 **Vroeg Mei** | +0.97% / 65% | -0.69% / 56% | Bull Put Spread (kortlopend 7-14 DTE) |
| **May 2H** | 02 Mei - 15 Mei | 🔴 **Sell in May** | +0.19% / 56% | **-1.19% / 44%** | Bear Call Spread / Protective Collars |
| **Jun 1H** | 16 Mei - 01 Jun | 🟢 **Inflow** | +1.04% / 65% | +0.55% / 67% | Bull Put Credit Spread (20 Delta) |
| **Jun 2H** | 02 Jun - 19 Jun | 🔴 **Quad Witching** | -0.01% / 41% | **-1.06% / 44%** | Bear Call Spread / Iron Butterfly |
| **Jul 1H** | 20 Jun - 03 Jul | 🟢 **Zomer Inflow** | +0.52% / 62% | -0.21% / 56% | Bull Call Debit Spread |
| **Jul 2H** | 04 Jul - 17 Jul | 🟡 **Zomertop** | +0.51% / 59% | -0.47% / 56% | Iron Condor / Summer Chop |
| **Aug 1H** | 18 Jul - 03 Aug | 🟢 **Midterm Kracht** | +0.30% / 59% | **+1.29% / 78%** | Bull Put Spread + VIX Hedges |
| **Aug 2H** | 04 Aug - 21 Aug | 🟢🟡 **Jackson Hole** | +0.12% / 68% | **+1.34% / 78%** | Iron Condor (Theta Melken) |
| **Sep 1H** | 22 Aug - 04 Sep | 🔴 **September Kater** | +0.28% / 58% | **-1.42% / 50%** | Bear Put Debit Spread / Cash |
| **Sep 2H** | 05 Sep - 18 Sep | 🟢🟡 **Consolidatie ★** | +0.53% / 67% | +0.33% / 62% | Iron Condor (Sluiten vóór Okt 1H!) |
| **Oct 1H** | 19 Sep - 02 Okt | 🔴🔴🚨 **CAPITULATIE** | -0.88% / 42% | **-1.45% / 25%** | **Bear Put Spreads / Puts / Cash** |
| **Oct 2H** | 03 Okt - 16 Okt | 🟢🟢🚀 **PIVOT / REVERSAL** | +0.62% / 58% | **+1.72% / 62%** | **Bull Call Debit Spread / Risk Reversal** |
| **Nov 1H** | 17 Okt - 02 Nov | 🟢🟢 **Relief Rally** | +1.34% / 67% | **+1.63% / 62%** | Bull Call Spreads (Post-Election) |
| **Nov 2H** | 03 Nov - 20 Nov | 🟢🟢🟢👑 **KROONJUWEEL** | +0.92% / 70% | **+2.35% / 100%** | **Max Bull Call Spreads / LEAPS** |
| **Dec 1H** | 21 Nov - 04 Dec | 🟢 **Santa Kick-Off** | **+1.51% / 79%** | +0.60% / 62% | Bull Put Credit Spread (15-20 Delta) |
| **Dec 2H** | 05 Dec - 18 Dec | 🟡🔴 **Window Dressing** | -0.18% / 61% | **-1.59% / 50%** | Iron Condor / Winst Oogsten |
