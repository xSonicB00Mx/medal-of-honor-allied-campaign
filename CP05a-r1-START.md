# CP05a-r1 - Blutspuren und Leichentreffer

Bitte die neuen Startdateien verwenden:

- [Allied Assault](Start-CP05a-r1-AA.cmd)
- [Spearhead](Start-CP05a-r1-SH.cmd)
- [Breakthrough](Start-CP05a-r1-BT.cmd)

Blutflecken bleiben jetzt **30 statt 10 Sekunden** sichtbar und sind **1,5-mal so gross**. Auch die fliegenden MP1-Partikel wurden um den Faktor 1,5 vergroessert. Die Groesse der Koerperwunden bleibt erhalten. Bei sehr vielen gleichzeitigen Effekten kann das begrenzte Fleckenbudget weiterhin alte Spuren vorzeitig ersetzen.

Blut auf Boeden und Waenden richtet sich jetzt nach der sichtbaren Oberflaeche. Zuvor konnten Kennzeichnungen der unsichtbaren Kollisionsgeometrie einen Fleck verhindern. AA wurde an Boden, Terrain und Wand nachgeprueft; Himmel, Wasser und unsichtbare Flaechen erhalten weiterhin keine Flecken. Spritzer brauchen einen freien Weg vom Koerper zur Umgebung.

Bereits tote Gegner und die bekannten menschlichen Kartenleichen lassen sich nun optisch beschiessen: Nebel, Tropfen, Ein-/Austrittswunden und erreichbare Umgebungsflecken folgen denselben Waffenregeln. Es entstehen keine neuen Todesreaktionen. **Corpse hit effects** unter **Options > HUD / Font Size** ist standardmaessig aktiv; die vorhandenen Schalter **Red hit mist**, **Blood drops and stains** und **Body wounds** gelten zusaetzlich.

Deine bisherigen Einstellungen, einschliesslich FOV, und Spielstaende wurden aus CP05-r2 in ein getrenntes Profil kopiert (47 Dateien, hashgeprueft). Zum Vergleichen kannst du denselben Spielstand laden, einen Gegner erneut beschiessen und die Flecken etwa eine halbe Minute beobachten. Die bisherigen r2-Startdateien bleiben als Rueckweg verfuegbar und verwenden ihr eigenes Profil.

[Technischer Bericht und Testgrenzen](checkpoints/CP05a/REPORT.md). Persoenliche Abnahme und Merge sind offen.
