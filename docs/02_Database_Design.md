# 2. 数据库设计

本文档描述了项目所使用的数据库表结构 (Schema)。数据库类型为 SQLite。

## 2.1. 表清单

| 表名 | 实体 | 说明 |
| :--- | :--- | :--- |
| `admins` | 管理员 | 存储后台管理系统的登录用户信息。 |
| `products` | 产品 | 存储产品信息。 |
| `product_categories`| 产品分类 | 存储产品的分类信息。 |
| `news` | 新闻 | 存储新闻动态、公司里程碑、产品里程牌等。 |
| `carousels` | 轮播图 | 存储主页轮播图信息。 |
| `resources` | 资源下载 | 存储可供下载的文件资源信息。 |
| `site_info` | 站点信息 | 单行表，存储联系我们、页脚等全局信息。 |

---

## 2.2. 表结构详情

### 2.2.1. `admins` - 管理员表

| 字段名 | 数据类型 | 约束 | 说明 |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | 主键, 自增 | 唯一标识 |
| `username` | VARCHAR(50) | 非空, 唯一 | 管理员用户名 |
| `hashed_password`| VARCHAR(255) | 非空 | 加密后的密码 |

### 2.2.2. `products` - 产品表

| 字段名 | 数据类型 | 约束 | 说明 |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | 主键, 自增 | 唯一标识 |
| `name` | VARCHAR(100) | 非空 | 产品名称 |
| `category_id` | INTEGER | 外键 (-> `product_categories.id`) | 关联的产品分类 |
| `image_path` | VARCHAR(255)| | 产品主图的存储路径 |
| `parameters` | TEXT | | 产品参数 (建议使用 JSON 格式存储) |
| `description` | TEXT | | 产品详述 (支持 HTML 或 Markdown) |
| `is_popular` | BOOLEAN | 默认 0 | 是否为最受欢迎的产品 (用于首页展示) |

### 2.2.3. `product_categories` - 产品分类表

| 字段名 | 数据类型 | 约束 | 说明 |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | 主键, 自增 | 唯一标识 |
| `name` | VARCHAR(50) | 非空, 唯一 | 分类名称 |

### 2.2.4. `news` - 新闻表

| 字段名 | 数据类型 | 约束 | 说明 |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | 主键, 自增 | 唯一标识 |
| `title` | VARCHAR(255)| 非空 | 新闻标题 |
| `category` | VARCHAR(50) | 非空 | 新闻类别 (枚举值) |
| `summary` | TEXT | | 新闻摘要 |
| `content` | TEXT | | 新闻正文 (支持 HTML 或 Markdown) |
| `created_at`| DATETIME | 默认当前时间 | 发布时间 |

> **新闻类别 (`category`) 枚举值说明:**
> *   `dynamic_info`: 动态资讯
> *   `company_milestone`: 公司里程碑
> *   `product_milestone`: 产品里程牌

### 2.2.5. `carousels` - 轮播图表

| 字段名 | 数据类型 | 约束 | 说明 |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | 主键, 自增 | 唯一标识 |
| `image_path` | VARCHAR(255)| 非空 | 图片的存储路径 |
| `link_to` | VARCHAR(255)| | 点击图片后的跳转链接，可为空 |
| `display_order` | INTEGER | 默认 0 | 显示顺序，数字越小越靠前 |

### 2.2.6. `resources` - 资源下载表

| 字段名 | 数据类型 | 约束 | 说明 |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | 主键, 自增 | 唯一标识 |
| `name` | VARCHAR(100)| 非空 | 资源名称 (如: "产品手册 v1.2") |
| `description`| TEXT | | 资源描述 |
| `file_path` | VARCHAR(255)| 非空 | 文件的存储路径 |
| `file_type` | VARCHAR(20) | | 文件类型 (如: PDF, ZIP, DOCX) |
| `version` | VARCHAR(20) | | 版本号 |
| `created_at`| DATETIME | 默认当前时间 | 上传时间 |

### 2.2.7. `site_info` - 站点信息表

这是一个单行表，用于存储全局配置信息。

| 字段名 | 数据类型 | 说明 |
| :--- | :--- | :--- |
| `id` | INTEGER | 主键 (值固定为 1) |
| `president_speech`| TEXT | 总裁致辞 |
| `company_details`| TEXT | 公司详情 (地址、电话、邮箱等) |
| `map_info` | TEXT | 地图嵌入代码或坐标信息 |
| `recruitment_info`| TEXT | 招聘信息 (支持 HTML) |
| `footer_links` | TEXT | 友情链接 (建议使用 JSON 格式存储) |
| `beian_info` | VARCHAR(255)| 网站备案信息 | 