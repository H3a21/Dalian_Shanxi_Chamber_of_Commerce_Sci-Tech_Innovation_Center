<template>
  <div class="captcha-fullscreen">
    <!-- 背景装饰 -->
    <div class="captcha-bg">
      <div class="bg-circle c1"></div>
      <div class="bg-circle c2"></div>
      <div class="bg-circle c3"></div>
      <div class="bg-pattern"></div>
    </div>

    <div class="captcha-container">
      <div class="captcha-card">
        <!-- 顶部图标 -->
        <div class="card-icon">
          <svg viewBox="0 0 72 72" width="72" height="72" fill="none">
            <circle cx="36" cy="36" r="36" fill="#e6f7ff" />
            <circle cx="36" cy="36" r="28" fill="#1890ff" fill-opacity="0.1" stroke="#1890ff" stroke-width="2"/>
            <path d="M32 38l4 4 8-10" stroke="#1890ff" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>
            <circle cx="36" cy="36" r="10" stroke="#1890ff" stroke-width="1.5" stroke-dasharray="3 3" fill="none"/>
          </svg>
        </div>

        <h1 class="card-title">安全验证</h1>
        <p class="card-desc">检测到异常操作，请完成以下验证后继续访问</p>

        <!-- 验证区域 -->
        <div class="verify-box">
          <div class="math-area">
            <div class="math-label">请计算</div>
            <div class="math-row">
              <span class="math-num">{{ num1 }}</span>
              <span class="math-op">+</span>
              <span class="math-num">{{ num2 }}</span>
              <span class="math-op">=</span>
              <span class="math-input-wrap">
                <input
                  ref="inputRef"
                  type="text"
                  class="math-input"
                  v-model="userAnswer"
                  maxlength="3"
                  @keyup.enter="verify"
                  autofocus
                />
              </span>
            </div>
          </div>

          <transition name="err">
            <div class="error-msg" v-if="errorMsg">{{ errorMsg }}</div>
          </transition>

          <button class="verify-btn" @click="verify" :disabled="verifying">
            <span v-if="!verifying">确认验证</span>
            <span v-else class="btn-loading">
              <span class="spinner"></span> 验证中...
            </span>
          </button>
        </div>

        <p class="card-footer-text">
          验证通过后将自动返回
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { resetClickGuard } from '../composables/useClickGuard'

const API_BASE = ''

export default {
  name: 'CaptchaView',
  setup() {
    const router = useRouter()
    const route = useRoute()
    const inputRef = ref(null)
    const userAnswer = ref('')
    const errorMsg = ref('')
    const verifying = ref(false)

    const num1 = ref(0)
    const num2 = ref(0)
    let correctAnswer = 0

    // ----- 防止回退 -----
    let popStateHandler = null

    function trapBackButton() {
      window.history.pushState({ captcha: true }, '')
      window.history.pushState({ captcha: true }, '')
      window.history.pushState({ captcha: true }, '')

      popStateHandler = () => {
        window.history.pushState({ captcha: true }, '')
      }
      window.addEventListener('popstate', popStateHandler)
    }

    function cleanupTrap() {
      if (popStateHandler) {
        window.removeEventListener('popstate', popStateHandler)
        popStateHandler = null
      }
    }

    // ----- 验证逻辑 -----
    function generateQuestion() {
      num1.value = Math.floor(Math.random() * 50) + 10
      num2.value = Math.floor(Math.random() * 40) + 10
      correctAnswer = num1.value + num2.value
    }

    function verify() {
      if (verifying.value) return
      const answer = parseInt(userAnswer.value)
      if (isNaN(answer)) {
        errorMsg.value = '请输入计算结果'
        return
      }
      verifying.value = true
      errorMsg.value = ''

      setTimeout(() => {
        if (answer === correctAnswer) {
          cleanupTrap()
          resetClickGuard()
          // 通知后端此 IP 已完成验证
          fetch(`${API_BASE}/api/captcha/verify`, { method: 'POST' }).catch(() => {})
          const redirect = route.query.redirect || '/'
          router.replace(redirect)
        } else {
          errorMsg.value = '计算结果不正确，请重新输入'
          userAnswer.value = ''
          verifying.value = false
          generateQuestion()
          nextTick(() => inputRef.value?.focus())
        }
      }, 600)
    }

    onMounted(() => {
      generateQuestion()
      trapBackButton()
      nextTick(() => inputRef.value?.focus())
    })

    onBeforeUnmount(() => {
      cleanupTrap()
    })

    return { num1, num2, userAnswer, errorMsg, verifying, inputRef, verify }
  }
}
</script>

<style scoped>
/* ========== 全屏容器 ========== */
.captcha-fullscreen {
  position: fixed;
  inset: 0;
  z-index: 99999;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f5ff;
  overflow: hidden;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
}

/* ========== 背景装饰 ========== */
.captcha-bg {
  position: absolute;
  inset: 0;
  overflow: hidden;
}

.bg-circle {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
}

.c1 {
  width: 500px;
  height: 500px;
  background: rgba(24, 144, 255, 0.08);
  top: -200px;
  right: -100px;
  animation: floatA 8s ease-in-out infinite;
}

.c2 {
  width: 400px;
  height: 400px;
  background: rgba(9, 109, 217, 0.06);
  bottom: -150px;
  left: -100px;
  animation: floatB 10s ease-in-out infinite;
}

.c3 {
  width: 250px;
  height: 250px;
  background: rgba(24, 144, 255, 0.04);
  top: 40%;
  left: 60%;
  animation: floatC 12s ease-in-out infinite;
}

.bg-pattern {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(24, 144, 255, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(24, 144, 255, 0.03) 1px, transparent 1px);
  background-size: 48px 48px;
}

@keyframes floatA {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(-30px, 30px); }
}
@keyframes floatB {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(30px, -20px); }
}
@keyframes floatC {
  0%, 100% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(-20px, 10px) scale(1.1); }
}

/* ========== 卡片 ========== */
.captcha-container {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 420px;
  padding: 20px;
}

.captcha-card {
  background: #ffffff;
  border-radius: 16px;
  padding: 44px 36px 32px;
  text-align: center;
  box-shadow: 0 8px 40px rgba(24, 144, 255, 0.1), 0 2px 12px rgba(0, 0, 0, 0.06);
  animation: cardUp 0.45s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes cardUp {
  from { opacity: 0; transform: translateY(30px) scale(0.97); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

/* 图标 */
.card-icon {
  margin-bottom: 20px;
}

/* 标题 */
.card-title {
  font-size: 24px;
  font-weight: 700;
  color: rgba(0, 0, 0, 0.85);
  margin: 0 0 8px;
  letter-spacing: 0.5px;
}

.card-desc {
  font-size: 14px;
  color: rgba(0, 0, 0, 0.45);
  margin: 0 0 28px;
  line-height: 1.6;
}

/* ========== 验证区域 ========== */
.verify-box {
  background: #fafbff;
  border-radius: 12px;
  padding: 24px 20px 20px;
  border: 1px solid #f0f4ff;
}

.math-area {
  margin-bottom: 20px;
}

.math-label {
  font-size: 13px;
  color: rgba(0, 0, 0, 0.45);
  margin-bottom: 16px;
}

.math-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.math-num {
  font-size: 34px;
  font-weight: 700;
  color: rgba(0, 0, 0, 0.85);
  min-width: 40px;
  text-align: center;
}

.math-op {
  font-size: 24px;
  color: #1890ff;
  font-weight: 400;
}

.math-input-wrap {
  position: relative;
  display: inline-flex;
}

.math-input {
  width: 68px;
  height: 48px;
  text-align: center;
  font-size: 26px;
  font-weight: 700;
  color: rgba(0, 0, 0, 0.85);
  background: #ffffff;
  border: 2px solid #e8e8e8;
  border-radius: 10px;
  outline: none;
  transition: all 0.25s;
  -moz-appearance: textfield;
  box-sizing: border-box;
}
.math-input::-webkit-outer-spin-button,
.math-input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
.math-input:focus {
  border-color: #1890ff;
  box-shadow: 0 0 0 3px rgba(24, 144, 255, 0.1);
}

/* 错误信息 */
.error-msg {
  color: #ff4d4f;
  font-size: 13px;
  margin-bottom: 16px;
  padding: 8px 16px;
  background: #fff2f0;
  border: 1px solid #ffccc7;
  border-radius: 8px;
}

.err-enter-active,
.err-leave-active {
  transition: all 0.25s ease;
}
.err-enter-from,
.err-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

/* 按钮 */
.verify-btn {
  width: 100%;
  padding: 13px;
  background: #1890ff;
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.25s;
  position: relative;
  overflow: hidden;
}

.verify-btn:hover:not(:disabled) {
  background: #096dd9;
  transform: translateY(-1px);
  box-shadow: 0 8px 24px rgba(24, 144, 255, 0.35);
}

.verify-btn:active:not(:disabled) {
  transform: translateY(0);
}

.verify-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 按钮加载状态 */
.btn-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 底部文字 */
.card-footer-text {
  font-size: 12px;
  color: rgba(0, 0, 0, 0.25);
  margin: 20px 0 0;
}

/* ========== 响应式 ========== */
@media (max-width: 480px) {
  .captcha-card {
    padding: 32px 20px 28px;
  }
  .card-title {
    font-size: 20px;
  }
  .card-desc {
    font-size: 13px;
  }
  .math-num {
    font-size: 28px;
    min-width: 32px;
  }
  .math-input {
    width: 56px;
    height: 42px;
    font-size: 22px;
  }
  .verify-btn {
    padding: 12px;
    font-size: 15px;
  }
}
</style>
