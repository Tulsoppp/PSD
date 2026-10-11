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

# Analisis dan Perbandingan Metrik Statistik Polutan (NO2, CO, SO2)

Analisis dan Perbandingan Metrik Statistik Polutan (NO2, CO, SO2)Notebook ini mendemonstrasikan perhitungan manual untuk metrik Mean Absolute Difference dan Mean Difference menggunakan Python, lalu membandingkannya dengan hasil ekstraksi fitur time-series dari TSFEL (Time Series Feature Extraction Library).1. Rumus yang DigunakanA. Mean Absolute DifferenceMetrik ini mengukur rata-rata dari fluktuasi lokal dengan menghitung rata-rata nilai absolut selisih antara titik data yang saling berurutan (berdekatan) dalam time series.
Rumus:
$$Mean\ Abs\ Diff = mean(\vert{}X_i - X_{i-1}\vert{})$$

Langkah-langkah Perhitungan:Pertahankan Urutan Waktu: Pastikan data tidak diurutkan berdasarkan nilai dari kecil ke besar, melainkan tetap berdasarkan urutan waktu kejadian aslinya.Hitung Selisih Antar-Titik Berdekatan: Hitung perbedaan antara titik data kedua dikurangi titik pertama, titik ketiga dikurangi titik kedua, dan seterusnya hingga akhir data.Absolutkan Hasil (Nilai Mutlak): Ubah semua hasil selisih yang didapatkan menjadi bernilai positif.Hitung Rata-rata (Mean): Jumlahkan seluruh hasil selisih absolut tersebut, lalu bagi dengan jumlah total selisih yang ada.B. Mean DifferenceMetrik ini mengukur rata-rata dari selisih berurutan dalam time series tanpa mengubah nilainya menjadi absolut. Ini membantu untuk melihat kecenderungan arah perubahan (tren keseluruhan) antara titik-titik yang berdekatan.
Rumus:
$$Mean\ Diff = mean(X_i - X_{i-1})$$

Langkah-langkah Perhitungan:Pertahankan Urutan Waktu: Sama seperti sebelumnya, data harus tetap dalam urutan waktu.Hitung Selisih Antar-Titik Berdekatan: Kurangi titik data saat ini dengan titik data sebelumnya secara berurutan.Hitung Rata-rata (Mean): Langsung hitung rata-rata dari seluruh selisih tersebut beserta nilai negatifnya (jika ada).2. Perbandingan Perhitungan Manual vs TSFELPada bagian ini, kita akan membuktikan dan membandingkan hasil perhitungan metrik statistik secara manual menggunakan numpy dengan hasil ekstraksi fitur otomatis dari library TSFEL. Dua metrik yang akan diuji adalah Mean Absolute Difference dan Mean Difference.import pandas as pd
import numpy as np
from IPython.display import display

# Definisi nama file yang akan diuji
```{code-cell}
import re
import pandas as pd
import numpy as np
from IPython.display import display

files = {
    'NO2': {'raw': '../../NO2_after.csv', 'tsfel': '../../NO2_Kertosono_TSFEL.csv'},
    'CO':  {'raw': '../../CO_after.csv', 'tsfel': '../../CO_Kertosono_TSFEL.csv'},
    'SO2': {'raw': '../../SO2_after.csv', 'tsfel': '../../SO2_Kertosono_TSFEL.csv'}
}

def normalize(name):
    """Menghilangkan spasi, underscore, dan huruf besar/kecil agar pencocokan nama kolom lebih fleksibel."""
    return re.sub(r'[^a-z0-9]', '', str(name).lower())

def find_column(df, target):
    """Mencari kolom di df yang namanya paling cocok dengan target (setelah dinormalisasi)."""
    target_norm = normalize(target)
    for col in df.columns:
        if normalize(col) == target_norm:
            return col
    # fallback: cari kolom yang MENGANDUNG target_norm (mis. ada prefix "0_")
    for col in df.columns:
        if target_norm in normalize(col):
            return col
    return None

results = []

for pol, f in files.items():
    try:
        # 1. Load Data Mentah
        df_raw = pd.read_csv(f['raw'])
        signal = df_raw[pol].dropna().values

        # 2. Perhitungan Manual
        # Mean Absolute Difference
        calc_mean_abs_diff = np.mean(np.abs(np.diff(signal)))

        # Mean Difference
        calc_mean_diff = np.mean(np.diff(signal))

        # 3. Load Data Ekstraksi TSFEL
        df_tsfel = pd.read_csv(f['tsfel'])

        # Debug: tampilkan nama-nama kolom yang tersedia (opsional, bisa dihapus/dikomentari)
        # print(f"Kolom TSFEL untuk {pol}: {df_tsfel.columns.tolist()}")

        col_mean_abs_diff = find_column(df_tsfel, 'mean abs diff')
        col_mean_diff = find_column(df_tsfel, 'mean diff')

        if col_mean_abs_diff is None or col_mean_diff is None:
            print(f"[{pol}] Kolom tidak ditemukan. Kolom tersedia: {df_tsfel.columns.tolist()}")
            continue

        def to_float(value):
            """Mengubah nilai (yang bisa saja terbaca sebagai string) menjadi float.
            Menangani kasus desimal berkoma (mis. '0,0123') maupun tanda kutip/spasi ekstra."""
            if isinstance(value, str):
                value = value.strip().strip('"').strip("'").replace(',', '.')
            return float(value)

        tsfel_mean_abs_diff = to_float(df_tsfel[col_mean_abs_diff].iloc[0])
        tsfel_mean_diff = to_float(df_tsfel[col_mean_diff].iloc[0])

        # 4. Menyimpan format ke list untuk DataFrame
        results.append({
            'Polutan': pol,
            'Metrik': 'Mean Abs Diff',
            'Manual Python': f"{calc_mean_abs_diff:.9f}",
            'Ekstraksi TSFEL': f"{tsfel_mean_abs_diff:.9f}"
        })

        results.append({
            'Polutan': '', # Dikosongkan agar tampilan tabel lebih rapi
            'Metrik': 'Mean Diff',
            'Manual Python': f"{calc_mean_diff:.9f}",
            'Ekstraksi TSFEL': f"{tsfel_mean_diff:.9f}"
        })

    except FileNotFoundError as e:
        print(f"File tidak ditemukan untuk {pol}: {e}")
    except KeyError as e:
        print(f"Kolom bermasalah untuk {pol}: {e}")
    except (ValueError, TypeError) as e:
        print(f"Nilai tidak bisa dikonversi ke angka untuk {pol}: {e}")

# 5. Menampilkan hasil komparasi dalam bentuk tabel
df_results = pd.DataFrame(results)
display(df_results)
```

# 5. Menampilkan hasil komparasi dalam bentuk tabel
df_results = pd.DataFrame(results)
display(df_results)
3. Kesimpulan dan AnalisisAkurasi Perhitungan:
Metodologi perhitungan menggunakan fungsi dasar numpy (np.mean(np.abs(np.diff(signal))) dan np.mean(np.diff(signal))) terbukti memberikan hasil yang ekuivalen dengan fungsionalitas kompleks yang ditawarkan oleh library TSFEL.Kecocokan Identik pada NO2 dan CO:
Hasil perhitungan manual untuk polutan NO2 dan CO 100% identik dengan hasil ekstraksi fitur default TSFEL hingga digit desimal yang sangat panjang (presisi floating point).Penyimpangan Sangat Kecil pada SO2:
Pada data SO2, mungkin terdapat perbedaan yang sangat marjinal (pada kisaran digit desimal yang jauh di belakang koma). Perbedaan super kecil ini umumnya wajar dalam data science dan terjadi akibat perbedaan penanganan batas tipe data (float precision rounding) atau filter pra-pemrosesan di dalam sistem under-the-hood TSFEL.