# Panduan Deployment Aplikasi Streamlit: Klasifikasi LULC Jawa Timur

Dokumentasi ini menjelaskan langkah-langkah komprehensif implementasi dan deployment aplikasi web interaktif **Klasifikasi Spasial Tutupan Lahan (LULC) Jawa Timur** menggunakan platform **Streamlit Community Cloud** yang terhubung langsung dengan repositori **GitHub**.

---

## Tautan Aplikasi & Repositori

- **URL Aplikasi Live (Streamlit Cloud):** [https://tugasutspsd.streamlit.app/](https://tugasutspsd.streamlit.app/)
- **Repositori GitHub:** [https://github.com/Tulsoppp/PSD](https://github.com/Tulsoppp/PSD)
- **Path Berkas Aplikasi Utama:** [`Tugas/UTS/streamlit_app.py`](https://github.com/Tulsoppp/PSD/blob/main/Tugas/UTS/streamlit_app.py)

---

## Arsitektur Sistem & Sumber Data

Dashboard membaca data dan geometri secara langsung dari berkas proyek. Berkas CSV merupakan sumber data piksel, sementara batas administrasi dan arsip ZIP menyediakan geometri untuk penyaringan data dan tampilan peta.

| Berkas | Lokasi di repositori | Kegunaan |
|---|---|---|
| `streamlit_app.py` | `Tugas/UTS/streamlit_app.py` | Antarmuka, pembersihan data, pemetaan, dan evaluasi model |
| `piksel_s2_JTM.csv` | `Tugas/UTS/piksel_s2_JTM.csv` | Sampel piksel Sentinel-2A, koordinat, label, band, dan indeks |
| `batas_jawa_timur.geojson` | `Tugas/UTS/batas_jawa_timur.geojson` | Batas administrasi untuk penyaringan sampel |
| `bangunan.zip`, `Danau.zip`, `Lahan Hijau.zip`, `Laut.zip`, `Magruve.zip`, `sawah.zip` | `DIGITASI/` | Poligon digitasi asli yang ditampilkan pada peta |
| `requirements.txt` | Akar repositori | Daftar pustaka Python proyek |
| `.streamlit/config.toml` | `.streamlit/config.toml` | Konfigurasi tema Streamlit |

Aplikasi menggunakan sembilan fitur Sentinel-2A: `B02`, `B03`, `B04`, `B08`, `B11`, `NDVI`, `NDWI`, `MNDWI`, dan `NDBI`. Piksel non-Laut di luar batas Jawa Timur disaring. Poligon Laut `Laut_0000` sampai `Laut_0018` dikecualikan karena berada melewati batas wilayah; poligon Laut lainnya tetap dipertahankan. Aturan pengecualian yang sama digunakan pada halaman business understanding sampai visualisasi peta, sementara CSV sumber tidak diubah. Geometri peta berasal dari poligon digitasi, bukan marker titik.

Model **Gaussian Naive Bayes** dan **K-Nearest Neighbors (KNN)** dilatih dan dievaluasi oleh aplikasi saat dijalankan. Pengguna dapat mengubah jumlah tetangga KNN dan filter kelas melalui panel aplikasi. Dashboard tidak bergantung pada berkas metrik atau prediksi CSV terpisah.

### Struktur berkas yang diperlukan

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
│       ├── piksel_s2_JTM.csv
│       └── streamlit_app.py
└── requirements.txt
```

Path tersebut penting: aplikasi mencari CSV dan GeoJSON di direktori yang sama dengan `streamlit_app.py`, serta mencari arsip digitasi di folder `DIGITASI` pada akar repositori.

---

## Persiapan Data Besar (Git LFS) untuk GitHub

CSV `Tugas/UTS/piksel_s2_JTM.csv` berukuran sekitar **117 MiB**. GitHub menolak berkas tunggal yang lebih besar dari 100 MiB jika diunggah sebagai berkas Git biasa. Gunakan **Git Large File Storage (Git LFS)** untuk CSV ini. Streamlit Community Cloud mendukung berkas yang disimpan dengan Git LFS.

Pastikan Git LFS sudah terpasang di komputer, kemudian jalankan perintah berikut dari akar repositori:

```bash
git lfs install
git lfs track "Tugas/UTS/piksel_s2_JTM.csv"
git add .gitattributes
```

Perintah tersebut membuat aturan LFS sebelum CSV ditambahkan ke Git. Pastikan akun GitHub memiliki kuota Git LFS yang cukup, lalu periksa bahwa CSV ditangani oleh LFS:

```bash
git check-attr filter -- "Tugas/UTS/piksel_s2_JTM.csv"
```

Hasil untuk atribut `filter` seharusnya menunjukkan `lfs`. Jika CSV sebelumnya sudah pernah ditambahkan ke Git sebagai berkas biasa, mengaktifkan LFS saja tidak mengubah riwayat commit lama; migrasikan berkas tersebut ke LFS sebelum deployment.

---

## Panduan Langkah-demi-Langkah Deployment

### Langkah 1: Periksa Dependensi dan Berkas

Repositori ini sudah memiliki `requirements.txt` di akar proyek. Berkas tersebut mencakup pustaka yang digunakan dashboard, termasuk Streamlit, pandas, NumPy, Matplotlib, scikit-learn, Folium, GeoPandas, dan Shapely. Community Cloud dapat menggunakan berkas dependensi di akar repositori meskipun berkas aplikasi berada di subdirektori.

Sebelum deployment, pastikan:

1. Seluruh berkas pada tabel sumber data tersedia pada path yang benar.
2. Keenam arsip ZIP digitasi dan CSV LFS ikut masuk ke repositori.
3. `.streamlit/config.toml` berada di akar repositori, bukan di dalam `Tugas/UTS/`.
4. Perubahan pada `requirements.txt` hanya berisi dependensi yang memang ingin digunakan untuk deployment.
5. Berkas CSV tidak tersimpan sebagai berkas Git biasa berukuran lebih dari 100 MiB.

---

### Langkah 2: Commit dan Unggah Berkas Deployment

Periksa perubahan lokal terlebih dahulu agar berkas lain yang tidak terkait tidak ikut ter-commit:

```bash
git status --short
```

Setelah Git LFS dikonfigurasi, tambahkan hanya berkas deployment yang diperlukan. Tinjau daftar staging sebelum membuat commit:

```bash
git add .gitattributes requirements.txt .streamlit/config.toml
git add Tugas/UTS/panduan.md Tugas/UTS/streamlit_app.py
git add Tugas/UTS/piksel_s2_JTM.csv Tugas/UTS/batas_jawa_timur.geojson
git add "DIGITASI/bangunan.zip" "DIGITASI/Danau.zip" "DIGITASI/Lahan Hijau.zip"
git add "DIGITASI/Laut.zip" "DIGITASI/Magruve.zip" "DIGITASI/sawah.zip"
git status --short
git lfs ls-files
```

Pastikan `piksel_s2_JTM.csv` tercantum pada keluaran `git lfs ls-files` dan tidak ada berkas proyek lain yang tidak dimaksudkan untuk diunggah. Lalu commit dan push ke branch `main`:

```bash
git commit -m "feat: prepare LULC dashboard for deployment"
git push origin main
```

Jika perubahan Anda berada di branch lain, push branch tersebut dan pilih branch yang sama saat membuat aplikasi. Jangan mengganti atau membuang perubahan lokal lain yang belum di-commit.

---

### Langkah 3: Membuat Deployment Aplikasi Baru di Streamlit Cloud

1. Buka [share.streamlit.io](https://share.streamlit.io/) dan masuk menggunakan akun GitHub yang memiliki akses ke repositori.
2. Pilih **Create app**.
3. Isi konfigurasi:
   - **Repository:** `Tulsoppp/PSD`
   - **Branch:** `main` (atau branch yang telah Anda push)
   - **Main file path:** `Tugas/UTS/streamlit_app.py`
   - **App URL:** pilih nama yang tersedia, misalnya `tugasutspsd` (alamat aplikasi: [https://tugasutspsd.streamlit.app/](https://tugasutspsd.streamlit.app/)).
4. Buka **Advanced settings** bila tersedia dan pilih versi Python yang sesuai dengan lingkungan pengembangan proyek, yaitu Python 3.12.
5. Pilih **Deploy**.

Streamlit Community Cloud menjalankan aplikasi dari akar repositori. Aplikasi menggunakan path relatif terhadap berkas skrip untuk dataset dan batas, sehingga path pada konfigurasi di atas harus tetap sesuai struktur repositori.

---

### Langkah 4: Proses Build & Verifikasi Cloud

Setelah proses build selesai, buka URL aplikasi dan pastikan:

- Ringkasan dashboard dan data sampel berhasil dimuat.
- Filter kelas, pilihan jumlah tetangga KNN, dan jumlah poligon pada peta berfungsi.
- Evaluasi Gaussian Naive Bayes dan KNN menampilkan metrik serta confusion matrix.
- Peta menampilkan citra satelit Esri dan poligon digitasi.
- Tidak ada pesan bahwa CSV, GeoJSON, atau arsip poligon tidak ditemukan.

Peta satelit menggunakan tile Esri melalui internet; layer citra dan referensi peta memerlukan koneksi keluar pada saat aplikasi digunakan.

Jika build gagal, buka **Manage app** lalu periksa log. Pesan kesalahan mengenai berkas data biasanya menandakan path atau berkas belum diunggah; kegagalan instalasi pustaka biasanya menandakan masalah pada dependensi atau versi Python.

---

## Siklus Pembaruan Otomatis (CI/CD Continuous Deployment)

Untuk menerbitkan perubahan berikutnya:

1. Perbarui kode atau data di branch deployment.
2. Jika memperbarui CSV besar, pertahankan pelacakan Git LFS.
3. Commit hanya berkas yang relevan dan push ke GitHub.
4. Streamlit Community Cloud akan mendeteksi commit baru dan membangun ulang aplikasi.

---

## Referensi

- [Streamlit Community Cloud: Deploy your app](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app)
- [Streamlit Community Cloud: File organization](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/file-organization)
- [GitHub Docs: About large files on GitHub](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github)