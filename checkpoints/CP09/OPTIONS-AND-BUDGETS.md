# Optionen und Effektbudgets

Bestandsaufnahme des gelieferten Codes; keine Budgeterhoehung. Gemeinsame
Praeferenzen werden zwischen AA/SH/BT uebernommen, getrennt vom Fortschritt.

| Cvar | Standard / Bedeutung |
|---|---|
| `ac_blood_mist` | 1, Treffernebel |
| `ac_world_blood` | 1, Tropfen und Weltblut |
| `ac_body_wounds` | 1, animierte Koerper-/Kopfwunden |
| `ac_corpse_effects` | 1, visuelle Leichen-/Sterbetreffer |
| `ac_player_flinch_percent` | 20, 0..100 in Zehnerschritten |
| `ac_bt_drop_limits` | 0, freie BT-Drops; 1 originale Einschraenkungen |
| `ac_hud_outline` | 0, zusaetzliche schwarze Kontur aus |
| `ac_hud_scale` | 1, Darstellung auf 0,5..2 begrenzt |
| `ac_menu_scale` | 1, Schriftgroesse, unveraenderte Menuegeometrie |

Weltblut aus stoppt Emissionen und entfernt aktive fallende Tropfen.
Bereits erzeugte Weltflecken laufen regulaer aus. Koerperwunden aus stoppt
neue Wunden und blendet vorhandene aus; Archive bleiben erhalten und koennen
beim Einschalten wieder sichtbar werden.

- 256 fallende Tropfen, 2,2 Sekunden Lebensdauer; sechs je geometrisch
  bestaetigter Ein-/Austrittsstelle. FIFO ersetzt alte Eintraege.
- Je 128 wartende Emissionen, Rueckseitenereignisse und Deduplikationen.
  Wartende Emissionen verfallen nach 250 ms.
- 64 gespeicherte Wunden global, maximal 32 je Actor; FIFO-Verdrangung.
  Keine pauschale Dreiminuten-Lebensdauer implementiert: fester Speicher-
  und Archivring begrenzt den Bedarf. Entfernung bei ungueltigem Besitzer/
  Modell oder Kontextreset; Save/Load behaelt Geometrie.
- Zeichnen: maximal acht verwundete Actors, jeweils 512 Dreiecke.
  Ganze Wunde zeichnen oder auslassen, keine Teil-Dreiecksliste.
  Entfernungsausblendung 384..512 Spieleinheiten.
- Kopfpatch maximal 256 Dreiecke, Koerperpatch maximal 64.
- Weltflecken 30 Sekunden. Gemeinsamer nativer Mark-Pool standardmaessig
  `cg_marks_max=256`, mindestens 32, inklusive anderer Einschussmarkierungen.
  Pooldruck kann frueher verdrangen.
- Partikelzufall und Wundorientierung verwenden eigene visuelle Streams.
  Vollstaendiger nativer Gameplay-RNG-Gleichheitsnachweis bleibt separat.

Schrotflinte gemaess neuerer Nutzeranforderung: kleine pelletweise Ein- und
Austrittswunden mit Tropfen. Der fruehere Ausschluss im Plan ist ueberholt.
Nahkampf/Explosionen erhalten keine kugelbasierten Ein-/Austrittswunden.
