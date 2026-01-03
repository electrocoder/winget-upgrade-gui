import subprocess
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import threading

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class AppUpdater(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Electrocoder | Smart Updater")
        self.geometry("1000x750")
        self.upgrades = []
        self.check_vars = {}
        self.is_processing = False
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.setup_ui()
        self.after(500, self.refresh_list)

    def setup_ui(self):
        self.header = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.header.grid(row=0, column=0, padx=30, pady=(40, 20), sticky="ew")
        self.main_title = ctk.CTkLabel(self.header, text="electrocoder", font=ctk.CTkFont(family="Segoe UI", size=32))
        self.main_title.pack(side="left", anchor="s")
        self.brand_lbl = ctk.CTkLabel(self.header, text="/ codecosoft", font=ctk.CTkFont(family="Segoe UI Light", size=18), text_color="#555555")
        self.brand_lbl.pack(side="left", padx=10, anchor="s", pady=5)

        self.list_frame = ctk.CTkScrollableFrame(self, fg_color="#121212", corner_radius=20, border_width=1, border_color="#222222")
        self.list_frame.grid(row=1, column=0, padx=30, pady=10, sticky="nsew")

        self.footer = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.footer.grid(row=2, column=0, padx=30, pady=25, sticky="ew")
        self.info_container = ctk.CTkFrame(self.footer, fg_color="transparent")
        self.info_container.pack(side="left", fill="x", expand=True)
        self.status_lbl = ctk.CTkLabel(self.info_container, text="Sistem Hazır", font=("Segoe UI", 13), text_color="#888888")
        self.status_lbl.pack(side="top", anchor="w")
        self.p_bar = ctk.CTkProgressBar(self.info_container, width=300, height=4, progress_color="#3b82f6", fg_color="#222222")
        self.p_bar.pack(side="top", anchor="w", pady=8); self.p_bar.set(0)

        self.btn_update = ctk.CTkButton(self.footer, text="Seçilenleri Güncelle", font=ctk.CTkFont(size=13, weight="bold"), height=40, corner_radius=8, fg_color="#ffffff", text_color="#000000", hover_color="#e0e0e0", command=self.bulk_update)
        self.btn_update.pack(side="right", padx=10)
        self.btn_refresh = ctk.CTkButton(self.footer, text="Yenile", width=80, height=40, corner_radius=8, fg_color="#1a1a1a", border_width=1, border_color="#333333", hover_color="#252525", command=self.refresh_list)
        self.btn_refresh.pack(side="right")

    def get_winget_output(self):
        try:
            cmd = subprocess.check_output("winget upgrade --source winget", shell=True, stderr=subprocess.STDOUT)
            lines = cmd.decode('utf-8', errors='ignore').splitlines()
            apps = []; idx = -1
            for i, line in enumerate(lines):
                if any(x in line for x in ["Version", "Sürüm"]):
                    h = line
                    self.c = {
                        "n": h.find("Name") if h.find("Name") != -1 else h.find("Ad"),
                        "i": h.find("Id") if h.find("Id") != -1 else h.find("Kimlik"),
                        "v": h.find("Version") if h.find("Version") != -1 else h.find("Sürüm"),
                        "a": h.find("Available") if h.find("Available") != -1 else h.find("Mevcut")
                    }
                    idx = i + 2; break
            if idx != -1:
                for line in lines[idx:]:
                    if not line.strip() or line.startswith('-'): continue
                    if "upgrades available" in line.lower() or "güncelleme mevcut" in line.lower(): break
                    try:
                        apps.append({
                            'name': line[self.c["n"]:self.c["i"]].strip(),
                            'id': line[self.c["i"]:self.c["v"]].strip(),
                            'v': line[self.c["v"]:self.c["a"]].strip(),
                            'new': line[self.c["a"]:].split()[0].strip()
                        })
                    except: continue
            return apps
        except: return []

    def refresh_list(self):
        if self.is_processing: return
        self.is_processing = True
        self.status_lbl.configure(text="Güncellemeler taranıyor...")
        for w in self.list_frame.winfo_children(): w.destroy()
        def scan():
            data = self.get_winget_output()
            self.after(0, lambda: self.draw_items(data))
        threading.Thread(target=scan, daemon=True).start()

    def draw_items(self, data):
        self.upgrades = data; self.check_vars = {}
        if not data:
            ctk.CTkLabel(self.list_frame, text="Sistem Güncel.", font=("Segoe UI", 14)).pack(pady=80)
        else:
            for item in data:
                card = ctk.CTkFrame(self.list_frame, fg_color="#1a1a1a", corner_radius=12, border_width=1, border_color="#252525")
                card.pack(fill="x", pady=6, padx=10)
                v = ctk.BooleanVar(); self.check_vars[item['id']] = v
                ctk.CTkCheckBox(card, text="", variable=v, width=20).pack(side="left", padx=15)
                info_frame = ctk.CTkFrame(card, fg_color="transparent")
                info_frame.pack(side="left", pady=12, fill="both", expand=True)
                ctk.CTkLabel(info_frame, text=item['name'], font=("Segoe UI", 13, "bold"), anchor="w").pack(fill="x")
                ctk.CTkLabel(info_frame, text=f"{item['v']}  →  {item['new']}", font=("Segoe UI Semilight", 11), text_color="#3b82f6", anchor="w").pack(fill="x")
                btn = ctk.CTkButton(card, text="Güncelle", width=90, height=30, corner_radius=6, fg_color="#222222", command=lambda p=item['id']: self.start_thread([p]))
                btn.pack(side="right", padx=15)
        self.status_lbl.configure(text=f"Tarama bitti: {len(data)} güncelleme bulundu.")
        self.is_processing = False

    def bulk_update(self):
        selected = [pid for pid, v in self.check_vars.items() if v.get()]
        if selected: self.start_thread(selected)

    def start_thread(self, pids):
        self.btn_update.configure(state="disabled")
        threading.Thread(target=self.work, args=(pids,), daemon=True).start()

    def work(self, pids):
        results = []
        for i, pid in enumerate(pids):
            self.after(0, lambda p=pid, idx=i: self.status_lbl.configure(text=f"Kuruluyor: {p}..."))
            
            # Winget komutunu çalıştır ve çıktısını al
            process = subprocess.run(
                ["winget", "upgrade", "--id", pid, "--silent", "--force", "--accept-package-agreements", "--accept-source-agreements"],
                shell=True, capture_output=True, text=True
            )
            
            # Başarı kontrolü: Çıkış kodu 0 olmalı ve çıktı içinde "Successfully installed" veya "Başarıyla yüklendi" geçmeli
            success = process.returncode == 0 and ("Successfully" in process.stdout or "Başarıyla" in process.stdout)
            
            if not success:
                results.append(f"❌ {pid} (Hata kodu: {process.returncode})")
            else:
                results.append(f"✅ {pid}")
            
            self.after(0, lambda idx=i: self.p_bar.set((idx+1)/len(pids)))
        
        self.after(0, lambda: self.done(results))

    def done(self, results):
        self.p_bar.set(0)
        self.btn_update.configure(state="normal")
        summary = "\n".join(results)
        messagebox.showinfo("İşlem Özeti", f"Sonuçlar:\n\n{summary}")
        self.refresh_list()

if __name__ == "__main__":
    app = AppUpdater()
    app.mainloop()