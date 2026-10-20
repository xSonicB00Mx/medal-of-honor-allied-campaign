# CP09 – Regression und Abnahmekandidat

Begonnen am 20.10.2026 auf Nutzerauftrag. Feature-freeze: nur Fehlerkorrekturen,
Pruefung und Auslieferung. Der Nutzer uebernimmt anschliessend den natuerlichen
Kampagnenabschluss mit seinem bestehenden Spielstand.

**Status: technische Pruefung laeuft; keine Gesamtspielabnahme, kein Merge.**

## Festgelegte Basis

- Ausgangsbranch `codex/cp08-operations-map`, Commit `880b3df1`.
- Inhalts-/HUD-Quellen `1354fb7e`; Engine/game/cgame `b5573702`.
- WCR-Fingerprint `3b6b38b5b04ba320a526196946c44394c4519e4197dc8d3d05788e186501cfcc`.
- Sieben aktive WCR-Module: AA Main/Bash/Reflections, SH Main/Reflections,
  BT Main/Reflections. Die originale Versionsnummer ist nicht belegt.
  Lose Eingaben sind im lokalen Manifest erfasst.
- Lokale BT-Dropintegration bleibt aktiv. Urspruengliche Patch-PK3:
  `d4122611afec4bb317eef1026f256cd0e1aa87fc85268218ceb19df71fb225fd`.
  Transport-ZIP, Autor und genaue Version waren beim damaligen Import nicht
  verfuegbar. Der ZIP-Erstimport aus dem Plan ist weiterhin nicht getestet.
- 9.072 Originaldateien, 9.000 Runtime-Basisdateien und 86 Moddateien werden
  gegen ihre gespeicherten Hashes geprueft. Persoenlicher Profilbaum vor
  und nach der nativen Matrix verglichen.

## Pruefverfahren

`tools/run_cp09.py <eindeutiger-laufname>` fuehrt native Tests seriell aus.
Alle Testprofile sind getrennt. Fortschritts-/Save-Sentinels pruefen Replay-
Grenzen. Installierte Binaerdateien muessen mit dem aktuellen Build
uebereinstimmen. Historische Menue-/Finale-/Flinch-Pakete werden in der
CP09-Runde nicht mehr als Test-Overrides eingesetzt.

Jeder Test bekommt eigenes Log und Windows-Prozessspeichermessungen.
Fehlschlaege bleiben erhalten, auch nach bestandenem Wiederholungstest.
Grenztests mit gesetztem Testfortschritt sind kein natuerlicher Durchlauf.
Konkrete Ergebnisse folgen nach Laufende.

Vorhandene C++-Tests: 65.536 Orientierungsseeds, getrennte Ein-/Austrittsfolgen,
Spiegelung, begrenzte lokale Ereignisspeicherung, geometrische Negativfaelle.
Kein Ersatz fuer den nativen Vergleich saemtlicher Gameplay-Zufallsfolgen.

## Installation und Rueckbau

`tools/cp09_candidate.py` erzeugt einen unabhaengigen lokalen Kandidaten aus
der **bereits importierten und zusammengefuehrten**, hashgeprueften Runtime.
Kein Netzwerkzugriff, keine Archive zur Laufzeit, keine Originalaenderung,
keine Profilkopie. Bytekopien statt Hardlinks/Junctions.

Erst nach vollstaendiger Pruefung wird der Staging-Ordner aktiviert.
Unterbrochene Kopien sind explizit fortsetzbar. Erneute Einrichtung desselben
Standes veraendert nichts. Abweichende Dateien werden gemeldet. Rueckbau
prueft zuerst alle Dateien und entfernt nur bekannte Moddateien.

Einrichtungs-/Rueckbautest bestanden: Unterbrechung nach 25 Dateien,
Wiederaufnahme, unveraenderte zweite Einrichtung, Ablehnung einer veraenderten
Moddatei, Rueckbau mit 9.000 unveraenderten Basisdateien und Save-Sentinel.

Gefundener Fehler: interne `Start-AA/SH/BT.cmd` verwiesen noch auf CP05a-Starter
ausserhalb der Runtime. CP09 bekommt eigenstaendige relative Starter.
Der normale CP08-Spielstarter war davon nicht betroffen.

Dies ist ein lokaler Wiederherstellungs-/Kandidatenweg, **kein universeller
Installer fuer beliebige rohe Spiel-, WCR- und ZIP-Bestaende**.

## Offene Abnahmegrenzen

- Natuerlicher Durchlauf, restaurierte WCR-Skriptketten und finales Berlin.
- Separate GPU-Timer-/Present-Messungen. `com_speeds` misst CPU-Wandzeit
  einschliesslich moeglicher Treiberwartezeit, keine GPU-Frametime.
- Langzeitmessungen und vollstaendiger kombinierter Waffen-/Leichen-/
  Oberflaechen-/Drop-/Gameplay-Zufallsvergleich.
- Erstinstallation aus nicht referenzierten Eingaben. Fehlende/abweichende
  WCR- oder BT-Dateien werden nicht durch andere Fassungen ersetzt.
- GL1 geliefert/nativ geprueft; keine GL2-Abnahme.

CP09 erst nach fehlenden technischen Nachweisen und getrenntem natuerlichen
Durchlauf als vollstaendig abgeschlossen bezeichnen.
