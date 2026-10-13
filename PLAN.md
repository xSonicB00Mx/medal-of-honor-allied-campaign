# Medal of Honor: Allied Campaign
## Verbindlicher Arbeitsauftrag für Codex

Stand des Plans: 13. Oktober 2026 · Revision 8. Vollständig aktualisierte Anleitung; ersetzt Revision 1 bis 7, nicht nur ein Ergänzungsblatt. Dieses Dokument beschreibt den Sollzustand und die Umsetzung; es behauptet nicht, dass die lokale Installation bereits untersucht oder die Mod bereits gebaut wurde.

**Neu in Revision 8:** Der übergebene MOHAA-Installationsordner wird laut Nutzer bereits **War Chest Restored** enthalten. Diese Mod ist verbindlicher Bestandteil der zu erhaltenden Inhaltsbasis von **Medal of Honor: Allied Campaign**, keine zu entfernende Altmod und kein zusätzlicher Downloadauftrag. Codex inventarisiert die tatsächlich installierte Fassung, aktive Zusatzpakete und Ressourcenherkunft und übernimmt sie in den geschützten Arbeitsstand. **Checkpoint 0 prüft jetzt ausdrücklich die WCR-Basis; Checkpoint 0a führt den lokalen BT-Drop-Patch damit zusammen.** UI, Bluteffekte, Körperwunden, Leichentreffer, Missionslader und Karte bauen anschließend darauf auf. Restaurierte Inhalte, funktionierende Optionen und bestehende Gameplay-Anpassungen bleiben erhalten, soweit eine ausdrücklich beauftragte Allied-Campaign-Änderung nicht genau diesen Teil ersetzt. Kein blindes Überschreiben, keine Rücksetzung auf Vanilla und keine Doppelanwendung gleichartiger Korrekturen. Die Checkpoint-Nummern und der von Codex betreute GitHub-Workflow bleiben erhalten. Hier wurden öffentliche Autorenbeschreibungen gelesen, **nicht** der lokale Installationsordner, die Modarchive oder ihre konkrete Kompatibilität geprüft.

**Weiterhin gültig aus Revision 7:** Der Nutzer hat keine praktische Git-/GitHub-Erfahrung und möchte das Repository nicht selbst verwalten. **Codex übernimmt die technische Repository-Pflege vollständig innerhalb der eingeräumten Berechtigungen:** Einrichtung, Arbeitsbranches, Commits, überprüfte Pushes, Pull Requests, Dokumentation, Versionierung, Testpakete und Wiederherstellung. Nach einer ausdrücklichen, auf den konkreten Testkandidaten bezogenen Freigabe im Codex-Chat führt **Codex auch den Merge** aus. Der Nutzer muss weder Git-Befehle eingeben noch Pull Requests manuell zusammenführen. Seine Aufgaben bleiben Anmeldung/Autorisierung, gegebenenfalls notwendige Sicherheitsbestätigungen, Spieltests und inhaltliche Entscheidungen. Keine automatische Featureabnahme, keine Umgehung von Schutzregeln und keine Zusage einer lückenlosen Hintergrundsicherung. Diese Datei richtet selbst weder ein Repository noch einen Kontozugang ein. Alle Modfeatures, Waffenregeln und Checkpoint-Nummern bleiben unverändert.

**Weiterhin gültig aus Revision 6:** Der Modname lautet **„Medal of Honor: Allied Campaign“**, ausdrücklich ohne „The“. Verwendet wird ein eigenes, zunächst privates Projekt-Repository mit einem Arbeitsbranch pro Checkpoint, nachvollziehbaren Sicherungen, eindeutig zugeordneten Testbuilds und erprobtem Rückbau. Originalspieldaten und lokal importierte Fremdassets bleiben auch aus einem privaten Git-Repository ausgeschlossen. Die frühere Vorgabe, der Nutzer müsse den PR persönlich übernehmen, ist durch die betreute Übernahme nach Chatfreigabe ersetzt.

**Unverändert aus Revision 5:** Der Nutzer lädt den Breakthrough-Patch selbst herunter und stellt ihn **als ZIP im MOHAA-Archiv** bereit. Codex verwendet dieses lokale Paket; **kein Patchdownload, kein Webseitenabruf zur Beschaffung und kein automatischer Ersatzdownload**. ZIP anhand seines Inhalts identifizieren, gegebenenfalls auch als verschachtelte Datei im bereitgestellten MOHAA-Archiv, und nur in einen getrennten Arbeitsbereich entpacken. Der Nutzer muss den Patch weder vorher entpacken noch installieren. Checkpoint 0a und alle bisherigen Funktions-/Abnahmeregeln bleiben erhalten. Diese Ankündigung ist kein Nachweis, dass das ZIP schon vorliegt oder geprüft wurde.

**Unverändert aus Revision 4:** Der vom Nutzer verlinkte Breakthrough-Patch **„Ammo and Health Drops“** wird verbindlicher Bestandteil aller Breakthrough-Missionen. Neuer, separat abnehmbarer Checkpoint **0a** nach der Ausgangsbasis und vor den Grafikänderungen; bestehende Checkpoint-Nummern einschließlich **5a** bleiben erhalten. Die Patchintegration muss auf den tatsächlich geprüften Patchdateien beruhen, im Breakthrough-Kontext standardmäßig aktiv sein und darf Allied Assault/Spearhead nicht verändern. Leichenbeschuss erzeugt weiterhin ausschließlich die vorgesehenen visuellen Effekte, niemals zusätzliche Munitions-/Heilungsdrops. Missionswechsel, Save/Load, Konfliktprüfung und Paketierung berücksichtigen den Patch ausdrücklich.

**Unverändert aus Revision 3:** Pistolen und Maschinenpistolen erzeugen kleine Eintrittswunden, dieselben großen Austrittswunden wie Gewehre/MGs sowie rückseitige Blutspritzer und Umgebungsflecken bei gültiger Geometrie. Jede Wunde behält ihre individuell zufällige Rotation/Spiegelung. Sämtliche Blutregeln gelten auch für Leichen. Die weiteren Ziele und Abnahmegrenzen bleiben erhalten.

## 1. Ziel und Umfang

**Projektname:** Medal of Honor: Allied Campaign. Empfohlener Repositoryname: `medal-of-honor-allied-campaign`. Der Repositoryname ist ein Vorschlag, kein bereits angelegtes Repository. Den gewählten Modnamen konsistent für Dokumentation, Mod-Startweg, Paketnamen und später die Mod-Menügestaltung verwenden. Historische Originalspiel-/Missionstitel, Credits und Lizenzhinweise nicht umbenennen. Keine neue Grafik-/Logoarbeit außerhalb des jeweils freigegebenen Checkpoints beginnen.

Erweitere Medal of Honor: Allied Assault einschließlich Spearhead und Breakthrough zu einer gemeinsamen Singleplayer-Erfahrung. Alle drei Kampagnen sollen in einer nachvollziehbaren chronologischen Missionsfolge spielbar sein. Bereits freigeschaltete Einsätze bleiben auf einer gemeinsamen, geografisch und historisch stimmigen Einsatzkarte auswählbar und wiederholbar.

Zusätzlich sind folgende Anforderungen verbindlich:

1. Auflösungs- und seitenverhältnisgerechte, lesbare Menüs, Schriften und HUD-Elemente in allen drei Spielen; insbesondere darf der Breakthrough-Kompass im Breitbild nicht verzerrt werden.
2. Die vorhandenen Trefferwölkchen an Gegnern werden rot eingefärbt. Dasselbe Treffernebel-System wird ab Checkpoint 5a auch bei neuen Treffern auf Leichen verwendet. Andere Rauch-, Staub- und Einschlageffekte bleiben unverändert.
3. Bluttexturen aus der lokalen Max-Payne-1-Installation werden für Bluteffekte verwendet. Sichtbare Tropfen fallen zu Boden und hinterlassen dort Flecken. **Pistolen, Maschinenpistolen, Gewehre und Maschinengewehre erzeugen bei gültiger Austrittsgeometrie auch rückseitige Blutspritzer und Flecken auf tatsächlich erreichbaren Flächen hinter dem Körper.** Eintrittsseitiger Blutnebel, Tropfen und erreichbare Bodenflecken bleiben zusätzlich erhalten.
4. Zwei vom Nutzer bereitgestellte Texturen werden punktgenau an getroffenen Körperoberflächen angebracht: Pistolen/Maschinenpistolen verwenden die kleine Eintrittstextur; Gewehre/Maschinengewehre die große Eintrittstextur. **Alle diese Waffengruppen verwenden für Austrittswunden die große Nutzertextur.** Für Pistolen-/MP-Austritte keine kleine Textur hochskalieren und keine dritte Textur voraussetzen. Jede neue Eintritts- und Austrittswunde erhält eine eigene Zufallsrotation und Zufallsspiegelung, die anschließend unverändert an dieser Wunde gespeichert bleiben.
5. Die Hauptmenü-Einsatzkarte wird grafisch und funktional erweitert, damit die gesamte kombinierte Kampagne darin Platz findet.
6. Leichen sind optisch beschießbar: Neue Schüsse auf tote Körper erzeugen ebenfalls Blutwolken, Blutspritzer, geeignete Umgebungsflecken und neue Körperwunden. Die Waffenregeln und die zufällige Texturorientierung gelten unverändert. Es wird kein lebender Zustand simuliert und keine zusätzliche Todesreaktion ausgelöst.

7. Alle Breakthrough-Missionen enthalten den vom Nutzer gewählten **Ammo-and-Health-Drops-Patch**. Er ist im Breakthrough-Kontext standardmäßig aktiv, unabhängig davon, ob eine Mission direkt, aus der Gesamtkampagne, als Wiederholung oder aus einem kompatiblen Mod-Spielstand gestartet wird. Die Patchwirkung bleibt auf Breakthrough beschränkt; AA und Spearhead behalten ihre bisherige Drop-Logik.

8. **War Chest Restored bleibt in allen drei Spielkontexten Bestandteil der bereitgestellten Ausgangsbasis.** Seine tatsächlich vorhandenen Restaurierungen, Fehlerkorrekturen, UI-/Optionsfunktionen, Modelle, Animationen, Dialoge und sonstigen aktiven Inhalte sind zu erhalten und in die gemeinsamen Systeme einzubinden. Maßgeblich ist der lokal dokumentierte Bestand, nicht eine vermutete Versionsnummer oder eine pauschal entpackte neue Modfassung. [S26–S29]

Nicht zum Auftrag gehören eigenständig neu entworfene Waffen, zusätzliche Physik/Ragdolls, neue Mehrspielerfunktionen, komplett neue Level oder eine neue Umschreibung der Handlung. Bereits mit War Chest Restored gelieferte und im übernommenen Bestand aktive Restaurierungen und Gameplay-/Balanceänderungen gehören dagegen zur Basis und werden nicht wegen dieser Umfangsgrenze entfernt. **Gegenüber dieser WCR-Basis ist die ausdrücklich beauftragte Änderung der Breakthrough-Munitions-/Heilungsdrops die einzige zusätzlich freigegebene Balancingänderung.** Darüber hinaus keine neuen Drop-Multiplikatoren, garantierten Drops, Schadens-/Gegneranpassungen oder eigenmächtigen Änderungen der Schwierigkeitsgrade einbauen. Bestehende WCR-Waffenwerte werden nicht unter dem Vorwand einer rein optischen Blutanpassung auf Vanilla zurückgesetzt.

### 1.1 Verbindliche Waffen- und Blutregeln

Diese Matrix ist eine gewünschte Spiel-/Darstellungsregel, keine Aussage über reale Wundballistik. Sie gilt in Allied Assault, Spearhead und Breakthrough gleichermaßen für lebende Gegner, Treffer während des Sterbens und Leichen:

| Waffengruppe | Eintrittstextur | Austrittstextur bei gültiger Geometrie | Eintrittsnebel / Tropfen | Eintrittsseitige bzw. erreichbare Bodenflecken | Rückseitiger Sprühzweig / Blut hinter dem Körper |
|---|---|---|---|---|---|
| Pistolen | klein | **groß** | ja | ja | **ja**, bei gültigem Austritt und erreichbarer Fläche |
| Maschinenpistolen | klein | **groß** | ja | ja | **ja**, bei gültigem Austritt und erreichbarer Fläche |
| Gewehre / Scharfschützengewehre | groß | **groß** | ja | ja | **ja**, bei gültigem Austritt und erreichbarer Fläche |
| Maschinengewehre / einschlägige stationäre MGs | groß | **groß** | ja | ja | **ja**, bei gültigem Austritt und erreichbarer Fläche |

**Die frühere Sperre für Pistolen und Maschinenpistolen entfällt vollständig.** Die kleine Eintrittstextur ist keine Sperre für Austritte oder rückseitiges Blut. Andere Waffenarten werden ausdrücklich zugeordnet oder separat behandelt; sie dürfen nicht versehentlich durch eine Schadensschwelle zu Gewehren werden.

„Groß“ bezeichnet die zweite, vom Nutzer gelieferte Körper-Treffertextur. Pistolen- und MP-Austritte verwenden exakt diese Ausgangstextur, dieselben Material-/Alpha-/Blend-Einstellungen und dieselbe Grundskalierung wie große Gewehr-/MG-Eintrittswunden. Auch Gewehr-/MG-Austritte verwenden diesen gemeinsamen großen Darstellungsstandard. Keine waffenabhängige Verkleinerung der Pistolen-/MP-Austritte und keine abweichende Ersatzgrafik. Die gewollte unabhängige Zufallsrotation/-spiegelung pro Wunde sowie die Anpassung an die jeweilige Körperoberfläche bleiben erhalten. Die MP1-Texturen dienen weiterhin Partikeln und Umgebungsflecken; sie ersetzen nicht die zwei Nutzertexturen für Körperwunden.

„Hinter dem Körper“ bezieht sich auf die Fortsetzung des tatsächlichen Schussstrahls durch den getroffenen Körper, nicht auf Kameraausrichtung, Himmelsrichtung oder Blickrichtung des Gegners. Bei allen vier aufgeführten Waffengruppen können von einer gültigen Austrittsstelle aus rückseitige Spritzer sowie Flecken an dahinterliegenden Wänden, Böden und geeigneten Objekten entstehen. Das gilt sowohl für direkt projizierte Flecken als auch für kollidierende Partikel. Nur Pistolen-/MP-Austrittswunden einzublenden, während ihr rückseitiger Sprüh- oder Weltfleckpfad weiterhin gesperrt ist, wäre eine unvollständige Umsetzung.

Trenne den Eintritts- vom Austrittszweig. Eintrittspartikel starten außerhalb der Eintrittsfläche und dürfen nicht durch den Körper tunneln. Austrittspartikel starten an der separat ermittelten Austrittsfläche; ein pauschal durch den Körper projizierter Fleck ist kein Ersatz für diese Prüfung. Beide Zweige berücksichtigen die tatsächlich zuerst erreichte Umgebungsfläche. Auch an einer liegenden Leiche dürfen Pistolen/MPs bei gültigem Austritt den dahinterliegenden Boden beflecken; weder Emitter noch Fleck dürfen dafür unter den Boden oder durch zusätzliche Hindernisse gesetzt werden. Ein verdeckter Fleck oder Austritt bleibt verdeckt. Ein von hinten beschossener Rücken ist relativ zu diesem Schuss die Eintrittsseite.

Hinterlege diese Regeln spätestens in Checkpoint 3 in **einer gemeinsamen Waffen-Effekttabelle**. Körperwunden, Nebel, Partikel und Weltflecken dürfen keine voneinander abweichenden Zuordnungen verwenden. Empfohlene, zunächst anzulegende Felder sind `weapon_id`, `entry_wound_material`, `exit_wound_material`, `allow_exit_wound` und `allow_exit_spray`; ergänze eine Version der Waffenpolicy. Das sind Entwurfsnamen, keine Behauptung über vorhandene Engine-APIs. Ein einzelnes gemeinsames `wound_material` reicht nicht mehr zur Auswahl beider Körpertexturen. Für Pistolen/MPs ist das Eintrittsmaterial klein und das Austrittsmaterial groß; für Gewehre/MGs sind beide groß. Für alle vier Gruppen sind beide `allow_exit_*`-Felder wahr. Effektoptionen, gültige Geometrie und Oberflächenerreichbarkeit werden zusätzlich geprüft; Materialgröße, Schadenswert oder die originale Gameplay-Durchdringung entscheiden nicht über diese optische Freigabe.

Die Sichtbarkeit der Körpertextur und die Berechtigung eines Austrittsspritzers sind getrennte Belange: Bei ausgeschalteten Körperwunden, aber eingeschaltetem Weltblut bleiben gültige rückseitige Bluteffekte für alle vier Gruppen möglich. Bei ausgeschaltetem Weltblut, aber eingeschalteten Körperwunden bleiben die erlaubten Austrittswunden möglich. Ein reiner Darstellungs-Schalter darf die gemeinsame Waffenpolicy nicht umschreiben. Die Visualisierung erzeugt weder neue Schadensereignisse noch zusätzliche Gameplay-Geschossdurchdringung.

### 1.2 Reihenfolge und Abnahmegrenzen

| Checkpoint | Nutzbares Ergebnis |
|---|---|
| 0 | Getestete, geschützte Ausgangsbasis **einschließlich der vorhandenen War-Chest-Restored-Installation** |
| **0a** | **Breakthrough: Ammo-and-Health-Drops-Patch mit WCR zusammengeführt, standardmäßig aktiv und kontextisoliert** |
| 1 | Vollständige UI-/HUD-Skalierung |
| 2 | Rote Gegner-Trefferwölkchen |
| 3 | MP1-Blutpartikel und Umgebungsflecken einschließlich rückseitigem Blut für Pistolen/MPs |
| 4 | Punktgenaue Eintrittswunden mit stabiler Zufallsrotation/-spiegelung |
| 5 | Geometrisch passende Austrittswunden mit großer Textur für Pistolen, MPs, Gewehre und MGs |
| **5a** | **Neue Treffer auf Leichen mit allen bis dahin abgenommenen Bluteffekten** |
| 6 | Gemeinsamer Missionslader |
| 7 | Chronologische Gesamtkampagne |
| 8 | Erweiterte Einsatzkarte |
| 9 | Gesamtregression und auslieferbarer Stand |

Checkpoint 2–5 liefern jeweils die benannte Funktion für lebende getroffene Gegner und ihre laufenden Treffer-/Todesanimationen. Bereits vorhandene Körperwunden bleiben beim Sterben erhalten. **Neue Treffer auf bereits tote Körper** sind der ausdrücklich separate Erweiterungsumfang von Checkpoint 5a; bis dahin darf dieser Teil nicht als erledigt ausgegeben werden. Die gemeinsame Waffenpolicy einschließlich rückseitigem Blut für Pistolen/MPs gehört bereits zu Checkpoint 3, die Texturvariation bereits zu Checkpoint 4, die sichtbaren Austrittswunden aller vier Gruppen zu Checkpoint 5. Nichts davon darf auf 5a verschoben werden.

Checkpoint **0a** ist ein eigenständiger Gameplay-/Skriptcheckpoint. Seine erste Abnahme erfolgt mit den separaten Spielkontexten aus Checkpoint 0; sie behauptet noch keine fertige gemeinsame Kampagne. Bei späteren Checkpoints 5a, 6, 7 und 9 werden die jeweils neu hinzukommenden Wechselwirkungen mitgeprüft. Bei bereits fortgeschrittener Arbeit wird 0a separat nachgeholt, ohne funktionierende Grafik- oder Kampagnenfeatures neu zu bauen.

**WCR wird vor 0a in Checkpoint 0 übernommen und geprüft, nicht erst am Ende über die fertige Mod kopiert.** Dafür entsteht kein zusätzlicher Checkpoint. Spätere Lieferungen bleiben kumulativ einschließlich WCR; die gezielten WCR-Regressionsfälle stehen in den jeweiligen Checkpoints. Bei schon laufender Entwicklung die WCR-Basis als getrennte, abnehmbare Kompatibilitätskorrektur nachführen und erst danach das nächste neue Feature beginnen.

### 1.3 Verbindlicher Breakthrough-Patch und Prüfstatus

Herkunftsreferenz des ausdrücklich gewünschten Patches [S8] – **kein Beschaffungsauftrag an Codex**:
`https://community.pcgamingwiki.com/files/file/2604-medal-of-honor-allied-assault-breakthrough-ammo-and-health-drops/`

Die über den Suchindex zugängliche Beschreibung dieser Downloadseite nennt ein PK3 mit Skriptänderungen, das einen Drop-Limiter entfernt und damit Munitions- und Heilungsdrops auf eine mit dem Hauptspiel vergleichbare Häufigkeit bringen soll. Das beschreibt das erklärte Patchziel, **keine verifizierte Prozentzahl und keinen bereits untersuchten Skript-Diff**. [S8]

**Bereitstellung:** Der Nutzer lädt genau diesen Patch eigenständig herunter und lässt ihn gezippt im bereitgestellten MOHAA-Archiv. Nutze ausschließlich dieses lokale ZIP als Patchquelle. Es kann im zugänglichen MOHAA-Verzeichnis oder als innere Datei des übergebenen MOHAA-Gesamtarchivs liegen. Beides ohne vorheriges Entpacken oder Installieren durch den Nutzer unterstützen. Keinen bestimmten Dateinamen voraussetzen; tatsächlichen Pfad, Archivinhalt und enthaltene Hinweise prüfen. Die Webadresse dient nur der Herkunftsdokumentation, nicht als Downloadabhängigkeit.

**Prüfstatus:** Revision 4 dokumentierte einen HTTP-403-Fehler beim direkten Seitenabruf. In Revision 5 bis 8 wurde diese Patchseite nicht erneut abgerufen; das angekündigte lokale ZIP und seine Readme wurden hier nicht untersucht. Archivname, genaue Version, Autorenschaft, interne Skriptpfade, konkrete Bedingungen und OpenMoHAA-Kompatibilität sind durch Codex am tatsächlich bereitgestellten Paket zu ermitteln. Keine geratenen Dateinamen oder Dropwerte als geprüft ausgeben. Keine stillschweigende Ersatzmod verwenden. Genau dieses lokale Paket untersuchen, seine relevante Änderung originalgetreu integrieren und testen.

### 1.4 Verbindliche War-Chest-Restored-Basis und Konfliktregeln

**Bereitstellung und Prüfstatus:** Der Nutzer stellt War Chest Restored bereits im MOHAA-Installationsordner bereit. Verwende diese lokalen Dateien. Die Herkunftsreferenz lautet `https://www.moddb.com/mods/war-chest-restored`. Kein erneuter Moddownload, keine automatische Aktualisierung und keine pauschale Neuinstallation. Ob die Daten lose, in PK3s oder zusätzlich in lokalen Lieferarchiven vorliegen, wird vor Ort ermittelt. Kein ungeprüfter Archivname, Versionsstring oder fester Installationspfad wird vorausgesetzt. Diese Planfassung hat die örtlichen Dateien nicht gesehen.

**Öffentlich beschriebene Überschneidungen – Hinweise für die lokale Prüfung:** Der Autor beschreibt Restaurierungen an Spielinhalten sowie Änderungen an HUD und Menüs. Die Optionsoberfläche enthält unter anderem Auflösung, Sichtfeld und Bildratenlimit; ein optionales OpenMoHAA-Paket ergänzt native Auflösung und randlosen Fenstermodus. Das ist keine Abnahme unserer vollständigen Skalierungsanforderungen. [S26] Version 1.1 beschreibt eine wiederhergestellte Fluchtsequenz am Breakthrough-Ende, veränderte Sanitätskit-Darstellung und NPC-Animationen. [S27] Der nachfolgende Patch 1.1.1 nennt unter anderem Briefing-/Savekorrekturen für OpenMoHAA sowie Änderungen an globalen Skripten. [S28] Aus diesen Angaben folgen die unten stehenden Prüfaufträge; die tatsächliche Dateiliste und Konflikte müssen lokal nachgewiesen werden.

Am 13. Oktober 2026 zeigten die geprüften Modseiten eine Vollversion 1.1 vom 30. April 2026 und einen als Teilupdate gekennzeichneten Patch 1.1.1 vom 20. Mai 2026. **Das ist nicht die festgelegte Version des Nutzerordners.** Codex dokumentiert die tatsächlich aktive Kombination, inklusive vorhandener Hotfixes und OpenMoHAA-Anpassungen. Ein Teilupdate allein gilt nicht als vollständige Basis. Fehlende oder abweichende Komponenten konkret melden, nicht still durch einen Download ersetzen. [S27–S29]

**Bedeutung von „Ausgangsverhalten“, „unverändert“ und „Original“ im übrigen Plan:** Für die Spiel-/Skriptregression ist ab dieser Revision die abgenommene Installation **mit WCR** maßgeblich. Ab 0a kommt der genau abgegrenzte BT-Drop-Merge hinzu. „AA/SH unverändert“ heißt daher unverändert gegenüber ihrer jeweiligen WCR-Basis, nicht Rücknahme von WCR. Originalarchive bleiben geschützte Eingaben und dürfen bei vorhandenen lokalen Dateien als technische Vergleichsreferenz dienen; ein Vanilla-Profil ist nicht die geforderte Lieferbasis. Die zwei Nutzer-Wundtexturen, MP1-Assets und Waffen-Effektmatrix bleiben unverändert verbindlich.

**Bestands- und Ressourcenmanifest:** Erfasse pro Spielkontext die vorhandenen Originalpakete, WCR-Dateien, aktiv installierten Zusatzmodule, anderen Overrides und späteren Allied-Campaign-Ergebnisse. Dokumentiere Version soweit belegt, SHA-256, relativen Dateipfad, innere Ressourcenpfade, Ladevorrang und Quelle der tatsächlich wirksamen Datei. Zusätzlich die Aufrufketten und semantischen Überschneidungen prüfen: Verschiedene Dateinamen schließen einen Konflikt an derselben KI-/Todes-/UI-Funktion nicht aus. Bei lose überschriebenen Dateien die Herkunft nur dann als WCR bestätigt ausweisen, wenn dafür lokaler Inhalt oder Dokumentation spricht; Unbekanntes nicht als Vanilla erfinden. Fehlende Originalreferenzen dürfen nicht durch Rekonstruktionen als vermeintlich echte Originaldateien ersetzt werden.

**Zusammenführung statt „letzte Datei gewinnt“:** Die logische Basis lautet Originaldaten → lokal aktive WCR-Fassung einschließlich benötigter vorhandener Kompatibilitätsanpassungen → geprüfte Allied-Campaign-Integration, in BT einschließlich 0a. Das ist eine inhaltliche Abhängigkeit, keine ungeprüfte Anweisung für alphabetische PK3-Namen. Tatsächliche Ressourcenauflösung am gepinnten Engine-Stand messen. Weder alle Pakete in alle drei Datenpfade kopieren noch allein durch weitere `zzz`-Präfixe einen Konflikt als gelöst betrachten. Für jede Kollision Entscheidung, betroffene Funktion, Eingabe-/Ergebnishashes und Test festhalten. Wenn verfügbar, Vanilla-, WCR-, Drop-Patch- und Allied-Campaign-Fassungen getrennt vergleichen und nur die benötigten Änderungen zusammenführen.

Die **ausdrücklich verlangte Allied-Campaign-Funktion hat in ihrem abgegrenzten Bereich Vorrang**, nicht automatisch eine ganze Allied-Campaign-Datei. Beispiel: Unsere UI-Skalierung ergänzt das vorhandene Menü, ohne dessen funktionierende Einstellungen zu entfernen; der Drop-Patch ändert die geprüfte Dropregel, ohne den Rest des WCR-KI-Skripts zurückzusetzen. Bereits gleichwertig vorhandene Fixes weiterverwenden und testen, nicht doppelt ausführen. Ein Konflikt gilt erst als gelöst, wenn sowohl die neue Anforderung als auch die unberührten WCR-Funktionen nachgewiesen sind. Ist beides mit dem aktuellen Lösungsweg nicht möglich, den konkreten Konflikt als offen ausweisen; keine stille Inhaltsstreichung oder Abschwächung.

**Optionale Inhalte und Engine-Kompatibilität:** Bereits aktive WCR-Zusätze bleiben Teil der dokumentierten Basis. Nur mitgelieferte, bislang inaktive Bonus-/Coop-Pakete nicht automatisch aktivieren. Ein lokal vorhandenes, für den gewählten OpenMoHAA-Stand erforderliches Kompatibilitätspaket zunächst prüfen und die gezielte Aktivierung in der CP0-Lieferung offen ausweisen; keine willkürliche komplette Bonusinstallation. Beigefügte Installations-/Deinstallationsprogramme nicht ungeprüft auf dem Eingabeordner ausführen. Die Moddb-Seite enthält außerdem einen Autorenhinweis vom 3. Oktober 2026 auf einen in OpenMoHAA-Entwicklungsständen korrigierten MG42-Skriptfehler. Daraus folgt ein gezielter Trigger-/Fortschrittstest, keine pauschale Versionsgarantie oder Freigabe eines ungeprüften Kommentar-Workarounds. [S29]

**Git, Wiederherstellung und Herkunft:** WCR-Pakete, extrahierte Fremdassets und nicht zur Weitergabe freigegebene Skriptfassungen bleiben nach der bestehenden Projektregel außerhalb von Git/Git LFS und GitHub-Releases, auch bei privaten Repositories. Versioniert werden eigene Integrationslogik, Abhängigkeits-/Hashmanifeste, Konfliktentscheidungen, Tests und zulässige Credits. Benötigte zusammengeführte Fremdskripte werden lokal aus den dokumentierten Eingaben erzeugt. Ein Build ist nur eindeutig, wenn neben dem Quellcommit auch WCR-Version/-Hashes, aktive Module und Merge-Rezeptversion feststehen. Hinweise und Urheberschaft aus den lokalen Dokumenten erhalten; der Projektname ersetzt keine Drittanbieter-Credits. Unbekannte Weitergabebedingungen nicht durch Vermutungen über kostenlose Mods ersetzen. **Rückbau von Allied Campaign stellt die übernommene WCR-Basis wieder her, nicht ein WCR-freies Vanilla-Spiel.**

## 2. Architekturentscheidung und technische Ausgangspunkte

Bevorzugte Basis ist ein eigener, reproduzierbar gebauter OpenMoHAA-Fork, der die vorhandenen Originaldaten verwendet. OpenMoHAA nennt Allied Assault sowie beide Erweiterungen ausdrücklich als unterstützte Singleplayer-Kampagnen. Das ist eine geeignete Ausgangsbasis, aber kein Nachweis, dass jede lokale Version und jede neue Funktion bereits fehlerfrei läuft. [S1]

Falls im Arbeitsordner bereits eine funktionierende Umsetzung unserer früheren Kampagnenidee vorhanden ist, analysiere sie zuerst. Übernimm getestete Komponenten; baue sie nicht ohne konkreten Grund neu.

Wichtige überprüfte Ansatzpunkte im öffentlich einsehbaren Quellstand:

- Die offizielle Startdokumentation unterscheidet `com_target_game` 0, 1 und 2 sowie `main`, `mainta` und `maintt`. Dabei wird auch das Protokoll passend zum Zielspiel gewählt. Eine gemeinsame Kampagne darf deshalb nicht allein durch das gleichzeitige Einhängen aller Archive behauptet werden. [S2]
- `code/cgame/cg_drawtools.cpp` enthält `CG_AdjustFrom640`, virtuelle HUD-Koordinaten und `uiHiResScale`. Der betrachtete Code hat mehrere Skalierungspfade; diese müssen gemeinsam geprüft werden. Das allein beweist noch nicht die konkrete Ursache jedes gemeldeten UI-Fehlers. [S3]
- `code/cgame/cg_specialfx.cpp` referenziert unter anderem `models/fx/bh_human_uniform_lite.tik` und `models/fx/bh_human_uniform_hard.tik`. Das sind konkrete Startpunkte für die Suche nach den Trefferwölkchen, keine ungeprüfte Garantie für sämtliche Trefferarten. [S4]
- `code/cgame/cg_marks.c` enthält `CG_ImpactMark` und Projektionspfade für Welt-, Terrain- und Inline-Model-Markierungen. Daraus folgt nicht automatisch eine fertige Lösung für animierte Körperwunden. [S5]
- `code/fgame/weaputils.cpp` enthält `BulletAttack` und die Weitergabe von Trefferposition, Normalen und Trefferregion. Im betrachteten AA-Protokollpfad wird `bulletlarge` anhand des Schadens gesetzt. Verwende diesen Schalter nicht ungeprüft als Zuordnung der beiden vom Nutzer gewünschten Waffengruppen. [S6]

Prüfe alle Namen am tatsächlich ausgecheckten Commit erneut. Keine geratenen Binäroffsets, erfundenen Dateinamen oder ungeprüften Behauptungen über vorhandene APIs. Codequellen dienen als Einstieg; entscheidend ist der reproduzierbare lokale Befund.

Die Enginequellen sind nur eine Ebene. Vor einer Änderung zusätzlich die effektiv geladenen WCR-Skripte, UI-Definitionen, Modelle und Konfigurationen untersuchen. Für die Enginewahl die WCR-Skriptkompatibilität in CP0 nachweisen und erst dann den Quellstand festlegen. Ein kompatiblerer Ausgangscommit ist hier zulässig; spätere Engine-Updates bleiben separate Wartungsänderungen. Keine Restaurierung löschen, um einen unpassenden alten Engine-Stand scheinbar kompatibel zu machen.

## 3. Verbindlicher Arbeitsmodus

### Ein Checkpoint pro Arbeitsrunde

Arbeite ausschließlich am aktuellen Checkpoint. Halte nach dessen Fertigstellung an und liefere einen startbaren, kumulativen Teststand. Beginne den nächsten Checkpoint erst nach Rückmeldung des Nutzers.

Checkpoint 0 ist die ausdrücklich bezeichnete Einrichtung einer getesteten Ausgangsbasis. Ab Checkpoint 0a muss jeder Zwischenstand eine nutzbare, durchgängig eingebaute Funktion liefern. Die spielübergreifende Integrationspflicht bedeutet nicht, Breakthrough-Drops auf andere Spiele auszuweiten: Bei 0a sind die Funktion in BT und ihre nachgewiesene Nichtwirkung in AA/SH maßgeblich. Ein Prototyp, der nur in einer Testmap oder bei einem einzigen Gegnermodell funktioniert, zählt nicht als abgeschlossenes Feature.

Bei Fehlerfeedback bleibst du im aktuellen Checkpoint und veröffentlichst eine korrigierte Revision. Vermische diese Reparatur nicht mit neuen Funktionen. Falls ein Checkpoint blockiert ist, dokumentiere die konkrete Ursache und erhalte den letzten funktionierenden Stand; ersetze die geforderte Funktion nicht stillschweigend durch eine schwächere.

### Schutz der Installation

Behandle die Originalarchive und Originalprogramme beider Spiele sowie den übernommenen WCR-Dateibestand als unveränderliche Eingaben. Verwende einen separaten Workspace, Mod-Overrides und einen eigenen Profil-/Save-Pfad. Sichere Dateien vor einer notwendigen Änderung und führe eine Liste jeder hinzugefügten bzw. veränderten Datei. Eigene Änderungen und unveröffentlichte Arbeit des Nutzers nicht durch Git-Reset, Clean oder pauschales Entpacken überschreiben.

Lege fest: Engine-Commit, Toolchain, Buildoptionen, Asset-Suchreihenfolge, Version des Mod-Manifests und Version des Save-Schemas. Für den Breakthrough-Patch zusätzlich Herkunfts-URL, lokalen relativen Quellpfad einschließlich eines gegebenenfalls inneren Archivpfads, Paketversion soweit vorhanden, SHA-256 des bereitgestellten Patch-ZIP und relevanter enthaltener Pakete sowie Version der lokalen Integration festhalten. Ein selbst ermittelter Hash dokumentiert die verwendete Kopie; ohne unabhängigen Referenzhash ist er kein Nachweis der Originalauthentizität. Keine stillen Upstream- oder Drittpatch-Updates zwischen Checkpoints.

Dasselbe gilt für WCR: lokale Fassung, aktive Module, Dateien-/Ressourcenherkunft und Inhalts-Hashes vor und nach dem Import vergleichen. Ein Wiederherstellungspunkt umfasst auch diese Abhängigkeit. Normale CP-Lieferungen dürfen WCR weder deinstallieren noch aktualisieren; reproduzierbare lokale Integrationsprodukte erhalten ein eigenes Besitz-/Dateimanifest, damit ein Rollback ausschließlich die dafür vorgesehenen Allied-Campaign-Dateien entfernt.

### Definition eines lieferbaren Checkpoints

Jede Lieferung enthält den startbaren Build samt benötigten Mod-Dateien, einen exakt dokumentierten Startweg, den exakten Git-Commit, den Arbeitsbranch, den bestätigten Remote-Sicherungsstatus und gegebenenfalls den zugehörigen Kandidaten-Tag, Änderungen seit der letzten Abnahme sowie die zugehörigen Testergebnisse. Gib dem Nutzer drei bis fünf konkrete Schritte für den Sicht-/Spieltest.

Trenne im Testbericht ausdrücklich: automatisiert bestanden, selbst im Spiel geprüft und noch vom Nutzer zu prüfen. Ein erfolgreicher Build ist kein bestandener Gameplay-Test. Schreibe keine vollständige Kampagnenabnahme, solange nur die Startmaps geladen wurden.

Verwende Statuswerte wie `IN_ARBEIT`, `BEREIT_ZUM_NUTZERTEST`, `ABGENOMMEN` und `BLOCKIERT`. Ein Stand darf nicht ohne Rückmeldung des Nutzers als von ihm abgenommen markiert werden.

## 3.1 Git-/GitHub-Workflow und echte Wiederherstellbarkeit

Dieser Abschnitt legt einen **von Codex betreuten Einzelprojekt-Workflow** fest. Der Nutzer entscheidet über die Mod und testet die Ergebnisse; Codex verwaltet die Entwicklungsgeschichte und führt die erlaubten technischen Schritte selbst aus. Keine Git-/GitHub-Kenntnisse des Nutzers voraussetzen. Keine Routineanweisung wie „Erstelle jetzt einen Branch“, „Pushe die Änderungen“ oder „Merge den PR“ an ihn delegieren, wenn Codex dafür selbst die eingeräumten Werkzeuge nutzen kann.

Die Delegation ist keine pauschale Erlaubnis zum Verbinden beliebiger Konten, zum Erstellen öffentlicher Repositories, zum Ändern fremder Projekte oder zum Erweitern von Kontoberechtigungen. Vor Remote-Schreibaktionen Eigentümer, konkretes Ziel-Repository und verfügbare Rechte anhand der tatsächlichen Umgebung prüfen. Für die Einrichtung ist ein neues privates Repository `medal-of-honor-allied-campaign` im ausdrücklich freigegebenen persönlichen Konto vorgesehen. Kein Organisationskonto auswählen und vorhandene gleichnamige Repositories nicht überschreiben. Fehlender Remote-Zugang verhindert keine sichere lokale Bestandsaufnahme, muss aber ausdrücklich als fehlende Remote-Sicherung gemeldet werden. Keine erfundene Repository-URL verwenden.

### Arbeitsteilung: Codex verwaltet, der Nutzer entscheidet

Codex übernimmt die lokale Git-Einrichtung, die zulässige Repositoryanlage, die Pflege der Projektregeln, Branches, Commits, Pushes, PRs, Testberichte und Versionsreferenzen. Es baut und paketiert Kandidaten, prüft den Remote-Sicherungsstand und führt nach konkreter Nutzerfreigabe deren technische Übernahme durch. Es erhält einen startbaren abgenommenen Stand und stellt ihn bei einem Rückbauwunsch wieder bereit, ohne ungesicherte Arbeit zu zerstören.

Der Nutzer erledigt nur Schritte, die seine Identität oder persönliche Entscheidung erfordern: Anmeldung und gegebenenfalls Zwei-Faktor-Bestätigung direkt beim Anbieter, erforderliche Betriebssystem-/Codex-Sicherheitsfreigaben sowie Spieltests und Freigaben im Codex-Chat. Codex bereitet diese Schritte vor und erklärt bei einem tatsächlichen Hindernis **nur die konkret notwendige Handlung**. Nicht routinemäßig einen GitHub-Grundkurs, manuelle Git-Kommandos oder GitHub Desktop als zusätzliche Voraussetzung verlangen.

„Eigenständig“ bedeutet hier **während der jeweils ausgeführten und autorisierten Codex-Aufgabe**. Die Kontoverbindung ist kein separater, dauerhaft laufender Sicherungsdienst. Keine Arbeit nach Sitzungsende, Sicherung jedes Tastendrucks oder Wiederherstellung noch nicht gespeicherter Änderungen zusagen. Keine geplanten Hintergrundaufgaben oder automatischen Merges einrichten, nur um Eigenständigkeit zu behaupten.

### Arbeitsumgebung und Zugang

Für dieses Projekt wird **lokale Codex-Ausführung im separaten Projekt-Workspace mit GitHub als Remote** bevorzugt. So können freigegebene lokale MOHAA-/Max-Payne-Eingaben und die Windows-Testumgebung getrennt von den hochgeladenen Quellen genutzt werden. Die lokale Codex-CLI kann Dateien bearbeiten und lokale Werkzeuge ausführen; ein Cloud-Task hat dagegen seine eigene eingerichtete Arbeitsumgebung. Die GitHub-Verbindung allein stellt dort keine lokale Windows-Spielinstallation bereit. Cloud-Arbeit bleibt für geeignete Quellcode-/Testaufgaben möglich, ersetzt aber keinen tatsächlichen lokalen Grafik-/Gameplay-Test. Lokale Werkzeugausführung ist außerdem keine Zusage, dass die Modellinferenz offline stattfindet. [S9, S10]

Codex verwendet ausschließlich den freigegebenen Projektbereich und notwendige Datenpfade. Originalspielordner nur lesen; Build, Entpacken und Laufzeitdateien in getrennten Ordnern schreiben. Keine vollständigen Installationen in ein Repository kopieren, nur damit ein Cloud-Task darauf zugreifen kann.

Bei der GitHub-Anbindung die offizielle Anmeldung bzw. App-Autorisierung verwenden und möglichst **Only select repositories** auf dieses Projekt beschränken. Die tatsächlich verlangten Berechtigungen prüfen; keine individuell frei wählbaren App-Rechte erfinden, wenn die verwendete Integration sie als festes Paket verlangt. Für lokale Git-Zugänge nur zweckgebundene, möglichst repositorybeschränkte Zugangsdaten in einem geeigneten Credential-Speicher verwenden. Keine Passwörter, Zugriffstoken, SSH-Privatschlüssel oder sonstigen Geheimnisse in Chat, Repository, Buildprotokoll oder Paket schreiben. Breite Administratorrechte und Zugriff auf andere Projekte sind für diesen Arbeitsablauf nicht vorgesehen. [S11]

Die normale lesende GitHub-Anbindung in ChatGPT ist nicht gleichbedeutend mit einem eingerichteten Codex-Schreibzugang. Die offizielle OpenAI-Hilfe unterscheidet ausdrücklich zwischen Repositoryanalyse in ChatGPT und Bearbeiten/Pushen über Codex. Vor einer Erfolgsmeldung die tatsächliche Fähigkeit zum erlaubten Push in den Arbeitsbranch nachweisen. [S12]

### Einmalige Einrichtung durch Codex

Zuerst Arbeitsordner, vorhandene Git-Historie, Git-Konfiguration, verfügbare Werkzeuge, GitHub-Anmeldestatus und bestehende Remotes prüfen. Einen vorhandenen funktionsfähigen Zugang wiederverwenden, sofern er für das konkrete Projekt freigegeben ist. Git-Identität projektlokal einstellen; keine globale Identität oder andere Projektzugänge stillschweigend umkonfigurieren. Eine erforderliche E-Mail-Adresse aus der vorhandenen freigegebenen Konfiguration bzw. dem tatsächlichen GitHub-Konto ermitteln, nicht erfinden oder aus privaten Originaldaten übernehmen.

Unter Windows sind Git und die **GitHub CLI (`gh`)** der bevorzugte einfache Werkzeugweg. OpenAI dokumentiert beide für lokale Entwicklungsarbeit und weist für GitHub-Funktionen auf `gh auth login` hin. Codex kann benötigte Installationen vorbereiten bzw. nach erforderlicher Zustimmung selbst ausführen. Nicht vorsorglich weitere Laufzeitumgebungen oder ein zweites Git-GUI installieren, wenn sie nicht gebraucht werden. Den Codex-Prozess nicht pauschal dauerhaft als Administrator starten. [S21]

Ist keine passende Anmeldung eingerichtet, den offiziellen Browser-Anmeldeweg starten und den Nutzer dort selbst bestätigen lassen. `gh auth login` unterstützt diesen Browserweg. Zugangsdaten dürfen nicht in den Chat eingefordert oder ausgegeben werden. Prüfen, dass ein geeigneter System-Credential-Speicher verwendet wird: Die CLI kann bei dessen Fehlen auf eine Klartextdatei zurückfallen; das nicht unbemerkt akzeptieren und `--insecure-storage` nicht verwenden. [S22]

**Berechtigungsgrenzen ehrlich dokumentieren:** Ein gewöhnlicher `gh auth login` ist nicht automatisch eine technisch auf ein einzelnes Repository beschränkte GitHub-App-Installation. Tatsächlich verwendete Zugangsmethode und Rechte prüfen. Wo verfügbar repositorybeschränkte Zugänge verwenden; andernfalls die breitere Reichweite vor der Autorisierung klar erklären. Die Regel „nur dieses Projekt bearbeiten“ nicht als technisch erzwungene Kontosperre ausgeben. Rechte für Repoanlage und spätere Pflege können unterschiedlich sein. Einen fehlenden Anlage-/Schreibzugriff nicht durch heimliche Scope-Erweiterung lösen. [S11, S22]

Nach Freigabe des konkreten Kontos und Anlageziels erstellt Codex das private Repository selbst, soweit der Zugriff dies erlaubt. Die GitHub CLI bietet mit `gh repo create` eine nichtinteraktive Anlage einschließlich privater Sichtbarkeit. Erst auf bestehende gleichnamige Ziele prüfen; nach der Anlage Eigentümer, Sichtbarkeit und Remote-Adresse erneut abfragen. Reicht die eingeräumte Berechtigung zur Anlage nicht aus, genau diesen Einrichtungsschritt als blockiert melden und die minimale erforderliche Nutzerhandlung erklären; daraus folgt keine dauerhafte manuelle Repo-Pflege. [S23]

Bei einem tatsächlich leeren, neuen Repository darf Codex einmalig einen ausdrücklich ungetesteten Quell-/Dokumentations-Bootstrap anlegen, damit ein Hauptbranch und ein PR-Ziel existieren. Dies ist die einzige initiale Ausnahme vom Verbot direkter Hauptbranch-Pushes und keine Abnahme eines Spielstands. Danach erfolgt die Basiseinrichtung auf `codex/cp00-baseline`. Bereits vorhandene Hauptstände dürfen über diese Ausnahme niemals ersetzt werden.

Codex richtet `.gitignore`, die kurze `AGENTS.md`, `PLAN.md`, `STATUS.md`, PR-Vorlage und die verfügbaren Schutzregeln ein. Anschließend einen erlaubten Arbeitsbranch pushen, dessen Commit-ID vom Remote frisch zurücklesen und einen PR für den Checkpoint vorbereiten. Erst den nachgewiesenen Zustand als eingerichtet melden; reine Kontoanmeldung genügt nicht.

Sandbox-, Netzwerk- oder Aktionsfreigaben können weiterhin nötig sein. Codex verwendet die vorgesehene Genehmigung und nennt bei einer Blockade den Zweck; es deaktiviert keine Sicherheitsmechanismen, um Rückfragen zu vermeiden. Lokale Schreib-/Netzwerkrechte und Genehmigungsregeln werden durch die Codex-Umgebung kontrolliert und nicht allein durch diesen Plan vergeben. [S25]

### Repository, Upstream und Inhalte

Vorgesehen ist zunächst ein eigenes **privates** Projekt-Repository. Ein normaler GitHub-Fork eines öffentlichen Repositories bleibt öffentlich; keinen privaten Fork über eine nicht vorhandene Sichtbarkeitsoption versprechen. Für eine private Entwicklung ein eigenständiges Repository mit sauber dokumentierter OpenMoHAA-Basis verwenden. Herkunft, ursprüngliche Commit-ID, Lizenz- und Copyright-Dateien bleiben erhalten. Vorhandene Git-Historie möglichst übernehmen, nicht bei jeder Lieferung durch ein neues Quell-ZIP ersetzen. [S13]

Es muss nachvollziehbar gesichert sein, **welcher tatsächlich geänderte Engine-Quellcode** zu jedem Modstand gehört. Ein Verweis nur auf einen alten Upstream-Commit reicht nicht, wenn lokale Rendereränderungen zusätzlich existieren. Bevorzugt die benötigten Quellen im Projekt mitversionieren; bei einem separaten Engine-Repository bzw. Submodule müssen auch dessen Änderungen gepusht, verfügbar und exakt gepinnt sein. Keine allein lokal existierenden Submodule-Commits. Upstream-Updates nur als eigene, bewusst freigegebene Wartungsänderung mit Regressionstests, nicht während eines anderen Checkpoints.

Versioniert werden eigene bzw. entsprechend nutzbare Quellen, Engineänderungen, Skripte, Shader, UI-Definitionen, Waffenpolicy, Missionsmanifest, Import-/Buildwerkzeuge, Tests, Dokumentation und freigegebene eigene Assetquellen. Die zwei Nutzer-Wundtexturen nur nach geklärter Einordnung als freigegebene Projektassets in das Repository übernehmen; andernfalls lokal importieren und anhand von Hashes referenzieren.

**Nicht in Git, Git LFS oder GitHub-Uploads aufnehmen:** vollständige MOHAA-/Max-Payne-Installationen und ihre Originalarchive, extrahierte MP1-Bluttexturen, proprietäre abgeleitete Importpakete, Originalprogramme, persönliche Spielstände, private lokale Pfadkonfigurationen, Zugangsdaten und ungeprüft mitverteilte Drittpatch-Dateien. Dies ist eine Projekt-Paketierungsregel, keine Behauptung über allgemeine Nutzungsrechte. Sie gilt auch bei privater Repositorysichtbarkeit. Das BT-Patch-ZIP bleibt im lokalen MOHAA-Eingabebestand; im Repository stehen Import-/Integrationslogik, relative Herkunftsreferenzen, Prüfsummen und die bereits verlangte Dokumentation. Erforderliche, nicht zur Mitverteilung freigegebene Skriptfassungen werden beim lokalen Import reproduzierbar erzeugt. Auch Textdokumente, Testberichte und Diffs vor dem Push auf eingebettete Originalinhalte bzw. Geheimnisse prüfen.

Eine projektbezogene `.gitignore` wird **vor** dem ersten eigenen Import eingerichtet, mit Ausschlüssen insbesondere für Eingaben, `generated-local/`, Buildausgaben, Testinstallationen, Profile/Saves und lokale Konfigurationen. Kein blindes globales `git add .`. Vor Commit/Push den tatsächlich vorgemerkten Diff und die Dateiliste prüfen. `.gitignore` entfernt keine bereits versionierten Dateien und ist keine Zugriffs- oder Geheimhaltungsschranke. Ein versehentlicher Geheimnis- oder Assetupload muss ausdrücklich gemeldet und gezielt bereinigt werden, nicht durch nachträgliches Ignorieren als erledigt gelten. [S14]

### Hauptstand und Checkpoint-Branches

`main` ist nach der ersten Abnahme der zuletzt integrierte, abgenommene Hauptstand. Solange Checkpoint 0 noch nicht abgenommen ist, ist ein reiner Quell-/Dokumentations-Bootstrap ausdrücklich **kein bereits spielgetesteter Modstand**. Die Einrichtung in CP00 darf sich nicht selbst als erfolgreich getestete Basis ausgeben.

Für jede Arbeitsrunde wird vom aktuellen freigegebenen Hauptstand ein eigener Branch erzeugt, beispielsweise `codex/cp00-baseline`, `codex/cp00a-bt-drops`, `codex/cp01-ui`, `codex/cp02-hit-clouds` oder `codex/cp05a-corpses`. Die zusätzliche Aufteilung ist kein Auftrag, mehrere Features parallel zu bauen. Genau ein Feature-Checkpoint ist aktiv. Fehler an diesem Kandidaten werden im selben Arbeitszweig weiter korrigiert; ein Fix für einen bereits integrierten Stand bekommt einen eigenen, klar bezeichneten Reparaturbranch.

Nach dem einmaligen Bootstrap pusht Codex nicht direkt nach `main`, führt keine eigenmächtigen Merges durch und aktiviert kein Auto-Merge. Jeder Checkpoint wird über einen Pull Request mit Umfang, Testnachweisen und noch offenen Nutzerprüfungen vorgeschlagen. **Nach ausdrücklicher Freigabe des konkreten Testkandidaten im Codex-Chat führt Codex selbst den erlaubten PR-Merge aus.** Die inhaltliche Abnahme bleibt beim Nutzer; er muss keinen Merge-Button bedienen und keine Git-Kommandos ausführen. Arbeitsregeln, CI-Prüfungen oder Branchschutz dürfen nicht ohne gesonderte ausdrückliche Freigabe abgeschwächt werden, um eine Änderung durchzubekommen.

Wo verfügbar, `main` mit erforderlichem PR, erfolgreichen Build-/Validierungschecks, deaktivierten Force-Pushes und Löschschutz absichern; keine Codex-Bypass-Ausnahme vorsehen. Tatsächliche Einstellungen dokumentieren und prüfen. Schutzregeln für private Repositories sind tarifabhängig: GitHub dokumentiert sie für Pro, Team und Enterprise; bei GitHub Free nicht als wirksame private Branchsperre voraussetzen. Organisatorische Regeln in `AGENTS.md` sind kein Ersatz für serverseitige Rechtekontrollen. Auch ein mit Besitzerrechten arbeitender lokaler Agent kann je nach Konfiguration weitreichende Rechte besitzen. [S15]

Einen externen Pflichtreview nur verlangen, wenn es dafür tatsächlich einen zweiten berechtigten Reviewer gibt. Bei Nutzung derselben GitHub-Identität für PR-Erstellung und Nutzerkonto keinen unmöglichen Selbstfreigabeprozess einrichten. Die ausdrückliche Nutzerabnahme im Codex-Chat bleibt verbindlich; sie wird nicht durch einen erfolgreichen KI-Code-Review ersetzt. Den belegten Nutzerentscheid dem Kandidaten zuordnen, aber keine eigenständige zweite GitHub-Revieweridentität oder kryptografisch unabhängige Freigabe vortäuschen. Chatfreigabe und serverseitiger Branchschutz sind unterschiedliche Schutzebenen. Ist ein Merge wegen tatsächlicher Regeln blockiert, nicht als Lösung die Regeln eigenmächtig umgehen.

### Kleine Commits und überprüfte Remote-Sicherung

Ein **Commit** sichert einen ausgewählten Quellzustand in Git; ein **Push** überträgt ihn in den Remote-Branch. Eine Kontoverbindung, eine geänderte Datei oder ein Chatabschluss ersetzt keinen dieser Schritte. [S16, S17]

Nach jeder logisch abgeschlossenen, nachvollziehbaren Änderung einen kleinen Commit mit Checkpoint und Zweck anlegen, zum Beispiel `CP01: keep Breakthrough compass square`. Keine Vermischung von UI-Arbeit, Bluteffekten, Neuformatierung großer fremder Dateien und Kampagnenänderungen in einem Sammelcommit. Bei längeren Arbeiten sinnvolle Zwischenstände auf dem Arbeitsbranch sichern, auch wenn der gesamte Checkpoint noch nicht fertig ist; unvollständige Zwischenstände eindeutig als WIP kennzeichnen. Unvollständige WIP-Commits zählen weder als testbarer Checkpoint noch als Nutzerfreigabe.

Nach jedem solchen Sicherungsschritt und spätestens vor einer Übergabe in den freigegebenen Arbeitsbranch pushen, sobald der Zugang verfügbar ist. Den Remote-Branch anschließend frisch abfragen und seine Commit-ID mit dem erwarteten lokalen Stand vergleichen. Nur ein überprüfter Remote-Stand wird als `AUF_GITHUB_GESICHERT` gemeldet. Bei fehlender Verbindung oder Rechten `NUR_LOKAL_GESICHERT` ausweisen, lokalen Commit und ausstehenden Push festhalten und die Arbeit erhalten. Keine Garantie, dass jeder ungespeicherte Zwischenschritt bei einem Absturz wiederherstellbar ist.

Vor Branchwechsel, Merge, Revert oder Paketierung den Arbeitsbaum prüfen. Fremde uncommittete Änderungen weder übernehmen noch verwerfen. Kein `reset --hard`, kein pauschales `clean`, keine erzwungenen Pushes und keine nachträgliche Umdeutung veröffentlichter Tags. Veröffentlichte Feature-Commits werden ohne ausdrücklichen Wartungsauftrag nicht umgeschrieben. Ein sauberer Verlauf entsteht durch passende Commitgrenzen, nicht durch das Löschen misslungener Versuche.

### Testkandidat, Freigabe und Releasezuordnung

Ein lieferbarer Testkandidat entsteht aus einem exakt identifizierten, für den Build relevanten sauberen Quellstand. Der Paketname kann beispielsweise `MOH_Allied_Campaign_CP01_rc01_<short-sha>.zip` lauten. Das ist ein Namensschema, kein schon erzeugter Build. Das Buildmanifest enthält vollständige Quell-/Engine-Commit-IDs, Toolchain- und Abhängigkeitsversionen, Buildoptionen, Asset-/Patchhashes einschließlich der WCR-Dateien und aktiven Module, Version der Konflikt-/Merge-Rezepte, Save-Schema, Waffenpolicyversion sowie Prüfsummen der tatsächlich erzeugten Dateien. Die Build-ID muss im Startprotokoll eindeutig sichtbar sein.

`checkpoints/CPxx/` enthält im Git-Repository **Berichte, Manifestdaten und Testanweisungen, nicht die Build-ZIPs oder privaten Testsavegames**. Große Binärausgaben liegen außerhalb der Quellhistorie. Eigene weitergebbare Mod-/Engine-Builds können als zum Tag gehörende GitHub-Release-Assets archiviert werden; proprietäre lokale Importprodukte werden daraus ausgeschlossen und separat lokal bereitgestellt. GitHub-Releases können Binärpakete enthalten und einem Git-Tag zugeordnet werden. Das von GitHub automatisch erzeugte Quell-ZIP ist kein fertig spielbarer Modbuild. [S18]

Der Bericht nennt mindestens Checkpoint, Kandidatenrevision, Branch, Commit, bestätigten Remote-Status, Paketpfad/-hash, automatisierte Ergebnisse, tatsächliche Spieltests und offene Prüfungen. Zunächst steht der Status auf `BEREIT_ZUM_NUTZERTEST`. Bei Fehlerfeedback wird ausschließlich dieser Checkpoint korrigiert und ein neuer Kandidat erzeugt. Frühere Kandidaten und ihre Berichte nicht unter gleichem Namen überschreiben.

Erst nach ausdrücklicher, dem konkreten Kandidaten zugeordneter Nutzerfreigabe setzt Codex dessen Abnahmestatus auf `ABGENOMMEN` und übernimmt den PR selbst mit den eingeräumten Rechten. Eine erfolgreiche Freigabe ist noch kein Nachweis eines tatsächlich abgeschlossenen Merges: den Übernahmestatus getrennt prüfen und melden. Ein abgenommener Stand bekommt einen nicht umzudeutenden Tag, etwa `cp01-ui-approved-r1`; neue Korrekturen erhalten einen neuen Namen. Für einfache Rücknahmen ist ein sauberer Squash-Merge pro Feature-Checkpoint eine geeignete Vorgabe. Vor einem solchen Merge müssen alle PR-Commits im Testkandidaten enthalten sein. Getesteter Kandidaten-SHA und endgültiger Merge-SHA werden beide dokumentiert; deren relevante Quelldaten müssen übereinstimmen. Nach dem Merge mindestens Build-/Start-Smoke-Test wiederholen. Bei inhaltlichen Mergekonfliktlösungen oder sonstigen Änderungen erneut einen Kandidaten testen, statt die alte Freigabe ungeprüft zu übernehmen.

### Verbindliche Chatfreigabe und technische Übernahme

Bei der Übergabe benennt Codex genau einen Testkandidaten mit verständlicher Kennung, beispielsweise `CP01-r1`. Seine Commit-ID, Paketprüfsumme, PR-Nummer und Testnachweise stehen im technischen Bericht. Ein ausdrückliches „CP01-r1 ist freigegeben, bitte übernehmen“ erlaubt die technische Übernahme dieses Kandidaten; auch eine eindeutige Zustimmung zum unmittelbar zuvor bezeichneten einzigen Kandidaten kann zugeordnet werden. Bloßes Schweigen, ein erfolgreicher Build, „danke“, ein Screenshot ohne Aussage oder ein weiterer Featurewunsch sind keine Abnahme. „Übernehmen“ erlaubt nicht automatisch den Beginn des nächsten Features; „übernehmen und mit Checkpoint 2 weitermachen“ erlaubt beides.

Codex hält die tatsächlich erhaltene Freigabe mit Kandidatenkennung, Commit und Zeitpunkt im PR-Bericht bzw. einem PR-Kommentar fest, ohne dadurch vor der Übernahme den getesteten Quellstand zu verändern. Keine Zustimmung im Namen des Nutzers erfinden. Nicht erreichbare frühere Chats ersetzen keine dokumentierte Freigabe. `STATUS.md` enthält anschließend den korrekten Stand; erforderliche reine Dokumentationsnachträge über den vorgesehenen PR-Weg vornehmen, ohne die Freigabe auf neuen Funktionscode auszudehnen.

Vor dem Merge prüft Codex erneut Ziel-Repo, Hauptstand, aktuellen PR-Kopf, Paketzuordnung, bestandene erforderliche Checks und das Vorliegen der Abnahme. Der freigegebene Kopf darf sich nicht still verändert haben. Die GitHub CLI unterstützt `gh pr merge` und die Bindung an einen erwarteten Kopf-Commit über `--match-head-commit`. Keine Administrator-Umgehung, kein automatisches späteres Mergen und keine Branchlöschung als Nebenwirkung aktivieren. Bei vorhandener Merge-Queue die tatsächliche Semantik vor dem Aufruf prüfen; nicht trotz ausstehender Checks ungewollt Auto-Merge auslösen. Bei inhaltlichen Änderungen seit dem Test einen neuen Kandidaten liefern. [S24]

Nach der Übernahme Remote-Hauptstand, tatsächlichen Merge-Commit und Quellzuordnung prüfen. Build-/Startnachweis wiederholen, den abgenommenen Stand eindeutig kennzeichnen und das Stable-Testziel erst bei erfolgreicher Validierung umstellen. Bei Problemen den bisherigen Stable-Build startbar erhalten. Ein konfliktbehafteter, blockierter oder fehlgeschlagener Merge wird von Codex beschrieben und im erlaubten Rahmen bearbeitet, nicht mit „Merge das selbst“ an den unerfahrenen Nutzer delegiert. Nur eine tatsächlich notwendige Berechtigungs- oder Inhaltsentscheidung erfordert seine Mitwirkung.

### Übergabe ohne Git-Fachkenntnisse

Jede Übergabe an den Nutzer enthält zuerst eine kurze deutsche Zusammenfassung: welcher Teststand vorliegt, was sich geändert hat, welchen bereitgestellten Startweg er nutzen soll, drei bis fünf konkrete Prüfungen und welcher letzte abgenommene Stand weiterhin startbar ist. Technische Commit-IDs, Dateilisten und ausführliche Logs bleiben zusätzlich im Bericht verfügbar, müssen aber nicht vom Nutzer interpretiert werden.

Den Sicherungsstatus getrennt vom Teststatus ausgeben: „auf GitHub gesichert“ nur nach Remote-Prüfung, ansonsten „nur lokal gesichert – GitHub-Übertragung noch offen“. „Zum Testen bereit“ ist nicht „vom Nutzer abgenommen“. Die einfache Testoberfläche bzw. bereitgestellten Startskripte müssen Kandidat und letzten abgenommenen Stand klar unterscheiden; Codex übernimmt deren Einrichtung im jeweiligen erlaubten Umfang. Vorhandene unterstützte Startwege wiederverwenden, statt außerhalb des Checkpoints eine neue Launcher-Anwendung zu entwickeln.

CI beginnt klein: reproduzierbarer Build, Schema-/Manifestprüfungen und gezielte Tests der neuen Funktionen. Nur Tests als bestanden melden, die tatsächlich ausgeführt wurden. Fehlende Spielassets oder Grafikzugriffe ausdrücklich als nicht durchgeführte Gameplay-/Sichttests kennzeichnen. Keine Uploads proprietärer Dateien zur Bequemlichkeit der CI. CI-Konfiguration, Secrets und Runnerzugang eng beschränken; keine unkontrollierte Ausführung fremder PRs auf dem persönlichen Spiel-/Arbeitsrechner.

### Rücknahme von Code UND Modinstallation

Für einen abgelehnten, noch nicht integrierten Kandidaten bleibt der stabile Hauptstand unverändert. Der Teststart wird wieder auf dessen getrennte Installation umgestellt. Den verworfenen Arbeitszweig bzw. seinen nachvollziehbaren Verlauf nicht heimlich löschen.

Eine bereits integrierte Änderung wird bei Bedarf in einem neuen Reparaturbranch über einen nachvollziehbaren Revert bzw. eine gezielte Rücknahme mit erneutem Test rückgängig gemacht. `git revert` erzeugt dafür neue Gegenänderungen, statt alte gemeinsame Geschichte zu entfernen. Abhängigkeiten zwischen Checkpoints vorher prüfen: Beispielsweise setzt Leichenbeschuss das zuvor entwickelte Treffer-/Wundsystem voraus. Ein isolierter Revert ist nicht automatisch konfliktfrei oder funktional ausreichend. Keine Zusage, jedes beliebige Feature lasse sich trotz späterer Abhängigkeiten mit einem Klick entfernen. [S19]

Für den sofortigen Spieltest stets zwei getrennte Ziele erhalten: **letzter abgenommener Build** und **aktueller Kandidat**. Die Entwicklungsdateien selbst sind kein dauerhaft stabiler Spielordner. Auf einen alten Stand nicht lediglich dessen EXE über neuere PK3-/Shader-/Skriptdateien kopieren. Entweder eine frische versionsgebundene Mod-Testinstallation verwenden oder anhand eines Besitz-/Dateimanifests ausschließlich modverwaltete Dateien vollständig ersetzen bzw. entfernen. Veraltete Overrides dürfen nicht aktiv liegen bleiben; Originaldaten und fremde Mods niemals pauschal löschen.

Vor einer Save-/Profil-/Kampagnenmigration eine getrennte lokale Sicherung anlegen. Ein Quellcode-Revert stellt weder Spielstände noch den Kampagnenfortschritt, lokale Einstellungen oder importierte Dateien zurück. Ältere Builds nur mit ausdrücklich kompatiblen Saves bzw. einer zugehörigen gesicherten Profilkopie starten. Save-/Asset-Migrationen versionieren; bei fehlender Abwärtskompatibilität einen klaren Wiederherstellungsweg anbieten, ohne die einzige vorhandene Kopie zu überschreiben.

Abgenommene Quellstände, private Eingaben, verwendete lokale Importprodukte, Profile und Test-/Releasepakete zusätzlich unabhängig vom laufenden Arbeitsordner sichern. Die gesicherte Eingabekopie und Hashreferenzen müssen für spätere Rebuilds erhalten bleiben. Eine zweite Sicherung soll nicht durch dieselben normalen Codex-Schreibrechte mitgelöscht werden können. Remote-Git allein deckt weder ausgeschlossene Daten noch sämtliche externe Build- und Testartefakte ab.

### Projektdokumentation statt Chatabhängigkeit

Im Repository liegen eine **kurze `AGENTS.md`** mit diesen Kernregeln, der vollständige Plan als `PLAN.md` sowie `STATUS.md` mit aktivem Checkpoint, letzter Abnahme, Branch/Commit, offenen Fehlern und nächstem freigegebenem Schritt. Codex liest `AGENTS.md` als Projektanweisung; der lange Plan gehört nicht vollständig in diese Datei. Zu Arbeitsbeginn die wirksamen Anweisungen und die einschlägigen Planabschnitte ausdrücklich prüfen. `AGENTS.md` ist eine Arbeitsanweisung, keine technisch unveränderliche Berechtigungssperre. [S20]

Codex pflegt diese Dateien selbst. In `AGENTS.md` steht ausdrücklich: „Der Nutzer verwaltet GitHub nicht selbst. Übernimm Routine-Git-/GitHub-Arbeit und technische Merges nach konkreter Chatfreigabe; verlange nur unvermeidbare Anmeldung, Sicherheitsbestätigung und inhaltliche Abnahme.“ Absprachen aus einem Chat werden mit Bezug auf die konkrete Nutzerfreigabe in diese Dokumentation übernommen. Eine neue Codex-Sitzung darf keinen abgenommenen Stand aus Erinnerung neu erfinden. Für jeden Checkpoint einen PR bzw. optional ein zugehöriges Issue mit denselben Abnahmekriterien führen; kein zusätzliches komplexes Projektmanagementsystem ist Voraussetzung.

Ergänze als kurze WCR-Kernregel in `AGENTS.md`: „War Chest Restored ist Teil der übernommenen Inhaltsbasis. Nicht entfernen, nicht neu herunterladen oder still aktualisieren; neue Features gezielt zusammenführen und bestehende Inhalte erhalten.“ `STATUS.md` verweist auf den aktiven WCR-Fingerprint, das Inhaltsprofil pro Spiel und offene Kompatibilitätsfälle. Pflege diese Angaben selbst; der Nutzer muss keine PK3-Reihenfolgen oder Skript-Diffs manuell verwalten.

### Zusätzliche Abnahme in Checkpoint 0

Vor Abschluss der Ausgangsbasis nachweisen: Original-/Importdaten sind korrekt ausgeschlossen; der erlaubte Remote-Arbeitsbranch enthält den erwarteten Commit; ein frischer separater Checkout erzeugt mit dokumentierten lokalen Eingaben denselben vorgesehenen Funktionsstand; und der Wechsel von einem Testkandidaten zurück zur gesicherten Basis hinterlässt keine alten Moddateien oder überschriebenen Profile. Diese Wiederherstellungsprobe erfolgt ausschließlich in temporären Testordnern. Kein echter Eingabedatensatz oder funktionierender Hauptstand wird dafür zerstört. Byte-identische Binärreproduzierbarkeit nur behaupten, wenn sie tatsächlich nachgewiesen wurde.

Die Einrichtungsabnahme umfasst außerdem: tatsächlicher Eigentümer und private Sichtbarkeit geprüft, verwendete Zugangsreichweite benannt, Codex kann den vorgesehenen Arbeitsbranch selbst sichern und den PR vorbereiten, die Chatabnahme ist an einen Kandidaten gebunden und es besteht kein unmöglicher Selbstreview-Zwang. Bei der ersten tatsächlichen Nutzerfreigabe wird auch die erlaubte technische Übernahme durch Codex überprüft; diesen späteren Schritt vorher nicht als schon durchgeführt abhaken.

Bei fehlender GitHub-Freigabe darf die lokale Basis vorgelegt werden, aber der GitHub-Teil bleibt `NICHT_EINGERICHTET` bzw. `BLOCKIERT`. Nicht ohne Hinweis auf eine gleichwertige manuelle ZIP-Historie ausweichen. Bereits vorhandene stabile Arbeit zuerst inventarisieren und als Baseline sichern; nicht wegen der Einführung von Git erneut implementieren.

## 4. Checkpoint 0 – Reproduzierbare, geschützte Ausgangsbasis mit War Chest Restored

**Ergebnis:** Alle drei Spiele starten mit der gewählten Engine-Basis und der übernommenen War-Chest-Restored-Fassung; Originalinstallation, WCR-Eingaben und bisherige Spielstände bleiben unberührt. Zusätzlich ist der Workflow aus Abschnitt 3.1 eingerichtet und geprüft, soweit der Nutzer Ziel-Repository und Zugriff freigegeben hat; offene Zugriffs-/Schutzgrenzen sind ausdrücklich ausgewiesen.

Inventarisiere die Allied-Assault-Installation einschließlich beider Erweiterungen. Erfasse Dateiversionen, Sprache, vorhandene Patches, PK3-Archive, bestehende Mods, ausführbare Dateien und relevante Suchpfade. Prüfe insbesondere, ob `mainta` und `maintt` tatsächlich vorhanden und vollständig sind. Ein fehlendes Add-on ist eine konkrete Blockade seiner Integration, kein Anlass, Originaldaten anderweitig zu beschaffen.

**WCR-Bestandsaufnahme und Übernahme:** Untersuche die vorhandene Mod anhand ihrer lokalen Readme, Changelogs, Pakete und losen Dateien. Erstelle das Manifest nach Abschnitt 1.4 und einen vor Änderungen gesicherten Vergleichsstand. Welche WCR-Module sind wirklich aktiv, welche nur beigelegt? Ist eine OpenMoHAA-Anpassung bereits installiert oder lokal verfügbar? Stammt eine Abweichung aus WCR, einem Hotfix oder einer anderen Mod? Diese Fragen soweit durch Dateien belegbar selbst auflösen; keine Versionsnummer aus der Moddb-Seite in den lokalen Bericht übernehmen.

Übernimm die effektive WCR-Inhaltsbasis in einen separaten, reproduzierbaren Testaufbau und prüfe die tatsächlich geladenen Ressourcen, nicht nur die Dateinamen. Noch keine eigenen UI-/Blutfeatures hinzufügen. Fehlende WCR-Daten oder unvollständige Teilupdates konkret als `WCR_BASIS_FEHLT`, `WCR_BASIS_UNVOLLSTAENDIG` bzw. ungeklärte Herkunft als `WCR_BASIS_UNGEKLAERT` dokumentieren. Sichere Inventur und Repoeinrichtung bleiben möglich, die vollständige CP0-Abnahme aber offen, solange die geforderte WCR-Basis nicht nachgewiesen ist. Nicht still mit Vanilla weiterarbeiten.

Erfasse auch das vom Nutzer angekündigte Patch-ZIP im bereitgestellten MOHAA-Archiv bzw. dessen zugänglichem Verzeichnisbaum. Prüfe gegebenenfalls die Dateiliste des äußeren MOHAA-Archivs; nicht das gesamte Laufwerk durchsuchen. Das ZIP in Checkpoint 0 nur identifizieren und unverändert inventarisieren, noch nicht aktivieren. Fehlt es noch, den konkreten Befund für 0a notieren; daraus folgt kein Downloadauftrag und keine Blockade der übrigen Basiseinrichtung. Prüfe außerdem, ob der Breakthrough-Drop-Patch oder andere Drop-Mods bereits installiert sind. Erfasse Paketprüfsummen, betroffene virtuelle Ressourcenpfade und die tatsächliche Ladepriorität, soweit schon feststellbar. Verändere die bestehende Nutzerinstallation nicht: Für den Drop-Vergleich nutze einen isolierten Datenaufbau mit der übernommenen WCR-Basis, in dem nur der zusätzliche Ammo-and-Health-Drops-Patch bzw. fremde Drop-Overrides gezielt ausgeklammert sind. WCR nicht insgesamt entfernen. Erfasse bereits in WCR wirksame Dropänderungen als Bestand; deren etwaige Gleichwertigkeit zum Nutzerpatch wird in 0a geprüft. Sichere diese BT-Drop-Referenzfälle einschließlich Schwierigkeitsgrad, Gegnerart, Killfolge und tatsächlich erzeugten Gegenständen. Eine zusätzliche reine Vanilla-Referenz ist nur bei lokal verfügbaren, belegten Originaldaten zulässig und ersetzt nicht die WCR-Referenz. Hier nur inventarisieren; der zusätzliche Patch-Merge erfolgt erst in 0a.

Inventarisiere die Max-Payne-1-Installation und unterscheide Originalarchive von eventuell installierten Blut-/Grafikmods. Prüfe, ob geeignete lokale Extraktionswerkzeuge verfügbar sind. RASMaker ist ein möglicher Werkzeugkandidat, dessen konkrete Version und Aufrufsyntax zunächst zu prüfen sind. Ein veröffentlichtes MP1-Modprojekt dokumentiert seine Verwendung zusammen mit `rl.dll`. [S7] Noch keine Blutassets in die Mod einbauen.

Prüfe, ob die beiden Wundtexturen des Nutzers bereits vorliegen. Wenn nicht, markiere Checkpoint 4, 5 und 5a als assetabhängig. Frühere Checkpoints bleiben bearbeitbar. Keine beliebigen Ersatztexturen als fertige Nutzerassets ausgeben.

Baue den festgelegten OpenMoHAA-Stand und richte einen gemeinsamen Mod-Startweg sowie einen isolierten Testprofilpfad ein. Separate Startprofile für AA/SH/BT sind in diesem Basisschritt zulässig, aber noch keine Kampagnenzusammenführung. `fs_homepath` ist der dokumentierte Ansatz für eigene beschreibbare Datenpfade. [S2]

Erstelle reproduzierbare Testszenen bzw. Testsavegames in allen drei Spielen: Menü/Optionen, ein gewöhnliches Gefecht, eine skriptintensive Situation und ein relevanter Levelübergang. Erfasse Referenzscreenshots und Frametimes. Speichern/Laden und Rückkehr zum Menü müssen in allen Kontexten funktionieren.

**Zusätzliche WCR-Basisprüfungen:** Wähle anhand des lokalen Changelogs pro Titel sichtbare restaurierte Inhalte und mindestens einen anspruchsvollen Skriptablauf. Prüfe vorhandene Optionsfunktionen, Dialog-/Untertitelabläufe, Modelle/Animationen, Briefingstart und Save/Load. Ergänze einen MG42-Benutzungs-/Fortschrittstest in AA; `m1l1` und `m2l1` sind durch den Autorenhinweis begründete Kandidaten, deren tatsächliche lokale Skripte geprüft werden müssen. [S29] Keine Erfolgsflags nur setzen, um eine blockierte Mission zu überspringen.

Prüfe außerdem die in der lokalen WCR-Fassung vorhandene erweiterte BT-Endsequenz bis zum echten Abschluss und sichere dafür eine wiederholbare Referenz. Fehlt sie, den Bestand gegen das lokale Changelog erklären; nicht ungefragt eine andere WCR-Version beschaffen. Alle automatisierten Prüfungen und tatsächlich durchgespielten Passagen getrennt protokollieren. Ein Startbildschirm mit WCR-Logo oder ein vorhandenes PK3 ist noch keine Inhaltsabnahme.

**Nutzerentscheidung vom 14.10.2026 für CP00-r4:** Den vollständigen BT-Finaltest einschließlich Flucht, Outro/Abspann und Timerfehlschlag auf ausdrücklichen Wunsch überspringen. Dieser Test ist damit für die aktuelle CP0-Runde abgewählt, nicht bestanden. Vorhandene Start-/Save-Nachweise und bekannte Skriptwarnungen bleiben getrennt dokumentiert. Die Entscheidung erteilt keine vollständige CP0-Abnahme, keinen Merge und keine CP0a-Freigabe.

Ergänze Referenzfälle für Gegner vor einer Wand, seitlich liegende bzw. auf dem Rücken liegende Leichen und bereits platzierte menschliche 3D-Leichen. Dokumentiere das unveränderte Treffer-/Kollisionsverhalten, das Verschwinden von Leichen und die bisherigen Statistik-/Skriptreaktionen. Erfasse Pistolen, MPs, Gewehre und MGs anhand der tatsächlichen Waffen-IDs. In diesem Schritt noch keine Leichenreaktionen implementieren.

**Abnahme:** Nutzer startet AA, Spearhead und Breakthrough mit WCR über die bereitgestellten Testwege, lädt je einen Teststand, speichert/lädt und kehrt zum Menü zurück. Gib insgesamt drei bis fünf konkrete Nutzerprüfschritte, in denen die WCR-Erkennung und ein geeigneter restaurierter Ablauf sichtbar nachprüfbar sind. Die übrigen technischen und gezielten Spieltests gehören mit ehrlichem Status in den Bericht; noch offene WCR-Fälle nicht als bestanden markieren. Dokumentiere bereits im übernommenen Bestand vorhandene Fehler getrennt von Engine-Kompatibilitäts- und Allied-Campaign-Regressionsfehlern. Die Wiederherstellungsprobe muss die WCR-Basis erhalten.

**Danach stoppen.**

## 4a. Checkpoint 0a – Breakthrough: Ammo and Health Drops

**Ergebnis:** Der vom Nutzer ausgewählte Drop-Patch ist mit der WCR-Basis zusammengeführt, in Breakthrough tatsächlich wirksam, auf diesen Spielkontext begrenzt und reproduzierbar integriert. Der Nutzer bekommt einen startbaren Stand mit der vollständigen Drop-Anpassung, noch ohne neue UI-, Blut- oder Kampagnenfeatures dieses Arbeitsschritts. Vorhandene abgenommene Features bleiben bei einer nachträglichen Integration erhalten.

### Originalpaket untersuchen und festlegen

**Lokales ZIP statt Download:** Verwende das vom Nutzer bereitgestellte Patch-ZIP aus dem MOHAA-Archiv. Kein Abruf der Downloadseite, kein Ausweichen auf Mirrors und keine automatische Suche nach einer neueren oder anderen Patchversion. Durchsuche nur den übergebenen MOHAA-Bestand und gegebenenfalls die Inhaltsliste seines äußeren Archivs. Identifiziere das Patch-ZIP anhand von Paketinhalt, Readme und Zuordnung zum gewünschten Ammo-and-Health-Drops-Patch; verlasse dich nicht ausschließlich auf den Dateinamen. Bei mehreren unterschiedlichen Kandidaten nicht willkürlich die vermeintlich neueste Datei wählen.

Kopiere bzw. extrahiere das gefundene ZIP in einen separaten lokalen Staging-Bereich und untersuche dort seinen Inhalt. Das äußere MOHAA-Archiv, das ursprüngliche Patch-ZIP und die installierten Originaldateien bleiben unverändert. Ein enthaltenes PK3 getrennt erkennen und untersuchen; ein Transport-ZIP nicht durch bloßes Umbenennen als spielbereites PK3 behandeln. Sichere Extraktion verwenden: absolute Pfade, Pfadausbrüche über `..` und Verknüpfungen aus dem Zielverzeichnis heraus nicht zulassen; verschachtelte Archive nicht unbegrenzt rekursiv entpacken. Keine beigefügten Programme automatisch ausführen.

Prüfe Readme, enthaltene Hinweise, tatsächliche Autorenschaft, Version/Datum soweit ausgewiesen und Prüfsummen. Nicht den Uploader automatisch als ursprünglichen Autor angeben. Dokumentiere den relativen Fundort, bei Verschachtelung äußeres Archiv und inneren Dateipfad, ZIP-Hash sowie Hashes der tatsächlich integrierten Pakete. Die vorhandene Webadresse bleibt reine Herkunftsreferenz. Eine bereits installierte Patchkopie auf Gleichheit oder Abweichungen prüfen, aber nicht stillschweigend anstelle des vom Nutzer gelieferten ZIP als neue Referenz verwenden.

Fehlt das angekündigte lokale ZIP, markiere diesen Checkpoint als `BLOCKIERT: PATCHPAKET_FEHLT`; bei beschädigtem bzw. nicht lesbarem Archiv als `BLOCKIERT: PATCHPAKET_UNLESBAR`, bei nicht eindeutig zuordenbaren unterschiedlichen Kandidaten als `BLOCKIERT: PATCHPAKET_UNEINDEUTIG`. Dokumentiere die durchsuchten bereitgestellten Pfade, konkrete Kandidaten und die bereits mögliche Bestands-/Konfliktprüfung. Behalte den letzten startbaren Stand und benenne die tatsächlich noch benötigte lokale Datei oder Auswahl. Keinen Ersatzdownload versuchen. Kein erfundenes Nachbauen aus dem Titel als Integration genau dieses Patches ausgeben; keine fremde Sammelmod als stillen Ersatz einsetzen.

Vergleiche **jede tatsächlich enthaltene Änderung** mit den entsprechenden Dateien der lokalen Breakthrough-Version und den bisherigen Mod-Overrides. Dokumentiere geänderte Funktionen/Threads, Bedingungen, Begrenzungen, Zufallsaufrufe, Itemauswahl und gegebenenfalls Unterschiede nach Schwierigkeit. Erzeuge einen nachvollziehbaren semantischen Diff. Nicht vorab annehmen, dass nur eine Datei, ein bestimmter Zähler oder eine feste Wahrscheinlichkeit betroffen ist. Beigaben außerhalb des Drop-Zwecks nicht unbesehen mitinstallieren.

Maßgeblich ist das Verhalten des untersuchten Originalpatches. Keine frei gewählten Prozentwerte oder garantierten Drops aus der Beschreibung ableiten. Kein Zwang, dass jeder getötete Gegner beide Gegenstände fallen lässt. Von dem Patch nicht geänderte Itemmengen, Ausschlüsse und Schwierigkeitsregeln bleiben bestehen.

### Eine wirksame Integration, ausschließlich in Breakthrough

Prüfe zuerst, ob das geprüfte PK3 mit dem festgelegten Engine-Stand direkt funktioniert. Bei Überschneidungen mit Modskripten die gezielten Änderungen zusammenführen und die Konfliktauflösung protokollieren, statt komplette Dateien blind durch die zuletzt kopierte Fassung zu ersetzen. Bei nötiger Portierung bleibt das Originalpaket die Referenz; jede unvermeidbare Verhaltensabweichung offen ausweisen. Ein bloß vorhandenes Archiv ist kein Funktionsnachweis.

Die Integration wird als Breakthrough-spezifischer Override bzw. gleichwertige, explizit kontextgebundene Skriptlogik geführt. Keine ungeprüfte Ablage in einem global aktiven gemeinsamen Ressourcenpaket. Es darf nur eine wirksame Implementierung derselben Dropänderung existieren; bereits vorhandene Pakete/Overrides über Inhalt und Ressourcenpfad erkennen, nicht allein über den Archivnamen. Die tatsächliche Herkunft der zur Laufzeit verwendeten Skripte im Testprotokoll nachweisen.

**Pflichtvergleich mit WCR:** Prüfe die tatsächlichen Todes-/Drop-Aufrufketten, globalen KI-Skripte und Itemdefinitionen gegen die in CP0 übernommene Fassung. Ob sich Dateien überschneiden oder derselbe Drop-Limiter bereits geändert wurde, muss aus dem lokalen Diff hervorgehen; hier wird kein Konflikt vorweg als bewiesen behauptet. Ist die gewünschte Änderung schon nachweislich gleichwertig wirksam, keine zweite Dropauswertung oder zusätzliche Multiplikation ergänzen. Dokumentiere die Gleichwertigkeit zum gelieferten Nutzerpatch und verwende genau einen aktiven Pfad.

Bei nicht identischen Änderungen nur die geprüfte Dropregel in die wirksame WCR-Logik einarbeiten. Restaurierungen, Missions-/NPC-Zustände, Itemdarstellung, Aufnahmesounds und andere nicht betroffene WCR-Regeln bleiben erhalten. Eine komplette ältere `ai.scr` oder andere Patchdatei über eine umfassendere WCR-Fassung zu legen, ist ohne funktionsgenauen Merge unzulässig. Originalreferenzen, soweit verfügbar, nur für den Diff heranziehen. Vorher/nachher geladene Skripte sowie tatsächlich erzeugte und aufgenommene Item-Instanzen nachweisen; Optik und tatsächliche Heil-/Munitionswirkung getrennt prüfen.

Im BT-Modprofil ist die Patchwirkung standardmäßig aktiv und kein vom Nutzer zusätzlich zu installierender Nachschritt. Ein isoliertes ungepatchtes A/B-Testprofil ist erlaubt, aber nicht der Auslieferungsstandard. Ein zusätzlicher Menüschalter ist für diesen Auftrag nicht erforderlich. Die Bluteffekt-Schalter dürfen die Patchwirkung nicht verändern.

AA und Spearhead behalten ihre Drop-Logik. Gemeinsame Modell-/Skriptnamen oder der Standort der Spieldaten sind kein ausreichendes Kriterium für die Aktivierung; maßgeblich ist der verlässlich eingerichtete Missions-/Spielkontext. Bei 0a getrennte Starts prüfen; die dynamischen Wechsel werden zusätzlich in 6 und 7 abgenommen.

### Tod, Leichen und Spielstände

Die vom Patch geänderte Dropauswertung gehört ausschließlich zum vorgesehenen echten Todes-/Dropereignis. Ein neuer visueller Treffer auf einen bereits toten Körper darf weder die Dropfunktion noch deren Zufallsentscheidung erneut auslösen. Der ursprüngliche Todesvorgang darf weiterhin die vom Patch vorgesehenen Gegenstände erzeugen; auch wenn mehrere Itemtypen zulässig sind, wird ihre Ausgabe nicht willkürlich auf ein einziges Item reduziert. Verboten ist das doppelte Ausführen derselben bereits abgearbeiteten Dropentscheidung.

Im Testreport Ereignis, NPC-/Corpse-Instanz, Zahl der Dropauswertungen und erzeugte Item-Instanzen nachvollziehbar zuordnen. Bereits korrekt funktionierende Engine-/Skriptzustände weiterverwenden; nur bei einem belegten Bedarf eine instanzgebundene, speicherbare Deduplizierung ergänzen. Neu gespawnte echte Gegner mit wiederverwendeter Entity-Nummer müssen ihre eigenen regulären Dropentscheidungen behalten.

Speichern/Laden darf abgearbeitete Tode nicht erneut auswerten, neue Drops rückwirkend an alte Leichen hängen oder vorhandene Gegenstände verdoppeln. Bereits ausgegebene und noch nicht aufgesammelte Gegenstände bleiben entsprechend dem ursprünglichen Save-System erhalten; ausstehende legitime Dropvorgänge werden korrekt und höchstens einmal fortgeführt. Keine alten Tötungen beim Laden erneut abspielen.

Patch-/Integrationsversion und BT-Kontext gehören in die Mod-Save-Metadaten. Für ältere Mod-Saves Kompatibilität testen: Sind gespeicherte Skriptzustände nicht sicher migrierbar, einen nachvollziehbaren Neustart des betroffenen Missionsabschnitts verlangen, statt den Save stillschweigend umzuschreiben. Vorhandenes Inventar, bereits ausgegebene Items und Wunden nicht neu berechnen. Originalspielstände bleiben unberührt.

### Abnahme – fünf konkrete Spieltests plus technische Nachweise

1. **Patchwirkung:** Eine definierte BT-Killfolge in der WCR-Basis ohne zusätzlichen 0a-Merge, einer Originalpatch-Referenz soweit ausführbar und dem zusammengeführten WCR+0a-Stand vergleichen. Itemtypen, Mengen, ausbleibende Drops und die aus dem Diff ermittelten Begrenzungen prüfen. Bei Zufallsentscheidungen reproduzierbare Testwerte bzw. ausreichend viele protokollierte Wiederholungen verwenden; wenige zufällige Kills belegen keine Dropquote. Einschränkungen einer nicht ausführbaren Originalengine-Referenz ausdrücklich nennen.
2. **Abdeckung:** Repräsentative Gefechte aus allen BT-Kampagnenabschnitten, relevante Gegner-/Skriptpfade und alle angebotenen Schwierigkeitsgrade prüfen. Aufgenommene Munition und Heilung müssen real wirksam sein. Die Prüfung umfasst genug aufeinanderfolgende Todesfälle und Levelübergänge, um die im Diff ermittelte frühere Begrenzung tatsächlich zu erreichen. Keine neue pauschale Vereinfachung von Schaden oder KI.
3. **Save/Load:** Vor einem Kill, nach einem Drop und nach dem Aufsammeln speichern/laden. Itemzustände bleiben korrekt; kein erneutes Würfeln oder Duplizieren bereits abgeschlossener Drops. Weitere echte Kills funktionieren. Einen geeigneten älteren Mod-Save prüfen oder die konkrete Grenze seiner Kompatibilität dokumentieren.
4. **Keine Fremdwirkung:** AA und SH mit identischem Referenzaufbau starten. Ihre Skriptherkunft, Dropbedingungen und Itemmengen bleiben unverändert. Der BT-Stand bleibt nach Neustart aktiv, ohne dass ein Nutzer das Paket manuell nachkopieren muss.
5. **Leichen-/Doppelereignisprüfung:** Einen Gegner töten und anschließend wiederholt dessen Leiche beschießen. Keine zusätzlichen Munitions-, Heilungs- oder Waffen-/Inventardrops durch diese Treffer, kein erneuter Kill. Vor Implementierung von 5a ist dies eine Negativprüfung; sind Leicheneffekte bereits vorhanden, müssen dabei die gewünschten Bluteffekte sichtbar bleiben. Nicht vorhandene Leichenbluteffekte in einem frühen 0a-Stand nicht als fertig ausgeben.

Zusätzlicher technischer Nachweis: Skriptkompatibilität am festgelegten OpenMoHAA-Commit, aktive Ressourcenherkunft, keine doppelte Integration, überprüfter Diff zum gewählten Patch sowie reproduzierbare Neuinstallation und Rücknahme im isolierten Testprofil. Den Patchimport mit gesperrtem Netzwerk aus dem lokalen ZIP testen, einschließlich ZIP im äußeren MOHAA-Archiv und bereits zugänglicher ZIP-Datei. Hashes der unveränderten Eingabearchive vor/nach dem Import vergleichen. Ein erneuter Import derselben Quelle darf keine zweite wirksame Patchkopie erzeugen; fehlende oder unlesbare Quellen dürfen weder Teilergebnisse aktivieren noch einen Download auslösen. Dieser Offline-Nachweis betrifft die Patchbereitstellung und -integration, nicht das erstmalige Beschaffen der Engine oder Toolchain. Der spätere Nachweis beim gemeinsamen Missionswechsel bleibt ausdrücklich Teil von 6/7, keine vorgezogene Kampagnenabnahme.

Liefere den kumulativen Teststand, Patch-/Integrationsmanifest, Konfliktbericht und konkrete Nutzer-Testanleitung. Drittanbieterhinweise erhalten. Der lokale ZIP-Import ist Bestandteil dieses Checkpoints, kein manueller Installationsnachschritt für den Nutzer. Eine Mitverteilung der Patchdateien oder zusammengeführter Fremdskripte über GitHub/Releasepakete nicht ohne geprüfte Bedingungen voraussetzen; der lokale Importpfad bleibt unabhängig davon erhalten. Diese Paketierungsentscheidung darf nicht dazu führen, dass die lokale BT-Mod ohne den gewünschten Patch als vollständig ausgeliefert wird.

**Danach stoppen.**

## 5. Checkpoint 1 – Vollständige UI-/HUD-Skalierung

**Ergebnis:** Alle drei Spiele lassen sich in hoher Auflösung und unterschiedlichen Seitenverhältnissen vollständig bedienen; der Breakthrough-Kompass bleibt unverzerrt.

**Auf WCR aufbauen:** Bestandsmenüs und ihre tatsächlich verwendeten CVars/Befehle aus CP0 übernehmen. Vorhandene funktionierende Einstellungen bleiben erreichbar und wirksam. Identische Optionen nicht als zweite, widersprüchliche Bedienelemente neu anlegen. Eine vorhandene WCR-Skalierung zunächst messen und nur fehlende/fehlerhafte Pfade ergänzen; keine doppelten Faktoren oder zwei gegeneinander arbeitende Seitenverhältniskorrekturen. Unsere Größenregler sollen vorhandene Mechanismen kontrolliert erweitern, nicht Auflösung/FOV zur Ersatz-UI-Skalierung missbrauchen. Abgenommene WCR-Funktionen wie Briefing-/Bonuszugänge nicht durch eine auf Vanilla beruhende Menüdatei verlieren.

Zusätzliche Abnahme: Für jeden tatsächlich vorhandenen WCR-Optionspunkt aus CP0 Bedienung, gespeicherten Wert und Wirkung vor/nach dem Umbau vergleichen. OpenMoHAA-spezifische Optionen, sofern Teil der aktiven lokalen Basis, ebenfalls prüfen. Ein optisch großes Menü mit verlorenen Funktionen ist kein bestandener Checkpoint.

### Gemeinsames Koordinatenmodell

Inventarisiere zunächst alle UI-Pfade: native Menüs, Optionsdialoge, HUD, scriptgesteuerte Anzeigen, Missionsziele, Untertitel, Speichern/Laden, Ladebildschirme, Mauszeiger, Tooltip-/Popup-Elemente sowie Zielfernrohr/Fernglas-Overlays. Bestehende Engine-Skalierung und Mod-Skalierung dürfen nicht doppelt angewendet werden. [S3]

Führe eine konsistente Umrechnung von logischem Layout in tatsächliche Ausgabepixel ein. Für proportionales 2D-Material gilt ein einheitlicher Faktor in X und Y. Trenne die Größe eines Elements von seiner Verankerung am linken/rechten/oberen/unteren Rand oder in einem begrenzten HUD-Sicherheitsbereich.

Eine klassische 4:3-Menüfläche darf zentriert proportional skaliert werden; zusätzlicher Breitbildraum kann gestalterisch gefüllt werden. Das Gameplay selbst darf durch den UI-Fix weder gestreckt noch auf 4:3 beschränkt werden. Große Widescreen-Flächen dürfen kein Anlass sein, sämtliche Bedienelemente extrem weit an die Außenränder zu verteilen.

Nutze eine automatisch zur Ausgabehöhe bzw. zum verfügbaren Layout passende Grundgröße plus gespeicherte Nutzerfaktoren. Vorgesehene Optionen: automatische Skalierung, Menü-/Schriftgröße, HUD-Größe und HUD-Sicherheitsbereich. Die genauen internen CVar-Namen sind neu zu definieren, keine behaupteten vorhandenen Engineoptionen.

Fenstergröße, tatsächliche Drawable-/Framebuffer-Größe und Betriebssystem-DPI-Skalierung sauber unterscheiden. DPI-Faktoren nicht zusätzlich multiplizieren, wenn sie bereits im Ausgabemaß enthalten sind. Rendering, Clipping, Mausposition und Klickflächen müssen dieselbe Transformation bzw. deren Inverse verwenden. Nach Auflösungswechsel, Fenstergrößenwechsel und Alt-Tab alle betroffenen Größen aktualisieren.

### Darstellung

Beim Kompass müssen Rahmen, Ziffernblatt, Nadel und Zielmarkierung dasselbe unverzerrte Koordinatensystem und denselben Rotationsmittelpunkt verwenden. Nicht nur das Hintergrundbild schmaler ziehen.

Schriftgrößen müssen mit Textmessung, Zeilenabstand und Umbruch übereinstimmen. Prüfe vorhandene Fontatlanten und ihre Filterung; ergänze bei Bedarf passende höher aufgelöste Atlanten bzw. einen geeigneten Fontpfad, ohne wahllos das Originaldesign auszutauschen. Lange deutsche Beschriftungen, Umlaute, mehrzeilige Ziele und Untertitel dürfen weder abgeschnitten noch unlesbar werden.

Kreise in Fadenkreuzen und Optikmasken bleiben kreisförmig. Schwarze Masken müssen außerhalb des Sichtbereichs lückenlos abdecken, ohne das eigentliche Bild zu verzerren. Falls ein anderer Skalierungspfad nötig ist, explizit klassifizieren statt sämtliche DrawStretchPic-Aufrufe global umzubiegen.

### Abnahme

Prüfe mindestens 1280×960 und 2560×1920 (4:3), 1920×1200 (16:10), 1920×1080, 2560×1440 und 3840×2160 (16:9), 3440×1440 und 5120×1440 (Ultrawide). Fenster/Vollbild und Windows-Skalierung 100 %, 150 % und 200 % in repräsentativen Kombinationen prüfen. Nicht verfügbare reale Monitorformate dürfen durch entsprechend große Fenster getestet, aber nicht als echter Monitortest bezeichnet werden.

Im Testbericht stehen normierte HUD-Größen, die Rundheit des Kompasses, unveränderte Zentrierung, korrektes Maus-Hit-Testing und Screenshots aller drei Kontexte. Die eingestellten Größen bleiben nach Neustart und Kontextwechsel erhalten.

**Danach stoppen.**

## 6. Checkpoint 2 – Ausschließlich rote Gegner-Trefferwölkchen

**Ergebnis:** Die vorhandenen kleinen Trefferwölkchen an Gegnern erscheinen rot; sämtliche anderen Effekte behalten ihr bisheriges Aussehen.

Verfolge den tatsächlichen Effektpfad vom bestätigten Körpertreffer zum verwendeten Emitter/Material. Beginne bei den in S4 genannten Human-Uniform-Effekten, erfasse aber auch weitere tatsächlich verwendete Körper-/Uniformvarianten. Geteilte Materialien gegebenenfalls für Körpertreffer duplizieren, statt eine globale Rauchtextur einzufärben.

Erhalte zunächst Größe, Bewegung und zeitlichen Verlauf des ursprünglichen Wölkchens. Passe Farbe und erforderlichenfalls das Blendverhalten so an, dass es nach rotem Blutnebel und nicht nach selbstleuchtendem pinkem Rauch aussieht. Weltstaub, Mündungsrauch, Rauchgranaten, Fahrzeugtreffer und Explosionen sind nicht Teil dieser Umfärbung.

Verfolge den tatsächlich mit WCR aktiven Trefferpfad einschließlich seiner Modelle, Materialien und Skriptaufrufe. Nur den eigenen roten Trefferzweig ersetzen/erweitern; WCR-Effekte für andere Oberflächen und NPC-Verhalten erhalten. Doppelte Wolken durch parallelen Original-/WCR-/Allied-Campaign-Aufruf ausdrücklich prüfen. „Funktion aus“ stellt das übernommene WCR-Ausgangsverhalten her, nicht ungefragt einen Vanilla-Ersatz.

Es gibt genau einen Treffernebel pro vorgesehenem Trefferereignis. Der später ergänzte Tropfeneffekt darf diesen nicht versehentlich ein zweites Mal erzeugen. Die Funktion bekommt einen gespeicherten Ein-/Aus-Schalter im Mod-Optionsbereich.

Halte den visuellen Effektaufruf von der Schadens-/Todesauswertung getrennt. Die spätere Leichenunterstützung muss ihn ohne erneutes Töten des Ziels nutzen können. Neue Schüsse auf Leichen werden erst in Checkpoint 5a fertig integriert; in Checkpoint 2 ist weder ein zweites Treffernebel-System noch eine Wiederbelebung von Leichen zulässig.

**Abnahme:** In AA, SH und BT mit mehreren Waffen Gegner treffen und direkt danach dieselben Waffen auf Holz, Stein und Metall abfeuern. Mit deaktivierter Funktion ist das Ausgangsverhalten wiederhergestellt. In dieser Lieferung gibt es noch keine neuen Flecken und Körperwunden.

**Danach stoppen.**

## 7. Checkpoint 3 – Max-Payne-Blut: Tropfen, Boden- und Wandflecken

**Ergebnis:** Die lokalen MP1-Blutassets sind tatsächlich integriert. Tropfen fliegen/fallen sichtbar, kollidieren mit der Umgebung und hinterlassen dort passende Flecken. Nahe Flächen hinter getroffenen Gegnern erhalten bei gültigem Austritt und ohne blockierende Hindernisse sichtbare Spritzer – ausdrücklich auch bei Pistolen und Maschinenpistolen, nicht nur bei Gewehren und MGs.

### Lokaler, wiederholbarer Import

Extrahiere benötigte Assets in einen separaten Arbeitsordner. Identifiziere Texturen, mögliche Spritesheets/Animationsfolgen und die zugehörigen Effektdefinitionen anhand der tatsächlichen Archive. Erzeuge ein kleines Vorschaumanifest mit Originalpfad, Prüfsumme, Abmessungen, Transparenz und geplanter Verwendung. Dateinamen allein genügen nicht zur Auswahl.

Nutze MP1-Texturen für die gewünschte Optik. Behandle Partikelverhalten als separat zu übertragende bzw. nachzubildende Logik: Laufzeit, Geschwindigkeit, Schwerkraft, Größe, Farbverlauf, Blendmodus, Kollisionsverhalten und Decal-Erzeugung. Behaupte nicht, dass das Kopieren eines Texturbildes automatisch den Max-Payne-Partikeleffekt portiert.

Prüfe Alphakanal, Farbsäume, Texturorientierung, Atlasaufteilung, Mipmaps und Blendmodus. Flecken sollen auf Oberflächen liegen und nicht selbst leuchten. Herkunft und jede nötige Konvertierung werden protokolliert. Keine MP1-Musik, Modelle oder sonstige nicht benötigte Dateien kopieren.

Die automatisch erzeugten MP1-Assetpakete bleiben lokale Buildprodukte und außerhalb des öffentlichen Quell-/Releasepakets. Ein auslieferbarer Importer soll sie aus der jeweiligen lokalen Installation erzeugen. Dies ist eine Paketierungsanforderung und keine pauschale Aussage über Nutzungs- oder Veröffentlichungsrechte.

### Gemeinsame Trefferinformationen

Führe spätestens hier einen konsistenten visuellen Trefferdatensatz ein: eindeutige Ereignis-ID, Spielkontext, Ziel-Entity samt Wiederverwendungskennung, tatsächliche Waffen-ID/Waffengruppe, Schusszeit, tatsächlicher Schussstrahl nach Streuung und die vorhandenen Trefferdaten. Ergänze einen stabilen visuellen Zufallsstartwert, den Lebenszustand zum Trefferzeitpunkt sowie eine eindeutige Zuordnung zur damaligen Körperpose. Eintritt und gegebenenfalls Austritt gehören zu demselben Trefferereignis. Diese Felder sind ein Schemasoll, nicht ungeprüft vorhandene APIs.

Die Originalberechnung von Schaden, KI-Reaktionen und Trefferstatistiken bleibt maßgeblich. Die separat abgenommene BT-Dropanpassung aus 0a bleibt aktiv, gehört aber nicht zum visuellen Effektverteiler: Nebel, Partikel, Körperwunden und deren Zufall dürfen keine zusätzlichen Dropaufrufe erzeugen. Erzeuge aus einem Treffer nicht mehrere widersprüchliche Effekte über verschiedene Hooks. Der visuelle Empfänger muss später auch einen bestätigten Leichentreffer ohne HP-Abzug verarbeiten können. Im gemeinsamen Effektverteiler ist deshalb ein pauschales `health <= 0 -> return` unzulässig; welche Zielzustände tatsächlich neue Treffer erhalten, wird bis Checkpoint 5a ausdrücklich begrenzt.

Verwende einen vom Gameplay-Zufall getrennten visuellen Zufallsstrom. Waffenstreuung, KI, Schaden und Missionsskripte dürfen durch aktivierte Bluteffekte oder zusätzliche Zufallsrotationen nicht andere Zufallswerte erhalten. Für reproduzierbare Tests protokolliere Ereignis-ID, Waffenzuordnung, Effektfreigaben und visuellen Startwert.

Die Gameplay-Referenz schließt die aktiven WCR-Anpassungen ein. Gleiche tatsächliche Waffen-/NPC-IDs und restaurierte Modelle mit CP0 ab; WCR-Recoil, Feuerraten, Itemverhalten oder Skriptsequenzen nicht für das Blutsystem überschreiben. Der visuelle Zusatzpfad nutzt bestätigte Treffer der wirksamen Basis, erzeugt keine neue Schadensauswertung und bindet nicht parallel einen zweiten Todes-/Drop-Handler ein.

### Tropfen und Umgebung

Partikel erhalten eine kurze Abstoßbewegung, Schwerkraft und eine zeitbasierte Bewegung. Kollisionen werden auf dem zurückgelegten Segment geprüft, damit schnelle Tropfen bei niedriger Framerate nicht durch dünne Flächen springen. Beim gültigen Auftreffen entsteht einmalig ein an der tatsächlichen Oberfläche ausgerichteter MP1-Blutfleck. Kein Fleck erst auf der Etage unterhalb der getroffenen Treppenstufe.

Trenne Eintrittsnebel/-tropfen vom rückseitigen Austrittssprühzweig. Beide Zweige sind für Pistolen, MPs, Gewehre und MGs vorgesehen; rückseitige Effekte benötigen immer eine gültige Austrittsgeometrie. Starte Eintrittspartikel knapp außerhalb der Eintrittsfläche und berücksichtige den Körper als Sperre für einen Weg durch ihn hindurch. Rückseitige Partikel starten separat an der ermittelten Austrittsfläche; sie werden nicht durch unkontrolliertes Streuen von Eintrittstropfen durch den Körper simuliert. Die gemeinsame Regel aus Abschnitt 1.1 muss sowohl den direkten Decalpfad als auch den Partikel-Kollisionspfad erreichen.

Nutze bzw. erweitere die vorhandenen Welt-Markierungswege und berücksichtige Terrain und bewegliche geeignete Flächen. Auf einer Tür befestigte Flecken müssen deren Bewegung mitmachen oder dort ausdrücklich nicht erzeugt werden, solange die Oberfläche nicht korrekt unterstützt ist. [S5]

Für alle vier in Abschnitt 1.1 freigegebenen Waffengruppen, ausdrücklich auch Pistolen und MPs, darf für Spritzer hinter dem Gegner ein kurzer, begrenzter visueller Trace in geeigneter Schuss-/Spritzrichtung verwendet werden. Der Beginn muss auf der plausibel ermittelten Austrittsseite liegen; bereits hier keine rückseitigen Spritzer bei einem reinen Streifkontakt ohne echten Austritt. Eine dafür notwendige geometrische Prüfung gehört zum sichtbaren Weltblut-Feature, auch wenn die animierte Austrittswunde erst in Checkpoint 5 folgt. Der Welttrace darf den tatsächlich durchquerten Zielkörper nur in diesem geometrisch bestätigten Austrittszweig ausnehmen. Keine andere Wand, Tür oder weitere blockierende Entity überspringen. Der jeweils erste geeignete Oberflächentreffer ist maßgeblich. Keine durch Wände sichtbaren Flecken, keine Flecken in der Luft und keine beliebig weit entfernten Spritzer.

**Pistolen und MPs müssen denselben rückseitigen Effektpfad wie Gewehre/MGs erreichen können.** Entferne alte Pistolen-/MP-Frühausstiege in Emittern, visuellen Traces und Weltflecken. Ein kleiner Uniformeffekt, eine kleine Eintrittstextur oder geringer Schadenswert darf den optischen Austritt nicht sperren. Die Freigabe gilt unabhängig davon, ob der Originalschuss im Gameplay den Körper durchdringt; der rein visuelle Zusatztrace darf seinerseits keinen zusätzlichen Schaden oder eigenständigen Treffer an anderen Zielen erzeugen. Ursprüngliche echte Schussdurchdringung bleibt unverändert.

Himmelsflächen, Wasser und Materialien, auf denen Decals unpassend sind, erhalten eine explizite Regel. Zufallsrotation/Variation darf das Material abwechslungsreicher machen, aber keine unkontrolliert großen Blutpfützen aus einzelnen Tropfen erzeugen. Performancegrenzen und Ausblendregeln gehören bereits in dieses Feature, nicht erst in den Schlusscheck.

### Abnahme

Teste einen Gegner dicht vor einer sauberen Wand, im freien Raum, auf einer Treppe, über einem höherliegenden Boden sowie neben einer beweglichen Tür. In allen drei Spielen und bei unterschiedlichen Bildraten müssen Tropfenbewegung, erster Oberflächentreffer und Fleckplatzierung nachvollziehbar sein. Dauerfeuer darf weder Partikel dauerhaft ansammeln noch die Schadensberechnung verändern.

Wiederhole die Wandtests getrennt mit Pistole, MP, Gewehr und MG, jeweils mit geleerten alten Flecken bzw. frisch geladenem Teststand. **Alle vier Gruppen:** Eintrittsnebel und erreichbare Bodenflecken sichtbar; bei eindeutig gültigem Austritt und erreichbarer Wand hinter dem Körper auch rückseitige Spritzer/Wandflecken sichtbar. Prüfe für Pistole und MP den direkten Weltfleckpfad und den Partikel-Kollisionspfad ebenso wie für Gewehr/MG. Schieße schräg und von der anderen Körperseite, damit die Regel nicht fälschlich an der Blickrichtung des Gegners hängt. Ergänze Negativfälle ohne gültigen Austritt, mit einer blockierenden Tür sowie ohne erreichbare rückseitige Fläche: Dort darf kein unberechtigter Fleck entstehen. Im Ereignisprotokoll müssen die freigegebenen bzw. geometrisch verworfenen Effektzweige nachvollziehbar sein; alte Tests mit der Vorgabe einer grundsätzlich sauberen Wand bei Pistole/MP sind durch diese neuen Positiv-/Negativtests zu ersetzen.

Prüfe die echten importierten MP1-Assets im Spiel, nicht nur generische Testmaterialien. Körperwunden sind weiterhin nicht Bestandteil dieser Lieferung.

**Danach stoppen.**

## 8. Checkpoint 4 – Punktgenaue, animierte Eintrittswunden

**Ergebnis:** Beide Nutzertexturen erscheinen auf der tatsächlich getroffenen Körperoberfläche, variieren pro Wunde durch Zufallsrotation/-spiegelung und bleiben dort beim Laufen, Ducken, Drehen, bei Treffer-/Todesanimationen und am liegenbleibenden Körper. Position und einmal gewählte Texturorientierung bleiben stabil.

**WCR-Modellabdeckung:** Die in CP0 erfassten aktiven Modell-, Material- und Animationsvarianten gehören zur Zielmenge, nicht nur Vanilla-Testgegner. Änderungen an Mesh-/Skelett-/Materialpfaden aus dem übernommenen Bestand bei Projektion, Hautverformung und Detailstufen berücksichtigen. Keine reparierte NPC-Animation oder restaurierte Ausrüstung durch ein altes Komplettmodell ersetzen, nur um Wunden einfacher anzubringen. Dieselbe Abdeckung gilt in Checkpoint 5 für Austritte und in 5a für Leichen. Die gemeinsame kleine/große Waffenmatrix bleibt davon unberührt.

### Waffengruppen und Texturen

Erweitere die bereits in Checkpoint 3 verwendete gemeinsame Waffen-Effekttabelle aus Abschnitt 1.1, statt eine zweite unabhängige Zuordnung anzulegen: Für **Eintritte** verwenden Pistolen und MPs die kleine Wundtextur; Gewehre, Scharfschützengewehre und Maschinengewehre einschließlich einschlägiger stationärer MGs die große Wundtextur. Hinterlege unabhängig davon für die späteren **Austritte** aller vier Gruppen das große Material. Ein gemeinsames Materialfeld darf nicht ungewollt Pistolen-/MP-Eintritte vergrößern oder deren Austritte verkleinern. Die Begriffe bezeichnen hier die vom Nutzer gewünschten Effektgruppen, nicht automatisch den realen Geschossdurchmesser.

Erfasse Waffenvarianten aus allen drei Spielen. Behandle Spezialfälle wie Schrot, Nahkampf und Explosionen separat und dokumentiert; diese erhalten nicht pauschal Gewehr-Eintrittswunden. Verlasse dich insbesondere nicht auf den schadensabhängigen `bulletlarge`-Wert des untersuchten AA-Pfads. [S6]

Prüfe die gelieferten Dateien, Transparenz, Orientierung und Auflösung. Bewahre die Originale. Notwendige technische Varianten wie Mipmaps oder Packformate dürfen erzeugt werden; die Gestaltung darf nicht stillschweigend neu erfunden werden. Ohne diese zwei Assets ist dieser Checkpoint nicht abnahmefähig.

### Zufallsrotation und Zufallsspiegelung pro Wunde

Jede neu angelegte Eintrittswunde bekommt einmalig eine gleichverteilte Rotation im Bereich 0 bis unter 360 Grad um die lokale Oberflächennormale sowie unabhängig gezogene horizontale und vertikale Spiegelungsflags der Decal-UVs. Je Flag gilt eine Wahrscheinlichkeit von 50 Prozent. Dadurch sind ungespiegelte, horizontal gespiegelte, vertikal gespiegelte und beidseitig gespiegelte Varianten möglich. Die Transformation wird um die Texturmitte ausgeführt. Gemeint ist zufällige Variation je Treffer, nicht dass alle Wunden denselben pauschalen Spiegelzustand erhalten.

Variiere nur die lokale Textur-/Decalorientierung. Trefferpunkt, Projektionsrichtung in den Körper, Größe der Waffengruppe, Haftung an der Oberfläche und Schussrichtung dürfen sich dadurch nicht verschieben. Bewahre Alpha und korrekte Oberflächendarstellung bei gespiegelten UVs; ein geänderter Drehsinn darf die Wunde nicht durch Backface-Culling verschwinden lassen. Keine globale Mutation des gemeinsam verwendeten Materials.

Leite den visuellen Zufallsstartwert aus dem eindeutigen Trefferereignis und einer Wundinstanzkennung ab. Bei mehreren legitimen Wundflächen desselben Schusses muss auch deren Kennung einfließen. Eintritt und späterer Austritt verwenden getrennte Untersequenzen, damit nicht automatisch identische Musterpaare entstehen. Verwende niemals die Framenummer, bloß den Zeitpunkt des Draw-Aufrufs oder eine pro Frame neu gezogene Zufallszahl als Darstellungsvorgabe.

Speichere mindestens `rotation`, `flip_u` und `flip_v` pro Wundinstanz; der zusätzliche Seed dient Reproduzierbarkeit und Tests. Die Werte dürfen sich bei Animation, Kamerawechsel, LOD-Wechsel, Culling, Wechsel von NPC zu Corpse, Save/Load oder erneutem Beschuss nicht mehr ändern. Neues Blut darf bestehende Wunden überlagern, aber deren Orientierung nicht neu auswürfeln. Verwende weiterhin ausschließlich die beiden gelieferten Ausgangstexturen; es werden keine zusätzlich vom Nutzer zu erstellenden Varianten benötigt.

### Oberfläche statt bloßer Trefferregion

Nutze den autoritativen bestätigten Treffer, verfeinere ihn aber bei Bedarf gegen die animierte sichtbare Geometrie des tatsächlich getroffenen Gegners. Verwende denselben Schussstrahl einschließlich Streuung und die zum Treffer passende Pose. Ein späterer Trace vom inzwischen verschobenen Fadenkreuz ist unzulässig.

Die Meldung einer groben Trefferregion allein genügt nicht für eine punktgenaue Wunde. Wenn die ursprüngliche Kollisionshülle getroffen wurde, aber kein entsprechender sichtbarer Oberflächentreffer existiert, erfinde keine Wunde an der Brustmitte. Logge den Fall, verwende nur eine begrenzte und dokumentierte Oberflächenannäherung und ändere zur Kaschierung nicht die Originalhitboxen.

### Bevorzugte technische Umsetzung

Prüfe vorhandene Funktionen zuerst. Falls kein geeigneter animierter Decalpfad existiert, ergänze einen.

Bevorzugt wird ein lokales, auf die getroffenen Mesh-Dreiecke projiziertes Decal. Begrenze seine Projektion räumlich sowie auf passende sichtbare Oberflächen; erzeuge keine Kopie auf der Körperrückseite. Für geclippte Decalpunkte können Dreiecksreferenzen mit baryzentrischen Koordinaten gespeichert und in späteren Frames aus den aktuell deformierten Quelldreiecken rekonstruiert werden. Materialkoordinaten des Decals bleiben erhalten.

Ein an genau einen Knochen gehängtes, frei schwebendes Rechteck genügt nicht als Endlösung: Es darf sich nicht von einer sich verformenden Schulter ablösen. Ebenso ist eine geteilte Uniformtextur kein sicherer Standardweg: Es darf keine Wunde auf einem anderen Gegner oder auf gespiegelten UV-Inseln erscheinen. Ein alternativer Ansatz ist nur dann gleichwertig, wenn er dieselben Sichttests besteht.

Behandle LOD-Wechsel, unterschiedliche Körpermeshes, Modellvarianten, Tod/Corpse-Übergänge, Culling, geringe Oberflächenabstände und Z-Fighting explizit. Waffen, Helm, Rucksack und Körper dürfen nicht allein wegen überlappender Bounding Boxes verwechselt werden. Erhalte die originale Spielwirkung solcher Treffer.

Wunden gehören einer Entity-Instanz mit Generation, nicht nur einer wiederverwendbaren Entity-Nummer. Bei Modellwechsel oder Despawn wird die Zuordnung sicher entfernt bzw. nachvollziehbar übertragen. Speichern/Laden muss die Zuordnung innerhalb des neuen Mod-Saveformats rekonstruieren können. Keine Rohzeiger archivieren.

### Abnahme

Schieße gezielt auf Arm, Schulter, Bein und Rumpf; beobachte die Figur anschließend in Bewegung und beim Umfallen. Prüfe unterschiedlich gekleidete Gegner aus allen drei Spielen, mehrere gleich aussehende Gegner nebeneinander, Nah-/Fernansicht mit LOD-Wechsel sowie Speichern/Laden.

Es dürfen keine schwebenden, wandernden, ungewollt auf eine zweite UV-Fläche duplizierten oder auf andere Figuren übertragenen Wunden entstehen. Die gewollte Spiegelung innerhalb genau einer Wundtextur ist hiervon ausdrücklich zu unterscheiden. Das passende kleine/große Eintrittsmaterial ist erkennbar; Pistolen und MPs müssen trotz ihres bereits eingetragenen großen Austrittsmaterials kleine Eintrittswunden behalten. In diesem Checkpoint noch keine Austrittswunden zeichnen; das bereits abgenommene rückseitige Weltblut aus Checkpoint 3 muss dennoch für alle vier Gruppen funktionieren.

Prüfe mehrere räumlich getrennte Treffer: Die Texturen variieren erkennbar in ihrer Orientierung; keine identische Standardausrichtung für jeden Schuss. Der isolierte Transformationstest prüft alle Spiegelkombinationen und repräsentative Winkel. Ein Test mit festem visuellem Seed ist reproduzierbar, unterschiedliche Ereignisse erhalten eigene Werte. Zufällige Wiederholungen einzelner Spiegelzustände sind zulässig. Vergleiche dieselben Wunden vor und nach Bewegung, Tod, LOD-Wechsel und Save/Load: Ihre gespeicherten Transformationswerte müssen identisch bleiben. Neue Treffer auf bereits tote Körper sind weiterhin der getrennte Umfang von Checkpoint 5a.

**Danach stoppen.**

## 9. Checkpoint 5 – Richtungsabhängige Austrittswunden

**Ergebnis:** Pistolen, Maschinenpistolen, Gewehre und Maschinengewehre können einen geometrisch plausiblen Austritt darstellen. Alle verwenden dafür die große Nutzertextur mit dem Darstellungsstandard großer Gewehr-/MG-Eintrittswunden. Pistolen/MPs behalten ihre kleinen Eintrittswunden. Jede Austrittstextur wird pro Wunde unabhängig zufällig rotiert und gespiegelt. Rückseitige Spritzer und Umgebungsflecken sind für alle vier Gruppen angebunden.

Verfolge für den bestätigten Körpertreffer denselben Strahl durch den tatsächlich getroffenen, passend animierten Körperbereich. Bestimme einen gültigen Übergang von innen nach außen. Der Austritt darf nicht durch Spiegeln am Entity-Ursprung oder ein festes Offset auf dem Rücken entstehen. Ein seitlich getroffener Oberarm bekommt keinen pauschalen Rückentreffer.

Mehrlagige Kleidung, nicht wasserdichte Meshes, Ausrüstung, tangentiale Streifschüsse und getrennte Intervalle wie Arm vor Brust sind explizite Testfälle. Suche nur nach tatsächlichen passenden Oberflächen. Bei uneindeutiger Geometrie ist ein dokumentiert ausgelassener Austritt besser als eine Wunde in der Luft; häufige Auslassungen bei normalen Durchschüssen sind allerdings ein Fehler, kein akzeptierter Ersatz des Features.

Nutze für **jeden Austritt** der vier Gruppen exakt die große Nutzertextur. Pistolen-/MP-Austritte müssen optisch demselben großen Wundprofil wie Gewehr-/MG-Eintritte und -Austritte entsprechen: gleiche Ausgangstextur, Material-/Alpha-/Blend-Einstellungen und Grundskalierung; keine verkleinerte Pistolen-/MP-Variante und keine bloß hochskalierte kleine Eintrittstextur. Definiere ein gemeinsam referenziertes großes Darstellungsprofil, sodass dessen Änderungen konsistent wirken. Eine dritte Textur ist nicht erforderlich. Zufallsrotation und Zufallsspiegelung sind verbindlich und verwenden das Verfahren aus Checkpoint 4 mit einer eigenen Wundkennung; kopiere nicht einfach die Transformation des Eintritts. Binde den Austritt mit demselben animationsfesten Verfahren wie den Eintritt an und archiviere seine Materialzuordnung und Transformationswerte ebenso.

Die Blutspritzer aus Checkpoint 3 verwenden nun dieselbe verfeinerte Austrittsberechnung als Ausgangspunkt. Dabei weder Nebel noch Tropfen doppelt erzeugen. Bei fehlender oder ungültiger Austrittsgeometrie darf auch kein davon abhängiger rückseitiger Spritzer erfunden werden. Die Waffenpolicy gibt Pistolen, MPs, Gewehre und MGs gleichermaßen frei; weder kleine Eintrittsmaterialien noch alte Pistolen-/MP-Sonderfälle dürfen den Pfad sperren. Eintrittsseitige Effekte bleiben unabhängig vom Erfolg der Austrittsbestimmung erhalten. Das Abschalten der gezeichneten Körperwunden darf erlaubtes Weltblut nicht ebenfalls abschalten.

Diese Erweiterung ist rein visuell. Sie darf keine neue Durchschuss-Schadensmechanik, keinen zusätzlichen Schaden an einer dahinterstehenden Figur und keine veränderte Materialdurchdringung einführen. Bereits vorhandene originale Durchdringung bleibt unangetastet.

**Abnahme:** Prüfe Pistolen-, MP-, Gewehr- und MG-Schüsse jeweils frontal, rückwärtig und seitlich; Arm vor Brust; Streifschuss; Gegner direkt vor einer Wand. Bei gewöhnlichen, geometrisch eindeutigen Körpertreffern müssen auch Pistole/MP eine kleine Eintrittswunde, eine große Austrittswunde und bei erreichbarer Fläche rückseitiges Blut erzeugen. Vergleiche das große Wundmaterial und seine Grundskalierung ausdrücklich mit Gewehr-/MG-Treffern. Teste die direkte Fleckprojektion und kollidierende rückseitige Partikel. Eintritt und Austritt behalten jeweils ihren eigenen gespeicherten Rotations-/Spiegelzustand bei Bewegung, Tod, LOD-Wechsel und Save/Load. Keine erfundenen Austritte bei ungültiger Geometrie oder Flecken durch zusätzliche Hindernisse. Körperwunden und Weltblut auch getrennt ein-/ausschalten. Schaden, ursprüngliche Geschossdurchdringung, Waffenstreuung und Hit-Statistik müssen dem Stand vor diesem Checkpoint entsprechen.

**Danach stoppen.**

## 10. Checkpoint 5a – Beschießbare Leichen mit vollständigen Bluteffekten

**Ergebnis:** Neue Schüsse auf bereits tote menschliche Körper erzeugen punktgenau die bis hierher abgenommenen Blutwolken, Spritzer, Tropfen, Umgebungsflecken und Körperwunden. Austritte mit großer Nutzertextur und rückseitiges Blut entstehen bei gültiger Geometrie für Pistolen, MPs, Gewehre und MGs. Bestehende Wunden bleiben erhalten; jede neue Wunde erhält eigene stabile Zufallsrotation/-spiegelung.

Dies ist ein eigenständiger, kumulativer Checkpoint nach 5 und vor 6. Baue dabei keine Kampagnenfunktion und keine neue Ragdoll-/Zerstückelungsphysik ein. Beginne erst, wenn die vorausgehenden Bluteffekte abgenommen sind.

### Erfasste Körper und Lebenszyklus

Erfasse frisch getötete Gegner, noch laufende Todesanimationen, bereits ruhig liegende Körper und in der Map von Anfang an vorhandene menschliche 3D-Leichen. Untersuche dafür die tatsächlichen NPC-, Corpse- und gegebenenfalls statischen Modellpfade in allen drei Spielen. Eine stumme Ausnahme für ein anderes Leichenmodell oder für als Props platzierte 3D-Leichen ist keine vollständige Umsetzung. Leichen, die nur als gemalte Hintergrundtextur ohne eigene Körpergeometrie vorkommen, nicht als beschießbares 3D-Modell behaupten.

Ein ursprünglich nicht mehr schadenempfangender bzw. nicht mehr im üblichen Bullet-Trace enthaltener Körper braucht einen gezielten visuellen Trefferweg. Das bloße Hinzufügen von Blut in eine nur bei lebenden NPCs ausgeführte Schadensfunktion reicht nicht. Belege im Testbericht, welche tatsächlichen Körperpfade erfasst werden.

Beim Übergang vom lebenden NPC zum Leichenobjekt müssen vorhandene Wunden einschließlich Oberflächenbindung und Transformationswerten mitwandern. Bleibt dieselbe Entity erhalten, werden ihre Wunden nicht neu erzeugt. Entsteht ein separates Corpse-Objekt, ist eine ausdrückliche Übertragung auf die passende Geometrie erforderlich. Das Zurücksetzen der Wunden auf eine frühere stehende Pose ist unzulässig.

### Bestätigter visueller Treffer, ohne erneuten Gameplay-Schaden

Prüfe zuerst, ob der bestehende Schusspfad tote Körper bereits zuverlässig meldet. Nutze ihn, wenn möglich. Falls nicht, ergänze einen getrennten, zielgerichteten visuellen Trace mit dem tatsächlichen Schussstrahl nach Streuung und zum selben Simulationszeitpunkt. Ein solches Zusatzsystem darf die originale Schadens-, Materialdurchdringungs-, Bewegungs- oder KI-Kollisionsmaske nicht pauschal ändern. Keine Leiche durch `health = 1`, erneute KI-Aktivierung oder einen weiteren Todesaufruf künstlich beschießbar machen.

Grenze eine zusätzliche Leichenprüfung durch den realen Schussverlauf und dessen blockierende Umgebung ein: Kein Leichentreffer durch Wand, geschlossene Tür oder ein vom Originalschuss nicht durchdrungenes Hindernis. Verwende für die endgültige Oberfläche die aktuelle liegende bzw. noch animierte Pose, nicht eine alte stehende Hitbox. Eine günstige räumliche Vorauswahl darf grob sein; die sichtbare Wunde darf es nicht. Helm, Ausrüstung und Körper weiterhin unterscheiden.

Ein optischer Leichentreffer führt ausschließlich in den gemeinsamen Effektverteiler aus Checkpoint 3. Er verursacht keinen neuen HP-Schaden, Kill, Kopfschussbonus, Missionsabschluss, Todesdialog, KI-Alarm oder Waffen-/Inventardrop. Die Mod fügt keine Trefferstatistik für Leichen hinzu. Originales Schussgeräusch und dadurch ausgelöste originale KI-Reaktionen bleiben unverändert; verboten sind zusätzliche Alarme durch die neue Leichentrefferverarbeitung. Bereits vorhandene echte Trefferwirkung des unveränderten Schusspfads – auch an anderen Zielen – bleibt unangetastet; der Zusatztrace ruft niemals selbst nochmals die Schadensfunktion auf.

Für Breakthrough ist die Negativprüfung ausdrücklich mit aktiviertem Drop-Patch aus 0a durchzuführen. Die eigentliche Tötung verwendet dessen reguläre Auswertung; spätere Schüsse auf den Körper erzeugen Blut, aber keine weitere Dropauswertung und keine zusätzlichen Munitions-/Heilungsgegenstände. Prüfe den Wechsel NPC→Corpse und Save/Load. Ein- oder Ausschalten der Bluteffekte darf bei sonst identischem Testablauf die Dropentscheidungen nicht ändern.

Erweitere diese Negativprüfung auf WCR-Skriptzustände: restaurierte Spawns, Begleiter-/Dialogbedingungen, echte NPC-Todesereignisse und zulässige Itemausgaben dürfen nicht erneut oder gar nicht ausgeführt werden. Zusätzliche 3D-Leichen und geänderte NPC-Modelle aus der aktiven WCR-Basis gehören zur bereits verlangten Körperabdeckung. Keine globale Änderung an WCR-`ai`-/Todesfunktionen, die nur das Beschießen vereinfacht, dafür aber Missionen oder den BT-Drop-Merge zurücksetzt.

Dedupliziere mit Schuss-/Trefferereignis, Ziel-Instanz samt Generation und gegebenenfalls Teilgeschoss-/Traceabschnittskennung. Der tödliche Treffer darf nicht einmal als NPC-Treffer und sofort nochmals als Leichentreffer verarbeitet werden. Ein späterer neuer Schuss auf denselben Körper muss dagegen ein neues Ereignis erhalten. Eintritt und berechtigter Austritt sind Teil dieses Ereignisses, keine zwei getrennten Tötungs- oder Treffermeldungen. Mehrere wirkliche Teilgeschosse nicht pauschal zu einem Treffer zusammenfassen; ihre Waffenregeln müssen zuvor festgelegt sein.

### Gleiches Blut- und Wundsystem für lebend und tot

Nutze dieselben Materialien, Partikelmodule, Waffenregeln und Decal-Renderer. Keine zweite, geringerwertige Leichenvariante mit festem Fleck in der Körpermitte. Jeder neue zulässige Treffer erzeugt am tatsächlichen Kontakt den roten Blutnebel und die MP1-Spritzer/-tropfen; Oberflächenflecken entstehen nur bei passendem Kontakt bzw. freigegebener Projektion.

Pistole/MP auf eine Leiche: kleine neue Eintrittswunde und bei gültiger Geometrie große Austrittswunde, jeweils mit eigener Zufallsorientierung. Gewehr/MG: große Eintrittswunde und bei gültiger Geometrie dieselbe große Austrittswunde. Für alle vier Gruppen entstehen Eintrittsnebel, erreichbare Spritzer/Bodenflecken sowie rückseitige Spritzer und geeignete Umgebungsflecken von der tatsächlichen Austrittsstelle aus. Die großen Austritte verwenden auch hier denselben Darstellungsstandard wie große Gewehr-/MG-Eintrittswunden; der tote Zielzustand darf weder Materialwahl noch Austrittsfreigabe verändern.

Bei einem flach auf dem Boden liegenden Körper muss Blut die tatsächliche Geometrie berücksichtigen. Partikel nicht unter dem Boden erzeugen und Decals nicht blind durch einen abdeckenden Torso hindurch projizieren oder zur Kamera versetzen, nur damit sie sichtbar sind. Ein geometrisch verdeckter Austritt bleibt verdeckt. **Bei allen vier Gruppen, einschließlich Pistolen/MPs,** darf ein tatsächlich erreichbarer Boden hinter einem gültigen Austritt einen Fleck erhalten, der aus passender Sicht sichtbar wird. Prüfe sehr kleine Abstände zwischen Austritt und Boden, bevor ein Emitter um einen Oberflächenabstand versetzt wird; dieser Versatz darf nicht unter die Bodenfläche springen. Bodenflecken neben oder hinter dem Körper dürfen nicht versehentlich mit der Leiche mitbewegt werden.

Neue Treffer verändern die bereits gespeicherten Winkel-/Spiegelwerte alter Wunden nicht. Verwendet eine statische 3D-Leiche einen anderen Meshpfad, bekommt sie einen gleichwertigen Oberflächen-Decaladapter statt eines schwebenden Ersatzrechtecks.

### Speicherung, Entfernung, Optionen und Lastgrenzen

Speichern/Laden erhält für weiterhin existierende Körper alle gespeicherten Wunden samt Zuordnung und Transformationswerten innerhalb der definierten Budgets. Es darf beim Laden keine alten Treffer erneut abspielen. Neue Treffer nach dem Laden sind wieder möglich. Rohzeiger, kurzlebige Renderindizes und bloß wiederverwendbare Entity-Nummern sind keine dauerhafte Identität.

Beim vorgesehenen Entfernen eines Körpers werden seine Körperwunden, Trefferregistrierung und Referenzen entfernt. Bereits platzierte Weltflecken bleiben bis zu ihrer eigenen Ausblendregel erhalten; noch laufende Partikel dürfen keine ungültigen Körperzeiger benötigen. Die Mod verlängert die Lebensdauer von Leichen nicht unbegrenzt und verändert keine Missionsskripte, nur um Decals zu behalten.

Ergänze eine gespeicherte, standardmäßig aktive Option für neue Leichentreffereffekte. Sie wirkt zusätzlich zu den allgemeinen Schaltern für Blutnebel, Weltblut und Körperwunden. Ist nur Weltblut deaktiviert, bleiben erlaubte Körperwunden möglich. Ist die Leichenoption deaktiviert, entstehen bei neuen Leichentreffern keine Mod-Bluteffekte; zuvor angebrachte Wunden bleiben entsprechend ihrer regulären Lebensdauer erhalten. Das Ausschalten darf keinen lebenden Gegner beeinflussen und keinen Spielstand beschädigen.

Nutze begrenzte Ereignis-, Partikel- und Decalbudgets. Bei ruhenden Körpern dürfen stabile Oberflächendaten zwischengespeichert werden; bei Restanimation/Bewegung müssen sie aktualisiert werden. Keine vollständige Geometriesuche über sämtliche Leichen in jedem Renderframe und keine aktive NPC-Simulation allein für Bluteffekte. Bei vielen Treffern ältere Effekte kontrolliert ausblenden; nicht unbegrenzt Speicher ansammeln oder nach längerem Spielen sämtliche neuen Trefferwirkung verlieren.

### Abnahme – fünf Spieltests und protokollierte Negativprüfungen

1. **Frischer und alter Körper:** Einen Gegner töten, noch während des Umfallens und danach gezielt Arm, Bein und Rumpf beschießen. Dasselbe bei einer länger liegenden sowie einer von Anfang an platzierten 3D-Leiche prüfen. Jeder neue Kontakt erzeugt die vorgesehenen Effekte an der tatsächlichen aktuellen Körperoberfläche. Der tödliche Schuss selbst wird nicht doppelt visualisiert.
2. **Waffenmatrix:** Je einen sauberen Teststand mit Pistole, MP, Gewehr und MG prüfen, sowohl vor einer Wand als auch am Boden. Pistole/MP: kleine Eintrittswunde, große Austrittswunde und rückseitiges Wand-/Bodenblut bei gültiger Geometrie und erreichbarer Fläche. Gewehr/MG: große Eintrittswunde und dieselbe große Austrittswunde samt rückseitigem Blut. Material-/Grundskalierungsvergleich aller Austritte durchführen. Eintrittsseitige Effekte bleiben vorhanden. Kein Austritt ohne passende Oberfläche, kein Fleck durch zusätzliche Hindernisse oder unterhalb des Bodens. Hinter einer geschlossenen Tür liegende Körper dürfen vom blockierten Schuss nicht getroffen werden.
3. **Variation und Persistenz:** Mehrere räumlich getrennte neue Wunden setzen, Kamerawinkel/Entfernung ändern, speichern/laden und nochmals schießen. Vorhandene Wunden behalten exakt ihre gespeicherten Rotationen/Spiegelungen; neue Wunden bekommen eigene. Kein Springen auf andere Figuren beim NPC-/Corpse-Wechsel oder bei wiederverwendeten Entity-IDs.
4. **Keine Gameplay-Nebenwirkung:** Kill-/Trefferstatistik, Missionsfortschritt, ursprüngliche Durchdringung, Bewegungsblockaden und Todesreaktionen vor und nach zusätzlichem Leichenbeschuss vergleichen. Keine Wiederbelebung, erneute Todesanimation, neuen Drops, zusätzlichen Alarme oder neuen Schäden durch den visuellen Zusatztrace. In BT den 0a-Patch aktiv lassen und zusätzliche Munition/Heilung durch Leichenbeschuss ausdrücklich ausschließen; die regulären Drops beim tatsächlichen Töten bleiben erhalten. Originale Reaktionen auf das Schussgeräusch nicht unterdrücken. Allgemeine Blutschalter und Leichenoption getrennt testen.
5. **Last und Aufräumen:** Wiederholt mehrere Körper beschießen, deren regulären Despawn abwarten und den Test nach Save/Load wiederholen. Budgets, Frametimes und Speicherentwicklung messen. Keine Geistereffekte an verschwundenen Körpern, kein dauerhaft wachsender Speicher und keine doppelte Partikelwolke pro Treffer.

Die Tests gelten für **AA, Spearhead und Breakthrough**. Pro Kontext Körpermodell/-typ, Waffen-ID, aktuelle Pose, ausgelöste Effektzweige, verbotene Effektzweige sowie tatsächlich geprüfte und noch offene Fälle protokollieren. Isolierte Tests prüfen die gemeinsame Waffenpolicy und die unveränderten Wundtransformationswerte zusätzlich automatisiert.

**Danach stoppen.**

## 11. Checkpoint 6 – Gemeinsamer Missionslader mit sicheren Spielkontextwechseln

**Ergebnis:** Aus einer gemeinsamen Oberfläche können Missionen aller drei Titel gestartet und wieder verlassen werden, ohne externe Originalprogramme manuell zu wechseln. Noch keine abschließend chronologische Freischaltung und noch keine neue Kartenillustration.

Baue einen gemeinsamen Frontend-/Campaign-Controller und einen expliziten Inhaltskontext pro Originaltitel. Jeder Kontext definiert seine überprüfte Archive-/Override-Reihenfolge, Skriptsemantik, erforderlichen Modelle/Waffen, UI-Anbindung und relevanten Engine-/Protokolleinstellungen. Respektiere echte Abhängigkeiten der Erweiterungen; rate ihre Suchpfade nicht.

Jeder Inhaltskontext enthält die in CP0 geprüften WCR-Bestandteile und ihre tatsächlichen Abhängigkeiten, BT zusätzlich den zusammengeführten 0a-Stand. Gemeinsame WCR-Dateien und titelabhängige Fassungen ausdrücklich unterscheiden. Nicht alle WCR-Pakete pauschal in jeden Kontext einhängen; umgekehrt darf der Wechsel nach AA/SH nicht sämtliche WCR-Korrekturen entfernen. Eine Ressource aus einem zuvor aktiven Spiel darf nicht aufgrund ihres gleichnamigen Pfads im Cache erhalten bleiben. WCR-Inhaltsprofil und Fingerprint gehören in Start-/Save-Metadaten.

Verändere nicht mitten im laufenden Level eine CVar und hoffe auf korrekte globale Zustände. Implementiere bei Bedarf einen geordneten Wechsel am Missionsrand: aktuelle Sitzung/Scriptwelt beenden, zuständige Ressourcen und Caches bereinigen, passenden Suchpfad und Spielmodus einrichten, benötigte Systeme initialisieren, Zielmission mit korrektem Anfangszustand laden. Behalte die gemeinsamen Benutzereinstellungen und Progressionsdaten getrennt davon.

Die technische Notwendigkeit folgt daraus, dass OpenMoHAA die Zielspiele einschließlich Protokoll unterscheidet. Ob der gewählte Commit bereits Teilfunktionen zum Wechsel bereitstellt, ist lokal zu prüfen. [S2]

Ein externer Launcher, der lediglich drei Original-EXEs startet, ist nicht die fertige Integration. Ein unvermeidbarer interner Neustart wäre gesondert zu dokumentieren und dürfte nicht stillschweigend als nahtloser Kontextwechsel gelten.

Binde den BT-Drop-Patch aus 0a vor der Skriptinitialisierung jeder BT-Mission in den Zielkontext ein. Beim Verlassen von BT die zuständigen Overrides, Skriptmodule und eventuelle Drop-Zustände geordnet entfernen. Ein nachträglicher Optionswert genügt nicht, wenn ein gecachtes Skript noch aus dem falschen Kontext stammt. AA-/SH-Missionen dürfen weder die BT-Änderung erben noch BT-Missionen nach einem vorherigen AA-/SH-Start auf ungepatchte Skripte zurückfallen. Diese Regeln gelten auch beim direkten Laden eines Mod-Saves aus einem anderen Kontext.

Identifiziere Missionen mit eindeutigen IDs einschließlich Spielkontext, nicht nur über möglicherweise kollidierende Mapnamen. Prüfe gleichnamige Skripte, Shader und Menüs. Inhalte eines zuvor geladenen Add-ons dürfen nach dem Wechsel keine andere Kampagne verändern.

Speichern/Laden bekommt eindeutige Kontext- und Formatmetadaten. Fremde oder nicht unterstützte Originalspielstände nicht ungeprüft laden und keinesfalls überschreiben. Die Unterstützung alter Saves ist separat nachzuweisen, nicht zu behaupten.

Beim Kontextwechsel sämtliche alten NPC-/Corpse-Trefferregistrierungen und instanzgebundenen Wundreferenzen entfernen. Keine Leichen-ID, Waffen-Effekttabelle oder Partikelreferenz aus AA ungeprüft in SH/BT weiterverwenden. Beim Laden eines Mod-Saves werden die passenden Körper- und Wundzustände im richtigen Kontext rekonstruiert; Rotation und Spiegelung bleiben unverändert.

**Abnahme:** Teste AA→SH, SH→AA, AA→BT, BT→AA, SH→BT und BT→SH. Kontrolliere nach jedem Wechsel Waffen, Modelle, Missionsziele, Menüs, Ton, Speichern/Laden und Rückkehr zur gemeinsamen Oberfläche. Ergänze bei BT-Zielen den Nachweis der aktiven 0a-Skripte und Patchwirkung; bei AA-/SH-Zielen den Nachweis unveränderter Drops. Prüfe zusätzliche Wiederholungen wie BT→AA→BT und BT→SH→BT sowie Save-Laden quer zum aktuellen Kontext. Leichenbeschuss darf in keinem Zielkontext zusätzliche Gegenstände erzeugen. Lade alle erfassten Missionsstarts automatisiert, soweit technisch möglich; echte Spieltests und bloßes Laden getrennt ausweisen.

Für jeden Wechsel außerdem einen in CP0 dokumentierten WCR-Referenzfall und die effektive Herkunft kritischer Menüs/Skripte prüfen. Wiederhole vorhandene WCR-Briefing-/Savefälle beim direkten Einstieg und beim Wechsel aus einem anderen Spiel. Nach einem Inhaltsfingerprint-Wechsel keine sicheren Save-Migrationen voraussetzen: Kompatibilität nachweisen oder den erforderlichen Missionsneustart unter Erhalt des Kampagnenfortschritts ausweisen.

**Danach stoppen.**

## 12. Checkpoint 7 – Vollständige chronologische Kampagne und Progression

**Ergebnis:** Eine neue gemeinsame Kampagne beginnt am vorgesehenen ersten Einsatz. Erfolgreiche Einsätze schalten chronologisch nachfolgende Inhalte frei. Bereits freigeschaltete Einsätze bleiben wiederholbar; Rückkehr und Fortsetzen funktionieren über Neustarts und Spielkontextwechsel hinweg.

### Verifiziertes Missionsmanifest

Erstelle ein datengetriebenes Manifest aller vorgesehenen Kampagnenmissionen und Unterabschnitte. Empfohlene Felder sind:

`id`, `source_game`, `operation_id`, `map_chain`, `display_name`, `game_date_start`, `game_date_end`, `date_precision`, `date_source`, `location_name`, `latitude`, `longitude`, `location_precision`, `location_source`, `protagonist`, `briefing`, `prerequisites`, `continuity_group`, `start_state`, `completion_event`, `next_id`, `replay_policy`, `gameplay_patch_profile`, `content_profile`, `content_fingerprint`, `completion_variant`, `optional_entry_points`.

Diese Feldnamen sind ein Schemasoll, keine schon vorhandene Spiel-API.

Das Patchprofil wird zentral aus `source_game` abgeleitet und validiert: sämtliche BT-Missionen/Unterabschnitte referenzieren die geprüfte 0a-Integration, AA/SH die jeweils unveränderte Drop-Logik. Keine Auswahl anhand des geografischen Orts, des Protagonistennamens oder der Position in der chronologischen Liste. Abweichende bzw. fehlende BT-Profile sind Manifestfehler. Die Save-Metadaten halten Profil-/Integrationsversion fest.

Das getrennte Inhaltsprofil beschreibt die tatsächlich verwendete WCR-Basis und gegebenenfalls notwendige titelabhängige Module; AA/SH sind deshalb nicht „ohne WCR“, nur „ohne BT-Drop-Merge“. `completion_variant` bezeichnet den lokal belegten Abschlussweg, nicht eine erfundene Engine-API. Vergleiche restaurierte Abläufe, Startzustände, Briefings und Übergänge mit dem lokalen WCR-Changelog und den wirksamen Skripten. Ein anhand von Vanilla recherchierter `completion_event` darf keine restaurierte Sequenz abschneiden.

**Besonders wichtig: Breakthrough-Finale.** Für eine lokale Fassung mit der erweiterten Flucht darf weder das Anfordern/Bestätigen des Luftangriffs noch ein früher Vanilla-Endtrigger schon die nächste Gesamtmission laden. Warte auf den tatsächlichen erfolgreichen Abschluss der WCR-Sequenz; Scheitern oder Tod ist kein Missionsabschluss. Dialoge, Timer, Begleiter und notwendige Skriptzustände bis dahin erhalten. [S27]

Restaurierte Teilsequenzen bleiben in ihrer Operation; nicht automatisch aus jedem neuen Trigger eine eigenständige chronologische Mission machen. Bereits vorhandene optionale Bonus-/Nebenaktivitäten und deren Menü-/Briefingzugänge erhalten, ohne sie ungefragt zur Pflichtkampagne zu erklären oder mit erfundenem Datum/Ort zu versehen. Optionale Inhalte dürfen Hauptfortschritt, Fortsetzen-Punkt und chronologische Nachfolger nicht versehentlich verändern. Inaktive Bonuspakete bleiben nach Abschnitt 1.4 inaktiv.

Verifiziere Datum, Ort, Reihenfolge und Abschnittsgrenzen anhand der tatsächlich installierten Briefings, Ladebildschirme, lokalisierten Texte und Missionsskripte. Ergänze bei Bedarf belastbare historische Quellen. Das ursprüngliche grobe Kampagnenkonzept ist nur Arbeitsgrundlage, keine bereits geprüfte Liste sämtlicher Maps.

Unterscheide das Datum der Spielhandlung vom Datum eines realen historischen Ereignisses. Erfundenen Operationen darf keine unbelegte reale Genauigkeit zugeschrieben werden. Keine Uhrzeiten oder Koordinaten erfinden. Unsichere Daten erhalten eine Genauigkeits-/Quellenangabe.

Sortiere nach den belegten Missionsdaten statt pauschal nach AA→Spearhead→Breakthrough. Wo sich Einsätze derselben Zeit überschneiden, definiere eine nachvollziehbare, dokumentierte Reihenfolge. Zusammenhängende Levelketten nicht ohne Prüfung auftrennen. Falls streng chronologische Sortierung und echte Skriptabhängigkeiten kollidieren, dokumentiere den konkreten Konflikt und löse Startzustände/Übergänge gezielt; gib eine unsortierte Kette nicht einfach als streng chronologisch aus.

### Progression und Startzustände

Nutze einen versionierten, separat gespeicherten Kampagnenfortschritt. Eine bloße Level-Ladung oder ein Konsolen-Mapwechsel darf keinen Abschluss markieren. Verknüpfe den Fortschritt mit dem tatsächlichen erfolgreichen Missionsabschluss. Behalte Fehlschläge, Neustarts und verschiedene Abschlusswege im Blick.

Schreibe Abschluss und Freischaltung atomar, bevor der Kontextwechsel beginnt. Ladefehler dürfen weder Fortschritt verlieren noch automatisch den nächsten Einsatz abschließen. Teste Abbruch/Wiederaufnahme zwischen Abschluss und neuem Missionsstart.

Innerhalb einer original zusammenhängenden Sequenz bleiben nötiges Inventar, Flags und Begleiterzustände erhalten. Bei unabhängigen Operationen bzw. Protagonistenwechseln werden die passenden Originalstartzustände verwendet. Keine Waffen willkürlich zwischen verschiedenen Figuren übertragen.

Wiederholung und Hauptfortschritt sind getrennt. Das Wiederholen eines früheren Einsatzes darf weder spätere Freischaltungen löschen noch den Fortsetzen-Punkt überschreiben, ohne dass dies ausdrücklich die definierte Bedienlogik ist. Ein eigenes Mod-Saveprofil bleibt von Originalkampagnen getrennt.

Briefings, Zwischensequenzen, Missionsziele und Originalprotagonisten bleiben erhalten. Die Mod verbindet die Kampagnenfolge, nicht die Figuren zu einem erfundenen einzelnen Soldaten. Endcredits dürfen die Gesamtkampagne nicht versehentlich am Ende eines inzwischen mittig liegenden Originalspiels beenden.

### Abnahme

Jede Mission steht genau einmal im Manifest, alle referenzierten Maps sind vorhanden, jede Fortsetzung und jede echte Kampagnengrenze wird überprüft. Jeder BT-Startweg – neue Kampagne, natürliche Fortsetzung, Mission wiederholen, Tod/Neustart, Save/Load – muss die 0a-Patchintegration verwenden. AA/SH bleiben unverändert. Ein vorhandener Profilverweis allein ersetzt nicht die Kontrolle der tatsächlich geladenen Skripte und ihres Verhaltens. Teste neue Kampagne, natürlichen Abschluss, Tod/Neustart, Save/Load, vorzeitiges Verlassen, Wiederholung eines früheren Einsatzes und Fortsetzung nach einem Neustart des Programms.

Eine temporäre gemeinsame Missionsliste darf hier als nutzbare Auswahl dienen. Sie muss bereits dasselbe Manifest und dieselben Freischaltzustände verwenden wie die spätere Karte. Die grafische Karte wird damit nicht als erledigt ausgegeben.

Zusätzliche Pflichtabnahme: Die lokal vorhandene erweiterte BT-Endsequenz natürlich bis zum Erfolg spielen und den Übergang in die Gesamtkampagne prüfen; daneben einen Fehlschlag, Tod/Neustart und Save/Load innerhalb dieser Sequenz. Erst der richtige Erfolg darf fortschalten. Prüfe einen vorhandenen optionalen WCR-Einstieg einschließlich Rückkehr und unverändertem Hauptfortschritt. Fehlt ein solcher Einstieg in der lokalen Basis, den Fall als nicht zutreffend begründen, nicht neu erfinden.

**Danach stoppen.**

## 13. Checkpoint 8 – Grafisch erweiterte, historische Einsatzkarte

**Ergebnis:** Die gemeinsame Kampagne ist vollständig über eine erweiterte Karte im Hauptmenü bedienbar. Karte, Fortschritt und Missionen widersprechen sich nicht.

Erweitere die vorhandene Gestaltung zu einer zusammenhängenden Einsatzkarte im passenden Originalstil. Verwende das geprüfte Manifest aus Checkpoint 7 als einzige Datenquelle für Marker, Missionsnamen, Datumsangaben, Orte, Zuordnung zu Originalspiel/Protagonist und Freischaltzustände.

Die vorhandene Gestaltung ist die übernommene WCR-Menü-/Briefingbasis, nicht ein blind zurückkopiertes Vanilla-Menü. Eine neue Einsatzkarte darf vorhandene Options-, Save-, Briefing-, Bonus- oder Creditszugänge nicht entfernen. Nötige Umplatzierungen in derselben Gestaltung verständlich lösen und testen. Restaurierte Missionsabschnitte erhalten ihre passende Zuordnung aus CP7; optionale Inhalte brauchen keinen erfundenen Kartenmarker. Die neue globale Modbezeichnung erhält WCR-/Drittanbieterhinweise dort, wo sie in Credits/Herkunft hingehören.

Arbeitsziel für die Übersicht ist Europa einschließlich des erforderlichen nördlichen Bereichs sowie Mittelmeer und Nordafrika. Leite die endgültigen Grenzen aus den tatsächlich belegten Einsatzorten ab, statt einen Einsatz außerhalb des Bildes durch einen falschen Markerort zu kaschieren.

Die geografische Grundlage muss überprüfbar sein. Verwende bekannte Koordinaten und eine dokumentierte Projektion bzw. eine kalibrierte Originalkarte. Dekorative Papiertextur, Falze und Zeichnungsstil dürfen gestaltet werden; Küsten, Städte und Einsatzorte dürfen nicht frei halluziniert oder aus einem ungeprüften KI-Bild übernommen werden.

Heutige Grenzen dürfen nicht unmarkiert als Kriegskarte erscheinen. Nutze entweder eine klar datierte historische, quellengeprüfte Grenzebene oder eine bewusst neutrale topografische Karte ohne politische Grenzbehauptung. Datumsabhängige Frontlinien sind nur bei verifizierten Daten einzubauen; ansonsten weglassen. Unbekannte bzw. fiktive Einsatzorte werden als Region dargestellt, nicht als erfundener präziser Punkt.

Brenne Marker und Texte nicht in die Hintergrundgrafik ein. Nutze eine passend hoch aufgelöste oder gekachelte Kartenfläche mit eigenständigen, bei Zoom lesbaren UI-Labels. Überschneidungen werden durch Detailausschnitte, Zoom oder aufklappbare lokale Missionsgruppen aufgelöst. Alle Einträge bleiben erreichbar; es darf keine stille Begrenzung auf die Anzahl der ursprünglichen Kartenmissionen geben.

Mindestens vier Zustände müssen eindeutig erkennbar sein: gesperrt, freigeschaltet, abgeschlossen und nächster Einsatz. Bei Auswahl erscheinen Datum, Ort, Titel, Kampagnenzugehörigkeit und der passende Start-/Wiederholen-Button. Originaltitel bzw. Protagonistenwechsel sind nachvollziehbar.

Chronologische Verbindungen dürfen als Missionsfolge dargestellt werden, aber nicht als historisch behauptete tatsächliche Reiseroute eines einzigen Soldaten. Trenne die Handlungsstränge bei Bedarf visuell. Die gesperrten Marker können sichtbar sein, ohne gestartete Missionen vorzutäuschen.

**Abnahme:** Vergleiche jeden Marker mit dem Manifest und seiner geografischen Quelle. Prüfe alle Einsätze, lokale Gruppen, Daten-/Namensfelder, gesperrte und wiederholbare Missionen sowie Start und Rückkehr zur Karte. Die gesamte UI-Testmatrix aus Checkpoint 1 gilt auch hier, besonders 4:3, 4K und Ultrawide. Kompass-/HUD-Fixes dürfen dabei nicht regressieren.

**Danach stoppen.**

## 14. Checkpoint 9 – Gesamtregression, Performance und auslieferbarer Stand

**Ergebnis:** Ein vollständig zusammengeführter, dokumentierter Modstand einschließlich Installation, lokalen Importen, Einstellungen und Rückbauweg.

Führe Regressionen nicht nur separat pro Feature aus, sondern in Kombination: hohe Auflösung, anderes Seitenverhältnis, mehrere lebende Gegner und Leichen, Dauerfeuer auf beide Zielzustände, Blutpartikel, Weltflecken, mehrere animierte Körperwunden mit stabiler Zufallsrotation/-spiegelung, Austritte, Kontextwechsel und Save/Load.

**WCR-Gesamtregression:** Vergleiche den Endstand mit der abgenommenen WCR-Basis und dem dokumentierten Konfliktmanifest. Die Prüfung umfasst restaurierte Inhalte und Skriptabläufe, Optionsfunktionen, Modell-/Animationsvarianten, Briefing/Save-Verhalten, Leichen-/Dropzustände sowie korrekten Abschluss restaurierter Endsequenzen. Bereits behobene WCR-Fehler dürfen nicht durch ältere Mod-Overrides zurückkehren. Ein fehlerfreier Vanilla-Durchlauf ersetzt keinen Durchlauf mit den tatsächlich zu liefernden WCR-Inhalten. Die genaue örtliche WCR-Version und alle aktiven Zusatzmodule in jedem Bericht ausweisen.

Die Drop-Regression wiederholt 0a mit allen inzwischen aktiven Systemen: BT-Patch aktiv, korrekte Munition/Heilung, keine zusätzlichen Drops durch Leichenbeschuss und keine Patchwirkung in AA/SH. Save/Load, Missionswiederholung und sämtliche Kontextwechsel dürfen weder den Patch verlieren noch Todesevents erneut ausführen. Reproduzierbare BT-Abläufe mit Bluteffekten an/aus müssen dieselben Dropentscheidungen behalten; optische Zufallsaufrufe dürfen den Gameplay-Zufall nicht konsumieren. Frische Installation, erneuter Import und ein bereits vorhandener Patch sind eigene Konflikt-/Idempotenzfälle.

Die verbindliche Waffenregression umfasst in allen drei Spielen lebende und tote Körper: Pistolen/MPs erzeugen kleine Eintrittswunden, große Austrittswunden und rückseitiges Blut; Gewehre/MGs große Eintrittswunden und dieselben großen Austrittswunden mit rückseitigem Blut. Die geometrischen Voraussetzungen und getrennten Effektschalter gelten für alle Gruppen gleich. Vergleiche das große Materialprofil über Waffen und Zielzustände hinweg und teste ausreichend viele MP-Treffer für Budget-/Dauerfeuerregressionen. Die Negativregression prüft weiterhin: keine erfundenen Austritte, keine Flecken durch zusätzliche Hindernisse oder unter dem Boden; keine zusätzlichen Gameplay-Schäden, Kills oder Todesreaktionen durch neue Leichentreffer; keine veränderten Transformationswerte bereits vorhandener Wunden bei Save/Load, Tod und Kontextwechsel. Prüfe Waffenstreuung und andere Gameplay-Zufallsfolgen mit Bluteffekten an/aus, damit der getrennte visuelle Zufallsstrom nachgewiesen ist.

Begrenze aktive Partikel, Weltflecken und Wunden pro Entity sowie global, einschließlich aller Leichen und wiederholter Treffer auf denselben Körper. Dokumentiere verwendete Budgets und Verlust-/Ausblendregeln. Erhöhe diese nur nach Messung. Aktualisiere aufwendige Oberflächendaten zielgerichtet, verwende konservative Sichtbarkeitsprüfungen und vermeide neue Vollmesh-Suchen für alle Gegner in jedem Frame. Optische Optimierungen dürfen keine NPCs entfernen, die Simulationsrate herabsetzen oder Missionsskripte verändern.

Erfasse CPU-/GPU-Frametimes, Median sowie hohe Perzentile und Speicherentwicklung bei denselben reproduzierbaren Szenen mit Effekten an und aus. Prüfe wiederholtes Speichern/Laden und wiederholte Kontextwechsel auf dauerhaft wachsenden Speicher. Keine pauschale Performancegarantie ohne gemessene Werte.

Für die neuen Optionen müssen Standardwerte, Persistenz, Bereichsgrenzen und Abhängigkeiten definiert sein. Blutfarbe/Treffernebel, Weltblut, Körperwunden und neue Leichentreffereffekte sollen sinnvoll deaktivierbar sein. Kein deaktiviertes Feature darf weiterhin sichtbar spawnen; kein Ausschalten darf bestehende Saves beschädigen. Die Waffenregeln gelten bei jeder Kombination der Schalter. Erläutere ausdrücklich den Unterschied zwischen nicht mehr neu erzeugten Effekten und bereits vorhandenen, regulär ausblendenden Wunden/Flecken.

Der Installer/Importer erkennt die lokalen Spiele, überprüft erforderliche Daten und erzeugt Modprodukte getrennt von den Originalen. Er muss wiederholbar sein und nach einem Fehler einen konsistenten Stand hinterlassen. Alle importierten proprietären Assets bleiben aus öffentlichen Quell- und Releasearchiven ausgeschlossen. Dokumentiere die verwendeten OpenMoHAA-Lizenz-/Quellhinweise und die Herkunft eigener Assets. [S1]

Der Installer importiert den festgelegten BT-Patch aus dem vom Nutzer mitgelieferten lokalen ZIP im MOHAA-Bestand bzw. als innere Datei des MOHAA-Archivs. Herkunftsreferenz, relative Quell-/Archivpfade, SHA-256, tatsächliche Credits und Integrationsversion dokumentieren. Vorhandene Installationen und Ressourcenüberschneidungen erkennen; keine zweite wirksame Patchkopie hinzufügen. **Kein Patchdownload bei Einrichtung, erneutem Import oder Spielstart; keine Netzwerkprüfung als Importvoraussetzung.** Der Nutzer muss das ZIP nicht manuell entpacken oder installieren. Der lokale Import muss vor Freigabe der BT-Kampagne abgeschlossen sein. Fehlen die geprüften Patchdaten, den betreffenden Stand als unvollständig melden, nicht stillschweigend ungepatchtes BT als vollständige Mod starten. Nach erfolgreichem Import verwendet das Spiel die integrierten Moddateien; das Eingabe-ZIP und seine ursprüngliche Position sind keine Laufzeitabhängigkeit.

Dokumentiere unterstützte Versionen, bekannte Einschränkungen, Savekompatibilität, Deinstallation und Wiederherstellung der Ausgangsbasis. Ein Releasepaket darf keine versteckten lokalen Pfadabhängigkeiten besitzen.

**WCR im lokalen Installer-/Rückbauweg:** Die vorhandene Installation bzw. bereitgestellten WCR-Dateien werden lokal geprüft und referenziert oder geschützt in den Modaufbau übernommen; kein Download als Einrichtungsvoraussetzung. Integrationsprodukte erst nach erfolgreicher Validierung vollständig aktivieren. Ein zweiter Import muss denselben definierten Stand herstellen, nicht eine zweite Schicht derselben Fixes. Fehlende oder geänderte Eingabehashes konkret melden und keinen WCR-losen Build als vollständige Mod ausgeben. Ein abweichender Nutzerbestand braucht eine geprüfte neue Import-/Kompatibilitätsreferenz, kein erzwungenes Überschreiben.

Nach erfolgreichem Import darf kein ungeplanter Zugriff auf ein ursprüngliches Transportarchiv nötig sein; tatsächlich benötigte lokale Inhaltsabhängigkeiten und ihre Sicherung dokumentieren. Automatische Upstream-Updates gehören nicht in den Spielstart. Teste frische Einrichtung, Wiederholung, Abbruch, Wiederherstellung und Deinstallation in getrennten Testordnern: Allied-Campaign-Dateien dürfen zurückgenommen werden, die ursprüngliche WCR-Installation bleibt exakt erhalten. Öffentliche/private GitHub-Pakete enthalten nur nach den Projektregeln freigegebene Inhalte; die lokale spielbare Lieferung muss trotzdem alle dokumentierten WCR-Abhängigkeiten vollständig nutzen können.

Eine vollständige Durchspielabnahme muss als eigene Abnahme erfolgen. Automatisierte Mapstarts und gezielte Übergangstests sind wertvoll, ersetzen sie aber nicht. Dokumentiere ehrlich, welche Abschnitte tatsächlich durchgespielt wurden und welche noch offen sind.

**Danach den Gesamtstand zur Abnahme liefern und stoppen.**

## 15. Vorgesehene Dokumentation und Ablage

Die genauen Namen können an ein vorhandenes Repository angepasst werden; die Trennung ist verbindlich:

```text
AGENTS.md                         kurze Arbeitsregeln inkl. Codex-Repo-Pflege und Chatfreigabe
.gitignore                        Ausschlüsse vor erstem Import; vorgemerkte Dateien extra prüfen
.github/                          PR-Vorlage, Build-/Validierungsworkflows ohne Spielasset-Upload
PLAN.md                           dieses Umsetzungskonzept
STATUS.md                         von Codex gepflegt; Stand, Sicherungsstatus, konkrete letzte Abnahme
sources/                          gesicherte Engine-Quellen bzw. verfügbarer gepinnter Engine-Fork
mod/                              eigene Skripte, Konfigurationen, Shader, UI
mod/effects/weapon_policy.json    zentrale, validierte Waffen-/Blutregeln
mod/breakthrough/                eigene BT-Integrationslogik; nicht freigegebene Ergebnisse lokal
third_party/bt_drops/manifest.json Herkunft, relative ZIP-/Archivpfade, Paketdaten, Hashes, Integration
third_party/bt_drops/INTEGRATION.md geprüfter Diff, Credits, Konflikte, Paketierung
third_party/wcr/manifest.json      lokale WCR-Fassung, aktive Module, Herkunft, Hashes; keine Assets
third_party/wcr/INTEGRATION.md     Bestandsprüfung, Mergeentscheidungen, Credits, Rückbau
third_party/resource_conflicts.json Ressourcenanbieter, aktive Fassung, Entscheidung, Testergebnis
campaign/manifest.json            validierte Missionsdaten
campaign/chronology_sources.md    Belege, Unsicherheiten, Reihenfolgekonflikte
tools/                            Build, lokaler Assetimport, Validierung
generated-local/                  lokale Importprodukte; auch aus privatem Git ausgeschlossen
input-local/                      optionale lokale Eingaben; ignoriert, außerhalb Git bevorzugt
build-local/                      Buildprodukte; aus Git ausgeschlossen
runtime-local/                    getrennte Stable-/Kandidateninstallationen; ignoriert
profiles-local/                   getrennte Profile/Saves; ignoriert und separat gesichert
tests/                            Testszenarien, Testskripte, Testsave-Metadaten
tests/blood/                      Waffenmatrix, Transformations- und Leichentests
tests/bt_drops/                   Dropreferenzen, Save/Load, Leichen- und Kontextregression
tests/wcr/                        Erhaltungstests für UI, Inhalte, Trigger, Finale, Save/Load
checkpoints/CPxx/                  Änderungen, Buildreferenz/-manifest, Testbericht, Testanleitung
artifacts-local/                  lokale Pakete inkl. benötigter Importprodukte; ignoriert
```

Im Testbericht jedes Checkpoints stehen Build-ID, Engine-Commit, WCR-Inhaltsfingerprint und aktive Module, geänderte Dateien, betroffene Ressourcen-/Mergeentscheidungen, geprüfte Spielkontexte, genaue Testbedingungen und vorhandene Einschränkungen. Lege für wiederholbare Sichttests feste Positionen/Blickrichtungen und möglichst reproduzierbare Treffer fest. Für Bluteffekte gehören Waffenpolicy samt Version, getrennte Eintritts-/Austrittsmaterialzuordnung, verwendetes großes Darstellungsprofil, Zielzustand, Ereigniskennung, visueller Seed und gespeicherte Winkel-/Spiegelwerte dazu. Checkpoint 5a erhält eine eigene Ablage, beispielsweise `checkpoints/CP05a/`, und eine eigene Nutzerabnahme. Dasselbe gilt für den Drop-Patch unter `checkpoints/CP00a/`; dessen Bericht ergänzt Patchhash, aktive Skriptherkunft, Integrationsprofil, Vergleichswerte und Nachweise zur einmaligen Dropauswertung. Nicht zur Mitverteilung freigegebene Drittdateien gehören in `generated-local/` bzw. einen gleichwertig ausgeschlossenen lokalen Eingabeordner, weder in das private noch in das öffentliche Repository. Build-ZIPs, Savegames und lokale Profile sind außerhalb der versionierten Checkpoint-Berichte zu halten; im Bericht stehen ihre überprüften Referenzen und Hashes. Die Ausschlüsse und die unabhängige lokale Sicherung gemäß Abschnitt 3.1 ergänzen diese Ablage.

## 16. Startanweisung

Beginne ausschließlich mit Checkpoint 0. Verwende den Modnamen „Medal of Honor: Allied Campaign“. **Der Nutzer hat keine GitHub-Erfahrung: Übernimm die technische Repository-Pflege selbst.** Prüfe bzw. bereite Git und GitHub CLI vor, führe durch eine nötige Browserautorisierung, lege das konkret freigegebene private Projekt-Repository an und richte Sicherungen und Projektregeln ein. Vorhandene Zugänge und Projekte zuerst prüfen; keine breiteren Kontorechte voraussetzen. Nach ausdrücklicher Kandidatenfreigabe führst du auch den PR-Merge selbst durch. Verlange vom Nutzer keine manuellen Branch-, Commit-, Push- oder Merge-Arbeiten. Bei tatsächlich nötiger Identitäts-/Sicherheitsbestätigung nur den konkreten Schritt erklären. Lies zuerst vorhandene Projektdateien, `AGENTS.md`, `STATUS.md`, dokumentierte Vorarbeiten und die tatsächlichen Installationen. Richte den Workflow aus Abschnitt 3.1 als Teil dieser Basis ein; vorhandene Git-Historie und Nutzerarbeit bleiben erhalten. Remote-Aktionen nur im konkret freigegebenen Ziel-Repository durchführen. Ein fehlender oder nicht autorisierter GitHub-Zugang wird klar gemeldet, nicht als schon eingerichtete Sicherung ausgegeben. Der Nutzer stellt **War Chest Restored bereits im Installationsordner** bereit: diese tatsächliche Fassung als zu erhaltende Inhaltsbasis inventarisieren, geschützt übernehmen und in CP0 prüfen. Nicht entfernen, neu herunterladen oder durch Vanilla ersetzen. Der Nutzer stellt den BT-Drop-Patch zusätzlich gezippt im MOHAA-Archiv bereit: dort lokal inventarisieren, nicht herunterladen, erst in 0a mit WCR zusammenführen. Erfasse den Istzustand, lege den geschützten Workspace an, baue die Ausgangsbasis und liefere den ersten startbaren Teststand mit klarer Testanleitung.

Starte danach nicht automatisch Checkpoint 0a. Warte auf die Rückmeldung zum ersten Teststand. Anschließend folgt zunächst 0a; erst nach dessen Abnahme Checkpoint 1. Nachfolgende Checkpoints folgen derselben Stop-/Abnahmeregel.

Falls bereits nach einer vorigen Planfassung gearbeitet wurde, lies zuerst `STATUS.md` und die bisherigen Abnahmen. Beginne nicht unnötig von vorn. **Anpassung aus Revision 8:** Sichere den bestehenden funktionierenden Stand, erfasse die lokale WCR-Basis und führe ihre Erhaltung als eigene Kompatibilitätsrunde nach. Noch keine weiteren Features damit vermischen. Bereits integrierte UI-, Drop-, Blut- oder Kampagnenänderungen gegen die WCR-Ressourcen und -Skriptpfade vergleichen; nur tatsächliche Konflikte gezielt korrigieren und dem Nutzer einen neuen eindeutig zugeordneten Kandidaten zur Abnahme geben. Betroffene WCR-Regressionsfälle einschließlich Finale und Briefing/Save nachprüfen; ältere Tags nicht umdeuten. `AGENTS.md`, `PLAN.md`, `STATUS.md`, Build-/Importmanifeste und Testberichte angleichen. Die WCR-Basis wird in CP0 geführt, ihr Drop-Merge in 0a; kein neu nummerierter Checkpoint und kein stilles Nachinstallieren über den aktuellen Build. **Anpassung aus Revision 7:** Vorhandenes Repository beibehalten. Die Zuständigkeit für Repo-Pflege und technische Übernahme nach Chatfreigabe in `AGENTS.md`, `PLAN.md`, `STATUS.md` und PR-Vorlage angleichen. Einen fälschlich eingerichteten Selbstreview-Zwang als Konfigurationsproblem melden; Schutzregeln nicht eigenmächtig lockern. Kein Neustart, keine Neuimplementation und keine Wiederholung bereits bestandener Spieltests nur wegen dieser organisatorischen Änderung. **Anpassung aus Revision 6:** Bestehenden Quellcode, funktionierende Builds, lokale Assets und Profile inventarisieren und unverändert sichern. Name, Repoablage, Commit-/Push-/PR-Workflow sowie Rückbautest in einer isolierten Einrichtungsrunde nachführen. Keine Funktionsänderungen damit vermischen und alte Tags/Versionszuordnungen nicht nachträglich umdeuten. **Anpassung aus Revision 5:** Eine bisher vorgesehene Onlinebeschaffung des BT-Patches durch den lokalen ZIP-Import ersetzen. Ist 0a bereits abgenommen, Herkunft und Hashes mit dem Nutzer-ZIP abgleichen und nur den Importweg bzw. tatsächlich erforderliche Konfliktkorrekturen separat prüfen; keine bereits funktionierende Patchintegration blind überschreiben. **Weiterhin gültige Arbeit aus Revision 4:** Nach Erhalt eines stabilen Ausgangsstands einen noch fehlenden 0a-Patch in einer eigenen Arbeitsrunde nachholen. Bestehende Features beibehalten; ihre Drop-Wechselwirkungen in 5a/6/7/9 jeweils gezielt prüfen und nötige Korrekturen separat liefern. Kein kompletter Neustart nur wegen der vorgezogenen Checkpoint-Nummer.

Prüfe bestehende Bluteffekte weiterhin gegen die aus **Revision 3** übernommenen Regeln: rückseitiges Blut für Pistolen/MPs in Checkpoint 3; getrennte Eintritts-/Austrittsmaterialfelder und weiterhin kleine Pistolen-/MP-Eintritte mit stabiler Zufallsorientierung in 4; große Austrittswunden für alle vier Gruppen in 5; dieselben Regeln für bereits umgesetzte Leichentreffer in 5a. Entferne alte Pistolen-/MP-Ausschlüsse aus Waffenpolicy, Emittern, visuellen Traces, Decalpfaden, Konfigurations-Defaults und Tests. Ersetze frühere Tests „kein Austritt/kein rückseitiges Blut bei Pistole/MP“ durch die neuen positiven Erwartungen plus die weiterhin gültigen Geometrie-/Hindernis-Negativfälle. Fehlende oder abweichende Punkte jeweils als eigene korrigierte Checkpoint-Revision liefern und abnehmen lassen; nicht alle Korrekturen und neue Features zugleich bauen. Einen noch nicht begonnenen Checkpoint 5a erst nach Abnahme der vorausgehenden Bluteffekte beginnen. Bereits funktionierende Kampagnenarbeit bleibt erhalten und wird danach mitgetestet.

Versioniere die Migration der Waffenpolicy. Beim Laden älterer Mod-Spielstände dürfen archivierte Revision-2-Defaults nicht die neuen Waffenregeln für zukünftige Treffer wieder überschreiben. Erhalte vorhandene Wundinstanzen samt Material, Position und Zufallsorientierung. Erzeuge fehlende historische Austritte oder Weltflecken nicht nachträglich und spiele alte Schussereignisse nicht erneut ab; die neue Freigabe gilt für neue Treffer. Prüfe Savekompatibilität und dokumentiere gegebenenfalls notwendige Schemaanpassungen, ohne Originalspielstände zu verändern.

Für die neue BT-Integration ebenfalls einen klaren Versions-/Migrationspfad dokumentieren. Zukünftige echte Tode in kompatiblen geladenen BT-Saves verwenden die neue Drop-Logik; ältere Leichen bekommen keine nachträglichen Gegenstände. Gespeicherte Skriptzustände am tatsächlichen Engine-Stand prüfen. Ist ein sicherer Wechsel nur beim nächsten Missionsstart möglich, diesen konkret ausweisen und nicht behaupten, der Patch wirke bereits mitten im alten Level. Eine notwendige Missionsneuladung darf nicht die globale Kampagnenprogression löschen.

## Technische Quellen

Die Quellen [S1]–[S8] und die zugehörigen Rechercheangaben wurden aus Revision 4 übernommen; Revision 5 bis 8 enthalten keine erneute Prüfung dieser OpenMoHAA-/MP1-/BT-Patchquellen. Für Revision 8 wurden am 13. Oktober 2026 die öffentlichen WCR-Autorenquellen [S26]–[S29] geprüft, nicht die lokalen Dateien oder Engine-Binärstände. Die Quellen [S9]–[S20] samt Prüfvermerken stammen aus Revision 6. Für Revision 7 wurden am 13. Oktober 2026 zusätzlich die offiziellen Dokumentationen [S21]–[S25] und die AGENTS.md-Dokumentation [S20] geprüft. Die neue Workflowgestaltung ist eine auf dieses Projekt zugeschnittene Vorgabe, keine Behauptung über eine bereits eingerichtete Verbindung oder vorhandene Dateien. [S8] dokumentiert die vom Nutzer vorgegebene Patchherkunft, keinen Downloadauftrag; die lokale Bereitstellung und Prüfgrenzen stehen in Abschnitt 1.3. Die Quellen ersetzen nicht die Prüfung des lokal verwendeten Commits. Die Implementierungsentwürfe, neuen Schemasoll-Felder und Abnahmekriterien in diesem Dokument sind Projektvorgaben; sie sind nicht als bereits vorhandene OpenMoHAA-Funktionen zu verstehen.

[S1] OpenMoHAA-Projektbeschreibung, Singleplayer-Unterstützung und Lizenzhinweise:
`https://github.com/openmoh/openmohaa`

[S2] Offizielle Startdokumentation: Zielspiel, Protokoll, Datenverzeichnisse und `fs_homepath`:
`https://github.com/openmoh/openmohaa/blob/main/docs/markdown/02-running/01-running.md`

[S3] OpenMoHAA-Quelltext: 2D-/HUD-Skalierung, `CG_AdjustFrom640`, `CG_HudDrawElements`:
`https://raw.githubusercontent.com/openmoh/openmohaa/main/code/cgame/cg_drawtools.cpp`

[S4] OpenMoHAA-Quelltext: Special Effects und Human-Uniform-Treffereffekte:
`https://raw.githubusercontent.com/openmoh/openmohaa/main/code/cgame/cg_specialfx.cpp`

[S5] OpenMoHAA-Quelltext: Welt-/Terrain-/Inline-Markierungen und `CG_ImpactMark`:
`https://raw.githubusercontent.com/openmoh/openmohaa/main/code/cgame/cg_marks.c`

[S6] OpenMoHAA-Quelltext: `BulletAttack`, `trace.location`, Schadensweitergabe und `bulletlarge`:
`https://raw.githubusercontent.com/openmoh/openmohaa/main/code/fgame/weaputils.cpp`

[S7] Primärquelle eines MP1-Modprojekts mit dokumentierter Nutzung von RASMaker/rl.dll:
`https://github.com/JasonWei512/Max-Payne-1-Level-Difficulty-Selector`


[S8] Vom Nutzer ausgewählte Patch-Downloadseite: „Medal of Honor: Allied Assault – Breakthrough – Ammo and Health Drops“:
`https://community.pcgamingwiki.com/files/file/2604-medal-of-honor-allied-assault-breakthrough-ammo-and-health-drops/`

Aus Revision 4 übernommener Recherchevermerk vom 13. Oktober 2026: Der Suchindex gab die Beschreibung eines PK3 mit entfernter Dropbegrenzung wieder; direkter Seitenabruf HTTP 403. Revision 5 bis 8 haben die Seite nicht erneut abgerufen und das vom Nutzer angekündigte lokale ZIP nicht eingesehen. Codex verwendet die URL ausschließlich als Herkunftsreferenz und untersucht das lokal bereitgestellte Paket, ohne selbst einen Patchdownload vorzunehmen. Keine bestätigte Aussage zu konkreter Paketversion, internen Skriptpfaden, exakten Dropwerten oder Kompatibilität mit dem festgelegten OpenMoHAA-Commit. Diese Prüfungen sind Bestandteil von 0a. Die verlangte Kontextisolierung, Deduplizierung und Abnahmetests sind eigene Projektanforderungen, nicht Behauptungen über bereits im Drittpatch vorhandene Funktionen.


### Quellen zum Git-/Codex-Workflow – geprüft am 13. Oktober 2026

[S9] OpenAI: Codex CLI, lokale Projektdateien und Werkzeugausführung:
`https://developers.openai.com/codex/cli`
Aktuelle Weiterleitung: `https://learn.chatgpt.com/docs/codex/cli`

[S10] OpenAI: Codex Cloud, Repositoryauswahl, eingerichtete Umgebungen und Review/PR:
`https://developers.openai.com/codex/cloud`
Aktuelle Weiterleitung: `https://learn.chatgpt.com/docs/cloud`

[S11] GitHub: Installation von GitHub Apps, angeforderte Rechte und Auswahl einzelner Repositories:
`https://docs.github.com/en/apps/using-github-apps/installing-a-github-app-from-a-third-party`

[S12] OpenAI Help Center: GitHub in ChatGPT, insbesondere Abgrenzung lesender Repositoryzugriffe zu Codex-Schreibzugriff:
`https://help.openai.com/en/articles/11145903-connecting-github-to-chatgpt`

[S13] GitHub: Sichtbarkeit und Berechtigungen von Forks:
`https://docs.github.com/en/pull-requests/reference/forks`

[S14] Git: Zweck und Grenzen von .gitignore, insbesondere bereits getrackte Dateien:
`https://git-scm.com/docs/gitignore`

[S15] GitHub: Branchschutz, Berechtigungen, Bypass und Verfügbarkeit nach Repositorysichtbarkeit/Tarif:
`https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches`

[S16] Git: Commit als explizites Aufzeichnen eines ausgewählten Quellstands:
`https://git-scm.com/docs/git-commit`

[S17] Git: Push als Übertragung/Aktualisierung von Remote-Referenzen:
`https://git-scm.com/docs/git-push`

[S18] GitHub: Releases, Tags, Binärdateien und automatisch erzeugte Quellarchive:
`https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases`

[S19] Git: Revert durch neue Gegenänderungen, Voraussetzungen und besondere Regeln für Merges:
`https://git-scm.com/docs/git-revert`

[S20] OpenAI: AGENTS.md als Projektanweisung, Hierarchie und Größenbegrenzung:
`https://developers.openai.com/codex/guides/agents-md`
Aktuelle Weiterleitung: `https://learn.chatgpt.com/docs/agent-configuration/agents-md`


### Ergänzende Quellen zur eigenständigen Repository-Pflege – Revision 7

Die beschriebenen Rollen, Freigabegrenzen, Kandidatenbindungen und Testberichte sind Projektvorgaben. Werkzeugdokumentation belegt die verfügbaren Grundoperationen, nicht deren erfolgreiche Ausführung in der noch zu prüfenden Nutzerumgebung.

[S21] OpenAI: lokale Windows-Entwicklungswerkzeuge, Git, GitHub CLI und Anmeldung:
`https://developers.openai.com/codex/app/windows`
Am 13. Oktober 2026 weitergeleitet auf `https://learn.chatgpt.com/docs/windows/windows-app`, Abschnitt „Useful developer tools“.

[S22] GitHub CLI: `gh auth login`, Browseranmeldung, Credential-Speicherung und Token-/Scope-Hinweise:
`https://cli.github.com/manual/gh_auth_login`

[S23] GitHub CLI: `gh repo create`, nichtinteraktive Repositoryanlage, Eigentümer und private Sichtbarkeit:
`https://cli.github.com/manual/gh_repo_create`

[S24] GitHub CLI: `gh pr merge`, erwarteter Kopf-Commit, Merge-Strategien, Auto-Merge und Merge-Queue-Verhalten:
`https://cli.github.com/manual/gh_pr_merge`

[S25] OpenAI: Agent approvals & security, lokale Sandbox, Netzwerkkontrollen und Genehmigungen:
`https://learn.chatgpt.com/docs/agent-approvals-security`


### Ergänzende Quellen zu War Chest Restored – Revision 8

Öffentliche Autorenangaben, am 13. Oktober 2026 gelesen. Die konkreten Integrationsregeln, Schemasoll-Felder und Tests sind Projektvorgaben. Sie behaupten weder einen nachgewiesenen lokalen Dateikonflikt noch eine bestimmte installierte Fassung. Moddb-Beschreibungen ersetzen nicht die örtlichen Readmes, Archive und Laufzeitnachweise. Keine WCR-Archive wurden für diese Planrevision heruntergeladen oder ausgeführt.

[S26] Metlar: „Introduction“, 4. April 2026; Inhaltsbereiche, UI/Optionen, optionale Inhalte und OpenMoHAA-Anpassung:
`https://www.moddb.com/mods/war-chest-restored/news/introduction127`

[S27] Metlar: „Version 1.1 Released“, 30. April 2026; insbesondere restaurierte BT-Endsequenz sowie Modell-/Animationsänderungen:
`https://www.moddb.com/mods/war-chest-restored/news/version-11-released19`

[S28] Metlar: „War Chest Restored Patch v1.1.1“, 20. Mai 2026; Teilupdate, Briefing-/Save- und globale Skriptkorrekturen:
`https://www.moddb.com/mods/war-chest-restored/downloads/war-chest-restored-patch-v111`

[S29] Projektübersicht und Autorenkommentare vom 3. Oktober 2026 zum MG42-/OpenMoHAA-Fall; Dateiliste als öffentlich sichtbare Versionsreferenz, nicht als lokaler Installationsnachweis:
`https://www.moddb.com/mods/war-chest-restored`
