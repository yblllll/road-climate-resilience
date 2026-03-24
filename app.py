"""
Road Climate Resilience Framework — Interactive Platform
=========================================================
Streamlit application for visualising and computing road-level
climate sensitivity from traffic and weather data.

Run:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
import json
import os
import sys
import streamlit

# Streamlit version compatibility
_ST_VERSION = tuple(int(x) for x in streamlit.__version__.split(".")[:2])
_USE_WIDTH = {"width": "stretch"} if _ST_VERSION >= (1, 45) else {"use_container_width": True}

# Page config
st.set_page_config(
    page_title="Road Climate Resilience Framework",
    page_icon="🛣️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Paths
DATA_DIR = os.path.join(os.path.dirname(__file__), "data", "example")
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
USER_RESULTS_DIR = os.path.join(UPLOAD_DIR, "results")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# DARe brand colours
DARE_NAVY = "#00295E"
DARE_GREEN = "#5B9A2F"
DARE_GRAY = "#32373C"
DARE_LIGHT = "#F5F7FA"

# Resolve logo paths for embedding
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
_logo_small_path = os.path.join(ASSETS_DIR, "dare_logo_small.png")
_logo_main_path = os.path.join(ASSETS_DIR, "dare_logo.png")       # green bg, user to provide
_watermark_path = os.path.join(ASSETS_DIR, "dare_watermark.png")   # faded sun, user to provide

# Build base64 logo for CSS embedding (avoids relative path issues)
import base64 as _b64

def _img_to_b64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return _b64.b64encode(f.read()).decode()
    return None

_logo_header_path = os.path.join(ASSETS_DIR, "dare_logo_header.png")
_sunburst_path = os.path.join(ASSETS_DIR, "dare_sunburst.png")
# Header center logo
_logo_b64 = _img_to_b64(_logo_header_path) or _img_to_b64(_logo_small_path)
# Sunburst background watermark
_sunburst_b64 = _img_to_b64(_sunburst_path)
_watermark_b64 = _img_to_b64(_watermark_path)

# CSS for watermark background (sunburst SVG fallback if no image)
_watermark_css = ""
if _sunburst_b64:
    _watermark_css = f"""
    /* Sunburst watermark — centered background behind content */
    [data-testid="stAppViewContainer"]::before {{
        content: "";
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -45%);
        width: 50%;
        height: 60%;
        background-image: url("data:image/png;base64,{_sunburst_b64}");
        background-size: contain;
        background-repeat: no-repeat;
        background-position: center;
        opacity: 0.15;
        pointer-events: none;
        z-index: 0;
    }}
    """
else:
    _watermark_css = ""

# Top header CSS with DARe logo centered
_topright_logo_css = ""
if _logo_b64:
    _topright_logo_css = f"""
    /* Fixed white header bar */
    [data-testid="stHeader"] {{
        background-color: #FFFFFF !important;
        height: 60px !important;
        border-bottom: 1px solid #e0e4e8;
        z-index: 998;
    }}
    /* DARe logo centered in header */
    [data-testid="stAppViewContainer"]::after {{
        content: "";
        position: fixed;
        top: 5px;
        left: 50%;
        transform: translateX(-50%);
        width: 140px;
        height: 50px;
        background-image: url("data:image/png;base64,{_logo_b64}");
        background-size: contain;
        background-repeat: no-repeat;
        background-position: center;
        pointer-events: none;
        z-index: 1000;
    }}
    """

# Inject DARe branded CSS
st.markdown(f"""
<style>
    /* Sidebar header */
    [data-testid="stSidebar"] > div:first-child {{
        padding-top: 1rem;
    }}
    /* Metric cards */
    [data-testid="stMetric"] {{
        background: {DARE_LIGHT};
        border: 1px solid #e0e4e8;
        border-radius: 8px;
        padding: 12px 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }}
    [data-testid="stMetricLabel"] {{
        color: {DARE_NAVY};
        font-weight: 600;
    }}
    /* Primary button */
    .stButton > button[kind="primary"] {{
        background-color: {DARE_NAVY};
        border-color: {DARE_NAVY};
    }}
    .stButton > button[kind="primary"]:hover {{
        background-color: {DARE_GREEN};
        border-color: {DARE_GREEN};
    }}
    /* Success messages */
    .stSuccess {{
        border-left-color: {DARE_GREEN};
    }}
    /* Divider */
    hr {{
        border-color: #e0e4e8;
    }}
    /* Footer brand bar */
    .dare-footer {{
        text-align: center;
        padding: 1rem 0;
        color: #8a9bae;
        font-size: 0.8rem;
        border-top: 1px solid #e0e4e8;
        margin-top: 2rem;
    }}
    .dare-footer a {{
        color: {DARE_NAVY};
        text-decoration: none;
    }}
    /* Ensure main content stays above watermark */
    [data-testid="stAppViewContainer"] > div {{
        position: relative;
        z-index: 1;
    }}
    {_watermark_css}
    {_topright_logo_css}
</style>
""", unsafe_allow_html=True)

# Discrete colour palettes (red=vulnerable → green=resilient)
PALETTES = {
    2: ["#d73027", "#1a9850"],
    3: ["#d73027", "#fee08b", "#1a9850"],
    4: ["#d73027", "#fc8d59", "#91cf60", "#1a9850"],
    5: ["#d73027", "#fc8d59", "#fee08b", "#91cf60", "#1a9850"],
    6: ["#d73027", "#fc8d59", "#fee08b", "#d9ef8b", "#91cf60", "#1a9850"],
    7: ["#d73027", "#f46d43", "#fee08b", "#ffffbf", "#d9ef8b", "#91cf60", "#1a9850"],
    8: ["#d73027", "#f46d43", "#fdae61", "#fee08b", "#d9ef8b", "#a6d96a", "#66bd63", "#1a9850"],
    9: ["#a50026", "#d73027", "#f46d43", "#fdae61", "#fee08b", "#d9ef8b", "#a6d96a", "#66bd63", "#1a9850"],
    10: ["#a50026", "#d73027", "#f46d43", "#fdae61", "#fee08b", "#d9ef8b", "#a6d96a", "#66bd63", "#1a9850", "#006837"],
}


# ---- Sidebar ----
# DARe logo (if available)
logo_path = os.path.join(os.path.dirname(__file__), "assets", "dare_logo_small.png")
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, width=200)
else:
    st.sidebar.markdown(
        f'<h2 style="color:{DARE_NAVY};margin-bottom:0;">Road Climate<br>Resilience</h2>',
        unsafe_allow_html=True,
    )
st.sidebar.markdown(
    f'<p style="color:{DARE_GREEN};font-weight:600;margin-top:4px;">'
    f'Estimate → Map → Explain</p>',
    unsafe_allow_html=True,
)

page = st.sidebar.radio(
    "Navigation",
    ["Interactive Resilience Map", "Summary Dashboard", "Run Your Own Analysis", "About"],
)


# ---- Helper functions ----
@st.cache_data
def _pick(filename, *dirs):
    """Return the first existing path for filename across directories (user results first)."""
    for d in dirs:
        p = os.path.join(d, filename)
        if os.path.exists(p):
            return p
    return None


def load_example_data():
    """Load data — prioritises user GLM results from uploads/results/, falls back to data/example/."""
    # Priority order: user results > example data
    dirs = [USER_RESULTS_DIR, DATA_DIR]

    data = {}
    data["source"] = "example"  # will be overridden if user data found

    # GeoJSON (always from example unless user uploaded)
    geojson_path = _pick("linkgis.geojson", *dirs)
    if geojson_path:
        with open(geojson_path) as f:
            data["geojson"] = json.load(f)

    links_path = _pick("srn_links_resilience.geojson", *dirs)
    if links_path:
        with open(links_path) as f:
            data["links_geojson"] = json.load(f)

    coef_path = _pick("link_coefficients_with_features.csv", *dirs)
    if coef_path:
        data["coefficients"] = pd.read_csv(coef_path)

    feature_path = _pick("road_features_with_infrastructure.csv", *dirs)
    if feature_path:
        data["features"] = pd.read_csv(feature_path)

    # GLM results — this is the key one that changes after user runs analysis
    glm_path = _pick("gamma_glm_full_results.csv", *dirs)
    if glm_path:
        data["glm_results"] = pd.read_csv(glm_path)
        if USER_RESULTS_DIR in glm_path:
            data["source"] = "user"

    # Model summary statistics
    summary_json_path = _pick("model_summary.json", *dirs)
    if summary_json_path:
        with open(summary_json_path) as f:
            data["model_summary"] = json.load(f)
        if USER_RESULTS_DIR in summary_json_path:
            data["source"] = "user"

    summary_txt_path = _pick("gamma_glm_summary.txt", *dirs)
    if summary_txt_path:
        with open(summary_txt_path) as f:
            data["model_summary_text"] = f.read()

    # Precipitation interaction results
    interaction_path = _pick("precipitation_interaction_results.csv", *dirs)
    if interaction_path:
        data["interactions"] = pd.read_csv(interaction_path)

    return data


def get_discrete_color(value, vmin, vmax, n_levels=5):
    """Map a coefficient to a discrete colour from a red-yellow-green palette."""
    if pd.isna(value):
        return "#888888", -1

    palette = PALETTES.get(n_levels, PALETTES[5])

    if vmax == vmin:
        idx = len(palette) // 2
    else:
        norm = (value - vmin) / (vmax - vmin)
        norm = max(0.0, min(1.0, norm))
        idx = int(norm * (len(palette) - 1))
        idx = min(idx, len(palette) - 1)

    return palette[idx], idx


def build_resilience_map(geojson_data, n_levels=5, center_lat=52.25, center_lon=0.1):
    """Build a Folium map with resilience-coloured markers."""
    m = folium.Map(location=[center_lat, center_lon], zoom_start=10,
                   tiles="CartoDB positron")

    features = geojson_data.get("features", [])
    if not features:
        return m

    # Get coefficient range for colour scaling
    coeffs = []
    for f in features:
        props = f.get("properties", {})
        val = props.get("precipit_1") or props.get("precipitat")
        if val is not None:
            coeffs.append(float(val))

    if not coeffs:
        return m

    vmin, vmax = min(coeffs), max(coeffs)

    for feature in features:
        props = feature.get("properties", {})
        geom = feature.get("geometry", {})
        coords = geom.get("coordinates", [])

        if not coords or len(coords) < 2:
            continue

        lon, lat = coords[0], coords[1]
        coef_total = props.get("precipit_1")  # total precipitation effect
        coef_interaction = props.get("interactio")  # interaction term
        highway = props.get("highway", "N/A")
        road_name = props.get("road_name", "N/A")
        link_name = props.get("linkname", "N/A")
        p_value = props.get("p_value", "N/A")
        significance = props.get("significan", "")

        color, _ = get_discrete_color(coef_total, vmin, vmax, n_levels) if coef_total is not None else ("#888888", -1)

        popup_html = f"""
        <div style="font-family: Arial; font-size: 12px; min-width: 220px;">
            <b style="font-size: 14px;">{road_name}</b><br>
            <hr style="margin: 4px 0;">
            <b>Highway:</b> {highway}<br>
            <b>Link ID:</b> {link_name}<br>
            <hr style="margin: 4px 0;">
            <b>Total Precip. Effect:</b> {f'{coef_total:.6f}' if isinstance(coef_total, (int, float)) else 'N/A'}<br>
            <b>Interaction Term:</b> {f'{coef_interaction:.6f}' if isinstance(coef_interaction, (int, float)) else 'N/A'}<br>
            <b>P-value:</b> {p_value} {significance}<br>
            <hr style="margin: 4px 0;">
            <i>More negative = speed drops more with rain</i>
        </div>
        """

        folium.CircleMarker(
            location=[lat, lon],
            radius=7,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.85,
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"{road_name} ({highway}): {f'{coef_total:.4f}' if isinstance(coef_total, (int, float)) else 'N/A'}",
        ).add_to(m)

    # Build dynamic legend from actual palette
    palette = PALETTES.get(n_levels, PALETTES[5])
    step = (vmax - vmin) / n_levels if vmax != vmin else 1

    legend_items = ""
    for i, col in enumerate(palette):
        lo = vmin + i * step
        hi = vmin + (i + 1) * step
        if i == 0:
            label = f"Less resilient ({lo:.4f} to {hi:.4f})"
        elif i == len(palette) - 1:
            label = f"More resilient ({lo:.4f} to {vmax:.4f})"
        else:
            label = f"Level {i+1} ({lo:.4f} to {hi:.4f})"
        legend_items += f'<span style="color: {col};">&#9679;</span> {label}<br>'

    legend_html = f"""
    <div style="position: fixed; bottom: 30px; left: 30px; z-index: 1000;
                background: white; padding: 10px; border: 1px solid grey;
                border-radius: 5px; font-size: 11px; max-height: 300px; overflow-y: auto;">
        <b>Precipitation Sensitivity ({n_levels} levels)</b><br>
        {legend_items}
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    return m


def build_link_map(links_geojson, n_levels=5, center_lat=52.25, center_lon=0.1):
    """Build a Folium map with road links drawn as coloured lines with hover highlighting."""
    m = folium.Map(location=[center_lat, center_lon], zoom_start=10,
                   tiles="CartoDB positron")

    features = links_geojson.get("features", [])
    if not features:
        return m

    # Get coefficient range from total_precip field
    coeffs = []
    for f in features:
        props = f.get("properties", {})
        val = props.get("total_precip")
        if val is not None and not (isinstance(val, float) and np.isnan(val)):
            coeffs.append(float(val))

    if not coeffs:
        return m

    vmin, vmax = min(coeffs), max(coeffs)

    # Pre-compute colour for each feature and store as a property
    for feature in features:
        props = feature.get("properties", {})
        coef_total = props.get("total_precip")
        if coef_total is not None and not (isinstance(coef_total, float) and np.isnan(coef_total)):
            color, _ = get_discrete_color(coef_total, vmin, vmax, n_levels)
            props["_color"] = color
            props["_weight"] = 4
        else:
            props["_color"] = "#cccccc"
            props["_weight"] = 2

        # Pre-format display fields for tooltip
        link_desc = props.get("linkdesc", "")
        road_name = props.get("roadname", "N/A")
        props["_display_name"] = link_desc if link_desc else road_name

        if coef_total is not None and not (isinstance(coef_total, float) and np.isnan(coef_total)):
            props["_coef_str"] = f"{coef_total:.6f}"
            props["_coef_short"] = f"{coef_total:.4f}"
        else:
            props["_coef_str"] = "N/A (no sensor match)"
            props["_coef_short"] = "no data"

        coef_match = props.get("coef_match")
        if coef_match is not None and not (isinstance(coef_match, float) and np.isnan(coef_match)):
            props["_interaction_str"] = f"{coef_match:.6f}"
        else:
            props["_interaction_str"] = "N/A"

    # Style function: colour each feature based on its pre-computed colour
    def style_function(feature):
        props = feature.get("properties", {})
        return {
            "color": props.get("_color", "#cccccc"),
            "weight": props.get("_weight", 2),
            "opacity": 0.85,
        }

    # Highlight function: brighten + thicken on hover
    def highlight_function(feature):
        return {
            "color": "#00ffff",
            "weight": 8,
            "opacity": 1.0,
        }

    # Tooltip
    tooltip = folium.GeoJsonTooltip(
        fields=["_display_name", "_coef_short"],
        aliases=["Link:", "Precip. Effect:"],
        sticky=True,
        style="font-size: 12px;",
    )

    # Popup
    popup = folium.GeoJsonPopup(
        fields=["roadname", "linkdesc", "linkref", "_coef_str", "_interaction_str"],
        aliases=["Highway", "Link Description", "Link Ref", "Total Precip. Effect", "Interaction Term"],
        style="font-size: 12px; min-width: 250px;",
    )

    # Add as a single GeoJson layer with hover highlighting
    folium.GeoJson(
        links_geojson,
        style_function=style_function,
        highlight_function=highlight_function,
        tooltip=tooltip,
        popup=popup,
    ).add_to(m)

    # Legend
    palette = PALETTES.get(n_levels, PALETTES[5])
    step = (vmax - vmin) / n_levels if vmax != vmin else 1

    legend_items = ""
    for i, col in enumerate(palette):
        lo = vmin + i * step
        hi = vmin + (i + 1) * step
        if i == 0:
            label = f"Less resilient ({lo:.4f} to {hi:.4f})"
        elif i == len(palette) - 1:
            label = f"More resilient ({lo:.4f} to {vmax:.4f})"
        else:
            label = f"Level {i+1} ({lo:.4f} to {hi:.4f})"
        legend_items += f'<span style="color: {col};">&#9632;</span> {label}<br>'

    legend_items += '<span style="color: #cccccc;">&#9632;</span> No sensor match<br>'
    legend_items += '<span style="color: #00ffff;">&#9632;</span> Hovered link<br>'

    legend_html = f"""
    <div style="position: fixed; bottom: 30px; left: 30px; z-index: 1000;
                background: white; padding: 10px; border: 1px solid grey;
                border-radius: 5px; font-size: 11px; max-height: 300px; overflow-y: auto;">
        <b>Precipitation Sensitivity ({n_levels} levels)</b><br>
        {legend_items}
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    return m


def _render_results_map(df, lat_col, lon_col, coef_col, gis_gdf=None):
    """Render a resilience map from a dataframe with coordinates and coefficients."""
    valid = df.dropna(subset=[lat_col, lon_col, coef_col]).copy()
    if len(valid) == 0:
        st.error("No valid rows with coordinates and coefficients.")
        return

    center_lat = valid[lat_col].mean()
    center_lon = valid[lon_col].mean()
    vmin = valid[coef_col].min()
    vmax = valid[coef_col].max()

    m = folium.Map(location=[center_lat, center_lon], zoom_start=10, tiles="CartoDB positron")

    # If we have GIS geometry (lines/polygons), render those instead of points
    if gis_gdf is not None:
        try:
            for _, row in gis_gdf.iterrows():
                coef_val = row[coef_col]
                if pd.isna(coef_val):
                    continue
                color, _ = get_discrete_color(coef_val, vmin, vmax)
                geom_type = row.geometry.geom_type
                if geom_type in ("LineString", "MultiLineString"):
                    coords = list(row.geometry.coords) if geom_type == "LineString" else \
                             [c for ls in row.geometry.geoms for c in ls.coords]
                    folium.PolyLine(
                        locations=[(c[1], c[0]) for c in coords],
                        color=color, weight=5, opacity=0.8,
                        tooltip=f"{coef_val:.4f}",
                    ).add_to(m)
                elif geom_type in ("Polygon", "MultiPolygon"):
                    folium.GeoJson(
                        row.geometry.__geo_interface__,
                        style_function=lambda x, c=color: {"fillColor": c, "color": c, "weight": 2, "fillOpacity": 0.6},
                        tooltip=f"{coef_val:.4f}",
                    ).add_to(m)
        except Exception:
            pass  # Fall through to point rendering

    # Point rendering (always works, even if line rendering fails)
    for _, row in valid.iterrows():
        coef_val = row[coef_col]
        color, _ = get_discrete_color(coef_val, vmin, vmax)

        popup_parts = []
        for dc in valid.columns:
            if dc not in [lat_col, lon_col, coef_col, "_lat", "_lon", "_centroid", "geometry"]:
                val = row.get(dc)
                if pd.notna(val):
                    popup_parts.append(f"<b>{dc}:</b> {val}")
                if len(popup_parts) >= 6:
                    break

        popup_html = f"""
        <div style="font-family: Arial; font-size: 12px;">
            <b>Coefficient:</b> {coef_val:.6f}<br>
            {'<br>'.join(popup_parts)}
        </div>
        """

        folium.CircleMarker(
            location=[row[lat_col], row[lon_col]],
            radius=7, color=color, fill=True, fill_color=color, fill_opacity=0.8,
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"{coef_val:.4f}",
        ).add_to(m)

    # Legend
    legend_html = """
    <div style="position: fixed; bottom: 30px; left: 30px; z-index: 1000;
                background: white; padding: 10px; border: 1px solid grey;
                border-radius: 5px; font-size: 12px;">
        <b>Precipitation Sensitivity</b><br>
        <span style="color: #00ff00;">&#9679;</span> More resilient<br>
        <span style="color: #ffff00;">&#9679;</span> Moderate<br>
        <span style="color: #ff0000;">&#9679;</span> Less resilient
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))
    st_folium(m, width=900, height=600)

    # Summary stats
    st.subheader("Summary Statistics")
    sc1, sc2, sc3, sc4 = st.columns(4)
    with sc1:
        st.metric("Total Links", len(valid))
    with sc2:
        st.metric("Mean Coefficient", f"{valid[coef_col].mean():.6f}")
    with sc3:
        st.metric("Most Vulnerable", f"{valid[coef_col].min():.6f}")
    with sc4:
        st.metric("Most Resilient", f"{valid[coef_col].max():.6f}")

    # Group stats if highway column exists
    hw_col = _auto_match(valid.columns, ["highway", "road_class", "road_type", "corridor"])
    if hw_col:
        st.subheader(f"By {hw_col}")
        hw_stats = valid.groupby(hw_col)[coef_col].agg(["mean", "count", "min", "max"]).round(6)
        hw_stats.columns = ["Mean", "N Links", "Min", "Max"]
        st.dataframe(hw_stats, **_USE_WIDTH)


# ---- Page: Interactive Resilience Map ----
if page == "Interactive Resilience Map":
    st.title("Interactive Road Climate Resilience Map")
    st.markdown("""
    This map shows the **precipitation sensitivity** of each road link on the Strategic Road Network (SRN),
    estimated from a Gamma GLM on **weekday** travel speed data (2022–2024).
    Hover over a point to see its resilience score; click for details.

    - **Green** = more resilient (smaller speed reduction when it rains)
    - **Red** = less resilient (larger speed reduction when it rains)

    *Note: The model uses weekday data only. Weekend traffic patterns differ substantially
    and are excluded to avoid confounding the climate sensitivity estimates.*
    """)

    data = load_example_data()

    if data.get("source") == "user":
        st.success("Showing results from your latest GLM analysis. Run a new analysis in **Run Your Own Analysis** to update.")
    else:
        st.info("Showing Cambridgeshire example data. Run your own analysis in **Run Your Own Analysis** to see your results here.")

    if "geojson" in data:
        # Controls row
        ctrl1, ctrl2, ctrl3 = st.columns([1, 1, 2])
        with ctrl1:
            n_levels = st.slider("Colour levels", min_value=2, max_value=10, value=5,
                                 help="Number of discrete colour categories for the legend")
        with ctrl2:
            has_links = "links_geojson" in data
            display_options = ["Points (sensor locations)", "Links (road geometry)"] if has_links else ["Points (sensor locations)"]
            display_mode = st.radio("Display mode", display_options,
                                    help="Points shows sensor locations. Links draws the actual road segments colour-coded by resilience.")

        col1, col2 = st.columns([3, 1])

        with col1:
            if display_mode.startswith("Links") and "links_geojson" in data:
                m = build_link_map(data["links_geojson"], n_levels=n_levels)
            else:
                m = build_resilience_map(data["geojson"], n_levels=n_levels)
            st_folium(m, width=900, height=600)

        with col2:
            st.subheader("Filter by Highway")
            if "coefficients" in data:
                df = data["coefficients"]
                highways = sorted(df["highway"].dropna().unique())
                selected = st.multiselect("Select highways:", highways, default=highways)

                # Summary stats for selection
                if selected:
                    filtered = df[df["highway"].isin(selected)]
                    coef_col = "coefficient" if "coefficient" in filtered.columns else "precipitat"
                    st.metric("Links shown", len(filtered))
                    st.metric("Mean sensitivity", f"{filtered[coef_col].mean():.6f}")
                    st.metric("Most vulnerable", f"{filtered[coef_col].min():.6f}")
                    st.metric("Most resilient", f"{filtered[coef_col].max():.6f}")
    else:
        st.warning("No example data found. Please ensure data/example/ contains linkgis.geojson.")


# ---- Page: Summary Dashboard ----
elif page == "Summary Dashboard":
    st.title("Summary Dashboard")

    data = load_example_data()

    if data.get("source") == "user":
        st.success("Showing results from your latest GLM analysis.")
    else:
        st.info("Showing Cambridgeshire example data. Run your own analysis to see your results here.")

    if "coefficients" in data:
        df = data["coefficients"]
        coef_col = "coefficient" if "coefficient" in df.columns else "precipitat"

        tab1, tab2, tab3 = st.tabs(["By Highway", "Road Features", "GLM Results"])

        with tab1:
            st.subheader("Precipitation Sensitivity by Highway")
            highway_stats = df.groupby("highway")[coef_col].agg(["mean", "std", "count", "min", "max"])
            highway_stats = highway_stats.sort_values("mean")
            highway_stats.columns = ["Mean Coef.", "Std Dev", "N Links", "Min", "Max"]

            fig = px.bar(
                highway_stats.reset_index(),
                x="highway", y="Mean Coef.",
                error_y="Std Dev",
                color="Mean Coef.",
                color_continuous_scale="RdYlGn",
                title="Mean Precipitation Sensitivity by Highway",
                labels={"Mean Coef.": "Mean Precipitation Coefficient", "highway": "Highway"},
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, **_USE_WIDTH)

            st.dataframe(highway_stats.round(6), **_USE_WIDTH)

        with tab2:
            st.subheader("Road Features vs Climate Sensitivity")
            if "features" in data:
                feat_df = data["features"]
                st.dataframe(feat_df.round(4), **_USE_WIDTH)

            # Show feature regression if coefficient data has features
            feature_cols = ["Number of lanes", "Speed limit (mph)", "Average daily flow", "Length (m)"]
            available_feats = [c for c in feature_cols if c in df.columns]

            if available_feats:
                feat_choice = st.selectbox("Scatter: Coefficient vs Feature", available_feats)
                fig2 = px.scatter(
                    df, x=feat_choice, y=coef_col,
                    color="highway",
                    title=f"Precipitation Sensitivity vs {feat_choice}",
                    trendline="ols",
                    labels={coef_col: "Precipitation Coefficient"},
                )
                fig2.update_layout(height=400)
                st.plotly_chart(fig2, **_USE_WIDTH)

        with tab3:
            if "glm_results" in data:
                glm_df = data["glm_results"].copy()
                has_full_stats = glm_df["std_err"].notna().any()
                has_pvalues = glm_df["p_value"].notna().any()

                # ---- Model Summary Panel (Stata-style) ----
                st.subheader("Model Summary")
                model_info = data.get("model_summary", {})

                # Format values (handle None gracefully)
                def _fmt(val, fmt=".4f"):
                    if val is None:
                        return "."
                    if isinstance(val, int):
                        return f"{val:,}"
                    if isinstance(val, float):
                        return f"{val:{fmt}}"
                    return str(val)

                n_obs = model_info.get("n_obs")
                n_clusters = model_info.get("n_clusters")
                n_params = model_info.get("n_parameters")
                deviance = model_info.get("deviance")
                pearson = model_info.get("pearson_chi2")
                aic_val = model_info.get("aic")
                bic_val = model_info.get("bic")
                ll_val = model_info.get("log_likelihood")
                dev_df = model_info.get("deviance_per_df")
                pear_df = model_info.get("pearson_per_df")
                df_model = model_info.get("df_model")
                df_resid = model_info.get("df_residual")

                # Build Stata-style monospace block
                stata_header = (
                    f"Generalized linear models                No. of obs      = {_fmt(n_obs):>12}\n"
                    f"Optimization     : ML                    No. of clusters = {_fmt(n_clusters):>12}\n"
                    f"                                         Residual df     = {_fmt(df_resid):>12}\n"
                    f"Deviance         = {_fmt(deviance):>14}       (1/df) Deviance = {_fmt(dev_df, '.6f'):>12}\n"
                    f"Pearson          = {_fmt(pearson):>14}       (1/df) Pearson  = {_fmt(pear_df, '.6f'):>12}\n"
                    f"\n"
                    f"Variance function: V(u) = u^2            [Gamma]\n"
                    f"Link function    : g(u) = ln(u)          [Log]\n"
                    f"\n"
                    f"Log pseudolikelihood = {_fmt(ll_val):>14}    AIC             = {_fmt(aic_val):>12}\n"
                    f"                                         BIC             = {_fmt(bic_val):>12}\n"
                    f"\n"
                    f"                                         (Std. err. adjusted for {_fmt(n_clusters)} clusters)"
                )
                st.code(stata_header, language=None)

                if n_obs is None:
                    st.info(
                        "Model fit statistics are placeholders. Run `scripts/export_stata_results.do` "
                        "in Stata, or use **Run Your Own Analysis** to populate them."
                    )

                # If we have a text summary, show it in an expander
                if "model_summary_text" in data:
                    with st.expander("Full model output"):
                        st.code(data["model_summary_text"], language=None)

                st.divider()

                # ---- Coefficient Table ----
                st.subheader("Coefficient Table")

                if not has_full_stats:
                    st.info(
                        "The example coefficients are from Stata (without SEs). "
                        "Run `scripts/export_stata_results.do` in Stata to export full statistics, "
                        "or use **Run Your Own Analysis** to generate them in Python."
                    )

                # Filter controls
                filter_type = st.selectbox(
                    "Show coefficients for:",
                    ["All", "Weather variables", "Time controls", "Link FEs", "Interactions"]
                )

                if filter_type == "Weather variables":
                    mask = glm_df["feature"].isin([
                        "precipitation_t", "temperature_t", "temp_below0_past6h"
                    ])
                elif filter_type == "Time controls":
                    mask = glm_df["feature"].str.contains(
                        "hour_|month_|year_|dow_|school|uni|bank|event|roadworks|accident"
                    )
                elif filter_type == "Link FEs":
                    mask = (
                        glm_df["feature"].str.startswith("link_")
                        & ~glm_df["feature"].str.contains("_precip|_x_precip")
                    )
                elif filter_type == "Interactions":
                    mask = glm_df["feature"].str.contains("_precip|_x_precip")
                else:
                    mask = pd.Series(True, index=glm_df.index)

                display_df = glm_df[mask].copy()

                # Build display table
                if has_full_stats or has_pvalues:
                    display_df["sig"] = display_df["p_value"].apply(
                        lambda p: "***" if pd.notna(p) and p < 0.001
                        else "**" if pd.notna(p) and p < 0.01
                        else "*" if pd.notna(p) and p < 0.05
                        else "+" if pd.notna(p) and p < 0.1
                        else ""
                    )
                    # Show available columns
                    show_cols = ["feature", "coefficient"]
                    if has_full_stats:
                        show_cols += ["std_err", "z_value"]
                    show_cols.append("p_value")
                    if has_full_stats:
                        show_cols += ["conf_int_lower", "conf_int_upper"]
                    show_cols.append("sig")
                    show_cols = [c for c in show_cols if c in display_df.columns]
                    styled = display_df[show_cols].round(6)
                    # Convert all columns to string to avoid Arrow mixed-type error
                    for col in styled.columns:
                        styled[col] = styled[col].astype(str).replace("nan", "-")
                    rename_map = {
                        "feature": "Variable", "coefficient": "Coef.",
                        "std_err": "Std. Err.", "z_value": "z",
                        "p_value": "P>|z|", "conf_int_lower": "[95% CI Low",
                        "conf_int_upper": "95% CI High]", "sig": "",
                    }
                    styled = styled.rename(columns={k: v for k, v in rename_map.items() if k in styled.columns})
                else:
                    styled = display_df[["feature", "coefficient"]].copy()
                    styled = styled.rename(columns={
                        "feature": "Variable", "coefficient": "Coef.",
                    })
                    styled["Coef."] = styled["Coef."].round(6)

                st.dataframe(styled, **_USE_WIDTH, height=400, hide_index=True)

                # Footer stats
                n_features = len(display_df)
                st.caption(f"Showing {n_features} coefficients ({filter_type})")
                if has_full_stats:
                    sig_counts = display_df["p_value"].apply(
                        lambda p: p < 0.05 if pd.notna(p) else False
                    ).sum()
                    st.caption(
                        f"Significant at 5%: {sig_counts}/{n_features}  |  "
                        f"Significance codes: *** p<0.001, ** p<0.01, * p<0.05, + p<0.1"
                    )
            else:
                st.info("GLM results file not found in data/example/.")

    else:
        st.warning("No coefficient data found.")


# ---- Page: Run Your Own Analysis ----
elif page == "Run Your Own Analysis":
    st.title("Run Your Own Analysis")

    upload_tab1, upload_tab2 = st.tabs([
        "Upload Raw Data (for GLM estimation)",
        "Upload Results (visualise on map)"
    ])

    # ---- Tab 1: Upload raw data for analysis ----
    with upload_tab1:
        st.markdown("""
        Upload your merged traffic + weather data to run the full resilience analysis pipeline.
        Supports **CSV**, **Excel (.xlsx)**, and **Parquet** formats.

        **Important**: The model estimates on **weekday data only** (Monday–Friday).
        Weekend observations will be automatically excluded during analysis.

        ### Required Data Fields

        Your data needs these **6 types of information** — column names are flexible
        (you can map them after upload):

        | Field | What it is | Example column names |
        |-------|-----------|---------------------|
        | **Datetime** | When was this observation? | `time`, `datetime`, `Report Date`, `timestamp` |
        | **Speed** | Average travel speed | `Avg mph`, `speed`, `avg_speed`, `mean_speed` |
        | **Volume** | Vehicle count | `Total Volume`, `volume`, `flow`, `traffic_count` |
        | **Link ID** | Road link identifier | `link name`, `link_id`, `road_id`, `sensor_id` |
        | **Temperature** | Air temperature (°C) | `air_temperature`, `temperature`, `temp` |
        | **Precipitation** | Rainfall amount (mm) | `prcp_amt`, `precipitation`, `rainfall` |

        **Optional** (improves model accuracy if available):
        - Accident/incident indicator (binary 0/1)
        - Maintenance/roadworks indicator (binary 0/1)
        - Other disruption variables (any binary columns)
        """)

        st.divider()

        input_method = st.radio(
            "How would you like to provide your data?",
            ["Enter file path (recommended for large files)", "Upload file (small files only, <200MB)"],
            horizontal=True,
        )

        upload_path = None

        # ---- File path history (remember last 10 files) ----
        _HISTORY_FILE = os.path.join(UPLOAD_DIR, "file_history.json")

        def _load_history():
            if os.path.exists(_HISTORY_FILE):
                try:
                    with open(_HISTORY_FILE) as f:
                        return json.load(f)
                except Exception:
                    pass
            return []

        def _save_history(path):
            history = _load_history()
            # Remove if already exists (will re-add at top)
            history = [h for h in history if h != path]
            history.insert(0, path)
            history = history[:10]  # Keep last 10
            os.makedirs(os.path.dirname(_HISTORY_FILE), exist_ok=True)
            with open(_HISTORY_FILE, "w") as f:
                json.dump(history, f)

        if input_method == "Enter file path (recommended for large files)":
            file_history = _load_history()

            if file_history:
                # Show history as selectbox + option to enter new path
                history_options = ["Enter a new path..."] + file_history
                selected = st.selectbox(
                    "Select a previously used file or enter a new path:",
                    history_options,
                    help="Your last 10 data files are remembered here.",
                    key="file_history_select",
                )
                if selected == "Enter a new path...":
                    raw_file_path = st.text_input(
                        "Full path to your data file (CSV, Excel, or Parquet)",
                        placeholder="/Users/you/data/merged_traffic_weather.csv",
                        key="new_path_input",
                    )
                else:
                    raw_file_path = selected
            else:
                raw_file_path = st.text_input(
                    "Full path to your data file (CSV, Excel, or Parquet)",
                    placeholder="/Users/you/data/merged_traffic_weather.csv",
                    help="Supports .csv, .xlsx, .parquet formats. "
                         "This avoids the slow upload process for large files (>1GB).",
                )

            if raw_file_path and os.path.exists(raw_file_path):
                file_size_mb = os.path.getsize(raw_file_path) / (1024**2)
                st.success(f"File found: `{os.path.basename(raw_file_path)}` ({file_size_mb:.1f} MB)")
                upload_path = raw_file_path
                _save_history(raw_file_path)  # Remember this path
            elif raw_file_path:
                st.error(f"File not found: `{raw_file_path}`")
        else:
            raw_file = st.file_uploader(
                "Upload your merged traffic + weather data",
                type=["csv", "xlsx", "parquet"],
                help="For files under 200MB. For larger files, use the file path option.",
                key="raw_upload",
            )
            if raw_file is not None:
                upload_path = os.path.join(UPLOAD_DIR, raw_file.name)
                with open(upload_path, "wb") as f:
                    f.write(raw_file.getbuffer())
                st.success(f"File saved: `uploads/{raw_file.name}`")

        # Helper: read file based on extension
        def _read_preview(path, nrows=100):
            ext = os.path.splitext(path)[1].lower()
            if ext == ".parquet":
                return pd.read_parquet(path).head(nrows)
            elif ext in (".xlsx", ".xls"):
                return pd.read_excel(path, nrows=nrows)
            else:
                return pd.read_csv(path, nrows=nrows, low_memory=False)

        # Helper: auto-detect best matching column
        def _auto_match(columns, keywords, exclude=None):
            """Find the best matching column name from a list of keywords."""
            cols_lower = {c.lower().replace(" ", "_").replace("-", "_"): c for c in columns}
            for kw in keywords:
                kw_norm = kw.lower().replace(" ", "_").replace("-", "_")
                # Exact match (case-insensitive)
                if kw_norm in cols_lower:
                    match = cols_lower[kw_norm]
                    if exclude and match in exclude:
                        continue
                    return match
                # Substring match
                for cn, orig in cols_lower.items():
                    if kw_norm in cn and (not exclude or orig not in exclude):
                        return orig
            return None

        if upload_path is not None:

            try:
                preview_df = _read_preview(upload_path)
                st.subheader("Data Preview")
                st.dataframe(preview_df.head(20), **_USE_WIDTH)

                st.subheader("Data Summary")
                col1, col2, col3 = st.columns(3)
                ext = os.path.splitext(upload_path)[1].lower()
                if ext == ".csv":
                    total_rows_estimate = sum(1 for _ in open(upload_path)) - 1
                else:
                    total_rows_estimate = len(preview_df)  # approximate for non-CSV
                with col1:
                    st.metric("Columns", len(preview_df.columns))
                with col2:
                    st.metric("Estimated Rows", f"{total_rows_estimate:,}")
                with col3:
                    link_guess = _auto_match(preview_df.columns,
                        ["link name", "link_name", "linkname", "link_id", "road_id", "sensor_id", "site_id", "Road Name", "Name"])
                    links = preview_df[link_guess].nunique() if link_guess else "?"
                    st.metric("Unique Links (sample)", links)

                # ---- Column Mapping UI ----
                st.divider()
                st.subheader("Column Mapping")
                st.markdown("Map your data columns to the required fields. "
                            "Auto-detection is attempted — **verify and correct** if needed.")

                all_cols = ["(not available)"] + list(preview_df.columns)

                # Define required fields with auto-detect keywords
                field_defs = {
                    "datetime": {
                        "label": "Datetime",
                        "keywords": ["time", "datetime", "Report Date", "timestamp", "date_time", "date"],
                        "required": True,
                        "help": "Column with date/time of each observation",
                    },
                    "speed": {
                        "label": "Speed (mph or km/h)",
                        "keywords": ["Avg mph", "avg_mph", "speed", "avgmph", "mean_speed", "avg_speed"],
                        "required": True,
                        "help": "Average travel speed for the road link",
                    },
                    "volume": {
                        "label": "Traffic volume",
                        "keywords": ["Total Volume", "total_volume", "volume", "flow", "traffic_count", "count", "AADT"],
                        "required": False,
                        "help": "Vehicle count (optional but recommended)",
                    },
                    "link_id": {
                        "label": "Road link identifier",
                        "keywords": ["link name", "link_name", "linkname", "link_id", "road_id", "sensor_id", "site_id", "Site Name"],
                        "required": True,
                        "help": "Unique identifier for each road segment/sensor",
                    },
                    "temperature": {
                        "label": "Temperature (°C)",
                        "keywords": ["air_temperature", "temperature", "temp", "Temperature_t"],
                        "required": True,
                        "help": "Air temperature in Celsius",
                    },
                    "precipitation": {
                        "label": "Precipitation (mm)",
                        "keywords": ["prcp_amt", "precipitation", "rainfall", "precip", "rain", "Precipitation_t"],
                        "required": True,
                        "help": "Rainfall amount in mm",
                    },
                    "accident": {
                        "label": "Accident indicator (0/1)",
                        "keywords": ["Accident", "accident", "Accident_t", "incident"],
                        "required": False,
                        "help": "Binary: 1 = accident occurred, 0 = no accident",
                    },
                    "maintenance": {
                        "label": "Maintenance/roadworks (0/1)",
                        "keywords": ["MaintenanceWorks", "maintenance", "Roadworks_t", "roadworks"],
                        "required": False,
                        "help": "Binary: 1 = roadworks, 0 = none",
                    },
                }

                # Auto-detect and let user override
                used_cols = set()
                col_mapping = {}
                map_cols = st.columns(2)

                for i, (field_key, fdef) in enumerate(field_defs.items()):
                    auto = _auto_match(preview_df.columns, fdef["keywords"], exclude=used_cols)
                    default_idx = all_cols.index(auto) if auto and auto in all_cols else 0
                    req_mark = " *" if fdef["required"] else ""

                    with map_cols[i % 2]:
                        chosen = st.selectbox(
                            f"{fdef['label']}{req_mark}",
                            all_cols,
                            index=default_idx,
                            help=fdef["help"],
                            key=f"map_{field_key}",
                        )

                    if chosen != "(not available)":
                        col_mapping[field_key] = chosen
                        used_cols.add(chosen)

                # Validate required fields
                missing_required = [
                    fdef["label"] for fk, fdef in field_defs.items()
                    if fdef["required"] and fk not in col_mapping
                ]

                if missing_required:
                    st.error(f"Please map these required fields: **{', '.join(missing_required)}**")
                else:
                    st.success("All required fields mapped!")

                    # Show final mapping summary
                    with st.expander("Column mapping summary"):
                        for fk, col_name in col_mapping.items():
                            st.write(f"  {field_defs[fk]['label']}  →  `{col_name}`")

                    # ---- Custom additional columns ----
                    with st.expander("Add extra variables (optional)"):
                        st.markdown("""
                        Add additional columns from your data as extra control variables in the regression.

                        **Notes:**
                        - Each added column will be included as an **additional regressor** in the GLM.
                        - The column should be **numeric** (continuous or binary 0/1).
                        - If your variable has a **non-linear** relationship with speed, please transform
                          it before uploading (e.g., log, squared, binned) — the GLM assumes a linear
                          relationship on the log-link scale.
                        - Categorical variables should be converted to dummies before uploading.
                        """)

                        available_extra = [c for c in preview_df.columns if c not in col_mapping.values()]
                        extra_cols = st.multiselect(
                            "Select additional columns to include as regressors:",
                            available_extra,
                            help="These will be added as control variables alongside the default ones.",
                            key="extra_cols",
                        )
                        if extra_cols:
                            st.caption(f"Selected {len(extra_cols)} extra variable(s): {', '.join(extra_cols)}")

                    st.divider()
                    st.subheader("Analysis Configuration")

                    sample_pct = st.slider(
                        "Sample percentage (use lower for testing, 100% for final)",
                        min_value=5, max_value=100, value=20, step=5,
                    )

                    speed_col = col_mapping.get("speed", "Avg mph")
                    link_col = col_mapping.get("link_id", "link name")

                    # Memory estimation
                    try:
                        import psutil
                        available_ram_gb = psutil.virtual_memory().available / (1024**3)
                        file_size_gb = os.path.getsize(upload_path) / (1024**3)
                        if file_size_gb > available_ram_gb * 0.7:
                            st.warning(
                                f"Large file ({file_size_gb:.1f} GB) with {available_ram_gb:.1f} GB RAM available. "
                                f"Consider reducing the sample percentage if you encounter memory issues."
                            )
                    except ImportError:
                        pass

                    if st.button("Run Resilience Analysis", type="primary"):
                        import subprocess

                        repo_dir = os.path.dirname(__file__)

                        def run_with_progress(cmd, status_label, timeout=3600):
                            """Run subprocess and parse PROGRESS: lines for the progress bar."""
                            progress_bar = st.progress(0, text=status_label)
                            log_expander = st.expander("Logs", expanded=False)
                            log_lines = []

                            proc = subprocess.Popen(
                                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True, bufsize=1
                            )
                            import time as _time
                            start = _time.time()

                            for line in proc.stdout:
                                line = line.strip()
                                if line.startswith("PROGRESS:"):
                                    parts = line.split(":", 2)
                                    if len(parts) >= 3:
                                        pct = int(parts[1])
                                        msg = parts[2]
                                        elapsed = int(_time.time() - start)
                                        progress_bar.progress(
                                            pct / 100,
                                            text=f"{msg} ({elapsed}s elapsed)"
                                        )
                                else:
                                    log_lines.append(line)

                            proc.wait(timeout=timeout)
                            stderr = proc.stderr.read()

                            with log_expander:
                                st.code("\n".join(log_lines[-30:]))  # Show last 30 lines

                            if proc.returncode != 0:
                                st.error(f"Process failed:\n{stderr}")
                                st.stop()

                            progress_bar.progress(1.0, text="Done!")
                            return proc.returncode

                        # Step 1: Data preparation
                        # Convert file to CSV if needed (Excel/Parquet)
                        if ext in (".xlsx", ".xls", ".parquet"):
                            st.info(f"Converting {ext} to CSV for processing...")
                            tmp_csv = os.path.join(UPLOAD_DIR, "converted_input.csv")
                            if ext == ".parquet":
                                pd.read_parquet(upload_path).to_csv(tmp_csv, index=False)
                            else:
                                pd.read_excel(upload_path).to_csv(tmp_csv, index=False)
                            upload_path_csv = tmp_csv
                        else:
                            upload_path_csv = upload_path

                        prep_output = os.path.join(UPLOAD_DIR, "prepared_data.csv")

                        # Build rename mapping for data_preparation script
                        rename_args = []
                        # Map user's column names to what the script expects
                        time_col = col_mapping.get("datetime", "time")
                        temp_col = col_mapping.get("temperature", "air_temperature")
                        precip_col = col_mapping.get("precipitation", "prcp_amt")
                        vol_col = col_mapping.get("volume", "Total Volume")
                        accident_col = col_mapping.get("accident", "")
                        maint_col = col_mapping.get("maintenance", "")

                        cmd1 = [
                            sys.executable, os.path.join(repo_dir, "scripts", "01_data_preparation.py"),
                            "--input", upload_path_csv,
                            "--output", prep_output,
                            "--speed-col", speed_col,
                            "--link-col", link_col,
                            "--time-col", time_col,
                            "--temp-col", temp_col,
                            "--precip-col", precip_col,
                            "--volume-col", vol_col,
                            "--sample", str(sample_pct / 100),
                        ]
                        run_with_progress(cmd1, "Step 1/2: Preparing data...", timeout=600)

                        # Step 2: GLM estimation
                        results_dir = os.path.join(UPLOAD_DIR, "results")
                        cmd2 = [
                            sys.executable, os.path.join(repo_dir, "scripts", "02_glm_estimation.py"),
                            "--input", prep_output,
                            "--output-dir", results_dir,
                        ]
                        run_with_progress(cmd2, "Step 2/2: Running Gamma GLM...", timeout=7200)

                        st.success("Analysis complete!")
                        st.balloons()

                        # Show results
                        results_file = os.path.join(results_dir, "precipitation_interaction_results.csv")
                        if os.path.exists(results_file):
                            result_df = pd.read_csv(results_file)
                            st.subheader("Precipitation Interaction Results")
                            st.dataframe(result_df.round(6), **_USE_WIDTH)

                            # Download buttons
                            st.divider()
                            dl_col1, dl_col2, dl_col3 = st.columns(3)
                            with dl_col1:
                                st.download_button(
                                    "Download Interaction Results",
                                    result_df.to_csv(index=False),
                                    "precipitation_interactions.csv",
                                    "text/csv",
                                )
                            full_results_path = os.path.join(results_dir, "gamma_glm_full_results.csv")
                            if os.path.exists(full_results_path):
                                with dl_col2:
                                    st.download_button(
                                        "Download Full GLM Results",
                                        open(full_results_path).read(),
                                        "gamma_glm_full_results.csv",
                                        "text/csv",
                                    )
                            summary_path = os.path.join(results_dir, "gamma_glm_summary.txt")
                            if os.path.exists(summary_path):
                                with dl_col3:
                                    st.download_button(
                                        "Download Model Summary",
                                        open(summary_path).read(),
                                        "gamma_glm_summary.txt",
                                        "text/plain",
                                    )

                            st.info("To visualise these on a map, go to the **Upload Results** tab and upload a CSV with latitude/longitude columns.")

            except Exception as e:
                st.error(f"Error reading file: {e}")

        # ---- Always show previous results if they exist on disk ----
        prev_results_file = os.path.join(USER_RESULTS_DIR, "precipitation_interaction_results.csv")
        prev_full_file = os.path.join(USER_RESULTS_DIR, "gamma_glm_full_results.csv")
        prev_summary_file = os.path.join(USER_RESULTS_DIR, "gamma_glm_summary.txt")
        prev_model_json = os.path.join(USER_RESULTS_DIR, "model_summary.json")

        if os.path.exists(prev_results_file):
            st.divider()
            st.subheader("Previous Analysis Results")
            import datetime as _dt
            mod_time = os.path.getmtime(prev_results_file)
            mod_str = _dt.datetime.fromtimestamp(mod_time).strftime("%Y-%m-%d %H:%M")
            st.caption(f"Last run: {mod_str}")

            prev_df = pd.read_csv(prev_results_file)
            st.dataframe(prev_df.round(6), **_USE_WIDTH)

            # Download buttons (always available)
            dl_c1, dl_c2, dl_c3 = st.columns(3)
            with dl_c1:
                st.download_button(
                    "Download Interaction Results",
                    prev_df.to_csv(index=False),
                    "precipitation_interactions.csv", "text/csv",
                    key="dl_prev_interactions",
                )
            if os.path.exists(prev_full_file):
                with dl_c2:
                    st.download_button(
                        "Download Full GLM Results",
                        open(prev_full_file).read(),
                        "gamma_glm_full_results.csv", "text/csv",
                        key="dl_prev_full",
                    )
            if os.path.exists(prev_summary_file):
                with dl_c3:
                    st.download_button(
                        "Download Model Summary",
                        open(prev_summary_file).read(),
                        "gamma_glm_summary.txt", "text/plain",
                        key="dl_prev_summary",
                    )

            st.info("These results are also shown in **Interactive Resilience Map** and **Summary Dashboard**. "
                    "Upload new data above to run a fresh analysis.")
        elif upload_path is None:
            st.info("Upload a data file to get started, or explore the Cambridgeshire example using the Map and Dashboard pages.")

    # ---- Tab 2: Upload results + GIS to visualise on map ----
    with upload_tab2:
        st.markdown("""
        Visualise your resilience results on an interactive map. Two options:

        **Option A**: Upload a results file that already has coordinates (latitude/longitude).

        **Option B**: Upload results + a separate GIS layer (Shapefile/GeoJSON), then match
        them by a shared identifier (e.g., link ID, road name).
        """)

        st.divider()

        vis_mode = st.radio(
            "How would you like to provide spatial data?",
            [
                "My results already have lat/lon coordinates",
                "I have a separate GIS layer (SHP/GeoJSON) to match with results",
            ],
            horizontal=True, key="vis_mode",
        )

        # ---- Step 1: Upload results ----
        st.subheader("Step 1: Upload Results")
        results_file = st.file_uploader(
            "Upload your resilience results",
            type=["csv", "xlsx", "parquet"],
            help="CSV/Excel/Parquet with coefficient values per road link.",
            key="results_upload",
        )

        result_df = None
        if results_file is not None:
            try:
                ext_r = os.path.splitext(results_file.name)[1].lower()
                if ext_r == ".parquet":
                    result_df = pd.read_parquet(results_file)
                elif ext_r in (".xlsx", ".xls"):
                    result_df = pd.read_excel(results_file)
                else:
                    result_df = pd.read_csv(results_file)
                st.success(f"Loaded {len(result_df)} rows, {len(result_df.columns)} columns")
                st.dataframe(result_df.head(5), **_USE_WIDTH)
            except Exception as e:
                st.error(f"Error reading results file: {e}")

        # Also allow loading from GLM run output
        glm_results_path = os.path.join(UPLOAD_DIR, "results", "precipitation_interaction_results.csv")
        if result_df is None and os.path.exists(glm_results_path):
            if st.button("Use results from last GLM run"):
                result_df = pd.read_csv(glm_results_path)
                st.success(f"Loaded {len(result_df)} links from last run")
                st.dataframe(result_df.head(5), **_USE_WIDTH)

        if result_df is not None:
            # ---- Select coefficient column ----
            all_result_cols = list(result_df.columns)
            coef_guess = _auto_match(all_result_cols,
                ["total_precipitation_effect", "precipitation_interaction_coefficient",
                 "coefficient", "coef", "sensitivity", "precip_coef"])
            coef_idx = all_result_cols.index(coef_guess) if coef_guess else 0
            coef_col = st.selectbox("Coefficient column (the value to visualise):",
                                     all_result_cols, index=coef_idx, key="coef_col")

            # ---- Option A: Results already have coordinates ----
            if vis_mode == "My results already have lat/lon coordinates":
                lat_guess = _auto_match(all_result_cols, ["latitude", "lat", "Latitude", "y"])
                lon_guess = _auto_match(all_result_cols, ["longitude", "lon", "Longitude", "lng", "x"])
                lat_idx = all_result_cols.index(lat_guess) if lat_guess else 0
                lon_idx = all_result_cols.index(lon_guess) if lon_guess else 0

                lc1, lc2 = st.columns(2)
                with lc1:
                    lat_col = st.selectbox("Latitude column:", all_result_cols, index=lat_idx, key="lat_col")
                with lc2:
                    lon_col = st.selectbox("Longitude column:", all_result_cols, index=lon_idx, key="lon_col")

                valid = result_df.dropna(subset=[lat_col, lon_col, coef_col]).copy()
                if len(valid) == 0:
                    st.error("No valid rows with coordinates and coefficients.")
                else:
                    _render_results_map(valid, lat_col, lon_col, coef_col)

            # ---- Option B: Separate GIS layer ----
            else:
                st.subheader("Step 2: Upload GIS Layer")
                st.markdown("""
                Upload your road network geometry. Supported formats:
                - **GeoJSON** (.geojson)
                - **Shapefile** (.shp — upload the .shp file; .dbf, .shx, .prj must be in the same folder)
                - **GeoPackage** (.gpkg)

                The GIS layer must have a field that matches your results (e.g., link ID, road name).
                """)

                gis_input_method = st.radio(
                    "How to provide GIS data?",
                    ["Upload file", "Enter file path"],
                    horizontal=True, key="gis_input",
                )

                gis_gdf = None

                if gis_input_method == "Enter file path":
                    gis_path = st.text_input(
                        "Path to your GIS file (.geojson, .shp, .gpkg)",
                        placeholder="/Users/you/data/road_network.geojson",
                        key="gis_path_input",
                    )
                    if gis_path and os.path.exists(gis_path):
                        try:
                            import geopandas as gpd
                            gis_gdf = gpd.read_file(gis_path)
                            st.success(f"Loaded {len(gis_gdf)} features from `{os.path.basename(gis_path)}`")
                        except ImportError:
                            st.error("Please install geopandas: `pip install geopandas`")
                        except Exception as e:
                            st.error(f"Error reading GIS file: {e}")
                else:
                    gis_file = st.file_uploader(
                        "Upload GIS file",
                        type=["geojson", "gpkg", "shp"],
                        key="gis_upload",
                    )
                    if gis_file is not None:
                        try:
                            import geopandas as gpd
                            gis_save_path = os.path.join(UPLOAD_DIR, gis_file.name)
                            with open(gis_save_path, "wb") as f:
                                f.write(gis_file.getbuffer())
                            gis_gdf = gpd.read_file(gis_save_path)
                            st.success(f"Loaded {len(gis_gdf)} features")
                        except ImportError:
                            st.error("Please install geopandas: `pip install geopandas`")
                        except Exception as e:
                            st.error(f"Error reading GIS file: {e}")

                if gis_gdf is not None:
                    st.subheader("Step 3: Match Fields")
                    st.markdown("Select which field in your **GIS layer** matches which field in your **results**.")

                    gc1, gc2 = st.columns(2)
                    gis_cols = [c for c in gis_gdf.columns if c != "geometry"]
                    with gc1:
                        gis_match_col = st.selectbox(
                            "GIS layer: match field",
                            gis_cols,
                            help="The field in your GIS layer that identifies each road link",
                            key="gis_match",
                        )
                        st.caption(f"Sample values: {list(gis_gdf[gis_match_col].head(5))}")
                    with gc2:
                        result_match_guess = _auto_match(all_result_cols,
                            ["link_name", "link_id", "linkname", "road_id", "sensor_id", gis_match_col])
                        r_idx = all_result_cols.index(result_match_guess) if result_match_guess else 0
                        result_match_col = st.selectbox(
                            "Results: match field",
                            all_result_cols,
                            index=r_idx,
                            help="The field in your results that matches the GIS layer",
                            key="result_match",
                        )
                        st.caption(f"Sample values: {list(result_df[result_match_col].head(5))}")

                    # Show match preview
                    gis_keys = set(gis_gdf[gis_match_col].astype(str).unique())
                    result_keys = set(result_df[result_match_col].astype(str).unique())
                    matched = gis_keys & result_keys
                    mc1, mc2, mc3 = st.columns(3)
                    with mc1:
                        st.metric("GIS features", len(gis_keys))
                    with mc2:
                        st.metric("Result links", len(result_keys))
                    with mc3:
                        match_pct = len(matched) / max(len(result_keys), 1) * 100
                        st.metric("Matched", f"{len(matched)} ({match_pct:.0f}%)")

                    if len(matched) == 0:
                        st.error("No matches found! Check that the match fields contain the same identifiers.")
                        st.write("GIS sample:", sorted(list(gis_keys))[:10])
                        st.write("Results sample:", sorted(list(result_keys))[:10])
                    else:
                        if match_pct < 50:
                            st.warning(f"Only {match_pct:.0f}% of results matched. Check field selection.")

                        if st.button("Generate Map", type="primary", key="gen_map"):
                            # Merge GIS geometry with results
                            gis_gdf[gis_match_col] = gis_gdf[gis_match_col].astype(str)
                            result_df[result_match_col] = result_df[result_match_col].astype(str)

                            merged = gis_gdf.merge(
                                result_df, left_on=gis_match_col, right_on=result_match_col, how="inner"
                            )
                            st.success(f"Merged: {len(merged)} features with coefficients")

                            # Get centroids for point display
                            merged["_centroid"] = merged.geometry.centroid
                            merged["_lat"] = merged["_centroid"].y
                            merged["_lon"] = merged["_centroid"].x

                            _render_results_map(
                                merged.drop(columns=["geometry", "_centroid"]),
                                "_lat", "_lon", coef_col,
                                gis_gdf=merged,  # pass for line/polygon rendering
                            )

        else:
            st.info("Upload a results file to get started, or run a GLM analysis in the **Upload Raw Data** tab first.")


# ---- Page: About ----
elif page == "About":
    st.title("About This Framework")

    st.markdown("""
    ## Road Climate Resilience Analytical Framework

    This open-source platform provides a lightweight, transferable methodology for assessing
    how weather conditions affect road network performance at the link level.

    ### The Framework: Estimate → Map → Explain

    1. **Estimate**: A Gamma GLM with log link models travel speed on **weekdays only**
       as a function of weather (temperature, precipitation), traffic volume, temporal
       controls (hour, month, year), calendar effects (school/university term, bank holidays),
       disruption events, and link × precipitation interactions. Standard errors are
       clustered at the road-link level. This produces a precipitation sensitivity
       coefficient for each road link.

    2. **Map**: Link-level coefficients are visualised on an interactive map, enabling
       planners to identify the most climate-vulnerable sections of their network.

    3. **Explain**: An OLS regression of link-level coefficients on road features
       (number of lanes, speed limit, road class, daily flow, length) reveals which
       physical characteristics are associated with greater or lesser climate resilience.

    ### Key Advantages

    - **Lightweight computation**: Standard GLM, runs on a laptop — no microsimulation needed
    - **Open data compatible**: Uses publicly available traffic counts, weather records,
      and road characteristics
    - **Transferable**: Any local authority can apply this framework to their own network
    - **Interpretable**: Results are directly meaningful for transport planning decisions

    ### Data Sources (Cambridgeshire Example)

    | Data | Source | Access |
    |------|--------|--------|
    | Traffic speed & volume | WebTRIS / MIDAS sensors | Open (National Highways) |
    | Weather | CEDA / Met Office MIDAS | Open (registration required) |
    | Road features | DfT Road Statistics | Open |
    | Transport disruptions | National Highways | Open |
    | Calendar controls | UK Gov / university websites | Open |

    ### Citation

    *To be added upon publication.*

    ### Author

    **Yibin Li**
    Postdoctoral Research Associate
    Department of Engineering, University of Cambridge
    [yl680@cantab.ac.uk](mailto:yl680@cantab.ac.uk)

    ### Contact

    For questions or collaboration:
    - Email: [yl680@cantab.ac.uk](mailto:yl680@cantab.ac.uk)
    - GitHub: [github.com/yblllll/road-climate-resilience](https://github.com/yblllll/road-climate-resilience)
    """)

    st.divider()
    st.markdown(
        f'<div class="dare-footer">'
        f'Developed as part of the <a href="https://dare.ac.uk" target="_blank">DARe</a> '
        f'Flex Fund Project — National Hub for Decarbonised, Adaptable, and Resilient '
        f'Transport Infrastructures'
        f'</div>',
        unsafe_allow_html=True,
    )
