import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建axios实例
const request = axios.create({
  baseURL: process.env.VUE_APP_API_BASE_URL || '', // Flask后端地址（默认同域，通过 .env 配置）
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器：添加token
request.interceptors.request.use(
  config => {
    // 从localStorage获取token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器：处理错误和消息
request.interceptors.response.use(
  response => {
    const res = response.data
    // 根据后端返回的code判断
    if (res.code === 200) {
      return res
    } else {
      // 非200 code，显示错误消息
      ElMessage({
        message: res.message || res.msg || '请求失败',
        type: 'error',
        duration: 3000
      })
      const err = new Error(res.message || res.msg || 'Error')
      err.response = { data: res }
      return Promise.reject(err)
    }
  },
  error => {
    // HTTP状态码错误
    let message = '网络错误'
    if (error.response) {
      // 优先使用后端返回的错误消息
      if (error.response.data && error.response.data.message) {
        message = error.response.data.message
      } else {
        switch (error.response.status) {
          case 400:
            message = '请求参数错误'
            break
          case 401:
            // 对于登录接口，不清除token，因为用户还没登录
            if (!error.config.url.includes('/api/login')) {
              // 检查是否有token：有token但401说明过期，跳转登录；无token则不跳转
              const currentToken = localStorage.getItem('token')
              if (currentToken) {
                message = '未授权，请重新登录'
                // 清除token并跳转到登录页
                localStorage.removeItem('token')
                localStorage.removeItem('user')
                window.location.href = '/auth?tab=login'
              } else {
                // 未登录状态访问接口，静默处理，不跳转
                message = error.response.data?.message || '请先登录后操作'
              }
            } else {
              message = '账号或密码错误' // 默认消息，会被后端具体消息覆盖
            }
            break
          case 422:
            // JWT token无效或格式错误，清除token并跳转登录
            message = '登录已过期，请重新登录'
            localStorage.removeItem('token')
            localStorage.removeItem('user')
            window.location.href = '/auth?tab=login'
            break
          case 403:
            message = '拒绝访问'
            break
          case 404:
            message = '请求地址不存在'
            break
          case 500:
            message = '服务器内部错误'
            break
          default:
            message = '网络错误'
        }
      }
    }
    ElMessage({
      message,
      type: 'error',
      duration: 3000
    })
    // 创建一个新的错误对象，包含正确的消息
    const newError = new Error(message)
    newError.response = error.response
    newError.config = error.config
    newError.request = error.request
    return Promise.reject(newError)
  }
)

export default request