Cypress.on('uncaught:exception', (err) => {
  if (err.message.includes('ResizeObserver loop')) {
    return false; // 忽略此类异常
  }
});

describe('产品列表页', () => {
  beforeEach(() => {
    // 假设路由为 /products，根据实际路由调整
    cy.visit('/products')
  })

  it('应能正常渲染产品卡片', () => {
    cy.get('.product-card').should('have.length.greaterThan', 0)
    cy.get('.product-card').first().within(() => {
      cy.get('img').should('be.visible')
      cy.get('h3').should('not.be.empty')
      cy.get('.price').should('contain', '￥')
    })
  })

  it('分页切换应能显示不同产品', () => {
    cy.get('.product-card').then(cards => {
      const firstPageFirstCard = cards[0].innerText
      cy.get('.el-pagination .btn-next').click()
      cy.wait(300)
      cy.get('.product-card').first().should(card => {
        expect(card.text()).not.to.eq(firstPageFirstCard)
      })
    })
  })

  it('分类筛选应能过滤产品', () => {
    cy.get('.el-select').click()
    cy.get('.el-select-dropdown__item').contains('音频设备').click()
    cy.get('.product-card').should('have.length.greaterThan', 0)
    cy.get('.product-card h3').each($el => {
      cy.wrap($el).invoke('text').then(name => {
        expect(['蓝牙耳机', '降噪耳机', '蓝牙音箱']).to.include(name.trim())
      })
    })
    cy.get('.el-select').click()
    cy.get('.el-select-dropdown__item').contains('全部').click()
    cy.get('.product-card').should('have.length.greaterThan', 0)
  })
}) 