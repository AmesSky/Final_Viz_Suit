import streamlit as st
import leafmap.foliumap as leafmap
import numpy as np
import imageio.v3 as iio
import matplotlib.pyplot as plt

st.set_page_config(page_title="Salt Lake City Suitability Web App", layout="wide")

st.title("🏙️ Salt Lake City Vertiport Suitability Analysis")
st.write("Explore suitability raster layers using an interactive map and charts.")

# ---------------------------------------
# LOCAL RASTER FILES
# ---------------------------------------
raster_paths = {
    "Vacant Land Suitability": "SLC_Suit_VC.tif",
    "Commercial/Industrial Suitability": "SLC_Suit_CI.tif",
}


# ---------------------------------------
# Load raster
# ---------------------------------------
@st.cache_data
def load_tif(path):
    arr = iio.imread(path)
    return arr.astype(np.int32)


# ---------------------------------------
# Suitability value → color mapping
# ---------------------------------------
color_map = {
    1: "#BEBEBE",  # neutral (gray)
    2: "#FFD700",  # possible (gold)
    3: "#FF4500",  # unsuitable (orange-red)
    4: "#32CD32",  # suitable (green)
    5: "#FF0000",  # highly suitable (red)
}

label_map = {
    1: "neutral",
    2: "possible",
    3: "unsuitable",
    4: "suitable",
    5: "highly suitable",
}

# ---------------------------------------
# Sidebar selection
# ---------------------------------------
selected_layer = st.sidebar.selectbox("📂 Choose a raster layer", list(raster_paths.keys()))
raster_file = raster_paths[selected_layer]

# ---------------------------------------
# Load raster
# ---------------------------------------
arr = load_tif(raster_file)
unique_values = np.unique(arr)

st.subheader("Raster Summary")
col1, col2 = st.columns(2)
with col1:
    st.write("**Unique values found in raster:**", unique_values.tolist())
with col2:
    st.write(f"**Shape:** {arr.shape}")

# ---------------------------------------
# Build colored PNG for map overlay
# ---------------------------------------
def raster_to_rgb(raster):
    rgb = np.zeros((raster.shape[0], raster.shape[1], 3), dtype=np.uint8)
    for val, hex_color in color_map.items():
        mask = raster == val
        rgb[mask] = tuple(int(hex_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    return rgb


rgb_img = raster_to_rgb(arr)
iio.imwrite("colored_temp.png", rgb_img)


# ---------------------------------------
# Interactive Map
# ---------------------------------------
st.subheader("🗺️ Interactive Suitability Map")

m = leafmap.Map(center=[40.75, -111.9], zoom=11)

# Add basemap
m.add_basemap("CartoDB.Positron")

# Add raster overlay
m.add_image(
    "colored_temp.png",
    bounds=[[40.45, -112.2], [41.1, -111.6]],  # adjust if needed
    opacity=0.75,
    name=selected_layer,
)

m.to_streamlit(width=900, height=600)


# ---------------------------------------
# Legend
# ---------------------------------------
st.subheader("📌 Suitability Legend")

for val, label in label_map.items():
    st.markdown(
        f"<div style='display:flex;align-items:center;'>"
        f"<div style='width:20px;height:20px;background:{color_map[val]};"
        f"margin-right:10px;'></div> {val} – {label}</div>",
        unsafe_allow_html=True,
    )


# ---------------------------------------
# Histogram Section
# ---------------------------------------
st.subheader("📊 Suitability Value Histogram")

fig, ax = plt.subplots(figsize=(7, 4))
ax.hist(arr.flatten(), bins=range(1, 7), edgecolor="black", color="#4682B4")
ax.set_title("Distribution of Suitability Classes")
ax.set_xlabel("Suitability Class")
ax.set_ylabel("Frequency")
st.pyplot(fig)
