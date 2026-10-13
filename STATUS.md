# Status

- Aktiver Checkpoint: **CP0 – TEILKANDIDAT ZUM SPIELTEST, NICHT ABGENOMMEN**.
- Kandidat: **CP00-r1**, eigene Runtime und getrennte AA-/SH-/BT-Profile.
- Letzte Nutzerabnahme: keine. Kein Stable-Build und kein Merge freigegeben.
- Arbeitsbranch: `codex/cp00-baseline`; privates `xSonicB00Mx/medal-of-honor-allied-campaign`.
- Gebaute Engine: `3eec4afb22093421b8776d2df92b87ec2fb4119e`; Deployment: `c83f4bedd3cc3bdd06e37ac1d999566313004f05`. Spätere Bericht-/Testcommits ändern diese Binärzuordnung nicht.
- GitHub: Quellstände gepusht und per Remote-SHA geprüft; CI für beide genannten Commits erfolgreich. Kein Merge. GitHub verweigert Branchschutz im aktuellen privaten Tarif (HTTP 403); Verfahrensregeln sind kein serverseitiger Schutz.
- WCR: sieben Pakete und lose Inhaltsbasis unverändert übernommen; ausgewählte Laufzeitquellen belegt. **WCR_BASIS_UNGEKLAERT**: lokale Versions-/Changelog-Zuordnung fehlt, vollständige Inhaltsabnahme offen.
- Bestanden: zwei saubere lokale Builds, Hashprüfung von Original/Kopie/Runtime, drei gerenderte Save/Load-Smokes mit Menürückkehr, Rückbau in Wegwerfkopie.
- Offen: WCR-/MG42-/Finale-/Levelübergangstests, Optionspersistenz, Treffer-/Leichen-/Drop-Referenzen, Frametimes und Skript-/Ressourcenwarnungen; siehe Bericht.
- Sicherung: unabhängige Dateikopie und lokales Testpaket geprüft; keine zusätzlich gegen dieselben Schreibrechte geschützte bzw. externe Sicherung.
- Nächster erlaubter Schritt: Nutzerfeedback und ausschließlich CP0-Korrekturen/ausstehende Prüfungen. **CP0a nicht beginnen**.

Details und fünf Spielprüfschritte: [CP00-r1-Bericht](checkpoints/CP00/REPORT.md).
