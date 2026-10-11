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

# 2. Data Understanding

## Sumber dan Karakteristik Data

Data yang digunakan dalam analisis ini adalah hasil ekstraksi sampel piksel citra satelit **Sentinel-2A Level-2A (Bottom-of-Atmosphere / BOA Surface Reflectance)** yang disimpan dalam berkas `piksel_s2_JTM.csv`, mengacu pada alur pengolahan pada notebook acuan `Tugas/UTS/test.ipynb`.

Sampel poligon Laut nomor 0 sampai 18 (`Laut_0000` hingga `Laut_0018`) sebanyak 58.000 piksel telah dihapus dan tidak diikutsertakan karena posisinya berada di luar batas wilayah administrasi Provinsi Jawa Timur.

Dataset valid yang dianalisis memiliki karakteristik utama:
* **Jumlah Baris (Piksel)**: **573.268 piksel**
* **Jumlah Kolom**: **19 kolom** (metadata koordinat geografis, atribut poligon, band spektral asli, dan indeks turunan)
* **Jumlah Poligon Sampel Ground Truth**: **280 poligon**

## Kelompok Variabel Dataset

| Kelompok | Kolom | Tipe Data | Kegunaan |
|---|---|---|---|
| **Identitas Sampel** | `poligon_id`, `poligon_no`, `sampel_id`, `tile_id` | Teks / Integer | Melacak poligon asal, ID fitur digitasi, dan nomor tile grid CDSE |
| **Label Kelas** | `label`, `label_teks` | Integer / Teks | Kategori kelas tutupan lahan (kode numerik 1-6 dan nama teks) |
| **Koordinat Spasial** | `px_row`, `px_col`, `lon`, `lat` | Integer / Float | Baris/kolom raster citra dan koordinat geografis (Longitude, Latitude) WGS84 |
| **Band Spektral Asli** | `B02`, `B03`, `B04`, `B08`, `B11` | Float | Nilai reflektansi permukaan BOA (Blue, Green, Red, NIR, SWIR) |
| **Indeks Spektral Turunan** | `NDVI`, `NDWI`, `MNDWI`, `NDBI` | Float | Indeks biofisik untuk mempertajam separasi vegetasi, air, dan kawasan terbangun |

Fitur prediktor yang dipakai untuk pemodelan klasifikasi adalah 9 fitur numerik:
$$\text{Fitur} = \{\text{B02}, \text{B03}, \text{B04}, \text{B08}, \text{B11}, \text{NDVI}, \text{NDWI}, \text{MNDWI}, \text{NDBI}\}$$

Kolom target (*label*) klasifikasi adalah `label_teks`.

## Formula Indeks Spektral

1. **NDVI (Normalized Difference Vegetation Index)**:
   $$\text{NDVI} = \frac{\text{B08} - \text{B04}}{\text{B08} + \text{B04} + 10^{-9}}$$
2. **NDWI (Normalized Difference Water Index - McFeeters)**:
   $$\text{NDWI} = \frac{\text{B03} - \text{B08}}{\text{B03} + \text{B08} + 10^{-9}}$$
3. **MNDWI (Modified NDWI - Xu)**:
   $$\text{MNDWI} = \frac{\text{B03} - \text{B11}}{\text{B03} + \text{B11} + 10^{-9}}$$
4. **NDBI (Normalized Difference Built-up Index)**:
   $$\text{NDBI} = \frac{\text{B11} - \text{B08}}{\text{B11} + \text{B08} + 10^{-9}}$$

## Pemeriksaan Dataset

Sel berikut memuat dataset dari file CSV, mengecualikan poligon laut di luar batas wilayah (nomor 0 sampai 18), memeriksa integritas fitur wajib, serta menampilkan ringkasan data dan lima baris pertama:

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

# Pengecualian poligon laut 0 sampai 18 karena melebihi batas wilayah Jawa Timur
excluded_laut = {f"Laut_{index:04d}" for index in range(19)}
df = df[~df["poligon_id"].isin(excluded_laut)].copy()

kolom_wajib = [
    "poligon_id", "label", "label_teks", "lon", "lat",
    "B02", "B03", "B04", "B08", "B11", "NDVI", "NDWI", "MNDWI", "NDBI",
]
kolom_hilang = sorted(set(kolom_wajib) - set(df.columns))
if kolom_hilang:
    raise ValueError(f"Kolom wajib tidak ditemukan: {kolom_hilang}")

print(f"File: {dataset_path.name}")
print(f"Jumlah baris (piksel) valid: {df.shape[0]:,}")
print(f"Jumlah kolom: {df.shape[1]}")
print(f"Jumlah poligon unik valid: {df['poligon_id'].nunique()}")

print("\nDistribusi sampel piksel per kelas (tanpa Laut 0-18):")
print(df["label_teks"].value_counts().to_string())

display(df.head())
```
