# Credits nur nach Berlin

2026-10-19: Bisher erfolgte die AA-/BT-Fortsetzung erst nach Credits-Ende oder Skip. Gewoehnliche Einzelmissionen starteten keinen Abspann.

Lokale Script-Overlays fuehren AA nach Flucht, Medaillenvergabe und Ausblenden, vor THE END zur naechsten Operation. BT geht nach seiner originalen Outro-Sequenz vor RollTheCredits weiter. Passender Allied-Campaign-Kontext und originales Abschlussflag bleiben erforderlich. Die bestehende Progressionslogik verwaltet Abschluss, naechste Operation und Wiederholungen. Alte Credits-Endhooks bleiben als Rueckfallebene erhalten. Keine Engine-/DLL-/Saveformat-Aenderungen. Originale und WCR-Scripts bleiben lokal; nur die Pakettransformation ist versioniert.

Berlin bleibt unveraendert: t3l2 -> briefing/briefingd1 -> credits. Manuell aufgerufene Credits werden nicht gesperrt.

## Native Tests und Grenzen

Isolierte Profile mit vorbereitetem Fortschritt und synthetischem Aufruf der echten Abschlussroutinen:

- aa-final-r1: completed 16383, danach Berlin-Einfuehrung in SH ohne AA-Abspann.
- bt-final-r2: completed 4095, danach Ardennen-Einfuehrung in SH ohne BT-Abspann.
- aa-replay-r2 und bt-replay-r1: AC_REPLAY_COMPLETE, Hauptfortschritt und Resume erhalten.
- berlin-final-r2: completed 32767, resume 15, echtes Schlussvideo debriefing.roq gestartet. Anschliessenden spmap-credits-Aufruf im unveraenderten Script geprueft. Video und Abspann nicht vollstaendig abgewartet.
- Direkte BT-/SH-Finalmapstarts erzeugen schon ohne Patch acht beziehungsweise zehn Spawn-/Waittill-Meldungen. Vergleich mit baseline-11 und baseline-14 bestaetigt identische Meldungen; keine zusaetzlichen Fehler durch den Patch.

Keine natuerliche Missionsdurchspielung oder persoenliche Nutzerabnahme behauptet. Rohprotokolle lokal unter profiles-local/campaign-finales. Keine persoenlichen Spielstaende verwendet.
