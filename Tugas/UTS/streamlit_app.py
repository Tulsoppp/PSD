import html
import json
from pathlib import Path

import folium
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shapely
import streamlit as st
from shapely.geometry import mapping, shape
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler


FEATURES = ["B02", "B03", "B04", "B08", "B11", "NDVI", "NDWI", "MNDWI", "NDBI"]
EXCLUDED_POLYGON_IDS = {f"Laut_{index:04d}" for index in range(19)}
SAMPLE_GEOMETRY_FILES = {
    "Bangunan": "bangunan.zip",
    "Danau": "Danau.zip",
    "Hutan": "Lahan Hijau.zip",
    "Laut": "Laut.zip",
    "Mangrove": "Magruve.zip",
    "Sawah": "sawah.zip",
}
REQUIRED_COLUMNS = [
    "poligon_id",
    "poligon_no",
    "label",
    "label_teks",
    "lon",
    "lat",
    *FEATURES,
]
CLASS_COLORS = {
    "Sawah": "#D6A800",
    "Bangunan": "#E41A1C",
    "Hutan": "#2E7D32",
    "Danau": "#4FC3F7",
    "Laut": "#0D47A1",
    "Mangrove": "#8E44AD",
}

st.set_page_config(
    page_title="Dashboard Tutupan Lahan Jawa Timur",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&display=swap');
    :root {
        --ink: #17332F;
        --muted: #647873;
        --line: #DFEAE6;
        --teal: #0F766E;
        --teal-dark: #0B514B;
        --surface: #FFFFFF;
        --canvas: #F3F7F5;
    }
    .stApp {
        background:
            radial-gradient(ellipse at 85% 0%, rgba(15,118,110,.07), transparent 28rem),
            var(--canvas);
        color: var(--ink);
    }
    html, body, [class*="st-"] { font-family: "IBM Plex Sans", sans-serif; }
    [data-testid="stHeader"] { background: rgba(243,247,245,.88); }
    [data-testid="stMainBlockContainer"] {
        max-width: 1480px;
        padding: 2rem clamp(1.25rem, 4vw, 3.5rem) 4rem;
    }
    [data-testid="stSidebar"] {
        background: #FBFDFC;
        border-right: 1px solid var(--line);
    }
    [data-testid="stSidebar"] > div:first-child { padding-top: 1.3rem; }
    [data-testid="stSidebar"] h2 {
        color: var(--ink);
        font-size: 1.12rem;
        letter-spacing: -.02em;
    }
    [data-testid="stSidebar"] h3 {
        color: var(--muted);
        font-size: .78rem;
        letter-spacing: .08em;
        text-transform: uppercase;
    }
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
        color: var(--muted);
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        margin-bottom: .55rem;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] strong,
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
    [data-testid="stSidebar"] [data-testid="stSlider"] p {
        color: var(--ink) !important;
    }
    h2 {
        color: var(--ink);
        font-size: 1.42rem !important;
        font-weight: 700 !important;
        letter-spacing: -.035em;
        margin-top: 2.2rem !important;
        margin-bottom: .9rem !important;
    }
    h3 {
        color: var(--ink);
        font-size: 1.04rem !important;
        font-weight: 600 !important;
        letter-spacing: -.02em;
    }
    div[data-testid="stMetric"] {
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 16px;
        padding: 1.15rem 1.25rem;
        box-shadow: 0 4px 14px rgba(24,65,55,.045);
        transition: transform .18s ease, box-shadow .18s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 9px 22px rgba(24,65,55,.09);
    }
    div[data-testid="stMetricLabel"] p {
        color: var(--muted);
        font-size: .8rem;
        font-weight: 600;
    }
    div[data-testid="stMetricValue"] {
        color: var(--teal-dark);
        font-size: 1.8rem;
        font-weight: 700;
        letter-spacing: -.045em;
    }
    .hero {
        position: relative;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 2rem;
        overflow: hidden;
        background:
            radial-gradient(circle at 82% 20%, rgba(119,219,191,.28), transparent 17rem),
            linear-gradient(115deg, #0B514B, #0F766E 62%, #17877B);
        color: white;
        padding: clamp(1.7rem, 4vw, 2.6rem);
        border: 1px solid rgba(255,255,255,.13);
        border-radius: 24px;
        margin-bottom: 1.25rem;
        box-shadow: 0 16px 36px rgba(11,81,75,.16);
    }
    .hero-kicker {
        color: #A9E4D4;
        font-size: .72rem;
        font-weight: 700;
        letter-spacing: .14em;
        text-transform: uppercase;
        margin-bottom: .65rem;
    }
    .hero h1 {
        color: white;
        margin: 0;
        font-size: clamp(1.65rem, 3vw, 2.35rem);
        font-weight: 700;
        letter-spacing: -.045em;
        line-height: 1.15;
    }
    .hero p { color: #D7F0E9; margin: .7rem 0 0; font-size: .98rem; }
    .hero-badge {
        flex: 0 0 auto;
        padding: .75rem 1rem;
        color: #E9FBF5;
        border: 1px solid rgba(225,255,245,.32);
        border-radius: 14px;
        background: rgba(255,255,255,.1);
        font-size: .72rem;
        font-weight: 600;
        letter-spacing: .08em;
        line-height: 1.65;
        text-align: center;
    }
    .section-card {
        background: linear-gradient(110deg, #FFFFFF, #F8FCFA);
        border: 1px solid var(--line);
        border-left: 4px solid var(--teal);
        border-radius: 16px;
        padding: 1.15rem 1.35rem;
        margin: .5rem 0 1.25rem;
        color: #435B55;
        line-height: 1.7;
        box-shadow: 0 4px 14px rgba(24,65,55,.035);
    }
    .section-card strong { color: var(--teal-dark); }
    [data-testid="stDataFrame"] {
        border: 1px solid var(--line);
        border-radius: 14px;
        overflow: hidden;
        box-shadow: 0 3px 12px rgba(24,65,55,.035);
    }
    [data-testid="stSelectbox"] > div > div,
    [data-testid="stMultiSelect"] > div > div {
        border-radius: 10px;
        border-color: #D5E3DE;
    }
    [data-testid="stRadio"] [role="radiogroup"] {
        gap: .4rem;
        flex-wrap: wrap;
        align-items: center;
        padding: .25rem;
        border: 1px solid var(--line);
        border-radius: 12px;
        background: rgba(255,255,255,.75);
    }
    [data-testid="stRadio"] label,
    [data-testid="stRadio"] label p {
        color: var(--ink) !important;
    }
    [data-testid="stRadioOption"] {
        padding: .35rem .65rem;
        border: 1px solid #B8D8CE;
        border-radius: 999px;
        background: #FFFFFF;
        transition: background .18s ease, border-color .18s ease;
    }
    [data-testid="stRadioOption"]:hover {
        border-color: var(--teal);
        background: #F5FBF8;
    }
    [data-testid="stRadioOption"][data-selected="true"] {
        background: var(--teal-dark);
    }
    [data-testid="stRadioOption"][data-selected="true"] p {
        color: white !important;
        font-weight: 600;
    }
    [data-testid="stDownloadButton"] button {
        min-height: 2.65rem;
        color: var(--teal-dark);
        border: 1px solid #B8D8CE;
        border-radius: 10px;
        background: #F5FBF8;
        font-weight: 600;
        transition: background .18s ease, border-color .18s ease;
    }
    [data-testid="stDownloadButton"] button:hover {
        color: white;
        border-color: var(--teal);
        background: var(--teal);
    }
    [data-testid="stCaptionContainer"] p {
        color: var(--muted);
        font-size: .82rem;
    }
    @media (max-width: 700px) {
        [data-testid="stMainBlockContainer"] { padding: 1rem 1rem 3rem; }
        .hero { align-items: flex-start; border-radius: 18px; }
        .hero-badge { display: none; }
        div[data-testid="stMetric"] { padding: .9rem; }
        div[data-testid="stMetricValue"] { font-size: 1.45rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner="Memuat dataset Sentinel-2A...")
def load_dataset(path_string: str, modified_ns: int) -> pd.DataFrame:
    dataset = Path(path_string)
    if dataset.stat().st_mtime_ns != modified_ns:
        raise OSError("Dataset berubah saat sedang dimuat. Muat ulang aplikasi.")
    return pd.read_csv(dataset)


@st.cache_data(show_spinner="Memuat batas administrasi Jawa Timur...")
def load_boundary(path_string: str, modified_ns: int) -> shapely.Geometry:
    boundary_file = Path(path_string)
    if boundary_file.stat().st_mtime_ns != modified_ns:
        raise OSError("Berkas batas berubah saat sedang dimuat. Muat ulang aplikasi.")
    with boundary_file.open(encoding="utf-8") as file:
        feature = json.load(file)
    if feature.get("properties", {}).get("adm1_pcode") != "ID35":
        raise ValueError("Berkas geometri bukan batas Provinsi Jawa Timur.")
    boundary = shape(feature["geometry"])
    if boundary.is_empty or not boundary.is_valid:
        raise ValueError("Geometri batas Provinsi Jawa Timur tidak valid.")
    return boundary


@st.cache_data(show_spinner="Memuat poligon hasil digitasi...")
def load_sample_geometries(
    digitasi_path_string: str,
    file_signatures: tuple[tuple[str, int], ...],
    boundary_path_string: str,
    boundary_modified_ns: int,
) -> dict[str, dict[int, dict[str, object]]]:
    digitasi_path = Path(digitasi_path_string)
    expected_signatures = dict(file_signatures)
    boundary = load_boundary(boundary_path_string, boundary_modified_ns)
    geometries: dict[str, dict[int, dict[str, object]]] = {}

    for land_class, filename in SAMPLE_GEOMETRY_FILES.items():
        source = digitasi_path / filename
        if source.stat().st_mtime_ns != expected_signatures[filename]:
            raise OSError("Berkas poligon berubah saat sedang dimuat. Muat ulang aplikasi.")
        layer = gpd.read_file(f"/vsizip/{source.as_posix()}/input.shp")
        if "FID" not in layer.columns:
            raise ValueError(f"Atribut FID tidak ditemukan pada {source}.")
        if layer["FID"].duplicated().any():
            raise ValueError(f"Atribut FID duplikat ditemukan pada {source}.")
        if layer.crs is None:
            raise ValueError(f"CRS tidak ditemukan pada {source}.")
        if layer.crs.to_epsg() != 4326:
            layer = layer.to_crs(epsg=4326)

        class_geometries: dict[int, dict[str, object]] = {}
        for feature in layer.itertuples():
            geometry = feature.geometry
            if geometry is None or geometry.is_empty:
                raise ValueError(f"Geometri kosong ditemukan pada {source}, FID {feature.FID}.")
            if not geometry.is_valid:
                geometry = shapely.make_valid(geometry)
            if land_class != "Laut":
                geometry = geometry.intersection(boundary)
            if not geometry.is_empty:
                class_geometries[int(feature.FID)] = mapping(geometry)
        geometries[land_class] = class_geometries

    return geometries


def filter_points_inside_boundary(
    data: pd.DataFrame, boundary: shapely.Geometry
) -> pd.DataFrame:
    coordinates = data[["lon", "lat"]].to_numpy(dtype=np.float64)
    finite_coordinates = np.isfinite(coordinates).all(axis=1)
    inside = np.zeros(len(data), dtype=bool)
    inside[finite_coordinates] = shapely.contains_xy(
        boundary,
        coordinates[finite_coordinates, 0],
        coordinates[finite_coordinates, 1],
    )
    keep_laut = data["label_teks"].eq("Laut").to_numpy()
    keep_polygon = ~data["poligon_id"].isin(EXCLUDED_POLYGON_IDS).to_numpy()
    return data.loc[finite_coordinates & keep_polygon & (inside | keep_laut)].copy()


@st.cache_data(show_spinner="Menyaring piksel di luar batas Jawa Timur...")
def load_filtered_dataset(
    path_string: str,
    modified_ns: int,
    boundary_path_string: str,
    boundary_modified_ns: int,
) -> pd.DataFrame:
    data = load_dataset(path_string, modified_ns)
    boundary = load_boundary(boundary_path_string, boundary_modified_ns)
    return filter_points_inside_boundary(data, boundary)


@st.cache_data(show_spinner="Menyiapkan sampel poligon...")
def make_polygons(
    path_string: str,
    modified_ns: int,
    boundary_path_string: str,
    boundary_modified_ns: int,
) -> pd.DataFrame:
    data = load_filtered_dataset(
        path_string, modified_ns, boundary_path_string, boundary_modified_ns
    )
    clean = (
        data[REQUIRED_COLUMNS]
        .replace([np.inf, -np.inf], np.nan)
        .dropna()
        .copy()
    )
    polygons = (
        clean.groupby("poligon_id", as_index=False)
        .agg(
            poligon_no=("poligon_no", "first"),
            label=("label", "first"),
            label_teks=("label_teks", "first"),
            lon=("lon", "mean"),
            lat=("lat", "mean"),
            **{feature: (feature, "mean") for feature in FEATURES},
        )
    )
    boundary = load_boundary(boundary_path_string, boundary_modified_ns)
    return filter_points_inside_boundary(polygons, boundary)


@st.cache_data(show_spinner="Melatih dan mengevaluasi model...")
def evaluate_models(
    path_string: str,
    modified_ns: int,
    boundary_path_string: str,
    boundary_modified_ns: int,
    neighbors: int,
) -> dict[str, dict[str, object]]:
    polygons = make_polygons(
        path_string, modified_ns, boundary_path_string, boundary_modified_ns
    )
    classes = sorted(polygons["label_teks"].unique())
    indices = np.arange(len(polygons))
    train_indices, test_indices = train_test_split(
        indices,
        test_size=0.3,
        random_state=42,
        stratify=polygons["label_teks"],
    )

    x_train = polygons.iloc[train_indices][FEATURES]
    x_test = polygons.iloc[test_indices][FEATURES]
    y_train = polygons.iloc[train_indices]["label_teks"]
    y_test = polygons.iloc[test_indices]["label_teks"]
    test_polygon_ids = polygons.iloc[test_indices]["poligon_id"]
    pixel_test = load_filtered_dataset(
        path_string,
        modified_ns,
        boundary_path_string,
        boundary_modified_ns,
    )
    pixel_test = pixel_test.loc[
        pixel_test["poligon_id"].isin(test_polygon_ids),
        ["poligon_id", "label_teks", *FEATURES],
    ].replace([np.inf, -np.inf], np.nan).dropna().copy()
    if pixel_test.empty:
        raise ValueError("Tidak ada piksel uji yang tersedia untuk peta evaluasi.")

    scaler = StandardScaler()
    x_train_scaled = scaler.fit_transform(x_train)
    x_test_scaled = scaler.transform(x_test)

    estimators = {
        "Gaussian Naive Bayes": GaussianNB(),
        f"K-Nearest Neighbors (k={neighbors})": KNeighborsClassifier(
            n_neighbors=neighbors
        ),
    }
    results: dict[str, dict[str, object]] = {}
    for name, estimator in estimators.items():
        estimator.fit(x_train_scaled, y_train)
        prediction = estimator.predict(x_test_scaled)
        report = classification_report(
            y_test, prediction, labels=classes, output_dict=True, zero_division=0
        )
        report_frame = pd.DataFrame(report).transpose()
        matrix = confusion_matrix(y_test, prediction, labels=classes)
        prediction_frame = polygons.iloc[test_indices][
            ["poligon_id", "poligon_no", "label_teks", "lon", "lat"]
        ].copy()
        prediction_frame = prediction_frame.rename(
            columns={"label_teks": "kelas_asli"}
        )
        prediction_frame["prediksi"] = prediction
        prediction_frame["benar"] = (
            prediction_frame["kelas_asli"] == prediction_frame["prediksi"]
        )
        pixel_prediction = pixel_test[["poligon_id", "label_teks"]].copy()
        pixel_prediction["benar"] = (
            estimator.predict(scaler.transform(pixel_test[FEATURES]))
            == pixel_prediction["label_teks"].to_numpy()
        )
        pixel_metrics = (
            pixel_prediction.groupby("poligon_id", as_index=False)
            .agg(
                piksel_benar=("benar", "sum"),
                jumlah_piksel_uji=("benar", "size"),
            )
        )
        pixel_metrics["akurasi_piksel"] = (
            pixel_metrics["piksel_benar"] / pixel_metrics["jumlah_piksel_uji"]
        )
        prediction_frame = prediction_frame.merge(
            pixel_metrics, on="poligon_id", how="left", validate="one_to_one"
        )
        if prediction_frame["akurasi_piksel"].isna().any():
            raise ValueError(
                "Sebagian poligon uji tidak memiliki piksel untuk peta evaluasi."
            )
        results[name] = {
            "accuracy": accuracy_score(y_test, prediction),
            "report": report_frame,
            "matrix": pd.DataFrame(
                matrix, index=classes, columns=classes
            ),
            "predictions": prediction_frame.reset_index(drop=True),
        }
    return results


def find_dataset() -> Path:
    dataset = Path(__file__).resolve().with_name("piksel_s2_JTM.csv")
    if not dataset.is_file():
        raise FileNotFoundError(
            f"Dataset tidak ditemukan di sebelah aplikasi: {dataset}"
        )
    return dataset


def find_boundary() -> Path:
    boundary = Path(__file__).resolve().with_name("batas_jawa_timur.geojson")
    if not boundary.is_file():
        raise FileNotFoundError(
            f"Batas Jawa Timur tidak ditemukan di sebelah aplikasi: {boundary}"
        )
    return boundary


def find_digitasi_folder() -> Path:
    digitasi = Path(__file__).resolve().parents[2] / "DIGITASI"
    missing_files = [
        filename
        for filename in SAMPLE_GEOMETRY_FILES.values()
        if not (digitasi / filename).is_file()
    ]
    if missing_files:
        raise FileNotFoundError(
            f"Arsip poligon tidak ditemukan di {digitasi}: {missing_files}"
        )
    return digitasi


st.markdown(
    """
    <div class="hero">
          <div>
            <div class="hero-kicker">Dashboard analisis geospasial</div>
            <h1>Klasifikasi Tutupan Lahan<br>Jawa Timur</h1>
            <p>Eksplorasi sampel Sentinel-2A dan evaluasi model klasifikasi</p>
          </div>
          <div class="hero-badge">SENTINEL-2A<br>JAWA TIMUR</div>
        </div>
    """,
    unsafe_allow_html=True,
)

try:
    dataset_path = find_dataset()
    boundary_path = find_boundary()
    digitasi_path = find_digitasi_folder()
    modified_ns = dataset_path.stat().st_mtime_ns
    boundary_modified_ns = boundary_path.stat().st_mtime_ns
    geometry_signatures = tuple(
        (filename, (digitasi_path / filename).stat().st_mtime_ns)
        for filename in SAMPLE_GEOMETRY_FILES.values()
    )
    source_df = load_dataset(str(dataset_path), modified_ns)
    missing_columns = sorted(set(REQUIRED_COLUMNS) - set(source_df.columns))
    if missing_columns:
        raise ValueError(f"Kolom dataset yang diperlukan tidak ditemukan: {missing_columns}")
    df = load_filtered_dataset(
        str(dataset_path),
        modified_ns,
        str(boundary_path),
        boundary_modified_ns,
    )
    if df.empty:
        raise ValueError("Tidak ada piksel yang berada di dalam batas Jawa Timur.")
    polygons = make_polygons(
        str(dataset_path),
        modified_ns,
        str(boundary_path),
        boundary_modified_ns,
    )
    sample_geometries = load_sample_geometries(
        str(digitasi_path),
        geometry_signatures,
        str(boundary_path),
        boundary_modified_ns,
    )
    missing_geometries = [
        (row.label_teks, int(row.poligon_no))
        for row in polygons.itertuples()
        if int(row.poligon_no) not in sample_geometries.get(row.label_teks, {})
    ]
    if missing_geometries:
        raise ValueError(
            f"Geometri digitasi tidak ditemukan untuk sampel: {missing_geometries[:5]}"
        )
    if polygons.empty:
        raise ValueError(
            "Tidak ada poligon valid yang tersisa di dalam batas Jawa Timur."
        )
except (OSError, ValueError, pd.errors.ParserError) as error:
    st.error(f"Dataset tidak dapat dimuat: {error}")
    st.stop()

classes = sorted(polygons["label_teks"].dropna().unique())
if not classes:
    st.error("Dataset tidak memiliki label kelas yang valid.")
    st.stop()

with st.sidebar:
    st.markdown("## Pengaturan")
    st.caption("Sumber data: `piksel_s2_JTM.csv`")
    st.markdown("### Kelas tutupan lahan")
    for land_class in classes:
        color = CLASS_COLORS.get(land_class, "#475569")
        st.markdown(
            f'<span style="color:{color}; font-size:1.1rem;">●</span> '
            f"**{html.escape(str(land_class))}**",
            unsafe_allow_html=True,
        )
    st.divider()
    selected_classes = st.multiselect(
        "Filter kelas pada peta dan tabel",
        options=classes,
        default=classes,
    )
    neighbors = st.slider(
        "Jumlah tetangga untuk KNN",
        min_value=1,
        max_value=min(15, max(1, len(polygons) - 1)),
        value=min(5, max(1, len(polygons) - 1)),
    )
    map_limit = st.slider(
        "Jumlah poligon yang ditampilkan di peta",
        min_value=1,
        max_value=len(polygons),
        value=len(polygons),
    )

try:
    results = evaluate_models(
        str(dataset_path),
        modified_ns,
        str(boundary_path),
        boundary_modified_ns,
        neighbors,
    )
except ValueError as error:
    st.error(f"Evaluasi model tidak dapat dijalankan: {error}")
    st.stop()

best_model = max(results, key=lambda name: float(results[name]["accuracy"]))
pixel_classes = df["label_teks"].value_counts()
st.markdown(
    f"""
    <div class="section-card">
    <b>Ringkasan analisis</b><br>
    Dataset mencakup <b>{len(df):,} piksel</b> yang diringkas menjadi
    <b>{len(polygons):,} poligon sampel</b>. Model terbaik saat ini adalah
    <b>{best_model}</b> dengan akurasi <b>{float(results[best_model]["accuracy"]):.2%}</b>.
    Peta menggunakan poligon hasil digitasi yang dicocokkan dengan FID/nomor poligon.
    </div>
    """,
    unsafe_allow_html=True,
)

metric_columns = st.columns(4)
metric_columns[0].metric("Piksel pada dataset", f"{len(df):,}")
metric_columns[1].metric("Poligon sampel", f"{len(polygons):,}")
metric_columns[2].metric("Jumlah kelas", len(classes))
metric_columns[3].metric("Akurasi terbaik", f"{float(results[best_model]['accuracy']):.2%}")

st.markdown("## Distribusi Sampel")
chart_columns = st.columns(2)
with chart_columns[0]:
    st.markdown("### Jumlah piksel per kelas")
    st.caption("Perbandingan jumlah sampel pada setiap kategori tutupan lahan.")
    pixel_counts = pixel_classes.reindex(classes, fill_value=0).sort_values()
    figure, axis = plt.subplots(figsize=(8, 4.5))
    figure.patch.set_facecolor("#FFFFFF")
    axis.set_facecolor("#FFFFFF")
    axis.barh(
        pixel_counts.index,
        pixel_counts.values,
        color=[CLASS_COLORS.get(name, "#475569") for name in pixel_counts.index],
        height=0.62,
    )
    axis.set_xlabel("Jumlah piksel")
    axis.set_ylabel("")
    axis.grid(axis="x", alpha=0.18, color="#6F8980")
    axis.set_axisbelow(True)
    axis.spines[["top", "right", "left"]].set_visible(False)
    axis.tick_params(axis="y", length=0, labelcolor="#344E46")
    axis.tick_params(axis="x", colors="#73857F")
    figure.tight_layout()
    st.pyplot(figure, width="stretch")
    plt.close(figure)

with chart_columns[1]:
    st.markdown("### Nilai NDVI per kelas")
    st.caption("Sebaran indeks vegetasi setelah kelas dipilih di panel samping.")
    box_classes = [name for name in classes if name in selected_classes]
    if box_classes:
        figure, axis = plt.subplots(figsize=(8, 4.5))
        values = [
            df.loc[df["label_teks"] == name, "NDVI"].dropna().sample(
                n=min(10000, df.loc[df["label_teks"] == name, "NDVI"].notna().sum()),
                random_state=42,
            )
            for name in box_classes
        ]
        boxes = axis.boxplot(values, tick_labels=box_classes, patch_artist=True)
        for box, name in zip(boxes["boxes"], box_classes):
            box.set_facecolor(CLASS_COLORS.get(name, "#CBD5E1"))
            box.set_alpha(0.78)
        figure.patch.set_facecolor("#FFFFFF")
        axis.set_facecolor("#FFFFFF")
        axis.set_ylabel("NDVI")
        axis.tick_params(axis="x", rotation=30)
        axis.grid(axis="y", alpha=0.18, color="#6F8980")
        axis.set_axisbelow(True)
        axis.spines[["top", "right"]].set_visible(False)
        axis.tick_params(colors="#73857F")
        figure.tight_layout()
        st.pyplot(figure, width="stretch")
        plt.close(figure)
    else:
        st.info("Pilih minimal satu kelas untuk menampilkan nilai NDVI.")

st.markdown("## Peta Sampel Interaktif")
if selected_classes:
    map_data = polygons[polygons["label_teks"].isin(selected_classes)].copy()
    map_data = map_data.head(map_limit)
    center = [float(map_data["lat"].mean()), float(map_data["lon"].mean())]
    sample_map = folium.Map(
        location=center,
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
    ).add_to(sample_map)
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
    ).add_to(sample_map)
    for land_class in selected_classes:
        safe_class = html.escape(str(land_class))
        layer = folium.FeatureGroup(name=safe_class)
        class_rows = map_data[map_data["label_teks"] == land_class]
        for row in class_rows.itertuples():
            color = CLASS_COLORS.get(land_class, "#475569")
            folium.GeoJson(
                data=sample_geometries[land_class][int(row.poligon_no)],
                style_function=lambda _feature, color=color: {
                    "color": color,
                    "weight": 1,
                    "fillColor": color,
                    "fillOpacity": 0.2,
                },
                tooltip=(
                    f"{html.escape(str(row.poligon_id))} | "
                    f"Kelas: {safe_class}"
                ),
            ).add_to(layer)
        layer.add_to(sample_map)
    folium.LayerControl(collapsed=False).add_to(sample_map)
    st.iframe(sample_map.get_root().render(), height=580)
    st.caption(
        f"Menampilkan {len(map_data):,} dari {len(polygons):,} poligon sampel "
        "hasil digitasi."
    )
else:
    st.info("Pilih minimal satu kelas pada sidebar untuk menampilkan peta.")

st.markdown("## Evaluasi Model")
st.caption("Perbandingan performa model pada pembagian data uji yang sama.")
comparison = pd.DataFrame(
    {
        name: {
            "Akurasi": float(result["accuracy"]),
            "Macro precision": float(result["report"].loc["macro avg", "precision"]),
            "Macro recall": float(result["report"].loc["macro avg", "recall"]),
            "Macro F1-score": float(result["report"].loc["macro avg", "f1-score"]),
        }
        for name, result in results.items()
    }
).T
st.dataframe(
    comparison.style
    .format("{:.2%}")
    .background_gradient(cmap="Greens", axis=None),
    width="stretch",
)

model_to_show = st.selectbox("Pilih model untuk melihat rincian", list(results))
model_result = results[model_to_show]
evaluation_columns = st.columns(2)
with evaluation_columns[0]:
    st.markdown(f"### Confusion matrix — {model_to_show}")
    st.dataframe(
        model_result["matrix"].style.background_gradient(cmap="Blues", axis=None),
        width="stretch",
    )
with evaluation_columns[1]:
    st.markdown(f"### Laporan klasifikasi — {model_to_show}")
    st.caption("Metrik dihitung untuk setiap kelas pada data uji.")
    report = model_result["report"].loc[classes, ["precision", "recall", "f1-score", "support"]]
    st.dataframe(
        report.style.format(
            {"precision": "{:.2f}", "recall": "{:.2f}", "f1-score": "{:.2f}", "support": "{:.0f}"}
        ),
        width="stretch",
    )

predictions = model_result["predictions"].copy()
predictions = predictions[predictions["kelas_asli"].isin(selected_classes)]
st.markdown(f"## Peta Hasil Prediksi — {model_to_show}")
st.caption(
    "Peta ini terpisah dari peta sampel di atas. Warna poligon menunjukkan "
    "kelas aktual; tanda centang hijau berarti prediksi kelas poligon cocok "
    "dengan kelas aktual, sedangkan tanda seru merah berarti kelasnya berbeda. "
    "Arahkan atau klik poligon untuk melihat akurasi piksel di dalamnya."
)
if predictions.empty:
    st.info("Pilih minimal satu kelas untuk menampilkan hasil prediksi pada peta.")
else:
    prediction_map = folium.Map(
        location=[
            float(predictions["lat"].mean()),
            float(predictions["lon"].mean()),
        ],
        zoom_start=6,
        tiles="Esri.WorldImagery",
    )
    folium.TileLayer(
        tiles="OpenStreetMap",
        name="OpenStreetMap",
        max_zoom=19,
        show=False,
    ).add_to(prediction_map)
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
    ).add_to(prediction_map)
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
    ).add_to(prediction_map)

    for land_class in selected_classes:
        class_rows = predictions[predictions["kelas_asli"] == land_class]
        if class_rows.empty:
            continue
        safe_class = html.escape(str(land_class))
        layer = folium.FeatureGroup(name=f"Kelas: {safe_class}", show=True)
        class_color = CLASS_COLORS.get(land_class, "#475569")
        for row in class_rows.itertuples():
            polygon_id = html.escape(str(row.poligon_id))
            accuracy = float(row.akurasi_piksel)
            status = (
                "Prediksi kelas poligon benar"
                if row.benar
                else "Prediksi kelas poligon salah"
            )
            details = (
                f"<b>{polygon_id}</b><br>"
                f"Kelas aktual: {safe_class}<br>"
                f"Prediksi poligon: {html.escape(str(row.prediksi))}<br>"
                f"Piksel uji benar: {int(row.piksel_benar):,}/"
                f"{int(row.jumlah_piksel_uji):,} "
                f"({accuracy:.1%})<br>"
                f"Status: {status}"
            )
            folium.GeoJson(
                data=sample_geometries[land_class][int(row.poligon_no)],
                style_function=lambda _feature, color=class_color: {
                    "color": color,
                    "weight": 1.5,
                    "fillColor": color,
                    "fillOpacity": 0.35,
                },
                tooltip=details,
                popup=folium.Popup(details, max_width=320),
            ).add_to(layer)
        layer.add_to(prediction_map)

    correct_layer = folium.FeatureGroup(name="Prediksi benar (Data Uji)")
    incorrect_layer = folium.FeatureGroup(name="Salah klasifikasi (Data Uji)")
    for row in predictions.itertuples():
        pixel_accuracy = float(row.akurasi_piksel)
        is_correct = bool(row.benar)
        status_label = (
            "Prediksi kelas poligon benar"
            if is_correct
            else "Prediksi kelas poligon salah"
        )
        status_color = "#10B981" if is_correct else "#E11D48"
        marker_character = "✓" if is_correct else "!"
        polygon_id = html.escape(str(row.poligon_id))
        details = (
            f"<b>{polygon_id}</b><br>"
            f"Kelas aktual: {html.escape(str(row.kelas_asli))}<br>"
            f"Prediksi poligon: {html.escape(str(row.prediksi))}<br>"
            f"Piksel uji benar: {int(row.piksel_benar):,}/"
            f"{int(row.jumlah_piksel_uji):,} ({pixel_accuracy:.1%})<br>"
            f"Status: {status_label}"
        )
        marker = folium.Marker(
            location=[float(row.lat), float(row.lon)],
            tooltip=f"{status_label}: {polygon_id}",
            popup=folium.Popup(details, max_width=320),
            icon=folium.DivIcon(
                html=(
                    '<div style="width:24px;height:24px;border:2px solid white;'
                    f'border-radius:50%;background:{status_color};color:white;'
                    'display:flex;align-items:center;justify-content:center;'
                    'font-weight:800;font-size:15px;'
                    'box-shadow:0 2px 8px rgba(0,0,0,.45);">'
                    f"{marker_character}</div>"
                ),
                icon_size=(24, 24),
                icon_anchor=(12, 12),
                class_name="prediction-status-marker",
            ),
        )
        (correct_layer if is_correct else incorrect_layer).add_child(marker)
    correct_layer.add_to(prediction_map)
    incorrect_layer.add_to(prediction_map)
    folium.LayerControl(collapsed=False).add_to(prediction_map)
    st.iframe(prediction_map.get_root().render(), height=580)
    st.caption(
        f"Data uji: {len(predictions):,} poligon; "
        f"{int(predictions['benar'].sum()):,} prediksi kelas poligon benar "
        f"({float(predictions['benar'].mean()):.2%}) dan "
        f"{int((~predictions['benar']).sum()):,} salah. "
        f"{int((predictions['akurasi_piksel'] == 1).sum()):,} poligon seluruh "
        f"pikselnya benar dan {int((predictions['akurasi_piksel'] < 1).sum()):,} "
        "poligon memiliki sebagian piksel yang salah; metrik ini berbeda dari "
        "akurasi klasifikasi tingkat poligon."
    )

status_filter = st.radio(
    "Filter hasil prediksi",
    ["Semua", "Prediksi benar", "Salah klasifikasi"],
    horizontal=True,
)
if status_filter == "Prediksi benar":
    predictions = predictions[predictions["benar"]]
elif status_filter == "Salah klasifikasi":
    predictions = predictions[~predictions["benar"]]

st.markdown("## Eksplorasi Data Uji")
st.caption("Filter status di bawah hanya mengatur tabel dan unduhan CSV.")
st.caption(f"Menampilkan {len(predictions):,} baris sesuai kelas dan status prediksi yang dipilih.")
st.dataframe(predictions, width="stretch", height=360)
st.download_button(
    "Unduh hasil prediksi data uji (CSV)",
    data=predictions.to_csv(index=False).encode("utf-8"),
    file_name="prediksi_tutupan_lahan_jatim.csv",
    mime="text/csv",
)

st.markdown("## Pratinjau Dataset")
preview = df[df["label_teks"].isin(selected_classes)] if selected_classes else df.iloc[0:0]
st.caption(f"Pratinjau dibatasi hingga 1.000 dari {len(preview):,} baris yang sesuai filter kelas.")
st.dataframe(preview.head(1000), width="stretch", height=360)
st.download_button(
    "Unduh dataset sesuai filter kelas (CSV)",
    data=preview.to_csv(index=False).encode("utf-8"),
    file_name="sampel_tutupan_lahan_jatim.csv",
    mime="text/csv",
)

st.caption(
    "Pembagian data menggunakan test_size=0.3, random_state=42, dan stratifikasi "
    "berdasarkan kelas. Piksel diringkas per poligon sebelum evaluasi untuk "
    "mengurangi kebocoran antar data latih dan data uji."
)