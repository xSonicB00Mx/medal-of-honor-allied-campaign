# Operations- und Mission-List-Korrekturen

2026-10-16. TriggerSave verwendet fuer automatische Kontrollpunkte savegame statt autosavegame. Im Score-Run wird dieser Trigger nun vor dem Speicherbefehl still verworfen. Manuelle Save/Load-Versuche behalten die sichtbare Sperrwarnung.

AC_UIItem erhielt mehrfach Argumente aus dem zweifachen va()-Ringpuffer. Bei Missionen und Markern ueberschrieb der Widgetname den Klickbefehl schon vor der Ausfuehrung. Argumente besitzen jetzt eigene Zeichenketten bereits bei der Parameteruebergabe. Die gewaehlte Mission wird gelb mit Auswahlpfeil markiert; abgeschlossene Missionen sind auswaehlbar und ueber Replay Mission startbar.

Unter der Karte ersetzen Easy/Medium/Hard die Legende. Die Wahl wird ueber Inhaltskontext-Neustarts mitgenommen und beim Missionsstart angewendet. Operations-Replays behalten die bisherigen Kampagnen-Einstellungen separat und stellen sie beim Verlassen/Abschluss wieder her. Die bestehende Fortschrittssperre fuer Replays bleibt bestehen. Mission List hat einen mittig angeordneten, 912 Einheiten breiten Titel.

Pruefung: Engine und game.dll RelWithDebInfo gebaut. Highscore empty menu-fixes-auto-r1: nativer trigger_save plus autosavegame ohne Meldung; manuelle Sperrmeldung, Score-Abschluss und Fortschritts-/Save-Sentinels erfolgreich. menus-r1: erzeugte Marker-/Missions-/Schwierigkeitsbefehle und Titelgeometrie geprueft, Screenshots gesichtet. mouse-r2: echter Mausklick auf Bizerte und Easy erfolgreich. finish-aa-r3: native bsptransition vom AA-Endlevel m2l3 beendet Replay, Fortschrittsdatei und Save-Sentinels bytegleich. replay-final-r1: echter AA-nach-BT-Kontextstart mit Hard und Rueckkehr zur vorherigen Schwierigkeit. Kein vollstaendiges manuelles Durchspielen behauptet.

BT e3l4 meldet bestehende Script-Diagnosen (PathNode/AISpawnPoint); dieselben Diagnosen wurden mit dem vorherigen installierten Build in baseline-r1 bestaetigt. Fruehe Testfixtures wurden korrigiert: regulare Starts erlauben keine Test-Skriptbefehle, und ein vorzeitig eingereihter Quit blockierte den nachgereihten nativen gamemap-Befehl. Der abschliessende AA-Test wartet auf AC_REPLAY_COMPLETE.

Persoenliche Nutzerabnahme und Merge ausstehend. Quelldaten und Nutzerprofil werden nicht zum Testen veraendert.
