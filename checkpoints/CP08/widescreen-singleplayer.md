# Widescreen-Fortsetzung: Single-Player

Installiert sind jetzt 42 von 45 ausgewaehlten Single-Player-Hintergruenden, davon 30 zusaetzlich zum bisherigen Zwoelferpaket. Drei AA-Ladebilder (m4l1, m4l2, m5l2) bleiben original: Gemini hat diese Vorlagen abgelehnt. Der Bildauftrag ist deshalb ein dokumentiertes Teilpaket, kein vollstaendiger Abschluss. Die Kampagnenstatistik behaelt ihr gerahmtes Originalfoto mit seitlicher Album-Papierflaeche.

Das finale Paket `widescreen-sp-final` ist installiert. 9.072 Originaldateien, 9.000 Basisdateien, acht MP1-Eingaben und alle 80 Nutzerdateien blieben hash-identisch. Separate native Nachtests des installierten Pakets bestanden in AA, SH und BT.

Auf Wunsch werden keine Multiplayer-Bilder erweitert. Inventarisierung und Paketierung filtern entsprechende UI-Ressourcen; alle drei erzeugten Bildpakete wurden auf ausgeschlossene Multiplayer-Ressourcen kontrolliert. Die separat getestete Multiplayer-Sperre und Jeep-MG-Korrektur sind unter [singleplayer-jeep.md](singleplayer-jeep.md) dokumentiert.

Gemini wurde mit 3.8 Flash und Denkaufwand High verwendet. Jede Generierung erhielt einen neuen Chat; zu keiner Zeit liefen zwei Bildanfragen gleichzeitig. Die lokale Freigabeliste speichert fuer jedes Ergebnis seine eigene Chatadresse, SHA-256 und Sichtpruefung. Wiederverwendet werden nur identische Seiten eines gemeinsamen Motivs: Die Breakthrough-Briefingvariante ohne Schaltflaechen unterscheidet sich ausschliesslich im erhaltenen Originalzentrum.

Originale Bildzentren und UI-Bindungen bleiben erhalten. SH-/BT-Ladebilder verwenden weiterhin das zuvor gelieferte proportionale Zoomverfahren ohne KI. Kleine Beleuchtungs- und Detailunterschiede zwischen Original und generierten Seiten koennen sichtbar bleiben, insbesondere bei originalen dynamischen Hervorhebungen. Vollstaendige Pixelidentitaet der gesamten Widescreen-Flaeche wird nicht behauptet.

Unpassende Ergebnisse werden nicht eingebaut. Dazu gehoerten abweichendes Tischmaterial, neue dunkle Vignetten, abbrechende Fotokanten und zu scharf gezeichnete Seiten um gemalte Abschlussbilder. Technische Gemini-Fehler und Anbieterablehnungen sind getrennt erfasst. Abgelehnte Vorlagen werden nicht mit veraenderten Sicherheitsvorgaben erneut angefragt.

Die nativen Darstellungspruefungen verwenden getrennte Profile. Zwei fruehe Ladebildlaeufe verwendeten falsche Menuebezeichnungen; die korrigierten Laeufe lesen bzw. verwenden die tatsaechlichen Ressourcennamen. Ein zusaetzlicher Statistiklauf verdeckte das zweite Fenster durch das erste; das Kampagnenfoto wurde danach separat sichtbar geprueft. Fehlversuche sind im maschinenlesbaren Bericht als Diagnosen erfasst, nicht als bestandene Tests. Diese Tests sind Darstellungs-/Integrationspruefungen, kein neuer vollstaendiger Missionsdurchlauf.

Aktueller Umfang und Einzelpruefungen: [widescreen-singleplayer-verification.json](widescreen-singleplayer-verification.json). Grafiken, Originaldaten, Spielstaende und vollstaendige lokale Protokolle bleiben von Git ausgeschlossen. Persoenliche Abnahme und Merge bleiben offen.

Start weiterhin mit `Start-CP08-r1.cmd`. Lokale Rueckrollkopien liegen unter `generated-local/widescreen/backups/`. Neue Spielaufnahmen und Jeep-Nachweise werden in `artifacts-local/CP08-r1-Widescreen-Singleplayer-Screenshots.zip` gebuendelt.
