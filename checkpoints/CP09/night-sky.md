# Spearhead D-Day: heller Himmel im vereinfachten Modus

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
