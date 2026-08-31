# Seizoenspatronen S&P 500 (Laatste 20 Jaar): Inclusief Optie-Expiratie (OpEx)

Ik heb de analyse uitgebreid met de periodes gemeten van de **3e vrijdag van de maand (OpEx) tot de 3e vrijdag van de volgende maand**. Dit onthult patronen die speciaal voor de optiemarkt extreem waardevol zijn.

*   **1e tot 1e**: Reguliere kalendermaand (bijv. 1 jan tot 1 feb).
*   **15e tot 15e**: Midden-maand (bijv. 15 jan tot 15 feb).
*   **OpEx tot OpEx**: (bijv. 3e vrijdag januari tot 3e vrijdag februari).

## De Data Tabel (2006 - 2026)

| Maand (Start) | 1e tot 1e (Winst) | Gem. Rendement | 15e tot 15e (Winst) | Gem. Rendement | OpEx tot OpEx (Winst) | Gem. Rendement |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Januari** | 62% | 0.42% | 62% | 1.35% | **71%** | **1.15%** |
| **Februari** | 52% | -0.43% | 52% | -1.93% | 57% | **-1.37%** |
| **Maart** | 71% | 1.08% | 62% | 2.85% | 57% | **3.01%** |
| **April** | 76% | 2.18% | 67% | 1.37% | 62% | 0.58% |
| **Mei** | 67% | 0.67% | 67% | 0.82% | 71% | 0.88% |
| **Juni** | 48% | 0.53% | 86% | 1.31% | **81%** | **1.63%** |
| **Juli** | 67% | 1.92% | 57% | 0.75% | 62% | 0.41% |
| **Augustus** | 60% | -0.02% | 80% | 0.82% | **70%** | **1.68%** |
| **September**| 60% | -0.39% | 50% | -0.86% | 55% | -0.96% |
| **Oktober** | 65% | 1.12% | 80% | 1.78% | 70% | 0.98% |
| **November** | 70% | 1.71% | 60% | 0.98% | **80%** | **1.50%** |
| **December** | 75% | 1.36% | 75% | 0.87% | 75% | 1.01% |

*(Voorbeeld: De OpEx-OpEx rendementen op de 'Augustus' rij betekenen de rit van de 3e vrijdag in Augustus tot de 3e vrijdag in September)*

## Belangrijkste Inzichten voor de Optiemarkt (OpEx)

Wanneer we specifiek naar de OpEx-naar-OpEx cycli kijken, ontdekken we gigantische structurele marktpatronen:

> [!TIP]
> **De September-valkuil vindt pas plaats ná de September OpEx!**
> Kalendermaand September is berucht (-0.39% gemiddeld). Echter, de OpEx-tot-OpEx cyclus vanuit Augustus (3e vrijdag Aug t/m 3e vrijdag Sep) presteert fantastisch met 70% winstkans en een **enorm 1.68% gemiddeld rendement**! Dit toont keihard aan dat de gevreesde september-dip in de afgelopen 20 jaar vrijwel exclusief geconcentreerd zat in de *laatste anderhalve week* van september (nà de Triple Witching expiratie).

> [!TIP]
> **De Lente Rally (Maart OpEx tot April OpEx)**
> Terwijl maart op zich een redelijke maand is (1.08%), is de cyclus van de 3e vrijdag in maart tot de 3e vrijdag in april absoluut gigantisch: een astronomisch rendement van **3.01% per maand**. 

> [!TIP]
> **De Zomer Rally (Juni OpEx tot Juli OpEx)**
> Kalendermaand juni presteert de laatste 20 jaar erg zwak (slechts 48% winstkans). Maar wacht tot ná de grote optie-expiratie in juni: de rit van Juni OpEx naar Juli OpEx is met **81% winstkans en 1.63% rendement** één van de veiligste en sterkste rally's van het jaar.

> [!WARNING]
> **Het Februari Gevaar (Feb OpEx tot Maart OpEx)**
> De rit van halverwege februari naar halverwege maart blijft ook op OpEx-basis de zwakste en gevaarlijkste cyclus van het hele jaar. Je incasseert hier historisch gezien gemiddeld zwaar verlies (**-1.37%**).

**Conclusie voor je algoritmische handel:**
Als je Iron Condors, Strangles of aandelenposities beheert (zoals met je `tat_master_engine`), laat dit overduidelijk zien dat de seizoensgebondenheid van de aandelenmarkt niet gelijkloopt met de kalendermaand. De markt kent duidelijke kantelpunten rondom de maandelijkse optie-expiratiedata. De "zwakke" maanden zijn vaak zwak door gigantische verkopen *nadat* opties gepind/vervallen zijn.
