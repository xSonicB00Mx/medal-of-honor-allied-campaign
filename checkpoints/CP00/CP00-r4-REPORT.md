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
| AA-MG42-Karte | m2l1 startet mit sichtbarer Schneeszene und vollständigem Save, keine Script-Error-Meldung. Kartenstart technisch geprüft (`r4-mg42-start-AA.json`); späterer natürlicher MG42-Test samt Missionsabschluss am 14.10.2026 vom Nutzer bestätigt. |
| BT-Finale | e3l4 startet, Haupt-/Tower-/Escape-/Outro-Ressourcen aus neuem WCR-Paket bestätigt; Szene und Save vorhanden. Bestehende acht Script-Error-Meldungen bleiben; Finalerfolg und Timerfehlschlag auf Nutzerwunsch vom 14.10.2026 nicht getestet (`r4-finale-start-BT.json`). |

**Fehlgeschlagene Testmethode erhalten:** Die ersten SH-/BT-Briefingproben hatten wartende Screenshot-/Quit-Befehle im Konsolenbuffer. `EventPlayMovie` hängt `cinematic` an denselben Buffer an; deshalb waren ihre Aufnahmen schwarz. Diese beiden Proben gelten ausdrücklich nicht als visuell bestanden. Der korrigierte Live-Test startet nur die Briefingkarte ohne nachfolgende Testbefehle; Filmaufnahmen und Logs bleiben lokal. Die erste BT-Liveaufnahme wurde erst im folgenden Missionsintro erfasst; eine getrennte Wiederholung dokumentiert den Briefingfilm selbst. Fenster nach den Tests geschlossen.

Die BT-e1l2-Szene meldet dreimal `ModifyDrive used improperly`, ebenso bereits der alte r1-Szenentest. Die acht e3l4-Skriptfehler entsprechen der vorherigen Kartenprobe; sie werden nicht durch den sichtbaren Start als harmlos erklärt. Der partielle Originalengine-Vergleich aus r3 bezog sich auf die **alte** WCR-Basis. Die neue KI-Fassung wird nicht pauschal als reine Diagnoseänderung eingestuft.

## Integrität, Paket und Rückkehr

Abschlussprüfung: Originalinstallation und neuer Snapshot stimmen bei allen **9072** erfassten Dateien überein; Runtime enthält **9000** bytegleiche Inhaltsdateien plus **17** eigene Dateien. Acht inventarisierte Max-Payne-Dateien unverändert. Das ist eine Prüfung gegen die neue autorisierte Inventarisierung; die Abweichungen zur ersten Basis bleiben in r3/r4-Berichten erhalten. `CP00-r4-integrity-final.json`.

Lokales Paket `artifacts-local/CP00-r4-local-runtime.zip`: CRC geprüft, vollständiger SHA in `CP00-r4-local-package.json`. Originalassets/Saves/Logs bleiben ausgeschlossen von GitHub. Der isolierte Rückbautest entfernt ausschließlich die eigenen Dateien aus `runtime-local/rollback-test-CP00-r4` und prüft danach den exakten Datensatz; Nutzerprofile und r4 bleiben unverändert (`CP00-r4-rollback-result.json`). Lokale Kopien und Quellbundle ersetzen keine externe oder gegen dieselben Schreibrechte geschützte Sicherung.

Nutzerprofile `AA`, `SH`, `BT` enthalten nur frisch auf r4 erzeugte Referenz-/Testsaves. Die zusätzlichen Skript-/Briefingproben liegen in separaten Profilen. FOV 90, Fenster 1280×960, GL1/OpenAL, 60-FPS-Limit; Diagnosemodus für die drei Nutzerprofile nach Sicherung der Testkonfiguration deaktiviert. Keine alten Nutzer-Saves migriert. Zur Rückkehr r4 schließen und die bisherigen `Start-CP00-r2-*.cmd` mit ihren erhaltenen r2-Profilen verwenden. Nicht EXE oder einzelne Pakete zwischen Kandidaten austauschen.

## Nutzerprüfung vom 14.10.2026

Der Nutzer bestätigt für den übergebenen CP00-r4-SH-Test: „Erstes Flakziel wurde gesprengt. Mission setzte normal fort“ und anschließend „Zweites Flakziel zerstört. Mission lief normal weiter“. Damit sind beide natürlichen Flaksprengungen mit jeweiligem anschließendem Missionsfortschritt durch Nutzerfeedback bestätigt. Dies ergänzt den synthetischen Ereignistest; es ist keine vollständige CP0-Abnahme oder Mergefreigabe.

Auf die Rückfrage zum Zwischenschritt Speichern, regulär beenden und neu laden bestätigt der Nutzer: „Beim ersten Flakziel ja. Beim zweiten Flakziel nicht“. Somit sind Save/Neustart/Laden am ersten Ziel sowie beide natürlichen Sprengungen und ihr anschließender Missionsfortschritt bestätigt. Der übergebene gezielte SH-Flaktest ist damit bestanden; ein zweiter separater Neustarttest am zweiten Ziel ist nicht erforderlich und wird nicht als durchgeführt behauptet. Die automatisierten r4-Save-/Load-Nachweise bleiben davon getrennt gültig. Vollständiger Missionsabschluss und natürlicher Levelübergang sind nicht aus „lief normal weiter“ abzuleiten. Keine vollständige CP0-Abnahme oder Mergefreigabe.

## Vorheriger, abgeschlossener SH-Nutzertest

1. Im Workspace **`Start-CP00-r4-SH.cmd`** starten. Im Ladebildschirm „Normandy – Invasion“ / `cp00_sh` laden; neuere automatische Testeinträge stehen ebenfalls in der Liste.
2. Normal bis zu den Flakzielen weiterspielen. Vor dem Anbringen einer Ladung einen eigenen Save anlegen, regulär beenden und diesen über denselben r4-Startweg laden.
3. Flakziele regulär sprengen und prüfen, ob der anschließende Missionsfortschritt funktioniert. Bei einer Blockade den letzten funktionierenden Schritt und den Save nennen. Keine Diagnosebefehle erforderlich.

AA und BT sind zusätzlich über `Start-CP00-r4-AA.cmd` bzw. `Start-CP00-r4-BT.cmd` startbar. Die bereits bestätigten Speicher-/FOV-Schritte müssen nicht nochmals in allen drei Spielen manuell wiederholt werden. Zum Zeitpunkt der SH-Übergabe waren MG42-/Finaldurchläufe und übrige CP0-Fälle noch offen; die spätere MG42-Bestätigung und der BT-Testverzicht sind unten dokumentiert.


## Vorbereitung des MG42-/BT-Spieltests (14.10.2026)

`tools/prepare_cp00_progression.py` erzeugt zwei unabhängige Profile und Workspace-Startdateien. Das Werkzeug prüft r4-Binärdateien, aktive WCR-Pakete, Engine-/Inhaltszuordnung und die drei Dateien jedes Referenzsaves gegen die bestehenden Manifeste; vorhandene Zielprofile/Launcher werden zurückgewiesen. Die unveränderten r4-Startspielstände stammen aus `r4-mg42-start-AA` und `r4-finale-start-BT`. Es werden keine Erfolgsflags gesetzt oder Originalskripte verändert. Bestehende AA-/SH-/BT-Nutzerprofile bleiben erhalten; Einstellungen werden ausschließlich in die neuen Profile kopiert. Engine und Runtime bleiben identisch.

| Test | Startdatei im Workspace | Ladeeintrag | Eigenes Profil |
|---|---|---|---|
| AA-MG42 | `Start-CP00-r4-MG42-AA.cmd` | Secret Documents of the Kriegsmarine (`cp00_m2l1`) | `profiles-local/CP00-r4/mission-MG42-AA` |
| BT-Finale | `Start-CP00-r4-Finale-BT.cmd` | Italy - Monte Battaglia (`cp00_e3l4`) | `profiles-local/CP00-r4/mission-Finale-BT` |

Beide tatsächlichen CMDs wurden ohne fs-Pfadüberschreibung gestartet, die Referenzen geladen und die sichtbaren Szenen geprüft. Ladeeinträge und passende Vorschaubilder sind sichtbar, FOV 90 bestätigt. Die ersten Menüaufnahmen waren durch die automatisch eingeblendete Startkonsole verdeckt; ergänzende Aufnahmen mit vorübergehendem `ui_console=0` zeigen die vollständigen Menüs. Die ursprünglichen kopierten Einstellungen wurden anschließend bytegleich wiederhergestellt. Die erste AA-Auswertung scheiterte nur an einem zu strengen Leerzeichenmuster für die FOV-Ausgabe; der erfolgreiche Spielstart musste nicht wiederholt werden. Laden erfolgte per Konsolenbefehl, nicht per geprüftem Mausklick. Metadaten: `CP00-r4-progression-preparation.json` und `CP00-r4-progression-launcher-check.json`; Logs/Bilder/Saves bleiben lokal. Alle vorbereiteten Save-, Konfigurations- und Launcherhashes nach Testende erneut bestätigt.

Die BT-Ladeprobe erzeugt keine neuen Script-Error-Zeilen; dies erklärt die acht Fehler beim ursprünglichen Kartenstart ausdrücklich nicht als behoben. Beide Saves liegen am Kartenanfang, nicht direkt vor dem späteren Prüfziel. Die neuen Launcher laden beim nächsten Start keinen Spielstand automatisch; eigener Fortschritt wird über das Lademenü fortgesetzt.

### Ursprünglich übergebene Prüfschritte (AA abgeschlossen, BT anschließend abgewählt)

1. Zuerst `Start-CP00-r4-MG42-AA.cmd` im Workspace starten und **Secret Documents of the Kriegsmarine** laden. Normal mit Grillo durch die Mission spielen, bis eine stationäre MG42 benutzbar ist.
2. Vor der Benutzung einen eigenen Save anlegen. Die MG42 mit der Benutzen-Taste (übernommene Belegung: **E**) übernehmen, schießen, verlassen und erneut übernehmen. Danach die Mission normal bis zum nächsten Abschnitt abschließen. Rückmeldung: Benutzung möglich, Gegner-/Missionsablauf weitergegangen, Levelübergang erreicht? Bei Stillstand den letzten Schritt und Save nennen. Der lokale `m2l1::s7_test`-Callback steuert zeitbegrenzte zusätzliche Gegnerwellen; ein bloßer Kartenstart ist kein Fortschrittsnachweis.
3. Danach `Start-CP00-r4-Finale-BT.cmd` starten und **Italy - Monte Battaglia** laden. Die Missionsziele normal spielen. Sobald **Confirm the Airstrike** ansteht, vor der Funkbestätigung einen separaten manuellen Save anlegen und für beide folgenden Fälle behalten.
4. Luftangriff bestätigen und die anschließende Flucht vollständig spielen. Prüfen, ob die Route bis zum echten Ende, Outro und Abspann weiterläuft. Die Funkbestätigung allein ist kein bestandener Finaltest. Das lokale Escape-Skript wartet auf fünf aufeinanderfolgende Trigger und erst danach auf den Abschluss der Sequenz.
5. Den Save vor der Funkbestätigung erneut laden, den Luftangriff bestätigen und diesmal die Fluchtzeit verstreichen lassen. Erwartet: Scheitern/Tod mit fehlgeschlagener Mission, kein erfolgreicher Abspann. Bei unverändertem mittlerem Schwierigkeitsgrad beträgt die Skriptfrist 90 Sekunden; danach folgt noch die kurze Fehlschlagsequenz. Ergebnis beider BT-Fälle getrennt melden.

Bei der Übergabe wurde zunächst das AA-Ergebnis erwartet; BT war für danach vorbereitet. Die folgende Nutzerentscheidung ersetzt diese weitere Testaufforderung.


## Nutzerbestätigung MG42 und Verzicht auf BT-Finaltest (14.10.2026)

Der Nutzer meldet zum übergebenen AA-MG42-Test: „Hat alles funktioniert und ich konnte die Mission auch abschließen.“ Damit gelten MG42 übernehmen, schießen, verlassen, erneut übernehmen und anschließender Missionsabschluss als durch den Nutzer bestätigt. Dies ist der natürliche Spieltest auf CP00-r4; der ältere synthetische Komponententest bleibt ein eigener Nachweis.

Anschließend entscheidet der Nutzer: „Lass uns den BT Final Test überspringen. Da wird auch schon alles funktionieren“. Diese direkte Anweisung ersetzt die entsprechende Testanforderung für die aktuelle CP0-Runde. Die vollständige BT-Flucht, Outro/Abspann und der Timerfehlschlag werden **auf Nutzerwunsch nicht durchgeführt**. Die Erwartung des Nutzers ist kein Prüfnachweis; diese Fälle erhalten keinen Erfolgsstatus. Die acht bekannten e3l4-Startfehler bleiben ungeklärt. Vorhandene Start-/Save-/Ladenachweise bleiben gültig; vorbereitete BT-Profile und Startdateien werden erhalten. Keine erneute Aufforderung zum BT-Finaltest ohne neuen Auftrag.

Weitere offene CP0-Punkte: zusätzliche Übergänge, Kampf-/Leichen-/Drop-Referenzen, Frametimes, übrige Optionspersistenz und noch ungeklärte Skriptwarnungen. Der Verzicht betrifft ausschließlich den BT-Finaltest; vollständige CP0-Abnahme, Merge oder CP0a wurden nicht freigegeben. Engine, Runtime und Spielstände wurden für diese Dokumentationsänderung nicht verändert.

## Weitere technische Teilprüfung (14.10.2026)

Optionspersistenz, Client-Timedemos und erste kontrollierte Kampf-/Leichenreferenzen sind im [separaten Referenzbericht](CP00-r4-BASELINE-REPORT.md) dokumentiert. 27/27 Optionsprüfungen bestanden. AA/SH liefern gültige Pistolentodesreferenzen, AA zusätzlich Waffenstatistiken; BT-Kampfreferenz und vollständige CP0-Matrix bleiben offen. Sämtliche verworfenen Aufbauten und Grenzen sind ausdrücklich ausgewiesen. Keine Engine- oder Inhaltsänderung.
