# Lokale Modellbeleuchtung, dynamische Lichter und Partikel

## Erneute Bereitstellung zur Analyse, 30.10.2026

Der Nutzer hat den Rueckbau widerrufen und die drei Erweiterungen fuer eigene
Analysen erneut beauftragt. Wiederhergestellt wird exakt die zuletzt korrigierte
Fassung `406a0616` (Implementierung `83fbf55a`), einschliesslich des reparierten
Waffenlichtpfads, der drei Schalter und der Seite Lighting & Particles.
Engine `101d26ba` und cgame `0d2d018e` stammen bytegleich aus der gesicherten,
bereits geprueften Fassung; keine erneute Kompilierung behauptet. Keine neue
Featureabnahme und keine Veraenderung persoenlicher Spielstaende.

## Zwischenzeitlicher Rueckbau (historisch)

**Zwischenzeitlich zurueckgenommen auf Nutzerauftrag vom 30.10.2026.** Die drei Erweiterungen
einschliesslich Optionsseite und ihrer spaeteren Waffenlicht-Korrektur wurden
vollstaendig aus Code und Spielmenues entfernt. Code, CMake, UI und Werkzeuge
entsprechen wieder `a9671da0`, dem Stand vor ihrer Einfuehrung. Die folgenden
Abschnitte dokumentieren diesen zwischenzeitlichen Rueckbau. Der erneute
Nutzerauftrag oben stellt die anschliessend beschriebene Implementierung wieder her.

Rueckbau installiert: gesicherte Engine `1f269954` (Source `88550606`),
cgame `af9d7974` und die drei damaligen Optionspakete in CP08-r1/CP09-r1
bytegleich wiederhergestellt. Native AA/SH/BT-Pruefung mit Save/Load,
Grafikneustart, Schatten und Optionslayout bestanden (`remove-lighting-test`).
9086/9090 Runtime-Dateien und 9072 Originaldateien verifiziert; alle Saves und
557 von 559 Profildateien unveraendert. In den verbleibenden zwei cfg-Dateien
wurden ausschliesslich die Eintraege der entfernten Optionen geloescht.
Nachweis und Transaktionssicherung: `generated-local/CP09/remove-lighting/`.

Direkter Nutzerauftrag vom 29.10.2026: Grafikvorschlaege 1, 4 und 5 in die
regulaere Mod integrieren. Kein separater Spielstand erforderlich.

## Korrektur 30.10.2026: Fehlendes Waffenlicht

Der Nutzer meldete fehlendes Umgebungslicht beim Schiessen. Reproduktion in
einer getrennten Kopie seines neuesten AA-Spielstands: m3l2, Thompson.
Die urspruenglichen Tests unten verwendeten gesetzte Dauerlichter und prueften
nicht den vollstaendigen Waffenablauf. Sie waren fuer diese Regression nicht
ausreichend; ihre erfolgreiche Ausfuehrung war keine visuelle Gesamtabnahme.

Ursachen und Korrektur:

- Der optimierte Vertex-Lichtpfad rief nur die alte Sphere/Grid-Funktion auf.
  Die neuen Beitraege liefen allein durch `ComputeColors`, waehrend der alte
  dynamische Beitrag bereits abgeschaltet war. Dadurch fehlte das Waffenlicht
  auf vielen normalen Ein-Pass-Modellen vollstaendig. Der schnelle Zeichenpfad
  nutzt nun dieselbe Farbberechnung wie der generische Pfad. Er behaelt seine
  optimierte Textur-/Array-Ausgabe; keine globale Abschaltung der Optimierung.
- Derselbe fehlende Aufruf betraf die lokalen Lichtgitter-Proben. Diese werden
  jetzt auch auf den zuvor ausgelassenen Modellen ausgefuehrt.
- Der neue gemeinsame Lightmap-Distanzabfall schwaechte kleine Waffenlichter
  auf Modellen/Rauch zusaetzlich ab. Die bisherigen modellspezifischen
  Einflussbereiche und Sphere/Grid-/Static-Lichtformeln gelten wieder; die
  Sichtbarkeit wird weiterhin am tatsaechlichen Vertex geprueft. Vorhanden
  beleuchteter Rauch verwendet wieder seinen urspruenglichen Distanzabfall.
- Welt-Lightmaps, Verdeckung durch BSP/bewegliche Brushes, Schadenslogik,
  Waffenparameter und Speicherformat werden in dieser Korrektur nicht geaendert.

Neue Nachweise: `test_ac_weapon_lighting.py` feuert die echte Waffe und erfasst
26 Frames. `test_ac_muzzle_response.py` reproduziert anschliessend die gemessene
Thompson-Lichtquelle (Radius 150, RGB .25/.20/.15) mit fester Kamera. So werden
Rueckstoss und zufaellige Partikel nicht mit einer Lichtkorrektur verwechselt.
Ein versuchter Pause-Vergleich war nicht bildstabil und wurde verworfen.

| Statische Bildprobe | Vor Korrektur, Verdeckung an | Nach Korrektur | Originallicht ohne Verdeckung |
|---|---:|---:|---:|
| Kopf | +0,03 | +19,76 | +18,84 |
| Oberkoerper | +0,02 | +7,33 | +5,81 |
| Zweiter Koerper | 0,00 | +10,25 | +8,34 |

Werte: mittlerer RGB-Zuwachs in festen Bildausschnitten (0..255), keine
physikalischen Luminanzen. Bei ausgeschalteter Quelle sind diese Ausschnitte
pixelgleich. Optimierter und erzwungener generischer Pfad liefern identische
Lichtwerte (`muzzle-final`, `muzzle-generic-final`, `parity.json`). Die zuvor
installierte Engine scheitert an diesen Kriterien (`muzzle-before-visible`).
Das echte Thompson-Feuer ist zusaetzlich in `fire-save-final` sichtbar geprueft.

Die lokale Lichtgitter-Korrektur ist im gleichmaessig beleuchteten Bocage-
Ausschnitt weiterhin sehr klein (unter 0,03 RGB-Stufen im Mittel). Das ist
keine neue GI und dort kein grosser sichtbarer Grafiksprung. Soft Particles
verbessern vorrangig Schnittkanten von Rauch/Staub mit Geometrie; sie veraendern
nicht grundsaetzlich die Beleuchtung der ganzen Szene.

Weitere Regression mit Engine
`101d26baac78ab0adca58963f30eff31707f8c9471c3e1a37121005d8c647ec9`:

- `fire-interior-final`: echtes MP40-Feuer in m2l2a, 26 Frames.
- `muzzle-walls-final --fast`: verdeckte Decke 0 fehlerhafte Lichtpixel,
  sichtbare Bodenprobe weiterhin 149.919 beleuchtete Pixel.
- `muzzle-door-final`: geschlossene Drehtuer 0 Lichtpixel, offen 14.300.
- `muzzle-aa-release --uhd`, `muzzle-sh-final`, `muzzle-bt-final`: je acht
  Bilder, Save/Load, Grafikneustart, native Optionsschalter und Defaults;
  persoenliche 555 Dateien jeweils hashgleich.
- `muzzle-stress-final`: UHD, 16 NPCs/acht Pickups/zwei Lichter mit AO/Schatten.
  249 Frames je Zustand: Zusatzbeleuchtung aus 6 ms Median/7 ms P95,
  an 15 ms Median/16 ms P95/20 ms Maximum. CPU-Wandzeit einschliesslich
  Treiberwartezeit. Der zuvor dokumentierte niedrigere Aufwand von 10 ms
  galt fuer die fehlerhafte Fassung, die viele Modelle nicht beleuchtete.

Korrektur aus Quellen-Commit `83fbf55abac2c52400202b16ffcfe9404fd0de56`
mit `tools/deploy_cp09_engine.py muzzle-aa-release` in CP08-r1 und CP09-r1
installiert. 9.086/9.090 Runtime-Dateien und 9.072 Originaldateien verifiziert;
alle 555 persoenlichen Profildateien hashgleich. Nur die Engine ersetzt,
game/cgame/Assets unveraendert. Nachweis und Rollback unter
`generated-local/CP09/muzzle-aa-release/`. Persoenliche Einstellung
`r_acDynamicLighting=0` bewusst beibehalten; der Nutzer kann die korrigierte
Option wieder einschalten. Kein Merge, CP09-Gesamtabnahme weiterhin offen.

Die folgenden Abschnitte dokumentieren die erste Lieferung vom 29.10.

## Umsetzung

- **Lokale Modellbeleuchtung:** sechs durch die Levelkollision begrenzte
  Proben des vorhandenen, trilinear interpolierten Lichtgitters. Die lokalen
  Farbgradienten werden anhand der animierten Modellnormalen rekonstruiert.
  Angehaengte Waffen teilen die Probe ihres Elternmodells. Die Korrektur bleibt
  relativ zur bisherigen Beleuchtung begrenzt; gleichmaessige Bereiche,
  Kartenlichtmaps, selbstleuchtende Modelle und reine Menueansichten behalten
  ihre bestehende Beleuchtung. Das ist eine Lichtgitter-Naeherung, keine neue
  Echtzeit-GI oder automatisch neu berechnete Kartenbeleuchtung.
- **Dynamische Lichter:** vorhandene Waffen-/Explosionslichter pruefen die
  Sichtbarkeit zur beleuchteten Weltflaeche bzw. zum Modellvertex. Solide
  BSP-/Terrainkollision und aktuell positionierte/gedrehte Brushmodelle
  blockieren die Strahlen. Urspruengliche, modellspezifische Lichtantwort;
  keine doppelte Addition aus dem alten Modelllichtpfad. Empfaengerproben von
  Flaechenlichtmaps werden fuer den Sichtbarkeitstest auf ihre sichtbare Ebene
  gelegt: einige Originalproben lagen acht Einheiten hinter der Wand.
  Die neue Option verwendet auch bei gesetztem `r_fastdlights` den genaueren
  Lichtmappfad. Die Quelllichtmaps bleiben fuer sofortiges Umschalten im RAM.
- **Diffuse Partikel:** Rauch, Staub, Dampf und Blutnebel erhalten lokale
  Beleuchtung an ihrem festen Mittelpunkt sowie erreichbares dynamisches
  Licht. Bereits im Client beleuchtete Partikel werden markiert und nicht
  nochmals abgedunkelt. Ein GLSL-Pass blendet Schnittkanten zu undurchsichtiger
  Geometrie ueber sechs Welteinheiten aus. Texturlagen, Alpha und Kartennebel
  bleiben beruecksichtigt. Feuer, Funken, Leuchtspuren, Glas, HUD und dauerhafte
  Blutmarkierungen gehoeren nicht zu diesem Pass.
- Exakte identische Lichtstrahlen werden nur innerhalb derselben Szene
  wiederverwendet. Keine Positionsquantisierung, keine Ergebnisse aus alten
  Bildern; bewegliche Brushmodelle erhalten zusaetzlich eine Welt-AABB-Vorpruefung.
- Neue Seite **Lighting & Particles**, erreichbar ueber **Lighting...** in
  Allied Campaign Options. `Local model lighting`, `Occluded dynamic lights`
  und `Lit soft particles` sind einzeln und sofort schaltbar, standardmaessig an.
  Die archivierten `r_acModelLighting`, `r_acDynamicLighting`, `r_acSoftParticles`
  werden vom bestehenden gemeinsamen `r_`-Praeferenzpfad uebernommen.
- Renderer und passendes `cgame.dll`; keine Aenderung an `game.dll`, Schaden,
  Missionsskripten, Fortschritt oder Speicherformat. Das neue Client-Renderflag
  erweitert keine Struktur und wird nicht als Spielzustand gespeichert.

## Technischer Nachweis

Finale Engine SHA-256:
`d0eea6b9b0955b0dac59a2a5bb03477de6f17a47b9997252ba35eaa9a3bb5b1f`.
Client SHA-256:
`0d2d018ec192206013873a88dafb16a0fceeb0c4f15dbaef8af63005240c7e27`.

Lokale Berichte und Bilder liegen unter `generated-local/CP09/` und bleiben
wegen Originalinhalten und Spielstandkopien ausserhalb von Git.

| Pruefung | Ergebnis / Bericht |
|---|---|
| AA, SH, BT | `lighting-release`, `lighting-sh-final`, `lighting-bt-final`: jeweils acht Bilder, aktivierte Proben/Partikel/Verdeckung, Save/Load und Grafikneustart |
| Native Optionen | Drei Checkboxen schalten auf 0; tatsaechlicher Defaults-Button setzt alle auf 1; getrennte Konfigurationsdateien geprueft |
| UHD | `lighting-uhd-final`: 3840x2160, gleiche Spiel-/Optionspruefungen, kein GL-Fehler im kombinierten Schatten-/AO-Pfad |
| Deckendurchschlag | `lighting-walls-final`: auch mit altem Fast-Modus vorher 659.115 fehlerhaft beleuchtete Pixel, neu 0; sichtbarer Boden weiterhin beleuchtet (149.919 Pixel) |
| Bewegliche Tuer | `lighting-door-final`: Bodenprobe ohne animierte Figuren, geschlossen vorher 14.300 Lichtpixel / neu 0; nach Drehung offen 14.300 Lichtpixel |
| Partikel-GPU | `lighting-particle-gpu-r2`: 324 Kombinationen aus Tiefe, Sichtfeld, Viewport, Abstand und Texturlagen; zusaetzlich fuenf Nebel-/Hintergrundpruefungen |
| Normandy-Boot | `lighting-boat-final`: fuenf Ansichten, AO/Schatten getrennt und kombiniert, 20 Bilder, kein GL-Fehler |
| UHD-Last | `lighting-stress-r3`: 16 NPCs, acht Pickups, zwei Lichter, Dampf, Schatten und AO |

UHD-Last auf diesem Rechner (RTX 4090, NVIDIA 610.88): `com_speeds`-CPU-Wandzeit
einschliesslich Treiberwartezeit, **keine** GPU-Query- oder Present-Messung.

| Neue Effekte | Frames | Median | P95 | P99 | Maximum |
|---|---:|---:|---:|---:|---:|
| Aus | 249 | 6 ms | 7 ms | 7 ms | 9 ms |
| An | 249 | 10 ms | 11 ms | 11 ms | 13 ms |

Vor Optimierung lag derselbe Aufbau bei 15 ms Median / 16 ms P95. Vorabtests
fanden ausserdem einen ungueltigen Fontnamen, die nur fuer zwei Einheiten
geeignete alte Texture-Unit-Hilfsfunktion und hinter Empfaengerflaechen liegende
Lichtmap-Proben. Diese Fehler sind vor der finalen Testreihe korrigiert.
Reine Testharness-Probleme (Konfigurationspfad, nachgestellte UI-Befehle,
fehlende Testskript-Freigabe und bewegte NPCs in einer Pixelprobe) wurden
ebenfalls korrigiert; fehlgeschlagene Laeufe gelten nicht als Abnahmen.

## Grenzen

- Verdeckung folgt der soliden Welt-/Brushkollision. Alpha-Lochmuster und
  rein dekorative Meshes ohne entsprechende Kollision sind keine exakten
  Lichtblocker. Modelllicht bleibt vertexbasiert, Weltlicht an die vorhandene
  Lichtmapaufloesung gebunden. Kein vollstaendiger neuer Schattenwurf aller
  Umgebungsobjekte durch jede Explosion.
- Es werden die bereits vom Spiel erzeugten dynamischen Lichter verwendet;
  der Auftrag aendert keine Waffenskripte oder Explosionsradien.
- Soft Particles verwenden die Tiefe sichtbarer undurchsichtiger Geometrie;
  transparente Oberflaechen und Portalansichten sind ausgenommen. Ohne die
  benoetigten GL-Funktionen bleibt die bisherige Partikeldarstellung erhalten.
- Geprueft ist GL1 auf diesem Rechner, nicht GL2 oder eine breite GPU-Matrix.
  Kein vollstaendiger natuerlicher Kampagnendurchlauf und keine CP09-Gesamtabnahme.
- Der bereits vor dieser Aenderung dokumentierte GL1-Fehler 1281 erscheint in
  SH/BT weiterhin vor den Zusatzpaessen bzw. bei deaktiviertem Schattenpass.
  Die separat gemessenen Schatten-/AO-Paesse und der GPU-Partikeltest melden 0.

## Installation

Engine, passendes cgame und die beiden Optionslayouts sind in **CP08-r1 und
CP09-r1 installiert**, Quellen-Commit `7d32ce0620ed918622cf6cb14a6bfdf6d885033c`.
Der normale Spielstarter verwendet damit die neuen, standardmaessig aktiven
Effekte. `game.dll`, Kunst-/Inhaltspakete und Speicherformat bleiben unveraendert.

`tools/deploy_cp09_engine.py lighting-release --options-layout --cgame`
verifizierte 9.086/9.090 Runtime-Dateien sowie 9.072 Originaldateien.
Alle 555 persoenlichen Profildateien blieben hashgleich. Der lokale
Installationsnachweis liegt in `generated-local/CP09/lighting-release/deployment.json`,
die ersetzten Moddateien liegen dort unter `rollback/`.

Kein Merge, keine Vorwegnahme der persoenlichen Kampagnenabnahme.
