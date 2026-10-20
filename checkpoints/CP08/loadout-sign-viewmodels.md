# LOADOUT-Schild und offene Waffenflaechen

## Aenderungen

Das Hauptmenue verwendet fuer LOADOUT jetzt eine generierte transparente
Schriftgrafik im Stil von OPTIONS: cremefarbene breite Serifenschrift, dunkle
Kontur und Schatten. Das Paket verwendet dieselbe 256x64-Zeichenflaeche,
Glyphengroesse, Grundlinie und Schraegstellung wie die uebrigen Schilder.
Die separate gelbe Textanzeige entfaellt. Die beleuchtete Multiplayer-Tuer
oeffnet weiterhin ausschliesslich LOADOUT.

Die offene Schrotflinten-Schulterpartie wurde in AA m2l1 mit FOV 90 reproduziert.
Bei FOV 80 bleibt dieser Teil ausserhalb des Bildausschnitts. Die Geometrie ist
vorhanden, aber ihre Rueckseiten werden ausgeblendet. Eindeutige Testmaterialien
mit beidseitiger Darstellung schlossen die Luecke. Ein frueher Test verwendete
versehentlich `fov` statt `cg_fov`; er gilt nicht als FOV-Vergleich.

Die Engine zeichnet nun normal einseitige Oberflaechen lokaler Ego-Waffen und
Arme beidseitig. Die Bedingung verlangt gleichzeitig RF_FIRST_PERSON und
RF_DEPTHHACK; Weltmodelle, andere Spieler, Vorschauen und ausdruecklich
rueckseitige Shader behalten ihre bisherigen Regeln. Befestigte Waffen
uebernehmen RF_FIRST_PERSON jetzt korrekt vom Spielermodell; zuvor stand
RF_THIRD_PERSON doppelt in dieser Maske. Damit gilt die Korrektur fuer alle
Waffenherkuenfte und nicht nur fuer einzeln umgeschriebene Materialien.
Waffenwerte, Animationen und Speicherformat bleiben unveraendert.

## Nachweise

- `shoulder-baseline90` / `shoulder-both90` / `shoulder-fixed90` unter
  `profiles-local/loadout`: derselbe alte isolierte AA-Spielstand, urspruenglich
  offene Schaftflaeche und korrigierte Darstellung. Der letzte Lauf verwendet
  den neuen Build ohne Testmaterialien; Nachladen des Spielstands funktioniert.
- `viewmodels-aa-r1`, `viewmodels-sh-r1`, `viewmodels-bt-r1`: jeweils Schrotflinte,
  Garand, BAR, Thompson, MP40, FG42, PPSH und Breda bei FOV 90/110. Zusaetzlich
  Schrotflinten-Schuss, Nachladen, Hocke, Drittperson und Menuevorschau.
  21 Aufnahmen je Kontext visuell geprueft, Fortschritts- und Savesentinels
  unveraendert. Werkzeug: `tools/test_loadout.py --case viewmodels`.
- `sign-r1`: native Hover- und Klick-Callbacks der Tuer in AA/SH/BT, neues
  Schild sichtbar, LOADOUT wird geoeffnet. `tools/test_loadout_sign.py`.
- Engine und cgame gebaut; CP00- und Kampagnenvalidierung sowie Diff-Pruefung
  bestanden. GL2-Gegenstueck mit MSVC auf Syntax/Typen geprueft; native
  Darstellungspruefung und Auslieferung verwenden GL1.

Die bekannten Inhaltswarnungen zu AA-Sandbag/Fence/Radar, SH-smokegrenade_start
und BT-e2l2-Prespawn/Mortar bleiben in den lokalen Ergebnisdateien erhalten.
Keine neuen Script-/Befehlsfehler ausser den bekannten BT-Prespawn-Meldungen.
Keine vollstaendige Pruefung jeder Waffenanimation in jeder Mission behauptet.

## Bildquelle

Builtin Imagegen, Modus Edit, echte Alpha-Transparenz. Referenz:
`generated-local/menu-lettering/options.png`; Ergebnis:
`generated-local/menu-lettering/loadout.png`. Prompt: OPTIONS durch LOADOUT
ersetzen, identische breite cremefarbene Slab-Serif-Versalien, schmale dunkle
Olivkontur und Schatten nach rechts unten, eine Zeile ohne Hintergrund.
Anschliessend nur dieselbe technische Zuschneide-/Skalierpipeline wie fuer die
anderen Menueschilder. Bild und Spielressourcen bleiben lokal.
