# Status

Stand 14.10.2026: **CP01-r1 ist implementiert und lokal spielbereit. Die vollständige CP1-Abnahme ist wegen dokumentierter Testlücken noch offen.** Kein CP2, kein Merge, keine persönliche Nutzerabnahme behauptet. Der Nutzer hatte die autonome Fortsetzung bis CP1 ausdrücklich freigegeben; weitere „mach weiter“-Zwischenfragen sind dafür nicht nötig.

Startdateien und Bedienung: [CP01-r1 starten](CP01-r1-START.md). Technischer Stand: [CP1-Bericht](checkpoints/CP01/CP01-r1-REPORT.md). Engine-/Quellcommit `114c0d8d941a15b5d748a058cb9d529319ac5506`; eigenes lokales Paket mit CRC und SHA-256 geprüft.

Die HUD-Skalierung umfasst alle drei Kontexte, proportionale Kompass-/Menü-/Textdarstellung, sichere Randverankerung, Optikmasken und gespeicherte Größen einschließlich Kontextwechsel. 24 Auflösungs-/Kampagnenläufe, 42 Einstellungs-Neustartprüfungen sowie finale Text-/Optik-/Save-Proben liegen vor. Frühere native Klicktests fanden und prüften den Menüreglerfehler. Spätere Fensteraufnahme scheiterte wiederholt mit `FrameArrived timed out`; echte Windows-DPI-Wechsel und Alt-Tab/Fensterziehen sind nicht vollständig geprüft. Ebenso bleibt die wahrnehmbare Einzelwirkung jedes vorhandenen WCR-Optionspunkts offen.

CP00a ist integriert und mit 27 kontrollierten Kills sowie echter Gesundheits-/Munitionsaufnahme geprüft; zusätzliche Afrika-/Italien-Diagnosen bleiben unvollständig. [CP00a-Bericht](checkpoints/CP00a/CP00a-r1-REPORT.md). CP0-Referenz und Originaleingaben unverändert. Der gewünschte Verzicht auf den BT-Finaltest bleibt bestehen. Frühere offene CP0-Fälle: [historischer Status](checkpoints/CP00/STATUS-before-CP1.md).

Privates GitHub-Projekt: Entwurfs-PR #1 CP0, #2 CP0a, #3 CP1. Push-/CI-Nachweise werden im Liefernachweis festgehalten. Keine Spielassets, Saves oder Screenshots in Git. Lokale ZIP-/Git-Sicherungen vorhanden; keine externe, gegen dieselben Schreibrechte geschützte Sicherung behauptet.
