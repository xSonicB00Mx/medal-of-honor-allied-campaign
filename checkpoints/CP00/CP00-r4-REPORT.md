# CP00-r4 – autorisierte lokale WCR-Aktualisierung

13.10.2026. **Technisch geprüfter Teilkandidat zum Spieltest; CP0 bleibt offen.** Der Nutzer hat die bewusste Aktualisierung seiner Originalinstallation bestätigt und ausdrücklich die neue lokale Fassung als künftige Basis gewünscht. Kein Download und keine Versionsnummer aus Zeitstempeln oder Websites abgeleitet. r2 und r3 bleiben mit ihrer bisherigen Basis erhalten. Keine vollständige Nutzerabnahme, kein Merge, kein CP0a.

## Neue Basis

`tools/import_cp00_wcr_revision.py --revision CP00-r4` erfasst alle Eingaben neu, weist Links zurück, prüft ZIP-CRC und kopiert 9072 Dateien unabhängig nach `input-local/CP00-r4`. Jede Kopie und ihre Quelle wurden gegen denselben SHA-256 geprüft. Es gibt sechs veränderte Dateien (fünf WCR-Pakete sowie Deinstallationsdatei), acht zusätzliche lose Audio-Dateien und keine entfernten Dateien. `CP00-r4-import.json` enthält die Einzeländerungen einschließlich hinzugefügter/geänderter Ressourcen in den Paketen. Die Deinstallation wird nur inventarisiert, niemals ausgeführt.

Sieben aktive WCR-Pakete, Fingerprint `3b6b38b5b04ba320a526196946c44394c4519e4197dc8d3d05788e186501cfcc`. Die historische Zuordnung bleibt unter `third_party/wcr/revisions/CP00-original.json` erhalten; neue Zuordnung `CP00-r4.json` und aktuelles Manifest. **WCR_BASIS_UNGEKLAERT** gilt weiterhin für die genaue Releasebezeichnung, nicht für die Hashzuordnung der lokalen Fassung.

Gezielte Skriptdiffs: AA `m2l1` entfernt Diagnoseausgaben, SH/BT `global/exploder.scr` und BT `global/bomber.scr` schalten Diagnoseausgaben hinter `debug`. Neue KI-Overrides und zusätzliche AA-Ressourcen erfordern Laufzeittests. Die tatsächlichen WCR-Skripte und Assets werden unverändert übernommen. Der zusätzliche BT-Drop-Patch bleibt unaktiviert; kein CP0a.

Die vorhandene r3-Engine aus `af7bb7c6e706fcc64e5933a22457333274f3de22` wird wiederverwendet. Es gibt keine weitere Engineänderung. Deployment, Prüfungen und Paketierung verwenden jetzt kandidatenbezogene Eingabe-/Datenmanifeste; ältere Manifeste und Runtime-Profile werden nicht umgedeutet. r4 erhält neue Referenzsaves auf der neuen Inhaltsbasis, keine alten Nutzer-Saves.

## Prüfung und Zuordnung

Deploymentstand `58ee14ba801ebbc1d34c1985df671d865d0d133b`, Engine unverändert `af7bb7c6e706fcc64e5933a22457333274f3de22`. `CP00-r4-build.json` enthält Binärhashes und die genaue Zuordnung der lokalen Datenmanifeste. Der vollständige lokale r3-Build und dessen erfolgreiche GitHub-CI gelten für diese identischen Binärdateien. Zusätzlich sind Push-CI `38473094326` und PR-CI `38473102172` des r4-Deploymentstands erfolgreich. Spätere Berichts-/Testwerkzeugcommits ändern diese Enginezuordnung nicht. CI läuft ohne Originalassets.

| Prüfung | Ergebnis und Grenze |
|---|---|
| Frische AA m1l2a, SH t1l2, BT e1l2 | Start, aktive Szene, neuer dreiteiliger Save, Laden und Menürückkehr bestanden. Effektive Karten- und neue KI-Skripte jeweils aus dem richtigen WCR-Paket belegt (`r4-scene-*.json`). |
| Tatsächliche Workspace-Launcher | In allen drei Spielen SAVE-Menücallback, Vorschaubild, Laden nach Prozessneustart und FOV 90 nach Neustart bestanden; kein fs-Pfadoverride im Test. Gerenderte Menüs mit beiden Saveeinträgen einzeln/als Übersicht geprüft (`CP00-r4-*-launcher-test.json`). Laden erfolgt automatisiert per Konsole; Schaltflächen nicht erneut per Maus geprüft. |
| SH-Offsetkompatibilität | Keine Befehlsablehnung; beide Testvektoren nach Speichern und Laden erhalten, beide Test-Detonationscallbacks ausgeführt (`offset-r4-accepted.json`). Keine künstlich abgeschlossenen Originalziele. |
| AA-Briefing | `briefing/briefing1` mit WCR-Skript gestartet; Projektion, Untertitel und Skip-Hinweis sichtbar. Kein vollständiger Briefingdurchlauf. |
| SH-/BT-Filmbriefings | Filme in separaten echten Spielfenstern sichtbar; danach t1l1 bzw. e1l1 mit Autosave geladen. BT erreichte die erste Mission ohne Skip-Eingabe. Bei SH wurden Escape/Alt+F4 versucht, daher kein ununterbrochener Gesamtdurchlauf behauptet. `CP00-r4-visual.json`. |
| AA-MG42-Karte | m2l1 startet mit sichtbarer Schneeszene und vollständigem Save, keine Script-Error-Meldung. Natürlicher MG42-Fortschritt nicht gespielt (`r4-mg42-start-AA.json`). |
| BT-Finale | e3l4 startet, Haupt-/Tower-/Escape-/Outro-Ressourcen aus neuem WCR-Paket bestätigt; Szene und Save vorhanden. Bestehende acht Script-Error-Meldungen bleiben; kein Finalerfolg oder Timerfehlschlag getestet (`r4-finale-start-BT.json`). |

**Fehlgeschlagene Testmethode erhalten:** Die ersten SH-/BT-Briefingproben hatten wartende Screenshot-/Quit-Befehle im Konsolenbuffer. `EventPlayMovie` hängt `cinematic` an denselben Buffer an; deshalb waren ihre Aufnahmen schwarz. Diese beiden Proben gelten ausdrücklich nicht als visuell bestanden. Der korrigierte Live-Test startet nur die Briefingkarte ohne nachfolgende Testbefehle; Filmaufnahmen und Logs bleiben lokal. Die erste BT-Liveaufnahme wurde erst im folgenden Missionsintro erfasst; eine getrennte Wiederholung dokumentiert den Briefingfilm selbst. Fenster nach den Tests geschlossen.

Die BT-e1l2-Szene meldet dreimal `ModifyDrive used improperly`, ebenso bereits der alte r1-Szenentest. Die acht e3l4-Skriptfehler entsprechen der vorherigen Kartenprobe; sie werden nicht durch den sichtbaren Start als harmlos erklärt. Der partielle Originalengine-Vergleich aus r3 bezog sich auf die **alte** WCR-Basis. Die neue KI-Fassung wird nicht pauschal als reine Diagnoseänderung eingestuft.

## Integrität, Paket und Rückkehr

Abschlussprüfung: Originalinstallation und neuer Snapshot stimmen bei allen **9072** erfassten Dateien überein; Runtime enthält **9000** bytegleiche Inhaltsdateien plus **17** eigene Dateien. Acht inventarisierte Max-Payne-Dateien unverändert. Das ist eine Prüfung gegen die neue autorisierte Inventarisierung; die Abweichungen zur ersten Basis bleiben in r3/r4-Berichten erhalten. `CP00-r4-integrity-final.json`.

Lokales Paket `artifacts-local/CP00-r4-local-runtime.zip`: CRC geprüft, vollständiger SHA in `CP00-r4-local-package.json`. Originalassets/Saves/Logs bleiben ausgeschlossen von GitHub. Der isolierte Rückbautest entfernt ausschließlich die eigenen Dateien aus `runtime-local/rollback-test-CP00-r4` und prüft danach den exakten Datensatz; Nutzerprofile und r4 bleiben unverändert (`CP00-r4-rollback-result.json`). Lokale Kopien und Quellbundle ersetzen keine externe oder gegen dieselben Schreibrechte geschützte Sicherung.

Nutzerprofile `AA`, `SH`, `BT` enthalten nur frisch auf r4 erzeugte Referenz-/Testsaves. Die zusätzlichen Skript-/Briefingproben liegen in separaten Profilen. FOV 90, Fenster 1280×960, GL1/OpenAL, 60-FPS-Limit; Diagnosemodus für die drei Nutzerprofile nach Sicherung der Testkonfiguration deaktiviert. Keine alten Nutzer-Saves migriert. Zur Rückkehr r4 schließen und die bisherigen `Start-CP00-r2-*.cmd` mit ihren erhaltenen r2-Profilen verwenden. Nicht EXE oder einzelne Pakete zwischen Kandidaten austauschen.

## Nutzerprüfung vom 14.10.2026

Der Nutzer bestätigt für den übergebenen CP00-r4-SH-Test: „Erstes Flakziel wurde gesprengt. Mission setzte normal fort“ und anschließend „Zweites Flakziel zerstört. Mission lief normal weiter“. Damit sind beide natürlichen Flaksprengungen mit jeweiligem anschließendem Missionsfortschritt durch Nutzerfeedback bestätigt. Dies ergänzt den synthetischen Ereignistest; es ist keine vollständige CP0-Abnahme oder Mergefreigabe.

Der vorgesehene Zwischenschritt Speichern, regulär beenden und neu laden wurde in diesen Rückmeldungen noch nicht ausdrücklich bestätigt. Die automatisierten r4-Save-/Load-Nachweise bleiben davon getrennt gültig. Vollständiger Missionsabschluss und natürlicher Levelübergang sind ebenfalls nicht aus „lief normal weiter“ abzuleiten. Beide erfolgreichen Sprengungen müssen für ihre Bestätigung nicht wiederholt werden.

## Übergebener Nutzertest

1. Im Workspace **`Start-CP00-r4-SH.cmd`** starten. Im Ladebildschirm „Normandy – Invasion“ / `cp00_sh` laden; neuere automatische Testeinträge stehen ebenfalls in der Liste.
2. Normal bis zu den Flakzielen weiterspielen. Vor dem Anbringen einer Ladung einen eigenen Save anlegen, regulär beenden und diesen über denselben r4-Startweg laden.
3. Flakziele regulär sprengen und prüfen, ob der anschließende Missionsfortschritt funktioniert. Bei einer Blockade den letzten funktionierenden Schritt und den Save nennen. Keine Diagnosebefehle erforderlich.

AA und BT sind zusätzlich über `Start-CP00-r4-AA.cmd` bzw. `Start-CP00-r4-BT.cmd` startbar. Die bereits bestätigten Speicher-/FOV-Schritte müssen nicht nochmals in allen drei Spielen manuell wiederholt werden. Vollständige MG42-/Finaldurchläufe, weitere Übergänge, Kampf-/Leichen-/Drop-Referenzen, Frametimes, übrige Optionspersistenz und verbleibende Skriptwarnungen sind weiter offene CP0-Fälle.
