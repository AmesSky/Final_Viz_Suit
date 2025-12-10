import streamlit as st
import leafmap.foliumap as leafmap
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import requests
import tempfile

# ---------------------------------------------------------
# Page setup
# ---------------------------------------------------------
st.set_page_config(page_title="Vertiport Suitability Explorer", layout="wide")

st.title("Vertiport Suitability Visualization – Salt Lake City")
st.markdown("""
This dashboard visualizes **vertiport suitability** for Salt Lake City based on the classified raster datasets.
Use the selector to switch between **Vacant Land** and **Commercial/Industrial Land** suitability maps.
""")

# ---------------------------------------------------------
# Raster URLs from GitHub
# ---------------------------------------------------------
raster_urls = {
    "Vacant Land Suitability":
        "https://raw.githubusercontent.com/AmesSky/Final_Viz_Suit/main/data/SLC_Suit_VC.tif",
    "Commercial/Industrial Suitability":
        "https://raw.githubusercontent.com/AmesSky/Final_Viz_Suit/main/data/SLC_Suit_CI.tif"
}

selected_name = st.selectbox("Choose a dataset:", list(raster_urls.keys()))
url = raster_urls[selected_name]

# ---------------------------------------------------------
# Download raster file to temporary directory
# ---------------------------------------------------------
@st.cache_data
def download_raster(url):
    r = requests.get(url)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".tif")
    tmp.write(r.content)
    tmp.flush()
    return tmp.name

local_path = download_raster(url)

# ---------------------------------------------------------
# Load TIFF (PIL – no georeferencing but values preserved)
# ---------------------------------------------------------
img = Image.open(local_path)
arr = np.array(img)

# ---------------------------------------------------------
# Suitability Classes (your exact values)
# 1 = neutral
# 2 = possible
# 3 = unsuitable
# 4 = suitable
# 5 = highly suitable
# ---------------------------------------------------------

color_map = {
    1: (191, 191, 191, 255),   # neutral (gray)
    2: (255, 255, 0, 255),     # possible (yellow)
    3: (0, 0, 255, 255),       # unsuitable (blue)
    4: (0, 255, 0, 255),       # suitable (green)
    5: (255, 0, 0, 255)        # highly suitable (red)
}

colored_img = np.zeros((arr.shape[0], arr.shape[1], 4), dtype=np.uint8)

for val, color in color_map.items():
    colored_img[arr == val] = color

# ---------------------------------------------------------
# Save colored raster PNG for overlay
# ---------------------------------------------------------
png_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
Image.fromarray(colored_img).save(png_temp.name)

# ---------------------------------------------------------
# Histogram of suitability values
# ---------------------------------------------------------
st.subheader("Suitability Value Histogram")

flat_vals = arr.flatten()
flat_vals = flat_vals[(flat_vals >= 1) & (flat_vals <= 5)]

fig, ax = plt.subplots(figsize=(6, 4))
ax.hist(flat_vals, bins=[1,2,3,4,5,6], color='green', edgecolor='black')
ax.set_xticks([1, 2, 3, 4, 5])
ax.set_xlabel("Suitability Class")
ax.set_ylabel("Frequency")
ax.set_title("Distribution of Suitability Values")
st.pyplot(fig)

# ---------------------------------------------------------
# Interactive Map Section
# ---------------------------------------------------------
st.subheader("Interactive Suitability Map")

m = leafmap.Map(center=[40.57, -111.92], zoom=11)

# Add basemap
m.add_basemap("Esri.WorldImagery")

# ---------------------------------------------------------
# Add the raster overlay using your correct WGS84 bounds
# Bounds computed from your EPSG:26912 raster:
# South = 40.501
# North = 40.639
# West  = -112.085
# East  = -111.754
# ---------------------------------------------------------
m.add_image(
    png_temp.name,
    bounds=[[40.501, -112.085], [40.639, -111.754]],
    opacity=0.55,
    layer_name=selected_name
)

# ---------------------------------------------------------
# Custom Legend (matches your raster)
# ---------------------------------------------------------
legend_dict = {
    "neutral": "#bfbfbf",
    "possible": "#ffff00",
    "unsuitable": "#0000ff",
    "suitable": "#00ff00",
    "highly suitable": "#ff0000"
}

m.add_legend(title="Suitability Classes", legend_dict=legend_dict)

# ---------------------------------------------------------
# Render the interactive map
# ---------------------------------------------------------
m.to_streamlit(height=650)
