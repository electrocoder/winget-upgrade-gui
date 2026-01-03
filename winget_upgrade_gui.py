# 03.01.2026
# electrocoder
# windows 11 otomatik uygulama güncelleyici arayüz

import subprocess
import tkinter as tk
from tkinter import messagebox, ttk
import re
import threading

def get_upgrades():
    try:
        # Run winget upgrade and capture output
        output = subprocess.check_output(["winget", "upgrade", "--source", "winget"], shell=True)
        lines = output.decode('utf-8', errors='ignore').splitlines()
        
        upgrades = []
        header_line = None
        name_col = id_col = ver_col = avail_col = source_col = None
        
        # Find the header line
        for i, line in enumerate(lines):
            if "Version" in line and "Available" in line:  # English
                header_line = line
                name_col = header_line.find("Name")
                id_col = header_line.find("Id")
                ver_col = header_line.find("Version")
                avail_col = header_line.find("Available")
                source_col = header_line.find("Source")
                start_index = i + 1
                break
            elif "Sürüm" in line and "Mevcut" in line:  # Turkish
                header_line = line
                name_col = header_line.find("Ad")
                id_col = header_line.find("Kimlik")
                ver_col = header_line.find("Sürüm")
                avail_col = header_line.find("Mevcut")
                source_col = header_line.find("Kaynak")
                start_index = i + 1
                break
        
        if header_line is None:
            return []
        
        # Parse the package lines until the summary line
        for line in lines[start_index:]:
            if re.match(r'^\d+ upgrades? available', line) or line.strip() == "":
                break
            if line.strip() and not line.startswith('-'):
                name = line[name_col:id_col].strip() if name_col is not None else ""
                pkg_id = line[id_col:ver_col].strip() if id_col is not None else ""
                version = line[ver_col:avail_col].strip() if ver_col is not None else ""
                available = line[avail_col:source_col].strip() if avail_col is not None else ""
                source = line[source_col:].strip() if source_col is not None else ""
                upgrades.append({
                    'name': name,
                    'id': pkg_id,
                    'version': version,
                    'available': available,
                    'source': source
                })
        
        return upgrades
    except Exception as e:
        messagebox.showerror("Error", f"Failed to get upgrades: {str(e)}")
        return []

def update_package(pkg_id, progress_var, status_label, progress_bar):
    try:
        process = subprocess.Popen(["winget", "upgrade", "--id", pkg_id, "--silent"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                status_label.config(text=output.strip())
                root.update_idletasks()
        
        process.communicate()
        if process.returncode == 0:
            messagebox.showinfo("Success", f"Updated package with ID: {pkg_id}")
        else:
            messagebox.showerror("Error", f"Failed to update {pkg_id}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to update: {str(e)}")
    finally:
        progress_var.set(100)  # Complete

def run_update(pkg_id, progress_frame, progress_var, status_label, progress_bar):
    progress_frame.pack(pady=10, fill=tk.X)
    status_label.config(text=f"Updating {pkg_id}...")
    progress_var.set(0)
    
    # Simulate progress since winget doesn't provide percentage
    def simulate_progress():
        for i in range(101):
            progress_var.set(i)
            root.after(50)  # Fake delay
    
    threading.Thread(target=simulate_progress).start()
    threading.Thread(target=update_package, args=(pkg_id, progress_var, status_label, progress_bar)).start()

def update_selected(progress_frame, progress_var, status_label, progress_bar):
    selected = [pkg_id for pkg_id, var in check_vars.items() if var.get()]
    for pkg_id in selected:
        run_update(pkg_id, progress_frame, progress_var, status_label, progress_bar)

def update_all(progress_frame, progress_var, status_label, progress_bar):
    all_ids = list(check_vars.keys())
    for pkg_id in all_ids:
        run_update(pkg_id, progress_frame, progress_var, status_label, progress_bar)

def refresh_list():
    global check_vars, upgrades, scrollable_frame
    # Clear existing list
    for widget in scrollable_frame.winfo_children():
        widget.destroy()
    
    # Reload upgrades
    upgrades = get_upgrades()
    
    if not upgrades:
        ttk.Label(scrollable_frame, text="No upgrades available or failed to load.", font=('Arial', 12)).pack(pady=20)
    else:
        check_vars = {}
        colors = ['#ffffff', '#f0f8ff']  # Alternating row colors
        for i, pkg in enumerate(upgrades):
            frame = ttk.Frame(scrollable_frame)
            frame.pack(fill=tk.X, pady=5)
            frame.configure(style='Row.TFrame')
            style.configure('Row.TFrame', background=colors[i % 2])
            
            check_var = tk.BooleanVar()
            check_vars[pkg['id']] = check_var
            ttk.Checkbutton(frame, variable=check_var).pack(side=tk.LEFT, padx=5)
            
            ttk.Label(frame, text=pkg['name'], width=40, anchor='w', background=colors[i % 2]).pack(side=tk.LEFT)
            ttk.Label(frame, text=pkg['version'], width=15, anchor='w', background=colors[i % 2]).pack(side=tk.LEFT)
            ttk.Label(frame, text=pkg['available'], width=15, anchor='w', background=colors[i % 2]).pack(side=tk.LEFT)
            
            update_btn = ttk.Button(frame, text="Güncelle", command=lambda p=pkg: run_update(p['id'], progress_frame, progress_var, status_label, progress_bar))
            update_btn.pack(side=tk.LEFT, padx=5)
    
    # Update scroll region
    scrollable_frame.event_generate("<Configure>")
    select_all_var.set(0)

# Main GUI
root = tk.Tk()
root.title("Winget Upgrade GUI")
root.geometry("800x600")
root.configure(bg='#e6f2ff')  # Light blue background

style = ttk.Style(root)
style.theme_use('clam')
style.configure('TFrame', background='#e6f2ff')
style.configure('TLabel', background='#e6f2ff', foreground='#333333', font=('Arial', 10))
style.configure('TButton', background='#4CAF50', foreground='white', font=('Arial', 10, 'bold'), padding=8)
style.map('TButton', background=[('active', '#45a049')])
style.configure('TCheckbutton', background='#e6f2ff', foreground='#333333', font=('Arial', 10))
style.configure('Horizontal.TProgressbar', troughcolor='#d9d9d9', background='#4CAF50')

upgrades = get_upgrades()

# Progress area (hidden initially)
progress_frame = ttk.Frame(root)
progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(progress_frame, variable=progress_var, maximum=100, style='Horizontal.TProgressbar')
progress_bar.pack(fill=tk.X, padx=20, pady=5)
status_label = ttk.Label(progress_frame, text="Starting update...", background='#e6f2ff')
status_label.pack(pady=5)

# Header
header_frame = ttk.Frame(root)
header_frame.pack(fill=tk.X, pady=10, padx=10)

ttk.Label(header_frame, text="", width=5).pack(side=tk.LEFT)  # Checkbox space
ttk.Label(header_frame, text="Name", width=40, anchor='w', font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
ttk.Label(header_frame, text="Current", width=15, anchor='w', font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
ttk.Label(header_frame, text="Available", width=15, anchor='w', font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
ttk.Label(header_frame, text="Action", width=15, font=('Arial', 10, 'bold')).pack(side=tk.LEFT)

# Scrollable area
canvas = tk.Canvas(root, bg='#e6f2ff', highlightthickness=0)
scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollable_frame = ttk.Frame(canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

# Mouse wheel support
def _on_mouse_wheel(event):
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

root.bind("<MouseWheel>", _on_mouse_wheel)

canvas.pack(side="left", fill="both", expand=True, padx=10)
scrollbar.pack(side="right", fill="y")

check_vars = {}
if not upgrades:
    ttk.Label(scrollable_frame, text="No upgrades available or failed to load.", font=('Arial', 12)).pack(pady=20)
else:
    colors = ['#ffffff', '#f0f8ff']  # Alternating row colors
    for i, pkg in enumerate(upgrades):
        frame = ttk.Frame(scrollable_frame)
        frame.pack(fill=tk.X, pady=5)
        frame.configure(style='Row.TFrame')
        style.configure('Row.TFrame', background=colors[i % 2])
        
        check_var = tk.BooleanVar()
        check_vars[pkg['id']] = check_var
        ttk.Checkbutton(frame, variable=check_var).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(frame, text=pkg['name'], width=40, anchor='w', background=colors[i % 2]).pack(side=tk.LEFT)
        ttk.Label(frame, text=pkg['version'], width=15, anchor='w', background=colors[i % 2]).pack(side=tk.LEFT)
        ttk.Label(frame, text=pkg['available'], width=15, anchor='w', background=colors[i % 2]).pack(side=tk.LEFT)
        
        update_btn = ttk.Button(frame, text="Güncelle", command=lambda p=pkg: run_update(p['id'], progress_frame, progress_var, status_label, progress_bar))
        update_btn.pack(side=tk.LEFT, padx=5)

# Bottom buttons (fixed at bottom)
btn_frame = ttk.Frame(root)
btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
    
select_all_var = tk.BooleanVar()
ttk.Checkbutton(btn_frame, text="Tümünü Seç", variable=select_all_var, 
                command=lambda: [v.set(select_all_var.get()) for v in check_vars.values()]).pack(side=tk.LEFT, padx=10)
    
ttk.Button(btn_frame, text="Seçilenleri Güncelle", command=lambda: update_selected(progress_frame, progress_var, status_label, progress_bar)).pack(side=tk.LEFT, padx=10)
ttk.Button(btn_frame, text="Tümünü Güncelle", command=lambda: update_all(progress_frame, progress_var, status_label, progress_bar)).pack(side=tk.LEFT, padx=10)
ttk.Button(btn_frame, text="Listeyi Yenile", command=refresh_list).pack(side=tk.LEFT, padx=10)

root.mainloop()
