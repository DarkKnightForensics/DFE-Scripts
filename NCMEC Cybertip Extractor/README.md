# CyberTip Extractor

**Version 2.0**  
Developed by [DarkKnightForensics](https://github.com/DarkKnightForensics)

## Overview
CyberTip Extractor is a forensic tool for extracting key data from NCMEC CyberTipline PDF and ZIP reports. It features a user-friendly GUI, dark mode, progress bar, and robust logging for forensic traceability.

## Features
- Drag & drop or select PDF/ZIP files for analysis
- Extracts hashes, IPs, emails, phone numbers, usernames, and platform info
- Displays MD5 hash for each loaded file
- Progress bar for batch processing
- Dark mode toggle
- Export extracted data and logs
- Detailed logging for forensic purposes

## Installation
1. Clone or download this repository.
2. Install required Python packages:
   ```bash
   pip install pymupdf tkinterdnd2
   ```
   (You may also need `tkinter` and `ttk` which are included with most Python installations.)

## Usage
1. Run the application:
   ```bash
   python cybertip_extractor.py
   ```
2. Drag and drop or select PDF/ZIP files to process.
3. View extracted data and MD5 hashes in the GUI.
4. Use the menu for dark mode, help, and exporting data/logs.

## Credits
Developed by [DarkKnightForensics](https://github.com/DarkKnightForensics)

## License
MIT License

Copyright (c) 2025 DarkKnightForensics

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
