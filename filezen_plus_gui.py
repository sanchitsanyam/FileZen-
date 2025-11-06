"""
FileZen+ — Live GUI: Intelligent File Organizer using Python OOP, Data Structures & GC
- GUI built with Tkinter (no external dependencies)
- Organizes files in a chosen folder by extension (PNG/, PDF/, TXT/, etc.)
- Demonstrates OOP (FileItem, FileOrganizer) and GC awareness
- Optional: delete files older than N days, and sort groups by size

Run:
  python filezen_plus_gui.py
"""

import os, shutil, time, gc, threading
from typing import Dict, List
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# --------------------------
# 1) Represent one file
# --------------------------
class FileItem:
    def __init__(self, path: str):
        self.path = path
        self.name = os.path.basename(path)
        self.ext = (os.path.splitext(self.name)[1].lower() or "none").strip(".")  # e.g., "png"

    def move_to(self, target_folder: str, log_fn=print):
        os.makedirs(target_folder, exist_ok=True)
        dest = os.path.join(target_folder, self.name)
        shutil.move(self.path, dest)
        log_fn(f"Moved: {self.name}  →  {target_folder}")

    def __del__(self):
        # Educational: shows when objects are reclaimed (timing is implementation-dependent)
        # Avoid heavy UI ops from __del__; just a lightweight print
        # (real UI logging is done during normal flow)
        pass

# --------------------------
# 2) Organizer with a dict
# --------------------------
class FileOrganizer:
    def __init__(self, base_folder: str, log_fn=print):
        self.base = os.path.abspath(base_folder)
        self.files_by_type: Dict[str, List[FileItem]] = {}
        self.log = log_fn

    def scan(self) -> None:
        """Scan base folder and group files by extension using a dictionary."""
        self.files_by_type.clear()
        count = 0
        try:
            entries = os.listdir(self.base)
        except Exception as e:
            self.log(f"[ERROR] Cannot list directory: {e}")
            return

        for entry in entries:
            path = os.path.join(self.base, entry)
            if os.path.isfile(path):
                item = FileItem(path)
                self.files_by_type.setdefault(item.ext or "OTHERS", []).append(item)
                count += 1

        self.log(f"Scanned: {count} files")
        self.log(f"Groups : {', '.join(sorted(self.files_by_type.keys())) or '(none)'}")

    def organize(self, sort_by_size: bool = False) -> None:
        """Move each group into its own subfolder. Optional: sort within each group by file size."""
        groups = list(self.files_by_type.items())
        if not groups:
            self.log("Nothing to organize. (Did you scan?)")
            return

        for ext, items in groups:
            if sort_by_size:
                try:
                    items.sort(key=lambda it: os.path.getsize(it.path))
                except FileNotFoundError:
                    # Some files may move during operation, skip missing
                    items = [it for it in items if os.path.exists(it.path)]
                    items.sort(key=lambda it: os.path.getsize(it.path))

            target = os.path.join(self.base, ext.upper() if ext else "OTHERS")
            for it in items:
                try:
                    it.move_to(target, log_fn=self.log)
                except Exception as e:
                    self.log(f"[WARN] Failed to move {it.name}: {e}")

        # Drop references so GC can reclaim FileItem objects; then nudge GC
        self.files_by_type.clear()
        gc.collect()
        self.log("Organization complete. (Dropped references and suggested GC.)")

    def clean_old_files(self, days: int = 30) -> int:
        """
        OPTIONAL: Delete files older than 'days' in the base folder.
        Simulates 'garbage collection' at the file-system level.
        """
        now = time.time()
        threshold = days * 24 * 60 * 60
        deleted = 0
        try:
            entries = os.listdir(self.base)
        except Exception as e:
            self.log(f"[ERROR] Cannot list directory: {e}")
            return 0

        for entry in entries:
            path = os.path.join(self.base, entry)
            if os.path.isfile(path):
                try:
                    age_days = (now - os.path.getmtime(path)) / (60 * 60 * 24)
                    if age_days > days:
                        os.remove(path)
                        deleted += 1
                        self.log(f"Deleted old file ({age_days:.1f} days): {entry}")
                except Exception as e:
                    self.log(f"[WARN] Could not handle {entry}: {e}")
        gc.collect()
        self.log(f"Old-file cleanup complete: {deleted} files removed.")
        return deleted

# --------------------------
# 3) GUI Application
# --------------------------
class FileZenApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FileZen+ — Intelligent File Organizer (Python OOP + GC)")
        self.geometry("780x560")
        self.resizable(False, False)

        self.base_folder_var = tk.StringVar(value=os.path.abspath("."))
        self.sort_var = tk.BooleanVar(value=False)
        self.cleanup_var = tk.BooleanVar(value=False)
        self.days_var = tk.IntVar(value=30)

        self._build_ui()
        self._organizer = None
        self._lock_ui(False)

    # UI construction
    def _build_ui(self):
        frm = ttk.Frame(self, padding=12)
        frm.pack(fill="both", expand=True)

        # Folder chooser
        row1 = ttk.Frame(frm)
        row1.pack(fill="x", pady=(0, 8))
        ttk.Label(row1, text="Folder:").pack(side="left")
        self.entry_folder = ttk.Entry(row1, textvariable=self.base_folder_var, width=70)
        self.entry_folder.pack(side="left", padx=6)
        ttk.Button(row1, text="Browse…", command=self.choose_folder).pack(side="left")

        # Options
        row2 = ttk.Frame(frm)
        row2.pack(fill="x", pady=(0, 6))
        ttk.Checkbutton(row2, text="Sort groups by file size", variable=self.sort_var).pack(side="left")
        ttk.Checkbutton(row2, text="Delete old files first", variable=self.cleanup_var).pack(side="left", padx=(18, 6))
        ttk.Label(row2, text="Days:").pack(side="left")
        self.spin_days = ttk.Spinbox(row2, from_=1, to=3650, textvariable=self.days_var, width=6)
        self.spin_days.pack(side="left")

        # Buttons
        row3 = ttk.Frame(frm)
        row3.pack(fill="x", pady=(4, 8))
        self.btn_scan = ttk.Button(row3, text="Scan", command=self._scan_thread)
        self.btn_scan.pack(side="left")
        self.btn_organize = ttk.Button(row3, text="Organize", command=self._organize_thread)
        self.btn_organize.pack(side="left", padx=6)
        self.btn_runall = ttk.Button(row3, text="Run All (Cleanup → Scan → Organize)", command=self._run_all_thread)
        self.btn_runall.pack(side="left", padx=6)

        # Log area
        ttk.Label(frm, text="Log:").pack(anchor="w")
        self.txt = tk.Text(frm, wrap="word", height=22, state="disabled")
        self.txt.pack(fill="both", expand=True)
        self.scroll = ttk.Scrollbar(self.txt, command=self.txt.yview)
        self.txt.configure(yscrollcommand=self.scroll.set)
        self.scroll.pack(side="right", fill="y")

        # Footer
        self.status = ttk.Label(frm, text="Ready.", anchor="w")
        self.status.pack(fill="x", pady=(6,0))

        # Style
        try:
            self._set_style()
        except Exception:
            pass

    def _set_style(self):
        style = ttk.Style()
        if "clam" in style.theme_names():
            style.theme_use("clam")

    def choose_folder(self):
        folder = filedialog.askdirectory(initialdir=self.base_folder_var.get(), title="Choose a folder")
        if folder:
            self.base_folder_var.set(folder)

    # Logging helpers
    def _log(self, msg: str):
        self.txt.configure(state="normal")
        self.txt.insert("end", msg + "\n")
        self.txt.see("end")
        self.txt.configure(state="disabled")

    def _clear_log(self):
        self.txt.configure(state="normal")
        self.txt.delete("1.0", "end")
        self.txt.configure(state="disabled")

    # Background execution helpers
    def _lock_ui(self, locked: bool):
        state = "disabled" if locked else "normal"
        for w in (self.entry_folder, self.btn_scan, self.btn_organize, self.btn_runall, self.spin_days):
            try:
                w.configure(state=state)
            except tk.TclError:
                pass

    def _with_organizer(self):
        base = self.base_folder_var.get().strip()
        if not base:
            messagebox.showerror("Error", "Please choose a folder.")
            return None
        if not os.path.isdir(base):
            messagebox.showerror("Error", f"Not a directory:\n{base}")
            return None
        self._organizer = FileOrganizer(base_folder=base, log_fn=lambda m: self.after(0, self._log, m))
        return self._organizer

    # Thread wrappers
    def _scan_thread(self):
        org = self._with_organizer()
        if not org:
            return
        self._run_in_thread(self._do_scan, org)

    def _organize_thread(self):
        org = self._with_organizer()
        if not org:
            return
        self._run_in_thread(self._do_organize, org, self.sort_var.get())

    def _run_all_thread(self):
        org = self._with_organizer()
        if not org:
            return
        self._run_in_thread(self._do_run_all, org, self.cleanup_var.get(), self.days_var.get(), self.sort_var.get())

    def _run_in_thread(self, fn, *args):
        self._lock_ui(True)
        self.status.configure(text="Working…")
        threading.Thread(target=self._thread_target, args=(fn, *args), daemon=True).start()

    def _thread_target(self, fn, *args):
        try:
            fn(*args)
        except Exception as e:
            self.after(0, self._log, f"[ERROR] {e}")
        finally:
            self.after(0, self._lock_ui, False)
            self.after(0, self.status.configure, {"text": "Ready."})

    # Actual tasks
    def _do_scan(self, org: FileOrganizer):
        self._clear_log()
        self._log(f"Base folder: {org.base}")
        org.scan()

    def _do_organize(self, org: FileOrganizer, sort_flag: bool):
        self._log(f"Organizing (sort_by_size={sort_flag})…")
        org.organize(sort_by_size=sort_flag)

    def _do_run_all(self, org: FileOrganizer, cleanup_flag: bool, days: int, sort_flag: bool):
        self._clear_log()
        self._log(f"Base folder: {org.base}")
        if cleanup_flag:
            self._log(f"Cleaning old files (> {days} days)…")
            org.clean_old_files(days=days)
        self._log("Scanning…")
        org.scan()
        self._log(f"Organizing (sort_by_size={sort_flag})…")
        org.organize(sort_by_size=sort_flag)

def main():
    app = FileZenApp()
    app.mainloop()

if __name__ == "__main__":
    main()
