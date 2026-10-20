# LOADOUT-Tuer und gemeinsame HUD-Kontur

Nutzer bestaetigt am 20.10.2026 nach eigenem Test, dass alle angebotenen Waffen
und Granaten funktionieren. Dieser Folgeauftrag aendert Zugang, Auswahl und HUD.

## Verhalten

- Der urspruengliche AA-Multiplayer-Tuerbereich mit seinem Hover-Leuchten oeffnet
  jetzt LOADOUT. Der aufgesetzte Textbutton ist entfernt; das Schild zeigt beim
  Hover LOADOUT. Multiplayer-Kommandos bleiben gesperrt.
- 37 waehlbare tragbare Waffen in sechs Kategorien. Beide Minendetektoren sowie
  M18, Nebelhandgranate, RDG-1 und die als Rauchgranate definierte Breda-Granate
  sind nicht mehr waehlbar. Die fuenf Sprenggranaten bleiben erhalten.
- Stabile Katalogpositionen und Ressourcen bleiben fuer bestehende Spielstaende
  erhalten. Entfernte Auswahlen werden beim Menueaufruf auf DEFAULT normalisiert;
  auch vor einem Menueaufruf lehnt die Spielervergabe diese Eintraege ab.
  Zufallsauswahl und Operations-Anzeige beachten dieselbe Freigabe.
- `HUD black outline` unter DISPLAY & HUD gilt sofort fuer AA/SH/BT, unabhaengig
  von der Herkunft der Waffe. Standard ist aus; Defaults setzt ebenfalls aus.
  Die archivierte Einstellung `ac_hud_outline` wird kampagnenuebergreifend geteilt.
- Gemeinsame Textausgabe fuer normale HUD-Labels, dynamische Waffennamen,
  Konfigstrings, Munitions-/Gesundheitszahlen und beide Meldungsfenster. Die
  AA-Ausrichtung bleibt beim Einschalten erhalten, auch bei links/oben-Text.
  Der bereits vorhandene kleine Schatten der Courier-Schrift bleibt erhalten;
  die zusaetzliche dicke Erweiterungs-Kontur ist optional.

## Pruefung

Native Builds von Engine, game und cgame. Testwerkzeug
`tools/test_loadout_preferences.py` verwendet ausschliesslich isolierte Profile.
Es prueft die echten Maus-Callbacks der Tuer, sechs ungueltige Alt-Auswahlen und
Direktbefehle, die fuenf angezeigten Sprenggranaten, den realen Options-Checkbox,
Standard aus, archivierte Einstellungen und Neustart im naechsten Spielkontext.
Drei verschiedene Waffenherkuenfte werden jeweils in AA, SH und BT mit/ohne
Kontur aufgenommen; die Einfuehrungssequenzen der Erweiterungen werden abgewartet.
AA laedt dabei einen vorherigen isolierten Spielstand. Persoenliche Saves werden
nicht verwendet oder veraendert.

Fruehe Testkorrekturen: Buttonbefehle werden an den Kommandopuffer angehaengt;
Fortsetzung deshalb erst nach dessen Entleerung. Gemeinsame Einstellungen stehen
in ac_preferences.cfg, nicht in der alten ac_shared.cfg. Die fuenf bereits
bekannten BT-e2l2-Prespawn-Warnungen werden getrennt dokumentiert und nicht als
neue Loadout-Fehler gewertet. Keine natuerlichen Komplettdurchlaeufe behauptet.

Abschliessender Lauf `profiles-local/loadout/preferences-r5`: alle drei Kontexte
bestanden; jeweils Thompson, PPSH und Breda aktiv ausgeruestet und Kontur an/aus
visuell geprueft. Neustarts AA -> SH, SH -> BT und BT -> AA behalten die Option.
Kampagnenvalidierung, CP00-Integritaetsregeln und Diff-Pruefung bestanden.

Installiert aus `47d6d5c8` als `loadout-hud-r4` plus
`hud-outline-options-r1`. Alle 86 eigenen Laufzeitdateien hashgeprueft;
Engine/Spielmodule entsprechen dem abschliessenden Testbuild. Bei beiden
Installationsschritten blieben 413 persoenliche Profildateien, 9072 Original-,
9000 Basis- und acht Max-Payne-Eingabedateien unveraendert. Ruecksicherungen und
lokale Update-ZIPs liegen unter den jeweiligen Batchnamen. Tuer-Hover mit
oeffnender/beleuchteter Tuer und LOADOUT-Schild abschliessend nativ kontrolliert
(`profiles-local/loadout/door-final-r1`). Keine Spielassets in Git. Kein Merge.
