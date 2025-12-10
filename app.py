import streamlit as st
import leafmap.foliumap as leafmap
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import requests
import tempfile

st.set_page_config(page_title="Vertiport Suitability Explorer", layout="wide")

raster_urls = {
    "Vacant Land Suitability":
        "https://raw.githubusercontent.com/AmesSky/Final_Viz_Suit/main/data/SLC_Suit_VC.tif",
    "Commercial/Industrial Suitability":
        "https://raw.githubusercontent.com/AmesSky/Final_Viz_Suit/main/data/SLC_Suit_CI.tif"
}

selected_name = st.selectbox("Choose dataset", list(raster_urls.keys()))
url = raster_urls[selected_name]

@st.cache_data
def download_raster(url):
    r = requests.get(url)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".tif")
    tmp.write(r.content)
    tmp.flush()
    return tmp.name

local_path = download_raster(url)

# Read raster with PIL
img = Image.open(local_path)
raster = np.array(img).astype("float32")

# Histogram
st.subheader("Histogram of Suitability Values")
fig, ax = plt.subplots()
ax.hist(raster.flatten(), bins=30)
st.pyplot(fig)

# Map
st.subheader("Spatial Visualization")
m = leafmap.Map(center=[40.75, -111.9], zoom=10)
m.add_raster(local_path, layer_name=selected_name, colormap="viridis")
m.to_streamlit(height=500)
