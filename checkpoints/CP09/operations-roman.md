# Operations: roemische Missionsnummern

Direkter Nutzerauftrag vom 20.10.2026 waehrend CP09.

Einzelne Kartenmarker und die Seitenliste verwenden I bis XV. Gruppenmarker
behalten arabische Zahlen fuer die Anzahl ihrer sichtbaren, freigeschalteten
Missionen. Laengere roemische Marker werden um denselben Kartenmittelpunkt
verbreitert. Missionen, Fortschrittsdatei und Auswahlkommandos bleiben gleich.

Engine-Build RelWithDebInfo erfolgreich. Sechs native 1920x1080-Menuepruefungen
ueber AA/SH/BT mit isolierten Fortschrittsstaenden bestanden: Startzustand,
VI einzeln, italienische Zweiergruppe, europaeische Dreiergruppe, XIII einzeln
und vollstaendig freigeschaltete Regionen. Beschriftung, gesperrte Missionen,
Auswahlkommandos und beide Richtungen des italienischen Gruppenwechsels anhand
der erzeugten nativen Menue-Ressourcen geprueft. Screenshots von Europa mit XIII
und Nordafrika/Italien visuell kontrolliert. Keine simulierte Mausabnahme.

Test: `tools/test_operations_numbers.py operations-roman-r1`.
Lokale Nachweise: `generated-local/CP09/operations-roman-r1/`.
427 persoenliche Profildateien nach dem Test bytegleich.

Auslieferung erfolgt mit `tools/deploy_cp09_engine.py operations-roman-r1`:
nur Engine fuer beide lokalen Starter CP08-r1/CP09-r1, vorher Hashpruefung,
Rueckbaukopie und anschliessende Manifest-/Profilpruefung. Die urspruengliche
CP09-Gesamtregression bleibt als historischer Ausgangsstand dokumentiert;
dieser Nachtest ersetzt keine vollstaendige CP09-Abnahme.
