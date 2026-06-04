# 🛰️ GeoAgent MCP

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/GEE-Google%20Earth%20Engine-34A853?style=for-the-badge&logo=googleearth" alt="GEE">
  <img src="https://img.shields.io/badge/MCP-Model%20Context%20Protocol-purple?style=for-the-badge" alt="MCP">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="MIT">
  <br>
  <strong>🧠 让 Claude Code 成为你的地理空间分析智能体</strong>
  <br>
  自然语言驱动 → 自动选择数据集 → 执行分析 → 生成地图 → 输出报告
</p>

---

## ✨ 为什么选择 GeoAgent MCP？

传统的 GEE 分析需要：
- ❌ 手动查找合适的数据集
- ❌ 编写复杂的 Python/JavaScript 代码
- ❌ 调试各种错误
- ❌ 反复查阅文档

**GeoAgent MCP 只需要一句话：**

```
"分析石家庄2015-2025年城市扩张趋势"
"黄河流域近10年NDVI变化统计"
"帮我找武汉2020年洪水淹没范围"
```

**Claude 自动完成余下所有步骤。**

---

## 🎯 功能矩阵

| 模块 | 功能 | 触发条件 |
|------|------|----------|
| 🔍 **Dataset Brain** | 任务类型 → 最优 GEE 数据集自动匹配 | 提及"城市扩张/NDVI/洪水"等关键词 |
| 📋 **Workflow Planner** | 自然语言 → 结构化分析计划 | 描述分析需求 |
| ⚡ **分析执行** | 自动生成 + 运行 GEE Python 脚本 | 提交分析任务 |
| 🗺️ **可视化** | 交互式 HTML 地图 + 静态 PNG 图表 | 分析完成后自动触发 |
| 📄 **报告生成** | Markdown/PDF 分析报告 | 分析完成后自动触发 |
| 📦 **数据导出** | CSV / GeoTIFF / JSON | 按需触发 |

### 支持的任务类型

| 任务 | 推荐数据集 | 常用指数 |
|------|-----------|----------|
| 🏙️ 城市扩张 | Dynamic World, Sentinel-2, Landsat 8 | NDBI, NDVI |
| 🌳 森林变化 | Global Forest Change, MODIS | NDVI, NBR |
| 🌾 土地利用 | ESA WorldCover, Dynamic World | NDVI |
| 💧 水体变化 | JRC GSW, Sentinel-1 SAR | NDWI, MNDWI |
| 🌿 植被指数 | MODIS MOD13Q1, Sentinel-2 | NDVI, EVI, SAVI |
| 💡 夜光分析 | VIIRS DNB, DMSP-OLS | - |
| ☀️ 光伏选址 | ERA5-Land Solar, MODIS LST | NDVI |
| 🌊 洪水监测 | Sentinel-1 SAR, JRC GSW | MNDWI |
| 🌡️ 地表温度 | MODIS MOD11A1, Landsat 8 | - |
| ⛰️ 地形分析 | SRTM 30m, ALOS DSM | - |

---

## 🚀 快速开始

### 前置要求

- Python >= 3.9
- [Google Earth Engine 账号](https://signup.earthengine.google.com/)
- [Google Cloud Project](https://console.cloud.google.com/)
- Claude Code / Claude Desktop

### 1. 安装

```bash
git clone https://github.com/hishdishdigsko/geoagent-mcp.git
cd geoagent-mcp
pip install -e .
```

### 2. GEE 认证

```bash
earthengine authenticate
```

### 3. 配置 Claude Code

```json
{
  "mcpServers": {
    "geoagent": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "geoagent_mcp.server"],
      "cwd": "/path/to/geoagent-mcp/src"
    }
  }
}
```

### 4. 开始使用

在 Claude Code 中说：`分析石家庄2015-2025城市扩张`

---

## 🏗️ 架构

```
GeoAgent-MCP/
├── src/geoagent_mcp/
│   ├── server.py           # MCP Server (10 Tools + 3 Resources)
│   ├── dataset_brain.py    # 知识库: 10类任务 × 多项数据集
│   ├── workflow_planner.py # 自然语言 → GEE 分析工作流
│   ├── executor.py         # 脚本生成器 + 执行引擎
│   ├── visualizer.py       # 交互式地图 + 统计图表
│   ├── reporter.py         # Markdown/PDF 报告
│   ├── auth.py             # GEE 认证管理
│   └── cli.py              # CLI 命令行工具
├── examples/
│   ├── shijiazhuang_urban.py  # 石家庄城市扩张
│   └── yellow_river_ndvi.py   # 黄河流域NDVI
└── GeoAgent_Output/           # 自动创建
    ├── maps/ | figures/ | data/ | reports/ | logs/
```

---

## 📊 基准数据集

- **Dynamic World V1** — Google/WRI 10m 全球土地覆盖
- **Global Forest Change** — Hansen 30m 森林变化 (2000-2023)
- **ESA WorldCover** — ESA 10m 土地覆盖
- **JRC Global Surface Water** — 38年地表水变化
- **MODIS MOD13Q1** — 250m NDVI/EVI (2000-至今)
- **Sentinel-2 MSI** — 10m 多光谱 (2017年至今)
- **Landsat 8/9** — 30m 多光谱 (2013年至今)
- **VIIRS DNB** — 500m 夜间灯光
- **SRTM 30m** — 全球 DEM

---

## 📄 许可证

MIT License © 2026 王总

---

<p align="center">
  <sub>Built with ❤️ by 王总 | Powered by Google Earth Engine & Claude Code</sub>
</p>
