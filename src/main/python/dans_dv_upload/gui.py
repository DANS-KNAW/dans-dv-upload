import os
import logging

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox
except ImportError:
    tk = None
    filedialog = None
    messagebox = None

def combined_gui_dialog():
    if tk is None:
        return None, None

    results = {"file": None, "doi": None}

    def browse_file():
        path = filedialog.askopenfilename(
            title="Select file to upload",
            initialdir=os.path.expanduser("~")
        )
        if path:
            file_var.set(path)

    def submit():
        file_path = file_var.get().strip()
        doi = doi_var.get().strip()

        if not doi:
            messagebox.showerror("Error", "Please enter a DOI.")
            return
        if not file_path:
            messagebox.showerror("Error", "Please select a file.")
            return

        results["file"] = file_path
        results["doi"] = doi
        root.destroy()

    root = tk.Tk()
    root.title("Upload file to dataset")

    doi_var = tk.StringVar()
    file_var = tk.StringVar()

    # Reversed order: DOI first
    tk.Label(root, text="Dataset DOI").grid(row=0, column=0, sticky="w", padx=5, pady=5)
    tk.Entry(root, textvariable=doi_var, width=50).grid(row=0, column=1, padx=5, pady=5)

    # File second
    tk.Label(root, text="File").grid(row=1, column=0, sticky="w", padx=5, pady=5)
    tk.Entry(root, textvariable=file_var, width=50).grid(row=1, column=1, padx=5, pady=5)
    tk.Button(root, text="Browse...", command=browse_file).grid(row=1, column=2, padx=5, pady=5)

    tk.Button(root, text="Submit", command=submit).grid(row=2, column=1, pady=10)

    # Center the window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    root.mainloop()
    return results["file"], results["doi"]
