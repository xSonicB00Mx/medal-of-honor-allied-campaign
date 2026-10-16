# Pelletweise Schrotflinteneffekte

2026-10-16: Ursache war der ausdrueckliche Ausschluss der Schrotflinte in weapon_policy.json. Die bestehende BulletAttack-Schleife behandelt bereits jeden der neun Pellets einzeln, einschliesslich der toten/dying Geometriepruefung. Keine neue Schadensschleife, kein neuer Gameplay-Zufall und keine Aenderung an WCR-Waffenwerten.

Policy 5 ordnet models/weapons/shotgun.tik einer eigenen Gruppe 5 zu. Jeder bestaetigte Pelletkontakt erzeugt eine kleine Eintrittswunde (Radius 1.8), bei bestaetigter Austrittsgeometrie ebenfalls eine kleine Austrittswunde. Jede Seite emittiert unabhaengig sechs Tropfen; Blutnebel, Oberflaechenflecken und rueckseitiger Spruehzweig laufen ueber die vorhandenen Mod-Pfade. Fehlende Oberflaechentreffer erzeugen keine erfundene Wunde. Alle Effektschalter gelten weiterhin.

Clientvalidierung und Wundenmaterialauswahl akzeptieren die neue Gruppe, auch beim Speichern/Laden. Das Limit pro Actor steigt von 16 auf 32, damit eine Salve mit 18 Eintritts-/Austrittswunden vollstaendig gespeichert werden kann. Die globalen Grenzen bleiben 64 gespeicherte Wunden, 256 Tropfen, 128 Emissionen sowie 512 gezeichnete Patchdreiecke pro Actor / acht Actors. Keine vergroesserten globalen Arrays oder Save-Records. Alte Gruppen behalten ihre bisherigen kleinen/grossen Materialregeln.

Native Tests tools/test_shotgun_blood.py, jeweils eigene Profile:

- AA aa-r1, SH sh-r1, BT bt-r1: neun bestaetigte Pellets, 18 kleine Wunden, 108 Tropfen, Nebel und Bodenflecken. Save/Load behaelt alle 18 Wunden. Gesamtschaden im stationaeren Test jeweils 297 (neun mal 33).
- AA aa-death-r1: erster Pellet toetet den Testactor; alle acht restlichen Pellets laufen durch den bereits bestehenden corpse/dying-Pfad. Erneut neun Kontakte, 18 Wunden, 108 Tropfen und genau ein Todesereignis. Kein weiterer Schaden an dem toten Actor.
- Gemessene serverseitige BulletAttack-Dauer inklusive Visuals/Debugausgabe: 2-3 ms pro Salve. Dies ist keine pauschale GPU-/FPS-Garantie fuer beliebige Szenen. Globale Render-/Partikelgrenzen bleiben erhalten.
- Alle vier Prozesse normal beendet, keine Script-/UI-/reliable-command-overflow-Fehler. Sichtkontrolle der nativen AA-Nahaufnahme bestaetigt die getrennten kleinen Eintrittswunden und Bodenflecken. Generationstest --check bestanden.

Keine persoenliche Nutzerabnahme oder Merge behauptet. Tests benutzen ausschliesslich isolierte Profile.
