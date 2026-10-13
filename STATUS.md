# Status

- Aktiver Checkpoint: **CP0 – TEILKANDIDAT ZUM SPIELTEST, NICHT ABGENOMMEN**.
- Kandidat: **CP00-r2**, eigene Runtime und getrennte AA-/SH-/BT-Profile. CP00-r1 nach Nutzerfeedback wegen Launcher-Schreibpfad und fehlender Save-Vorschaubilder zurückgezogen.
- In Arbeit: **CP00-r3**, gezielte Registrierung des SH-`explosionoffset`-Handlers; Original-DLL-Abgleich und r2-Negativkontrolle erfolgt, Build/positiver Test noch offen. Berichtigte Original-BT-Logauswertung im [r3-Bericht](checkpoints/CP00/CP00-r3-REPORT.md).
- Letzte Nutzerrückmeldung (13.10.2026): „hat geklappt. fahre fort“ bestätigt die r2-Nachprüfung von Speichern/Laden, Missionsvorschaubildern und FOV-Persistenz. Keine vollständige CP0-Abnahme und kein Merge freigegeben.
- Arbeitsbranch: `codex/cp00-baseline`; privates `xSonicB00Mx/medal-of-honor-allied-campaign`.
- Gebaute Engine unverändert: `3eec4afb22093421b8776d2df92b87ec2fb4119e`; r2-Deployment: `4d86762c` (voller SHA im r2-Buildmanifest). Spätere Bericht-/Testcommits ändern diese Binärzuordnung nicht.
- GitHub: Quellstände werden auf dem CP0-Arbeitsbranch gesichert und per Remote-SHA geprüft; aktuelle CI-Ergebnisse im Entwurfs-PR. Kein Merge. GitHub verweigert Branchschutz im aktuellen privaten Tarif (HTTP 403); Verfahrensregeln sind kein serverseitiger Schutz.
- WCR: sieben Pakete und lose Inhaltsbasis unverändert übernommen; ausgewählte Laufzeitquellen belegt. **WCR_BASIS_UNGEKLAERT**: lokale Versions-/Changelog-Zuordnung fehlt, vollständige Inhaltsabnahme offen.
- Bestanden: zwei saubere Engine-Builds; r2-Start über alle drei tatsächlichen Workspace-CMDs, neuer Save durch Menücallback mit Vorschaubild, Laden nach Neustart, FOV 90 nach Neustart; drei Speichermenüs visuell geprüft. In AA Save/Load zusätzlich tatsächlich mit der Maus geklickt. Original-/Runtime-Hashes und isolierter Rückbau geprüft.
- Zusätzlich geprüft: AA-MG42-Callback isoliert bestanden (1 / 1 / 2 bei Besteigen/Aussteigen/erneutem Besteigen); m2l1- und e3l4-Start mit Saves, BT-Finalressourcen zur Laufzeit bestätigt. Neue BT-Spawn-/Pfadfehler und SH-Explosionsversatz-Lücke dokumentiert. Originalengine-Vergleich durch Startabbruch `0xC0000005` nicht gelungen; siehe [WCR-Nachprüfung](checkpoints/CP00/CP00-r2-WCR-FOLLOWUP.md).
- Offen: natürliche WCR-/MG42-/Finale-/Levelübergangstests, übrige Optionspersistenz, Treffer-/Leichen-/Drop-Referenzen, Frametimes und Skript-/Ressourcenwarnungen; siehe Bericht. FOV-Persistenz ist bestätigt.
- Sicherung: unabhängige Dateikopie und lokales Testpaket geprüft; keine zusätzlich gegen dieselben Schreibrechte geschützte bzw. externe Sicherung.
- Nächster erlaubter Schritt: Nutzerfeedback und ausschließlich CP0-Korrekturen/ausstehende Prüfungen. **CP0a nicht beginnen**.

Aktuelle Korrektur und Nutzerprüfschritte: [CP00-r2-Bericht](checkpoints/CP00/CP00-r2-REPORT.md). Ältere CP0-Spiel- und Schutzgrenzen bleiben offen.
