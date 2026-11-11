# Spearhead D-Day: heller Himmel im vereinfachten Modus

## 08.11.2026: Seitliche Himmelsbeleuchtung statt reiner Dachmaske

Die vorherige Innenraumkorrektur war zu restriktiv: Ein einzelner senkrechter
Strahl behandelte ganze Aussenfassaden unter kleinen Dachueberstaenden wie
Innenraeume. Die alten Tests konservierten diesen Fehler, weil sie genau diese
Fassaden als dunkel zu haltende Flaechen einordneten. Das Nutzerfeedback wurde
an den bestehenden AA-Kameras reproduziert; die Fassade hatte praktisch keine
Blitzaufhellung.

Die GL1-Wetterdarstellung ermittelt jetzt die sichtbare Himmelsbeleuchtung aus
neun festen Richtungen (Zenit und acht schräge Richtungen). Vollstaendige,
zweiseitig gezeichnete Architektur blockiert die Strahlen; Fenster lassen
sichtbare Aussenbereiche aufleuchten. Die Oberflaechenausrichtung gewichtet
die Sichtbarkeit, mit einem kleinen diffusen Anteil fuer Blattunterseiten.
Eine weiche Ueberblendung verhindert das bisherige Alles-oder-nichts-Verhalten
an Dachueberstaenden. Die Kameraposition entscheidet nicht ueber den ganzen
Bildschirm. r_fastsky, normale Nebelfarbe, Wetterdauer und HUD bleiben erhalten.

Feste Projektionen ueber das gesamte Level verhindern Blickwinkel- und
Entfernungsgrenzen. Ein 3x3-Tiefenatlas verwendet normalerweise 2048 Pixel pro
Richtung, auf Hardware mit kleinerer maximaler Textur 1024. Alle drei benoetigten
Tiefentexturen werden auf gueltige Framebuffer-Anbindung geprueft; bei fehlender
Unterstuetzung bleibt der sichere Himmelsblitz. Die statische Architektur wird
nach Kartenladen oder Grafikneustart einmal aufgebaut. Fuer bewegliche Brush-
Tueren und Plattformen wird nur dieser Atlas auf der GPU kopiert und mit den
aktuellen Transformationen ergaenzt. Unveraenderte Szenen verwenden beide
Atlanten erneut. Explizite Kartenereignisse invalidieren den Cache auch bei
wiederverwendeter Weltadresse. Der normale Modellschattenpfad bleibt unveraendert.

Eine fruehe Variante mit gleich gewichteten Richtungen erzeugte einen hellen
Saum am inneren Fensterrahmen und wurde verworfen. Die finale Gewichtung laesst
die nach aussen orientierte Holzlaibung Licht erhalten, waehrend der zum Raum
zeigende Rahmen dunkel bleibt. Offline-BSP-Strahlen bestaetigen die getrennten
Normalen (+X beziehungsweise -Y). Entsprechend pruefen die Tests die wirkliche
Rahmenflaeche und die wirklichen Fassaden; eine Toroeffnung ist nicht Teil der
positiven Mauerwerkskontrolle. Belege: `lightning-hemisphere-review`.

Die zusaetzliche BT-Bildkontrolle fand einen dunklen Strassenfleck, obwohl
grobe Helligkeitskontrollen bereits bestanden. Ursache war keine fehlende
Himmelsverbindung: Bei flach betrachteten Boeden ueberschritten beide
Nachbarpixel die bisherige Augentiefen-Grenze, so dass die Normale auf null
fiel. Der Roh-Tiefenverlauf war dort dagegen exakt linear. Eine begrenzte
Ebenenpruefung (drei Tiefen-LSB plus zwei Prozent der Steigung) erhaelt nun
Normale und MSAA-Toleranz auf solchen Flaechen. Fuenf Tiefenproben waehlen
bevorzugt die Seite, deren Ebene den Mittelpunkt tatsaechlich rekonstruiert.
An gekruemmten Strassendreiecken muessen alternativ vier aufeinanderfolgende
Gradienten gleichgerichtet sein und hoechstens um Faktor zwei variieren.
Echte Objektspruenge bestehen diese Kontinuitaetspruefung nicht. Es wurde
keine Wand entfernt und kein grosser Tiefenbias hinzugefuegt. Numerische
Belege: `lightning-hemisphere-bt-depth` und `lightning-hemisphere-review`.

Die vergroesserte Bildkontrolle entdeckte ausserdem schmale helle Pixel direkt
unter einer Zimmerdecke. Die Atlasfilterung griff dort ueber die Deckenkante.
Eine konservative 3x3-Abdeckung sichert jetzt nahe Wand-/Deckenkontakte; ihre
Staerke nimmt in echten Weltabstaenden weich ab. Entfernte Verdeckungsgrenzen
bleiben bilinear gefiltert, damit Aussenfassaden keine groben Atlas-Treppen
zeigen. Der Abstand allein reichte nicht: Benachbarte steile Gelaendedreiecke
wurden faelschlich als Deckenkontakt erkannt. Zusaetzlich muss der Blocker
oberhalb des Empfaengers liegen und seine aus Atlasnachbarn rekonstruierte
Flaeche eine Decken-/Dachneigung besitzen. Tieferliegender Boden und steile
Felswaende aktivieren diese konservative Kontaktbehandlung nicht. Ungueltige
Atlasrand-/Himmelsnachbarn werden verworfen; die vier Zusatzproben werden nur
fuer nahe verdeckte Strahlen benoetigt. Nach oben gerichtetes Terrain behaelt
seine Ebenenfilterung. Die Vergleichstoleranz betraegt nur ein Tiefen-LSB.
Der Test prueft diese Bereiche pixelgenau, nicht nur anhand unauffaelliger
Raum-/Strassenmittelwerte.

Ein verbleibender einzelner UHD-Deckenpixel lag durch Tiefenquantisierung
0.002 Welteinheiten ueber der echten Deckenebene. Die getrennte Hoehenpruefung
des Kontaktblockers erlaubt deshalb 0.01 Welteinheiten Rundungsabweichung;
die eigentlichen Tiefenvergleiche/Empfaengerpositionen werden nicht verschoben.
Die anschliessende strenge UHD-Innenraumpruefung besteht vollstaendig.

Eine letzte BT-Abweichung war dagegen ein Fixturefehler: Save/Load liess den
Spieler aufstehen, so dass die Kamerahoehe von 2519 auf 2552 stieg. Derselbe
Bildbereich traf anschliessend andere Strassenstellen, deren seitliche
Himmelsrichtungen tatsaechlich durch entfernte Geometrie blockiert sind.
Synchroner Szenen-/Atlasdump und korrekte Normalen schliessen dort den
frueheren Nullnormalen-/Kontaktfehler aus. Nur die gezielten Terrainkontrollen
verwenden jetzt ihre fest validierte Kamera (6296,-5600,2519), Winkel
(0,270,0). Die vorhergehenden Save/Load-/Neustartkontrollen behalten die
normale Spieleransicht. Kein Pixelgrenzwert wurde dafuer gelockert.

Der Cache-Test deckte ausserdem acht wirklich im Wind schwingende AA-
Fensterlaeden auf. Ihre laufenden Updates sind korrekt; ein Test auf eine
unveraenderte Szene darf sie nicht als Fehler werten. Nur in diesem isolierten
Cache-Test werden diese vorhandenen Laeden ausgeblendet, dann eine echte
Brush-Tuer geklont, verschoben, gedreht, verborgen, gezeigt und entfernt.
Die normalen Bildtests behalten alle originalen Fensterlaeden.

Die statische Erstvorbereitung bleibt ausserhalb des ersten Blitzes. Danach
entfaellt die Fingerprint-/Atlasaktualisierung zwischen Blitzen vollstaendig;
auch staendig schwingende Laeden verursachen dann keine fortlaufenden
Atlas-Kopien. Beim naechsten Blitz wird die aktuelle Brush-Pose geprueft und
bei Bedarf aktualisiert. Der Cache-Test kontrolliert diese Pause und das
anschliessende Nachziehen einer waehrenddessen verschobenen Tuer.

Finale Nachweise unter `generated-local/CP09/`, alle fuer denselben Build:

| Lauf | Ergebnis |
|---|---|
| `lightning-hemisphere-aa-release2` | UHD, vier Innen-/Fenster-/Aussenkameras, beide TAA-Modi, Fassadenabdeckung und Save/Load bestanden. 26 Bilder, 48 Kontrollen. Deckenpixel ohne TAA maximal +2 RGB; Fassadenabdeckung 99.03-100 Prozent. |
| `lightning-hemisphere-msaa-release2` | Echte MSAA4-Abnahme mit optionalen Modellschatten/AO aus; beide TAA-Modi und gleiche Innen-/Fassadenkontrollen bestanden. |
| `lightning-hemisphere-sh-release2` | Spearhead-Wetter, normale helle Nebelfarbe, explizite Fastsky-Wahl, TAA, Save/Load, Grafikneustart und kurze Original-Pulsfolge bestanden. |
| `lightning-hemisphere-bt-release3` | Bestehender e2l2-Save, 22 Wetterfaelle und 14 Terrainkontrollen bestanden. Feste Terrainkamera ohne verdeckenden eigenen Spielerkoerper; NPCs bleiben sichtbar. Strassen-Antwort 0.561-0.609, schwache Pixel maximal 0.43 Prozent bei unveraenderter 1-Prozent-Grenze. |
| `lightning-hemisphere-cache-release2` | 13 Lebenszyklusfaelle bestanden: Spawn, Versatz, Drehung, Aus-/Einblenden, Entfernen, Pause ohne Blitz, erneuter Blitz, Save/Load und Grafikneustart. Cache-Nachweis allein ist keine Bildabnahme. |

Der nominell bestandene BT-Lauf `lightning-hemisphere-bt-release2` ist als
Bildnachweis ungueltig: Die feste Kamera sah zunaechst in den eigenen
Spielerkoerper. Der finale Lauf `release3` blendet ausschliesslich in dieser
Testphase den eigenen Koerper/das Viewmodel aus. Keine Testschwelle wurde
gelockert; Vollbilder wurden zusaetzlich unabhaengig kontrolliert.
Die Puls-Erholung wird mit einer unbeleuchteten Aufnahme derselben Kamera
verglichen, nicht mit der vorherigen stehenden Spieleransicht.

Alle finalen Laeufe: GL-Fehler null, 703 persoenliche Dateien unveraendert,
Binärhashes frisch mit den tatsaechlichen Testdateien abgeglichen. Auf der
Test-GPU (RTX 4090) liegen synchronisierte Effektmessungen meist bei 1-2 ms,
bei UHD/Brush-Updates maximal 4 ms. Einmalige statische Erstaufbauten werden
getrennt erfasst (BT 151 ms); zwischen Blitzen faellt keine Atlasarbeit an.
Die normale 2048er-Konfiguration wurde nativ getestet; der 1024er-Pfad fuer
aeltere GPUs und absichtlicher VRAM-Mangel wurden nicht nativ erprobt.
Dies ist gezielte GL1-Regression, keine erneute Gesamtspielabnahme.

Source `35276e80`, Engine
`4b6b2778c2cae9f64859bdf05b8a3318c8f7c858f0e5e1c6ccb73cc0d57fd1ae`.
Keine Aenderung an game.dll (`139b51a1`), cgame.dll (`d1cf1e29`), Assets,
Missionsskripten, Speicherformat oder persoenlichem Kampagnenfortschritt.

Diese Engine ist in CP08-r1 und CP09-r1 installiert. Deployment hat 9072
Originaldateien sowie 9086/9090 Runtime-Dateien verifiziert; alle 703
persoenlichen Profildateien blieben unveraendert. Nachweis:
`generated-local/CP09/lightning-hemisphere-aa-release2/deployment.json`.
Der dortige Ordner `rollback` enthaelt die vorherige Engine und Manifeste.
Arbeitsbranch `codex/cp09-regression`; kein Merge in main.

## 08.11.2026: Gewitter auf sichtbare Aussenbereiche begrenzen

Nutzerfeedback: Der neue Ganzbild-Blitz hellte auch geschlossene Raeume auf.
Eine erste Beschraenkung auf Himmelstiefe beseitigte den starken Weissblend,
liess aber in AA noch 7-9 RGB-Stufen Nebelaufhellung im Raum uebrig. Der
Native-Vergleich mit deaktiviertem Nebel isoliert diese zweite Ursache:
Innenflaechen dann exakt unveraendert, Himmel durch das Fenster weiterhin hell.
AA setzt in `CG_ParseFogInfo_ver_6` absichtlich Bias 0.001 statt 0; deshalb
greift der 18-Prozent-Nebelbeginn des Renderers hier nicht.

`World::UpdateFog` uebertraegt waehrend eines erkannten Gewitterblitzes nun
die normale gespeicherte Nebelfarbe. Die eigentliche Welt-/Skriptfarbe bleibt
unangetastet: alte Flash-/Unflash-Skripte und Saves mitten im Blitz behalten
ihre Bedeutung. Einzelne RGB-Komponenten muessen gueltig sein. Normale helle
Nebelfarben ausserhalb eines Blitzes werden weiterhin unveraendert uebertragen.
Das Speicherformat und die Engine/cgame-Schnittstelle aendern sich nicht.

Die GL1-Aufhellung benutzt jetzt die echte Szenentiefe und eine feste
4096er Tiefenkarte der ueberdeckenden Decken des Levels. BSP, statische Architekturmodelle und
bewegliche Brush-Tueren werden unabhaengig von Kamerasicht/PVS beruecksichtigt.
Vegetationsmaterialien und die bekannten Baum-/Buschmodellfamilien werden
nur in diesem Wetterpass ausgeschlossen: Blattwerk darf kein Gebaeudedach
simulieren. Alpha-getestete, explizit nicht solide Draht-/Zaunkarten werden
ebenfalls ausgeschlossen. Einseitige Materialien tragen nur ihre Unterseiten
bei, damit obere Hang-/Dachflaechen nicht selbst zu Decken werden; echte
zweiseitige Abdeckungen wie Zeltstoff bleiben erhalten. Der normale
Modellschattenpfad bleibt unveraendert. Ein kleiner
Versatz zur sichtbaren Flaechenseite unterscheidet Fassade und Innenwand;
die Dachhoehentoleranz bleibt 0.5 Welteinheiten. Dachueberstaende schuetzen
auch darunterliegende Aussenflaechen. Keine ortsweite Umschaltung anhand der
Spielerposition und keine CPU-Strahlen pro Bildpunkt.

Die Aufhellung liegt jetzt vor der zeitlichen Aufloesung, damit Bild und
Verdeckungsmaske gemeinsam vom TAA-Jitter befreit werden. Die bereits vorhandene
History-Invalidierung an Blitzflanken verhindert Nachleuchten. MSAA verwendet
eine begrenzte Tiefenebenen-Toleranz mit Sprungpruefung; der Himmel bleibt auf
exakter Ferntiefe. So werden schräge Aeste nicht streifig und Fensterrahmen
nicht ueberblendet. Shader/Speicher werden beim ersten Weltbild vorbereitet;
der zusaetzliche Geometriepass laeuft nur waehrend eines Blitzes. Fehlt die
benoetigte GL-Unterstuetzung, bleibt ein sicherer, tiefengepruefter Himmelsblitz.

Regression: `tools/test_lightning_outdoor.py` verwendet vier in nativen
Screenshots bestaetigte m5l1b-Kameras: geschlossener Raum, intaktes Fenster,
Aussenansicht und zerbrochenes Fenster. Innenwaende/Fensterrahmen duerfen
hoechstens 3 RGB-Stufen abweichen; sichtbarer Aussenhimmel UND Aussenmauerwerk
muessen mindestens 10 Stufen heller werden. TAA aus/an, Save/Load und optional
MSAA werden getrennt geprueft. Zwei anfangs als freie Fassaden gewaehlte
Aussenbereiche liegen nach BSP-Strahlpruefung unter 16-24 Einheiten breiten
Dachueberstaenden. Sie bleiben als abgeschattete Negativkontrollen erhalten;
eine nachweislich freie Dachflaeche ist die zusaetzliche Positivkontrolle.
Diagnose-/Survey-Laeufe sind keine Abnahme und werden vom Deployment abgewiesen.

Zwischenstand `lightning-outdoor-r3`: 26 Aufnahmen mit MSAA4, TAA an/aus, optionalen
Modellschatten/AO ausgeschaltet sowie Save/Load bestanden. Innenbereiche
maximal 0.42 RGB-Stufen Abweichung; sichtbarer Himmel mindestens +70.85,
freie Aussenflaechen mindestens +31.09. Verdeckte Fassaden maximal 1.66.
726 aktive Blitzbilder: zusaetzlicher Pass im Median 2 ms, maximal 4 ms
auf dem Testrechner, einschliesslich GPU-Synchronisation zur Messung.
GL-Fehler und vorher anstehende Fehler jeweils 0; 703 Profildateien unveraendert.

Die anschliessende BT-Bildkontrolle fand Streifen und Dreiecke, die grosse
Helligkeitsmittelwerte uebersehen hatten. Ein unmaskierter Diagnosevergleich
isolierte die Deckenklassifikation. Der Tiefenreadback bewies: Die betroffene
Felsunterseite und der abgetastete Deckenwert gehoerten zur gleichen Ebene
(Abweichung nur 0.006-0.033 Welteinheiten). Die Korrektur zum Texelzentrum war
aber auf positive Z-Normalen beschraenkt. Sie gilt jetzt symmetrisch fuer
|Normalen-Z| ueber 0.25; die Schutzluecke ist dadurch konstant etwa 3.87 statt
wechselnd 0.85-7.37 Einheiten. Kein erhoehter globaler Bias oder Min-Filter.
Echte Felsunterseiten bleiben gleichmaessig abgeschirmt, freie Hang-/Boden-
flaechen blitzen. Die BT-Pixelpruefung kontrolliert beide Faelle nach Ende
des archivierten Einblend-Fades, jeweils mit TAA an/aus.
Steile Wandflaechen mit |Normalen-Z| unter 0.25 werden nur im Wetter-
Tiefenpass verworfen: ihre subtexelbreiten Fussabdruecke erzeugten sonst
isolierte schwarze Schlitze. Die Steigung stammt aus geometrischer Tiefe
und Weltmassstab, einschliesslich Modell-/Tueren-Transformation. Die zwei
Wetteruniforms werden anschliessend auf 0 gesetzt; regulaere Modellschatten
verwenden weiterhin alle bisherigen Flaechen.

Vier Tiefenproben glaetten die Verdeckungsgrenze per bilinearer Sichtbarkeit,
nicht per gemischter Dachhoehe. Jede Probe erhaelt ihre eigene Ebenenkorrektur.
Eine sichtbare Unterseite kann ihre eigene Abdeckung zudem analytisch erkennen:
Ihr Abstand zur gleichen Strukturebene betraegt nach dem 2-Einheiten-Normal-
versatz exakt -2/Normalen-Z. Ein Treffer innerhalb 0.125 Welteinheiten in einem
der vier Nachbartexel rekonstruiert diese Abdeckung auch an Rasterkanten.
Damit verschwinden die regelmaessigen Zacken am nahen Felsueberhang, ohne
andere Flaechen durch einen groesseren globalen Tiefenbias zu verdunkeln.

Eine zusaetzliche UHD-Kantenpruefung fand trotz kleiner Raum-Mittelwerte eine
ein Pixel breite helle Naht am Paravent. Der Tiefenabzug zeigte eine echte
Innenwand, keinen Kartenspalt: Die rechte Nachbarprobe sprang 36.989 Einheiten
zum Paravent. Quad-Ableitungen erfanden daraus eine nach aussen gerichtete
Normale und 68.7 Prozent Sichtbarkeit. Die Normalenberechnung waehlt nun pro
Achse den naechsten zusammenhaengenden Tiefennachbarn; bei zwei ungueltigen
Nachbarn bleibt der Normalenversatz 0. Der schmale Nahtbereich ist als eigene
Negativkontrolle im Fenster-/Innenraumtest enthalten.

`r_acLightningDebug 3` ermoeglicht einen einmaligen lokalen Tiefenreadback
pro Grafik-Kontext zur Diagnose. Normale Tests benutzen Wert 1, Spieler
standardmaessig 0; der Diagnosemodus ist keine Auslieferungsabnahme.

Beim Save-Screenshot eines fruehen Testlaufs trat ein separater Nullzugriff
auf: ein ausgeblendeter Spieler hatte einen Renderplatz, aber keinen gueltigen
Skelettzeiger. Minidump: CG_AttachEntity -> RE_TIKI_Orientation ->
TIKI_GetSkeletor(NULL). CG_ModelAnim prueft jetzt auch das Eltern-Skelett und
den Modellhandle, bevor Tags ausgewertet werden; der Anhang wartet andernfalls
einen Frame. Die normalen Ego-/Zoom-Modelle behalten diese gueltigen Zeiger.
Weitere Save/Load-Laeufe bestanden. Keine Aenderung am Saveformat.

Die unten beschriebene Ganzbildmischung ist der historische Vorlaeufer und
wird durch diese Innenraumkorrektur ersetzt.

Finale native Nachweise in `generated-local/CP09`:

- `lightning-outdoor-final`: 26 UHD-Aufnahmen, vier Kameras, TAA an/aus und
  Save/Load bestanden. Innenkontrollen einschliesslich schmaler Paraventkante
  maximal 1.29 RGB-Stufen MAD, geschuetzte Fassaden maximal 0.98. Sichtbarer
  Himmel mindestens +70.87, freie Geometrie mindestens +28.01. Der zuvor
  fehlerhafte Kantenspalt ist ohne TAA exakt unveraendert; der ganze geschlossene
  Raum hat dann maximal 2 RGB-Stufen Pixelabweichung. Visuell keine weisse Naht.
- `lightning-msaa-final`: gleiche 26 Aufnahmen mit echtem MSAA4 bei 1080p,
  Modellschatten/AO explizit ausgeschaltet. Innenkontrollen maximal 1.95 MAD,
  Fassaden maximal 1.97; Himmel mindestens +70.89, freie Geometrie +28.06.
- `lightning-bt-final`: e2l2, TAA an/aus, kurze Originalpulse, normales helles
  Nebelbild als Negativkontrolle, explizites Fastsky, Save/Load und Grafikneustart.
  Zusaetzliche spaete Pixelkontrollen unterscheiden Felsunterseite, steile
  offene Waende und freie Boeden; keine Streifen-/Zackenmuster in der Bildkontrolle.
- `lightning-sh-final`: gleiche Wetter-/TAA-/Save-/Grafikneustartkontrollen
  in Spearhead bestanden, ohne neue Skript- oder GL-Fehler.
- `lightning-legacy-final`: auf der alten game-DLL 3d6e1833 mitten im echten
  BT-Blitz gespeichert; finaler Kandidat stellt den Zustand ohne erneuten
  Flash-Aufruf wieder her und beendet ihn korrekt. Die alte Eingabe bleibt
  unveraendert. Engine-/cgame-/game-Hashes entsprechen dem finalen Kandidaten.
- Der synchronisierte Blitzpass benoetigte im finalen UHD-Lauf bei 724 aktiven
  Bildern 3 ms Median / 5 ms Maximum; im MSAA-Lauf 3 / 4 ms bei 733 Bildern.
  Das sind Messwerte dieses Rechners mit Debug-Synchronisation, keine allgemeine
  Leistungszusage. Kein zusaetzlicher Geometriepass ausserhalb des Blitzes.

Alle finalen Laeufe verwenden Engine `ca661d557584a447c7d61694b72b0b3c7558c1f90f8124cffc6ad34967ea9e5f`,
game `139b51a1d9bbd20b114e53f58aa8a64f262798e69265136e75a50f880f3ee057` und
cgame `d1cf1e29120439810254f65e1fefd34129e8a3b6209daf37d2d8efbe18cc39bb`.
GL-Fehler und vorher anstehende Fehler sind 0; 703 persoenliche Profildateien
bleiben hashgleich. Geprueft wurde der ausgelieferte GL1-Pfad; kein Anspruch
auf eine neue GL2-Implementierung oder persoenliche Gesamtkampagnenabnahme.

Auslieferung: Source `683eea53392ecca18434ef2c45a08f96e5e02533` mit den oben
geprueften drei Binaerdateien gemeinsam in CP08-r1 und CP09-r1 installiert.
Deployment verifiziert 9086 beziehungsweise 9090 Runtime-Dateien, 9072
Originaldateien sowie 703 unveraenderte persoenliche Profildateien.
Nachweis: `generated-local/CP09/lightning-outdoor-final/deployment.json`;
Rueckbausicherung im dortigen Unterordner `rollback`. Keine Assets oder
Missionsskripte ersetzt; kein Merge oder persoenliche Gesamtabnahme.

## 08.11.2026: Blitzwirkung vom vereinfachten Himmel trennen

Die vorherige Sperre schuetzte die Spieleroption, entfernte aber zugleich den
Wettertrick, mit dem der Himmel aufgehellt wurde. Der Kontrolllauf
`generated-local/CP09/lightning-before` bestaetigt: Wetternebel wird heller,
der detaillierte Himmel bleibt dunkel. Die Skriptsperre bleibt erforderlich;
Blitze erhalten jetzt einen eigenen temporaeren Renderzustand.

Die aktiven Wetterpakete unterscheiden sich: Nur WCR-AA setzt
`weather_skyisbright`; die Erweiterungen besitzen dieses Flag nicht. Daher
uebersetzt `ScriptThread::SetCvarEvent` die alten Wetter-Schreibversuche in
`level.ac_weather_flash_requested`, sobald Wetterobjektzaehler und normale
Nebelfarbe initialisiert sind. `World::UpdateFog` verbindet diesen Auftrag
mit der Aufhellung gegenueber `level.farplane_color`. Rueckkehr zur normalen
Farbe loescht den Auftrag auch bei veraltetem Ruecksetzwert 1. Eine spaetere
helle Nebelfarbe allein loest keinen Blitz aus.

Fehlt die neue Levelvariable in einem alten Spielstand mitten im Blitz,
wird sie einmalig aus dem AA-Gewitterflag oder dem exakten alten weissen
Flash-Farbwert der Erweiterungen wiederhergestellt. Danach ist ihr Wert 0
verbindlich und aktiviert keine weitere farbbasierte Erkennung. Die vorhandene
Levelvariablenspeicherung uebernimmt den Wert; kein neues Archivfeld oder
Speicherformat. Level-/Skriptvariablen werden vor dem World-Objekt restauriert.
Ein optionaler letzter Wert in `CS_FOGINFO` uebertraegt den Blitz an cgame und
Renderer; alte Configstrings bedeuten Zustand 0.

Der aktive GL1-Renderer mischt die fertige 3D-Szene kurz gegen Weiss
(Alpha 0.65 mal normierte Blitzstaerke). Damit werden auch Wolken, nahe Modelle
und Umgebung erfasst, ohne die Himmelsstruktur gegen eine einfarbige Flaeche
auszutauschen. Die originalen Donner-/Regen-/Lichtobjekte und Blitzabstaende
bleiben erhalten. Der Effekt liegt nach TAA/Objekt-Blur und vor HUD/Menues,
einschliesslich des direkten Set2DWindow-Pfads. TAA verwirft seine Historie an
Blitzflanken, damit auch der originale helle Nebel nicht nachzieht.

`r_fastsky` wird dabei weder gesetzt noch gespeichert. Eine ausdrueckliche
Spielerwahl 1 bleibt ebenfalls erhalten. Engine/cgame besitzen passende
Versions-/Strukturgroessenpruefungen fuer die erweiterte refdef-Schnittstelle;
die drei getesteten Binaerdateien werden gemeinsam ausgeliefert. GL2 uebernimmt
das Feld strukturell, der neue Effekt ist fuer den ausgelieferten GL1-Pfad
implementiert und geprueft.

Bei der GL-Pruefung zusaetzlich einen vorhandenen leeren Wolken-Zeichenaufruf
gefunden: Skyboxen ohne eigene Wolkengeometrie riefen LockArraysEXT mit null
Vertices auf. Diesen leeren Pass ueberspringen; sichtbare Geometrie bleibt
erhalten. Danach sowohl vor als auch nach dem Blitzpass GL-Fehler 0.

Native Regression mit `tools/test_weather_lightning.py`: AA m5l1b und SH t1l3
aus Savekopien, BT e1l1 als getrennte Renderpruefung, jeweils TAA an/aus,
Blitz/Rueckkehr, negative Nebelkontrolle, explizites Fastsky 1, Save/Load mitten
im Blitz und Grafikneustart. Eine endliche Folge benutzt die originalen
flash/unflash-Einstiege mit den echten 0.2/0.1/0.1-Sekunden-Abstaenden der
ersten Donner-Variante; alle drei Pulse werden gerendert und enden auf 0.
Kein zusaetzlicher zufaelliger Endlos-Gewitterthread im Test.

AA in UHD ebenfalls bestanden: Helligkeitsmittel im oberen Bildbereich mit
TAA 84.50 -> 193.15 -> 84.73; Weltbereich 67.14 -> 188.83 -> 67.10.
Deckender Kompassbereich weicht beim Blitz nur um 0.75 RGB-Stufen ab
(Toleranz 2; fehlerhafter erster HUD-Pfad lag bei 94.70).
Vorpruefungen: lightning-aa-r3, lightning-sh, lightning-bt-r2, lightning-release
unter generated-local/CP09. Diese ersten Testfixtures setzten faelschlich auch
in den Erweiterungen das AA-Wetterflag; der Paket-Audit deckte diese Luecke
auf. Finale Pruefungen verwenden ausschliesslich die originalen flash/unflash-
Einstiege ohne kuenstliches Flag: lightning-release-r2 (UHD), lightning-sh-native
und lightning-bt-native. Auch nach explizitem Fastsky 1 und Unflash erzeugt
eine normale helle Nebelfarbe keinen Blitz. Die BT-Direktstart-Skriptfehler sind unveraendert
im alten Kontrolllauf enthalten; die Intro-Schwarzblende wird ausschliesslich
in dessen Testprofil aufgehoben. Das ist keine BT-Missionsabnahme.

Zusaetzlicher regulaerer BT-Save e2l20000 (e2l2, Waldweg zu Fuss) in
`lightning-bt-native` besteht dieselben Pruefungen ohne Skriptfehler. Die ersten
Bilder enthalten noch die normale Einblendung des Missionsstarts; nach
Save/Load und Grafikneustart sind Himmel, Welt und unveraenderte Untertitel visuell
geprueft, ohne Intro-Korrektur im Testprofil. Alle 813 protokollierten
Blitzframes melden GL-Fehler 0, ebenso deren eingehenden Rendererzustand.

`tools/test_legacy_lightning_save.py` prueft zusaetzlich die alte Savefassung:
alte Engine/game/cgame erzeugen einen BT-Save nach genau einem echten Flash,
waehrend der Skriptthread nur noch wartet. Die neuen Binaerdateien laden
denselben unveraenderten Save und zeichnen den Blitz bereits vor einem neuen
Flashbefehl. Anschliessendes Unflash und gewoehnlicher heller Nebel bleiben
ohne Effekt. Kein kuenstliches AA-Flag und kein neuer Marker im alten Fixture;
Nachweis `lightning-legacy-save`, Skriptfehler und GL-Fehler 0.

Getestete Binaerdateien: Engine 040ae62d, game 884d675a, cgame 01de08c6.
Alle 699 persoenlichen Dateien einschliesslich Spielstaenden und Einstellungen
sind durch die Tests unveraendert. Keine Wetter-/Missionsskripte oder Assets
in der Installation ersetzt.

Auslieferung Source 9e6d88b7: Engine/game/cgame gemeinsam in CP08-r1 und
CP09-r1 installiert. 9086/9090 Runtime-Dateien und 9072 Originaldateien
verifiziert, alle 699 persoenlichen Dateien beim Deployment unveraendert.
Rueckbausicherung und Bericht unter
generated-local/CP09/lightning-release-r2/{rollback,deployment.json}.
Kein Merge und keine persoenliche Gesamtspielabnahme vorweggenommen.

## 08.11.2026: Spielerwahl gegen Gewitterskripte schuetzen

Die reine Profilkorrektur vom 28.10. war unvollstaendig. Das aktive WCR-
`global/weather.scr` setzt in `flash` die Spieleroption `r_fastsky` auf 1
und stellt in `unflash` den in einer Levelvariable gemerkten Wert wieder her.
Dadurch wird eine temporaere Wetterwirkung als archivierte, kampagnenweit
geteilte Grafikoption behandelt. Unterbrechungen und veraltete gespeicherte
Ruecksetzwerte koennen 1 dauerhaft erhalten. Der genaue historische Moment
der Umstellung im Nutzerprofil ist nicht protokolliert.

Reproduktion mit bisheriger DLL und Kopie des aktuellen m5l1b-Quicksaves:
ausdrueckliche 0 wird durch den echten Wetter-Flash zu 1; eine anschliessende
Ruecksetzung mit veraltetem Levelwert 1 stellt ebenfalls 1 ein.

`ScriptThread::SetCvarEvent` ignoriert jetzt ausschliesslich skriptseitige
Schreibzugriffe auf `r_fastsky` (unabhaengig von Gross-/Kleinschreibung).
Die normale Konsolen-/Menuewahl und deren Speicherung bleiben unveraendert.
Regen, Donner, Farplane-Farbe und Wetterobjekte werden nicht entfernt.
Der Schutz greift auch fuer fortgesetzte Skriptthreads aus alten Saves;
kein geaendertes Speicherformat und kein Austausch archivierter Skripte.

Persoenliches AA-Profil und gemeinsame Preferences mit Sicherung auf 0
zurueckgesetzt. SH/BT standen bereits auf 0. Nur diese zwei Konfigurations-
zeilen geaendert; alle 697 anderen Dateien einschliesslich Saves unveraendert.
Nachweis: generated-local/CP09/sky-player-choice/profile-repair.json.

Regressionswerkzeug: tools/test_sky_player_choice.py. Es verwendet getrennte
Profile, die installierte Engine und wahlweise die alte oder neue Spiel-DLL.
Quellen/Spielstaende/WCR-Pakete werden nicht in Git aufgenommen.

Native Nachweise: sky-choice-baseline-r2 reproduziert die alten Wetter-
Schreibzugriffe. sky-choice-release (AA m5l1b), sky-choice-expansions (SH t1l3)
und sky-choice-bt (BT e1l1) pruefen blockierte Skriptwerte in beiden Richtungen,
unveraenderte andere Skript-Cvars, 18 Sekunden laufende Mission, Save/Load,
Grafikneustart und erhaltene explizite Spielerwahl nach Prozessneustart.
AA-On wird ausserdem beim Start von SH und BT aus denselben Preferences gelesen.
AA-Bildvergleich zeigt bei 0 Wolken, bei ausdruecklicher 1 die vereinfachte
Flaeche. 699 persoenliche Dateien bleiben durch alle Tests unveraendert.

Abnahmegrenze: Direkteinstieg in BT e1l1 meldet bereits mit der alten DLL
mehrere WCR-Skriptfehler (prespawn/spawn, Parade und Autotruck). Saemtliche
Fehlerorte und Meldungen des Korrekturlaufs sind auch im alten Kontrolllauf
enthalten; keine pauschale Fehlerunterdrueckung. Der aeltere e3l3-Save zeigte
ebenfalls Fahrzeugskriptmeldungen und ist kein fehlerfreier Regressionstest.
Ein direkter SH-t1l3-Start meldete einen friendly.scr-Spawnfehler; die
abschliessende SH-Pruefung verwendet den vorhandenen Save und laeuft ohne
Skriptfehler. Diese Nebenbefunde sind durch den Himmel-Fix nicht behoben.

Getestete game.dll: 3d6e1833ec1709f903d9177e748ba34224b3a883e14576b2074acf8624fa590c.
Engine f567924a, cgame, Spielskripte und Assets unveraendert.
Zusammengefuehrtes Ergebnis: generated-local/CP09/sky-choice-release/result.json.

Auslieferung Source 6ae93008: ausschliesslich game.dll in CP08-r1/CP09-r1
ersetzt. 9086/9090 Runtime-Dateien und 9072 Originaldateien verifiziert;
699 persoenliche Dateien beim Deployment unveraendert. Rueckbausicherung und
Nachweis unter generated-local/CP09/sky-choice-release/{rollback,deployment.json}.
Kein Merge; keine persoenliche Gesamtspielabnahme vorweggenommen.

Die folgenden Abschnitte dokumentieren die vorherigen Korrekturen.

Ursache: Das persoenliche Profil verwendet `r_fastsky 1`. Der Renderer ersetzte
den Himmel in einem Clear-Pfad durch festes RGB (0.5, 0.5, 1.0), unabhaengig von
der Tageszeit der Karte. In t1l1 wird daraus mit Gamma 1.3 eine helle blauviolette
Flaeche. Die Nacht-Lichtkarten und die WCR-Missionsskripte sind intakt.

Korrektur: Der vereinfachte Himmel verwendet die Farplane-Farbe der aktuellen
Ansicht mit dem bestehenden identityLight-Faktor. Keine globale Abdunklung,
keine Aenderung von Profilen, Saveformat, Missionen oder normalem Skybox-Modus.
Auch ohne aktivierten Nebel wird kein veralteter GL-Nebelzustand benutzt.

Native Pruefung: `tools/test_night_sky.py`, getrennte Profile, Kopie des bestehenden
Spearhead-Spielstands t1l10001. Feste Testkamera im Aussenbereich; vereinfachter
Himmel, normaler Himmel und vereinfachter Himmel ohne Nebel. Vorher 493867 bzw.
493797 Pixel des fehlerhaften hellblauen Hintergrunds; nachher jeweils null.
Screenshots vorher/nachher visuell geprueft: dunkler Nachthimmel, Landschaft und
Scheinwerfer erhalten. Vorhandener Spielstand erfolgreich geladen. Alle 462
persoenlichen Profildateien nach beiden Testlaeufen byteidentisch.

Build: openmohaa RelWithDebInfo erfolgreich. Getestete EXE SHA256:
`2ba609fbf0b604092d12e9debe4132d4c08d6b9e4ba2b5abf24987f366a79db9`.
Berichte/Bilder: generated-local/CP09/night-sky-{before,fixed},
profiles-local/night-sky/night-sky-{before,fixed}.
Die natuerliche Missionsabnahme durch den Nutzer bleibt offen.

## 28.10.2026: Vollstaendigen Himmel in allen drei Profilkontexten aktivieren

Die vorherige Korrektur schaltete den vereinfachten Himmel nicht ab. Im
persoenlichen Profil stand weiterhin `r_fastsky 1`, sowohl in den drei
omconfig.cfg-Dateien als auch in main/ac_preferences.cfg. Damit blieb die
eigentliche Himmelsdarstellung zugunsten der einfarbigen Flaeche ausgeblendet.

Auf die erneute Meldung zu Spearhead t1l3 hin diese vier Einstellungen auf
`r_fastsky 0` gesetzt, mit lokaler Sicherung der vorherigen Dateien. Keine
Engine-, Karten- oder Saveformat-Aenderung; die gemeinsame Einstellung gilt
fuer beide CP08/CP09-Starter und wird beim Kampagnenwechsel weitergegeben.
Die normale Grafikoption bleibt bedienbar, wird nicht zwangsweise gesperrt.

Pruefung: getrennte Kopien der Konfigurationen in AA, SH und BT gestartet;
alle melden r_fastsky 0. Kopie des aktuellen SH-Quicksaves erfolgreich als
t1l3 geladen; Wert bleibt 0. Bildvergleich mit nach oben gerichteter Testkamera:
bei 1 einfarbige Flaeche, bei 0 strukturierter Himmel. Erste Versuche ohne
Developer-Modus beim Start aktivierten die Testkamera nicht; erst der
abschliessende Lauf mit Developer-Modus belegt diesen Bildvergleich.
Testdaten: generated-local/CP09/full-sky-20261028; isolierte Profile unter
profiles-local/full-sky-20261028*. Der natuerliche Missionsablauf wurde damit
nicht erneut durchgespielt. Persoenliche Saves und Fortschritt unveraendert;
nur die vier genannten Konfigurationsdateien wurden gezielt geaendert.

Auslieferung: Engine ce1d5be3 in CP08-r1 und CP09-r1 installiert; 9086/9090
Laufzeitdateien und 9072 Originaldateien geprueft, 462 persoenliche Dateien
unveraendert. Rollback und Deploymentbericht unter night-sky-fixed.
