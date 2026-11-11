# CP08-r1: zwei Kartenbereiche und Treffer waehrend der Sterbeanimation

Die Karte im normalen Hauptmenue oeffnet jetzt die gemeinsame Einsatzwahl. Die bisherigen Missionsauswahl-Aktionen in AA, SH und BT sind auf `ac_campaign` umgebunden. Der Starter zeigt zuerst das Hauptmenue. WCR-Credits und andere Menuewege bleiben erhalten.

Es gibt nur noch **North Africa & Italy** und **Europe**. Gesperrte Operationen erscheinen weder als Marker noch in der Liste oder in der Vor-/Zuruecknavigation. Direkte gesperrte Auswahl faellt sicher auf einen freigeschalteten Einsatz zurueck. Sichtbare Zustaende sind CURRENT und COMPLETE; Available/Next/Locked als Kategorien entfallen. Benachbarte sichtbare Marker lassen sich als Gruppe durchschalten; jeder Einsatz bleibt direkt ueber die Liste erreichbar. Englische Spieltexte, mittiges proportionales 16:9-Menue.

## Sterbeanimation

Die native Kollisionsbox eines gerade getoeteten Actors konnte Kugeln abfangen. Die synchrone Einzelspieler-Kugelabfrage ueberspringt jetzt ausschliesslich tote Actors und stellt deren Contents sofort vor Schaden-/Eventverarbeitung wieder her. Dies gilt fuer die normale und die umgekehrte Materialpruefung. Es gibt weder Relink noch erneuten Todesaufruf oder Gameplay-Zufallsziehung. Die optische Abfrage trifft das animierte Mesh nur innerhalb des vom normalen Welt-/Gegnertreffer begrenzten Segments. Sie erzeugt die vorhandenen Blut-/Wundeffekte ohne weiteren Schaden oder Drops am sterbenden Actor. Das Durchdringen gilt auch bei abgeschalteten Bluteffekten.

## Nachweise

- Nativer Windows-Build erfolgreich; Metadaten-/Kampagnenvalidierung und bestehender C++-Visualtest bestanden.
- Frisches Profil zeigt nur Operation Torch; Europa ist noch leer. Vollstaendiger synthetischer Testfortschritt zeigt alle 15 Einsaetze in zwei Bereichen. Full HD, 4K, 4:3 und Ultrawide geprueft. Finale Full-HD-/Ultrawide-Aufnahmen visuell kontrolliert. Nutzerprofil nicht freigeschaltet oder veraendert.
- Sechs native Schusstests: Colt45 in AA/SH/BT sowie MP40, Kar98 und BAR in AA. Echter erster Toetungsschuss, danach Schuesse waehrend der nativen Sterbeanimation. 72 unmittelbar gepaarte Schuesse mit Leicheneffekten an/aus: gleicher Schaden am hinteren Actor in jedem Paar. Jeder Test enthaelt positive Treffer am animierten Vorderkoerper und hinteren Gegner innerhalb desselben Schusses; Vorderkoerper bleibt bei 0 Lebenspunkten, genau ein Todesereignis. Neue Wunden/Mist werden vom Client empfangen und gerendert.
- Ein Teil der 72 Paare verfehlt bei spaeteren Animationsposen den Koerper oder trifft den Boden; diese Nullschadenpaare sind keine Durchdringungsbelege. Die Zahl positiver gleichzeitiger Koerper-/Hintermanntreffer steht separat im JSON.

Maschinenlesbare Zusammenfassung: [feedback-two-regions-verification.json](feedback-two-regions-verification.json). Einzelberichte enthalten Binaerhashes, Ereignisse und lokale Bildpfade. Die ersten fuenf finalen Schusstests verwenden dieselbe finale game.dll und einen Engine-Stand vor der rein optischen Entfernung der Karten-Ortsbeschriftung; MP40 und die finalen Menuebilder verwenden auch die finale EXE.

Fruehe `dying-*-probe/on/near/final-*`-Laeufe sind Entwicklungsdiagnosen. Getrennte on/off-Laeufe hatten unterschiedliche Todesposen und sind kein gleicher Schadensvergleich. `dying-release-mp40.json` und `dying-release-kar98.json` schossen vor Waffenbereitschaft; `dying-release-mp40-ready.json` traf das animierte Mesh nicht. Diese Versuche gelten nicht als bestanden. Die positiven, gepaarten Wiederholungen sind in der Zusammenfassung explizit ausgewaehlt.

Grenzen: kein kompletter Kampagnendurchlauf, keine Gesamtmatrix aller WCR-Modelle/Waffen/Todesanimationen, keine pauschale Aussage ueber alle Gameplay-Zufallsfolgen. Der Hauptmenue-Klickpfad wurde anhand der gepackten Widgetaktion und nativen Menueausgabe geprueft, nicht durch physischen Mausklick. Keine persoenliche Abnahme und kein Merge.
