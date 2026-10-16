# Ballistische Moerser-Zielhilfe

2026-10-17: BT-Moerserbeschriftung auf englisches "Mortar" umgestellt und Textfeld verbreitert. Roter Bodenring und leuchtende vertikale Saeule markieren den berechneten ersten Kontakt der Granate.

Die Vorschau verwendet GetMuzzlePosition und die echten TIKI-Projektilparameter (Geschwindigkeit, Schwerkraft, Lebensdauer, Kollisionsbox, Zusatzgeschwindigkeit). Integration entspricht MOVETYPE_BOUNCE mit Serverzeitschritt, Geschwindigkeitsgrenze und Projektil-Kollisionsmaske. Eigene Waffen-/Sockelcontents werden ausschliesslich waehrend der synchronen Abfrage ausgeblendet und durch RAII wiederhergestellt; alte Saves ohne brauchbare Sockelbindung werden anhand des initial beruehrten granatwerfer_base-Modells beruecksichtigt. Keine neuen archivierten Felder, Gameplay-Zufallszahlen, Projektilspawns oder Schadensaenderungen. Maximal 1024 Sweeps je Serverframe; nur beim vom Spieler bedienten Moerser. Clientmarker verfaellt nach 150 ms ohne Aktualisierung, nach Absteigen oder ungueltiger Flugbahn. Himmelskontakte erzeugen keine erfundene Bodenmarkierung.

Validierung mit tools/test_mortar_aim.py in isolierten Profilen:

- Persoenlichen BT-e2l3-Quicksave als Kopie erfolgreich geladen; aus der Kopie neu gespeichert und erneut geladen. Persoenliche Profildateien per SHA256 vor/nach jedem erfolgreichen Test unveraendert.
- final-r1 --turn -50 --expect-ground: 205 Vorhersagen; vorhergesagter und echter Einschlag identisch bei (1656.414, -2981.798, 13.054), Fehler 0.000 in den protokollierten Koordinaten. Nach Absteigen keine weiteren Zielmeldungen. Native Screenshots bestaetigen lesbares HUD, sichtbare rote Markierung und deren Verschwinden nach Absteigen.
- user-r6: urspruengliche Blickrichtung, Laden/Schuss/erneutes Laden erfolgreich. Ein bewegter Panzer veraendert den tatsaechlichen ersten Kontakt waehrend der Flugzeit; die Vorschau stellt die Welt zum Zeitpunkt des Zielens dar, keine Vorhersage zukuenftiger Fahrzeugbewegungen.
- Rechtsdrehung: Himmel/ungueltiger Startkontakt blendet Marker aus; keine falsche Bodenposition.
- Release-with-debug-info-Builds game/cgame erfolgreich. Drei Warnungen ueber fehlende Breda-Clipanimation beim Laden im Testprotokoll; keine Scriptfehler oder unbekannten Kommandos. Diese Assetwarnung wurde in diesem Auftrag nicht behoben.

Keine persoenliche Abnahme oder Merge behauptet. Originalassets, Saves und Binaerdateien nicht versioniert.

Installiert als mortar-aim-r1 aus 0d8aa726. Alle 75 Laufzeitdateien hashgeprueft, game/cgame bytegleich mit dem Testbuild. 350 persoenliche Profildateien, 9072 Originaldateien, 9000 Basisdateien und acht MP-Eingaben unveraendert. Ruecksicherung: generated-local/widescreen/backups/mortar-aim-r1.
