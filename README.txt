
BitLocker Detection and Key Export Tool v1
Author: Garrett Harney
Date: June 2025

===============================================================================

Purpose:
This tool is designed for live forensic triage on a Windows machine to identify 
BitLocker-encrypted drives and locate any associated BitLocker recovery key 
files stored locally across all attached drives.

===============================================================================

Functionality:
- Detects all active drive letters (C: through Z:)
- Executes 'manage-bde' commands to capture encryption status
- Recursively scans all drives for .txt files containing "bitlocker"
- Copies matching recovery key files into an 'exported_keys' folder
- Logs all output to BITLOCKER_AUDIT_[COMPUTERNAME].txt
- Displays all actions in the CMD window

===============================================================================

Forensic Notes:
- Script does not alter any system files
- Keys are copied only, not modified
- Best practice is to run from clean external media

===============================================================================

Usage:
1. Place this script on a forensic USB
2. Run as Administrator
3. Review report and collected files

===============================================================================

Tested On:
- Windows 10/11 (x64)

===============================================================================

Output:
- BITLOCKER_AUDIT_[ComputerName].txt
- exported_keys folder
