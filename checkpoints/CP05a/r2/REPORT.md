# CP05a-r2 - BT-Strassenprojektion

Der Nutzer sah im BT-Test Blut auf Gras, aber keine Flecken auf der erdigen Strasse. Dieser konkrete Fehler in CP05a-r1 ist bestaetigt und korrigiert. Engine-Quellstand `a3c13d93689f47044c5fa6e79ea10b723135c162`, unveraenderter Branch `codex/cp05a-corpse-effects` und Entwurfs-PR #8. Keine neue Checkpoint-Abnahme oder Mergefreigabe unterstellt.

## Ursache und Korrektur

Die Strasse in `e2l2` ist die gekruemmte BSP-Flaeche 194 mit Shader `textures/misc_outside/bocroad_full`. Ihr sichtbares Dreiecksnetz liegt an der getesteten Stelle etwa 1,25-1,83 Einheiten unter dem Kollisionsnetz. Die Tropfen treffen korrekt auf `SURF_DIRT`; das bisherige nur 0,5 Einheiten tiefe Projektionsvolumen erreicht jedoch die sichtbare Strasse nicht. Die vorhandene Korrektur konnte nur in der Gegenrichtung zur sichtbaren Flaeche versetzen. Das war kein fehlendes Blutmaterial und kein Ausschluss von Erde als Material.

Der GL1-Praezisionspfad darf sein weiterhin duennes Projektionsvolumen nun um hoechstens zwei Einheiten hinter den Kollisionspunkt versetzen, ausschliesslich wenn die naechste sichtbare Flaeche ein gekruemmtes Grid ist. Die Flaechensuche wird um denselben kleinen Bereich erweitert. Flache Flaechen bekommen keine neue Tiefenfreigabe. Es gibt keine tiefe Projektion auf beliebige darunterliegende Boeden. Waffen, Kollisionsmasken, Texturen, Fleckengroesse, Lebensdauer und Spiel-DLLs bleiben unveraendert.

## Nachweise

`road-before.json` und `road-after.json` stammen vom selben hashgebundenen BT-Save mit derselben Leiche und Kamera. Es sind echte native Schuesse; individuelle Timings und Zufallsseeds unterscheiden sich, daher kein Anspruch auf pixelidentische Partikelbahnen. Im Vorher-Lauf liefern 12 von 13 Projektionen null Fragmente. Nach der Korrektur liefern alle 17 Projektionen Flecken, darunter sichtbare Flecken direkt auf der Erde. Alle 17 verschwinden nach 30.001-30.018 ms.

Die Bilder `profiles-local/CP05a-r2/road-before/maintt/screenshots/shot0002.png` und `road-after/maintt/screenshots/shot0002.png` wurden direkt angesehen: vorher keine Strassenflecken, danach sichtbare Blutspuren unter und neben der Leiche auf der Erde. `road-after/.../shot0003.png` zeigt sie nach etwa 26 Sekunden weiterhin. Bilder und Saves bleiben lokal.

Der native AA-Wand-/Bodentest auf `m1l2a` bestaetigt weiterhin die vorhandene Projektion; `r2-AA-wall-confirmed.json` enthaelt den bestaetigten Pistolentreffer. Der erste kurze 50-ms-Schuss in `r2-AA-wall.json` traf nicht und ist ausdruecklich kein bestandener Oberflaechentest. Der Harness fordert jetzt einen bestaetigten Treffer und haelt den Abzug 180 ms.

`r2-AA-blocker.json` prueft Leichentreffer mit vier Waffengruppen, Save/Load, Abschaltung und eine blockierende Wand. Weiterhin genau ein urspruengliches Todesereignis, kein Leichentreffer durch die blockierende Wand und keine neuen Treffer bei abgeschalteter Option. Entfernte Leichen hinterlassen nach Save/Load keine Wunddaten. `verification.json` fasst die bestaetigten Ergebnisse zusammen.

Nativer Windows-Build und Metadaten-/Ausschlusspruefung erfolgreich. Binaerhashes stehen in den Testdateien und `build-manifest.json`; nur `openmohaa.exe` aendert sich gegenueber r1. GitHub- und Auslieferungsnachweise werden in der lokalen Delivery-Datei festgehalten.

## Bereitstellung

Neue Startdateien `Start-CP05a-r2-AA/SH/BT.cmd`, getrennte Runtime und Profile. 47 Nutzerdateien aus CP05a-r1 unveraendert kopiert und hashgeprueft. Vorherige Kandidaten bleiben unveraendert. 9.072 geschuetzte Eingabedateien, 9.000 Runtime-Basisdateien und MP1-Eingaben geprueft. Das lokale Laufzeit-ZIP ist CRC-/SHA-geprueft und enthaelt Originalassets; es wird nicht hochgeladen.

Der konkrete BT-Strassenfall und die genannten Regressionen sind getestet. Keine vollstaendige neue Material-/Kartenmatrix, kein GL2-Test und keine erneute komplette SH/BT-Waffenmatrix. Die allgemeinen CP05a-r1-Testgrenzen gelten weiter. Persoenliche Abnahme und Merge bleiben offen.
