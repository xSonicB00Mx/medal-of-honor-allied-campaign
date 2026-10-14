# Status

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
