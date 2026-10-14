# CP00-r4: BT-Kampfreferenz zu Fuß, 14.10.2026

**Gültige kontrollierte BT-Referenz für Colt45, MP40, Kar98 und BAR.** Nach Nutzerkorrektur wurde der Fahrzeugstart ersetzt durch den normalen e2l2-Flugplatzeinstieg nach seiner Besprechung. Keine Engine-/WCR-Inhaltsänderung, keine Missionsfreischaltung, kein CP0a. Das abgewählte BT-Finale wurde nicht getestet.

Engine `af7bb7c6e706fcc64e5933a22457333274f3de22`, EXE-SHA-256 `5f1eee385de3b26750b45b7aa1e98566801b716566b97af11fa5586cb5c21c91`, WCR-Fingerprint `3b6b38b5b04ba320a526196946c44394c4519e4197dc8d3d05788e186501cfcc`. 1280×960, FOV 90, Skill 1, getrennte lokale Profile, Diagnosemodus für Messskripte. Der Start erfolgte in einem neuen Profil; vorhandene Nutzerprofile blieben unberührt.

## Voraussetzungen tatsächlich geprüft

`r4-bt-foot-e2l2.json`: reguläres Briefing abgewartet, `BriefOver=1`, kein Fahrzeug/keine Turretbindung, Carcano sichtbar. Normale Seitwärtsbewegung änderte die Position von `(6296, -5600, 2470)` auf `(6140.761, -5600.980, 2505.142)`. Ein normaler Angriff erhöhte den Schusszähler 0→1 und senkte die sichtbare Magazinmunition 6→5. Drei Bilder geprüft. Kein Teleport, keine erzwungene Physikfreigabe, kein künstlicher Abschluss. Save `cp00_foot_ready` mit vollständigem SAV/SSV/TGA-Satz erstellt und in getrennten Folgeprofilen erfolgreich geladen.

Der Kampfaufruf verlangt jetzt für BT diesen visuell geprüften Vorprüfbericht plus exakt hashgleiche Save-Dateien; er übernimmt daraus auch den Kartennamen. Ohne Vorprüfung bricht das Werkzeug vor Profilanlage und Spielstart ab (Negativprobe bestanden). Eine bloße aktive Waffenreferenz genügt nicht.

## Ergebnisse

Ein eigener WCR-Soldat wurde zusätzlich platziert; seine KI bleibt nur während des lebenden Zielzustands für reproduzierbares Zielen aus und wird beim echten Tod wieder eingeschaltet. Spielerangriffe bleiben normale Eingaben. Wie bei AA/SH ist dies ein kontrollierter Referenzaufbau, keine natürliche Missionsabnahme.

| Waffe | Schüsse nach Tötung → nach Leichenbeschuss | Treffer | Kills | abgeschlossene Ziele |
|---|---:|---:|---:|---:|
| Colt45 | 8 → 11 | 3 → 3 | 1 → 1 | 0 → 0 |
| MP40 | 10 → 14 | 4 → 4 | 1 → 1 | 0 → 0 |
| Kar98 | 4 → 6 | 2 → 2 | 1 → 1 | 0 → 0 |
| BAR | 8 → 11 | 2 → 2 | 1 → 1 | 0 → 0 |

Die Schusszahlen enthalten den einen vorangegangenen Carcano-Probeschuss im Referenzsave. Unterschiedliche Feuerraten ergeben unterschiedliche Schusszahlen trotz gleicher Eingabeimpulse. In allen vier Läufen: Gesundheit des Ziels 100→0, beobachtete Todesereignisse 0→1→1→1, keine zusätzlichen Treffer/Kills/Ziele durch die späteren Schüsse. Leichen auf den Bildern sichtbar; Kar98 liefert Rückenlage, die anderen Läufe eine eingerollte seitliche/vordere Lage. Die Colt45-Leiche bleibt auch nach weiteren 20 Sekunden sichtbar; die Matrixläufe warten zusätzlich 3 Sekunden.

Metadaten: `r4-foot-combat-v2-BT.json`, `r4-foot-matrix-mp40-BT.json`, `r4-foot-matrix-kar98-BT.json`, `r4-foot-matrix-bar-v2-BT.json`. Der erste BAR-Lauf `r4-foot-matrix-bar-BT.json` bleibt zusätzlich erhalten. Kein Script-Error in diesen gültigen Kampfproben. Die effektive Herkunft von KI-/Todesskript, Gegner und jeweiliger Testwaffe wird im Log per `which` festgehalten.

**Dropgrenze:** e2l2 setzt bereits im gelieferten Kartenskript `level.nodropweapons=1`. Der Kar98-Eintrag des lebenden Testgegners ist nach seinem Tod nicht mehr in der Umgebungsliste. Kein zusätzlicher Gesundheits-/Munitionsdrop durch die späteren Schüsse beobachtet. Daraus folgt keine allgemeine BT-Dropquote oder Prüfung der gewünschten CP0a-Dropänderung. Missionseigene Sperren wurden nicht geändert; systematische Serien und andere Missionskontexte bleiben offen.

## Methodenfehler erhalten und behoben

- `r4-foot-combat-v1-BT` ist ungültig: Ein bodennaher horizontaler Volumentrace wurde am Hang in allen Richtungen blockiert (`CP00_PLACEMENT=0`), deshalb entstand kein Gegner. Nachfolgende fehlende-Entität-Fehler stammen vom Diagnoseaufbau. Die neue Prüfung sucht oberhalb des Hangs und senkt anschließend die ganze Kollisionsbox auf den Boden ab.
- Die eigentlichen Schussbefehle liegen nun in einer getrennten Fortsetzungsdatei. Das Hilfsskript gibt sie erst nach erfolgreicher Platzierung und lebendem Ziel frei; sonst endet die Probe ohne Schusssequenz.
- Der frühere optionale Befehl `+reload` war unbekannt; die korrekte normale Belegung lautet `reload`. Tatsächlich abgegebene zusätzliche Schüsse der früheren Läufe sind durch Zähler und sichtbare Munition belegt, aber jene Läufe sind **kein manueller Nachladetest**. Der wiederholte BAR-Lauf mit korrektem Befehl hat keine Unknown-command-Meldung. Unbekannte Befehle werden jetzt gesondert erfasst und verlangen Prüfung.
- Die endgültige Auswertung verlangt zusätzlich echte Schuss-/Killzunahme in der lebenden Phase und weitere Schüsse ohne zusätzliche Treffer/Kills/Ziele in der Leichenphase. Früher verworfene Fahrzeugstarts bleiben ungültige Methodenversuche; sie sind kein belegter BT-Kampffehler.

## Sicherung und Restumfang

Lokale Bilder, Logs, Konfigurationen und Saves werden als eigenes Beweispaket gesichert; nur eigene Werkzeuge und Metadaten gehen nach GitHub. Einzelheiten der Archivprüfung stehen in `CP00-r4-bt-foot-package.json`. Alte Pakete werden nicht umgeschrieben. Geprüfte Savequellen und Beweisdateien werden vor Sicherung erneut gehasht.

Die zuvor fehlende BT-Kampfreferenz ist damit für diese vier Waffen und diesen kontrollierten Kontext vorhanden. Offen bleiben systematische Drops, weitere Modelle/statische Leichen/Posen/Wandfälle, natürliche Übergänge, Live-Kampfframetimes und weitere Menü-/Warnungsprüfungen. **Keine vollständige CP0-Abnahme, kein Merge, kein CP0a.**
