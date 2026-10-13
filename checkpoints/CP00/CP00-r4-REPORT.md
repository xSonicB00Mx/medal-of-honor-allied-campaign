# CP00-r4 – autorisierte lokale WCR-Aktualisierung

13.10.2026. In Vorbereitung; CP0 bleibt offen. Der Nutzer hat die bewusste Aktualisierung seiner Originalinstallation bestätigt und ausdrücklich die neue lokale Fassung als künftige Basis gewünscht. Kein Download und keine Versionsnummer aus Zeitstempeln oder Websites abgeleitet. r2 und r3 bleiben mit ihrer bisherigen Basis erhalten.

## Neue Basis

`tools/import_cp00_wcr_revision.py --revision CP00-r4` erfasst alle Eingaben neu, weist Links zurück, prüft ZIP-CRC und kopiert 9072 Dateien unabhängig nach `input-local/CP00-r4`. Jede Kopie und ihre Quelle wurden gegen denselben SHA-256 geprüft. Es gibt sechs veränderte Dateien (fünf WCR-Pakete sowie Deinstallationsdatei), acht zusätzliche lose Audio-Dateien und keine entfernten Dateien. `CP00-r4-import.json` enthält die Einzeländerungen einschließlich hinzugefügter/geänderter Ressourcen in den Paketen. Die Deinstallation wird nur inventarisiert, niemals ausgeführt.

Sieben aktive WCR-Pakete, Fingerprint `3b6b38b5b04ba320a526196946c44394c4519e4197dc8d3d05788e186501cfcc`. Die historische Zuordnung bleibt unter `third_party/wcr/revisions/CP00-original.json` erhalten; neue Zuordnung `CP00-r4.json` und aktuelles Manifest. **WCR_BASIS_UNGEKLAERT** gilt weiterhin für die genaue Releasebezeichnung, nicht für die Hashzuordnung der lokalen Fassung.

Gezielte Skriptdiffs: AA `m2l1` entfernt Diagnoseausgaben, SH/BT `global/exploder.scr` und BT `global/bomber.scr` schalten Diagnoseausgaben hinter `debug`. Neue KI-Overrides und zusätzliche AA-Ressourcen erfordern Laufzeittests. Die tatsächlichen WCR-Skripte und Assets werden unverändert übernommen. Der zusätzliche BT-Drop-Patch bleibt unaktiviert; kein CP0a.

Die vorhandene r3-Engine aus `af7bb7c6e706fcc64e5933a22457333274f3de22` wird wiederverwendet. Es gibt keine weitere Engineänderung. Deployment, Prüfungen und Paketierung verwenden jetzt kandidatenbezogene Eingabe-/Datenmanifeste; ältere Manifeste und Runtime-Profile werden nicht umgedeutet. r4 erhält neue Referenzsaves auf der neuen Inhaltsbasis, keine alten Nutzer-Saves.

## Ausstehende Prüfung

Frische AA-/SH-/BT-Szenen, tatsächliche Launcher, Save/Load/FOV, sichtbare Briefing-/Speichermenüs, SH-Offsettest, AA-MG42-Kartenstart und BT-Finalressourcen werden auf r4 geprüft. Natürliche Missions-/Finaldurchläufe bleiben davon getrennt. Integrität, Paket-CRC, isolierter Rückbau und GitHub-Sicherung folgen vor Übergabe.
