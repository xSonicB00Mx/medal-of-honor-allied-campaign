# CP06-r1 – gemeinsamer Missionslader

Technischer Kandidat auf Basis CP05a-r3. Die neue Missionsoberflaeche ist aus den drei erhaltenen WCR-Hauptmenues erreichbar. Sie bietet 54 inventarisierte Kartenabschnitte sowie die drei Save-Oberflaechen. Native Karten-IDs sind hier absichtlich sichtbar; chronologische Freischaltung und historische Karte folgen in CP7/8. Alle bisherigen Hauptmenueaktionen bleiben erhalten.

## Kontextwechsel

Ein Wechsel startet dieselbe gemeinsame OpenMoHAA-Binaerdatei intern neu. Der neue Prozess wartet vor Dateisystem-/Spielinitialisierung auf das Ende des alten. Das ist eine sichtbare Ladeunterbrechung, kein nahtloser Wechsel im selben Prozess und kein Start einer Original-EXE. Der erste Versuch, die Systeme innerhalb desselben Prozesses neu zu initialisieren, scheiterte nach der Audioinitialisierung. Er ist als `lifecycle-01.json` dokumentiert und nicht Bestandteil der gelieferten Implementierung.

Zielspiel, Protokoll und Suchpfade werden beim frischen Prozessstart gesetzt. WCR bleibt titelbezogen geladen, der Drop-Merge nur in BT. Tastaturbelegung und gemeinsame Darstellungs-/Effektwerte werden beim Wechsel uebergeben. Vorherige NPC-, Wund-, Shader-, Modell- und Audiozustande bleiben nicht im Speicher des neuen Prozesses. Die Startargumentkapazitaet wurde von 32 auf 64 erhoeht, da die alte Grenze den Zielkartenbefehl abgeschnitten hatte.

Neue Saves erhalten eine `ACM1`-Metadatendatei mit Spielkontext, WCR-/Drop-Inhaltsfingerprint, Patchprofil und Karte. Im gemeinsamen Kampagnenmodus werden nicht zugeordnete oder widerspruechliche Saves vor dem Laden abgewiesen. Aeltere Kandidaten und deren Nutzerprofile bleiben getrennt. `ac_load <0|1|2> <slot>` bietet einen expliziten kontextuebergreifenden Ladeweg. Die originale Server-/Wundserialisierung bleibt unveraendert.

## Nachweise und Grenzen

Die sechs gerichteten Neustartwechsel starteten echte Level, schrieben Saves und luden sie erneut. Effektive WCR- und BT-Drop-Skriptprovider sind in den `restart-*.json`-Berichten festgehalten. Beim AA-SH-Lauf war die erste Testauswertung falsch negativ: `developer 0` protokolliert `CS_ACTIVE` nicht; vorhandene Saves und der abgeschlossene Ladepfad bestaetigen den Lauf. Die Testauswertung verwendet inzwischen die echten Speicherdateien. `final-AA-BT.json` prueft zusaetzlich die neue Save-Metadatenannahme und zeigt die gemeinsame Oberflaeche nach Save/Load. Gerendertes Menue visuell kontrolliert.

Die laufende Einzelstartmatrix wird getrennt in `map-starts.json` dokumentiert. Ein erfolgreicher Start ist kein vollstaendiger Missionsdurchlauf. Natuerliche Missionsabschluesse, gesamte WCR-/Drop-/Leichen-Verhaltensmatrix nach allen Wechseln und persoenliche Abnahme werden hier nicht behauptet. CP7 prueft die neu hinzugefuegte Progression separat. Der zuvor vom Nutzer ausgelassene BT-Finaldurchlauf bleibt als fehlender Nachweis kenntlich.

Linux/macOS-Kontextneustarts sind nicht implementiert; der beauftragte Windows-Teststand verwendet Win32-Prozessstart ohne Shellauswertung. Kein Merge freigegeben oder ausgefuehrt.
