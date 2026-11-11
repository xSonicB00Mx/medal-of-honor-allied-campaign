# Flinching-Modi und live umschaltbare BT-Dropregeln

2026-10-18: Nutzer bestellt Flinching mit 20 Prozent sowie aus/original/reduziert im Menue und bestaetigt den Schalter fuer urspruengliche BT-Dropbeschraenkungen.

Hit flinch: ac_player_flinch_mode 0=Off, 1=Reduced (20%), 2=Original. Neuer Standard 1; die fruehere boolesche ac_player_flinch-Einstellung ist obsolet und ueberschreibt den neuen Standard nicht. Multiplikation erfolgt nach der urspruenglichen Winkelberechnung und Begrenzung, daher exakt 20 Prozent fuer Pitch/Yaw/Roll und deren Abklingen. Rotblendung, Schaden, Waffenrueckstoss und Erdbeben bleiben unveraendert. Keine neuen Savefelder.

BT drop restrictions: ac_bt_drop_limits 0=aus (Standard), 1=an. An stellt die urspruenglichen global/loadout.scr-Regeln wieder her: Gesundheit und Waffen gesperrt ausser beides in e1l1 sowie Waffen in e1l3; zusaetzliche gespeicherte Skriptsperren und Hard-Gesundheitssperre gelten. Die Regeln wurden gegen die lokalen Original-pak*-Skripte geprueft. Damit funktioniert die Umschaltung auch bei alten Saves, deren Level-Flags durch das bisherige Drop-Paket auf 0 stehen. Aus hebt Missions-/Schwierigkeitssperren fuer automatische Drops auf; der bestehende Gesundheitszaehler bleibt statt garantierter Drops aktiv. Individuelle DontDropWeapons-Ausnahmen, explizite ForceDrop-Flags, vorhandene Gegenstaende und WCR-Loadout-/Munitionswerte bleiben erhalten. Keine Nachlieferung fuer bereits tote Gegner. AA/SH behalten ihre bestehenden Dropregeln.

Menue: dreistufiger Slider mit benanntem aktuellem Wert und Checkbox BT drop restrictions. Rechte Effektzeilen kompakter angeordnet; FHD-Sichtkontrolle ohne Ueberlappungen. Beide Einstellungen archiviert und in der gemeinsamen Praeferenzliste; Defaults setzt reduziert/freigegebene Drops.

Native Pruefung:
- AA modes-aa, SH modes-sh, BT modes-bt: jeweils aus/reduziert/original/aus, 78/77/77 Samples. Aus exakt null, reduziert innerhalb Rundungsgenauigkeit 0.2 mal Quelle, original exakt Quelle. Rote Alphaeinblendung bleibt erhalten. Keine Script-/Event-/Kommando-Fehler.
- BT live-r1: e2l2-Referenzsave, vier echte Testactor-Tode mit Grenzen an/aus/an/aus in derselben Sitzung. An keine Drops; aus je eine Kar98 und Gesundheitsbox, Drop() bestaetigt. Fuer deterministische Gesundheitsdrops waren die Testschwellen auf 1 gesetzt. Save/Load zwischen Phasen erfolgreich. Test nutzt gespeicherte Referenzschwierigkeit; Hard-Sonderregel separat im Code geprueft, nicht als native Hard-Abnahme behauptet.
- flinch-drops-r2: Kontextkette AA -> SH -> BT -> AA und frische Prozesse aller Kampagnen erhalten beide Optionen und bestehende Praeferenzen.
- game und Engine erfolgreich gebaut. Ausschliesslich isolierte Testprofile; persoenliche Abnahme und Merge nicht behauptet.

Installiert als flinch-drops-r2 aus fc992325; alle 78 Laufzeitdateien hashgeprueft. 382 persoenliche Profildateien, 9072 Originaldateien, 9000 Basisdateien und acht MP-Eingaben unveraendert. Ruecksicherung des unmittelbar vorherigen stabilen Standes: generated-local/widescreen/backups/flinch-drops-r2.
