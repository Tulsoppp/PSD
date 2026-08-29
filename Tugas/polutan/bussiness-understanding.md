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

# Business Understanding

## 1. Latar Belakang

Kualitas udara merupakan salah satu indikator penting bagi kesehatan masyarakat, kenyamanan hidup, dan kelestarian lingkungan. Udara yang tercemar dapat meningkatkan risiko gangguan pernapasan, mengurangi jarak pandang, memengaruhi produktivitas masyarakat, serta memperburuk kondisi lingkungan dalam jangka panjang. Seiring dengan meningkatnya jumlah kendaraan, mobilitas penduduk, kegiatan industri, pembakaran bahan bakar, dan aktivitas rumah tangga, potensi peningkatan konsentrasi gas polutan di atmosfer juga semakin besar.

Kabupaten Jombang merupakan salah satu wilayah yang berkembang di Jawa Timur dengan perpaduan kawasan perkotaan, permukiman, lahan pertanian, kawasan industri, dan jaringan jalan yang menghubungkan berbagai daerah. Keragaman penggunaan lahan dan aktivitas masyarakat tersebut dapat menimbulkan variasi emisi dari satu waktu atau lokasi ke waktu dan lokasi lainnya. Karena itu, kondisi kualitas udara di Kabupaten Jombang perlu dipahami melalui pengamatan yang dilakukan secara berkala dan menggunakan data yang dapat menggambarkan perubahan wilayah secara luas.

Dalam proyek ini, data pengamatan dari satelit **Copernicus Sentinel-5P** digunakan untuk mengamati perubahan relatif konsentrasi gas polutan di wilayah Kabupaten Jombang. Data tersebut diambil melalui _Copernicus Data Space Ecosystem_, kemudian diproses menjadi data tabular berbentuk deret waktu (_Time Series_) mulai dari akhir tahun 2023. Pendekatan ini memungkinkan analisis dilakukan secara lebih terstruktur untuk melihat pola harian, kecenderungan perubahan, dan periode ketika konsentrasi polutan mengalami peningkatan.

Tiga jenis gas polutan utama yang menjadi fokus pemantauan adalah:

- **Nitrogen Dioksida (NO₂):** Banyak dihasilkan dari pembakaran bahan bakar kendaraan bermotor dan aktivitas industri. Polutan ini juga dapat berperan dalam pembentukan ozon permukaan serta partikulat sekunder.
- **Karbon Monoksida (CO):** Gas beracun yang dihasilkan dari pembakaran tidak sempurna, misalnya dari emisi kendaraan, penggunaan bahan bakar padat, dan pembakaran terbuka. Konsentrasi yang tinggi dapat mengurangi kemampuan darah dalam membawa oksigen.
- **Belerang Dioksida (SO₂):** Polutan yang dapat berasal dari pembakaran bahan bakar fosil yang mengandung sulfur maupun sumber alami. SO₂ berpotensi mengiritasi saluran pernapasan dan berkontribusi terhadap pembentukan hujan asam.

Nilai dari Sentinel-5P perlu dipahami sebagai pengukuran kolom atmosfer, bukan pengukuran langsung konsentrasi udara pada ketinggian hidung manusia. Hasil pengamatan dapat dipengaruhi oleh tutupan awan, resolusi spasial satelit, kondisi cuaca, arah angin, dan waktu perekaman. Oleh sebab itu, analisis pada proyek ini menekankan pola dan perubahan relatif dari waktu ke waktu. Data satelit dapat melengkapi pengukuran stasiun darat, tetapi tidak dimaksudkan untuk menggantikannya.

## 2. Rumusan Masalah

Beberapa permasalahan utama yang ingin dijawab melalui analisis data ini adalah:

- Bagaimana perubahan dan tren konsentrasi harian gas polutan (NO₂, CO, dan SO₂) di wilayah Kabupaten Jombang?
- Apakah terdapat pola berulang, kecenderungan peningkatan atau penurunan jangka panjang, maupun lonjakan (anomali) mendadak pada tingkat polusi udara di wilayah tersebut?
- Bagaimana karakteristik masing-masing polutan dan apakah perubahan satu polutan terlihat bersamaan dengan perubahan polutan lainnya?
- Periode atau kondisi seperti apa yang perlu mendapat perhatian lebih lanjut melalui pengukuran lapangan dan informasi meteorologi?

## 3. Tujuan Proyek

Tujuan dari eksplorasi sains data ini adalah:

- Mengotomatisasi pengumpulan data citra satelit spasial (NetCDF) dan mentransformasikannya ke dalam dataset tabular (CSV) yang siap dianalisis.
- Menentukan dan menggunakan wilayah pengamatan Kabupaten Jombang secara konsisten pada setiap tahap pengolahan data.
- Melakukan pemeriksaan kualitas data, penanganan nilai kosong, penyesuaian format tanggal, dan analisis data eksploratif (EDA) untuk mengidentifikasi perilaku serta tren perubahan gas polutan secara temporal.
- Mengidentifikasi periode dengan nilai yang relatif tinggi, rendah, atau tidak biasa sebagai bahan interpretasi dan pemeriksaan lebih lanjut.
- Menyediakan dasar data historis yang terdokumentasi untuk keperluan analisis prediktif (_forecasting_) kualitas udara di Kabupaten Jombang pada masa mendatang.

## 4. Manfaat Proyek

Hasil dari pengolahan data dan pemahaman ini diharapkan dapat memberikan dampak positif, antara lain:

- **Pemerintah / Pembuat Kebijakan:** Memberikan wawasan (_insight_) berbasis data sebagai salah satu landasan untuk menyusun kebijakan lingkungan, melakukan pengawasan emisi, menentukan kebutuhan pengukuran lapangan, atau mengevaluasi dampak aktivitas transportasi dan industri.
- **Masyarakat Kabupaten Jombang:** Menjadi sumber informasi yang lebih transparan mengenai perubahan kualitas udara dan meningkatkan kesadaran terhadap aktivitas yang dapat menghasilkan emisi.
- **Peneliti dan Akademisi:** Menyediakan contoh penerapan pengolahan data spasial dari citra satelit menjadi data deret waktu yang dapat dianalisis secara reproducible.
- **Data Scientist:** Menjadi _use case_ untuk menerapkan proses _Data Science Lifecycle_, mulai dari pengumpulan dan pembersihan data hingga visualisasi, deteksi anomali, dan pemodelan _forecasting_.

Interpretasi hasil tetap perlu dilakukan secara hati-hati. Kenaikan nilai polutan pada data satelit tidak secara otomatis membuktikan adanya satu sumber emisi tertentu. Temuan dalam proyek ini lebih tepat digunakan sebagai gambaran awal mengenai pola atmosfer di Kabupaten Jombang dan sebagai dasar untuk analisis lanjutan dengan data kualitas udara permukaan, cuaca, kepadatan lalu lintas, serta catatan aktivitas industri atau pembakaran apabila data tersebut tersedia.
