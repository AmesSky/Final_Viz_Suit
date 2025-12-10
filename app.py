import streamlit as st
import leafmap.foliumap as leafmap
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import requests
import tempfile

# ------------------------------------------
# Setup
# ------------------------------------------
st.set_page_config(page_title="Vertiport Suitability Explorer", layout="wide")

st.title("Vertiport Suitability Visualization – Salt Lake City")

raster_urls = {
    "Vacant Land Suitability":
        "https://raw.githubusercontent.com/AmesSky/Final_Viz_Suit/main/data/SLC_Suit_VC.tif",
    "Commercial/Industrial Suitability":
        "https://raw.githubusercontent.com/AmesSky/Final_Viz_Suit/main/data/SLC_Suit_CI.tif"
}

selected_name = st.selectbox("Choose dataset:", raster_urls.keys())
url = raster_urls[selected_name]

# ------------------------------------------
# Download raster
# ------------------------------------------
@st.cache_data
def download_raster(url):
    r = requests.get(url)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".tif")
    tmp.write(r.content)
    tmp.flush()
    return tmp.name

local_path = download_raster(url)

# ------------------------------------------
# Load TIFF (force palette mode to raw values)
# ------------------------------------------
img = Image.open(local_path).convert("P")
arr = np.array(img).astype("int32")

# ------------------------------------------
# 🔍 DEBUGGING BLOCK — PRINT RASTER VALUES
# ------------------------------------------
st.subheader("Debug Information (Raster Inspection)")
st.write("Unique raster values:", np.unique(arr)[:50])   # Print first 50 unique values
st.write("Min value:", arr.min(), "Max value:", arr.max())
st.write("Raster shape:", arr.shape)

# STOP EXECUTION UNTIL WE KNOW THE VALUE RANGE
st.stop()
