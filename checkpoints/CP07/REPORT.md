# CP07-r1 – chronologische Kampagne

Technischer Kandidat mit 15 Einsaetzen, 53 Hauptabschnitten und einem getrennten optionalen AA-Abschnitt. `mod/campaign/missions.json` ist die gemeinsame Datenquelle. Der Generator gleicht alle 54 inventarisierten Karten ab, prueft eindeutige Zuordnung, Nachfolger und titelabhaengiges Drop-Profil. Originalketten bleiben innerhalb einer Operation erhalten; an unabhaengigen Operationen startet der native Einstieg mit dessen eigener Ausruestung. Protagonisten werden nicht zusammengelegt.

Die lokal wirksamen Briefing-/Ladetexte und Skripte bestimmen Datum, Ort und Grenzen. Die AA-Widerstandsmission enthaelt widerspruechliche Datumsangaben (12. und 22. Juni); die zusammenhaengende Kette bleibt erhalten und wird als Zeitraum ausgewiesen. Bei den beiden Normandy-Einsaetzen am 6. Juni gilt eine dokumentierte stabile Reihenfolge SH vor AA, keine Behauptung einer minutengenauen gemeinsamen Reiseroute. Fuer Berlin fehlt in den geprueften Spieltexten ein exaktes Datum; die Oberflaeche behauptet deshalb nur 1945. Der optionale Abschnitt m4l0 erhaelt kein erfundenes Pflichtdatum.

## Fortschritt und Spielstaende

`ACPROG1` liegt getrennt von den Spielstaenden im gemeinsamen Profil. Abschluesse werden vor einem Kontextwechsel atomar ersetzt, mit einer geprueften Sicherung des vorherigen Standes. Unvollstaendige temporaere Dateien werden ignoriert; fehlende/beschaedigte Hauptdateien koennen aus einer gueltigen Sicherung gelesen werden. Sind beide ungueltig, bleiben sie erhalten und die Kampagne schreibt keinen erfundenen Fortschritt.

Nur der erfolgreiche native Intermissionspfad stellt einen einmaligen Uebergangsnachweis bereit. Direkte map/gamemap-Befehle, optionale Einstiege, Tod und Missionsfehlschlag schalten nichts frei. Wiederholungen kehren zur Auswahl zurueck und veraendern weder Freischaltungen noch Haupt-Fortsetzenpunkt. Fortsetzen verwendet den letzten erfolgreichen Kampagnensave im richtigen Spielkontext. `ACM2` speichert zusaetzlich Operation und Wiederholungsmodus; erst ein gueltiger Spielstand stellt diese Zuordnung wieder her. ACM1 bleibt als nicht zugeordneter Spielstand lesbar. Gemeinsame Optionen und Tasten werden auch beim normalen Programmneustart uebernommen.

Die AA-/BT-Credits bleiben vorhanden. Nur beim Verlassen der Credits nach gesetztem nativem Erfolgsflag (`level.end_level` bzw. `level.escaped`) wird die Kampagnenfortsetzung angestossen. BT-Luftangriff, Flucht, Timer, Begleiter und Fehlschlagsskripte werden nicht umgeschrieben. Der letzte SH-Einsatz behaelt sein Originaldebriefing und seine Credits.

## Nachweise und offene Abnahme

Die JSON-Dateien enthalten echte Engine-Laeufe mit getrennten Profilen und Binaerhashes. `boundary-final-*` prueft alle 15 Grenzen mit vorbereiteten Profilen und synthetisch ausgeloester nativer Intermission. Das ist **kein natuerlicher Missionsdurchlauf**. Jede Grenze schrieb die erwartete Abschlussmaske; Entwicklungsdiagnosen aus direkt gestarteten Originalskripten sind separat erhalten und gegen CP6 verglichen. Ein bestandener Zustandsvergleich ist kein fehlerfreier Gameplaynachweis. Fruehe `boundary-00*`-Fehlversuche dokumentieren korrigierte Test-/Startup-Probleme.

Wiederholung, Konsolenwechsel, Fehlschlag, Save/Load, Credits-Schutz und Dateiwiederherstellung werden getrennt protokolliert. Der zuvor vom Nutzer uebersprungene natuerliche BT-Finaltest bleibt offen; insbesondere ist die vollstaendige Flucht mit Save/Load und Tod/Neustart nicht nachtraeglich behauptet. Auch ein kompletter natuerlicher Durchlauf aller 53 Abschnitte und die gesamte Drop-/WCR-Verhaltensmatrix sind nicht durch synthetische Grenztests ersetzt. CP7 ist implementiert, aber diese vollstaendige Gameplayabnahme und persoenliche Abnahme bleiben offen. Kein Merge.
