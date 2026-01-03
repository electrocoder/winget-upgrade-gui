import subprocess
import threading
import tkinter as tk
from tkinter import messagebox
from typing import List, Dict
import customtkinter as ctk

try:
    import pywinstyles
    HAS_STYLE = True
except ImportError:
    HAS_STYLE = False

class WingetManager:
    @staticmethod
    def get_updatable_apps() -> List[Dict[str, str]]:
        try:
            cmd = subprocess.check_output("winget upgrade --source winget", shell=True, stderr=subprocess.STDOUT).decode('utf-8', errors='ignore')
            lines = cmd.splitlines()
            apps = []; idx = -1
            for i, line in enumerate(lines):
                if any(x in line for x in ["Version", "Sürüm"]):
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
    def upgrade_app(app_id: str):
        subprocess.run(["winget", "upgrade", "--id", app_id, "--silent", "--force", "--accept-package-agreements", "--accept-source-agreements"], shell=True)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("winget_upgrade_gui v8.5")
        self.geometry("1150x850")
        
        # --- LOGO HAZIRLIĞI ---
        try:
            import requests
            from PIL import Image
            from io import BytesIO
            
            logo_url = "https://mesebilisim.github.io/mesebilisim-logo-220x51.png"
            response = requests.get(logo_url, timeout=5)
            raw_img = Image.open(BytesIO(response.content))
            
            # Hem açık hem koyu tema için logoyu tanımlıyoruz
            self.logo_image = ctk.CTkImage(
                light_image=raw_img, 
                dark_image=raw_img, 
                size=(180, 42)
            )
        except Exception as e:
            print(f"Logo yükleme hatası: {e}")
            self.logo_image = None
        # ----------------------

        # State (Durum) Değişkenleri
        self.check_vars = {}
        self.is_busy = False
        
        # Layout ve UI Kurulumu
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._setup_ui()
        self._apply_glass()
        
        # Başlangıç Sayfası
        self.select_frame_by_name("home")
        self.start_scan()

    def _apply_glass(self):
        if HAS_STYLE:
            mode = ctk.get_appearance_mode()
            # Light modda tam beyaz, Dark modda tam siyah taban
            bg = "#FFFFFF" if mode == "Light" else "#000000"
            self.configure(fg_color=bg)
            try:
                pywinstyles.apply_style(self, "acrylic")
                self.attributes("-alpha", 0.97)
            except: pass

    def _setup_ui(self):
        # --- SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=("#F2F2F2", "#080808"))
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="Winget Upgrade GUI", font=("Segoe UI", 20, "bold"), text_color=("#1A73E8", "#3B82F6")).pack(pady=30)

        self.btn_home = ctk.CTkButton(self.sidebar, text="Güncellemeler", fg_color="transparent", text_color=("#000000", "#AAAAAA"), hover_color=("#E5E5E5", "#151515"), anchor="w", command=lambda: self.select_frame_by_name("home"))
        self.btn_home.pack(fill="x", padx=20, pady=5)

        self.btn_settings = ctk.CTkButton(self.sidebar, text="Ayarlar", fg_color="transparent", text_color=("#000000", "#AAAAAA"), hover_color=("#E5E5E5", "#151515"), anchor="w", command=lambda: self.select_frame_by_name("settings"))
        self.btn_settings.pack(fill="x", padx=20, pady=5)

        self.btn_about = ctk.CTkButton(self.sidebar, text="Hakkında", fg_color="transparent", text_color=("#000000", "#AAAAAA"), hover_color=("#E5E5E5", "#151515"), anchor="w", command=lambda: self.select_frame_by_name("about"))
        self.btn_about.pack(fill="x", padx=20, pady=5)

        # --- HOME FRAME ---
        self.home_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.list_view = ctk.CTkScrollableFrame(self.home_frame, fg_color=("#FFFFFF", "#030303"), corner_radius=15, border_width=1, border_color=("#DDDDDD", "#151515"))
        self.list_view.pack(fill="both", expand=True, padx=30, pady=(20, 10))
        
        self.footer = ctk.CTkFrame(self.home_frame, fg_color=("#F9F9F9", "#080808"), corner_radius=15)
        self.footer.pack(fill="x", padx=30, pady=20)
        
        self.btn_scan_act = ctk.CTkButton(self.footer, text="Taramayı Yenile", width=120, command=self.start_scan)
        self.btn_scan_act.pack(side="left", padx=20)
        
        self.p_bar = ctk.CTkProgressBar(self.footer, width=300, progress_color="#3B82F6")
        self.p_bar.pack(side="left", padx=20)
        self.p_bar.set(0)

        self.btn_update_act = ctk.CTkButton(self.footer, text="GÜNCELLEMEYİ BAŞLAT", font=("Segoe UI", 12, "bold"), fg_color=("#1A73E8", "#FFFFFF"), text_color=("#FFFFFF", "#000000"), command=self.run_update)
        self.btn_update_act.pack(side="right", padx=20)

        # --- SETTINGS FRAME ---
        self.settings_frame = ctk.CTkFrame(self, fg_color="transparent")
        ctk.CTkLabel(self.settings_frame, text="Ayarlar", font=("Segoe UI", 24, "bold"), text_color=("#000000", "#FFFFFF")).pack(pady=30, padx=40, anchor="w")
        ctk.CTkLabel(self.settings_frame, text="Görünüm Modu:", text_color=("#333333", "#CCCCCC")).pack(padx=40, anchor="w")
        self.theme_opt = ctk.CTkOptionMenu(self.settings_frame, values=["Dark", "Light"], command=self.change_theme)
        self.theme_opt.pack(padx=40, pady=10, anchor="w")

        # --- ABOUT FRAME ---
        self.about_frame = ctk.CTkFrame(self, fg_color="transparent")
        ctk.CTkLabel(self.about_frame, text="Hakkında", font=("Segoe UI", 24, "bold"), text_color=("#000000", "#FFFFFF")).pack(pady=30, padx=40, anchor="w")
        ctk.CTkLabel(self.about_frame, text="winget_upgrade_gui v8.5\n\nBu uygulama Meşe Bilişim tarafından\nsisteminizi güncel tutmak için tasarlandı.", justify="left", text_color=("#444444", "#888888")).pack(padx=40, anchor="w")

    def select_frame_by_name(self, name):
        self.home_frame.grid_forget(); self.settings_frame.grid_forget(); self.about_frame.grid_forget()
        self.btn_home.configure(fg_color="transparent"); self.btn_settings.configure(fg_color="transparent"); self.btn_about.configure(fg_color="transparent")
        
        if name == "home":
            self.home_frame.grid(row=0, column=1, sticky="nsew")
            self.btn_home.configure(fg_color=("#E5E5E5", "#151515"))
        elif name == "settings":
            self.settings_frame.grid(row=0, column=1, sticky="nsew")
            self.btn_settings.configure(fg_color=("#E5E5E5", "#151515"))
        elif name == "about":
            self.about_frame.grid(row=0, column=1, sticky="nsew")
            self.btn_about.configure(fg_color=("#E5E5E5", "#151515"))

    def change_theme(self, mode):
        ctk.set_appearance_mode(mode)
        self.after(200, self._apply_glass)

    def start_scan(self):
        if self.is_busy: return
        self.is_busy = True
        self.btn_update_act.configure(state="disabled")
        for w in self.list_view.winfo_children(): w.destroy()
        ctk.CTkLabel(self.list_view, text="🔍 Güncellemeler kontrol ediliyor...", text_color=("#333333", "#888888")).pack(pady=100)
        threading.Thread(target=self._scan_task, daemon=True).start()

    def _scan_task(self):
        apps = WingetManager.get_updatable_apps()
        self.after(0, lambda: self._draw_apps(apps))

    def _draw_apps(self, apps):
        self.is_busy = False
        for w in self.list_view.winfo_children(): w.destroy()
        self.check_vars.clear()
        
        if not apps:
            ctk.CTkLabel(self.list_view, text="✅ Sisteminiz tamamen güncel.", font=("Segoe UI", 16), text_color="#3B82F6").pack(pady=100)
        else:
            for app in apps:
                card = ctk.CTkFrame(self.list_view, fg_color=("#F2F2F2", "#0A0A0A"), corner_radius=10, border_width=1, border_color=("#E0E0E0", "#1A1A1A"))
                card.pack(fill="x", pady=5, padx=15)
                
                var = ctk.BooleanVar(value=False)
                self.check_vars[app['id']] = var
                
                # Checkbox metni temaya göre netleşti
                ctk.CTkCheckBox(card, text=f"{app['name']} ({app['old']} ➔ {app['new']})", variable=var, text_color=("#000000", "#FFFFFF"), font=("Segoe UI", 13, "bold")).pack(side="left", padx=20, pady=15)
        
        self.btn_update_act.configure(state="normal")

    def run_update(self):
        selected = [pid for pid, var in self.check_vars.items() if var.get()]
        if not selected:
            messagebox.showwarning("Seçim Yok", "Lütfen en az bir uygulama seçin.")
            return
        self.is_busy = True
        self.btn_update_act.configure(state="disabled")
        threading.Thread(target=self._update_task, args=(selected,), daemon=True).start()

    def _update_task(self, ids):
        total = len(ids)
        for i, app_id in enumerate(ids):
            WingetManager.upgrade_app(app_id)
            self.after(0, lambda v=(i+1)/total: self.p_bar.set(v))
        
        self.after(0, self._finish_update)

    def _finish_update(self):
        messagebox.showinfo("Bitti", "Güncellemeler yüklendi.")
        self.start_scan()

if __name__ == "__main__":
    app = App()
    app.mainloop()