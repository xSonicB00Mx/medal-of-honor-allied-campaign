## Aktuell: Hochaufloesende Stoppuhr und Zuendschnur

Nachkorrektur timers-r2 installiert: Metallkante entfernt und Seilmaterial am Anschluss vereinheitlicht; beide Varianten im UHD-HUD geprueft.

Fuenf Grafikebenen installiert, Zeigermittelpunkte und Schnuranschluss ausgerichtet. AA/SH/BT bei UHD/HUD 1.66 geprueft; Funken-/Rauchanimation und Countdown-Logik erhalten. [Bericht und Prompts](checkpoints/CP08/timer-upscale.md).

## Aktuell: Hochaufloesende Lebensanzeige

Vier abgestimmte Ebenen mit 128x512 Pixeln installiert. AA/SH/BT bei UHD und HUD 1.66 mit verschiedenen Gesundheitsstaenden und Aenderungsblitz geprueft; Spielstaende unveraendert. [Bericht, Prompts und Testgrenzen](checkpoints/CP08/health-upscale.md).

## Aktuell: Hochaufloesende Inventarsymbole

Nachkorrektur inventory-r3: Handbuch jetzt mit deutscher Beschriftung und originalnahem Layout; siehe [Bericht](checkpoints/CP08/inventory-manual-r3.md).

Vorherige Nachkorrektur inventory-r2: Drahtschneider mit korrekten Schneiden und Tiger-II-Handbuch mit Panzerzeichnung. UHD/HUD 1.66 visuell geprueft; Spielstaende und Einstellungen unveraendert.

15 Gegenstandsmotive und 32 Zaehlervarianten mit 512x512 Pixeln installiert; AA/SH/BT bei UHD und HUD 1.66 geprueft. Originalpositionen, Transparenz und Inventarlogik bleiben erhalten. Zwei Ausweise und drei Uniformen bleiben wegen Ablehnungen des Bilddienstes im Original. [Umfang, Prompts und Tests](checkpoints/CP08/inventory-upscale.md).

## Aktuell: Hochaufloesende Munitionsanzeige

19 Munitions- und Spezialanzeigen aus 18 transparenten Imagegen-Vorlagen vorbereitet. Originalgroessen und Patronenabstaende bleiben durch angepasste Texturkachelung erhalten. [Bericht und Testgrenzen](checkpoints/CP08/ammo-upscale.md).

## Aktuell: Hochaufloesender Kompass

Kompass nach Nutzerfeedback korrigiert: transparente Rose statt zweiter geschlossener Scheibe, einheitliche Proportionen und gemeinsamer Mittelpunkt mit dem runden Gehaeuse. Mehrere Blickrichtungen bei UHD/HUD 1.66 geprueft. [Bericht](checkpoints/CP08/compass-upscale.md). Multiplayer-Grafiken ausgenommen.

## Aktuell: Courier New fuer Menues und HUD

Courier New Bold jetzt mit natuerlichen Zeichenbreiten, Originalfarben und kleinem Schlagschatten. Engstellen in HUD, Steuerung, Zahlenfeldern und Mission List angepasst; native Menuepruefungen in AA/SH/BT sowie 4:3. [Umfang und Nachweise](checkpoints/CP08/courier-fonts.md).

## Aktuell: Mission List Highscore-Modus

Level-Complete zeigt das vorhandene Gemini-16:9-Bild mit Helm und Sonnenuntergang; der Statistikblock steht auf Nutzerwunsch links. Proportionale Darstellung bleibt erhalten; siehe denselben Bericht.

Getrennte Rekorde fuer Easy/Medium/Hard, letzter Levelscore, native Kampfwertung und Abschlussstatistik. Speichern/Laden waehrend eines Laufs gesperrt. [Regeln und Nachweise](checkpoints/CP08/highscore.md).

## Aktuell: Gesperrte Levels und Briefing-Auswahl

Alle Levelplaetze bleiben sichtbar; nicht abgeschlossene Levels sind rot als LOCKED gesperrt. Briefing Room bietet die wachsende Auswahl freigeschalteter Originalbriefings. [Bericht](checkpoints/CP08/unlock-menus.md).

## Aktuell: Briefing Room und einzelne Level wiederholen

Briefing Room folgt dem regulaeren Fortschritt. Mission List zeigt abgeschlossene Einzel-Levels mit Schwierigkeit je Start; Replay endet im Hauptmenue und schuetzt Kampagnenfortschritt/Saves. Native Tests und Grenzen: [Bericht](checkpoints/CP08/level-replay.md).

## Aktuell: Einheitliche Hauptmenue-Schriftzuege

Acht weitere transparente Beschriftungen im freigegebenen Operations-Stil erzeugt und fuer AA/SH/BT eingebaut. Native Bildtests bestanden; Operations-Ausrichtung erhalten. [Bericht und Prompts](checkpoints/CP08/menu-lettering.md).

## Aktuell: Operations-Schriftzug und Kopfzeile

Reset Progress oben rechts; Previous/Next entfernt. Transparenter OPERATIONS-Schriftzug mit dem eingebauten Bildgenerator im Stil der Originalschilder erstellt. [Prompt und Bericht](checkpoints/CP08/operations-sign.md).

## Aktuell: Operations und Reset Progress

Hauptmenue-Schild zeigt Operations. Reset Progress in der Einsatzkarte verlangt eine separate Bestaetigung und behaelt Saves/Optionen. Isolierte Tests pruefen Abbrechen, Reset und Neustart; aktiver Nutzerfortschritt bleibt unberuehrt. [Bericht](checkpoints/CP08/operations-reset.md).

## Aktuell: AA-Medaillen in 16:9

Medaillenkasten und Reset-Dialog auf 960x540 angepasst, Medaillen proportional erhalten. Native Full-HD- und 4:3-Tests bestanden. [Bericht](checkpoints/CP08/aa-medals-wide.md).

## Aktuell: Restbilder fuer Single-Player

46 vollstaendige Hintergruende fertig; AA-Hilfeseite mit Gemini 3.8 Flash / High ergaenzt. Drei vorhandene breite SH-Abschlussgemaelde werden mit unveraenderten Einblendzeiten bildfuellend dargestellt. Native Sichtpruefungen bestanden. Multiplayer- und Kalibrierungsbilder bleiben ausgenommen. [Bericht](checkpoints/CP08/remaining-art.md).

## Aktuell: Gemeinsame Kampagnenoptionen

Grafik, Audio, Maus-/Joysticksteuerung, HUD und normale/Alt-/Strg-Belegungen werden gemeinsam gespeichert. Native AA -> SH -> BT -> AA-Wechsel und drei Neustarts bestanden; Spielstandszeiger und Missionsstatistik bleiben getrennt. [Bericht](checkpoints/CP08/shared-preferences.md).

## Aktuell: Vollstaendige 16:9-Hintergruende

Alle 45 ausgewaehlten Hintergruende verwenden jetzt das vollstaendige Bild ohne Originalzentrum. Drei neue Ladebilder stammen direkt vom Nutzer (m4l1, m4l2, m5l2). Bedienelemente bleiben unveraendert; die optische Menueausrichtung beurteilt der Nutzer im Anschluss. [Bericht](checkpoints/CP08/widescreen-fullframe.md).

## Aktuell: Widescreen-Single-Player-Paket installiert

42 von 45 ausgewaehlten SP-Hintergruenden sind fertig und installiert, 30 davon neu. Gemini 3.8 Flash / High, neue Chats und serielle Generierung. Drei AA-Vorlagen wurden von Gemini abgelehnt und bleiben original; keine Multiplayer-Bilder erzeugt. AA-/SH-/BT-Nachtests bestanden, Originale und alle 80 Nutzerdateien unveraendert. [Bericht und offene Bilder](checkpoints/CP08/widescreen-singleplayer.md). SH-/BT-Ladezoom bleibt erhalten.

## Aktuell: Single-Player und Jeep-MG

Multiplayer ist in AA, SH und BT nicht mehr anwaehlbar; alternative Menue-, Verbindungs- und Kartenaufrufe werden abgewiesen. Das echte m1l3a-Jeep-MG erzeugt jetzt die freigegebenen Bluteffekte. Native Tests bestanden, in CP08-r1 installiert, 80 Nutzerdateien unveraendert. [Bericht](checkpoints/CP08/singleplayer-jeep.md). Gemini-Bildarbeit wird mit 3.8 Flash / High und einem neuen Chat pro Bild fortgesetzt; Multiplayer-Bilder sind ausgeschlossen.

## Aktuell: SH-/BT-Ladebilder vergroessert

Alle neun SH- und elf BT-Kampagnenladebilder werden auf Breitbild proportional vergroessert und zentriert. Motive, Fotorand und Ladeanzeige bleiben erhalten; in 4:3 bleibt der urspruengliche Ausschnitt. In CP08-r1 installiert, elf isolierte native Prueflaeufe bestanden. Keine neuen KI-Bilder erforderlich. [Nachweise](checkpoints/CP08/loading-zoom.md). Die 36 weiteren Gemini-Hintergruende des vorherigen Auftrags bleiben offen.

## 16:9-Bilder, vorheriges Teilpaket

Zwoelf Gemini-/Nano-Banana-Erweiterungen sind im CP08-r1-Startstand eingebaut: drei Hauptmenues, AA-Briefing-/Missionsraum, AA-Optionshauptmenue und sechs AA-Ladebilder. Originalzentren und Bedienelemente bleiben erhalten. 36 weitere ausgewaehlte Hintergruende sind offen; Gemini meldete ein Kontingentlimit bis 15.10.2026, 00:32 Uhr. Kein vollstaendiger Abschluss des Bildauftrags. [Umfang, Nachweise und Fortsetzung](checkpoints/CP08/widescreen-art.md).

## Aktuelle Korrektur: MG-Ruckler

Der Kartenhinweis ist entfernt. Lokale Wundreferenzen verhindern den bei MG-Dauerfeuer reproduzierten Nachrichtenstau. Drei MG-Nachtests halten 50-ms-Snapshots; Save/Load und 36 AA-/SH-/BT-Durchschussvergleiche bestanden. [Bericht und Grenzen](checkpoints/CP08/mg-feedback.md).

## Aktuelles Feedback: CP08-r1

Hauptmenue-Karte ersetzt die alte Missionsauswahl; nur zwei Regionen und ausschliesslich freigeschaltete Einsaetze. Blut/Wunden waehrend der Sterbeanimation mit durchdringenden Kugeln. 72 gepaarte Schadensvergleiche in sechs nativen Laeufen bestanden. [Aenderungen, Nachweise und Grenzen](checkpoints/CP08/feedback-two-regions.md). Die folgenden sechs-Ansichten-/vier-Zustaende-Angaben beschreiben historische Staende.

## Fortsetzung bis CP8

CP6 bis CP8 sind als technische Kandidaten implementiert. CP6-/CP7-CI bestanden; alle 54 Karten starten mit Save-Ausgabe. CP7: 15 synthetische Abschlussgrenzen mit korrektem Fortschritt, getrennte Wiederholungen, Save-Metadaten und Wiederherstellung. CP8: geografische Einsatzkarte mit 15 Operationen, vier Zustaenden und sechs Ansichten; native Menuepruefungen in Full HD, 4K, 4:3 und Ultrawide bestanden. Continue Campaign und FOV 90 ueber Programmneustart und SH-zu-AA-Wechsel bestaetigt. [Start](CP08-r1-START.md), [Nachweise und Grenzen](checkpoints/CP08/REPORT.md). Natuerliche Vollabnahme bleibt offen.

# Status

Aktueller Auftrag: autonom bis einschliesslich CP8. Missionslader, chronologische Progression und Einsatzkarte sind implementiert und technisch geprueft. Persoenliche Abnahme, vollstaendiger natuerlicher Kampagnendurchlauf und Merge werden nicht unterstellt. Die folgenden Eintraege dokumentieren vorherige Lieferstaende.

Stand 14.10.2026 nach Menuefeedback: **CP05a-r3 benennt das gemeinsame Zusatzmenue in Allied Campaign Options um und liefert ein mittiges 16:9-Layout ohne ueberlappende Bedienelemente.** [Startdateien](CP05a-r3-START.md), [Pruefbericht](checkpoints/CP05a/r3/REPORT.md). Getrennte Bereiche fuer Display/HUD und Effekte; die Seite bleibt beim Verstellen ihrer Regler stabil. 56 Nutzerdateien aus r2 uebernommen. Quelle `5a9b6aa7e9877d4fb3dd328838d9ab4940deb5ce` remote verifiziert. Keine persoenliche Abnahme oder Merge unterstellt.

Stand 14.10.2026 nach BT-Strassenfeedback: **CP05a-r2 korrigiert fehlende Blutspuren auf der erdigen Strasse im Breakthrough-Test.** [Startanleitung](CP05a-r2-START.md), [Vorher/Nachher und Pruefbericht](checkpoints/CP05a/r2/REPORT.md). Die sichtbare gekruemmte Strasse lag knapp unter der Kollisionsflaeche; die begrenzte Projektion gleicht dies jetzt aus. 47 Nutzerdateien aus CP05a-r1 uebernommen. Quellstand `a3c13d93689f47044c5fa6e79ea10b723135c162` frisch remote verifiziert. Persoenliche Abnahme und Merge bleiben offen.

Stand 14.10.2026 nach weiterem Nutzerfeedback: **CP05a-r1 liefert 30 Sekunden sichtbares und 1,5-mal groesseres Weltblut, korrigierte Boden-/Wandprojektion und optische Leichentreffer in AA/SH/BT.** [Neue Startanleitung](CP05a-r1-START.md), [Pruefbericht und Grenzen](checkpoints/CP05a/REPORT.md). 47 Einstellungs-/Spielstandsdateien aus r2 wurden unveraendert uebernommen. Quellstand `08e6aba4aabb7e9d9cafa50d9df0e7f6118dd571` ist auf GitHub frisch verifiziert; Entwurfs-PR #8. Die neueste Nutzeranweisung erweitert die fruehere CP5-Grenze um Leichentreffer. Persoenliche Abnahme, vollstaendige Checkpointmatrix und Merge bleiben offen.

Stand 14.10.2026 nach Nutzerfeedback: **CP05-r2 korrigiert sichtbare MP1-Partikel/Weltflecken, die Charakterbeleuchtung der Wunden und die Zentrierung der Briefings.** [Neue Startanleitung](CP05-r2-START.md), [Korrekturbericht](checkpoints/CP05/r2/REPORT.md). Einstellungen und Saves aus r1 wurden in ein getrenntes Profil kopiert; r1 und Originaldaten bleiben unverändert. Der Korrektur-Quellstand `89437fe58fc41a4d11b21e0a762560bced56c12a` wurde auf GitHub frisch verifiziert. Persönliche Abnahme und Merge bleiben offen.

Vorheriger Stand 14.10.2026: **Die Features bis einschließlich CP5 sind als CP05-r1 implementiert und lokal spielbereit.** Vollständige technische Abnahme, persönliche Nutzerabnahme und Merge sind getrennt davon und bleiben offen. Die autonome Fortsetzung bis CP5 sowie englische Spieloptionen wurden im Chat freigegeben. Keine weitere „mach weiter“-Bestätigung erforderlich; CP5a und Kampagnenarbeit bleiben außerhalb des Auftrags.

Vorheriger Einstieg: [CP05-r1 starten](CP05-r1-START.md). Quellstand der Engine: `c0f6342352b2971f52c462574e528f58edf9220b`. [CP5-Bericht](checkpoints/CP05/REPORT.md) und die zugehörigen JSON-Nachweise enthalten Binärhashes, Testbedingungen, lokale Paketsicherung und Grenzen.

| Bereich | Lieferstand |
| --- | --- |
| CP1 | HUD-/Schriftskalierung, proportionale Menüs/Kompass, sichere Ränder und gespeicherte Größen; neue Spieloptionen Englisch. Erneut geprüft in AA 4K, SH Full HD und BT Ultrawide, einschließlich Save/Load. |
| CP2 | Roter menschlicher Treffernebel; genaue gemeinsame Waffenfreigabe, gespeicherter eigener Schalter. |
| CP3 | Originale lokale MP1-Bluttexturen, kollidierende Tropfen und präzise Weltflecken; aktuelle Zielkörper/Ausrüstung blockieren im CP5-Stand zusätzlich geometrisch. |
| CP4 | Kleine Pistolen-/MP-Eintritte, große Gewehr-/MG-Eintritte, deformierbare Meshbindung und unveränderte gespeicherte Wundorientierungen. |
| CP5 | Große geometrisch bestätigte Austritte für alle vier Gruppen, getrennte Zufallsorientierung, begrenzte Arm-/Streifintervalle und kompatibles Lesen von CP4-Wundsaves. |

Echte native Schüsse aus drei Richtungen in allen drei Spielkontexten, Regionen-/Wand-/Todestests, getrennte Effektschalter, Schrotflinten-Ausschluss und Save-Migration sind dokumentiert. Der isolierte Transformationslauf umfasst 65.536 Seeds. Die echten Startdateien teilen alle sieben UI-/Effekteinstellungen zwischen AA, SH und BT; die neuen Nutzerprofile stehen wieder auf Standardgrößen, aktivierten Effekten und FOV 90.

Verbleibende Grenzen: keine vollständige Kombination sämtlicher WCR-Varianten und aller Waffen, keine umfassende Mehrgegner-/Hindernis-Lastmatrix, kein vollständiger deterministischer End-to-End-Nachweis aller Gameplay-Zufallsfolgen, keine echten Windows-DPI-/Alt-Tab-Wechsel und kein GL2-Test. Frühe Diagnosen und fehlgeschlagene Teiltests sind in den Berichten ausdrücklich als solche gekennzeichnet. Keiner dieser Punkte wird als bestanden ausgegeben.

Originalinstallation, _forCodex, MP1-Eingaben und ältere Kandidaten bleiben unverändert. CP05-r1 besitzt ein CRC-/SHA-geprüftes lokales Laufzeitpaket; Originalassets und Saves werden nicht nach GitHub übertragen. CP0a-Drops bleiben integriert; der vom Nutzer übersprungene BT-Finaltest wurde nicht nachträglich als bestanden erklärt.

Privates Projekt: Entwurfs-PRs #1 CP0, #2 CP0a, #3 CP1, #4 CP2, #5 CP3, #6 CP4 und #7 CP5. Keine Merges ausgeführt. Push-/CI-Nachweise und abschließende Sicherung werden unter CP05 geführt.
