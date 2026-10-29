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

Die regulaeren Installationen CP08-r1 und CP09-r1 wurden mit
`tools/deploy_cp09_engine.py model-shadows-r4 --options-layout --cgame`
aktualisiert. Source-Commit: `a9f7c4862acff21b1c72b6fda6d09f525368a6af`.
Danach 9086 bzw. 9090 Laufzeitdateien gegen die Manifeste verifiziert;
9072 Originaldateien und alle 531 persoenlichen Profildateien hashgleich.
Der lokale Deployment-Bericht und Rollback liegen im selben ignorierten
Ergebnisordner. Der Source-Commit wurde auf `codex/cp09-regression` gepusht
und durch einen frisch gelesenen Remote-SHA bestaetigt; kein Merge nach main.

## 29.10.2026: Blickwinkelabhaengige Kontakte auf dem Normandy-Boot

Nutzerbeobachtung in AA `m3l1a`: Schatten veraendern sich beim Umschauen.
Der Modellschatten-Shader verwendete `fwidth(p.z)` in Kamerapixeln fuer
Empfaengertoleranz und Tiefenbias. Damit aenderte ein Kameraschwenk die
Akzeptanz derselben Kontaktstelle trotz unveraenderter Licht-/Modellgeometrie.
Ausserdem verglichen alle 25 Filtertaps mit der Tiefe des zentralen Pixels,
statt mit der jeweiligen Tiefe der geneigten Empfaengerflaeche.

Korrektur: Bildschirmableitungen werden ueber die inverse 2x2-Jacobi-Matrix
in einen Gradienten in Licht-UV umgerechnet. Sowohl First-Receiver-Pruefung
als auch PCF vergleichen mit der Empfaengerebene am tatsaechlichen
Shadow-Map-Texelzentrum. Konstante Tiefentoleranzen ersetzen den
kamerapixelabhaengigen Bias. Numerisch entartete Projektionen werden verworfen.
AO, Spielskripte und Saveformat sind unveraendert.

Validierung der Engine
`6916445b53b7081231a4570f1e3471bf5bda7571ddbae19f7c3cb568163641dd`:

- `test_shadow_receiver.py boat-receiver-gpu-final`: echte GLSL-Programme
  auf der GPU, 48 Kombinationen aus geneigter Flaeche, Kameraskalierung,
  Scherung/Perspektive und Kontakt/frei/koplanar/verdeckt bestanden.
  Alte Quelle scheitert schon am ersten Kontakttest: Alpha je nach Kamera
  0.000/0.085/0.1475/0.229 statt 0.4; korrigiert durchgehend 0.4.
- `test_ao_boat.py boat-shadow-normandy-final`: fuenf Ansichten auf dem
  echten Landungsboot, jeweils aus/nur Modellschatten/nur AO/beides,
  insgesamt 20 Screenshots. Vorwaerts-, Seiten- und Bodenansichten visuell
  geprueft. Boat/Actors bleiben animiert: kein behaupteter identischer
  Weltzustand zwischen diesen Bildern. Der deterministische Vergleich
  erfolgt separat im GPU-Test. Erste Diagnosebilder mit schwarzem
  Missionsauftakt wurden verworfen; der Test lehnt leere Aufnahmen ab.
- `test_model_shadows.py boat-shadow-release`: AA/SH/BT, NPC/Pickup,
  Bewegung, Save/Load, Grafikneustart und Live-Option bestanden.
- `test_model_shadow_stress.py boat-shadows-uhd`: 3840x2160, 24 Schatten,
  aktiver Schattenpass meist 3-4 ms, maximal 5 ms auf dem Testrechner.
- Keine GL-Fehler im Schattenpass. Der bekannte GL1-Fehler 1281 vor dem
  Pass wird weiterhin getrennt erfasst. 535 persoenliche Profildateien
  nach den Spieltests hashgleich.

Die zuvor dokumentierten Grenzen der kameraseitig eingereichten Geometrie
und der bildraumbasierten AO bleiben bestehen. Diese Korrektur beseitigt
den nachgewiesenen winkelabhaengigen Tiefenbias, behauptet aber keine
vollstaendige Sichtbarkeit verdeckter/offscreen Geometrie. CP09 bleibt offen.
