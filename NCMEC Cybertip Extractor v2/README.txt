# CyberTip Extractor

CyberTip Extractor is a Python application that helps you extract and organize information from NCMEC CyberTip PDF and ZIP files. It features a simple, user-friendly interface—no technical knowledge required!

## What Does It Do?
- Extracts emails, phone numbers, IP addresses, and more from CyberTip reports
- Supports both PDF and ZIP files
- Easy drag-and-drop interface
- Dark mode option for comfortable viewing
- Keeps a log file for troubleshooting

## How to Use CyberTip Extractor (Python Version)

### 1. Getting Started
1. **Install Python**
   - Download and install Python from https://www.python.org/downloads/
   - During installation, check the box that says "Add Python to PATH".

2. **Install Required Libraries Automatically**
   - Double-click the `install_requirements.bat` file in this folder.
   - This will automatically install all the required Python libraries for you.
   - If you prefer, you can also open Command Prompt in this folder and run:
     ```
     pip install -r requirements.txt
     ```

3. **Run the Application**
   - In the same folder, double-click `cybertip_extractor.py` (if Python files are associated with Python on your system),
     or open Command Prompt and run:
     ```
     python cybertip_extractor.py
     ```

### 2. Using the App
- Drag and drop your CyberTip PDF or ZIP files into the window, or use the file selection button.
- The app will automatically extract and display the important information.
- Use the menu for help, instructions, or to switch to dark mode.

### 3. Where to Find Results
- Extracted data appears in the app window.
- A log file named `cybertip_parser.log` is saved in the same folder as the app for troubleshooting.

## Troubleshooting
- If the app does not start, make sure Python is installed and added to PATH.
- If you see an error message, check that all required libraries are installed (run `install_requirements.bat` again if needed).
- For technical issues, check the `cybertip_parser.log` file for details.

## About
CyberTip Extractor was created to make it easy for anyone to extract and organize data from NCMEC CyberTip reports. Please use responsibly and securely.

## Contact
For questions, support, or feedback, please contact me on GitHub:
- GitHub: https://github.com/DarkKnightForensics
