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

# Preprocessing dan Ekstraksi Fitur

## Preprocessing: Penanganan Outliers dan Interpolasi

Pada tahap _Data Understanding_, data hasil crawling Sentinel-5P untuk Kecamatan Bandarkedungmulyo memiliki beberapa _missing values_. Data tersebut diperoleh melalui `openEO` dari koleksi `SENTINEL_5P_L2`, kemudian diringkas menggunakan rata-rata harian dan rata-rata spasial pada area penelitian. File yang digunakan dalam tahap ini adalah `NO2_Bandarkedungmulyo_timeseries.csv`.

Data NO2 memiliki 365 baris dengan periode `2025-08-31` sampai `2026-08-30`. Dari 365 baris tersebut, 182 nilai tersedia dan 183 nilai merupakan missing value. Agar data dapat digunakan untuk ekstraksi fitur secara berkesinambungan, outlier dideteksi menggunakan metode Rentang Interkuartil (IQR), kemudian missing value dan outlier diisi menggunakan interpolasi linier.

### Sumber Data dan Crawling Sentinel-5P

Data polutan diambil dari Copernicus Data Space menggunakan pustaka `openeo`. Proses autentikasi dilakukan melalui akun Copernicus:

```python
import openeo

connection = openeo.connect(
    "openeo.dataspace.copernicus.eu"
).authenticate_oidc()
```

Area penelitian Kecamatan Bandarkedungmulyo dinyatakan sebagai poligon GeoJSON. Koordinat menggunakan urutan `[longitude, latitude]`:

```python
aoi = {
    "type": "Polygon",
    "coordinates": [[
        [112.1100469, -7.6193825],
        [112.1674055997562, -7.6193825],
        [112.1674055997562, -7.533958294404002],
        [112.1100469, -7.533958294404002],
        [112.1100469, -7.6193825]
    ]]
}
```

Crawling menggunakan koleksi `SENTINEL_5P_L2` pada rentang waktu `2025-09-01` sampai `2026-09-01`. Nilai `bands` diganti sesuai polutan yang ingin diambil, yaitu `CO`, `NO2`, atau `SO2`. `aggregate_temporal_period` digunakan untuk memperoleh rata-rata harian, sedangkan `aggregate_spatial` digunakan untuk menghitung rata-rata piksel di dalam AOI.

Contoh pengambilan data NO2 dari `test.ipynb`:

```python
s5post = connection.load_collection(
    "SENTINEL_5P_L2",
    temporal_extent=["2025-09-01", "2026-09-01"],
    spatial_extent={
        "west": 112.1100469,
        "south": -7.6193825,
        "east": 112.1674055997562,
        "north": -7.533958294404002
    },
    bands=["NO2"],
)

# Agregasi temporal menjadi satu nilai per hari
s5p_no2_daily = s5post.aggregate_temporal_period(
    reducer="mean", period="day"
)

# Agregasi spasial menjadi satu nilai rata-rata untuk AOI
s5p_no2_aoi = s5p_no2_daily.aggregate_spatial(
    reducer="mean", geometries=aoi
)

result = s5p_no2_aoi.save_result(format="CSV")
job = result.create_job(title="s5p_no2_timeseries")
job.start_and_wait()
job.get_results().download_files("output_no2")
```

Proses yang sama dilakukan untuk CO dan SO2 dengan mengganti `bands`, judul job, dan folder keluaran. Hasil crawling kemudian dinormalisasi menggunakan Pandas:

```python
import pandas as pd

df_no2 = pd.read_csv("output_no2/timeseries.csv", sep=",")
df_no2 = df_no2[["date", "NO2"]].copy()
df_no2["date"] = pd.to_datetime(df_no2["date"], errors="coerce")
df_no2["NO2"] = pd.to_numeric(df_no2["NO2"], errors="coerce")
df_no2["date"] = df_no2["date"].dt.strftime("%Y-%m-%d")

df_no2.to_csv(
    "NO2_Bandarkedungmulyo_timeseries.csv",
    index=False,
)
```

Hasil crawling yang tersedia adalah `CO_Bandarkedungmulyo_timeseries.csv`, `NO2_Bandarkedungmulyo_timeseries.csv`, dan `SO2_Bandarkedungmulyo_timeseries.csv`. Ketiganya memiliki 365 tanggal. Missing value pada masing-masing file adalah 127 untuk CO, 183 untuk NO2, dan 134 untuk SO2. Missing value tersebut dipertahankan pada file hasil crawling karena menunjukkan tidak tersedianya observasi valid pada tanggal tertentu.

### Deteksi dan Visualisasi Outlier (Metode IQR)

Outlier atau pencilan adalah observasi yang nilainya cukup jauh dari pola umum data. Dalam data kualitas udara, outlier dapat menunjukkan lonjakan polusi yang benar-benar terjadi, misalnya akibat pembakaran, aktivitas kendaraan, atau kondisi atmosfer tertentu. Namun, outlier juga dapat muncul karena gangguan sensor, kesalahan pencatatan, atau kualitas hasil pengamatan satelit. Oleh sebab itu, outlier tidak langsung dihapus. Nilainya terlebih dahulu ditandai agar dapat diperiksa dan ditangani pada tahap berikutnya.

Pada analisis ini, outlier dideteksi menggunakan metode _Interquartile Range_ (IQR). Metode ini membandingkan nilai data dengan bagian tengah distribusi, sehingga tidak terlalu dipengaruhi oleh nilai ekstrem. Perhitungannya dilakukan melalui beberapa tahap berikut:

1. **Q1 (kuartil pertama)** adalah nilai yang membatasi 25% data terendah.
2. **Q3 (kuartil ketiga)** adalah nilai yang membatasi 75% data terendah, atau dengan kata lain awal dari 25% data tertinggi.
3. **IQR** adalah jarak antara Q1 dan Q3, dengan rumus `IQR = Q3 - Q1`. Rentang ini mencakup bagian tengah 50% data.
4. **Batas bawah** dihitung menggunakan rumus `Q1 - 1.5 * IQR`.
5. **Batas atas** dihitung menggunakan rumus `Q3 + 1.5 * IQR`.

Suatu nilai NO2 diklasifikasikan sebagai outlier apabila nilainya lebih kecil dari batas bawah atau lebih besar dari batas atas. Faktor `1.5` merupakan aturan umum dalam boxplot dan metode IQR. Jadi, kode tidak menentukan outlier hanya berdasarkan apakah nilai tersebut terlihat besar, tetapi berdasarkan perbandingan nilai tersebut terhadap distribusi keseluruhan data NO2.

```{code-cell}
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv("../../NO2_Bandarkedungmulyo_timeseries.csv")
df["date"] = pd.to_datetime(df["date"])
df["NO2"] = pd.to_numeric(df["NO2"], errors="coerce")
df = df.sort_values("date").reset_index(drop=True)

# Hitung IQR dari nilai NO2 yang tersedia
Q1 = df["NO2"].quantile(0.25)
Q3 = df["NO2"].quantile(0.75)
IQR = Q3 - Q1

lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

# Filter outlier
outliers_iqr = df[
    (df["NO2"] < lower_bound)
    | (df["NO2"] > upper_bound)
]

print("Jumlah Outlier (IQR):", len(outliers_iqr))
print(outliers_iqr[["date", "NO2"]].head())
```

Pada data NO2 Bandarkedungmulyo diperoleh `Q1 = 0.0000248372`, `Q3 = 0.0000420177`, dan `IQR = 0.0000171805`. Artinya, 50% data yang berada di bagian tengah terletak antara `0.0000248372` dan `0.0000420177`. Berdasarkan nilai tersebut, batas outlier dihitung sebagai berikut:

```text
Batas bawah = Q1 - 1.5 * IQR
             = 0.0000248372 - 1.5 * 0.0000171805
             = -0.0000009336

Batas atas  = Q3 + 1.5 * IQR
             = 0.0000420177 + 1.5 * 0.0000171805
             = 0.0000677884
```

Batas bawah bernilai negatif, sedangkan konsentrasi NO2 pada data ini tidak ada yang lebih kecil dari batas tersebut. Karena itu, tidak ada outlier pada sisi bawah. Sebaliknya, terdapat dua nilai yang lebih besar daripada batas atas `0.0000677884`, yaitu:

| Tanggal    | Nilai NO2 |
| ---------- | --------: |
| 2025-10-02 |  0.000072 |
| 2025-10-15 |  0.000069 |

Dengan demikian, jumlah outlier adalah **2**, karena hanya dua baris tersebut yang memenuhi kondisi:

```python
(df["NO2"] < lower_bound) | (df["NO2"] > upper_bound)
```

Penting untuk membedakan outlier dengan _missing value_. Missing value adalah data yang tidak tersedia dan direpresentasikan sebagai `NaN`, sedangkan outlier adalah data yang tersedia tetapi nilainya berada di luar batas distribusi. Nilai `NaN` tidak memenuhi kondisi lebih kecil atau lebih besar dari batas IQR, sehingga tidak ikut dihitung oleh `outliers_iqr`. Pada dataset ini terdapat 183 missing value dan 2 outlier. Jika kedua outlier kemudian diubah menjadi `NaN`, jumlah nilai kosong yang perlu diisi menjadi 185, yaitu `183 + 2`.

Hasil outlier teman yang berjumlah **0** dapat terjadi apabila dataset yang digunakan berbeda, kolom yang dianalisis berbeda, periode datanya berbeda, atau data sudah dibersihkan maupun diinterpolasi terlebih dahulu. Nilai Q1, Q3, IQR, serta batas bawah dan batas atas akan berubah mengikuti data yang digunakan. Jika tidak ada nilai yang lebih kecil dari batas bawah atau lebih besar dari batas atas, maka `len(outliers_iqr)` memang menghasilkan 0. Jadi, perbedaan antara hasil 2 dan 0 belum tentu menunjukkan kesalahan kode; perbedaan tersebut harus ditelusuri dengan membandingkan file input, jumlah data valid, dan nilai batas IQR.

Untuk memastikan perbandingan dilakukan pada dasar yang sama, informasi berikut dapat dicetak pada kedua program:

```python
print("Jumlah baris:", len(df))
print("Jumlah data NO2 yang tersedia:", df["NO2"].notna().sum())
print("Q1:", Q1)
print("Q3:", Q3)
print("IQR:", IQR)
print("Batas bawah:", lower_bound)
print("Batas atas:", upper_bound)
print(outliers_iqr[["date", "NO2"]])
```

Jika semua nilai tersebut sama, hasil jumlah outlier seharusnya juga sama. Jika hasilnya berbeda, penyebabnya biasanya terletak pada file atau tahap preprocessing yang digunakan sebelum perhitungan IQR.

Visualisasi batas ambang IQR terhadap distribusi data:

```{code-cell}
plt.figure(figsize=(15, 5))
plt.plot(df["date"], df["NO2"], label="NO2", linewidth=1)

plt.scatter(
    outliers_iqr["date"],
    outliers_iqr["NO2"],
    color="red",
    marker="o",
    label="Outliers",
)

plt.axhline(
    upper_bound,
    color="orange",
    linestyle="dashed",
    label="Upper Bound (IQR)",
)
plt.axhline(
    lower_bound,
    color="blue",
    linestyle="dashed",
    label="Lower Bound (IQR)",
)

plt.title("Deteksi Outlier Data NO2 Bandarkedungmulyo")
plt.xlabel("Tanggal")
plt.ylabel("Kadar NO2")
plt.legend()
plt.tight_layout()
plt.xticks(
    ticks=[df["date"].iloc[0], df["date"].iloc[-1]],
    labels=[
        df["date"].iloc[0].strftime("%Y-%m-%d"),
        df["date"].iloc[-1].strftime("%Y-%m-%d"),
    ],
)
plt.show()
```

### Penanganan Outlier dan Interpolasi Data

Setelah outlier ditemukan, nilai tersebut ditandai sebagai nilai kosong (`NaN`). Missing value yang berasal dari hasil crawling tetap kosong. Selanjutnya, interpolasi linier digunakan untuk mengisi nilai kosong berdasarkan nilai sebelum dan sesudahnya. `bfill()` dan `ffill()` digunakan sebagai pelengkap untuk nilai kosong pada bagian awal atau akhir data.

```{code-cell}
# Tandai outlier menjadi NaN
outlier_mask = (
    (df["NO2"] < lower_bound)
    | (df["NO2"] > upper_bound)
)
df["NO2_cleaned"] = df["NO2"].mask(outlier_mask)

# Interpolasi linier berdasarkan urutan data
# Data sudah diurutkan berdasarkan tanggal
df["NO2_filled"] = df["NO2_cleaned"].interpolate(method="linear")
df["NO2_filled"] = df["NO2_filled"].bfill().ffill()

print("Missing sebelum interpolasi:", df["NO2_cleaned"].isna().sum())
print("Missing setelah interpolasi:", df["NO2_filled"].isna().sum())
```

Jumlah nilai yang diproses adalah 185, yaitu 183 missing value awal ditambah 2 outlier. Setelah interpolasi dan pengisian pada bagian tepi, jumlah missing value menjadi 0. Jumlah baris tetap 365 karena tidak ada baris yang dihapus.

Data hasil preprocessing disimpan sebagai `NO2_Bandarkedungmulyo_timeseries_final.csv`:

```python
from pathlib import Path

df_no2_hasil = df[["date", "NO2_filled"]].copy()
df_no2_hasil = df_no2_hasil.rename(columns={"NO2_filled": "NO2"})
df_no2_hasil = df_no2_hasil.sort_values("date").reset_index(drop=True)

output_hasil = Path("../../NO2_Bandarkedungmulyo_timeseries_final.csv")
df_no2_hasil.to_csv(output_hasil, index=False)

print("File data berhasil disimpan:", output_hasil)
print("Jumlah baris:", len(df_no2_hasil))
print("Jumlah missing NO2:", df_no2_hasil["NO2"].isna().sum())
```

Grafik setelah penanganan outlier dan interpolasi:

```{code-cell}
plt.figure(figsize=(15, 5))
plt.plot(
    df["date"],
    df["NO2_filled"],
    label="NO2 setelah interpolasi",
    linewidth=1,
)
plt.title("Data NO2 Setelah Penanganan Outlier dan Interpolasi")
plt.xlabel("Tanggal")
plt.ylabel("Kadar NO2")
plt.legend()
plt.tight_layout()
plt.show()
```

## Ekstraksi Fitur Deret Waktu (Time Series)

Dengan data NO2 yang sudah lengkap, tanpa missing value, dan telah diproses dari outlier, proses dilanjutkan ke ekstraksi fitur. Pustaka yang digunakan adalah `tsfel` (_Time Series Feature Extraction Library_). TSFEL menghitung karakteristik sinyal dari beberapa sudut pandang, seperti statistik, urutan waktu, frekuensi, wavelet, dan kompleksitas fraktal.

Kode berikut mengekstraksi 68 fitur pada data NO2 Bandarkedungmulyo:

```python
import pandas as pd
import numpy as np
import inspect
import tsfel.feature_extraction.features as tsfel_features

# ---------- 1. Muat data yang sudah dibersihkan ----------
df = pd.read_csv("../../NO2_Bandarkedungmulyo_timeseries_final.csv")
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date").reset_index(drop=True)

target_pollutant = "NO2"
df[target_pollutant] = pd.to_numeric(
    df[target_pollutant],
    errors="coerce",
)

# Pemeriksaan terakhir apabila masih ada nilai kosong
df_clean = (
    df.set_index("date")
    .interpolate(method="time")
    .ffill()
    .bfill()
)

fs = 1
signal_1d = df_clean[target_pollutant].astype(float).values

# ---------- 2. Daftar 68 fitur TSFEL ----------
FEATURE_LIST = """abs_energy auc autocorr average_power calc_centroid calc_max calc_mean
calc_median calc_min calc_std calc_var dfa distance ecdf ecdf_percentile ecdf_percentile_count
ecdf_slope entropy fundamental_frequency higuchi_fractal_dimension hist_mode human_range_energy
hurst_exponent interq_range kurtosis lempel_ziv lpcc max_frequency max_power_spectrum
maximum_fractal_length mean_abs_deviation mean_abs_diff mean_diff median_abs_deviation
median_abs_diff median_diff median_frequency mfcc mse negative_turning neighbourhood_peaks
petrosian_fractal_dimension pk_pk_distance positive_turning power_bandwidth rms skewness slope
spectral_centroid spectral_decrease spectral_distance spectral_entropy spectral_kurtosis
spectral_positive_turning spectral_roll_off spectral_roll_on spectral_skewness spectral_slope
spectral_spread spectral_variation spectrogram_mean_coeff sum_abs_diff wavelet_abs_mean
wavelet_energy wavelet_entropy wavelet_std wavelet_var zero_cross""".split()

print("Jumlah fitur yang diminta:", len(FEATURE_LIST))

# ---------- 3. Menyeragamkan output TSFEL menjadi skalar ----------
def to_scalar(result):
    if isinstance(result, dict) and "values" in result:
        result = result["values"]
    if isinstance(result, (list, tuple, np.ndarray)):
        values = np.asarray(result, dtype=float)
        return float(np.nanmean(values))
    return float(result)


def extract_one(fn_name, signal, fs):
    function = getattr(tsfel_features, fn_name)
    parameters = inspect.signature(function).parameters
    if "fs" in parameters:
        result = function(signal, fs)
    else:
        result = function(signal)
    return to_scalar(result)


# ---------- 4. Ekstraksi setiap fitur ----------
row = {}
for fn_name in FEATURE_LIST:
    row[fn_name] = extract_one(fn_name, signal_1d, fs)

extracted_features_final = pd.DataFrame([row])

print(
    "Jumlah fitur yang dihasilkan:",
    extracted_features_final.shape[1],
)

extracted_features_final.to_csv(
    "../../NO2_Bandarkedungmulyo_TSFEL.csv",
    index=False,
)
```

Data hasil ekstraksi fitur menggunakan TSFEL:

```{code-cell}
:tags: [hide-input]
df_features = pd.read_csv("../../NO2_Bandarkedungmulyo_TSFEL.csv")
df_features.head(5)
```

Hasil ekstraksi memiliki satu baris dan 68 kolom. Satu baris tersebut merupakan ringkasan seluruh sinyal NO2 selama 365 hari, sedangkan setiap kolom berisi satu karakteristik sinyal.

## Penjelasan Domain TSFEL

TSFEL membagi fitur deret waktu ke dalam domain statistik, temporal, spectral, dan pada pemetaan yang digunakan di `test.ipynb`, domain fractal. Pembagian ini membantu menjelaskan karakteristik apa yang diukur oleh setiap fitur.

### 1. Domain Statistical

Domain statistik menjelaskan pusat, rentang, penyebaran, dan bentuk distribusi nilai NO2 tanpa memperhatikan urutan waktunya secara langsung.

- **`calc_max`, `calc_min`, `calc_mean`, `calc_median`**: nilai maksimum, minimum, rata-rata, dan median sinyal.
- **`calc_std`, `calc_var`, `interq_range`**: ukuran penyebaran data dan rentang antarkuartil.
- **`ecdf`, `ecdf_percentile`, `ecdf_percentile_count`, `ecdf_slope`**: karakteristik distribusi kumulatif empiris.
- **`hist_mode`**: nilai yang paling sering muncul pada histogram.
- **`kurtosis` dan `skewness`**: bentuk dan kemiringan distribusi nilai NO2.
- **`mean_abs_deviation` dan `median_abs_deviation`**: deviasi absolut dari pusat data.
- **`abs_energy`, `average_power`, `pk_pk_distance`, dan `rms`**: energi, daya rata-rata, jarak puncak-ke-lembah, dan besar sinyal.

Pada hasil data Anda, domain statistical berisi 21 fitur dan disimpan ke `NO2_fitur_statistical.csv`.

### 2. Domain Temporal

Domain temporal mempertimbangkan urutan kemunculan data sehingga dapat menggambarkan perubahan NO2 dari satu hari ke hari berikutnya.

- **`auc`**: luas area di bawah kurva sinyal.
- **`autocorr`**: hubungan sinyal dengan versi sinyal yang digeser terhadap waktu.
- **`calc_centroid`**: pusat massa sinyal pada sumbu waktu.
- **`mean_abs_diff`, `mean_diff`, `median_abs_diff`, `median_diff`**: perubahan rata-rata dan median antarhari.
- **`negative_turning`, `positive_turning`**: jumlah perubahan arah naik dan turun.
- **`neighbourhood_peaks`**: jumlah atau karakteristik puncak lokal di sekitar suatu titik.
- **`slope`**: kecenderungan umum sinyal untuk naik atau turun.
- **`distance` dan `sum_abs_diff`**: panjang lintasan serta total perubahan absolut sinyal.
- **`lempel_ziv` dan `zero_cross`**: kompleksitas pola dan frekuensi sinyal melewati nilai acuan.

Domain temporal pada hasil Anda berisi 15 fitur dan disimpan ke `NO2_fitur_temporal.csv`.

### 3. Domain Spectral

Domain spectral mengubah sinyal ke ranah frekuensi untuk mempelajari periodisitas, distribusi energi, dan pola waktu-frekuensi.

- **`fundamental_frequency`, `max_frequency`, dan `median_frequency`**: frekuensi dasar, tertinggi, dan median.
- **`spectral_centroid`, `spectral_spread`, dan `power_bandwidth`**: pusat, penyebaran, dan lebar pita energi.
- **`max_power_spectrum`**: daya terbesar pada spektrum.
- **`spectral_entropy`**: tingkat keteraturan atau kerataan distribusi energi spektrum.
- **`spectral_decrease`, `spectral_distance`, `spectral_slope`, dan `spectral_variation`**: perubahan profil energi pada frekuensi yang berbeda.
- **`spectral_roll_on` dan `spectral_roll_off`**: batas frekuensi ketika bagian tertentu dari energi sudah tercapai.
- **`spectral_kurtosis`, `spectral_skewness`, dan `spectral_positive_turning`**: bentuk serta perubahan profil spektrum.
- **`lpcc`, `mfcc`, dan `spectrogram_mean_coeff`**: representasi ringkas dari karakteristik waktu-frekuensi.
- **`wavelet_abs_mean`, `wavelet_energy`, `wavelet_entropy`, `wavelet_std`, dan `wavelet_var`**: karakteristik koefisien wavelet.

Domain spectral berisi 26 fitur dan disimpan ke `NO2_fitur_spectral.csv`.

### 4. Domain Fractal

Domain fractal mengukur tingkat kompleksitas, kekasaran, dan ketergantungan jangka panjang sinyal.

- **`dfa`**: analisis fluktuasi setelah tren dihilangkan.
- **`higuchi_fractal_dimension`**: dimensi fraktal berdasarkan kekasaran kurva.
- **`hurst_exponent`**: kecenderungan sinyal memiliki memori jangka panjang.
- **`maximum_fractal_length`**: ukuran panjang fraktal maksimum.
- **`mse`**: ukuran kesalahan kuadrat rata-rata pada karakteristik sinyal.
- **`petrosian_fractal_dimension`**: kompleksitas berdasarkan perubahan arah sinyal.

Domain fractal berisi 6 fitur dan disimpan ke `NO2_fitur_fractal.csv`.

Secara keseluruhan, hasil TSFEL terdiri atas 21 fitur statistical, 15 fitur temporal, 26 fitur spectral, dan 6 fitur fractal, sehingga totalnya adalah 68 fitur.
