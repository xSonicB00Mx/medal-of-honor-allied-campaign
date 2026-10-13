# CP00-r2 – Speichermenü und dauerhafte Einstellungen korrigiert

13.10.2026. Reaktion auf Nutzerfeedback: In AA, SH und BT fehlten Save-Vorschaubilder, Speichern funktionierte nicht, FOV 90 fiel beim Neustart auf 80 zurück. **Zwei von uns verursachte Bereitstellungsfehler**, keine WCR-Änderung und keine Nutzerfehlbedienung. CP00-r1 ist zurückgezogen; Dateien/Profile bleiben als Vergleich erhalten. Keine Abnahme, kein Merge, kein CP0a.

## Ursache und Änderung

1. r1 übergab `fs_homepath` als absoluten Pfad mit wörtlichem `..\..`. `FS_CreatePath` in `code/qcommon/files.cpp` verweigert Pfade mit `..`; dadurch wurden Save-/Konfigurations-/Log-Schreibzugriffe blockiert. Der ursprüngliche automatisierte Test benutzte bereits aufgelöste Pfade und konnte diesen Launcherfehler nicht erkennen. r2 löst Profil- und Basispfad mit Windows-CMD `%%~fI` auf, bevor sie an die Engine gehen. Die Sicherheitsprüfung der Engine bleibt unangetastet.
2. Ein vollständiger Save besteht aus `.sav`, `.ssv` **und `.tga`**. Die r1-Teststandübernahme und der spätere AA-Reset hatten nur die ersten beiden Dateien übernommen. r2 übernimmt die originale, von der Engine erzeugte Vorschau mit Hashprüfung. Keine Ersatzbilder und keine Änderung der WCR-Menüs.

Neue Kandidatenordner und getrennte Profile verhindern ein Überschreiben der r1-Diagnose. AA-/SH-/BT-Profile aus der Nutzerprüfung wurden zusätzlich unter `profiles-local/CP00-r1-user-feedback-*` gesichert. Die vorgefundenen Nutzerprofile enthielten jeweils nur die vorbereiteten zwei Save-Dateien, passend zum Schreibpfadfehler.

Engine-Binärdateien unverändert aus `3eec4afb22093421b8776d2df92b87ec2fb4119e`. r2-Deploymentstand `4d86762c` (voller SHA: `CP00-r2-build.json`). Kein neuer Engine-Build erforderlich; neue Änderungen betreffen Launcher-Erzeugung, Save-Übernahme, Regressionstests, Paketierung und Berichte. 8992 WCR-/Spielinhaltsdateien bleiben bytegleich; Fingerprint und offene WCR-Befunde aus r1 gelten weiter.

## Prüfungen

| Nachweis | AA | SH | BT |
|---|---|---|---|
| Tatsächliche `Start-CP00-r2-*.cmd` gestartet, kein fs-Pfadoverride durch Test | bestanden | bestanden | bestanden |
| SAVE-Menücallback erzeugt neuen Save plus Vorschaubild | bestanden | bestanden | bestanden |
| Derselbe neu erzeugte Save nach Prozessneustart geladen | bestanden | bestanden | bestanden |
| FOV von 80 auf 90 gesetzt; Konfiguration geschrieben; nach Neustart 90 gelesen | bestanden | bestanden | bestanden |
| Gerendertes Speichermenü: Hintergrund, Vorschaubild, alter und neuer Eintrag sichtbar | geprüft | geprüft | geprüft |
| Save- und Load-Schaltflächen tatsächlich per Maus bedient | bestanden | nicht separat geklickt | nicht separat geklickt |

Automatisierter Einstieg: `tools/test_cp00_launchers.py --candidate CP00-r2 --game AA` (analog SH/BT; nur auf frischen Profilen). Der Test übergibt keine fs-Pfade, ruft den gleichen Save-Callback wie die Schaltfläche auf und prüft den neuen Save nach Neustart. Der automatisierte Ladevorgang selbst erfolgt über den Konsolenbefehl; davon getrennt wurde in AA der sichtbare LOAD-Button geklickt und die Rückkehr in den Hof mit Waffe/HUD beobachtet.

Ein erster AA-Testversuch scheiterte an der Testskriptreihenfolge: Der Load-Callback hängt seinen Befehl hinten an den Befehlsbuffer; ein bereits dort eingeplantes `quit` kam vorher. Dieser Versuch ist unter `AA-test-attempt1` erhalten, nicht als erfolgreich gewertet. Der korrigierte Test verwendet einen echten zweiten Prozess; der ergänzende Mausklick bestätigt den echten Load-Button.

Testbedingungen: Fenster 1280×960, GL1, OpenAL, 60-FPS-Limit, Netzwerk im Test aus. Die drei neuen Profile behalten FOV 90 und die getesteten Fenstereinstellungen. Einstellungen können wieder normal im Menü geändert werden. Restart-Screenshots enthalten teilweise die Diagnosekonsole; die FOV-Zahl wurde zusätzlich aus der gespeicherten Konfiguration und dem frischen Prozesslog verifiziert. Die Speichermenübilder aus dem ersten Testlauf sind frei von diesem Overlay.

Einzelnachweise: `CP00-r2-AA-launcher-test.json`, `CP00-r2-SH-launcher-test.json`, `CP00-r2-BT-launcher-test.json`, `CP00-r2-live-ui.json`. Originale Testlogs und Renderbilder liegen ausschließlich lokal unter `generated-local/CP00-r2` und `profiles-local/CP00-r2`. Erneute Original-/Runtime-Hashprüfung: `CP00-r2-integrity-final.json`; Rückbau: `CP00-r2-rollback-result.json`. Vollständiges lokales Paket samt SHA-256: `CP00-r2-local-package.json`. Es enthält Originalspieldaten und bleibt von GitHub ausgeschlossen.

## Erneuter Nutzertest

1. **AA:** Im Workspace `Start-CP00-r2-AA.cmd` per Windows-Explorer starten. Im Ladebildschirm muss das Missionsbild sichtbar sein. „The Rescue Mission“ / `cp00_aa` laden, speichern und den neu angelegten Eintrag wieder laden.
2. **Spearhead:** `Start-CP00-r2-SH.cmd` starten; denselben Ablauf mit „Normandy – Invasion“ / `cp00_sh` prüfen.
3. **Breakthrough:** `Start-CP00-r2-BT.cmd` starten; denselben Ablauf mit „Tunisia – Battle of Kasserine Pass II“ / `cp00_bt` prüfen.
4. In einem Spiel FOV auf einen anderen Wert stellen, übernehmen, normal beenden und mit derselben r2-Startdatei erneut starten. Der gewählte Wert muss erhalten sein. Aktuell ist 90 voreingestellt, weil dieser Wert im Regressionstest verwendet wurde.

Die neu erzeugten Test-Saves stehen zusätzlich zu den Referenzständen in der Liste; den neuesten erkennt man an Datum/Uhrzeit. Alte r1-Startdateien nicht für diese Nachprüfung verwenden. Zur bisherigen Originalinstallation zurückkehren: r2 schließen, bisherigen Originalstartweg nutzen. Originale und alte Saves wurden nicht verändert; r2 wird bei Rückbau nur in einer gesonderten Kopie geprüft.

Die weiteren offenen CP0-Fälle (unter anderem MG42-Fortschritt, BT-Finale, natürliche Übergänge, Kampf-/Drop-/Leichenreferenzen, Frametimes) und Schutzgrenzen bleiben offen. Diese Korrektur ist keine vollständige CP0-Abnahme.
