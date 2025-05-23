echo off
set LOCALHOST=%COMPUTERNAME%
set KILL_CMD="C:\PROGRA~1\ANSYSI~1\ANSYSS~1\v242\fluent/ntbin/win64/winkill.exe"

start "tell.exe" /B "C:\PROGRA~1\ANSYSI~1\ANSYSS~1\v242\fluent\ntbin\win64\tell.exe" ClouDsBlade14 51817 CLEANUP_EXITING
timeout /t 1
"C:\PROGRA~1\ANSYSI~1\ANSYSS~1\v242\fluent\ntbin\win64\kill.exe" tell.exe
if /i "%LOCALHOST%"=="ClouDsBlade14" (%KILL_CMD% 3700) 
if /i "%LOCALHOST%"=="ClouDsBlade14" (%KILL_CMD% 7676) 
if /i "%LOCALHOST%"=="ClouDsBlade14" (%KILL_CMD% 34056) 
if /i "%LOCALHOST%"=="ClouDsBlade14" (%KILL_CMD% 4628) 
if /i "%LOCALHOST%"=="ClouDsBlade14" (%KILL_CMD% 9584) 
if /i "%LOCALHOST%"=="ClouDsBlade14" (%KILL_CMD% 6724)
del "C:\Users\cvest\Claudio\Oxford\3rd Year\B3\CubeSat_project\Claudio\Aerothermal\CFD\cleanup-fluent-ClouDsBlade14-9584.bat"
