# Vollstaendige Geschuetzbeschriftungen

Nutzerscreenshot: persoenliches BT-Profil, `screenshots/shot0002.tga`.
Das Feld fuer "Modello 37" war nur 72 virtuelle Pixel breit. Die bestehende
Courier-Anpassung verbreiterte nur Widgets namens `weaponname`; stationaere
Waffen verwenden auch `healthnumber` oder `name`.

Die gemeinsame Layoutkorrektur erkennt rechtsbuendige statische
Waffenbeschriftungen anhand ihres Inhalts und erweitert sie in den freien
linken Bereich ihres bestehenden HUD-Fensters. Die rechte Textkante bleibt
fest, die Hoehe betraegt mindestens 22 virtuelle Pixel. Beim Modello waechst
das Feld auf 172 Pixel. Munition, Zustand, Symbole, Farben und Stat-Bindungen
bleiben unveraendert. Keine Schriftverkleinerung und keine Engine-Aenderung.

Korrigiert sind Modello 37, Nebelwerfer, 15 cm C/36, Flak 88, Bohler, AA Gun
und die verbleibende linke Reserve des bereits reparierten Mortar-Felds.
Der gemeinsame Helfer wird sowohl beim Courier-Paketbau als auch auf die
effektiven HUDs im kampagnenuebergreifenden Ressourcenpaket angewendet.
Damit ueberdeckt kein aelterer LOADOUT-Import die Reparatur.

## Pruefung

- Alle 28 vorhandenen statischen Namensfelder der drei Spielkontexte gegen
  ihre tatsaechlichen Courier-Metriken geprueft: vollstaendige Breite plus
  Konturreserve vorhanden.
- Vergleich aller geaenderten HUD-Dateien: ausschliesslich Rechteckzeilen
  veraendert, alle Bindungen und sonstigen Ressourcen identisch.
- Isolierter nativer BT-Test mit einer Kopie des persoenlichen Quicksaves,
  3840x2160, HUD 1.5 und 2.0, schwarze Kontur eingeschaltet. Die sieben echten
  HUD-Ressourcen wurden als Layout-Pruefansichten eingeblendet; das ist keine
  Behauptung, jedes Geschuetz in diesem Spielstand bedient zu haben.
- Vorher: "dello 37"; nachher: vollstaendig "Modello 37".
  Lokale Nachweise unter `profiles-local/weapon-name-fix` und
  `generated-local/weapon-name-fix`.
- Fruehe Prueflaufkorrekturen: interner AA-Gun-Menutitel zunaechst unvollstaendig;
  normales Ausblenden liess Testanzeigen ueberlappen. Abschliessender Lauf
  `fixed-r3` blendet die vorige Ansicht sofort aus.
- CP00-Integritaetsregeln und Diff-Pruefung bestanden. Persoenliche Saves und
  Einstellungen werden nicht als Testprofil benutzt oder ueberschrieben.

Installiert aus `1354fb7e` als `emplacement-hud-names-r1`. Alle 86 eigenen
Laufzeitdateien hashgeprueft. 427 persoenliche Profildateien, 9072 Original-,
9000 Basis- und acht Max-Payne-Eingabedateien unveraendert. Ruecksicherung unter
`generated-local/widescreen/backups/emplacement-hud-names-r1`; lokales Update
`artifacts-local/CP08-r1-emplacement-hud-names-r1-update.zip`. Keine Binaer-
oder Speicherformataenderung. Keine persoenliche Abnahme oder Merge behauptet.
