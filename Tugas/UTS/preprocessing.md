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

Tahap pra-pemrosesan data (*Data Preprocessing*) bertujuan untuk mempersiapkan data masukan agar siap dan optimal saat diproses oleh algoritma **K-Nearest Neighbors (KNN)**, mengacu pada alur eksperimen `Tugas/UTS/test.ipynb`.

Tahapan preprocessing meliputi:
1. **Pengecualian Poligon di Luar Batas (Laut 0-18)**
2. **Seleksi Fitur (X) dan Target (y)**
3. **Pembersihan Data (*Data Cleaning*)**
4. **Pemisahan Data (*Stratified Train-Test Split* 80:20)**
5. **Standarisasi Skala Fitur (*StandardScaler*)**

---

## 1. Pengecualian Sampel Laut di Luar Batas Wilayah

Sampel poligon Laut nomor 0 sampai 18 (`Laut_0000` hingga `Laut_0018`) sebanyak 58.000 piksel dihapus dan tidak digunakan karena lokasinya berada melewati batas administrasi Provinsi Jawa Timur. Dengan demikian, data yang diproses murni berasal dari teritorial Jawa Timur.

---

## 2. Seleksi Fitur dan Target

Fitur masukan yang digunakan mencakup 5 band spektral asli Sentinel-2A dan 4 indeks spektral turunan:

$$\text{Fitur } (X) = [\text{B02}, \text{B03}, \text{B04}, \text{B08}, \text{B11}, \text{NDVI}, \text{NDWI}, \text{MNDWI}, \text{NDBI}]$$

Variabel target yang akan diprediksi adalah kolom kategori tutupan lahan:

$$\text{Target } (y) = \text{label\_teks}$$

Nilai kosong (*missing values*) atau nilai tak hingga (*infinite values*) dibersihkan untuk memastikan kualitas data masukan:

```python
fitur = ['B02', 'B03', 'B04', 'B08', 'B11', 'NDVI', 'NDWI', 'MNDWI', 'NDBI']
df_bersih = df.dropna(subset=fitur + ['label_teks']).copy()

X = df_bersih[fitur]
y = df_bersih['label_teks']
```

---

## 3. Pembagian Data (Stratified Train-Test Split 80:20)

Dataset dibagi menggunakan skema *Stratified Train-Test Split* dengan proporsi **80% data latih** dan **20% data uji**:
* **Data Latih (*Training Set*)**: **458.614 piksel** (digunakan untuk mempelajari ruang fitur dan tetangga terdekat)
* **Data Uji (*Testing Set*)**: **114.654 piksel** (digunakan untuk pengujian independen performa model)

Parameter `random_state=42` ditetapkan agar pembagian data dapat direproduksi secara konsisten (*reproducible*), dan `stratify=y` memastikan rasio proporsi keenam kelas tutupan lahan tetap seimbang di kedua himpunan data.

---

## 4. Standarisasi Fitur (StandardScaler)

Algoritma KNN menentukan kelas berdasarkan perhitungan jarak Euclidean ($L_2\text{-norm}$) di ruang fitur multidimensi. Karena nilai band spektral mentah Sentinel-2A memiliki rentang nilai besar ($0 - 10.000$), sedangkan indeks spektral turunan bernilai kecil (rentang $-1.0$ hingga $+1.0$), fitur berdimensi besar akan mendominasi perhitungan jarak jika tidak distandarkan.

Oleh karena itu, seluruh fitur ditransformasikan menggunakan `StandardScaler`:
$$z = \frac{x - \mu}{\sigma}$$

di mana $\mu$ adalah nilai rata-rata (*mean*) dan $\sigma$ adalah standar deviasi fitur pada data latih. Objek `StandardScaler` hanya di-*fit* pada data latih (`X_train`), kemudian digunakan untuk mentransformasikan data latih dan data uji (`X_test`) agar tidak terjadi kebocoran informasi (*data leakage*).

---

## Eksekusi Kode Preprocessing

Sel berikut menjalankan seluruh alur preprocessing dari berkas `piksel_s2_JTM.csv` dengan memfilter poligon laut 0-18:

```{code-cell}
from pathlib import Path
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

# 1. Hapus sampel laut nomor 0 sampai 18
excluded_laut = {f"Laut_{index:04d}" for index in range(19)}
df_clean = df[~df["poligon_id"].isin(excluded_laut)].copy()

# 2. Menentukan Fitur (X) dan Target (y)
fitur = ['B02', 'B03', 'B04', 'B08', 'B11', 'NDVI', 'NDWI', 'MNDWI', 'NDBI']
df_clean = df_clean.dropna(subset=fitur + ['label_teks'])

X = df_clean[fitur]
y = df_clean['label_teks']

# 3. Pembagian Data Latih dan Uji (80:20 Stratified)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"Jumlah Total Piksel Valid: {len(df_clean):,}")
print(f"Jumlah Data Latih (80%)  : {X_train.shape[0]:,}")
print(f"Jumlah Data Uji (20%)    : {X_test.shape[0]:,}")

# 4. Standarisasi Fitur
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print("\nBentuk matriks fitur terstandarisasi:")
print(f"X_train_scaled: {X_train_scaled.shape}")
print(f"X_test_scaled : {X_test_scaled.shape}")
```
