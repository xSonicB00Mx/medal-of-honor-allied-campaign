# Optionales Spieler-Trefferflinching

2026-10-17: Player hit flinch in Allied Campaign Options, standardmaessig aus. ac_player_flinch ist archiviert und Teil der kampagnenuebergreifenden Praeferenzen. Defaults setzt den Schalter auf aus.

Ursache: Player::DamageFeedback berechnet Trefferwinkel unabhaengig vom roten damage_blend. Die Kamera erhielt diese Winkel in der Playerstate-Aufbereitung. Ausschliesslich dieser Trefferzweig wird im Einzelspieler bei deaktiviertem Schalter ausgelassen. DamageFeedback, Trefferpunkte, rote Einblendung, Richtungsanzeige, Animationen, Waffenrueckstoss und geskriptete Erdbeben bleiben erhalten. Keine Aenderung von Archivfeldern oder Saveformat; alte gespeicherte Trefferwinkel werden ebenfalls vor der Kameraausgabe gefiltert. Einschalten wirkt ohne Neustart.

Tests:

- Native Builds game und openmohaa erfolgreich.
- tools/test_player_flinch.py: AA aa-r3, SH sh-r2, BT bt-r2; jeweils aus/an/aus und 58 protokollierte Feedbacksamples. Diagnostische gerichtete Treffer ziehen 10 Gesundheit ab; rote Alphaeinblendung in beiden Schalterstellungen vorhanden. Bei aus alle Treffer-Kamerawinkel null, bei an urspruengliche Winkel ungleich null. Keine Scriptfehler, unbekannten Befehle oder ungueltigen Events. Isolierte Profile; Erweiterungen laden kopierte Referenzspielstaende.
- Native Menueansicht 1920x1080 geprueft: Beschriftung und Checkbox passen in die freie rechte letzte Zeile. Bestehender Nutzerhintergrund und alle effektiven Einstellungen erhalten.
- tools/test_shared_preferences.py --run-id flinch-r1: AA -> SH -> BT -> AA und anschliessend frische Prozesse aller drei Kampagnen. ac_player_flinch=1 bleibt erhalten, ebenso bisherige Grafik-/Steuerungspraeferenzen; Missionszustand wird nicht geteilt.

Keine Nutzerabnahme oder Merge behauptet. Testprofile und Bildschirmbilder bleiben lokal.
