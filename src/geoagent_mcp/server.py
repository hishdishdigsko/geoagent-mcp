"""
GeoAgent MCP Server - 基于 Google Earth Engine 的全流程地理空间分析 Agent

提供 Tools:
  - geo_search_dataset: 任务类型 → 最优 GEE 数据集
  - geo_plan_workflow: 自然语言 → GEE 分析工作流
  - geo_execute_analysis: 执行分析脚本
  - geo_generate_script: 生成 GEE Python 脚本
  - geo_generate_map: 生成交互式地图
  - geo_generate_report: 生成分析报告
  - geo_check_auth: 检查 GEE 认证状态
  - geo_list_categories: 列出支持的任务类型
"""

import asyncio
import os
import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.server import FastMCP
from mcp.types import TextContent, ImageContent

from .dataset_brain import search_dataset, list_all_categories, get_index_info
from .workflow_planner import generate_workflow, workflow_to_generation_plan
from .executor import generate_script, execute_script
from .visualizer import (
    generate_interactive_map,
    generate_time_series_chart,
    generate_classification_map,
)
from .reporter import generate_markdown_report, generate_summary
from .auth import check_auth, initialize_gee, setup_gee


mcp = FastMCP("GeoAgent")

OUTPUT_DIR = Path(__file__).parent.parent.parent / "GeoAgent_Output"


@mcp.tool()
def geo_search_dataset(task_type: str) -> str:
    """根据任务类型搜索最优 GEE 数据集"""
    result = search_dataset(task_type)
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
def geo_list_categories() -> str:
    """列出所有支持的任务类型和分析类别"""
    cats = list_all_categories()
    return json.dumps({
        "categories": cats,
        "count": len(cats),
        "note": "使用 geo_search_dataset 查询特定类型的推荐数据集"
    }, ensure_ascii=False, indent=2)


@mcp.tool()
def geo_plan_workflow(user_query: str, geojson_path: str = "") -> str:
    """将自然语言任务解析为 GEE 分析工作流"""
    path = geojson_path if geojson_path else None
    workflow = generate_workflow(user_query, path)
    plan = workflow_to_generation_plan(workflow)
    result = {
        "plan_text": plan,
        "workflow": {
            "title": workflow.title,
            "task_type": workflow.task_type,
            "region": workflow.region_of_interest,
            "time_start": workflow.time_start,
            "time_end": workflow.time_end,
            "datasets": [d["ee_id"] for d in workflow.datasets],
            "indices": workflow.indices,
            "steps_count": len(workflow.steps),
        }
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
def geo_generate_script(user_query: str) -> str:
    """根据任务描述生成可执行的 GEE Python 脚本"""
    workflow = generate_workflow(user_query)
    script = generate_script(workflow)
    return script


@mcp.tool()
def geo_execute_analysis(user_query: str) -> str:
    """执行完整的 GEE 分析流程"""
    workflow = generate_workflow(user_query)
    script = generate_script(workflow)
    result = execute_script(script, timeout=600)

    output_files = {}
    for subdir in ["maps", "figures", "data", "reports"]:
        p = OUTPUT_DIR / subdir
        if p.exists():
            output_files[subdir] = [f.name for f in p.iterdir() if f.is_file()]

    return json.dumps({
        "success": result["success"],
        "workflow": {
            "title": workflow.title,
            "task_type": workflow.task_type,
            "region": workflow.region_of_interest,
        },
        "stdout": result.get("stdout", "")[-2000:],
        "output_files": output_files,
        "script_path": result.get("script_path", ""),
        "message": "分析完成!" if result["success"] else f"执行失败: {result.get('stderr', '')[:500]}"
    }, ensure_ascii=False, indent=2)


@mcp.tool()
def geo_check_auth() -> str:
    """检查 GEE 认证和连接状态"""
    auth = check_auth()
    if auth["authenticated"]:
        init = initialize_gee(auth.get("project_id"))
        return json.dumps({
            "authenticated": True,
            "project_id": auth.get("project_id"),
            "gee_connected": init["success"],
            "message": init["message"]
        }, ensure_ascii=False, indent=2)
    else:
        return json.dumps({
            "authenticated": False,
            "message": auth["message"],
            "help": "运行 geo_setup_gee 完成认证和初始化"
        }, ensure_ascii=False, indent=2)


@mcp.tool()
def geo_setup_gee(project_id: str = "") -> str:
    """执行 GEE 完整设置（认证 + 初始化）"""
    if project_id:
        os.environ["EARTHENGINE_PROJECT"] = project_id
    result = setup_gee()
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
def geo_generate_map(
    center_lat: float = 35.0,
    center_lon: float = 105.0,
    zoom: int = 5,
    title: str = "GeoAgent Map",
    geojson_data: str = ""
) -> str:
    """生成交互式 HTML 地图"""
    layers = []
    if geojson_data:
        try:
            gj = json.loads(geojson_data)
            layers.append({"name": "ROI", "type": "geojson", "data": gj})
        except json.JSONDecodeError:
            pass

    map_path = generate_interactive_map(
        center=(center_lat, center_lon),
        zoom=zoom,
        title=title,
        layers=layers
    )
    return json.dumps({
        "success": True,
        "map_path": map_path,
        "message": f"地图已生成: {map_path}"
    }, ensure_ascii=False, indent=2)


@mcp.tool()
def geo_generate_report(user_query: str) -> str:
    """生成完整的 Markdown 分析报告"""
    workflow = generate_workflow(user_query)
    summary = generate_summary({}, workflow)
    report_path = generate_markdown_report(workflow, summary)
    return json.dumps({
        "success": True,
        "report_path": report_path,
        "summary": summary
    }, ensure_ascii=False, indent=2)


@mcp.tool()
def geo_export_result(data: str, format: str = "csv", filename: str = "") -> str:
    """导出分析结果为指定格式"""
    import pandas as pd

    if not filename:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"export_{ts}"

    try:
        parsed = json.loads(data)
        df = pd.DataFrame(parsed if isinstance(parsed, list) else [parsed])

        if format == "csv":
            path = OUTPUT_DIR / "data" / f"{filename}.csv"
            os.makedirs(path.parent, exist_ok=True)
            df.to_csv(path, index=False)
        elif format == "json":
            path = OUTPUT_DIR / "data" / f"{filename}.json"
            os.makedirs(path.parent, exist_ok=True)
            df.to_json(path, orient="records", force_ascii=False)
        else:
            path = OUTPUT_DIR / "data" / f"{filename}.{format}"
            os.makedirs(path.parent, exist_ok=True)
            df.to_csv(path, index=False)

        return json.dumps({
            "success": True, "path": str(path),
            "format": format, "rows": len(df)
        }, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False, indent=2)


@mcp.resource("geoagent://datasets")
def get_datasets_resource() -> str:
    """获取数据集目录"""
    cats = list_all_categories()
    result = {}
    for cat in cats:
        r = search_dataset(cat)
        result[cat] = [d["name"] for d in r.get("datasets", [])]
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.resource("geoagent://indices")
def get_indices_resource() -> str:
    """获取支持的指数列表"""
    from .dataset_brain import INDEX_FORMULAS
    return json.dumps(INDEX_FORMULAS, ensure_ascii=False, indent=2)


@mcp.resource("geoagent://output/{subdir}")
def get_output_files(subdir: str) -> str:
    """获取输出目录中的文件列表"""
    path = OUTPUT_DIR / subdir
    if not path.exists():
        return json.dumps({"error": f"目录不存在: {subdir}", "valid": ["maps", "figures", "data", "reports", "logs"]})
    files = [f.name for f in path.iterdir() if f.is_file()]
    return json.dumps({"directory": subdir, "files": files, "count": len(files)}, ensure_ascii=False)


def main():
    """启动 GeoAgent MCP Server"""
    print("🛰️  GeoAgent MCP Server v0.1.0")
    print(f"   输出目录: {OUTPUT_DIR}")
    mcp.run()


if __name__ == "__main__":
    main()
