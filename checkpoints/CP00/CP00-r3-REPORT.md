# CP00-r3 – Spearhead-Ereigniszuordnung

13.10.2026. **Technisch geprüfter Teilkandidat auf der bisherigen WCR-Basis.** CP0 bleibt offen, kein Merge und kein CP0a. CP00-r2 und seine bestätigten Nutzerprofile bleiben erhalten. Bei der Abschlussprüfung wurden abweichende WCR-Dateien in der Originalinstallation gefunden; Der Nutzer hat die bewusste Aktualisierung bestätigt und ihre künftige Verwendung beauftragt; sie wird separat für r4 erfasst. Diese Dateien wurden nicht in r3 übernommen.

## Korrektur und Referenz

Die WCR-Karte t1l2 sendet zweimal `explosionoffset` an `ThrobbingBox_ExplodePlayerFlak88`. OpenMoHAA besitzt Setter und archiviertes Vektorfeld, hatte den Setter jedoch nicht in der Ereignistabelle registriert. Eine zusätzliche Zuordnung in `code/fgame/Entities.cpp` stellt die Annahme des Befehls wieder her.

**Korrektur der vorherigen Einordnung:** Ein unbenutztes Offsetfeld allein beweist hier keinen zusätzlichen Kompatibilitätsfehler. Die lokale originale Spearhead-DLL wurde statisch geprüft: Ihre Ereignistabelle bindet den Setter, dieser speichert den Vektor; ihre Explosionsroutine verwendet trotzdem die bisherige Effektposition und den festen Schadensversatz von 128. Deshalb bleiben Effektposition, Schadensradius/-höhe, Modelle, WCR-Skripte und Saveformat unverändert. Kein erfundener neuer Versatzmechanismus.

Referenz ist ausschließlich `mainta/gamex86.dll` aus dem geschützten lokalen Snapshot, SHA-256 `33f8c707da12d746b474634f11ce1701c53ebe7cd74d71904c453811eb5d7ec7`. Lokale Analyse mit vorhandenem MSVC dumpbin 14.44.35228.0: Ereigniskonstruktor über Zeichenkette und Response-Tabelle zugeordnet, Setter und Explosionsroutine untersucht. Tabelleninitialisierung bei VA `0x310A7450`, Setter `0x310A8240`, Explosionsroutine `0x310A7610`, konstante Höhe 128 bei `0x311CE4E0`. Disassemblat und Fremdbinärdatei bleiben ausschließlich lokal. Dies ist ein statischer Vergleich, kein erfolgreicher Originalengine-Spieltest. Ein zusätzlicher SH-Startversuch endete mit Code 0 ohne beobachtete Spielszene/SH-Log.

## Regressionstest

`tools/test_cp00_explosionoffset.py` startet t1l2 in einem neuen Profil, setzt zwei unterscheidbare Vektoren auf zusätzliche Test-Flakladungen, speichert, startet den Prozess neu und lädt erneut. Der nur lokal gebaute `tools/cp00-save-probe` liest die selbst erzeugten Saves mit dem unveränderten Engine-Decoder und zählt die beiden Vektoren. Anschließend werden nur die Testladungen mit Schaden 0 ausgelöst; beide gespeicherten Callbacks müssen laufen. Keine Missionsflags und keine originalen Flakobjekte werden künstlich abgeschlossen.

Negativkontrolle auf CP00-r2 bestanden: vier abgewiesene Offsetbefehle (zwei Karte, zwei Test), beide Vektoren vor/nach Laden nicht archiviert, beide Test-Detonationscallbacks ausgeführt. `offset-r2-control-v2.json`. Erster Versuch `offset-r2-control.json` scheiterte an der Testskript-Syntax eines negativen Vektorliterals; mit der von WCR verwendeten Zeichenkettenform korrigiert. Dieser fehlgeschlagene Versuch bleibt erhalten.

Positivkontrolle auf r3 bestanden: keine abgewiesenen Offsetbefehle, beide Vektoren jeweils einmal vor und nach Prozessneustart/Laden archiviert, beide Test-Detonationscallbacks ausgeführt. `offset-r3-accepted.json`. Eine vollständige natürliche Spreng-/Missionsabnahme ist damit weiterhin nicht behauptet.

## Build und Lieferung

Sauberer Quellcommit und Engine-Revision: `af7bb7c6e706fcc64e5933a22457333274f3de22`. Lokaler vollständiger VS2022-x64-Build in `build-local/cp00-r3`, RelWithDebInfo, erfolgreich. `CP00-r3-build.json` ordnet alle Binärhashes zu. Gegenüber der r2-Engine ist genau eine Ereigniszuordnung geändert. Spätere Testwerkzeug-/Berichtcommits erfordern keinen neuen Engine-Build.

GitHub-CI dieses Quellstands: Pushlauf `38471264421` und PR-Lauf `38471270920` erfolgreich. Die CI baut ohne Originalassets; sie ersetzt die lokalen Spieltests nicht. Quellstände werden im privaten Arbeitsbranch gesichert, nicht nach main übernommen.

In **AA, SH und BT** bestanden: tatsächliche Workspace-CMD gestartet ohne fs-Pfadüberschreibung im Test, bisherigen Referenzsave geladen, neuen Save durch den SAVE-Menücallback mit Vorschaubild erzeugt, Prozess beendet, denselben neuen Save geladen, FOV 90 aus dem frischen Prozess bestätigt. Die drei gerenderten Speichermenüs wurden einzeln visuell geprüft: Hintergrund, Missionsbild, bisheriger und neuer Saveeintrag sichtbar. Nachweise: `CP00-r3-{AA,SH,BT}-launcher-test.json`.

Laden erfolgte im automatisierten r3-Test per Konsolenbefehl; Mausklicks auf die Schaltflächen wurden in dieser Runde nicht wiederholt. Der vorherige r2-Maus-/Nutzertest bleibt ein eigener Nachweis. Fenster 1280×960, 60 FPS, GL1/OpenAL, Netzwerk im Test aus. Die Profile behalten FOV 90; `developer` wurde nach Sicherung der getesteten Konfiguration von 1 auf 0 zurückgestellt. Diagnose-Flakobjekte liegen ausschließlich im getrennten Offset-Testprofil, nicht in den AA-/SH-/BT-Nutzerprofilen.

Der isolierte Rückbautest hat die 17 eigenen Dateien nur aus einer neuen Runtime-Kopie entfernt; danach blieben exakt 8992 WCR-/Spieldateien übrig, Profile und eigentlicher r3-Kandidat unverändert (`CP00-r3-rollback-result.json`). Das lokale Paket enthält Originalspieldaten und wird niemals nach GitHub hochgeladen. Es ist eine unabhängige lokale Kopie, keine zusätzlich gegen dieselben Schreibrechte geschützte/externe Sicherung.

## Abweichende Originaleingaben

Die gewöhnliche Abschlussprüfung brach korrekt beim ersten abweichenden Originalhash ab. Die anschließende Vollprüfung aller 9064 erfassten Dateien fand fünf veränderte WCR-Pakete (`AA_Pak1-Main`, `SH_Pak1-Main`, `SH_Plus-Reflections`, `BT_Pak1-Main`, `BT_Plus-Reflections`) sowie `Uninstall-WCRestored.bat`. ZIP-Inhalte unterscheiden sich tatsächlich, nicht nur Kompressionsdaten. Der Nutzer bestätigte im Chat die bewusste Aktualisierung und beauftragte die neue Fassung als künftige Basis. Aus Dateizeitstempeln wird kein Änderungszeitpunkt abgeleitet.

Die unabhängige Eingangssicherung hat weiterhin **9064 von 9064 korrekten Hashes**. r3 stimmt mit deren 8992 ausgewählten Inhaltsdateien überein. `verify_cp00_delivery.py --snapshot-only` sichert ausschließlich diesen vorhandenen Kandidaten und erfasst die sechs Originalabweichungen ausdrücklich; ohne diesen Modus verweigert das Werkzeug bei Originalabweichungen weiterhin die Paketierung. Der Modus übernimmt keine abweichenden Dateien und lockert weder Snapshot- noch Runtime-Hashprüfungen. Deshalb gilt **nicht** mehr „Originalinstallation unverändert“. Nachweise: `CP00-r3-input-recheck.json`, `CP00-r3-integrity-final.json`; Paket-Hash/CRC: `CP00-r3-local-package.json`.

Der bisherige WCR-Paketfingerprint bleibt `0d681481b7deaaa76fbeb5466de634e6e6b0caf271b975e1f8052408b41f4fe9`. WCR-Versionszuordnung bleibt offen; die autorisierte Übernahme der abweichenden Fassung wird im nächsten r4-Zwischenstand dokumentiert. Keine stillschweigende Aktualisierung der Basis.

## Gezielter nächster Spieltest

1. `Start-CP00-r3-SH.cmd` im Workspace starten. Unter Laden den vorbereiteten Stand „Normandy – Invasion“ (`cp00_sh`, t1l2) wählen; neuere Test-Saves stehen ebenfalls in der Liste.
2. Die Mission normal bis zu den Flak-Sprengzielen spielen. Vor dem Anbringen einer Ladung einen eigenen Save anlegen, normal beenden und diesen über denselben r3-Startweg laden.
3. Die Flakziele regulär sprengen und den anschließenden Missionsfortschritt beobachten. Bei einer Blockade den letzten funktionierenden Schritt und den betroffenen Save nennen; weder Diagnosekonsole noch Missionsflags sind erforderlich.

Dieser Ablauf prüft den noch offenen natürlichen Flakfortschritt auf der bisherigen Basis. AA-/BT-Save-/FOV-Tests müssen dafür nicht nochmals manuell wiederholt werden. Die abweichende Originalfassung ist davon getrennt zu klären. Für die Rückkehr zum bestätigten r2 denselben bisherigen `Start-CP00-r2-*.cmd` verwenden; dessen Runtime und Profile wurden nicht verändert. Natürliche MG42-/BT-Finalabläufe, Übergänge, Kampf-/Drop-/Leichenreferenzen, Frametimes und weitere Warnungen bleiben CP0-Aufgaben.

## Berichtigung zum Original-BT-Vergleich

In der isolierten Originalkopie wurde nachträglich `maintt/qconsole.log` gefunden (Dateizeit 13.10.2026 23:10:38). Die Aussage im früheren Nachprüfungsbericht, der Originalprozess habe kein Log erzeugt und sei vor der Spielinitialisierung beendet worden, war falsch. Das Log belegt Rendererinitialisierung, Kartenstart und Autosave vor dem erfassten Abbruch `0xC0000005`.

Es enthält ebenfalls fünf ungültige AISpawnPoint-Trigger-Warteaufrufe, einen PathNode-Trigger-Warteaufruf, den Wetter-`spawn`-Wartefehler, fehlende `aipronechance`/`aicrouchchance`-Ereignisse und das fehlende Spline-Ziel t449. Diese Meldungen sind bereits mit der gelieferten Originalengine nachgewiesen. Die zusätzliche OpenMoHAA-Meldung über das unzulässige Löschen eines PathNode ist damit nicht automatisch erklärt. Fortgang und vollständiges Finale bleiben ungeprüft; keine pauschale Harmlosigkeitsbehauptung.
