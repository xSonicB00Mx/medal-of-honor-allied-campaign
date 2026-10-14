# CP00a-r1 – lokale BT-Integration

Der Auftrag vom 14.10.2026 erlaubt die autonome Fortsetzung bis CP1. Keine persönliche Spielabnahme und kein Merge behauptet. Die mitgelieferte PK3 wird ausschließlich lokal verarbeitet; ihre ursprünglichen zehn Skripte werden nicht auf GitHub veröffentlicht.

## Umsetzung

`tools/import_cp00a.py` verifiziert die Eingabe SHA-256 `d4122611afec4bb317eef1026f256cd0e1aa87fc85268218ceb19df71fb225fd`, vergleicht Patch gegen dessen ursprüngliche BT-Basis und überträgt ausschließlich die tatsächlich geänderten Munitions-/Dropregeln auf die vorhandenen WCR-Skripte. WCR-Waffen, Kampagnenvariablen, KI, Medaillen und vorhandene gleichwertige Änderungen bleiben erhalten. Zehn Eingaben ergeben sechs aktive zusammengeführte Ressourcen. Ausgabe: `zzzz_AC_BT_Drops.pk3`, SHA-256 `3638dca7306fe570278fe9ae4497acbe57bb398a7ffc8967d750fff36a699da8`. Genaue Regeln und Eingabehashes: `CP00a-r1-import.json`.

Ein Neustart der jeweiligen BT-Mission ist nötig. Bereits laufende Missionen in alten Saves erhalten keine rückwirkenden Drop-/Loadoutänderungen. AA und SH laden dieses Paket nicht. Die unabhängige CP00-r4-Referenz bleibt erhalten.

## Nachweise und Grenzen

- Wiederholter Import liefert identische Bytes; fehlende Eingabe verändert das vorhandene Produkt nicht (`import-verification.json`). Keine Netzwerkoperationen.
- e2l2 frisch gestartet: drei gültige Serien mit je neun realen Zielkills, Schwierigkeit Leicht/Mittel/Schwer, Save/Load nach Ziel 5. Je neun Waffendrops; Gesundheit 2/2/0 entsprechend der vorhandenen Schwierigkeitslogik. Kein zusätzlicher Drop, Treffer, Kill oder Zielabschluss durch anschließenden Leichenbeschuss.
- Normales Aufnehmen der gefallenen MP40: echte SMG-Reserve 0→64, nach Save/Load weiterhin 64. Gesundheit 730→750 interne Einheiten, nach Save/Load weiterhin 750. Das Objekt ist entfernt. Nachweis `pickup-BT-v3.json`; keine direkte Aufrufsimulation des Pickup-Callbacks.
- Die fünf e2l2-`prespawn`-Warnungen sind bereits in der unveränderten r4-Fußreferenz vorhanden und im Bericht gesondert ausgewiesen.
- `cp00a-middle-BT`, `pickup-BT-v1` und `pickup-BT-v2` sind verworfene/partielle Diagnoseaufbauten, keine vollständig bestandenen Tests. v1 verwendete eine nicht gesetzte Skriptvariable; v2 sammelte Gesundheit, verfehlte aber die danebenliegende Waffe. Korrektur in v3.
- Afrika e1l3 enthält zusätzliche Skriptwarnungen und ist trotz messbarer Drops nicht als bestanden gewertet. Italien e3l1 erreicht den kontrollierten Fuß-Aufbau nicht zuverlässig und ist ungültig. Keine vollständige Drei-Schauplatz- oder Kampagnenabnahme behauptet. BT-Finaltest bleibt ausdrücklich ausgelassen.

CP00a ist implementiert und für die CP1-HUD-Arbeit technisch nutzbar; die umfassende CP00a-Spielabnahme bleibt mit diesen Grenzen offen. Die HUD-Lieferung macht diese offenen Fälle nicht rückwirkend zu Erfolgen.
