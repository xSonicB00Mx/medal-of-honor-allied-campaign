# LOADOUT fuer abgeschlossene Operations

Nutzerauftrag: persistente Ausruestung aus AA, SH und BT, ausschliesslich fuer
Wiederholungen abgeschlossener Kampagnenmissionen. Keine Multiplayer-Freigabe.

## Bedienung

Der fruehere Multiplayer-Platz im gemeinsamen Hauptmenue oeffnet LOADOUT.
Sieben Kategorien enthalten 44 tragbare Waffen und Ausruestungsvarianten.
Pro Kategorie kann eine Waffe oder DEFAULT ausgewaehlt werden. Die Auswahl wird
sofort gespeichert und zwischen AA, SH und BT geteilt. DEFAULT oben setzt alle
Kategorien zurueck; SHUFFLE LOADOUT stellt eine zufaellige Ausruestung zusammen.
Das Menue zeigt echte texturierte Waffenmodelle und deren Ursprungskampagne.
Operations bietet bei abgeschlossenen Einsaetzen einen direkten Loadout-Link.

Nur ein ueber Operations gestarteter, bereits abgeschlossener Einsatz erhaelt
die Auswahl. Neue Missionen, gesperrte Einsaetze, Briefing-Wiederholungen und
Mission-List-Highscore-Runs erhalten sie nicht. Die vorhandene Replay-Logik
schuetzt weiterhin den eigentlichen Kampagnenfortschritt.

Zusaetzliche unterschiedliche Waffen derselben Klasse lassen sich in diesen
Replays aufsammeln. Erneutes Druecken der gebundenen Klassen-Taste schaltet sie
durch; das funktioniert auch mit umbelegten Tasten. Ein Duplikat derselben Waffe
wird weiterhin als Munition behandelt. DEFAULT beeinflusst die Ausruestung des
naechsten Starts, nicht rueckwirkend einen laufenden Einsatz oder Spielstand.

## Umsetzung und Kompatibilitaet

- Gemeinsamer generierter Katalog, sieben archivierte und synchronisierte
  Auswahlvariablen; separate Freigabe aus dem geprueften Operations-Fortschritt.
- Vergabe nach der geskripteten Startausruestung, sobald der Spieler bewaffnet
  und steuerbar ist. Zwischensequenzen, Fahrzeuge und Geschuetze werden abgewartet.
- Ein vorhandener archivierter Level-Variablenbereich verhindert mehrfache
  Vergabe nach dem Laden. Keine Aenderung am binaeren Spielstandformat.
- Additive lokale Pakete ergaenzen fehlende Modelle, Materialien, Animationen,
  Projektile, Sounds, Inventareintraege und Munitions-HUDs. Native Waffendefinitionen
  und vorhandene Animationsnamen behalten ihre Prioritaet. Die gemeinsame
  Waffen-Zustandstabelle wird nur in freigegebenen Operations-Replays verwendet.
- Aufstellbares MG42 einschliesslich abgeleiteter Aufbau-/Basis-/FPS-Modelle.
  Waehrend des Aufbaus bleibt das Weltmodell sichtbar, statt eine nicht vorhandene
  Setup-FPS-Datei anzufordern.
- Replay-Minen reagieren auch auf KI. Eine eigene kleine Skriptlogik ersetzt hier
  die Multiplayer-Klassenpruefung, begrenzt auf acht Minen und ermoeglicht
  Entschaerfen, Beschiessen und Speichern. Native Missionsminen bleiben unveraendert.
- Ein beim Test gefundener Fehler beim Laden von `Container<str>` ist korrigiert:
  reservierte String-Speicherplaetze werden vor dem Einlesen konstruiert.
  Gespeicherte Bytes und Archive-Version 14 bleiben identisch.

Stationaere Bordwaffen, Fahrzeuge und Geschuetze sind weiterhin an ihre jeweiligen
Missionen gebunden; sie sind keine tragbaren Inventarwaffen. Doppelte Lite-/Start-
Definitionen werden nicht als separate Loadout-Waffen angeboten. Die ungewoehnliche
native FG42-Definition (fuenf Schuss, halbautomatisch) wird nicht neu ausbalanciert.

## Pruefungen

Native isolierte Testprofile pruefen Waffenwahl, Schussverbrauch, Nachladen,
physische Waffen-Pickups und Klassenwechsel sowie echte `ac_mission`-/
`ac_level_replay`-Starts mit Kontext-Neustart. Hinzu kommen gemeinsame Einstellungen,
DEFAULT/Locked/New/Score-Grenzen, Save/Load und ein vor der Archivkorrektur erzeugter
Testspielstand. Tests verwenden gesetzten Testfortschritt und gezielte Skript-
Fixtures; sie sind keine natuerlichen Komplettdurchlaeufe aller Missionen.

Lokale Befunde und Screenshots liegen unter `profiles-local/loadout/`,
Build-/Paketberichte unter `generated-local/loadout/`. Geschuetzte Eingaben und
das persoenliche Profil werden bei der Installation nochmals per Hash geprueft.
Spielassets, Binaerdateien, Screenshots und Saves werden nicht nach GitHub geladen.

Abgeschlossene Pruefungen:

- Native Builds von Engine, game.dll und cgame.dll erfolgreich.
- Alle 44 Katalogeintraege in AA ausgewaehlt und benutzt; Schuss-/Munitionsverbrauch
  und Nachladen geprueft. Das Garand wurde fuer den nativen Nachladezyklus zuerst
  leergeschossen. Das tragbare MG42 erhielt einen gesonderten Aufbau-/Schusstest.
- Zehn SH-Waffen in BT und zehn BT-Waffen in SH getestet. Der DeLisle-Nachtest
  wartet das Ende der geskripteten Einfuehrung ab, bevor er die Waffe prueft.
- Physischer Pickup und Klassenwechsel durch drei MPs erfolgreich.
- Gewehrgranate sowie Aufbau, Schiessen und Save/Load des tragbaren MG42 erfolgreich.
- Replay-Mine platziert, gespeichert, geladen und durch KI-Kontakt ausgeloest.
  Der erste Kontakt-Fixture hatte KI deaktiviert und damit auch die regulaere
  Beruehrungspruefung abgeschaltet; mit aktiver KI besteht er ohne direkte Touch-Injektion.
- Echter Levelwechsel m2l1 -> m2l2a behaelt den Replay-Kontext und den geschuetzten
  Fortschritt; die Auswahl wird nach einem geskripteten Ausruestungsreset ergaenzt.
- Echte Operations-Kontextstarts in AA/SH/BT einschliesslich Save/Load erfolgreich;
  neue/gesperrte Missionen, DEFAULT und Mission List separat geprueft.
- Gemeinsame Einstellungen AA -> SH -> BT -> AA und frische Neustarts erfolgreich.
- Vor der Archivkorrektur erzeugter Testspielstand laedt mit dem korrigierten Code.
- LOADOUT mit texturierten 3D-Waffen und Hauptmenue visuell kontrolliert.
- CP00-/Kampagnenvalidierung, Waffenrichtliniengenerator und Diff-Pruefung erfolgreich.

Die lokale Ergebniszuordnung steht in `loadout-validation.json`. In BT e3l3
bleiben drei urspruengliche Skriptmeldungen bestehen (NULL listener/self und
waittill spawn). Ein Vergleichslauf ohne Loadout-Ressourcenpaket reproduziert
exakt diese Meldungen; der Loadout-Lauf hat keine zusaetzlichen Skriptfehler.
Weitere native Asset-Warnungen sind unverkuerzt in den lokalen Logs erhalten.

Die Installation folgt nach dem Quellcode-Commit und wird separat protokolliert.
Keine persoenliche Nutzerabnahme und kein Merge behauptet.
