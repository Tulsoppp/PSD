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

# 5. Pemodelan dan Evaluasi

Kedua model dilatih menggunakan sembilan fitur spektral yang telah diagregasi pada tingkat poligon dan distandarkan. Evaluasi dilakukan terhadap 90 poligon pada data uji. Setiap kelas memiliki 15 sampel uji pada hasil notebook.

## Gaussian Naive Bayes

Model dibuat menggunakan `GaussianNB`. Algoritma ini menerapkan Teorema Bayes dan memodelkan distribusi fitur tiap kelas sebagai distribusi Gaussian. Prediksi pada data uji dibandingkan dengan label sebenarnya menggunakan akurasi dan *classification report*.

Output akurasi dan laporan klasifikasi lengkap akan muncul dari sel pemodelan di bagian akhir halaman.

## K-Nearest Neighbors

Model KNN menggunakan `KNeighborsClassifier` dengan `n_neighbors=5`. Kelas suatu observasi ditentukan dari kelas mayoritas di antara lima tetangga terdekat pada ruang fitur yang telah distandarkan.

Output akurasi dan laporan klasifikasi lengkap akan muncul dari sel pemodelan di bagian akhir halaman.

## Perbandingan

Pada output notebook yang tersimpan sebelumnya, KNN memperoleh akurasi lebih tinggi daripada Gaussian Naive Bayes. Namun, hasil per kelas tetap penting: *recall* kelas Sawah pada KNN relatif rendah. Sel pemodelan di bawah menghitung ulang semua metrik langsung dari dataset yang dibaca saat eksekusi.

Nilai tersebut merupakan hasil satu pembagian data dengan `random_state=42`. Pengujian dengan validasi silang atau sampel tambahan dapat memberikan gambaran kestabilan kinerja yang lebih luas.

## Menjalankan Pemodelan

Sel berikut menyiapkan data dengan proses yang sama pada bagian preprocessing, melatih kedua model, lalu menampilkan akurasi dan *classification report* setiap model. Dengan demikian, metrik di halaman ini dihitung ulang dari CSV ketika sel dijalankan.

```{code-cell}
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
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

X_train, X_test, y_train, y_test = train_test_split(
    poligon[fitur],
    poligon["label_teks"],
    test_size=0.3,
    random_state=42,
    stratify=poligon["label_teks"],
)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

models = {
    "Gaussian Naive Bayes": GaussianNB(),
    "K-Nearest Neighbors (k=5)": KNeighborsClassifier(n_neighbors=5),
}
for nama, model in models.items():
    model.fit(X_train_scaled, y_train)
    prediksi = model.predict(X_test_scaled)
    print(f"=== {nama} ===")
    print(f"Akurasi: {accuracy_score(y_test, prediksi) * 100:.2f}%")
    print(classification_report(y_test, prediksi, zero_division=0))
```
