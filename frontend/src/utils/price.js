export function formatPrice(price) {
  if (price === null || price === undefined || price === '') return ''
  const text = String(price).trim()
  if (/^\d+(\.\d+)?$/.test(text)) return `￥${text}`
  return text
}
