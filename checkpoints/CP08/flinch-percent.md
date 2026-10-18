# Hit-Flinch-Prozentregler

2026-10-18: Hit flinch bietet 0 bis 100 Prozent in zehn Prozentpunkten pro Schritt, inklusive Prozentanzeige. Rechter Abschnitt heisst Additional Options. Standard und Defaults bleiben 20 Prozent.

ac_player_flinch_percent ersetzt den Dreistufenwert. Initialisierung nach Konfigurationsimport migriert fehlenden Prozentwert aus ac_player_flinch_mode: 0 -> 0, 1 -> 20, 2 -> 100. Ein vorhandener Prozentwert hat Vorrang. Neue Profile starten bei 20. Gemeinsame Kampagnenpraeferenzen speichern den Prozentwert. Trefferwinkel werden nach Originalbegrenzung mit dem gewaehlten Anteil multipliziert; externe Werte werden auf 0..100 begrenzt und auf Zehnerschritte gerundet. Rote Schadenseinblendung, Rueckstoss, BT-Dropoption und Saveformat unveraendert.

Native Tests in isolierten Profilen:
- AA percent-aa (213 Samples), SH percent-sh und BT percent-bt (je 212): alle elf Stufen anhand echter gerichteter Schadensereignisse geprueft. Ausgabe entspricht Quelle mal Prozent innerhalb Protokollrundung, Rotblendung erhalten, keine Script-/Event-/Kommando-Fehler.
- flinch-percent: AA -> SH -> BT -> AA und frische Prozesse aller Kampagnen behalten 70 Prozent und BT-Dropoption.
- test_flinch_migration.py: Off/Reduced/Original ergeben 0/20/100; vorhandene 70 Prozent werden nicht ueberschrieben; neues Profil 20 Prozent.
- Native FHD-Menueansicht: Prozentwert und Additional Options korrekt, keine Ueberlappungen. game/Engine erfolgreich gebaut.

Keine persoenliche Nutzerabnahme oder Merge behauptet.

Installiert als flinch-percent-r3 aus 3f7ea7b8. Alle 78 Laufzeitdateien hashgeprueft, Engine/game/cgame bytegleich mit Testbuild. 382 persoenliche Profildateien, 9072 Originaldateien, 9000 Basisdateien und acht MP-Eingaben unveraendert. Ruecksicherung: generated-local/widescreen/backups/flinch-percent-r3.

## Korrektur 2026-10-18: Maus-Raster

Die vorherigen Tests prueften Schadenswerte, nicht den Mauspfad des Reglers. stepsize galt nur fuer Pfeile; Pressed/MouseDragged schrieben kontinuierliche Werte. Der Flinch-Regler rundet jetzt vor jeder Ausgabe auf 0/10/.../100. Beim Einlesen werden alte Zwischenwerte ebenso normalisiert. Andere Slider bleiben unveraendert. Ueberschrift jetzt ADDITIONAL OPTIONS.

Engine-Build erfolgreich. tools/test_flinch_slider.py prueft pro Kampagne 121 echte Widget-Klickereignisse und 121 Ziehereignisse: alle elf Stufen erreicht, keine Zwischenwerte, alter Wert 37 wird 40 und als 40 gespeichert. Pakete aller drei Kampagnen auf Grossschreibung geprueft; native Menueaufnahme kontrolliert. Isolierte Profile snap-r4; keine persoenliche Abnahme behauptet.
