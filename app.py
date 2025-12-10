import streamlit as st
import leafmap.foliumap as leafmap
import rasterio
import numpy as np
import matplotlib.pyplot as plt
import requests
import tempfile

st.set_page_config(page_title="Vertiport Suitability Explorer", layout="wide")

st.title("Vertiport Suitability Web Application")
st.markdown("""
Explore vertiport suitability for Salt Lake City based on **Vacant Land** and 
**Commercial/Industrial Land** datasets hosted in the GitHub repository.
""")

# ------------------------------------------------------------
# 1. GitHub RAW URLs for your specific repository
# ------------------------------------------------------------
raster_urls = {
    "Vacant Land Suitability (Salt Lake City)": 
        "https://raw.githubusercontent.com/AmesSky/Final_Viz_Suit/main/data/SLC_Suit_VC.tif",

    "Commercial/Industrial Suitability (Salt Lake City)": 
        "https://raw.githubusercontent.com/AmesSky/Final_Viz_Suit/main/data/SLC_Suit_CI.tif"
}

# ------------------------------------------------------------
# 2. User selects raster dataset
# ------------------------------------------------------------
selected_dataset = st.selectbox(
    "Select a suitability raster to explore:",
    list(raster_urls.keys())
)

raster_url = raster_urls[selected_dataset]

# ------------------------------------------------------------
# 3. Download raster to a temporary file (cached)
# ------------------------------------------------------------
@st.cache_data(show_spinner=True)
def download_raster(url):
    r = requests.get(url)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".tif")
    tmp.write(r.content)
    tmp.flush()
    return tmp.name

local_raster_path = download_raster(raster_url)

# ------------------------------------------------------------
# 4. Load raster
# ------------------------------------------------------------
with rasterio.open(local_raster_path) as src:
    raster = src.read(1).astype("float32")
    raster[raster == src.nodata] = np.nan

# ------------------------------------------------------------
# 5. Slider for filtering values
# ------------------------------------------------------------
min_val = int(np.nanmin(raster))
max_val = int(np.nanmax(raster))

selected_range = st.slider(
    "Filter suitability values:",
    min_value=min_val,
    max_value=max_val,
    value=(min_val, max_val)
)

raster_filtered = np.where((raster >= selected_range[0]) & 
                           (raster <= selected_range[1]), raster, np.nan)

# ------------------------------------------------------------
# 6. Visualization (Histogram + Map)
# ------------------------------------------------------------
col1, col2 = st.columns([1, 1])

# Histogram
with col1:
    st.subheader("Histogram of Suitability Values")
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.hist(raster_filtered[~np.isnan(raster_filtered)], bins=30)
    ax.set_title("Suitability Distribution")
    ax.set_xlabel("Suitability Score")
    ax.set_ylabel("Count")
    st.pyplot(fig)

# Map Viewer
with col2:
    st.subheader("Map Viewer")
    m = leafmap.Map(center=[40.75, -111.9], zoom=10)
    m.add_raster(
        local_raster_path,
        colormap="viridis",
        layer_name=selected_dataset
    )
    m.to_streamlit(height=500)

# Footer
st.markdown("""
---
### Instructions
- **Choose a dataset** from the drop-down menu  
- **Use the slider** to filter suitability values  
- **Explore the histogram** to understand distribution  
- **Pan/zoom the map** to find spatial patterns  
""")
