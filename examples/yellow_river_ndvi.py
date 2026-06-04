"""
示例任务2: 黄河流域近10年NDVI变化
使用 MODIS MOD13Q1 NDVI 产品 (250m, 16-day)
"""

import ee, geemap, pandas as pd, numpy as np, os

OUTPUT_DIR = "../GeoAgent_Output"
YELLOW_RIVER = ee.Geometry.Rectangle([95.0, 32.0, 119.0, 42.0])

for d in ["maps", "figures", "data"]:
    os.makedirs(f"{OUTPUT_DIR}/{d}", exist_ok=True)

try:
    ee.Initialize()
    print("GEE OK")
except:
    print("Please run: earthengine authenticate")
    exit(1)

print("Loading MODIS NDVI...")
modis = ee.ImageCollection("MODIS/061/MOD13Q1").filterDate("2015-01-01", "2025-12-31").filterBounds(YELLOW_RIVER).select(["NDVI", "EVI", "DetailedQA"])

def mask_qa(image):
    qa = image.select("DetailedQA")
    return image.updateMask(qa.bitwiseAnd(3).lte(1)).multiply(0.0001)
modis_clean = modis.map(mask_qa)
print(f"Images: {modis_clean.size().getInfo()}")

print("Computing annual NDVI...")
years = list(range(2015, 2026))
annual_results = []
for year in years:
    ndvi_year = modis_clean.filterDate(f"{year}-06-01", f"{year}-09-30").select("NDVI")
    mean_ndvi = ndvi_year.mean().reduceRegion(reducer=ee.Reducer.mean(), geometry=YELLOW_RIVER, scale=1000, maxPixels=1e13).get("NDVI").getInfo()
    max_ndvi = ndvi_year.max().reduceRegion(reducer=ee.Reducer.max(), geometry=YELLOW_RIVER, scale=1000, maxPixels=1e13).get("NDVI").getInfo()
    annual_results.append({"year": year, "NDVI_mean": round(mean_ndvi, 4), "NDVI_max": round(max_ndvi, 4)})
    print(f"  {year}: mean={mean_ndvi:.4f}, max={max_ndvi:.4f}")

df = pd.DataFrame(annual_results)
df.to_csv(f"{OUTPUT_DIR}/data/yellow_river_ndvi.csv", index=False)

z_mean = np.polyfit(df["year"], df["NDVI_mean"], 1)
change_mean = df["NDVI_mean"].iloc[-1] - df["NDVI_mean"].iloc[0]
print(f"NDVI trend: {z_mean[0]:.5f}/yr (total change: {change_mean:+.4f})")
if change_mean > 0:
    print("🌿 Vegetation improving!")
else:
    print("⚠️ Vegetation degrading!")

import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

fig, axes = plt.subplots(2, 1, figsize=(12, 10))
for ax, col, color in zip(axes, ["NDVI_mean", "NDVI_max"], ["#4CAF50", "#2196F3"]):
    ax.plot(df["year"], df[col], "o-", color=color, linewidth=2.5, markersize=10)
    ax.fill_between(df["year"], df[col], alpha=0.2, color=color)
    z = np.polyfit(df["year"], df[col], 1)
    p = np.poly1d(z)
    ax.plot(df["year"], p(df["year"]), "--", color="#F44336", linewidth=2, label=f"Trend ({z[0]:.5f}/yr)")
    ax.set_xlabel("Year"); ax.set_ylabel("NDVI")
    ax.set_title(f"Yellow River Basin {col} (2015-2025)", fontsize=14, fontweight="bold")
    ax.grid(True, alpha=0.3); ax.legend()
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/figures/yellow_river_ndvi_trend.png", dpi=150, bbox_inches="tight")
plt.close()

print("Generating map...")
Map = geemap.Map(center=[37.0, 110.0], zoom=5)
Map.add_basemap("SATELLITE")
ndvi_viz = {"min": 0.0, "max": 0.9, "palette": ["#8B0000", "#FF0000", "#FF8C00", "#FFD700", "#ADFF2F", "#006400", "#000080"]}
Map.addLayer(modis_clean.select("NDVI").mean().clip(YELLOW_RIVER), ndvi_viz, "NDVI Mean (2015-2025)")
Map.addLayerControl()
Map.to_html(f"{OUTPUT_DIR}/maps/yellow_river_ndvi.html")

print("\nDone! Output: " + OUTPUT_DIR)
