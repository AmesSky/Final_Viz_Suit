import streamlit as st
import leafmap.foliumap as leafmap
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import requests
import tempfile

st.set_page_config(page_title="Vertiport Suitability Explorer", layout="wide")

st.title("Vertiport Suitability Visualization – Salt Lake City")

# Raster sources
raster_urls = {
    "Vacant Land Suitability":
        "https://raw.githubusercontent.com/AmesSky/Final_Viz_Suit/main/data/SLC_Suit_VC.tif",
    "Commercial/Industrial Suitability":
        "https://raw.githubusercontent.com/AmesSky/Final_Viz_Suit/main/data/SLC_Suit_CI.tif"
}

selected_name = st.selectbox("Choose dataset:", raster_urls.keys())
url = raster_urls[selected_name]

# Download raster
@st.cache_data
def download_raster(url):
    r = requests.get(url)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".tif")
    tmp.write(r.content)
    tmp.flush()
    return tmp.name

local_path = download_raster(url)

# Load TIFF (indexed)
img = Image.open(local_path).convert("P")
arr = np.array(img).astype("int32")

# -----------------------------
# Reclassify scaled values → 1–5
# -----------------------------
reclass_map = {
    17: 1,   # neutral
    34: 2,   # possible
    51: 3,   # unsuitable
    68: 4,   # suitable
    85: 5    # highly suitable
}

arr_reclass = np.zeros_like(arr)

for old, new in reclass_map.items():
    arr_reclass[arr == old] = new

valid_values = arr_reclass[arr_reclass > 0]

# -----------------------------
# Histogram
# -----------------------------
st.subheader("Suitability Histogram")

fig, ax = plt.subplots(figsize=(5, 4))
ax.hist(valid_values, bins=[1,2,3,4,5,6], edgecolor='black', color='green')
ax.set_xticks([1,2,3,4,5])
ax.set_xlabel("Suitability Class")
ax.set_ylabel("Frequency")
st.pyplot(fig)

# -----------------------------
# Color mapping for overlay
# -----------------------------
color_map = {
    1: (191, 191, 191, 255),   # neutral
    2: (255, 255, 0, 255),     # possible
    3: (0, 0, 255, 255),       # unsuitable
    4: (0, 255, 0, 255),       # suitable
    5: (255, 0, 0, 255)        # highly suitable
}

rgba = np.zeros((arr.shape[0], arr.shape[1], 4), dtype=np.uint8)

for val, color in color_map.items():
    rgba[arr_reclass == val] = color

# Save PNG overlay
png_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
Image.fromarray(rgba).save(png_temp.name)

# -----------------------------
# Map
# -----------------------------
st.subheader("Interactive Suitability Map")

m = leafmap.Map(center=[40.57, -111.92], zoom=11)
m.add_basemap("Esri.WorldImagery")

bounds = [[40.501, -112.085], [40.639, -111.754]]

m.add_image(
    png_temp.name,
    bounds=bounds,
    opacity=0.55,
    layer_name=selected_name
)

legend_dict = {
    "neutral": "#bfbfbf",
    "possible": "#ffff00",
    "unsuitable": "#0000ff",
    "suitable": "#00ff00",
    "highly suitable": "#ff0000"
}

m.add_legend(title="Suitability Classes", legend_dict=legend_dict)

m.to_streamlit(height=650)
