# Penjelasan Metrik Statistika Deskriptif Kertosono (NO2)

Dalam analisis data, ringkasan metrik yang disajikan dalam bentuk tabel disebut sebagai **Statistika Deskriptif (Descriptive Statistics)**. Ringkasan ini umumnya dimanfaatkan pada tahap awal analisis, yakni **Exploratory Data Analysis (EDA)**. Tujuannya adalah untuk memahami karakteristik, pola distribusi, serta kualitas data sebelum beralih ke tahap pemrosesan lanjutan, peramalan (_forecasting_), maupun pemodelan.

Seluruh hasil pada bagian ini dihitung dari file `NO2_Kertosono_timeseries.csv`. File memiliki header `date,NO2` dan menggunakan pemisah koma. Dataset berisi 365 baris harian pada periode 31 Agustus 2025 sampai 30 Agustus 2026. Dari 365 baris tersebut, 230 nilai NO2 valid dan 135 nilai missing.

Tabel berikut hanya menyajikan ringkasan konsentrasi NO2 beserta metode perhitungan manualnya:

## 1. Min & Max

- **Penjelasan:** Merupakan nilai observasi terendah (Min) dan tertinggi (Max) dalam suatu kumpulan data. Metrik ini berguna untuk mengidentifikasi batas bawah dan batas atas dari rentang data.
- **Perhitungan Manual:** Urutkan seluruh data mulai dari nilai yang terkecil hingga yang terbesar.
  - $Min = X_1$ (Data pada urutan pertama)
  - $Max = X_n$ (Data pada urutan terakhir)

### Hasil Perhitungan

| Polutan |            Min |           Max |
| ------- | -------------: | ------------: |
| NO2     | -0.00000401320 | 0.00005627621 |

## 2. Mean

- **Penjelasan:** Merupakan nilai pusat (rata-rata) dari sekumpulan data. Nilai ini diperoleh dengan menjumlahkan seluruh observasi, kemudian membaginya dengan total jumlah observasi yang valid.
- **Perhitungan Manual:**

  $$ \bar{x} = \frac{\sum\_{i=1}^{n} x_i}{n} $$

  _(Jumlahkan seluruh nilai konsentrasi polutan, lalu bagi dengan total baris data yang tersedia)_.

### Hasil Perhitungan

| Polutan | n valid |               Mean |
| ------- | ------: | -----------------: |
| NO2     |     230 | 0.0000305613596571 |

## 3. Std. Deviation (Standar Deviasi)

- **Penjelasan:** Mengukur sejauh mana rata-rata simpangan titik-titik data terhadap nilai Mean-nya. Standar deviasi yang rendah mengindikasikan bahwa data cenderung mengelompok di sekitar rata-rata (konsisten), sementara nilai yang tinggi menunjukkan adanya rentang fluktuasi yang lebar.
- **Perhitungan Manual (Sampel):**

  $$ s = \sqrt{\frac{\sum\_{i=1}^{n} (x_i - \bar{x})^2}{n-1}} $$

### Hasil Perhitungan

| Polutan | Standar deviasi sampel |
| ------- | ---------------------: |
| NO2     |     0.0000096712057877 |

## 4. Variance (Varians)

- **Penjelasan:** Merupakan rata-rata dari kuadrat selisih antara setiap titik data dengan nilai Mean. Secara matematis, varians adalah nilai kuadrat dari Standar Deviasi.
- **Perhitungan Manual (Sampel):**

  $$ s^2 = \frac{\sum\_{i=1}^{n} (x_i - \bar{x})^2}{n-1} $$

### Hasil Perhitungan

| Polutan |           Varians sampel |
| ------- | -----------------------: |
| NO2     | 0.0000000000935322213865 |

## 5. Skewness

- **Penjelasan:** Mengukur tingkat asimetri (ketidakseimbangan) distribusi data terhadap nilai rata-ratanya.
  - _Skewness = 0_: Data terdistribusi secara simetris (normal) dan berpusat di tengah.
  - _Skewness > 0 (Positif)_: Ekor distribusi memanjang ke arah kanan (menunjukkan adanya nilai ekstrem yang tinggi). Berdasarkan data NO2, distribusinya memiliki skewness positif.
  - _Skewness < 0 (Negatif)_: Ekor distribusi memanjang ke arah kiri.
- **Perhitungan Manual (Fisher-Pearson):**

  $$ Skewness = \frac{n}{(n-1)(n-2)} \sum\_{i=1}^{n} \left(\frac{x_i - \bar{x}}{s}\right)^3 $$

### Hasil Perhitungan

| Polutan |  Skewness |
| ------- | --------: |
| NO2     | -0.016182 |

## 6. Kurtosis

- **Penjelasan:** Mengukur tingkat keruncingan atau bobot ekor (_tailedness_) dari suatu distribusi data. Metrik ini menunjukkan seberapa ekstrem _outlier_ (pencilan) yang ada di dalam data. Sebagian besar perangkat lunak (_software_) secara khusus menghitung _Excess Kurtosis_.
  - _Kurtosis ≈ 0_: Distribusi normal (Mesokurtik).
  - _Kurtosis > 0_: Memiliki puncak yang tajam dengan ekor yang tebal, mengindikasikan adanya nilai ekstrem (Leptokurtik). Pada data NO2, excess kurtosis bernilai positif.
  - _Kurtosis < 0_: Puncaknya cenderung lebih datar dibandingkan distribusi normal (Platikurtik).
- **Perhitungan Manual (Excess Kurtosis Sampel):**

  $$ Kurtosis = \left[ \frac{n(n+1)}{(n-1)(n-2)(n-3)} \sum \left(\frac{x_i - \bar{x}}{s}\right)^4 \right] - \frac{3(n-1)^2}{(n-2)(n-3)} $$

### Hasil Perhitungan

| Polutan | Excess kurtosis |
| ------- | --------------: |
| NO2     |        0.117164 |

## 7. Overall Sum

- **Penjelasan:** Merupakan jumlah total dari keseluruhan nilai pada variabel yang bersangkutan.
- **Perhitungan Manual:**

  $$ Sum = \sum\_{i=1}^{n} x_i $$

### Hasil Perhitungan

| Polutan |      Overall sum |
| ------- | ---------------: |
| NO2     | 0.00702911272114 |

## 8. Metrik Kualitas / Anomali Data

Kelompok metrik ini memegang peranan krusial saat melakukan ekstraksi data mentah melalui API atau dari citra satelit, karena rentan terhadap kegagalan saat proses perekaman nilai.

- **No. missings:** Menunjukkan jumlah sel yang kosong (NULL / NA) akibat data tidak berhasil terekam pada periode waktu tertentu.
- **No. NaNs (Not a Number):** Menunjukkan jumlah entri yang dapat dibaca tetapi nilainya tidak terdefinisi secara matematis (contohnya 0/0).
- **No. +infs / No. -infs:** Menunjukkan adanya nilai batas tak terhingga.
- **Perhitungan Manual:** Menghitung frekuensi (N) kemunculan baris yang memuat nilai-nilai khusus tersebut.

### Hasil Perhitungan

| Polutan | Total baris | Valid | Missing/non-numeric | NaN | +Inf | -Inf |
| ------- | ----------: | ----: | ------------------: | --: | ---: | ---: |
| NO2     |         365 |   230 |                 135 |   0 |    0 |    0 |

## 9. Median

- _Catatan: Pada tabel sebelumnya, nilai Median belum dihitung secara menyeluruh (ditunjukkan dengan ikon tanda tanya berwarna merah)._
- **Penjelasan:** Merupakan nilai yang persis berada di tengah kumpulan data setelah diurutkan. Metrik ini kerap dimanfaatkan sebagai alternatif pengganti rata-rata (Mean) sebab Median tidak rentan terhadap pengaruh nilai _outlier_ yang ekstrem.
- **Perhitungan Manual:** Urutkan seluruh data mulai dari $X_1$ hingga $X_n$.
  - Bila jumlah observasi ($n$) bernilai ganjil: $Median = X_{(n+1)/2}$
  - Bila jumlah observasi ($n$) bernilai genap: $Median = \frac{X_{n/2} + X_{(n/2)+1}}{2}$

### Hasil Perhitungan

| Polutan |             Median |
| ------- | -----------------: |
| NO2     | 0.0000304086523784 |

# **Implementasi Analisis Data Polutan: Dari Cloud Database ke KNIME**

Panduan ini menguraikan tahapan-tahapan untuk menghubungkan database PostgreSQL di platform Aiven, melakukan inspeksi data menggunakan DBeaver, serta mengekstraksi metrik statistika deskriptif menggunakan KNIME Analytics Platform. Pada konfigurasi terbaru, layanan PostgreSQL Aiven menggunakan database `defaultdb`, host khusus Aiven, port `10316`, pengguna `avnadmin`, dan koneksi terenkripsi dengan SSL mode `require`.

## Langkah 1: Memperoleh Kredensial Database dari Aiven

Sebelum membuka koneksi melalui DBeaver atau KNIME, parameter koneksi harus diambil dari dashboard Aiven yang sedang aktif. Informasi pada dashboard menjadi acuan utama karena host dan port setiap layanan Aiven dapat berbeda.

1. Akses _dashboard_ atau console **Aiven**, lalu buka proyek yang digunakan untuk menyimpan layanan PostgreSQL.
2. Pada menu **Projects**, buka layanan PostgreSQL yang sedang aktif, kemudian pilih halaman **Overview**.
3. Buka bagian **Connection information**. Berdasarkan konfigurasi pada screenshot Anda, parameter koneksinya adalah:
   - **Database name:** `defaultdb`
   - **Host:** `pg-105bbb4-posgresqlsaindatapsl.aivencloud.com`
   - **Port:** `10316`
   - **User:** `avnadmin`
   - **Password:** gunakan password yang ditampilkan melalui ikon mata atau tombol salin pada dashboard Aiven
   - **SSL mode:** `require`
4. Password tidak perlu ditulis ke dalam laporan atau kode sumber. Masukkan password langsung pada kolom kredensial DBeaver dan KNIME, atau simpan melalui pengelola kredensial aplikasi.
5. Apabila aplikasi klien meminta sertifikat, buka bagian **CA certificate**, pilih **Show**, lalu unduh sertifikat tersebut. Sertifikat ini digunakan untuk memverifikasi keamanan koneksi PostgreSQL.

Konfigurasi tersebut dapat ditulis dalam bentuk URI PostgreSQL berikut. Bagian `<PASSWORD>` harus diganti langsung pada aplikasi dan tidak disimpan di repository:

```text
postgresql://avnadmin:<PASSWORD>@pg-105bbb4-posgresqlsaindatapsl.aivencloud.com:10316/defaultdb?sslmode=require
```

![Grafik Data](../../img/avien.png)

---

## Langkah 2: Mengonfigurasi Koneksi di DBeaver

DBeaver digunakan untuk menguji koneksi dan meninjau tabel beserta datanya secara langsung sebelum data diproses di KNIME. Pengujian ini penting karena dapat memastikan bahwa host, port, database, username, password, dan SSL sudah benar.

1. Buka aplikasi **DBeaver**, lalu pilih **New Database Connection**.
2. Pilih jenis database **PostgreSQL**, kemudian klik **Next**.
3. Pada tab **Main** atau **Connection**, isikan parameter berikut:
   - **Host:** `pg-105bbb4-posgresqlsaindatapsl.aivencloud.com`
   - **Port:** `10316`
   - **Database:** `defaultdb`
   - **Username:** `avnadmin`
   - **Password:** masukkan password dari dashboard Aiven
4. Buka pengaturan SSL pada koneksi DBeaver, lalu tetapkan mode SSL menjadi **require**. Jika DBeaver meminta CA certificate, pilih file sertifikat yang diunduh dari Aiven.
5. Klik **Test Connection**. Koneksi dianggap berhasil apabila DBeaver dapat terhubung tanpa pesan kegagalan autentikasi atau kegagalan SSL.
6. Klik **Finish** untuk menyimpan koneksi. Beri nama koneksi yang mudah dikenali, misalnya `Aiven PSD Polutan`.

Jika koneksi gagal, periksa kembali tiga hal utama: port harus `10316`, nama database harus `defaultdb`, dan SSL harus diatur ke `require`. Kesalahan satu karakter pada host atau penggunaan port lama dapat menyebabkan DBeaver tidak menemukan server.

![Grafik Data](../../img/pgadmin.png)

---

## Langkah 3: Melakukan Inspeksi Tabel Data di DBeaver

Setelah koneksi berhasil, data perlu diperiksa terlebih dahulu untuk memastikan tabel dan kolom yang digunakan memang tersedia di database `defaultdb`.

1. Pada panel **Database Navigator** DBeaver, buka koneksi `Aiven PSD Polutan`.
2. Navigasikan struktur database melalui `defaultdb` > **Schemas** > `public` > **Tables**.
3. Pilih tabel `polutan`, kemudian klik kanan dan pilih **View Data** > **All Rows**.
4. Pastikan kolom deret waktu yang terlihat adalah `date` dan `no2`. Kedua kolom tersebut menjadi dasar analisis dalam laporan ini.
5. Periksa tipe data setiap kolom. Kolom `date` harus berisi tanggal, sedangkan kolom `no2` harus dapat dibaca sebagai angka.
6. Nilai `[null]` atau sel kosong perlu dicatat sebagai _missing values_. Nilai tersebut tidak boleh langsung dianggap sebagai angka nol karena dapat mengubah rata-rata, variance, skewness, dan hasil analisis lainnya.
7. Setelah pemeriksaan selesai, catat nama tabel dan nama kolom secara tepat agar konfigurasi node KNIME menggunakan sumber data yang sama.

![Grafik Data](../../img/pg_tabel.png)

---

## Langkah 4: Menyusun Alur Kerja (Workflow) di KNIME

Beralih menuju KNIME Analytics Platform guna menarik data dari database dan melakukan perhitungan statistiknya secara otomatis.

1. Jalankan **KNIME Analytics Platform** lalu buatlah _workflow_ (alur kerja) yang baru.
2. Tarik (_drag-and-drop_) _node_ di bawah ini dari _Node Repository_ menuju ke _workspace_:
   - **PostgreSQL Connector:** Berfungsi menghubungkan KNIME dengan server Aiven.
   - **DB Table Selector:** Berfungsi untuk menyeleksi tabel di dalam database.
   - **DB Reader:** Berfungsi untuk memuat tabel ke dalam memori KNIME.
   - **Statistics:** Berfungsi untuk menghitung metrik-metrik statistik.
3. Hubungkan setiap _node_ tersebut mengikuti urutan yang telah disebutkan di atas.
4. **Konfigurasi Node:**
   - Lakukan klik ganda pada **PostgreSQL Connector**, lalu isikan _Hostname_ `pg-105bbb4-posgresqlsaindatapsl.aivencloud.com`, _Port_ `10316`, _Database name_ `defaultdb`, serta _Credentials_ (`avnadmin` dan password Aiven) yang identik dengan langkah 1 dan 2.
   - Atur SSL pada konfigurasi koneksi menjadi `require` apabila tersedia pada dialog node atau driver PostgreSQL.
   - Lakukan klik ganda pada **DB Table Selector**, kemudian pilih skema `public` serta tabel `polutan`.
5. Klik kanan pada **DB Reader** lalu pilih opsi **Execute**. Jika prosesnya berhasil, lampu indikator di bagian bawah _node_ akan berubah menjadi hijau.

![Grafik Data](../../img/k_tabel.png)

---

## Langkah 5: Membaca Output Statistika Deskriptif

Setelah data berhasil dimuat ke dalam KNIME, tahapan yang terakhir adalah menjalankan perhitungan analitiknya.

1. Klik kanan pada node **Statistics** kemudian pilih **Execute**.
2. Bila lampu indikator telah berwarna hijau, klik kanan kembali pada node **Statistics** lalu pilih menu **Statistics View** (atau ikon bergambar kaca pembesar).
3. Tabel metrik statistik akan ditampilkan, yang memuat:
   - **Min, Max, Mean:** Guna mengamati rentang serta nilai rata-rata NO2.
   - **Std. deviation & Variance:** Guna meninjau tingkat fluktuasi nilai NO2.
   - **Skewness & Kurtosis:** Guna melihat bentuk asimetri dan tingkat keberadaan nilai-nilai ekstrem (_outlier_) pada NO2.
   - **No. missings:** Menyatakan jumlah data NO2 yang kosong. Pada file final yang digunakan, seluruh 365 nilai NO2 tersedia.
   - **Histogram:** Menyajikan visualisasi sebaran data NO2.

![Grafik Data](../../img/k_hasil.png)
![Grafik Data](../../img/k_grafik.png)

### Perhitungan Manual

Perhitungan manual di bawah ini mengacu pada dataset `NO2_Kertosono_timeseries.csv`. File memiliki header `date,NO2` dan dibaca dengan `pd.read_csv`. Dataset memiliki 365 baris pada periode 31 Agustus 2025 sampai 30 Agustus 2026. Perhitungan statistik hanya menggunakan 230 nilai NO2 valid; 135 nilai kosong tidak dimasukkan ke dalam perhitungan.

### Hasil Hitung Manual NO2

Data dibaca dengan aturan berikut: kolom `date` berisi tanggal dan kolom `NO2` berisi konsentrasi. Nilai kosong diabaikan dengan `dropna()`. Setelah 230 nilai valid diurutkan, diperoleh hasil berikut:

| Metrik                 |            Hasil |
| ---------------------- | ---------------: |
| Jumlah baris ($N$)     |              365 |
| Nilai valid ($n$)      |              230 |
| Missing value          |              135 |
| Nilai minimum          | -0.0000040132004 |
| Nilai maksimum         |  0.0000562762066 |
| Jumlah nilai           | 0.00702911272114 |
| Mean                   |  0.0000305613597 |
| Median                 |  0.0000304086524 |
| Q1                     |  0.0000242778334 |
| Q3                     |  0.0000373656302 |
| Standar deviasi sampel |  0.0000096712058 |
| Varians sampel         |  0.0000000000935 |
| Skewness               | -0.0161824245556 |
| Excess kurtosis        |  0.1171638770415 |

#### 1. Minimum, Maksimum, dan Jumlah

Nilai minimum adalah nilai terkecil setelah data diurutkan, sedangkan nilai maksimum adalah nilai terbesar:

$$
Min = X_1 = -0.0000040132004
$$

$$
Max = X_n = 0.0000562762066
$$

Jumlah seluruh nilai NO2 adalah:

$$
\sum_{i=1}^{n}x_i = 0.00702911272114
$$

#### 2. Mean

Mean dihitung dengan membagi jumlah seluruh nilai dengan jumlah data:

$$
\bar{x} = \frac{\sum_{i=1}^{n}x_i}{n}
            = \frac{0.00702911272114}{230}
            = 0.0000305613596571
$$

#### 3. Median

Karena jumlah data valid adalah 230, median dihitung sebagai rata-rata dua nilai tengah:

$$
	ext{Posisi median} = \frac{230}{2} = 115,\quad 116
$$

Nilai pada posisi ke-115 dan ke-116 setelah diurutkan adalah:

$$
Median = \frac{X_{115}+X_{116}}{2} = 0.0000304086523784
$$

#### 4. Varians dan Standar Deviasi

Varians sampel dihitung dari jumlah kuadrat selisih setiap nilai terhadap mean:

$$
s^2 = \frac{\sum_{i=1}^{n}(x_i-\bar{x})^2}{n-1}
      = 0.0000000000935322213865
$$

Standar deviasi adalah akar kuadrat varians:

$$
s = \sqrt{s^2}
   = \sqrt{0.0000000000935322213865}
   = 0.0000096712057877
$$

Nilai standar deviasi yang besar menunjukkan bahwa nilai NO2 memiliki rentang penyebaran yang lebar dari mean. Hal ini juga dipengaruhi oleh beberapa nilai tinggi pada dataset.

#### 5. Skewness dan Excess Kurtosis

Skewness menggunakan rumus Fisher-Pearson:

$$
Skewness = \frac{n}{(n-1)(n-2)}
\sum_{i=1}^{n}\left(\frac{x_i-\bar{x}}{s}\right)^3
$$

Dengan data ini, diperoleh:

$$
Skewness = -0.0161824245555655
$$

Nilai skewness yang sedikit negatif menunjukkan distribusi NO2 relatif simetris dengan kecenderungan ekor kiri yang sangat kecil.

Excess kurtosis dihitung dengan rumus:

$$
Kurtosis = \left[\frac{n(n+1)}{(n-1)(n-2)(n-3)}
\sum_{i=1}^{n}\left(\frac{x_i-\bar{x}}{s}\right)^4\right]
- \frac{3(n-1)^2}{(n-2)(n-3)}
$$

Hasil perhitungannya adalah:

$$
Excess\ kurtosis = 0.11716387704150044
$$

#### 6. Deteksi Outlier dengan IQR

Kuartil pertama dan kuartil ketiga dari data NO2 adalah:

$$
Q1 = 0.0000242778334268
$$

$$
Q3 = 0.0000373656301917
$$

Rentang interkuartil dihitung dengan:

$$
IQR = Q3-Q1
      = 0.0000373656301917-0.0000242778334268
      = 0.0000130877967649
$$

Batas bawah dan batas atas ditentukan dengan faktor $1.5$:

$$
	ext{Batas bawah} = Q1-1.5(IQR)
                           = 0.0000242778334268-1.5(0.0000130877967649)
                           = 0.0000046461382794
$$

$$
	ext{Batas atas} = Q3+1.5(IQR)
                         = 0.0000373656301917+1.5(0.0000130877967649)
                         = 0.0000569973253391
$$

Nilai NO2 yang lebih kecil dari batas bawah atau lebih besar dari batas atas dikategorikan sebagai outlier. Tidak ada nilai yang lebih besar dari batas atas. Terdapat satu nilai yang lebih kecil dari batas bawah:

| Tanggal    |        Nilai NO2 |
| ---------- | ---------------: |
| 2026-01-30 | -0.0000040132004 |

Jadi, jumlah outlier berdasarkan metode IQR adalah **1**. Nilai `NaN` tidak dihitung sebagai outlier karena bukan nilai numerik yang dapat dibandingkan dengan batas IQR.

<!-- Arsip contoh perhitungan lama dihapus dari tampilan laporan.
5. Overall Sum
   $$
   \begin{aligned}
   OS &= \bar{x} \times n \\
   \\
   OS &= 1.98E10 \times 309 \\
   \\
   OS &= 6.1182E12
   \end{aligned}
   $$

## Contoh Rumus Kolom `NO2`

Contoh berikut menjelaskan bentuk penerapan rumus. Angka hasil resmi untuk dataset terbaru adalah yang tercantum pada tabel ringkasan di atas.

Diketahui:

$$
n &= 365 - 183 = 182 \\
\bar{x} &= 3.4274E-05
$$

1. Standar Deviasi
   Std. Dev. yang tercatat pada tabel adalah $s = 1.43E11$, sehingga jumlah kuadrat deviasi dapat ditelusuri kembali:

   $$
   \sum_{i=1}^{n}(x_i-\bar{x})^2 &= s^2 \times (n-1) \\
   \\
   \sum_{i=1}^{n}(x_i-\bar{x})^2 &= (1.43E11)^2 \times (87-1) \\
   \\
   \sum_{i=1}^{n}(x_i-\bar{x})^2 &= 1.758614E24
   $$

   $$
   s &= \sqrt{\frac{1.758614E24}{87-1}}\\
   \\
   s &= \sqrt{2.0449E22}\\
   \\
   s &= 1.43E11
   $$

2. Variansi

   $$
   v &= s^2\\
   \\
   v &= (1.43E11)^2\\
   \\
   v &= 2.0449E22
   $$

3. Skewness

   $$
   Skewness &= \underbrace{\frac{n}{(n-1)(n-2)}}_{A} \underbrace{\sum_{i=1}^{n}\left(\frac{x_i-\bar{x}}{s}\right)^3}_{B}\\
   \\
   A &= \frac{87}{(87-1)(87-2)} = \frac{87}{7310}\\
   \\
   A &= 0.0119015\\
   \\
   B &= \left(\frac{x_1 - 1.31E11}{1.43E11}\right)^3 + \left(\frac{x_2 - 1.31E11}{1.43E11}\right)^3 + \ldots + \left(\frac{x_n - 1.31E11}{1.43E11}\right)^3\\
   \\
   B &= \frac{Skewness}{A} = \frac{1.0242}{0.0119015}\\
   \\
   B &= 86.0563\\
   \\
   Skewness &= 0.0119015 \times 86.0563\\
   \\
   Skewness &= 1.0242
   $$

4. Kurtosis

   $$
   A &= \frac{87(87+1)}{(87-1)(87-2)(87-3)}\\
   \\
   A &= \frac{7656}{614040}\\
   \\
   A &= 0.0124682 \\
   \\
   C &= \frac{3(87-1)^2}{(87-2)(87-3)}\\
   \\
   C &= \frac{22188}{7140}\\
   \\
   C &= 3.107563\\
   \\
   B &= \left(\frac{x_1 - 1.31E11}{1.43E11}\right)^4 + \left(\frac{x_2 - 1.31E11}{1.43E11}\right)^4 + \ldots + \left(\frac{x_n - 1.31E11}{1.43E11}\right)^4\\
   \\
   B &= \frac{Kurtosis + C}{A} = \frac{-0.3149 + 3.107563}{0.0124682}\\
   \\
   B &= 223.9821\\
   \\
   Kurtosis &= 0.0124682 \times 223.9821 - 3.107563\\
   \\
   Kurtosis &= -0.3149
   $$

5. Overall Sum
   $$
   \begin{aligned}
   OS &= \bar{x} \times n \\
   \\
   OS &= 1.31E11 \times 87 \\
   \\
   OS &= 1.1397E13
   \end{aligned}
   $$
-->
