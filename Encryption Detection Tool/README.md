# BitLocker, VeraCrypt, and TrueCrypt Detection & Key Export Tool

## Overview
This Windows batch script is designed for digital forensics and incident response. It detects BitLocker, VeraCrypt, and TrueCrypt encryption on all drives of a Windows system, and exports any found recovery keys or container files to a folder on the same USB drive from which the script is run. It also generates a detailed log for error tracking and forensic documentation.

## Features
- Scans all drives (C: to Z:) for BitLocker encryption and logs status
- Searches for BitLocker recovery keys (`BitLocker*Recovery*Key*.txt`)
- Searches for VeraCrypt containers (`*.hc`), TrueCrypt containers (`*.tc`), and VeraCrypt config files (`veracrypt.xml`)
- Copies all found keys and containers to the `exported_keys` folder on the USB
- Logs all findings and errors to a detailed `LOG.txt` file
- No data is written to the suspect's computer
- Requires Administrator privileges

## Usage
1. **Copy the script to a USB drive.**
2. **Plug the USB drive into the target (suspect) Windows computer.**
3. **Open Command Prompt as Administrator:**
   - Press `Win + S`, type `cmd`, right-click on "Command Prompt", and select "Run as administrator".
4. **Navigate to the USB drive:**
   - Example: `E:` (replace `E:` with your USB drive letter)
5. **Run the script:**
   - Type the script name and press Enter (e.g., `BitLocker_Detection_Tool_v1.cmd`)
6. **Follow the on-screen instructions.**
7. **Wait for the script to finish.**
   - All findings and exported files will be saved to the USB drive.
   - The script will display a message when it is safe to remove the USB.

## Output
- `BITLOCKER_AUDIT_<COMPUTERNAME>.txt`: Main triage report
- `exported_keys/`: Folder containing all exported keys and containers
- `LOG.txt`: Detailed log of all actions, errors, and debug output

## Troubleshooting
- If the script window closes immediately, make sure you are running it as Administrator from Command Prompt.
- If you encounter errors, check the `LOG.txt` file for details.

## Disclaimer
- For forensic use only. Use responsibly and in accordance with all applicable laws and policies.

---
Created by: [DarkKnightForensics]
Date: June 2025
