@echo off
rem BitLocker Detection and Key Export Tool (Forensic-Ready Minimal Version)

:: Enable delayed expansion
setlocal enabledelayedexpansion

:: Define output paths
set "output=%~dp0BITLOCKER_AUDIT_%computername%.txt"
set "exportDir=%~dp0exported_keys"

:: Start header
echo ======== BITLOCKER TRIAGE REPORT ======== > "%output%"
echo ======== BITLOCKER TRIAGE REPORT ========

:: Timestamp
for /f %%t in ('powershell -Command "Get-Date -Format 'yyyy-MM-dd HH:mm:ss'"') do (
    echo %%t >> "%output%"
    echo %%t
)

:: Host Information
echo Hostname: %computername% >> "%output%"
echo Hostname: %computername%
echo Username: %username% >> "%output%"
echo Username: %username%
echo Domain: %UserDomain% >> "%output%"
echo Domain: %UserDomain%

:: Timezone
for /f "tokens=*" %%z in ('tzutil /g') do (
    echo Time Zone: %%z >> "%output%"
    echo Time Zone: %%z
)

:: Scan each drive for BitLocker
for %%d in (C D E F G H I J K L M N O P Q R S T U V W X Y Z) do (
    if exist %%d:\ (
        set "drv=%%d:"
        echo ======== DRIVE !drv! BITLOCKER STATUS ======== >> "%output%"
        echo ======== DRIVE !drv! BITLOCKER STATUS ========
        echo Volume !drv! >> "%output%"
        echo Volume !drv!
        for /f "tokens=*" %%x in ('manage-bde -protectors -get !drv! 2^>nul') do (
            echo %%x >> "%output%"
            echo %%x
        )
        for /f "tokens=*" %%x in ('manage-bde -status !drv! 2^>nul') do (
            echo %%x >> "%output%"
            echo %%x
        )
    )
)

:: Create export directory if needed
if not exist "%exportDir%" mkdir "%exportDir%"

:: Search all drives for recovery keys
echo ======== SEARCHING FOR RECOVERY KEYS ======== >> "%output%"
echo ======== SEARCHING FOR RECOVERY KEYS ========
echo (Lists filenames only) >> "%output%"
echo (Lists filenames only)

for %%d in (C D E F G H I J K L M N O P Q R S T U V W X Y Z) do (
    if exist %%d:\ (
        for /f "delims=" %%f in ('dir /s /b %%d:\ ^| findstr /i "recovery" ^| findstr /i ".txt" 2^>nul') do (
            echo Found: %%f >> "%output%"
            echo Found: %%f
            copy "%%f" "%exportDir%" >nul 2>&1
        )
    )
)

:: Timestamp end
echo End Time: >> "%output%"
for /f %%t in ('powershell -Command "Get-Date -Format 'yyyy-MM-dd HH:mm:ss'"') do (
    echo %%t >> "%output%"
    echo %%t
)

:: Notify user
echo.
echo BitLocker triage complete. Output saved to: "%output%"
echo BitLocker triage complete. Output saved to: "%output%"
pause