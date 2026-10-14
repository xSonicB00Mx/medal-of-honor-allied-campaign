@echo off
setlocal
for %%I in ("%~dp0..") do set "REPO=%%~fI"
set "RUNTIME=%REPO%\runtime-local\CP01-r2"
if "%AC_GAME%"=="AA" (set "GAME_NUMBER=0"& set "GAME_FOLDER=main") else if "%AC_GAME%"=="SH" (set "GAME_NUMBER=1"& set "GAME_FOLDER=mainta") else if "%AC_GAME%"=="BT" (set "GAME_NUMBER=2"& set "GAME_FOLDER=maintt") else (exit /b 2)
if not exist "%RUNTIME%\COMPLETE" (echo CP01-r2 ist nicht vollstaendig bereitgestellt.& pause& exit /b 3)
set "USER_ROOT=%REPO%\profiles-local\CP01-r2\user"
set "PROFILE=%USER_ROOT%\%AC_GAME%"
set "CONFIG=%PROFILE%\%GAME_FOLDER%\configs\omconfig.cfg"
set "SHARED=%USER_ROOT%\ac_ui_shared.cfg"
if not exist "%PROFILE%\%GAME_FOLDER%\configs" mkdir "%PROFILE%\%GAME_FOLDER%\configs"
if not exist "%CONFIG%" if exist "%REPO%\profiles-local\CP00-r4\%AC_GAME%\%GAME_FOLDER%\configs\omconfig.cfg" copy /Y "%REPO%\profiles-local\CP00-r4\%AC_GAME%\%GAME_FOLDER%\configs\omconfig.cfg" "%CONFIG%" >nul
if not exist "%SHARED%" (echo // Shared Allied Campaign UI preferences)>"%SHARED%"
copy /Y "%SHARED%" "%PROFILE%\%GAME_FOLDER%\ac_ui_shared.cfg" >nul
echo Allied Campaign CP01-r2 - %AC_GAME%
start "" /wait /D "%RUNTIME%" "%RUNTIME%\openmohaa.exe" +set com_target_game %GAME_NUMBER% +set fs_basepath "%RUNTIME%" +set fs_homepath "%PROFILE%" +set fs_steampath "%RUNTIME%" +set fs_gogpath "%RUNTIME%" +set fs_microsoftstorepath "%RUNTIME%" +set net_enabled 0 +set logfile 2 +exec ac_ui_shared.cfg %*
set "GAME_EXIT=%ERRORLEVEL%"
if exist "%CONFIG%" findstr /B /C:"seta ac_ui_auto " /C:"seta ac_menu_scale " /C:"seta ac_hud_scale " /C:"seta ac_hud_safe " "%CONFIG%" >"%SHARED%"
exit /b %GAME_EXIT%
