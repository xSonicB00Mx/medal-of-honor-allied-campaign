# CP00-r4: Drop-Ausgangsreferenzen, 14.10.2026

**Vier kontrollierte Serien mit insgesamt 36 gültigen Kills abgeschlossen.** Die unveränderte WCR-Basis liefert in den ausgewählten AA-/SH-Kontexten Waffen und Gesundheitsgegenstände; BT e2l2 unterdrückt beides missionsseitig. Auf AA „Schwer“ bleiben Waffen erhalten, Gesundheitsdrops entfallen. Der zusätzliche BT-Drop-Patch bleibt **nur inventarisiert, nicht integriert**. Keine Engine-/Inhaltsänderung, kein BT-Finaltest, kein CP0a oder Merge.

Engine `af7bb7c6e706fcc64e5933a22457333274f3de22`, EXE-SHA-256 `5f1eee385de3b26750b45b7aa1e98566801b716566b97af11fa5586cb5c21c91`, WCR-Fingerprint `3b6b38b5b04ba320a526196946c44394c4519e4197dc8d3d05788e186501cfcc`. 1280×960, FOV 90, getrennte Profile. Ursprüngliche Runtime, Nutzerprofile und Quellspielstände bleiben unverändert.

## Verfahren und Ergebnisse

Pro Serie sechs zusätzliche Gegner mit Kar98, danach drei mit MP40. Normale Colt45-Spielereingaben töten die Ziele; anschließend wird nachweislich erneut auf die Leichen geschossen. Die lebende Ziel-KI ist für reproduzierbares Zielen aus, ab dem Tod wieder an. Nur Spielermunition wird für die Diagnose aufgefüllt. Dropflags, Drop-Zähler und Gegner-Drop-Overrides werden nicht gesetzt. Eigene Testleichen werden nach jeder Messung entfernt, um die folgende Zielposition freizuhalten; fallengelassene Gegenstände bleiben dem normalen Lebenszyklus überlassen.

Der Vergleich erfasst neu entstandene **besitzerlose** Entitäten per ID und Modell. Noch vom Gegner oder Spieler getragene Waffen zählen nicht als Drops. Native Kill-/Treffer-/Zielzähler und tatsächliche Schusszunahme sichern die beiden Testphasen ab. Nach dem fünften Gegner erfolgt Save/Load innerhalb desselben Prozesses; die Reihe wird danach fortgesetzt.

| Kontext | Kills | Waffen-Drops | Gesundheitsdrops | neue Gegenstände durch Leichenbeschuss |
|---|---:|---:|---:|---:|
| AA Mittel | 9 | 9 | 2 | 0 |
| SH Mittel | 9 | 9 | 2 | 0 |
| BT e2l2 Mittel | 9 | 0 | 0 | 0 |
| AA Schwer | 9 | 9 | 0 | 0 |

In beiden mittleren AA-/SH-Serien erscheinen die Gesundheitsgegenstände nach Ziel 6 und Ziel 9. Das entspricht dem beobachteten Startzustand und der Engine-Logik: Gewehrgegner zählen einen Punkt, andere Waffengruppen standardmäßig zwei; Schwelle sechs, sofern Schwierigkeit und Missionsflags Gesundheitsdrops zulassen. Die tatsächlich geprüften Gegnerwaffen sind `models/weapons/kar98.tik` und `models/weapons/mp40.tik`. Auf Schwer unterdrückt der Skill-Zweig die automatische Gesundheitsausgabe. Kein zusätzlicher Treffer, Kill oder Zielabschluss durch die spätere Leichenphase in allen 36 gültigen Fällen.

AA startet in m2l1, SH lädt eine unabhängige Kopie des bereits vorhandenen t1l2-Flakspielstands, BT lädt den zuvor geprüften e2l2-Fußsave. Die aktive BT-Datei `global/loadout.scr` aus `Restoration_BT_Pak1-Main.pk3` setzt für e2l2 sowohl `nodrophealth=1` als auch `nodropweapons=1`. Das ist **keine allgemeine Aussage über alle BT-Missionen**. Der ergänzende [Ressourcenkatalog](CP00-r4-drop-policy-catalog.json) enthält Hashes und ausgewählte statische Zuweisungen; Textanalyse allein gilt nicht als Nachweis der Ausführung aller Zweige.

JSON-Nachweise: `r4-drops-v1-AA/SH/BT.json` und `r4-drops-hard-v2-AA.json`. Alle vier Spielprozesse endeten regulär; keine Script-Error-/Unknown-command-Meldungen in den gültigen Reihen. Dreifache Bildreferenz je Serie nach Ziel 1, 6 und 9. Auf der AA-Schneefläche sind Teile der Körper/Gegenstände verdeckt; die exakte Dropidentität wird dort durch Entitätsdaten belegt, nicht durch eine behauptete vollständige Sichtprüfung jedes Items. SH-/BT-Bilder zeigen die jeweiligen Leichenzustände; Einzelgegenstände sind in SH teilweise dunkel.

## Aufnahme nach erneutem Prozessstart

`r4-drop-pickup-SH.json` lädt den Endsave der SH-Serie in einem weiteren unabhängigen Profil. Normales Vorwärtslaufen zum letzten Gesundheitsdrop entfernt dessen Entität und erhöht die internen Gesundheitswerte **686→750**; die sichtbare HUD-Anzeige steigt **91→100**. Meldung „Recovered 25 Health“ sichtbar. Es wurden weder Spielergesundheit gesetzt noch Pickup-Callbacks direkt aufgerufen. Somit sind Erzeugung, Erhalt über Save/Load und tatsächliche Aufnahme dieses Gesundheitsdrops nachgewiesen.

Auf demselben Weg meldet das Spiel zweimal „Got 64 Smg Rounds“ beim Einsammeln dort liegender Waffen. Das belegt die sichtbare Munitionsaufnahme, jedoch wurde der Munitionsbestand nicht separat vor/nachher abgefragt; kein exakt gemessener Inventarzuwachs von 128 behauptet.

## Verworfener Schwierigkeitsaufbau und Auswertung

`r4-drops-hard-AA.json` ist **ungültig als Schwer-Test**: Der frühe Kommandozeilenwert wurde bei Serverinitialisierung durch `SV_MediumMode_f` überschrieben. Tatsächlich lief Skill 1; der eigene Prozess wurde bei Entdeckung gestoppt. Die Daten bleiben als unvollständiger Methodenversuch erhalten und zählen nicht zu den 36 gültigen Kills.

Der korrigierte Ablauf führt den regulären Befehl `difficultyHard` nach Initialisierung und vor dem Kartenstart aus. Ein Skript prüft vor jedem Testgegner den aktiven Skill, die Auswertung prüft ihn zusätzlich vor/nach Save/Load und am Ende. Eine weitere Auswertekorrektur behandelt die gleichwertigen Logwerte `2` und `2.000000` numerisch: Die Spielreihe war vollständig und fehlerfrei, nur der erste Python-Stringvergleich schlug fehl. Die gespeicherten Daten wurden anschließend mit dem korrigierten Prüfer vollständig validiert; kein unnötiger erneuter Spieldurchlauf.

Reproduzierbarer reiner Nachprüfaufruf: `python tools/test_cp00_drop_series.py AA --run-id r4-drops-hard-v2 --skill 2 --verify-only`. Entsprechend `--run-id r4-drops-v1` für AA/SH/BT auf Mittel. Ungeprüfte Schwierigkeitsänderungen beim Laden der SH-/BT-Saves werden vor Profilanlage abgewiesen. Die Aufnahmeprobe verweigert ebenfalls vorhandene Zielprofile und prüft die Savequellen gegen die Serienhashes.

## Grenzen und nächster CP0-Schritt

Dies sind kontrollierte Serien eines Gegnergrundmodells. Sie ersetzen keine vollständigen natürlichen WCR-Spawnerabläufe, keine Drop-Abnahme jeder BT-Mission, keine Prüfung aller Schwierigkeitsgrade und keine Integration des zusätzlichen Patches. Die Aussagen über automatische Gesundheitsdrops gelten für den aufgeführten normalen Enginepfad; vorhandene Force-/No-drop-Ausnahmen wurden nicht umgeschrieben. Das natürliche Verschwinden der Testleichen wird durch ihre gezielte Entfernung in diesen Reihen ausdrücklich nicht geprüft; dafür gelten die gesonderten Leichenreferenzen.

Die ausgewählten Drop-Ausgangsreferenzen sind vorhanden. Als nächste technische CP0-Arbeit folgen Wandtreffer und bereits platzierte menschliche 3D-Leichen; außerdem bleiben weitere natürliche Übergänge, Live-Kampfframetimes und offene Menü-/Warnungsprüfungen. **Keine vollständige CP0-Abnahme.** Paket-CRC/SHA und erneut geprüfte Referenzen werden in `CP00-r4-drops-package.json` festgehalten. Keine Assets oder Saves werden nach GitHub hochgeladen.
