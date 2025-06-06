import os
import re
import fitz  # PyMuPDF
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinterdnd2 import TkinterDnD
from datetime import datetime
import zipfile
import tempfile

class CyberTipExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CyberTip Extractor - MD5, IP, Service, Usernames")
        self.root.geometry("850x700")
        self.hashes = set()
        self.ip_entries = set()
        self.services = set()
        self.usernames = set()
        self.loaded_files = set()

        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.main_frame)
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.label = tk.Label(self.scrollable_frame, text="Drag & drop or select PDF/CSV/ZIP files.")
        self.label.grid(row=0, column=0, columnspan=4, pady=10)

        self.drop_area = tk.Label(self.scrollable_frame, text="Drop PDF, CSV, or ZIP files here", bg="#e0e0e0", width=70, height=5, relief="ridge")
        self.drop_area.grid(row=1, column=0, columnspan=4, pady=5)
        self.drop_area.drop_target_register('DND_Files')
        self.drop_area.dnd_bind('<<Drop>>', self.handle_drop)

        tk.Button(self.scrollable_frame, text="Select Files", command=self.select_files).grid(row=2, column=0, pady=5)
        tk.Button(self.scrollable_frame, text="Clear Loaded Files", command=self.clear_files).grid(row=2, column=1, pady=5)
        tk.Button(self.scrollable_frame, text="Export to TXT Files", command=self.export_txt_files).grid(row=2, column=2, pady=5)

        tk.Label(self.scrollable_frame, text="Loaded Files:").grid(row=3, column=0, sticky='w')
        self.file_listbox = tk.Listbox(self.scrollable_frame, width=70, height=4)
        self.file_listbox.grid(row=4, column=0, columnspan=4, pady=5)

        self._add_labeled_listbox("MD5 Hashes:", "md5_listbox", 5, 0)
        self._add_labeled_listbox("IP Addresses with Timestamps:", "ip_listbox", 5, 2)
        self._add_labeled_listbox("Chat Services:", "service_listbox", 7, 0)
        self._add_labeled_listbox("Usernames:", "username_listbox", 7, 2)

        self.status = tk.Label(self.scrollable_frame, text="Ready.", fg="green")
        self.status.grid(row=9, column=0, columnspan=4, pady=10)

    def _add_labeled_listbox(self, label, attr_name, row, col):
        tk.Label(self.scrollable_frame, text=label).grid(row=row, column=col, sticky='w')
        listbox = tk.Listbox(self.scrollable_frame, width=40, height=6)
        listbox.grid(row=row + 1, column=col, padx=10, pady=5)
        setattr(self, attr_name, listbox)

    def handle_drop(self, event):
        paths = self.root.tk.splitlist(event.data)
        files = [p for p in paths if p.lower().endswith(('.pdf', '.csv', '.zip'))]
        self.load_files(files)

    def select_files(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("Supported Files", "*.pdf *.csv *.zip")])
        self.load_files(file_paths)

    def load_files(self, paths):
        for path in paths:
            if path in self.loaded_files:
                continue
            try:
                if path.lower().endswith(".zip") and os.path.isfile(path):
                    self.process_zip_file(path)
                elif path.lower().endswith(".pdf"):
                    self.extract_from_pdf(path)
                elif path.lower().endswith(".csv"):
                    self.extract_from_csv(path)
                self.loaded_files.add(path)
                self.file_listbox.insert(tk.END, os.path.basename(path))
            except Exception as e:
                messagebox.showerror("Error", f"Failed to process {os.path.basename(path)}:\n{e}")
        self.refresh_display()

    def process_zip_file(self, zip_path):
        with tempfile.TemporaryDirectory() as extract_dir:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
                for root, _, files in os.walk(extract_dir):
                    for file in files:
                        full_path = os.path.join(root, file)
                        if file.lower().endswith(".pdf"):
                            self.extract_from_pdf(full_path)
                        elif file.lower().endswith(".csv"):
                            self.extract_from_csv(full_path)

    def extract_from_pdf(self, path):
        doc = fitz.open(path)
        text = ""
        capture = False
        for page in doc:
            page_text = page.get_text("text")
            if "Section A" in page_text:
                capture = True
            if "Section D" in page_text:
                capture = False
            if capture:
                text += page_text
        doc.close()

        self.extract_md5(text)
        self.extract_ips(text)
        self.extract_services(text)
        self.extract_usernames(text)

    def extract_from_csv(self, path):
        df = pd.read_csv(path, dtype=str).fillna('')
        content = df.to_string(index=False)
        self.extract_md5(content)
        self.extract_ips(content)
        self.extract_services(content)
        self.extract_usernames(content)

    def extract_md5(self, text):
        found_hashes = re.findall(r"\b[a-fA-F0-9]{32}\b", text)
        self.hashes.update(found_hashes)

    def extract_ips(self, text):
        ip_timestamp_pattern = re.findall(r'(\b\d{1,3}(?:\.\d{1,3}){3}\b).*?(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}|\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2})', text, re.DOTALL)
        for ip, timestamp in ip_timestamp_pattern:
            self.ip_entries.add((ip.strip(), timestamp.strip()))

    def extract_services(self, text):
        found_services = re.findall(r"Chat Service/IM Client:\s*(\S+)", text)
        self.services.update(s.strip() for s in found_services)

    def extract_usernames(self, text):
        patterns = [
            r"Screen/User Name:\s*(\S+)",
            r"Display Name:\s*(\S+)",
            r"ESP User ID:\s*(\S+)",
            r"Home Email Address:\s*(\S+)"
        ]
        for pattern in patterns:
            self.usernames.update(re.findall(pattern, text))

    def parse_timestamp(self, timestamp):
        formats = ["%Y-%m-%d %H:%M:%S", "%m-%d-%Y %H:%M:%S"]
        for fmt in formats:
            try:
                return datetime.strptime(timestamp, fmt)
            except ValueError:
                continue
        return datetime.min

    def refresh_display(self):
        self.md5_listbox.delete(0, tk.END)
        for h in sorted(self.hashes):
            self.md5_listbox.insert(tk.END, h)

        self.ip_listbox.delete(0, tk.END)
        for ip, ts in sorted(self.ip_entries, key=lambda x: self.parse_timestamp(x[1])):
            self.ip_listbox.insert(tk.END, f"{ip} → {ts}")

        self.service_listbox.delete(0, tk.END)
        for service in sorted(self.services):
            self.service_listbox.insert(tk.END, service)

        self.username_listbox.delete(0, tk.END)
        for user in sorted(self.usernames):
            self.username_listbox.insert(tk.END, user)

        self.status.config(text=f"Loaded {len(self.loaded_files)} file(s). {len(self.hashes)} hashes, {len(self.ip_entries)} IPs, {len(self.services)} services, {len(self.usernames)} usernames.")

    def export_txt_files(self):
        if not (self.hashes or self.ip_entries or self.services or self.usernames):
            messagebox.showwarning("No Data", "No data to export.")
            return
        folder = filedialog.askdirectory(title="Select Folder to Save")
        if not folder:
            return

        def write_list(path, lines):
            with open(path, 'w') as f:
                for line in lines:
                    f.write(line + '\n')

        write_list(os.path.join(folder, "md5_hashes.txt"), sorted(self.hashes))
        write_list(os.path.join(folder, "ip_addresses.txt"), [f"{ip}\t{ts}" for ip, ts in sorted(self.ip_entries, key=lambda x: self.parse_timestamp(x[1]))])
        write_list(os.path.join(folder, "chat_services.txt"), sorted(self.services))
        write_list(os.path.join(folder, "usernames.txt"), sorted(self.usernames))

        self.status.config(text=f"Export complete to {folder}.")

    def clear_files(self):
        self.hashes.clear()
        self.ip_entries.clear()
        self.services.clear()
        self.usernames.clear()
        self.loaded_files.clear()
        self.file_listbox.delete(0, tk.END)
        self.md5_listbox.delete(0, tk.END)
        self.ip_listbox.delete(0, tk.END)
        self.service_listbox.delete(0, tk.END)
        self.username_listbox.delete(0, tk.END)
        self.status.config(text="Cleared all data.")

if __name__ == '__main__':
    root = TkinterDnD.Tk()
    app = CyberTipExtractorApp(root)
    root.mainloop()
