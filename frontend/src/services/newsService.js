import { apiRequest } from './apiClient'

// 模拟新闻数据（接口不可用时首页兜底）
const mockNews = [
  { id: 20, title: '全国技术支持升级为 7×12 小时，新增远程巡检', date: '2025-08-08', source: '官方新闻', summary: '工作日 8:00-20:00 受理故障，每月可预约一次远程巡检，提前发现证书和备份问题。' },
  { id: 19, title: '亮相 2025 中国软博会，智能办公方案获创新奖', date: '2025-06-21', source: '行业资讯', summary: '展会期间完成多场现场演示，并与三家区域集成商达成意向合作。' },
  { id: 18, title: '数据中台 2.0 发布，统一企业数据资产目录', date: '2025-04-16', source: '产品动态', summary: '新增血缘可视化和质量规则，帮助业务部门看清指标从哪来、能不能信。' },
  { id: 1, title: '公司发布全新一代智能办公系统', date: '2024-06-20', source: '官方新闻', summary: '新系统集成了AI助手、自动化流程和数据分析功能，旨在大幅提升企业协作效率和决策水平。' },
]

export function getMockNews() {
  return Promise.resolve(mockNews)
}

export async function fetchNews({ page = 1, pageSize = 10, keyword = '' } = {}) {
  const params = new URLSearchParams({ page, page_size: pageSize, keyword })
  return apiRequest(`/api/news?${params.toString()}`)
}

export async function fetchNewsDetail(id) {
  return apiRequest(`/api/news/${id}`)
}

export async function createNews(news) {
  return apiRequest('/api/news', { method: 'POST', body: news })
}

export async function updateNews(id, news) {
  return apiRequest(`/api/news/${id}`, { method: 'PUT', body: news })
}

export async function deleteNews(id) {
  return apiRequest(`/api/news/${id}`, { method: 'DELETE' })
}
