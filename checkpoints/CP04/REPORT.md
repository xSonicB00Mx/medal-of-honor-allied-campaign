# CP04-r1 – animierte Eintrittswunden

Technischer Kandidat auf CP03-r1, autonom gemäß Chatfreigabe umgesetzt. Keine persönliche Nutzerabnahme, kein Merge und keine behauptete vollständige Sichtabnahme. Austrittswunden werden in diesem Stand noch nicht gezeichnet.

Die beiden unveränderten Nutzer-PNGs werden lokal mit ihren Originalabmessungen und Alpha als TGA importiert. Hashes und Konvertierung: import.json. Keine Texturen in Git. Pistole/MP verwenden das kleine Profil (Radius 1,8), Gewehr/MG das gemeinsame große Profil (3,5). Exakte IDs bleiben in der gemeinsamen versionierten Waffenpolicy.

Bestätigte Treffer verwenden die bereits verfeinerte, tatsächlich deformierte Serveroberfläche. Ein zusammenhängender Ausschnitt ihrer Dreiecke wird am Trefferpunkt geclippt und über baryzentrische Koordinaten gebunden. Jede Ecke folgt im Renderer den vollständigen Bone-Gewichten und der aktuellen interpolierten Animation; kein an einem Bone befestigtes Rechteck. Verdeckte Surfaces werden ausgelassen. Beleuchtung, Alpha und die gemeinsame große Materialdefinition bleiben erhalten. Die WCR-Modelle und Animationen werden nicht ersetzt.

Ein separater deterministischer Zufallsstrom wählt pro Wunde Rotation und zwei unabhängige Spiegelwerte. Die produktiven Transformationsfunktionen bestehen einen isolierten C++-Test mit 65.536 Seeds, allen vier Spiegelkombinationen und fünf repräsentativen Winkeln. Wundgeometrie, Materialgruppe, Instanzkennung, Modellvariante, Seed und Transformation werden ohne Rohzeiger in einem versionierten Cgame-Anhang gespeichert. Originale Saves ohne diesen Anhang bleiben lesbar. Neue Wundsaves benötigen diesen oder einen späteren kompatiblen Build. Beim Laden wird die Modellvariante geprüft und die Instanzkennung einmalig neu gebunden. Der Snapshot-Neustart verwendet nun das tatsächliche Servercount-Flag; vorgelagerte Snapshots löschen die noch zu ladenden Wunden nicht mehr. Geladene Cgame-Daten werden genau einmal konsumiert.

Budgets: 64 Wunden in der Szene, 16 je Actor, 32 geclippte Dreiecke je Wunde, 512 Dreiecke je Actor und acht gezeichnete verwundete Actors pro Frame. FIFO verdrängt ältere Wunden. Ein zu komplexer Ausschnitt wird vollständig ausgelassen, nicht abgeschnitten. Bis 384 Einheiten volle Deckkraft, bis 512 Ausblendung. Nur diese nahen, begrenzten Actors verwenden das volle Skelettmesh, damit die gespeicherten Dreiecke nicht durch einen LOD-Kollaps ersetzt werden. Außerhalb davon greift normales LOD. Das ist eine bewusste Distanz-/Budgetregel, keine implementierte Übertragung auf kollabierte LOD-Dreiecke.

## Nachweise

- AA-v1–v4 sind Fehlersuche (Modellvariantenkennung und Save-Restart), keine Erfolgsnachweise. AA-v5 zeigt sichtbare kleine Wunden, sauberes Ausblenden und identische Wunden nach Laden.
- AA-groups: alle vier Waffenklassen. SH-motion: alle Klassen, Drehen und echte walk_bored_forward-Animation. BT-regions: Arm, Schulter, Bein und Rumpf bei 30 FPS, Bewegung und Entfernung/LOD. AA-death: Regionen bei 120 FPS, echter Tod und gespeicherte Wunden am Körper.
- AA-final: letzter Binärstand, 60 FPS, Bewegung, Todesanimation, Save/Load; drei Wunden, 52 Draw-Nachweise, drei restaurierte Wunden, keine Skriptfehler. Frühere umfangreichere Läufe haben eigene Binärhashes; sie werden nicht als identischer finaler Build ausgegeben.
- validate_wound_run.py vergleicht jede ausgegebene Rotation/Spiegelung und jeden Seed mit dem ursprünglichen Ereignis und prüft die Draw-Nachweise nach dem Laden. Sichtbilder bleiben in getrennten lokalen Testprofilen.
- Die englische Option **Body wounds** blendet vorhandene Wunden aus und verhindert neue Körperwunden. Weltblut und Nebel bleiben unabhängig. Originaldaten, WCR-Basis und MP1-Quelle werden beim Paketbau erneut per Hash geprüft.

## Grenzen

Nicht jede WCR-Modellvariante, Duckanimation, Beleuchtung und Mehrgegner-Lastszene ist vollständig geprüft. Zwei BT-Regionstreffer der groben Originalhitbox fanden keine sichtbare Oberfläche; dort wurde keine Wunde erfunden. Die vollständige CP3-Hindernismatrix und die dort berichtete Einschränkung bei bewegten Körpern bleiben bestehen. Der finale Nachtbuild ist ein spielbarer technischer Kandidat, keine vom Nutzer erteilte Abnahme.
