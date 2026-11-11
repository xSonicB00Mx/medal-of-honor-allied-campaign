# CP09 lokal starten und zurueckkehren

Der Arbeitsstand bleibt privat und enthaelt lokal lizenzpflichtige Spiel-,
WCR- und Max-Payne-Ressourcen. Runtime-/Assetpakete nicht auf GitHub hochladen.
Git enthaelt nur eigene Quellen, Werkzeuge, Metadaten und Dokumentation.

## Bestehender Spielstand

`Start-CP09-r1.cmd` im Workspace ruft `tools/start_cp09.cmd` auf. Er startet
`runtime-local/CP09-r1` mit dem **bestehenden** Profil
`profiles-local/CP08-r1/user`. Der Profilname wird aus Kompatibilitaetsgruenden
beibehalten. Kein Kopieren, Reset oder Zuruecksetzen des Kampagnenfortschritts.

Der bisherige `Start-CP08-r1.cmd` bleibt als Rueckkehrweg erhalten. CP09-r1
verwendet dieselben Engine-/game-/cgame-Dateien und dasselbe Saveformat.
Beide Starter lesen dasselbe Profil; nicht gleichzeitig starten.

## Eigenstaendige lokale Kopie

Die internen Starter im neuen Runtime-Ordner haben keine CP05-/Workspace-
Abhaengigkeit mehr. `Start-Allied-Campaign.cmd` startet dort absichtlich ein
separates Profil `user/`. Diese internen Starter **nicht** fuer das Fortsetzen
des bisherigen persoenlichen Profils verwenden.

Einrichtung vom verifizierten, bereits zusammengefuehrten Bestand:

```text
python tools/cp09_candidate.py install runtime-local/CP09-r1
python tools/cp09_candidate.py verify runtime-local/CP09-r1
```

Bei unterbrochener Kopie liegt nur `CP09-r1.staging` vor; keine aktivierte
Installation. Nach Ursachepruefung denselben Installationsaufruf mit
`--resume` wiederholen. Bei geaenderten Eingaben stoppt das Werkzeug.
Nicht durch manuelles Anlegen von COMPLETE umgehen.

Rueckbau nur des ausgewaehlten Kandidaten:

```text
python tools/cp09_candidate.py uninstall runtime-local/CP09-r1
```

Er entfernt nach Integritaetspruefung bekannte Moddateien. Die 9.000
Basisdateien und unbekannte Nutzer-/Profildateien bleiben stehen. Der
Originalbestand sowie das persoenliche CP08-Profil sind nicht Ziel des
Rueckbaus. Bei veraenderten Moddateien wird vor dem Loeschen abgebrochen.

## Quellen und Grenzen

OpenMoHAA-Lizenz liegt als `OpenMoHAA-COPYING.txt` in der Runtime; die
Original-EULA und Kartencredits sind ebenfalls enthalten. Urspruenge der
lokalen Assets stehen in `third_party/`, `mod/campaign/GEOGRAPHY.md` und
den CP08-Artwork-/HUD-Berichten. Nutzerbilder, Gemini-/Bildgenerator-Ergebnisse
und daraus paketierte Spielgrafik bleiben lokale Daten.

Referenz: Windows x64, OpenMoHAA-GL1, vorhandene AA/SH/BT-WCR-Basis mit dem
im CP09-Bericht bezeichneten Fingerprint. Kein automatisches Update oder
Download. Beliebige andere WCR-/Spielversionen und ein Erstimport aus dem
nicht mehr verfuegbaren BT-Transport-ZIP sind nicht als getestet freigegeben.
Der Spielstart braucht diese historischen Eingabeorte nicht.
