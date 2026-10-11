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

Peta interaktif menggunakan geometri poligon digitasi asli dari arsip shapefile di folder `DIGITASI`. Atribut `FID` pada shapefile dicocokkan dengan `poligon_no` pada CSV. Poligon daratan dipotong mengikuti batas Jawa Timur; piksel daratan di luar batas juga disaring sebelum agregasi. Poligon Laut `Laut_0000` hingga `Laut_0018` dikecualikan dari data peta karena berada melewati batas wilayah, konsisten dengan tahap EDA dan pemodelan. Pengecualian hanya diterapkan pada data analisis; CSV sumber tidak diubah. Basemap memakai citra satelit Esri World Imagery dengan layer referensi Esri untuk label/nama tempat, batas, dan jalan.

## Layer dan Informasi Peta

- Setiap kelas dibuat sebagai *feature layer* tersendiri.
- Warna poligon ditentukan melalui kamus warna kelas.
- Poligon menampilkan `poligon_id` dan `label_teks` ketika diarahkan.
- `LayerControl` memungkinkan layer kelas ditampilkan atau disembunyikan.
- Hasil peta disimpan sebagai `peta_sampel_JTM.html` di folder dataset, yaitu folder `Tugas/UTS`.

Jalankan sel berikut untuk menyaring data, mencocokkan poligon digitasi ke sampel, membangun peta, dan menyimpan hasilnya sebagai HTML.

```{code-cell}
import json
from pathlib import Path

import folium
import geopandas as gpd
import numpy as np
import pandas as pd
import shapely
from shapely.geometry import mapping, shape

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

project_path = dataset_path.parents[2]
digitasi_path = project_path / "DIGITASI"
boundary_path = dataset_path.with_name("batas_jawa_timur.geojson")
if not boundary_path.is_file():
    raise FileNotFoundError(f"Batas Jawa Timur tidak ditemukan: {boundary_path}")

with boundary_path.open(encoding="utf-8") as file:
    boundary_feature = json.load(file)
if boundary_feature.get("properties", {}).get("adm1_pcode") != "ID35":
    raise ValueError("Berkas geometri bukan batas Provinsi Jawa Timur.")
boundary = shape(boundary_feature["geometry"])
if boundary.is_empty or not boundary.is_valid:
    raise ValueError("Geometri batas Provinsi Jawa Timur tidak valid.")

file_by_class = {
    "Bangunan": "bangunan.zip",
    "Danau": "Danau.zip",
    "Hutan": "Lahan Hijau.zip",
    "Laut": "Laut.zip",
    "Mangrove": "Magruve.zip",
    "Sawah": "sawah.zip",
}
geometry_by_class = {}
for land_class, filename in file_by_class.items():
    archive_path = digitasi_path / filename
    if not archive_path.is_file():
        raise FileNotFoundError(f"Arsip poligon tidak ditemukan: {archive_path}")
    layer = gpd.read_file(f"/vsizip/{archive_path.as_posix()}/input.shp")
    if "FID" not in layer.columns:
        raise ValueError(f"Atribut FID tidak ditemukan pada {archive_path}.")
    if layer["FID"].duplicated().any():
        raise ValueError(f"Atribut FID duplikat ditemukan pada {archive_path}.")
    if layer.crs is None:
        raise ValueError(f"CRS tidak ditemukan pada {archive_path}.")
    if layer.crs.to_epsg() != 4326:
        layer = layer.to_crs(epsg=4326)

    geometries = {}
    for feature in layer.itertuples():
        geometry = feature.geometry
        if geometry is None or geometry.is_empty:
            raise ValueError(
                f"Geometri kosong pada {archive_path}, FID {feature.FID}."
            )
        if not geometry.is_valid:
            geometry = shapely.make_valid(geometry)
        if land_class != "Laut":
            geometry = geometry.intersection(boundary)
        if not geometry.is_empty:
            geometries[int(feature.FID)] = mapping(geometry)
    geometry_by_class[land_class] = geometries

df = pd.read_csv(dataset_path)
fitur = ["B02", "B03", "B04", "B08", "B11", "NDVI", "NDWI", "MNDWI", "NDBI"]
kolom_agregasi = [
    "poligon_id", "poligon_no", "label", "label_teks", "lon", "lat", *fitur
]
df_bersih = (
    df[kolom_agregasi]
    .replace([np.inf, -np.inf], np.nan)
    .dropna()
    .copy()
)
excluded_polygon_ids = {f"Laut_{index:04d}" for index in range(19)}
df_bersih = df_bersih[~df_bersih["poligon_id"].isin(excluded_polygon_ids)].copy()
coordinates = df_bersih[["lon", "lat"]].to_numpy(dtype=np.float64)
finite_coordinates = np.isfinite(coordinates).all(axis=1)
inside_boundary = np.zeros(len(df_bersih), dtype=bool)
inside_boundary[finite_coordinates] = shapely.contains_xy(
    boundary,
    coordinates[finite_coordinates, 0],
    coordinates[finite_coordinates, 1],
)
keep_laut = df_bersih["label_teks"].eq("Laut").to_numpy()
df_bersih = df_bersih.loc[
    finite_coordinates & (inside_boundary | keep_laut)
].copy()

poligon = (
    df_bersih.groupby("poligon_id", as_index=False)
    .agg(
        poligon_no=("poligon_no", "first"),
        label=("label", "first"),
        label_teks=("label_teks", "first"),
        lon=("lon", "mean"),
        lat=("lat", "mean"),
        **{nama_fitur: (nama_fitur, "mean") for nama_fitur in fitur},
    )
)
coordinates = poligon[["lon", "lat"]].to_numpy(dtype=np.float64)
finite_coordinates = np.isfinite(coordinates).all(axis=1)
inside_boundary = np.zeros(len(poligon), dtype=bool)
inside_boundary[finite_coordinates] = shapely.contains_xy(
    boundary,
    coordinates[finite_coordinates, 0],
    coordinates[finite_coordinates, 1],
)
keep_laut = poligon["label_teks"].eq("Laut").to_numpy()
poligon = poligon.loc[
    finite_coordinates & (inside_boundary | keep_laut)
].copy()

missing_geometries = [
    (row.label_teks, int(row.poligon_no))
    for row in poligon.itertuples()
    if int(row.poligon_no) not in geometry_by_class.get(row.label_teks, {})
]
if missing_geometries:
    raise ValueError(
        f"Geometri digitasi tidak ditemukan untuk sampel: {missing_geometries[:5]}"
    )

warna = {
    "Sawah": "#D6A800",
    "Bangunan": "#E41A1C",
    "Hutan": "#2E7D32",
    "Danau": "#4FC3F7",
    "Laut": "#0D47A1",
    "Mangrove": "#8E44AD",
}
peta = folium.Map(
    location=[poligon["lat"].mean(), poligon["lon"].mean()],
    zoom_start=6,
    tiles="Esri.WorldImagery",
)
folium.TileLayer(
    tiles=(
        "https://server.arcgisonline.com/ArcGIS/rest/services/Reference/"
        "World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}"
    ),
    name="Label dan batas",
    attr="Tiles &copy; Esri",
    overlay=True,
    control=True,
    show=True,
    max_zoom=19,
).add_to(peta)
folium.TileLayer(
    tiles=(
        "https://server.arcgisonline.com/ArcGIS/rest/services/Reference/"
        "World_Transportation/MapServer/tile/{z}/{y}/{x}"
    ),
    name="Jalan",
    attr="Tiles &copy; Esri",
    overlay=True,
    control=True,
    show=True,
    max_zoom=19,
).add_to(peta)
for kelas in sorted(poligon["label_teks"].dropna().unique()):
    warna_kelas = warna.get(str(kelas), "#475569")
    layer = folium.FeatureGroup(name=str(kelas))
    class_rows = poligon[poligon["label_teks"] == kelas]
    for row in class_rows.itertuples():
        folium.GeoJson(
            data=geometry_by_class[kelas][int(row.poligon_no)],
            style_function=lambda _feature, color=warna_kelas: {
                "color": color,
                "weight": 1,
                "fillColor": color,
                "fillOpacity": 0.2,
            },
            tooltip=f"{row.poligon_id} | Kelas: {row.label_teks}",
        ).add_to(layer)
    layer.add_to(peta)

folium.LayerControl(collapsed=False).add_to(peta)
map_path = dataset_path.parent / "peta_sampel_JTM.html"
peta.save(str(map_path))
print(
    f"Peta satelit tersimpan: {map_path} "
    f"({len(poligon):,} poligon digitasi)."
)
peta
```

## Peta Evaluasi Prediksi KNN

Peta ini terpisah dari peta sampel dan hanya menampilkan poligon pada data uji. Model KNN dilatih dari 70% poligon dan diuji pada 30% poligon yang tidak dipakai saat pelatihan, dengan pembagian yang sama seperti bagian pemodelan (`random_state=42` dan stratifikasi kelas). Warna poligon menunjukkan kelas prediksi; penanda hijau berarti kelas prediksi poligon sama dengan label aslinya, sedangkan penanda merah berarti kelasnya berbeda. Ini mengikuti akurasi model yang dihitung pada tingkat poligon. Rincian popup juga menunjukkan persentase piksel uji yang benar di dalam poligon; jumlah ini memakai ukuran evaluasi yang berbeda.

Jalankan sel ini setelah sel peta sampel di atas. Peta akan ditampilkan dan disimpan terpisah sebagai `peta_prediksi_JTM.html` di folder dataset.

```{code-cell}
import html

import folium
import numpy as np
from branca.element import Element
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler

train_indices, test_indices = train_test_split(
    np.arange(len(poligon)),
    test_size=0.3,
    random_state=42,
    stratify=poligon["label_teks"],
)
train_poligon = poligon.iloc[train_indices]
test_poligon = poligon.iloc[test_indices].copy()

scaler_prediksi = StandardScaler()
x_train_scaled = scaler_prediksi.fit_transform(train_poligon[fitur])
x_test_scaled = scaler_prediksi.transform(test_poligon[fitur])
knn_model = KNeighborsClassifier(n_neighbors=5)
knn_model.fit(x_train_scaled, train_poligon["label_teks"])

test_poligon["prediksi"] = knn_model.predict(x_test_scaled)
test_poligon = test_poligon.rename(columns={"label_teks": "kelas_asli"})
pixel_uji = df_bersih.loc[
    df_bersih["poligon_id"].isin(test_poligon["poligon_id"]),
    ["poligon_id", "label_teks", "lon", "lat", *fitur],
].copy()
pixel_uji["prediksi"] = knn_model.predict(
    scaler_prediksi.transform(pixel_uji[fitur])
)
pixel_uji["benar"] = pixel_uji["prediksi"] == pixel_uji["label_teks"]
akurasi_piksel = pixel_uji.groupby("poligon_id", as_index=False).agg(
    piksel_benar=("benar", "sum"),
    jumlah_piksel_uji=("benar", "size"),
)
akurasi_piksel["akurasi_piksel"] = (
    akurasi_piksel["piksel_benar"] / akurasi_piksel["jumlah_piksel_uji"]
)
test_poligon = test_poligon.merge(
    akurasi_piksel, on="poligon_id", how="left", validate="one_to_one"
)
if test_poligon["akurasi_piksel"].isna().any():
    raise ValueError("Sebagian poligon uji tidak memiliki piksel untuk peta.")

akurasi_poligon = accuracy_score(
    test_poligon["kelas_asli"], test_poligon["prediksi"]
)
print(f"Jumlah poligon uji: {len(test_poligon):,}")
print(f"Akurasi KNN tingkat poligon: {akurasi_poligon:.2%}")
print(
    "Prediksi kelas poligon benar: "
    f"{int((test_poligon['kelas_asli'] == test_poligon['prediksi']).sum()):,}"
)
print(
    "Poligon dengan semua piksel uji benar: "
    f"{int((test_poligon['akurasi_piksel'] == 1).sum()):,}"
)

peta_prediksi = folium.Map(
    location=[poligon["lat"].mean(), poligon["lon"].mean()],
    zoom_start=6,
    tiles="Esri.WorldImagery",
)
folium.TileLayer(
    tiles=(
        "https://server.arcgisonline.com/ArcGIS/rest/services/Reference/"
        "World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}"
    ),
    name="Label dan batas",
    attr="Tiles &copy; Esri",
    overlay=True,
    control=True,
    show=True,
    max_zoom=19,
).add_to(peta_prediksi)
folium.TileLayer(
    tiles=(
        "https://server.arcgisonline.com/ArcGIS/rest/services/Reference/"
        "World_Transportation/MapServer/tile/{z}/{y}/{x}"
    ),
    name="Jalan",
    attr="Tiles &copy; Esri",
    overlay=True,
    control=True,
    show=True,
    max_zoom=19,
).add_to(peta_prediksi)

for kelas_prediksi in sorted(test_poligon["prediksi"].unique()):
    warna_kelas = warna.get(str(kelas_prediksi), "#475569")
    layer = folium.FeatureGroup(name=f"Prediksi: {kelas_prediksi}")
    rows = test_poligon[test_poligon["prediksi"] == kelas_prediksi]
    for row in rows.itertuples():
        kelas_asli = str(row.kelas_asli)
        kelas_prediksi_teks = str(row.prediksi)
        polygon_id = html.escape(str(row.poligon_id))
        geometri = geometry_by_class[kelas_asli][int(row.poligon_no)]
        detail = (
            f"<b>{polygon_id}</b><br>"
            f"Kelas aktual: {html.escape(kelas_asli)}<br>"
            f"Prediksi KNN: {html.escape(kelas_prediksi_teks)}<br>"
            f"Piksel uji benar: {int(row.piksel_benar):,}/"
            f"{int(row.jumlah_piksel_uji):,} "
            f"({float(row.akurasi_piksel):.1%})"
        )
        folium.GeoJson(
            data=geometri,
            style_function=lambda _feature, color=warna_kelas: {
                "color": color,
                "weight": 1,
                "fillColor": color,
                "fillOpacity": 0.2,
            },
            tooltip=detail,
            popup=folium.Popup(detail, max_width=320),
        ).add_to(layer)
    layer.add_to(peta_prediksi)

benar_layer = folium.FeatureGroup(name="Prediksi benar (Data Uji)")
salah_layer = folium.FeatureGroup(name="Salah klasifikasi (Data Uji)")
for row in test_poligon.itertuples():
    prediksi_benar = row.kelas_asli == row.prediksi
    warna_status = "#10B981" if prediksi_benar else "#E11D48"
    simbol = "✓" if prediksi_benar else "!"
    polygon_id = html.escape(str(row.poligon_id))
    status = (
        "Prediksi kelas poligon benar"
        if prediksi_benar
        else "Prediksi kelas poligon salah"
    )
    popup = (
        f"<b>{polygon_id}</b><br>"
        f"Kelas aktual: {html.escape(str(row.kelas_asli))}<br>"
        f"Prediksi KNN: {html.escape(str(row.prediksi))}<br>"
        f"Piksel uji benar: {int(row.piksel_benar):,}/"
        f"{int(row.jumlah_piksel_uji):,} "
        f"({float(row.akurasi_piksel):.1%})<br>"
        f"Status: {status}"
    )
    marker = folium.Marker(
        location=[float(row.lat), float(row.lon)],
        tooltip=f"{status}: {polygon_id}",
        popup=folium.Popup(popup, max_width=320),
        icon=folium.DivIcon(
            html=(
                '<div style="width:24px;height:24px;border:2px solid white;'
                f'border-radius:50%;background:{warna_status};color:white;'
                'display:flex;align-items:center;justify-content:center;'
                'font-weight:800;font-size:15px;'
                'box-shadow:0 2px 8px rgba(0,0,0,.45);">'
                f"{simbol}</div>"
            ),
            icon_size=(24, 24),
            icon_anchor=(12, 12),
            class_name="prediction-status-marker",
        ),
    )
    (benar_layer if prediksi_benar else salah_layer).add_child(marker)

benar_layer.add_to(peta_prediksi)
salah_layer.add_to(peta_prediksi)
jumlah_prediksi_benar = int(
    (test_poligon["kelas_asli"] == test_poligon["prediksi"]).sum()
)
jumlah_prediksi_salah = len(test_poligon) - jumlah_prediksi_benar
ringkasan_peta = Element(
    f"""
    <div style="
        position: fixed; top: 12px; left: 50px; z-index: 9999;
        background: rgba(255,255,255,.96); padding: 10px 14px;
        border: 1px solid #cbd5e1; border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,.2);
        font: 13px/1.5 Arial, sans-serif; color: #1f2937;">
      <b>Evaluasi KNN — tingkat poligon</b><br>
      Akurasi: {akurasi_poligon:.2%} ({jumlah_prediksi_benar}/{len(test_poligon)})<br>
      <span style="color:#059669">✓ Benar: {jumlah_prediksi_benar}</span>
      &nbsp; <span style="color:#e11d48">! Salah: {jumlah_prediksi_salah}</span>
    </div>
    """
)
ringkasan_peta.add_to(peta_prediksi.get_root().html)
folium.LayerControl(collapsed=False).add_to(peta_prediksi)
peta_prediksi.save(str(dataset_path.parent / "peta_prediksi_JTM.html"))
peta_prediksi
```

## Peta Prediksi Piksel Sampel

CSV proyek menyimpan koordinat dan fitur spektral untuk piksel sampel, bukan citra raster lengkap. Sel ini menampilkan prediksi KNN untuk piksel dari poligon uji sebagai overlay transparan yang bisa diaktifkan per kelas. Piksel salah klasifikasi tersedia sebagai layer terpisah. Area tanpa titik sampel sengaja dibiarkan kosong; peta ini tidak menginterpolasi atau mengklaim prediksi untuk seluruh Jawa Timur.

Jalankan setelah sel evaluasi KNN di atas. Hasilnya disimpan sebagai `peta_prediksi_piksel_JTM.html` di folder dataset.

```{code-cell}
from folium.raster_layers import ImageOverlay

koordinat = pixel_uji[["lon", "lat"]].to_numpy(dtype=np.float64)
if not np.isfinite(koordinat).all():
    raise ValueError("Koordinat piksel uji mengandung nilai yang tidak valid.")

lon = koordinat[:, 0]
lat = koordinat[:, 1]
lon_min, lon_max = float(lon.min()), float(lon.max())
lat_min, lat_max = float(lat.min()), float(lat.max())
mercator_y = np.log(np.tan(np.pi / 4 + np.deg2rad(lat) / 2))
mercator_min, mercator_max = float(mercator_y.min()), float(mercator_y.max())
image_width = 1600
image_height = max(
    1,
    round(
        image_width
        * (mercator_max - mercator_min)
        / np.deg2rad(lon_max - lon_min)
    ),
)
x_pixel = np.rint((lon - lon_min) / (lon_max - lon_min) * (image_width - 1)).astype(
    np.int32
)
y_pixel = np.rint(
    (mercator_max - mercator_y)
    / (mercator_max - mercator_min)
    * (image_height - 1)
).astype(np.int32)
image_bounds = [[lat_min, lon_min], [lat_max, lon_max]]


def buat_overlay_piksel(mask, warna_hex):
    image = np.zeros((image_height, image_width, 4), dtype=np.uint8)
    red, green, blue = (
        int(warna_hex[index : index + 2], 16) for index in (1, 3, 5)
    )
    image[y_pixel[mask], x_pixel[mask]] = (red, green, blue, 220)
    return image


peta_piksel = folium.Map(
    location=[float(lat.mean()), float(lon.mean())],
    zoom_start=7,
    tiles="Esri.WorldImagery",
)
folium.TileLayer(
    tiles=(
        "https://server.arcgisonline.com/ArcGIS/rest/services/Reference/"
        "World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}"
    ),
    name="Label dan batas",
    attr="Tiles &copy; Esri",
    overlay=True,
    control=True,
    show=True,
    max_zoom=19,
).add_to(peta_piksel)

for kelas_prediksi in sorted(pixel_uji["prediksi"].unique()):
    warna_kelas = warna.get(str(kelas_prediksi), "#475569")
    mask_kelas = pixel_uji["prediksi"].eq(kelas_prediksi).to_numpy()
    ImageOverlay(
        image=buat_overlay_piksel(mask_kelas, warna_kelas),
        bounds=image_bounds,
        name=f"Prediksi sampel: {kelas_prediksi}",
        opacity=1,
        overlay=True,
        control=True,
        show=True,
        pixelated=True,
    ).add_to(peta_piksel)

mask_salah = ~pixel_uji["benar"].to_numpy()
if mask_salah.any():
    ImageOverlay(
        image=buat_overlay_piksel(mask_salah, "#FF1744"),
        bounds=image_bounds,
        name="Piksel salah klasifikasi (Data Uji)",
        opacity=1,
        overlay=True,
        control=True,
        show=False,
        pixelated=True,
    ).add_to(peta_piksel)

folium.LayerControl(collapsed=False).add_to(peta_piksel)
pixel_map_path = dataset_path.parent / "peta_prediksi_piksel_JTM.html"
peta_piksel.save(str(pixel_map_path))
print(f"Jumlah piksel uji pada peta: {len(pixel_uji):,}")
print(
    "Jumlah piksel salah klasifikasi: "
    f"{int(mask_salah.sum()):,}"
)
peta_piksel
```

## Batasan Interpretasi

Peta sampel menunjukkan poligon digitasi dan label aslinya. Peta evaluasi dan peta piksel menampilkan prediksi pada data uji saja. Peta piksel menggambar lokasi sampel yang tercatat di CSV tanpa mengisi area kosong. Peta raster prediksi seluruh provinsi memerlukan citra GeoTIFF Sentinel-2 dengan band yang cocok; data CSV sampel saja tidak mewakili raster seluruh wilayah.
