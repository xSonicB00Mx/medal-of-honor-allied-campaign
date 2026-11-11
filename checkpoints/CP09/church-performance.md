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

## Rueckbau auf ausdruecklichen Nutzerauftrag

Nach der Diagnose hat der Nutzer alle drei nur testweise wieder eingebauten
Erweiterungen abgelehnt. Lokale Modellbeleuchtung, verdeckte dynamische Lichter
und Lit Soft Particles sind vollstaendig entfernt: Rendererimplementierung,
Aufrufe, temporaere Partikelkennzeichnung, Build-Eintrag und Optionsseite.
Urspruengliche Licht-/Partikelpfade sind wiederhergestellt; TAA, verstarkte
Objektbewegungsunschaerfe, Modellschatten und AO bleiben erhalten. Das passende
cgame wird wegen der entfernten rendererinternen Partikelkennung mitgebaut.
Das Spiel-/Speicherformat aendert sich nicht.

`church-effects-removed` prueft den aktuellen Save erneut mit UHD, TAA,
Blur 50%, Schatten und AO. Nach demselben Weg werden 18 Sekunden einschliesslich
der Kampfphase erfasst: 2115 Bilder, Median 8 ms, P95 9 ms, Maximum 16 ms.
Anschliessend sind Speichern und Laden derselben Kopie erfolgreich. Alle 595
persoenlichen Profildateien bleiben hashgleich. Der im ersten Abschnitt
beschriebene Optimierungsansatz ist durch den gewuenschten Rueckbau ersetzt.

Native AA-UHD-, Spearhead- und Breakthrough-Pruefungen der finalen Engine
(`remove-lighting-aa-release`, `remove-lighting-sh-release`,
`remove-lighting-bt-release`) bestehen Waffenbewegung/Feuer/Nachladen,
Objektbewegungsvektoren, unveraendertes HUD, Save/Load, Grafikneustart sowie
TAA-/Blur-Optionsbedienung. Keine Temporal-GL-Fehler oder Pufferueberlaeufe.
Die TAA-/Blur-, Schatten- und AO-Implementierungen sind gegen den zuvor
installierten Stand bytegleich; die urspruenglichen Licht-/Modell-/Partikelpfade
wurden zusaetzlich gegen den Stand vor Einfuehrung der drei Effekte verglichen.

`remove-lighting-ui-release` besteht die echte Optionsnavigation ohne Lighting-
Button, bei weiterhin erreichbarer AA-&-Motion-Seite, Grafik-/Seitenverhaeltnis-,
FOV- und Kartenwechsel. Die bereinigte Optionsseite wurde visuell geprueft.

Nach Entfernen des letzten ungenutzten Partikelpuffers wurde die finale Engine
neu gebaut und erneut in allen drei Spielen sowie an der Kirche getestet.
`church-removal-release`: 2109 Bilder, Median 8 ms, P95 9 ms, einzelner maximaler
Frame 27 ms. Der anhaltende Einbruch ist ausgeblieben; diese Messung behauptet
keine absolute Freiheit von einzelnen Frame-Spitzen. Save/Load bestanden.

Finale Engine: `f567924a3a3dbb671056a6136dc7a3d43bd6744e058622be269cf7f1eed1ee47`.
Passendes cgame: `cdb016b9672275d61f0c0a051ed5e544ed9cc9b3b0b925ee59a89d753e0906f1`.

## Installation

Quellen-Commit `19ddd629e938e2cefee93e8e0d4d87af6ac26fd7` ist in **CP08-r1 und
CP09-r1 installiert**, einschliesslich passendem cgame und den drei bereinigten
Optionspaketen. Die einzige Paketquelle der entfernten Optionsseite wurde in
allen Kampagnen ersetzt. `game.dll`, Inhalts-/Kunstpakete und persoenliche
Einstellungen bleiben unveraendert.

`generated-local/CP09/remove-lighting-aa-release/deployment.json` bestaetigt
9086/9090 Runtime-Dateien, 9072 Originaldateien und 595 hashgleiche persoenliche
Dateien. Die ersetzten Moddateien liegen im zugehoerigen `rollback/`.
Keine persoenliche Gesamtabnahme und kein Merge.
