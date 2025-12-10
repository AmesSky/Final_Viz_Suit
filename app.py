import streamlit as st
import numpy as np
import rasterio
import matplotlib.pyplot as plt
import leafmap.foliumap as leafmap
from streamlit.components.v1 import html

# ----------------------------
# PAGE SETUP
# ----------------------------
st.set_page_config(page_title="Salt Lake Suitability Explorer", layout="wide")

st.title("🌄 Salt Lake City Suitability Analysis Web App")
st.markdown("Explore suitability raster layers using an interactive map and charts.")

# ----------------------------
# RASTER DATA (GitHub URLs)
# ----------------------------
RASTER_URLS = {
    "Vacant Land Suitability": "https://raw.githubusercontent.com/AmesSky/Final_Viz_Suit/main/SLC_Suit_VC.tif",
    "Commercial Suitability": "https://raw.githubusercontent.com/AmesSky/Final_Viz_Suit/main/SLC_Suit_CI.tif",
}

selected_raster = st.sidebar.selectbox("Select a suitability raster:", list(RASTER_URLS.keys()))
raster_path = RASTER_URLS[selected_raster]


# ----------------------------
# LOAD RASTER SAFELY
# ----------------------------
@st.cache_data
def load_raster(raster_url):
    with rasterio.open(raster_url) as src:
        arr = src.read(1)
        profile = src.profile
        bounds = src.bounds
    return arr, profile, bounds


arr, profile, bounds = load_raster(raster_path)

st.subheader("Raster Information")
st.write(f"Shape: {arr.shape}")
st.write(f"Min value: {np.min(arr)}, Max value: {np.max(arr)}")

unique_vals = np.unique(arr)
st.write("Unique raster values:", unique_vals)


# ----------------------------
# HISTOGRAM (STATIC)
# ----------------------------
st.subheader("Suitability Histogram")

fig, ax = plt.subplots(figsize=(6, 3))

ax.hist(arr.flatten(), bins=len(unique_vals), edgecolor="black")
ax.set_title("Distribution of Raster Values")
ax.set_xlabel("Suitability Value")
ax.set_ylabel("Count")

st.pyplot(fig)


# ----------------------------
# SUITABILITY COLOR MAP
# ----------------------------
color_map = {
    1: "#BEBEBE",   # neutral (gray)
    2: "#FFD700",   # possible (yellow)
    3: "#800080",   # unsuitable (purple)
    4: "#00FF00",   # suitable (green)
    5: "#FF0000",   # highly suitable (red)
}

st.subheader("Interactive Suitability Map")

# ----------------------------
# LEAFMAP SETUP (FOLIUM BACKEND)
# ----------------------------
m = leafmap.Map(center=[40.75, -111.9], zoom=10)

# Add basemap
m.add_basemap("HYBRID")


# ----------------------------
# BUILD COLOR OVERLAY PNG
# ----------------------------
def create_color_png(arr):
    """Convert classified raster to an RGB image for overlay."""
    rgb = np.zeros((arr.shape[0], arr.shape[1], 3), dtype=np.uint8)

    for value, hex_color in color_map.items():
        rgb[arr == value] = tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))

    return rgb


rgb_image = create_color_png(arr)


# ----------------------------
# ADD RASTER TO MAP
# ----------------------------
# Build bounds for folium
img_bounds = [
    [bounds.bottom, bounds.left],
    [bounds.top, bounds.right],
]

m.add_image(
    rgb_image,
    img_bounds,
    opacity=0.7,
    name=selected_raster
)

m.add_layer_control()


# ----------------------------
# RENDER FULLY INTERACTIVE MAP
# ----------------------------
map_html = m.to_html()
html(map_html, height=700)


# ----------------------------
# LEGEND
# ----------------------------
st.subheader("Legend")
for label, color in zip(
        ["neutral", "possible", "unsuitable", "suitable", "highly suitable"],
        ["#BEBEBE", "#FFD700", "#800080", "#00FF00", "#FF0000"]):

    st.markdown(
        f"<div style='display:flex;align-items:center;'>"
        f"<div style='width:20px;height:20px;background:{color};margin-right:10px;'></div>"
        f"{label}</div>",
        unsafe_allow_html=True
    )
