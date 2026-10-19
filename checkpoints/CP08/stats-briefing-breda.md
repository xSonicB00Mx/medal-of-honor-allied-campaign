# Kampagnenstatistik, AA-Briefings und Breda 30

2026-10-19, Nutzerfeedback mit drei Bildschirmfotos.

- Kampagnenstatistik: Originalfelder waren fuer die neue Schrift zu schmal (unter anderem 32 virtuelle Pixel fuer Prozentwerte). Lokale Overlay-Pakete verbreitern Werte und Beschriftungen, ordnen die Spalten neu und erhalten alle Cvar-Bindungen, Hintergruende und Schriftarten. AA: drei Ressourcen; SH und BT: jeweils sechs, einschliesslich mission_success_1 bis 3. Keine Originalassets im Repository.
- AA-Briefings: Die laufenden Briefing-Maps zeichnen ihre Raumkulisse ueber Script-HUD-Elemente und umgehen damit den bereits angepassten Menuehintergrund. Der Client ersetzt die beiden alten Raumkacheln durch das vorhandene vollstaendige 16:9-Bild. Projektorfolien, Untertitel, Blendphasen und Skip-Hinweis behalten ihre gemeinsame zentrierte Geometrie. Auf 4:3 wird die breite Kulisse seitlich beschnitten, nicht verzerrt.
- Breda: Der stationaere Typ models/statweapons/It_W_Breda_gun.tik fehlte in der exakten Waffenliste. Er verwendet nun das vorhandene MG-Blutprofil (Gruppe 4). Die tragbare Breda war bereits erfasst. Schaden, Munition, Streuung und Schussfolge bleiben unveraendert; kein Saveformatwechsel.

## Pruefung

game/cgame RelWithDebInfo erfolgreich gebaut; generierte Policy mit 40 exakten IDs validiert; git diff --check sauber.

Isolierte native Profile unter profiles-local/stats-briefing-breda:

- stats-aa-r3 und stats-bt-r3: Full HD; stats-sh-r3: UHD. Erfolgs-/Fehlschlagstatistik sowie alle drei Erweiterungs-Abschlussansichten mit Testwerten angezeigt. Sichtkontrolle repraesentativer AA-, SH- und BT-Erfolgsansichten: 100.0, fuenfstellige Zaehler, Zeit und lange Beschriftungen ohne Abschneiden/Spaltenueberlagerung. Der anfaengliche pushmenu-Test zeigte die Erweiterungsansichten nicht korrekt; korrigiert auf den nativen showmenu-Pfad und erneut ausgefuehrt.
- briefing-aa-r1: alle sechs echten AA-Briefing-Maps in Full HD geladen, Screenshots und keine Script-/Ressourcenfehler. Erste und letzte Ansicht visuell geprueft: bildfuellender Raum, passende Projektionsflaeche, zentrierter Skip-Hinweis.
- breda-r2: echte stationaere Breda im isolierten BT-Spielstand mit kontrolliertem Ziel. Acht bestaetigte Treffer mit Gruppe 4, jeweils Eintritt und Austritt, 16 Tropfen-Emissionen, Nebel und Weltblut. 16 Wunden gespeichert und 16 wieder geladen; Screenshot mit Koerperwunde und Bodenblut geprueft. Erste Testfixture scheiterte am deaktivierten Entwickler-Scriptbefehl und wurde vor dem erfolgreichen Test korrigiert.

Keine natuerliche Durchspielung aller Missionen oder persoenliche Nutzerabnahme behauptet. Testwerte sind synthetisch. Persoenliches Profil nicht fuer Tests verwendet.
