# CP05-r1 starten

Dieser Kandidat enthält HUD-/Schriftskalierung, roten Treffernebel, Blutpartikel/Weltflecken sowie animierte Eintritts- und Austrittswunden. Alle neuen Spieloptionen sind auf Englisch.

Im Workspace eine dieser Dateien starten:

- [Allied Assault](Start-CP05-r1-AA.cmd)
- [Spearhead](Start-CP05-r1-SH.cmd)
- [Breakthrough](Start-CP05-r1-BT.cmd)

Im Spiel **Options → HUD / Font Size** öffnen. **Automatic scaling**, **Menu and font size**, **HUD size** und **HUD safe area** steuern die Darstellung. **Red hit mist**, **Blood drops and stains** und **Body wounds** sind getrennte Schalter. **Defaults** setzt diese Einstellungen zurück.

Die Einstellungen bleiben nach Beenden und beim Wechsel zwischen diesen drei Startdateien erhalten. Die neuen Profile liegen unter `profiles-local/CP05-r1/user`. Sie beginnen mit FOV 90 und der bisherigen Fensterauflösung 1280×960; Auflösung/Vollbild lassen sich in den Grafikoptionen einstellen. Die HUD-Automatik passt sich daran an. Spielstände und Profile älterer Kandidaten bleiben an ihrem bisherigen Ort.

Originale Spielstände und CP4-Wundsaves sind in CP5 lesbar. Neue CP5-Wundsaves benötigen CP5 oder einen späteren kompatiblen Build. Historische Treffer erhalten beim Laden keine nachträglich erfundenen Austritte. Für die schon integrierten BT-Dropregeln gilt weiterhin die dokumentierte Missionsstart-Einschränkung aus CP0a.

Kleine Eintritte bei Pistolen/MPs, große Eintritte bei Gewehr/MG, große geometrisch bestätigte Austritte bei allen vier Gruppen. Körperwunden bleiben innerhalb der dokumentierten Budgets am Körper; Weltflecken verblassen nach zehn Sekunden. Bereits tote Körper neu zu beschießen ist der spätere CP5a-Umfang.

Technischer Spielkandidat; keine persönliche Nutzerabnahme und kein Merge. Prüfungen und verbleibende Grenzen: [CP5-Bericht](checkpoints/CP05/REPORT.md). Die Vorgänger und die Originalinstallation bleiben als Rückweg erhalten. Die lokale Sicherung liegt unter `artifacts-local/CP05-r1-runtime.zip`; sie enthält Originaldaten und wird nicht zu GitHub hochgeladen.
