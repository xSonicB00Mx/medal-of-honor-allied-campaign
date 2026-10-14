# CP08-r1: MG-Ruckler und Kartenhinweis

`Approximate mission area` wurde aus der Missionsauswahl entfernt; beide regionalen Ansichten wurden nativ in Full HD geprueft und visuell kontrolliert.

## Ursache und Korrektur

Die Wundgeometrie wurde bisher als viele grosse Hex-Textnachrichten ueber denselben zuverlaessigen Kanal wie Spielzustandsupdates uebertragen. Ein-/Austrittswunden bei MG-Treffern fragmentierten die Pakete und blockierten weitere Snapshots. Der reproduzierte m1l1-MG-Lauf erreichte 509 ausstehende Befehle, 24.732 Bytes pro Snapshot und bis zu 250 ms Abstand bereits vor dem Ueberlauf. Danach trennte die Engine die lokale Verbindung. Die exakte Oberflaechenabfrage selbst brauchte maximal 206 Mikrosekunden; die Patchberechnung maximal 97 Mikrosekunden. Der Engpass lag in der Uebertragung, nicht in einer notwendigen Reduktion der Todesanimationen.

Lokales Einzelspiel uebergibt nun dieselben unveraenderten Wunddaten ueber einen begrenzten Speicher innerhalb des Prozesses. Nur eine kurze Referenz durchlaeuft den normalen zuverlaessigen Befehlskanal, sodass Reihenfolge und Zeitpunkt zur zugehoerigen Zustandsaktualisierung erhalten bleiben. Es gibt keine Verringerung der Textur-/Geometriequalitaet und keine Effektdrosselung. Der Speicher umfasst maximal 256 Transportdatensaetze; verbrauchte, nach CGame-Neustart ungueltige oder verdraengte Referenzen koennen nicht auf andere Treffer zeigen. Normale Szenen-/Actor-Wundlimits bleiben erhalten. Nichtlokale Verbindungen und Demoaufnahmen verwenden weiterhin das eigenstaendige alte Drahtformat; deren Performance ist nicht Gegenstand dieser Korrektur.

Kugelpfad, Durchdringen sterbender Gegner, Schadensberechnung, Todesereignisse und Drops wurden in dieser Korrektur nicht geaendert. Die DLL-Schnittstelle ist nun Version 16, waehrend das unveraenderte Level-Speicherformat explizit Version 15 behaelt. Engine, game.dll und cgame.dll werden gemeinsam geliefert.

## Messungen und Regressionen

Der isolierte Test kopiert den bestehenden m1l1-Spielstand, versetzt das dortige MG auf eine per Weltabfrage freie Schussbahn und erzeugt nur im Testprofil Ziele. Native MG-Shoot-Ereignisse erfolgen alle 60 ms. Erst erhaelt ein Ziel sechs Sekunden Dauerfeuer, anschliessend folgen fuenf natuerliche Todesanimationen. Das ersetzt keine manuelle Wiederholung der gesamten originalen Gegnerwelle.

- Drei korrigierte MG-Laeufe: Snapshotabstand durchgehend 50 ms in Ruhe, Feuer- und Todesphase. Keine Bildberechnung ueber 33 ms; hoechster gemessener Wert 11 ms. Ohne Effekt-Debugausgabe maximal 8 ms. Kein Befehlsueberlauf oder Verbindungsabbruch.
- In zwei Laeufen wurden alle 248 beziehungsweise 235 erzeugten Wunden empfangen. Die Todesphase enthaelt 21 beziehungsweise 15 optische Koerpertreffer waehrend der Animation.
- Bestehender Save mit 33 Wunden geladen. Neuer Save mit 41 Wunden geschrieben und mit 41 Wunden wieder geladen. Originalprofil und seine Saves bleiben unberuehrt.
- AA, SH und BT: 36 gepaarte Durchschusstests mit Leicheneffekten an/aus haben identischen Hintermann-Schaden; jeder der drei Laeufe bestaetigt animierte Koerpertreffer, durchdringende Kugeln und genau ein Todesereignis. Zwei erste AA-/BT-Laeufe verfehlten das animierte Mesh und gelten nicht als bestanden; die expliziten Becken-Wiederholungen sind die positiven Nachweise.
- Nativer Release-Build, C++-Tests fuer Datensatztransport/Orientierung/Trefferintervalle sowie Metadaten-/Kampagnenvalidatoren bestanden. Optionale `ac_perf`-Diagnose erfasst Snapshotgroessen/Abstaende und ab Stufe 2 Geometriezeiten; standardmaessig aus.

[Maschinenlesbare Zusammenfassung](mg-feedback-verification.json), [Vorher-Nachweis](mg-before-reproduction.json), [normaler MG-Nachtest](mg-after-normal.json), [Save/Load](mg-after-roundtrip.json). Fruehe unbrauchbare Aufbauversuche sind lokal als Diagnosen erhalten und nicht als bestandene Tests gezaehlt. Keine pauschale Freigabe aller Karten/WCR-Varianten, keine persoenliche Abnahme und kein Merge.
