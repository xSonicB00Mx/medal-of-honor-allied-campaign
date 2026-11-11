# CP03-r1 – MP1-Tropfen und Weltflecken

Technischer Kandidat auf CP02-r1. Keine persönliche Abnahme und kein Merge. Die spätere autonome Fortsetzung bis CP5 ist im Chat freigegeben. Die vollständige Abnahmematrix bleibt offen; dieser Bericht behauptet keinen abgeschlossenen CP3-Sichttest.

## Umsetzung

Selektiver, hashgebundener Offline-Importer: zwei originale MP1-JPEGs (Farbe und separate Alpha-Maske) werden ohne Umfärbung/Skalierung als RGBA-TGA in ein ausschließlich lokales PK3 gepackt. Vorschau, Originalpfade, Hashes und Konvertierung stehen in import.json. Leser: Tatsh/dade, MIT, Commit 7ec5af866752cd2c6ec3c8f88ec593b561e77321; Lizenz/Anpassung unter tools/ras_reader. Kein Musik-/Modellimport. Partikelverhalten ist eine unabhängige Nachbildung, kein behaupteter RPS-Port.

Ein bestätigter lebender Actor-Geschosstreffer wird vor der unveränderten Damage-Auswertung gegen die tatsächliche Serverpose verfeinert. Dreiecke werden über alle Bone-Gewichte deformiert. Ereignis, Zeit, Kontext, Modell, Instanzkennung, Pose-Hash, tatsächlicher Schussstrahl und isolierter Seed werden diagnostiziert. Nicht bestätigte Geometrie erfindet keine Körpermittenposition. Ausrüstungssurfaces werden ausgeschlossen. Neue Leichentreffer bleiben außerhalb CP3–5; der Clientempfänger selbst besitzt keine HP-Sperre.

Eine versionierte Waffenpolicy enthält 37 exakte IDs einschließlich zweier geprüfter TurretGun-MG42-Modelle. Generator und --check verhindern abweichende Körpermaterial-/Austrittszuordnungen. Alle vier Gruppen nutzen den rückseitigen Zweig; kleine Eintritte sperren ihn nicht. Bestehende Schadens-/Statistik-/Drop-Funktionen werden nicht zusätzlich aufgerufen. Der Geometriepfad unterdrückt prozedurale Blink-Zufallsaufrufe; sein eigener xorshift-Zufall verändert keine Gameplay-RNG-Folge.

Maximal 256 Tropfen, je 6 für Eintritt/Austritt, Lebensdauer 2,2 s, Sweeps in maximal 16-ms-Schritten, Schwerkraft 320. Ein Tropfen erzeugt höchstens einen Fleck; Körperhalbebene verhindert Rückwärtsflug in den getroffenen Körper. Andere Entities blockieren. Nur statische Weltflächen erhalten Flecken; bewegliche Türen blockieren, werden aber bis zu korrekter Mitbewegung nicht beklebt. Himmel/Wasser/Schleim/Lava/Pfützen werden ausgelassen. Die Weltmarken verwenden das bestehende Budget und verblassen nach 10 s. Direkter Rückwärtsspritzer reicht höchstens 96 Einheiten ab geometrisch bestätigtem Austritt.

AA-Schnee verwendet hier gekrümmte sichtbare Flächen, deren Kollisionsproxy etwa 12 Einheiten darunter liegt. Präzise Blutprojektion kann maximal 16 Einheiten zur nächstliegenden sichtbaren Fläche auf der Auftreffseite korrigieren, niemals auf eine tiefere Etage suchen. Der schmale Projektionsbereich verhindert die frühere tiefe Blindprojektion. GL1 unterstützt zusätzlich kleine Heightfield- und Dreiecksflächen. GL2 ist nicht Bestandteil des lokalen Builds und nicht abgenommen.

## Prüfstand und Grenzen

Alle Diagnosen liegen in separaten Profilen, echte native Waffen treffen einen testweise widerstandsfähigen stationären Gegner. AA-v1–v17 sind Fehlersuche, keine Erfolgsnachweise. AA-v18 zeigt im gespeicherten Screenshot kleine originale MP1-Flecken auf Schnee; Fragmente sind tatsächlich gerendert. SH-r1 und BT-r1 enthalten alle vier Gruppen, Save/Load, jeweils fehlerfreies Ende; ihre Binärhashes stehen in den Ergebnissen. AA-wall-r1 prüft alle vier Gruppen vor einer erreichbaren echten Wand, einschließlich Pistolen-/MP-Rückspritzern. Spätere Instanzprüfung wurde als eigene Binärrevision gebaut, weshalb frühere Resultate nicht stillschweigend als identischer finaler Build gelten.

Offen bleiben die vollständige Kombination aller Kampagnen mit Treppe, höherem Boden, beweglicher Tür, mehreren FPS-Werten, Streifschüssen und WCR-Modellvarianten; genaue Nachprüfung des bewegten Zielkörpers für Eintrittstropfen; vollständiger Terrain-/Materialvergleich. Die ursprünglichen Nebel werden noch im bestehenden Effektpfad verarbeitet; die Sonderwaffenabgrenzung dieses Nebelpfads ist separat zu prüfen. Weltflecken/Tropfen sind transient und werden bei Laden zurückgesetzt. Körperwunden sind hier noch nicht implementiert.

Start: Start-CP03-r1-AA/SH/BT.cmd. Neue englische Option: Blood drops and stains. Die Originalbasis bleibt unverändert. Das lokale Runtime-ZIP enthält Original-/Drittassets und darf nicht auf GitHub hochgeladen werden. Manifest und Integritätsprotokoll werden nach Quellsicherung erzeugt.
