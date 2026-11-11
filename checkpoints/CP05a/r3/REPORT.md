# CP05a-r3 - gemeinsames 16:9-Optionsmenue

Auftrag: Das Zusatzmenue fuer alle Allied-Campaign-Features in **Allied Campaign Options** umbenennen und die ueberlappende Darstellung durch ein breiteres 16:9-Layout korrigieren. Engine-/UI-Quelle: `5a9b6aa7e9877d4fb3dd328838d9ab4940deb5ce`, frisch remote verifiziert auf `codex/cp05a-corpse-effects`. Entwurfs-PR #8 bleibt ungemergt.

Die bisherige 640x480-Seite hat jetzt einen 960x540-Entwurfsraum. Links stehen Anzeige-/HUD-Einstellungen, rechts die vier Effektschalter. Alle 25 Elemente haben getrennte Rechtecke; Wertefelder liegen neben, Beschriftungen ueber den Reglern. Der Titel und der Einstieg in allen drei Optionsmenues sind englisch und von der Lokalisierung ausgenommen. Die vorhandenen acht WCR-Optionsbindungen pro Spiel wurden beim Verpacken erhalten.

Die Seite und ihre Nachfahren verwenden einheitlich `min(Breite/960, Hoehe/540)`. Zeichnung, Begrenzungsrechtecke und Maus-Hitboxen nutzen denselben vorhandenen Widgetpfad. Die Seite passt mittig auf 16:9, 4:3 und Ultrawide. Ihre eigene Groesse haengt bewusst nicht von den Reglern ab, die der Nutzer dort bedient: Dadurch bleiben Regler und Eingabefelder beim Aendern von Menu-/HUD-Groesse und automatischer Skalierung stabil. Alle bisherigen Spielmenues behalten ihre eigene Skalierung. Der Einstiegsbutton hat einen eigenen internen Namen, damit er nicht faelschlich die Skalierung der ganzen Einstellungsseite erbt.

## Pruefung

Nativer Windows-Build erfolgreich. `tools/test_campaign_options.py` oeffnet die echten Menues in isolierten Profilen, erfasst die tatsaechlichen Widgetrechtecke und prueft alle Elementpaare auf Ueberlappung und alle Elemente auf Begrenzung innerhalb der Seite. Es prueft ausserdem gleichbleibende Geometrie bei Menugroesse 0,65 und 1,5, HUD-Groesse 2, automatischer Skalierung aus/ein sowie Schliessen und erneutem Oeffnen. Die finalen Laeufe heissen `clean-*` und enthalten die exakten Binaerhashes.

Finale Aufloesungen: AA 1920x1080, 1280x960 und 2560x1080; SH 1280x720; BT 2560x1440. Die unverdeckten Bilder wurden zur Kontrolle von Textbreiten, Zahlenfeldern und Abstaenden angesehen. Ein zusaetzlicher AA-4K-Lauf ist separat protokolliert. Die ersten Diagnosebilder enthielten eine Entwicklerkonsole; sie gelten nur als Geometrienachweise. Ein Zwischenversuch mit Elternlosigkeit als Containererkennung bestand die Groessenpruefung nicht und wurde vor der Auslieferung korrigiert. Kein erfolgreicher physischer Maus-, OS-DPI- oder Alt-Tab-Test wird daraus abgeleitet.

## Bereitstellung

`Start-CP05a-r3-AA/SH/BT.cmd` verwenden getrennte Runtime und Nutzerprofile. 56 Nutzerdateien aus r2 wurden unveraendert kopiert. `build-manifest.json`, `integrity.json` und `package.json` binden die Binaerdateien, erhaltene Basis und CRC-/SHA-gepruefte lokale Laufzeitsicherung. Originalassets und Spielstaende bleiben aus Git ausgeschlossen. Die Spiel-DLLs, Blutlogik, Saveschemata und vorherigen Kandidaten sind unveraendert. Github-Build- und Delivery-Nachweise werden lokal im Auslieferungsprotokoll festgehalten.

Persoenliche Abnahme und Merge bleiben offen. Die allgemeinen Gameplay-/Material-Testgrenzen aus r2 bleiben bestehen; diese Lieferung aendert nur Menue und UI-Skalierung.
