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

_logo_b64 = _img_to_b64(_logo_small_path)
_watermark_b64 = _img_to_b64(_watermark_path)

# CSS for watermark background (sunburst SVG fallback if no image)
_watermark_css = ""
if _watermark_b64:
    _watermark_css = f"""
    /* Watermark from image */
    [data-testid="stAppViewContainer"]::before {{
        content: "";
        position: fixed;
        bottom: -10%;
        left: -5%;
        width: 60%;
        height: 80%;
        background-image: url("data:image/png;base64,{_watermark_b64}");
        background-size: contain;
        background-repeat: no-repeat;
        opacity: 0.04;
        pointer-events: none;
        z-index: 0;
    }}
    """
else:
    # CSS-only sunburst watermark (approximation of the DARe starburst)
    _watermark_css = f"""
    [data-testid="stAppViewContainer"]::before {{
        content: "";
        position: fixed;
        bottom: -15%;
        left: -10%;
        width: 500px;
        height: 500px;
        background: conic-gradient(
            from 0deg,
            transparent 0deg, {DARE_GREEN}08 5deg, transparent 10deg,
            transparent 30deg, {DARE_GREEN}08 35deg, transparent 40deg,
            transparent 60deg, {DARE_GREEN}08 65deg, transparent 70deg,
            transparent 90deg, {DARE_GREEN}08 95deg, transparent 100deg,
            transparent 120deg, {DARE_GREEN}08 125deg, transparent 130deg,
            transparent 150deg, {DARE_GREEN}08 155deg, transparent 160deg,
            transparent 180deg, {DARE_GREEN}08 185deg, transparent 190deg,
            transparent 210deg, {DARE_GREEN}08 215deg, transparent 220deg,
            transparent 240deg, {DARE_GREEN}08 245deg, transparent 250deg,
            transparent 270deg, {DARE_GREEN}08 275deg, transparent 280deg,
            transparent 300deg, {DARE_GREEN}08 305deg, transparent 310deg,
            transparent 330deg, {DARE_GREEN}08 335deg, transparent 340deg,
            transparent 360deg
        );
        border-radius: 50%;
        opacity: 0.6;
        pointer-events: none;
        z-index: 0;
    }}
    """

# Top-right logo CSS
_topright_logo_css = ""
if _logo_b64:
    _topright_logo_css = f"""
    /* Fixed white header bar — covers content when scrolling */
    [data-testid="stHeader"] {{
        background-color: #FFFFFF !important;
        height: 70px !important;
        border-bottom: 1px solid #e0e4e8;
        z-index: 998;
    }}
    /* DARe logo inside the header bar */
    [data-testid="stAppViewContainer"]::after {{
        content: "";
        position: fixed;
        top: 8px;
        left: 250px;
        width: 200px;
        height: 55px;
        background-image: url("data:image/png;base64,{_logo_b64}");
        background-size: contain;
        background-repeat: no-repeat;
        pointer-events: none;
        z-index: 1000;
    }}
    /* Push main content below the 70px header */
    .stMainBlockContainer {{
        padding-top: 30px !important;
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
def load_example_data():
    """Load the Cambridgeshire example dataset."""
    geojson_path = os.path.join(DATA_DIR, "linkgis.geojson")
    coef_path = os.path.join(DATA_DIR, "link_coefficients_with_features.csv")
    feature_path = os.path.join(DATA_DIR, "road_features_with_infrastructure.csv")
    glm_path = os.path.join(DATA_DIR, "gamma_glm_full_results.csv")

    data = {}
    if os.path.exists(geojson_path):
        with open(geojson_path) as f:
            data["geojson"] = json.load(f)
    links_path = os.path.join(DATA_DIR, "srn_links_resilience.geojson")
    if os.path.exists(links_path):
        with open(links_path) as f:
            data["links_geojson"] = json.load(f)
    if os.path.exists(coef_path):
        data["coefficients"] = pd.read_csv(coef_path)
    if os.path.exists(feature_path):
        data["features"] = pd.read_csv(feature_path)
    if os.path.exists(glm_path):
        data["glm_results"] = pd.read_csv(glm_path)
    # Load model summary statistics (JSON)
    summary_json_path = os.path.join(DATA_DIR, "model_summary.json")
    if os.path.exists(summary_json_path):
        with open(summary_json_path) as f:
            data["model_summary"] = json.load(f)
    # Also check for summary text
    summary_txt_path = os.path.join(DATA_DIR, "gamma_glm_summary.txt")
    if os.path.exists(summary_txt_path):
        with open(summary_txt_path) as f:
            data["model_summary_text"] = f.read()
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
        Upload your merged traffic + weather CSV to run the full resilience analysis pipeline.

        **Important**: The model estimates on **weekday data only** (Monday–Friday).
        Weekend observations will be automatically excluded during analysis, as weekend
        traffic patterns differ substantially and would confound climate sensitivity estimates.

        ### Required Columns

        | Column | Description | Source |
        |--------|-------------|--------|
        | `time` | Datetime (e.g., 2024-01-15T08:00:00) | National Highways WebTRIS |
        | `Avg mph` | Average speed in mph | National Highways WebTRIS |
        | `Total Volume` | Vehicle count | National Highways WebTRIS |
        | `link name` | Road link identifier | National Highways WebTRIS |
        | `air_temperature` | Temperature (°C) | Met Office |
        | `prcp_amt` | Precipitation (mm) | Met Office |
        | `Accident` | Binary (0/1) | Alchera |
        | `MaintenanceWorks` | Binary (0/1) | Alchera |

        Optional: `AbnormalTraffic`, `GeneralObstruction`, `EnvironmentalObstruction`,
        `VehicleObstruction`, `AnimalPresenceObstruction`, `RoadOrCarriagewayOrLaneManagement`
        """)

        st.divider()

        input_method = st.radio(
            "How would you like to provide your data?",
            ["Enter file path (recommended for large files)", "Upload file (small files only, <200MB)"],
            horizontal=True,
        )

        upload_path = None

        if input_method == "Enter file path (recommended for large files)":
            raw_file_path = st.text_input(
                "Full path to your merged traffic + weather CSV",
                placeholder="/Users/you/data/merged_traffic_weather.csv",
                help="Enter the full path to the CSV file on your computer. "
                     "This avoids the slow upload process for large files (>1GB).",
            )
            if raw_file_path and os.path.exists(raw_file_path):
                file_size_mb = os.path.getsize(raw_file_path) / (1024**2)
                st.success(f"File found: `{os.path.basename(raw_file_path)}` ({file_size_mb:.1f} MB)")
                upload_path = raw_file_path
            elif raw_file_path:
                st.error(f"File not found: `{raw_file_path}`")
        else:
            raw_file = st.file_uploader(
                "Upload your merged traffic + weather CSV",
                type=["csv"],
                help="For files under 200MB. For larger files, use the file path option.",
                key="raw_upload",
            )
            if raw_file is not None:
                upload_path = os.path.join(UPLOAD_DIR, raw_file.name)
                with open(upload_path, "wb") as f:
                    f.write(raw_file.getbuffer())
                st.success(f"File saved: `uploads/{raw_file.name}`")

        if upload_path is not None:

            try:
                preview_df = pd.read_csv(upload_path, nrows=100)
                st.subheader("Data Preview")
                st.dataframe(preview_df.head(20), **_USE_WIDTH)

                st.subheader("Data Summary")
                col1, col2, col3 = st.columns(3)
                total_rows_estimate = sum(1 for _ in open(upload_path)) - 1
                with col1:
                    st.metric("Columns", len(preview_df.columns))
                with col2:
                    st.metric("Estimated Rows", f"{total_rows_estimate:,}")
                with col3:
                    links = preview_df.get("link name", preview_df.get("link_name", pd.Series())).nunique()
                    st.metric("Unique Links (sample)", links)

                # Check required columns
                required = ["time", "Avg mph", "link name", "air_temperature", "prcp_amt"]
                alt_names = {
                    "time": ["Report Date", "datetime", "timestamp"],
                    "Avg mph": ["avg_mph", "speed", "avgmph"],
                    "link name": ["link_name", "linkname", "Road_Name"],
                    "air_temperature": ["temperature", "temp"],
                    "prcp_amt": ["precipitation", "rainfall", "precip"],
                }

                missing = []
                found_mapping = {}
                for req in required:
                    if req in preview_df.columns:
                        found_mapping[req] = req
                    else:
                        found_alt = False
                        for alt in alt_names.get(req, []):
                            if alt in preview_df.columns:
                                found_mapping[req] = alt
                                found_alt = True
                                break
                        if not found_alt:
                            missing.append(req)

                if missing:
                    st.error(f"Missing required columns: {missing}")
                    st.info(f"Available columns: {list(preview_df.columns)}")
                else:
                    st.success("All required columns found!")
                    if found_mapping:
                        st.write("Column mapping:", found_mapping)

                    st.divider()
                    st.subheader("Analysis Configuration")

                    sample_pct = st.slider(
                        "Sample percentage (use lower for testing, 100% for final)",
                        min_value=5, max_value=100, value=20, step=5,
                    )

                    speed_col = st.selectbox(
                        "Speed column:",
                        [found_mapping.get("Avg mph", "Avg mph")]
                        + [c for c in preview_df.columns if "mph" in c.lower() or "speed" in c.lower()],
                    )

                    link_col = st.selectbox(
                        "Link identifier column:",
                        [found_mapping.get("link name", "link name")]
                        + [c for c in preview_df.columns if "link" in c.lower() or "road" in c.lower()],
                    )

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
                        prep_output = os.path.join(UPLOAD_DIR, "prepared_data.csv")
                        cmd1 = [
                            sys.executable, os.path.join(repo_dir, "scripts", "01_data_preparation.py"),
                            "--input", upload_path,
                            "--output", prep_output,
                            "--speed-col", speed_col,
                            "--link-col", link_col,
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

        else:
            st.info("Upload a CSV file to get started, or explore the Cambridgeshire example using the Map and Dashboard pages.")

    # ---- Tab 2: Upload results to visualise on map ----
    with upload_tab2:
        st.markdown("""
        Upload a CSV with your resilience analysis results to visualise them on an interactive map.

        ### Required Columns

        | Column | Description |
        |--------|-------------|
        | `latitude` | Latitude of road link (WGS84) |
        | `longitude` | Longitude of road link (WGS84) |
        | `coefficient` | Precipitation sensitivity coefficient |

        ### Optional Columns (for richer tooltips)
        `link_name`, `highway`, `road_name`, `p_value`, `significance_level`,
        `Number of lanes`, `Speed limit (mph)`, `Average daily flow`
        """)

        st.divider()

        results_file = st.file_uploader(
            "Upload your results CSV",
            type=["csv"],
            help="CSV with at least latitude, longitude, and a precipitation coefficient column.",
            key="results_upload",
        )

        if results_file is not None:
            try:
                result_df = pd.read_csv(results_file)
                st.success(f"Loaded {len(result_df)} road links")

                # Find coordinate columns
                lat_col = None
                lon_col = None
                for c in result_df.columns:
                    cl = c.lower()
                    if "lat" in cl:
                        lat_col = c
                    if "lon" in cl:
                        lon_col = c

                coef_col = None
                for candidate in ["coefficient", "precipitat", "precipitation_interaction_coefficient",
                                  "total_precipitation_effect", "precip_coef"]:
                    if candidate in result_df.columns:
                        coef_col = candidate
                        break

                if not lat_col or not lon_col:
                    st.error("Could not find latitude/longitude columns. Please ensure your CSV has columns containing 'lat' and 'lon'.")
                    st.info(f"Available columns: {list(result_df.columns)}")
                elif not coef_col:
                    st.error("Could not find a coefficient column. Expected one of: coefficient, precipitat, precipitation_interaction_coefficient")
                    st.info(f"Available columns: {list(result_df.columns)}")
                else:
                    st.write(f"Using: **{lat_col}** (lat), **{lon_col}** (lon), **{coef_col}** (coefficient)")

                    # Preview data
                    st.subheader("Data Preview")
                    st.dataframe(result_df.head(10).round(6), **_USE_WIDTH)

                    # Build map
                    st.subheader("Resilience Map")

                    valid = result_df.dropna(subset=[lat_col, lon_col, coef_col])
                    center_lat = valid[lat_col].mean()
                    center_lon = valid[lon_col].mean()
                    vmin = valid[coef_col].min()
                    vmax = valid[coef_col].max()

                    m = folium.Map(location=[center_lat, center_lon], zoom_start=10, tiles="CartoDB positron")

                    for _, row in valid.iterrows():
                        coef_val = row[coef_col]
                        color, _ = get_discrete_color(coef_val, vmin, vmax)

                        # Build popup from available columns
                        popup_parts = []
                        for display_col in ["road_name", "highway", "link_name", "linkname",
                                            "Number of lanes", "Speed limit (mph)", "p_value"]:
                            if display_col in row.index and pd.notna(row[display_col]):
                                popup_parts.append(f"<b>{display_col}:</b> {row[display_col]}")

                        popup_html = f"""
                        <div style="font-family: Arial; font-size: 12px;">
                            <b>Coefficient:</b> {coef_val:.6f}<br>
                            {'<br>'.join(popup_parts)}
                        </div>
                        """

                        label = str(row.get("road_name", row.get("linkname", row.get("link_name", ""))))

                        folium.CircleMarker(
                            location=[row[lat_col], row[lon_col]],
                            radius=7,
                            color=color,
                            fill=True,
                            fill_color=color,
                            fill_opacity=0.8,
                            popup=folium.Popup(popup_html, max_width=300),
                            tooltip=f"{label}: {coef_val:.4f}",
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
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Links", len(valid))
                    with col2:
                        st.metric("Mean Coefficient", f"{valid[coef_col].mean():.6f}")
                    with col3:
                        st.metric("Most Vulnerable", f"{valid[coef_col].min():.6f}")
                    with col4:
                        st.metric("Most Resilient", f"{valid[coef_col].max():.6f}")

                    if "highway" in valid.columns:
                        st.subheader("By Highway")
                        hw_stats = valid.groupby("highway")[coef_col].agg(["mean", "count", "min", "max"]).round(6)
                        hw_stats.columns = ["Mean", "N Links", "Min", "Max"]
                        st.dataframe(hw_stats, **_USE_WIDTH)

            except Exception as e:
                st.error(f"Error processing file: {e}")

        else:
            st.info("Upload a results CSV to visualise your road-level resilience scores on an interactive map.")


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

    If you use this framework in your research, please cite:
    > [Paper reference to be added upon publication]

    ### Contact

    For questions or collaboration, please open an issue on
    [GitHub](https://github.com/YOUR_USERNAME/road-climate-resilience).
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
