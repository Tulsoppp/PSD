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

Informasi penggunaan dan tutupan lahan (*Land Use / Land Cover* atau LULC) berguna untuk analisis ruang, pengelolaan lingkungan, dan perencanaan wilayah. Interpretasi citra satelit secara manual membutuhkan waktu, terutama ketika data terdiri atas banyak piksel dan beberapa kelas tutupan lahan.

Proyek ini menggunakan data citra Sentinel-2A yang telah diekstraksi menjadi nilai spektral dan indeks turunannya. Nilai-nilai tersebut digunakan oleh model *machine learning* untuk membantu mengklasifikasikan tutupan lahan.

## Tujuan

1. Menyusun model klasifikasi tutupan lahan dari fitur spektral Sentinel-2A.
2. Membandingkan kinerja Gaussian Naive Bayes dan *K-Nearest Neighbors* (KNN).
3. Mengevaluasi hasil model menggunakan data uji dan metrik klasifikasi.
4. Menampilkan sebaran sampel tutupan lahan pada peta interaktif.

## Kelas dan Ruang Lingkup

Analisis mempertahankan enam kelas tutupan lahan. Untuk menyamakan cakupan dengan dashboard Streamlit, poligon Laut `Laut_0000` sampai `Laut_0018` dikecualikan karena berada melewati batas wilayah analisis. Baris tersebut hanya dikeluarkan dari data analisis; berkas CSV sumber tidak diubah. Kode berikut menerapkan pengecualian sebelum menampilkan kelas yang tersedia.

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
poligon_laut_dikecualikan = {f"Laut_{index:04d}" for index in range(19)}
baris_dikecualikan = df["poligon_id"].isin(poligon_laut_dikecualikan)
print(f"Baris piksel yang dikecualikan: {baris_dikecualikan.sum():,}")
df = df.loc[~baris_dikecualikan].copy()
print(f"Dataset: {dataset_path}")
print(f"Jumlah kelas: {df['label_teks'].nunique()}")
print("Kelas:", ", ".join(sorted(df["label_teks"].dropna().unique())))
```

Analisis menggunakan satu baris agregat untuk setiap poligon sampel agar piksel dari poligon yang sama tidak tersebar sekaligus ke data latih dan data uji. Sampel Laut lain tetap digunakan; yang dikecualikan hanya poligon yang disebutkan di atas.

Peta pada notebook digunakan untuk menampilkan lokasi sampel dan labelnya. Peta tersebut bukan peta prediksi penuh untuk seluruh piksel citra.

## Pertanyaan Analisis

- Seberapa baik fitur spektral dan indeks turunan membedakan kelas tutupan lahan?
- Bagaimana perbandingan kinerja Gaussian Naive Bayes dan KNN pada data uji?
- Di kelas mana model masih sering melakukan kesalahan klasifikasi?
