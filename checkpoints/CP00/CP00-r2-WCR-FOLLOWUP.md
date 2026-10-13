# CP00-r2 – WCR-Nachprüfung nach bestätigter Speicherkorrektur

13.10.2026. CP0 bleibt offen. Engine `3eec4afb22093421b8776d2df92b87ec2fb4119e`, unveränderte CP00-r2-Binärdateien und WCR-Pakete. Kein neuer Kandidat, kein Merge, kein CP0a. Nutzerbestätigung „hat geklappt. fahre fort“ gilt für die zuvor übergebenen Save-/Vorschaubild-/FOV-Korrekturen.

## Zusätzlich ausgeführt

- **AA m2l1:** unveränderte WCR-Karte in frischem Profil gestartet, aktive Schneeszene mit Springfield und HUD gerendert, vollständigen Save erzeugt, normal beendet. `mg42-start-AA.json` enthält Dateihashes. Kein durchgespielter Level.
- **MG42-Komponententest:** eigene zusätzliche Testwaffe verwendet den effektiv geladenen `models/statweapons/mg42_gun.tik` aus `main/pak7.pk3`. Der normale Engine-Ereignishandler `doUse` wird mit dem Spieler als Benutzer aufgerufen. `setthread` führt unseren eigenen Callback beim ersten Besteigen einmal aus, beim Aussteigen nicht erneut, beim zweiten Besteigen ein zweites Mal. Ergebnis **1 / 1 / 2**, bestanden. Nur die Testwaffe erhält einen eigenen Callback; keine WCR-Missionsflags werden gesetzt. `sv_cheats=1` wird ausschließlich für den Einstieg in das Diagnose-Skript verwendet. Das ersetzt weder die räumliche Benutzen-Abfrage der Taste noch den natürlichen Missionsfortschritt.
- **BT e3l4:** aktive Startszene gerendert, vollständigen Save erzeugt, normal beendet. `which` bestätigt Hauptskript, Tower, Escape und Outro aus `Restoration_BT_Pak1-Main.pk3`. `finale-start-BT.json` enthält Hashes und Laufzeitquellen. Die Flucht wurde nicht durchgespielt.
- **Originalengine-Vergleich versucht:** 9007 Dateien aus dem verifizierten Eingangssnapshot unabhängig in `runtime-local/CP00-original-reference` kopiert und einzeln gehasht. Kein Link und keine Veränderung der Originalinstallation. Die BT-Originalengine beendet sich vor Spielfenster/Spielprotokoll; nach einem ersten unmittelbar beendeten Versuch ergibt der kontrollierte Wiederholungsversuch Exit `0xC0000005`. Damit liegt **kein erfolgreicher Originalengine-Vergleich** vor. Keine System-/Kompatibilitätseinstellungen geändert.

Der erste MG42-Testversuch verwendete irrtümlich `use` anstelle des in `entity.cpp` definierten Ereignisnamens `doUse`. Er scheiterte am Testskript, nicht an einem nachgewiesenen MG42-Enginefehler. `turret-callback-AA.json` und dessen Profil bleiben als fehlgeschlagener Versuch erhalten. Maßgeblicher korrigierter Lauf: `turret-callback-AA-v2.json`. Nachträglich ergänzte Quell-/Hashfelder stammen aus unverändertem Manifest und vorhandenen Logs; keine zusätzlichen Spieltestläufe behauptet.

## Lokale Skriptkette und offene Befunde

| Fall | Beleg | Konsequenz |
|---|---|---|
| AA m1l1 MG42 | `maps/m1l1.scr`: nach totem MG-Schützen und geöffnetem Türabschnitt bindet die Karte `blowthedoor2` an die MG42. Dieser Callback setzt den regulären Fortschrittszustand. | Volltest muss diese Voraussetzungen natürlich erreichen, MG benutzen und anschließende Verstärkungs-/Endsequenz prüfen. Komponententest allein reicht nicht. |
| AA m2l1 MG42 | `maps/m2l1.scr`: `s7_test` ist der MG-Callback und stößt zeitlich begrenzte zusätzliche Spawns an. | Natürliches Besteigen/Schießen und Übergang nach m2l2a bleiben offen. |
| MG42-Enginekorrektur | Upstream-Commit `44ce0595c2bbe1c3d5933e16e9130c2d7cf1306d` ist Vorfahr der gebauten Engine; er korrigiert die `setthread`-Zuordnung auf `P_EventSetThread`. | Quellenbeleg plus bestandener Laufzeit-Komponententest; keine erneute identische Korrektur nötig. |
| SH t1l2 Flak | WCR fordert `explosionoffset` 128 bzw. 300 an. In `Entities.cpp` existieren Ereignis, Setter und archiviertes Feld, aber die Response-Tabelle bindet den Setter nicht; `DoExplosion` verwendet das Feld nicht. | Konkrete Implementierungslücke. Nur die Warnung durch Registrierung zu entfernen wäre unvollständig. Beabsichtigte Effekt-/Schadensposition und Sprengfolge vor einer Korrektur abgleichen. |
| BT e3l4 Spawn-/Pfadfehler | Laufzeit: fünfmal ungültiges `waittill trigger` für AISpawnPoint, einmal für PathNode, unerlaubtes Löschen eines PathNode; außerdem ungültiges `waittill spawn` in weather.scr. | Nicht als harmlos gewertet. Gegner-/Triggerabläufe und Ursache offen; ohne erfolgreichen Originalvergleich keine pauschale Zuordnung zu WCR oder unserer Engine. |
| BT e3l4 weitere Warnungen | Nicht vorhandene `aipronechance`/`aicrouchchance`-Ereignisse, fehlendes Spline-Ziel `t449`, Ressourcen-/Fahrzeugtonwarnungen. | Im lokalen Log erhalten; sichtbarer Kartenstart ist keine vollständige Kompatibilitätsabnahme. |
| BT erweiterte Flucht | `e3l4.scr` wartet nach Luftangriffsbestätigung auf `ObjectiveEscapeCastle`. Escape aktiviert nacheinander fünf Trigger, setzt den Erfolgszustand erst nach dem letzten; der Timer führt bei Scheitern zu Tod/Missionsfehler. Danach folgen Cleanup und Outro bis Credits. | Restaurierter Ablauf lokal belegt. Weder Radiobestätigung noch vorzeitiger Trigger darf später als Kampagnenabschluss behandelt werden. Natürlicher Erfolg und Scheitern noch zu testen. |

Ressourcenhashes und Zeilenhinweise: `wcr-followup-audit.json`. Die vollständigen Dritt-Skripte, Renderbilder und Logs bleiben ausschließlich in ignorierten lokalen Ordnern. Benutzerprofile `AA`, `SH`, `BT` wurden in dieser Runde nicht bearbeitet; die neuen Testprofile heißen `mg42-start-AA`, `finale-start-BT` und `turret-callback-AA[-v2]`.

## Reproduktion und nächster Schritt

`tools/probe_cp00_map.py AA m2l1 --run-id <neuer-name> --seconds 15` bzw. `BT e3l4 --seconds 30`; `tools/test_cp00_turret.py --run-id <neuer-name>`. Die Werkzeuge verweigern vorhandene Profile. Sie starten ausschließlich CP00-r2; Kartenstart, Komponententest und vollständige Mission sind getrennte Ergebnisse.

Weiter ausschließlich CP0: SH-Explosionsversatz und BT-Triggerfehler eingrenzen/korrigieren, danach natürliche MG42-/Finalabläufe sowie übrige Kampf-/Übergangs-/Performancefälle prüfen. Keine neue Spieltestaufforderung für die bereits bestätigte Speicherkorrektur. Startwege für den weiterhin einzigen Nutzerkandidaten bleiben `Start-CP00-r2-AA.cmd`, `Start-CP00-r2-SH.cmd`, `Start-CP00-r2-BT.cmd`; Details und Rückkehr zur unveränderten Originalinstallation im r2-Bericht.
