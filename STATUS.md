# Status

- Aktiver Checkpoint: **CP0 – TEILKANDIDAT ZUM SPIELTEST, NICHT ABGENOMMEN**.
- Kandidat: **CP00-r3**, eigene Runtime und getrennte AA-/SH-/BT-Profile; SH-`explosionoffset`-Handler registriert. r2 und dessen bestätigte Nutzerprofile bleiben erhalten. r1 bleibt zurückgezogen.
- r3: sauberer Build, positive/negative Ereignis- und Savekontrolle sowie Launcher-/Save-/Vorschaubild-/FOV-Tests in AA, SH und BT bestanden. Berichtigte Original-BT-Logauswertung im [r3-Bericht](checkpoints/CP00/CP00-r3-REPORT.md).
- Letzte Nutzerrückmeldung (13.10.2026): „hat geklappt. fahre fort“ bestätigt die r2-Nachprüfung von Speichern/Laden, Missionsvorschaubildern und FOV-Persistenz. Keine vollständige CP0-Abnahme und kein Merge freigegeben.
- Arbeitsbranch: `codex/cp00-baseline`; privates `xSonicB00Mx/medal-of-honor-allied-campaign`.
- Gebaute r3-Engine: `af7bb7c6e706fcc64e5933a22457333274f3de22`; vollständige Dateihashes im r3-Buildmanifest. Spätere Bericht-/Testwerkzeugcommits ändern diese Binärzuordnung nicht. r2 bleibt auf `3eec4afb22093421b8776d2df92b87ec2fb4119e`.
- GitHub: Quellstände werden auf dem CP0-Arbeitsbranch gesichert und per Remote-SHA geprüft; aktuelle CI-Ergebnisse im Entwurfs-PR. Kein Merge. GitHub verweigert Branchschutz im aktuellen privaten Tarif (HTTP 403); Verfahrensregeln sind kein serverseitiger Schutz.
- WCR: sieben Pakete und lose Inhaltsbasis unverändert übernommen; ausgewählte Laufzeitquellen belegt. **WCR_BASIS_UNGEKLAERT**: lokale Versions-/Changelog-Zuordnung fehlt, vollständige Inhaltsabnahme offen.
- **Autorisierte WCR-Aktualisierung in Arbeit:** Der Nutzer bestätigt die bewusste Aktualisierung und beauftragt die neue Fassung als künftige Basis. Neuer unabhängiger Snapshot `input-local/CP00-r4`: 9072 Dateien, davon sechs geändert und acht Audio-Dateien hinzugekommen. WCR-Fingerprint `3b6b38b5b04ba320a526196946c44394c4519e4197dc8d3d05788e186501cfcc`. Versionsnummer weiterhin unbelegt. r4 wird getrennt bereitgestellt; frische Saves, keine Migration alter Nutzerprofile. Alte Basis und r2/r3 bleiben erhalten.
- Bestanden: zwei saubere Engine-Builds; r2-Start über alle drei tatsächlichen Workspace-CMDs, neuer Save durch Menücallback mit Vorschaubild, Laden nach Neustart, FOV 90 nach Neustart; drei Speichermenüs visuell geprüft. In AA Save/Load zusätzlich tatsächlich mit der Maus geklickt. Original-/Runtime-Hashes und isolierter Rückbau geprüft.
- Zusätzlich geprüft: AA-MG42-Callback isoliert bestanden (1 / 1 / 2); m2l1- und e3l4-Start mit Saves, BT-Finalressourcen bestätigt. Nachträglich gefundenes Original-BT-Log belegt Initialisierung, Autosave und mehrere gleiche Warnungen vor `0xC0000005`; kein vollständiger Originaldurchlauf. SH-Registrierungslücke in r3 korrigiert; die unveränderte Explosionsposition entspricht der Original-DLL.
- Offen: natürliche WCR-/MG42-/Finale-/Levelübergangstests, übrige Optionspersistenz, Treffer-/Leichen-/Drop-Referenzen, Frametimes und Skript-/Ressourcenwarnungen; siehe Bericht. FOV-Persistenz ist bestätigt.
- Sicherung: unabhängige Dateikopie und lokales Testpaket geprüft; keine zusätzlich gegen dieselben Schreibrechte geschützte bzw. externe Sicherung.
- Nächster erlaubter Schritt: Nutzerfeedback und ausschließlich CP0-Korrekturen/ausstehende Prüfungen. **CP0a nicht beginnen**.

Aktuelle Korrektur und Nutzerprüfschritte: [CP00-r3-Bericht](checkpoints/CP00/CP00-r3-REPORT.md). Ältere CP0-Spiel- und Schutzgrenzen bleiben offen.
