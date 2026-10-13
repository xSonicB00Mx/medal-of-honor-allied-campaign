# CP00-r3 – Spearhead-Ereigniszuordnung

13.10.2026. **In Vorbereitung, noch nicht als Nutzerkandidat übergeben.** CP0 bleibt offen, kein Merge und kein CP0a. CP00-r2 und seine bestätigten Nutzerprofile bleiben erhalten.

## Korrektur und Referenz

Die WCR-Karte t1l2 sendet zweimal `explosionoffset` an `ThrobbingBox_ExplodePlayerFlak88`. OpenMoHAA besitzt Setter und archiviertes Vektorfeld, hatte den Setter jedoch nicht in der Ereignistabelle registriert. Eine zusätzliche Zuordnung in `code/fgame/Entities.cpp` stellt die Annahme des Befehls wieder her.

**Korrektur der vorherigen Einordnung:** Ein unbenutztes Offsetfeld allein beweist hier keinen zusätzlichen Kompatibilitätsfehler. Die lokale originale Spearhead-DLL wurde statisch geprüft: Ihre Ereignistabelle bindet den Setter, dieser speichert den Vektor; ihre Explosionsroutine verwendet trotzdem die bisherige Effektposition und den festen Schadensversatz von 128. Deshalb bleiben Effektposition, Schadensradius/-höhe, Modelle, WCR-Skripte und Saveformat unverändert. Kein erfundener neuer Versatzmechanismus.

Referenz ist ausschließlich `mainta/gamex86.dll` aus dem geschützten lokalen Snapshot, SHA-256 `33f8c707da12d746b474634f11ce1701c53ebe7cd74d71904c453811eb5d7ec7`. Lokale Analyse mit vorhandenem MSVC dumpbin 14.44.35228.0: Ereigniskonstruktor über Zeichenkette und Response-Tabelle zugeordnet, Setter und Explosionsroutine untersucht. Tabelleninitialisierung bei VA `0x310A7450`, Setter `0x310A8240`, Explosionsroutine `0x310A7610`, konstante Höhe 128 bei `0x311CE4E0`. Disassemblat und Fremdbinärdatei bleiben ausschließlich lokal. Dies ist ein statischer Vergleich, kein erfolgreicher Originalengine-Spieltest. Ein zusätzlicher SH-Startversuch endete mit Code 0 ohne beobachtete Spielszene/SH-Log.

## Regressionstest

`tools/test_cp00_explosionoffset.py` startet t1l2 in einem neuen Profil, setzt zwei unterscheidbare Vektoren auf zusätzliche Test-Flakladungen, speichert, startet den Prozess neu und lädt erneut. Der nur lokal gebaute `tools/cp00-save-probe` liest die selbst erzeugten Saves mit dem unveränderten Engine-Decoder und zählt die beiden Vektoren. Anschließend werden nur die Testladungen mit Schaden 0 ausgelöst; beide gespeicherten Callbacks müssen laufen. Keine Missionsflags und keine originalen Flakobjekte werden künstlich abgeschlossen.

Negativkontrolle auf CP00-r2 bestanden: vier abgewiesene Offsetbefehle (zwei Karte, zwei Test), beide Vektoren vor/nach Laden nicht archiviert, beide Test-Detonationscallbacks ausgeführt. `offset-r2-control-v2.json`. Erster Versuch `offset-r2-control.json` scheiterte an der Testskript-Syntax eines negativen Vektorliterals; mit der von WCR verwendeten Zeichenkettenform korrigiert. Dieser fehlgeschlagene Versuch bleibt erhalten.

Build, positiver Regressionstest und Bereitstellung von r3 folgen aus einem sauberen Quellcommit. Eine vollständige natürliche Spreng-/Missionsabnahme ist damit weiterhin nicht behauptet.

## Berichtigung zum Original-BT-Vergleich

In der isolierten Originalkopie wurde nachträglich `maintt/qconsole.log` gefunden (Dateizeit 13.10.2026 23:10:38). Die Aussage im früheren Nachprüfungsbericht, der Originalprozess habe kein Log erzeugt und sei vor der Spielinitialisierung beendet worden, war falsch. Das Log belegt Rendererinitialisierung, Kartenstart und Autosave vor dem erfassten Abbruch `0xC0000005`.

Es enthält ebenfalls fünf ungültige AISpawnPoint-Trigger-Warteaufrufe, einen PathNode-Trigger-Warteaufruf, den Wetter-`spawn`-Wartefehler, fehlende `aipronechance`/`aicrouchchance`-Ereignisse und das fehlende Spline-Ziel t449. Diese Meldungen sind bereits mit der gelieferten Originalengine nachgewiesen. Die zusätzliche OpenMoHAA-Meldung über das unzulässige Löschen eines PathNode ist damit nicht automatisch erklärt. Fortgang und vollständiges Finale bleiben ungeprüft; keine pauschale Harmlosigkeitsbehauptung.
