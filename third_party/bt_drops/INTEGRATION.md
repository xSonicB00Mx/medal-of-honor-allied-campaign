# Lokale Integration

Aufruf im Repository: `python tools/import_cp00a.py --help`. Das Werkzeug verwendet ausschließlich die lokal bereitgestellte, per SHA-256 festgelegte PK3 und die dokumentierte WCR-Basis. Es lädt keine Ersatzfassung herunter. Die äußere Transport-ZIP lag nicht vor; Autor und genaue Versionsbezeichnung sind unbekannt.

Der semantische Merge und die Hashes sämtlicher zehn Skripte stehen in `checkpoints/CP00a/CP00a-r1-import.json`. Ausgaben und vollständige Fremdskript-Diffs bleiben unter `generated-local`. Nur die resultierende eigene lokale PK3 gehört in `maintt`; keine Installation in `main` oder `mainta`.

Rückbau: CP00-r4 bleibt eine unabhängige unveränderte Runtime. Zum gezielten Deaktivieren ausschließlich `maintt/zzzz_AC_BT_Drops.pk3` aus der eigenen CP00a/CP1-Runtime herausnehmen und die Mission neu beginnen. Alte Saves werden nicht automatisch konvertiert. Nicht die ursprüngliche Installation verändern.

Nachweise und noch offene Spieltests: `checkpoints/CP00a/CP00a-r1-REPORT.md`.
