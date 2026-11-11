# CP08-r1: 16:9-Hintergruende, erstes Teilpaket

Nachtrag: Die folgende Beschreibung ist der historische Stand des ersten Teilpakets. Nach neuer Nutzerfreigabe werden jetzt alle SH-/BT-Kampagnenladebilder ohne KI proportional vergroessert; siehe [Loading Zoom](loading-zoom.md). Die Outpainting-Warteliste bleibt davon getrennt.

Zwischenstand 15.10.2026: Zwoelf visuell gepruefte Gemini-/Nano-Banana-Erweiterungen sind lokal eingebaut. Der Gesamtauftrag ist noch nicht abgeschlossen. Gemini verweigerte den naechsten Bildauftrag wegen des Kontingents und zeigte als Ruecksetzzeit den 15.10. um 00:32 Uhr an. Es wurden keine parallelen Generierungsanfragen und keine Upgrades ausgefuehrt.

Enthalten sind die Hauptmenues von AA, SH und BT, der dunkle AA-Briefingraum mit seinen bestehenden Projektionsfolien, der helle AA-Missionsraum, das AA-Optionshauptmenue sowie sechs AA-Ladebilder: m1l1, m1l2a, m1l2b, m1l3a, m2l1 und m2l3. Gemeinsame Briefingressourcen werden in den Erweiterungen wiederverwendet. Die vorhandene Einsatzkarte bleibt der Hauptmenue-Kartenaufruf.

Die lokale Arbeitsliste enthaelt insgesamt 48 ausgewaehlte Hintergruende; 36 sind noch offen. Dazu gehoert eine erneute Korrektur von m2l2a, dessen angeschnittenes Foto Gemini zweimal nicht passend fortgesetzt hat. Fehlgeschlagene Bilder werden nicht eingebaut. Die absichtlich schwarz umrandeten neun SH-Ladebilder und drei SH-Filmrahmen wurden geprueft und beibehalten; BT-Ladebilder sind wie beauftragt ausgeschlossen. Schwarze Platzhalter, Kalibrierungs-/Testbilder, kleine Netzwerkdialoge und Hilfs-/Textflaechen gehoeren nicht zur Outpainting-Liste.

## Darstellung und lokale Verarbeitung

Die Engine zeichnet ausschliesslich die generierten linken und rechten Seiten um das weiterhin originale 4:3-Zentrum. Originaltexturen, Texte, Buttons, Hoverbereiche, animierte Einblendungen und Missionsinformationen bleiben bestehen. Der Packager fuegt jeder betroffenen Menuewurzel nur eine `widescreenbackground`-Direktive hinzu und prueft die unveraenderten restlichen Quelldaten. Der Standard `r_loadjpg=1` wird bei der Vorlagenrekonstruktion beruecksichtigt, damit SH-/BT-JPGs die geerbten AA-TGAs korrekt ersetzen.

Die Gemini-Vorlage ist eine 1536x864-Flaeche mit dem Original in der Mitte und weissen Seitenstreifen. Nur gepruefte und SHA-256-verifizierte Ergebnisse kommen in die lokalen PK3-Dateien. 4:3 zeichnet keine Erweiterungen, 16:10 beschneidet die Seiten am Bildschirmrand, Ultrawide behaelt ein mittiges 16:9-Bild. Diese Aenderung fuegt kein neues Spielmenue hinzu und veraendert keine Spracheinstellungen.

## Pruefungen und Grenzen

- Nativer RelWithDebInfo-Build erfolgreich. Zwoelf Hintergruende in AA/SH/BT visuell kontrolliert; abschliessender AA-Lauf mit zehn Hintergruenden und Einsatzkarte ohne Ressourcen-/Layoutfehler. Installierte Fassung in allen drei Spielkontexten mit getrennten Testprofilen gestartet.
- Full HD, 1024x768, 1680x1050 und 2560x1080 getestet. AA-Hauptmenue und Briefing in 4:3 sowie das Briefingzentrum in Full HD sind pixelgenau gleich der Referenz. Beim Ladebild unterscheiden sich nur Bildpunkte der animierten Ladeanzeige. In den SH-/BT-Hauptmenuezentren unterscheiden sich nur Bildpunkte des originalen laufenden Ventilators.
- 9.072 Originaldateien, 9.000 Laufzeit-Basisdateien, acht erfasste MP1-Dateien und alle 26 Dateien des aktiven Nutzerprofils unveraendert. Vorhandene Laufzeitdateien und Manifest wurden vor dem Einbau unabhaengig gesichert. Keine Spielstands-/DLL-API-Aenderung.
- Fruehe Versuche mit sichtbarer Konsole, falschem Menueaufruf, schwarzem Shader oder unpassenden Gemini-Bildern sind Diagnosen und keine bestandenen Tests. Ein Test verwendete faelschlich `pushmenu ac_campaign`; der korrigierte Lauf benutzt `ac_campaign` und prueft `ac_campaign_operations`.
- Die Spieltests pruefen Darstellung und Menueintegration, keinen neuen vollstaendigen Kampagnendurchlauf. Kleine Unterschiede in Beleuchtung/Details an einzelnen generierten Uebergaengen koennen sichtbar bleiben. Keine persoenliche Abnahme und kein Merge.

Maschinenlesbarer Nachweis: [widescreen-art-verification.json](widescreen-art-verification.json). Originalbilder, Gemini-Ausgaben, PK3-Dateien, Screenshots und ZIPs bleiben ausschliesslich in ignorierten lokalen Ordnern.

## Start, Sicherung und Fortsetzung

Weiterhin `Start-CP08-r1.cmd` verwenden. Die zwoelf fertigen Erweiterungen sind im bestehenden Laufzeitstand enthalten. Das lokale Screenshot-ZIP heisst `artifacts-local/CP08-r1-Widescreen-batch1-Screenshots.zip`; das lokale Updatepaket heisst `artifacts-local/CP08-r1-widescreen-batch1-update.zip`. Beide enthalten Spielgrafiken und duerfen nicht nach GitHub hochgeladen werden.

Die Rueckrollkopie liegt unter `generated-local/widescreen/backups/widescreen-batch1`: vorherige EXE und Manifest sowie eine Liste der vorher nicht vorhandenen PK3-Dateien. Die Fortsetzung verwendet `generated-local/widescreen/effective/queue.json`, `pending.json`, `approved.json`, `rejected.json` und `progress.json`. Bereits gepruefte Bilder nicht erneut generieren; auch weiterhin nur einen Gemini-Bildauftrag gleichzeitig starten. Nach weiteren Bildern neu paketieren und in isolierten Profilen pruefen. Der Gemini-Tab bleibt fuer die Fortsetzung erhalten; es ist keine automatische spaetere Ausfuehrung eingerichtet.
