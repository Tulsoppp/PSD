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

# 6. Visualisasi Peta Hasil Klasifikasi / Digitasi

Visualisasi geospasial memegang peranan krusial dalam menyajikan hasil analisis tutupan lahan (*Land Use / Land Cover*) kepada pengambil kebijakan dan publik. Sampel poligon Laut nomor 0 sampai 18 (`Laut_0000` hingga `Laut_0018`) telah dihapus dan tidak ditampilkan pada peta karena lokasinya berada melewati batas administrasi Provinsi Jawa Timur.

Mengacu pada tahapan eksperimen dalam notebook `Tugas/UTS/test.ipynb`, disajikan dua jenis peta interaktif berbasis pustaka **Folium**:

1. **Peta 1 (Folium Vektor - Rekonstruksi Convex Hull)**: Menampilkan poligon sampel ground truth yang direkonstruksi dari kumpulan koordinat titik piksel.
2. **Peta 2 (Folium Raster - Inferensi Regional Jawa Timur 250m)**: Menampilkan inferensi tutupan lahan per piksel di seluruh Provinsi Jawa Timur menggunakan model **K-Nearest Neighbors (KNN)** pada citra komposit openEO `jatim_250m.tif`.

---

## 1. Peta Rekonstruksi Poligon Ground Truth (Convex Hull)

Untuk menjaga performa render peta agar tetap ringan dan responsif, titik-titik sampel piksel yang telah disaring (tanpa Laut 0-18) digabungkan (*dissolve*) berdasarkan `poligon_id` dan direkonstruksi menjadi batas poligon tunggal menggunakan algoritma **Convex Hull** (selubung cembung).

### Fitur Peta 1:
* **Palet Warna Tematik per Kelas**:
  - Sawah: Kuning Keemasan (`#FFD92F`)
  - Bangunan: Merah Terang (`#E41A1C`)
  - Hutan / Lahan Hijau: Hijau Hutan (`#2E7D32`)
  - Laut / Perairan Terbuka: Biru Laut Tua (`#0D47A1`)
  - Mangrove: Ungu Lembayung (`#8E44AD`)
  - Danau: Biru Muda (`#4FC3F7`)
* **Layer Interaktif**: Setiap kelas tutupan lahan memiliki `FeatureGroup` tersendiri yang dapat dinyalakan/dimatikan pada panel kontrol lapisan (*LayerControl*).
* **Multi-Basemap**: Dilengkapi basemap satelit resolusi tinggi Google Satellite dan Esri World Imagery.

```{code-cell}
from pathlib import Path
import folium
import geopandas as gpd
import pandas as pd

dataset_path = next(
    (
        candidate
        for folder in (Path.cwd(), *Path.cwd().parents)
        for candidate in (
            folder / "piksel_s2_JTM.csv",
            folder / "Tugas" / "UTS" / "piksel_s2_JTM.csv",
        )
        if candidate.is_file()
    ),
    None,
)
if dataset_path is None:
    raise FileNotFoundError("Dataset piksel_s2_JTM.csv tidak ditemukan.")

df = pd.read_csv(dataset_path)

# Hapus sampel poligon laut 0 sampai 18 agar tidak digambar pada peta
excluded_laut = {f"Laut_{index:04d}" for index in range(19)}
df = df[~df["poligon_id"].isin(excluded_laut)].copy()

# Rekonstruksi Titik menjadi Poligon (Convex Hull)
gdf = gpd.GeoDataFrame(
    df, geometry=gpd.points_from_xy(df.lon, df.lat), crs="EPSG:4326"
)

polygons = gdf.dissolve(by='poligon_id', aggfunc='first').reset_index()
polygons['geometry'] = polygons['geometry'].convex_hull
polygons = polygons[~polygons['geometry'].is_empty]

map_center = [df['lat'].mean(), df['lon'].mean()]

m1 = folium.Map(
    location=map_center,
    zoom_start=9,
    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attr='Esri Satellite'
)

folium.TileLayer(
    tiles='OpenStreetMap',
    name='OpenStreetMap',
    overlay=False
).add_to(m1)

colors = {
    'Sawah': '#FFD92F',
    'Bangunan': '#E41A1C',
    'Mangrove': '#8E44AD',
    'Hutan': '#2E7D32',
    'Laut': '#0D47A1',
    'Danau': '#4FC3F7'
}

feature_groups = {}
for label in polygons['label_teks'].unique():
    label_str = str(label)
    feature_groups[label_str] = folium.FeatureGroup(name=label_str)
    m1.add_child(feature_groups[label_str])

for idx, row in polygons.iterrows():
    label_str = str(row['label_teks'])
    color = colors.get(label_str, 'black')
    try:
        folium.GeoJson(
            data=row['geometry'].__geo_interface__,
            style_function=lambda x, c=color: {
                'fillColor': c,
                'color': c,
                'weight': 1.5,
                'fillOpacity': 0.65
            },
            tooltip=f"{label_str} (Poligon ID: {row['poligon_id']})"
        ).add_to(feature_groups[label_str])
    except Exception:
        pass

folium.LayerControl(collapsed=False).add_to(m1)
m1.save("peta_sampel_JTM.html")
m1
```

#### Pratinjau Interaktif Peta 1 (Sampel Ground Truth Vektor)
Peta interaktif berikut menampilkan rekonstruksi spasial poligon ground truth 6 kelas tutupan lahan di Jawa Timur (573.268 piksel valid dalam 280 poligon, tanpa laut 0 sampai 18):

<iframe src="peta_sampel_JTM.html" width="100%" height="520px" style="border: 1px solid #cbd5e1; border-radius: 12px; margin: 15px 0;"></iframe>

Tautan Akses Langsung: [Buka Peta 1 Interaktif Layar Penuh (peta_sampel_JTM.html)](peta_sampel_JTM.html)

---

## 2. Peta Inferensi Regional Skala Jawa Timur (Citra 250m)

Peta kedua memetakan hasil inferensi model **KNN** pada citra komposit optik Sentinel-2A skala regional (`jatim_250m.tif`) yang diunduh via openEO CDSE:

* Resolusi spasial agregasi: $0.0025^\circ$ (~250 meter).
* Setiap kelas tutupan lahan diproyeksikan sebagai lapisan `ImageOverlay` transparan (opasitas 70%), sehingga kontur dan relief bumi pada basemap satelit tetap terlihat.
* Pengguna dapat memilih untuk melihat sebaran hutan, sawah, atau bangunan secara terisolasi menggunakan kontrol layer di pojok kanan atas.

```{code-cell}
import os
import rasterio
import numpy as np
import folium
from folium.raster_layers import ImageOverlay
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier

def hex_to_rgb(hex_code):
    hex_code = hex_code.lstrip('#')
    return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))

file_raster = next(
    (
        candidate
        for folder in (Path.cwd(), *Path.cwd().parents)
        for candidate in (
            folder / "jatim_250m.tif",
            folder / "Tugas" / "UTS" / "jatim_250m.tif",
        )
        if candidate.is_file()
    ),
    None,
)

if file_raster and file_raster.is_file():
    with rasterio.open(str(file_raster)) as src:
        b2 = src.read(1).astype(float)
        b3 = src.read(2).astype(float)
        b4 = src.read(3).astype(float)
        b8 = src.read(4).astype(float)
        b11 = src.read(5).astype(float)
        bounds = src.bounds
        img_bounds = [[bounds.bottom, bounds.left], [bounds.top, bounds.right]]
        center_lat = (bounds.bottom + bounds.top) / 2
        center_lon = (bounds.left + bounds.right) / 2

    e = 1e-9
    ndvi = (b8 - b4) / (b8 + b4 + e)
    ndwi = (b3 - b8) / (b3 + b8 + e)
    mndwi = (b3 - b11) / (b3 + b11 + e)
    ndbi = (b11 - b8) / (b11 + b8 + e)
    height, width = b2.shape

    features_stack = np.column_stack((
        b2.flatten(), b3.flatten(), b4.flatten(), b8.flatten(), b11.flatten(),
        ndvi.flatten(), ndwi.flatten(), mndwi.flatten(), ndbi.flatten()
    ))
    valid_mask = (b2.flatten() > 0)

    # Menggunakan model KNN yang dilatih pada data terfilter (tanpa laut 0-18)
    fitur = ['B02', 'B03', 'B04', 'B08', 'B11', 'NDVI', 'NDWI', 'MNDWI', 'NDBI']
    df_clean = df.dropna(subset=fitur + ['label_teks'])
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(df_clean[fitur])
    knn = KNeighborsClassifier(n_neighbors=5)
    knn.fit(X_train_scaled, df_clean['label_teks'])

    features_scaled = scaler.transform(features_stack)
    pred_1d = knn.predict(features_scaled)
    pred_2d = pred_1d.reshape((height, width))
    valid_2d = valid_mask.reshape((height, width))

    m2 = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=8,
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri Satellite'
    )

    for label_str, hex_color in colors.items():
        rgba_img = np.zeros((height, width, 4), dtype=np.uint8)
        mask = (pred_2d == label_str) & valid_2d
        if np.any(mask):
            r, g, b = hex_to_rgb(hex_color)
            rgba_img[mask, 0] = r
            rgba_img[mask, 1] = g
            rgba_img[mask, 2] = b
            rgba_img[mask, 3] = 180
            ImageOverlay(
                image=rgba_img,
                bounds=img_bounds,
                opacity=0.7,
                name=f"Sebaran {label_str}",
                show=True
            ).add_to(m2)

    folium.LayerControl(collapsed=False).add_to(m2)
    m2.save("peta_prediksi_JTM.html")
    m2
else:
    print("File jatim_250m.tif tidak ditemukan.")
```

#### Pratinjau Interaktif Peta 2 (Inferensi Regional Jawa Timur 250m)
Peta interaktif berikut menampilkan sebaran klasifikasi tutupan lahan regional seluruh Provinsi Jawa Timur menggunakan model KNN pada citra Sentinel-2A resolusi 250m:

<iframe src="peta_prediksi_JTM.html" width="100%" height="520px" style="border: 1px solid #cbd5e1; border-radius: 12px; margin: 15px 0;"></iframe>

Tautan Akses Langsung: [Buka Peta 2 Interaktif Layar Penuh (peta_prediksi_JTM.html)](peta_prediksi_JTM.html)

