# Allied Campaign Options: klare Bereiche

Nutzerauftrag 21.10.2026: das gewachsene Optionsmenue aufraeumen.

- Eine gemeinsame 16:9-Seite mit DISPLAY & HUD, BLOOD EFFECTS und ADDITIONAL OPTIONS.
- Gleichmaessige Zeilen, linksbuendige Beschriftungen, ausgerichtete Schalter,
  goldene Abschnittstitel und dezente Flaechen auf dem vorhandenen Nutzerhintergrund.
- Kurze englische Erklaerungen fuer Bluteffekte, Trefferreaktion und BT-Dropregeln.
- Alle elf bisherigen Einstellungen, Bereiche, Standardwerte und Cvar-Bindungen
  erhalten. Hit flinch weiterhin ausschliesslich in 10-Prozent-Schritten.
- Die drei numerischen Groessenfelder entfernen bei inaktiver Anzeige lediglich
  ueberfluessige nachgestellte Nullen. Gespeicherte Genauigkeit und Eingabe bleiben
  erhalten. Beispiel: 1.660000 wird als 1.66 angezeigt.
- Paketierung verwendet nun direkt die kanonische URC-Datei statt alte
  Laufzeitpakete durch Textaustausch zusammenzusetzen.

Native Tests mit getrennten Profilen: AA 1920x1080, SH 1280x960, BT 3440x1440;
Schriftgroesse 100% und 65%, unveraenderte Menuegeometrie, keine ueberlappenden
Steuerelemente. Alle sieben Schalter und vier Regler bedient. Hit-flinch-Drag
erreicht alle elf erlaubten Werte. Defaults stellt alle elf Werte wieder her;
Back kehrt ins aufrufende Hauptmenue zurueck. AA-/BT-Screenshots visuell geprueft.
427 persoenliche Profildateien im Test unveraendert. Keine neue Durchspielabnahme.

Werkzeuge: `package_flinch_options.py`, `test_options_layout.py` und
`deploy_cp09_engine.py --options-layout`. Lokale Testbilder und Berichte liegen
unter `generated-local/CP09/options-layout-r*/`. Fruehe Testlaeufe fanden einen
nicht vorhandenen Font und abgeschnittene Dezimalzahlen; beides ist korrigiert.

Finaler Lauf `options-layout-r5` bestanden und fuer CP08-r1/CP09-r1 installiert.
Quelle: `a06a52d78f5640b1ed3b79f65e1e33eb1200d9eb`.
Engine-SHA256: `8a5a2cefcde606bc6fed2056050c4828c9b005665e244c23417720ddbf45f356`.
Integritaet: 9.072 Originaldateien geprueft, 9.086 CP08- und 9.090 CP09-Dateien
gegen aktualisierte Manifeste bestaetigt. 427 persoenliche Profildateien
unveraendert. Rueckbaukopien unter dem lokalen Testbericht im Ordner `rollback`.
