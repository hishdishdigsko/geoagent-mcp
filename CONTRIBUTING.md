# 贡献指南

欢迎为 GeoAgent MCP 做贡献！

## 如何贡献

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 开发环境

```bash
pip install -e ".[dev]"
```

## 添加新数据集

编辑 `src/geoagent_mcp/dataset_brain.py` 中的 `DATASET_KNOWLEDGE_BASE`，添加新数据集即可。

## 添加新任务类型

1. 在 `DATASET_KNOWLEDGE_BASE` 中添加新类型
2. 在 `TASK_KEYWORDS` 中添加关键词
3. 提交 PR

## 代码规范

- 使用 `ruff` 进行 lint
- 使用 `black` 进行格式化
- 添加类型注解
