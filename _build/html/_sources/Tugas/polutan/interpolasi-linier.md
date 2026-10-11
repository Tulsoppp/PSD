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

# Preprocessing Data Polutan Kertosono dengan Interpolasi Linier

## 1. Data yang digunakan

Analisis ini menggunakan data harian polutan Kecamatan Kertosono, Kabupaten Nganjuk, dari hasil pengolahan data Sentinel-5P. Data CO, NO₂, dan SO₂ tersedia dalam tiga berkas:

- `co.csv`
- `no2.csv`
- `so2.csv`

Setiap berkas memiliki kolom tanggal (`date`), indeks fitur (`feature_index`), dan nilai polutan. Rentang data yang tersedia adalah 30 Agustus 2025 sampai 30 Agustus 2026, sebanyak 366 baris per polutan.

Pemeriksaan berkas menunjukkan bahwa sebagian nilai polutan kosong. Selain itu, beberapa nilai ditandai sebagai outlier dengan metode IQR. Ringkasan kondisi awal:

| Polutan | Jumlah baris | Missing value | Outlier IQR |
|---|---:|---:|---:|
| CO | 366 | 104 | 3 |
| NO₂ | 366 | 136 | 1 |
| SO₂ | 366 | 101 | 13 |

## 2. Deteksi outlier dengan IQR

IQR (*Interquartile Range*) digunakan untuk menandai nilai yang jauh dari sebaran mayoritas data. Perhitungannya menggunakan kuartil pertama (`Q1`) dan kuartil ketiga (`Q3`):

$$
IQR = Q3 - Q1
$$

$$
\text{batas bawah} = Q1 - 1.5 \times IQR
$$

$$
\text{batas atas} = Q3 + 1.5 \times IQR
$$

Nilai di luar batas tersebut ditandai sebagai outlier, kemudian diperlakukan sebagai nilai kosong sebelum interpolasi. Nilai kosong yang memang sudah ada di sumber data juga diisi dalam tahap interpolasi.

Outlier merupakan penanda statistik, bukan bukti bahwa pengukuran pasti salah. Pada analisis ini nilai tersebut diganti agar tidak mendominasi ekstraksi fitur; keputusan tersebut perlu dipertimbangkan kembali jika tersedia informasi validasi lapangan.

## 3. Apa yang dimaksud interpolasi linier?

Interpolasi linier mengisi nilai yang hilang di antara dua titik yang diketahui dengan menghubungkan kedua titik menggunakan garis lurus. Jika nilai pada waktu \(t_0\) adalah \(y_0\), dan nilai pada waktu \(t_1\) adalah \(y_1\), nilai di waktu \(t\) diestimasi dengan:

$$
y(t) = y_0 + \frac{t-t_0}{t_1-t_0}(y_1-y_0)
$$

Metode ini sesuai untuk mengisi celah di dalam deret waktu menggunakan garis lurus di antara titik yang diketahui. Untuk nilai kosong di awal atau akhir deret yang tidak memiliki dua titik pembatas, kode menggunakan nilai terdekat (`bfill`/`ffill`) setelah interpolasi.

## 4. Implementasi pada data polutan

Kode berikut membaca berkas sumber milik proyek, menghitung batas IQR dari nilai yang tersedia, menandai outlier, lalu melakukan interpolasi linier berdasarkan tanggal. Hasil tiap polutan disimpan ke berkas `*_after.csv`, dan hasil gabungannya ke `Polutan_Kertosono.csv`.

Jalankan kode dari direktori notebook `Tugas/polutan`, sehingga jalur `../../` mengarah ke direktori utama proyek.

```python
from pathlib import Path

import pandas as pd

base_dir = Path("../../")
pollutants = {
    "CO": "co.csv",
    "NO2": "no2.csv",
    "SO2": "so2.csv",
}

processed = []

for pollutant, filename in pollutants.items():
    df = pd.read_csv(base_dir / filename)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df[pollutant] = pd.to_numeric(df[pollutant], errors="coerce")
    df = df.dropna(subset=["date"]).sort_values("date")

    if df["date"].duplicated().any():
        raise ValueError(f"Terdapat tanggal duplikat pada {filename}")

    values = df[pollutant]
    valid_values = values.dropna()
    if valid_values.empty:
        raise ValueError(f"Tidak ada nilai valid untuk {pollutant} pada {filename}")

    q1 = valid_values.quantile(0.25)
    q3 = valid_values.quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    outliers = values.notna() & (
        (values < lower_bound) | (values > upper_bound)
    )

    # Simpan tahap penandaan outlier sebagai audit sebelum imputasi.
    df[pollutant] = values.mask(outliers)
    df[["date", pollutant]].to_csv(
        base_dir / f"{pollutant}_Outlier.csv", index=False
    )

    # Interpolasi berbasis waktu untuk celah internal, lalu isi batas deret.
    df = df.set_index("date").sort_index()
    df[pollutant] = (
        df[pollutant]
        .interpolate(method="time", limit_direction="both")
        .bfill()
        .ffill()
    )

    remaining_missing = int(df[pollutant].isna().sum())
    if remaining_missing:
        raise ValueError(
            f"{pollutant} masih memiliki {remaining_missing} nilai kosong "
            "setelah interpolasi. Periksa data sumber."
        )

    result = df[[pollutant]].reset_index()
    result.to_csv(base_dir / f"{pollutant}_after.csv", index=False)
    processed.append(result)
    print(
        f"{pollutant}: {len(result)} baris, "
        f"{int(outliers.sum())} outlier ditandai, "
        f"{remaining_missing} missing value tersisa"
    )

combined = processed[0]
for result in processed[1:]:
    combined = combined.merge(result, on="date", how="outer", validate="one_to_one")

combined = combined.sort_values("date").reset_index(drop=True)
if combined[["CO", "NO2", "SO2"]].isna().any().any():
    raise ValueError("Dataset gabungan masih memiliki nilai kosong.")

combined.to_csv(base_dir / "Polutan_Kertosono.csv", index=False)
print(f"Dataset gabungan tersimpan: {len(combined)} baris")
```

## 5. Validasi hasil

Setelah kode dijalankan, pastikan jumlah baris dan tanggal sesuai, serta tidak ada nilai kosong pada hasil per polutan maupun dataset gabungan. Validasi sederhana:

```python
for pollutant in pollutants:
    result = pd.read_csv(base_dir / f"{pollutant}_after.csv")
    print(
        pollutant,
        "baris =", len(result),
        "missing =", int(result[pollutant].isna().sum()),
    )

combined_check = pd.read_csv(base_dir / "Polutan_Kertosono.csv")
print(
    "Gabungan:",
    len(combined_check),
    "baris; missing =",
    int(combined_check[["CO", "NO2", "SO2"]].isna().sum().sum()),
)
```

Hasil yang diharapkan untuk ketiga berkas adalah 366 baris dan 0 missing value setelah pemrosesan berhasil. Berkas hasil yang sudah ada sebelumnya masih dapat berisi nilai kosong; jalankan ulang kode di atas dari data sumber untuk menghasilkan keluaran yang sudah divalidasi.

## 6. Catatan interpretasi

Interpolasi menghasilkan **perkiraan** pada tanggal yang tidak memiliki pengukuran, bukan pengukuran satelit baru. Semakin panjang celah kosong, semakin besar pula ketidakpastian nilai interpolasinya. Karena itu:

- catat nilai asli, nilai outlier yang ditandai, dan nilai hasil imputasi bila analisis membutuhkan audit;
- gunakan hasil imputasi untuk menjaga kelengkapan deret waktu, bukan sebagai pengganti validasi lapangan;
- pertimbangkan panjang celah dan keterbatasan data Sentinel-5P saat menginterpretasikan tren; dan
- simpan salinan data sumber agar tahapan pembersihan dapat diulang.

## 7. Kesimpulan

Data CO, NO₂, dan SO₂ milik proyek Kertosono masing-masing memiliki 366 baris dengan nilai kosong dan sejumlah outlier. Pada preprocessing versi ini, outlier ditandai menggunakan batas IQR, lalu outlier dan missing value diisi menggunakan interpolasi linier berbasis tanggal. Nilai kosong di bagian ujung deret diisi dengan nilai terdekat.

Hasil tiap polutan disimpan sebagai `CO_after.csv`, `NO2_after.csv`, dan `SO2_after.csv`, sedangkan data gabungannya disimpan sebagai `Polutan_Kertosono.csv`. Sebelum ekstraksi fitur atau analisis lanjutan, jalankan validasi untuk memastikan semua keluaran memiliki jumlah baris yang sesuai dan tidak lagi mengandung missing value.
