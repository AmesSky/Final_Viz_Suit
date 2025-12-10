import streamlit as st
import leafmap.foliumap as leafmap
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import requests
import tempfile

st.set_page_config(page_title="Vertiport Suitability Explorer", layout="wide")

# GitHub paths
raster_urls = {
    "Vacant Land Suitability":
        "https://raw.githubusercontent.com/AmesSky/Final_Viz_Suit/main/data/SLC_Suit_VC.tif",
    "Commercial/Industrial Suitability":
        "https://raw.githubusercontent.com/AmesSky/Final_Viz_Suit/main/data/SLC_Suit_CI.tif"
}

selected_name = st.selectbox("Choose dataset:", list(raster_urls.keys()))
url = raster_urls[selected_name]

@st.cache_data
def download_raster(url):
    r = requests.get(url)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".tif")
    tmp.write(r.content)
    tmp.flush()
    return tmp.name

local_path = download_raster(url)

# -----------------------------------
# 1. Load raster pixel values (PIL)
# -----------------------------------
img = Image.open(local_path)
raster = np.array(img).astype("float32")

# Handle nodata if needed
raster[raster == 0] = np.nan

# -----------------------------------
# 2. Histogram visualization
# -----------------------------------
st.subheader("Histogram of Suitability Values")
fig, ax = plt.subplots()
ax.hist(raster.flatten(), bins=30, color="green")
st.pyplot(fig)

# -----------------------------------
# 3. Map visualization using PNG overlay
# -----------------------------------
st.subheader("Spatial Visualization")

# Convert to PNG for overlay
png_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
Image.fromarray((np.nan_to_num(raster) / np.nanmax(raster) * 255).astype("uint8")).save(png_temp.name)

m = leafmap.Map(center=[40.75, -111.90], zoom=10)

# This works on Streamlit Cloud (no GDAL required)
m.add_image(
    png_temp.name,
    bounds=[[40.4, -112.2], [41.1, -111.6]],
    opacity=0.7,
    layer_name=selected_name
)

m.to_streamlit(height=500)
