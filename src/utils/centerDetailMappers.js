/** 将 API 详情数据映射为成果/需求中心详情展示格式 */

export function formatFieldWithOther(fields, other) {
  const arr = Array.isArray(fields) ? fields.filter(f => f !== '其他') : []
  let result = arr.join('、')
  if (other && other.trim()) {
    result += (result ? '、' : '') + `其他：${other}`
  }
  return result || '其他'
}

export function formatTransferPreference(preference) {
  if (!preference) return '未指定'

  const parts = []
  if (preference.preferred_method) {
    parts.push(preference.preferred_method)
  }

  if (preference.tech_transfer?.enabled && preference.tech_transfer.expected_fee) {
    parts.push(`预期费用：${preference.tech_transfer.expected_fee}万元`)
  } else if (preference.tech_license?.enabled && preference.tech_license.expected_fee) {
    parts.push(`预期费用：${preference.tech_license.expected_fee}万元`)
  } else if (preference.tech_investment?.enabled && preference.tech_investment.valuation) {
    parts.push(`估值：${preference.tech_investment.valuation}万元`)
  }
  if (preference.other) {
    parts.push(`其他：${preference.other}`)
  }

  return parts.length > 0 ? parts.join('，') : '未指定'
}

export function formatExpectedCompleteDate(dateObj) {
  if (!dateObj || !dateObj.year) return null
  if (dateObj.month) {
    return `${dateObj.year}年${dateObj.month}月`
  }
  return `${dateObj.year}年`
}

function formatRegion(region) {
  if (!region) return '-'
  if (typeof region === 'string') return region || '-'
  const province = region.province || ''
  const city = region.city || ''
  if (province && city && city !== province) {
    return `${province}${city}`
  }
  return province || city || '-'
}

export function mapAchievementToCenterDetail(item) {
  if (!item) return null

  const desc = item.description || {}
  const tp = item.transfer_preference || {}

  return {
    id: item.achievement_code || item.achievementNumber || item.id || '-',
    title: item.achievement_name || item.title || '-',
    owner: item.owner || item.holder || '未知',
    field: formatFieldWithOther(item.tech_fields || item.technologyFields, item.tech_fields_other || item.otherTechnologyField),
    maturity: item.tech_maturity || item.maturity || '未知',
    transferDisplay: formatFieldWithOther(item.transfer_methods || item.transferMethods, item.transfer_methods_other || item.otherTransferMethod) || '未指定',
    region: formatRegion(item.region),
    summary: desc.summary || item.summary || '-',
    advantage: desc.advantages || item.advantages || '-',
    innovation: desc.innovation_level || item.innovationLevel || '-',
    compare: desc.advantages || item.advantages || '-',
    indicator: desc.core_indicators || item.coreTechnicalIndicators || '-',
    ipr: desc.intellectual_property || item.intellectualProperties || '-',
    collab: formatTransferPreference(tp),
    deadline: formatExpectedCompleteDate(tp.expected_complete_date) || item.expectedCompletionDate || '未指定'
  }
}

export function mapRequirementToCenterDetail(item) {
  if (!item) return null

  const desc = item.description || {}
  const budget = desc.budget

  return {
    id: item.demand_code || item.id || '-',
    title: item.demand_name || '-',
    org: item.company_name || '未知',
    region: formatRegion(item.region),
    field: formatFieldWithOther(item.tech_fields, item.tech_fields_other),
    type: formatFieldWithOther(item.demand_types, item.demand_types_other),
    status: item.match_status || '待对接',
    budget: budget != null && budget !== '' ? `${budget}万元` : '未指定',
    overview: desc.overview || '-',
    issues: desc.target_problems || '-'
  }
}
