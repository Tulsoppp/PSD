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

# Data Understanding

## Data Collection

Langkah pertama dalam proyek ini adalah mengumpulkan data polutan udara (seperti NO₂, CO, SO₂, dan O₃) yang bertipe deret waktu (_Time Series_). Dataset ini diambil dari platform satelit [Copernicus Data Space Ecosystem](https://dataspace.copernicus.eu/).

Buat akun terlebih dahulu di website Copernicus agar bisa melakukan crawling data menggunakan library openEO.

### Install Library

Untuk melakukan proses crawling data, kita membutuhkan pustaka Python pendukung yaitu `openeo` untuk berkomunikasi dengan API Copernicus.

```bash
pip install openeo
```

### Autentikasi dan Pengambilan Data

Skrip di bawah ini melakukan proses autentikasi untuk menghubungkan sistem lokal kita dengan server Copernicus menggunakan _device code flow_.

```python
import openeo

connection = openeo.connect("openeo.dataspace.copernicus.eu").authenticate_oidc()
```

Saat menjalankan baris di atas, akan muncul permintaan autentikasi:

```
Visit (link authentikasi) 📋 to authenticate.
✅ Authorized successfully
Authenticated using device code flow.
```

Klik link autentikasi lalu login menggunakan akun Copernicus.

### Definisi Area dan Pengambilan Data NO₂, SO₂, O₃ dan CO dari geojson

Setelah berhasil masuk, langkah selanjutnya adalah menentukan wilayah pengamatan yang akan dianalisis. Untuk studi kasus ini, wilayah yang dipilih adalah Kabupaten Jombang, Jawa Timur, karena karakteristiknya yang mencerminkan kombinasi aktivitas perkotaan, permukiman, lahan pertanian, serta beberapa sektor industri dan transportasi yang berpotensi memengaruhi kualitas udara. Oleh karena itu, dibutuhkan batas wilayah yang konsisten agar setiap data polutan yang diambil dapat merepresentasikan kondisi atmosfer di Kabupaten Jombang secara lebih akurat.

Titik koordinat batas wilayah Kabupaten Jombang (dalam bentuk poligon) diperoleh menggunakan alat bantu pemetaan [geojson.io](https://geojson.io). Pada platform tersebut, kita menggambar area yang mewakili wilayah studi, lalu menyalin koordinat batasnya ke dalam format yang dapat dibaca oleh API openEO. Proses ini penting dilakukan karena satelit Sentinel-5P tidak memproduksi data untuk satu titik saja, melainkan untuk area yang dibentuk oleh piksel-piksel spasial yang mencakup wilayah tertentu. Dengan membatasi area pengamatan secara eksplisit, analisis yang dilakukan menjadi lebih relevan dan sesuai dengan konteks geografis Kabupaten Jombang.

![Grafik Data](../../img/geojeson.png)

Koordinat yang didapatkan dimasukkan ke dalam variabel `aoi` (Area of Interest). Variabel ini berfungsi sebagai mask atau batas wilayah yang akan digunakan saat mengambil data polutan dari Sentinel-5P. Setelah itu, satelit diminta untuk mengunduh data berdasarkan _bounding box_ wilayah tersebut dengan menyesuaikan variabel `s5post` atribut `bands`. Proses ini memastikan bahwa semua data yang dikumpulkan berasal dari area yang sama, sehingga hasil time series dapat dibandingkan antar hari dengan konsistensi geografis yang lebih baik.

Karena satelit mungkin merekam area yang sama beberapa kali dalam satu hari, dilakukan **agregasi temporal harian** agar hanya terdapat satu nilai rata-rata per hari. Selanjutnya, dilakukan **agregasi spasial** untuk merangkum seluruh _grid_ di wilayah Kabupaten Jombang menjadi satu nilai tunggal yang mewakili kondisi rata-rata seluruh area studi. Dengan pendekatan ini, data yang dihasilkan lebih stabil dan lebih mudah dipakai untuk analisis tren, pola harian, maupun perbandingan antar polutan dalam konteks kualitas udara Kabupaten Jombang.

```python
aoi = {
    "type": "Polygon",
    "coordinates": [
        [
            [
              112.1154439,
              -7.4349656
            ],
            [
              112.377686357102,
              -7.4349656
            ],
            [
              112.377686357102,
              -7.6321375642630755
            ],
            [
              112.1154439,
              -7.6321375642630755
            ],
            [
              112.1154439,
              -7.4349656
            ]
        ]
    ]
}

s5post = connection.load_collection(
    "SENTINEL_5P_L2",
    temporal_extent=["2025-08-29", "2026-08-29"],
    spatial_extent={
        "west": 112.1154439,
        "south": -7.6321375642630755,
        "east": 112.377686357102,
        "north": -7.4349656
    },
    bands=["O3"],
)

# Agregasi harian agar tidak ada lebih dari satu data per hari
s5p_o3_daily = s5post.aggregate_temporal_period(reducer="mean", period="day")

# Agregasi spasial untuk menghasilkan rata-rata time series per AOI
s5p_o3_aoi = s5p_o3_daily.aggregate_spatial(reducer="mean", geometries=aoi)

# Simpan hasil sebagai CSV
result = s5p_o3_aoi.save_result(format="CSV")

# Jalankan job
job = result.create_job(title="s5p_o3_timeseries")
job.start_and_wait()

# Download
job.get_results().download_files("output_o3")
```

Tunggu proses selesai. Status dan progres eksekusi bisa dipantau di [openEO editor](https://editor.openeo.org/?server=https%3A%2F%2Fopeneo.dataspace.copernicus.eu%2Fopeneo%2F1.2). Setelah diproses oleh server, output akan otomatis diunduh dalam format **CSV**.

![Grafik Data](../../img/openeo.png)

```
0:00:00 Job 'j-2608250945264132925ebef4140e0037': send 'start'
0:00:03 Job 'j-2608250945264132925ebef4140e0037': queued (progress 0%)
0:00:08 Job 'j-2608250945264132925ebef4140e0037': queued (progress 0%)
0:00:15 Job 'j-2608250945264132925ebef4140e0037': queued (progress 0%)
0:00:23 Job 'j-2608250945264132925ebef4140e0037': queued (progress 0%)
0:00:33 Job 'j-2608250945264132925ebef4140e0037': queued (progress 0%)
0:00:46 Job 'j-2608250945264132925ebef4140e0037': running (progress N/A)
0:01:02 Job 'j-2608250945264132925ebef4140e0037': running (progress N/A)
0:01:21 Job 'j-2608250945264132925ebef4140e0037': running (progress N/A)
0:01:45 Job 'j-2608250945264132925ebef4140e0037': running (progress N/A)
0:02:16 Job 'j-2608250945264132925ebef4140e0037': running (progress N/A)
0:02:53 Job 'j-2608250945264132925ebef4140e0037': running (progress N/A)
0:03:40 Job 'j-2608250945264132925ebef4140e0037': finished (progress 100%)
```

### Hasil CSV

Pada tahap terakhir, kita memuat file CSV (O₃, SO₂, CO dan NO₂) yang telah dirapikan menggunakan pustaka Pandas. Data ini sekarang sudah terstruktur sebagai dataset _Time Series_ dan siap digunakan untuk analisis lanjutan. Berikut adalah cuplikan data tersebut:

1. CO

```{code-cell}
import pandas as pd
import numpy as np
df = pd.read_csv("../../output_co/timeseries.csv")
df.head(5)
```

Penjelasan: tabel di atas menunjukkan beberapa baris awal data CO yang berisi kolom tanggal dan nilai konsentrasi CO. Kolom `date` merepresentasikan waktu pengamatan, sedangkan nilai `CO` menunjukkan konsentrasi gas karbon monoksida pada hari tersebut. Tampilan awal ini membantu memastikan data sudah terbaca dengan benar sebelum analisis lebih lanjut.

2. SO2

```{code-cell}
df = pd.read_csv("../../output_so2/timeseries.csv")
df.head(5)
```

Penjelasan: hasil ini menampilkan beberapa baris awal data SO₂. Nilai pada kolom `SO2` menggambarkan konsentrasi sulfur dioksida dalam rentang waktu tertentu. Jika pola datanya konsisten, maka analisis tren dan deteksi anomali dapat dilakukan dengan lebih valid.

3. NO 2

```{code-cell}
df = pd.read_csv("../../output_no2/timeseries.csv")
df.head(5)
```

Penjelasan: pada data NO₂, nilai yang muncul memperlihatkan jumlah nitrogen dioksida pada hari-hari tertentu. Data ini penting karena NO₂ sering dikaitkan dengan aktivitas transportasi, industri, dan pembakaran yang berpengaruh terhadap kualitas udara.

4. O₃

```{code-cell}
df = pd.read_csv("../../output_o3/timeseries.csv")
df.head(5)
```

Penjelasan: data O₃ menampilkan konsentrasi ozon yang diukur pada periode yang sama dengan polutan lain. Ozon memiliki perilaku yang berbeda dibandingkan NO₂, SO₂, dan CO, sehingga hasil ini perlu dianalisis bersama-sama agar pola kualitas udara dapat dibandingkan secara lebih lengkap.

### Normalisasi Tanggal

Data waktu (tanggal) yang diperoleh dari Copernicus menyertakan zona waktu yang tidak diperlukan. Oleh karena itu, kita perlu menormalisasinya menjadi format standar yang seragam yaitu `YYYY-MM-DD` agar lebih mudah diolah. Berikut adalah kode yang digunakan untuk menyeragamkan format tanggal:

```python
import pandas as pd

df = pd.read_csv("../../output_so2/timeseries.csv")

# pastikan kolom tanggal valid
df["date"] = pd.to_datetime(df["date"], errors="coerce")

# ambil hanya bulan dan tahun
df["date"] = df["date"].dt.strftime("%Y-%m-%d")

new_df = pd.DataFrame({
    "date": df['date'],
    "SO2": df['SO2']
})

new_df.to_csv("SO2_Timeseries.csv", index=False)
```

Setelah proses normalisasi dilakukan pada seluruh dataset polutan, format waktu pada dataset menjadi lebih rapi dan konsisten. Berikut adalah cuplikan dataset setelah tanggal dinormalisasi:

1. CO

```{code-cell}
import pandas as pd
import numpy as np
df = pd.read_csv("../../output_co/timeseries.csv")
df.head(5)
```

Penjelasan: setelah normalisasi, kolom tanggal menjadi lebih rapi dan siap digunakan untuk analisis deret waktu. Hal ini penting karena setiap nilai polutan harus terhubung dengan tanggal yang jelas agar tidak terjadi kesalahan dalam melihat tren harian.

2. SO2

```{code-cell}
df = pd.read_csv("../../output_so2/timeseries.csv")
df.head(5)
```

Penjelasan: format tanggal yang sudah seragam memudahkan proses pengurutan data, pengecekan hari yang hilang, dan pembuatan grafik tren SO₂ secara lebih akurat.

3. NO 2

```{code-cell}
df = pd.read_csv("../../output_no2/timeseries.csv")
df.head(5)
```

Penjelasan: dengan tanggal yang terstandarisasi, data NO₂ bisa dianalisis untuk melihat pola harian, mingguan, atau musiman tanpa terhambat oleh format waktu yang berbeda-beda.

4. O₃

```{code-cell}
df = pd.read_csv("../../output_o3/timeseries.csv")
df.head(5)
```

Penjelasan: data O₃ setelah normalisasi menunjukkan bahwa semua observasi memiliki format tanggal yang sama sehingga proses perbandingan antar hari menjadi lebih konsisten dan lebih mudah ditafsirkan.

## Missing Values

_Missing values_ (nilai yang hilang) adalah kondisi di mana terdapat informasi yang kosong atau tidak terekam dalam dataset. Pada kasus data deret waktu yang diambil menggunakan satelit, kekosongan data ini wajar terjadi, biasanya akibat faktor cuaca (area tertutup awan tebal sehingga sensor tidak dapat membaca permukaan bumi) atau karena orbit satelit yang tidak merekam area tersebut pada hari tertentu. Mengidentifikasi keberadaan _missing values_ sangat penting sebelum melakukan analisis lebih lanjut.

Pada proyek ini, kita mengecek dua bentuk _missing values_:

1. **Tanggal yang Hilang**: Memastikan apakah ada urutan hari yang terlewat (bolong) dari rentang waktu awal hingga akhir (25 Agustus 2025 - 25 Agustus 2026).
2. **Data yang Hilang**: Memeriksa jumlah nilai polutan yang kosong (`NaN`) pada record tanggal yang sudah terekam.

### Tanggal Yang Hilang

1. CO

```{code-cell}
import pandas as pd

df = pd.read_csv("../../output_co/timeseries.csv")
df['date'] = pd.to_datetime(df['date'], errors='coerce')

# Buat rentang tanggal lengkap
start_date = "2025-08-25"
end_date = "2026-08-25"
full_range = pd.date_range(start=start_date, end=end_date, freq='D')

# Cek tanggal yang hilang
missing_dates = full_range.difference(df['date'].dropna())

print(f"Jumlah hari missing: {len(missing_dates)}")
print("Daftar tanggal missing:")
print(missing_dates)
```

Penjelasan: hasil ini menunjukkan apakah terdapat tanggal yang tidak ada dalam data CO selama periode observasi. Jika ada tanggal yang hilang, artinya data tidak tercatat pada hari tersebut, kemungkinan karena sensor tidak berhasil menangkap citra atau kondisi cuaca tidak mendukung.

2. SO2

```{code-cell}
import pandas as pd

df = pd.read_csv("../../output_so2/timeseries.csv")
df['date'] = pd.to_datetime(df['date'], errors='coerce')

# Buat rentang tanggal lengkap
start_date = "2025-08-25"
end_date = "2026-08-25"
full_range = pd.date_range(start=start_date, end=end_date, freq='D')

# Cek tanggal yang hilang
missing_dates = full_range.difference(df['date'].dropna())

print(f"Jumlah hari missing: {len(missing_dates)}")
print("Daftar tanggal missing:")
print(missing_dates)
```

Penjelasan: hasil SO₂ ini menunjukkan hari-hari yang tidak memiliki rekaman konsentrasi SO₂. Ketidakhadiran data semacam ini perlu diperhatikan karena jika tidak ditangani, analisis tren dapat terdistorsi dan menghasilkan pola yang tidak mewakili kondisi sebenarnya.

3. NO₂

```{code-cell}
import pandas as pd

df = pd.read_csv("../../output_no2/timeseries.csv")
df['date'] = pd.to_datetime(df['date'], errors='coerce')

# Buat rentang tanggal lengkap
start_date = "2025-08-25"
end_date = "2026-08-25"
full_range = pd.date_range(start=start_date, end=end_date, freq='D')

# Cek tanggal yang hilang
missing_dates = full_range.difference(df['date'].dropna())

print(f"Jumlah hari missing: {len(missing_dates)}")
print("Daftar tanggal missing:")
print(missing_dates)
```

Penjelasan: hasil NO₂ ini menandakan bahwa terdapat hari-hari tertentu yang tidak tersedia dalam dataset. Keterbatasan ini bisa berasal dari kualitas citra satelit yang rendah atau area pengamatan yang terhalang oleh kondisi atmosfer tertentu. Data yang hilang harus diperhitungkan dalam tahap preprocessing.

4. O₃

```{code-cell}
import pandas as pd

df = pd.read_csv("../../output_o3/timeseries.csv")
df['date'] = pd.to_datetime(df['date'], errors='coerce')

# Buat rentang tanggal lengkap
start_date = "2025-08-25"
end_date = "2026-08-25"
full_range = pd.date_range(start=start_date, end=end_date, freq='D')

# Cek tanggal yang hilang
missing_dates = full_range.difference(df['date'].dropna())

print(f"Jumlah hari missing: {len(missing_dates)}")
print("Daftar tanggal missing:")
print(missing_dates)
```

Penjelasan: hasil O₃ ini berfungsi untuk mengecek apakah ada celah waktu dalam seri data. Jika jumlah tanggal yang hilang cukup banyak, maka penggunaan metode imputasi atau pemotongan rentang waktu akan menjadi langkah yang penting sebelum analisis lanjutan dilakukan.

### Data Yang Hilang

Selain urutan tanggal, kita juga mengecek jumlah baris data yang memiliki nilai konsentrasi polutan kosong (`NaN`).

1. CO

```{code-cell}
import pandas as pd

df = pd.read_csv("../../output_co/timeseries.csv")
missing_value = df['CO'].isna().sum()
print(missing_value)
```

Penjelasan: angka yang muncul pada kode ini menunjukkan jumlah nilai `NaN` dalam kolom CO. Semakin besar angka tersebut, semakin banyak data yang tidak lengkap pada variabel CO, sehingga perlu ditangani sebelum masuk ke tahap pemodelan agar hasil analisis tidak bias.

Implementasi pada tools `Orange Data Mining`

```{image} ../../img/tgco.png
:alt: Grafik Data
:width: 100%
:align: center
```

2. SO₂

```{code-cell}
import pandas as pd

df = pd.read_csv("../../output_so2/timeseries.csv")
missing_value = df['SO2'].isna().sum()
print(missing_value)
```

Penjelasan: nilai `NaN` pada SO₂ menandakan ada data yang tidak tercatat dalam konsentrasi sulfur dioksida. Jika nilai ini banyak, maka daerah yang diamati berpotensi mengalami hambatan dalam pengambilan data satelit, sehingga interpretasi terhadap tren SO₂ perlu dilakukan secara hati-hati.

Implementasi pada tools `Orange Data Mining`

```{image} ../../img/tgso2.png
:alt: Grafik Data
:width: 100%
:align: center
```

3. NO₂

```{code-cell}
import pandas as pd

df = pd.read_csv("../../output_no2/timeseries.csv")
missing_value = df['NO2'].isna().sum()
print(missing_value)
```

Penjelasan: hasil ini menunjukkan banyaknya data NO₂ yang kosong. Hal ini penting karena NO₂ sering menjadi indikator kuat terhadap emisi kendaraan dan aktivitas industri, sehingga kekosongan data dapat menurunkan kualitas analisis pola harian dan musiman di wilayah studi.

Implementasi pada tools `Orange Data Mining`

```{image} ../../img/tgno2.png
:alt: Grafik Data
:width: 100%
:align: center
```

4. O₃

```{code-cell}
import pandas as pd

df = pd.read_csv("../../output_o3/timeseries.csv")
missing_value = df['O3'].isna().sum()
print(missing_value)
```

Penjelasan: jumlah `NaN` pada O₃ memperlihatkan seberapa sering parameter ozon tidak berhasil terekam. Karena ozon sangat dipengaruhi oleh proses fotokimia di atmosfer, data yang hilang atau tidak stabil perlu diperiksa agar kesimpulan tidak keliru saat menganalisis pola udara.

Implementasi pada tools `Orange Data Mining`

```{image} ../../img/tgo3.png
:alt: Grafik Data
:width: 100%
:align: center
```

## Outliers

_Outliers_ (pencilan) adalah titik data yang nilainya menyimpang secara drastis atau ekstrem dari mayoritas distribusi data lainnya. Pada data deret waktu kualitas udara, _outlier_ bisa jadi merupakan lonjakan polusi nyata yang terjadi akibat peristiwa tertentu (misalnya kebakaran hutan atau peningkatan aktivitas industri mendadak), atau bisa juga sekadar _noise_ / _error_ pada pembacaan sensor satelit.

Pada tahap _data understanding_ ini, kita mengeksplorasi _outliers_ menggunakan algoritma **Isolation Forest** dari pustaka `scikit-learn`. Algoritma deteksi anomali ini bekerja dengan cara "mengisolasi" observasi melalui pemisahan data secara acak, di mana anomali akan lebih cepat/mudah diisolasi. Kita mengatur parameter _contamination_ (estimasi persentase _outlier_ di dalam dataset) sebesar 5%. Hasil prediksi dari model yang bernilai `-1` menandakan bahwa baris tersebut terdeteksi sebagai _outlier_.

1. CO

```{code-cell}
import pandas as pd
from sklearn.ensemble import IsolationForest

df = pd.read_csv("../../output_co/timeseries.csv")
df_clean = df.dropna(subset=['CO']).copy()

model = IsolationForest(contamination=0.05, random_state=42) # contamination 0.05 = 5%
pred = model.fit_predict(df_clean[['CO']])

# Nilai -1 merepresentasikan outlier
jumlah_outlier = (pred == -1).sum()
print("Jumlah outlier:", jumlah_outlier)
```

Penjelasan: jumlah outlier pada CO menunjukkan ada beberapa hari yang memiliki nilai sangat berbeda dari mayoritas data. Hal ini bisa menandakan adanya lonjakan emisi yang nyata atau data yang tidak representatif, sehingga perlu dikaji lebih lanjut sebelum dilanjutkan ke tahap pemodelan.

Implementasi pada tools `Orange Data Mining`

```{image} ../../img/tghco.png
:alt: Grafik Data
:width: 100%
:align: center
```

```{image} ../../img/tghgco.png
:alt: Grafik Data
:width: 100%
:align: center
```

2. SO₂

```{code-cell}
import pandas as pd
from sklearn.ensemble import IsolationForest

df = pd.read_csv("../../output_so2/timeseries.csv")
df_clean = df.dropna(subset=['SO2']).copy()

model = IsolationForest(contamination=0.05, random_state=42) # contamination 0.05 = 5%
pred = model.fit_predict(df_clean[['SO2']])

# Nilai -1 merepresentasikan outlier
jumlah_outlier = (pred == -1).sum()
print("Jumlah outlier:", jumlah_outlier)
```

Penjelasan: SO₂ yang terdeteksi sebagai outlier sering kali terkait dengan lonjakan emisi yang tiba-tiba, seperti aktivitas industri atau pembakaran. Nilai-nilai ekstrem ini perlu dicek apakah benar-benar merupakan kejadian nyata atau sekadar noise yang harus dibuang.

Implementasi pada tools `Orange Data Mining`

```{image} ../../img/tghso2.png
:alt: Grafik Data
:width: 100%
:align: center
```

```{image} ../../img/tghgso2.png
:alt: Grafik Data
:width: 100%
:align: center
```

3. NO₂

```{code-cell}
import pandas as pd
from sklearn.ensemble import IsolationForest

df = pd.read_csv("../../output_no2/timeseries.csv")
df_clean = df.dropna(subset=['NO2']).copy()

model = IsolationForest(contamination=0.05, random_state=42) # contamination 0.05 = 5%
pred = model.fit_predict(df_clean[['NO2']])

# Nilai -1 merepresentasikan outlier
jumlah_outlier = (pred == -1).sum()
print("Jumlah outlier:", jumlah_outlier)
```

Penjelasan: outlier pada NO₂ menunjukkan adanya hari dengan konsentrasi nitrogen dioksida yang sangat tinggi dibanding rata-rata. Kondisi seperti ini sering dikaitkan dengan peningkatan aktivitas transportasi, industri, atau faktor meteorologis yang memengaruhi distribusi polutan.

Implementasi pada tools `Orange Data Mining`

```{image} ../../img/tghno2.png
:alt: Grafik Data
:width: 100%
:align: center
```

```{image} ../../img/tghgno2.png
:alt: Grafik Data
:width: 100%
:align: center
```

4. O₃

```{code-cell}
import pandas as pd
from sklearn.ensemble import IsolationForest

df = pd.read_csv("../../output_o3/timeseries.csv")
df_clean = df.dropna(subset=['O3']).copy()

model = IsolationForest(contamination=0.05, random_state=42) # contamination 0.05 = 5%
pred = model.fit_predict(df_clean[['O3']])

# Nilai -1 merepresentasikan outlier
jumlah_outlier = (pred == -1).sum()
print("Jumlah outlier:", jumlah_outlier)
```

Penjelasan: outlier pada O₃ bisa menunjukkan adanya periode dengan konsentrasi ozon yang sangat berbeda dari kebanyakan hari. Karena ozon terbentuk melalui reaksi kimia atmosfer, anomali semacam ini sering kali menarik untuk dikaitkan dengan kondisi cuaca dan intensitas sinar matahari.

Implementasi pada tools `Orange Data Mining`

```{image} ../../img/tgho3.png
:alt: Grafik Data
:width: 100%
:align: center
```

```{image} ../../img/tghgo3.png
:alt: Grafik Data
:width: 100%
:align: center
```

## Menggabungkan Data Polutan Kabupaten Jombang

Setelah masing-masing dataset polutan (O₃, CO, NO₂, dan SO₂) selesai diproses, langkah selanjutnya adalah menggabungkan keempat data tersebut menjadi satu tabel terpadu yang merepresentasikan kondisi udara di Kabupaten Jombang. Karena semua dataset memiliki kolom tanggal yang sama, penggabungan dilakukan berdasarkan kolom `date` sehingga seluruh variabel polutan dapat disatukan dalam satu dataset untuk analisis multivariat. Dengan format tersebut, proses eksplorasi, pemodelan, serta evaluasi tren kualitas udara di wilayah Jombang dapat dilakukan secara lebih konsisten dan terstruktur.

Berikut adalah contoh kode Python menggunakan pustaka Pandas untuk menyatukan data polutan Kabupaten Jombang dan menyimpannya ke file baru bernama `Polutan_Jombang.csv`:

```python
import pandas as pd
from pathlib import Path

# Cari root proyek secara otomatis agar file tetap terbaca dari notebook mana pun
candidates = [
    Path.cwd(),
    Path.cwd().parent,
    Path.cwd().parent.parent,
]
project_root = next((p for p in candidates if (p / "CO_Jombang_timeseries.csv").exists()), Path.cwd())

# Dataset O3 hasil ekstraksi dari Sentinel-5P
# Dataset CO, NO2, dan SO2 merupakan data time series Kabupaten Jombang

df_o3 = pd.read_csv(project_root / "output_o3" / "timeseries.csv")[["date", "O3"]]
df_co = pd.read_csv(project_root / "CO_Jombang_timeseries.csv")[["date", "co"]].rename(columns={"co": "CO"})
df_no2 = pd.read_csv(project_root / "NO2_Jombang_timeseries.csv")[["date", "NO2"]]
df_so2 = pd.read_csv(project_root / "SO2_Jombang_timeseries.csv")[["date", "SO2"]]

# Normalisasi format tanggal agar sinkron
for df in [df_o3, df_co, df_no2, df_so2]:
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")

# Gabungkan data berdasarkan tanggal
polutan_jombang = df_o3.merge(df_co, on="date", how="inner") \
    .merge(df_no2, on="date", how="inner") \
    .merge(df_so2, on="date", how="inner")

polutan_jombang.to_csv(project_root / "Polutan_Jombang.csv", index=False)
```

```{code-cell}
:tags: [hide-input]
from pathlib import Path

candidates = [
    Path.cwd(),
    Path.cwd().parent,
    Path.cwd().parent.parent,
]
project_root = next((p for p in candidates if (p / "Polutan_Jombang.csv").exists()), Path.cwd())

df = pd.read_csv(project_root / "Polutan_Jombang.csv")
display_df = df.head(5).copy()

for col in ["O3", "CO", "NO2", "SO2"]:
    if col in display_df.columns:
        display_df[col] = pd.to_numeric(display_df[col], errors="coerce")

display_df.style.format({
    "date": lambda x: x[:10] if isinstance(x, str) else x,
    "O3": "{:.6g}",
    "CO": "{:.6g}",
    "NO2": "{:.6g}",
    "SO2": "{:.6g}",
}).set_table_styles([
    {"selector": "th", "props": [("text-align", "center"), ("padding", "8px 10px"), ("background-color", "#f3f4f6"), ("font-size", "12px")]},
    {"selector": "td", "props": [("text-align", "center"), ("padding", "8px 10px"), ("font-size", "12px")]},
    {"selector": "table", "props": [("border-collapse", "collapse"), ("border", "1px solid #dfe3e8"), ("width", "100%"), ("max-width", "700px")]},
    {"selector": "tbody tr:hover", "props": [("background-color", "#f9fafb")]}
]).hide(axis="index")
```

## Visualisasi

```bash
pip install matplotlib
```


```{figure} ../../img/time_series_co_jombang.png
---
width: 100%
name: time-series-co-jombang
---
Time Series CO - Kabupaten Jombang
```

```{figure} ../../img/time_series_no2_jombang.png
---
width: 100%
name: time-series-no2-jombang
---
Time Series NO₂ - Kabupaten Jombang
```

```{figure} ../../img/time_series_so2_jombang.png
---
width: 100%
name: time-series-so2-jombang
---
Time Series SO₂ - Kabupaten Jombang
```

```{figure} ../../img/time_series_o3_jombang.png
---
width: 100%
name: time-series-o3-jombang
---
Time Series O₃ - Kabupaten Jombang
```

Penjelasan visual: setiap grafik menampilkan fluktuasi konsentrasi satu polutan di Kabupaten Jombang selama periode pengamatan. CO dan NO₂ menunjukkan variasi yang lebih dinamis, SO₂ memiliki lonjakan yang cukup mencolok pada beberapa titik, sedangkan O₃ cenderung lebih stabil. Pembagian ini memudahkan pembacaan pola per polutan dan mempermudah interpretasi terhadap dinamika kualitas udara di wilayah Jombang.

