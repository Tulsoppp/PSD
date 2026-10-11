# Panduan Deployment Aplikasi Streamlit: Klasifikasi LULC Jawa Timur (KNN)

Dokumentasi ini menjelaskan langkah-langkah komprehensif implementasi dan deployment aplikasi web interaktif **Klasifikasi Spasial Tutupan Lahan (LULC) Jawa Timur** berbasis algoritma **K-Nearest Neighbors (KNN)** menggunakan platform **Streamlit Community Cloud** yang terhubung langsung dengan repositori **GitHub**.

---

## Tautan Aplikasi & Repositori

- **URL Aplikasi Live (Streamlit Cloud):** https://tugasutspsd.streamlit.app/
- **Repositori GitHub:** https://github.com/Tulsoppp/PSD
- **Path Berkas Aplikasi Utama:** [`Tugas/UTS/streamlit_app.py`](https://github.com/Tulsoppp/PSD/blob/main/Tugas/UTS/streamlit_app.py)

---

## Arsitektur Sistem & Sumber Data

Dashboard membaca data citra dan geometri langsung dari repositori proyek:

| Berkas | Lokasi di repositori | Kegunaan |
|---|---|---|
| `streamlit_app.py` | `Tugas/UTS/streamlit_app.py` | Antarmuka web, pemrosesan data, pemodelan KNN, dan pemetaan interaktif |
| `piksel_s2_JTM.csv` | `Tugas/UTS/piksel_s2_JTM.csv` | Sampel piksel Sentinel-2A (573.268 baris valid setelah penyaringan laut 0-18) |
| `batas_jawa_timur.geojson` | `Tugas/UTS/batas_jawa_timur.geojson` | Batas administrasi Provinsi Jawa Timur untuk validasi spasial |
| `jatim_250m.tif` | `Tugas/UTS/jatim_250m.tif` | Citra komposit openEO resolusi 250m untuk inferensi tutupan lahan se-Jawa Timur |
| `requirements.txt` | Akar repositori | Daftar pustaka Python yang dibutuhkan aplikasi |
| `.streamlit/config.toml` | `.streamlit/config.toml` | Konfigurasi tema antarmuka Streamlit |

Sampel poligon Laut nomor 0 sampai 18 (`Laut_0000` hingga `Laut_0018`) sebanyak 58.000 piksel dikeluarkan dari data analisis karena melewati batas administrasi Jawa Timur. Model **K-Nearest Neighbors (KNN, $k=5$)** dilatih dan dievaluasi secara dinamis oleh aplikasi. Pengguna dapat memilih jumlah tetangga $k$ melalui panel navigasi samping (*sidebar*) serta memfilter kelas tutupan lahan pada peta dan tabel data.

### Struktur Berkas yang Diperlukan

```text
PSD/
├── .streamlit/
│   └── config.toml
├── DIGITASI/
│   ├── bangunan.zip
│   ├── Danau.zip
│   ├── Lahan Hijau.zip
│   ├── Laut.zip
│   ├── Magruve.zip
│   └── sawah.zip
├── Tugas/
│   └── UTS/
│       ├── batas_jawa_timur.geojson
│       ├── jatim_250m.tif
│       ├── piksel_s2_JTM.csv
│       ├── test.ipynb
│       ├── klasifikasi-jawatimur.md
│       ├── bab.md
│       ├── business-understanding.md
│       ├── data-understanding.md
│       ├── eda.md
│       ├── preprocessing.md
│       ├── pemodelan-evaluasi.md
│       ├── visualisasi-peta.md
│       ├── panduan.md
│       └── streamlit_app.py
└── requirements.txt
```

---

## Persiapan Data Besar (Git LFS) untuk GitHub

File CSV `Tugas/UTS/piksel_s2_JTM.csv` berukuran sekitar **117 MiB**. GitHub membatasi unggahan berkas tunggal maksimal 100 MiB untuk berkas Git biasa. Oleh karena itu, berkas ini dikelola menggunakan **Git Large File Storage (Git LFS)**:

```bash
git lfs install
git lfs track "Tugas/UTS/piksel_s2_JTM.csv"
git add .gitattributes
```

Verifikasi bahwa pelacakan LFS aktif:

```bash
git check-attr filter -- "Tugas/UTS/piksel_s2_JTM.csv"
```

Output yang diharapkan adalah `filter: lfs`.

---

## Panduan Langkah-demi-Langkah Deployment

### Langkah 1: Periksa Dependensi dan Berkas
Pastikan seluruh paket yang dibutuhkan tercantum dalam `requirements.txt`:
```text
streamlit
pandas
numpy
scikit-learn
matplotlib
seaborn
folium
geopandas
shapely
rasterio
```

### Langkah 2: Commit dan Push ke GitHub
```bash
git add .
git commit -m "feat: update LULC spatial classification with KNN model and interactive maps without sea 0-18"
git push origin main
```

### Langkah 3: Konfigurasi Deployment di Streamlit Community Cloud
1. Kunjungi https://share.streamlit.io/ dan login dengan akun GitHub.
2. Klik tombol **New app** / **Create app**.
3. Masukkan konfigurasi berikut:
   - **Repository:** `Tulsoppp/PSD`
   - **Branch:** `main`
   - **Main file path:** `Tugas/UTS/streamlit_app.py`
   - **App URL:** `tugasutspsd` (sehingga URL menjadi `https://tugasutspsd.streamlit.app/`)
4. Pada **Advanced Settings**, pilih Python 3.12 (atau versi yang sesuai).
5. Klik **Deploy**.

---

## Panduan Menjalankan Secara Lokal

Untuk menguji dan menjalankan aplikasi Streamlit di komputer lokal Anda:

```bash
# Jalankan server lokal Streamlit
streamlit run Tugas/UTS/streamlit_app.py
```

Setelah server aktif, browser akan otomatis membuka alamat lokal: `http://localhost:8501`.