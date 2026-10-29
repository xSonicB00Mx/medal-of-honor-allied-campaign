# CP09 – Regression und Abnahmekandidat

Begonnen am 20.10.2026 auf Nutzerauftrag. Feature-freeze: nur Fehlerkorrekturen,
Pruefung und Auslieferung. Der Nutzer uebernimmt anschliessend den natuerlichen
Kampagnenabschluss mit seinem bestehenden Spielstand.

**Status: erste technische Runde abgeschlossen, CP09 insgesamt weiterhin offen.
Keine Gesamtspielabnahme, kein Merge.**

Nachtrag 29.10.2026: [Lokale Beleuchtung und Partikel](lighting-particles.md).
Nutzerauftrag zu Vorschlaegen 1/4/5: Lichtgitter-Proben fuer Modelle,
verdeckte dynamische Lichter und beleuchtete Soft Particles mit eigener
Optionsseite. AA/SH/BT, Save/Load, Live-Optionen, Grafikneustart, UHD,
Decke/Drehtuer, GPU-Partikelpruefungen und Normandy-Boot bestanden.

Nachtrag 29.10.2026: [Schatten durch Waende korrigiert](model-shadows.md).
BSP-/statische Levelblocker unabhaengig von der Kamerasicht, aktuelle
Brushmodell-Transformationen, Lichtseiten- und Filtertap-Pruefung.
Nativer Deckendurchschlag vorher reproduziert, danach 0 fehlerhafte Pixel
bei erhaltener Bodenschattenkontrolle. GPU-, AA/SH/BT-, Normandy- und UHD-Tests
bestanden. Engine 1f269954 in CP08/CP09 installiert, 551 Profildateien unveraendert.

Nachtrag 29.10.2026: [Schattenkontakt auf dem Normandy-Boot](model-shadows.md).
Kamerapixelabhaengigen Tiefenbias durch Empfaengerebenen in Lichtprojektion
ersetzt. 48 GPU-Faelle, fuenf Bootswinkel mit getrennten Effekten, AA/SH/BT,
Save/Load, Renderer-Neustart und UHD geprueft. Engine 6916445b in CP08/CP09
installiert; 535 persoenliche Profildateien unveraendert.

Weiterer Nachtrag 29.10.2026: [Schwebende Prop-AO und Distanzstabilisierung](ambient-occlusion.md).
Statischer TIKI-Massstab korrigiert, validierte zeitliche Rueckprojektion ergaenzt.
Schreibmaschine, Tiefenabgleich, GPU-Distanz-/Verlaufstests, AA/SH/BT, Kamerawinkel,
Renderer-Neustart, UHD und Modellschatten geprueft. Engine 1ecbe66e in CP08/CP09
installiert, 535 persoenliche Profildateien unveraendert.

Nachtrag 29.10.2026: [AO-Blickwinkel-/Kantenkorrektur](ambient-occlusion.md),
geometrische Normalen fuer Umgebungsmodelle, stabilere Integration und
Silhouetten-Tiefenabgleich. AA/SH/BT, Brueckenregression, Kameraschwenks und UHD
geprueft; regulaere CP08-/CP09-Engine aktualisiert, 535 Profildateien unveraendert.

Weiterer direkter Nutzerauftrag vom 28.10.2026: [Hochwertige Ambient Occlusion](ambient-occlusion.md),
GTAO-basierter GL1-Pass, gemeinsame Option und isolierte Spielpruefungen.

Neuer direkter Nutzerauftrag vom 28.10.2026: [Dynamische NPC-/Pickup-Schatten](model-shadows.md),
GL1, gemeinsamer Live-Schalter und isolierte AA/SH/BT-/UHD-Pruefungen.

Nachtrag auf direkten Nutzerauftrag: [Roemische Missionsnummern in Operations](operations-roman.md),
sechs native Menuepruefungen bestanden, in CP08-r1 und CP09-r1 installiert.
Arabische Gruppenanzahlen und persoenlicher Fortschritt bleiben erhalten.

Nachtrag 21.10.2026: [Optionsmenue aufgeraeumt](options-layout.md), drei klare
Bereiche und kompakte Werte. Native Darstellungs-/Bedientests in AA/SH/BT
bestanden; fuer CP08-r1 und CP09-r1 installiert.

## Festgelegte Basis

- Ausgangsbranch `codex/cp08-operations-map`, Commit `880b3df1`.
- Inhalts-/HUD-Quellen `1354fb7e`; Engine/game/cgame `b5573702`.
- WCR-Fingerprint `3b6b38b5b04ba320a526196946c44394c4519e4197dc8d3d05788e186501cfcc`.
- Sieben aktive WCR-Module: AA Main/Bash/Reflections, SH Main/Reflections,
  BT Main/Reflections. Die originale Versionsnummer ist nicht belegt.
  Lose Eingaben sind im lokalen Manifest erfasst.
- Lokale BT-Dropintegration bleibt aktiv. Urspruengliche Patch-PK3:
  `d4122611afec4bb317eef1026f256cd0e1aa87fc85268218ceb19df71fb225fd`.
  Transport-ZIP, Autor und genaue Version waren beim damaligen Import nicht
  verfuegbar. Der ZIP-Erstimport aus dem Plan ist weiterhin nicht getestet.
- 9.072 Originaldateien, 9.000 Runtime-Basisdateien und 86 Moddateien werden
  gegen ihre gespeicherten Hashes geprueft. Persoenlicher Profilbaum vor
  und nach der nativen Matrix verglichen.

## Pruefverfahren

`tools/run_cp09.py <eindeutiger-laufname>` fuehrt native Tests seriell aus.
Alle Testprofile sind getrennt. Fortschritts-/Save-Sentinels pruefen Replay-
Grenzen. Installierte Binaerdateien muessen mit dem aktuellen Build
uebereinstimmen. Historische Menue-/Finale-/Flinch-Pakete werden in der
CP09-Runde nicht mehr als Test-Overrides eingesetzt.

Jeder Test bekommt eigenes Log und Windows-Prozessspeichermessungen.
Fehlschlaege bleiben erhalten, auch nach bestandenem Wiederholungstest.
Grenztests mit gesetztem Testfortschritt sind kein natuerlicher Durchlauf.
Ergebnis: 46 Werkzeuglaeufe fuer 44 unterschiedliche Faelle. 40 Faelle ohne
Fehlschlag, vier BT-LOADOUT-Faelle mit den exakt bereits dokumentierten drei
Skriptfehlern. Der erste AA-Droptest hatte faelschlich BT-spezifische
Diagnoseausgaben erwartet; korrigierter Wiederholungstest bestanden.
Die urspruenglichen Fehlschlaege bleiben im Ergebnisbericht erhalten.

Nachweise in [regression.json](regression.json):

- AA/SH/BT: Menue-Rueckkehr, Schrotflintenpellets, Kopf-/Koerperwunden mit
  Save/Load, BT-Dropumschaltung und AA/SH-Isolation.
- Scorekampf inklusive stiller Autosaves und Save-/Load-Sperre, Abbruch ohne
  Punkte, Operations-Replayabschluss mit geschuetztem Kampagnenfortschritt.
- Alle drei Spiele: LOADOUT-Replay, neue Mission, Score, DEFAULT und gesperrte
  Mission. AA/SH ohne Skriptfehler; BT-Funktionsassertionen bestanden, bekannte
  Skriptdiagnosen separat in [known-bt-e3l3.json](known-bt-e3l3.json).
- Gemeinsame Einstellungen AA -> SH -> BT -> AA plus frische Neustarts.
- Fadenkreuze bei 3840x2160, 1280x960 und 3440x1440; Projektionsabweichung im
  Testprotokoll kleiner 0,002 Pixel. Nativer AA-HUD- und BT-Operations-Screenshot
  visuell kontrolliert. Kein physischer Monitor-/DPI-Wechseltest.
- Finale-Grenzen AA/BT setzen fort; Berlin startet debriefing.roq, dessen
  unveraenderter Skriptpfad anschliessend die Credits aufruft.
- Zehn Save-/Load-Zyklen mit einer Bytekopie des aktuellen persoenlichen
  BT-Quicksaves: elf erfolgreiche Ladevorgaenge inklusive Erstladen.
  Private Bytes nach Aufwaermphase um rund 17,6 MiB niedriger; kein fortlaufender
  Anstieg in diesen zehn Zyklen. Keine allgemeine Langzeit-Leakgarantie.
- 427 persoenliche Profildateien unveraendert; alle Original-/Runtime-Hashes
  vor und nach beiden Runden unveraendert.

### MG-Belastung

AA m1l1, echte montierte MG42, lebendes Ziel und mehrere Sterbeereignisse;
1920x1080, 60-FPS-Limit, GL1, RTX 4090, NVIDIA 610.88. CPU-Identifier:
AMD64 Family 26 Model 68 Stepping 0. `com_speeds`-Millisekunden:

| Phase | Effekte | Frames | Median | P95 | P99 | Maximum |
|---|---:|---:|---:|---:|---:|---:|
| Dauerfeuer | aus | 374 | 2 | 3 | 3 | 9 |
| Dauerfeuer | an | 374 | 3 | 5 | 5 | 6 |
| Sterbephase | aus | 406 | 2 | 3 | 4 | 8 |
| Sterbephase | an | 406 | 3 | 4 | 5 | 6 |

Snapshotabstand maximal 50 ms, keine Skript-/Command-Overflow-Fehler.
Wundarchive vor/nach Laden identisch: aus 6/6 vorhandene Datensaetze,
an 64/64 Datensaetze am festen Budget. Debugausgabe erst fuer den
anschliessenden Archivtest aktiviert, nicht waehrend der Zeitmessung.
CPU-Wandzeit inklusive moeglicher Treiberwartezeit, keine GPU-Queryzeit.

Vorhandene C++-Tests: 65.536 Orientierungsseeds, getrennte Ein-/Austrittsfolgen,
Spiegelung, begrenzte lokale Ereignisspeicherung, geometrische Negativfaelle.
Kein Ersatz fuer den nativen Vergleich saemtlicher Gameplay-Zufallsfolgen.

## Installation und Rueckbau

`tools/cp09_candidate.py` erzeugt einen unabhaengigen lokalen Kandidaten aus
der **bereits importierten und zusammengefuehrten**, hashgeprueften Runtime.
Kein Netzwerkzugriff, keine Archive zur Laufzeit, keine Originalaenderung,
keine Profilkopie. Bytekopien statt Hardlinks/Junctions.

Erst nach vollstaendiger Pruefung wird der Staging-Ordner aktiviert.
Unterbrochene Kopien sind explizit fortsetzbar. Erneute Einrichtung desselben
Standes veraendert nichts. Abweichende Dateien werden gemeldet. Rueckbau
prueft zuerst alle Dateien und entfernt nur bekannte Moddateien.

Einrichtungs-/Rueckbautest bestanden: Unterbrechung nach 25 Dateien,
Wiederaufnahme, unveraenderte zweite Einrichtung, Ablehnung einer veraenderten
Moddatei, Rueckbau mit 9.000 unveraenderten Basisdateien und Save-Sentinel.

Gefundener Fehler: interne `Start-AA/SH/BT.cmd` verwiesen noch auf CP05a-Starter
ausserhalb der Runtime. CP09 bekommt eigenstaendige relative Starter.
Der normale CP08-Spielstarter war davon nicht betroffen.

`runtime-local/CP09-r1` ist erstellt und hashgeprueft: 9.000 Basisdateien und
90 eigene Dateien inklusive vier neuer Starter-/Inventar-/Hinweisdateien.
Nativer Start aus diesem Kandidaten, AA->BT-Prozesswechsel und Laden der Kopie
des aktuellen BT-Spielstands bestanden; keine CP08-Runtime im Suchpfad.
`Start-CP09-r1.cmd` im Workspace verwendet das bestehende persoenliche Profil.
Details: [INSTALLATION.md](INSTALLATION.md), [PLAYER-TEST.md](PLAYER-TEST.md).

Dies ist ein lokaler Wiederherstellungs-/Kandidatenweg, **kein universeller
Installer fuer beliebige rohe Spiel-, WCR- und ZIP-Bestaende**.

## Offene Abnahmegrenzen

- Natuerlicher Durchlauf, restaurierte WCR-Skriptketten und finales Berlin.
- Separate GPU-Timer-/Present-Messungen. `com_speeds` misst CPU-Wandzeit
  einschliesslich moeglicher Treiberwartezeit, keine GPU-Frametime.
- Langzeitmessungen und vollstaendiger kombinierter Waffen-/Leichen-/
  Oberflaechen-/Drop-/Gameplay-Zufallsvergleich.
- Erstinstallation aus nicht referenzierten Eingaben. Fehlende/abweichende
  WCR- oder BT-Dateien werden nicht durch andere Fassungen ersetzt.
- GL1 geliefert/nativ geprueft; keine GL2-Abnahme.

CP09 erst nach fehlenden technischen Nachweisen und getrenntem natuerlichen
Durchlauf als vollstaendig abgeschlossen bezeichnen.
