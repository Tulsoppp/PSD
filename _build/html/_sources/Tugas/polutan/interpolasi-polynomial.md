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

# Preprocessing Data Polutan Kertosono dengan Interpolasi Polinomial

## 1. Kondisi data awal

Dataset yang digunakan pada proyek ini adalah data deret waktu konsentrasi polutan wilayah Kecamatan Kertosono, Kabupaten Nganjuk, yang berasal dari hasil agregasi data Sentinel-5P. Data disimpan dalam tiga file utama, yaitu `co.csv`, `no2.csv`, dan `so2.csv`. Masing-masing file berisi kolom `date`, `feature_index`, dan variabel polutan utama.

Pada tahap awal, data belum sepenuhnya bersih. Ada beberapa masalah kualitas data yang umum terjadi pada time series satelit, yaitu:

- nilai `NaN` akibat data tidak terukur atau tidak berhasil diproses;
- nilai ekstrem yang kemungkinan merupakan outlier;
- perubahan tren yang terpotong karena hilangnya nilai pada beberapa tanggal.

Dengan demikian, tahap preprocessing menjadi sangat penting sebelum data masuk ke proses ekstraksi fitur.

## 2. Statistik awal dataset

Berdasarkan dataset yang saya miliki, jumlah data harian yang digunakan adalah 366 hari. Kondisi data sebelum preprocessing dapat dirangkum sebagai berikut:

| Polutan | Jumlah data | Missing value | Outlier IQR |
| ------- | ----------: | ------------: | ----------: |
| CO      |         366 |           104 |           3 |
| NO2     |         366 |           136 |           1 |
| SO2     |         366 |           101 |          13 |

Dari tabel tersebut terlihat bahwa semua polutan memiliki banyak nilai yang hilang dan beberapa titik ekstrem. Ini menandakan bahwa dataset perlu dibersihkan sebelum digunakan untuk ekstraksi fitur dan analisis lanjutan.

## 3. Mengapa metode IQR dipakai?

Metode IQR (Interquartile Range) digunakan untuk menentukan batas normal data dengan cara membandingkan distribusi data dengan kuartil. Rumus dasarnya adalah:

$$
Q1 = \text{kuartil ke-1}, \quad Q3 = \text{kuartil ke-3}
$$

$$
IQR = Q3 - Q1
$$

$$
\text{batas bawah} = Q1 - 1.5 \times IQR
$$

$$
\text{batas atas} = Q3 + 1.5 \times IQR
$$

Semua nilai yang lebih kecil dari batas bawah atau lebih besar dari batas atas dianggap sebagai outlier. Metode ini sangat cocok untuk data time series karena dapat menahan pengaruh nilai ekstrem tanpa menghapus seluruh tren harian.

Pada dataset Kertosono, nilai ambang yang didapatkan adalah:

| Polutan |        Q1 |       Q3 |      IQR | Lower bound | Upper bound | Outlier |
| ------- | --------: | -------: | -------: | ----------: | ----------: | ------: |
| CO      |   0.02773 |  0.03327 |  0.00554 |     0.01942 |     0.04158 |       3 |
| NO2     |  2.43e-05 | 3.74e-05 | 1.31e-05 |    4.65e-06 |    5.70e-05 |       1 |
| SO2     | -1.38e-05 | 1.99e-04 | 2.13e-04 |   -3.33e-04 |    5.19e-04 |      13 |

Nilai SO2 memiliki Q1 yang negatif karena pada data mentah ada beberapa pengamatan yang sangat kecil bahkan bernilai negatif. Hal ini bisa disebabkan oleh noise sensor atau hasil ekstraksi satelit yang belum dibersihkan. Karena itu, proses interpola dan outlier cleaning sangat penting agar seri waktu tetap stabil.

## 4. Implementasi deteksi outlier pada dataset nyata

Kode berikut adalah bentuk implementasi yang saya gunakan untuk mengolah dataset Kertosono dengan pendekatan IQR. Saya langsung membaca dataset `co.csv`, `no2.csv`, dan `so2.csv` yang ada di folder kerja.

```python
import pandas as pd

for pollutant in ['CO', 'NO2', 'SO2']:
    df = pd.read_csv(f'../../{pollutant.lower()}.csv')
    s = pd.to_numeric(df[pollutant], errors='coerce')

    q1 = s.quantile(0.25)
    q3 = s.quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    outliers = (s < lower_bound) | (s > upper_bound)
    print(pollutant, 'missing=', int(s.isna().sum()), 'outlier=', int(outliers.sum()))
```

Hasil eksekusi tersebut menunjukkan bahwa:

- CO memiliki 104 missing value dan 3 outlier;
- NO2 memiliki 136 missing value dan 1 outlier;
- SO2 memiliki 101 missing value dan 13 outlier.

Hal ini merupakan bukti bahwa dataset asli belum siap langsung dipakai untuk analisis fitur, karena variasi data sangat dipengaruhi oleh nilai yang hilang dan titik ekstrem.

## 5. Proses interpolasi polinomial

Setelah outlier terdeteksi, langkah selanjutnya adalah mengubah nilai ekstrem tersebut menjadi `NaN` dan mengisinya kembali dengan interpolasi polinomial. Saya menggunakan pendekatan `interpolate(method='polynomial', order=1)` yang secara numerik bekerja seperti garis lurus yang menghubungkan dua titik data di sekitar celah tersebut.

Tujuan utama dari langkah ini adalah agar perubahan data tetap halus dan tidak terlalu memotong tren temporal. Saya juga menambahkan `bfill()` dan `ffill()` agar nilai yang berada di bagian awal atau akhir seri dapat diisi dengan data yang paling dekat, sehingga tidak ada nilai kosong yang tertinggal.

```python
import pandas as pd
import numpy as np

for pollutant in ['CO', 'NO2', 'SO2']:
    df = pd.read_csv(f'../../{pollutant.lower()}.csv')
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)
    df[pollutant] = pd.to_numeric(df[pollutant], errors='coerce')

    while True:
        q1 = df[pollutant].quantile(0.25)
        q3 = df[pollutant].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        outliers = (df[pollutant] < lower_bound) | (df[pollutant] > upper_bound)
        if not outliers.any():
            break

        df[pollutant] = df[pollutant].mask(outliers)
        df[pollutant] = df[pollutant].interpolate(method='polynomial', order=1).bfill().ffill()

    df[[ 'date', pollutant ]].to_csv(f'../../{pollutant}_after.csv', index=False)
    print(f'{pollutant} preprocessing selesai')
```

## 6. Hasil preprocessing yang diperoleh

Setelah proses di atas, data yang sudah dibersihkan kemudian disimpan dalam file berikut:

- `CO_after.csv`
- `NO2_after.csv`
- `SO2_after.csv`

Hasil validasi menunjukkan bahwa data telah menjadi lebih stabil dan konsisten. Meskipun sebagian nilai di bagian awal seri tetap menggunakan metode `bfill/ffill` karena tidak ada titik sebelumnya, secara umum pola tren dari setiap polutan menjadi lebih halus dan lebih cocok untuk proses ekstraksi fitur.

Selain itu, data gabungan akhir disimpan dalam `Polutan_Kertosono.csv` dengan kolom berikut:

```python
date, CO, NO2, SO2
```

File ini berisi 366 baris data dengan tanggal yang terurut dari 30 Agustus 2025 sampai 30 Agustus 2026. Tanggal ini menjadi dasar untuk membangun input time series sebelum dilanjutkan ke tahap feature extraction.

## 7. Interpretasi hasil dari dataset saya

Berdasarkan hasil data Kertosono, beberapa hal penting dapat diambil:

1. CO cenderung memiliki pola yang relatif stabil, tetapi masih terdapat 3 nilai ekstrem dan 104 nilai yang hilang. Hal ini membuat data perlu dibersihkan sebelum dibuat model.
2. NO2 memiliki jumlah outlier paling sedikit, yaitu 1, tetapi jumlah missing value cukup besar, yaitu 136. Ini menunjukkan bahwa keberadaan nilai kosong menjadi masalah utama pada NO2.
3. SO2 merupakan polutan yang paling fluktuatif. Ia memiliki 13 outlier, yang paling tinggi di antara ketiga polutan, dan juga memiliki 101 missing value. Ini menandakan bahwa SO2 sangat sensitif terhadap noise data satelit.

Dengan demikian, interpolasi polinomial bukan hanya sekadar teknik pengisian, tetapi juga menjadi langkah penting untuk menjaga kontinuitas tren temporal dan memastikan fitur yang diekstraksi tidak terdistorsi oleh nilai yang tidak representatif.

## 8. Kesimpulan

Tahap preprocessing menggunakan IQR dan interpolasi polinomial sangat diperlukan untuk data polutan Kertosono. Dataset asli yang saya miliki memiliki banyak missing value dan outlier, sehingga jika langsung digunakan maka hasil ekstraksi fitur bisa menghasilkan representasi yang tidak akurat.

Metode ini membuat data menjadi lebih rapi, lebih konsisten, dan lebih siap diproses untuk tahap berikutnya, yaitu ekstraksi fitur statistik, temporal, spektral, dan fraktal. Dengan hasil yang telah saya gunakan dari dataset nyata, proses analisis menjadi lebih sesuai dengan karakteristik data yang sebenarnya.

---

Catatan: file hasil preprocessing yang telah dibentuk dalam proyek ini adalah dataset bersih per polutan (`CO_after.csv`, `NO2_after.csv`, `SO2_after.csv`) serta file gabungan utama (`Polutan_Kertosono.csv`). Data ini kemudian menjadi dasar untuk tahap feature extraction dan pemodelan selanjutnya.
