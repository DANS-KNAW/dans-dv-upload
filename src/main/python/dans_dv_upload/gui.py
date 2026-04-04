import os
import logging

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
except ImportError:
    tk = None
    filedialog = None
    messagebox = None
    ttk = None

def combined_gui_dialog(dataverses, default_dataverse_name):
    if tk is None:
        return None, None, None

    results = {"file": None, "doi": None, "dataverse": None}

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
        label = dataverse_var.get()
        dataverse_name = next((dv['name'] for dv in dataverses if dv['label'] == label), None)

        if not doi:
            messagebox.showerror("Error", "Please enter a DOI.")
            return
        if not file_path:
            messagebox.showerror("Error", "Please select a file.")
            return
        if not dataverse_name:
            messagebox.showerror("Error", "Please select a dataverse.")
            return

        results["file"] = file_path
        results["doi"] = doi
        results["dataverse"] = dataverse_name
        
        # Switch to progress view
        for child in root.winfo_children():
            child.grid_forget()
        
        tk.Label(root, text="Uploading file...").grid(row=0, column=0, padx=20, pady=10)
        progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
        progress_bar.grid(row=1, column=0, padx=20, pady=10)
        
        def update_progress(current, total):
            if total > 0:
                percent = (current / total) * 100
                progress_bar["value"] = percent
                root.update_idletasks()

        results["update_progress"] = update_progress
        root.quit() # Exit mainloop but keep window alive

    root = tk.Tk()
    root.title("Upload file to dataset")

    doi_var = tk.StringVar()
    file_var = tk.StringVar()
    dataverse_var = tk.StringVar()

    # Dataverse selection
    labels = [dv['label'] for dv in dataverses]
    default_label = next((dv['label'] for dv in dataverses if dv['name'] == default_dataverse_name),
                         labels[0] if labels else "")
    dataverse_var.set(default_label)

    tk.Label(root, text="Dataverse").grid(row=0, column=0, sticky="w", padx=5, pady=5)
    if labels:
        tk.OptionMenu(root, dataverse_var, *labels).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
    else:
        tk.Entry(root, textvariable=dataverse_var, state='disabled', width=50).grid(row=0, column=1, padx=5, pady=5)

    # DOI
    tk.Label(root, text="Dataset DOI").grid(row=1, column=0, sticky="w", padx=5, pady=5)
    tk.Entry(root, textvariable=doi_var, width=50).grid(row=1, column=1, padx=5, pady=5)

    # File
    tk.Label(root, text="File").grid(row=2, column=0, sticky="w", padx=5, pady=5)
    tk.Entry(root, textvariable=file_var, width=50).grid(row=2, column=1, padx=5, pady=5)
    tk.Button(root, text="Browse...", command=browse_file).grid(row=2, column=2, padx=5, pady=5)

    tk.Button(root, text="Submit", command=submit).grid(row=3, column=1, pady=10)

    # Center the window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    root.mainloop()
    return results["file"], results["doi"], results["dataverse"], results.get("update_progress"), root

def show_finished_message(root):
    if tk is not None:
        messagebox.showinfo("Finished", "Finished")
        root.destroy()
