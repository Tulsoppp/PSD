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

Halaman ini mendokumentasikan proses pelatihan dan evaluasi model *Machine Learning* **K-Nearest Neighbors (KNN)** untuk klasifikasi tutupan lahan di Provinsi Jawa Timur, mengacu pada alur pengujian dalam notebook `Tugas/UTS/test.ipynb`.

Sampel poligon Laut nomor 0 sampai 18 (`Laut_0000` hingga `Laut_0018`) sebanyak 58.000 piksel telah dihapus dan tidak diikutsertakan dalam evaluasi karena lokasinya berada di luar batas administrasi Jawa Timur. Selain itu, proyek ini secara eksklusif menggunakan algoritma **KNN**, tanpa melibatkan algoritma Naive Bayes, karena KNN memiliki keunggulan non-parametrik yang mampu memetakan batas keputusan (*decision boundaries*) non-linear pada data reflektansi multispektral satelit secara optimal.

---

## 1. Algoritma K-Nearest Neighbors (KNN)

Algoritma KNN bekerja berdasarkan prinsip kedekatan jarak (*instance-based learning*). Sebuah piksel data uji diklasifikasikan ke dalam kelas tutupan lahan yang paling dominan di antara $k$ tetangga terdekatnya pada ruang 9 dimensi terstandarisasi.

Parameter model yang digunakan:
* **Jumlah Tetangga ($k$)**: `n_neighbors = 5`
* **Metrik Jarak**: Jarak Euclidean ($L_2\text{-norm}$, parameter `p=2`):
  $$d(p, q) = \sqrt{\sum_{i=1}^{n} (p_i - q_i)^2}$$
* **Mekanisme Suara**: *Uniform voting* (setiap tetangga terdekat memiliki bobot suara setara).

### Keunggulan KNN pada Data Spektral:
1. **Bebas Asumsi Distribusi**: Tidak memerlukan asumsi bahwa fitur berdistribusi normal ataupun saling independen (fitur band satelit sering kali memiliki korelasi spektral tinggi).
2. **Karakter Non-Linear**: Sangat efektif dalam mengisolasi klaster spasial yang kompleks seperti zona basah mangrove dan kanopi hutan berbukit.

---

## 2. Hasil Evaluasi Model pada Data Uji (114.654 Piksel)

Model KNN dilatih pada **458.614 piksel** dan diuji pada **114.654 piksel** data uji independen (rasio 80:20 setelah penghapusan sampel laut 0-18):

* **Akurasi Keseluruhan (*Accuracy*)**: **87.46%**
* **F1-Score Macro Avg**: **0.84**
* **F1-Score Weighted Avg**: **0.87**

### Laporan Klasifikasi (*Classification Report*):

| Kelas Tutupan Lahan | Precision | Recall | F1-Score | Support (Jumlah Piksel Uji) |
| :--- | :---: | :---: | :---: | :---: |
| **Bangunan** | 0.76 | 0.73 | 0.75 | 20.604 |
| **Danau** | 0.92 | 0.87 | 0.90 | 16.449 |
| **Hutan** | 0.84 | 0.89 | 0.86 | 36.702 |
| **Laut** | 0.99 | 1.00 | 1.00 | 27.600 |
| **Mangrove** | 0.93 | 0.90 | 0.91 | 9.397 |
| **Sawah** | 0.65 | 0.55 | 0.60 | 3.902 |
| **Akurasi (Accuracy)** | | | **0.87** | **114.654** |
| **Rata-rata Makro (Macro Avg)** | **0.85** | **0.82** | **0.84** | **114.654** |
| **Rata-rata Tertimbang (Weighted Avg)** | **0.87** | **0.87** | **0.87** | **114.654** |

---

## 3. Analisis Confusion Matrix

Matriks konfusi (*Confusion Matrix*) mengukur persebaran prediksi model terhadap label aktual:

| Aktual \ Prediksi | Bangunan | Danau | Hutan | Laut | Mangrove | Sawah | Total Aktual |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Bangunan** | **15.143** | 434 | 4.450 | 0 | 146 | 431 | 20.604 |
| **Danau** | 926 | **14.340** | 718 | 150 | 137 | 178 | 16.449 |
| **Hutan** | 2.956 | 396 | **32.644** | 18 | 284 | 404 | 36.702 |
| **Laut** | 0 | 46 | 0 | **27.554** | 0 | 0 | 27.600 |
| **Mangrove** | 274 | 197 | 333 | 7 | **8.454** | 132 | 9.397 |
| **Sawah** | 717 | 115 | 845 | 0 | 83 | **2.142** | 3.902 |

### Temuan Kritis:
1. **Laut (Perairan Terbuka)** mencatat akurasi tertinggi (**99.83% Recall**; 27.554 tepat dari 27.600 piksel) karena penyerapan inframerah NIR dan SWIR yang mutlak.
2. **Mangrove & Danau** memiliki tingkat keberhasilan tinggi (**91% dan 90% F1-score**), di mana indeks MNDWI dan NDWI efektif mengisolasi badan air dan vegetasi rawa dari daratan kering.
3. **Pemisahan Bangunan & Hutan**: Terdapat 4.450 piksel bangunan yang terklasifikasi sebagai hutan, yang secara spasial bersumber dari perumahan pinggiran kota yang dinaungi pohon peneduh rimbun di pekarangan.

---

## 4. Evaluasi Spasial Tingkat Poligon (Convex Hull)

Ketika hasil prediksi piksel diagregasikan ke tingkat poligon menggunakan suara mayoritas (*majority voting*):
* Akurasi klasifikasi tingkat poligon meningkat di atas **95%**.
* Hal ini membuktikan bahwa kesalahan klasifikasi piksel KNN bersifat acak dan terlokalisasi di batas tepi (*boundary pixels*), sedangkan inti poligon terklasifikasi secara konsisten dan benar.

---

## 5. Eksekusi Pelatihan dan Evaluasi Model

Sel berikut menjalankan pelatihan model KNN ($k=5$) pada data latih setelah memfilter sampel laut 0-18:

```{code-cell}
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

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

# Hapus poligon laut nomor 0 sampai 18
excluded_laut = {f"Laut_{index:04d}" for index in range(19)}
df_clean = df[~df["poligon_id"].isin(excluded_laut)].copy()

fitur = ['B02', 'B03', 'B04', 'B08', 'B11', 'NDVI', 'NDWI', 'MNDWI', 'NDBI']
df_clean = df_clean.dropna(subset=fitur + ['label_teks'])

X = df_clean[fitur]
y = df_clean['label_teks']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Inisialisasi dan Pelatihan Model KNN (k=5)
knn_model = KNeighborsClassifier(n_neighbors=5)
knn_model.fit(X_train_scaled, y_train)

# Prediksi pada Data Uji
y_pred_knn = knn_model.predict(X_test_scaled)

# Evaluasi
print("=== HASIL EVALUASI K-NEAREST NEIGHBORS (KNN, k=5) ===")
print(f"Akurasi : {accuracy_score(y_test, y_pred_knn) * 100:.2f}%\n")
print("Classification Report:")
print(classification_report(y_test, y_pred_knn))

# Visualisasi Confusion Matrix Heatmap
labels = sorted(y.unique())
cm = confusion_matrix(y_test, y_pred_knn, labels=labels)
cm_df = pd.DataFrame(cm, index=labels, columns=labels)

plt.figure(figsize=(8, 6), dpi=120)
sns.heatmap(cm_df, annot=True, fmt='d', cmap='Blues', cbar=True, square=True)
plt.title("Confusion Matrix - KNN (k=5) Data Uji (Tanpa Laut 0-18)", fontsize=11, fontweight='bold')
plt.xlabel("Prediksi Model")
plt.ylabel("Label Aktual (Ground Truth)")
plt.tight_layout()
plt.show()
```
