# Allied Campaign: Installerplanung

Stand: 26.10.2026. Nutzerauftrag: planen, **noch keinen Installer erstellen**.
Dieses Dokument legt den vorgesehenen Ablauf und die noch zu pruefenden
Voraussetzungen fest. Es bestaetigt keine Installation auf einer rohen Warchest.
Keine Downloads von Paketen, Paketgenerierung oder Laufzeitaenderungen in dieser Planungsrunde.

## Ziel

Ein Windows-x64-Setup erkennt eine unveraenderte, vollstaendige Installation von
Allied Assault, Spearhead und Breakthrough. Nach der Eingabe von Quell- und
Zielordner laedt es zuerst die freigegebene WCR-Fassung herunter, installiert
diese und anschliessend Allied Campaign samt passender Engine und Abhaengigkeiten.
Kein manuelles PK3-Kopieren, kein separat installiertes Python, Git oder Compiler.
Bedienoberflaeche und Fehlermeldungen im Setup auf Englisch.

## Vorgesehener Ablauf

1. **Detect Game:** bekannte Installationsorte suchen, manuelle Ordnerwahl anbieten.
   Nicht nur EXE-Namen, sondern Archive, erforderliche Ressourcen, Sprache und
   Versionsfingerprints aller drei Spiele pruefen. Unterstuetzte Varianten in
   einer expliziten Tabelle fuehren. Fehlende Erweiterungen, unbekannte Mischstaende
   oder Fremdmods verstaendlich melden. Alte CD-/Sprachfassungen nicht ungeprueft
   als kompatibel behandeln; erforderliche Originalpatches pro Variante definieren.
2. **Choose Location:** separaten Allied-Campaign-Zielordner vorschlagen, bevorzugt
   auf dem Laufwerk des Spiels. Originalinstallation bleibt die gelesene Quelle.
   Quelle und Ziel duerfen weder identisch noch ineinander verschachtelt sein.
   Freien Platz fuer Datenkopie, Downloads, Entpacken und Update-Rollback berechnen.
3. **Download WCR:** exakt freigegebene Vollversion und erforderlichen Patch von
   der Quelle des Autors beziehen. Versionsnummer, Dateigroesse und SHA-256 im
   Release-Manifest festschreiben. Kein Download eines beliebigen "latest".
   Transport und Weiterleitungen pruefen, nur erwartete Dateien akzeptieren.
   Unterbrochene Downloads fortsetzen und anschliessend vollstaendig verifizieren.
   Falls der Hoster einen Browser-Schritt verlangt: Original-Downloadseite und
   Auswahl eines lokal geladenen, identisch geprueften Archivs anbieten. Kein
   stiller Fremd-Mirror und keine Zusage eines unbeaufsichtigten Downloads, bevor
   der tatsaechliche Downloadpfad getestet wurde.
4. **Prepare Game:** nur benoetigte Originalspieldaten aus dem Besitz des Spielers
   in einen Arbeitsordner auf dem Ziellaufwerk kopieren. Keine Saves, persoenlichen
   Einstellungen, Originalstarter oder beliebigen fremden PK3s uebernehmen.
   Keine Hardlinks/Junctions zur Originalinstallation.
5. **Install WCR:** Archive in den Arbeitsordner entpacken, Pfade und Groessen
   begrenzen, absolute/uebergeordnete Pfade und Links ablehnen. Nur die getesteten
   Module und erforderlichen losen Dateien uebernehmen. Keine ungeprueften
   Installations-/Deinstallationsskripte aus Downloads ausfuehren. Ergebnis mit
   der freigegebenen WCR-Basis vergleichen.
6. **Install Allied Campaign:** zusammengehoerige EXE, game.dll, cgame.dll,
   benoetigte Laufzeitbibliotheken, UI/HUD/Karten/Effekte und Integrationspakete
   installieren. Kampagnenuebergreifende Waffenressourcen lokal aus den drei
   Originalspielen/WCR ableiten. Paketprioritaeten und gezielte Skriptaenderungen
   anhand bekannter Eingabehashes anwenden; bei Abweichungen abbrechen.
7. **Verify and Activate:** Gesamtmanifest pruefen und erst dann die fertige
   Installation aktivieren. Startmenue-/Desktopverknuepfung optional erstellen.
   Ein normaler Einstieg in Allied Campaign mit Startvideos; interne Kampagnenwechsel
   weiterhin ohne Startvideos. Erst nach erfolgreichem Abschluss Start anbieten.

## Verzeichnis- und Updatekonzept

- Spielinhalte, Downloadcache, Entpacken und Rollback standardmaessig auf dem
  gewaehlten Ziellaufwerk. Kleine systembedingte TEMP-Dateien nicht ausschliessen,
  aber keine gigabytegrossen versteckten Kopien auf C: erzeugen.
- Beschreibbares, separates Benutzerprofil mit stabiler Zuordnung zur Installation;
  bevorzugt ebenfalls auf dem Ziellaufwerk. Rechte pruefen, nicht auf Schreibrechte
  in Program Files vertrauen. Keine pauschale Administratorpflicht fuer das Spiel.
- Profile enthalten Saves, Fortschritt, Highscores, Loadouts und Einstellungen.
  Updates ersetzen diese nicht. Ein spaeterer Import des Entwicklungsprofils ist
  ein eigener, optionaler Kopiervorgang mit Backup und Kompatibilitaetspruefung.
- Unfertige Installation bekommt keine gueltige Startmarkierung. Bei Fehlern bleibt
  die vorhandene Version startbar; Arbeitsordner kann repariert/fortgesetzt werden.
- Updates fuehren ein Dateibesitz-Manifest. Nur eigene, unveraenderte Altdateien
  ersetzen/entfernen; fremde oder nachtraeglich modifizierte Dateien erhalten bzw.
  als Konflikt behandeln. Alte PK3s gezielt entfernen, damit keine Schattenkopien laden.
- Deinstallation entfernt eigene Programmdateien und Verknuepfungen. Profildaten
  standardmaessig behalten; deren Loeschung ist eine gesonderte bewusste Auswahl.
  Warchest-Quellinstallation und andere Mods bleiben erhalten.

## Paketierung: lokaler Kandidat ist kein Releasepaket

`tools/cp09_candidate.py` arbeitet mit der bereits importierten Entwicklungsbasis.
Seine Runtime enthaelt Originalspiel-/WCR-/Max-Payne-Daten und ist ausdruecklich
als lokal und nicht zum Upload vorgesehen. Ein AC-Dateiname belegt keine Herkunft.
Die bestehenden Paketierungswerkzeuge muessen fuer den Release aus expliziten,
versionsgebundenen Eingaben statt aus einem gewachsenen Runtime-Verzeichnis arbeiten.

| Kategorie | Geplanter Umgang |
| --- | --- |
| Eigene Engine/Game/Cgame-Aenderungen | Passende Release-Binaerdateien, Quellstand, Buildanleitung und Lizenztexte zusammen bereitstellen |
| Originale MOHAA/SH/BT-Assets | Lokal aus gepruefter Warchest ableiten; nicht mit dem Setup ausliefern |
| WCR | Externe, festgelegte Downloads; Autorenhinweise erhalten; Module/lose Dateien genau zuordnen |
| Geaenderte Original-/WCR-Skripte | Lokal aus bekannten Originalen und dokumentierten Aenderungsrezepten erzeugen; Verbreitbarkeit der Rezepte separat pruefen |
| Neue HUD-/Menuegrafiken und Nutzerbilder | Vollstaendige Herkunfts- und Freigabeliste je Datei, einschliesslich abgeleiteter Bilder |
| Max-Payne-Blutressourcen | Freigabe klaeren oder gleichwertige eigene Ressourcen einsetzen; rohe Warchest allein liefert diese nicht |
| Courier-New-Bold-Atlanten | Font-/Atlasverwendung pruefen; ggf. lokal aus vorhandenem Windows-Font erzeugen, mit klarer Fehlermeldung falls nicht vorhanden |
| BT-Dropintegration | Bisherige externe Patchbasis identifizieren und reproduzierbar einbinden; keinen zweiten Drop-Patch darueberinstallieren |

Eine zusaetzlich benoetigte Max-Payne-Installation waere mit dem gewuenschten
"nur rohe Warchest"-Ziel unvereinbar. Die Herkunftsfragen werden vor der
Veroeffentlichung geloest, nicht durch einen funktional unvollstaendigen Installer.
Keine Kontaktaufnahme mit Autoren oder Veroeffentlichung durch diesen Plan autorisiert.

## Noch offene Voraussetzungen

1. **WCR-Zuordnung:** `third_party/wcr/manifest.json` hat `version: null`, sieben
   aktive Module und Fingerprint
   `3b6b38b5b04ba320a526196946c44394c4519e4197dc8d3d05788e186501cfcc`.
   Die am 26.10.2026 gelesene Autorenseite bietet Vollversion 1.1 und Patch 1.1.1.
   Dass diese Archive exakt unsere Basis ergeben, ist noch nicht nachgewiesen.
   Spaeter Vollversion plus Patch vergleichen, inklusive loser Dateien und
   OpenMoHAA-spezifischer Optionen. Bei Abweichung bewusste Basisauswahl plus Regression.
2. **Saubere Ausgangsbasis:** einen wirklich unveraenderten Warchest-Testbestand
   beschaffen bzw. vom Nutzer vorhandene Originalinstallation verifizieren. Unsere
   aktuelle WCR-Installation ist dafuer kein Ersatz. Sprach-/Vertriebsvarianten
   erst nach Test als unterstuetzt deklarieren.
3. **Releaseinventar:** jede benoetigte Datei mit Herkunft, Eingabehash, Rezept,
   Auslieferungsart und Lizenzhinweis erfassen. Fehlende lokale Entwicklungsinputs
   und private Pfade aus Paketierungswerkzeugen beseitigen.
4. **Laufzeitabhaengigkeiten:** DLL-Abhaengigkeiten des finalen Builds auf einem
   sauberen Windows ohne Entwicklerwerkzeuge pruefen; erforderliche offizielle
   Redistributables oder zulassige lokale Bibliotheken versionsgebunden aufnehmen.
5. **Starter konsolidieren:** die persoenlichen CP08/CP09-Starter verwenden bereits
   `cl_playintro 1`; der historische Standalone-Generator in cp09_candidate.py
   noch 0. Der neue Release-Starter muss die aktuelle gewuenschte Einstellung 1
   und relative Pfade verwenden. In dieser Planungsrunde nichts daran geaendert.
6. **Freigabe:** natuerlichen Kampagnenabschluss, verbleibende CP09-Fehler und
   abschliessenden Release-Quellstand festlegen. Keine automatische Merge-/Releasefreigabe.

## Technischer Vorschlag und Bauphasen

Vorgeschlagen: Inno Setup als Windows-Assistent, mit einem kleinen mitgelieferten
Import-/Pruefhelfer fuer die spielabhaengigen Ressourcen. Konkrete Toolversion,
Archivbibliothek und Signierung erst beim Bau festlegen. Der Nutzer soll kein
Python oder andere Entwicklungswerkzeuge installieren muessen. Unser eigenes
auslieferbares Material vorzugsweise im Setup mitliefern; WCR extern herunterladen.
Die konkrete Paketgroesse ist erst nach dem Releaseinventar belastbar.

Spaetere Reihenfolge: (1) Quellen/Versionen klaeren, (2) reproduzierbares
Releaseinventar und lokalen Import bauen, (3) Setup darum bauen,
(4) Installation/Update/Rollback/Deinstallation auf sauberem System testen,
(5) Releasekandidat mit Quellcode, Pruefsummen und Changelog zur Abnahme.
Aktuell wird ausschliesslich dieser Plan erstellt.

## Abnahmetests fuer den spaeteren Installer

- Von frischer Warchest bis zum Hauptmenue ohne Entwicklungsordner, Internet nur
  fuer deklarierte Downloads. Externe Originalinstallation danach byteidentisch.
- AA, SH, BT starten; Missionswechsel, vereinheitlichte Saves, Fortschritt,
  Einstellungen, WCR-Skripte, HUD, FMVs, Blut und LOADOUT-Abhaengigkeiten pruefen.
- Im neuen Installationsbestand gleiche effektive Ressourcen und Paketprioritaeten
  wie im freigegebenen Kandidaten; keine Testprofile, Logs oder private Saves im Setup.
- Pfade mit Leerzeichen/Umlauten, Standardbenutzer, schreibgeschuetzte Quelle,
  fehlende Erweiterung, unbekannte Sprache/Version, fremde Mod, wenig freier Platz.
- Downloadabbruch, falscher Hash, defektes Archiv, Quelle nicht erreichbar,
  Installation abgebrochen, wiederholte Installation und besetzte Programmdateien.
- Update und Rollback erhalten Saves, Scores, Fortschritt und Einstellungen;
  Deinstallation laesst Originalspiel und standardmaessig Benutzerprofil erhalten.
- Speicherbedarf auf C: und Ziel messen; Cache/Arbeitsdateien nach Erfolg bereinigen.

## Quellen der Planung

- Lokal: README.md; checkpoints/CP09/REPORT.md; third_party/wcr/manifest.json;
  third_party/bt_drops/manifest.json; third_party/user_assets.json;
  third_party/mp1/manifest.json; tools/cp09_candidate.py; tools/package_loadout.py;
  tools/package_courier_fonts.py; tools/package_effects.py.
- [WCR Vollversion 1.1](https://www.moddb.com/mods/war-chest-restored/downloads/war-chest-restored-v11)
  und [Patch 1.1.1](https://www.moddb.com/downloads/war-chest-restored-patch-v111):
  Releasearten und notwendige Vollversion vor Patch; keine Archive heruntergeladen.
- [Inno Setup](https://jrsoftware.org/isinfo.php): Windows-Setup, Dateidownload/-pruefung,
  Archivextraktion und Deinstallation als geeignete Grundfunktionen.
