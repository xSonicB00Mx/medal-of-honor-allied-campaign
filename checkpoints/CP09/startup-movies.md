# Original startup movies restored

The normal CP08 and CP09 launchers explicitly passed cl_playintro 0, inherited
from test launches. Both now pass 1. The root Start-CP08-r1.cmd and
Start-CP09-r1.cmd wrappers already call those scripts, so the fix is live.

The command-line override is reapplied after ac_preferences.cfg is read, so
existing profiles that contain cl_playintro 0 also play the intro at next start.
Internal ac_context launches still pass 0; no intro on campaign transitions.
No executable rebuild, runtime asset change, or personal profile edit required.

Native check: CP09 installed engine, isolated home directory, copied shared
preferences with the old zero value, developer 0, command-line cl_playintro 1.
The original startup sequence ran to completion without keyboard intervention
and reached Main Menu after approximately 184 seconds. Menu confirmed by
ac_ui_report and native screenshot. EAlogo, 2015intro and intro RoQ/MP3 files
are present; RoQ frame counts correspond to 3.03, 4.03 and 166.83 seconds.
Per-movie debug messages are absent at developer 0; an initial test assertion
expecting those messages was invalid. The end-to-end menu completion and elapsed
time were verified independently. No claim of pixel-by-pixel movie review.
Local evidence: generated-local/CP09/startup-movies and profiles-local/startup-movies.
