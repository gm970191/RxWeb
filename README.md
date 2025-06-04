# RxWEB 项目说明

## 项目概述
本项目 `RxWEB` 是一个基于 Python Flask 后端和 Vue 前端的通用公司网站，包含产品展示、新闻发布、资源共享等功能，同时提供了联系我们页面展示公司详情、地图、总裁致辞和招聘信息。

## 项目结构
```
 RxWeb/
    ├── backend/
    │   └── app.py  # Flask 后端主文件，定义 API 路由和数据库操作
    ├── company.db  # 数据库文件，存储网站相关数据
    └── frontend/
        └── src/
            ├── views/  # 存放 Vue 视图组件
            ├── router/  # 存放前端路由配置文件
            └── App.vue  # 根组件
```

## 初步版本发布
本项目现已完成初步版本开发，可进行基本功能的使用和测试。后续会持续优化和添加新功能。

## 忽略清单
为了避免提交不必要的文件和目录，项目中添加了 `.gitignore` 文件，该文件会忽略 `node_modules` 目录、日志文件、环境变量文件、打包输出目录和临时文件等。如果你需要提交这些文件，请手动从 `.gitignore` 中移除对应的规则。

## 数据库
数据库文件 `company.db` 位于与 `backend` 目录平级的位置，后端代码 `app.py` 中通过 `sqlite3.connect('../company.db')` 连接数据库。

## 运行项目
### 后端
1. 确保安装 Python 环境。
2. 打开终端，进入 `d:\Projects\RxWeb\backend` 目录。
3. 运行 `python app.py` 启动 Flask 后端服务。

### 前端
1. 确保安装 Node.js 和 npm。
2. 打开终端，进入 `d:\Projects\RxWeb\frontend` 目录。
3. 运行 `npm install` 安装依赖。
4. 运行 `npm run serve` 启动 Vue 前端开发服务器。

## 常见问题
### 网站只显示“欢迎访问公司网站”
可能是前端未正确渲染数据或请求未成功，可检查浏览器开发者工具查看请求情况。

### 运行程序后只返回 JSON 数据而非页面
后端路由均返回 JSON 数据，若需要返回 HTML 页面，可使用 Flask 的 `render_template` 函数渲染 HTML 模板。# RxWeb
