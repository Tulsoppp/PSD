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

# Polutan di Kabupaten Jombang

Selamat datang di sub-bab **Polutan di Kabupaten Jombang**. Bagian ini merupakan studi kasus sains data yang berfokus pada pemantauan dan analisis kualitas udara, khususnya konsentrasi gas polutan di wilayah Kabupaten Jombang, Jawa Timur.

Kabupaten Jombang merupakan wilayah yang memiliki perpaduan kawasan perkotaan, permukiman, lahan pertanian, kawasan industri, serta jaringan jalan yang menghubungkan berbagai daerah di Jawa Timur. Keragaman aktivitas tersebut membuat kualitas udara perlu diamati secara berkala. Pertumbuhan kendaraan bermotor, kegiatan industri, pembakaran bahan bakar, pembakaran sampah, dan aktivitas pertanian dapat menghasilkan emisi yang memengaruhi kondisi atmosfer. Analisis berbasis data membantu melihat perubahan polutan secara lebih terukur dan memberikan gambaran mengenai pola kualitas udara dari waktu ke waktu.

Pemantauan ini tidak dimaksudkan untuk menggantikan pengukuran langsung di stasiun pemantauan kualitas udara. Sebaliknya, data satelit digunakan sebagai sumber informasi spasial dan temporal yang dapat melengkapi pengamatan lapangan. Dengan cakupan wilayah yang luas, citra satelit dapat membantu mengidentifikasi kecenderungan umum konsentrasi polutan di Kabupaten Jombang, membandingkan kondisi antarwaktu, serta menjadi dasar untuk menentukan area yang perlu dikaji lebih lanjut.

Melalui pemanfaatan data citra satelit **Copernicus Sentinel-5P**, proyek ini melacak fluktuasi konsentrasi tiga jenis gas polutan utama yang sangat berdampak pada kesehatan lingkungan, yaitu:

- **Nitrogen Dioksida (NO₂)**
- **Karbon Monoksida (CO)**
- **Belerang Dioksida (SO₂)**

Ketiga polutan tersebut memiliki karakteristik dan sumber emisi yang berbeda. **NO₂** banyak berkaitan dengan pembakaran bahan bakar pada kendaraan dan kegiatan industri, serta dapat berkontribusi terhadap pembentukan ozon permukaan dan partikulat sekunder. **CO** merupakan gas yang dihasilkan dari pembakaran tidak sempurna, misalnya dari kendaraan bermotor, penggunaan bahan bakar padat, atau pembakaran terbuka. Sementara itu, **SO₂** umumnya berhubungan dengan pembakaran bahan bakar yang mengandung sulfur dan dapat memicu iritasi saluran pernapasan serta pembentukan hujan asam.

Nilai yang diperoleh dari Sentinel-5P perlu dipahami sebagai pengukuran kolom atmosfer, sehingga nilainya tidak selalu sama dengan konsentrasi udara yang dihirup manusia di permukaan. Awan, resolusi spasial, kondisi cuaca, arah angin, dan waktu perekaman dapat memengaruhi hasil pengamatan. Oleh karena itu, interpretasi data dilakukan dengan melihat pola dan perubahan relatif, bukan hanya satu nilai pada satu lokasi. Hasil analisis juga sebaiknya dibandingkan dengan data stasiun darat, informasi cuaca, dan catatan aktivitas lokal apabila tersedia.

Proyek ini mendemonstrasikan siklus utuh dari sains data (_Data Science Lifecycle_), mulai dari memahami masalah lingkungan di Kabupaten Jombang, menentukan kebutuhan analisis, mengumpulkan data, membersihkan data, melakukan eksplorasi, hingga menyajikan hasil dalam bentuk visualisasi dan kesimpulan. Setiap tahap dirancang agar proses analisis dapat ditelusuri, diulang, dan dikembangkan untuk pemantauan pada periode berikutnya.

Secara umum, analisis ini dapat membantu menjawab beberapa pertanyaan penting: bagaimana perubahan konsentrasi NO₂, CO, dan SO₂ dari waktu ke waktu; apakah terdapat periode dengan kenaikan atau penurunan yang menonjol; bagaimana perbedaan pola antarwilayah; serta faktor aktivitas dan kondisi atmosfer apa yang mungkin berkaitan dengan perubahan tersebut. Jawaban atas pertanyaan ini dapat menjadi bahan awal bagi edukasi masyarakat, pengelolaan lingkungan, dan perencanaan pengukuran kualitas udara yang lebih terarah.

Anda dapat menelusuri tahapan-tahapan proyek ini melalui halaman-halaman berikut:

1. **Business Understanding:** Membahas latar belakang, rumusan masalah, tujuan, dan manfaat mengapa analisis kualitas udara ini sangat penting untuk dilakukan.
2. **Data Understanding:** Menjelaskan langkah-langkah teknis pengumpulan data (_crawling_) dari satelit, definisi wilayah Kabupaten Jombang, karakteristik variabel polutan, hingga ekstraksi informasi spasial menjadi dataset tabular (_Time Series_) yang siap dianalisis.
3. **Data Preparation:** Menjelaskan proses pemeriksaan kualitas data, penanganan nilai kosong, penyesuaian format tanggal, dan penyiapan data agar dapat digunakan secara konsisten.
4. **Exploratory Data Analysis:** Menampilkan pola, tren, perbandingan, dan hubungan antarvariabel polutan melalui tabel serta visualisasi.
5. **Evaluation dan Conclusion:** Merangkum temuan utama, keterbatasan penggunaan data satelit, serta peluang pengembangan analisis kualitas udara di Kabupaten Jombang.
