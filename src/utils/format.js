/**
 * 数字格式化工具函数
 */

/**
 * 将数字格式化为千位分隔符格式（从右往左每三位加逗号）
 * @param {number|string} num - 要格式化的数字
 * @param {number} decimals - 保留小数位数
 * @returns {string} 格式化后的字符串
 */
export function formatNumberWithCommas(num, decimals = 0) {
  if (num === null || num === undefined || num === '') return ''

  // 转换为数字
  const number = Number(num)
  if (isNaN(number)) return String(num)

  // 处理小数部分
  const fixedNum = decimals > 0 ? number.toFixed(decimals) : Math.round(number).toString()

  // 分割整数和小数部分
  const parts = fixedNum.split('.')
  let integerPart = parts[0]
  const decimalPart = parts.length > 1 ? `.${parts[1]}` : ''

  // 添加千位分隔符
  integerPart = integerPart.replace(/\B(?=(\d{3})+(?!\d))/g, ',')

  return integerPart + decimalPart
}

/**
 * 将千位分隔符格式的数字字符串转换为数字
 * @param {string} str - 带千位分隔符的字符串
 * @returns {number} 转换后的数字
 */
export function parseNumberWithCommas(str) {
  if (!str) return null
  // 移除所有逗号和非数字字符（除小数点外）
  const numStr = str.replace(/,/g, '')
  const num = parseFloat(numStr)
  return isNaN(num) ? null : num
}

/**
 * 验证百分比是否在0-100范围内
 * @param {number|string} percent - 百分比值
 * @returns {boolean} 是否在有效范围内
 */
export function isValidPercent(percent) {
  if (percent === null || percent === undefined || percent === '') return true // 空值不验证

  const num = Number(percent)
  if (isNaN(num)) return false

  return num >= 0 && num <= 100
}

/**
 * 获取百分比验证错误信息
 * @param {number|string} percent - 百分比值
 * @returns {string} 错误信息，空字符串表示有效
 */
export function getPercentError(percent) {
  if (percent === null || percent === undefined || percent === '') return ''

  const num = Number(percent)
  if (isNaN(num)) return '请输入有效的数字'

  if (num < 0) return '百分比不能小于0%'
  if (num > 100) return '百分比不能超过100%'

  return ''
}