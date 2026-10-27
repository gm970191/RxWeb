import { site } from '../site'

// 下载页目前只读本地演示数据，内容随站点切换
const mockDownloads = site.downloads

export function getMockDownloads() {
  return Promise.resolve(mockDownloads);
} 