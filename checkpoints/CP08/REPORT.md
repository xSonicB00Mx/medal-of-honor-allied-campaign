# CP08-r1 – gemeinsame Einsatzkarte

Neueste Erweiterung: [Briefing Room und einzelne Level wiederholen](level-replay.md).

Fruehere Korrektur: [MG-Ruckler und entfernter Kartenhinweis](mg-feedback.md).

Aktueller Stand: [Zwei Regionen, unsichtbare gesperrte Einsaetze und Sterbeanimationstreffer](feedback-two-regions.md). Der folgende Bericht dokumentiert den urspruenglichen CP8-Kandidaten; sein sechs-Ansichten-/vier-Zustaende-Layout wurde durch das neue Feedback ersetzt.

Technischer Kandidat auf CP7 mit einer geografisch belegten Uebersicht und fuenf regionalen Ausschnitten. Alle 15 Einsaetze, ihre Daten, Orte, Originalspiele und Protagonisten kommen aus dem gemeinsamen Manifest. Drei Normandy-Einsaetze teilen einen Ortsanker und bleiben ueber Marker und regionale Liste einzeln erreichbar. Previous/Next bietet einen zusaetzlichen vollstaendigen Auswahlweg.

Die Karte verwendet Natural-Earth-Kuesten und GeoNames-Regionanker in einer einheitlichen Mercatorprojektion. Unbekannte/fiktive Ziele werden als ungefaehre Regionen bezeichnet. Keine politischen Grenz- oder Frontbehauptungen. Sechs 2240 x 1320 Hintergrundbilder enthalten weder Texte noch Missionsmarker; alle Bedienelemente werden nativ gerendert. Quellen, Lizenzen und Einschraenkungen: `mod/campaign/GEOGRAPHY.md`.

## Implementierung und Pruefungen

Die vier Zustaende sind farblich und textlich unterscheidbar. Ein begonnener aktueller Einsatz mit gespeichertem Fortsetzenpunkt ist Available, ein noch nicht begonnener Nachfolger Next. Einzelmarker verwenden zusaetzlich L/A/C/N. Gesperrte Einsaetze lassen sich ansehen, aber nicht starten. Replay kehrt zur Karte zurueck. Der Haupt-Fortsetzen-Save ist gegen gleichnamiges Ueberschreiben aus Replay oder optionalen Abschnitten geschuetzt.

Native UI-Laeufe pruefen alle 15 Auswahlen pro Aufloesung: 1920 x 1080, 3840 x 2160, 1280 x 960 (SH) und 3440 x 1440 (BT). Root-Geometrie ist proportional und mittig, alle Screenshots besitzen die angeforderte Framebuffergroesse. Regionsansichten und das vorhandene Optionsmenue wurden visuell kontrolliert. Die fruehen Aufnahmen zeigten alte Bildreste ausserhalb des 16:9-Menues; eine vollstaendige Hintergrundfuellung behebt sie in den clean-Laeufen. Kein physischer Monitor-/DPI-Umschalttest behauptet.

Die dynamische Menueerneuerung ersetzt nur ihren eigenen Widgetbaum; andere WCR-Menues bleiben erhalten. Wiederholte Auswahl aller Eintraege lief ohne Menuefehler. Ein Kontrolltest schuetzt die echten Bytes eines Haupt-Speicherplatzes sowohl bei Replay als auch beim optionalen m4l0-Einstieg. Uninitialisierte Effektoptionen werden nicht als leere Werte weitergegeben; ihre Standardwerte sind bereits vor dem ersten Kontextwechsel registriert.

`validate_campaign.py` prueft ohne Originalassets alle 54 Kartenabschnitte, die Reihenfolge, die Headerkonsistenz, alle 90 projizierten Markerpositionen und die vollstaendige Abdeckung der Ausschnitte durch die Kuestendaten. Native End-to-End-/Speicherberichte liegen daneben. Testprofile und deren Freischaltungen werden nicht ins Nutzerprofil uebernommen.

## Grenzen

Der native Fortsetzen-Test (`resume-e2e.json`) beginnt Operation Torch, durchlaeuft das Originalbriefing bis m1l1 und sichert den Fortsetzenpunkt. Nach normalem Beenden und einem vollstaendigen Neustart im SH-Kontext wechselt Continue Campaign nach AA und laedt diesen Spielstand mit unveraendertem Fortschritt und FOV 90. Eine nur lokal und voruebergehend eingesetzte Test-Briefingdatei steuert Diagnose/Beenden; sie wurde entfernt und ist nicht Bestandteil des Kandidaten. Die abschliessenden vier UI-Laeufe (`final-*.json`) pruefen die letzte Menuefassung; Full-HD-Einsatzkarte und Allied Campaign Options wurden als echte Spiel-Screenshots visuell geprueft.

Die natuerliche Gesamt-Gameplayabnahme ist weiterhin offen. Die 15 CP7-Grenztests verwenden synthetische native Intermissions und ersetzen keinen Durchlauf aller 53 Hauptabschnitte. Die separat gemeldeten Entwicklungsdiagnosen wurden auch mit der CP6-Basis reproduziert; deren Gameplayauswirkungen sind nicht pauschal entkraeftet. Der vom Nutzer uebersprungene vollstaendige BT-Finaltest bleibt offen, ebenso die gesamte kombinierte WCR-/Drop-/Tod-/Ladematrix. Das ist kein als vollstaendig bestanden ausgegebener CP9-Regressionslauf. Keine persoenliche Abnahme und kein Merge.
