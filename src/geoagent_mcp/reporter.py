"""
报告生成模块 - 自动生成 Markdown/PDF 分析报告
"""

import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

OUTPUT_DIR = Path(__file__).parent.parent.parent / "GeoAgent_Output"


def generate_markdown_report(
    workflow, results: Dict[str, Any],
    figures: List[str] = None, maps: List[str] = None,
    output_path: str = None
) -> str:
    """生成 Markdown 格式分析报告"""
    if output_path is None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = OUTPUT_DIR / "reports" / f"report_{ts}.md"
    os.makedirs(Path(output_path).parent, exist_ok=True)

    lines = [
        f"# 🌍 {workflow.title}", "",
        f"> 自动生成报告 | GeoAgent MCP | {datetime.now().strftime('%Y-%m-%d %H:%M')}", "",
        "---", "",
        "## 📋 分析概览", "",
        "| 项目 | 内容 |", "|------|------|",
        f"| 任务类型 | {workflow.task_type} |",
        f"| 研究区域 | {workflow.region_of_interest} |",
        f"| 时间范围 | {workflow.time_start} - {workflow.time_end} |",
        f"| 计算指数 | {', '.join(workflow.indices) or '无'} |",
        f"| 使用数据 | {workflow.datasets[0]['name'] if workflow.datasets else 'N/A'} |",
        f"| 云掩膜 | {'是' if workflow.cloud_mask else '否'} |", "",
        "## 🔧 分析流程", "",
    ]

    for step in workflow.steps:
        lines.append(f"**{step.step_id}. [{step.step_type}]** {step.description}")
    lines.append("")

    lines += ["## 📊 数据源", ""]
    for ds in workflow.datasets[:3]:
        lines += [
            f"- **{ds['name']}** ({ds['resolution']})",
            f"  - Earth Engine ID: `{ds['ee_id']}`",
            f"  - 时间范围: {ds['temporal_range']}",
            f"  - 说明: {ds['description']}", ""
        ]

    from .dataset_brain import INDEX_FORMULAS
    lines += ["## 🧮 计算指数", ""]
    for idx_name in workflow.indices:
        info = INDEX_FORMULAS.get(idx_name, {})
        if info:
            lines += [f"**{idx_name}** = `{info.get('formula', '')}`", f"> {info.get('description', '')}", ""]

    lines += ["## 💡 结论与建议", "", "（请根据分析结果补充具体结论）", ""]
    lines += ["---", f"*报告由 GeoAgent MCP v0.1.0 自动生成 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"]

    report = "\n".join(lines)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)
    return str(output_path)


def generate_pdf_report(markdown_path: str, output_path: str = None) -> str:
    """将 Markdown 报告转换为 PDF"""
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import cm

    if output_path is None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = OUTPUT_DIR / "reports" / f"report_{ts}.pdf"
    os.makedirs(Path(output_path).parent, exist_ok=True)

    with open(markdown_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    doc = SimpleDocTemplate(output_path, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    story = []

    for line in md_content.split("\n"):
        if line.startswith("# "): story.append(Paragraph(line[2:], styles["Title"]))
        elif line.startswith("## "): story.append(Paragraph(line[3:], styles["Heading2"]))
        elif line.startswith("### "): story.append(Paragraph(line[4:], styles["Heading3"]))
        elif line.startswith("- "): story.append(Paragraph(f"• {line[2:]}", styles["Normal"]))
        elif line.startswith("> "): story.append(Paragraph(f"<i>{line[2:]}</i>", styles["Italic"]))
        elif line.strip() and not line.startswith("!"): story.append(Paragraph(line, styles["Normal"]))
        else: story.append(Spacer(1, 6))

    doc.build(story)
    return str(output_path)


def generate_summary(results: Dict[str, Any], workflow) -> Dict[str, Any]:
    """生成分析摘要"""
    summary = {
        "title": workflow.title,
        "task_type": workflow.task_type,
        "region": workflow.region_of_interest,
        "period": f"{workflow.time_start}-{workflow.time_end}",
        "indices_used": workflow.indices,
        "datasets_used": [d["name"] for d in workflow.datasets],
        "execution_time": datetime.now().isoformat(),
        "output_files": {"maps": [], "figures": [], "data": [], "reports": []}
    }
    for subdir in ["maps", "figures", "data", "reports"]:
        path = OUTPUT_DIR / subdir
        if path.exists():
            summary["output_files"][subdir] = [str(p.relative_to(OUTPUT_DIR)) for p in path.iterdir() if p.is_file()]
    return summary
