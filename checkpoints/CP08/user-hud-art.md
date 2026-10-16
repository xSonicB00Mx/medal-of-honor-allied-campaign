# Nutzerbilder: Uniformen, Ausweise und Sepia-Ladebild

2026-10-16: Die gelieferten RGBA-Master ersetzen die fuenf bisher ausgenommenen Inventarsymbole. Zuordnung nach Originalvergleich: Bild 1 uniform_dak, 2 uniform, 3 papers2, 4 papers1, 5 uniform_weh. Unveraenderte Proportionen, transparente Kanten, 512x512-Texturen innerhalb der achtfachen Originalgrenzen; bestehende HUD-Rechtecke und Inventarskripte bleiben erhalten.

Alle bisherigen Inventartexturen sind bytegleich. In AA/SH/BT kommen jeweils nur die fuenf Texturen und ihre Shader hinzu. Quelldateien und Pakete bleiben lokal und ausserhalb Git.

Das gelieferte Sepiabild ersetzt nur AA ui/loading_default.urc als durchgehender 1920x1080-Hintergrund. Ladebalken bleibt eingebunden. Andere Ladebilder, Erweiterungshintergruende, Multiplayer-Menues und Abschlussstatistik bleiben unveraendert.

Native Tests: tools/test_inventory_art.py user-uniforms-r1 (3840x2160, HUD 1.66, neun Aufnahmen inklusive Hinzufuegen/Entfernen und Zaehlern), tools/test_widescreen_art.py --run-id user-sepia-r1 --installed --menus loading_default --overlay generated-local/widescreen/sepia/packages (1920x1080). Beide erfolgreich; Uniformen, Ausweise und Ladehintergrund visuell geprueft. Erweiterungen paketweise geprueft, kein erneuter nativer SH/BT-Inventartest. Keine Nutzerabnahme und kein Merge unterstellt.

Installiert: user-inventory-r1 und user-sepia-r1, Quellcommit 40e1cd90. Alle 63 verwalteten Laufzeitdateien hashgeprueft. Beide Lieferungen bestaetigen 9072 Originaldateien, 9000 Basisdateien, 8 Max-Payne-Eingaben und 131 persoenliche Profildateien unveraendert. Rueckrollkopien und Screenshot-ZIP lokal vorhanden.
