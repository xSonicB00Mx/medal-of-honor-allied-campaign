# CP08-r1: vorhandene SH-/BT-Ladebilder im Breitbild

Die Nutzerergaenzung vom 15.10.2026 ersetzt fuer diese Ladebilder die bisherige Vorgabe, ihre schwarzen Aussenraender unveraendert zu lassen. Alle neun Spearhead- und elf Breakthrough-Kampagnenladebilder sind jetzt proportional vergroessert und zentriert. Hierfuer wurden keine Gemini-Anfragen gestellt. Die 36 offenen Hintergruende des getrennten Outpainting-Auftrags bleiben offen.

Die Bildinhalte sind nicht exakt 16:9: SH liegt ungefaehr bei 1,90 bis 2,11:1, BT mit seinem ausgefransten Fotorand bei 1,86:1. Entfernt werden nur breite schwarze Aussenflaechen; die Motive und Fotorandverzierungen bleiben vollstaendig erhalten. Deshalb bleiben in 16:9 je nach Motiv schmale horizontale Balken. Auf Ultrawide wird die gesamte Bildhoehe genutzt und seitlich zentriert. In 4:3 bleibt der urspruengliche Ausschnitt erhalten. Die Ladeanzeige behaelt ihre bisherige Position und Groesse.

## Umsetzung und Nachweise

Die neue `loadingbackground`-Direktive zeichnet die zusammengefuegten Originaltexturen anhand expliziter Bildgrenzen. Der lokale Packager respektiert den vorhandenen Standard `r_loadjpg=1`, erhaelt alle anderen URC-Anweisungen einschliesslich `loadingbar.txt` und erstellt separate `zzzzzzz_AC_LoadingZoom.pk3`-Pakete fuer `mainta` und `maintt`. Der 640x480-Bildinhalt liegt unverkleinert in einer 1024x512-Textur. Die Grenzen enthalten zwei zusaetzliche Quellpixel als Reserve fuer dunkle Bildraender. AA, Hauptmenues und Briefings erhalten dadurch keine neue Ladebild-Direktive.

- RelWithDebInfo-Build erfolgreich; Engine-Quellstand `dcd7b900f8b4b420061284290568c296b6bc423c`. Keine Spiel-/cgame-DLL- oder Saveformat-Aenderung.
- Alle 20 Ladebilder in 1920x1080 nativ gerendert und visuell geprueft. Zusaetzlich SH in 1920x1200, BT in 2560x1080 und AA-Hauptmenue, AA-Ladebild sowie Einsatzkarte geprueft. Keine Ressourcen-/Layoutfehler.
- Zwei native 1280x960-Referenzpaare zeigen denselben 4:3-Ausschnitt. Winzige Filterunterschiede an der ehemaligen Zweitextur-Naht bleiben: mittlere Kanalabweichung jeweils kleiner als 0,02 von 255, ausserhalb der animierten Ladeanzeige. Keine Behauptung pixelgenauer Identitaet.
- Nach dem Einbau SH und BT erneut direkt aus der installierten Runtime gestartet; zusammen elf erfolgreiche isolierte Testlaeufe. Alle 32 eigenen Runtime-Dateien gegen das Manifest geprueft.
- 9.072 Originaldateien, 9.000 Runtime-Basisdateien, acht MP1-Eingaben und 26 Dateien des aktiven Nutzerprofils unveraendert. WCR-Basis unveraendert. Keine Tests im Nutzerprofil.

Die Tests pruefen die Ladebild-Darstellung, keinen neuen vollstaendigen Missionsdurchlauf. GL2 wurde nicht getestet. Persoenliche Abnahme und Merge werden nicht unterstellt. Maschinenlesbare Ergebnisse: [loading-zoom-verification.json](loading-zoom-verification.json).

## Start und lokale Sicherung

Weiterhin `Start-CP08-r1.cmd` verwenden. Die Anpassung ist bereits in `runtime-local/CP08-r1` installiert. `artifacts-local/CP08-r1-LoadingZoom-Screenshots.zip` enthaelt alle 20 Full-HD-Aufnahmen und eine Uebersicht. `artifacts-local/CP08-r1-loading-zoom-r1-update.zip` enthaelt die geaenderte EXE, beide neuen Pakete und das Manifest. Diese Grafikdateien bleiben lokal und werden nicht nach GitHub hochgeladen.

Rueckrollkopie: `generated-local/widescreen/backups/loading-zoom-r1`. Sie enthaelt vorherige EXE und Manifest sowie die Liste der beiden vorher nicht vorhandenen Pakete. Ein Rueckbau stellt diese Kopien wieder her und entfernt ausschliesslich diese beiden neu hinzugekommenen Pakete. Das vorhandene Gemini-Teilpaket bleibt erhalten.
