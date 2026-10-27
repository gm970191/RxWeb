Cypress.on('uncaught:exception', (err) => {
  if (err.message.includes('ResizeObserver loop')) {
    return false;
  }
});

describe('新闻详情页跳转', () => {
  it('点击新闻标题应跳转到详情页并显示正确内容', () => {
    cy.visit('/news')
    // 获取第一个新闻标题文本
    cy.get('.news-title a').first().then($a => {
      const title = $a.text()
      cy.wrap($a).click()
      // 跳转后校验详情页标题
      cy.url().should('include', '/news/')
      cy.get('.news-title').should('contain', title)
      // 校验详情页有发布日期、来源、摘要等
      cy.get('.news-meta').should('contain', '发布日期')
      cy.get('.news-meta').should('contain', '来源')
      cy.get('.news-summary').should('not.be.empty')
      cy.get('.news-content').should('not.be.empty')
    })
  })
}) 