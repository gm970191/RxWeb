// 模拟下载资源数据
const mockDownloads = [
  { id: 1, name: 'RxWeb前端框架V3.0.zip', description: '包含完整的框架代码、文档和示例。', version: '3.0.0', size: '25.8 MB', date: '2024-06-18' },
  { id: 2, name: '智能办公系统用户手册.pdf', description: '详细介绍了系统的各项功能和使用方法。', version: '1.0.0', size: '5.2 MB', date: '2024-06-20' },
  { id: 3, name: '产品介绍白皮书.pdf', description: '深入解读我们核心产品的技术架构与商业价值。', version: '2.1.0', size: '12.3 MB', date: '2024-05-30' },
  { id: 4, name: 'API接口文档.md', description: '为开发者提供的详细接口说明和调用示例。', version: '1.5.2', size: '1.1 MB', date: '2024-06-22' },
  { id: 5, name: '安全补丁SP2406.patch', description: '针对近期发现的安全漏洞的修复补丁。', version: '1.0.1', size: '876 KB', date: '2024-06-12' },
  { id: 6, name: '公司Logo及VI设计规范.zip', description: '包含公司全套Logo矢量图和VI使用规范。', version: '2.0', size: '18.9 MB', date: '2024-04-10' },
];

export function getMockDownloads() {
  return Promise.resolve(mockDownloads);
} 