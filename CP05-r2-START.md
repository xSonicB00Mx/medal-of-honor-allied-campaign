# CP05-r2 – Korrektur deines Feedbacks

Bitte diese neuen Startdateien verwenden:

- [Allied Assault](Start-CP05-r2-AA.cmd)
- [Spearhead](Start-CP05-r2-SH.cmd)
- [Breakthrough](Start-CP05-r2-BT.cmd)

**Blutpartikel und Umgebungsflecken:** Die fliegenden Partikel verwenden jetzt die originalen MP1-Partikelbilder mit ihrer eigenen Alpha-Maske. Tropfen und Flecken sind sichtbar größer. Der Startpunkt folgt der tatsächlich gezeichneten Körperpose, damit Trefferanimationen den Emitter nicht schon beim Entstehen einschließen. Nahe Wände bekommen bei einem freien, gültigen Austritt ebenfalls Flecken. Die Flecken verblassen weiterhin nach zehn Sekunden.

**Körperwunden:** Sie verwenden jetzt die Charakterbeleuchtung des getroffenen Gegners. Im Schatten werden sie entsprechend dunkler; die bereitgestellten Originaltexturen wurden nicht umgefärbt.

**Briefings:** AA-Bildtafeln und Vollbildvideos stehen proportional und mittig im Bild. Die Briefingfläche bleibt unabhängig von HUD-Größe und HUD-Rand. Neue Optionen bleiben auf Englisch.

Deine r1-Einstellungen und Spielstände wurden unverändert in das getrennte r2-Profil kopiert. Im Spiel unter **Options → HUD / Font Size** ist **Blood drops and stains** der Schalter für Partikel und Umgebungsflecken; **Body wounds** steuert die Körperwunden.

Für deinen Vergleich:

1. Ein AA-Briefing bei deiner Widescreen-Auflösung öffnen: beide Seitenränder sollen gleich breit sein.
2. Einen lebenden Gegner treffen und direkt auf die fallenden Tropfen sowie den Boden achten.
3. Einen Gegner nahe vor einer Wand treffen; Spritzer entstehen nur bei einem freien Austritt zur Wand.
4. Körperwunden in einer dunklen Umgebung vergleichen und einen Spielstand laden.

Rückweg: Die bisherigen **Start-CP05-r1-…cmd** bleiben unverändert vorhanden. r1 und r2 besitzen getrennte Profile. Neue Treffer auf bereits tote Körper bleiben außerhalb CP5.

Technische Nachweise und verbleibende allgemeine Grenzen: [CP05-r2-Bericht](checkpoints/CP05/r2/REPORT.md). Keine persönliche Abnahme und kein Merge unterstellt.
