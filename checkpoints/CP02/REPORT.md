# CP02-r1 – Red hit mist

Implementiert, lokal startbar und getrennt gesichert. Neuer gespeicherter Schalter **Red hit mist** auf der englischen HUD-Seite. Kumulative Basis CP01-r2/WCR/BT-Drops, Enginequellstand 450ef22eb9e9003a9001b187b2e8b917a5c78984. Start-CP02-r1-AA/SH/BT.cmd.

AA/SH/BT: je vier Waffen (Colt45, MP40, Kar98, BAR) mit Schalter aus/an, bestätigte Körpertreffereffekte je Gruppe; 42 protokollierte Nebelereignisse insgesamt. Echte Waffenfeuer in normalen Maps an isoliert erzeugtem stationärem Diagnosegegner mit erhöhter Testgesundheit. Save/Load und gespeicherter Aus-Wert nach Zurück geprüft. Normale Spielgegner/Schadenswerte werden nicht geändert. Kein CP3-Weltblut oder Körperwunden enthalten.

Die effektiven Human-Uniform-Emitter und bodyhitpuff-Shader sind in allen drei Kontexten inventarisiert. Nur ihre RGB-Werte werden für eine Emission skaliert und sofort wiederhergestellt. Lebenszeit, Bewegung, Größe und Alpha bleiben erhalten; Shader benutzt Alpha-Blending. Der Aus-Zweig bleibt die WCR-Basis. Kein Material/Originalasset ersetzt. AA-Sichtaufnahme zeigt roten Nebel, Mündungsrauch bleibt grau. Eine vollständige Material-Sichtmatrix (Holz/Stein/Metall/Explosion/Fahrzeug) ist noch offen; die Codeselektion schließt diese Effekt-IDs aus. Die ursprüngliche Distanzbegrenzung gleichzeitiger Körpernebel wird bei aktiver Option durch genau einen Aufruf pro empfangenem Körpertreffer ersetzt.

Ungültige Diagnosen v1 (developer=0 verhinderte Skriptbefehle) und v2 (Waffenwechsel zu kurz) sind erhalten und zählen nicht als bestandene Matrix. v3 korrigiert beide Ursachen. Kein Nutzerabnahme-/Mergeanspruch. Frühere CP1-DPI/WCR-Wirkungsgrenzen bleiben offen. Der Nutzer hat eigenständige Weiterarbeit bis CP5 autorisiert.

Lokales Paket und Hash: package.json; enthält Originaldaten und bleibt von GitHub ausgeschlossen. Rückbau durch Start des unveränderten CP01-r1/r2 mit dessen eigenen Profilen. Bei Nutzerprüfung: AA/SH/BT starten, **Red hit mist** aus/an vergleichen, Größe und Bewegung beobachten, Holz/Stein/Metall beschießen, Einstellung nach Neustart prüfen.
