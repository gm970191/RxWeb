# 3. API 接口设计 (Endpoints)

本文档定义了前后端分离架构中的 RESTful API 接口。所有接口均以 `/api` 为前缀。

## 3.1. 公共接口 (Public Access)

这些接口无需认证即可访问，用于网站前台的数据展示。

---

### 3.1.1. 站点与轮播图

-   **`GET /api/site-info`**
    -   **描述:** 获取全局站点信息，用于"联系我们"页面和页脚。
    -   **返回:** `200 OK` - 包含所有站点信息的 JSON 对象。

-   **`GET /api/carousels`**
    -   **描述:** 获取所有启用的轮播图列表，按 `display_order` 排序。
    -   **返回:** `200 OK` - 包含轮播图对象的数组。

---

### 3.1.2. 产品

-   **`GET /api/products`**
    -   **描述:** 获取产品列表，支持按分类和是否热门进行筛选。
    -   **查询参数:**
        -   `category_id` (integer, 可选): 按产品分类ID筛选。
        -   `is_popular` (boolean, 可选): 筛选首页热门产品。
        -   `page` (integer, 可选): 分页页码。
        -   `size` (integer, 可选): 每页数量。
    -   **返回:** `200 OK` - 包含产品对象的分页列表。

-   **`GET /api/products/{id}`**
    -   **描述:** 获取单个产品的详细信息。
    -   **返回:** `200 OK` - 单个产品对象的 JSON。`404 Not Found` - 如果产品不存在。

-   **`GET /api/product-categories`**
    -   **描述:** 获取所有产品分类的列表。
    -   **返回:** `200 OK` - 包含产品分类对象的数组。

---

### 3.1.3. 新闻

-   **`GET /api/news`**
    -   **描述:** 获取新闻列表，支持按分类筛选。
    -   **查询参数:**
        -   `category` (string, 可选): 按新闻类别筛选 (如: `dynamic_info`, `product_milestone`)。
        -   `page` (integer, 可选): 分页页码。
        -   `size` (integer, 可选): 每页数量。
    -   **返回:** `200 OK` - 包含新闻概要对象的分页列表。

-   **`GET /api/news/{id}`**
    -   **描述:** 获取单条新闻的详细内容。
    -   **返回:** `200 OK` - 单条新闻对象的 JSON。`404 Not Found` - 如果新闻不存在。

---

### 3.1.4. 资源下载

-   **`GET /api/resources`**
    -   **描述:** 获取可供下载的资源列表。
    -   **查询参数:**
        -   `page` (integer, 可选): 分页页码。
        -   `size` (integer, 可选): 每页数量。
    -   **返回:** `200 OK` - 包含资源文件信息对象的分页列表。

## 3.2. 管理接口 (Admin Access)

这些接口需要管理员登录并提供有效的 JWT (JSON Web Token) 进行认证。用于后台管理页面。

---

### 3.2.1. 认证

-   **`POST /api/auth/login`**
    -   **描述:** 管理员登录。
    -   **请求体:** `{ "username": "...", "password": "..." }`
    -   **返回:** `200 OK` - `{ "access_token": "...", "token_type": "bearer" }`。`401 Unauthorized` - 凭证无效。

---

### 3.2.2. 管理接口通用规则

对于所有需要认证的资源管理接口 (产品、新闻、分类、资源等)，遵循标准的 RESTful 模式：

| 方法 | 路径 | 描述 |
|:--- |:--- |:--- |
| `POST` | `/api/{resource}` | 创建一个新资源。 |
| `PUT` | `/api/{resource}/{id}` | 更新一个指定ID的资源。 |
| `DELETE`| `/api/{resource}/{id}` | 删除一个指定ID的资源。 |
| `GET` | `/api/{resource}` | 获取资源列表 (管理视图，可能包含更多信息)。 |
| `GET` | `/api/{resource}/{id}`| 获取单个资源的完整信息 (用于编辑)。 |

---

### 3.2.3. 具体管理接口

-   **产品管理:** `POST /api/products`, `PUT /api/products/{id}`, `DELETE /api/products/{id}`
-   **产品分类管理:** `POST /api/product-categories`, `PUT /api/product-categories/{id}`, `DELETE /api/product-categories/{id}`
-   **新闻管理:** `POST /api/news`, `PUT /api/news/{id}`, `DELETE /api/news/{id}`
-   **轮播图管理:** `POST /api/carousels`, `PUT /api/carousels/{id}`, `DELETE /api/carousels/{id}`
-   **资源下载管理:** `POST /api/resources`, `PUT /api/resources/{id}`, `DELETE /api/resources/{id}`
-   **站点信息管理:** `PUT /api/site-info` (因为只有一条记录，所以使用 PUT 更新)
-   **文件上传:**
    -   **`POST /api/upload`**
    -   **描述:** 用于上传图片或文件 (如产品图、资源文件)。
    -   **请求体:** `multipart/form-data`
    -   **返回:** `200 OK` - `{ "file_path": "/path/to/uploaded/file.jpg" }` 