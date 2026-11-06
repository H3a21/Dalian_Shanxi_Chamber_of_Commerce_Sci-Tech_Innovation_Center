<template>
  <div class="forgot-page">
    <main class="page-section">
      <div class="forgot-layout">
        <div class="forgot-card">
          <h2 class="forgot-title">忘记密码</h2>
          <p class="forgot-subtitle">请输入您的手机号，我们将发送验证码帮助您重置密码</p>

          <div class="forgot-form">
            <div class="input-group" :class="{ error: forgotErrors.phone }">
              <div class="input-wrapper">
                <svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="5" y="2" width="14" height="20" rx="2" ry="2"></rect><line x1="12" y1="18" x2="12.01" y2="18"></line></svg>
                <input type="text" placeholder="请输入手机号" v-model="forgotForm.phone" @input="validatePhone">
              </div>
              <div class="error-msg" v-if="forgotErrors.phone">{{ forgotErrors.phone }}</div>
            </div>
            <div class="input-group verify-group" :class="{ error: forgotErrors.code }">
              <div class="input-wrapper">
                <svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
                <input type="text" placeholder="请输入验证码" v-model="forgotForm.code">
              </div>
              <button class="get-code-btn" @click="sendForgotCode" :disabled="forgotCodeDisabled">
                {{ forgotCodeBtnText }}
              </button>
              <div class="error-msg" v-if="forgotErrors.code">{{ forgotErrors.code }}</div>
            </div>
            <div class="input-group" :class="{ error: forgotErrors.password }">
              <div class="input-wrapper">
                <svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
                <input type="password" placeholder="请输入新密码" v-model="forgotForm.password" @input="validatePassword">
              </div>
              <div class="error-msg" v-if="forgotErrors.password">{{ forgotErrors.password }}</div>
            </div>
            <div class="input-group" :class="{ error: forgotErrors.confirm }">
              <div class="input-wrapper">
                <svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
                <input type="password" placeholder="请确认新密码" v-model="forgotForm.confirm" @input="validateConfirm">
              </div>
              <div class="error-msg" v-if="forgotErrors.confirm">{{ forgotErrors.confirm }}</div>
            </div>
            <button class="submit-btn" @click="handleForgot" :disabled="forgotLoading">
              {{ forgotLoading ? '重置中...' : '重置密码' }}
            </button>
          </div>

          <div class="back-to-login">
            <router-link to="/auth?tab=login">返回登录</router-link>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import useAuth from '../composables/useAuth'

const router = useRouter()
const auth = useAuth()

// 忘记密码表单
const forgotForm = reactive({
  phone: '',
  code: '',
  password: '',
  confirm: ''
})
const forgotErrors = reactive({
  phone: '',
  code: '',
  password: '',
  confirm: ''
})
const forgotLoading = ref(false)
const forgotCodeDisabled = ref(false)
const forgotCodeCountdown = ref(0)
const phoneCheckTimer = ref(null)
const forgotCodeBtnText = computed(() => {
  if (forgotCodeCountdown.value > 0) {
    return `${forgotCodeCountdown.value}秒后重新获取`
  }
  return '获取验证码'
})

// 验证手机号
function validatePhone() {
  if (!forgotForm.phone) {
    forgotErrors.phone = '请输入手机号'
    return
  } else if (!/^1\d{10}$/.test(forgotForm.phone)) {
    forgotErrors.phone = '手机号格式不正确'
    return
  } else {
    forgotErrors.phone = ''
  }

  // 防抖检查手机号是否已注册
  if (phoneCheckTimer.value) {
    clearTimeout(phoneCheckTimer.value)
    phoneCheckTimer.value = null
  }

  phoneCheckTimer.value = setTimeout(async () => {
    // 防止手机号被清空后发送请求
    if (!forgotForm.phone || !/^1\d{10}$/.test(forgotForm.phone)) {
      return
    }
    const res = await auth.checkPhoneRegistered(forgotForm.phone)
    if (res.success && !res.registered) {
      forgotErrors.phone = '该手机号未注册，请先注册'
    } else if (!res.success) {
      // 检查失败，不显示错误，避免干扰用户
      console.error('检查手机号失败:', res.message)
    }
  }, 500)
}

// 验证密码
function validatePassword() {
  if (!forgotForm.password) {
    forgotErrors.password = '请输入密码'
  } else if (forgotForm.password.length < 6) {
    forgotErrors.password = '密码长度至少6位'
  } else {
    forgotErrors.password = ''
  }
}

// 验证确认密码
function validateConfirm() {
  if (!forgotForm.confirm) {
    forgotErrors.confirm = '请确认密码'
  } else if (forgotForm.password !== forgotForm.confirm) {
    forgotErrors.confirm = '两次输入的密码不一致'
  } else {
    forgotErrors.confirm = ''
  }
}

// 发送忘记密码验证码
async function sendForgotCode() {
  validatePhone()
  if (forgotErrors.phone) return

  forgotCodeDisabled.value = true
  forgotCodeCountdown.value = 60

  const res = await auth.sendSmsCode(forgotForm.phone, 'reset')
  if (res.success) {
    // 开始倒计时
    const timer = setInterval(() => {
      forgotCodeCountdown.value--
      if (forgotCodeCountdown.value <= 0) {
        clearInterval(timer)
        forgotCodeDisabled.value = false
      }
    }, 1000)
  } else {
    forgotCodeDisabled.value = false
    forgotCodeCountdown.value = 0
  }
}

// 处理忘记密码
async function handleForgot() {
  // 验证
  validatePhone()
  validatePassword()
  validateConfirm()

  if (!forgotForm.code) {
    forgotErrors.code = '请输入验证码'
    return
  }

  // 如果有错误，停止
  if (forgotErrors.phone || forgotErrors.password || forgotErrors.confirm || forgotErrors.code) {
    return
  }

  forgotLoading.value = true
  const res = await auth.resetPassword(forgotForm.phone, forgotForm.password, forgotForm.code)
  forgotLoading.value = false

  if (res.success) {
    // 重置成功，跳转到登录页面
    router.push('/auth?tab=login')
    // 清空表单
    forgotForm.phone = ''
    forgotForm.code = ''
    forgotForm.password = ''
    forgotForm.confirm = ''
  }
}
</script>

<style scoped>
.forgot-layout {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 70px);
  padding: 40px 0;
}
.forgot-card {
  background: var(--white);
  width: 420px;
  padding: 40px;
  border-radius: 8px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.08);
}
.forgot-title {
  font-size: 24px;
  color: var(--text-main);
  text-align: center;
  margin-bottom: 10px;
}
.forgot-subtitle {
  font-size: 14px;
  color: var(--text-muted);
  text-align: center;
  margin-bottom: 30px;
}

/* 表单内容区 */
.forgot-form {
  margin-bottom: 25px;
}

.input-group {
  position: relative;
  margin-bottom: 25px;
  padding-bottom: 0;
}

/* 图标定位 */
.input-icon {
  position: absolute;
  left: 15px;
  top: 50%;
  transform: translateY(-50%);
  width: 18px;
  height: 18px;
  color: #c0c4cc;
}

/* 输入框样式 */
.input-group input[type="text"],
.input-group input[type="password"] {
  width: 100%;
  padding: 14px 15px 14px 45px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
  color: var(--text-main);
  outline: none;
  transition: border-color 0.3s;
}

.input-group input:focus {
  border-color: var(--theme-blue);
}

/* 错误状态 */
.input-group.error input {
  border-color: #ff4d4f;
}
.input-group.error .input-icon {
  color: #ff4d4f;
}
.error-msg {
  color: #ff4d4f;
  font-size: 12px;
  position: absolute;
  top: 100%;
  left: 45px;
  margin-top: 0;
}
.verify-group .error-msg {
  left: 0;
  padding-left: 45px;
}

/* 获取验证码组 */
.verify-group {
  display: flex;
  gap: 15px;
}
.verify-group input {
  flex: 1;
}
.get-code-btn {
  background-color: transparent;
  color: var(--theme-blue);
  border: 1px solid var(--theme-blue);
  border-radius: 4px;
  padding: 0 15px;
  cursor: pointer;
  font-size: 14px;
  white-space: nowrap;
  transition: all 0.3s;
}
.get-code-btn:hover:not(:disabled) {
  background-color: #e6f7ff;
}
.get-code-btn:disabled {
  color: #ccc;
  border-color: #ccc;
  cursor: not-allowed;
}

/* 提交大按钮 */
.submit-btn {
  width: 100%;
  background-color: var(--theme-blue);
  color: var(--white);
  border: none;
  padding: 14px;
  border-radius: 30px;
  font-size: 16px;
  cursor: pointer;
  letter-spacing: 2px;
  transition: background-color 0.3s;
}
.submit-btn:hover:not(:disabled) {
  background-color: #0073e6;
}
.submit-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

/* 返回登录链接 */
.back-to-login {
  text-align: center;
  margin-top: 20px;
}
.back-to-login a {
  color: var(--theme-blue);
  font-size: 14px;
  text-decoration: none;
}
.back-to-login a:hover {
  text-decoration: underline;
}

/* ================= 响应式 ================= */
@media (max-width: 768px) {
  .forgot-layout { padding: 12px; min-height: calc(100vh - 60px); }
  .forgot-card { max-width: 100%; padding: 24px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); }
  .forgot-title { font-size: 22px; }
  .forgot-subtitle { font-size: 13px; }
  .verify-group { flex-direction: column; gap: 8px; }
  .get-code-btn { width: 100%; padding: 10px; text-align: center; }
  .submit-btn { font-size: 14px; padding: 12px; }
}

@media (max-width: 480px) {
  .forgot-card { padding: 16px; }
  .forgot-layout { padding: 8px; }
}
</style>