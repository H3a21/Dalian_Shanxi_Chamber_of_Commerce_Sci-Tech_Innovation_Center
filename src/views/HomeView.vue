<template>
  <div class="home">
    <!-- 加载状态 -->
    <div v-if="pageLoading" class="page-loading">
      <div class="loader-spinner"></div>
      <span>加载中...</span>
    </div>

    <template v-else>
      <!-- ===== Vue 动态组件（轮播图、按钮、成果/需求卡片） ===== -->
      <el-carousel :interval="3000" height="400px" class="hero-carousel">
        <el-carousel-item v-for="(image, index) in carouselImages" :key="index">
          <div class="carousel-image" :style="{ backgroundImage: `url(${resolveImageUrl(image.url)})` }">
            <div class="carousel-caption">{{ image.title }}</div>
          </div>
        </el-carousel-item>
      </el-carousel>
      <div class="action-buttons">
        <button class="action-btn" @click="goToAchievement">成果发布</button>
        <button class="action-btn" @click="goToDemand">需求发布</button>
      </div>
      <div class="display-modules">
        <div class="two-column-layout">
          <div class="column achievement-column">
            <div class="column-header">
              <h2 class="column-title">成果展示</h2>
              <button class="more-btn" @click="goToAchievementCenter">更多 &gt;</button>
            </div>
            <div class="cards-list">
              <div v-for="achievement in achievementList" :key="achievement.id" class="result-card" @click="openAchievementDrawer(achievement)">
                <div class="result-content">
                  <h3>{{ achievement.title }}</h3>
                  <div class="result-meta">
                    <span class="meta-item">成果编号：{{ achievement.code }}</span>
                    <span class="meta-item">拟转化方式：{{ achievement.transferType }}</span>
                    <span class="meta-item">所在地区：{{ achievement.region }}</span>
                    <span class="meta-item">成熟度：{{ achievement.maturity }}</span>
                  </div>
                </div>
                <div class="result-actions">
                  <button class="contact-btn" @click.stop="openChatModal('achievement', achievement.code)">我要对接</button>
                </div>
              </div>
            </div>
          </div>
          <div class="column demand-column">
            <div class="column-header">
              <h2 class="column-title">需求展示</h2>
              <button class="more-btn" @click="goToDemandCenter">更多 &gt;</button>
            </div>
            <div class="cards-list">
              <div v-for="demand in demandList" :key="demand.id" class="demand-item" @click="openDemandDrawer(demand)">
                <div class="demand-content">
                  <h3>{{ demand.title }}</h3>
                  <div class="demand-meta">
                    <span class="meta-item">需求编号：{{ demand.id }}</span>
                    <span class="meta-item">技术领域：{{ demand.techField }}</span>
                    <span class="meta-item">所在地区：{{ demand.region }}</span>
                    <span class="meta-item">需求类型：{{ demand.type }}</span>
                    <span class="meta-item">供需状态：{{ demand.status }}</span>
                  </div>
                </div>
                <div class="demand-actions">
                  <button class="contact-btn" @click.stop="openChatModal('demand', demand.id)">我要对接</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ===== 编辑器自定义内容（用户添加的备案号等组件，剥离自动填充部分后只保留用户自加内容） ===== -->
      <div v-if="editorCustomHtml" class="editor-custom-area" v-html="editorCustomHtml"></div>
    </template>

    <!-- ===== Vue 交互组件（不受 v-html 影响） ===== -->

    <!-- 成果详情抽屉 -->
    <div class="drawer-overlay" :class="{ active: showAchievementDrawer }" @click="closeAchievementDrawer"></div>
    <div class="drawer" :class="{ active: showAchievementDrawer }">
      <div class="drawer-header">
        <h2 class="drawer-title">成果详情</h2>
        <div class="drawer-close" @click="closeAchievementDrawer">&times;</div>
      </div>
      <div class="drawer-body">
        <fieldset class="form-section">
          <legend>一、成果基本信息</legend>
          <div class="form-grid">
            <div class="form-item full-width">
              <label>成果名称：</label>
              <span class="readonly-field" style="font-weight: bold; color: #2196f3;">{{ drawerAchievement.title || '-' }}</span>
            </div>
            <div class="form-item">
              <label>企业名称/持有人：</label>
              <span class="readonly-field">{{ drawerAchievement.owner || '-' }}</span>
            </div>
            <div class="form-item">
              <label>成果编号：</label>
              <span class="readonly-field">{{ drawerAchievement.code || '-' }}</span>
            </div>
            <div class="form-item">
              <label>技术领域：</label>
              <span class="readonly-field">{{ drawerAchievement.field || '-' }}</span>
            </div>
            <div class="form-item">
              <label>技术成熟度：</label>
              <span class="readonly-field" style="font-weight: bold; color: #2196f3;">{{ drawerAchievement.maturity || '-' }}</span>
            </div>
            <div class="form-item full-width">
              <label>拟转化方式：</label>
              <span class="readonly-field">{{ drawerAchievement.transferDisplay || '-' }}</span>
            </div>
          </div>
        </fieldset>

        <fieldset class="form-section">
          <legend>二、成果描述</legend>
          <div class="form-item full-width" style="margin-bottom: 15px;">
            <label>成果摘要：</label>
            <div class="readonly-field" style="height: auto;">{{ drawerAchievement.summary || '-' }}</div>
          </div>
          <div class="form-item full-width" style="margin-bottom: 15px;">
            <label>技术优势描述：</label>
            <div class="readonly-field" style="height: auto;">{{ drawerAchievement.advantage || '-' }}</div>
          </div>
          <div class="form-grid">
            <div class="form-item">
              <label>创新性评价：</label>
              <span class="readonly-field">{{ drawerAchievement.innovation || '-' }}</span>
            </div>
            <div class="form-item">
              <label>核心技术指标：</label>
              <span class="readonly-field">{{ drawerAchievement.indicator || '-' }}</span>
            </div>
            <div class="form-item full-width">
              <label>与现有技术相比的优势：</label>
              <div class="readonly-field" style="height: auto;">{{ drawerAchievement.compare || '-' }}</div>
            </div>
            <div class="form-item full-width">
              <label>获得的知识产权情况：</label>
              <div class="readonly-field" style="height: auto;">{{ drawerAchievement.ipr || '-' }}</div>
            </div>
          </div>
        </fieldset>

        <fieldset class="form-section">
          <legend>三、成果转化期望</legend>
          <div class="form-item full-width">
            <label>合作方式偏好及财务预期：</label>
            <span class="readonly-field" style="color: #faad14; font-weight: bold;">{{ drawerAchievement.collab || '-' }}</span>
          </div>
          <div class="form-item full-width">
            <label>期望完成转化时间：</label>
            <span class="readonly-field">{{ drawerAchievement.deadline || '-' }}</span>
          </div>
        </fieldset>
      </div>
      <div class="drawer-footer">
        <button class="contact-btn" style="width: 260px; height: 45px; font-size: 16px; font-weight: bold;" @click="handleDrawerContact('achievement')">立即对接</button>
      </div>
    </div>

    <!-- 需求详情抽屉 -->
    <div class="drawer-overlay" :class="{ active: showDemandDrawer }" @click="closeDemandDrawer"></div>
    <div class="drawer" :class="{ active: showDemandDrawer }">
      <div class="drawer-header">
        <h2 class="drawer-title">需求详情</h2>
        <div class="drawer-close" @click="closeDemandDrawer">&times;</div>
      </div>
      <div class="drawer-body">
        <fieldset class="form-section">
          <legend>一、需求基本信息</legend>
          <div class="form-grid">
            <div class="form-item full-width">
              <label>需求名称：</label>
              <span id="dt-title" class="readonly-field" style="font-weight: bold; color: #2196f3;">{{ drawerDemand.title || '-' }}</span>
            </div>
            <div class="form-item">
              <label>企业名称：</label>
              <span id="dt-org" class="readonly-field">{{ drawerDemand.org || '-' }}</span>
            </div>
            <div class="form-item">
              <label>需求编号：</label>
              <span id="dt-id" class="readonly-field">{{ drawerDemand.id || '-' }}</span>
            </div>
            <div class="form-item">
              <label>所属地区：</label>
              <span id="dt-region" class="readonly-field">{{ drawerDemand.region || '-' }}</span>
            </div>
            <div class="form-item">
              <label>技术领域：</label>
              <span id="dt-field" class="readonly-field">{{ drawerDemand.techField || '-' }}</span>
            </div>
            <div class="form-item">
              <label>需求类型：</label>
              <span id="dt-type" class="readonly-field">{{ drawerDemand.type || '-' }}</span>
            </div>
            <div class="form-item">
              <label>供需状态：</label>
              <span id="dt-status" class="readonly-field" style="font-weight: bold; color: #2196f3;">{{ drawerDemand.status || '-' }}</span>
            </div>
            <div class="form-item">
              <label>项目预算：</label>
              <span id="dt-budget" class="readonly-field">{{ drawerDemand.budget || '-' }}</span>
            </div>
          </div>
        </fieldset>

        <fieldset class="form-section">
          <legend>二、需求描述</legend>
          <div class="form-item full-width" style="margin-bottom: 15px;">
            <label>需求概述：</label>
            <div id="dt-overview" class="readonly-field" style="height: auto;">{{ drawerDemand.overview || '-' }}</div>
          </div>
          <div class="form-item full-width">
            <label>期望解决的问题：</label>
            <div id="dt-issues" class="readonly-field" style="height: auto;">{{ drawerDemand.issues || '-' }}</div>
          </div>
        </fieldset>
      </div>
      <div class="drawer-footer">
        <button class="contact-btn" style="width: 260px; height: 45px; font-size: 16px; font-weight: bold;" @click="handleDrawerContact('demand')">立即对接</button>
      </div>
    </div>

    <!-- 成果发布弹窗 -->
    <el-dialog
      v-model="showPublishDialog"
      width="80%"
      :close-on-click-modal="false"
      :show-close="false"
      class="home-dialog"
    >
      <template #header>
        <div class="home-dialog-header">
          <span class="home-dialog-title">《成果采集表》</span>
          <button class="home-dialog-close" @click="showPublishDialog = false">×</button>
        </div>
      </template>
      <publish-view v-if="showPublishDialog" ref="publishFormRef" :is-dialog="true" @success="handlePublishSuccess" />
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showPublishDialog = false">取消</el-button>
          <el-button type="primary" @click="submitPublishForm">提交审核</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 需求发布弹窗 -->
    <el-dialog
      v-model="showRequireDialog"
      width="80%"
      :close-on-click-modal="false"
      :show-close="false"
      class="home-dialog"
    >
      <template #header>
        <div class="home-dialog-header">
          <span class="home-dialog-title">《需求采集表》</span>
          <button class="home-dialog-close" @click="showRequireDialog = false">×</button>
        </div>
      </template>
      <require-view v-if="showRequireDialog" ref="requireFormRef" :is-dialog="true" @success="handleRequireSuccess" />
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showRequireDialog = false">取消</el-button>
          <el-button type="primary" @click="submitRequireForm">提交审核</el-button>
        </span>
      </template>
    </el-dialog>

  </div>
</template>

<script>
import useAuth from '../composables/useAuth'
import PublishView from './PublishView.vue'
import RequireView from './RequireView.vue'
import request from '../utils/request'

export default {
  name: 'HomeView',
  components: {
    PublishView,
    RequireView
  },
  inject: ['globalOpenChat'],
  data() {
    return {
      carouselImages: [],
      baseApiUrl: window.location.origin,
      achievementList: [],
      demandList: [],
      showPublishDialog: false,
      showRequireDialog: false,
      publishFormRef: null,
      requireFormRef: null,
      pendingPublish: false,
      pendingRequire: false,
      // 详情抽屉
      showAchievementDrawer: false,
      showDemandDrawer: false,
      drawerAchievement: {},
      drawerDemand: {},
      allAchievementsDetail: [],
      allDemandsDetail: [],
      // 编辑器自定义内容（剥离自动填充后，只保留用户添加的组件）
      editorCustomHtml: '',
      pageLoading: true
    }
  },
  created() {
    // 加载编辑器自定义内容（备案号等用户添加的组件）
    this.loadEditorCustomContent()
    // 从API获取主页展示数据（动态加载，管理员可控制）
    this.fetchAchievements()
    this.fetchRequirements()
    this.fetchAchievementDetails()
    this.fetchDemandDetails()
    this.fetchCarouselImages()
    // 检查URL查询参数
    const query = this.$route.query
    if (query.showDialog === 'publish') {
      this.showPublishDialog = true
      this.$router.replace({ query: {} })
    } else if (query.showDialog === 'require') {
      this.showRequireDialog = true
      this.$router.replace({ query: {} })
    }
  },
  computed: {
    auth() {
      return useAuth()
    },
    isLoggedIn() {
      return this.auth.isLoggedIn?.value || false
    }
  },
  watch: {
    isLoggedIn(newVal) {
      if (newVal) {
        if (this.pendingPublish) {
          this.showPublishDialog = true
          this.pendingPublish = false
        }
        if (this.pendingRequire) {
          this.showRequireDialog = true
          this.pendingRequire = false
        }
      }
    }
  },
  methods: {
    // ========== 加载编辑器自定义内容（只保留用户添加的组件，去掉自动填充的轮播图/按钮/卡片） ==========
    async loadEditorCustomContent() {
      try {
        const res = await fetch('/api/editor/site/pages/home/view')
        if (!res.ok) {
          this.pageLoading = false
          return
        }
        const html = await res.text()
        // 提取 <style> 标签中的样式（用户自定义组件的样式）
        let customStyles = ''
        const styleRegex = /<style[^>]*>([\s\S]*?)<\/style>/gi
        let match
        while ((match = styleRegex.exec(html)) !== null) {
          customStyles += match[1] + '\n'
        }
        // 提取 <body> 内的内容
        const bodyMatch = html.match(/<body[^>]*>([\s\S]*?)<\/body>/i)
        if (!bodyMatch) {
          this.pageLoading = false
          return
        }
        let body = bodyMatch[1]
        // 移除 script 标签
        body = body.replace(/<script[^>]*>[\s\S]*?<\/script>/gi, '')

        // 去掉自动填充的首页内容（编辑器中自动生成的轮播图/按钮/卡片等 <section class="home-..."> 结构）
        // 只保留用户自己添加的组件（如联网备案号等）
        body = body.replace(/<section[^>]*class="[^"]*home-[^"]*"[^>]*>[\s\S]*?<\/section>/gi, '')

        // 清理多余空行
        body = body.trim()

        if (body) {
          this.editorCustomHtml = (customStyles ? `<style>${customStyles}</style>` : '') + body
        }
      } catch (e) {
        console.error('加载编辑器自定义内容失败:', e)
      }
      this.pageLoading = false
    },

    // ========== 交互功能 ==========
    goToAchievement() {
      if (!this.isLoggedIn) {
        this.auth.openLoginPrompt('/publish')
      } else if (!this.auth.requireVerified()) {
        return
      } else {
        this.showPublishDialog = true
      }
    },
    goToDemand() {
      if (!this.isLoggedIn) {
        this.auth.openLoginPrompt('/require')
      } else if (!this.auth.requireVerified()) {
        return
      } else {
        this.showRequireDialog = true
      }
    },
    submitPublishForm() {
      if (this.$refs.publishFormRef) {
        this.$refs.publishFormRef.submitForm()
      }
    },
    submitRequireForm() {
      if (this.$refs.requireFormRef) {
        this.$refs.requireFormRef.submitForm()
      }
    },
    handlePublishSuccess() {
      this.showPublishDialog = false
    },
    handleRequireSuccess() {
      this.showRequireDialog = false
    },
    goToAchievementCenter() {
      this.$router.push('/achievement')
    },
    goToDemandCenter() {
      this.$router.push('/demand')
    },
    openChatModal(type, id) {
      if (!this.isLoggedIn) {
        this.auth.openLoginPrompt(this.$route.fullPath)
        return
      }
      if (!this.auth.requireVerified()) {
        return
      }
      if (this.globalOpenChat && type && id) {
        this.globalOpenChat(type, id)
      } else {
        this.$message.info('对接功能开发中，请联系客服')
      }
    },
    async fetchAchievements() {
      try {
        const response = await request.get('/api/publish/public/achievements', { params: { limit: 3 } })
        if (response.code === 200) {
          this.achievementList = (response.data || []).map(item => ({
            id: item.id,
            code: item.achievement_code,
            title: item.achievement_name,
            transferType: this.formatFieldWithOther(
              typeof item.transfer_methods === 'string' ? item.transfer_methods.split(', ').filter(Boolean) : (item.transfer_methods || []),
              item.transfer_methods_other
            ) || '-',
            region: item.region || '-',
            maturity: item.tech_maturity || '-'
          }))
        }
      } catch (error) {
        console.error('获取成果展示数据失败:', error)
      }
    },
    async fetchRequirements() {
      try {
        const response = await request.get('/api/publish/public/requirements', { params: { limit: 3 } })
        if (response.code === 200) {
          this.demandList = (response.data || []).map(item => ({
            id: item.demand_code || item.id,
            title: item.demand_name,
            techField: this.formatFieldWithOther(item.tech_fields, item.tech_fields_other) || '-',
            region: item.region || '-',
            type: this.formatFieldWithOther(item.demand_types, item.demand_types_other) || '-',
            status: '待对接'
          }))
        }
      } catch (error) {
        console.error('获取需求展示数据失败:', error)
      }
    },
    openAchievementDrawer(achievement) {
      if (!this.isLoggedIn) {
        this.auth.openLoginPrompt(this.$route.fullPath)
        return
      }
      const detail = this.allAchievementsDetail.find(item => item.achievement_code === achievement.code)
      if (detail) {
        this.drawerAchievement = {
          title: detail.achievement_name || '-',
          code: detail.achievement_code || '-',
          owner: detail.owner || '-',
          field: this.formatFieldWithOther(detail.tech_fields, detail.tech_fields_other) || '-',
          maturity: detail.tech_maturity || '-',
          transferDisplay: this.formatFieldWithOther(detail.transfer_methods, detail.transfer_methods_other) || '-',
          region: detail.region || '-',
          summary: detail.summary || '-',
          advantage: detail.advantages || '-',
          innovation: detail.innovation_level || '-',
          indicator: detail.core_indicators || '-',
          compare: detail.advantages || '-',
          ipr: detail.intellectual_property || '-',
          collab: this.formatTransferPreference(detail.transfer_preference),
          deadline: this.formatExpectedCompleteDate(detail.transfer_preference?.expected_complete_date) || '未指定'
        }
      } else {
        this.drawerAchievement = { ...achievement }
      }
      this.showAchievementDrawer = true
    },
    closeAchievementDrawer() {
      this.showAchievementDrawer = false
    },
    openDemandDrawer(demand) {
      if (!this.isLoggedIn) {
        this.auth.openLoginPrompt(this.$route.fullPath)
        return
      }
      const detail = this.allDemandsDetail.find(item => (item.demand_code === demand.id))
      if (detail) {
        this.drawerDemand = {
          title: detail.demand_name || '-',
          id: detail.demand_code || '-',
          org: detail.company_name || '-',
          region: detail.region || '-',
          techField: this.formatFieldWithOther(detail.tech_fields, detail.tech_fields_other) || '-',
          type: this.formatFieldWithOther(detail.demand_types, detail.demand_types_other) || '-',
          status: '待对接',
          budget: detail.budget ? `${detail.budget}万元` : '未指定',
          overview: detail.overview || '-',
          issues: detail.target_problems || '-'
        }
      } else {
        this.drawerDemand = { ...demand }
      }
      this.showDemandDrawer = true
    },
    closeDemandDrawer() {
      this.showDemandDrawer = false
    },
    handleDrawerContact(type) {
      if (!this.isLoggedIn) {
        if (type === 'achievement') {
          this.closeAchievementDrawer()
        } else {
          this.closeDemandDrawer()
        }
        this.auth.openLoginPrompt(this.$route.fullPath)
        return
      }
      if (!this.auth.requireVerified()) {
        return
      }
      const id = type === 'achievement'
        ? this.drawerAchievement?.code
        : this.drawerDemand?.id
      if (type === 'achievement') {
        this.closeAchievementDrawer()
      } else {
        this.closeDemandDrawer()
      }
      if (this.globalOpenChat && id) {
        this.globalOpenChat(type, id)
      } else {
        this.$message.info('对接功能开发中，请联系客服')
      }
    },
    formatTransferPreference(preference) {
      if (!preference) return '未指定'
      const parts = []
      if (preference.preferred_method) {
        parts.push(preference.preferred_method)
      }
      if (preference.tech_transfer?.enabled && preference.tech_transfer.expected_fee) {
        parts.push(`预期费用：${preference.tech_transfer.expected_fee}万元`)
      } else if (preference.tech_license?.enabled && preference.tech_license.expected_fee) {
        parts.push(`预期费用：${preference.tech_license.expected_fee}万元`)
      } else if (preference.tech_investment?.enabled && preference.tech_investment.valuation) {
        parts.push(`估值：${preference.tech_investment.valuation}万元`)
      }
      if (preference.other) {
        parts.push(`其他：${preference.other}`)
      }
      return parts.length > 0 ? parts.join('，') : '未指定'
    },
    formatExpectedCompleteDate(dateObj) {
      if (!dateObj || !dateObj.year) return null
      if (dateObj.month) {
        return `${dateObj.year}年${dateObj.month}月`
      }
      return `${dateObj.year}年`
    },
    resolveImageUrl(url) {
      if (!url) return ''
      if (url.startsWith('http://') || url.startsWith('https://')) return url
      return (this.baseApiUrl || window.location.origin) + url
    },
    async fetchCarouselImages() {
      try {
        const res = await fetch('/api/editor/config/all')
        const data = await res.json()
        if (data.code === 200 && data.data) {
          if (Array.isArray(data.data.carousel_images) && data.data.carousel_images.length > 0) {
            this.carouselImages = data.data.carousel_images
          } else {
            this.carouselImages = [{ url: 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2072&auto=format&fit=crop', title: '科技创新 · 引领未来' }]
          }
        } else {
          this.carouselImages = [{ url: 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2072&auto=format&fit=crop', title: '科技创新 · 引领未来' }]
        }
      } catch (e) {
        console.error('获取轮播图配置失败:', e)
        this.carouselImages = [{ url: 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2072&auto=format&fit=crop', title: '科技创新 · 引领未来' }]
      }
    },
    formatFieldWithOther(fields, other) {
      const arr = Array.isArray(fields) ? fields.filter(f => f !== '其他') : []
      let result = arr.join('、')
      if (other && other.trim()) {
        result += (result ? '、' : '') + `其他：${other}`
      }
      return result || '其他'
    },
    async fetchAchievementDetails() {
      try {
        const response = await request.get('/api/publish/public/achievements/center', { params: { limit: 100 } })
        if (response.code === 200 && response.data) {
          this.allAchievementsDetail = response.data
        }
      } catch (error) {
        console.error('获取成果详情数据失败:', error)
      }
    },
    async fetchDemandDetails() {
      try {
        const response = await request.get('/api/publish/public/requirements/center', { params: { limit: 100 } })
        if (response.code === 200 && response.data) {
          this.allDemandsDetail = response.data
        }
      } catch (error) {
        console.error('获取需求详情数据失败:', error)
      }
    }
  }
}
</script>

<style scoped>
/* ================= 加载状态 ================= */
.page-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 80px 20px;
  color: #666;
  font-size: 15px;
}

.loader-spinner {
  width: 28px;
  height: 28px;
  border: 3px solid #e0e0e0;
  border-top-color: #4a90d9;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ================= 主页样式 ================= */
.hero-carousel {
  max-width: 1200px;
  margin: 20px auto;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.carousel-image {
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
  position: relative;
}

.carousel-caption {
  position: absolute;
  bottom: 40px;
  left: 50%;
  transform: translateX(-50%);
  background-color: rgba(0, 0, 0, 0.6);
  color: var(--white);
  padding: 12px 24px;
  border-radius: 30px;
  font-size: 20px;
  font-weight: bold;
  white-space: nowrap;
}

.action-buttons {
  max-width: 1200px;
  margin: 30px auto;
  display: flex;
  justify-content: center;
  gap: 40px;
}

.action-btn {
  padding: 15px 50px;
  font-size: 18px;
  background-color: var(--white);
  border: 1px solid var(--border-color);
  border-radius: 30px;
  cursor: pointer;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
  transition: all 0.3s;
  font-weight: bold;
  color: var(--text-main);
}

.action-btn:hover {
  background-color: var(--primary-color);
  color: var(--white);
  border-color: var(--primary-color);
  transform: translateY(-2px);
}

.display-modules {
  max-width: 1200px;
  margin: 0 auto 40px;
}

.two-column-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
  align-items: stretch;
}

.column {
  background-color: var(--white);
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  min-height: 360px;
}

.column-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid var(--border-color);
}

.column-title {
  font-size: 20px;
  color: var(--text-main);
  margin: 0;
}

.more-btn {
  padding: 6px 16px;
  background-color: transparent;
  border: 1px solid var(--primary-color);
  color: var(--primary-color);
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.more-btn:hover {
  background-color: var(--primary-color);
  color: white;
}

.cards-list {
  display: grid;
  grid-template-rows: 1fr 1fr 1fr;
  gap: 15px;
  flex: 1;
}

.result-card, .demand-item {
  cursor: pointer;
  background-color: white;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  display: flex;
  justify-content: space-between;
  min-height: 180px;
}

.result-card:hover, .demand-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.result-content, .demand-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.result-content h3, .demand-content h3 {
  font-size: 16px;
  margin-bottom: 16px;
  color: #333;
  line-height: 1.5;
  font-weight: 600;
}

.result-meta, .demand-meta {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px 20px;
  font-size: 13px;
  color: #666;
  line-height: 1.5;
}

.meta-item {
  position: relative;
  padding: 2px 0;
}

.result-actions, .demand-actions {
  display: flex;
  align-items: center;
  margin-left: 20px;
}

.contact-btn {
  padding: 10px 20px;
  background-color: #2196f3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.contact-btn:hover {
  background-color: #1976d2;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(33, 150, 243, 0.3);
}

/* 编辑器自定义内容区域（如备案号等） */
.editor-custom-area {
  width: 100%;
}

@media (max-width: 1024px) {
  .hero-carousel {
    margin: 16px auto;
    border-radius: 8px;
  }
  .carousel-caption {
    font-size: 16px;
    padding: 10px 20px;
    bottom: 30px;
  }
  .action-buttons {
    gap: 24px;
    margin: 24px auto;
    padding: 0 16px;
  }
  .action-btn {
    padding: 12px 36px;
    font-size: 16px;
  }
  .display-modules {
    padding: 0 16px;
  }
  .result-meta, .demand-meta {
    grid-template-columns: repeat(2, 1fr);
    gap: 8px 16px;
  }
}

@media (max-width: 768px) {
  .hero-carousel {
    height: 220px !important;
    margin: 12px auto;
    border-radius: 0;
  }
  .carousel-caption {
    font-size: 14px;
    padding: 8px 16px;
    bottom: 20px;
    white-space: normal;
    max-width: 90%;
    text-align: center;
  }
  .two-column-layout {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  .action-buttons {
    flex-direction: column;
    gap: 12px;
    align-items: center;
    margin: 20px auto;
    padding: 0 16px;
  }
  .action-btn {
    width: 100%;
    max-width: 300px;
    padding: 12px 24px;
    font-size: 15px;
  }
  .column {
    padding: 16px;
  }
  .column-title {
    font-size: 17px;
  }
  .result-card, .demand-item {
    flex-direction: column;
    min-height: auto;
    padding: 16px;
    gap: 12px;
  }
  .result-meta, .demand-meta {
    grid-template-columns: 1fr;
    gap: 6px;
  }
  .result-content h3, .demand-content h3 {
    font-size: 15px;
    margin-bottom: 10px;
  }
  .result-actions, .demand-actions {
    margin-left: 0;
    justify-content: flex-end;
  }
  .contact-btn {
    padding: 8px 16px;
    font-size: 13px;
    width: 100%;
  }
  .display-modules {
    padding: 0 12px;
  }

  /* 抽屉手机端全屏 */
  .drawer {
    width: 100vw !important;
    left: -100vw !important;
  }
  .drawer-header {
    padding: 16px 20px;
  }
  .drawer-title {
    font-size: 17px;
  }
  .drawer-body {
    padding: 16px;
  }
  .drawer-footer {
    padding: 16px 20px;
  }
  .form-section {
    padding: 14px;
  }
  .form-grid {
    grid-template-columns: 1fr !important;
    gap: 12px;
  }
  .form-section legend {
    font-size: 14px;
  }
  .home-dialog :deep(.el-dialog) {
    width: 92% !important;
    max-width: 92% !important;
  }
}

@media (max-width: 480px) {
  .hero-carousel {
    height: 180px !important;
  }
  .carousel-caption {
    font-size: 12px;
    padding: 6px 12px;
  }
}

/* ================= 发布弹窗 ================= */
.home-dialog {
  border-radius: 12px;
  overflow: hidden;
}
.home-dialog :deep(.el-dialog__body) {
  padding: 20px;
  max-height: 70vh;
  overflow-y: auto;
}

.home-dialog-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px 0;
}
.home-dialog-title {
  font-size: 18px;
  font-weight: 700;
  color: #303133;
  letter-spacing: 0.5px;
}
.home-dialog-close {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: #f5f5f5;
  border-radius: 50%;
  font-size: 18px;
  color: #999;
  cursor: pointer;
  transition: all 0.2s ease;
  line-height: 1;
  padding: 0;
}
.home-dialog-close:hover {
  background: #ff4d4f;
  color: #fff;
  transform: rotate(90deg);
}

/* ================= 详情抽屉样式 ================= */
.drawer-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 10001;
  opacity: 0;
  pointer-events: none;
  transition: 0.3s;
}
.drawer-overlay.active {
  opacity: 1;
  pointer-events: auto;
}
.drawer {
  position: fixed;
  left: -850px;
  top: 0;
  width: 800px;
  max-width: 100vw;
  height: 100vh;
  background: white;
  z-index: 10002;
  transition: 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: 4px 0 24px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
}
.drawer.active {
  left: 0;
}
.drawer-header {
  padding: 24px 30px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #f8fbff;
  flex-shrink: 0;
}
.drawer-title {
  font-size: 20px;
  color: #2196f3;
  font-weight: bold;
}
.drawer-close {
  font-size: 28px;
  cursor: pointer;
  color: #aaa;
  font-weight: bold;
  line-height: 1;
}
.drawer-close:hover {
  color: #333;
}
.drawer-body {
  padding: 30px;
  overflow-y: auto;
  flex: 1;
}
.drawer-footer {
  padding: 20px 30px;
  border-top: 1px solid #eee;
  background: #fff;
  display: flex;
  justify-content: center;
  flex-shrink: 0;
}
.form-section {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 25px;
  background: #fff;
}
.form-section legend {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  padding: 0 10px;
  width: auto;
  margin-left: 10px;
}
.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-top: 15px;
}
.form-item.full-width {
  grid-column: 1 / -1;
}
.form-item label {
  font-size: 14px;
  font-weight: 600;
  color: #555;
  display: block;
  margin-bottom: 8px;
}
.readonly-field {
  font-size: 14px;
  color: #333;
  padding: 10px 12px;
  background-color: #f9f9f9;
  border: 1px solid #ddd;
  border-radius: 4px;
  min-height: 40px;
  display: block;
  word-break: break-all;
  line-height: 1.5;
}
</style>
