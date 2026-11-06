<template>
  <div class="profile-page">
    <main class="page-section">
      <div class="profile-layout">
        <div class="profile-card">
          <h2 class="profile-title">个人中心</h2>
          <div class="profile-info">
            <div class="info-item">
              <span class="label">用户名：</span>
              <span class="value">{{ user.username || '未设置' }}</span>
            </div>
            <div class="info-item">
              <span class="label">手机号：</span>
              <span class="value">{{ user.phone }}</span>
            </div>
            <div class="info-item">
              <span class="label">角色：</span>
              <span class="value">{{ user.role === 'admin' ? '管理员' : '普通用户' }}</span>
            </div>
          </div>
          <div class="profile-actions">
            <button class="action-btn" @click="handleLogout">退出登录</button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import useAuth from '../composables/useAuth'

const router = useRouter()
const auth = useAuth()

const user = reactive({
  username: '',
  phone: '',
  role: '',
  status: ''
})

onMounted(() => {
  if (!auth.isLoggedIn.value) {
    router.push('/auth?tab=login')
    return
  }
  Object.assign(user, auth.state.user)
})

function handleLogout() {
  auth.logout()
  router.push('/')
}
</script>

<style scoped>
.profile-layout {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 70px);
  padding: 40px 0;
}
.profile-card {
  background: var(--white);
  width: 500px;
  padding: 40px;
  border-radius: 8px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.08);
}
.profile-title {
  font-size: 24px;
  color: var(--text-main);
  margin-bottom: 30px;
  text-align: center;
}
.profile-info {
  margin-bottom: 30px;
}
.info-item {
  display: flex;
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--border-color);
}
.info-item:last-child {
  border-bottom: none;
}
.label {
  width: 100px;
  color: var(--text-muted);
  font-weight: 500;
}
.value {
  flex: 1;
  color: var(--text-main);
}
.profile-actions {
  text-align: center;
}
.action-btn {
  background-color: var(--theme-blue);
  color: var(--white);
  border: none;
  padding: 12px 30px;
  border-radius: 30px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}
.action-btn:hover {
  background-color: #0073e6;
}
</style>