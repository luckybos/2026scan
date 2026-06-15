# 🥗 Smart Diet Agent Frontend

基于 Streamlit 的智能饮食助手前端应用

## 快速开始

```bash
# 安装依赖
pip install streamlit requests python-dotenv

# 设置环境变量
cp .env.example .env

# 启动应用
streamlit run app.py
```

## 功能特性

- 用户注册与登录
- 营养查询
- 食谱推荐
- 每日饮食计划
- 智能对话助手

## 项目结构

```
frontend/
├── app.py              # 主应用入口
├── components/         # 组件目录
│   ├── sidebar.py      # 侧边栏组件
│   ├── chat.py         # 聊天组件
│   ├── nutrition.py    # 营养查询组件
│   └── recipe.py       # 食谱组件
├── utils/              # 工具函数
│   └── api_client.py   # API客户端
└── .env.example        # 环境变量示例
```
