# 4. 前端设计

本文档描述了项目前端应用（基于 Vue 3）的结构、页面、组件和关键实现策略。

## 4.1. 核心设计原则

-   **组件化:** 遵循 Vue 的核心思想，将 UI 拆分为一系列可复用、自包含的组件。
-   **响应式设计:** 所有页面和组件都必须能够适应不同尺寸的屏幕（从桌面到移动设备）。将使用 Element Plus 的响应式栅格系统和 CSS 媒体查询来实现。
-   **关注点分离:** 逻辑（JavaScript）、结构（HTML模板）和样式（CSS）应保持分离。API 请求逻辑将被封装在专门的 `services` 目录中，全局状态由 `stores` 目录中的 Pinia 统一管理。

## 4.2. 页面 (Views)

`src/views` 目录下的 `.vue` 文件代表了应用中的不同页面。

| 页面组件 | 路由路径 | 描述 |
| :--- | :--- | :--- |
| `Home.vue` | `/` | **主页**：包含轮播图、最受欢迎的产品、热点新闻。 |
| `Products.vue` | `/products` | **产品页**：展示产品分类和产品列表。 |
| `ProductDetail.vue`| `/products/:id` | **产品详情页**：展示单个产品的图片、参数和详述。 |
| `News.vue` | `/news` | **新闻页**：按分类展示新闻列表。 |
| `NewsDetail.vue` | `/news/:id` | **新闻详情页**：展示单条新闻的完整内容。 |
| `Downloads.vue` | `/downloads` | **资源下载页**：展示可下载的资源列表。 |
| `Contact.vue` | `/contact` | **联系我们页**：展示公司详情、地图、总裁致辞等。 |
| `Login.vue` | `/login` | **登录页**：后台管理员登录入口。 |
| `Admin.vue` | `/admin` | **管理后台**：一个整合了所有内容管理功能的单页，需要登录访问。 |

## 4.3. 可复用组件 (Components)

`src/components` 目录存放应用中通用的 UI 构建块。

| 组件 | 描述 |
| :--- | :--- |
| `TheHeader.vue` | **统一顶部导航栏**：包含 Logo 和导航菜单，在所有页面共享。 |
| `TheFooter.vue` | **统一页脚**：包含友情链接和备案信息，在所有页面共享。 |
| `Carousel.vue` | **轮播图组件**：用于主页。 |
| `ProductCard.vue` | **产品卡片**：在产品列表页和主页使用，展示产品缩略图和名称。 |
| `NewsItem.vue` | **新闻条目**：在新闻列表页和主页使用，展示新闻标题和摘要。 |
| `ResourceItem.vue`| **资源下载条目**：在资源下载页使用，展示文件名、描述和下载按钮。|

## 4.4. 路由 (Routing)

路由配置位于 `src/router/index.js`，使用 `vue-router`。

-   公共路由: `/`, `/products`, `/products/:id`, `/news`, `/news/:id`, `/downloads`, `/contact`, `/login`。
-   受保护的路由: `/admin`。将使用路由守卫（`beforeEach`）来检查用户是否已登录（即 Pinia store 中是否存在有效的 token）。如果未登录，访问 `/admin` 将被重定向到 `/login`。

## 4.5. 状态管理 (State Management)

使用 `Pinia` 进行状态管理，定义在 `src/stores` 目录下。

-   **`auth.js`**:
    -   `state`: `user`, `token`。
    -   `actions`: `login()`, `logout()`。
    -   `getters`: `isAuthenticated`。

## 4.6. API 服务 (Services)

所有与后端 API 的交互都将被封装在 `src/services` 目录下的模块中。这使得组件本身保持干净，不直接处理 HTTP 请求的复杂性。

-   **`apiClient.js`**: 创建并配置一个 Axios 实例，包括设置 `baseURL` 和请求拦截器（用于自动附加认证 Token）。
-   **`products.js`**: 封装所有与产品相关的 API 调用。
-   **`news.js`**: 封装所有与新闻相关的 API 调用。
-   **`resources.js`**: 封装所有与资源下载相关的 API 调用。
-   **`site.js`**: 封装获取站点信息的 API 调用。 