# AA m3l3: Performanceeinbruch vor der Kirche (31.10.2026)

Nutzerauftrag: Ursache im aktuellen Spielstand untersuchen. Keine Aenderung der
installierten Engine, Einstellungen oder Spielstaende vorgenommen.

## Befund

Die CPU-Verdeckungspruefungen von `r_acDynamicLighting` (UI: **Occluded dynamic
lights**) verursachen den beobachteten Einbruch, sobald die dynamische Lichtquelle
an der Kirche aktiv ist. Die installierte Engine ist `6386c6f4`.

Eine isolierte Kopie des aktuellen m3l3-Quicksaves wurde mit den gespeicherten
UHD-Einstellungen, TAA und Object Motion Blur 50% gestartet. Sechs Sekunden
Vorwaertsbewegung fuehren vor die Kirche. Godmode verhindert den Tod waehrend
der Messung; Gegner und Missionsereignisse bleiben aktiv. Der erste Versuch
mit notarget war als Reproduktion ungeeignet: ohne Kampflicht trat der Einbruch
an der untersuchten Stelle nicht auf.

`church-lighting-isolation` zeigt bei aktivem Licht 23--25 ms typische Bildzeit,
mit ausgeschalteter Lichtverdeckung 9--10 ms. Andere Einzelabschaltungen von
TAA/Blur, Modellschatten, AO oder lokaler Modellbeleuchtung beseitigen den
Einbruch nicht. Die Lichtdiagnose meldet zeitweise 215000--244000 Sichttests pro
Sekundenintervall. Die dort geprueften Lichtwege werden als blockiert verworfen.

Ein weiterer Versuch laedt denselben Save fuer jede Variante neu und laeuft
denselben Weg. `church-paired-confirm`:

| Variante | Median | P95 | Maximum |
| --- | ---: | ---: | ---: |
| Alle aktuellen Effekte | 10 ms | 19 ms | 26 ms |
| Nur Occluded dynamic lights aus | 9 ms | 10 ms | 13 ms |
| Nur Lit Soft Particles aus | 17 ms | 25 ms | 26 ms |

Kampfereignisse starten nicht in jedem Durchlauf zum exakt gleichen Zeitpunkt.
Darum sind Gesamtmediane ueber teilweise lichtfreie Zeitfenster nicht als
exakter Leistungsvergleich zu interpretieren. Die wiederholten Live-Umschaltungen
und die Korrelation mit den Trace-Zahlen grenzen den teuren Pfad ein.
Gemessen wird CPU-Wandzeit inklusive Treiberwartezeit, keine GPU-Zeitmessung.

Die protokollierte Lichtquelle liegt etwa bei `(2433, -2127, -176)`, Radius 140.
Es ist damit kein allgemeiner UHD-/TAA-Einbruch. Die Missions-/Serverzeiten
bleiben klein; die Zusatzzeit liegt auf der Client-/Renderingseite.

## Codeursache und naechster Fix

`R_ACLightVisible` in `code/renderergl1/tr_ac_lighting.c` fuehrt pro Empfaenger
Kollisionstests gegen die Welt und gegebenenfalls Brushmodelle aus; der Cache
gilt nur fuer identische Koordinaten in derselben Szene. Der Weltlichtpfad in
`tr_shade.c` testet die Sichtbarkeit bereits im Vertex-Durchlauf, bevor er
Dreiecke ausserhalb des Lichtbereichs verwirft. Dadurch wird auch fuer spaeter
unbenutzte Vertices teure Arbeit ausgefuehrt.

Ein Fix muss die relevanten beleuchteten Dreiecke zuerst bestimmen und nur deren
benoetigte Vertices auf Verdeckung pruefen. Dabei nicht einfach einzelne
ausserhalb liegende Eckpunkte verwerfen: Dreiecke koennen den Lichtbereich
ueberspannen, obwohl ihre Eckpunkte ausserhalb liegen. Modell-/Partikelpfade
ebenfalls gezielt profilieren. Dies ist ein begruendeter Optimierungsansatz,
noch keine implementierte oder abgenommene Korrektur.

## Nachweise

- Werkzeug: `tools/diagnose_church_performance.py`, Optionen `--lighting`, `--paired`.
- Ergebnisse/Bilder: `generated-local/CP09/church-combat-near`,
  `church-lighting-isolation`, `church-paired-confirm`.
- Konsolenlogs: entsprechende isolierte Ordner unter `profiles-local/CP09`.
- Alle 595 persoenlichen Profildateien nach jedem Lauf hashgleich.
- Kein natuerlicher Gesamtdurchlauf, keine Runtime-Aenderung, kein Merge.
