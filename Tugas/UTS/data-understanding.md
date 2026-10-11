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

## Sumber dan Bentuk Data

Data yang digunakan adalah hasil ekstraksi sampel piksel citra Sentinel-2A dan disimpan dalam `piksel_s2_JTM.csv`. Notebook memuat berkas tersebut dari folder proyek dan memeriksa keberadaan sejumlah kolom yang diperlukan sebelum analisis dilanjutkan.

Berkas sumber berisi **631.268 baris piksel** dan **19 kolom** pada saat pencatatan. Angka tersebut adalah jumlah baris sebelum penyaringan. Setiap baris merepresentasikan sampel piksel, sedangkan identitas poligon digunakan untuk menghubungkan piksel-piksel yang berasal dari sampel yang sama.

## Kelompok Variabel

| Kelompok | Kolom | Kegunaan |
|---|---|---|
| Identitas sampel | `poligon_id`, `poligon_no`, `sampel_id`, `tile_id` | Menelusuri poligon, sampel, dan tile asal |
| Label | `label`, `label_teks` | Menyimpan kelas dalam bentuk kode dan nama |
| Posisi | `px_row`, `px_col`, `lon`, `lat` | Menyimpan posisi piksel dan koordinat geografis |
| Band spektral | `B02`, `B03`, `B04`, `B08`, `B11` | Menyimpan nilai spektral Sentinel-2A |
| Indeks spektral | `NDVI`, `NDWI`, `MNDWI`, `NDBI` | Merangkum karakteristik spektral yang berkaitan dengan vegetasi, air, dan kawasan terbangun |

Model menggunakan sembilan fitur numerik: lima band (`B02`, `B03`, `B04`, `B08`, `B11`) dan empat indeks (`NDVI`, `NDWI`, `MNDWI`, `NDBI`). Kolom `label_teks` menjadi target klasifikasi.

## Pemeriksaan Data

Notebook memeriksa kolom wajib sebelum memproses data. Jika ada kolom yang hilang, proses dihentikan dengan pesan yang menyebutkan kolom tersebut. Pemeriksaan ini membantu memastikan bahwa dataset sesuai dengan struktur yang dibutuhkan. Untuk menyamakan ruang lingkup analisis dan dashboard, poligon Laut `Laut_0000` sampai `Laut_0018` dikeluarkan dari data analisis karena berada melewati batas wilayah. Baris di CSV sumber tidak dihapus; poligon Laut lainnya tetap dipertahankan.

Satu baris piksel tidak sama dengan satu sampel poligon. Karena itu, jumlah baris piksel yang besar tidak boleh dianggap sebagai jumlah observasi independen untuk evaluasi model. Dashboard menyaring koordinat piksel terhadap batas provinsi terlebih dahulu, lalu menggabungkan piksel berdasarkan `poligon_id` dan memastikan titik rata-rata poligon daratan juga berada di dalam batas sebelum pembagian data. Filter koordinat dashboard mempertahankan sampel Laut yang tidak termasuk dalam daftar pengecualian.

## Output yang Ditampilkan Notebook

Sel berikut memuat ulang dataset, memeriksa kolom wajib, menampilkan ukuran data, dan menghasilkan lima baris pertama langsung dari CSV:

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
kolom_wajib = [
    "poligon_id", "label", "label_teks", "lon", "lat",
    "B02", "B03", "B04", "B08", "B11", "NDVI", "NDWI", "MNDWI", "NDBI",
]
kolom_hilang = sorted(set(kolom_wajib) - set(df.columns))
if kolom_hilang:
    raise ValueError(f"Kolom wajib tidak ditemukan: {kolom_hilang}")

poligon_laut_dikecualikan = {f"Laut_{index:04d}" for index in range(19)}
baris_dikecualikan = df["poligon_id"].isin(poligon_laut_dikecualikan)
jumlah_dikecualikan = int(baris_dikecualikan.sum())
df = df.loc[~baris_dikecualikan].copy()

print(f"Dataset: {dataset_path}")
print(f"Baris piksel dikecualikan: {jumlah_dikecualikan:,}")
print(f"Jumlah baris (piksel): {len(df):,}")
print(f"Jumlah kolom: {df.shape[1]}")
display(df.head())
```
