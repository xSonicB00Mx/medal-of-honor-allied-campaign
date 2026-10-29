# Lokale Modellbeleuchtung, dynamische Lichter und Partikel

Direkter Nutzerauftrag vom 29.10.2026: Grafikvorschlaege 1, 4 und 5 in die
regulaere Mod integrieren. Kein separater Spielstand erforderlich.

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
  blockieren die Strahlen. Gemeinsamer begrenzter quadratischer Distanzabfall;
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

Installation erfolgt ueber `tools/deploy_cp09_engine.py lighting-release
--options-layout --cgame`, mit Hashpruefung, Sicherung der ersetzten Moddateien
und Rueckbau bei Fehlern. Installationsnachweis wird nach erfolgtem Kopieren
ergänzt. Originalinstallation und persoenliches Profil bleiben geschuetzt.
