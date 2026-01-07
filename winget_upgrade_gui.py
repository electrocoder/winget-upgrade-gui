import subprocess
import threading
import os
import ctypes
import sys
import tkinter as tk
from tkinter import messagebox
from typing import List, Dict

# --- OTOMATİK KÜTÜPHANE KONTROLÜ ---
def check_requirements():
    try:
        import PIL
        import pywinstyles
        import customtkinter
    except ImportError:
        print("Eksik kütüphaneler kuruluyor, lütfen bekleyin...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow", "pywinstyles", "customtkinter"])
        os.execl(sys.executable, sys.executable, *sys.argv)

check_requirements()

import customtkinter as ctk
from PIL import Image

# --- WINDOWS SİSTEM AYARI ---
try:
    myappid = 'mse.winget.manager.v2.0.1' 
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except:
    pass

class WingetManager:
    @staticmethod
    def get_updatable_apps() -> List[Dict[str, str]]:
        try:
            subprocess.run("winget source update", shell=True, capture_output=True, text=True)
            cmd = subprocess.check_output("winget upgrade --source winget", shell=True, stderr=subprocess.STDOUT).decode('utf-8', errors='ignore')
            lines = cmd.splitlines()
            apps = []; idx = -1
            for i, line in enumerate(lines):
                if any(x in line for x in ["Version", "Sürüm", "Name", "Ad"]):
                    h = line
                    cols = {"n": h.find("Name") if h.find("Name") != -1 else h.find("Ad"),
                            "i": h.find("Id") if h.find("Id") != -1 else h.find("Kimlik"),
                            "v": h.find("Version") if h.find("Version") != -1 else h.find("Sürüm"),
                            "a": h.find("Available") if h.find("Available") != -1 else h.find("Mevcut")}
                    idx = i + 2; break
            if idx != -1:
                for line in lines[idx:]:
                    if not line.strip() or line.startswith('-'): continue
                    try:
                        apps.append({
                            'name': line[cols["n"]:cols["i"]].strip(),
                            'id': line[cols["i"]:cols["v"]].strip(),
                            'old': line[cols["v"]:cols["a"]].strip(),
                            'new': line[cols["a"]:].split()[0].strip()
                        })
                    except: continue
            return apps
        except: return []

    @staticmethod
    def upgrade_app_with_feedback(app_id: str, callback):
        process = subprocess.Popen(
            ["winget", "upgrade", "--id", app_id, "--silent", "--force", 
             "--accept-package-agreements", "--accept-source-agreements"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
            text=True, shell=True, errors='replace'
        )
        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None: break
            if line: callback(line.strip())
        return process.poll()

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Winget Manager Pro")
        self.geometry("1150x850")
        
        self.base_path = os.path.dirname(__file__)
        self.logo_wide = os.path.join(self.base_path, "logo.png")
        self.logo_ico = os.path.join(self.base_path, "logo.ico")
        
        self._load_icon()
        self.current_theme = "dark"
        ctk.set_appearance_mode(self.current_theme)

        self.check_vars = {}
        self.is_busy = False

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._setup_ui()
        self.select_frame_by_name("home")
        self.after(500, self.start_scan)

    def _load_icon(self):
        try:
            if os.path.exists(self.logo_ico):
                self.iconbitmap(self.logo_ico)
            elif os.path.exists(self.logo_wide):
                self.img_ref = tk.PhotoImage(file=self.logo_wide)
                self.iconphoto(True, self.img_ref)
        except: pass

    def toggle_theme(self):
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        ctk.set_appearance_mode(self.current_theme)
        # Buton metnini güncelle
        self.theme_btn.configure(text="🌙 Karanlık Mod" if self.current_theme == "light" else "☀️ Aydınlık Mod")

    def log(self, message):
        self.log_view.configure(state="normal")
        self.log_view.insert("end", f"> {message}\n")
        self.log_view.see("end")
        self.log_view.configure(state="disabled")

    def _setup_ui(self):
        # --- SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        
        if os.path.exists(self.logo_wide):
            img = ctk.CTkImage(Image.open(self.logo_wide), size=(200, 100))
            ctk.CTkLabel(self.sidebar, image=img, text="").pack(pady=(30, 0))

        ctk.CTkLabel(self.sidebar, text="Winget\nManager Pro", font=("Segoe UI", 24, "bold"), text_color="#3B82F6").pack(pady=(5, 30))

        self.btn_home = ctk.CTkButton(self.sidebar, text="🏠 Güncellemeler", anchor="w", command=lambda: self.select_frame_by_name("home"))
        self.btn_home.pack(fill="x", padx=20, pady=5)

        self.btn_about = ctk.CTkButton(self.sidebar, text="ℹ️ Hakkında", anchor="w", command=lambda: self.select_frame_by_name("about"))
        self.btn_about.pack(fill="x", padx=20, pady=5)

        # --- DÜZELTİLEN TEMA BUTONU ---
        self.theme_btn = ctk.CTkButton(
            self.sidebar, 
            text="☀️ Aydınlık Mod", 
            fg_color="transparent", 
            border_width=1,
            # (Aydınlık modda siyah yazı, Karanlık modda beyaz yazı)
            text_color=("#000000", "#FFFFFF"),
            border_color=("#3B82F6", "#3B82F6"),
            command=self.toggle_theme
        )
        self.theme_btn.pack(side="bottom", pady=30, padx=20, fill="x")

        # --- MAIN CONTAINER ---
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)

        self.home_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self._setup_home_page()

        self.about_frame = ctk.CTkScrollableFrame(self.main_container, fg_color="transparent")
        self._setup_about_content()

    def _setup_home_page(self):
        self.home_frame.grid_columnconfigure(0, weight=1)
        self.home_frame.grid_rowconfigure(1, weight=1)
        self.top_bar = ctk.CTkFrame(self.home_frame, fg_color="transparent")
        self.top_bar.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        ctk.CTkButton(self.top_bar, text="Tümünü Seç / Kaldır", width=160, command=self.toggle_all_selection).pack(side="left")
        self.btn_scan = ctk.CTkButton(self.top_bar, text="🔄 Yenile", width=100, command=self.start_scan, fg_color="#3B82F6")
        self.btn_scan.pack(side="right")
        self.list_view = ctk.CTkScrollableFrame(self.home_frame, corner_radius=15, border_width=1)
        self.list_view.grid(row=1, column=0, sticky="nsew")
        self.log_view = ctk.CTkTextbox(self.home_frame, height=130, state="disabled", font=("Consolas", 11))
        self.log_view.grid(row=2, column=0, sticky="ew", pady=(15, 0))
        self.footer = ctk.CTkFrame(self.home_frame, height=80, corner_radius=15)
        self.footer.grid(row=3, column=0, sticky="ew", pady=(15, 0))
        self.btn_run = ctk.CTkButton(self.footer, text="GÜNCELLEMEYİ BAŞLAT", font=("Segoe UI", 13, "bold"), fg_color="#2EB872", hover_color="#1E7E4E", command=self.run_update)
        self.btn_run.pack(side="right", padx=20, pady=20)
        self.status_label = ctk.CTkLabel(self.footer, text="Hazır", font=("Segoe UI", 12))
        self.status_label.pack(side="left", padx=20)

    def _setup_about_content(self):
        if os.path.exists(self.logo_wide):
            img = ctk.CTkImage(Image.open(self.logo_wide), size=(400, 200))
            ctk.CTkLabel(self.about_frame, image=img, text="").pack(pady=(20, 10))
        ctk.CTkLabel(self.about_frame, text="Winget Manager Pro", font=("Segoe UI", 34, "bold"), text_color="#3B82F6").pack()
        ctk.CTkLabel(self.about_frame, text="Sürüm 2.0.1 Stable | 2026 Edition", font=("Segoe UI", 16), text_color="gray").pack(pady=(5, 20))
        feat_container = ctk.CTkFrame(self.about_frame, fg_color="transparent")
        feat_container.pack(pady=20, padx=40, fill="x")
        feat_container.grid_columnconfigure((0, 1), weight=1)
        features = [
            ("🚀 Yıldırım Hızı", "Winget motoru sayesinde saniyeler içinde tarama yapar."),
            ("🛡️ Tam Güvenlik", "Paketler doğrudan resmi depolardan doğrulanarak gelir."),
            ("🎨 Modern Arayüz", "Şık, hızlı ve tema destekli tasarım."),
            ("📝 Şeffaf Log", "Her işlemin sonucunu anlık olarak izleyin.")
        ]
        for i, (title, desc) in enumerate(features):
            card = ctk.CTkFrame(feat_container, corner_radius=15, border_width=1, border_color=("#DBDBDB", "#2B2B2B"))
            card.grid(row=i//2, column=i%2, padx=10, pady=10, sticky="nsew")
            ctk.CTkLabel(card, text=title, font=("Segoe UI", 18, "bold"), text_color="#3B82F6").pack(pady=(15, 5))
            ctk.CTkLabel(card, text=desc, font=("Segoe UI", 13), wraplength=250, justify="center").pack(pady=(0, 15), padx=10)
        info_frame = ctk.CTkFrame(self.about_frame, corner_radius=15)
        info_frame.pack(pady=30, padx=50, fill="x")
        btn_gh = ctk.CTkButton(info_frame, text="GitHub Proje Sayfası", fg_color="#24292e", command=lambda: os.system("start https://github.com/electrocoder/winget-upgrade-gui"))
        btn_gh.pack(pady=15)

    def select_frame_by_name(self, name):
        self.home_frame.grid_forget(); self.about_frame.grid_forget()
        if name == "home": self.home_frame.grid(row=0, column=0, sticky="nsew")
        else: self.about_frame.grid(row=0, column=0, sticky="nsew")

    def toggle_all_selection(self):
        if not self.check_vars: return
        target = not all(v.get() for v in self.check_vars.values())
        for v in self.check_vars.values(): v.set(target)

    def start_scan(self):
        if self.is_busy: return
        self.is_busy = True
        self.status_label.configure(text="Sistem taranıyor...")
        self.btn_scan.configure(state="disabled")
        threading.Thread(target=self._scan_task, daemon=True).start()

    def _scan_task(self):
        apps = WingetManager.get_updatable_apps()
        self.after(0, lambda: self._draw_apps(apps))

    def _draw_apps(self, apps):
        for w in self.list_view.winfo_children(): w.destroy()
        self.check_vars.clear()
        if not apps:
            ctk.CTkLabel(self.list_view, text="Harika! Tüm paketler güncel.", font=("Segoe UI", 14)).pack(pady=50)
        else:
            for app in apps:
                f = ctk.CTkFrame(self.list_view)
                f.pack(fill="x", pady=2, padx=5)
                v = ctk.BooleanVar()
                self.check_vars[app['id']] = v
                ctk.CTkCheckBox(f, text=f"{app['name']} ({app['old']} -> {app['new']})", variable=v).pack(side="left", padx=10, pady=10)
        self.is_busy = False
        self.btn_scan.configure(state="normal")
        self.status_label.configure(text=f"{len(apps)} güncelleme bulundu.")

    def run_update(self):
        selected = [aid for aid, v in self.check_vars.items() if v.get()]
        if not selected or self.is_busy: return
        self.is_busy = True
        self.btn_run.configure(state="disabled")
        self.log("İşlem başlatıldı...")
        threading.Thread(target=self._update_task, args=(selected,), daemon=True).start()

    def _update_task(self, ids):
        total = len(ids)
        for i, aid in enumerate(ids):
            self.after(0, lambda a=aid, n=i+1: self.status_label.configure(text=f"Güncelleniyor ({n}/{total}): {a}"))
            WingetManager.upgrade_app_with_feedback(aid, self.log)
        self.after(0, self._finalize_update)

    def _finalize_update(self):
        self.is_busy = False
        self.btn_run.configure(state="normal")
        self.log("Bitti.")
        messagebox.showinfo("Başarılı", "Güncellemeler tamamlandı.")
        self.start_scan()

if __name__ == "__main__":
    app = App()
    app.mainloop()