echo off
set LOCALHOST=%COMPUTERNAME%
set KILL_CMD="C:\PROGRA~1\ANSYSI~1\ANSYSS~1\v242\fluent/ntbin/win64/winkill.exe"

start "tell.exe" /B "C:\PROGRA~1\ANSYSI~1\ANSYSS~1\v242\fluent\ntbin\win64\tell.exe" ClouDsBlade14 52663 CLEANUP_EXITING
timeout /t 1
"C:\PROGRA~1\ANSYSI~1\ANSYSS~1\v242\fluent\ntbin\win64\kill.exe" tell.exe
if /i "%LOCALHOST%"=="ClouDsBlade14" (%KILL_CMD% 111868) 
if /i "%LOCALHOST%"=="ClouDsBlade14" (%KILL_CMD% 12284) 
if /i "%LOCALHOST%"=="ClouDsBlade14" (%KILL_CMD% 16784) 
if /i "%LOCALHOST%"=="ClouDsBlade14" (%KILL_CMD% 112024) 
if /i "%LOCALHOST%"=="ClouDsBlade14" (%KILL_CMD% 91652) 
if /i "%LOCALHOST%"=="ClouDsBlade14" (%KILL_CMD% 102204)
del "C:\Users\cvest\Claudio\Oxford\3rd Year\B3\CubeSat_project\Claudio\Aerothermal\CFD\2d Sim\cleanup-fluent-ClouDsBlade14-91652.bat"
