# Spearhead D-Day: heller Himmel im vereinfachten Modus

Ursache: Das persoenliche Profil verwendet `r_fastsky 1`. Der Renderer ersetzte
den Himmel in einem Clear-Pfad durch festes RGB (0.5, 0.5, 1.0), unabhaengig von
der Tageszeit der Karte. In t1l1 wird daraus mit Gamma 1.3 eine helle blauviolette
Flaeche. Die Nacht-Lichtkarten und die WCR-Missionsskripte sind intakt.

Korrektur: Der vereinfachte Himmel verwendet die Farplane-Farbe der aktuellen
Ansicht mit dem bestehenden identityLight-Faktor. Keine globale Abdunklung,
keine Aenderung von Profilen, Saveformat, Missionen oder normalem Skybox-Modus.
Auch ohne aktivierten Nebel wird kein veralteter GL-Nebelzustand benutzt.

Native Pruefung: `tools/test_night_sky.py`, getrennte Profile, Kopie des bestehenden
Spearhead-Spielstands t1l10001. Feste Testkamera im Aussenbereich; vereinfachter
Himmel, normaler Himmel und vereinfachter Himmel ohne Nebel. Vorher 493867 bzw.
493797 Pixel des fehlerhaften hellblauen Hintergrunds; nachher jeweils null.
Screenshots vorher/nachher visuell geprueft: dunkler Nachthimmel, Landschaft und
Scheinwerfer erhalten. Vorhandener Spielstand erfolgreich geladen. Alle 462
persoenlichen Profildateien nach beiden Testlaeufen byteidentisch.

Build: openmohaa RelWithDebInfo erfolgreich. Getestete EXE SHA256:
`2ba609fbf0b604092d12e9debe4132d4c08d6b9e4ba2b5abf24987f366a79db9`.
Berichte/Bilder: generated-local/CP09/night-sky-{before,fixed},
profiles-local/night-sky/night-sky-{before,fixed}.
Die natuerliche Missionsabnahme durch den Nutzer bleibt offen.
