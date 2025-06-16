import os
import re
import fitz  # PyMuPDF
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinterdnd2 import TkinterDnD
from datetime import datetime
import zipfile
import tempfile
from collections import defaultdict
import logging
import platform
import socket
import time
import shutil
import hashlib
from tkinter import simpledialog

class CyberTipExtractorApp:
    # Pre-compile regex patterns for efficiency
    EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
    # Improved phone pattern: require word boundaries and avoid matching inside hashes or IDs
    PHONE_PATTERN = re.compile(r"(?<![\w\d])(?:\+1[-.\s]?)?(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})(?![\w\d])")
    HASH_PATTERN = re.compile(r"\b[a-fA-F0-9]{32}\b")
    IP_TIME_PATTERN = re.compile(r"IP Address[:\s]*([\d.]+).*?(\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2} UTC)", re.DOTALL)
    TABLE_IP_PATTERN = re.compile(r"IP Address\s+([\d.]+)\s+Upload\s+(\d{2}-\d{4} \d{2}:\d{2}:\d{2} UTC)")
    USERNAME_PATTERNS = [re.compile(fr"{key}\s*(\S+)") for key in ["Screen/User Name:", "Display Name:", "ESP User ID:"]]
    SUBMITTER_PATTERN = re.compile(r"Submitter:\s*(.*?)\n(.*?)(?:\n|$)", re.DOTALL)
    SECTION_PATTERN = re.compile(r"Section [A-D]:.*")

    def __init__(self, root):
        self.root = root
        self.root.title("CyberTip Extractor v2.0")
        self.root.geometry("750x850")
        self.data = defaultdict(set)
        self.loaded_files = set()
        self.dark_mode = False
        self.setup_logging()
        self.log_system_info()
        self._build_gui()
        self.logger.info("GUI started.")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_logging(self):
        log_path = os.path.join(os.getcwd(), "cybertip_parser.log")
        logging.basicConfig(
            filename=log_path,
            filemode='a',
            format='%(asctime)s [%(levelname)s]: %(message)s',
            level=logging.DEBUG
        )
        self.logger = logging.getLogger("CyberTipLogger")
        self.logger.info("Logging initialized.")

    def log_system_info(self):
        try:
            computer_name = socket.gethostname()
            user = os.environ.get('USERNAME') or os.environ.get('USER')
            sys_info = platform.platform()
            self.logger.info(f"System Info: Computer Name: {computer_name}, User: {user}, Platform: {sys_info}")
        except Exception as e:
            self.logger.warning(f"Failed to log system info: {e}")

    def on_close(self):
        self.logger.info("GUI closed.")
        self.root.destroy()

    def _build_gui(self):
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Menu bar with Help/About
        menubar = tk.Menu(self.root)
        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=self.show_about)
        helpmenu.add_command(label="Instructions", command=self.show_instructions)
        menubar.add_cascade(label="Help", menu=helpmenu)
        # Dark mode toggle
        viewmenu = tk.Menu(menubar, tearoff=0)
        viewmenu.add_command(label="Toggle Dark Mode", command=self.toggle_dark_mode)
        menubar.add_cascade(label="View", menu=viewmenu)
        self.root.config(menu=menubar)

        self.canvas = tk.Canvas(self.main_frame)
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        tk.Label(self.scrollable_frame, text="Drag & drop or select PDF/ZIP files.").grid(row=0, column=0, columnspan=4, pady=10)
        self.drop_area = tk.Label(self.scrollable_frame, text="Drop PDF or ZIP files here", bg="#e0e0e0", width=70, height=5, relief="ridge")
        self.drop_area.grid(row=1, column=0, columnspan=4, pady=5)
        self.drop_area.drop_target_register('DND_Files')
        self.drop_area.dnd_bind('<<Drop>>', self.handle_drop)

        tk.Button(self.scrollable_frame, text="Select Files", command=self.select_files).grid(row=2, column=0, pady=5)
        tk.Button(self.scrollable_frame, text="Clear Loaded Files", command=self.clear_files).grid(row=2, column=1, pady=5)
        tk.Button(self.scrollable_frame, text="Export to TXT", command=self.export_to_txt).grid(row=2, column=2, pady=5)
        tk.Button(self.scrollable_frame, text="Export Log", command=self.export_log).grid(row=2, column=3, pady=5)

        tk.Label(self.scrollable_frame, text="Loaded Files (with MD5 Hash):").grid(row=3, column=0, sticky='w')
        self.file_listbox = tk.Listbox(self.scrollable_frame, width=100, height=6)
        self.file_listbox.grid(row=4, column=0, columnspan=4, pady=5)

        self.data_listboxes = {}
        data_fields = ['hashes', 'ips', 'emails', 'phones', 'usernames', 'platforms']
        for idx, field in enumerate(data_fields):
            row = 5 + (idx // 2) * 2
            col = (idx % 2) * 2
            tk.Label(self.scrollable_frame, text=field.title() + ":").grid(row=row, column=col, sticky='w')
            listbox = tk.Listbox(self.scrollable_frame, width=40, height=6)
            listbox.grid(row=row+1, column=col, padx=10, pady=5)
            self.data_listboxes[field] = listbox

        self.status = tk.Label(self.scrollable_frame, text="Ready.", fg="green")
        self.status.grid(row=11, column=0, columnspan=4, pady=10)

        self.progress = ttk.Progressbar(self.scrollable_frame, orient=tk.HORIZONTAL, length=600, mode='determinate')
        self.progress.grid(row=12, column=0, columnspan=4, pady=10)

    def show_about(self):
        messagebox.showinfo(
            "About",
            "CyberTip Extractor\nVersion 2.0\nDeveloped by DarkKnightForensics\nhttps://github.com/DarkKnightForensics"
        )

    def show_instructions(self):
        messagebox.showinfo("Instructions", "1. Drag and drop or select PDF/ZIP files.\n2. Extracted data will appear below.\n3. Use Export to TXT to save results.\n4. Use Export Log to save the log file.")

    def export_log(self):
        log_path = os.path.join(os.getcwd(), "cybertip_parser.log")
        dest = filedialog.asksaveasfilename(defaultextension=".log", filetypes=[("Log Files", "*.log"), ("All Files", "*.*")])
        if dest:
            try:
                with open(log_path, "r", encoding="utf-8") as src, open(dest, "w", encoding="utf-8") as dst:
                    dst.write(src.read())
                messagebox.showinfo("Export Log", f"Log exported to {dest}")
            except Exception as e:
                messagebox.showerror("Export Log Error", f"Failed to export log: {e}")

    def export_to_txt(self):
        directory = filedialog.askdirectory(title="Select folder to export .txt files")
        if not directory:
            return
        try:
            start = time.time()
            self.logger.info(f"Starting export to: {directory}")
            for key, values in self.data.items():
                filename = os.path.join(directory, f"{key}.txt")
                sorted_values = sorted(values)
                if key == "ips":
                    def extract_dt(item):
                        try:
                            return datetime.strptime(item.split("→")[-1].strip(), "%Y-%m-%d %H:%M:%S")
                        except:
                            return datetime.min
                    sorted_values = sorted(values, key=extract_dt)
                with open(filename, 'w', encoding='utf-8') as f:
                    for item in sorted_values:
                        f.write(item + "\n")
                self.logger.info(f"Exported {len(sorted_values)} items to {filename}")
            elapsed = time.time() - start
            messagebox.showinfo("Export Complete", f"Data exported to {directory}")
            self.logger.info(f"Exported data to: {directory} in {elapsed:.2f} seconds")
        except Exception as e:
            self.logger.error(f"Failed to export data: {e}")
            messagebox.showerror("Export Error", f"An error occurred while exporting:\n{e}")

    def handle_drop(self, event):
        paths = self.root.tk.splitlist(event.data)
        files = [p for p in paths if p.lower().endswith(('.pdf', '.zip'))]
        self.load_files(files)

    def select_files(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("Supported Files", "*.pdf *.zip")])
        self.load_files(file_paths)

    def load_files(self, paths):
        start_all = time.time()
        total_files = len([p for p in paths if p.lower().endswith(('.pdf', '.zip')) and p not in self.loaded_files])
        self.progress['value'] = 0
        self.progress['maximum'] = total_files if total_files > 0 else 1
        processed = 0
        for path in paths:
            if path in self.loaded_files:
                continue
            if not path.lower().endswith(('.pdf', '.zip')):
                self.logger.warning(f"Skipped unsupported file type: {path}")
                messagebox.showwarning("Unsupported File", f"File skipped (not PDF/ZIP): {os.path.basename(path)}")
                continue
            try:
                # Compute and log MD5 hash before processing
                md5_hash = self._get_md5_hash(path)
                self.logger.info(f"MD5 hash for {path}: {md5_hash}")
                start = time.time()
                self.logger.info(f"Starting processing: {path}")
                if path.lower().endswith(".zip"):
                    self.process_zip_file(path)
                elif path.lower().endswith(".pdf"):
                    self.process_pdf(path)
                self.loaded_files.add(path)
                display_str = f"{os.path.basename(path)}  |  MD5: {md5_hash}"
                self.file_listbox.insert(tk.END, display_str)
                elapsed = time.time() - start
                self.logger.info(f"Finished processing: {path} in {elapsed:.2f} seconds")
                for key in self.data:
                    self.logger.info(f"{key}: {len(self.data[key])} items extracted after {os.path.basename(path)}")
            except Exception as e:
                self.logger.error(f"Failed to process {path}: {e}")
                self.show_error_popup(f"Failed to process {os.path.basename(path)}:\n{e}")
            processed += 1
            self.progress['value'] = processed
            self.root.update_idletasks()
        self.refresh_display()
        total_elapsed = time.time() - start_all
        self.logger.info(f"All files processed in {total_elapsed:.2f} seconds. Total files: {len(self.loaded_files)}")
        for key in self.data:
            self.logger.info(f"SUMMARY: {key}: {len(self.data[key])} total items.")
        self.progress['value'] = 0

    def show_error_popup(self, msg):
        # Improved error popup with copy option
        def copy_to_clipboard():
            self.root.clipboard_clear()
            self.root.clipboard_append(msg)
        err_win = tk.Toplevel(self.root)
        err_win.title("Error Details")
        tk.Label(err_win, text=msg, justify='left', wraplength=500).pack(padx=10, pady=10)
        tk.Button(err_win, text="Copy Details", command=copy_to_clipboard).pack(pady=5)
        tk.Button(err_win, text="Close", command=err_win.destroy).pack(pady=5)

    def refresh_display(self):
        for key, listbox in self.data_listboxes.items():
            listbox.delete(0, tk.END)
            for item in sorted(self.data[key]):
                listbox.insert(tk.END, item)
        self.status.config(text=f"Loaded {len(self.loaded_files)} file(s).")

    def clear_files(self):
        self.logger.info("Clearing all loaded files and extracted data.")
        self.data.clear()
        self.loaded_files.clear()
        self.file_listbox.delete(0, tk.END)
        for listbox in self.data_listboxes.values():
            listbox.delete(0, tk.END)
        self.status.config(text="Cleared all data.")

    def _get_md5_hash(self, file_path):
        import hashlib
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def process_pdf(self, path):
        doc = fitz.open(path)
        full_text = "\n".join(page.get_text("text") for page in doc)
        doc.close()
        self.extract_from_text(full_text)

    def extract_from_text(self, text):
        matches = list(self.SECTION_PATTERN.finditer(text))
        sections = {}
        for i, match in enumerate(matches):
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            sections[match.group().strip()] = text[start:end].strip()
        for name, section_text in sections.items():
            if name.startswith("Section A") or name.startswith("Section B") or name.startswith("Section C"):
                self.parse_section(section_text)
        self._extract_platform(text)

    def _extract_platform(self, text):
        submitter_match = self.SUBMITTER_PATTERN.search(text)
        if submitter_match:
            platform_line = submitter_match.group(2).strip()
            if platform_line and not platform_line.lower().startswith("point of contact"):
                self.data['platforms'].add(platform_line)
                self.logger.debug(f"Extracted platform from Submitter section: {platform_line}")

    def parse_section(self, section_text):
        hashes = self.HASH_PATTERN.findall(section_text)
        self.data['hashes'].update(hashes)
        md5_set = set(hashes)
        ip_time_matches = self.IP_TIME_PATTERN.findall(section_text)
        for ip, timestamp in ip_time_matches:
            try:
                dt = datetime.strptime(timestamp, "%m-%d-%Y %H:%M:%S UTC")
                ts_clean = dt.strftime("%Y-%m-%d %H:%M:%S")
                self.data['ips'].add(f"{ip} → {ts_clean}")
            except Exception:
                continue
        table_matches = self.TABLE_IP_PATTERN.findall(section_text)
        for ip, timestamp in table_matches:
            try:
                dt = datetime.strptime(timestamp, "%m-%d-%Y %H:%M:%S UTC")
                ts_clean = dt.strftime("%Y-%m-%d %H:%M:%S")
                self.data['ips'].add(f"{ip} → {ts_clean}")
            except Exception:
                continue
        for email in self.EMAIL_PATTERN.findall(section_text):
            if not any(domain in email.lower() for domain in [".gov", "@ncmec.org", "@ilag.gov"]):
                self.data['emails'].add(email)
        for match in self.PHONE_PATTERN.finditer(section_text):
            phone = match.group(1)
            digits_only = re.sub(r"\D", "", phone)
            if digits_only not in {"2177829030", "8774462632"} and not any(digits_only in h for h in md5_set):
                self.data['phones'].add(phone)
        patterns = ["Screen/User Name:", "Display Name:", "ESP User ID:"]
        for key in patterns:
            usernames = re.findall(fr"{key}\s*(\S+)", section_text)
            self.data['usernames'].update(usernames)

    def process_zip_file(self, path):
        with zipfile.ZipFile(path, 'r') as zip_ref:
            # Extract to a temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                zip_ref.extractall(temp_dir)
                self.logger.info(f"Extracted ZIP file to temporary directory: {temp_dir}")
                # Process each file in the extracted content
                for file_name in os.listdir(temp_dir):
                    file_path = os.path.join(temp_dir, file_name)
                    if file_name.lower().endswith(".pdf"):
                        self.logger.info(f"Processing PDF file in ZIP: {file_name}")
                        self.process_pdf(file_path)
                    else:
                        self.logger.warning(f"Skipped unsupported file type in ZIP: {file_name}")

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        bg = '#222222' if self.dark_mode else '#f0f0f0'
        fg = '#f0f0f0' if self.dark_mode else '#000000'
        widget_bg = '#333333' if self.dark_mode else '#e0e0e0'
        select_bg = '#444444' if self.dark_mode else '#c0c0c0'
        self.root.configure(bg=bg)
        self.main_frame.configure(bg=bg)
        self.canvas.configure(bg=bg, highlightbackground=bg)
        self.scrollable_frame.configure(bg=bg)
        # Update all widgets in the scrollable frame
        for widget in self.scrollable_frame.winfo_children():
            if isinstance(widget, tk.Label):
                widget.configure(bg=widget_bg, fg=fg)
            elif isinstance(widget, tk.Button):
                widget.configure(bg=bg, fg=fg, activebackground=widget_bg, activeforeground=fg)
            elif isinstance(widget, tk.Listbox):
                widget.configure(bg=bg, fg=fg, selectbackground=select_bg, selectforeground=fg)
            elif isinstance(widget, ttk.Progressbar):
                style = ttk.Style()
                style.theme_use('default')
                style.configure("TProgressbar", troughcolor=bg, background=select_bg, bordercolor=bg, lightcolor=bg, darkcolor=bg)
        self.status.configure(bg=bg, fg=fg)
        # Update menu colors (best effort, limited by Tkinter)
        try:
            self.root.option_add('*Menu.background', widget_bg)
            self.root.option_add('*Menu.foreground', fg)
            self.root.option_add('*Menu.activeBackground', select_bg)
            self.root.option_add('*Menu.activeForeground', fg)
        except Exception:
            pass

if __name__ == '__main__':
    root = TkinterDnD.Tk()
    app = CyberTipExtractorApp(root)
    root.mainloop()
