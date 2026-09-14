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

# Polutan di Kecamatan Bandarkedungmulyo

Selamat datang di sub-bab **Polutan di Kecamatan Bandarkedungmulyo**. Bagian ini merupakan studi kasus sains data yang berfokus pada pemantauan dan analisis kualitas udara, khususnya konsentrasi gas polutan di Kecamatan Bandarkedungmulyo, Kabupaten Jombang, Jawa Timur.

Kecamatan Bandarkedungmulyo merupakan salah satu kecamatan di Kabupaten Jombang yang memiliki permukiman, lahan pertanian, jaringan jalan, dan berbagai aktivitas masyarakat. Keragaman aktivitas tersebut membuat kualitas udara perlu diamati secara berkala. Kendaraan bermotor, pembakaran bahan bakar, pembakaran sampah, aktivitas pertanian, serta kegiatan ekonomi dapat menghasilkan emisi yang memengaruhi kondisi atmosfer. Analisis berbasis data membantu melihat perubahan polutan secara lebih terukur dan memberikan gambaran mengenai pola kualitas udara di wilayah penelitian dari waktu ke waktu.

Pemantauan ini tidak dimaksudkan untuk menggantikan pengukuran langsung di stasiun pemantauan kualitas udara. Sebaliknya, data satelit digunakan sebagai sumber informasi spasial dan temporal yang dapat melengkapi pengamatan lapangan. Pada proyek ini, koordinat _Area of Interest_ (AOI) digunakan untuk merangkum nilai beberapa piksel menjadi nilai rata-rata harian yang mewakili Kecamatan Bandarkedungmulyo. Hasilnya dapat digunakan untuk membandingkan kondisi antarwaktu serta menentukan periode yang perlu dikaji lebih lanjut menggunakan data lapangan dan meteorologi.

Melalui pemanfaatan data citra satelit **Copernicus Sentinel-5P**, proyek ini melacak fluktuasi konsentrasi tiga jenis gas polutan utama yang sangat berdampak pada kesehatan lingkungan, yaitu:

- **Karbon Monoksida (CO)**
- **Belerang Dioksida (SO₂)**
- **Nitrogen Dioksida (NO₂)**

Ketiga polutan tersebut memiliki karakteristik dan sumber emisi yang berbeda. **CO** merupakan gas yang dihasilkan dari pembakaran tidak sempurna, misalnya dari kendaraan bermotor, penggunaan bahan bakar padat, atau pembakaran terbuka. **SO₂** umumnya berhubungan dengan pembakaran bahan bakar yang mengandung sulfur dan dapat memicu iritasi saluran pernapasan serta pembentukan hujan asam. Sementara itu, **NO₂** banyak berkaitan dengan pembakaran bahan bakar pada kendaraan dan kegiatan industri serta dapat berkontribusi terhadap pembentukan partikulat sekunder.

Nilai yang diperoleh dari Sentinel-5P perlu dipahami sebagai pengukuran kolom atmosfer, sehingga nilainya tidak selalu sama dengan konsentrasi udara yang dihirup manusia di permukaan. Awan, resolusi spasial, kondisi cuaca, arah angin, dan waktu perekaman dapat memengaruhi hasil pengamatan. Oleh karena itu, interpretasi data dilakukan dengan melihat pola dan perubahan relatif, bukan hanya satu nilai pada satu lokasi. Hasil analisis juga sebaiknya dibandingkan dengan data stasiun darat, informasi cuaca, dan catatan aktivitas lokal apabila tersedia.

Proyek ini mendemonstrasikan siklus utuh dari sains data (_Data Science Lifecycle_), mulai dari memahami masalah lingkungan di Kecamatan Bandarkedungmulyo, menentukan kebutuhan analisis, mengumpulkan data, membersihkan data, melakukan eksplorasi, hingga menyajikan hasil dalam bentuk visualisasi dan kesimpulan. Data crawling yang digunakan mencakup periode sekitar satu tahun pada 2025–2026. Setiap tahap dirancang agar proses analisis dapat ditelusuri, diulang, dan dikembangkan untuk pemantauan pada periode berikutnya.

Secara umum, analisis ini dapat membantu menjawab beberapa pertanyaan penting: bagaimana perubahan konsentrasi CO, SO₂, dan NO₂ dari waktu ke waktu; apakah terdapat periode dengan kenaikan atau penurunan yang menonjol; kapan terjadi anomali; serta faktor aktivitas dan kondisi atmosfer apa yang mungkin berkaitan dengan perubahan tersebut. Karena analisis berfokus pada satu AOI, hasil utama yang dibahas adalah pola temporal di Bandarkedungmulyo, bukan perbedaan antarwilayah. Jawaban atas pertanyaan ini dapat menjadi bahan awal bagi edukasi masyarakat, pengelolaan lingkungan, dan perencanaan pengukuran kualitas udara yang lebih terarah.

Anda dapat menelusuri tahapan-tahapan proyek ini melalui halaman-halaman berikut:

1. **Business Understanding:** Membahas latar belakang, rumusan masalah, tujuan, dan manfaat mengapa analisis kualitas udara ini sangat penting untuk dilakukan.
2. **Data Understanding:** Menjelaskan langkah-langkah teknis pengumpulan data (_crawling_) dari satelit, definisi AOI Kecamatan Bandarkedungmulyo, karakteristik variabel polutan, hingga ekstraksi informasi spasial menjadi dataset tabular (_Time Series_) yang siap dianalisis.
3. **Data Preparation:** Menjelaskan proses pemeriksaan kualitas data, penanganan nilai kosong, penyesuaian format tanggal, dan penyiapan data agar dapat digunakan secara konsisten.
4. **Exploratory Data Analysis:** Menampilkan pola, tren, perbandingan, dan hubungan antarvariabel polutan melalui tabel serta visualisasi.
5. **Evaluation dan Conclusion:** Merangkum temuan utama, keterbatasan penggunaan data satelit, serta peluang pengembangan analisis kualitas udara di Kecamatan Bandarkedungmulyo.
