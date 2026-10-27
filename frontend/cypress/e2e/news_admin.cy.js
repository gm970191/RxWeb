Cypress.on('uncaught:exception', (err) => {
  if (err.message.includes('ResizeObserver loop')) {
    return false;
  }
});

describe('新闻管理功能', () => {
  beforeEach(() => {
    cy.visit('/login')
    cy.get('input[placeholder="邮箱"]').type('admin@rxweb.com')
    cy.get('input[placeholder="密码"]').type('rxweb123')
    cy.contains('button', '登录').click()
    cy.url().should('include', '/admin/news')
    cy.contains('新闻管理')
  })

  it('可以新增新闻', () => {
    cy.contains('新增新闻').click()
    cy.get('input[placeholder="请输入标题"]').type('自动化测试新闻', {force: true})
    cy.get('input[placeholder="请选择日期"]').type('2025-07-01', {force: true})
    cy.get('input[placeholder="请输入来源"]').type('自动化', {force: true})
    cy.get('textarea[placeholder="请输入摘要"]').type('这是自动化测试新增的新闻摘要', {force: true})
    cy.get('textarea[placeholder="请输入正文"]').type('这是自动化测试新增的新闻正文内容', {force: true})
    cy.contains('保存').click()
    cy.contains('新增成功')
    cy.contains('自动化测试新闻')
  })

  it('可以编辑新闻', () => {
    cy.intercept('PUT', '/api/news/*').as('updateNews')
    cy.contains('自动化测试新闻').parents('tr').within(() => {
      cy.contains('编辑').click()
    })
    cy.get('input[placeholder="请输入标题"]').clear().type('自动化测试新闻-已编辑', {force: true})
    cy.contains('保存').click()
    cy.wait('@updateNews')
    cy.contains('保存成功')
    cy.contains('自动化测试新闻-已编辑')
  })

  it('可以删除新闻', () => {
    cy.intercept('DELETE', '/api/news/*').as('deleteNews')
    cy.contains('自动化测试新闻-已编辑').parents('tr').within(() => {
      cy.contains('删除').click()
    })
    cy.contains('确定').click()
    cy.wait('@deleteNews')
    cy.contains('删除成功')
    cy.contains('自动化测试新闻-已编辑').should('not.exist')
  })

  it('可以分页浏览新闻', () => {
    cy.visit('/admin')
    cy.get('.el-pagination').should('exist')
    cy.get('.el-table__row').should('have.length.at.least', 1)
    cy.get('.el-pagination .btn-next').click()
    cy.wait(500)
    cy.get('.el-table__row').should('have.length.at.least', 1)
  })

  it('可以搜索新闻', () => {
    cy.visit('/admin')
    cy.get('input[placeholder="搜索标题/摘要/来源"]').type('自动化')
    cy.contains('搜索').click()
    cy.get('.el-table__row').should('have.length.at.least', 1)
    cy.get('.el-table__row').first().should('contain.text', '自动化')
  })

  it('可以预览新闻详情', () => {
    cy.visit('/admin')
    cy.get('.el-table__row').first().within(() => {
      cy.contains('预览').click()
    })
    cy.get('.el-dialog__title').should('contain', '新闻详情')
    cy.get('.el-dialog').should('contain.text', '摘要')
    cy.get('.el-dialog').should('contain.text', '正文')
    cy.contains('关闭').click()
  })
}) 