# CP09: Temporal anti-aliasing and object motion blur

Direkter Nutzerauftrag vom 30.10.2026: echtes TAA und getrennt regelbare
Objektbewegungsunschaerfe, ausdruecklich keine globale Kameraunschaerfe.
Die zuvor wiederhergestellten Beleuchtungs-/Partikeleffekte bleiben erhalten.

## Bedienung

Allied Campaign Options -> **AA & Motion...** -> **ANTI-ALIASING & MOTION**.
Beide Einstellungen wirken sofort und werden kampagnenuebergreifend gespeichert.

| Option | Cvar | Standard | Bedeutung |
|---|---|---|---|
| Temporal anti-aliasing (TAA) | `r_acTAA` | 1 | Zeitliche Kantenglaettung an/aus |
| Object motion blur | `r_acObjectMotionBlur` | 0 | Off bis 100%, in 10%-Schritten |

Seit der Rueckmeldung zur zu schwachen Wirkung entsprechen 100% einer
Belichtungsdauer von **1/15 Sekunde**, viermal der urspruenglichen 1/60 Sekunde.
Die Berechnung beruecksichtigt die tatsaechliche Zeit zwischen den Spielbildern.
Die Laenge wird aufloesungsabhaengig begrenzt: 64 Pixel bei 1080p, 128 bei UHD
(insgesamt 32 bis 128 Pixel). Kamerabewegung allein erzeugt keine Unschaerfe.
NPC-Animationen, bewegte Pickups/Modelle, Patronenhuelsen und die Animation der
eigenen Waffe liefern dagegen objektbezogene Bewegung. Der HUD-/Menuepass
liegt hinter der zeitlichen Bildverarbeitung und bleibt davon unberuehrt.
Motion Blur funktioniert auch bei abgeschaltetem TAA.

## Renderer

- GL1 erhaelt eine 16-Phasen-Halton-Projektionsverschiebung, Farb-/Tiefenhistorie
  und echte vorherige deformierte Modellvertices. Kein FXAA als TAA bezeichnet,
  keine reine Kamerageschwindigkeitsnaeherung fuer animierte Modelle.
- Surface-/Modell-/Material-/Entity-Identitaeten und Topologie validieren die
  Historie. Tempmodels erhalten Poolslot plus Erzeugungszeit, damit gleichzeitig
  ausgeworfene Huelsen und wiederverwendete Slots nicht verwechselt werden.
  Mehrdeutige Oberflaechen verwerfen nur ihre eigene Bewegungszuordnung.
- Kamerareprojektion und Objektbewegung sind getrennte Felder. Fuer die
  Viewmodel-Waffe wird die vorherige Pose in Kamerakoordinaten verglichen.
- TAA verwendet Catmull-Rom-Rekonstruktion fuer aktuelles Bild und Historie,
  Tiefen-/Identitaetspruefung, YCoCg-Varianzbegrenzung und Ray-Clipping.
  Beleuchtungswechsel und schnelle Bewegung reduzieren die Historiengewichtung.
  Farbmischung geschieht in naeherungsweise linearem Licht.
- Freigelegte Flaechen, Kameraschnitte, FOV-Aenderung, Karten-/Zeitwechsel,
  Aufloesungswechsel und Renderer-Neustart verwerfen die unpassende Historie.
  AO-Rekonstruktion beruecksichtigt denselben Projektionsversatz.
- Blur nutzt ausschliesslich Objektbewegung, sucht bewegte Silhouetten in der
  Nachbarschaft und prueft die Tiefe bei jedem gewichteten Sample. Die
  gespeicherte TAA-Historie liegt **vor** Motion Blur, damit sich keine
  verwischten Silhouetten rekursiv aufbauen.
- Bei MSAA wird der Abstand eines aufgeloesten Tiefensamples zum Pixelzentrum
  durch die lokale Dreiecksneigung begrenzt. Kein pauschal grosser Tiefenbias,
  der verborgene Modelle durch Waende zulassen wuerde.
- Weltgeometrie behaelt ihre normale Batchbildung. Dynamische Oberflaechen
  werden fuer ihre deformierten Vertices separat erfasst. Speicher ist begrenzt:
  262144 eindeutige Historienvertices, 524288 expandierte Dreiecksvertices,
  8192 Batches. Ueberlauf verwirft die Historie statt Speicher zu ueberschreiben.
- Zusaetzliche Renderfelder sind weder Netzwerk- noch Speicherformat. Engine
  und cgame muessen wegen des Render-ABI gemeinsam installiert werden;
  `game.dll` und vorhandene Spielstaende bleiben kompatibel.

## Pruefungen

Die Testwerkzeuge verwenden getrennte Profile unter `profiles-local/CP09` und
kopieren benoetigte Referenzspielstaende. Persoenliche Dateien werden gehasht.
Screenshots, Float-Bewegungsdaten und Logs bleiben lokal/ignoriert.

`tools/test_temporal_gpu.py temporal-gpu-msaa-fixed` besteht **30 GPU-Faelle**
mit den unveraendert aus dem Quelltext geladenen GLSL-Shadern:

- Kamera-/Objekttrennung bei 60/80/110 Grad FOV, Kameratranslation und Viewmodel;
- unterschiedliche interpolierte Bewegungen deformierter Modellvertices;
- schraege MSAA-Tiefenflaeche und vollstaendige Verdeckung durch eine Wand;
- Kamerareprojektion einschliesslich Jitter, Reset, Disocclusion, Identitaetswechsel,
  reaktive Transparenz und Begrenzung unpassender Historienfarben;
- Subpixelkante gegen eine 8x8-Supersampling-Referenz: mittlerer absoluter Fehler
  **0.002226 statt 0.004042** nach Aufwaermphase, rund 45% weniger in dieser
  synthetischen Probe. Dies ist keine pauschale Qualitaetskennzahl aller Szenen;
- unveraendertes Bild bei reiner Kamerabewegung, bewegte Silhouette, Off,
  Vordergrundwand und gleiche Belichtung bei 30/60/120 FPS.

Native Pruefungen erfassen AA/SH/BT, UHD, bewegte Modelle, Kameraschwenks,
echtes Waffenfeuer/Nachladen, die vorhandenen Bluteffekte, Save/Load,
`vid_restart`, Checkbox/Slider/Defaults und unveraenderte persoenliche Profile.
Die finale 4x-MSAA-Probe `temporal-msaa-final` erfasst 8099 bewegte Pixel der
rotierenden Pickup-Probe statt lediglich 498 vor der Tiefenabgleichkorrektur.
Die staerkere Regression fordert ausserdem eine Mindestabdeckung der gesamten
NPC-/Pickup-Geometrie, statt nur einige vorhandene Bewegungsvektoren zu zaehlen.

`temporal-lifecycle-validated` besteht TAA/Blur einzeln und gemeinsam,
Live-FOV-Wechsel, 1600x900 -> 640x480 -> 1600x900, Kartenwechsel m2l2a -> m2l2b
sowie Hin-/Ruecknavigation ueber den echten Optionsbutton. Sieben Screenshots
zeigen keine leeren Szenen. `temporal-preferences-release` bestaetigt die
Uebernahme von TAA=0 und Blur=70 durch AA -> SH -> BT -> AA und anschliessende
Neustarts aller drei Kampagnen, ohne Missionszustand als Einstellung mitzunehmen.

Vorab gefundene Fehler wurden behoben: HUD-Aufrufe ueber den unmittelbaren
2D-Pfad, zu weiche bilineare Historie, mehrdeutige Tempmodel-Kennungen und der
MSAA-Tiefenabgleich. Fehlgeschlagene Vorablaeufe sind keine Abnahmen.
Testharness-Korrekturen betrafen unter anderem `reload` statt `+reload`, die
Wartezeit bis zur schussbereiten Waffe, UI-Befehlswarteschlange und eine
Intro-Schwarzblende. Der gruenen HUD-Textur wird im Pixelvergleich maximal
2/255 Restabweichung zum schwarzen Diagnosehintergrund zugestanden.

Die finale binaeridentische Testreihe ist bestanden:

| Lokaler Nachweis unter generated-local/CP09 | Kampagne/Aufloesung | Bewegte Pixel |
|---|---|---:|
| temporal-aa-delivery | AA, 3840x2160 | 63805 |
| temporal-sh-delivery | SH, 1600x900 | 3036 |
| temporal-bt-delivery | BT, 3840x2160 | 72910 |

Alle drei Laeufe bestaetigen 571 unveraenderte persoenliche Dateien, gueltige
Bewegungsdaten, Nullbewegung der Welt im Objektfeld, keine neuen Shader-/GL-
Fehler im Temporalpass und keinen Geometriepufferueberlauf. Die jeweiligen
12 Screenshots bleiben lokal. Die Zahlen sind Szenenproben, kein Qualitaetsranking.

`temporal-stress-delivery` misst die finale Engine bei UHD mit 16 NPCs,
acht Pickups, zwei Lichtern, Partikeln, AO und Schatten. `com_speeds` liefert
CPU-Wandzeiten einschliesslich Treiberwartezeiten, keine GPU-Timestamps:

| Optionen | Frames | Median | P95 | P99 | Maximum |
|---|---:|---:|---:|---:|---:|
| TAA/Blur aus | 249 | 15 ms | 16 ms | 16 ms | 17 ms |
| TAA an | 230 | 17 ms | 18 ms | 19 ms | 21 ms |
| TAA + Blur 100% | 231 | 17 ms | 18 ms | 19 ms | 21 ms |

## Grenzen und DLSS

- Getestet wird GL1 auf einer RTX 4090, OpenGL 4.6/NVIDIA 610.88. Keine
  behauptete Abnahme auf anderen GPU-Familien oder im optionalen GL2-Renderer.
- Transparente Partikel, animierte Texturmaterialien und Portalansichten werden
  konservativ behandelt: ihre unzuverlaessige Historie wird nicht aufaddiert;
  transparente Partikel erhalten keine eigene Objektverwischung. Verdeckte
  Farbinformationen kann ein bildbasierter Blur nicht neu erzeugen.
- TAA kann bei feinen bewegten Details weicher als ein ungefiltertes Einzelbild
  wirken. Clipping/Disocclusion begrenzen Ghosting, garantieren aber keine
  Artefaktfreiheit jeder denkbaren Szene. Beide Optionen sind unabhaengig schaltbar.
- Die praezisen Farb-/Tiefen-/Bewegungspuffer beanspruchen etwa 80 Byte pro
  Bildpixel, bei UHD rund **633 MiB** zusaetzlichen GPU-Speicher sowie begrenzte
  CPU-Geometriehistorie. Nicht unterstuetzte GL-Funktionen/FBO-Formate deaktivieren
  den neuen Pfad; `r_acTemporalReady` zeigt die Verfuegbarkeit an.
- Echtes DLSS ist **nicht** enthalten. Der aktuelle
  [NVIDIA Streamline Programming Guide](https://github.com/NVIDIA-RTX/Streamline/blob/main/docs/ProgrammingGuide.md)
  integriert D3D11/D3D12/Vulkan, nicht diesen OpenGL-Kompatibilitaetsrenderer.
  Ein entsprechender Backend-/Interop-Umbau waere eine eigene grosse Aufgabe.
  Die hier implementierte temporale Rekonstruktion wird ausdruecklich TAA genannt.
- Kein vollstaendiger natuerlicher Kampagnendurchlauf und keine persoenliche
  Gesamtspielabnahme. CP09 bleibt offen; keine Mergefreigabe unterstellt.

## Erstinstallation

Getestete Engine: `992d5a0a4afdaa31c3413ef9c0a27863b330ad49b2ce2421e32f5a38f5d89919`.
Passendes cgame: `e1cdf10fb0403915d7ae8ed5e1d2be7ddf62ecc2670b97f82c8f2e0dd29d75b3`.
Quellen-Commit: `fac172f1c91fc9d521463442b66cc34032f48915`.

Die getestete Engine, das passende cgame und alle drei gemeinsamen Optionspakete
sind in **CP08-r1 und CP09-r1 installiert**. Der normale Modstarter verwendet
diese Fassung. `tools/deploy_cp09_engine.py temporal-aa-delivery --cgame
--options-layout` verifizierte 9086/9090 Runtime-Dateien sowie 9072 Originaldateien.
Alle **571 persoenlichen Dateien**, einschliesslich Spielstaenden und Einstellungen,
blieben hashgleich. `game.dll` und die vorhandenen Kunst-/Inhaltspakete bleiben
unveraendert; nur das bereits vorhandene gemeinsame Optionspaket wurde erweitert.

Nachweis: `generated-local/CP09/temporal-aa-delivery/deployment.json`.
Die ersetzten Moddateien liegen dort unter `rollback/`. Keine neue isolierte
Testversion als fertige Installation ausgegeben, kein Merge.

## Nachbesserung: deutlich sichtbarer Regelbereich (30.10.2026)

Der Nutzer sah bei laufenden Gegnern und der eigenen Waffe selbst bei 100%
kaum eine Wirkung und beauftragte ausdruecklich eine deutliche Verstaerkung.
Die gespeicherte Einstellung war korrekt. Ein Vergleich desselben gerenderten
Bildes vor/nach dem Filter in einer Kopie seines neuesten m3l3-Spielstands
zeigte: der Pfad arbeitete, aber 1/60 Sekunde und die feste 32-Pixel-Grenze
waren insbesondere bei UHD zu zurueckhaltend.

- 100% verwendet jetzt 1/15 Sekunde, also vierfache Belichtungsdauer. Niedrigere
  Einstellungen bleiben linear regelbar, 0% bleibt vollstaendig aus.
- Das Limit skaliert mit der Bildhoehe: 64 Pixel bei Full HD, 128 bei UHD.
  Die Nachbarschaftssuche folgt derselben Skalierung und erfasst auch kurze
  und laengere Silhouettenspuren.
- Statt einen unveraenderten 17-Sample-Filter auseinanderzuziehen, verwendet
  der Filter geschwindigkeitsabhaengig bis zu 65 Samples. Kamera-/Objekttrennung,
  Tiefenverdeckung, unverwischte TAA-Historie und HUD-Reihenfolge bleiben erhalten.
- Neue Diagnose `r_acTemporalDebug 4`: einmalige Aufnahme derselben Szene mit
  Shutter=0 und dem eingestellten Shutter sowie Objektbewegungsdaten. Damit
  werden Animations-/Kameraunterschiede zwischen zwei Screenshots als Ursache
  eines vermeintlichen Effekts ausgeschlossen. Nicht standardmaessig aktiv.

`tools/test_object_motion.py` prueft Bewegung, Feuer und Nachladen in einer
Kopie des aktuellen Spielstands, alternativ einen laufenden NPC vor feststehender
Kamera. `object-motion-current-before/after` dokumentieren die Untersuchung;
`object-motion-npc-final` zeigt deutliche Unterschiede ausschliesslich am
bewegten Modell (286289 bzw. 359244 Pixel ueber 3/255 Aenderung bei 100%).
In allen Off-Vergleichen sind beide Bilder bytegleich. 579 persoenliche Dateien
bleiben unveraendert. Die ersten NPC-Testbilder vor Anlaufen der Animation
haben erwartungsgemaess keine Bewegungsunschaerfe.

`object-motion-gpu-final` besteht 31 GPU-Faelle, einschliesslich einer neuen
Pruefung identischer relativer Unschaerfelaenge bei 1080p und UHD.
`object-motion-aa-final` (UHD), `object-motion-sh-final` und
`object-motion-bt-final` bestehen die nativen Waffen-/HUD-/Options-, Save/Load-
und Grafikneustart-Pruefungen ohne Temporal-GL-Fehler oder Pufferueberlauf.
`object-motion-stress-final` misst 15 ms Median ohne Effekte, 17 ms mit TAA und
17 ms mit TAA plus Blur 100%; P95 jeweils 16/18/18 ms, P99 17/18/20 ms.
Dies bleibt eine CPU-Wandzeitmessung einschliesslich Treiberwartezeiten.

Getestete Engine: `6386c6f4e50843ef831ceff669dc5da7cdb40ac610881055e29b052b9c299f8b`.
cgame und Speicherformat bleiben unveraendert. Quellen-Commit
`b92d709afe39366999fe61cacb8c9fa248dc991f` ist in CP08-r1/CP09-r1 installiert.
Nachweis `generated-local/CP09/object-motion-aa-final/deployment.json`:
9086/9090 Runtime-Dateien und 9072 Originale verifiziert, alle 579 persoenlichen
Dateien hashgleich. Die gespeicherte Einstellung 100% wurde nicht zurueckgesetzt.
Die ersetzten Moddateien sind im dortigen `rollback/` gesichert.
