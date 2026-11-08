## 2026-11-08: Himmel bleibt unter Kontrolle des Spielers

- Erneut r_fastsky 1 im AA-Profil/gemeinsamen Preferences gefunden. Wetter-Flash setzt 1, Unflash stellt einen alten Levelwert wieder her; die bisherige Profilkorrektur schuetzte nicht davor.
- ScriptThread::SetCvarEvent ignoriert jetzt ausschliesslich Skriptzugriffe auf r_fastsky. Standard und persoenliche Einstellung 0; ausdrueckliche Konsolen-/Menuewahl bleibt moeglich. Alte Saves ebenfalls geschuetzt, kein neues Speicherformat.
- AA m5l1b und SH t1l3 aus bestehenden Saves sowie BT e1l1 geprueft: Wetter, beide Schaltrichtungen, Save/Load, Grafik-/Prozessneustart, gemeinsame Spielerwahl. BT-Missionsskriptmeldungen durch Vergleich mit alter DLL als bereits vorhanden bestaetigt.
- Source 6ae93008, game.dll 3d6e1833 in CP08-r1/CP09-r1 installiert. 9086/9090 Runtime-Dateien und 9072 Originaldateien verifiziert. Engine/cgame/Assets unveraendert. 699 Profildateien bei Tests/Deployment unveraendert; davor nur zwei r_fastsky-Zeilen mit Sicherung korrigiert, Saves unberuehrt.
- Nachweise checkpoints/CP09/night-sky.md und generated-local/CP09/sky-choice-release/deployment.json. Kein Merge.

## 2026-11-03: Options-Seitennavigation eindeutig getrennt

- Nutzerfeedback: spaltenbreite Reiter wirkten wie Spaltenueberschriften. Ersetzt durch eine gemeinsame Navigationsleiste mit PAGE 1 OF 2 / PAGE 2 OF 2, zentriertem Seitentitel und Blaetterpfeilen. Nicht verfuegbare Richtung ist grau und nicht bedienbar.
- Inhalte, Bindings, Einstellungen und seitenweise Defaults unveraendert. Native AA/SH/BT-Pruefung bei 1080p, 4:3, Ultrawide und UHD samt kleiner/grosser Schrift bestanden; Screenshots geprueft.
- Source a8bdf3ec, sechs UI-Pakete in CP08/CP09 ersetzt. 9086/9090 Runtime-Dateien, 9072 Originale und 683 unveraenderte Profildateien verifiziert. Engine/DLLs unveraendert, Rueckbausicherung vorhanden.
- Nachweis generated-local/CP09/options-page-navigation/deployment.json und checkpoints/CP09/options-regroup.md. Kein Merge.

## 2026-11-03: Allied Campaign Options aufgeraeumt

- Zwei einheitliche Kategorien: Interface & Gameplay fuer HUD/Schrift/Flinch/BT-Drops und Graphics & Effects fuer TAA, AO, Modellschatten, Object Motion Blur sowie alle Bluteffekte. Aktiver Reiter markiert; klare Spalten, Hilfstexte und gemeinsame Abstaende.
- Page defaults setzt nur die aktuelle Seite zurueck. Alle bisherigen Cvars/Werte bleiben erhalten; Flinch und Blur weiterhin ausschliesslich in 10%-Schritten.
- Echte Bedienpruefung AA/SH/BT bei 1080p, 4:3, Ultrawide und UHD; keine Widget-Ueberlappungen, beide Schriftgroessen, Tabs/Back, alle 15 Einstellungen und getrennte Defaults bestanden. Ingame-/Grafikneustart-/Kartenwechselpruefung ebenfalls bestanden.
- Source 4a44de98. Ausschliesslich die sechs Optionspakete in CP08-r1/CP09-r1 installiert; Engine f567924a und DLLs unveraendert. 9086/9090 Runtime-Dateien, 9072 Originale und 683 unveraenderte persoenliche Dateien verifiziert.
- Nachweis checkpoints/CP09/options-regroup.md und generated-local/CP09/options-regroup-r2/deployment.json; Rueckbausicherung vorhanden. Keine neue Grafikfunktion, kein Merge.

## 2026-10-31: Levellicht-Pilot auf Nutzerwunsch zurueckgenommen

- Nutzer lehnt die Gesamtwirkung als zu starke Veraenderung ab. Pilot e29b1d53 vollstaendig aus aktivem Renderer, Buildanbindung und Werkzeugen entfernt; Code entspricht wieder 69b26086.
- Separate Pilot-Runtime und beide Starter nach generated-local/CP09/relight-withdrawn archiviert. Lokales Build-EXE wieder bytegleich zur regulaeren Engine f567924a. CP08-r1/CP09-r1 waren nie umgestellt und bleiben unveraendert.
- Persoenliche Spielstaende und Einstellungen unveraendert; kein Spielprozess lief beim Rueckbau. Vergleichsbilder bleiben als historische Referenz erhalten.
- Positives Nutzerfeedback: Schatten unter dem Fahrzeug erdet es besser. Nur als Hinweis festgehalten, keine isolierte Schattenaenderung beauftragt oder eingebaut.
- Details checkpoints/CP09/level-relight-pilot.md. Kein neuer Spieleingriff, keine globale Installation, kein Merge.

## 2026-10-31: Drei experimentelle Beleuchtungs-/Partikeloptionen erneut entfernt

- Kirchen-Einbruch in aktueller m3l3-Spielstandkopie auf CPU-Lichtverdeckung eingegrenzt: zeitweise ueber 200000 Sichtpruefungen pro Sekunde und 23--25 ms Bildzeit.
- Nutzer verlangt erneut vollstaendigen Rueckbau aller drei Analyse-Features. Lokale Modellbeleuchtung, verdeckte dynamische Lichter und Lit Soft Particles samt Optionsseite/Build-/Clientanbindung entfernt. Urspruengliche Licht-/Partikelpfade wiederhergestellt. TAA, verstaerkter Object Motion Blur, Modellschatten und AO erhalten.
- Finale Kirche/UHD: Median 8 ms, P95 9 ms ueber 2109 Frames, einzelne Spitze 27 ms. AA/SH/BT, Waffen, Save/Load, Grafikneustart, Optionsnavigation, Seitenverhaeltnis/FOV/Kartenwechsel bestanden.
- Source 19ddd629; Engine f567924a und cgame cdb016b9 in CP08-r1/CP09-r1 installiert. 9086/9090 Runtime-Dateien und 9072 Originale verifiziert, 595 persoenliche Dateien/Spielstaende hashgleich. Vorhandene TAA-/Blur-Wahl erhalten.
- Nachweis checkpoints/CP09/church-performance.md und generated-local/CP09/remove-lighting-aa-release/deployment.json. Kein Merge, CP09-Gesamtabnahme offen.

## 2026-10-30: Objektbewegungsunschaerfe deutlich verstaerkt

- Nutzerrueckmeldung zu kaum sichtbarem Blur bei 100% an Gegnern/eigener Waffe nachvollzogen: Einstellung war aktiv, 1/60s und feste 32-Pixel-Grenze bei UHD zu schwach. Vergleich desselben Spielbilds vor/nach Filter in Kopie des neuesten Spielstands.
- 100% jetzt 1/15s (vierfache Belichtungsdauer); Limit 64 Pixel/1080p bzw. 128/UHD. Geschwindigkeitsabhaengiger Filter bis 65 Samples und skalierte Silhouettensuche. Kamerabewegung allein bleibt ohne Blur; Off liefert bytegleiche Bilder.
- Laufender NPC, eigene Waffe/Bewegung/Nachladen, 31 GPU-Faelle und AA/SH/BT inklusive UHD, Save/Load, HUD und Optionsbedienung bestanden. UHD-Stress TAA+Blur 17 ms Median/18 ms P95 CPU-Wandzeit.
- Quellen b92d709a, Engine 6386c6f4 in CP08-r1/CP09-r1 installiert; cgame/game unveraendert. 9086/9090 Runtime-Dateien und 9072 Originale verifiziert, 579 persoenliche Dateien/Spielstaende hashgleich, gespeicherte 100%-Wahl erhalten.
- Nachweise generated-local/CP09/object-motion-* und checkpoints/CP09/temporal-rendering.md. Kein Merge, CP09-Gesamtabnahme offen.

## 2026-10-30: Echtes TAA und reine Objektbewegungsunschaerfe eingebaut

- Direkter Featureauftrag: zeitliche Kantenglaettung mit Projektionsjitter, Tiefen-/Farbhistorie und deformierten Modellvertices; getrennte, kamerabereinigte Bewegungsvektoren fuer Object Motion Blur. HUD/Menues bleiben hinter dem Effektpass.
- Neue Seite Allied Campaign Options -> AA & Motion...: TAA standardmaessig an; Object motion blur Off bis 100% in 10%-Schritten, standardmaessig aus. Live und kampagnenuebergreifend. Kein DLSS: aktueller GL1-Renderer hat keinen passenden Streamline-Backendpfad.
- 30 GPU-Faelle, AA/SH/BT, UHD, echtes 4x MSAA, Waffenfeuer/Nachladen, Save/Load, Grafik-/Aufloesungs-/FOV-/Kartenwechsel und UI-Pruefungen bestanden. MSAA-Tiefenabgleich und Tempmodel-Identitaeten korrigiert. UHD-Stress: 15 ms Median aus / 17 ms TAA / 17 ms TAA+Blur, CPU-Wandzeit inklusive Treiberwartezeit.
- Quellen fac172f1, Engine 992d5a0a, cgame e1cdf10f in CP08-r1/CP09-r1 installiert. 9086/9090 Runtime-Dateien und 9072 Originale verifiziert; 571 persoenliche Dateien inklusive Spielstaenden unveraendert. Spiel-/Speicherformat unveraendert.
- Nachweise generated-local/CP09/temporal-*-delivery und checkpoints/CP09/temporal-rendering.md. Bestehende Beleuchtungs-/Partikel-, Schatten- und AO-Features erhalten. CP09-Gesamtabnahme offen; kein Merge.

## 2026-10-30: Beleuchtungs-/Partikel-Erweiterungen zur Nutzeranalyse wieder eingebaut

- Neuer ausdruecklicher Auftrag nach Rueckbau: exakt die zuletzt korrigierte Fassung 406a0616 einschliesslich Waffenlichtkorrektur und Optionsseite Lighting & Particles wiederhergestellt.
- Source cd500952; gesicherte Engine 101d26ba und cgame 0d2d018e bytegleich erneut eingesetzt, keine neue Kompilierung. Alle drei Effekte einzeln live schaltbar, bei fehlenden Einstellungen standardmaessig an.
- Native erneute AA-Pruefung: Save/Load, Grafikneustart, alle Checkboxen und Defaults bestanden. Vorherige AA/SH/BT-/UHD-Regression gilt fuer exakt diese Binaerdateien.
- In CP08-r1/CP09-r1 installiert; 9086/9090 Runtime-Dateien und 9072 Originale verifiziert. Alle 567 persoenlichen Dateien inklusive Spielstaenden und Einstellungen unveraendert. Nachweis generated-local/CP09/lighting-reenabled. Nutzeranalyse steht aus; kein Merge, CP09 offen.

## 2026-10-30: Drei Beleuchtungs-/Partikel-Erweiterungen vollstaendig zurueckgenommen

- Ausdruecklicher Nutzerauftrag: lokale Modellbeleuchtung, verdeckte dynamische Lichter und Lit Soft Particles samt Optionen und nachtraeglicher Waffenlichtkorrektur entfernt.
- Code/CMake/UI/Werkzeuge entsprechen wieder a9671da0 (vor Einfuehrung). Optionsseite Lighting & Particles und ihr Zugang entfernt. Vorhandene Modellschatten mit Wandverdeckung und Ambient Occlusion erhalten.
- Originale gesicherte Engine 1f269954 und cgame af9d7974 sowie alle drei alten Optionspakete in CP08-r1/CP09-r1 bytegleich wiederhergestellt. Passende lokale Build-Binaerdateien ebenfalls zurueckgesetzt; keine neue Kompilierung behauptet.
- Native AA/SH/BT-Pruefung mit Save/Load, Grafikneustart, Modellschatten, Live-Schalter und Optionslayout bestanden. 9086/9090 Runtime-Dateien und 9072 Originaldateien verifiziert. 557 von 559 Profildateien, darunter alle Spielstaende, unveraendert hashgeprueft; ausschliesslich neue Cvar-Zeilen aus zwei Konfigurationen entfernt (559 Dateien insgesamt).
- Nachweis/Transaktionssicherung generated-local/CP09/remove-lighting; Spieltest remove-lighting-test. Historischer Bericht checkpoints/CP09/lighting-particles.md als zurueckgenommen gekennzeichnet. Kein Merge, CP09-Gesamtabnahme offen.

## 2026-10-30: Fehlendes Waffenlicht im optimierten Renderer behoben

- Nutzerfehler in Kopie des aktuellen m3l2-Spielstands mit echter Thompson reproduziert. Optimierter Modellpfad liess neue Lichtbeitraege aus, nachdem das alte Licht bereits unterdrueckt wurde.
- Gemeinsame Farbberechnung fuer schnellen/generischen Pfad; lokale Lichtgitter-Proben erreichen nun ebenfalls diese Modelle. Urspruengliche Modell-/Rauch-Lichtantwort wiederhergestellt, Verdeckung weiterhin vertexgenau.
- Regressionsprobe scheitert mit alter Engine; neue schnelle/generische Pfade liefern gleiche Lichtwerte. Echtes Feuer innen/aussen, Decke/Drehtuer, AA/SH/BT, Save/Load, Grafikneustart und UHD geprueft. UHD-Last 15 ms Median/16 ms P95 CPU-Wandzeit; gleichmaessiges Bocage-Licht bleibt bei lokalen Proben dezent.
- Engine 101d26ba aus Source 83fbf55a in CP08-r1/CP09-r1 installiert. 9086/9090 Runtime-Dateien, 9072 Originaldateien und 555 unveraenderte persoenliche Dateien verifiziert. Persoenliche Option Occluded dynamic lights bleibt aus. Details checkpoints/CP09/lighting-particles.md. Kein Merge, CP09-Gesamtabnahme offen.

## 2026-10-29: Lokale Beleuchtung und Soft Particles implementiert und geprueft

- Direkter Nutzerauftrag fuer Vorschlaege 1/4/5: lokale Lichtgitter-Proben, verdeckte dynamische Lichter, beleuchtete Soft Particles.
- Neue Seite Lighting & Particles mit drei gemeinsamen Live-Schaltern. Spiel-/Speicherformat unveraendert.
- AA/SH/BT, Save/Load, Renderer-Neustart, UHD, Decke/Drehtuer, Partikel-GPU und Normandy-Boot bestanden. UHD-Last mit 16 NPCs, acht Pickups und zwei Lichtern: 10 ms Median / 11 ms P95 CPU-Wandzeit.
- Engine d0eea6b9 und cgame 0d2d018e aus Source 7d32ce06 in CP08-r1/CP09-r1 installiert. 9086/9090 Runtime-Dateien und 9072 Originaldateien verifiziert, 555 persoenliche Profildateien unveraendert. Details checkpoints/CP09/lighting-particles.md. CP09-Gesamtabnahme offen, kein Merge.

## 2026-10-29: Durch Waende scheinende Modellschatten behoben

- Verdeckte BSP-/statische Levelgeometrie blockiert Schatten unabhaengig von der Kamera. Bewegliche Brushmodelle verwenden ihre aktuelle Transformation.
- Keine Projektion auf die unbeleuchtete Wandrueckseite; jeder PCF-Tap prueft seine eigene Verdeckung.
- Nativer m2l2a-Deckentest: vorher 105726 fehlerhafte Schattenpixel, nachher 0; sichtbarer Bodenschatten bleibt erhalten. 60 GPU-Faelle plus Filtertest, AA/SH/BT, Save/Load, Grafikneustart, Normandy-Boot und UHD bestanden.
- Engine 1f269954, Source 88550606, in CP08-r1/CP09-r1 installiert. 9086/9090 Runtime-Dateien und 9072 Originaldateien verifiziert, 551 persoenliche Profildateien unveraendert.
- Details checkpoints/CP09/model-shadows.md. CP09-Gesamtabnahme offen, kein Merge.

## 2026-10-29: Blickwinkelabhaengigen Modellschatten-Bias korrigiert

- Schatten-Tiefenvergleich nutzt die Empfaengerebene in Licht-UV statt Kamerapixel-Steilheit; auch alle PCF-Filtertaps folgen der Flaeche.
- Alte Quelle reproduziert den Kontaktverlust im GPU-Test; neue Quelle besteht 48 Kamera-/Tiefenfaelle. Landungsboot m3l1a in fuenf Ansichten mit getrennten Effekten geprueft.
- AA/SH/BT, Save/Load, Renderer-Neustart, Live-Schalter und UHD bestanden. Keine GL-Fehler im Schattenpass.
- Engine 6916445b aus Source 790e9b68 in CP08-r1/CP09-r1 installiert; 9086/9090 Runtime-Dateien, 9072 Originaldateien und 535 persoenliche Profildateien verifiziert.
- Bericht checkpoints/CP09/model-shadows.md; Sichtbarkeits-/Bildraumgrenzen bleiben dokumentiert. CP09 offen, kein Merge.

## 2026-10-29: Schwebende AO auf statischen Modellen behoben

- Fehlender TIKI-/Instanzmassstab im AO-/Schatten-Geometriepass korrigiert; echte m2l2a-Schreibmaschine vorher/nachher und gegen normalen Tiefenpuffer geprueft.
- Zeitlich stabilisierte AO mit Kamera-Rueckprojektion, Tiefen-/Normalenpruefung und begrenztem Verlauf; keine feste Kamera-Abschaltdistanz.
- GPU-Regression bis 2880 Einheiten, fuenf Prop-Ansichten, AA/SH/BT, Kameraschwenks, Save/Load, Aufloesungswechsel, UHD und separate Modellschatten bestanden.
- Engine 1ecbe66e in CP08-r1/CP09-r1 installiert; 9086/9090 Runtime-Dateien, 9072 Originaldateien und 535 unveraenderte persoenliche Profildateien verifiziert.
- Source e2067c3c, Bericht checkpoints/CP09/ambient-occlusion.md. CP09-Gesamtabnahme weiterhin offen, kein Merge.

## 2026-10-29: AO-Blickwinkel und falsche Kanten korrigiert

- TIKI-Umgebungsmodelle nutzen geometrische Flaechennormalen; falsche Dreiecksmuster auf der SH-Bruecke beseitigt. NPC-/Pickup-Normalen bleiben geglaettet.
- Gleichmaessige Integration um den Pixel-Blickstrahl, sphaerischer Radius und korrigierte Normalengewichtung; Tiefenspruenge ziehen keine Hintergrund-AO mehr auf Vordergrundkanten.
- Analytische GPU-Regression, 15 native Kamerawinkel, AA/SH/BT mit Save/Load, Renderer-/Aufloesungswechsel und UHD bestanden. Bildraumgrenzen bleiben dokumentiert.
- Engine c861c762 in CP08-r1 und CP09-r1 installiert; 9086/9090 Laufzeitdateien und 9072 Originaldateien verifiziert, 535 persoenliche Profildateien unveraendert.
- Source 0a549e91 auf CP09-Arbeitsbranch gesichert. Details: checkpoints/CP09/ambient-occlusion.md. Kein Merge, CP09-Gesamtabnahme offen.

## 2026-10-28: Hochwertige Ambient Occlusion

- Direkter Nutzerauftrag: GTAO-basierte Kontaktverschattung, volle Aufloesung, geglaettete Modellnormalen und kantenbewahrende Filterung.
- Ambient occlusion als kampagnenuebergreifender Live-Schalter, standardmaessig an.
- AA/SH/BT, Save/Load, Renderer-/Aufloesungswechsel, Optionen und UHD-Stresstest bestanden; Modellschatten separat regressiert.
- CP08-r1 und CP09-r1 aktualisiert, 9086/9090 Laufzeitdateien verifiziert, 531 persoenliche Profildateien unveraendert.
- Details, Messwerte und Bildraum-Grenzen: checkpoints/CP09/ambient-occlusion.md. CP09-Gesamtabnahme weiterhin offen.

## 2026-10-28: Dynamische Modellschatten

- Expliziter Nutzerauftrag: regulaere GL1-Mod, NPCs und Pickups, keine neuen Umgebungsschatten.
- Geprueft in AA/SH/BT mit Save/Load, Renderer-Neustart, Live-Option und UHD-Stresstest.
- Gemeinsamer Schalter Dynamic model shadows, standardmaessig an; 531 Profildateien in Tests unveraendert.
- In CP08-r1 und CP09-r1 installiert, 9086/9090 Laufzeitdateien verifiziert; Source a9f7c486 auf GitHub bestaetigt.
- Details und Grenzen: checkpoints/CP09/model-shadows.md. CP09-Gesamtabnahme weiterhin offen.

## 2026-10-28: Vollstaendiger Himmel kampagnenuebergreifend aktiviert

- Vorherige Farbkorrektur hatte r_fastsky nicht deaktiviert; persoenliches Profil stand in allen Kontexten auf 1.
- Jetzt vier Konfigurationswerte auf 0, gesichert; 503 andere Profildateien unveraendert.
- AA/SH/BT-Start und Kopie des aktuellen t1l3-Saves geprueft; strukturierter Himmel im Bildvergleich.
- Details: checkpoints/CP09/night-sky.md. Keine Engine- oder Saveaenderung.

## 2026-10-26: Installer-Lieferumfang praezisiert

- Alle benoetigten Modressourcen und Laufzeitabhaengigkeiten im kostenlosen Setup mitliefern.
- WCR zuerst vollstaendig pruefen; kompatiblen Bestand ohne Download uebernehmen.
- Nur fehlendes/zu reparierendes WCR extern beziehen; keine Max-Payne-/Fontgenerierungs-Voraussetzung.
- Weiterhin ausschliesslich Planung, kein Installerbau.

## 2026-10-26: Installerplanung, noch kein Installerbau

- Nutzerauftrag: spaeter rohe Warchest erkennen, WCR herunterladen, danach Allied Campaign installieren.
- Ablauf, getrennte Installation, Paketierung, Updates/Rollback und Abnahme geplant.
- Offen: WCR-Releasezuordnung, saubere Ausgangsbasis und Releaseherkunft aller Assets.
- Keine Pakete heruntergeladen, kein Installer erzeugt, keine Runtime-/Profilveraenderung.
- Plan: checkpoints/CP09/INSTALLER-PLAN.md.

## 2026-10-25: Startup movies restored

- CP08/CP09 normal launchers now use cl_playintro 1; internal campaign switches retain 0.
- Original intro chain completed naturally in isolated profile (184 seconds), then Main Menu verified.
- Launcher-only change; no binaries, assets or personal profile modified.

## 2026-10-24: Spearhead D-Day night sky fixed

- Simplified sky used hard-coded daylight blue; now uses map/view atmosphere color.
- Existing t1l1 save tested in isolation; fog on/off and normal sky checked.
- Engine ce1d5be3 installed in CP08-r1 and CP09-r1; 462 personal files unchanged.
- Details: checkpoints/CP09/night-sky.md. Natural playthrough acceptance remains open.

## Gemeinsame Spielstandliste (22.10.2026)

Operations hat einen Saved-Games-Zugang fuer AA/SH/BT, neueste Saves zuerst,
mit automatischem Kontextwechsel beim Laden. Native Ladevorgaenge fuer alle
drei Kampagnen getestet; CP08-r1/CP09-r1 aktualisiert, 456 persoenliche
Profildateien unveraendert. [Bericht](checkpoints/CP09/unified-saves.md).

## Ladeblende beim Kampagnenwechsel (22.10.2026)

Desktop-Startluecke durch eine separate Ladeblende abgedeckt. Alle sechs
Wechselrichtungen im Fenster und UHD-Vollbild sowie Aufloesungswechsel und
Abbruchbereinigung geprueft. In CP08-r1/CP09-r1 installiert; alle 456
persoenlichen Profildateien unveraendert.
[Bericht](checkpoints/CP09/context-cover.md).

## AB41-MG-Bluteffekte korrigiert (22.10.2026)

Exakte MG-Zuordnung und visuelle Waffenreferenz fuer besitzerlose Schuesse
korrigiert. AB41- und Breda-Tests inklusive Wunden-Save/Load bestanden.
In CP08-r1/CP09-r1 installiert; 439 persoenliche Profildateien unveraendert.
[Bericht](checkpoints/CP09/ab41-blood.md).

## Optionsmenue aufgeraeumt (21.10.2026)

DISPLAY & HUD, BLOOD EFFECTS und ADDITIONAL OPTIONS als klare Bereiche.
Alle elf Einstellungen erhalten; AA/SH/BT-Bedienung und 16:9/4:3/Ultrawide
geprueft. In CP08-r1/CP09-r1 installiert, 427 persoenliche Profildateien
unveraendert. [Bericht](checkpoints/CP09/options-layout.md).

## CP09 begonnen - Regression und separate Durchspielabnahme

Erste technische Runde: 44 unterschiedliche Prueffaelle, davon 40 ohne
Fehlschlag und vier mit exakt bekannten BT-Skriptdiagnosen. CP09-r1 ist lokal
startbar; 427 persoenliche Profildateien unveraendert. GPU-/Langzeitpruefung
und natuerliche Durchspielabnahme bleiben offen.

Nutzerfreigabe 20.10.2026: CP09 beginnen. Feature-freeze bleibt bestehen.
Technische Matrix in isolierten Profilen; danach beendet der Nutzer die
Kampagne mit seinem bestehenden Spielstand. Kein Reset, keine vorweggenommene
Gesamtabnahme und kein Merge. [CP09-Bericht](checkpoints/CP09/REPORT.md).

## Funktionsumfang abgeschlossen / Geschuetz-HUD korrigiert

Nutzerfestlegung vom 20.10.2026: Feature-complete, nur noch Bugfixes. CP09 ist
noch nicht als abgeschlossen oder vollstaendig durchgefuehrt freigegeben.
Abgeschnittene Namen stationaerer Waffen verbreitert, einschliesslich Modello 37.
[Bericht](checkpoints/CP08/emplacement-hud-names.md).

## Aktuell: LOADOUT-Schriftzug und Ego-Waffenflaechen

LOADOUT nutzt die generierte Schriftgrafik im Stil der anderen Hauptmenueschilder.
Bei breitem FOV offene Schaft-/Armrueckseiten werden in der Egoansicht geschlossen,
fuer alle Waffenherkuenfte. Acht Waffen je AA/SH/BT, alter AA-Testsave und native
Tuerbedienung geprueft. [Bericht](checkpoints/CP08/loadout-sign-viewmodels.md).

## Aktuell: LOADOUT-Tuer, Auswahlfilter und globale HUD-Kontur

Fruehere Multiplayer-Tuer mit Hover-Leuchten oeffnet LOADOUT. 37 waehlbare Waffen,
fuenf Sprenggranaten, keine Minendetektoren. HUD black outline standardmaessig aus,
sofort und kampagnenuebergreifend schaltbar. Nutzer bestaetigt vorherigen Waffen-
und Granatentest. [Bericht](checkpoints/CP08/loadout-hud-preferences.md).

## Aktuell: LOADOUT-Modellflaechen und Rauch-Effekte

FG42/G43/SVT-Materialien gegen fehlende Flaechen korrigiert; Sprite-Abhaengigkeiten kampagnenuebergreifend vervollstaendigt. Granaten-Sounds in AA/SH/BT ausgeloest, AA zusaetzlich bis OpenAL verfolgt; gemeldeter Tonausfall noch nicht reproduziert. [Bericht](checkpoints/CP08/loadout-models-effects.md).

## Aktuell: LOADOUT fuer Operations-Replays

43 tragbare Waffen aus AA/SH/BT, sieben Slots, echte 3D-Vorschau, DEFAULT und Zufallsauswahl. Nur abgeschlossene Operations-Replays; Mission List und neue Missionen unveraendert. Klassenweises Durchschalten zusaetzlicher Pickups. Native Waffen-, Kontext-, Speicher- und Fortschrittstests abgeschlossen. [Bericht](checkpoints/CP08/loadout.md).

## Aktuell: Statistik, AA-Briefings und Breda korrigiert

Breitere Kampagnenstatistik, echte AA-Briefings mit vorhandenem 16:9-Raumhintergrund und MG-Blutprofil fuer die stationaere Breda. Native Tests erfolgreich. [Bericht](checkpoints/CP08/stats-briefing-breda.md).

## Aktuell: Credits erst nach Berlin

AA-/BT-Finales setzen die gemeinsame Kampagne vor dem Abspann fort. Berlin behaelt Schlussvideo und Credits. [Bericht](checkpoints/CP08/campaign-finales.md).

## Aktuell: Hit-Flinch-Prozentregler

0 bis 100 Prozent in Zehnerschritten, alte Auswahl migriert, Abschnitt Additional Options. Alle Stufen in AA/SH/BT sowie Persistenz geprueft. [Bericht](checkpoints/CP08/flinch-percent.md).

## Aktuell: Drei Flinching-Modi und BT-Dropoption

Standardmaessig 20 Prozent Flinching; Off/Reduced/Original und BT drop restrictions im Optionsmenue, sofort wirksam und kampagnenuebergreifend gespeichert. [Bericht](checkpoints/CP08/flinch-modes-drop-options.md).

## Aktuell: Stabiler Stand und Speicherbereinigung

Nutzer bestaetigt aktuellen Stand als stabil. 172.23 GiB alte lokale Versionen und Testprodukte entfernt; aktuelle Installation und persoenliches Profil hashidentisch erhalten. Historische Auslieferungs-/Rollback-Pfade sind entfernt. [Bericht](checkpoints/CP08/storage-cleanup.md).

## Aktuell: Optionales Spieler-Flinching

Treffer-Kamerabewegung standardmaessig aus, in Allied Campaign Options schaltbar. Rotblendung bleibt erhalten. AA/SH/BT und kampagnenuebergreifende Speicherung geprueft. [Bericht](checkpoints/CP08/player-flinch.md).

## Aktuell: Moerser-Zielhilfe und lesbare Beschriftung

Roter Einschlagmarker mit echter Ballistik; vorhandener BT-Spielstand als Kopie geladen und erneut gespeichert. Boden-Probetreffer deckungsgleich. [Bericht](checkpoints/CP08/mortar-aim.md).

## Aktuell: Schrotflinte mit pelletweisen Bluteffekten

Neun Pellets erzeugen unabhaengige kleine Wunden und Tropfen; AA/SH/BT sowie toedliche Salve und Save/Load nativ geprueft. [Bericht](checkpoints/CP08/shotgun-blood.md).

## Aktuell: Einheitliche Menues und direkte Rueckkehr

AA-Oberflaeche fuer alle Kampagnen, rote CURRENT-Markierung und atomarer Main-Menu-Wechsel ohne Musik-Neustart. Sechs native isolierte Tests bestanden. [Bericht](checkpoints/CP08/shared-menus-navigation.md).

## Aktuell: Gemeinsamer Menuehintergrund

Nutzerbild in Operations, Mission List, Briefing Room und Allied Campaign Options integriert; vier native Ansichten geprueft. [Bericht](checkpoints/CP08/menu-background.md).

## Aktuell: Operations-Auswahl, Schwierigkeit und stille Score-Autosaves

Vier Nutzerkorrekturen implementiert und isoliert geprueft. [Bericht](checkpoints/CP08/operations-feedback.md).

## Aktuell: Neue Kampagnenkarten

Beide gelieferten Regionen installiert und mit 15 Missionsauswahlen nativ geprueft. [Bericht](checkpoints/CP08/user-map-art.md).

## Aktuell: Gelieferte HD-Inventarbilder und Sepia-Ladebild

Drei Uniformen und zwei Ausweise integriert; AA-Standardladebild in echtem 16:9. UHD-HUD und Ladebild nativ geprueft. [Bericht](checkpoints/CP08/user-hud-art.md).

## Aktuell: Zusammenhaengende Kopfwundprojektion

Kopfwunden folgen steilen Gesichtsfl�chen und ueberbruecken UV-Naehte. Kopf-Dreiecke liegen buendig auf der Haut statt einzeln angehoben zu werden; eigenes begrenztes Geometriebudget. Koerperprojektion unveraendert. [Bericht](checkpoints/CP08/head-wound-projection.md).

## Aktuell: Kopfwunden und Quicksave

Feine Kopfmeshes erhalten bei Budgetueberschreitung einen kleineren vollstaendigen Wundpatch. Speichern registriert lebende Actor-Modelle nicht erneut; Wunden behalten ihre Instanzzuordnung. Full-detail-Flag im tatsaechlichen LOD-Pfad korrigiert. Feste Speichergrenzen bleiben bestehen. [Ursachen und Nachweise](checkpoints/CP08/wound-regression.md).

## Aktuell: Menu font size skaliert ausschliesslich Schrift

100 Prozent Courier New Bold als Basis wiederhergestellt. Menu font size veraendert nur Text, nicht Menueflaechen oder Mausziele. HUD separat; bisherige kampagnenuebergreifende Einstellung bleibt erhalten. Siehe [Bericht](checkpoints/CP08/menu-polish.md).

## Aktuell: Menueschrift, Hover-Buttons und HD-Cursor

Menueschrift auf exakt 66 Prozent reduziert; getrennte Font-Aliase erhalten die HUD-Schriftgroessen. Quit und Back to Game zeigen beim echten Maus-Hover wieder transparente goldene Schrift. Neuer HD-Bronzecursor skaliert proportional zur Bildschirm-/Fensterhoehe, auch im SDL-Hardwarepfad. [Bericht und Testgrenzen](checkpoints/CP08/menu-polish.md).

## Aktuell: Richtungszeichen, Sonderanzeige und Missionszielfenster

Roter Richtungsmarker, offene/erledigte Zielrahmen und dezenter Zielfenster-Hintergrund hochaufloesend installiert. SH/BT-Flak-Farbmaske passt pixelgenau zum erneuerten Symbol. Native UHD-Pruefung in AA/SH/BT; separate Testprofile, alle 80 persoenlichen Profildateien unveraendert. Multiplayer-Symbole ausgenommen. [Bericht, Prompts und Testgrenzen](checkpoints/CP08/special-hud-upscale.md).

## Aktuell: Dynamische Fadenkreuze

Vier getrennte Linien mit Mittelpunkt und dunkler Kontur installiert. Die Oeffnung folgt der echten Waffenstreuung bei Bewegung, Dauerfeuer und Erholung, mit korrekter FOV-/Aufloesungsprojektion. Sie markiert den 95%-Bereich der gaussfoermigen Kugelstreuung; HUD-Groesse beeinflusst nur Strich/Punkt. AA/SH/BT, Full HD/UHD, Optiken und Save/Load geprueft; 80 persoenliche Profildateien unveraendert. [Formel, Nachweise und Grenzen](checkpoints/CP08/dynamic-crosshair.md).

## Aktuell: Hochaufloesende Waffengruppen

Sechs Waffengruppen mit je drei Zustaenden als 512x256-Metallreliefs installiert: vorhanden silbern, ausgeruestet bronze, nicht vorhanden dunkel. Originale Anordnung und Auswahlpuls erhalten. [Bericht und Prompts](checkpoints/CP08/weapon-group-upscale.md).

## Aktuell: Hochaufloesende optische Overlays

Sechs Texturen fuer Zielfernrohre, Fernglas, Kamera und Gasmaske installiert. Geometrische Masken mit originalen Zielmarkierungen rekonstruiert, Gasmaskenrahmen per Imagegen erneuert; Kamera verwendet jetzt ihre eigene Maske. [Bericht, Prompt und Testgrenzen](checkpoints/CP08/overlay-upscale.md).

## Aktuell: Hochaufloesende Stoppuhr und Zuendschnur

Nachkorrektur timers-r2 installiert: Metallkante entfernt und Seilmaterial am Anschluss vereinheitlicht; beide Varianten im UHD-HUD geprueft.

Fuenf Grafikebenen installiert, Zeigermittelpunkte und Schnuranschluss ausgerichtet. AA/SH/BT bei UHD/HUD 1.66 geprueft; Funken-/Rauchanimation und Countdown-Logik erhalten. [Bericht und Prompts](checkpoints/CP08/timer-upscale.md).

## Aktuell: Hochaufloesende Lebensanzeige

Vier abgestimmte Ebenen mit 128x512 Pixeln installiert. AA/SH/BT bei UHD und HUD 1.66 mit verschiedenen Gesundheitsstaenden und Aenderungsblitz geprueft; Spielstaende unveraendert. [Bericht, Prompts und Testgrenzen](checkpoints/CP08/health-upscale.md).

## Aktuell: Hochaufloesende Inventarsymbole

Nachkorrektur inventory-r3: Handbuch jetzt mit deutscher Beschriftung und originalnahem Layout; siehe [Bericht](checkpoints/CP08/inventory-manual-r3.md).

Vorherige Nachkorrektur inventory-r2: Drahtschneider mit korrekten Schneiden und Tiger-II-Handbuch mit Panzerzeichnung. UHD/HUD 1.66 visuell geprueft; Spielstaende und Einstellungen unveraendert.

15 Gegenstandsmotive und 32 Zaehlervarianten mit 512x512 Pixeln installiert; AA/SH/BT bei UHD und HUD 1.66 geprueft. Originalpositionen, Transparenz und Inventarlogik bleiben erhalten. Zwei Ausweise und drei Uniformen bleiben wegen Ablehnungen des Bilddienstes im Original. [Umfang, Prompts und Tests](checkpoints/CP08/inventory-upscale.md).

## Aktuell: Hochaufloesende Munitionsanzeige

19 Munitions- und Spezialanzeigen aus 18 transparenten Imagegen-Vorlagen vorbereitet. Originalgroessen und Patronenabstaende bleiben durch angepasste Texturkachelung erhalten. [Bericht und Testgrenzen](checkpoints/CP08/ammo-upscale.md).

## Aktuell: Hochaufloesender Kompass

Kompass nach Nutzerfeedback korrigiert: transparente Rose statt zweiter geschlossener Scheibe, einheitliche Proportionen und gemeinsamer Mittelpunkt mit dem runden Gehaeuse. Mehrere Blickrichtungen bei UHD/HUD 1.66 geprueft. [Bericht](checkpoints/CP08/compass-upscale.md). Multiplayer-Grafiken ausgenommen.

## Aktuell: Courier New fuer Menues und HUD

Courier New Bold jetzt mit natuerlichen Zeichenbreiten, Originalfarben und kleinem Schlagschatten. Engstellen in HUD, Steuerung, Zahlenfeldern und Mission List angepasst; native Menuepruefungen in AA/SH/BT sowie 4:3. [Umfang und Nachweise](checkpoints/CP08/courier-fonts.md).

## Aktuell: Mission List Highscore-Modus

Level-Complete zeigt das vorhandene Gemini-16:9-Bild mit Helm und Sonnenuntergang; der Statistikblock steht auf Nutzerwunsch links. Proportionale Darstellung bleibt erhalten; siehe denselben Bericht.

Getrennte Rekorde fuer Easy/Medium/Hard, letzter Levelscore, native Kampfwertung und Abschlussstatistik. Speichern/Laden waehrend eines Laufs gesperrt. [Regeln und Nachweise](checkpoints/CP08/highscore.md).

## Aktuell: Gesperrte Levels und Briefing-Auswahl

Alle Levelplaetze bleiben sichtbar; nicht abgeschlossene Levels sind rot als LOCKED gesperrt. Briefing Room bietet die wachsende Auswahl freigeschalteter Originalbriefings. [Bericht](checkpoints/CP08/unlock-menus.md).

## Aktuell: Briefing Room und einzelne Level wiederholen

Briefing Room folgt dem regulaeren Fortschritt. Mission List zeigt abgeschlossene Einzel-Levels mit Schwierigkeit je Start; Replay endet im Hauptmenue und schuetzt Kampagnenfortschritt/Saves. Native Tests und Grenzen: [Bericht](checkpoints/CP08/level-replay.md).

## Aktuell: Einheitliche Hauptmenue-Schriftzuege

Acht weitere transparente Beschriftungen im freigegebenen Operations-Stil erzeugt und fuer AA/SH/BT eingebaut. Native Bildtests bestanden; Operations-Ausrichtung erhalten. [Bericht und Prompts](checkpoints/CP08/menu-lettering.md).

## Aktuell: Operations-Schriftzug und Kopfzeile

Reset Progress oben rechts; Previous/Next entfernt. Transparenter OPERATIONS-Schriftzug mit dem eingebauten Bildgenerator im Stil der Originalschilder erstellt. [Prompt und Bericht](checkpoints/CP08/operations-sign.md).

## Aktuell: Operations und Reset Progress

Hauptmenue-Schild zeigt Operations. Reset Progress in der Einsatzkarte verlangt eine separate Bestaetigung und behaelt Saves/Optionen. Isolierte Tests pruefen Abbrechen, Reset und Neustart; aktiver Nutzerfortschritt bleibt unberuehrt. [Bericht](checkpoints/CP08/operations-reset.md).

## Aktuell: AA-Medaillen in 16:9

Medaillenkasten und Reset-Dialog auf 960x540 angepasst, Medaillen proportional erhalten. Native Full-HD- und 4:3-Tests bestanden. [Bericht](checkpoints/CP08/aa-medals-wide.md).

## Aktuell: Restbilder fuer Single-Player

46 vollstaendige Hintergruende fertig; AA-Hilfeseite mit Gemini 3.8 Flash / High ergaenzt. Drei vorhandene breite SH-Abschlussgemaelde werden mit unveraenderten Einblendzeiten bildfuellend dargestellt. Native Sichtpruefungen bestanden. Multiplayer- und Kalibrierungsbilder bleiben ausgenommen. [Bericht](checkpoints/CP08/remaining-art.md).

## Aktuell: Gemeinsame Kampagnenoptionen

Grafik, Audio, Maus-/Joysticksteuerung, HUD und normale/Alt-/Strg-Belegungen werden gemeinsam gespeichert. Native AA -> SH -> BT -> AA-Wechsel und drei Neustarts bestanden; Spielstandszeiger und Missionsstatistik bleiben getrennt. [Bericht](checkpoints/CP08/shared-preferences.md).

## Aktuell: Vollstaendige 16:9-Hintergruende

Alle 45 ausgewaehlten Hintergruende verwenden jetzt das vollstaendige Bild ohne Originalzentrum. Drei neue Ladebilder stammen direkt vom Nutzer (m4l1, m4l2, m5l2). Bedienelemente bleiben unveraendert; die optische Menueausrichtung beurteilt der Nutzer im Anschluss. [Bericht](checkpoints/CP08/widescreen-fullframe.md).

## Aktuell: Widescreen-Single-Player-Paket installiert

42 von 45 ausgewaehlten SP-Hintergruenden sind fertig und installiert, 30 davon neu. Gemini 3.8 Flash / High, neue Chats und serielle Generierung. Drei AA-Vorlagen wurden von Gemini abgelehnt und bleiben original; keine Multiplayer-Bilder erzeugt. AA-/SH-/BT-Nachtests bestanden, Originale und alle 80 Nutzerdateien unveraendert. [Bericht und offene Bilder](checkpoints/CP08/widescreen-singleplayer.md). SH-/BT-Ladezoom bleibt erhalten.

## Aktuell: Single-Player und Jeep-MG

Multiplayer ist in AA, SH und BT nicht mehr anwaehlbar; alternative Menue-, Verbindungs- und Kartenaufrufe werden abgewiesen. Das echte m1l3a-Jeep-MG erzeugt jetzt die freigegebenen Bluteffekte. Native Tests bestanden, in CP08-r1 installiert, 80 Nutzerdateien unveraendert. [Bericht](checkpoints/CP08/singleplayer-jeep.md). Gemini-Bildarbeit wird mit 3.8 Flash / High und einem neuen Chat pro Bild fortgesetzt; Multiplayer-Bilder sind ausgeschlossen.

## Aktuell: SH-/BT-Ladebilder vergroessert

Alle neun SH- und elf BT-Kampagnenladebilder werden auf Breitbild proportional vergroessert und zentriert. Motive, Fotorand und Ladeanzeige bleiben erhalten; in 4:3 bleibt der urspruengliche Ausschnitt. In CP08-r1 installiert, elf isolierte native Prueflaeufe bestanden. Keine neuen KI-Bilder erforderlich. [Nachweise](checkpoints/CP08/loading-zoom.md). Die 36 weiteren Gemini-Hintergruende des vorherigen Auftrags bleiben offen.

## 16:9-Bilder, vorheriges Teilpaket

Zwoelf Gemini-/Nano-Banana-Erweiterungen sind im CP08-r1-Startstand eingebaut: drei Hauptmenues, AA-Briefing-/Missionsraum, AA-Optionshauptmenue und sechs AA-Ladebilder. Originalzentren und Bedienelemente bleiben erhalten. 36 weitere ausgewaehlte Hintergruende sind offen; Gemini meldete ein Kontingentlimit bis 15.10.2026, 00:32 Uhr. Kein vollstaendiger Abschluss des Bildauftrags. [Umfang, Nachweise und Fortsetzung](checkpoints/CP08/widescreen-art.md).

## Aktuelle Korrektur: MG-Ruckler

Der Kartenhinweis ist entfernt. Lokale Wundreferenzen verhindern den bei MG-Dauerfeuer reproduzierten Nachrichtenstau. Drei MG-Nachtests halten 50-ms-Snapshots; Save/Load und 36 AA-/SH-/BT-Durchschussvergleiche bestanden. [Bericht und Grenzen](checkpoints/CP08/mg-feedback.md).

## Aktuelles Feedback: CP08-r1

Hauptmenue-Karte ersetzt die alte Missionsauswahl; nur zwei Regionen und ausschliesslich freigeschaltete Einsaetze. Blut/Wunden waehrend der Sterbeanimation mit durchdringenden Kugeln. 72 gepaarte Schadensvergleiche in sechs nativen Laeufen bestanden. [Aenderungen, Nachweise und Grenzen](checkpoints/CP08/feedback-two-regions.md). Die folgenden sechs-Ansichten-/vier-Zustaende-Angaben beschreiben historische Staende.

## Fortsetzung bis CP8

CP6 bis CP8 sind als technische Kandidaten implementiert. CP6-/CP7-CI bestanden; alle 54 Karten starten mit Save-Ausgabe. CP7: 15 synthetische Abschlussgrenzen mit korrektem Fortschritt, getrennte Wiederholungen, Save-Metadaten und Wiederherstellung. CP8: geografische Einsatzkarte mit 15 Operationen, vier Zustaenden und sechs Ansichten; native Menuepruefungen in Full HD, 4K, 4:3 und Ultrawide bestanden. Continue Campaign und FOV 90 ueber Programmneustart und SH-zu-AA-Wechsel bestaetigt. [Start](CP08-r1-START.md), [Nachweise und Grenzen](checkpoints/CP08/REPORT.md). Natuerliche Vollabnahme bleibt offen.

# Status

Aktueller Auftrag: autonom bis einschliesslich CP8. Missionslader, chronologische Progression und Einsatzkarte sind implementiert und technisch geprueft. Persoenliche Abnahme, vollstaendiger natuerlicher Kampagnendurchlauf und Merge werden nicht unterstellt. Die folgenden Eintraege dokumentieren vorherige Lieferstaende.

Stand 14.10.2026 nach Menuefeedback: **CP05a-r3 benennt das gemeinsame Zusatzmenue in Allied Campaign Options um und liefert ein mittiges 16:9-Layout ohne ueberlappende Bedienelemente.** [Startdateien](CP05a-r3-START.md), [Pruefbericht](checkpoints/CP05a/r3/REPORT.md). Getrennte Bereiche fuer Display/HUD und Effekte; die Seite bleibt beim Verstellen ihrer Regler stabil. 56 Nutzerdateien aus r2 uebernommen. Quelle `5a9b6aa7e9877d4fb3dd328838d9ab4940deb5ce` remote verifiziert. Keine persoenliche Abnahme oder Merge unterstellt.

Stand 14.10.2026 nach BT-Strassenfeedback: **CP05a-r2 korrigiert fehlende Blutspuren auf der erdigen Strasse im Breakthrough-Test.** [Startanleitung](CP05a-r2-START.md), [Vorher/Nachher und Pruefbericht](checkpoints/CP05a/r2/REPORT.md). Die sichtbare gekruemmte Strasse lag knapp unter der Kollisionsflaeche; die begrenzte Projektion gleicht dies jetzt aus. 47 Nutzerdateien aus CP05a-r1 uebernommen. Quellstand `a3c13d93689f47044c5fa6e79ea10b723135c162` frisch remote verifiziert. Persoenliche Abnahme und Merge bleiben offen.

Stand 14.10.2026 nach weiterem Nutzerfeedback: **CP05a-r1 liefert 30 Sekunden sichtbares und 1,5-mal groesseres Weltblut, korrigierte Boden-/Wandprojektion und optische Leichentreffer in AA/SH/BT.** [Neue Startanleitung](CP05a-r1-START.md), [Pruefbericht und Grenzen](checkpoints/CP05a/REPORT.md). 47 Einstellungs-/Spielstandsdateien aus r2 wurden unveraendert uebernommen. Quellstand `08e6aba4aabb7e9d9cafa50d9df0e7f6118dd571` ist auf GitHub frisch verifiziert; Entwurfs-PR #8. Die neueste Nutzeranweisung erweitert die fruehere CP5-Grenze um Leichentreffer. Persoenliche Abnahme, vollstaendige Checkpointmatrix und Merge bleiben offen.

Stand 14.10.2026 nach Nutzerfeedback: **CP05-r2 korrigiert sichtbare MP1-Partikel/Weltflecken, die Charakterbeleuchtung der Wunden und die Zentrierung der Briefings.** [Neue Startanleitung](CP05-r2-START.md), [Korrekturbericht](checkpoints/CP05/r2/REPORT.md). Einstellungen und Saves aus r1 wurden in ein getrenntes Profil kopiert; r1 und Originaldaten bleiben unverändert. Der Korrektur-Quellstand `89437fe58fc41a4d11b21e0a762560bced56c12a` wurde auf GitHub frisch verifiziert. Persönliche Abnahme und Merge bleiben offen.

Vorheriger Stand 14.10.2026: **Die Features bis einschließlich CP5 sind als CP05-r1 implementiert und lokal spielbereit.** Vollständige technische Abnahme, persönliche Nutzerabnahme und Merge sind getrennt davon und bleiben offen. Die autonome Fortsetzung bis CP5 sowie englische Spieloptionen wurden im Chat freigegeben. Keine weitere „mach weiter“-Bestätigung erforderlich; CP5a und Kampagnenarbeit bleiben außerhalb des Auftrags.

Vorheriger Einstieg: [CP05-r1 starten](CP05-r1-START.md). Quellstand der Engine: `c0f6342352b2971f52c462574e528f58edf9220b`. [CP5-Bericht](checkpoints/CP05/REPORT.md) und die zugehörigen JSON-Nachweise enthalten Binärhashes, Testbedingungen, lokale Paketsicherung und Grenzen.

| Bereich | Lieferstand |
| --- | --- |
| CP1 | HUD-/Schriftskalierung, proportionale Menüs/Kompass, sichere Ränder und gespeicherte Größen; neue Spieloptionen Englisch. Erneut geprüft in AA 4K, SH Full HD und BT Ultrawide, einschließlich Save/Load. |
| CP2 | Roter menschlicher Treffernebel; genaue gemeinsame Waffenfreigabe, gespeicherter eigener Schalter. |
| CP3 | Originale lokale MP1-Bluttexturen, kollidierende Tropfen und präzise Weltflecken; aktuelle Zielkörper/Ausrüstung blockieren im CP5-Stand zusätzlich geometrisch. |
| CP4 | Kleine Pistolen-/MP-Eintritte, große Gewehr-/MG-Eintritte, deformierbare Meshbindung und unveränderte gespeicherte Wundorientierungen. |
| CP5 | Große geometrisch bestätigte Austritte für alle vier Gruppen, getrennte Zufallsorientierung, begrenzte Arm-/Streifintervalle und kompatibles Lesen von CP4-Wundsaves. |

Echte native Schüsse aus drei Richtungen in allen drei Spielkontexten, Regionen-/Wand-/Todestests, getrennte Effektschalter, Schrotflinten-Ausschluss und Save-Migration sind dokumentiert. Der isolierte Transformationslauf umfasst 65.536 Seeds. Die echten Startdateien teilen alle sieben UI-/Effekteinstellungen zwischen AA, SH und BT; die neuen Nutzerprofile stehen wieder auf Standardgrößen, aktivierten Effekten und FOV 90.

Verbleibende Grenzen: keine vollständige Kombination sämtlicher WCR-Varianten und aller Waffen, keine umfassende Mehrgegner-/Hindernis-Lastmatrix, kein vollständiger deterministischer End-to-End-Nachweis aller Gameplay-Zufallsfolgen, keine echten Windows-DPI-/Alt-Tab-Wechsel und kein GL2-Test. Frühe Diagnosen und fehlgeschlagene Teiltests sind in den Berichten ausdrücklich als solche gekennzeichnet. Keiner dieser Punkte wird als bestanden ausgegeben.

Originalinstallation, _forCodex, MP1-Eingaben und ältere Kandidaten bleiben unverändert. CP05-r1 besitzt ein CRC-/SHA-geprüftes lokales Laufzeitpaket; Originalassets und Saves werden nicht nach GitHub übertragen. CP0a-Drops bleiben integriert; der vom Nutzer übersprungene BT-Finaltest wurde nicht nachträglich als bestanden erklärt.

Privates Projekt: Entwurfs-PRs #1 CP0, #2 CP0a, #3 CP1, #4 CP2, #5 CP3, #6 CP4 und #7 CP5. Keine Merges ausgeführt. Push-/CI-Nachweise und abschließende Sicherung werden unter CP05 geführt.
