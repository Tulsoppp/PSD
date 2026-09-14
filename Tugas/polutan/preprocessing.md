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

TSFEL (_Time Series Feature Extraction Library_) mengekstraksi karakteristik sinyal dari beberapa sudut pandang. Pada analisis ini, 365 nilai NO2 harian diperlakukan sebagai satu sinyal satu dimensi. Karena `fs = 1`, satu sampel merepresentasikan satu hari dan frekuensi yang dihasilkan fitur spectral dibaca dalam satuan siklus per hari. Dengan demikian, fitur TSFEL bukan 68 pengamatan baru, melainkan 68 ringkasan matematis dari satu deret waktu NO2.

Pembagian domain penting karena setiap domain menjawab pertanyaan yang berbeda:

1. **Statistical** menjawab: bagaimana distribusi dan besarnya nilai NO2?
2. **Temporal** menjawab: bagaimana nilai NO2 berubah menurut urutan hari?
3. **Spectral** menjawab: apakah terdapat pola berulang atau energi pada frekuensi tertentu?
4. **Fractal** menjawab: seberapa kompleks, kasar, dan memiliki memori jangka panjang sinyal tersebut?

Nilai fitur harus dibandingkan dengan hati-hati. Fitur dalam satu domain dapat memiliki skala, satuan, dan sensitivitas yang berbeda. Selain itu, beberapa fitur TSFEL dirancang untuk sinyal umum, sehingga nilainya perlu dipahami sebagai indikator pola pada data ini, bukan langsung sebagai konsentrasi atau satuan kualitas udara.

### Notasi, Rumus, dan Contoh Perhitungan 68 Fitur

Bagian ini menggunakan sinyal contoh pendek berikut agar rumus lebih mudah diperiksa:

$$
x = [1, 2, 3, 2], \qquad N=4, \qquad \Delta t=1
$$

Contoh tersebut bukan pengganti hasil 365 hari pada data NO2, tetapi menunjukkan cara kerja rumus. Pada data aktual, $x_i$ adalah kadar NO2 pada hari ke-$i$. Notasi yang digunakan adalah $\bar{x}$ untuk rata-rata, $\operatorname{median}(x)$ untuk median, $F(x)$ untuk ECDF, $X_k$ untuk koefisien Fourier, dan $P_k=|X_k|^2$ untuk daya spektrum. Rumus di bawah adalah rumus inti atau bentuk konseptual; beberapa implementasi TSFEL memiliki parameter, normalisasi, dan definisi ambang tambahan.

#### Rumus Domain Statistical

| Fitur                   | Rumus inti                                                             | Contoh dengan $x=[1,2,3,2]$                                                                 |
| ----------------------- | ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| `abs_energy`            | $E=\sum_{i=1}^{N}x_i^2$                                                | $1^2+2^2+3^2+2^2=18$                                                                        |
| `average_power`         | $P=E/N$                                                                | $18/4=4.5$                                                                                  |
| `calc_max`              | $\max(x_i)$                                                            | $\max(1,2,3,2)=3$                                                                           |
| `calc_mean`             | $\bar{x}=\frac{1}{N}\sum x_i$                                          | $(1+2+3+2)/4=2$                                                                             |
| `calc_median`           | Nilai tengah setelah data diurutkan                                    | Data terurut $[1,2,2,3]$, median $=(2+2)/2=2$                                               |
| `calc_min`              | $\min(x_i)$                                                            | $\min(1,2,3,2)=1$                                                                           |
| `calc_std`              | $s=\sqrt{\frac{1}{N-1}\sum(x_i-\bar{x})^2}$                            | $\sqrt{[(1-2)^2+0^2+1^2+0^2]/3}=0.816$                                                      |
| `calc_var`              | $s^2=\frac{1}{N-1}\sum(x_i-\bar{x})^2$                                 | $2/3=0.667$                                                                                 |
| `interq_range`          | $IQR=Q_3-Q_1$                                                          | Dengan kuartil interpolasi umum, $Q_1=1.75$, $Q_3=2.25$, jadi $IQR=0.5$                     |
| `ecdf`                  | $F(a)=\frac{1}{N}\sum_{i=1}^{N}\mathbf{1}(x_i\leq a)$                  | Untuk $a=2$, $F(2)=3/4=0.75$                                                                |
| `ecdf_percentile`       | $p(a)=100F(a)$ atau nilai $a$ pada persentil tertentu                  | Untuk $a=2$, persentil kumulatifnya $75\%$                                                  |
| `ecdf_percentile_count` | $C(a)=\sum\mathbf{1}(x_i\leq a)$                                       | Untuk $a=2$, $C(2)=3$                                                                       |
| `ecdf_slope`            | $\frac{\Delta F}{\Delta a}$                                            | Jika $F$ berubah $0.5$ pada rentang nilai $1$, slope $=0.5/1=0.5$                           |
| `entropy`               | $H=-\sum_j p_j\log p_j$                                                | Jika tiga bin memiliki $p=[0.25,0.5,0.25]$, $H=-\sum p\log_2p=1.5$ bit                      |
| `hist_mode`             | $\operatorname{argmax}_b\;n_b$                                         | Bin dengan frekuensi terbanyak adalah bin mode; hasil tepat bergantung jumlah bin histogram |
| `kurtosis`              | $\frac{1}{N}\sum[(x_i-\bar{x})/s]^4$ dikurangi 3 untuk excess kurtosis | Mengukur ekor distribusi; contoh numeriknya bergantung apakah TSFEL memakai bias correction |
| `skewness`              | $\frac{1}{N}\sum[(x_i-\bar{x})/s]^3$                                   | Pada contoh yang simetris terhadap 2, skewness mendekati $0$                                |
| `mean_abs_deviation`    | $MAD_\mu=\frac{1}{N}\sum_i \lvert x_i-\bar{x}\rvert$                   | $(1+0+1+0)/4=0.5$                                                                           |
| `median_abs_deviation`  | $MAD=\operatorname{median}(\lvert x_i-\operatorname{median}(x)\rvert)$ | Deviasi $[1,0,1,0]$, median $=0.5$                                                          |
| `pk_pk_distance`        | $D_{p-p}=\max(x)-\min(x)$                                              | $3-1=2$                                                                                     |
| `rms`                   | $RMS=\sqrt{\frac{1}{N}\sum x_i^2}$                                     | $\sqrt{18/4}=2.121$                                                                         |

#### Rumus Domain Temporal

| Fitur                 | Rumus inti                                                                                               | Contoh dengan $x=[1,2,3,2]$                                                                                                                         |
| --------------------- | -------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| `auc`                 | $A\approx\sum_{i=1}^{N-1}\frac{x_i+x_{i+1}}{2}\Delta t$                                                  | $(1.5+2.5+2.5)\times1=6.5$                                                                                                                          |
| `autocorr`            | $\rho_k=\frac{\sum_{i=1}^{N-k}(x_i-\bar{x})(x_{i+k}-\bar{x})}{\sum_{i=1}^{N}(x_i-\bar{x})^2}$            | Untuk lag $k=1$, pembilang $=0$, sehingga $\rho_1=0$ pada definisi ini                                                                              |
| `calc_centroid`       | $t_c=\frac{\sum t_i x_i}{\sum x_i}$                                                                      | Dengan $t=[0,1,2,3]$, $t_c=(0+2+6+6)/8=1.75$                                                                                                        |
| `distance`            | $L=\sum_{i=1}^{N-1}\sqrt{(t_{i+1}-t_i)^2+(x_{i+1}-x_i)^2}$                                               | $\sqrt2+\sqrt2+\sqrt2=4.243$                                                                                                                        |
| `mean_abs_diff`       | $\frac{1}{N-1}\sum_i \lvert x_{i+1}-x_i\rvert$                                                           | $(1+1+1)/3=1$                                                                                                                                       |
| `mean_diff`           | $\frac{1}{N-1}\sum(x_{i+1}-x_i)$                                                                         | $(1+1-1)/3=0.333$                                                                                                                                   |
| `median_abs_diff`     | $\operatorname{median}(\lvert x_{i+1}-x_i\rvert)$                                                        | Median $[1,1,1]=1$                                                                                                                                  |
| `median_diff`         | $\operatorname{median}(x_{i+1}-x_i)$                                                                     | Median $[1,1,-1]=1$                                                                                                                                 |
| `negative_turning`    | $\sum_{i=2}^{N-1}\mathbf{1}[(x_i-x_{i-1})>0\land(x_{i+1}-x_i)<0]$                                        | Pola $1\to2\to3\to2$ memiliki satu puncak turun, jadi hasil $=1$                                                                                    |
| `positive_turning`    | $\sum_{i=2}^{N-1}\mathbf{1}[(x_i-x_{i-1})<0\land(x_{i+1}-x_i)>0]$                                        | Contoh tidak memiliki lembah naik, jadi hasil $=0$                                                                                                  |
| `neighbourhood_peaks` | $\sum_i\mathbf{1}[x_i>x_{i-r},x_i>x_{i+r}]$                                                              | Nilai 3 lebih besar dari tetangganya, sehingga terdapat satu puncak lokal untuk radius $r=1$                                                        |
| `slope`               | $b=\frac{\sum(t_i-\bar{t})(x_i-\bar{x})}{\sum(t_i-\bar{t})^2}$                                           | Untuk $t=[0,1,2,3]$, $b=0.2$                                                                                                                        |
| `sum_abs_diff`        | $S=\sum_{i=1}^{N-1}\lvert x_{i+1}-x_i\rvert$                                                             | $1+1+1=3$                                                                                                                                           |
| `zero_cross`          | $Z=\sum_{i=1}^{N-1}\mathbf{1}[x_i x_{i+1}<0]$                                                            | Tidak ada nilai yang melewati nol, jadi $Z=0$                                                                                                       |
| `lempel_ziv`          | Membuat urutan simbol, lalu menghitung pola baru yang belum pernah muncul; rasio umumnya $c(N)\log_2N/N$ | Setelah diskretisasi contoh menjadi simbol `A B C B`, jumlah pola baru dihitung oleh parser LZ; hasil dapat berubah sesuai aturan simbolisasi TSFEL |

#### Rumus Domain Spectral

Transformasi Fourier diskret digunakan sebagai dasar:

$$
X_k=\sum_{n=0}^{N-1}x_n e^{-2\pi i kn/N},\qquad
f_k=\frac{k f_s}{N},\qquad P_k=|X_k|^2.
$$

| Fitur                       | Rumus inti                                                         | Contoh/interpretasi                                                                                        |
| --------------------------- | ------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------- |
| `fundamental_frequency`     | $f_0=\arg\max_{f_k>0}P_k$                                          | Jika puncak daya terbesar berada pada bin $k=1$, dengan $N=4$ dan $f_s=1$, maka $f_0=1/4=0.25$ siklus/hari |
| `max_frequency`             | $\max\{f_k:P_k>0\}$                                                | Dengan $N=4$, frekuensi Nyquist adalah $f_s/2=0.5$ siklus/hari                                             |
| `max_power_spectrum`        | $\max_k P_k$                                                       | Ambil daya terbesar dari semua bin Fourier                                                                 |
| `median_frequency`          | Frekuensi $f_m$ saat kumulatif daya mencapai $50\%$                | Jika setengah daya tercapai pada bin $k=1$, maka $f_m=0.25$ siklus/hari                                    |
| `spectral_centroid`         | $C=\frac{\sum f_kP_k}{\sum P_k}$                                   | Jika $P=[1,2,1]$ pada $f=[0,0.25,0.5]$, $C=(0+0.5+0.5)/4=0.25$                                             |
| `spectral_spread`           | $\sqrt{\frac{\sum P_k(f_k-C)^2}{\sum P_k}}$                        | Mengukur sebaran daya di sekitar centroid; daya yang menyebar menghasilkan spread lebih besar              |
| `power_bandwidth`           | $f_{upper}-f_{lower}$ untuk band daya yang ditentukan              | Jika band energi berada dari $0.1$ sampai $0.4$, bandwidth $=0.3$ siklus/hari                              |
| `spectral_entropy`          | $H_s=-\sum q_k\log_2q_k$, $q_k=P_k/\sum P_k$                       | Untuk $q=[0.5,0.5]$, $H_s=1$ bit; daya yang terkonsentrasi memberi entropy lebih rendah                    |
| `spectral_roll_on`          | Frekuensi saat kumulatif daya melewati ambang awal                 | Jika ambang tercapai pada $f=0.10$, roll-on $=0.10$ siklus/hari                                            |
| `spectral_roll_off`         | Frekuensi saat kumulatif daya melewati ambang akhir, sering $85\%$ | Jika $85\%$ daya tercapai pada $0.40$, roll-off $=0.40$ siklus/hari                                        |
| `spectral_slope`            | Kemiringan regresi $P_k=a f_k+b$                                   | $a<0$ berarti daya cenderung turun saat frekuensi meningkat                                                |
| `spectral_decrease`         | $D=\frac{1}{K-1}\sum_{k=1}^{K-1}\frac{P_{k+1}-P_1}{k}$             | Nilai menggambarkan penurunan daya relatif terhadap bin awal                                               |
| `spectral_distance`         | $\sum_k \lvert P_{k+1}-P_k\rvert$ atau jarak antarprofil spektrum  | Spektrum dengan banyak perubahan tajam menghasilkan jarak lebih besar                                      |
| `spectral_variation`        | $\frac{\|P_t-P_{t-1}\|}{\|P_{t-1}\|}$                              | Pada spektrogram, mengukur perubahan spektrum antarjendela waktu                                           |
| `spectral_kurtosis`         | $\frac{\sum q_k(f_k-C)^4}{(\sum q_k(f_k-C)^2)^2}$                  | Nilai tinggi menunjukkan energi terkonsentrasi tajam di sekitar frekuensi tertentu                         |
| `spectral_skewness`         | $\frac{\sum q_k(f_k-C)^3}{(\sum q_k(f_k-C)^2)^{3/2}}$              | Positif berarti ekor energi lebih panjang ke frekuensi tinggi                                              |
| `spectral_positive_turning` | $\sum_k\mathbf{1}[P_k>P_{k-1}\land P_{k+1}>P_k]$                   | Menghitung kenaikan lokal pada profil daya                                                                 |
| `lpcc`                      | Koefisien cepstrum: $c_m=\mathcal{F}^{-1}(\log \lvert A(f)\rvert)$ | Nilai merupakan ringkasan bentuk spektrum; tepatnya bergantung orde LPCC                                   |
| `mfcc`                      | $c_m=\sum_b\log(E_b)\cos[\pi m(b+1/2)/B]$                          | Energi tiap filter mel $E_b$ diubah menjadi koefisien; parameter filterbank memengaruhi hasil              |
| `spectrogram_mean_coeff`    | $\frac{1}{T K}\sum_{t,k}S(t,k)$                                    | Rata-rata seluruh koefisien spektrogram; hasil bergantung ukuran jendela dan overlap                       |
| `human_range_energy`        | $E_{band}=\sum_{f\in[f_l,f_u]}P(f)$                                | Jika band memiliki daya $2,3,1$, energinya $=6$; band persis ditentukan implementasi                       |
| `wavelet_abs_mean`          | $\frac{1}{M}\sum_j \lvert w_j\rvert$                               | Koefisien wavelet $[1,-2,1]$ memberi mean absolut $4/3$                                                    |
| `wavelet_energy`            | $E_w=\sum_jw_j^2$                                                  | Untuk $[1,-2,1]$, $E_w=1+4+1=6$                                                                            |
| `wavelet_entropy`           | $H_w=-\sum_jp_j\log_2p_j$, $p_j=w_j^2/E_w$                         | Untuk kuadrat $[1,4,1]$, $p=[1/6,4/6,1/6]$ lalu entropy dihitung dari distribusi itu                       |
| `wavelet_std`               | $\sqrt{\frac{1}{M-1}\sum(w_j-\bar{w})^2}$                          | Untuk $[1,-2,1]$, mean $=0$, std $=\sqrt3$                                                                 |
| `wavelet_var`               | $\frac{1}{M-1}\sum(w_j-\bar{w})^2$                                 | Untuk contoh sama, varians $=3$                                                                            |

#### Rumus Domain Fractal

| Fitur                         | Rumus inti                                                                                              | Contoh/interpretasi                                                                                              |
| ----------------------------- | ------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| `dfa`                         | Untuk ukuran jendela $s$, $F(s)=\sqrt{\frac{1}{N}\sum[Y(i)-Y_s(i)]^2}$, kemudian $F(s)\propto s^\alpha$ | Kemiringan regresi $\log F(s)$ terhadap $\log s$ adalah $\alpha$; $\alpha>0.5$ mengarah pada persistensi         |
| `higuchi_fractal_dimension`   | Hitung panjang kurva $L(k)$ pada skala $k$, lalu $L(k)\propto k^{-D}$                                   | $D$ adalah kemiringan regresi log-log; kurva lebih kasar cenderung memiliki $D$ lebih tinggi                     |
| `hurst_exponent`              | $R/S\propto n^H$ atau hubungan scaling setara                                                           | $H\approx0.5$ mendekati acak, $H>0.5$ persisten, dan $H<0.5$ antipersisten                                       |
| `maximum_fractal_length`      | Panjang maksimum kurva pada skala: $L_{max}=\max_kL(k)$                                                 | Dari beberapa $L(k)$, ambil nilai terbesar; hasil bergantung skala yang diuji                                    |
| `mse`                         | $MSE=\frac{1}{n}\sum_{i=1}^{n}(y_i-\hat{y}_i)^2$                                                        | Jika error $[1,-1,2]$, MSE $=(1+1+4)/3=2$; pada TSFEL ini merupakan deskriptor, bukan error model prediksi       |
| `petrosian_fractal_dimension` | $D_P=\frac{\log_{10}N}{\log_{10}N+\log_{10}(N/(N+0.4N_\Delta))}$                                        | Untuk $N=100$ dan jumlah perubahan arah $N_\Delta=20$, substitusi ke rumus menghasilkan estimasi dimensi fraktal |

Rumus pada tabel memberi contoh numerik sederhana, sedangkan nilai dalam `NO2_Bandarkedungmulyo_TSFEL.csv` dihitung menggunakan 365 sampel dan implementasi fungsi TSFEL. Untuk fitur yang menggunakan histogram, Fourier, wavelet, spektrogram, atau algoritma kompleksitas, perubahan jumlah bin, jendela, skala, threshold, dan normalisasi dapat mengubah hasil meskipun sinyalnya sama. Oleh karena itu, parameter tersebut harus dibuat konsisten ketika membandingkan beberapa lokasi atau periode.

### 1. Domain Statistical

Domain statistical menjelaskan distribusi nilai NO2 tanpa memperhatikan urutan tanggal secara langsung. Jika tanggal seluruh data diacak tetapi kumpulan nilainya tetap sama, sebagian besar fitur pada domain ini akan tetap sama. Domain ini berguna untuk menjawab apakah kadar NO2 cenderung rendah atau tinggi, seberapa lebar variasinya, dan apakah distribusinya simetris.

| Fitur                                        | Penjelasan dan interpretasi pada NO2                                                                                                                                                                           |
| -------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `calc_max`, `calc_min`                       | Nilai tertinggi dan terendah dalam 365 hari. Keduanya menunjukkan batas observasi yang muncul pada periode penelitian, tetapi tidak menjelaskan kapan nilai tersebut terjadi.                                  |
| `calc_mean`, `calc_median`                   | Rata-rata dan nilai tengah. Perbedaan yang besar antara keduanya dapat mengindikasikan distribusi yang tidak simetris atau pengaruh nilai ekstrem.                                                             |
| `calc_std`, `calc_var`                       | Simpangan baku dan varians sebagai ukuran penyebaran. Varians merupakan kuadrat simpangan baku sehingga satuannya juga ikut dikuadratkan.                                                                      |
| `interq_range`                               | Rentang 50% data tengah, yaitu `Q3 - Q1`. Fitur ini relatif lebih tahan terhadap nilai ekstrem dibandingkan rentang maksimum-minimum.                                                                          |
| `mean_abs_deviation`, `median_abs_deviation` | Rata-rata atau median jarak absolut setiap nilai terhadap pusat data. Nilai besar menunjukkan data lebih menyebar; median absolut biasanya lebih tahan terhadap pencilan.                                      |
| `kurtosis`                                   | Keruncingan dan ketebalan ekor distribusi. Nilai tinggi dapat menunjukkan adanya ekor berat atau nilai yang jauh dari pusat, sedangkan interpretasinya bergantung pada definisi kurtosis yang dipakai pustaka. |
| `skewness`                                   | Kemencengan distribusi. Nilai positif menunjukkan ekor relatif lebih panjang ke arah nilai tinggi, sedangkan nilai negatif menunjukkan ekor ke arah nilai rendah.                                              |
| `hist_mode`                                  | Perkiraan nilai yang paling sering muncul berdasarkan histogram. Hasilnya dipengaruhi oleh pembagian bin, sehingga bukan selalu nilai observasi yang benar-benar paling sering muncul.                         |
| `entropy`                                    | Ketidakpastian atau keragaman distribusi nilai. Entropi lebih tinggi menunjukkan nilai tersebar pada lebih banyak keadaan, tetapi maknanya dipengaruhi oleh cara sinyal didiskretisasi.                        |
| `ecdf`                                       | Ringkasan fungsi distribusi kumulatif empiris, yaitu proporsi data yang berada di bawah ambang tertentu. Nilainya menggambarkan distribusi keseluruhan, bukan urutan harian.                                   |
| `ecdf_percentile`, `ecdf_percentile_count`   | Ringkasan posisi persentil dan jumlah data yang memenuhi kriteria distribusi empiris. Fitur ini membantu melihat posisi nilai terhadap keseluruhan populasi data.                                              |
| `ecdf_slope`                                 | Kemiringan perubahan fungsi distribusi kumulatif. Perubahan yang lebih curam menandakan banyak nilai terkonsentrasi pada rentang nilai yang sempit.                                                            |
| `abs_energy`, `average_power`                | `abs_energy` merupakan jumlah kuadrat nilai sinyal, sedangkan `average_power` adalah energi rata-rata per sampel. Keduanya merepresentasikan besarnya amplitudo NO2 secara keseluruhan.                        |
| `rms`                                        | Akar rata-rata kuadrat nilai. RMS mempertimbangkan semua nilai dan memberi bobot lebih besar pada nilai tinggi, sehingga berguna untuk mengukur level sinyal efektif.                                          |
| `pk_pk_distance`                             | Jarak dari puncak tertinggi ke lembah terendah, secara umum terkait dengan `max - min`. Nilai besar menunjukkan rentang amplitudo yang lebar.                                                                  |

Pada hasil data ini, `calc_mean` sekitar `3.16e-05`, sedangkan `calc_std` sekitar `1.14e-05`. Angka tersebut menunjukkan bahwa ringkasan pusat dan variasi berada pada skala yang berbeda dari fitur seperti `abs_energy` atau `calc_var`. Nilai-nilai tersebut tidak boleh dibandingkan hanya berdasarkan besar angka tanpa memperhatikan definisi dan satuannya.

Pada hasil data Anda, domain statistical berisi 21 fitur dan disimpan ke `NO2_fitur_statistical.csv`.

### 2. Domain Temporal

Domain temporal mempertahankan urutan 365 hari. Domain ini menggambarkan perubahan, arah, ketergantungan antarwaktu, dan bentuk lintasan sinyal. Berbeda dari domain statistical, dua sinyal dengan nilai yang sama tetapi urutan tanggal berbeda dapat menghasilkan fitur temporal yang berbeda.

| Fitur                                  | Penjelasan dan interpretasi pada NO2                                                                                                                                                                                                                 |
| -------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `auc`                                  | Luas area di bawah kurva. Untuk data harian, nilainya berkaitan dengan akumulasi kadar NO2 sepanjang periode, sehingga dipengaruhi oleh level rata-rata dan panjang periode.                                                                         |
| `autocorr`                             | Korelasi sinyal dengan versi yang digeser. Nilai ini menunjukkan kemiripan pola antarposisi waktu tertentu; autokorelasi yang tinggi dapat mengindikasikan kesinambungan atau pola berulang.                                                         |
| `calc_centroid`                        | Titik pusat berbobot pada sumbu waktu. Nilai ini menunjukkan apakah energi atau amplitudo sinyal lebih terkonsentrasi pada awal, tengah, atau akhir periode.                                                                                         |
| `mean_diff`, `median_diff`             | Rata-rata dan median perubahan bertanda antarhari. Nilai positif menunjukkan kecenderungan kenaikan, sedangkan nilai negatif menunjukkan kecenderungan penurunan.                                                                                    |
| `mean_abs_diff`, `median_abs_diff`     | Rata-rata dan median besar perubahan tanpa memperhatikan arah. Nilai tinggi menunjukkan NO2 lebih tidak stabil dari hari ke hari.                                                                                                                    |
| `positive_turning`, `negative_turning` | Jumlah perubahan arah lokal pada pola naik dan turun. Fitur ini membantu menggambarkan seberapa sering sinyal berbelok, bukan sekadar berapa tinggi nilai NO2.                                                                                       |
| `neighbourhood_peaks`                  | Puncak lokal yang terdeteksi dibandingkan dengan nilai di lingkungan sekitarnya. Puncak lokal dapat merepresentasikan episode kenaikan singkat, tetapi hasilnya dipengaruhi parameter deteksi dan noise.                                             |
| `slope`                                | Kemiringan tren global sinyal terhadap waktu. Slope positif berarti kecenderungan meningkat selama periode, sedangkan slope negatif berarti menurun. Slope yang mendekati nol tidak berarti sinyal konstan karena fluktuasi lokal masih dapat besar. |
| `distance`                             | Panjang lintasan sinyal pada bidang waktu-nilai. Lintasan makin panjang apabila perubahan antarhari makin sering atau besar.                                                                                                                         |
| `sum_abs_diff`                         | Total perubahan absolut antarhari. Fitur ini mengakumulasi seluruh gerakan sinyal dan tidak saling meniadakan seperti `mean_diff`.                                                                                                                   |
| `lempel_ziv`                           | Ukuran kompleksitas pola berdasarkan jumlah pola atau suburutan baru yang muncul. Nilai lebih tinggi secara umum menunjukkan pola yang lebih beragam atau kurang berulang.                                                                           |
| `zero_cross`                           | Jumlah perpindahan sinyal melewati nilai acuan. Pada data kadar NO2 yang seluruhnya positif, nilai ini dapat nol karena sinyal tidak melintasi nol; hasil nol bukan berarti tidak ada perubahan.                                                     |

Contoh interpretasi hasil: `mean_diff` yang sangat dekat nol bersama `slope` yang kecil menunjukkan tidak ada kecenderungan linear kuat selama setahun. Namun, `mean_abs_diff` tetap positif dan jumlah turning point cukup besar, sehingga sinyal tetap mengalami naik-turun harian. Ini memperlihatkan mengapa satu fitur tidak cukup untuk menyimpulkan perilaku deret waktu.

Domain temporal pada hasil Anda berisi 15 fitur dan disimpan ke `NO2_fitur_temporal.csv`.

### 3. Domain Spectral

Domain spectral menganalisis sinyal pada ranah frekuensi. Dengan transformasi Fourier, perubahan terhadap waktu direpresentasikan sebagai komponen frekuensi dan daya. Pada data ini, frekuensi dibaca sebagai siklus per hari; misalnya frekuensi `1/365` siklus per hari berkaitan dengan pola tahunan, sedangkan frekuensi yang lebih tinggi merepresentasikan perubahan yang lebih cepat. Karena panjang data hanya 365 hari dan pengamatan dilakukan sekali per hari, fitur spectral tidak dapat menjelaskan variasi intrahari.

| Kelompok fitur                                                                        | Penjelasan                                                                                                                                                                                                                                       |
| ------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `fundamental_frequency`, `max_frequency`, `median_frequency`                          | Menunjukkan frekuensi dasar, frekuensi dominan/tertinggi yang terdeteksi, dan titik tengah distribusi frekuensi. Frekuensi rendah mengarah pada perubahan lambat; frekuensi tinggi mengarah pada fluktuasi cepat.                                |
| `max_power_spectrum`                                                                  | Daya terbesar pada spektrum. Puncak yang kuat dapat menunjukkan komponen periodik dominan, tetapi tidak otomatis membuktikan penyebab periodisitas tersebut.                                                                                     |
| `spectral_centroid`, `spectral_spread`, `power_bandwidth`                             | Centroid adalah pusat gravitasi energi spektrum; spread mengukur penyebaran energi di sekitar centroid; bandwidth mengukur lebar pita frekuensi yang membawa energi.                                                                             |
| `spectral_entropy`                                                                    | Mengukur seberapa merata energi tersebar di berbagai frekuensi. Entropi rendah cenderung menunjukkan energi terkonsentrasi pada beberapa frekuensi, sedangkan entropi tinggi menunjukkan spektrum lebih menyebar.                                |
| `spectral_roll_on`, `spectral_roll_off`                                               | Frekuensi batas ketika proporsi tertentu dari energi spektrum telah tercapai. Roll-off yang lebih tinggi berarti energi menjangkau frekuensi yang lebih tinggi.                                                                                  |
| `spectral_slope`, `spectral_decrease`, `spectral_distance`, `spectral_variation`      | Menggambarkan kemiringan, penurunan, jarak, dan perubahan bentuk spektrum antarbagian frekuensi. Fitur-fitur ini menjelaskan profil energi, bukan kadar NO2 secara langsung.                                                                     |
| `spectral_kurtosis`, `spectral_skewness`                                              | Menggambarkan keruncingan dan kemencengan distribusi energi pada ranah frekuensi.                                                                                                                                                                |
| `spectral_positive_turning`                                                           | Jumlah perubahan arah naik pada kurva spektrum. Nilai tinggi menunjukkan profil spektrum memiliki banyak perubahan lokal.                                                                                                                        |
| `lpcc`, `mfcc`                                                                        | Koefisien yang merangkum bentuk spektral menggunakan pendekatan parametrik. Walaupun populer pada analisis suara, pada data NO2 fitur ini dipakai sebagai deskriptor numerik bentuk sinyal, bukan sebagai indikator suara.                       |
| `spectrogram_mean_coeff`                                                              | Ringkasan rata-rata koefisien spektrogram, yaitu representasi energi pada waktu dan frekuensi.                                                                                                                                                   |
| `human_range_energy`                                                                  | Energi pada rentang frekuensi tertentu yang didefinisikan TSFEL sebagai rentang terkait persepsi manusia. Untuk NO2, fitur ini sebaiknya diperlakukan sebagai energi pada band yang ditentukan algoritma, bukan sebagai makna biologis langsung. |
| `wavelet_abs_mean`, `wavelet_energy`, `wavelet_entropy`, `wavelet_std`, `wavelet_var` | Ringkasan koefisien wavelet. Wavelet dapat menangkap perubahan lokal pada beberapa skala waktu, sehingga melengkapi Fourier yang lebih global.                                                                                                   |

Nilai spectral sangat bergantung pada panjang sinyal, frekuensi sampling, detrending, dan cara normalisasi. Karena itu, perbandingan spectral antarwilayah atau antarperiode sebaiknya menggunakan panjang periode dan pengaturan preprocessing yang sama. Fitur spectral juga menunjukkan pola frekuensi, bukan hubungan sebab-akibat dengan sumber emisi.

Domain spectral berisi 26 fitur dan disimpan ke `NO2_fitur_spectral.csv`.

### 4. Domain Fractal

Domain fractal mengukur kompleksitas, kekasaran, dan ketergantungan jangka panjang. Deret waktu yang tampak tidak teratur belum tentu acak sepenuhnya; analisis fractal berusaha mengukur apakah ketidakteraturan tersebut memiliki struktur pada beberapa skala waktu.

| Fitur                         | Penjelasan dan interpretasi                                                                                                                                                                                                                                                                     |
| ----------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `dfa`                         | Detrended Fluctuation Analysis mengukur bagaimana fluktuasi sinyal berubah terhadap ukuran jendela setelah tren lokal dihilangkan. Fitur ini digunakan untuk menilai scaling dan kemungkinan ketergantungan jangka panjang.                                                                     |
| `higuchi_fractal_dimension`   | Mengestimasi dimensi fraktal menggunakan panjang kurva pada beberapa skala. Nilai yang lebih tinggi umumnya berkaitan dengan kurva yang lebih kasar dan kompleks.                                                                                                                               |
| `hurst_exponent`              | Menggambarkan persistensi sinyal. Nilai di atas sekitar `0.5` sering dikaitkan dengan kecenderungan perubahan yang berlanjut, nilai sekitar `0.5` dengan perilaku mendekati acak, dan nilai di bawahnya dengan kecenderungan berbalik. Batas ini adalah interpretasi umum, bukan aturan mutlak. |
| `maximum_fractal_length`      | Ringkasan panjang fraktal maksimum yang dihitung algoritma. Fitur ini sensitif terhadap skala dan bentuk sinyal, sehingga paling bermakna ketika dibandingkan pada preprocessing yang sama.                                                                                                     |
| `mse`                         | Mean Squared Error yang dikembalikan oleh fitur TSFEL. Dalam konteks ini, nilainya dipakai sebagai deskriptor numerik kompleksitas/ketidakpastian sesuai implementasi TSFEL, bukan langsung sebagai error model prediksi.                                                                       |
| `petrosian_fractal_dimension` | Estimasi dimensi fraktal berdasarkan jumlah perubahan arah sinyal dan panjang sinyal. Nilai ini membantu membedakan pola yang halus dari pola yang lebih berosilasi.                                                                                                                            |

Pada hasil data ini, `hurst_exponent` sekitar `0.80`. Secara deskriptif, angka tersebut konsisten dengan adanya persistensi atau memori jangka panjang pada pola NO2. Namun, kesimpulan tersebut perlu dibaca hati-hati karena deret hanya terdiri dari 365 titik, telah melalui imputasi, dan berasal dari satu lokasi. Interpolasi dapat mengurangi atau mengubah fluktuasi lokal yang ikut memengaruhi fitur fractal.

Domain fractal berisi 6 fitur dan disimpan ke `NO2_fitur_fractal.csv`.

Secara keseluruhan, hasil TSFEL terdiri atas 21 fitur statistical, 15 fitur temporal, 26 fitur spectral, dan 6 fitur fractal, sehingga totalnya adalah 68 fitur.

### Cara Membaca Hasil Secara Terpadu

Keempat domain sebaiknya dibaca bersama. Domain statistical dapat menunjukkan level dan variasi dasar NO2; domain temporal dapat menjelaskan apakah perubahan tersebut berlangsung stabil, berfluktuasi, atau memiliki banyak puncak; domain spectral dapat mengungkap konsentrasi energi pada skala waktu tertentu; sedangkan domain fractal dapat memberikan informasi tambahan tentang kompleksitas dan persistensi.

Sebagai contoh, rata-rata yang relatif stabil tetapi `mean_abs_diff` dan jumlah puncak lokal yang tinggi berarti kadar NO2 secara keseluruhan tidak mengalami perubahan level yang besar, tetapi tetap berfluktuasi dari hari ke hari. Jika pada saat yang sama spectral entropy tinggi, energi perubahan kemungkinan tersebar pada banyak frekuensi dan tidak terkonsentrasi pada satu siklus dominan. Interpretasi seperti ini lebih informatif daripada menyimpulkan kondisi hanya dari `calc_mean` atau satu fitur lain.

Hasil ekstraksi kemudian disimpan sebagai empat file ringkasan: `NO2_fitur_statistical.csv`, `NO2_fitur_temporal.csv`, `NO2_fitur_spectral.csv`, dan `NO2_fitur_fractal.csv`. Masing-masing file memiliki satu baris karena seluruh periode 365 hari diproses sebagai satu segmen sinyal. Jika analisis membutuhkan perbandingan antarbulan atau prediksi perperiode, sinyal perlu dibagi menjadi beberapa jendela waktu terlebih dahulu. Ekstraksi satu baris untuk seluruh tahun tidak dapat digunakan untuk menyimpulkan perubahan fitur dari bulan ke bulan.
