# CP00-r1 – technische Ausgangsbasis und offene Spielabnahme

**Nach Nutzerprüfung zurückgezogen:** Die r1-Startdateien enthalten einen nicht normalisierten Profilpfad, der Schreibzugriffe verhindert; den bereitgestellten Saves fehlen außerdem Vorschaubilder. Die unten protokollierten Konsolentests umgingen den Launcherfehler. Aktueller Korrekturkandidat: [CP00-r2](CP00-r2-REPORT.md). Dies sind Bereitstellungsfehler von Allied Campaign, keine nachgewiesenen WCR-Basisfehler.

Stand: 13.10.2026. Dieser Kandidat ist startbar, aber **keine vollständige CP0-Abnahme**. Ausschließlich Einrichtung, Inventar, Engine-Build und Basistests wurden umgesetzt. CP0a ist nicht freigegeben.

## Start und Teststände

Im Workspace liegen `Start-CP00-r1-AA.cmd`, `Start-CP00-r1-SH.cmd` und `Start-CP00-r1-BT.cmd`. Sie verwenden `runtime-local/CP00-r1` und getrennte Profile unter `profiles-local/CP00-r1/AA`, `SH`, `BT`. Basis-, Home-, Steam-, GOG- und Microsoft-Store-Suchpfade sind ausdrücklich auf den isolierten Aufbau gesetzt. Keine Hardlinks/Junctions zu Eingaben, keine importierten Originalspielstände. Nur eigene neue Teststände wurden in diese Nutzerprofile kopiert.

| Profil | Teststand | Karte / erwartete Szene |
|---|---|---|
| AA | `cp00_aa` | `m1l2a`, The Rescue Mission, Hof mit M1 Garand |
| SH | `cp00_sh` | `t1l2`, Normandy – Invasion, Funkdialog an der Windmühle |
| BT | `cp00_bt` | `e1l2`, Fahrzeugkolonne/Jeepfahrt durch Felsdurchfahrt |

Das Lade-Menü kann Missionsnamen statt interner Save-Namen anzeigen. Nach dem Laden gegebenenfalls „Continue“ anklicken. Diese Stände sind nur für diese Engine-Version geprüft. Alte Original-Saves wurden nicht auf Kompatibilität getestet.

Lokales Komplettpaket: `artifacts-local/CP00-r1-local-runtime.zip`, 2.811.360.801 Bytes. SHA-256: `36e93a60e1124e5fe09865cff5a634f4c2fcb318baa739fcbdf5ba322d899452`. Es enthält Runtime, Launcher, eigene Teststände und Originalspieldaten: ausschließlich lokal, **nicht auf GitHub hochladen**. Wiederherstellung nur in einen neuen leeren Ordner, ohne vorhandene Profile zu überschreiben.

## Fünf Nutzerprüfschritte

1. **AA:** AA-Startdatei öffnen, Teststand `cp00_aa` / „The Rescue Mission“ laden. Hof, M1 Garand und HUD prüfen; bewegen, zielen, schießen. In einen neuen eigenen Slot speichern, laden und zum Hauptmenü zurückkehren.
2. **Spearhead:** SH-Startdatei öffnen und `cp00_sh` / „Normandy – Invasion“ laden. Funkdialog an der Windmühle, Untertitel und Soldaten verfolgen. Nach Rückkehr der Steuerung bewegen; eigenen Slot speichern/laden und zum Menü zurückkehren. Dies ist noch keine vollständige WCR-Missionsprüfung.
3. **Breakthrough:** BT-Startdatei öffnen und `cp00_bt` laden. Jeep-/Kolonnenfahrt, Modelle, Dialoge und Fahrzeugton prüfen. Eigenen Slot speichern/laden und zum Menü zurückkehren. Fahrzeugton-Warnungen sind bereits bekannt und offen.
4. **AA-Missionsstart:** Eine neue erste Mission starten. WCR-Briefing „Rangers Lead the Way“ und Fahrt nach Algier prüfen; möglichst bis zur MG42-Nutzung und anschließendem Missionsfortschritt spielen. Bei Blockade Mission, letzte Aktion und Save nennen; keine Erfolgsflags setzen.
5. **Optionen/Rückmeldung:** Eine harmlose Option ändern, Spielteil normal schließen und neu starten; Persistenz prüfen. Je Spielteil Ergebnis und Fehler melden. BT-Finale, natürliche Levelübergänge und gezielte Referenzfälle bleiben gesonderte CP0-Prüfungen; diese fünf Schritte ersetzen sie nicht.

## Quell- und Buildzuordnung

| Gegenstand | Festgelegter Stand |
|---|---|
| Upstream | OpenMoHAA `a2f340195975f4f042e28a60b62561dd9a0b2700` |
| Engine im Kandidaten | `3eec4afb22093421b8776d2df92b87ec2fb4119e` |
| Deploymentstand | `c83f4bedd3cc3bdd06e37ac1d999566313004f05` |
| Branch | `codex/cp00-baseline` |
| Einmaliger Bootstrap auf main | `d5c399dab9bb078711cba3569cbbc7ea3a9c26cd` |
| Buildmanifest | `CP00-r1-build.json` |
| openmohaa.exe SHA-256 | `ed50e53a812d9ef1ef5ba196d1ce95f6fbecf75b388eabffec11cbfc2f61a464` |

Engine 0.83.0 unstable, Windows x64, MSVC 14.44.35207, SDK 10.0.26100.0, CMake 4.4.4, RelWithDebInfo. HTTP aus, GL1 statisch, GL2 aus, OpenAL an. OpenAL Soft 1.24.3, gebündeltes SDL 2.32.8, WinFlexBison 2.5.25. Downloadhashes: `toolchain.json`; beim Parser ist keine unabhängige veröffentlichte Prüfsumme belegt.

Rebuild: exakten Engine-Commit separat auschecken; `tools/build-cp00.ps1 -CMake <cmake.exe> -FlexBison <Ordner> -BuildDirectory <neuer leerer Buildordner>`. Visual Studio 2022 und genannter SDK erforderlich. SOURCE_DATE_EPOCH kommt vom Commit. Zweiter Checkout ohne Hardlinks erfolgreich kompiliert; **Binärhashes unterscheiden sich**, unter anderem sind PDB-/Buildpfade nicht normalisiert. Nachbaubarkeit durch Kompilieren belegt, keine Bitidentität und keine vollständige separate Spielprüfung des zweiten Builds. Siehe `rebuild.json`.

Der vor SDK-Installation konfigurierte Cache war unbrauchbar. Erfolgreiche Builds: `build-local/cp00-clean`, `build-local/repro-build`. Alte Fehlkonfigurationscaches nicht wiederverwenden; lokale Fehlerlogs bleiben erhalten.

## Bestand und Änderungen

9064 Eingabedateien, 2.815.749.802 Bytes, vollständig gehasht und unabhängig kopiert. AA, SH (`mainta`), BT (`maintt`) vorhanden. 25 PK3-Container geprüft: 24 im Spielbestand und ein nicht aktivierter Drop-Patch. Englische Ressourcen (`Pak6EnUk`) vorhanden; EXE-Versionsfelder in `input-program-versions.json`, nicht mit WCR-Version gleichsetzen.

WCR: sieben aktive Restoration-Pakete einschließlich AA Bash und drei Reflections-Module. Paketfingerprint: `0d681481b7deaaa76fbeb5466de634e6e6b0caf271b975e1f8052408b41f4fe9`. Lose Dateien ebenfalls übernommen; vollständiger Eingabemanifest-Hash im Buildmanifest. Kein WCR-Paket entfernt, ersetzt oder heruntergeladen. Keine belastbare lokale Versions-/Changelog-Zuordnung und kein separates OpenMoHAA-Anpassungspaket gefunden: **WCR_BASIS_UNGEKLAERT**, nicht die Behauptung, WCR fehle vollständig.

`_forCodex/ZZZ_more_ammo_health_Breakthrough.pk3` ist ein direkt bereitgestellter ZIP-kompatibler PK3-Container; kein äußeres ZIP gefunden. Zehn Skriptressourcen inventarisiert, darunter `global/loadout.scr` und `maps/e3l4.scr`; nicht aktiviert. Autor/Version lokal unbelegt. MP1-RAS/EXE und beide Wundtexturen inventarisiert, nicht importiert; kein Extraktionswerkzeug gefunden, Weitergaberechte ungeklärt.

Runtime: 8992 unveränderte Inhaltsdateien aus main/mainta/maintt, ohne originale saves/configs. Neu sind Engineprogramme/-DLLs, SDL/OpenAL, Lizenzen, Launcher und Buildmanifest. Vollständige eigene Dateiliste samt Hashes: `CP00-r1-build.json`; neue Saves außerhalb der Runtime: `local-evidence.json`.

Engine-Quelländerungen: Windows-Exportabfragen in `code/fgame/g_public.h` und `code/cgame/cg_public.h` verwenden `_WIN32`; `code/qcommon/q_shared.h` respektiert bereits gesetztes PRODUCT_DATE. Keine neuen Gameplay-/UI-/Blut-/Wund-/Leichen-/Kartenfunktionen. Zusätzlich Inventar-, Build-, Deployment-, Test-/Rückbauwerkzeuge, Projektregeln und Dokumentation. Neun upstream-eigene Workflows unverändert unter `docs/upstream-workflows` archiviert; eigener CP0-Workflow mit minimalen Rechten prüft Metadaten und baut ohne Spieldaten. Lizenz-/Herkunftshinweise bleiben erhalten.

## Automatisiert geprüft

| Prüfung | Ergebnis und Grenze |
|---|---|
| Original/Ausgangskopie | 9064 SHA-256 erneut identisch; MP1-Inventardateien ebenfalls unverändert |
| Runtime | 8992 Inhaltsdateien und 17 eigene Dateien entsprechen den Manifesten |
| PK3/ZIP | Inventarisierte Container und lokales Testpaket CRC-geprüft |
| Zwei frische Builds | Erfolgreich; unterschiedliche Binärhashes dokumentiert |
| GitHub CI | Engine- und Deployment-Commit erfolgreich; keine Spieltests auf CI |
| Save/Load AA/SH/BT | Neuer Stand geschrieben, `Game Loaded`, aktive Szene, Menü, Exit 0; `scene-*.json` |
| Rückbau | Nur eigene Engine/Launcher in unabhängiger Wegwerfkopie entfernt; exakt 8992 WCR-Inhaltsdateien erhalten; Profile/Kandidat unverändert |
| Ausschlüsse | Keine Original-PK3/RAS/Saves, Profile, Logs, Buildpakete oder Zugangsdaten versioniert |

Smokebedingungen: 1280×960, Fenster, GL1, OpenAL, maximal 60 FPS, Netzwerk für automatisierten Test aus, frische Profile. Enginewartewerte sind Millisekunden. `finishloadingscreen` entspricht dem normalen Continue-Button, setzt keine Missionsfortschrittsflags. Frühere `smoke-AA`/`rendered-*`-Versuche zeigten teilweise nur den Ladebildschirm; für die Szenenprüfung sind **scene-*** maßgeblich.

Laufzeitquellen durch `which`: AA `maps/m1l2a.scr` aus Restoration_AA_Pak1-Main, SH `maps/t1l2.scr` aus Restoration_SH_Pak1-Main, BT `maps/e1l2.scr` aus Restoration_BT_Pak1-Main. `global/ai.scr` jeweils AA Pak0, SH pak1, BT pak1. Kontexte: AA main, SH main+mainta, BT main+maintt; BT lädt nicht zusätzlich mainta. Übrige Konfliktmatrix weiterhin statische Vorhersage, keine pauschale Laufzeitabnahme.

## Selbst im Spiel bzw. am Renderbild geprüft

- AA m1l1: WCR-Briefing sichtbar, per Maus fortgesetzt; Lastwagenintro mit Soldaten/Gefecht bis sichtbarer Waffe/HUD beobachtet. Keine vollständige MG42-Prüfung. Tastatureingaben der Computersteuerung nicht verlässlich bestätigt; erster Diagnoselauf als eigener Prozess beendet. Spätere Smokes normal mit Exit 0 beendet.
- AA m1l2a: nach Save/Load Hof, Garand und HUD, anschließend Menübild geprüft.
- SH t1l2: nach Save/Load Windmühle, Soldaten/Funkdialog und sichtbare Untertitel, anschließend Menübild geprüft.
- BT e1l2: nach Save/Load Jeep, Soldaten/Kolonne und Felsdurchfahrt, anschließend Menübild geprüft.

Screenshots/Logs bleiben lokal; Pfade/Hashes in `local-evidence.json`. OpenAL-Initialisierung und RTX-4090-Renderer im Log bestätigt; korrekt hörbarer Gesamtton damit nicht nachgewiesen. Engine-Textlogs haben ein UTC+1-Label, das nicht als korrekte lokale Sommerzeit interpretiert wird.

## Fehler und offene Abnahmekriterien

| Befund | Einordnung / noch zu klären |
|---|---|
| AA m1l1: `dooropen`-Label fehlt | Sowohl in lokalem Pak5- als auch WCR-Skript kein entsprechendes Label; keine von uns geänderte Ressource. Originalengine-Verhalten und Fortschrittswirkung unbestätigt |
| AA: fehlendes truckride_viewmodel/fx_fence_wood; m1l2a voice type `m` | Ressourcen-/Engine-Kompatibilität offen; nicht als harmloser Basisfehler behauptet |
| SH t1l2: `explosionoffset` für Flak-Objekte fehlgeschlagen | Konkrete Skript-Kompatibilität offen; Flak-/Missionsfunktion nicht bestanden |
| SH: `smokegrenade_start` nicht geladen | Ressourcen-/Modellkompatibilität offen |
| BT: fehlende Fahrzeug-Soundaliases, `Unknown token growradius` | Ton-/Effektkompatibilität offen; sichtbare Kolonne allein genügt nicht |
| Übersetzungs-/Shader-/NPC-Leash-Warnungen | Lokale Logs; nicht pauschal ignoriert oder neuen Modfeatures zugeschrieben |

Nicht abgeschlossen: vollständige WCR-Optionen/Briefings/Dialoge/Animationen, AA-MG42 mit echtem Fortschritt, anspruchsvoller SH-Ablauf, restauriertes BT-Finale bis Abschluss, natürliche Levelübergänge, gewöhnliche Gefechte aller Titel, Waffen-ID-/Wand-/Leichen-/Despawn-/Statistikreferenzen, BT-Drops mit Schwierigkeit/Gegner/Killfolge, CPU-/GPU-Frametimes/Perzentile und längere Speicherprüfung. Keine Performancezahlen oder durchgespielten Missionen erfunden.

Konkrete Grenzen: kein verlässlich bestätigter Tastatur-Gameplaypfad der UI-Automation; Smokes ersetzen diese Fälle nicht. Lokale WCR-Versionsunterlagen fehlen. Unabhängige Schreibschutz-/Backupgrenze und serverseitiger Branchschutz nicht hergestellt. Deshalb transparente Teilübergabe, **keine Fertigmeldung für CP0**. Die fünf Nutzerprüfschritte ersetzen nicht die weiter ausstehenden technischen/gezielten CP0-Prüfungen durch Codex.

## Sicherung und Rückkehr

Originalinstallation und alte Saves unverändert. Zum Zurückgehen Kandidaten schließen und bisherigen Originalstartweg verwenden; Kandidaten-Saves nicht ins Originalprofil kopieren. Vollständige Ausgangskopie: `_ac-backup-local/CP00-input` neben dem Workspace, Hashmanifest daneben. Bei Dateiverlust stellt Codex in einen neuen leeren Zielordner wieder her und prüft vor Aktivierung die Hashes; Nutzer müssen nichts manuell ersetzen.

Rückbauprobe nur in eigens erzeugter `runtime-local/rollback-test-*`-Kopie, **keine Anweisung zum Löschen von Original oder Kandidat**. Sie prüft WCR-Daten; Originalprogramme sind im vollständigen Eingabesnapshot gesichert.

Repository privat, Besitzer xSonicB00Mx verifiziert. Quellen/Manifeste remote, Originaldaten ausschließlich lokal. Nach einmaligem Bootstrap kein main-Push, kein Merge/Auto-Merge/Force-Push. Branchschutz mit HTTP 403 wegen privatem Repositorytarif abgewiesen; weder Veröffentlichung noch Schutzumgehung. Offener technischer Schutzpunkt.

Zusätzliche Lieferkopie und verifiziertes Git-Bundle werden außerhalb des Workspace unter `_ac-backup-local/CP00-r1-delivery` mit lokalem Sicherungsbeleg abgelegt. Unabhängige Dateikopie auf demselben Laufwerk, **kein gegen dieselben Windows-Schreibrechte oder Laufwerksausfall geschütztes Backup**. Geschützte/externe Sicherung offen; keine eigenmächtigen ACL-/Systemänderungen.

Nach Übergabe: Nutzerfeedback und CP0-Nachprüfung/Korrektur. Kein CP0a ohne ausdrückliche weitere Freigabe.
