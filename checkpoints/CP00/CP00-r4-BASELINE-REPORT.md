# CP00-r4: technische Ausgangsreferenzen vom 14.10.2026

**Teilprüfung, keine vollständige CP0-Abnahme.** Engine und WCR-Inhalte sind unverändert. BT-Finale bleibt gemäß Nutzerentscheidung ausgelassen; CP0a und Merge bleiben außerhalb dieser Arbeit.

Engine `af7bb7c6e706fcc64e5933a22457333274f3de22`, EXE-SHA-256 `5f1eee385de3b26750b45b7aa1e98566801b716566b97af11fa5586cb5c21c91`, WCR-Fingerprint `3b6b38b5b04ba320a526196946c44394c4519e4197dc8d3d05788e186501cfcc`. Ausschließlich getrennte Diagnoseprofile. Eigene Werkzeuge und Metadaten in Git; Logs, Bilder, Demos und Saves ausschließlich lokal.

## Optionspersistenz

`r4-options-v2-AA/SH/BT.json`: jeweils **9/9 bestanden**, insgesamt 27 Prüfungen. Getestet: Effekt-/Musiklautstärke, Mausempfindlichkeit, vertikale Mausachse, Untertitel, Fadenkreuz, Schatten, Texturdetail und Gamma. Werte wurden geändert, nach vollständigem Prozessneustart gelesen, zurückgestellt und nach einem weiteren Neustart erneut gelesen. Originale Nutzerkonfigurationen wurden nur kopiert und blieben bytegleich. Dies prüft archivierte Cvars, nicht sämtliche Menübedienelemente oder die wahrgenommene Audio-/Mauswirkung. Der bereits bestätigte FOV-Test bleibt ein separater Befund.

Erster AA-Versuch `r4-options-AA` ist ein verworfener Methodenversuch: `set` und `quit` im selben Befehlsbuffer ließen keinen nachfolgenden Frame für das automatische Schreiben der Konfiguration zu. Die korrigierte Methode wartet 1200 ms; keine Enginekorrektur war erforderlich.

## Frametimes als Client-Replay-Referenz

Je Spiel eine 30-Sekunden-Aufzeichnung, zweimal in einem frischen Prozess abgespielt: AA m2l1, SH t1l2, BT e1l2. 1280×960, FOV 90, GL1, Skill 1, lokale RTX 4090. Szenenbilder der Aufzeichnung geprüft: Schneestraße, SH-Einstieg mit Soldaten, BT-Fahrsequenz.

| Spiel/Lauf | Dauerwerte | Mittel ms | p95 ms | p99 ms | Maximum ms |
|---|---:|---:|---:|---:|---:|
| AA replay1 | 598 | 8.477 | 9 | 10 | 17 |
| AA replay2 | 598 | 8.475 | 9 | 10 | 17 |
| SH replay1 | 598 | 8.470 | 9 | 10 | 18 |
| SH replay2 | 598 | 8.477 | 9 | 10 | 17 |
| BT measured1 | 598 | 8.487 | 9 | 10 | 18 |
| BT measured2 | 598 | 8.502 | 9 | 10 | 24 |

Der Enginebericht zählt 599 Frames, die Dauerdatei enthält 598 Werte; kein Wert erreicht die enginebedingte Begrenzung von 255 ms. Messauflösung 1 ms. **Dies sind Client-Timedemos, keine Live-Kampf-, KI- oder Bildausgabe-Latenzmessungen.** Der Replay-Simulationsschritt beträgt 50 ms, die normale Aufzeichnung lief mit 60-fps-Limit. Der Timedemo-Mittelwert von etwa 118 fps ist kein Versprechen für den Kampagnenbetrieb. Keine Ursache für eine mögliche externe Begrenzung behauptet.

Verworfene Anläufe: Ein AA-Logmatcher erwartete zunächst eine bei `developer=0` fehlende Debugzeile; die intakte Aufnahme wurde wiederverwendet. BT verweigerte zunächst die geschützte Timedemo-Cvar. Erst Replays mit der tatsächlichen Diagnose-Cvar `cheats=1` erzeugten gültige Dauermessungen; die vorherigen Echtzeit-Replays werden nicht als Messung gewertet.

## Kontrollierte Kampf- und Leichenreferenzen

Eigener zusätzlich gespawnter WCR-Soldat mit Kar98, normale Waffen und Spielereingaben. Seine KI ist für reproduzierbares Zielen zunächst aus und wird beim echten Todesereignis wieder aktiviert, damit Animation und Leichenverarbeitung regulär ablaufen. Kein natürliches Missionsgefecht und keine Missionsabnahme. Diagnosemodus und Hilfsskript begrenzen die Übertragbarkeit auf den normalen Spielbetrieb.

- **AA Colt45 (`r4-baseline-v4-AA`)**: lebend 100 HP, nach Beschuss 0 HP; Todeszähler 0→1→1→1. Liegende Leiche bleibt nach zusätzlichem Beschuss und 20 Sekunden sichtbar. Kar98 nach dem Tod vorhanden, nach zusätzlichem Beschuss weiter vorhanden, nach der Wartezeit nicht mehr in der Umgebungsliste. Bei diesem einzelnen Tod kein Gesundheitsdrop beobachtet; daraus folgt keine allgemeine Dropquote.
- **SH Colt45 (`r4-baseline-v5-SH`)**: gleicher Todeszählerverlauf, Leiche in Bauchlage nach 20 Sekunden sichtbar. Grundlage ist eine unabhängige Kopie des bestehenden t1l2-Saves nach dem Flaktest; alle drei Originaldateihashes nach Abschluss erneut bestätigt. Kein weiterer natürlicher Missionsfortschritt behauptet.
- In beiden gültigen Pistolentests blockieren die zwei Diagnose-Strahlen den lebenden Gegner, passieren nach dem Tod die Leichenposition. Die protokollierte obere Kollisionsgrenze fällt von 94 bis auf 8 Einheiten. Dies beschreibt die vorhandene Basis, keine neue Leichentrefferfunktion.

Zusätzliche AA-Waffenläufe protokollieren die echten Spielerstatistiken. Die Zahlen sind tatsächlich abgegebene Schüsse, nicht die Anzahl der Eingabeimpulse:

| Waffe | Schüsse nach Tötung → nach Leichenbeschuss | Treffer vorher → nachher | Kills vorher → nachher | abgeschlossene Ziele |
|---|---:|---:|---:|---:|
| MP40 | 9 → 13 | 4 → 4 | 1 → 1 | 0 → 0 |
| Kar98 | 3 → 5 | 2 → 2 | 1 → 1 | 0 → 0 |
| BAR | 7 → 10 | 2 → 2 | 1 → 1 | 0 → 0 |

Diese drei Läufe warten abschließend 3 Sekunden. Keine erneute Tötung, kein zusätzlicher Trefferzähler und kein abgeschlossenes Ziel durch die weiteren Schüsse beobachtet. **MP40-/Kar98-Leichen sind auf den Bildern stark von der Schneefläche verdeckt**; daher keine gültige vollständige Posenreferenz. BAR-Leiche sichtbar. Kein Nachweis aller Waffen, Posen, Wände, statischen Leichen oder Dropvarianten.

## BT: Referenz weiter offen

**Korrektur nach Nutzerhinweis:** Die gewählten BT-Einstiege beginnen im fahrenden Fahrzeug ohne verfügbare Spielerwaffe. Der Kampfaufbau wurde zu früh gestartet; damit fehlte bereits die Voraussetzung für einen kontrollierten Schusstest. Das ist ein Fehler bei der Testauswahl, kein nachgewiesener Waffen- oder Kampffehler von BT. Die Versuche auf e1l3/e2l3 liefern folglich keinen gültigen lebend→tot-Vergleich: Das Testziel war bereits vor den vorgesehenen Spielerschüssen tot; die neueren Statistikproben zählen null Schüsse. Änderungen an Zielplatzierung und Gegnerpriorität konnten die fehlende Spielerkontrolle nicht beheben und waren dafür ungeeignet. Begleitende Start-/Spawn-/Array-/NULL-Skriptfehler sind dokumentiert, aber ohne gleichwertigen Vergleich zur Originalengine weder als neue Regression noch als unbedenklich eingeordnet.

Die anschließende e1l2-Beobachtung (`r4-bt-foot-entry.json`) protokolliert den regulären Erhalt des Minendetektors und eine aktive Thompson. Das Skript forderte danach Bild/Save an; es entstanden weder diese Referenzdateien noch die Abschlussmarkierung. Prozessende mit Code 1, Ursache nicht geklärt. Zusätzliche Array-/Typfehler stehen im Log. Der JSON-Wert `timed_out` beschreibt nur die in-game Timeoutmarkierung, nicht die Ursache des Prozessendes. **Kein bestandener Kampfreferenztest.** Der nächste BT-Ansatz benötigt einen verlässlich bedienbaren Fußabschnitt und einen überprüften Speicherpunkt. Vor dem Spawnen eines Testgegners sind Fahrzeug-/Introende, freie Bewegung, sichtbare aktive Waffe und ein tatsächlich abgegebener Probeschuss zu prüfen. Bei fehlender Voraussetzung den Aufbau abbrechen, statt weitere Kampfresultate zu sammeln. Eine aktive Waffenreferenz allein reicht nicht. Keine Erfolgsflags oder künstlichen Missionssprünge verwenden.

## Verworfenes und statischer Katalog

Frühere AA-Aufbauten: erster Versuch mit Vektorsyntaxfehler; v2 mit falschen Bounds-Gettern und unzulässigem Console-Datei/Label-Aufruf; v3 mit nach dem Tod deaktivierter KI und eingefrorener stehender Animation. SH v4 hatte einen ungeeigneten Introstart und Fehler bei Entitäten ohne Modell. Alle Metadaten bleiben mit ausdrücklicher INVALID-Bewertung erhalten. Erfolgreiches Prozessende allein bedeutet keinen bestandenen Referenztest.

`CP00-r4-combat-resource-catalog.json` enthält ausgewählte Waffen-/Leichen-/KI-Ressourcen mit vorhergesagtem Paketlieferanten und Hash: 14/24/38 Waffen für AA/SH/BT, jeweils 30 ausgewählte menschliche Leichenmodelle und zwei Skripte. Statischer, bewusst unvollständiger Katalog; keine pauschale Laufzeitabnahme aller Einträge. Die verwendeten vier Waffen, der Soldat sowie KI-/Todesskripte wurden zusätzlich über `which` in den jeweiligen Referenzlogs zugeordnet.

Quellbefunde: `Sentient::DropInventoryItems` berücksichtigt Schwierigkeit, Missionssperren und Zähler/Overrides; `Actor::BecomeCorpse` setzt die Leiche auf nicht solide und startet die spätere Entfernung; `DeathEmbalm` senkt die Kollisionshöhe. `Entity::DeathSink` entfernt im Einzelspieler erst bei getrennten Sichtbereichen. Diese Codebefunde erklären mögliche Beobachtungen, ersetzen aber keine noch ausstehenden Dropserien oder Missionsprüfungen. Der lokale BT-Drop-Patch bleibt **nur inventarisiert, nicht integriert**.

## Sicherung und Restumfang

396 referenzierte lokale Dateien einschließlich kopierter Savequellen wurden nach den Versuchen erneut per SHA-256 geprüft, ohne Abweichung. Lokales Beweispaket und Git-Sicherung werden getrennt geführt. Die vollständigen Eingaben und Runtime wurden in dieser Teilrunde nicht neu inventarisiert; deren vorhandene r4-Integritätsprüfung bleibt ein früherer Nachweis.

Offen bleiben weitere natürliche Übergänge, eine gültige BT-Kampfreferenz, systematische Dropserien, zusätzliche Waffen-/Posen-/statische Leichen-/Wandfälle, Live-Kampfframetimes, Menübedienung jenseits der bereits geprüften Save/FOV-Wege sowie die Ursachen der Skriptwarnungen. SH-Flak und AA-MG42 bleiben nutzerbestätigt. BT-Finale bleibt ausdrücklich ausgelassen. **Keine vollständige CP0-Freigabe, kein Merge, kein Beginn von CP0a.**
