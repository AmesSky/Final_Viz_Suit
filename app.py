import streamlit as st
import numpy as np
import imageio.v3 as iio
import matplotlib.pyplot as plt
import leafmap.foliumap as leafmap
from streamlit.components.v1 import html

# ----------------------------
# PAGE SETTINGS
# ----------------------------
st.set_page_config(page_title="Salt Lake Suitability Explorer", layout="wide")
st.title("🌄 Salt Lake City Suitability Analysis Web App")

st.markdown("Explore suitability raster layers using an interactive map and charts.")

# ----------------------------
# RASTER LOCATIONS (GitHub RAW)
# ----------------------------
RASTER_URLS = {
    "Vacant Land Suitability": "https://raw.githubusercontent.com/AmesSky/Final_Viz_Suit/main/SLC_Suit_VC.tif",
    "Commercial Suitability": "https://raw.githubusercontent.com/AmesSky/Final_Viz_Suit/main/SLC_Suit_CI.tif",
}

selected_raster = st.sidebar.selectbox("Select a suitability raster:", list(RASTER_URLS.keys()))
raster_url = RASTER_URLS[selected_raster]


# ----------------------------
# LOAD RASTER WITHOUT RASTERIO
# Using imageio (Streamlit Cloud compatible)
# ----------------------------
@st.cache_data
def load_tif(url):
    arr = iio.imread(url)  # Reads TIFF into numpy array
    return arr

arr = load_tif(raster_url)

st.subheader("Raster Information")
st.write(f"Shape: {arr.shape}")
st.write(f"Unique values: {np.unique(arr)}")

# ----------------------------
# HISTOGRAM
# ----------------------------
st.subheader("Suitability Value Histogram")

fig, ax = plt.subplots(figsize=(6, 3))
ax.hist(arr.flatten(), bins=len(np.unique(arr)), edgecolor="black")
ax.set_title("Distribution of Suitability Values")
ax.set_xlabel("Suitability Code")
ax.set_ylabel("Frequency")
st.pyplot(fig)

# ----------------------------
# SUITABILITY COLORS
# ----------------------------
color_map = {
    1: "#BEBEBE",
    2: "#FFD700",
    3: "#800080",
    4: "#00FF00",
    5: "#FF0000",
}

# convert raster to color PNG
def convert_to_rgb(arr):
    rgb = np.zeros((arr.shape[0], arr.shape[1], 3), dtype=np.uint8)
    for val, color in color_map.items():
        rgb[arr == val] = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
    return rgb

rgb = convert_to_rgb(arr)

# ----------------------------
# INTERACTIVE MAP
# ----------------------------
st.subheader("Interactive Map")

m = leafmap.Map(center=[40.75, -111.9], zoom=10)
m.add_basemap("HYBRID")

# approximate bounds (lat/lon) for visualization  
bounds = [[40.55, -112.15], [40.90, -111.7]]

m.add_image(rgb, bounds, opacity=0.75, name=selected_raster)
m.add_layer_control()

html(m.to_html(), height=700)

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
