# 1. 系统架构设计

本文档定义了"瑞学软件(RxWeb)"项目的整体技术架构、技术选型与代码目录结构。

## 1.1. 技术选型 (Tech Stack)

| 分类 | 技术 | 说明 |
| :--- | :--- | :--- |
| **前端** | **Vue 3** | 采用 Composition API 以提高代码组织性与复用性。 |
| | **Vite** | 下一代前端构建工具，提供极速的开发服务器和打包体验。 |
| | **Vue Router** | Vue 官方的路由管理器。 |
| | **Pinia** | Vue 官方推荐的状态管理库，轻量、简洁、易用。 |
| | **Element Plus** | 强大且丰富的桌面端 UI 组件库，用于构建专业统一的界面。 |
| | **Axios** | 成熟可靠的 HTTP 请求库，用于与后端 API 通信。 |
| **后端** | **Python 3** | 主流、稳定的后端开发语言。 |
| | **FastAPI** | 高性能的 Python Web 框架，自带交互式 API 文档，非常适合前后端分离项目。|
| | **UV** | 现代化的 Python 包管理工具，提供快速的依赖解析。 |
| | **SQLAlchemy** | 功能强大的数据库 ORM (对象关系映射) 库。 |
| | **Pydantic** | 用于 API 的数据格式定义与校验，是 FastAPI 的核心部分。 |
| **数据库** | **SQLite** | 轻量级的本地文件数据库，便于开发与部署。 |

## 1.2. 项目目录结构设计

为了保证代码的清晰度、可维护性和未来可扩展性，项目将遵循以下目录结构。

```
RxWeb/
├── .gitignore
├── README.md                # 项目说明
├── requirements.txt         # 由 uv 管理的 Python 依赖
├── data/                    # 数据库目录
│   └── company.db           # SQLite 数据库文件
│
├── docs/                    # 存放所有设计文档
│   ├── 01_System_Architecture.md
│   ├── 02_Database_Design.md
│   ├── 03_API_Endpoints.md
│   └── 04_Frontend_Design.md
│
├── backend/                 # 后端代码 (Python FastAPI)
│   ├── app/                 # FastAPI 应用核心目录
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI 应用入口
│   │   ├── db.py            # 数据库连接与会话管理
│   │   ├── models/          # SQLAlchemy 数据模型 (表结构)
│   │   ├── schemas/         # Pydantic 数据模式 (API 数据格式)
│   │   ├── crud/            # 数据库增删改查 (CRUD) 逻辑
│   │   └── api/             # API 路由/端点
│   └── tests/               # 后端测试代码
│
└── frontend/                # 前端代码 (Vue)
    ├── public/              # 静态资源目录
    ├── src/
    │   ├── assets/          # 样式、字体、图片等资源
    │   ├── components/      # 可复用的 UI 组件
    │   ├── views/           # 页面级组件
    │   ├── router/          # 路由配置
    │   ├── stores/          # Pinia 状态管理
    │   ├── services/        # API 请求服务
    │   └── App.vue          # 根组件
    ├── index.html
    ├── package.json         # 前端项目依赖
    └── vite.config.js       # Vite 配置文件
``` 