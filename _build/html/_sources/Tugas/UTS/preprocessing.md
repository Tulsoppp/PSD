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

# 4. Preprocessing Data

## Pemilihan Fitur dan Pembersihan

Fitur yang digunakan untuk klasifikasi adalah:

`B02`, `B03`, `B04`, `B08`, `B11`, `NDVI`, `NDWI`, `MNDWI`, dan `NDBI`.

Baris yang memiliki nilai tak hingga (`inf` atau `-inf`) diubah menjadi nilai kosong, kemudian baris dengan nilai kosong pada kolom yang digunakan dihapus. Data yang telah dibersihkan mencakup label dan koordinat agar bisa dipakai untuk pemodelan maupun pemetaan.

## Agregasi per Poligon

Semua piksel dengan `poligon_id` yang sama diringkas menjadi satu observasi. Nilai fitur serta koordinat (`lon`, `lat`) dihitung menggunakan rata-rata. Label numerik dan label teks diambil dari baris pertama pada setiap poligon.

Agregasi ini mencegah piksel-piksel dari poligon yang sama tersebar ke data latih dan data uji, yang dapat membuat evaluasi terlihat lebih baik daripada kemampuan generalisasi model yang sebenarnya.

## Pembagian Data

Data poligon dibagi menjadi:

- **70% data latih**
- **30% data uji**

Pembagian menggunakan `random_state=42` agar hasil pembagian dapat direproduksi dan `stratify=y` untuk mempertahankan proporsi kelas. Jumlah poligon dan pembagiannya ditampilkan langsung oleh sel preprocessing di bawah.

## Standarisasi

`StandardScaler` digunakan untuk menstandarkan skala fitur. Scaler hanya di-*fit* pada data latih, kemudian digunakan untuk mentransformasi data latih dan data uji. Dengan demikian, informasi dari data uji tidak digunakan saat menentukan parameter standarisasi.

Data hasil standarisasi digunakan oleh Gaussian Naive Bayes dan KNN.

## Menjalankan Preprocessing

Sel ini menjalankan pembersihan, agregasi per poligon, pembagian data, dan standarisasi. Angka jumlah data akan muncul dari dataset yang dibaca saat sel dijalankan.

```{code-cell}
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

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
fitur = ["B02", "B03", "B04", "B08", "B11", "NDVI", "NDWI", "MNDWI", "NDBI"]
kolom_agregasi = ["poligon_id", "label", "label_teks", "lon", "lat", *fitur]
df_bersih = df[kolom_agregasi].replace([np.inf, -np.inf], np.nan).dropna().copy()

poligon = (
    df_bersih.groupby("poligon_id", as_index=False)
    .agg(
        label=("label", "first"),
        label_teks=("label_teks", "first"),
        lon=("lon", "mean"),
        lat=("lat", "mean"),
        **{nama_fitur: (nama_fitur, "mean") for nama_fitur in fitur},
    )
)

X = poligon[fitur]
y = poligon["label_teks"]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print(f"Jumlah poligon: {len(poligon):,}")
print(f"Jumlah data latih: {len(X_train):,}")
print(f"Jumlah data uji: {len(X_test):,}")
```
