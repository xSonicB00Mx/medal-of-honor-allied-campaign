# Gemeinsame Spielstandliste

Direkter Nutzerauftrag 22.10.2026: die drei kampagnenspezifischen Save-Zugaenge
im Operations-Menue zu einer datumsortierten Liste mit automatischem Laden
der passenden Erweiterung zusammenfassen.

Ein Button `Saved Games` oeffnet nun eine gemeinsame Liste des aktiven Profils.
Spalten: lokales Datum/Uhrzeit, Kampagne und Spielstandname. Sortierung nach dem
numerischen Speicherzeitpunkt im Save-Header, neueste zuerst. Zehn Eintraege
pro Seite, sichtbare goldene Auswahl, Refresh und Load Selected Game.
AA/SH/BT bleiben auch bei identischen Slotnamen getrennt. Das Profil hat
Vorrang vor gleichnamigen Basisdateien. Beschaedigte/falsche Header und Eintraege
ohne SAV werden uebersprungen. Titel werden als Daten bereinigt, Slotnamen
vor der Verwendung in Befehlen validiert.

Laden im aktuellen Kontext verwendet den bestehenden nativen Load-Befehl;
andere Kampagnen verwenden den bestehenden ac_load-Wechsel samt Ladeblende.
Das aktive config-Verzeichnis wird jetzt beim Kontextwechsel mitgegeben.
Inhalts-/Save-Kompatibilitaetspruefung und die Highscore-Ladesperre bleiben
aktiv. Keine Spielstaende werden verschoben, neu geschrieben oder geloescht.
Das native Speicher-/Lademenue ausserhalb dieses Operations-Zugangs bleibt erhalten.

Native Pruefung `test_unified_saves.py unified-saves-r2`:

- 14 Eintraege ueber zwei Seiten, strikt absteigende Zeitstempel.
- Drei identische Slotnamen aus AA/SH/BT als getrennte, richtig zugeordnete Zeilen.
- Beschaedigter Header und falscher Kampagnentyp ausgeschlossen.
- Lange Titel mit Anfuehrungszeichen/Backslashes sicher dargestellt; Screenshot
  der Liste bei 1920x1080 visuell geprueft, keine abgeschnittenen Spalten.
- Kopien vorhandener Nutzer-Saves aus jeder der drei Kampagnen erfolgreich
  geladen; native Metadatenannahme und Game Loaded bestaetigt.
- Fremdkontexte melden die Uebernahme durch den neuen Prozess nach der Ladeblende.
- Originales persoenliches Profil vor/nach dem gesamten Test per Hash unveraendert.

Frueher Test r1 fand eine hinter dem Test-Quit angehaengte Load-Anweisung.
Der ausgewaehlte Load wird jetzt unmittelbar vor die restliche Befehlswarteschlange
eingefuegt; finaler Lauf r2 bestanden. Belege bleiben lokal unter
`generated-local/CP09/unified-saves-r2` und `profiles-local/unified-saves/`.

Installiert in CP08-r1 und CP09-r1, Quelle `5c71300d`.
Engine-SHA256: `af1614e419f638250c2068dde682a63e44067ea41118f54aadb3d2e059f0888c`.
9072 Originaldateien, 9086/9090 Runtime-Dateien verifiziert; alle 456
persoenlichen Profildateien unveraendert. Nur Engine ersetzt, lokale
Rueckbaukopien im Berichtordner unter `rollback`.
