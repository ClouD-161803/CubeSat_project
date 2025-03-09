echo off
set LOCALHOST=%COMPUTERNAME%
set KILL_CMD="C:\PROGRA~1\ANSYSI~1\ANSYSS~1\v242\fluent/ntbin/win64/winkill.exe"

start "tell.exe" /B "C:\PROGRA~1\ANSYSI~1\ANSYSS~1\v242\fluent\ntbin\win64\tell.exe" ClouDsBlade14 62138 CLEANUP_EXITING
timeout /t 1
"C:\PROGRA~1\ANSYSI~1\ANSYSS~1\v242\fluent\ntbin\win64\kill.exe" tell.exe
if /i "%LOCALHOST%"=="ClouDsBlade14" (%KILL_CMD% 17212) 
if /i "%LOCALHOST%"=="ClouDsBlade14" (%KILL_CMD% 34328) 
if /i "%LOCALHOST%"=="ClouDsBlade14" (%KILL_CMD% 40776) 
if /i "%LOCALHOST%"=="ClouDsBlade14" (%KILL_CMD% 24456) 
if /i "%LOCALHOST%"=="ClouDsBlade14" (%KILL_CMD% 10060) 
if /i "%LOCALHOST%"=="ClouDsBlade14" (%KILL_CMD% 17016)
del "C:\Users\cvest\Claudio\Oxford\3rd Year\B3\CubeSat_project\Claudio\Aerothermal\CFD\cleanup-fluent-ClouDsBlade14-10060.bat"
