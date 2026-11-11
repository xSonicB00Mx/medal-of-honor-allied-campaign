# CP05-r2 – sichtbares Weltblut, Charakterbeleuchtung, mittige Briefings

Korrektur des Nutzerfeedbacks vom 14.10.2026, in der gewünschten Reihenfolge begonnen: zuerst fehlende sichtbare Blutpartikel/Umgebungsflecken, danach Körperbeleuchtung und Briefingposition. Engine-Quellstand: `89437fe58fc41a4d11b21e0a762560bced56c12a`. Kein neuer Checkpointumfang, keine CP5a-Leichentreffer, kein Merge und keine unterstellte Nutzerabnahme.

## Ursachen und Änderungen

Der r1-Vergleich zeigt bereits einige Bodenflecken, aber nur als kleine Pixelspuren. Für fliegende Tropfen wurde zudem dieselbe MP1-Bodenflecktextur verwendet. r2 importiert selektiv die 16 originalen RGB-TGA-Partikelbilder und ihre PCX-Alpha-Masken aus dem lokal vorhandenen `blood_projectile_trail.rps`. Archiv, RPS und einzelne Bilddaten sind hashgebunden; unveränderte Auflösung 16×16, keine Umfärbung. Die Simulation bleibt eine eigene begrenzte Implementierung, kein RPS-Codeport. Herkunft und Konvertierung stehen in `mp1-import.json`. Keine Fremdassets im Git.

Tropfenradius 1,8 statt 0,7; Bodenfleckradius 3–5 statt 0,9–1,7; direkter Rückspritzer 7 statt 3,5. Weltflecken verwenden weiterhin die originale MP1-Decaltextur. Die bestehenden Lebensdauern und Budgets gelten weiter. Es werden keine zusätzlichen Schadensereignisse erzeugt und keine Waffenwerte geändert.

Die serverseitig bestätigte Eintritts-/Austrittsfläche wird nun zusätzlich über Mesh, Dreieck und baryzentrische Koordinaten übertragen. Erst beim Aufbau der aktuellen Clientpose wird dort emittiert. Damit startet ein Partikel nicht an einem veralteten Weltpunkt innerhalb einer neu begonnenen Trefferanimation. Kollisionen gegen Körper, Ausrüstung und Umgebung bleiben aktiv; eine tatsächlich verdeckte Rückseite erzeugt keine durchgehenden Spritzer. Der initiale Vergleich mit normal reagierendem Gegner und die isolierten freien Wandtests stehen getrennt in den JSON-Dateien.

Die r1-Körperwunden verwendeten `GetLightingForDecal`: eine Welt-Lightgrid-Probe, die die Flächennormale ignoriert und nicht der Charakterbeleuchtung entspricht. r2 ordnet die deformierten Wunddreiecke ihrem Actor im Renderer zu, transformiert sie in dessen Modellraum und verwendet `lightingSpherical` mit seiner vorhandenen Beleuchtung und den aktuellen Dreiecksnormalen. Die Texturen, ihr Alpha, Wundgröße und gespeicherte Orientierung bleiben erhalten. Weltflecken werden anschließend ausdrücklich wieder im Weltkoordinatensystem gezeichnet.

AA-Briefings bestehen aus geskripteten `huddraw`-Bildteilen. Diese wurden proportional skaliert, aber weiter links verankert. Ihre gemeinsame 640×480-Fläche wird nun zentriert und unabhängig von HUD-Größe/-Rand eingepasst. Vollbild-RoQ-Videos erhalten ebenfalls eine zentrierte 4:3-Fläche. Schwarze Ränder werden direkt im unmittelbaren Video-Zeichenweg gelöscht; eingebettete Videorechtecke bleiben unverändert.

## Prüfungen

Native Windows-Builds erfolgreich. Metadaten-/Ausschlussprüfung, alle 37 Waffen-IDs sowie die vorhandenen 65.536 Zufalls-/Transformationsfälle und Intervallfälle erfolgreich. GitHub-Build fuer Quellstand `89437fe` erfolgreich: [Lauf 38530780174](https://github.com/xSonicB00Mx/medal-of-honor-allied-campaign/actions/runs/38530780174). Der abschliessende Auslieferungsstand wird in der lokalen Delivery-Datei festgehalten.

- AA-Vorher/Nachher bei 1920×1080: Briefing vorher x=0–1439, nachher x=240–1679; auch bei HUD-Größe 1,5 und Rand 0,8 bleibt die Bildfläche zentriert.

- Finaler Build auch bei 2560x1080 (Bild x=560-1999) und 1280x960 (Bild x=0-1279) visuell und anhand der Bildgrenzen erfolgreich geprueft.
- Identischer gespeicherter AA-Gegner: Die mittlere rote Komponente der sichtbaren Wundpixel sinkt im Schatten von 62,56 auf 28,48. Eine gezielte Fullbright-Diagnose erhöht sie zusammen mit dem Körper auf 98,63. Das ist ein Nachweis der Beleuchtungsanbindung, kein Ersatz für sämtliche Kartenlichtsituationen. Die normale Auslieferung aktiviert diese Diagnose nicht.

- Sichtbare fliegende Partikel und Bodenflecken mit normalen Trefferreaktionen in AA, SH und BT; native echte Schüsse, getrennte Testprofile. Screenshots manuell geprüft.

- Finaler AA-Wandtest mit Pistole, MP, Gewehr und MG: 9 bestätigte Treffer, 117 Weltmarken/Fragmentmeldungen, darunter 9 direkte rückseitige Wandflecken; keine fehlenden Körpercaches oder Patch-Budgetfehler. Ein-/Austritte und Save/Load separat validiert.

- Getrennte Schalter für Nebel, Weltblut und Körperwunden sowie alle aus, Schrotflinten-Ausschluss und Persistenz nach echtem Prozessneustart erfolgreich geprüft.

- Finaler SH-Bewegungs-/Ducktest und BT-Test mit genau einem echten Todesereignis; Wunddaten und Save/Load validiert.

- SH- und BT-Videos im finalen Build direkt gestartet und mit dem Computer-Use-Skill am tatsächlichen Spielfenster geprüft: laufendes Bild, zentriert, gleiche schwarze Seitenränder bei 1280×720.

Frühe `briefing-SH-wide`-/`briefing-BT-fhd`-Skripte sind **keine** erfolgreichen Videosichttests: Die vorab gefüllte Konsolenwarteschlange verzögerte den vom Mapskript angehängten Film bis hinter `quit`. Ihre schwarzen Raumaufnahmen bleiben als Diagnose erhalten. Die gesonderten `movie-*-verified`-Läufe ersetzen diesen Nachweis. Auch die erste Live-Videofassung mit hellen Randflächen zählt nicht als bestandener finaler Test.

Der Build und die Texturpakete sind in `build-manifest.json` bzw. den Importmanifesten eindeutig zugeordnet. Einzelne frühe Vergleichsläufe verwenden einen Vorbuild vor der reinen Korrektur der Videoränder; ihre eigenen Hashes bleiben erhalten. `visual-review.json` beschreibt die tatsächlich angesehenen Bilder und die native Videoprüfung.

## Bereitstellung und Grenzen

Die Startdateien **Start-CP05-r2-AA/SH/BT.cmd** nutzen `runtime-local/CP05-r2` und `profiles-local/CP05-r2/user`. 38 Dateien aus dem bisherigen r1-Nutzerprofil einschließlich Saves und Konfiguration wurden unverändert kopiert und hashverglichen. Die Tests benutzen eigene Profile. Keine neuen Benutzereinstellungen erzwungen.

9.072 geschützte Eingabedateien, 9.000 Runtime-Basisdateien und die MP1-Eingaben unverändert geprüft. Alle 23 eigenen r1-Runtime-Dateien stimmen weiterhin mit dem r1-Manifest überein. CRC-/SHA-geprüfte lokale Sicherung: `artifacts-local/CP05-r2-runtime.zip`; enthält Originalassets und wird nicht hochgeladen.

Die drei gemeldeten Darstellungsfehler sind im geprüften GL1-Kandidaten korrigiert. Allgemeine CP5-Testlücken aus dem r1-Bericht bleiben offen, insbesondere die vollständige Modell-/Waffen-/Umgebungsmatrix und GL2. Die persönliche visuelle Abnahme des Nutzers steht aus. Eine technische Korrektur ist keine automatische Freigabe zum Merge.
