---
jupytext:
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.11.5
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

# 1. Business Understanding

## Latar Belakang

Informasi penggunaan dan tutupan lahan (*Land Use / Land Cover* atau LULC) sangat berguna untuk analisis ruang, pengelolaan lingkungan, mitigasi risiko bencana, dan perencanaan wilayah di Provinsi Jawa Timur. Keragaman lanskap Jawa Timur yang luas—mencakup persawahan irigasi, perkotaan metropolitan, gugusan hutan pegunungan, badan air danau/waduk, perairan laut, hingga vegetasi mangrove pesisir—menuntut metode pemetaan yang cepat, otomatis, dan dapat diperbarui secara berkala.

Interpretasi citra satelit secara manual membutuhkan waktu yang sangat besar, biaya operasional tinggi, serta rentan terhadap subjektivitas surveyor. Oleh karena itu, pendekatan otomatisasi berbasis *Machine Learning* menggunakan citra satelit multispektral Sentinel-2A menjadi solusi yang andal.

Proyek ini menggunakan data citra Sentinel-2A Level-2A yang diekstraksi ke dalam nilai reflektansi spektral dan indeks turunannya pada berkas `piksel_s2_JTM.csv`, mengacu pada alur eksperimen dalam notebook `Tugas/UTS/test.ipynb`.

## Pengecualian Sampel di Luar Batas Wilayah

Dalam dataset awal, sampel poligon Laut bernomor `Laut_0000` sampai `Laut_0018` (19 poligon dengan total 58.000 piksel) berada melewati batas wilayah administrasi Provinsi Jawa Timur. Oleh karena itu, seluruh sampel tersebut dihapus dan tidak dimasukkan ke dalam analisis, evaluasi model, maupun visualisasi peta. Data laut yang dipertahankan adalah poligon `Laut_0019` hingga `Laut_0048` (30 poligon) yang berada di dalam wilayah perairan Jawa Timur.

## Tujuan

1. **Membangun Model Klasifikasi Berbasis KNN**: Mengembangkan model klasifikasi tutupan lahan otomatis menggunakan algoritma **K-Nearest Neighbors (KNN, $k=5$)**.
2. **Optimalisasi Fitur Spektral**: Memanfaatkan kombinasi 5 band optik Sentinel-2A (`B02`, `B03`, `B04`, `B08`, `B11`) dan 4 indeks spektral (`NDVI`, `NDWI`, `MNDWI`, `NDBI`) untuk separasi kelas yang kokoh.
3. **Evaluasi Performa Model**: Menguji keandalan model pada data uji independen (114.654 piksel) menggunakan metrik akurasi, *precision*, *recall*, *F1-score*, dan matriks konfusi.
4. **Visualisasi Spasial Ganda**: Menampilkan sebaran poligon ground truth interaktif berbasis *Convex Hull* dan peta klasifikasi regional satu provinsi Jawa Timur (`jatim_250m.tif`).
5. **Deployment Web**: Mempublikasikan sistem deteksi interaktif melalui dashboard Streamlit.

## Kelas dan Ruang Lingkup

Analisis mengklasifikasikan 6 kelas tutupan lahan utama di Provinsi Jawa Timur:
1. **Sawah**: Lahan pertanian padi berpetak, genangan air sawah, dan fase vegetatif padi.
2. **Bangunan**: Kawasan terbangun permukiman, gedung, jalan aspal/beton, dan fasilitas industri.
3. **Hutan**: Vegetasi alami kanopi pohon lebat, hutan pegunungan, dan perkebunan tahunan rapat.
4. **Danau**: Badan air tawar pedalaman (waduk buatan, telaga, bendungan, dan danau alami).
5. **Laut**: Badan air asin pesisir dan laut terbuka (nomor 19 sampai 48).
6. **Mangrove**: Komunitas hutan bakau pasang surut di muara sungai dan pantai berlumpur pesisir.

```{code-cell}
from pathlib import Path
import pandas as pd

dataset_path = next(
    (
        candidate
        for folder in (Path.cwd(), *Path.cwd().parents)
        for candidate in (
            folder / "piksel_s2_JTM.csv",
            folder / "Tugas" / "UTS" / "piksel_s2_JTM.csv",
        )
        if candidate.is_file()
    ),
    None,
)
if dataset_path is None:
    raise FileNotFoundError("Dataset piksel_s2_JTM.csv tidak ditemukan.")

df = pd.read_csv(dataset_path)

# Hapus data poligon laut 0 sampai 18 karena melebihi batas Jawa Timur
excluded_laut = {f"Laut_{index:04d}" for index in range(19)}
df = df[~df["poligon_id"].isin(excluded_laut)].copy()

print(f"Dataset: {dataset_path.name}")
print(f"Total baris piksel valid: {len(df):,}")
print(f"Total poligon valid: {df['poligon_id'].nunique()}")
print(f"Jumlah kelas: {df['label_teks'].nunique()}")
print("Daftar kelas:", ", ".join(sorted(df["label_teks"].dropna().unique())))
print("\nSebaran piksel per kelas (setelah filter laut 0-18):")
print(df["label_teks"].value_counts().to_string())
```

## Pertanyaan Analisis

- Seberapa efektif kombinasi 5 band spektral Sentinel-2A dan 4 indeks turunan dalam membedakan 6 kelas tutupan lahan?
- Bagaimana performa dan akurasi klasifikasi algoritma **K-Nearest Neighbors (KNN, $k=5$)** pada data uji independen?
- Di kelas mana model KNN mencapai akurasi tertinggi dan bagaimana karakteristik kesalahan klasifikasinya pada matriks konfusi?
- Bagaimana efektivitas visualisasi spasial berbasis poligon *Convex Hull* dan inferensi citra regional skala 250m?
