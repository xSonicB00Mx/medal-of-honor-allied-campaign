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
  Reichweite. Distanz-/Dickenabfall begrenzt dunkle Saeume an duennen Objekten.
- Zwei raeumliche Neun-Tap-Filter mit Normalen-, Ebenen- und Tiefenpruefung.
  Kein zufaelliger Wechsel pro Frame und kein Historybuffer mit Nachzieheffekten.
- Einmalige Komposition gegen den originalen Szenentiefenpuffer; keine mehrfache
  Abdunklung ueberlappender opaker Materialien. Ein begrenzter, neigungsabhaengiger
  Tiefenabstand gleicht Rundungsunterschiede des alten Fixed-Function-Pfads aus.
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
synchronisierten Pass und dessen GL-Fehler. Beide sind Entwicklungsdiagnosen,
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

Volle UHD-Aufloesung braucht etwa 222 MiB Texturspeicher fuer die AO-Puffer
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
