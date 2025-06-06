CyberTip Extractor - MD5, IP, Chat Service, and Usernames

This application is designed to extract MD5 hashes, IP addresses with timestamps, chat services (like Kik, Discord), and usernames from NCMEC CyberTip PDFs, CSVs, or ZIPs containing those files.

------------
How to Install:
------------

1. Install Python (https://www.python.org/downloads/) if not already installed.
   - During installation, ensure you check "Add Python to PATH".

2. Open Command Prompt and install dependencies:

   pip install pymupdf pandas tkinterdnd2

3. Double-click or run the Python script:

   python cybertip_extractor.py

------------
How to Use:
------------

- Drag and drop PDF, CSV, or ZIP files (from CyberTips) into the app window.
- The app will auto-extract the data from Sections A–C (ignores Section D).
- All unique data will appear live in the app under:
  - MD5 Hashes
  - IPs with Timestamps
  - Chat Services
  - Usernames

- Click "Export to TXT Files" to generate clean export files.

------------
Notes:
------------
- ZIP support is automatic — the app will extract and scan PDFs and CSVs inside.
- All temporary files are automatically deleted after processing.
