"""
GEE 认证管理模块
- 检测认证状态
- 自动执行认证流程
- 管理 Google Cloud Project
"""

import ee
import json
import os
import subprocess
import sys
from pathlib import Path


def get_credentials_path() -> Path:
    """获取 GEE credentials 路径"""
    return Path.home() / ".config" / "earthengine" / "credentials"


def check_auth() -> dict:
    """
    检测 GEE 认证状态
    Returns: {"authenticated": bool, "project_id": str|None, "message": str}
    """
    result = {
        "authenticated": False,
        "project_id": None,
        "message": ""
    }

    cred_path = get_credentials_path()

    if cred_path.exists():
        try:
            with open(cred_path) as f:
                creds = json.load(f)
            if creds.get("refresh_token") or creds.get("access_token"):
                result["authenticated"] = True
                result["message"] = "✅ GEE 认证已就绪"
                result["project_id"] = creds.get("project") or creds.get("quota_project_id") or os.environ.get("EARTHENGINE_PROJECT", "")
            else:
                result["message"] = "⚠️ 认证文件存在但 token 无效"
        except Exception as e:
            result["message"] = f"⚠️ 读取认证文件失败: {e}"
    else:
        result["message"] = "⚠️ GEE 未认证，需要执行认证流程"
        cred_path.parent.mkdir(parents=True, exist_ok=True)

    if not result["project_id"]:
        result["project_id"] = os.environ.get("EARTHENGINE_PROJECT", "")

    return result


def authenticate() -> dict:
    """执行 GEE 认证流程"""
    try:
        print("\n🔐 开始 GEE 认证...")
        print("   浏览器将自动打开 Google 登录页面")
        print("   请完成授权后回到此处\n")

        result = subprocess.run(
            [sys.executable, "-m", "earthengine", "authenticate"],
            capture_output=False,
            text=True,
            timeout=300
        )

        if result.returncode == 0:
            return {"success": True, "message": "✅ GEE 认证成功"}
        else:
            return {"success": False, "message": f"❌ 认证失败 (exit code: {result.returncode})"}

    except subprocess.TimeoutExpired:
        return {"success": False, "message": "❌ 认证超时 (5分钟)"}
    except Exception as e:
        return {"success": False, "message": f"❌ 认证异常: {e}"}


def initialize_gee(project_id: str = None) -> dict:
    """初始化 GEE 连接"""
    try:
        if project_id:
            ee.Initialize(project=project_id)
        else:
            ee.Initialize()
        return {
            "success": True,
            "message": f"✅ GEE 连接成功 (project: {project_id or 'default'})",
            "project": project_id or "default"
        }
    except Exception as e:
        error_msg = str(e)
        if "timeout" in error_msg.lower() or "connect" in error_msg.lower():
            return {
                "success": False,
                "message": (
                    f"❌ GEE 连接失败 (网络超时)\n"
                    f"   中国大陆可能需要配置代理:\n"
                    f"   set HTTPS_PROXY=http://127.0.0.1:7890\n"
                    f"   或: os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:XXXX'\n"
                    f"   原始错误: {error_msg}"
                ),
                "project": project_id
            }
        return {
            "success": False,
            "message": f"❌ GEE 初始化失败: {error_msg}",
            "project": project_id
        }


def setup_gee() -> dict:
    """完整的 GEE 设置流程"""
    print("\n" + "=" * 60)
    print("🛰️  GeoAgent MCP - GEE 环境初始化")
    print("=" * 60)

    auth_status = check_auth()
    print(auth_status["message"])

    if not auth_status["authenticated"]:
        print("\n⚠️ 需要完成 GEE 认证...")
        auth_result = authenticate()
        print(auth_result["message"])
        if not auth_result["success"]:
            return {"success": False, "message": "认证失败，无法继续"}
    else:
        auth_result = {"success": True}

    project_id = auth_status.get("project_id", "")
    if not project_id:
        print("\n📋 请输入 Google Cloud Project ID:")
        print("   (可在 https://console.cloud.google.com 创建)")
        project_id = input("   Project ID > ").strip()
        if project_id:
            os.environ["EARTHENGINE_PROJECT"] = project_id

    print("\n🔗 正在连接 GEE...")
    init_result = initialize_gee(project_id)
    print(init_result["message"])

    return init_result
