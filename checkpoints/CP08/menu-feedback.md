# Menu feedback and effect screenshots

Removed the Natural Earth / GeoNames text field from the operations menu at the user's request. Attribution and geographic provenance remain in `mod/campaign/GEOGRAPHY.md`; a copy accompanies the local runtime update.

The updated engine builds successfully. Native Full-HD menu rendering and all fifteen operation selections passed (`menu-no-source-row.json`). No effect implementation changed.

Actual native AA screenshots from an isolated diagnostic profile, with a stationary high-health target and a real Kar98 shot (not a natural mission encounter):

- Blood Mist: `profiles-local/CP08-r1/effects-close/main/screenshots/shot0003.png` (red haze at impact; the pale cloud is weapon smoke).
- Blood Drops: `profiles-local/CP08-r1/effects-close/main/screenshots/shot0012.png` (falling red droplets).
- Stains: `profiles-local/CP08-r1/effects-close/main/screenshots/shot0018.png` (snow surface).
- Body Wounds: `profiles-local/CP08-r1/effects-close/main/screenshots/shot0017.png` (chest).

Images are unretouched native frames, converted losslessly from TGA to PNG. Native runs exited successfully, with confirmed hit/mark events and no detected script errors. The first `effects-mist` capture is retained as diagnostic evidence; `effects-close` is the selected presentation sequence. User profiles were not modified.

The original CP08-r1 runtime ZIP and its package report remain the pre-feedback snapshot. The local menu-feedback update ZIP records the replacement executable and updated runtime manifest separately. The existing Start-CP08-r1.cmd uses the updated runtime.
