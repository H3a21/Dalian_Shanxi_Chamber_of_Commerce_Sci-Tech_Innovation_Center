import { createRouter, createWebHistory } from 'vue-router'
import { state } from '../composables/useAuth'
import HomeView from '../views/HomeView.vue'
import AuthView from '../views/AuthView.vue'
import AchievementView from '../views/AchievementView.vue'
import AchievementDetailView from '../views/AchievementDetailView.vue'
import PersonalCenterView from '../views/PersonalCenterView.vue'
import ForgotPasswordView from '../views/ForgotPasswordView.vue'
import ExpertView from '../views/ExpertView.vue'
import DemandCenterView from '../views/DemandCenterView.vue'
import FinancialView from '../views/FinancialView.vue'
import PlaceholderView from '../views/PlaceholderView.vue'
import DynamicPageView from '../views/DynamicPageView.vue'
// AboutView 保留备用，后续可通过配置切换
// import AboutView from '../views/AboutView.vue'
import PrivacyView from '../views/PrivacyView.vue'
import TermsView from '../views/TermsView.vue'
import AdminChatView from '../views/AdminChatView.vue'
import MessagesView from '../views/MessagesView.vue'
import PublishView from '../views/PublishView.vue'
import RequireView from '../views/RequireView.vue'
import PartnerView from '../views/PartnerView.vue'
import AdminView from '../views/Adminview.vue'

const routes = [
  { path: '/admin-editor', name: 'admin-editor', component: () => import('../views/AdminEditorView.vue') },
  { path: '/', name: 'home', component: HomeView },
  { path: '/achievement', name: 'achievement', component: AchievementView },
  { path: '/achievement/:id', name: 'achievement-detail', component: AchievementDetailView, props: true },
  { path: '/auth', name: 'auth', component: AuthView },
  { path: '/profile', name: 'profile', component: PersonalCenterView },
  { path: '/forgot-password', name: 'forgot-password', component: ForgotPasswordView },
  { path: '/demand', name: 'demand', component: DemandCenterView },
  { path: '/incubation', name: 'incubation', component: PlaceholderView },
  { path: '/talent', name: 'talent', component: PlaceholderView },
  { path: '/expert', name: 'expert', component: ExpertView },
  { path: '/partner', name: 'partner', component: PartnerView },
  { path: '/finance', name: 'finance', component: FinancialView },
  { path: '/about', name: 'about', component: DynamicPageView },
  { path: '/page/:pagePath', name: 'dynamic-page', component: DynamicPageView },
  { path: '/privacy', name: 'privacy', component: PrivacyView },
  { path: '/terms', name: 'terms', component: TermsView },
  { path: '/admin-chat', name: 'admin-chat', component: AdminChatView },
  { path: '/publish', name: 'publish', component: PublishView },
  { path: '/require', name: 'require', component: RequireView },
  { path: '/admin', name: 'admin', component: AdminView },
  { path: '/messages', name: 'messages', component: MessagesView },
  { path: '/captcha', name: 'captcha', component: () => import('../views/CaptchaView.vue') }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
  scrollBehavior () {
    return { top: 0 }
  }
})

router.beforeEach((to, from, next) => {
  // 获取用户角色（与App.vue中的逻辑保持一致）
  const getRole = () => {
    // 从 auth.state.user 获取 role
    if (state.user && state.user.role) return state.user.role

    // 如果你的项目把 role 存到了 localStorage，这里也兼容
    const localRole = localStorage.getItem('role')
    if (localRole) return localRole

    // 从localStorage的user对象获取
    try {
      const userStr = localStorage.getItem('user')
      if (userStr) {
        const user = JSON.parse(userStr)
        if (user && user.role) return user.role
      }
    } catch (e) {
      console.error('Failed to parse user from localStorage', e)
    }

    // 兼容旧逻辑：没有 role 时保留 admin 用户名兜底
    let username = ''
    if (state.user && state.user.username) {
      username = state.user.username
    } else {
      try {
        const userStr = localStorage.getItem('user')
        if (userStr) {
          const user = JSON.parse(userStr)
          if (user && user.username) username = user.username
        }
      } catch (e) {
        // ignore
      }
    }
    if (username === 'admin') return 'admin'

    return 'common' // 默认角色
  }

  // 已登录用户角色检查
  if (state.token) {
    const role = getRole()

    // 客服用户只能访问客服界面
    if (role === 'agent') {
      if (to.path !== '/admin-chat') {
        // 重定向到客服界面
        return next('/admin-chat')
      }
      // 允许访问客服界面
      return next()
    }

    // 普通用户不能访问客服界面
    if (role === 'common' && to.path === '/admin-chat') {
      // 重定向到主页
      return next('/')
    }

    // 只有管理员可以访问/admin和/admin-editor路径
    if ((to.path === '/admin' || to.path === '/admin-editor') && role !== 'admin') {
      // 重定向到主页
      return next('/')
    }

    // 管理员和普通用户可以继续后续检查
  }

  // 所有路径都放行，未登录用户也可访问页面
  next();
});

// 路由追踪：每次页面切换时记录访问
const routeTitleMap = {
  '/': '首页',
  '/achievement': '成果中心',
  '/demand': '需求中心',
  '/incubation': '项目孵化',
  '/talent': '人才培养',
  '/expert': '专家中心',
  '/partner': '合作伙伴',
  '/finance': '金融服务',
  '/about': '关于我们',
  '/page': '动态页面',
  '/privacy': '隐私政策',
  '/terms': '使用条款',
  '/profile': '个人中心',
  '/admin': '后台管理',
  '/admin-editor': '网站编辑',
  '/admin-chat': '客服中心',
  '/publish': '发布成果',
  '/require': '发布需求',
  '/forgot-password': '忘记密码',
  '/auth': '登录注册',
  '/messages': '消息中心'
}

router.afterEach((to) => {
  // 静默追踪，不阻塞导航
  const path = to.path
  const title = routeTitleMap[path] || path
  fetch('/api/publish/visit/track', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ path, title })
  }).catch(() => {
    // 静默失败，不影响用户
  })
})

export default router
