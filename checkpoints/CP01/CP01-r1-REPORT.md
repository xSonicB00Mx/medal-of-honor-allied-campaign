# CP01-r1 – HUD- und Menüskalierung

Stand: 14.10.2026. **Implementiert und als lokaler Spielkandidat bereitgestellt. Die vollständige Abnahmematrix des Plans ist noch nicht abgeschlossen.** Der autonome Auftrag wurde bis zur CP1-Implementierung ausgeführt; keine Zwischenfreigabe, persönliche Spielabnahme oder Übernahme nach main unterstellt. CP2 wurde nicht begonnen.

## Eindeutiger Kandidat

- Quell-/Engine-Commit: `cc88cacc6b922c28bbd718916c3f3e5bbb49b86a`. Buildkennung im Spielprotokoll: `0.83.0-unstable+0.cc88cacc`.
- Runtime: `runtime-local/CP01-r1`. Start: `Start-CP01-r1-AA.cmd`, `Start-CP01-r1-SH.cmd`, `Start-CP01-r1-BT.cmd` im Workspace.
- Eigene Benutzerprofile: `profiles-local/CP01-r1/user`. Diagnoseprofile sind davon getrennt. Keine alten Saves automatisch migriert.
- Privater Entwurfs-PR #3, gestapelt auf CP00a-PR #2 und CP0-PR #1. Kein Merge.
- Lokales Paket: `artifacts-local/CP01-r1-local-runtime.zip`, SHA-256 `72d8e06a2477377fc4dbe8b84ac59043334a34a8ab93999d8eac70bf5f1d3de2`, 2.814.448.166 Bytes, ZIP-CRC geprüft. Enthält Originaldaten: **nicht hochladen**.
- Alle Binär-/Paketprüfsummen und Buildoptionen: `build-manifest.json`. Originaleingaben 9072/9072 unverändert, Runtime-Basis 9000/9000 unverändert, erfasste Max-Payne-Dateien unverändert (`integrity.json`). Keine Hardlinks oder externe Datensicherung behauptet.

## Verhalten

Das bestehende WCR-Optionsmenü erhält einen Einstieg **HUD / Schriftgröße**. Vier gespeicherte Einstellungen: Automatik, Menü-/Schriftgröße, HUD-Größe und HUD-Sicherheitsbereich. Größen wirken sofort und bleiben auch bei Zurück/Escape bestehen. Die Startdateien übernehmen die zuletzt beendeten UI-Einstellungen in den nächsten Kampagnenkontext. Vorhandene FOV-/Steuerungswerte werden aus r4 übernommen, FOV 90 ist geprüft. Die Startdateien benötigen keine PowerShell-Skriptausführung und ändern keine Windows-Richtlinien.

Proportionale Elemente benutzen denselben X-/Y-Faktor. Größe und Randverankerung werden getrennt; auf Ultrawide wird das HUD innerhalb einer maximalen 16:9-Fläche verankert. Die klassische Menüfläche passt vollständig ins Fenster. Menügröße 1 ist die volle passende Fläche; kleiner ist bis 0,65 möglich. HUD-Größe reicht von 0,5 bis 2, der Sicherheitsbereich von 0,8 bis 1.

Kompass-Ebenen, Drehmitte, Textmessung und Widget-Klickflächen teilen das Koordinatenmodell. Missionsziele und native Untertitel brechen anhand der tatsächlich verwendeten Schrift um. Script-HUD bleibt proportional; vollständige Überblendungsflächen werden gesondert behandelt. Fernglasmasken bleiben 4:3-proportional mit schwarzen Seitenflächen, Zielfernrohre kreisförmig. Zentrale Meldungen und Pausensymbole folgen ebenfalls der HUD-Größe. Gameplay-Seitenverhältnis und FOV werden durch die UI-Skalierung nicht verändert. Vorhandene Schriftatlanten werden beibehalten; große Schrift kann entsprechend der Originalauflösung weicher erscheinen.

## Geprüft

| Prüfung | Ergebnis / genaue Grenze |
|---|---|
| Acht Auflösungen × AA/SH/BT | 24/24: 1280×960, 2560×1920, 1920×1200, 1920×1080, 2560×1440, 3840×2160, 3440×1440, 5120×1440. Tatsächliche gerenderte Fenster/Framebuffer, keine acht physischen Monitore. |
| Normierte Kompasshöhe | AA konstant 0,13333 der Bildhöhe; SH/BT konstant 0,14467. Breite=Höhe; alle Ebenen proportional. `matrix-summary.json`. |
| Größenwechsel + Save/Load | HUD-Faktor 1,25 erhöht Kompassgröße um genau diesen Faktor; Save/Load erhält die Geometrie in allen 24 Läufen. |
| Neue und bestehende Werte | 14 Werte je Kontext über Änderung, Prozessneustart und Wiederherstellung, 42/42; einschließlich FOV 90. `persistence-v1-*.json`. |
| Kontextwechsel | Echte Workspace-CMDs: AA schreibt, SH und BT übernehmen alle vier Größenwerte. Abschließend Standardgrößen und FOV 90. `launcher-persistence.json`. |
| Native Mausbedienung | HUD-Regler, Automatikschalter, Menüregler, Zurück und WCR-Einstieg bedient. Entdecktes Zurückspringen des sich selbst verschiebenden Reglers korrigiert. Rücknahme bei `popmenu 1` anschließend per Laufzeitprüfung korrigiert/verifiziert. |
| Deutsche Texte / Optik / Saves | Vier lange Ziele, Umlaute, mehrzeilige Untertitel, Script-HUD, echte ausgerüstete Ferngläser/Sniper und Save-Menü mit Vorschaubild. Endgültige Binärdateien in `delivery-AA-text`, `delivery-SH-text`, `delivery-BT-text`, jeweils ohne Skript-/Befehlsfehler. |
| Erhaltene WCR-Ressourcen | 195 AA-, 283 SH-, 323 BT-UI-Ressourcen inventarisiert. Alle ursprünglichen Bindungen bleiben erhalten; nur ein Einstieg ergänzt. `CP01-ui-resource-audit.json`. |
| Vollbild | 1920×1080 mit Spiel, HUD, Save/Load und Menüs bestanden. Große Fenster sind nicht als physische Ultrawide-Monitore ausgegeben. |
| Optionsseiten / Neuinitialisierung | Je AA/SH/BT fünf bestehende Optionsseiten geladen, dargestellt und vermessen; danach Fenster 1600×900 → Vollbild 1920×1200 → Fenster 1280×960 im selben Prozess. Menügröße 0,85 bleibt erhalten, acht Screenshots je Lauf. `reflow-*.json`, ausgelieferte Binärdateien. |
| Build / Integrität | Lokaler MSVC-x64-Build erfolgreich; Quellstand und Produkt-Hashes festgehalten. Separate GitHub-Builds, keine Spielassets in Git. |

Die 24er-Matrix gehört zum ersten UI-Build; spätere Text-, Regler- und Persistenzkorrekturen sind separat mit Binärhash dokumentiert. Die abschließenden `delivery-*-text.json` beziehen sich auf den ausgelieferten Commit. Nicht alle früheren Berichte werden deshalb als Tests derselben Binärdatei ausgegeben.

## Noch offene Abnahmepunkte

1. Reale Windows-Skalierungswechsel 100/150/200 %, native Fensterzieh- und Alt-Tab-Prüfung: nicht vollständig durchgeführt. Die spätere Computer-Use-Aufnahme scheiterte einschließlich einmaliger Wiederherstellung mit **`FrameArrived timed out: timed out waiting on channel`**. Kein Sicherheitsdialog und keine Windows-Skalierung automatisch geändert. Renderer-Neuinitialisierung per Videobefehl wird separat geprüft und ist kein Ersatznachweis für diese OS-Interaktionen.
2. Alle WCR-Optionsbindungen sind erhalten; eine vollständige Einzelprüfung der wahrnehmbaren Wirkung jedes Optionspunkts vor/nach Umbau ist nicht abgeschlossen. 42 Persistenzprüfungen ersetzen keine vollständige Wirkungsabnahme. Hardware-Mauszeiger/DPI-Verhalten bleibt dabei ein offener Punkt.
3. CP0/CP0a: frühere offene Missions-/Kampfprüfungen bleiben offen. Der CP00a-Bericht nennt unvollständige Afrika-/Italien-Aufbauten. BT-Finaltest bleibt auf ausdrücklichen Nutzerwunsch ausgelassen.

Damit ist die HUD-Funktion als überprüfter Kandidat verfügbar, aber **„CP1 vollständig abgenommen“ wäre nicht belegt**. Die noch offenen Punkte werden nicht durch eine Versionskennung oder einen erfolgreichen Build geschlossen.

## Wiederherstellung

CP00-r4 und dessen Profile/ZIP bleiben unverändert. Dessen Startdateien verwenden weiterhin den bisherigen Stand. Das CP01-Paket enthält die Workspace-Unterordner und Startdateien und ist zur lokalen Wiederherstellung in einen passenden Workspace bestimmt. Keine Originalinstallation überschreiben. Das zusätzliche BT-Paket wirkt nur in BT; für seine vollständige Aktivierung eine Mission neu starten.
