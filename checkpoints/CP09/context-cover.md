# Kampagnenwechsel ohne sichtbare Desktop-Startluecke

Der bisherige Windows-Kontextwechsel startet einen neuen Prozess, der auf das
Ende des alten wartet. Zwischen Zerstoerung und Neuerstellung des SDL-Fensters
war deshalb der Desktop sichtbar.

Eine kurzlebige Instanz derselben EXE zeichnet jetzt ausschliesslich eine
schwarze Ladeblende mit englischem Hinweis. Sie laedt weder SDL noch Spiel,
Assets, Konfiguration oder Savegames. Der alte Prozess wartet auf die fertig
gezeichnete Blende; der neue meldet nach dem ersten praesentierten Frame seines
sichtbaren Spielfensters die Uebernahme. Danach beendet sich die Blende.
Im Fenstermodus deckt sie das bisherige Spielfenster ab. Bei Vollbild deckt sie
den Spielmonitor ab und folgt dessen Aufloesungswechseln. Keine feste Pause
und keine Aenderung der Kampagnen-/Save-/Kontrolluebernahme.

Fehlertoleranz: Endet der neue Prozess vorzeitig, schliesst die Blende ebenfalls.
Zusaetzlich maximal 120 Sekunden Lebenszeit; ein fehlgeschlagener Blendenstart
blockiert den Spielwechsel nicht dauerhaft. Kein neuer Installer/Helper erforderlich.

Native Tests in getrennten Profilen:

- Alle sechs gerichteten Wechsel zwischen AA, SH und BT, je einmal im Fenster
  und im UHD-Vollbild (3840x2160); sowohl Menue- als auch direkte Levelstarts.
- Nach letzter Anpassung des fruehen Helper-Einstiegs erneuter Wechsel im
  Fenster und bei 1280x720-Vollbild mit Rueckkehr zur UHD-Desktopaufloesung.
- Sichtbare Fenster etwa alle 10 ms abgefragt: keine Probe ohne altes/neues
  Spielfenster oder Ladeblende waehrend des beobachteten Uebergangs. Jede Blende
  meldet ready vor Neustart und endet nach presented; keine verbliebenen Helper.
- Abbruchtest mit isoliertem Dummy-Zielprozess: Blende gezeichnet, anschliessend
  Zielprozess beendet; Blende beendet sich erfolgreich innerhalb des Testlimits.

Werkzeuge: `test_context_cover.py`, `test_context_cover_failure.py`.
Berichte unter `generated-local/CP09/context-cover-*`; keine persoenlichen Saves
verwendet. Fenster-/Render-Synchronisation getestet, keine pixelweise Videoanalyse
oder Aussage ueber saemtliche Grafiktreiber und Monitorkonfigurationen.
