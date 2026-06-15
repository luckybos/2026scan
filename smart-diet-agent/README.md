# 🥗 Smart Diet Agent

> 智能饮食助手 - 基于大语言模型的个性化营养推荐系统

---

## 📋 项目简介

Smart Diet Agent 是一个基于大语言模型的智能饮食助手，能够根据用户的健康状况、饮食偏好和目标，提供个性化的营养建议和食谱推荐。

## 🎯 核心功能

- **营养计算**: 智能计算食物的营养成分
- **食谱生成**: 根据用户需求生成个性化食谱
- **用户画像**: 管理用户健康档案和饮食偏好
- **智能对话**: 自然语言交互，解答饮食相关问题

## 📁 目录结构

```
smart-diet-agent/
├── data/              # 数据处理脚本
├── src/               # 源代码
│   ├── core/          # 核心业务引擎
│   ├── agent/         # 智能体编排
│   ├── api/           # API接口层
│   └── common/        # 公共组件
├── frontend/          # 前端界面
├── tests/             # 单元测试
└── ...
```

## 🚀 快速开始

```bash
# 安装依赖
poetry install

# 设置环境变量
cp .env.example .env

# 启动服务
poetry run uvicorn src.api.main:app --reload
```

## 🛠️ 技术栈

| 分类 | 技术 |
|------|------|
| 大语言模型 | LangChain / LangGraph |
| 数据库 | PostgreSQL |
| API框架 | FastAPI |
| 前端 | Streamlit |
| 依赖管理 | Poetry |
