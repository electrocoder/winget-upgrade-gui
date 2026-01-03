# 🚀 MEŞE BİLİŞİM | winget_upgrade_gui v8.6

![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)
![Framework](https://img.shields.io/badge/framework-CustomTkinter-orange.svg)
![Style](https://img.shields.io/badge/style-Acrylic_Glass-purple.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

Windows uygulamalarınızı tek tıkla güncel tutmanızı sağlayan, **Acrylic Glass** efektli, modern ve Dashboard tabanlı Winget yöneticisi.

---

## ✨ Öne Çıkan Özellikler

- **🗂️ Dashboard Mimarisi:** Sidebar üzerinden sekmeler arası hızlı ve akıcı geçiş.
- **💎 Acrylic Glass Efekti:** Modern "buzlu cam" arayüzü (Windows 10 ve 11 uyumlu).
- **🎨 Dinamik Tema:** Dark ve Light mod geçişlerinde otomatik kontrast ayarı.
- **🖼️ Logo Desteği:** Kurumsal kimliğe uygun High-DPI logo entegrasyonu.
- **🔍 Otomatik Tarama:** Uygulama açıldığı anda güncellemeleri kontrol eden mekanizma.

![Ana Ekran](https://github.com/user-attachments/assets/47c9d0c4-2c15-4963-8ea3-22e5863d4969)

![Detaylar](https://github.com/user-attachments/assets/77016039-ba2f-442b-80f4-4947a3ef8d9c)



## 🚀 Kurulum ve Çalıştırma
- **1. Kütüphaneleri Yükleyin
Uygulamanın çalışması için gerekli tüm bağımlılıkları terminale (CMD veya PowerShell) aşağıdaki komutu yapıştırarak kurun:
```
pip install customtkinter Pillow requests pywinstyles
```
- **2. Uygulamayı Başlatın
Kütüphane kurulumu tamamlandıktan sonra, projenin bulunduğu dizinde şu komutu çalıştırarak arayüzü başlatabilirsiniz:
```
python winget_upgrade_gui.py
```
- **3. Çalıştırma
Proje klasöründe terminali açın ve uygulamayı başlatın:
```
python winget_upgrade_gui.py
```

## 🛠️ Teknik Detaylar
Uygulama, Windows'un yerleşik paket yöneticisi olan Winget altyapısını kullanır. Güvenli bir işlem süreci için şu parametreleri otomatik olarak onaylar:

--accept-package-agreements (Paket anlaşmalarını onayla)

--accept-source-agreements (Kaynak anlaşmalarını onayla)

--force (Zorunlu güncelleme modunu aktif et)
