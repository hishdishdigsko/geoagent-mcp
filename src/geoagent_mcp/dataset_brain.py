"""
Dataset Brain - 任务类型 → 最优 GEE 数据集 知识库

维护内置知识库，将用户任务类型映射到最优 GEE 数据集。
支持中文关键词自动匹配。
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
import json
from pathlib import Path


@dataclass
class DatasetInfo:
    """GEE 数据集信息"""
    name: str
    ee_id: str
    resolution: str
    temporal_range: str
    bands: List[str] = field(default_factory=list)
    description: str = ""
    provider: str = ""
    usage_notes: str = ""


DATASET_KNOWLEDGE_BASE: Dict[str, List[DatasetInfo]] = {
    "城市扩张": [
        DatasetInfo(
            name="Dynamic World V1",
            ee_id="GOOGLE/DYNAMICWORLD/V1",
            resolution="10m",
            temporal_range="2015-06 至今",
            bands=["label", "water", "trees", "grass", "flooded_vegetation", "crops",
                    "shrub_and_scrub", "built", "bare", "snow_and_ice"],
            description="Google 与 WRI 联合推出的 10m 全球土地利用分类数据集",
            provider="Google / WRI",
            usage_notes="适合快速土地利用分类，直接获取 built 类别"
        ),
        DatasetInfo(
            name="Sentinel-2 MSI Level-2A",
            ee_id="COPERNICUS/S2_SR_HARMONIZED",
            resolution="10-20m",
            temporal_range="2017-03 至今",
            bands=["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B8A", "B9", "B11", "B12"],
            description="欧空局 Sentinel-2 地表反射率数据",
            provider="ESA",
            usage_notes="10m 分辨率，适合精细城市边界提取"
        ),
        DatasetInfo(
            name="Landsat 8 Collection 2 Level-2",
            ee_id="LANDSAT/LC08/C02/T1_L2",
            resolution="30m",
            temporal_range="2013-04 至今",
            bands=["SR_B1", "SR_B2", "SR_B3", "SR_B4", "SR_B5", "SR_B6", "SR_B7",
                    "ST_B10", "SR_QA_AEROSOL"],
            description="USGS Landsat 8 地表反射率数据",
            provider="USGS/NASA",
            usage_notes="30m，历史存档丰富，适合长时间序列分析"
        ),
        DatasetInfo(
            name="World Settlement Footprint",
            ee_id="DLR/WSF/WSF2015/v1",
            resolution="10m",
            temporal_range="2015",
            bands=["settlement"],
            description="德国宇航中心全球建成区数据(2015)",
            provider="DLR",
            usage_notes="直接提供建成区掩膜，适合对比验证"
        ),
    ],
    "森林变化": [
        DatasetInfo(
            name="Global Forest Change",
            ee_id="UMD/hansen/global_forest_change_2023_v1_11",
            resolution="30m",
            temporal_range="2000-2023",
            bands=["treecover2000", "loss", "gain", "lossyear"],
            description="Hansen 全球森林变化数据集（马里兰大学）",
            provider="UMD / Google",
            usage_notes="最权威的森林变化数据，年度更新"
        ),
        DatasetInfo(
            name="Sentinel-2 MSI",
            ee_id="COPERNICUS/S2_SR_HARMONIZED",
            resolution="10m",
            temporal_range="2017-03 至今",
            bands=["B2", "B3", "B4", "B8", "B11", "B12"],
            description="用于计算 NDVI/NBR 等植被指数监测森林健康",
            provider="ESA",
            usage_notes="适合森林健康监测与火灾评估"
        ),
        DatasetInfo(
            name="MODIS Vegetation Indices 16-Day",
            ee_id="MODIS/061/MOD13Q1",
            resolution="250m",
            temporal_range="2000-02 至今",
            bands=["NDVI", "EVI", "DetailedQA"],
            description="MODIS 16天合成植被指数产品",
            provider="NASA LP DAAC",
            usage_notes="适合大尺度长时间序列植被监测"
        ),
    ],
    "土地利用": [
        DatasetInfo(
            name="ESA WorldCover",
            ee_id="ESA/WorldCover/v200",
            resolution="10m",
            temporal_range="2020-2021",
            bands=["Map"],
            description="ESA 全球 10m 土地覆盖产品",
            provider="ESA",
            usage_notes="11类土地覆盖，精度高"
        ),
        DatasetInfo(
            name="Dynamic World V1",
            ee_id="GOOGLE/DYNAMICWORLD/V1",
            resolution="10m",
            temporal_range="2015-06 至今",
            bands=["label"],
            description="Google 10m 近实时土地利用",
            provider="Google / WRI",
            usage_notes="9类土地覆盖，时间序列完整"
        ),
        DatasetInfo(
            name="MODIS Land Cover Type (MCD12Q1)",
            ee_id="MODIS/061/MCD12Q1",
            resolution="500m",
            temporal_range="2001-2022",
            bands=["LC_Type1"],
            description="MODIS 年度全球土地覆盖分类",
            provider="NASA LP DAAC",
            usage_notes="适合全球尺度多年变化分析"
        ),
    ],
    "水体变化": [
        DatasetInfo(
            name="Global Surface Water",
            ee_id="JRC/GSW1_4/GlobalSurfaceWater",
            resolution="30m",
            temporal_range="1984-2021",
            bands=["occurrence", "change_abs", "change_norm", "seasonality", "max_extent"],
            description="JRC 全球地表水数据集",
            provider="EC JRC / Google",
            usage_notes="最完整的地表水变化数据，38年跨度"
        ),
        DatasetInfo(
            name="Sentinel-2 (水体指数)",
            ee_id="COPERNICUS/S2_SR_HARMONIZED",
            resolution="10m",
            temporal_range="2017-03 至今",
            bands=["B3", "B8", "B11", "B12"],
            description="可用于计算 NDWI/MNDWI 水体指数",
            provider="ESA",
            usage_notes="适合精细水体提取"
        ),
    ],
    "植被指数": [
        DatasetInfo(
            name="MODIS NDVI/EVI (MOD13Q1)",
            ee_id="MODIS/061/MOD13Q1",
            resolution="250m",
            temporal_range="2000-02 至今",
            bands=["NDVI", "EVI", "DetailedQA"],
            description="MODIS 16天 NDVI/EVI 产品",
            provider="NASA LP DAAC",
            usage_notes="最常用的植被指数产品，支持长时间序列"
        ),
        DatasetInfo(
            name="Sentinel-2 (NDVI)",
            ee_id="COPERNICUS/S2_SR_HARMONIZED",
            resolution="10m",
            temporal_range="2017-03 至今",
            bands=["B4", "B8", "B2"],
            description="高分辨率 NDVI 计算底图",
            provider="ESA",
            usage_notes="10m NDVI，适合精细农业与植被监测"
        ),
        DatasetInfo(
            name="Landsat 8 (NDVI)",
            ee_id="LANDSAT/LC08/C02/T1_L2",
            resolution="30m",
            temporal_range="2013-04 至今",
            bands=["SR_B4", "SR_B5"],
            description="Landsat 8 NDVI 计算底图",
            provider="USGS/NASA",
            usage_notes="适合 2013 年以来的 NDVI 时间序列"
        ),
    ],
    "夜光分析": [
        DatasetInfo(
            name="VIIRS Nighttime Day/Night Band",
            ee_id="NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG",
            resolution="500m",
            temporal_range="2012-04 至今",
            bands=["avg_rad", "cf_cvg", "cvg"],
            description="VIIRS 夜间灯光月合成产品",
            provider="NOAA",
            usage_notes="适合城市扩张、经济活动评估"
        ),
        DatasetInfo(
            name="DMSP-OLS Nighttime Lights",
            ee_id="NOAA/DMSP-OLS/NIGHTTIME_LIGHTS/F182013",
            resolution="1km",
            temporal_range="1992-2013",
            bands=["stable_lights", "avg_vis", "cf_cvg"],
            description="DMSP-OLS 年度夜间灯光数据",
            provider="NOAA",
            usage_notes="适合历史夜光分析（1992-2013）"
        ),
    ],
    "光伏选址": [
        DatasetInfo(
            name="ERA5-Land Solar Radiation",
            ee_id="ECMWF/ERA5_LAND/HOURLY",
            resolution="~11km",
            temporal_range="1950 至今",
            bands=["surface_solar_radiation_downwards"],
            description="ERA5-Land 太阳辐射数据",
            provider="ECMWF",
            usage_notes="适合大尺度太阳能评估"
        ),
        DatasetInfo(
            name="MODIS Land Surface Temperature",
            ee_id="MODIS/061/MOD11A1",
            resolution="1km",
            temporal_range="2000-02 至今",
            bands=["LST_Day_1km", "LST_Night_1km"],
            description="MODIS 地表温度数据",
            provider="NASA LP DAAC",
            usage_notes="辅助光伏选址地温分析"
        ),
    ],
    "洪水监测": [
        DatasetInfo(
            name="Sentinel-1 SAR GRD",
            ee_id="COPERNICUS/S1_GRD",
            resolution="10m",
            temporal_range="2014-10 至今",
            bands=["VV", "VH", "HH", "HV", "angle"],
            description="Sentinel-1 合成孔径雷达数据",
            provider="ESA",
            usage_notes="SAR 穿透云层，洪水监测首选"
        ),
        DatasetInfo(
            name="Global Surface Water",
            ee_id="JRC/GSW1_4/GlobalSurfaceWater",
            resolution="30m",
            temporal_range="1984-2021",
            bands=["occurrence", "max_extent"],
            description="历史地表水范围参考",
            provider="EC JRC",
            usage_notes="洪水事件的历史基线参考"
        ),
    ],
    "地表温度": [
        DatasetInfo(
            name="MODIS LST (MOD11A1)",
            ee_id="MODIS/061/MOD11A1",
            resolution="1km",
            temporal_range="2000-02 至今",
            bands=["LST_Day_1km", "LST_Night_1km"],
            description="MODIS 每日地表温度",
            provider="NASA LP DAAC",
            usage_notes="热岛效应分析首选"
        ),
        DatasetInfo(
            name="Landsat 8 Thermal Band",
            ee_id="LANDSAT/LC08/C02/T1_L2",
            resolution="100m (热红外)",
            temporal_range="2013-04 至今",
            bands=["ST_B10"],
            description="Landsat 8 热红外波段",
            provider="USGS/NASA",
            usage_notes="城市热岛精细分析"
        ),
    ],
    "地形分析": [
        DatasetInfo(
            name="SRTM Digital Elevation 30m",
            ee_id="USGS/SRTMGL1_003",
            resolution="30m",
            temporal_range="2000 (固定)",
            bands=["elevation", "slope", "aspect"],
            description="NASA SRTM 30m DEM",
            provider="NASA / USGS",
            usage_notes="最常用 DEM 数据"
        ),
        DatasetInfo(
            name="ALOS DSM 30m",
            ee_id="JAXA/ALOS/AW3D30/V3_2",
            resolution="30m",
            temporal_range="2006-2011 (固定)",
            bands=["DSM"],
            description="JAXA ALOS 全球 DSM",
            provider="JAXA",
            usage_notes="精度优于 SRTM 部分地区"
        ),
    ],
}

INDEX_FORMULAS = {
    "NDVI": {
        "formula": "(NIR - RED) / (NIR + RED)",
        "description": "归一化植被指数",
        "sentinel2": "B8=NIR, B4=RED",
        "landsat8": "B5=NIR, B4=RED",
        "modis": "B2=NIR, B1=RED",
        "value_range": "-1 到 1，植被 > 0.2",
    },
    "EVI": {
        "formula": "2.5 * (NIR - RED) / (NIR + 6*RED - 7.5*BLUE + 1)",
        "description": "增强植被指数（减少大气影响）",
        "sentinel2": "B8=NIR, B4=RED, B2=BLUE",
        "value_range": "-1 到 1",
    },
    "NDWI": {
        "formula": "(GREEN - NIR) / (GREEN + NIR)",
        "description": "归一化水体指数",
        "sentinel2": "B3=GREEN, B8=NIR",
        "landsat8": "B3=GREEN, B5=NIR",
        "value_range": "-1 到 1，水体 > 0",
    },
    "MNDWI": {
        "formula": "(GREEN - SWIR) / (GREEN + SWIR)",
        "description": "改进归一化水体指数",
        "sentinel2": "B3=GREEN, B11=SWIR1",
        "landsat8": "B3=GREEN, B6=SWIR1",
        "value_range": "-1 到 1，水体 > 0（比 NDWI 更准确）",
    },
    "NBR": {
        "formula": "(NIR - SWIR2) / (NIR + SWIR2)",
        "description": "归一化燃烧比（火灾评估）",
        "sentinel2": "B8=NIR, B12=SWIR2",
        "landsat8": "B5=NIR, B7=SWIR2",
        "value_range": "-1 到 1，烧伤区域 < 0",
    },
    "NDBI": {
        "formula": "(SWIR - NIR) / (SWIR + NIR)",
        "description": "归一化建筑指数",
        "sentinel2": "B11=SWIR1, B8=NIR",
        "landsat8": "B6=SWIR1, B5=NIR",
        "value_range": "-1 到 1，建成区 > 0",
    },
    "SAVI": {
        "formula": "(NIR - RED) * (1 + L) / (NIR + RED + L), L=0.5",
        "description": "土壤调节植被指数（减少土壤背景影响）",
        "value_range": "-1 到 1",
    },
}

TASK_KEYWORDS = {
    "城市扩张": ["城市", "扩张", "建成区", "城市化", "建设用地", "城镇", "urban"],
    "森林变化": ["森林", "林地", "毁林", "造林", "砍伐", "forest", "deforestation"],
    "土地利用": ["土地", "地表覆盖", "地类", "覆盖类型", "land use", "land cover", "lulc"],
    "水体变化": ["水体", "水域", "湖泊", "水库", "water", "lake", "reservoir"],
    "植被指数": ["植被", "NDVI", "EVI", "绿度", "vegetation", "greening"],
    "夜光分析": ["夜光", "夜间灯光", "灯光", "nighttime", "viirs", "dmsp", "npp"],
    "光伏选址": ["光伏", "太阳能", "光伏电站", "solar", "photovoltaic", "pv"],
    "洪水监测": ["洪水", "洪涝", "淹没", "flood", "inundation"],
    "地表温度": ["温度", "热岛", "地表温度", "LST", "temperature", "heat island"],
    "地形分析": ["地形", "高程", "DEM", "坡度", "坡向", "elevation", "slope"],
}


def search_dataset(task_type: str) -> dict:
    """根据任务类型搜索最优 GEE 数据集"""
    task_lower = task_type.lower()
    matched_category = None
    best_score = 0

    for category, keywords in TASK_KEYWORDS.items():
        score = 0
        for kw in keywords:
            if kw.lower() in task_lower:
                score += len(kw)
        if score > best_score:
            best_score = score
            matched_category = category

    if not matched_category:
        return {
            "task_type": task_type,
            "matched_category": None,
            "datasets": [],
            "recommended_indices": [],
            "tips": f"未找到匹配的任务类型。支持的类型: {', '.join(TASK_KEYWORDS.keys())}"
        }

    datasets = DATASET_KNOWLEDGE_BASE.get(matched_category, [])

    index_recommendations = {
        "城市扩张": ["NDBI", "NDVI", "NDWI"],
        "森林变化": ["NDVI", "NBR", "EVI"],
        "土地利用": ["NDVI"],
        "水体变化": ["NDWI", "MNDWI"],
        "植被指数": ["NDVI", "EVI", "SAVI"],
        "夜光分析": [],
        "光伏选址": ["NDVI"],
        "洪水监测": ["MNDWI", "NDWI"],
        "地表温度": ["NDVI"],
        "地形分析": [],
    }

    tips_map = {
        "城市扩张": "建议先用 Dynamic World 快速提取建成区，再用 Landsat 长时间序列计算 NDBI 进行变化分析",
        "森林变化": "建议先用 Hansen GFC 获取森林变化基线，再结合 Sentinel-2 NDVI 做精细化分析",
        "植被指数": "MODIS 适合大尺度长时序（2000-至今），Sentinel-2 适合 2017 年后的精细分析",
        "水体变化": "JRC GSW 已提供完整水体变化信息，可直接使用；Sentinel-1 SAR 适合洪水期间实时监测",
    }

    return {
        "task_type": task_type,
        "matched_category": matched_category,
        "datasets": [
            {
                "name": d.name,
                "ee_id": d.ee_id,
                "resolution": d.resolution,
                "temporal_range": d.temporal_range,
                "bands": d.bands,
                "description": d.description,
                "provider": d.provider,
                "usage_notes": d.usage_notes,
            }
            for d in datasets
        ],
        "recommended_indices": index_recommendations.get(matched_category, []),
        "tips": tips_map.get(matched_category, "根据需求选择合适的空间分辨率与时间范围")
    }


def list_all_categories() -> List[str]:
    """列出所有支持的任务类别"""
    return list(TASK_KEYWORDS.keys())


def get_index_info(index_name: str) -> Optional[dict]:
    """获取指定指数的详细信息"""
    return INDEX_FORMULAS.get(index_name.upper())
