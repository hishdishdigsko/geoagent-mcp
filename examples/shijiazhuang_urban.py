"""
示例任务1: 分析石家庄2015-2025城市扩张
使用 Dynamic World + Sentinel-2 数据，计算 NDBI 追踪城市扩张
"""

import ee, geemap, pandas as pd, numpy as np, os

OUTPUT_DIR = "../GeoAgent_Output"
SHIJIAZHUANG = ee.Geometry.Rectangle([113.5, 37.5, 115.0, 38.8])

os.makedirs(f"{OUTPUT_DIR}/maps", exist_ok=True)
os.makedirs(f"{OUTPUT_DIR}/figures", exist_ok=True)
os.makedirs(f"{OUTPUT_DIR}/data", exist_ok=True)

try:
    ee.Initialize()
    print("GEE OK")
except:
    print("Please run: earthengine authenticate")
    exit(1)

print("Loading Dynamic World...")
dw = ee.ImageCollection("GOOGLE/DYNAMICWORLD/V1").filterDate("2015-01-01", "2025-12-31").filterBounds(SHIJIAZHUANG)
dw_built_mean_2015 = dw.select("built").filterDate("2015-01-01", "2015-12-31").mean()
dw_built_mean_2025 = dw.select("built").filterDate("2025-01-01", "2025-12-31").mean()

print("Loading Sentinel-2...")
def mask_s2_clouds(image):
    qa = image.select("QA60")
    mask = qa.bitwiseAnd(1 << 10).eq(0).And(qa.bitwiseAnd(1 << 11).eq(0))
    return image.updateMask(mask).divide(10000)

def calc_ndbi(image):
    return image.expression("(SWIR - NIR) / (SWIR + NIR)", {"SWIR": image.select("B11"), "NIR": image.select("B8")}).rename("NDBI")

s2 = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED").filterDate("2015-01-01", "2025-12-31").filterBounds(SHIJIAZHUANG).filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 30)).map(mask_s2_clouds)
s2_ndbi = s2.map(calc_ndbi)
print(f"S2 images: {s2.size().getInfo()}")

print("Computing annual NDBI...")
years = list(range(2015, 2026))
annual_ndbi = []
for year in years:
    ndbi_year = s2_ndbi.filterDate(f"{year}-06-01", f"{year}-09-30").mean()
    mean_val = ndbi_year.reduceRegion(reducer=ee.Reducer.mean(), geometry=SHIJIAZHUANG, scale=100, maxPixels=1e13).get("NDBI").getInfo()
    annual_ndbi.append({"year": year, "NDBI_mean": mean_val})
    print(f"  {year}: NDBI = {mean_val:.4f}")

df = pd.DataFrame(annual_ndbi)
df.to_csv(f"{OUTPUT_DIR}/data/shijiazhuang_ndbi.csv", index=False)

import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(df["year"], df["NDBI_mean"], "o-", color="#FF5722", linewidth=2.5, markersize=10)
ax.fill_between(df["year"], df["NDBI_mean"], alpha=0.2, color="#FF5722")
z = np.polyfit(df["year"], df["NDBI_mean"], 1)
p = np.poly1d(z)
ax.plot(df["year"], p(df["year"]), "--", color="#1976D2", linewidth=2, label=f"Trend (slope={z[0]:.5f}/yr)")
ax.set_xlabel("Year"); ax.set_ylabel("NDBI")
ax.set_title("Shijiazhuang NDBI Trend (2015-2025)", fontsize=15, fontweight="bold")
ax.grid(True, alpha=0.3); ax.legend(fontsize=12)
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/figures/shijiazhuang_ndbi_trend.png", dpi=150, bbox_inches="tight")
plt.close()

print("Estimating built-up area...")
built_2015 = dw_built_mean_2015.gt(0.5).selfMask()
built_2025 = dw_built_mean_2025.gt(0.5).selfMask()
area_2015 = built_2015.multiply(ee.Image.pixelArea()).reduceRegion(reducer=ee.Reducer.sum(), geometry=SHIJIAZHUANG, scale=100, maxPixels=1e13).get("built").getInfo() / 1e6
area_2025 = built_2025.multiply(ee.Image.pixelArea()).reduceRegion(reducer=ee.Reducer.sum(), geometry=SHIJIAZHUANG, scale=100, maxPixels=1e13).get("built").getInfo() / 1e6
print(f"  2015: {area_2015:.1f} km2, 2025: {area_2025:.1f} km2, Expansion: {area_2025-area_2015:.1f} km2 ({(area_2025/area_2015-1)*100:.1f}%)")

print("Generating map...")
Map = geemap.Map(center=[38.05, 114.5], zoom=9)
Map.add_basemap("SATELLITE")
ndbi_viz = {"min": -0.3, "max": 0.3, "palette": ["green", "yellow", "red", "gray"]}
Map.addLayer(s2_ndbi.filterDate("2015-06-01", "2015-09-30").mean().clip(SHIJIAZHUANG), ndbi_viz, "NDBI 2015")
Map.addLayer(s2_ndbi.filterDate("2025-06-01", "2025-09-30").mean().clip(SHIJIAZHUANG), ndbi_viz, "NDBI 2025")
Map.addLayerControl()
Map.to_html(f"{OUTPUT_DIR}/maps/shijiazhuang_urban_expansion.html")

print("\nDone! Output: " + OUTPUT_DIR)
