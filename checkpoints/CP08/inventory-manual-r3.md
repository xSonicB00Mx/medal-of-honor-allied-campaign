# Tiger II manual r3

User correction: German text and closer fidelity to the original low-resolution sprite. Built-in Imagegen edit mode with transparent background, using source/item_tigerii_manual-1a406778.png as the authoritative reference.

Final prompt: Restore the original booklet's landscape proportions, clockwise tilt, aged beige cover, dark left illustration panel and small muted red title on the right. Interpret the indistinct illustration as a period Tiger II tank and crewman drawing. Text exactly "Tiger II" and "Anleitung"; no English text. Preserve the original composition and restrained palette, transparent background and visible edges. Do not use the previous full-width tank and oversized headline layout.

Selected master: generated-local/hud-upscale/items/generated/item_tigerii_manual.png. Built-in output: exec-9c19c736-6850-4231-be01-cbd5150ab0b7.png. Previous master retained in generated/revisions-r2. Packaged texture: generated-local/hud-upscale/items/prepared/item_tigerii_manual.png, 512x512 RGBA, uniformly registered to original bounds. No change to the other inventory artwork or gameplay.

Verification: candidate-aa-r3 passed in the native engine at 3840x2160, HUD 1.66. Screenshot 07 visually inspected. Exactly the manual texture changed in each campaign package; archive CRC and 512x512 full-range alpha checks passed. Installed inventory-r3 from f9c4b3dc; deployed hashes match tested packages. Integrity: 9072 original files, 9000 runtime-base files, eight MP1 inputs and all 80 user-profile files unchanged. Rollback in generated-local/widescreen/backups/inventory-r3.
