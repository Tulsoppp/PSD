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

Peta interaktif menggunakan geometri poligon digitasi asli dari arsip shapefile di folder `DIGITASI`. Atribut `FID` pada shapefile dicocokkan dengan `poligon_no` pada CSV. Poligon daratan dipotong mengikuti batas Jawa Timur; piksel daratan di luar batas juga disaring sebelum agregasi. Poligon `Laut_0000` hingga `Laut_0018` dikecualikan. Basemap memakai citra satelit Esri World Imagery dengan layer referensi Esri untuk label/nama tempat, batas, dan jalan.

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

## Batasan Interpretasi

Visualisasi menunjukkan **poligon sampel digitasi dan label aslinya**, bukan hasil `predict` model pada seluruh piksel citra. CSV digunakan untuk menyaring sampel, menghitung pusat peta, dan mencocokkan poligon digitasi; geometri yang digambar berasal dari shapefile asli.
