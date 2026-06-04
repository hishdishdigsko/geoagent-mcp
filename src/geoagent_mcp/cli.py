"""
GeoAgent MCP 命令行工具
"""

import sys, json, click
from pathlib import Path

from .dataset_brain import search_dataset, list_all_categories
from .workflow_planner import generate_workflow, workflow_to_generation_plan
from .auth import check_auth, setup_gee
from .executor import generate_script as gen_script, execute_script


@click.group()
@click.version_option(version="0.1.0", prog_name="geoagent-mcp")
def cli():
    """🛰️  GeoAgent MCP - GEE 全流程地理空间分析 Agent"""
    pass


@cli.command()
def start():
    """启动 GeoAgent MCP Server"""
    from .server import main
    main()


@cli.command()
def setup():
    """完整 GEE 环境设置（认证 + 项目配置）"""
    setup_gee()


@cli.command()
def status():
    """检查 GEE 认证状态"""
    result = check_auth()
    print(json.dumps(result, ensure_ascii=False, indent=2))


@cli.command()
@click.argument("task_type")
def dataset(task_type):
    """查询任务类型推荐的数据集"""
    result = search_dataset(task_type)
    print(json.dumps(result, ensure_ascii=False, indent=2))


@cli.command()
def categories():
    """列出所有支持的任务类别"""
    for c in list_all_categories():
        print(f"  📂 {c}")


@cli.command()
@click.argument("query")
@click.option("--script-only", is_flag=True, help="仅生成脚本，不执行")
def analyze(query, script_only):
    """执行 GEE 分析任务"""
    workflow = generate_workflow(query)
    plan = workflow_to_generation_plan(workflow)
    print(plan)

    if script_only:
        script = gen_script(workflow)
        script_path = Path(f"geoagent_script_{workflow.task_type}.py")
        script_path.write_text(script, encoding="utf-8")
        print(f"\n✅ 脚本已保存: {script_path}")
    else:
        print("\n🚀 开始执行...")
        script = gen_script(workflow)
        result = execute_script(script)
        if result["success"]:
            print("✅ 完成!")
            print(result["stdout"][-500:])
        else:
            print("❌ 失败:", result["stderr"])


@cli.command()
@click.argument("query")
def plan(query):
    """仅生成分析计划"""
    workflow = generate_workflow(query)
    print(workflow_to_generation_plan(workflow))


if __name__ == "__main__":
    cli()
