# Hochwertige Ambient Occlusion (28.10.2026)

Direkter Nutzerauftrag nach den dynamischen Modellschatten: weiche, hochwertige
Ambient Occlusion statt eines einfachen kantenbetonenden SSAO-Filters.

## Umsetzung

Eigenstaendige GTAO-basierte Implementierung im regulaeren GL1-Renderer,
`code/renderergl1/tr_ac_ao.c`. Grundlage ist die kosinusgewichtete Integration
von Verdeckungshorizonten aus [Jimenez et al., GTAO](https://www.activision.com/cdn/research/Practical_Real_Time_Strategies_for_Accurate_Indirect_Occlusion_NEW%20VERSION_COLOR.pdf).
Die [XeGTAO-Dokumentation und Referenz](https://github.com/GameTechDev/XeGTAO)
wurden fuer Sampling, duenne Verdeckungsobjekte und Filterung konsultiert.
Dies ist weder eine vollstaendige XeGTAO-Portierung noch Raytracing.

- Eigener Normalen-/Tiefenpass aus bereits animierter, opaker Szenengeometrie.
  Geglaettete Skelettnormalen vermeiden eine Betonung einzelner NPC-Dreiecke;
  Weltgeometrie nutzt echte Flaechennormalen statt unsicherer Silhouettenableitungen
  aus dem Tiefenbild. Alpha-getestete Ausschnitte bleiben ausgeschnitten.
- Volle Renderaufloesung, sechs Schnitte mit je vier Samples auf beiden Seiten
  (48 Tiefensamples pro Pixel), quadratische Sampleverteilung und 32 Welteinheiten
  Reichweite. Sphaerischer Distanzabfall begrenzt die lokale Verdeckung.
- Zwei raeumliche Neun-Tap-Filter mit Normalen-, Ebenen- und Tiefenpruefung.
  Kein zufaelliger Wechsel pro Frame. Seit 29.10.2026 folgt eine tiefen-/normalen-
  gepruefte zeitliche Stabilisierung mit begrenztem Historyeinfluss (siehe Nachtrag).
- Einmalige Komposition gegen den originalen Szenentiefenpuffer; keine mehrfache
  Abdunklung ueberlappender opaker Materialien. Ein begrenzter, neigungsabhaengiger
  Tiefenabstand gleicht Rundungsunterschiede des alten Fixed-Function-Pfads aus;
  Silhouettenspruenge werden dabei nicht als Flaechenneigung gewertet.
- Keine AO auf HUD, Menues, Himmel, First-Person-Waffe oder transparenten Effekten.
  Nebel reduziert den Effekt entsprechend der Sichtweite.
- Neue Modellschatten und AO koennen gemeinsam laufen. Bei aktiver AO entfaellt
  deren bisherige kuenstliche Ambient-Kontaktsilhouette in Bereichen ohne direkte
  Lichtquelle; echte lichtgerichtete Modellschatten bleiben erhalten.
- `Ambient occlusion` in Allied Campaign Options, standardmaessig aktiv,
  sofort schaltbar. Archiviertes `r_acAmbientOcclusion` wird durch die vorhandene
  gemeinsame `r_`-Praeferenzverwaltung kampagnenuebergreifend uebernommen.
  Defaults aktiviert AO. Keine Aenderung der Spiel-/Save-Strukturen.
- Ressourcen werden bei Aufloesungswechsel neu dimensioniert und bei
  Renderer-Neustart freigegeben. Fehlt Shader-/Float-FBO-Unterstuetzung, bleibt
  AO aus. Sichtbare Geometrie wird gemeinsam mit dem Schattenpass begrenzt erfasst;
  ein Ueberlauf laesst beide Zusatzpaesse fuer dieses Bild aus.

`r_acAODebug 1` zeigt die AO-Komposition in Weiss/Grau; `2` misst den
synchronisierten Pass und dessen GL-Fehler. `3` schreibt einmal die RGBA32F-
Normalen/Tiefen als `ao-geometry.f32` sowie die unabhaengige Szenentiefe als
`ao-window-depth.f32` ins aktive Profil und schaltet auf `2`
zurueck. Groesse und Projektionsskalen stehen im Log. Dies sind Entwicklungsdiagnosen,
keine gespeicherten Spieloptionen. `r_acShadowDebug 4` protokolliert zusaetzlich
Geometrie/Materialsortierung fuer die Diagnose alter Materialien.

## Abnahme

Build: MSVC RelWithDebInfo, GL1 `openmohaa`; game/cgame unveraendert.
Die Ergebnisse liegen in ignorierten, getrennten CP09-Testprofilen.

- `test_ambient_occlusion.py gtao-r3`: AA `m2l1`, Kopie des SH-Spielstands
  `t1l3`, BT-Fussgaengerfixture `e2l2`. Aus/an, isolierte AO-Ansicht, gemeinsame
  Modellschatten, animiertes Modell/Pickup, Save/Load, `vid_restart`, nativer
  Optionsschalter und gespeicherter Optionswert. Zehn Bilder pro Kampagne.
- `test_ambient_occlusion_stress.py gtao-uhd-r3`: 3840x2160, HUD 1.66,
  16 zusaetzliche NPCs und acht Pickups. Getrennte Aus/an/Diagnose/Kombinationsbilder.
- `test_options_layout.py gtao-options-r2 --packages-report
  generated-local/CP09/gtao-r3/result.json`: 1920x1080, 1280x960, 3440x1440;
  Controls, Defaults, Back, 10%-Flinchschritte und ueberlappungsfreies Layout.
- `test_ambient_occlusion_views.py gtao-views-r5`: Dorf `m3l2`, geschlossener
  Waggon `m6l3a`, Umschaltung 16:9 auf 4:3 mit Renderer-Neustart.
  Regression fuer die zuvor lueckenhafte Fassadenkomposition und unveraenderte
  Darstellung der First-Person-Waffe in der AO-Diagnose.

Bildvergleiche werden zusaetzlich visuell geprueft; erfolgreiche GL-Aufrufe allein
sind kein Nachweis fuer Bildqualitaet. Der bekannte GL-Fehler 1281 vor Beginn
des Zusatzpasses wird getrennt protokolliert; er tritt auch ohne neue Effekte auf.

Der AO-Pass lag in den 1600x900-Szenen bei 0–3 ms, im UHD-Stresstest bei
3–6 ms (Median 4 ms), gemessen mit GPU-Synchronisation auf diesem Rechner.
30 Modellgruppen waren in der UHD-Szene erfasst. Die Testkarte bot keine direkte
Lichtquelle fuer Modellschatten; deshalb ersetzt dort AO die bisherige
Ambient-Silhouette. Der bestehende Modellschattenpfad wurde mit AO aus separat regressiert.

`test_model_shadows.py gtao-shadow-regression` bestand nach der gemeinsamen
Geometrieaenderung erneut in AA, SH und BT, einschliesslich Save/Load,
Renderer-Neustart und Schatten-Schalter. Die persoenlichen 531 Profildateien
blieben in den geschuetzten Laeufen hashgleich. Kein GL-Fehler innerhalb des
AO-Passes. Pixelkontrollen der Diagnosebilder unterscheiden weiss bleibende
freie Flaechen von lokal abgedunkelten Kontakten; sie ersetzen keine Sichtpruefung.

Getestete Engine: `63179f4ae470fc004e345bf54c056066d7dc1e7581cf8dd5b8251e13a4b877c7`.

## Grenzen

GTAO arbeitet weiterhin im Bildraum. Verdeckte oder ausserhalb des Bilds liegende
Geometrie ist keine vollstaendige Quelle fuer diese AO; Spiegel-/Portalansichten
sind ausgenommen. Es ist lokale Kontaktverschattung, kein Ersatz fuer globale
Beleuchtung oder gebackene Lichtkarten. Der alte Beleuchtungspfad trennt direktes
und indirektes Licht nicht sauber: die begrenzte AO-Komposition moduliert das
fertige Szenenlicht. Transparente Vegetationsschichten sind keine soliden
AO-Empfaenger. Die Qualitaet wird nicht fuer jede Karte und GPU behauptet.

Volle UHD-Aufloesung braucht mit den Verlaufspuffern etwa 380 MiB Texturspeicher fuer die AO-Puffer
(zuzueglich Treiberverwaltung); der gemeinsame Geometriepuffer ist fest begrenzt.
Passmessungen umfassen nicht die gesamte Spiel-Frametime oder die vorgelagerte
Geometrieerfassung. Hardwarebasis der nativen Tests: GeForce RTX 4090.
Natuerlicher Kampagnendurchlauf und CP09-Gesamtabnahme bleiben offen.

## Auslieferung

Die regulaeren CP08-r1-/CP09-r1-Installationen wurden mit
`tools/deploy_cp09_engine.py gtao-r3 --options-layout` aktualisiert.
Source-Commit: `f279dc06a9b6eccb01aeee94449d39df08a4062d`.
Engine-Hash entspricht exakt den Abschlusspruefungen. 9086 bzw. 9090
Laufzeitdateien gegen die Manifeste verifiziert; 9072 Originaldateien und
alle 531 persoenlichen Profildateien hashgleich. Game/cgame/Artwork unveraendert.
Deployment-Bericht und gesicherter Rueckbau liegen unter
`generated-local/CP09/gtao-r3/`. Kein Merge nach main; CP09-Gesamtabnahme offen.

## Nachtrag: Blickwinkel- und Silhouettenkorrektur

Nutzer meldete mit der Kamera wandernde AO und falsch geschwaerzte Kanten.
Die Tiefenrekonstruktion selbst war konsistent; korrigiert wurden diese Stellen:

- Der wichtigste zusaetzlich im Spiel reproduzierte Fehler betraf TIKI-
  Umgebungsmodelle. Der t1l3-Brueckenboden hatte stark gekippte, interpolierte
  Beleuchtungsnormalen trotz ebener Geometrie. Die AO erzeugte dadurch grosse
  dunkle Dreiecke und runde Umschlagstellen der kameraseitigen Normalenausrichtung.
  Geglaettete Modellnormalen werden jetzt nur fuer markierte NPCs/Pickups genutzt;
  Umgebungsmodelle verwenden ihre tatsaechlichen Flaechennormalen. Der Effekt
  wurde in der Spearhead-Kopie visuell und anhand des echten G-Buffers bestaetigt.
- Die sechs Integrationsschnitte liegen nun gleichmaessig um den tatsaechlichen
  Blickstrahl des Pixels. Zuvor lagen sie in der Kamera-Bildebene und deckten
  besonders am Rand eines breiten Sichtfelds ungleichmaessige Winkel ab.
  Die Sample-Abstaende werden passend perspektivisch projiziert; die minimale
  Sample-Laenge verdreht die Schnitte nicht mehr komponentenweise.
- Entfernt wurde die 1,35-fache Gewichtung der Kameratiefenrichtung. Sie machte
  den eigentlich sphaerischen Wirkungsradius zu einem mitdrehenden Ellipsoid.
- Blockiertes Licht wird mit der Laenge der projizierten Flaechennormale
  integriert, statt jeden Schnitt separat auf seinen eigenen Basiswert zu
  normieren. Die analytisch freie Hemisphaere bleibt 1; dadurch verursacht die
  endliche Winkelabtastung keine kuenstliche Grundabdunklung freier Flaechen.
- Der Kompositionsbias verwendet den jeweils naechsten Tiefennachbarn pro Achse
  statt einer Ableitung ueber eine Silhouette. Ein Tiefensprung hatte sonst
  Hintergrund-AO vor eine sichtbare Vordergrundflaeche ziehen koennen.
- Der AO-Geometriepass respektiert die Vorder-/Rueckseiteneinstellung des
  Originalmaterials. Die zweiseitige Erfassung aus Sicht einer Schattenlichtquelle
  bleibt separat erhalten. Keine Aenderung an Spiel-, Save- oder Optionsformaten.

Reproduzierbarer GPU-Test: `tools/test_ao_geometry.py` kompiliert die echten
GLSL-Strings aus `tr_ac_ao.c` in einem unsichtbaren SDL/OpenGL-Kontext. Analytische
Ebenen und ein konvexer Quader pruefen freie Flaechen, Bodenkontakt, neun
Kamerapositionen und fuenf Schwenks vom identischen Standpunkt. Ein eigener
Tiefensprung testet die Komposition gegen einen tatsaechlichen Tiefenpuffer.

- Vorher (`ao-geometry-baseline-regression`): Sichtbarkeit desselben Kontakts
  schwankt beim 60-Grad-Schwenk um 0,01372; der verdeckte Hintergrund schwaerzt
  eine Vordergrundspalte bis auf 0,45. Der Regressionstest schlaegt fehl.
- Korrigiert (`ao-geometry-fixed`): Schwankung 0,00426, also rund 69 Prozent
  geringer; die Vordergrundspalte bleibt 1,0. Freie analytische Flaechen haben
  mindestens 0,99994 Sichtbarkeit, der sichtbare AO-Testbereich weiterhin 0,45.
  Das ist ein begrenzter Geometrietest, keine weltweite Qualitaetsgarantie.
- Native Kameraschwenks: `tools/test_ao_camera.py ao-camera-fixed-r2`, `m3l2`
  und `m6l3a`, jeweils fuenf Winkel mit Diagnose- und Farbbildern. Keine GL-Fehler.
  Der direkte `m6l3a`-Start erzeugt bereits mit der alten Engine vier bekannte
  NULL-Deathlistener aus `global/friendly.scr`, da die uebernommenen Gefangenen
  fehlen. Nur diese exakten Meldungen werden im Kameratest separat erfasst;
  sie werden nicht als durch die AO-Korrektur behobene Spielfehler ausgegeben.
  Der zuerst irrtuemlich vor Abschluss des Builds gestartete Lauf
  `ao-camera-fix-r1` enthaelt noch die alte Engine und ist kein Fixnachweis.

Die erste kampagnenweite Korrekturrunde `ao-viewfix` bestand die Laufpruefungen,
zeigte bei der anschliessenden Sichtpruefung aber noch den oben beschriebenen
Brueckenfehler. Sie wurde nicht ausgeliefert. `ao-bridge-normal-probe` konserviert
die falschen Normalen, `ao-bridge-normal-fix` den korrigierten G-Buffer und die
saubere AO-Ansicht. An den drei freien Bodenkontrollen steht die Diagnose danach
auf 255/255/255 statt grossflaechiger Eigenverschattung. Ein vierter Kontrollpunkt
prueft nur die Normale, weil er berechtigt nahe an einem Brueckenpfeiler liegt.
`test_ambient_occlusion.py --bridge-normals --spearhead-save <Kopie>` sichert diese
zusaetzliche Regression; die Eingabekopie wird niemals direkt bespielt.

Abschliessend mit Engine
`c861c7623c4a4dc7a9a2e89777f08c1bdd9907f1dc550426bb7b71e1efbea584` geprueft:

- `ao-geometry-final`: analytische GPU-Regression einschliesslich Silhouettenbias.
- `ao-viewfix-final --bridge-normals --spearhead-save <gesicherte Kopie>`:
  AA/SH/BT, Ein/Aus, Diagnose, NPC/Pickup, gemeinsame Schattenoption, Save/Load,
  Renderer-Neustart und Optionsschalter. Die Brueckennormalen stimmen an vier
  Kontrollpunkten mit den unabhaengig aus Tiefe rekonstruierten Flaechennormalen
  ueberein (Skalarprodukt mindestens 0,9999999).
- `ao-camera-final --spearhead-save <gesicherte Kopie>`: je fuenf Kamerawinkel
  im AA-Dorf, AA-Waggon und auf der SH-Bruecke, Diagnose- und Farbbilder.
- `ao-viewfix-final-resize`: 16:9/4:3, Renderer-Neustart, Fassadenkomposition und
  unveraenderte First-Person-Waffe.
- `ao-viewfix-final-uhd`: 3840x2160, 30 erfasste Modellgruppen, 3-5 ms
  synchronisierter AO-Pass auf der vorhandenen RTX 4090. Keine GL-Fehler im Pass;
  die bekannten vorherigen GL-Fehler werden weiterhin getrennt erfasst.

Die geschuetzten Testlaeufe bestaetigen 535 unveraenderte persoenliche
Profildateien. Screenshots/Normalen-Dumps/Saves bleiben lokal und ignoriert.
Keine persoenliche Gesamtspielabnahme oder neue CP09-Freigabe unterstellt.

Ausgeliefert mit `tools/deploy_cp09_engine.py ao-viewfix-final`: Engine-Source
`0a549e9159c737af8645c71d1646627ff660a4c1`, obiger Engine-Hash in CP08-r1/CP09-r1.
9086/9090 Laufzeitdateien, 9072 Originaldateien und 535 persoenliche Profildateien
verifiziert. Nur die Engine ersetzt; game/cgame, Spielinhalte und Optionen
unveraendert. Deploymentbericht und Rueckbau:
`generated-local/CP09/ao-viewfix-final/deployment.json` bzw. `rollback/`.

Die grundlegende Bildraumgrenze bleibt: hinter anderen Objekten oder ausserhalb
des Bilds liegende Geometrie kann weiterhin fehlen. Die Korrektur reduziert
unbegruendete Blickwinkelabhaengigkeit, behauptet aber keine vollstaendig
blickwinkelunabhaengige Weltgeometrie-AO oder Raytracing.


## Nachtrag 29.10.2026: schwebende Prop-AO und Distanzstabilisierung

Nutzer meldet vergroesserte, ueber Schreibmaschinen schwebende AO und sichtbares
Aufpoppen. In `m2l2a` mit der bisherigen regulaeren Engine direkt reproduziert:
Die Diagnose zeichnet eine nahezu doppelt grosse Schreibmaschine oberhalb der
sichtbaren Maschine; auch Tisch-/Stuhl-/Lampen-Kontakte sind versetzt.

Ursache: `R_RotateForStaticModel` multipliziert die Modellmatrix mit
`TIKI.load_scale * StaticModel.scale`, laesst `ori.axis` aber unskaliert.
Die gemeinsame AO-/Schatten-Geometrieerfassung hatte nur `ori.axis` verwendet.
Bei der Schreibmaschine fehlte so der Massstab 0,52. Die Erfassung verwendet
nun denselben Gesamtmassstab wie der normale Renderer. Das gilt fuer alle
statischen Modelle und deren Verwendung als Schattenempfaenger/-verdeckung;
keine neue Umgebungsschattenfunktion, keine Aenderung der eigentlichen Modelle.

Der AO-Wirkungsradius von 32 Welteinheiten ist ein **Kontaktradius**, keine
Kamera-Abschaltdistanz. Es gibt weiterhin keinen festen Abstand, ab dem AO
abgeschaltet wird. Kleine ferne Objekte haben aber nur wenige Bildpunkte:
Abtastwechsel koennen deshalb Kontaktverschattung sprunghaft veraendern.
Neu ist eine zeitliche Stabilisierung nach den raeumlichen Filtern:

- Vorherige Geometrie/Visibility werden in Renderertexturen gehalten; keine
  Spielstanddaten. Rueckprojektion mit vorheriger Sicht-/Projektionsmatrix.
- Uebereinstimmung von Tiefe und Flaechennormale erforderlich. Neue/verdeckte
  Flaechen, Kameraschnitte, Teleports, Renderer-/Aufloesungswechsel, Zeitruecksprung
  und Ein/Aus-Wechsel verwerfen ungueltigen Verlauf.
- Zeitabhaengige Filterung (75 ms Zeitkonstante, Mindestschritt 8 ms), keine
  zusaetzliche Entfernungsabschaltung. Der lokale aktuelle Sichtbarkeitsbereich
  begrenzt den Verlauf mit 0,08 Reserve, damit bewegte NPCs keine lange dunkle
  Spur auf unveraenderten Empfaengern hinterlassen.
- Vier Textursampler erforderlich; etwa 380 MiB AO-Texturspeicher bei UHD,
  zuzueglich Treiberverwaltung. Der 48-Sample-Horizontpass bleibt unveraendert.
  Ein untersuchter 4-Tap-Abtastungsansatz wurde wegen geringen Gewinns verworfen.

### Nachweise

- `test_ao_props.py ao-props-before-r4 --baseline`: fuenf echte Ansichten der
  gebackenen `m2l2a`-Schreibmaschine, 15 Aus/An/AO-Bilder. Der Fehler ist sichtbar.
  Die ersten Probeversuche hatten den Kamerabefehl durch die originale
  `thereisnomonkey`-Cheatsperre deaktiviert; sie sind **kein** Sichtnachweis.
  Der Test verlangt jetzt explizite Bestaetigungen aller ausgefuehrten Kameras.
- `test_ao_props.py ao-props-final`: dieselben Ansichten korrigiert. Zusaetzlich
  Vergleich des AO-Geometriepuffers mit dem unabhaengigen normalen Tiefenpuffer
  auf dem Schreibmaschinengehaeuse: Median 1,79e-7, P99 7,15e-7 im normierten
  Tiefenraum. Die grosse schwebende Silhouette ist verschwunden.
- `test_ao_geometry.py ao-props-temporal`: vorhandene Ebenen-/Silhouetten-/
  Kamerawinkelregression bestanden. Kontakt-AO eines 20x20x30-Quaders bleibt
  in 13 Entfernungen von 120 bis 2880 Einheiten vorhanden. Das belegt keine
  perfekte Konstanz einer nur noch wenige Pixel grossen Form.
- Derselbe GPU-Test kompiliert auch den echten Verlaufsshader: periodische
  Schwankung auf 11,14 Prozent reduziert, Tiefen-/Normalenabweichungen und
  Reset ohne alten AO-Einfluss, kontrollierte Kameraverschiebung korrekt.
  Bei entferntem Verdeckungsobjekt bleibt maximal 0,064 alte Verdeckung nach
  einem Testschritt (vor der 0,7-Kompositionsstaerke). Das ist ein begrenzter
  Shader-Regressionswert, keine allgemeine Prozentgarantie fuer Spielszenen.
- `test_ambient_occlusion.py ao-props-release --bridge-normals
  --spearhead-save <gesicherte Kopie>`: AA/SH/BT, Aus/An, bewegte Modelle,
  Save/Load, Renderer-Neustart, Optionsschalter und SH-Brueckennormalen bestanden;
  535 persoenliche Profildateien hashgleich.
- `ao-props-resize`: 16:9/4:3, Renderer-Neustart, Fassaden und Viewmodelausschluss.
- `ao-props-uhd`: 3840x2160 mit 30 Modellgruppen, AO-Pass 3-6 ms auf RTX 4090;
  keine GL-Fehler im Zusatzpass. Bekannte vorherige GL-1281 separat protokolliert.

Die Bildraumgrenze bleibt: verdeckte/offscreen Geometrie ist nicht vollstaendig
verfuegbar; Unterpixelobjekte und die Sichtweite/Nebel der Karte begrenzen die
Sichtbarkeit. Die Korrektur verspricht keine Weltgeometrie-AO oder Raytracing.

Weitere Abschlusspruefungen mit derselben Engine:
`ao-props-camera` (15 native Kamerawinkel AA-Dorf/AA-Waggon/SH-Bruecke) und
`ao-props-shadows` (AO aus, Modellschatten AA/SH/BT einschliesslich
Save/Load/Renderer-Neustart) bestanden. Beim direkten Waggonstart sind die
bereits dokumentierten vier NULL-Deathlistener separat ausgewiesen.

Gepruefter Engine-SHA256:
`1ecbe66ed1d14aec9cde41cff8ff48afcf4739e7577a98a887e75fe0dc8bf2b6`.
