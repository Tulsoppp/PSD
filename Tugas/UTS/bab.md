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

# Klasifikasi Penggunaan dan Tutupan Lahan di Jawa Timur

Selamat datang di proyek klasifikasi penggunaan dan tutupan lahan (*Land Use / Land Cover* atau LULC). Proyek ini memanfaatkan citra satelit **Sentinel-2A** dan metode *machine learning* untuk mengelompokkan sampel wilayah ke dalam kelas tutupan lahan.

Informasi tutupan lahan berguna untuk memahami karakteristik permukaan bumi, mendukung analisis keruangan, serta membantu perencanaan dan pengelolaan lingkungan. Pengamatan secara manual terhadap citra berukuran besar memerlukan waktu dan dapat menjadi tidak konsisten. Analisis data spektral dan algoritma klasifikasi dapat membantu proses tersebut dilakukan secara lebih sistematis.

Dataset proyek, `piksel_s2_JTM.csv`, berisi hasil ekstraksi sampel piksel Sentinel-2A. Data mencakup lima band spektral, yaitu B02, B03, B04, B08, dan B11, serta empat indeks turunan: NDVI, NDWI, MNDWI, dan NDBI. Koordinat geografis dan label kelas turut digunakan untuk memahami lokasi serta kategori setiap sampel. Dataset yang dianalisis memiliki 631.268 baris piksel dan 19 kolom.

Kelas yang dianalisis adalah **Bangunan, Danau, Hutan, Laut, Mangrove, dan Sawah**. Karena banyak piksel dapat berasal dari poligon sampel yang sama, data diringkas berdasarkan `poligon_id` sebelum pemodelan. Langkah ini menjaga agar piksel dari satu poligon tidak terbagi sekaligus ke data latih dan data uji.

Proyek ini membandingkan dua algoritma klasifikasi, yaitu **Gaussian Naive Bayes** dan **K-Nearest Neighbors (KNN)**. Fitur distandarkan sebelum model dilatih, lalu kinerja dievaluasi menggunakan akurasi serta *precision*, *recall*, dan *F1-score*. Pada hasil pengujian yang tersedia, Gaussian Naive Bayes memperoleh akurasi 70,00%, sedangkan KNN memperoleh 75,56%. Angka tersebut berasal dari satu pembagian data uji dan tidak dengan sendirinya menjamin kinerja yang sama pada wilayah atau sampel lain.

Hasil juga ditampilkan melalui grafik distribusi jumlah piksel per kelas, boxplot nilai NDVI, laporan evaluasi model, dan peta interaktif yang memperlihatkan lokasi sampel. Peta tersebut menunjukkan titik sampel berdasarkan label dataset; peta ini bukan prediksi tutupan lahan untuk seluruh piksel citra.

Analisis ini merupakan demonstrasi alur sains data dari pemahaman masalah dan data, eksplorasi, preprocessing, pemodelan, evaluasi, hingga penyajian hasil. Interpretasi kelas dari citra satelit memiliki keterbatasan, antara lain resolusi spasial, kondisi atmosfer, kualitas sampel, dan kemiripan karakteristik spektral antar kelas. Karena itu, hasil klasifikasi sebaiknya dipandang sebagai analisis berbasis sampel dan dilengkapi validasi lapangan atau sumber data lain sebelum digunakan untuk keputusan operasional.

Anda dapat menelusuri tahapan proyek melalui halaman berikut:

1. **Business Understanding:** Menjelaskan latar belakang, tujuan, ruang lingkup, dan pertanyaan analisis klasifikasi tutupan lahan.
2. **Data Understanding:** Menguraikan sumber, struktur, variabel, dan pemeriksaan dataset Sentinel-2A.
3. **Exploratory Data Analysis (EDA):** Menampilkan distribusi jumlah piksel tiap kelas dan distribusi NDVI berdasarkan kelas.
4. **Preprocessing Data:** Membersihkan nilai yang tidak valid, merangkum data per poligon, membagi data latih dan uji, serta melakukan standarisasi.
5. **Pemodelan dan Evaluasi:** Melatih Gaussian Naive Bayes dan KNN, kemudian membandingkan metrik hasil klasifikasi.
6. **Visualisasi Peta:** Menampilkan lokasi sampel per kelas pada peta interaktif Folium.