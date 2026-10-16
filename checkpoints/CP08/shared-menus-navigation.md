# Einheitliche Menues und direkte Rueckkehr

2026-10-16: Acht Ansichten (AA-Hauptmenue sowie AA-Options-/Steuerungsansichten) in allen drei Kontexten paketiert. Bilder und Shader bekommen eigene Namen, damit Erweiterungsassets die AA-Darstellung nicht ueberschreiben. Generierte Operations-Beschriftung bleibt erhalten. War Records, Medaillen, Save/Load, Missionsbriefings, Ladebilder und Spiel-DLLs werden nicht ersetzt. Pakete/Assets bleiben lokal und ignoriert.

Ursache des Rueckkehr-/Musikfehlers: PopMenu sperrt den Menustack bis zum naechsten Eventdurchlauf, wodurch das folgende pushmenu main verloren ging. Im Spiel blieb kein Menue; ausserhalb des Spiels oeffnete die automatische Disconnected-Behandlung main und startete die Intromusik neu. ac_main_menu ersetzt die zwei getrennten Befehle atomar ohne Disconnect oder Sound-Neustart. Auch die entsprechenden Score-Abschlussbuttons verwenden den korrigierten Pfad.

CURRENT und aktuelle Kartenmarker verwenden 1/0.58/0.45 wie Reset Progress. Die Auswahl bleibt gelb mit Pfeil, abgeschlossene Eintraege gruen.

RelWithDebInfo-Engine erfolgreich gebaut. Native isolierte Tests mit tools/test_menu_navigation.py in 1600x900:

- AA aa-menu-r1, SH sh-menu-r2, BT bt-menu-r1: Operations/Mission List/Briefing Room jeweils zurueck zu main; Musikposition waechst monoton, kein Neustart. Haupt-/Options-/Steuerungsansichten sowie native War Records und Save/Load geoeffnet.
- AA aa-game-r1 (m1l1), SH sh-game-r1 (t1l1), BT bt-game-r1 (e1l1): derselbe Rueckkehrpfad bei laufender Mission, Client bleibt aktiv. Kein Disconnect/Progress-Reset.
- SH sh-menu-r2: CURRENT-Farbe, privater Operations-Schriftzug und Optionslayout anhand nativer Screenshots geprueft. Die Tests rufen dieselben Befehle wie die Buttons auf; kein manueller Klicktest behauptet.
- Fortschrittssentinel in allen sechs Profilen unveraendert. Keine Unknown-command-/fehlendes-Menue-/UI-Exception-Fehler. Nutzerprofil nicht zum Testen verwendet.

Keine persoenliche Nutzerabnahme oder Merge behauptet.

Installiert als shared-menus-r1 aus Commit cea81c16. Alle 72 verwalteten Dateien hashgeprueft, Engine bytegleich mit Testbuild. Integritaet: 9072 Originaldateien, 9000 Basisdateien, 8 MP-Eingaben und 261 aktuelle persoenliche Profildateien unveraendert. Ruecksicherung: generated-local/widescreen/backups/shared-menus-r1.
