const CLICK_WINDOW = 3000
const MAX_CLICKS = 5

const clickTimestamps = []
let locked = false
let redirectPath = '/'
let notifying = false

const API_BASE = ''

export function registerClick() {
  if (locked) return true

  const now = Date.now()
  // 移除超出时间窗口的点击记录
  let i = 0
  while (i < clickTimestamps.length) {
    if (now - clickTimestamps[i] > CLICK_WINDOW) {
      clickTimestamps.splice(i, 1)
    } else {
      i++
    }
  }
  clickTimestamps.push(now)

  if (clickTimestamps.length >= MAX_CLICKS) {
    locked = true
    // 通知后端记录此 IP 需要验证
    if (!notifying) {
      notifying = true
      fetch(`${API_BASE}/api/captcha/trigger`, { method: 'POST' }).catch(() => {})
    }
    return true
  }
  return false
}

export function isClickLocked() {
  return locked
}

export function resetClickGuard() {
  clickTimestamps.length = 0
  locked = false
  notifying = false
}

export function setRedirectPath(path) {
  redirectPath = path
}

export function getRedirectPath() {
  return redirectPath
}
