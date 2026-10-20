# LOADOUT: Modellflaechen und Granateneffekte

## Bestaetigte Korrekturen

FG42, G43 und SVT zeigten offene bzw. fehlende Flaechen an Zielfernrohr,
Visierung und Gehaeuse. Die Nah-Clipping-Ebene und abgeschaltetes LOD behoben
den Fehler nicht. Eindeutige, zweiseitige Materialvarianten an diesen drei
Modellen schliessen die Luecken. Texturen, Alphatests, Spiegelung und saemtliche
Waffen-/Animationsparameter bleiben erhalten. Die Paketierung verwendet jeweils
die vorhandene Definition des Kampagnenkontexts und aendert nur Shadernamen.
Originalarchive und Modelle werden nicht bearbeitet; die lokalen Modpakete
enthalten die abgeleiteten Definitionen und bleiben ausserhalb von Git.

Der Ressourcenimport folgte bisher physischen `.spr`-Dateien. Viele Effekte
verwenden stattdessen einen Shader ohne Dateiendung. Der Import verfolgt nun
auch diese Materialien und ihre Texturen. Das beseitigt die fehlenden
Rauchgranaten-Sprites in AA und ergaenzt weitere importierte Effektmaterialien.

## Granatensounds: noch kein reproduzierter Ausfall

Alle neun Granaten wurden in isolierten AA-, SH- und BT-Profilen geworfen.
Die fuenf Sprenggranaten loesen jeweils `grenade_explode` aus; die vier
Rauchgranaten jeweils ihren Startsound. Die italienische Bomba hat im
vorhandenen AA/SH-Import eine 30-Sekunden-Zuendung und wird entsprechend lange
beobachtet. Die Breda-Granate verwendet bereits in der Inhaltsbasis Rauch;
sie wird nicht nachtraeglich in eine Sprenggranate umgewandelt.

`debugSound 2` protokolliert nun Alias, Datei, Lautstaerke und Entitaet direkt
vor der Sounduebergabe. Der abschliessende AA-Test bestaetigt zusaetzlich ueber
`s_show_sounds`, dass OpenAL alle neun erwarteten Effektsounds mit positiver
Lautstaerke uebernimmt. Der erste Testauswerter verglich Dateinamen faelschlich
mit Gross-/Kleinschreibung; OpenAL normalisiert diese. Der Auswerter wurde
korrigiert und derselbe native Lauf erneut ausgewertet.

Das ist ein technischer Ausgabenachweis, keine persoenliche Hoerabnahme.
Eine Ursache fuer den gemeldeten fehlenden Explosionssound ist noch nicht
bestaetigt. Die optional erfragten Granaten-/Missionsangaben stehen aus.
Es gibt deshalb keine behauptete Behebung dieses Tonausfalls und keine
pauschale Lautstaerke-, Zuendzeit- oder Gameplayaenderung.

## Lokale Pruefbelege

- `profiles-local/loadout/models-aa-fixed`: sechs Waffen, beide LOD-Einstellungen;
  FG42/G43/SVT nach der Korrektur visuell vollstaendig.
- `profiles-local/loadout/models-sh-fixed` und `models-bt-fixed`: derselbe
  Vergleich in SH/BT, zusaetzlich die drei korrigierten Modelle in der
  LOADOUT-Vorschau. Native Laeufe erfolgreich, Modelle visuell kontrolliert.
- `profiles-local/loadout/grenadefx-aa-baseline`: alle neun Granaten vor der
  Ressourcenreparatur; fehlende Rauchmaterialien reproduziert.
- `profiles-local/loadout/grenadefx-bt-baseline`: alle neun Granaten in BT.
- `profiles-local/loadout/grenadefx-sh-fixed`: alle neun Granaten in SH.
- `profiles-local/loadout/grenadefx-aa-fixed`: nach der Korrektur keine fehlenden
  Rauchmaterialien; alle erwarteten Sounds bis OpenAL nachgewiesen.

Saves und Fortschritt der Testprofile blieben erhalten. Vorhandene native
Warnungen sind in den Ergebnisdateien unverkuerzt dokumentiert, unter anderem
AA-Sandbag/Fence/Radar, BT-Prespawn/Mortar-Material und SH-smokegrenade_start.
Sie werden nicht pauschal als durch diesen Auftrag behoben bezeichnet.

Die Tests sind gezielte Szenarien, keine vollstaendigen Kampagnendurchlaeufe.
Client-Modul gebaut, Kampagnenvalidierung und Kataloggenerator erfolgreich;
Paketintegritaet und Shaderverweise in allen drei Paketen geprueft.
