"""
Workflow Planner - 将自然语言任务解析为 GEE 分析流程
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
import re
from datetime import datetime

from .dataset_brain import search_dataset, INDEX_FORMULAS


@dataclass
class WorkflowStep:
    step_id: int
    step_type: str
    description: str
    ee_code_snippet: str = ""
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalysisWorkflow:
    title: str
    task_type: str
    description: str
    region_of_interest: str
    time_start: str
    time_end: str
    datasets: List[Dict] = field(default_factory=list)
    indices: List[str] = field(default_factory=list)
    steps: List[WorkflowStep] = field(default_factory=list)
    output_format: List[str] = field(default_factory=lambda: ["html", "png", "csv"])
    cloud_mask: bool = True


def extract_time_range(text: str) -> tuple:
    current_year = datetime.now().year
    range_pattern = r'(\d{4})\s*[-到至]\s*(\d{4})'
    m = re.search(range_pattern, text)
    if m:
        return m.group(1), m.group(2)
    recent_pattern = r'(?:近|过去|最近)(\d+)年'
    m = re.search(recent_pattern, text)
    if m:
        n = int(m.group(1))
        return str(current_year - n), str(current_year)
    single_year = re.search(r'(\d{4})年', text)
    if single_year:
        y = single_year.group(1)
        return y, y
    return str(current_year - 5), str(current_year)


def extract_region(text: str) -> str:
    VERB_PREFIXES = ['分析', '统计', '研究', '评估', '计算', '查看', '监测']
    NOUN_SUFFIXES = ['市', '省', '县', '区', '镇', '村', '流域', '盆地', '三角洲', '平原', '高原', '沙漠']

    m = re.search(r'([一-鿿]{2,8}(?:' + '|'.join(NOUN_SUFFIXES) + '))', text)
    if m:
        return m.group(1)

    for vp in VERB_PREFIXES:
        if vp in text:
            idx = text.index(vp) + len(vp)
            rest = text[idx:]
            m = re.search(r'([一-鿿]{2,6})', rest)
            if m and m.group(1) not in VERB_PREFIXES:
                return m.group(1)

    m = re.search(r'([一-鿿]{2,4})\d{4}', text)
    if m and m.group(1) not in VERB_PREFIXES:
        return m.group(1)

    m = re.search(r'([一-鿿]{2,4})(?:的|近|在|城市|森林|土地|水体|植被|洪水|变化|扩张|趋势)', text)
    if m:
        return m.group(1)

    m = re.search(r'([一-鿿]{2,4})', text)
    if m and m.group(1) not in VERB_PREFIXES:
        return m.group(1)

    return ""


def generate_workflow(user_query: str, geojson_path: str = None) -> AnalysisWorkflow:
    dataset_result = search_dataset(user_query)
    task_type = dataset_result["matched_category"] or "通用分析"
    time_start, time_end = extract_time_range(user_query)
    region = extract_region(user_query) or "研究区域"

    needed_indices = []
    query_upper = user_query.upper()
    for idx_name in ["NDVI", "EVI", "NDWI", "MNDWI", "NDBI", "NBR", "SAVI"]:
        if idx_name in query_upper:
            needed_indices.append(idx_name)
    if not needed_indices:
        needed_indices = dataset_result.get("recommended_indices", ["NDVI"])[:2]

    datasets = dataset_result.get("datasets", [])
    primary_dataset = datasets[0] if datasets else None

    steps = []
    if primary_dataset:
        steps.append(WorkflowStep(
            step_id=1, step_type="load_data",
            description=f"加载 {primary_dataset['name']} 数据集",
            ee_code_snippet=f'ee.ImageCollection("{primary_dataset["ee_id"]}").filterDate("{time_start}-01-01", "{time_end}-12-31")',
            params={"dataset": primary_dataset["ee_id"], "name": primary_dataset["name"]}
        ))

    if geojson_path:
        steps.append(WorkflowStep(step_id=2, step_type="set_roi",
            description="导入 GeoJSON 边界",
            ee_code_snippet=f'roi = geemap.geojson_to_ee("{geojson_path}")',
            params={"roi_source": "geojson", "path": geojson_path}))
    else:
        steps.append(WorkflowStep(step_id=2, step_type="set_roi",
            description=f"定义研究区域: {region}",
            params={"roi_source": "manual", "region_name": region}))

    if task_type in ["城市扩张", "植被指数", "土地利用", "森林变化"]:
        steps.append(WorkflowStep(step_id=3, step_type="cloud_mask",
            description="应用云掩膜",
            ee_code_snippet="def mask_clouds(image): qa = image.select('QA60'); ...",
            params={"method": "sentinel2_qa60"}))

    sid = 4
    for idx_name in needed_indices:
        idx_info = INDEX_FORMULAS.get(idx_name, {})
        steps.append(WorkflowStep(step_id=sid, step_type="calculate_index",
            description=f"计算 {idx_name} ({idx_info.get('description', '')})",
            params={"index": idx_name, "formula": idx_info.get("formula", "")}))
        sid += 1

    steps.append(WorkflowStep(step_id=sid, step_type="reduce",
        description="计算时间序列均值和变化趋势",
        params={"method": "annual_mean", "composite_period": "summer"}))
    sid += 1

    if task_type in ["城市扩张", "土地利用", "森林变化"]:
        steps.append(WorkflowStep(step_id=sid, step_type="change_detection",
            description=f"{task_type}变化检测分析",
            params={"method": "difference"}))
        sid += 1

    steps.append(WorkflowStep(step_id=sid, step_type="visualize",
        description="生成交互式地图和统计图表",
        params={"outputs": ["interactive_map", "time_series_chart"]}))

    steps.append(WorkflowStep(step_id=sid + 1, step_type="export",
        description="导出结果为 GeoTIFF, CSV, PNG, HTML",
        params={"formats": ["tiff", "csv", "png", "html"]}))

    return AnalysisWorkflow(
        title=f"{task_type}分析: {region} ({time_start}-{time_end})",
        task_type=task_type,
        description=f"基于 {primary_dataset['name'] if primary_dataset else '多源数据'} 的{region}{task_type}分析",
        region_of_interest=region,
        time_start=time_start, time_end=time_end,
        datasets=datasets, indices=needed_indices, steps=steps,
    )


def workflow_to_generation_plan(workflow: AnalysisWorkflow) -> str:
    lines = [
        f"📋 分析计划: {workflow.title}",
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"📂 任务类型: {workflow.task_type}",
        f"📍 研究区域: {workflow.region_of_interest}",
        f"📅 时间范围: {workflow.time_start} - {workflow.time_end}",
        f"📊 使用数据: {', '.join(d['name'] for d in workflow.datasets[:3])}",
        f"🧮 计算指数: {', '.join(workflow.indices) or '无'}",
        f"☁️  云掩膜: {'是' if workflow.cloud_mask else '否'}",
        f"📤 输出格式: {', '.join(workflow.output_format)}",
        f"",
        f"📝 分析步骤:",
    ]
    for step in workflow.steps:
        lines.append(f"   {step.step_id}. [{step.step_type}] {step.description}")
    return "\n".join(lines)
