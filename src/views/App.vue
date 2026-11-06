<template>
  <div id="app">
    <header>
      <div class="header-container">
        <div class="logo" @click="$router.push('/')">大连山西商会科创中心</div>

        <ul class="nav-menu" v-if="userRole !== 'agent'">
          <li :class="{ active: isActive('/') }" @click="navigate('/')">主页</li>
          <li :class="{ active: isActive('/achievement') }" @click="navigate('/achievement')">成果中心</li>
          <li :class="{ active: isActive('/demand') }" @click="navigate('/demand')">需求中心</li>
          <li :class="{ active: isActive('/expert') }" @click="navigate('/expert')">专家中心</li>
          <li :class="{ active: isActive('/partner') }" @click="navigate('/partner')">合作伙伴</li>
          <li :class="{ active: isActive('/finance') }" @click="navigate('/finance')">金融服务</li>
          <li :class="{ active: isActive('/about') }" @click="navigate('/about')">关于我们</li>
        </ul>

        <div class="auth-actions">
          <template v-if="!isLoggedIn">
            <span @click="$router.push({ path: '/auth', query: { tab: 'login' } })">登录</span>
            /
            <span @click="$router.push({ path: '/auth', query: { tab: 'register' } })">注册</span>
            <span @click="openCustomerService" v-if="userRole !== 'agent'">客服</span>
          </template>

          <template v-else>
            <el-dropdown @command="handleCommand">
              <span class="user-dropdown">
                {{ username }}
                <el-icon class="el-icon--right">
                  <arrow-down />
                </el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile" v-if="userRole !== 'agent'">个人中心</el-dropdown-item>
                  <el-dropdown-item command="logout">退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>

            <span @click="openCustomerService" v-if="userRole !== 'agent'">客服</span>
          </template>
        </div>
      </div>
    </header>

    <main>
      <router-view />
    </main>

    <el-dialog
      v-model="auth.state.showLoginModal"
      title="登录/注册"
      width="400px"
      :before-close="auth.closeLoginModal"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
    >
      <AuthView />
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="auth.closeLoginModal">取消</el-button>
        </span>
      </template>
    </el-dialog>

    <ChatWidget v-show="$route.path !== '/admin-chat'" ref="chatWidgetRef" />
  </div>
</template>

<script>
import { computed, watchEffect, ref } from 'vue';
import { useRouter } from 'vue-router';
import { ElDropdown, ElDropdownMenu, ElDropdownItem, ElIcon, ElDialog, ElButton } from 'element-plus';
import { ArrowDown } from '@element-plus/icons-vue';
import useAuth from './composables/useAuth';
import AuthView from './views/AuthView.vue';
import ChatWidget from './components/ChatWidget.vue';

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
    AuthView,
    ChatWidget,
  },
  setup() {
    const router = useRouter();
    const auth = useAuth();

    const isLoggedIn = computed(() => auth.isLoggedIn.value);
    const username = computed(() => auth.username.value);

    const userRole = computed(() => {
      // 优先使用 composable/state 里的 role
      if (auth.state && auth.state.role) return auth.state.role;

      // 如果你的项目把 role 存到了 localStorage，这里也兼容
      const localRole = localStorage.getItem('role');
      if (localRole) return localRole;

      // 兼容旧逻辑：没有 role 时保留 admin 用户名兜底
      if (username.value === 'admin') return 'admin';

      return 'common';
    });

    const chatWidgetRef = ref(null);

    const handleCommand = (command) => {
      if (command === 'profile') {
        router.push('/profile');
      } else if (command === 'logout') {
        auth.logout();
        window.location.href = '/';
      }
    };

    watchEffect(() => {
      if (auth.state.token && auth.state.targetRoute) {
        const target = auth.state.targetRoute;
        auth.state.targetRoute = null;
        router.push(target);
      }
    });

    const isActive = (path) => {
      if (path === '/') {
        return router.currentRoute.value.path === path;
      }
      return router.currentRoute.value.path.startsWith(path);
    };

    const navigate = (path) => {
      router.push(path);
    };

    const openCustomerService = () => {
      // 未登录：默认打开普通用户客服小窗
      if (!isLoggedIn.value) {
        if (chatWidgetRef.value) chatWidgetRef.value.openChat();
        return;
      }

      // 管理员和客服：跳转客服后台
      if (userRole.value === 'admin' || userRole.value === 'agent') {
        router.push('/admin-chat');
        return;
      }

      // 普通用户：打开右下角小窗
      if (chatWidgetRef.value) {
        chatWidgetRef.value.openChat();
      }
    };

    return {
      isLoggedIn,
      username,
      userRole,
      handleCommand,
      auth,
      isActive,
      navigate,
      openCustomerService,
      chatWidgetRef,
    };
  },
};
</script>

<style>
:root {
  --primary-color: #0056b3;
  --primary-hover: #004494;
  --bg-color: #f5f7fa;
  --text-main: #333333;
  --text-muted: #666666;
  --border-color: #ebebeb;
  --white: #ffffff;
  --theme-blue: #0084ff;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
}

body {
  background-color: var(--bg-color);
  color: var(--text-main);
  line-height: 1.6;
}

a {
  text-decoration: none;
  color: inherit;
}

ul {
  list-style: none;
}

::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background-color: #f5f7fa;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background-color: #c0c8d6;
  border-radius: 4px;
  border: 2px solid #f5f7fa;
  background-clip: padding-box;
}

::-webkit-scrollbar-thumb:hover {
  background-color: var(--primary-color);
}

main {
  min-height: calc(100vh - 70px);
}

header {
  background-color: var(--white);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 70px;
  padding: 0 20px;
}

.logo {
  font-size: 22px;
  font-weight: bold;
  color: var(--primary-color);
  letter-spacing: 1px;
  cursor: pointer;
}

.nav-menu {
  display: flex;
  gap: 30px;
}

.nav-menu li {
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
  padding: 5px 0;
  border-bottom: 2px solid transparent;
  transition: all 0.3s;
}

.nav-menu li:hover,
.nav-menu li.active {
  color: var(--primary-color);
  border-bottom: 2px solid var(--primary-color);
}

.auth-actions {
  font-size: 14px;
  color: var(--text-muted);
}

.auth-actions span,
.auth-actions .el-dropdown {
  margin: 0 10px;
  cursor: pointer;
  transition: color 0.3s;
}

.auth-actions span:hover,
.auth-actions .el-dropdown:hover {
  color: var(--theme-blue);
}

#app {
  font-family: inherit;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

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
</style>