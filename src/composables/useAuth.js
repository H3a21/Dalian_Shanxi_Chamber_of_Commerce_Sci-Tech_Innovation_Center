import { reactive, computed } from 'vue'
import request from '../utils/request'
import { ElMessage } from 'element-plus'

// 从localStorage初始化用户状态
const state = reactive({
  token: localStorage.getItem('token') || '',
  user: JSON.parse(localStorage.getItem('user') || 'null'),
  showLoginModal: false,
  targetRoute: null,
  showLoginPrompt: false,
  loginPromptPath: ''
})

// 是否已登录
const isLoggedIn = computed(() => !!state.token)

// 用户名显示
const username = computed(() => state.user?.username || state.user?.phone || '')

// 是否已实名认证
const isVerified = computed(() => {
  return !!(state.user?.real_name && state.user?.id_card)
})

// 获取用户完整信息（含实名认证状态）
const fetchUserProfile = async () => {
  if (!state.token) return
  try {
    const res = await request.get('/api/me')
    if (res.code === 200) {
      const userData = {
        id: state.user?.id,
        username: state.user?.username,
        phone: state.user?.phone,
        role: state.user?.role,
        status: state.user?.status,
        ...res.data
      }
      state.user = {
        id: userData.id,
        username: userData.username,
        phone: userData.phone,
        role: userData.role,
        status: userData.status,
        real_name: userData.real_name || '',
        id_card: userData.id_card || ''
      }
      localStorage.setItem('user', JSON.stringify(state.user))
    }
  } catch (error) {
    console.error('获取用户信息失败:', error)
  }
}

// 实名认证检查 - 未认证则提示并返回 false
const requireVerified = () => {
  if (!isVerified.value) {
    ElMessage.warning({
      message: '请前往「个人中心→基本信息」完成实名认证，否则无法使用网站全部功能，谢谢您的配合~',
      duration: 2000
    })
    return false
  }
  return true
}

// 初始化时如果已登录，获取用户完整信息
if (state.token) {
  fetchUserProfile()
}

// 登录方法
const login = async (account, password) => {
  try {
    const res = await request.post('/api/login', {
      username: account,
      password
    })
    if (res.code === 200) {
      const { token, user_id, username, phone, role, status } = res.data
      state.token = token
      state.user = { id: user_id, username, phone, role, status }
      localStorage.setItem('token', token)
      localStorage.setItem('user', JSON.stringify({ id: user_id, username, phone, role, status }))
      // 获取完整用户信息（含实名认证状态）
      fetchUserProfile()
      ElMessage({
        message: '登录成功',
        type: 'success',
        duration: 2000
      })
      closeLoginModal()
      return { success: true }
    } else {
      // 实际上拦截器已经处理了非200情况，但这里仍做处理
      return { success: false, message: res.message }
    }
  } catch (error) {
    return { success: false, message: error.message }
  }
}

// 注册方法
const register = async (phone, password, smsCode, username = '') => {
  try {
    const res = await request.post('/api/register', {
      phone,
      password,
      sms_code: smsCode,
      username: username || undefined
    })
    if (res.code === 200) {
      ElMessage({
        message: '注册成功，请登录',
        type: 'success',
        duration: 2000
      })
      return { success: true }
    } else {
      return { success: false, message: res.message }
    }
  } catch (error) {
    return { success: false, message: error.message }
  }
}

// 发送短信验证码
const sendSmsCode = async (phone, type = 'register') => {
  try {
    const res = await request.post('/api/send_sms', {
      phone,
      type
    })
    if (res.code === 200) {
      ElMessage({
        message: '验证码已发送',
        type: 'success',
        duration: 2000
      })
      return { success: true }
    } else {
      return { success: false, message: res.message }
    }
  } catch (error) {
    return { success: false, message: error.message }
  }
}

// 检查手机号是否已注册
const checkPhoneRegistered = async (phone) => {
  try {
    const res = await request.post('/api/check_phone', { phone })
    if (res.code === 200) {
      return { success: true, registered: res.registered }
    } else {
      return { success: false, message: res.message }
    }
  } catch (error) {
    return { success: false, message: error.message }
  }
}

// 重置密码
const resetPassword = async (phone, newPassword, smsCode) => {
  try {
    const res = await request.post('/api/reset_password', {
      phone,
      new_password: newPassword,
      sms_code: smsCode
    })
    if (res.code === 200) {
      ElMessage({
        message: '密码重置成功',
        type: 'success',
        duration: 2000
      })
      return { success: true }
    } else {
      return { success: false, message: res.message }
    }
  } catch (error) {
    return { success: false, message: error.message }
  }
}

// 退出登录
const logout = () => {
  state.token = ''
  state.user = null
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  ElMessage({
    message: '已退出登录',
    type: 'info',
    duration: 2000
  })
}

// 打开登录模态框
const openLoginModal = (targetRoute = null) => {
  state.targetRoute = targetRoute
  state.showLoginModal = true
}

// 关闭登录模态框
const closeLoginModal = () => {
  state.showLoginModal = false
  state.targetRoute = null
}

// 打开登录提示弹窗
const openLoginPrompt = (path = '') => {
  state.loginPromptPath = path
  state.showLoginPrompt = true
}

// 关闭登录提示弹窗
const closeLoginPrompt = () => {
  state.showLoginPrompt = false
  state.loginPromptPath = ''
}

// 命名导出，供路由守卫使用
export { state, openLoginPrompt }

export default function useAuth() {
  return {
    state,
    isLoggedIn,
    username,
    isVerified,
    login,
    register,
    sendSmsCode,
    checkPhoneRegistered,
    resetPassword,
    logout,
    openLoginModal,
    closeLoginModal,
    openLoginPrompt,
    closeLoginPrompt,
    fetchUserProfile,
    requireVerified
  }
}