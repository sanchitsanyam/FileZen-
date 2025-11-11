#  FileZen+ — Intelligent File Organizer using Python OOP, Data Structures & GC

A **Python + Tkinter GUI** project that automatically organizes files in a chosen folder by their type  
(Images, Documents, Code, etc.). It visually demonstrates **Object-Oriented Programming concepts** and  
**Garbage Collection awareness**, designed for academic coursework (Module V).

---

##  Features

- GUI built with **Tkinter**
- Groups files by extension using a **dictionary (hash map)**
- Moves them into subfolders (e.g., `PNG/`, `PDF/`, `TXT/`, `PY/`)
- Optional: **sort files by size**
- Optional: **delete old unused files** (>N days)
- Shows **object cleanup (GC)** after processing

---

##  Learning Objectives (Module V Mapping)

| Concept | Implementation |
|----------|----------------|
| **Classes & Objects** | `FileItem`, `FileOrganizer`, `FileZenApp` |
| **Attributes / Instances** | `name`, `path`, `ext` per file |
| **Encapsulation & Composition** | Organizer owns multiple FileItem objects |
| **Data Structures** | Dictionary mapping `ext → list[FileItem]` |
| **Algorithms** | Sorting (Timsort O(n log n)) |
| **Garbage Collection** | Explicit `gc.collect()` & `__del__()` for lifecycle demo |
| **OS Concept** | File cleanup simulates GC at filesystem level |

---

##  Installation

```bash
git clone https://github.com/YourUsername/FileZen-Plus.git
cd FileZen-Plus
python filezen_plus_gui.py
```

✅ Requires Python 3.8+  
All modules used are in the Python Standard Library.

---

## 🧪 How to Test

1. Extract the dummy folder in `/demo/FileZen_Test.zip`
2. Launch the app with:
   ```bash
   python filezen_plus_gui.py
   ```
3. Click **Browse...** → select the extracted folder.
4. Click **Run All (Cleanup → Scan → Organize)**.
5. Watch the folder neatly restructured into subfolders.

---

## Folder Output Example

```
FileZen_Test/
 ├── TXT/     → notes.txt
 ├── CSV/     → data.csv
 ├── PY/      → script.py
 ├── PNG/     → image1.png
 └── PDF/     → report.pdf
```

---

## 🖼️ Screenshot (Live System)

Below is the real **FileZen+ GUI** running on Windows while scanning 4000+ files:

![FileZen+ GUI Screenshot](<img width="964" height="728" alt="image" src="https://github.com/user-attachments/assets/6a7cf239-5ecc-44d5-93e4-f173203484b2" />
)

---

## Folder Structure

```
FileZen-Plus/
├── filezen_plus_gui.py
├── README.md
├── LICENSE
├── requirements.txt
├── demo/
│   └── FileZen_Test.zip
└── screenshots/
    └── ui_preview.png
```

---

## License
Released under the **MIT License** — free for educational and personal use.

---


