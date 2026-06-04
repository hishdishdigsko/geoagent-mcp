"""
分析执行模块 - 自动生成并运行 GEE Python 脚本
"""

import subprocess, sys, os, json, tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from .dataset_brain import INDEX_FORMULAS

OUTPUT_DIR = Path(__file__).parent.parent.parent / "GeoAgent_Output"


def generate_script(workflow, output_dir: Path = None) -> str:
    """根据工作流生成完整的 GEE Python 可执行脚本"""
    if output_dir is None:
        output_dir = OUTPUT_DIR

    idx = workflow.indices or ["NDVI"]
    ds = workflow.datasets[0] if workflow.datasets else {"ee_id": "COPERNICUS/S2_SR_HARMONIZED", "name": "Sentinel-2"}
    roi = workflow.region_of_interest
    t0, t1 = workflow.time_start, workflow.time_end

    script = f'''"""
GeoAgent MCP - 自动生成分析脚本
任务: {workflow.title}
生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

import ee, geemap, geopandas as gpd, pandas as pd, numpy as np, os
from datetime import datetime
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUTPUT_DIR = r"{output_dir.absolute()}"
for d in ["maps", "figures", "data"]:
    os.makedirs(OUTPUT_DIR + "/" + d, exist_ok=True)

REGION_NAME = "{roi}"
TIME_START = "{t0}-01-01"
TIME_END = "{t1}-12-31"

try:
    ee.Initialize()
    print("GEE OK")
except Exception as e:
    print(f"GEE Error: {{e}}")
    exit(1)

print(f"Loading {ds.get('name', 'Dataset')}...")
collection = ee.ImageCollection("{ds['ee_id']}").filterDate(TIME_START, TIME_END)
'''

    if "COPERNICUS" in ds["ee_id"] or "S2" in ds["ee_id"]:
        script += '''
def mask_s2_clouds(image):
    qa = image.select("QA60")
    cloud_bit_mask = 1 << 10
    cirrus_bit_mask = 1 << 11
    mask = qa.bitwiseAnd(cloud_bit_mask).eq(0)\
        .And(qa.bitwiseAnd(cirrus_bit_mask).eq(0))
    return image.updateMask(mask).divide(10000)
collection = collection.map(mask_s2_clouds)
print("Cloud masked")
'''

    for index_name in idx:
        info = INDEX_FORMULAS.get(index_name, {})
        if info:
            script += f'''
def calc_{index_name.lower()}(image):
    return image.expression(
        "{info.get("formula", "")}",
        {{"NIR": image.select("B8"), "RED": image.select("B4"),
         "BLUE": image.select("B2"), "GREEN": image.select("B3"),
         "SWIR": image.select("B11"), "SWIR1": image.select("B11"),
         "SWIR2": image.select("B12")}}
    ).rename("{index_name}")
'''

    script += f'''
roi = collection.first().geometry()
print(f"ROI: {{REGION_NAME}}")

years = list(range({t0}, {t1} + 1))
annual_means = []

for year in years:
    yearly = collection.filterDate(f"{{year}}-06-01", f"{{year}}-09-30")
'''
    for idxn in idx:
        script += f'    {idxn.lower()}_mean = yearly.map(calc_{idxn.lower()}).mean()\n'

    script += '''
    annual_means.append({"year": year,
'''
    for idxn in idx:
        script += f'        "{idxn}_mean": {idxn.lower()}_mean.reduceRegion(\n            reducer=ee.Reducer.mean(), geometry=roi, scale=100, maxPixels=1e13\n        ).get("{idxn}").getInfo(),\n'
    script += '    })\n    print(f"    {year} OK")\n\n'

    script += '''
df = pd.DataFrame(annual_means)
print(df.to_string())
df.to_csv(OUTPUT_DIR + "/data/time_series.csv", index=False)

fig, ax = plt.subplots(figsize=(12, 6))
'''
    for idxn in idx:
        script += f'''
ax.plot(df["year"], df["{idxn}_mean"], "o-", label="{idxn}")
'''
    script += '''
ax.set_xlabel("Year"); ax.set_ylabel("Value")
ax.set_title(f"{REGION_NAME} Time Series ({t0}-{t1})")
ax.grid(True, alpha=0.3); ax.legend()
plt.tight_layout()
plt.savefig(OUTPUT_DIR + "/figures/trend.png", dpi=150)
plt.close()

print("Generating map...")
Map = geemap.Map()
Map.add_basemap("SATELLITE")
Map.centerObject(roi, 8)
'''
    for idxn in idx:
        viz_str = '{"min": -0.2, "max": 0.8, "palette": ["red", "yellow", "green"]}'
        script += f'''
Map.addLayer(collection.map(calc_{idxn.lower()}).mean().clip(roi), {viz_str}, "{idxn} ({t0}-{t1})")
'''
    script += '''
Map.addLayerControl()
Map.to_html(OUTPUT_DIR + "/maps/analysis_result.html")

print("\nAnalysis Complete!")
print(f"Output: {OUTPUT_DIR}")
'''
    return script


def execute_script(script: str, timeout: int = 600) -> Dict[str, Any]:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
        f.write(script)
        script_path = f.name
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True, text=True, timeout=timeout,
            cwd=str(OUTPUT_DIR.parent)
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout, "stderr": result.stderr,
            "exit_code": result.returncode, "script_path": script_path
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "stdout": "", "stderr": f"Timeout ({timeout}s)", "exit_code": -1, "script_path": script_path}
    except Exception as e:
        return {"success": False, "stdout": "", "stderr": str(e), "exit_code": -1, "script_path": script_path}


def execute_analysis(workflow, output_dir: Path = None) -> Dict[str, Any]:
    script = generate_script(workflow, output_dir)
    return execute_script(script)


def batch_execute(workflows: list) -> list:
    results = []
    for i, wf in enumerate(workflows):
        print(f"\nTask {i+1}/{len(workflows)}: {wf.title}")
        results.append(execute_analysis(wf))
    return results
