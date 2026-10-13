# CP0: lokale WCR-Basis

Sieben installierte Pakete: AA Main, Bash, Reflections; SH Main, Reflections;
BT Main, Reflections. Alle bleiben aktiv. Lose Daten werden ebenfalls übernommen.
Das lokale Deinstallationsskript nennt zahlreiche lose WCR-Sounddateien; es wird
nicht ausgeführt. Ohne lokale Readme/Changelog ist die genaue Versionsnummer
ungeklärt. Paketfingerprint und Ressourcenmanifest ersetzen keine Spielabnahme.

Kein OpenMoHAA-Zusatzpaket als separate lokale Datei gefunden. Keine optionalen
Pakete nachgeladen oder eigenmächtig ergänzt. `maps/m1l1.scr`, `maps/m2l1.scr`
und `maps/e3l4.scr` sind WCR-Ressourcen und werden gezielt geprüft. Der gewählte
Upstream-Stand enthält den TurretGun-setthread-Fix 44ce0595; sein Vorhandensein
ist kein Nachweis eines bestandenen MG42-Fortschrittstests.

`resource_conflicts.json` enthält statische Anbieter und Hashes. Tatsächliche
Suchpfade und ausgewählte Anbieter müssen zusätzlich mit Engine `path`/`which`
bestätigt werden. Keine Skript-Merges in CP0. Autoren-/Lizenzhinweise in den
lokalen Eingaben bleiben unverändert. WCR-Assets gelangen nicht ins Repository.

Rückbau: getrennte WCR-Eingabekopie erneut in ein neues Laufzeitziel kopieren;
keine Originaldateien löschen und keine alten Profile über neue schreiben.
