# AA-Medaillenansicht in 16:9

Die AA-Medaillenansicht und ihr Reset-Bestaetigungsdialog verwenden jetzt eine zentrierte 960x540-Flaeche. Der vorhandene rote Medaillenkasten wird verbreitert, Medaillen und Texttafeln behalten ihre Proportionen. Die Positionen der einzelnen Medaillen folgen den verbreiterten Faecherpositionen. Befehle, Freischaltbedingungen und Hover-Beschriftungen bleiben unveraendert; die Paketierung vergleicht diese Bindungen mit der Originalressource.

Das explizite `widecanvas`-Attribut teilt dieselbe proportionale Skalierung zwischen Zeichnung, Clipping und Mauskoordinaten. Es betrifft nur die beiden angepassten AA-Ressourcen. Auf 4:3 wird die gesamte breite Ansicht zentriert eingepasst.

Lokaler RelWithDebInfo-Build bestanden. Native Tests `medals-wide-r1` (1920x1080, Ansicht und Reset-Dialog) sowie `medals-43-r1` (1280x960) bestanden ohne Ressourcenfehler. Alle neun Medaillen wurden ausschliesslich in separaten Testprofilen eingeblendet. Der echte Nutzerfortschritt wurde nicht veraendert, kein Reset ausgefuehrt. Die 16:9-Aufnahmen wurden visuell geprueft.

Dies ist eine Layoutanpassung mit vorhandenen Assets, keine neue KI-Generierung. Screenshots und Originalressourcen bleiben lokal. Persoenliche Abnahme und Merge bleiben offen.
Installiert in CP08-r1 mit Engine 01dc7803. Installierter Nachtest medals-installed-r1 fuer beide Menues bestanden. 9072 Originaldateien, 9000 Runtime-Basisdateien, acht MP1-Dateien und alle 80 Nutzerdateien unveraendert; Rollback unter generated-local/widescreen/backups/aa-medals-wide-r1 vorhanden.
