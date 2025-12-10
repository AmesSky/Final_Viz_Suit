# -----------------------
# Load raster and reclassify to RGBA colors
# -----------------------

import streamlit as st
import leafmap.foliumap as leafmap
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import requests
import tempfile

st.set_page_config(page_title="Vertiport Suitability Explorer", layout="wide")

# GitHub raster URLs
raster_urls = {
    "Vacant Land Suitability":
        "https://raw.githubusercontent.com/AmesSky/Final_Viz_Suit/main/data/SLC_Suit_VC.tif",
    "Commercial/Industrial Suitability":
        "https://raw.githubusercontent.com/AmesSky/Final_Viz_Suit/main/data/SLC_Suit_CI.tif"
}

selected_name = st.selectbox("Choose dataset:", list(raster_urls.keys()))
url = raster_urls[selected_name]

# Download raster from GitHub
@st.cache_data
def download_raster(url):
    r = requests.get(url)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".tif")
    tmp.write(r.content)
    tmp.flush()
    return tmp.name

local_path = download_raster(url)

# Read raster as array
img = Image.open(local_path)
arr = np.array(img)

# Suitability classes (your actual values)
# 1 = neutral
# 2 = possible
# 3 = unsuitable
# 4 = suitable
# 5 = highly suitable

color_map = {
    1: (191, 191, 191, 255),   # neutral (gray)
    2: (255, 255, 0, 255),     # possible (yellow)
    3: (0, 0, 255, 255),       # unsuitable (blue)
    4: (0, 255, 0, 255),       # suitable (green)
    5: (255, 0, 0, 255)        # highly suitable (red)
}

# Create color raster
colored_img = np.zeros((arr.shape[0], arr.shape[1], 4), dtype=np.uint8)

for val, color in color_map.items():
    colored_img[arr == val] = color

# Save colored PNG
png_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
Image.fromarray(colored_img).save(png_temp.name)

# -----------------------
# Spatial visualization
# -----------------------
st.subheader("Spatial Visualization")

m = leafmap.Map(center=[40.75, -111.9], zoom=10)
m.add_basemap("Esri.WorldImagery")

# Adjust bounds to match Salt Lake City region
m.add_image(
    png_temp.name,
    bounds=[[40.4, -112.2], [41.1, -111.6]],
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

m.to_streamlit(height=600)
