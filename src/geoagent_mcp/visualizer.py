"""
可视化模块 - 自动生成交互式地图与静态图表
"""

import os
from pathlib import Path
from datetime import datetime

OUTPUT_DIR = Path(__file__).parent.parent.parent / "GeoAgent_Output"


def generate_interactive_map(
    center: tuple = (35.0, 105.0), zoom: int = 5,
    layers: list = None, title: str = "GeoAgent Analysis Map",
    output_path: str = None
) -> str:
    """生成交互式 HTML 地图"""
    import folium

    if output_path is None:
        output_path = OUTPUT_DIR / "maps" / f"map_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    os.makedirs(Path(output_path).parent, exist_ok=True)

    m = folium.Map(location=list(center), zoom_start=zoom, tiles="OpenStreetMap")

    if layers:
        for layer in layers:
            name = layer.get("name", "Layer")
            ltype = layer.get("type", "")
            if ltype == "geojson" and layer.get("data"):
                folium.GeoJson(layer["data"], name=name,
                    style_function=lambda x: {"fillColor": "#2196F3", "color": "#1976D2", "weight": 2, "fillOpacity": 0.3}).add_to(m)
            elif ltype == "marker" and layer.get("data"):
                for pt in (layer["data"] if isinstance(layer["data"], list) else [layer["data"]]):
                    folium.Marker(location=[pt.get("lat", 0), pt.get("lon", 0)], popup=pt.get("label", "")).add_to(m)

    folium.LayerControl().add_to(m)
    title_html = f'<h3 style="text-align:center;margin-top:10px;"><b>{title}</b></h3>'
    m.get_root().html.add_child(folium.Element(title_html))
    m.save(str(output_path))
    return str(output_path)


def generate_time_series_chart(
    data, x_key: str = "year", y_keys: list = None,
    title: str = "Time Series Analysis", xlabel: str = "Year", ylabel: str = "Value",
    output_path: str = None
) -> str:
    """生成时间序列统计图"""
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np

    if output_path is None:
        output_path = OUTPUT_DIR / "figures" / f"chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    os.makedirs(Path(output_path).parent, exist_ok=True)

    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False

    import pandas as pd
    df = pd.DataFrame(data) if isinstance(data, dict) else data
    if y_keys is None:
        y_keys = [c for c in df.columns if c != x_key]

    n_plots = len(y_keys)
    fig, axes = plt.subplots(n_plots, 1, figsize=(12, 4 * n_plots))
    if n_plots == 1:
        axes = [axes]

    for ax, col in zip(axes, y_keys):
        if col in df.columns:
            x_vals = df[x_key].values
            y_vals = df[col].values
            ax.plot(x_vals, y_vals, "o-", color="#2196F3", linewidth=2, markersize=8)
            ax.fill_between(x_vals, y_vals, alpha=0.2, color="#2196F3")
            ax.set_xlabel(xlabel, fontsize=12); ax.set_ylabel(col, fontsize=12)
            ax.set_title(f"{title} - {col}", fontsize=14, fontweight="bold")
            ax.grid(True, alpha=0.3)
            mask = ~np.isnan(y_vals)
            if mask.sum() >= 2:
                z = np.polyfit(x_vals[mask], y_vals[mask], 1)
                p = np.poly1d(z)
                ax.plot(x_vals, p(x_vals), "--", color="#FF5722", linewidth=1, label=f"Trend (slope={z[0]:.4f}/yr)")
                ax.legend()

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    return str(output_path)


def generate_classification_map(
    data: list, labels: list, colors: list = None,
    title: str = "Land Cover Classification", output_path: str = None
) -> str:
    """生成分类统计饼图/柱状图"""
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    if output_path is None:
        output_path = OUTPUT_DIR / "figures" / f"classification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    os.makedirs(Path(output_path).parent, exist_ok=True)

    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False

    if colors is None:
        colors = plt.cm.Set3(range(len(data)))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    ax1.pie(data, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
    ax1.set_title(f"{title} - 面积占比", fontsize=13, fontweight="bold")

    bars = ax2.bar(range(len(data)), data, color=colors)
    ax2.set_xticks(range(len(data)))
    ax2.set_xticklabels(labels, rotation=45, ha="right")
    ax2.set_ylabel("Area (km²)", fontsize=12)
    ax2.set_title(f"{title} - 面积统计", fontsize=13, fontweight="bold")
    for bar, val in zip(bars, data):
        ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height(), f'{val:.1f}', ha='center', va='bottom', fontsize=10)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    return str(output_path)
