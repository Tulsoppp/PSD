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

Poligon Laut `Laut_0000` sampai `Laut_0018` dikecualikan terlebih dahulu karena berada melewati batas wilayah analisis, mengikuti filter pada dashboard Streamlit. Pengecualian ini hanya berlaku pada data analisis dan tidak menghapus baris dari CSV sumber; poligon Laut lainnya tetap digunakan.

Piksel non-Laut di luar batas Jawa Timur juga disaring, sama seperti dashboard. Setelah agregasi, titik rata-rata setiap poligon non-Laut diperiksa kembali; poligon yang titiknya berada di luar batas tidak dimasukkan ke pemodelan. Baris yang memiliki nilai tak hingga (`inf` atau `-inf`) diubah menjadi nilai kosong, kemudian baris dengan nilai kosong pada kolom yang digunakan dihapus.

## Agregasi per Poligon

Semua piksel dengan `poligon_id` yang sama diringkas menjadi satu observasi. Nilai fitur serta koordinat (`lon`, `lat`) dihitung menggunakan rata-rata. Label numerik dan label teks diambil dari baris pertama pada setiap poligon.

Agregasi ini mencegah piksel-piksel dari poligon yang sama tersebar ke data latih dan data uji, yang dapat membuat evaluasi terlihat lebih baik daripada kemampuan generalisasi model yang sebenarnya.
Dengan dataset dan batas wilayah proyek saat ini, seluruh penyaringan menghasilkan **278 poligon**. Jumlah tersebut dihitung ulang oleh sel di bawah, bukan ditetapkan secara manual.

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
import json
from pathlib import Path

import numpy as np
import pandas as pd
import shapely
from shapely.geometry import shape
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
boundary_path = dataset_path.with_name("batas_jawa_timur.geojson")
if not boundary_path.is_file():
    raise FileNotFoundError(f"Batas Jawa Timur tidak ditemukan: {boundary_path}")
with boundary_path.open(encoding="utf-8") as file:
    boundary_feature = json.load(file)
if boundary_feature.get("properties", {}).get("adm1_pcode") != "ID35":
    raise ValueError("Berkas geometri bukan batas Provinsi Jawa Timur.")
boundary = shape(boundary_feature["geometry"])
if boundary.is_empty or not boundary.is_valid:
    raise ValueError("Geometri batas Provinsi Jawa Timur tidak valid.")

poligon_laut_dikecualikan = {f"Laut_{index:04d}" for index in range(19)}
baris_dikecualikan = df["poligon_id"].isin(poligon_laut_dikecualikan)
jumlah_dikecualikan = int(baris_dikecualikan.sum())
coordinates = df[["lon", "lat"]].to_numpy(dtype=np.float64)
finite_coordinates = np.isfinite(coordinates).all(axis=1)
inside_boundary = np.zeros(len(df), dtype=bool)
inside_boundary[finite_coordinates] = shapely.contains_xy(
    boundary,
    coordinates[finite_coordinates, 0],
    coordinates[finite_coordinates, 1],
)
keep_laut = df["label_teks"].eq("Laut").to_numpy()
keep_polygon = ~baris_dikecualikan.to_numpy()
df = df.loc[finite_coordinates & keep_polygon & (inside_boundary | keep_laut)].copy()
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
coordinates = poligon[["lon", "lat"]].to_numpy(dtype=np.float64)
finite_coordinates = np.isfinite(coordinates).all(axis=1)
inside_boundary = np.zeros(len(poligon), dtype=bool)
inside_boundary[finite_coordinates] = shapely.contains_xy(
    boundary,
    coordinates[finite_coordinates, 0],
    coordinates[finite_coordinates, 1],
)
keep_laut = poligon["label_teks"].eq("Laut").to_numpy()
poligon = poligon.loc[
    finite_coordinates & (inside_boundary | keep_laut)
].copy()

X = poligon[fitur]
y = poligon["label_teks"]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print(f"Jumlah poligon: {len(poligon):,}")
print(f"Baris piksel Laut dikecualikan: {jumlah_dikecualikan:,}")
print(f"Jumlah data latih: {len(X_train):,}")
print(f"Jumlah data uji: {len(X_test):,}")
```
