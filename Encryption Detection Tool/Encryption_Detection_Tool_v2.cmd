@echo off
rem BitLocker, VeraCrypt, and TrueCrypt Detection and Key Export Tool (Forensic-Ready Minimal Version, Improved, with Detailed Logging)

:: Enable delayed expansion
setlocal enabledelayedexpansion

:: Define output paths
set "output=%~dp0BITLOCKER_AUDIT_%computername%.txt"
set "exportDir=%~dp0exported_keys"
set "logfile=%~dp0LOG.txt"

:: Start log
(echo [START] %date% %time% - Script started. > "%logfile%"
 echo [INFO] Host: %computername% User: %username% Domain: %UserDomain% >> "%logfile%"
 echo [INFO] Output: %output% >> "%logfile%"
 echo [INFO] ExportDir: %exportDir% >> "%logfile%"
)

:: Start header
echo ======== BITLOCKER/VERACRYPT/TRUECRYPT TRIAGE REPORT ======== > "%output%"
echo ======== BITLOCKER/VERACRYPT/TRUECRYPT TRIAGE REPORT ========

:: Timestamp (batch-native)
echo %date% %time% >> "%output%"
echo %date% %time%
echo [INFO] Timestamp recorded: %date% %time% >> "%logfile%"

:: Host Information
echo Hostname: %computername% >> "%output%"
echo Hostname: %computername%
echo Username: %username% >> "%output%"
echo Username: %username%
echo Domain: %UserDomain% >> "%output%"
echo Domain: %UserDomain%
echo [INFO] Host info recorded. >> "%logfile%"

:: Timezone
for /f "tokens=*" %%z in ('tzutil /g') do (
    echo Time Zone: %%z >> "%output%"
    echo Time Zone: %%z
    echo [INFO] Time Zone: %%z >> "%logfile%"
)

:: Scan each drive for BitLocker
set "drives=C D E F G H I J K L M N O P Q R S T U V W X Y Z"
echo [STEP] Scanning drives for BitLocker status... >> "%logfile%"
for %%d in (%drives%) do (
    if exist %%d:\ (
        set "drv=%%d:"
        echo ======== DRIVE !drv! BITLOCKER STATUS ======== >> "%output%"
        echo ======== DRIVE !drv! BITLOCKER STATUS ========
        echo Volume !drv! >> "%output%"
        echo Volume !drv!
        echo [INFO] Scanning !drv! for BitLocker. >> "%logfile%"
        for /f "tokens=*" %%x in ('manage-bde -protectors -get !drv! 2^>nul') do (
            echo %%x >> "%output%"
            echo %%x
            echo [DETAIL] !drv! manage-bde -protectors: %%x >> "%logfile%"
        )
        for /f "tokens=*" %%x in ('manage-bde -status !drv! 2^>nul') do (
            echo %%x >> "%output%"
            echo %%x
            echo [DETAIL] !drv! manage-bde -status: %%x >> "%logfile%"
        )
    ) else (
        echo [WARN] Drive %%d: not present. >> "%logfile%"
    )
)
echo [STEP] BitLocker scan complete. >> "%logfile%"

:: Create export directory if needed
if not exist "%exportDir%" mkdir "%exportDir%"
echo [INFO] Export directory checked/created. >> "%logfile%"

:: Search all drives for BitLocker recovery keys
set "pattern=BitLocker*Recovery*Key*.txt"
echo ======== SEARCHING FOR BITLOCKER RECOVERY KEYS ======== >> "%output%"
echo ======== SEARCHING FOR BITLOCKER RECOVERY KEYS ========
echo (Lists BitLocker key filenames only) >> "%output%"
echo (Lists BitLocker key filenames only)
echo [STEP] Searching for BitLocker recovery keys... >> "%logfile%"
for %%d in (%drives%) do (
    if exist %%d:\ (
        set "foundKey=0"
        echo Searching drive %%d: for BitLocker recovery keys...
        echo [INFO] Searching drive %%d: for BitLocker keys. >> "%logfile%"
        for /f "delims=" %%f in ('dir /s /b %%d:\!pattern! 2^>nul') do (
            echo Found BitLocker key: %%f >> "%output%"
            echo Found BitLocker key: %%f
            echo [SUCCESS] Found BitLocker key: %%f >> "%logfile%"
            copy "%%f" "%exportDir%" >nul 2>&1
            if errorlevel 1 (
                echo [ERROR] Failed to copy BitLocker key: %%f >> "%logfile%"
            ) else (
                echo [INFO] Copied BitLocker key: %%f >> "%logfile%"
            )
            set "foundKey=1"
        )
        if !foundKey! == 0 echo [INFO] No BitLocker keys found on %%d: >> "%logfile%"
    )
)
echo [STEP] BitLocker key search complete. >> "%logfile%"

:: Search all drives for VeraCrypt/TrueCrypt containers and configs
echo ======== SEARCHING FOR VERACRYPT/TRUECRYPT CONTAINERS ======== >> "%output%"
echo ======== SEARCHING FOR VERACRYPT/TRUECRYPT CONTAINERS ========
echo (Lists .hc, .tc, and veracrypt.xml files) >> "%output%"
echo (Lists .hc, .tc, and veracrypt.xml files)
echo [STEP] Searching for VeraCrypt/TrueCrypt containers/configs... >> "%logfile%"
for %%d in (%drives%) do (
    if exist %%d:\ (
        set "foundVC=0"
        echo Searching drive %%d: for VeraCrypt/TrueCrypt containers...
        echo [INFO] Searching drive %%d: for VeraCrypt/TrueCrypt. >> "%logfile%"
        for /f "delims=" %%f in ('dir /s /b %%d:\*.hc 2^>nul') do (
            echo Found VeraCrypt container: %%f >> "%output%"
            echo Found VeraCrypt container: %%f
            echo [SUCCESS] Found VeraCrypt container: %%f >> "%logfile%"
            copy "%%f" "%exportDir%" >nul 2>&1
            if errorlevel 1 (
                echo [ERROR] Failed to copy VeraCrypt container: %%f >> "%logfile%"
            ) else (
                echo [INFO] Copied VeraCrypt container: %%f >> "%logfile%"
            )
            set "foundVC=1"
        )
        for /f "delims=" %%f in ('dir /s /b %%d:\*.tc 2^>nul') do (
            echo Found TrueCrypt container: %%f >> "%output%"
            echo Found TrueCrypt container: %%f
            echo [SUCCESS] Found TrueCrypt container: %%f >> "%logfile%"
            copy "%%f" "%exportDir%" >nul 2>&1
            if errorlevel 1 (
                echo [ERROR] Failed to copy TrueCrypt container: %%f >> "%logfile%"
            ) else (
                echo [INFO] Copied TrueCrypt container: %%f >> "%logfile%"
            )
            set "foundVC=1"
        )
        for /f "delims=" %%f in ('dir /s /b %%d:\veracrypt.xml 2^>nul') do (
            echo Found VeraCrypt config: %%f >> "%output%"
            echo Found VeraCrypt config: %%f
            echo [SUCCESS] Found VeraCrypt config: %%f >> "%logfile%"
            copy "%%f" "%exportDir%" >nul 2>&1
            if errorlevel 1 (
                echo [ERROR] Failed to copy VeraCrypt config: %%f >> "%logfile%"
            ) else (
                echo [INFO] Copied VeraCrypt config: %%f >> "%logfile%"
            )
            set "foundVC=1"
        )
        if !foundVC! == 0 echo [INFO] No VeraCrypt/TrueCrypt containers found on %%d: >> "%logfile%"
    )
)
echo [STEP] VeraCrypt/TrueCrypt search complete. >> "%logfile%"

:: Timestamp end
echo End Time: >> "%output%"
echo %date% %time% >> "%output%"
echo %date% %time%
echo [END] %date% %time% - Script finished. >> "%logfile%"

:: Notify user
echo.
echo Triage complete. Output saved to: "%output%"
echo Triage complete. Output saved to: "%output%"
echo Log file saved to: "%logfile%"
pause