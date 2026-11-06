<template>
  <div class="editor-app">
    <!-- 登录界面（非管理员时显示） -->
    <div v-if="!isLoggedIn" class="login-layout">
      <div class="login-card">
        <div class="login-icon">&#9998;</div>
        <h2>网站编辑器</h2>
        <p style="color:#888;margin-bottom:24px;">请输入编辑器账号密码</p>
        <div class="login-form">
          <div class="form-group">
            <input v-model="loginForm.account" type="text" class="form-input" placeholder="账号" @keydown.enter="handleLogin" />
          </div>
          <div class="form-group">
            <input v-model="loginForm.password" type="password" class="form-input" placeholder="密码" @keydown.enter="handleLogin" />
          </div>
          <div v-if="loginError" class="login-error">{{ loginError }}</div>
          <button class="login-btn" @click="handleLogin" :disabled="loginLoading">
            {{ loginLoading ? '登录中...' : '登录' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 编辑器主界面 -->
    <div v-else class="editor-layout">
      <!-- 顶部工具栏 -->
      <div class="editor-topbar">
        <div class="topbar-left">
          <button class="tb-btn back-btn" @click="goBack">← 返回</button>
          <span class="topbar-brand">&#9998; 网站编辑器</span>
          <span class="topbar-sep">|</span>
          <select v-model="currentPageId" class="page-select" @change="switchPage">
            <option value="">-- 选择页面 --</option>
            <option v-for="p in editablePages" :key="p.id" :value="p.id">{{ p.page_name }}</option>
          </select>
        </div>
        <div class="topbar-center">
          <button class="tb-btn config-btn" @click="openConfigDialog">⚙ 全局设置</button>
          <button class="tb-btn" @click="openImportModal">📥 导入HTML</button>
          <button class="tb-btn" @click="previewPage" :disabled="!currentPageId">👁 预览</button>
          <button class="tb-btn save-btn" @click="savePage" :disabled="!currentPageId || isSaving">
            {{ isSaving ? '保存中...' : '💾 保存' }}
          </button>
        </div>
        <div class="topbar-right">
          <button class="tb-btn" @click="toggleFullscreen" title="全屏">⛶</button>
        </div>
      </div>

      <!-- 编辑器主体 -->
      <div class="editor-main">
        <div id="gjs" class="gjs-container"></div>
        <div v-if="pageLoading" class="canvas-loader">
          <div class="loader-spinner"></div>
          <span>加载页面中...</span>
        </div>
      </div>
    </div>

    <!-- ========== 全局设置弹窗 ========== -->
    <el-dialog v-model="showConfigDialog" width="780px" top="5vh" destroy-on-close class="config-dialog">
      <template #header>
        <div style="display:flex;align-items:center;gap:10px;">
          <el-icon :size="22" color="#409eff"><component :is="Setting" /></el-icon>
          <span style="font-size:18px;font-weight:600;">全局站点设置</span>
        </div>
      </template>
      <el-tabs v-model="configTab" class="config-tabs">
        <!-- Tab 1: Logo 与网站名称 -->
        <el-tab-pane name="basic">
          <template #label>
            <span style="display:flex;align-items:center;gap:6px;"><el-icon><component :is="Picture" /></el-icon>Logo 与网站名称</span>
          </template>
          <div style="display:flex;flex-direction:column;gap:20px;padding:4px 0;">
            <!-- 浏览器标签卡片 -->
            <div class="config-card">
              <div class="config-card-header">
                <el-icon :size="18" color="#409eff"><component :is="Monitor" /></el-icon>
                <span>浏览器标签页</span>
              </div>
              <div class="config-card-body">
                <div class="config-field">
                  <div class="config-field-label">标签标题</div>
                  <el-input v-model="globalConfig.browser_title" placeholder="如：大连山西商会科创中心" clearable />
                  <div class="config-field-hint">显示在浏览器标签页上的标题文字</div>
                </div>
                <div class="config-field">
                  <div class="config-field-label">标签图标（Favicon）</div>
                  <div style="display:flex;gap:12px;align-items:center;">
                    <el-upload action="#" :show-file-list="false" :http-request="uploadFavicon" :before-upload="beforeImageUpload" accept="image/*">
                      <el-button type="primary" plain size="small">
                        <el-icon style="margin-right:4px;"><component :is="Upload" /></el-icon>上传图标
                      </el-button>
                    </el-upload>
                    <div class="config-preview-tip">推荐 32×32 像素，PNG 或 ICO 格式</div>
                  </div>
                  <div style="margin-top:12px;display:flex;align-items:center;gap:12px;">
                    <div class="favicon-preview" @click="globalConfig.favicon ? openImgPreview(resolveImg(globalConfig.favicon)) : null">
                      <img v-if="globalConfig.favicon" :src="resolveImg(globalConfig.favicon)" @error="e=>e.target.style.display='none'" />
                      <img v-else :src="defaultFaviconUrl" @error="e=>e.target.style.display='none'" />
                    </div>
                    <el-input v-model="globalConfig.favicon" placeholder="或直接输入图片URL" clearable style="flex:1;" size="default" />
                  </div>
                </div>
              </div>
            </div>

            <!-- 导航栏卡片 -->
            <div class="config-card">
              <div class="config-card-header">
                <el-icon :size="18" color="#409eff"><component :is="HomeFilled" /></el-icon>
                <span>网站导航栏</span>
              </div>
              <div class="config-card-body">
                <div class="config-field">
                  <div class="config-field-label">网站名称</div>
                  <el-input v-model="globalConfig.site_name" placeholder="如：大连山西商会科创中心" clearable />
                </div>
                <div class="config-field">
                  <div class="config-field-label">导航栏 Logo</div>
                  <div style="display:flex;gap:12px;align-items:center;">
                    <el-upload action="#" :show-file-list="false" :http-request="uploadLogo" :before-upload="beforeImageUpload" accept="image/*">
                      <el-button type="primary" plain size="small">
                        <el-icon style="margin-right:4px;"><component :is="Upload" /></el-icon>上传 Logo
                      </el-button>
                    </el-upload>
                    <div class="config-preview-tip">建议尺寸 200×60 像素以内</div>
                  </div>
                  <div style="margin-top:12px;display:flex;gap:12px;align-items:flex-start;">
                    <div class="logo-preview" @click="openLogoPreview">
                      <img v-if="globalConfig.site_logo" :src="resolveImg(globalConfig.site_logo)" @error="e=>e.target.style.display='none'" />
                      <img v-else :src="defaultLogoUrl" @error="e=>e.target.style.display='none'" />
                      <div class="preview-overlay"><el-icon><component :is="ZoomIn" /></el-icon></div>
                    </div>
                    <el-input v-model="globalConfig.site_logo" placeholder="或直接输入图片URL" clearable style="flex:1;" size="default" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <!-- Tab 2: 导航菜单 -->
        <el-tab-pane name="nav">
          <template #label>
            <span style="display:flex;align-items:center;gap:6px;"><el-icon><component :is="Menu" /></el-icon>主页导航栏</span>
          </template>
          <div style="padding:4px 0;">
            <div class="config-card">
              <div class="config-card-header">
                <el-icon :size="18" color="#409eff"><component :is="List" /></el-icon>
                <span>导航菜单项</span>
                <span style="font-size:12px;color:#909399;font-weight:400;margin-left:4px;">（拖拽排序暂不支持）</span>
              </div>
              <div class="config-card-body">
                <div v-for="(item, index) in globalConfig.nav_menu" :key="index" class="nav-menu-item">
                  <span class="nav-menu-index">{{ index + 1 }}</span>
                  <el-input v-model="item.name" placeholder="菜单名称" style="width:150px;" clearable />
                  <el-input v-model="item.path" placeholder="跳转路径（如：/about）" style="flex:1;" clearable />
                  <el-button type="danger" :icon="Delete" circle size="small" @click="globalConfig.nav_menu.splice(index, 1)" />
                </div>
                <el-button type="primary" plain :icon="Plus" @click="globalConfig.nav_menu.push({ name: '新菜单', path: '/page/new' })">添加菜单项</el-button>
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
      <template #footer>
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <div style="font-size:12px;color:#909399;">配置保存后需刷新前台页面才能看到效果</div>
          <div style="display:flex;gap:10px;">
            <el-button @click="showConfigDialog = false">取消</el-button>
            <el-button type="primary" @click="saveGlobalConfig" :loading="configSaving">保存站点设置</el-button>
          </div>
        </div>
      </template>
    </el-dialog>

    <!-- ========== 导入HTML弹窗 ========== -->
    <el-dialog v-model="showImportModal" title="导入HTML代码" width="650px">
      <div style="margin-bottom:14px;">
        <p style="font-size:13px;color:#909399;margin-bottom:8px;">在浏览器打开目标页面 → F12 → 右键 &lt;html&gt; → Copy OuterHTML，粘贴到下方。</p>
        <el-input type="textarea" :rows="8" v-model="importHtmlText" placeholder="粘贴 HTML 代码..." />
      </div>
      <div style="margin-bottom:14px;">
        <p style="font-size:13px;color:#909399;margin-bottom:8px;">CSS（可选）</p>
        <el-input type="textarea" :rows="4" v-model="importCssText" placeholder="粘贴 CSS..." />
      </div>
      <template #footer>
        <el-button @click="showImportModal = false">取消</el-button>
        <el-button type="primary" @click="confirmImport">导入到编辑器</el-button>
      </template>
    </el-dialog>

    <!-- ========== 图片预览弹窗 ========== -->
    <el-dialog v-model="showImgPreview" title="图片预览" width="auto" top="5vh" destroy-on-close>
      <img :src="previewImgUrl" style="max-width:80vw;max-height:80vh;display:block;margin:0 auto;" />
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, computed, nextTick, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Delete, Setting, Picture, Monitor, Upload, HomeFilled, Menu, List, Plus, ZoomIn } from '@element-plus/icons-vue'
import defaultLogo from '@/assets/logo.png'
import grapesjs from 'grapesjs'
import 'grapesjs/dist/css/grapes.min.css'
import webPreset from 'grapesjs-preset-webpage'
import formsPlugin from 'grapesjs-plugin-forms'
import navbarPlugin from 'grapesjs-navbar'
import tabsPlugin from 'grapesjs-tabs'
import flexboxPlugin from 'grapesjs-blocks-flexbox'
import customCodePlugin from 'grapesjs-custom-code'
import styleBgPlugin from 'grapesjs-style-bg'
import styleGradientPlugin from 'grapesjs-style-gradient'
import styleFilterPlugin from 'grapesjs-style-filter'
import suggestClassesPlugin from 'grapesjs-ui-suggest-classes'
import floatPlugin from 'grapesjs-float'

const BASE_URL = window.location.origin
const STORAGE_KEY = 'editor_token'

function authHeaders() {
  const token = localStorage.getItem('token') || localStorage.getItem(STORAGE_KEY)
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  }
}

export default {
  name: 'AdminEditorView',
  components: {
    Setting, Picture, Monitor, Upload, HomeFilled, Menu, List, ZoomIn
  },
  setup() {
    const router = useRouter()
    // ========== 登录状态 ==========
    const isLoggedIn = ref(false)
    const loginForm = reactive({ account: '', password: '' })
    const loginLoading = ref(false)
    const loginError = ref('')

    // ========== 编辑器状态 ==========
    let editor = null
    const pages = ref([])
    const currentPageId = ref('')
    const pageLoading = ref(false)
    const isSaving = ref(false)

    // ========== 弹窗 ==========
    const showConfigDialog = ref(false)
    const configTab = ref('basic')
    const configSaving = ref(false)
    const showImportModal = ref(false)
    const importHtmlText = ref('')
    const importCssText = ref('')
    const showImgPreview = ref(false)
    const previewImgUrl = ref('')

    // ========== 全局配置 ==========
    const globalConfig = reactive({
      site_name: '大连山西商会科创中心',
      browser_title: '大连山西商会科创中心',
      site_logo: '',
      favicon: '',
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

    // 默认资源（项目静态文件，当数据库未配置时作为预览兜底）
    const defaultLogoUrl = defaultLogo  // src/assets/logo.png 的 webpack 解析路径
    const defaultFaviconUrl = '/favicon.ico'  // public/favicon.ico 由 Vue dev server 托管

    // 可编辑页面列表（仅首页和关于我们）
    const editablePages = computed(() =>
      pages.value.filter(p => p.page_path === 'home' || p.page_path === 'about')
    )

    // ========== 工具函数 ==========
    function resolveImg(url) {
      if (!url) return ''
      if (url.startsWith('http://') || url.startsWith('https://')) return url
      return BASE_URL + url
    }

    function beforeImageUpload(file) {
      const isImage = file.type.startsWith('image/')
      const isLt10M = file.size / 1024 / 1024 < 10
      if (!isImage) { ElMessage.error('只能上传图片！'); return false }
      if (!isLt10M) { ElMessage.error('图片不能超过10MB！'); return false }
      return true
    }

    // ========== 登录逻辑 ==========
    async function tryAdminAutoLogin() {
      const adminToken = localStorage.getItem('token')
      if (!adminToken) return false
      try {
        const res = await fetch(`${BASE_URL}/api/editor/check-token`, {
          headers: { 'Authorization': `Bearer ${adminToken}` }
        })
        const data = await res.json()
        if (data.code === 200) {
          isLoggedIn.value = true
          localStorage.setItem(STORAGE_KEY, adminToken)
          return true
        }
      } catch (e) { /* fallback to login screen */ }
      return false
    }

    async function handleLogin() {
      const account = loginForm.account.trim()
      const password = loginForm.password
      if (!account || !password) { loginError.value = '请输入账号和密码'; return }
      loginLoading.value = true
      loginError.value = ''
      try {
        const res = await fetch(`${BASE_URL}/api/editor/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ account, password })
        })
        const data = await res.json()
        if (data.code === 200) {
          localStorage.setItem(STORAGE_KEY, data.data.token)
          isLoggedIn.value = true
          await nextTick()
          initEditor()
        } else {
          loginError.value = data.msg || '登录失败'
        }
      } catch (e) { loginError.value = '无法连接到服务器' }
      loginLoading.value = false
    }

    // ========== 页面管理 ==========
    async function loadPages() {
      try {
        const res = await fetch(`${BASE_URL}/api/editor/site/pages`, { headers: authHeaders() })
        const data = await res.json()
        if (data.code === 200) pages.value = data.data || []
      } catch (e) { console.error('加载页面列表失败:', e) }
    }

    async function switchPage() {
      if (!editor) return
      if (!currentPageId.value) { editor.DomComponents.clear(); return }
      editor.DomComponents.clear()
      editor.setStyle('')
      pageLoading.value = true

      let loaded = false
      try {
        const res = await fetch(`${BASE_URL}/api/editor/site/pages/${currentPageId.value}`, { headers: authHeaders() })
        const data = await res.json()
        if (data.code === 200) {
          const page = data.data
          if (page.gjs_data) {
            try {
              editor.loadProjectData(JSON.parse(page.gjs_data))
              loaded = true
            } catch { /* fallback */ }
          }
          if (!loaded && page.html_content) {
            editor.setComponents(page.html_content)
            editor.setStyle(page.css_content || '')
            loaded = true
          }
        }
      } catch (e) { console.error('加载页面失败:', e) }

      if (!loaded) {
        // 尝试从全局配置自动填充已知页面
        const currentPage = pages.value.find(p => p.id === currentPageId.value)
        if (currentPage) {
          loaded = await autoPopulatePage(currentPage)
        }
      }

      if (!loaded) {
        editor.setComponents('<div style="padding:40px;text-align:center;color:#999;">从左侧拖拽组件到此处开始编辑，或点击「导入HTML」粘贴现有页面代码。</div>')
      }
      pageLoading.value = false
    }

    // ========== 自动填充页面内容 ==========
    async function autoPopulatePage(page) {
      try {
        const res = await fetch(`${BASE_URL}/api/editor/config/all`)
        const d = await res.json()
        const cfg = d.data || {}

        if (page.page_path === 'about') {
          const ac = cfg.about_content || {}
          // 从AboutView.vue获取默认值
          const intro = ac.intro_text || '大连市山西商会科创中心（英文名称"Dalian Shanxi Chamber of Commerce Science and Technology Innovation Center"）是在自愿、平等、合作、互利的基础上，由大连市山西商会发起，联合企业、高校和科研院所有识之士共同组建的产学研成果对接和创业孵化非营利性组织。中心隶属于大连市山西商会，在大连市山西商会指导下开展工作，服务对象包括企业，高校和科研院所创新创业群体，以及认同本章程的社会各界组织和人士。'
          const missions = Array.isArray(ac.mission_items) && ac.mission_items.length
            ? ac.mission_items : [
              { title: '高水平转化一批成果', desc: '推动科研成果高效转化，打通从实验室到产业化的关键通道。' },
              { title: '高产值孵化一批公司', desc: '孵化培育具有核心竞争力的科技型企业，实现高产值增长。' },
              { title: '高技术赋能一批企业', desc: '以先进技术赋能传统企业，助力产业升级和数字化转型。' },
              { title: '高质量培养一批人才', desc: '培养产学研复合型高端人才，为创新发展提供坚实的人才支撑。' }
            ]
          const advantages = Array.isArray(ac.advantage_items) && ac.advantage_items.length
            ? ac.advantage_items : [
              { title: '专业团队', desc: '汇聚行业顶尖专家和技术人才，平均从业经验超过10年。' },
              { title: '安全可靠', desc: '严格的质量控制体系和完善的安全保障机制。' },
              { title: '生态合作', desc: '与产业链上下游企业建立深度合作关系。' }
            ]
          const mechanisms = Array.isArray(ac.mechanism_items) && ac.mechanism_items.length
            ? ac.mechanism_items : [
              { title: '信息互通机制', desc: '采用多种形式高效率的发布成果信息和需求信息。' },
              { title: '交流对接机制', desc: '举办交流对接和讲座研讨活动，促进产学研深度合作。' },
              { title: '互访联动机制', desc: '组织企业和高校走访调研，收集需求与成果。' }
            ]
          const addr = ac.contact_address || 'xxxxxxxxx'
          const phone = ac.contact_phone || 'xxxxxxxx'
          const email = ac.contact_email || 'xxxxxxxx'

          const html = `<section class="page-banner" style="position:relative;height:280px;overflow:hidden;">
  <img src="https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1600" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;" data-gjs-type="image" />
  <div style="position:absolute;inset:0;background:linear-gradient(135deg,rgba(24,144,255,0.85),rgba(0,21,41,0.85));display:flex;align-items:center;justify-content:center;">
    <div style="text-align:center;color:white;"><h1 style="font-size:36px;font-weight:600;">关于我们</h1></div>
  </div>
</section>

<section class="bdg-sect" style="padding:0;background:white;">
  <div style="max-width:1200px;margin:0 auto;padding:0 20px;">
    <p class="paragraph" style="font-size:16px;line-height:1.8;color:rgba(0,0,0,0.62);text-align:center;max-width:900px;margin:0 auto;padding:32px 0;">Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua</p>
  </div>
</section>

<section class="about-intro-section" style="padding:64px 0;background:white;">
  <div style="max-width:1200px;margin:0 auto;padding:0 20px;">
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:56px;align-items:center;">
      <div style="position:relative;padding-left:28px;border-left:3px solid #1890ff;">
        <span style="font-size:11px;letter-spacing:4px;color:#1890ff;font-weight:500;">ABOUT US</span>
        <h2 style="font-size:28px;font-weight:300;letter-spacing:3px;margin:16px 0;">商会简介</h2>
        <div style="width:40px;height:2px;background:#1890ff;margin-bottom:20px;"></div>
        <p style="font-size:15px;line-height:1.9;color:rgba(0,0,0,0.62);">${intro}</p>
      </div>
      <div style="padding:12px;position:relative;min-height:320px;">
        <div style="position:absolute;top:0;left:0;width:100%;height:100%;border:2px solid #1890ff;border-radius:10px;opacity:0.2;pointer-events:none;"></div>
        <img src="https://images.unsplash.com/photo-1581093450021-4a7360e9a6b5?w=800" style="width:100%;border-radius:6px;box-shadow:0 8px 24px rgba(0,0,0,0.1);position:relative;z-index:1;" />
      </div>
    </div>
  </div>
</section>

<section class="mission-vision-section" style="padding:48px 0;background:transparent;">
  <div style="max-width:1200px;margin:0 auto;padding:0 20px;">
    <div style="text-align:center;margin-bottom:40px;"><h2 style="font-size:24px;font-weight:600;">使命与愿景</h2></div>
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:24px;">
      ${missions.map((item, i) => {
        const colors = ['linear-gradient(135deg,#1890ff,#096dd9)', 'linear-gradient(135deg,#52c41a,#389e0d)', 'linear-gradient(135deg,#722ed1,#531dab)', 'linear-gradient(135deg,#faad14,#d48806)']
        return `<div style="background:white;padding:32px 24px;border-radius:8px;text-align:center;border:1px solid #f0f0f0;transition:all 0.3s;">
          <div style="width:64px;height:64px;margin:0 auto 20px;border-radius:50%;background:${colors[i % colors.length]};display:flex;align-items:center;justify-content:center;color:white;font-size:28px;"><i class="fas fa-star"></i></div>
          <h3 style="font-size:18px;font-weight:600;margin-bottom:16px;">${item.title || ''}</h3>
          <p style="font-size:14px;color:rgba(0,0,0,0.65);">${item.desc || ''}</p>
        </div>`
      }).join('')}
    </div>
  </div>
</section>

<section class="advantages-section" style="padding:48px 0;background:white;">
  <div style="max-width:1200px;margin:0 auto;padding:0 20px;">
    <div style="text-align:center;margin-bottom:40px;"><h2 style="font-size:24px;font-weight:600;">核心优势</h2></div>
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:24px;">
      ${advantages.map((item) => `
        <div style="padding:32px 24px;border-radius:8px;border:1px solid #f0f0f0;text-align:center;transition:all 0.3s;">
          <div style="width:56px;height:56px;margin:0 auto 20px;border-radius:50%;background:linear-gradient(135deg,#1890ff,#096dd9);display:flex;align-items:center;justify-content:center;color:white;font-size:24px;"><i class="fas fa-check-circle"></i></div>
          <h3 style="font-size:16px;font-weight:600;margin-bottom:12px;">${item.title || ''}</h3>
          <p style="font-size:14px;color:rgba(0,0,0,0.65);">${item.desc || ''}</p>
        </div>`
      ).join('')}
    </div>
  </div>
</section>

<section class="mechanism-section" style="padding:48px 0;background:#fafafa;">
  <div style="max-width:1200px;margin:0 auto;padding:0 20px;">
    <div style="text-align:center;margin-bottom:40px;"><h2 style="font-size:24px;font-weight:600;">运行机制</h2></div>
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:24px;">
      ${mechanisms.map((item) => `
        <div style="padding:32px 24px;border-radius:8px;border:1px solid #f0f0f0;background:white;text-align:center;transition:all 0.3s;">
          <div style="width:56px;height:56px;margin:0 auto 20px;border-radius:50%;background:linear-gradient(135deg,#1890ff,#096dd9);display:flex;align-items:center;justify-content:center;color:white;font-size:24px;"><i class="fas fa-cog"></i></div>
          <h3 style="font-size:16px;font-weight:600;margin-bottom:12px;">${item.title || ''}</h3>
          <p style="font-size:14px;color:rgba(0,0,0,0.65);">${item.desc || ''}</p>
        </div>`
      ).join('')}
    </div>
  </div>
</section>

<footer class="site-footer" style="padding:48px 0 24px;background:#fafafa;border-top:1px solid #f0f0f0;">
  <div style="max-width:1200px;margin:0 auto;padding:0 20px;">
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:48px;margin-bottom:40px;">
      <div>
        <h3 style="font-weight:600;margin-bottom:20px;">大连山西商会科创中心</h3>
        <p style="color:rgba(0,0,0,0.65);font-size:14px;margin-bottom:16px;">产学研成果对接平台</p>
        <div style="display:flex;gap:12px;">
          ${['fab fa-weixin','fab fa-weibo','fab fa-qq','fab fa-linkedin'].map(icon => `
            <a href="#" style="width:32px;height:32px;background:#f5f5f5;border-radius:50%;display:flex;align-items:center;justify-content:center;color:rgba(0,0,0,0.65);text-decoration:none;"><i class="${icon}"></i></a>
          `).join('')}
        </div>
      </div>
      <div>
        <h4 style="font-weight:600;margin-bottom:20px;">快速链接</h4>
        <ul style="list-style:none;padding:0;">
          <li style="margin-bottom:12px;"><a href="/achievement" target="_parent" style="color:#1890ff;font-size:14px;text-decoration:none;">成果中心</a></li>
          <li style="margin-bottom:12px;"><a href="/demand" target="_parent" style="color:#1890ff;font-size:14px;text-decoration:none;">需求中心</a></li>
          <li style="margin-bottom:12px;"><a href="/incubation" target="_parent" style="color:#1890ff;font-size:14px;text-decoration:none;">项目孵化</a></li>
          <li style="margin-bottom:12px;"><a href="/talent" target="_parent" style="color:#1890ff;font-size:14px;text-decoration:none;">人才培养</a></li>
          <li style="margin-bottom:12px;"><a href="/expert" target="_parent" style="color:#1890ff;font-size:14px;text-decoration:none;">专家中心</a></li>
          <li style="margin-bottom:12px;"><a href="/partner" target="_parent" style="color:#1890ff;font-size:14px;text-decoration:none;">合作伙伴</a></li>
          <li style="margin-bottom:12px;"><a href="/finance" target="_parent" style="color:#1890ff;font-size:14px;text-decoration:none;">金融服务</a></li>
        </ul>
      </div>
      <div>
        <h4 style="font-weight:600;margin-bottom:20px;">服务支持</h4>
        <ul style="list-style:none;padding:0;">
          <li style="margin-bottom:12px;"><a href="#" style="color:rgba(0,0,0,0.65);font-size:14px;text-decoration:none;">帮助中心</a></li>
          <li style="margin-bottom:12px;"><a href="#" style="color:rgba(0,0,0,0.65);font-size:14px;text-decoration:none;">客服中心</a></li>
          <li style="margin-bottom:12px;"><a href="#" style="color:rgba(0,0,0,0.65);font-size:14px;text-decoration:none;">使用指南</a></li>
          <li style="margin-bottom:12px;"><a href="#" style="color:rgba(0,0,0,0.65);font-size:14px;text-decoration:none;">常见问题</a></li>
        </ul>
      </div>
      <div>
        <h4 style="font-weight:600;margin-bottom:20px;">联系我们</h4>
        <ul style="list-style:none;padding:0;">
          <li style="display:flex;gap:12px;margin-bottom:12px;color:rgba(0,0,0,0.65);font-size:14px;"><i class="fas fa-map-marker-alt"></i> ${addr}</li>
          <li style="display:flex;gap:12px;margin-bottom:12px;color:rgba(0,0,0,0.65);font-size:14px;"><i class="fas fa-phone"></i> ${phone}</li>
          <li style="display:flex;gap:12px;margin-bottom:12px;color:rgba(0,0,0,0.65);font-size:14px;"><i class="fas fa-envelope"></i> ${email}</li>
        </ul>
      </div>
    </div>
    <div style="text-align:center;padding-top:24px;border-top:1px solid #f0f0f0;color:rgba(0,0,0,0.45);font-size:14px;">
      <p>&copy; 2024 大连山西商会科创中心 版权所有</p>
    </div>
  </div>
</footer>`

          editor.setComponents(html)
          return true

        } else if (page.page_path === 'home') {
          // 获取轮播图
          const carouselImages = Array.isArray(cfg.carousel_images) && cfg.carousel_images.length
            ? cfg.carousel_images
            : [{ url: 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2072&auto=format&fit=crop', title: '科技创新 · 引领未来' }]

          // 获取成果和需求数据
          let achievements = [], demands = []
          try {
            const [achRes, demRes] = await Promise.all([
              fetch(`${BASE_URL}/api/publish/public/achievements?limit=3`),
              fetch(`${BASE_URL}/api/publish/public/requirements?limit=3`)
            ])
            const achData = await achRes.json()
            const demData = await demRes.json()
            if (achData.code === 200) achievements = achData.data || []
            if (demData.code === 200) demands = demData.data || []
          } catch (e) { /* 静默失败，使用空数组 */ }

          const formatField = (fields, other) => {
            const arr = Array.isArray(fields) ? fields.filter(f => f !== '其他')
              : typeof fields === 'string' ? fields.split(',').map(s => s.trim()).filter(f => f !== '其他') : []
            let result = arr.join('、')
            if (other && other.trim()) result += (result ? '、' : '') + '其他：' + other.trim()
            return result || '其他'
          }

          const slidesHtml = carouselImages.map(img => `
            <div style="min-width:100%;height:100%;position:relative;overflow:hidden;">
              <img src="${img.url}" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;" data-gjs-type="image" />
              <span style="position:absolute;bottom:40px;left:50%;transform:translateX(-50%);background:rgba(0,0,0,0.6);color:white;padding:12px 24px;border-radius:30px;font-size:20px;font-weight:bold;">${img.title || ''}</span>
            </div>
          `).join('')

          const achievementCards = (achievements.length ? achievements : [{}]).map(item => {
            const methods = Array.isArray(item.transfer_methods) ? item.transfer_methods
              : typeof item.transfer_methods === 'string' ? item.transfer_methods.split(',').map(s => s.trim()).filter(Boolean) : []
            return `<div style="border:1px solid #e9ecef;border-radius:8px;padding:20px;min-height:120px;display:flex;justify-content:space-between;align-items:center;">
              <div style="flex:1;">
                <h3 style="font-size:16px;margin-bottom:8px;color:#333;">${item.achievement_name || '(暂无成果数据)'}</h3>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
                  <span style="font-size:13px;color:#666;">成果编号：${item.achievement_code || '-'}</span>
                  <span style="font-size:13px;color:#666;">拟转化方式：${formatField(methods, item.transfer_methods_other)}</span>
                  <span style="font-size:13px;color:#666;">所在地区：${item.region || '-'}</span>
                  <span style="font-size:13px;color:#666;">成熟度：${item.tech_maturity || '-'}</span>
                </div>
              </div>
              <div style="margin-left:20px;"><span style="padding:10px 20px;background:#2196f3;color:white;border:none;border-radius:4px;font-size:14px;cursor:pointer;">我要对接</span></div>
            </div>`
          }).join('')

          const demandCards = (demands.length ? demands : [{}]).map(item => {
            const fields = Array.isArray(item.tech_fields) ? item.tech_fields
              : typeof item.tech_fields === 'string' ? item.tech_fields.split(',').map(s => s.trim()).filter(Boolean) : []
            return `<div style="border:1px solid #e9ecef;border-radius:8px;padding:20px;min-height:120px;display:flex;justify-content:space-between;align-items:center;">
              <div style="flex:1;">
                <h3 style="font-size:16px;margin-bottom:8px;color:#333;">${item.demand_name || '(暂无需求数据)'}</h3>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
                  <span style="font-size:13px;color:#666;">需求编号：${item.demand_code || item.id || '-'}</span>
                  <span style="font-size:13px;color:#666;">技术领域：${formatField(fields, item.tech_fields_other)}</span>
                  <span style="font-size:13px;color:#666;">所在地区：${item.region || '-'}</span>
                  <span style="font-size:13px;color:#666;">供需状态：待对接</span>
                </div>
              </div>
              <div style="margin-left:20px;"><span style="padding:10px 20px;background:#2196f3;color:white;border:none;border-radius:4px;font-size:14px;cursor:pointer;">我要对接</span></div>
            </div>`
          }).join('')

          const html = `<section class="home-carousel" style="max-width:1200px;margin:20px auto;border-radius:8px;overflow:hidden;box-shadow:0 4px 15px rgba(0,0,0,0.1);">
  <div style="width:100%;height:400px;display:flex;overflow-x:auto;scroll-snap-type:x mandatory;scrollbar-width:none;">
    ${slidesHtml}
  </div>
</section>

<section class="home-actions" style="max-width:1200px;margin:30px auto;display:flex;justify-content:center;gap:40px;">
  <div style="padding:15px 50px;background:white;border:1px solid #e0e0e0;border-radius:30px;cursor:pointer;box-shadow:0 4px 6px rgba(0,0,0,0.05);font-size:18px;font-weight:bold;color:#333;transition:all 0.3s;text-align:center;">成果发布</div>
  <div style="padding:15px 50px;background:white;border:1px solid #e0e0e0;border-radius:30px;cursor:pointer;box-shadow:0 4px 6px rgba(0,0,0,0.05);font-size:18px;font-weight:bold;color:#333;transition:all 0.3s;text-align:center;">需求发布</div>
</section>

<section class="home-content" style="max-width:1200px;margin:0 auto 40px;">
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:30px;">
    <div class="home-column" style="background:white;border-radius:8px;padding:20px;box-shadow:0 2px 12px rgba(0,0,0,0.08);">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;padding-bottom:15px;border-bottom:1px solid #e0e0e0;">
        <h2 style="font-size:20px;color:#333;margin:0;">成果展示</h2>
        <span style="padding:6px 16px;border:1px solid #1890ff;color:#1890ff;border-radius:4px;font-size:14px;">更多 &gt;</span>
      </div>
      <div style="display:flex;flex-direction:column;gap:15px;">${achievementCards}</div>
    </div>
    <div class="home-column" style="background:white;border-radius:8px;padding:20px;box-shadow:0 2px 12px rgba(0,0,0,0.08);">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;padding-bottom:15px;border-bottom:1px solid #e0e0e0;">
        <h2 style="font-size:20px;color:#333;margin:0;">需求展示</h2>
        <span style="padding:6px 16px;border:1px solid #1890ff;color:#1890ff;border-radius:4px;font-size:14px;">更多 &gt;</span>
      </div>
      <div style="display:flex;flex-direction:column;gap:15px;">${demandCards}</div>
    </div>
  </div>
</section>`

          editor.setComponents(html)
          return true
        }
      } catch (e) {
        console.error('自动填充页面失败:', e)
      }
      return false
    }

    async function savePage() {
      if (!editor || !currentPageId.value) return
      isSaving.value = true
      try {
        const html = editor.getHtml()
        const css = editor.getCss()
        const gjsData = JSON.stringify(editor.getProjectData())
        const res = await fetch(`${BASE_URL}/api/editor/site/pages/${currentPageId.value}`, {
          method: 'PUT',
          headers: authHeaders(),
          body: JSON.stringify({ html_content: html, css_content: css, gjs_data: gjsData })
        })
        const data = await res.json()
        if (data.code === 200) {
          ElMessage.success('保存成功')
        } else {
          ElMessage.error(data.msg || '保存失败')
        }
      } catch (e) {
        ElMessage.error('保存失败：' + e.message)
      }
      isSaving.value = false
    }

    async function previewPage() {
      if (!editor || !currentPageId.value) return
      const html = editor.getHtml()
      const css = editor.getCss()
      const full = `<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>预览</title><style>${css}</style></head><body>${html}</body></html>`
      const win = window.open('', '_blank')
      if (win) { win.document.write(full); win.document.close() }
    }

    // ========== 全局配置 ==========
    async function openConfigDialog() {
      try {
        const res = await fetch(`${BASE_URL}/api/editor/config/all`)
        const data = await res.json()
        if (data.code === 200 && data.data) {
          const d = data.data
          if (d.site_name) globalConfig.site_name = d.site_name
          if (d.browser_title) globalConfig.browser_title = d.browser_title
          else globalConfig.browser_title = document.title // 自动获取当前浏览器标签标题
          if (d.site_logo) globalConfig.site_logo = d.site_logo
          if (d.favicon) globalConfig.favicon = d.favicon
          if (Array.isArray(d.nav_menu)) globalConfig.nav_menu = d.nav_menu
        } else {
          // API返回空时也使用当前页面标题
          globalConfig.browser_title = document.title
        }
      } catch (e) {
        console.error('加载配置失败:', e)
        globalConfig.browser_title = document.title
      }
      showConfigDialog.value = true
    }

    function openImgPreview(url) {
      previewImgUrl.value = url
      showImgPreview.value = true
    }

    function openLogoPreview() {
      const url = globalConfig.site_logo ? resolveImg(globalConfig.site_logo) : defaultLogoUrl
      if (url) { previewImgUrl.value = url; showImgPreview.value = true }
    }

    async function saveGlobalConfig() {
      configSaving.value = true
      try {
        const payload = {
          site_name: globalConfig.site_name,
          browser_title: globalConfig.browser_title,
          site_logo: globalConfig.site_logo,
          favicon: globalConfig.favicon,
          nav_menu: globalConfig.nav_menu
        }
        const res = await fetch(`${BASE_URL}/api/editor/config/update`, {
          method: 'POST',
          headers: authHeaders(),
          body: JSON.stringify(payload)
        })
        const data = await res.json()
        if (data.code === 200) {
          ElMessage.success('站点设置保存成功！刷新前台即可看到效果')
          showConfigDialog.value = false
        } else {
          ElMessage.error(data.message || '保存失败')
        }
      } catch (e) { ElMessage.error('保存失败') }
      configSaving.value = false
    }

    // ========== 图片上传 ==========
    async function uploadLogo(options) {
      const fd = new FormData(); fd.append('file', options.file)
      const res = await fetch(`${BASE_URL}/api/editor/upload/image`, {
        method: 'POST', headers: { 'Authorization': `Bearer ${localStorage.getItem(STORAGE_KEY)}` }, body: fd
      })
      const data = await res.json()
      if (data.code === 200) { globalConfig.site_logo = data.data.url; ElMessage.success('上传成功') }
      else { ElMessage.error(data.message || '上传失败') }
    }

    async function uploadFavicon(options) {
      const fd = new FormData(); fd.append('file', options.file)
      const res = await fetch(`${BASE_URL}/api/editor/upload/image`, {
        method: 'POST', headers: { 'Authorization': `Bearer ${localStorage.getItem(STORAGE_KEY)}` }, body: fd
      })
      const data = await res.json()
      if (data.code === 200) { globalConfig.favicon = data.data.url; ElMessage.success('上传成功') }
      else { ElMessage.error(data.message || '上传失败') }
    }

    // ========== 导入HTML ==========
    function openImportModal() {
      importHtmlText.value = ''
      importCssText.value = ''
      showImportModal.value = true
    }

    function confirmImport() {
      if (!editor) return
      if (importHtmlText.value.trim()) editor.setComponents(importHtmlText.value.trim())
      if (importCssText.value.trim()) editor.setStyle(importCssText.value.trim())
      showImportModal.value = false
      ElMessage.success('已导入到编辑器')
    }

    // ========== 全屏 ==========
    function toggleFullscreen() {
      if (editor) editor.runCommand('core:fullscreen')
    }

    // ========== 返回 ==========
    function goBack() { router.push('/admin') }

    // ========== GrapesJS 初始化 ==========
    function initEditor() {
      if (editor) return
      editor = grapesjs.init({
        container: '#gjs',
        height: '100%',
        width: '100%',
        storageManager: false,
        undoManager: true,
        fromElement: false,
        selectorManager: { componentFirst: true },

        plugins: [webPreset, formsPlugin, navbarPlugin, tabsPlugin,
          flexboxPlugin, customCodePlugin,
          styleBgPlugin, styleGradientPlugin, styleFilterPlugin,
          suggestClassesPlugin, floatPlugin],

        styleManager: {
          sectors: [
            { name: '布局', open: false, buildProps: ['display', 'position', 'width', 'height', 'max-width', 'overflow'] },
            { name: '间距', open: false, buildProps: ['margin', 'margin-top', 'margin-bottom', 'padding', 'padding-top', 'padding-bottom'] },
            { name: '背景', open: false, buildProps: ['background-color', 'background-image', 'background-size', 'background-repeat'] },
            { name: '排版', open: false, buildProps: ['font-family', 'font-size', 'font-weight', 'color', 'text-align', 'line-height'] },
            { name: '边框', open: false, buildProps: ['border', 'border-radius', 'box-shadow'] },
            { name: '特效', open: false, buildProps: ['opacity', 'transition', 'transform'] },
            { name: 'Flex', open: false, buildProps: ['flex-direction', 'flex-wrap', 'justify-content', 'align-items', 'gap'] }
          ]
        },

        canvas: {
          styles: [
            'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css'
          ]
        },

        deviceManager: {
          devices: [
            { name: '桌面', width: '', priority: 1 },
            { name: '平板', width: '768px', priority: 2 },
            { name: '手机', width: '375px', priority: 3 }
          ]
        }
      })

      // 注册自定义块（不覆盖插件默认块）
      const bm = editor.BlockManager
      bm.add('section-hero', {
        label: '<b>🏠 首页横幅</b>',
        content: `<section style="position:relative;height:400px;background:linear-gradient(135deg,rgba(24,144,255,0.9),rgba(0,21,41,0.9)),url('https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1600');background-size:cover;background-position:center;display:flex;align-items:center;justify-content:center;">
          <div style="text-align:center;color:white;max-width:800px;padding:0 20px;">
            <h1 style="font-size:36px;margin-bottom:16px;">科技创新 · 引领未来</h1>
            <p style="font-size:16px;opacity:0.85;">推动科技成果转化，服务产业创新发展</p>
          </div>
        </section>`
      })
      bm.add('section-about-banner', {
        label: '<b>📄 关于我们横幅</b>',
        content: `<section style="position:relative;height:280px;background:linear-gradient(135deg,rgba(24,144,255,0.85),rgba(0,21,41,0.85)),url('https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1600');background-size:cover;background-position:center;display:flex;align-items:center;justify-content:center;">
          <div style="text-align:center;color:white;"><h1 style="font-size:36px;">关于我们</h1></div>
        </section>`
      })
      bm.add('section-intro', {
        label: '<b>📝 公司简介</b>',
        content: `<section style="padding:48px 0;background:white;"><div style="max-width:1200px;margin:0 auto;padding:0 20px;">
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:48px;align-items:center;">
            <div><h2 style="font-size:28px;margin-bottom:20px;">商会简介</h2><p style="font-size:15px;color:rgba(0,0,0,0.62);line-height:1.9;">大连市山西商会科创中心是在自愿、平等、合作、互利的基础上，由大连市山西商会发起，联合企业、高校和科研院所有识之士共同组建的产学研成果对接和创业孵化非营利性组织。</p></div>
            <div style="min-height:320px;border:2px solid rgba(24,144,255,0.2);border-radius:8px;display:flex;align-items:center;justify-content:center;"><img src="https://images.unsplash.com/photo-1581093450021-4a7360e9a6b5?w=800" style="width:100%;border-radius:8px;box-shadow:0 8px 24px rgba(0,0,0,0.1);" /></div>
          </div>
        </div></section>`
      })
      bm.add('section-mission', {
        label: '<b>🎯 使命愿景</b>',
        content: `<section style="padding:48px 0;background:#fafafa;"><div style="max-width:1200px;margin:0 auto;padding:0 20px;">
          <div style="text-align:center;margin-bottom:40px;"><h2 style="font-size:24px;">使命与愿景</h2></div>
          <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:24px;">
            <div style="background:white;padding:32px 20px;border-radius:8px;text-align:center;border:1px solid #f0f0f0;">
              <div style="width:64px;height:64px;margin:0 auto 20px;border-radius:50%;background:linear-gradient(135deg,#1890ff,#096dd9);display:flex;align-items:center;justify-content:center;font-size:28px;color:white;">🚀</div>
              <h3 style="font-size:18px;margin-bottom:12px;">高水平转化一批成果</h3>
              <p style="font-size:14px;color:rgba(0,0,0,0.65);">推动科研成果高效转化</p>
            </div>
            <div style="background:white;padding:32px 20px;border-radius:8px;text-align:center;border:1px solid #f0f0f0;">
              <div style="width:64px;height:64px;margin:0 auto 20px;border-radius:50%;background:linear-gradient(135deg,#52c41a,#389e0d);display:flex;align-items:center;justify-content:center;font-size:28px;color:white;">💡</div>
              <h3 style="font-size:18px;margin-bottom:12px;">高产值孵化一批公司</h3>
              <p style="font-size:14px;color:rgba(0,0,0,0.65);">孵化科技型企业</p>
            </div>
            <div style="background:white;padding:32px 20px;border-radius:8px;text-align:center;border:1px solid #f0f0f0;">
              <div style="width:64px;height:64px;margin:0 auto 20px;border-radius:50%;background:linear-gradient(135deg,#722ed1,#531dab);display:flex;align-items:center;justify-content:center;font-size:28px;color:white;">⚙</div>
              <h3 style="font-size:18px;margin-bottom:12px;">高技术赋能一批企业</h3>
              <p style="font-size:14px;color:rgba(0,0,0,0.65);">技术赋能产业升级</p>
            </div>
            <div style="background:white;padding:32px 20px;border-radius:8px;text-align:center;border:1px solid #f0f0f0;">
              <div style="width:64px;height:64px;margin:0 auto 20px;border-radius:50%;background:linear-gradient(135deg,#faad14,#d48806);display:flex;align-items:center;justify-content:center;font-size:28px;color:white;">👤</div>
              <h3 style="font-size:18px;margin-bottom:12px;">高质量培养一批人才</h3>
              <p style="font-size:14px;color:rgba(0,0,0,0.65);">培养复合型人才</p>
            </div>
          </div>
        </div></section>`
      })
      bm.add('section-advantages', {
        label: '<b>⭐ 核心优势</b>',
        content: `<section style="padding:48px 0;background:white;"><div style="max-width:1200px;margin:0 auto;padding:0 20px;">
          <div style="text-align:center;margin-bottom:40px;"><h2 style="font-size:24px;">核心优势</h2></div>
          <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:24px;">
            <div style="padding:24px;border:1px solid #f0f0f0;border-radius:8px;text-align:center;">
              <div style="width:56px;height:56px;margin:0 auto 16px;border-radius:50%;background:linear-gradient(135deg,#1890ff,#096dd9);display:flex;align-items:center;justify-content:center;color:white;font-size:24px;">👥</div>
              <h3 style="font-size:16px;margin-bottom:8px;">专业团队</h3>
              <p style="font-size:14px;color:rgba(0,0,0,0.65);">汇聚行业顶尖专家</p>
            </div>
            <div style="padding:24px;border:1px solid #f0f0f0;border-radius:8px;text-align:center;">
              <div style="width:56px;height:56px;margin:0 auto 16px;border-radius:50%;background:linear-gradient(135deg,#1890ff,#096dd9);display:flex;align-items:center;justify-content:center;color:white;font-size:24px;">🛡</div>
              <h3 style="font-size:16px;margin-bottom:8px;">安全可靠</h3>
              <p style="font-size:14px;color:rgba(0,0,0,0.65);">严格质量管控体系</p>
            </div>
            <div style="padding:24px;border:1px solid #f0f0f0;border-radius:8px;text-align:center;">
              <div style="width:56px;height:56px;margin:0 auto 16px;border-radius:50%;background:linear-gradient(135deg,#1890ff,#096dd9);display:flex;align-items:center;justify-content:center;color:white;font-size:24px;">🤝</div>
              <h3 style="font-size:16px;margin-bottom:8px;">生态合作</h3>
              <p style="font-size:14px;color:rgba(0,0,0,0.65);">深度合作共赢</p>
            </div>
          </div>
        </div></section>`
      })
      bm.add('section-footer', {
        label: '<b>🏢 页脚</b>',
        content: `<footer style="padding:48px 0 24px;background:#fafafa;border-top:1px solid #f0f0f0;">
          <div style="max-width:1200px;margin:0 auto;padding:0 20px;">
            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:48px;margin-bottom:40px;">
              <div><h3 style="margin-bottom:16px;">大连山西商会科创中心</h3><p style="font-size:14px;color:rgba(0,0,0,0.65);">产学研成果对接平台</p></div>
              <div><h4 style="margin-bottom:16px;">快速链接</h4><ul style="list-style:none;padding:0;"><li style="margin-bottom:8px;"><a href="/achievement" style="color:rgba(0,0,0,0.65);text-decoration:none;">成果中心</a></li><li style="margin-bottom:8px;"><a href="/demand" style="color:rgba(0,0,0,0.65);text-decoration:none;">需求中心</a></li></ul></div>
              <div><h4 style="margin-bottom:16px;">联系我们</h4><ul style="list-style:none;padding:0;"><li style="margin-bottom:8px;font-size:14px;color:rgba(0,0,0,0.65);">电话：xxxxxxxx</li><li style="margin-bottom:8px;font-size:14px;color:rgba(0,0,0,0.65);">邮箱：xxxxxxxx</li></ul></div>
            </div>
            <div style="text-align:center;padding-top:24px;border-top:1px solid #f0f0f0;color:rgba(0,0,0,0.45);font-size:14px;">
              <p>© 2024 大连山西商会科创中心 版权所有</p>
            </div>
          </div>
        </footer>`
      })
      bm.add('text-block', {
        label: '<b>📝 文本块</b>',
        content: '<div style="padding:20px;font-size:16px;line-height:1.8;"><h2 style="margin-bottom:16px;">标题</h2><p>在此输入正文内容...</p></div>'
      })
      bm.add('image-full', {
        label: '<b>🖼 图片</b>',
        content: '<div style="padding:20px;text-align:center;min-height:320px;border:2px solid rgba(24,144,255,0.2);border-radius:8px;"><img src="https://via.placeholder.com/800x400" style="max-width:100%;border-radius:8px;" /></div>'
      })

      // —— 联网备案号组件（Extra 类别）——
      const BEIAN_BASE64 = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACQAAAAoCAYAAACWwljjAAAFQklEQVRYw+3Wa1BUdRjH8SOpMeg4WhZGpDIxiaaTeUFgWrxE4AVRQJGlRRAVIV1JkbgMgQLi5AVBQSVLSp0xlEAUKBEEFZCrCstll8UV2AV2YbmoGCrYv31+R95UL5pmmtamZ+bz6rz5nvOc/5zDcX9jGLs/iTxuyvIlWYkRFeTHA2HVRFtzfhthTG5KuH96/vUgNlC4mMgyw1NJit/aAXLKazYje9xtIMZ/OZz50gW+9hcNkvoLEemEPbnrSP47QYwxQ5Ifv54RqzcXwFFvSyjaOhfavN8F7Y5ZcC/HH9JOB4LNa9Zw5YA76OZV8vIGMdZtSp7cDrtOnOavYiQhTAiPwi1AMtIQaqyngsxpBtw2GAGDKfaQmpUAa6xc4Vfp4UtEdzAMycsT9JQ1Tyctl/2eEkuTlYysF/rCUNxMqDEzgTqzSXBnpgnIHCzgjvEEuD52DLBr3rA1MAaWmNtB582wdtIljZ9G9D+IPU6aTxIPBjHCcXvg3CEh9K2fDLWvjIH6D6fwTIyheuwEqLUyhzLOALq8pkN+bgRw3HY4FBsMzxojZxP9DequLjAlQwVrbpIjhyIY4UYGQ/buhdBqPxlk3Gion2IMDQIz3kJe/ZS34I7uHkmD7VSQVgYDNyIAwsNCgfXGXoOBPjP9DKrOCAogA2etGTmTHAMcFwFZye7wS5QlVHGjoEw4A2qPCUBZ6AzNcQ5Q/YYRdO+YB1U3dsDwypLio4FJ3ECryIzWz6Cm3NgTRHN8HiPF6eHAGSbAdh8feFZkB7krzaHE9h2o85sDsiAbkIsXQMN+e2CtGyF0kzdwXCgU5++D/ouLQFV4OEU/g2Q/iNuIPNaKkQflAWBqexxGjhLDVUcL6IwSQN3SGVChe6FJg9dckCx6D1QBliDZLIAxo7eA8eyv4KE0BJqTrHkZvnL9DJKn+Twmt0NsGGHZy2Dn3kQYfsQ53Hh4/r4RNGz8AIpdzKEuaAF0RC2E57MmQgE3ATjuM/CPiANW7AqSfQJQ5vk362eQKmd3JrmXsoSRocpNIMnbB9zbceDIWUPmuHFQNMkISqa9DpUvNK6YDpW2s8DfwBK48WFQnhMCgzUBoLy0BrRVe5P0NWjPLdKUsJiR1tR1wGp8IeZwMgx/SrgRvjxuAziNcwLvyathLOcJHLflhRDYGRYFrNET2rJ5yvPLoas0tOj/oL8UpC4JHyTSU+6MNCS4gvKoAB5WiKG+MAQSg0WwLXQ/ZJ3xhao0FxB5hYCbUwAEfhEF3Td8QP2dAOQnPwFlxgrolUVq9TPoaX+ZB2nLc2Gk6awj1MU78HZZwJMid2Byb550JQwVO0NfxlJgdz14vWKeRAiK6DlQF28PLZdcoLNcBIO92bb6GTQ8Q/13RURT6tlH2gvXMlITLYD6uI+gp2ozdF0VQXumM6ivCqGvahM8kPiDItkeGo8tB025GFQ3xFrSr06zI3/4yde7oN7m0sWk5eKWDqK5JWJQvAHac9ygq3Adr9gTNNc3QG85rzPfHe5/7wDtPwuhp/Zz6CjyhaZzwi6ivfetHdH/oP77+3PJQOsuRnqkQdCa4wWqyx6gyecpL64GTaEX7ycXUJz4GJp0B4O0X/Hg0Xp1tFV+8Ei1k6c5coHofxBrrzQinbKYo0SVJ+wn6iurGHlY5gY911aDJnMFaHXXiDp9GQyvtKfUA9QFTtBZ7gPdit0tpFd9OpwwFmlA9D/o9yNLDpxIKmI8PMnNSNtviCLVpYTITzrXEGWaq4qos0WgOPdpCenIF+eRrurjB4k0PXopYZG6gMg/D/gNBUxhAbSAmKMAAAAASUVORK5CYII='
      bm.add('beian-icp', {
        label: '<b>📋 联网备案号</b>',
        category: { id: 'extra', label: '📦 Extra' },
        content: `<section style="padding:20px 0;background:#fafafa;border-top:1px solid #f0f0f0;">
          <div style="max-width:1200px;margin:0 auto;padding:0 20px;display:flex;align-items:center;justify-content:center;gap:4px;flex-wrap:wrap;">
            <img src="${BEIAN_BASE64}" style="width:20px;height:24px;vertical-align:middle;display:inline-block;" />
            <a href="https://beian.mps.gov.cn/#/query/webSearch?code=21029602001232" rel="noreferrer" target="_blank" style="font-size:14px;color:rgba(0,0,0,0.65);text-decoration:none;vertical-align:middle;">
              辽公网安备21029602001232号
            </a>
            <span style="font-size:14px;color:rgba(0,0,0,0.35);margin:0 4px;">|</span>
            <a href="https://beian.miit.gov.cn/#/Integrated/index" rel="noreferrer" target="_blank" style="font-size:14px;color:rgba(0,0,0,0.65);text-decoration:none;vertical-align:middle;">
              辽ICP备2026005357号
            </a>
          </div>
          <div style="text-align:center;padding-top:12px;color:rgba(0,0,0,0.45);font-size:14px;">
            &copy; 2024 大连山西商会科创中心 版权所有
          </div>
        </section>`
      })

      editor.on('load', () => {
        const pn = editor.Panels
        const blockBtn = pn.getButton('views', 'open-blocks')
        if (blockBtn) blockBtn.set('active', true)
        loadPages()
      })
    }

    // ========== 生命周期 ==========
    onMounted(async () => {
      const ok = await tryAdminAutoLogin()
      if (ok) {
        await nextTick()
        initEditor()
      }
    })

    onUnmounted(() => {
      if (editor) { editor.destroy(); editor = null }
    })

    return {
      isLoggedIn, loginForm, loginLoading, loginError, handleLogin,
      pages, editablePages, currentPageId, pageLoading, isSaving,
      switchPage, savePage, previewPage, goBack,
      showConfigDialog, configTab, configSaving, globalConfig,
      openConfigDialog, saveGlobalConfig, resolveImg, beforeImageUpload,
      uploadLogo, uploadFavicon,
      showImportModal, importHtmlText, importCssText, openImportModal, confirmImport,
      showImgPreview, previewImgUrl, openImgPreview, openLogoPreview,
      defaultLogoUrl, defaultFaviconUrl,
      toggleFullscreen,
      Delete, Setting, Picture, Monitor, Upload, HomeFilled, Menu, List, Plus, ZoomIn
    }
  }
}
</script>

<style scoped>
/* ===== 全局 ===== */
.editor-app {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  z-index: 10000;
  background: #f0f2f5;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
}
.form-input { width:100%; padding:8px 12px; border:1px solid #d9d9d9; border-radius:6px; font-size:14px; outline:none; box-sizing:border-box; }
.form-input:focus { border-color:#4a90d9; box-shadow:0 0 0 2px rgba(74,144,217,.15); }

/* ===== 登录 ===== */
.login-layout {
  display:flex; align-items:center; justify-content:center;
  height:100%;
  background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460);
}
.login-card {
  background:#fff; border-radius:16px; padding:40px; width:360px;
  box-shadow:0 20px 60px rgba(0,0,0,.3); text-align:center;
}
.login-icon { font-size:48px; margin-bottom:8px; }
.login-card h2 { margin:0 0 4px; font-size:22px; color:#333; }
.login-form { text-align:left; }
.login-form .form-group { margin-bottom:16px; }
.login-error { color:#e74c3c; font-size:13px; margin-bottom:12px; }
.login-btn {
  width:100%; padding:10px; background:#4a90d9; color:#fff; border:none;
  border-radius:8px; font-size:15px; cursor:pointer; transition:background .2s;
}
.login-btn:hover { background:#357abd; }
.login-btn:disabled { background:#a0c4e8; cursor:not-allowed; }

/* ===== 编辑器布局 ===== */
.editor-layout {
  display:flex; flex-direction:column; height:100vh; width:100vw; overflow:hidden;
}

/* ===== 顶部工具栏 ===== */
.editor-topbar {
  display:flex; align-items:center; justify-content:space-between;
  height:48px; padding:0 14px;
  background:#2c3e50; color:#fff; flex-shrink:0; gap:10px;
  z-index:10001;
}
.topbar-left { display:flex; align-items:center; gap:10px; }
.topbar-brand { font-size:15px; font-weight:600; }
.topbar-sep { color:#5a7a9a; }
.topbar-center { display:flex; align-items:center; gap:6px; }
.topbar-right { display:flex; align-items:center; gap:6px; }
.page-select {
  padding:4px 8px; border:1px solid #5a7a9a; border-radius:4px;
  background:#34495e; color:#fff; font-size:13px; min-width:130px; outline:none;
}
.page-select option { background:#fff; color:#333; }
.tb-btn {
  padding:5px 12px; border:1px solid #5a7a9a; border-radius:4px;
  background:transparent; color:#ecf0f1; font-size:13px; cursor:pointer;
  transition:all .2s; white-space:nowrap;
}
.tb-btn:hover { background:#34495e; border-color:#7fa5c7; }
.tb-btn:disabled { opacity:.4; cursor:not-allowed; }
.save-btn { background:#27ae60; border-color:#27ae60; color:#fff; }
.save-btn:hover { background:#2ecc71; }
.config-btn { background:#e6a23c; border-color:#e6a23c; }
.config-btn:hover { background:#ebb563; }
.back-btn { border-color:#5a7a9a; }

/* ===== 编辑器主体 ===== */
.editor-main {
  flex:1; position:relative; overflow:hidden;
}
#gjs {
  height:100%; width:100%; border:none;
}
/* 覆盖 GrapesJS 样式，使其从头填充 */
#gjs .gjs-editor, #gjs .gjs-cv-canvas { top:0; }

/* ===== 加载遮罩 ===== */
.canvas-loader {
  position:absolute; top:0; left:0; right:0; bottom:0;
  background:rgba(255,255,255,.85); display:flex; align-items:center; justify-content:center;
  gap:12px; z-index:100;
}
.loader-spinner {
  width:32px; height:32px; border:3px solid #e0e0e0; border-top-color:#4a90d9;
  border-radius:50%; animation:spin .8s linear infinite;
}
@keyframes spin { to { transform:rotate(360deg) } }

/* ===== 全局设置弹窗 ===== */
.config-dialog .el-dialog__body { padding:16px 24px; }
.config-tabs .el-tabs__content { padding:8px 4px 4px; }
.config-card {
  border:1px solid #ebeef5;
  border-radius:8px;
  background:#fff;
  overflow:hidden;
  transition:box-shadow .2s;
}
.config-card:hover { box-shadow:0 2px 12px rgba(0,0,0,.06); }
.config-card-header {
  display:flex; align-items:center; gap:8px;
  padding:12px 16px;
  background:#f8f9fb;
  border-bottom:1px solid #ebeef5;
  font-size:14px; font-weight:600; color:#303133;
}
.config-card-body { padding:16px; }
.config-field { margin-bottom:18px; }
.config-field:last-child { margin-bottom:0; }
.config-field-label {
  font-size:13px; font-weight:500; color:#606266;
  margin-bottom:8px;
}
.config-field-hint {
  font-size:12px; color:#909399;
  margin-top:4px;
}
.config-preview-tip {
  font-size:12px; color:#909399;
}
.logo-preview {
  position:relative;
  width:200px; min-height:56px;
  border:1px solid #e4e7ed; border-radius:6px;
  background:#fafafa;
  display:flex; align-items:center; justify-content:center;
  cursor:pointer; overflow:hidden; flex-shrink:0;
  transition:border-color .2s;
}
.logo-preview:hover { border-color:#409eff; }
.logo-preview img {
  max-height:48px; max-width:180px;
  object-fit:contain; display:block; padding:4px;
}
.preview-overlay {
  position:absolute; inset:0;
  background:rgba(0,0,0,.03);
  display:flex; align-items:center; justify-content:center;
  opacity:0; transition:opacity .2s;
  color:#409eff; font-size:18px;
}
.logo-preview:hover .preview-overlay { opacity:1; }
.favicon-preview {
  width:42px; height:42px; flex-shrink:0;
  border:1px solid #e4e7ed; border-radius:6px;
  background:#fafafa;
  display:flex; align-items:center; justify-content:center;
  cursor:pointer; overflow:hidden;
  transition:border-color .2s;
}
.favicon-preview:hover { border-color:#409eff; }
.favicon-preview img {
  max-height:28px; max-width:28px;
  object-fit:contain; display:block;
}
.nav-menu-item {
  display:flex; gap:10px; align-items:center;
  margin-bottom:10px; padding:8px 10px;
  border:1px solid #ebeef5; border-radius:6px;
  background:#fafcff;
  transition:border-color .2s;
}
.nav-menu-item:hover { border-color:#c0c4cc; }
.nav-menu-index {
  display:inline-flex; align-items:center; justify-content:center;
  width:24px; height:24px; flex-shrink:0;
  background:#ecf5ff; color:#409eff;
  border-radius:50%; font-size:12px; font-weight:600;
}
</style>
