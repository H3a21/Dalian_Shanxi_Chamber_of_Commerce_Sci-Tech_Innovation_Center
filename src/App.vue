<template>
  <div id="app">
    <header v-if="$route.path !== '/captcha'">
      <div class="header-container">
        <div class="logo" @click="$router.push('/')">
          <img v-if="siteConfig.site_logo" :src="resolveImageUrl(siteConfig.site_logo)" class="logo-img" @error="e => e.target.style.display='none'" />
          <el-icon v-else class="logo-icon"><Lightning /></el-icon>
          {{ siteConfig.site_name || '大连山西商会科创中心' }}
        </div>
        <ul class="nav-menu" v-if="userRole !== 'agent'">
          <li
            v-for="(item, index) in siteConfig.nav_menu"
            :key="index"
            :class="{ active: isActive(item.path) }"
            @click="navigate(item.path)"
          >{{ item.name }}</li>
        </ul>
        <div class="auth-actions">
          <template v-if="!isLoggedIn">
            <span @click="$router.push({ path: '/auth', query: { tab: 'login' } })">登录</span> /
            <span @click="$router.push({ path: '/auth', query: { tab: 'register' } })">注册</span>
          </template>
          <template v-else>
            <!-- 消息图标下拉框（客服用户不显示） -->
            <el-dropdown v-if="userRole !== 'agent'" trigger="hover" @command="handleMessageCommand" class="message-dropdown">
              <span class="message-icon-wrapper">
                <el-icon class="message-icon"><Message /></el-icon>
                <span class="message-badge" v-if="unreadCount > 0">{{ unreadCount > 99 ? '99+' : unreadCount }}</span>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="all">查看所有消息</el-dropdown-item>
                  <el-dropdown-item v-for="msg in messageList" :key="msg.id" :command="msg.id" class="message-item" :class="msgTypeDotClass(msg)">
                    <div class="message-item-top">
                      <div class="message-title">{{ msg.title }}</div>
                    </div>
                    <div class="message-preview">{{ msg.content }}</div>
                    <div class="message-time">{{ msg.time }}</div>
                  </el-dropdown-item>
                  <el-dropdown-item v-if="messageList.length === 0" disabled>暂无消息</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
            <el-dropdown @command="handleCommand">
              <span class="user-dropdown">
                {{ username }}<el-icon class="el-icon--right"><arrow-down /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile" v-if="userRole !== 'agent'">个人中心</el-dropdown-item>
                  <el-dropdown-item command="logout">退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
            <span @click="openCustomerService" v-if="userRole !== 'agent'">{{ userRole === 'admin' ? '管理' : '客服' }}</span>
          </template>
          <!-- 手机端汉堡菜单按钮 -->
          <button class="hamburger-btn" @click="mobileMenuOpen = !mobileMenuOpen" :class="{ active: mobileMenuOpen }" aria-label="菜单">
            <span></span><span></span><span></span>
          </button>
        </div>
      </div>
      <!-- 手机端导航面板 -->
      <div class="mobile-nav-overlay" :class="{ active: mobileMenuOpen }" @click="mobileMenuOpen = false"></div>
      <div class="mobile-nav-panel" :class="{ active: mobileMenuOpen }">
        <ul class="mobile-nav-menu" v-if="userRole !== 'agent'">
          <li
            v-for="(item, index) in siteConfig.nav_menu"
            :key="index"
            :class="{ active: isActive(item.path) }"
            @click="navigate(item.path); mobileMenuOpen = false"
          >{{ item.name }}</li>
        </ul>
      </div>
    </header>

    <main :class="{ 'full-height': isAdminRoute }">
      <router-view />
    </main>

    <ChatWidget v-show="isLoggedIn && userRole !== 'admin' && userRole !== 'agent' && $route.path !== '/admin-chat' && $route.path !== '/captcha'" ref="chatWidgetRef" />

    <!-- 未登录提示弹窗 -->
    <el-dialog
      v-model="auth.state.showLoginPrompt"
      title="提示"
      width="420px"
      :close-on-click-modal="false"
      :show-close="true"
      :z-index="9999"
      @close="auth.closeLoginPrompt"
      class="login-prompt-dialog"
    >
      <div class="login-prompt-content">
        <div class="prompt-icon">🔒</div>
        <p class="prompt-text">您尚未登录，请登录后继续操作</p>
        <p class="prompt-subtext">登录后可享受更多服务</p>
        <div class="prompt-actions">
          <el-button class="login-btn" type="primary" @click="goToLogin">登录</el-button>
          <el-button class="register-btn" @click="goToRegister">注册</el-button>
        </div>
      </div>
    </el-dialog>

  </div>
</template>

<script>
import { computed, ref, provide, watch, onBeforeUnmount, onMounted, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElDropdown, ElDropdownMenu, ElDropdownItem, ElIcon, ElDialog, ElButton } from 'element-plus'
import { ArrowDown, Message, Lightning } from '@element-plus/icons-vue'
import useAuth from './composables/useAuth'
import ChatWidget from './components/ChatWidget.vue'
import request from './utils/request'
import { io } from 'socket.io-client'
import { registerClick, setRedirectPath } from './composables/useClickGuard'

export default {
  name: 'App',
  components: {
    ElDropdown,
    ElDropdownMenu,
    ElDropdownItem,
    ElIcon,
    ElDialog,
    ElButton,
    ArrowDown,
    Message,
    Lightning,
    ChatWidget
  },
  setup() {
    const router = useRouter()
    const route = useRoute()
    const auth = useAuth()
    const isLoggedIn = computed(() => auth.isLoggedIn.value)
    const username = computed(() => auth.username.value)
    const chatWidgetRef = ref(null)

    const userRole = computed(() => {
      // 从 auth.state.user 获取 role
      if (auth.state.user && auth.state.user.role) return auth.state.user.role

      // 如果你的项目把 role 存到了 localStorage，这里也兼容
      const localRole = localStorage.getItem('role')
      if (localRole) return localRole

      // 兼容旧逻辑：没有 role 时保留 admin 用户名兜底
      if (username.value === 'admin') return 'admin'

      return 'common'
    })

    // 跳转到登录页面
    const goToLogin = () => {
      const path = auth.state.loginPromptPath
      auth.closeLoginPrompt()

      // 如果当前在主页，并且触发的是成果发布或需求发布，则跳转到登录页面，登录成功后返回主页并弹出对应对话框
      if (route.path === '/' && (path === '/publish' || path === '/require')) {
        const dialogType = path === '/publish' ? 'publish' : 'require'
        router.push({
          path: '/auth',
          query: { redirect: '/?showDialog=' + dialogType, tab: 'login' }
        })
      } else {
        router.push({
          path: '/auth',
          query: { redirect: path, tab: 'login' }
        })
      }
    }

    // 跳转到注册页面
    const goToRegister = () => {
      const path = auth.state.loginPromptPath
      auth.closeLoginPrompt()

      // 如果当前在主页，并且触发的是成果发布或需求发布，则跳转到注册页面，注册/登录成功后返回主页并弹出对应对话框
      if (route.path === '/' && (path === '/publish' || path === '/require')) {
        const dialogType = path === '/publish' ? 'publish' : 'require'
        router.push({
          path: '/auth',
          query: { redirect: '/?showDialog=' + dialogType, tab: 'register' }
        })
      } else {
        router.push({
          path: '/auth',
          query: { redirect: path, tab: 'register' }
        })
      }
    }

    const handleCommand = (command) => {
      if (command === 'profile') {
        router.push('/profile')
      } else if (command === 'logout') {
        auth.logout()
        // 退出后刷新页面以更新导航栏（或直接跳转到首页）
        window.location.href = '/'
      }
    }

    // 跳转到登录/注册页面


    const isActive = (path) => {
      if (path === '/') {
        return route.path === path
      }
      return route.path.startsWith(path)
    }

    const navigate = (path) => {
      // 所有页面均可访问，未登录用户也可浏览
      router.push(path)
    }

    const openCustomerService = () => {
      // 未登录：默认打开普通用户客服小窗
      if (!isLoggedIn.value) {
        if (chatWidgetRef.value) chatWidgetRef.value.openChat()
        return
      }

      // 管理员：跳转管理后台
      if (userRole.value === 'admin') {
        router.push('/admin')
        return
      }

      // 客服：跳转客服后台
      if (userRole.value === 'agent') {
        router.push('/admin-chat')
        return
      }

      // 普通用户：打开右下角小窗
      if (chatWidgetRef.value) {
        chatWidgetRef.value.openChat()
      }
    }

    // 消息相关
    const unreadCount = ref(0)
    const messageList = ref([])
    let msgTimer = null

    async function fetchMessageData() {
      try {
        // 获取未读数量
        const countRes = await request.get('/api/messages/unread-count')
        if (countRes.code === 200) {
          unreadCount.value = countRes.data.count || 0
        }
        // 获取最近3条消息（下拉预览）
        const listRes = await request.get('/api/messages', { params: { page: 1, page_size: 3 } })
        if (listRes.code === 200) {
          messageList.value = (listRes.data || []).map(m => ({
            id: m.id,
            title: m.title,
            content: m.content,
            time: m.create_time,
            biz_type: m.biz_type,
            msg_type: m.msg_type
          }))
        }
      } catch (e) {
        // 静默失败
      }
    }

    // 导航栏消息类型圆点样式
    function msgTypeDotClass(msg) {
      if (msg.biz_type === 'achievement') return 'dot-achievement'
      if (msg.biz_type === 'demand') return 'dot-demand'
      if (msg.msg_type === 'system') return 'dot-system'
      return 'dot-achievement'
    }

    const handleMessageCommand = (command) => {
      if (command === 'all') {
        router.push('/messages')
      } else {
        // 点击单条消息 → 标记已读 → 跳转到消息中心
        const msgId = parseInt(command)
        if (msgId) {
          request.put(`/api/messages/${msgId}/read`).then(() => {
            fetchMessageData()
          }).catch(() => {})
        }
        router.push('/messages')
      }
    }

    // 从消息页面返回时刷新未读数
    watch(() => route.path, (newPath, oldPath) => {
      if (oldPath === '/messages' && newPath !== '/messages') {
        fetchMessageData()
      }
      // captcha 页面禁止 body 滚动
      document.body.style.overflow = newPath === '/captcha' ? 'hidden' : ''
    })

    const isAdminRoute = computed(() => route.path === '/admin')
    const mobileMenuOpen = ref(false)

    // ================= 站点配置（Logo、名称、导航栏） =================
    const siteConfig = reactive({
      site_name: '大连山西商会科创中心',
      site_logo: '',
      nav_menu: [
        { name: '主页', path: '/' },
        { name: '成果中心', path: '/achievement' },
        { name: '需求中心', path: '/demand' },
        { name: '项目孵化', path: '/incubation' },
        { name: '人才培养', path: '/talent' },
        { name: '专家中心', path: '/expert' },
        { name: '合作伙伴', path: '/partner' },
        { name: '金融服务', path: '/finance' },
        { name: '关于我们', path: '/about' }
      ]
    })

    function resolveImageUrl(url) {
      if (!url) return ''
      if (url.startsWith('http://') || url.startsWith('https://')) return url
      return window.location.origin + url
    }

    async function fetchSiteConfig() {
      try {
        const res = await fetch('/api/editor/config/all')
        const data = await res.json()
        if (data.code === 200 && data.data) {
          if (data.data.site_name) siteConfig.site_name = data.data.site_name
          if (data.data.site_logo) siteConfig.site_logo = data.data.site_logo
          if (data.data.browser_title) document.title = data.data.browser_title
          if (Array.isArray(data.data.nav_menu) && data.data.nav_menu.length > 0) {
            siteConfig.nav_menu = data.data.nav_menu
          }
        }
      } catch (e) {
        // 静默失败，使用默认值
      }
    }
    // ================================================================

    // ================= 全局点击安全防护 =================
    function handleGlobalClick(e) {
      // 只追踪 button / a[button] / [role="button"] 元素
      const target = e.target.closest('button, a[class*="btn"], [role="button"], .el-button, .action-btn, .contact-btn, .search-btn, .submit-btn, .detail-btn, .verify-btn')
      if (!target) return
      // 跳过验证页面自身，防止死循环
      if (route.path === '/captcha') return

      setRedirectPath(route.fullPath)
      if (registerClick()) {
        router.replace('/captcha')
      }
    }

    onMounted(() => {
      fetchSiteConfig()
      document.addEventListener('click', handleGlobalClick, true)
      // 检查是否需要人机验证
      const token = localStorage.getItem('token')
      fetch('/api/captcha/status', {
        headers: token ? { 'Authorization': `Bearer ${token}` } : {}
      })
        .then(r => r.json())
        .then(res => {
          if (res.code === 200 && res.data?.need_captcha && route.path !== '/captcha') {
            router.replace('/captcha')
          }
        })
        .catch(() => {})
    })
    onBeforeUnmount(() => {
      document.removeEventListener('click', handleGlobalClick, true)
    })
    // =================================================


    // Socket.IO 实时消息推送
    let msgSocket = null

    function connectMessageSocket() {
      const token = localStorage.getItem('token')
      if (!token) return
      try {
        msgSocket = io({
          transports: ['websocket'],
          query: { token }
        })
        msgSocket.on('connect', () => {
          console.log('[消息] Socket.IO 已连接')
        })
        msgSocket.on('new_message', (data) => {
          console.log('[消息] 收到实时通知:', data.title)
          fetchMessageData()
        })
        msgSocket.on('disconnect', () => {
          console.log('[消息] Socket.IO 已断开')
        })
      } catch (e) {
        console.warn('[消息] Socket.IO 连接失败:', e)
      }
    }

    function disconnectMessageSocket() {
      if (msgSocket) {
        msgSocket.disconnect()
        msgSocket = null
      }
    }
    // 监听登录状态，登录后获取消息，退出时清理
    watch(isLoggedIn, (val) => {
      if (val) {
        fetchMessageData()
        msgTimer = setInterval(fetchMessageData, 5000)
        connectMessageSocket()
      } else {
        if (msgTimer) {
          clearInterval(msgTimer)
          msgTimer = null
        }
        unreadCount.value = 0
        messageList.value = []
        disconnectMessageSocket()
      }
    }, { immediate: true })

    onBeforeUnmount(() => {
      if (msgTimer) clearInterval(msgTimer)
      disconnectMessageSocket()
    })

    // 全局打开聊天窗口函数
    const globalOpenChat = (referenceType, referenceId) => {
      if (chatWidgetRef.value) {
        if (referenceType && referenceId) {
          chatWidgetRef.value.openChatWithContext(referenceType, referenceId);
        } else {
          chatWidgetRef.value.openChat();
        }
      }
    }

    // 提供全局函数给子组件使用
    provide('globalOpenChat', globalOpenChat)
    provide('refreshMessageCount', fetchMessageData)

    return {
      isLoggedIn,
      username,
      userRole,
      handleCommand,
      auth,
      isActive,
      navigate,
      openCustomerService,
      goToLogin,
      goToRegister,
      chatWidgetRef,
      unreadCount,
      messageList,
      handleMessageCommand,
      isAdminRoute,
      mobileMenuOpen,
      globalOpenChat,
      fetchMessageData,
      siteConfig,
      resolveImageUrl,
      msgTypeDotClass
    }
  }
}
</script>

<style>
/* ================= 基础重置与变量 ================= */
:root {
  --primary-color: #1890ff;
  --primary-dark: #096dd9;
  --primary-hover: #096dd9;
  --bg-color: #f0f2f5;
  --text-main: rgba(0, 0, 0, 0.85);
  --text-secondary: rgba(0, 0, 0, 0.65);
  --text-muted: rgba(0, 0, 0, 0.45);
  --text-light: rgba(0, 0, 0, 0.45);
  --border-color: #f0f0f0;
  --white: #ffffff;
  --theme-blue: #1890ff;
  --transition: all 0.3s;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
}

body {
  background-color: var(--bg-color);
  color: var(--text-main);
  line-height: 1.6;
}

/* 隐藏全局滚动条 */
::-webkit-scrollbar { display: none; }
* { scrollbar-width: none; -ms-overflow-style: none; }

a { text-decoration: none; color: inherit; }
ul { list-style: none; }

/* ================= 主要内容区域 ================= */
main {
  min-height: calc(100vh - 70px);
}

/* ================= 头部导航栏 (公用) ================= */
header {
  background-color: var(--white);
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-container {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 70px;
  padding: 0 24px;
}

.logo {
  font-size: 22px;
  font-weight: bold;
  color: var(--primary-color);
  letter-spacing: 1px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-img {
  height: 36px;
  max-width: 160px;
  object-fit: contain;
}

.logo-icon {
  font-size: 28px;
}

.nav-menu {
  display: flex;
  gap: 24px;
}

.nav-menu li {
  cursor: pointer;
  font-size: 15px;
  font-weight: 500;
  padding: 5px 0;
  border-bottom: 2px solid transparent;
  transition: all 0.3s;
  white-space: nowrap;
}

.nav-menu li:hover, .nav-menu li.active {
  color: var(--primary-color);
  border-bottom: 2px solid var(--primary-color);
}

.auth-actions {
  font-size: 14px;
  color: var(--text-muted);
  display: flex;
  align-items: center;
  height: 100%;
}
.auth-actions span, .auth-actions .el-dropdown { margin: 0 10px; cursor: pointer; transition: color 0.3s; display: flex; align-items: center; }
.auth-actions span:hover, .auth-actions .el-dropdown:hover { color: var(--theme-blue); }

#app {
  font-family: inherit;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* 页面过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 用户下拉菜单 */
.user-dropdown {
  cursor: pointer;
  color: var(--text-muted);
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border-radius: 4px;
  transition: color 0.3s;
}
.user-dropdown:hover {
  color: var(--theme-blue);
}

/* 登录对话框 */
.login-prompt-dialog .el-dialog__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
  height: 56px;
  box-sizing: border-box;
}

.login-prompt-dialog .el-dialog__title {
  font-size: 16px;
  font-weight: 500;
  line-height: 24px;
  color: var(--text-main);
  margin: 0;
}

.login-prompt-dialog .el-dialog__headerbtn {
  position: absolute;
  top: 50%;
  right: 20px;
  transform: translateY(-50%);
  font-size: 16px;
}

.login-prompt-dialog .el-dialog__body {
  padding: 20px;
}

.login-prompt-content {
  text-align: center;
  padding: 10px 0 20px;
}

.prompt-icon {
  font-size: 48px;
  margin-bottom: 16px;
  color: var(--primary-color);
}

.prompt-text {
  font-size: 18px;
  font-weight: 500;
  color: var(--text-main);
  margin-bottom: 8px;
}

.prompt-subtext {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 24px;
}

.prompt-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
}

.login-btn {
  min-width: 100px;
}

.register-btn {
  min-width: 100px;
  border-color: var(--primary-color);
  color: var(--primary-color);
}
.register-btn:hover {
  background-color: var(--primary-color);
  color: white;
}

/* 消息图标下拉框 */
.message-dropdown {
  margin-right: 10px;
}
.message-icon-wrapper {
  position: relative;
  display: inline-block;
  cursor: pointer;
  padding: 6px 10px;
  border-radius: 4px;
  transition: color 0.3s;
  color: var(--text-muted);
}
.message-icon-wrapper:hover {
  color: var(--theme-blue);
}
.message-icon {
  font-size: 24px;
}
.message-badge {
  position: absolute;
  top: -6px;
  right: -6px;
  background: linear-gradient(135deg, #ff6b6b 0%, #ff4d4f 60%, #e8001a 100%);
  color: #ffffff;
  border-radius: 8px;
  min-width: 16px;
  height: 16px;
  font-size: 10px;
  line-height: 16px;
  text-align: center;
  padding: 0 4px;
  font-weight: 700;
  box-sizing: border-box;
  box-shadow: 0 2px 6px rgba(255, 77, 79, 0.55), 0 0 0 2px #ffffff;
  letter-spacing: 0;
  animation: badge-pop 0.35s cubic-bezier(0.34, 1.56, 0.64, 1) both;
  transform-origin: center center;
}

@keyframes badge-pop {
  0%   { transform: scale(0); opacity: 0; }
  60%  { transform: scale(1.15); opacity: 1; }
  100% { transform: scale(1); opacity: 1; }
}
.message-item {
  white-space: normal !important;
  line-height: 1.4;
  padding: 10px 14px !important;
  max-width: 320px;
  min-width: 220px;
  display: flex !important;
  flex-direction: column !important;
  align-items: stretch !important;
}
.message-title {
  font-weight: 600;
  font-size: 14px;
  color: var(--text-main);
  margin-bottom: 6px;
  display: block;
}
.message-preview {
  font-size: 12px;
  color: var(--text-secondary);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.5;
  margin-bottom: 6px;
}
.message-time {
  font-size: 11px;
  color: var(--text-muted);
  display: block;
}

/* 导航栏消息类型彩色左边框 */
.message-item-top {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
  width: 100%;
}
.message-item-top .message-title {
  margin-bottom: 0;
  flex: 1;
}
.message-item.dot-achievement,
.message-item.dot-demand,
.message-item.dot-system {
  position: relative;
  overflow: hidden;
}
.message-item.dot-achievement::before,
.message-item.dot-demand::before,
.message-item.dot-system::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  width: 4px;
  height: 100%;
  pointer-events: none;
}
.message-item.dot-achievement::before {
  background: linear-gradient(180deg, #0050b3 0%, #ffffff 100%);
}
.message-item.dot-demand::before {
  background: linear-gradient(180deg, #237804 0%, #ffffff 100%);
}
.message-item.dot-system::before {
  background: linear-gradient(180deg, #d46b08 0%, #ffffff 100%);
}

.full-height {
  min-height: calc(100vh - 70px);
  height: calc(100vh - 70px);
}

/* ================= 汉堡菜单按钮 ================= */
.hamburger-btn {
  display: none;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  width: 36px;
  height: 36px;
  border: none;
  background: transparent;
  cursor: pointer;
  padding: 6px;
  gap: 5px;
  margin-left: 8px;
  border-radius: 4px;
  transition: background 0.2s;
}
.hamburger-btn:hover { background: #f5f5f5; }
.hamburger-btn span {
  display: block;
  width: 22px;
  height: 2.5px;
  background: var(--text-muted);
  border-radius: 2px;
  transition: all 0.3s ease;
}
.hamburger-btn.active span:nth-child(1) {
  transform: rotate(45deg) translate(5px, 5px);
}
.hamburger-btn.active span:nth-child(2) {
  opacity: 0;
}
.hamburger-btn.active span:nth-child(3) {
  transform: rotate(-45deg) translate(5px, -5px);
}

/* ================= 手机端导航面板 ================= */
.mobile-nav-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.3);
  z-index: 98;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.3s;
}
.mobile-nav-overlay.active {
  opacity: 1;
  pointer-events: auto;
}
.mobile-nav-panel {
  position: fixed;
  top: 70px;
  left: 0;
  width: 100%;
  max-height: 0;
  overflow: hidden;
  background: white;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  z-index: 99;
  transition: max-height 0.35s ease;
}
.mobile-nav-panel.active {
  max-height: 500px;
  overflow-y: auto;
}
.mobile-nav-menu {
  list-style: none;
  padding: 8px 0;
  margin: 0;
}
.mobile-nav-menu li {
  padding: 14px 24px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  color: var(--text-main);
  border-left: 3px solid transparent;
  transition: all 0.2s;
}
.mobile-nav-menu li:hover,
.mobile-nav-menu li.active {
  color: var(--primary-color);
  background: #f0f7ff;
  border-left-color: var(--primary-color);
}

/* ================= 响应式全局样式 ================= */
@media (max-width: 1024px) {
  .header-container {
    padding: 0 16px;
  }
  .logo {
    font-size: 18px;
  }
  .logo-icon {
    font-size: 24px;
  }
  .nav-menu {
    gap: 14px;
  }
  .nav-menu li {
    font-size: 13px;
  }
}

@media (max-width: 768px) {
  .hamburger-btn {
    display: flex;
  }
  .nav-menu {
    display: none;
  }
  .header-container {
    height: 60px;
  }
  header {
    position: sticky;
    top: 0;
  }
  .logo {
    font-size: 16px;
  }
  .logo-icon {
    font-size: 20px;
  }
  .auth-actions span,
  .auth-actions .el-dropdown {
    margin: 0 6px;
    font-size: 13px;
  }
  .message-icon {
    font-size: 20px !important;
  }
  main {
    min-height: calc(100vh - 60px);
  }
  .full-height {
    min-height: calc(100vh - 60px);
    height: calc(100vh - 60px);
  }
  .message-dropdown {
    margin-right: 0;
  }
}

@media (max-width: 480px) {
  header .header-container {
    padding: 0 10px;
  }
  .logo {
    font-size: 14px;
    gap: 6px;
  }
  .logo-icon {
    font-size: 18px;
  }
  .auth-actions span,
  .auth-actions .el-dropdown {
    margin: 0 4px;
    font-size: 12px;
  }
}

</style>
