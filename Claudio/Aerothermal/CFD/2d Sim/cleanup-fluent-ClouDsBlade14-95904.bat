echo off
set LOCALHOST=%COMPUTERNAME%
set KILL_CMD="C:\PROGRA~1\ANSYSI~1\ANSYSS~1\v242\fluent/ntbin/win64/winkill.exe"

start "tell.exe" /B "C:\PROGRA~1\ANSYSI~1\ANSYSS~1\v242\fluent\ntbin\win64\tell.exe" ClouDsBlade14 59908 CLEANUP_EXITING
timeout /t 1
"C:\PROGRA~1\ANSYSI~1\ANSYSS~1\v242\fluent\ntbin\win64\kill.exe" tell.exe
if /i "%LOCALHOST%"=="ClouDsBlade14" (%KILL_CMD% 99540) 
if /i "%LOCALHOST%"=="ClouDsBlade14" (%KILL_CMD% 79456) 
if /i "%LOCALHOST%"=="ClouDsBlade14" (%KILL_CMD% 86972) 
if /i "%LOCALHOST%"=="ClouDsBlade14" (%KILL_CMD% 99332) 
if /i "%LOCALHOST%"=="ClouDsBlade14" (%KILL_CMD% 95904) 
if /i "%LOCALHOST%"=="ClouDsBlade14" (%KILL_CMD% 96540)
del "C:\Users\cvest\Claudio\Oxford\3rd Year\B3\CubeSat_project\Claudio\Aerothermal\CFD\2d Sim\cleanup-fluent-ClouDsBlade14-95904.bat"
