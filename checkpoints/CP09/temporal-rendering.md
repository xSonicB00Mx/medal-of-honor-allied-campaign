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

100% entsprechen einer Belichtungsdauer von 1/60 Sekunde; die Berechnung
beruecksichtigt die tatsaechliche Zeit zwischen den Spielbildern. Die Laenge
wird auf 32 Bildpixel begrenzt. Kamerabewegung allein erzeugt keine Unschaerfe.
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

## Auslieferung

Getestete Engine: `992d5a0a4afdaa31c3413ef9c0a27863b330ad49b2ce2421e32f5a38f5d89919`.
Passendes cgame: `e1cdf10fb0403915d7ae8ed5e1d2be7ddf62ecc2670b97f82c8f2e0dd29d75b3`.
Der transaktionale Installationsnachweis wird im Anschluss ergaenzt.
