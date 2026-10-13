# Status

- Aktiver Checkpoint: **CP0 – TEILKANDIDAT ZUM SPIELTEST, NICHT ABGENOMMEN**.
- Kandidat: **CP00-r2**, eigene Runtime und getrennte AA-/SH-/BT-Profile. CP00-r1 nach Nutzerfeedback wegen Launcher-Schreibpfad und fehlender Save-Vorschaubilder zurückgezogen.
- Letzte Nutzerabnahme: keine. Kein Stable-Build und kein Merge freigegeben.
- Arbeitsbranch: `codex/cp00-baseline`; privates `xSonicB00Mx/medal-of-honor-allied-campaign`.
- Gebaute Engine unverändert: `3eec4afb22093421b8776d2df92b87ec2fb4119e`; r2-Deployment: `4d86762c` (voller SHA im r2-Buildmanifest). Spätere Bericht-/Testcommits ändern diese Binärzuordnung nicht.
- GitHub: Quellstände werden auf dem CP0-Arbeitsbranch gesichert und per Remote-SHA geprüft; aktuelle CI-Ergebnisse im Entwurfs-PR. Kein Merge. GitHub verweigert Branchschutz im aktuellen privaten Tarif (HTTP 403); Verfahrensregeln sind kein serverseitiger Schutz.
- WCR: sieben Pakete und lose Inhaltsbasis unverändert übernommen; ausgewählte Laufzeitquellen belegt. **WCR_BASIS_UNGEKLAERT**: lokale Versions-/Changelog-Zuordnung fehlt, vollständige Inhaltsabnahme offen.
- Bestanden: zwei saubere Engine-Builds; r2-Start über alle drei tatsächlichen Workspace-CMDs, neuer Save durch Menücallback mit Vorschaubild, Laden nach Neustart, FOV 90 nach Neustart; drei Speichermenüs visuell geprüft. In AA Save/Load zusätzlich tatsächlich mit der Maus geklickt. Original-/Runtime-Hashes und isolierter Rückbau geprüft.
- Offen: WCR-/MG42-/Finale-/Levelübergangstests, Optionspersistenz, Treffer-/Leichen-/Drop-Referenzen, Frametimes und Skript-/Ressourcenwarnungen; siehe Bericht.
- Sicherung: unabhängige Dateikopie und lokales Testpaket geprüft; keine zusätzlich gegen dieselben Schreibrechte geschützte bzw. externe Sicherung.
- Nächster erlaubter Schritt: Nutzerfeedback und ausschließlich CP0-Korrekturen/ausstehende Prüfungen. **CP0a nicht beginnen**.

Aktuelle Korrektur und Nutzerprüfschritte: [CP00-r2-Bericht](checkpoints/CP00/CP00-r2-REPORT.md). Ältere CP0-Spiel- und Schutzgrenzen bleiben offen.
