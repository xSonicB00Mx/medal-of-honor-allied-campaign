# AB41-Maschinengewehr: Bluteffekte

Nutzermeldung: Fahrzeug-MG (als AB21 bezeichnet), nicht die Kanone.

Zwei Ursachen korrigiert: `models/vehicles/ab_turret_mini.tik` fehlte in der
exakten MG-Zuordnung; bei Geschossen ohne lebenden Sentient-Besitzer wurde
zudem die Waffenreferenz vor der visuellen Auswertung verworfen. Die rein
visuelle Auswertung behaelt jetzt die urspruengliche Referenz. Schaden,
Statistik-Zuordnung, Streuung, Munition und Projektilverhalten bleiben unveraendert.
Kein Saveformat und keine Missionsskripte geaendert.

Nativer BT-Test mit isolierter Kopie eines vorhandenen e2l2-Spielstands:
acht Schussereignisse mit je zwei Kugeln, 16 bestaetigte MG-Treffer, 32
Tropfenereignisse, aktivierter/autorisierter Nebel und Weltblutspuren.
32 Ein-/Austrittswunden gespeichert und wieder geladen. Zielgesundheit
wie im fehlschlagenden Vorher-Test: 7120 von 10000. Keine Skriptfehler.
Testberichte: `profiles-local/stats-briefing-breda/ab41-final/`.
Fruehe Tests r1/r2 dokumentieren fehlende Effekte trotz korrektem Schaden.
Die Screenshots zeigen den Spielerblick, nicht das ausserhalb platzierte
Testziel; Effektabnahme hier anhand nativer Treffer-/Clientdiagnosen.
Keine natuerliche Fahrzeugmissions-Abnahme vorweggenommen.
Stationaere Breda als Regression ebenfalls bestanden: acht Treffer, 16
Tropfenereignisse, Nebel/Weltspuren und 16 Wunden nach Save/Load erhalten
(`ab41-breda-regression`).

Game-DLL SHA256:
`4fbf734baf683e299d8cfa9c79a72305090289211144a1f914532310f5d0cc4f`.
Deployment verwendet `deploy_cp09_engine.py --game-only` mit Rueckbaukopien,
Runtime-Manifestpruefung sowie Schutzpruefung fuer Originale und Nutzerprofil.

Installiert in CP08-r1 und CP09-r1, Quelle `43161930`.
9072 Originaldateien, 9086 CP08- und 9090 CP09-Dateien geprueft.
Alle 439 persoenlichen Profildateien unveraendert. Nur game.dll ersetzt;
Engine, Cgame und Assets unveraendert.
