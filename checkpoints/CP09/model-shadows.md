# Dynamische Modellschatten – 28.10.2026

Direkter Nutzerauftrag trotz CP09-Featurefreeze: in die regulaere Mod einbauen,
NPCs und Pickups; Umgebung vorerst nicht als neuer Schattenwerfer.

## Umsetzung

- Neuer GL1-Schattenpass aus den bereits animierten Modell-Dreiecken. NPCs,
  aufhebbare Gegenstaende und angehaengte Waffen teilen eine Modell-Silhouette.
  Spieler/Viewmodel und die unsichtbaren Leichen-Kollisionsproxies sind ausgenommen.
- Zwei wiederverwendete 1024er Tiefentexturen: Modell-Silhouette und erster
  Empfaenger aus Sicht der Lichtquelle. Die Umgebung empfaengt und begrenzt die
  Projektion, erzeugt aber keine neuen eigenen Schatten.
- Staerkste erreichbare Karten-/dynamische Lichtquelle; zusaetzliche Sonnenpruefung
  unabhaengig von unvollstaendigen BSP-Lichtlisten. Bereiche ohne direkte Quelle
  erhalten eine dezente senkrechte Kontaktsilhouette als Ambient-Naeherung.
- Gefilterte Raender, Entfernungs- und Nebelausblendung. Kein fester schiefer
  Projektionsvektor wie beim alten experimentellen Verfahren.
- `Dynamic model shadows` in Allied Campaign Options, standardmaessig an.
  `r_acModelShadows` ist archiviert, wird ueber die vorhandene gemeinsame
  Renderer-Praeferenzverwaltung uebernommen und wirkt sofort. Defaults schaltet
  es ein. Aus bzw. fehlende OpenGL-Unterstuetzung verwendet den bisherigen
  `cg_shadows`-Modus.
- Keine Aenderung von Missionsskripten, Schadensregeln, Saveformat oder `game.dll`.
  Engine und `cgame.dll` muessen wegen der erweiterten internen Renderstruktur
  gemeinsam installiert werden. Die Deployment-Hilfe prueft beide Test-Hashes
  und sichert beide Dateien fuer den Rollback.

## Native Pruefung

`tools/test_model_shadows.py model-shadows-r4`:

| Kontext | Ausgangspunkt | Ergebnis |
| --- | --- | --- |
| AA | m2l1, kontrollierter NPC und Pickup auf Schnee | Schatten/Animation, Save/Load, vid_restart, Optionsschalter bestanden |
| SH | Kopie des aktuellen t1l3-Spielstands, Bruecke bei Nacht | gleiche Pruefungen bestanden |
| BT | isolierter e2l2-Fussgaenger-Spielstand, unebener Weg | gleiche Pruefungen bestanden |

18 Screenshots einschliesslich Aus/An-Vergleich, veraenderter Pose und
Pickup-Drehung, geladenem Save, Renderer-Neustart und Menue liegen unter
`generated-local/CP09/model-shadows-r4/`. Stichproben visuell geprueft; der
Schnee-Vergleich wurde zusaetzlich anhand veraenderter Bodenpixel kontrolliert.
Der alte Schattenmodus war fuer den Vergleich vollstaendig ausgeschaltet.
Ein zusaetzlicher Diagnose-Durchlauf in m3l2 pruefte Kartenlichtquellen.

`tools/test_model_shadow_stress.py model-shadows-uhd-r2`:
3840x2160, HUD 1.66, 16 NPCs plus acht Pickups, 24 aktive Schatten.
Synchronisierte Zeit des zusaetzlichen Schattenpasses auf diesem Rechner
ueberwiegend 3–4 ms, maximal 5 ms; die einfachen Szenen lagen bei 0–2 ms
(Millisekundenmessung). Das ist **keine** Gesamt-Frametime oder Aussage ueber
andere GPUs. Geometrieerfassung und kompletter Spielbetrieb sind nicht in
dieser Passmessung enthalten.

OpenGL-Pruefung: kein Fehler innerhalb des neuen Passes. Fehler 1281 tritt in
diesem Renderer bereits vor dem Pass und auch bei deaktiviertem neuen Verfahren
auf; separat protokolliert und nicht als neuer Schattenfehler gewertet.

`tools/test_options_layout.py model-shadows-options-r1 --packages-report
generated-local/CP09/model-shadows-r4/result.json`:
AA 1920x1080, SH 1280x960, BT 3440x1440; alle Controls, Defaults, Rueckkehr,
10%-Flinchschritte, unveraenderter Menue-Rahmen bei Schriftgroessenwechsel und
Ueberlappungsfreiheit bestanden. Alle 531 persoenlichen Profildateien blieben
waehrend der geprueften Laeufe hashgleich.

Getestete Binaerdateien:

- Engine: `ce0d40c715a542b74e19d113bf0da561a18db6cfc55003a87a2b09320d3b9f4d`
- Cgame: `af9d79741591fe37e9440995e4b8ba06e6b41dc0b25402a1c46d27e247217d32`
- Unveraendertes Game: `4fbf734baf683e299d8cfa9c79a72305090289211144a1f914532310f5d0cc4f`

## Grenzen

Dies ist Modell-Shadow-Mapping mit einer dominanten Lichtquelle, kein kompletter
Neubau der Beleuchtung. Keine Selbstverschattung einzelner Koerperteile, keine
neuen Weltgeometrie-Schatten und keine transparenten Empfaenger. Erfasst wird
die fuer den jeweiligen Kamerablick eingereichte Geometrie; nicht eingereichte
Modelle/Blocker ausserhalb des Sichtbarkeitsbereichs koennen fehlen.

Die Ressourcen sind fest begrenzt: maximal 128 erfasste/64 projizierte Modelle,
1400 Einheiten Reichweite mit Fade ab 900, 524288 Dreiecksvertices und 8192
Batches. Ein Geometrie-Ueberlauf laesst den Pass dieses Bildes aus. Die
Ambient-Kontaktsilhouette ist bewusst eine Naeherung. GL2 und andere GPUs sind
damit nicht abgenommen. Natuerlicher Kampagnendurchlauf und CP09-Gesamtabnahme
bleiben offen.

Die regulaere Installation wird nach dem Source-Commit mit
`tools/deploy_cp09_engine.py model-shadows-r4 --options-layout --cgame`
gegen die geprueften Hashes aktualisiert. Der lokale Deployment-Bericht und
Rollback liegen im selben ignorierten Ergebnisordner.
