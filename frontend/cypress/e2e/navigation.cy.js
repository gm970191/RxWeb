describe('导航栏链接跳转测试', () => {
  // 忽略来自应用程序的特定良性错误
  Cypress.on('uncaught:exception', (err, runnable) => {
    // 当我们看到这个特定的 ResizeObserver 错误时，
    // 返回 false 可以阻止 Cypress 使测试失败
    if (err.message.includes('ResizeObserver loop')) {
      return false;
    }
  });

  const navLinks = [
    { text: '主页', path: '/' },
    { text: '产品中心', path: '/products' },
    { text: '新闻动态', path: '/news' },
    { text: '资源下载', path: 'downloads' },
    { text: '联系我们', path: '/contact' },
  ];

  beforeEach(() => {
    // 访问 baseUrl，该 baseUrl 在 cypress.config.cjs 中定义
    cy.visit('/');
  });

  navLinks.forEach(link => {
    it(`点击导航栏"${link.text}"应跳转到 ${link.path}`, () => {
      // 找到包含文本的导航项并点击
      cy.get('.el-menu').contains(link.text).click();
      
      // 验证 URL 是否正确
      cy.url().should('include', link.path);
      
      // 验证页面主要标题是否包含预期文本
      // 注意：'产品中心' 页的 h1 是 '产品中心'，所以replace不是必需的，但为了通用性保留
      cy.get('h1').should('contain', link.text.replace('中心', '')); 
    });
  });
}); 