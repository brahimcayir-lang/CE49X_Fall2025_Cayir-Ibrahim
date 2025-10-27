"""
==============================================================
Lab 3: ERA5 Weather Data Analysis
Author: Ibrahim Çayır
Student ID: 2020403207
Course: CE49X - Fall 2025
==============================================================

🎯 AMAÇ:
ERA5 reanalysis veri seti kullanılarak Berlin ve Münih için
rüzgar hızı analizleri yapılır. Analiz adımları şunlardır:

1️⃣ CSV dosyalarını güvenli şekilde yükleme ve doğrulama  
2️⃣ u10m ve v10m bileşenlerinden rüzgar hızını (magnitude) hesaplama  
3️⃣ Aylık ve mevsimsel ortalamaları çıkarma  
4️⃣ İki şehir arasında karşılaştırmalı grafik çizme  
5️⃣ Sonuç özetlerini CSV olarak dışa aktarma  

Kod, farklı bilgisayarlarda da çalışabilir çünkü dizin yolları
dinamik olarak oluşturulur (göreceli path yöntemi).
"""

# =====================================================
# === 0. Gerekli Kütüphanelerin Yüklenmesi ===
# =====================================================

# Pathlib → modern dosya yolu yönetimi (Windows, Linux, macOS fark etmeksizin çalışır)
# os → klasör oluşturma, dosya var mı kontrol etme gibi sistem fonksiyonları
# pandas → veri manipülasyonu (DataFrame yapısı)
# numpy → hızlı matematiksel hesaplar (örneğin karekök, ortalama vb)
# matplotlib → veri görselleştirme
# seaborn → matplotlib üzerine kurulmuş, estetik grafik stili sağlar

from pathlib import Path
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


# =====================================================
# === 1. Veri Yükleme Fonksiyonu ===
# =====================================================

def load_data(file_path):
    """
    CSV dosyasını güvenli bir şekilde yükler ve zaman kolonu tespit eder.

    Adımlar:
    1️⃣ Dosya var mı kontrol edilir.  
    2️⃣ CSV pandas DataFrame olarak okunur.  
    3️⃣ time/date benzeri kolon otomatik bulunur.  
    4️⃣ Zaman bilgisi datetime tipine çevrilir (analiz kolaylığı için).  

    Dönüş:
        → Başarılıysa: pandas.DataFrame
        → Hatalıysa: None
    """

    # Dosya yolu nesnesi (Pathlib sayesinde platform bağımsız)
    p = Path(file_path)

    # Eğer dosya yoksa kullanıcıya bilgi ver ve işlemi durdur
    if not p.exists():
        print(f"❌ File not found: {p}")
        return None

    try:
        # CSV dosyasını oku → pandas otomatik olarak virgül ayırıcıyı tanır
        df = pd.read_csv(str(p))

        # Muhtemel zaman kolonlarını listele
        # lower() → büyük/küçük harf farkını ortadan kaldırır
        time_candidates = [
            c for c in df.columns
            if c.lower() in {"time", "timestamp", "date", "valid_time", "datetime"}
        ]

        # Eğer bu kolonlardan biri varsa datetime tipine çevir
        if time_candidates:
            src = time_candidates[0]  # ilk eşleşeni seç
            df["time"] = pd.to_datetime(df[src])
        else:
            # Beklenen kolonlardan hiçbiri yoksa kullanıcıya hata ver
            raise KeyError(
                "No time-like column found. Expected one of: time, timestamp, date, valid_time, datetime"
            )

        # Veri hakkında bilgi ver (kaç satır / sütun)
        print(f"✅ Loaded: {p.name} | Rows: {df.shape[0]}, Columns: {df.shape[1]}")
        return df

    except Exception as e:
        # Örneğin dosya bozuksa veya kodlama hatası varsa hata mesajı göster
        print(f"⚠️ Error loading {p}: {e}")
        return None


# =====================================================
# === 2. Rüzgar Hızı (Vektör Büyüklüğü) Hesabı ===
# =====================================================

def add_wind_speed(df):
    """
    ERA5 veri setinde rüzgar 2 bileşen halinde verilir:
        - u10m → doğu-batı yönü (x-ekseni)
        - v10m → kuzey-güney yönü (y-ekseni)
    Gerçek rüzgar hızı, bu iki bileşenin vektörel toplamıdır.

    Formül:
        wind_speed = √(u10m² + v10m²)
    """

    # Önce gerekli kolonlar var mı kontrol et
    if not {"u10m", "v10m"}.issubset(df.columns):
        missing = {"u10m", "v10m"} - set(df.columns)
        raise KeyError(f"Missing columns for wind speed: {sorted(missing)}")

    # Numpy ile vektör büyüklüğü hesaplanır (tüm satırlar için)
    df["wind_speed"] = np.sqrt(df["u10m"]**2 + df["v10m"]**2)

    # Yeni kolon eklendi → aynı DataFrame döndürülür
    return df


# =====================================================
# === 3. Aylık ve Mevsimsel Ortalama Hesabı ===
# =====================================================

def monthly_and_seasonal_stats(df, city_name):
    """
    Amaç:
        Her ay ve mevsim için ortalama rüzgar hızını hesaplamak.

    Kullanılan işlemler:
        → datetime özelliklerinden .dt.month ile ay bilgisi alınır.
        → mevsim hesaplaması: month % 12 // 3 + 1
    """

    # ----------------------------------------------------------
    # .dt.month → datetime tipindeki "time" kolonundan ay numarası (1–12) alır
    # ----------------------------------------------------------
    df["month"] = df["time"].dt.month

    # ----------------------------------------------------------
    # 🌤️ Mevsim Hesabı:
    # ----------------------------------------------------------
    # df["month"] % 12 → Aralık (12) ayını 0 yapar (mod işlemi)
    # // 3 → 0–2 → 0 (Kış), 3–5 → 1 (İlkbahar), 6–8 → 2 (Yaz), 9–11 → 3 (Sonbahar)
    # +1 → mevsim numarasını 1’den başlatır
    #
    # Sonuç:
    #   1 = Winter (Dec–Feb)
    #   2 = Spring (Mar–May)
    #   3 = Summer (Jun–Aug)
    #   4 = Fall (Sep–Nov)
    df["season"] = df["month"] % 12 // 3 + 1

    # ----------------------------------------------------------
    # Aylık ortalama → aynı ay numarasına sahip satırların ortalaması
    # groupby("month")["wind_speed"].mean() işlemi bunu yapar
    # ----------------------------------------------------------
    monthly_avg = df.groupby("month")["wind_speed"].mean()

    # ----------------------------------------------------------
    # Mevsimsel ortalama → 1-4 arası season numarasına göre ortalama
    # ----------------------------------------------------------
    seasonal_avg = df.groupby("season")["wind_speed"].mean()

    # round(2) → sayıları 2 ondalık basamağa yuvarlar (görsellik için)
    # Örn: 5.6789 → 5.68
    print(f"\n🌆 {city_name} — Monthly Average Wind Speed (m/s):\n", monthly_avg.round(2))
    print(f"\n🌦️ {city_name} — Seasonal Average Wind Speed (m/s):\n", seasonal_avg.round(2))

    # Fonksiyon hem aylık hem mevsimsel ortalamaları döndürür
    return monthly_avg, seasonal_avg


# =====================================================
# === 4. Grafiksel Karşılaştırmalar ===
# =====================================================

def plot_monthly_comparison(berlin_monthly, munich_monthly):
    """
    Aylık ortalama rüzgar hızlarını karşılaştıran çizgi grafik.

    X → ay (1–12)
    Y → ortalama hız (m/s)
    """

    plt.figure(figsize=(10, 6))          # grafik boyutu (inch cinsinden)
    plt.plot(berlin_monthly.index, berlin_monthly.values, label="Berlin", marker="o")
    plt.plot(munich_monthly.index, munich_monthly.values, label="Munich", marker="s")
    plt.title("Monthly Average Wind Speed (2024)")
    plt.xlabel("Month")
    plt.ylabel("Wind Speed (m/s)")
    plt.legend()                         # şehir isimleri için açıklama kutusu
    plt.grid(True)                       # ızgara çizgileri okunabilirliği artırır
    plt.tight_layout()                   # kenar boşluklarını otomatik ayarlar
    plt.show()                           # grafiği ekrana bastırır


def plot_seasonal_comparison(berlin_seasonal, munich_seasonal):
    """
    Mevsimsel ortalama rüzgar hızlarını çubuk grafikle gösterir.
    Gruplanmış bar chart kullanılarak iki şehir yan yana gösterilir.
    """

    seasons = ["Winter", "Spring", "Summer", "Fall"]  # etiketler
    x = np.arange(len(seasons))  # 0,1,2,3 → bar pozisyonları
    width = 0.35                 # bar kalınlığı

    plt.figure(figsize=(8, 5))
    plt.bar(x - width/2, berlin_seasonal.values, width, label="Berlin")
    plt.bar(x + width/2, munich_seasonal.values, width, label="Munich")
    plt.title("Seasonal Average Wind Speed (2024)")
    plt.xticks(x, seasons)       # x eksenine mevsim isimleri yaz
    plt.ylabel("Wind Speed (m/s)")
    plt.legend()
    plt.tight_layout()
    plt.show()


# =====================================================
# === 5. Sonuçların CSV'ye Kaydedilmesi ===
# =====================================================

def save_results_to_csv(berlin_monthly, munich_monthly, out_dir):
    """
    Berlin ve Münih’in aylık ortalamalarını tek bir CSV dosyasına yazar.

    → Çıktı dosya adı: era5_wind_summary.csv
    → Sütunlar:
        Month, Berlin_Avg_Wind, Munich_Avg_Wind
    """

    out_dir = Path(out_dir)
    os.makedirs(out_dir, exist_ok=True)  # klasör yoksa oluştur (idempotent işlem)

    # DataFrame oluşturulur (satırlar: aylar)
    summary = pd.DataFrame({
        "Month": berlin_monthly.index,
        "Berlin_Avg_Wind": berlin_monthly.values,
        "Munich_Avg_Wind": munich_monthly.values,
    })

    # Dosya yolu + kayıt işlemi
    out_path = out_dir / "era5_wind_summary.csv"
    summary.to_csv(out_path, index=False)  # index kolonunu dahil etme
    print(f"💾 Results successfully saved to: {out_path}")


# =====================================================
# === 6. Ana Çalışma Bloğu ===
# =====================================================

if __name__ == "__main__":
    # Bu blok sadece dosya doğrudan çalıştırıldığında yürütülür (import edildiğinde değil).

    # 1️⃣ Ana proje dizinini dinamik bul
    # __file__ → şu anda çalışan dosyanın yoludur.
    # .resolve() → tam path üretir
    # .parents[2] → iki klasör yukarı çıkar (örnek: .../CE49X-Fall25/)
    REPO_ROOT = Path(__file__).resolve().parents[2]

    # 2️⃣ Veri ve çıktı klasörleri
    DATA_DIR = REPO_ROOT / "datasets"
    OUTPUT_DIR = REPO_ROOT / "outputs"

    # 3️⃣ Beklenen CSV dosya yolları
    berlin_path = DATA_DIR / "berlin_era5_wind_20241231_20241231.csv"
    munich_path = DATA_DIR / "munich_era5_wind_20241231_20241231.csv"

    # 4️⃣ Alternatif isimli dosyalar için esnek arama fonksiyonu
    def pick_first(pattern):
        candidates = sorted(DATA_DIR.glob(pattern))
        return candidates[-1] if candidates else None

    # Dosyalar yoksa benzer isimli birini bul
    if not berlin_path.exists():
        alt = pick_first("*berlin*wind*.csv") or pick_first("*berlin*.csv")
        if alt is not None:
            berlin_path = alt
    if not munich_path.exists():
        alt = pick_first("*munich*wind*.csv") or pick_first("*munich*.csv")
        if alt is not None:
            munich_path = alt

    # 5️⃣ Kullanıcıya mevcut durum bilgisi
    print("\n=== ERA5 Weather Data Analysis ===")
    print("Repository root:", REPO_ROOT)
    print("Data directory:", DATA_DIR)
    print("Berlin dataset:", berlin_path)
    print("Munich dataset:", munich_path)

    # Dosyaların varlığını kontrol et (yoksa program durur)
    for p in [berlin_path, munich_path]:
        if not p or not Path(p).exists():
            print(f"⚠️ File not found: {p}")
            if DATA_DIR.exists():
                print("\nAvailable files in datasets directory:")
                for f in sorted(DATA_DIR.glob("*.csv")):
                    print(" -", f.name)
            raise SystemExit(1)  # programı güvenli şekilde durdur

    # 6️⃣ Verileri yükle
    berlin = load_data(berlin_path)
    munich = load_data(munich_path)

    # 7️⃣ Yükleme başarılıysa analiz başlat
    if berlin is not None and munich is not None:

        # Rüzgar hızı bileşenlerini hesapla
        berlin = add_wind_speed(berlin)
        munich = add_wind_speed(munich)

        # Aylık ve mevsimsel ortalamaları çıkar
        berlin_monthly, berlin_seasonal = monthly_and_seasonal_stats(berlin, "Berlin")
        munich_monthly, munich_seasonal = monthly_and_seasonal_stats(munich, "Munich")

        # Görselleştirmeleri çiz
        plot_monthly_comparison(berlin_monthly, munich_monthly)
        plot_seasonal_comparison(berlin_seasonal, munich_seasonal)

        # Sonuçları kaydet
        save_results_to_csv(berlin_monthly, munich_monthly, OUTPUT_DIR)

    else:
        print("🚫 Could not process datasets. Please check your file paths and retry.")
