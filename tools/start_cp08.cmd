@echo off
setlocal
for %%I in ("%~dp0..") do set "REPO=%%~fI"
set "RUNTIME=%REPO%\runtime-local\CP08-r1"
set "PROFILE=%REPO%\profiles-local\CP08-r1\user"
if not exist "%RUNTIME%\COMPLETE" exit /b 3
start "" /D "%RUNTIME%" "%RUNTIME%\openmohaa.exe" +set com_target_game 0 +set fs_basepath "%RUNTIME%" +set fs_homepath "%PROFILE%" +set fs_steampath "%RUNTIME%" +set fs_gogpath "%RUNTIME%" +set fs_microsoftstorepath "%RUNTIME%" +set net_enabled 0 +set ac_campaign_mode 1 +set cl_playintro 0 +set logfile 2 +set developer 0 +set ui_console 0 %*
