<template>
  <div class="expert-container">
    <main>
      <section class="search-section" v-show="view === 'list'" :style="{ backgroundImage: `url(${require('@/assets/find.png')})` }">
        <div class="search-container">
          <input type="text" class="search-input" placeholder="输入专家姓名、单位或专业词汇检索..."
            v-model="searchKeyword" @keyup.enter="executeSearch">
          <button class="search-btn" @click="executeSearch">搜索</button>
        </div>
      </section>

      <div class="container">
        <div id="list-view" v-show="view === 'list'">

          <div class="filter-card">
            <div class="filter-card-header">
              <div class="filter-card-title">
                <span class="filter-dot"></span>筛选条件
                <span class="filter-badge" v-if="activeFilterCount > 0">{{ activeFilterCount }}</span>
              </div>
              <button class="filter-reset" @click="resetAllFilters">重置筛选</button>
            </div>
            <div class="filter-row">
              <div class="filter-label">研究方向</div>
              <div class="filter-tags">
                <span class="filter-chip" :class="{ active: filterDomain.includes('全部') || filterDomain.length === 0 }" @click="handleFilterClick('全部')">全部</span>
                <span class="filter-chip" :class="{ active: filterDomain.includes('新一代信息技术') }" @click="handleFilterClick('新一代信息技术')">新一代信息技术</span>
                <span class="filter-chip" :class="{ active: filterDomain.includes('人工智能') }" @click="handleFilterClick('人工智能')">人工智能</span>
                <span class="filter-chip" :class="{ active: filterDomain.includes('大数据') }" @click="handleFilterClick('大数据')">大数据</span>
                <span class="filter-chip" :class="{ active: filterDomain.includes('区块链') }" @click="handleFilterClick('区块链')">区块链</span>
                <span class="filter-chip" :class="{ active: filterDomain.includes('云计算') }" @click="handleFilterClick('云计算')">云计算</span>
                <span class="filter-chip" :class="{ active: filterDomain.includes('高端装备制造') }" @click="handleFilterClick('高端装备制造')">高端装备制造</span>
                <span class="filter-chip" :class="{ active: filterDomain.includes('机器人') }" @click="handleFilterClick('机器人')">机器人</span>
                <span class="filter-chip" :class="{ active: filterDomain.includes('航空航天') }" @click="handleFilterClick('航空航天')">航空航天</span>
                <span class="filter-chip" :class="{ active: filterDomain.includes('海洋工程') }" @click="handleFilterClick('海洋工程')">海洋工程</span>
                <span class="filter-chip" :class="{ active: filterDomain.includes('新材料') }" @click="handleFilterClick('新材料')">新材料</span>
                <span class="filter-chip" :class="{ active: filterDomain.includes('新能源') }" @click="handleFilterClick('新能源')">新能源</span>
                <span class="filter-chip" :class="{ active: filterDomain.includes('节能环保') }" @click="handleFilterClick('节能环保')">节能环保</span>
                <span class="filter-chip" :class="{ active: filterDomain.includes('生物医药') }" @click="handleFilterClick('生物医药')">生物医药</span>
                <span class="filter-chip" :class="{ active: filterDomain.includes('医疗器械') }" @click="handleFilterClick('医疗器械')">医疗器械</span>
                <span class="filter-chip" :class="{ active: filterDomain.includes('现代农业') }" @click="handleFilterClick('现代农业')">现代农业</span>
                <span class="filter-chip" :class="{ active: filterDomain.includes('其他') }" @click="handleFilterClick('其他')">其他</span>
              </div>
            </div>
            <div class="active-summary" v-if="activeFilterChips.length > 0">
              <span class="active-chip" v-for="chip in activeFilterChips" :key="chip.option">
                {{ chip.option }}
                <span class="active-chip-rm" @click.stop="removeFilter(chip.option)">&times;</span>
              </span>
              <span class="active-clear" @click="resetAllFilters">清除全部</span>
            </div>
          </div>

          <div v-if="loading" class="empty-state">
            <span style="font-size: 18px; font-weight: 700; color: var(--text-muted);">加载中...</span>
          </div>

          <div class="grid" id="expert-grid" v-else>
            <div v-if="currentData.length === 0" class="empty-state">
              <svg width="56" height="56" viewBox="0 0 24 24" fill="none" stroke="#cbd5e1" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom:16px;">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                <circle cx="8.5" cy="8.5" r="1.5"></circle>
                <polyline points="21 15 16 10 5 21"></polyline>
              </svg>
              <template v-if="experts.length === 0">
                <span style="font-size: 18px; font-weight: 700; color: var(--text-dark); margin-bottom: 8px;">暂无专家数据</span>
                <span style="color: var(--text-muted); margin-bottom: 24px;">请等待管理员录入专家信息</span>
              </template>
              <template v-else>
                <span style="font-size: 18px; font-weight: 700; color: var(--text-dark); margin-bottom: 8px;">专家库中暂无匹配档案</span>
                <span style="color: var(--text-muted); margin-bottom: 24px;">请尝试放宽检索关键词或更换研究领域</span>
                <button class="reset-btn" style="border-radius: 8px; border-left: 1px solid var(--border-subtle); padding: 8px 24px; font-weight: 600;" @click="resetSearch">返回全库</button>
              </template>
            </div>

            <div class="expert-card" v-for="item in paginatedData" :key="item.id" @click="openDetail(item)">
              <div class="expert-avatar-box">
                <img :src="item.image" :alt="item.name" loading="lazy">
              </div>
              <div class="expert-info">
                <div class="expert-header">
                  <div class="expert-name">{{ item.name }}</div>
                  <div class="expert-title">{{ item.title }}</div>
                </div>
                <div class="expert-unit">{{ item.unit }}</div>
                <div class="expert-domains">
                  <span class="domain-tag" v-for="domain in item.domains" :key="domain">{{ domain }}</span>
                </div>

                <div class="expert-stats">
                  <div class="stat-badge">
                    <span>{{ item.exp }}</span> 年经验
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="pagination-wrapper" v-if="currentData.length > 0">
            <div class="pagination-complex" id="pagination-container">
              <div class="page-total">共 {{ currentData.length }} 位专家档案</div>
              <div class="page-controls">
                <button class="page-btn" @click="changePage('prev')" :disabled="currentPage === 1">&lt;</button>

                <template v-for="p in paginationPages" :key="p">
                  <span v-if="p === '...'" class="page-btn dots">...</span>
                  <button v-else class="page-btn" :class="{ active: p === currentPage }" @click="changePage(p)">{{ p }}</button>
                </template>

                <button class="page-btn" @click="changePage('next')" :disabled="currentPage === totalPages">&gt;</button>
              </div>

              <div class="page-sizer" style="margin-left: 16px;">
                <select class="page-select" @change="changePageSize($event.target.value)" v-model="pageSize">
                  <option value="6">6 条/页</option>
                  <option value="12">12 条/页</option>
                </select>
              </div>
              <div class="page-jumper" style="margin-left: 16px;">
                跳至 <input type="number" class="jump-input" :min="1" :max="totalPages"
                  @keydown.enter="jumpToPage($event.target.value)" v-model="jumpPage"> 页
              </div>
            </div>
          </div>
        </div>

        <div id="detail-view" v-show="view === 'detail'">

          <div class="back-nav">
            <div class="back-btn" @click="closeDetail">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <line x1="19" y1="12" x2="5" y2="12"></line>
                <polyline points="12 19 5 12 12 5"></polyline>
              </svg>
              返回专家库
            </div>
          </div>

          <div class="dossier-layout">

            <div class="dossier-sidebar">
              <div class="profile-card">
                <div class="profile-card-header"></div>
                <div class="profile-card-body">
                  <img :src="currentDetail.image" :alt="currentDetail.name" class="avatar-lg">
                  <div class="name-lg">{{ currentDetail.name }}</div>
                  <div class="title-lg">{{ currentDetail.title }}</div>
                  <div class="unit-lg">{{ currentDetail.unit }}</div>

                  <div id="dt-domains" style="margin-top: 16px; display: flex; flex-wrap: wrap; gap: 6px; justify-content: center;">
                    <span class="domain-tag" v-for="domain in currentDetail.domains" :key="domain">{{ domain }}</span>
                  </div>
                </div>
              </div>

              <div class="info-card">
                <div class="info-row"><span class="info-label">性别</span><span class="info-val">{{ currentDetail.gender }}</span></div>
                <div class="info-row"><span class="info-label">最高学历</span><span class="info-val">{{ currentDetail.edu }}</span></div>
                <div class="info-row"><span class="info-label">院校及专业</span><span class="info-val" style="text-align: right; max-width: 140px;">{{ currentDetail.school }}</span></div>
                <div class="info-row"><span class="info-label">从业经验</span><span class="info-val">{{ currentDetail.exp }} 年</span></div>
              </div>

              <div class="privacy-box">
                <strong>🔒 数据安全说明</strong><br>
                平台严格执行脱敏政策。专家的详尽联系方式、证件影印件及原件清单已被系统隐藏，仅授权管理员后台可见。
              </div>
            </div>

            <div class="dossier-main">

              <div class="section-box" v-if="currentDetail.personal_profile">
                <h2 class="section-header">个人简介</h2>
                <p class="bio-text">{{ currentDetail.personal_profile }}</p>
              </div>

              <div class="section-box">
                <h2 class="section-header">评估资质与核心能力</h2>
                <div class="qual-grid">
                  <div class="qual-item">
                    <h4>技术职称</h4>
                    <p>{{ currentDetail.level }}</p>
                  </div>
                  <div class="qual-item">
                    <h4>社会荣誉</h4>
                    <p>{{ currentDetail.honor || '无' }}</p>
                  </div>
                </div>
              </div>

              <div class="section-box">
                <h2 class="section-header">代表性科研与转化成果</h2>
                <div class="achievement-list">
                  <div class="achieve-item">
                    <h4>核心专利情况</h4>
                    <p>{{ currentDetail.patents || '暂无记录' }}</p>
                  </div>
                  <div class="achieve-item">
                    <h4>主导/参与科研项目</h4>
                    <p>{{ currentDetail.projects || '暂无记录' }}</p>
                  </div>
                  <div class="achieve-item">
                    <h4>重要获奖情况</h4>
                    <p>{{ currentDetail.awards || '暂无记录' }}</p>
                  </div>
                </div>
              </div>

            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import request from '../utils/request'
import useAuth from '../composables/useAuth'

const DEFAULT_AVATAR = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(
  '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="500" viewBox="0 0 400 500">' +
  '<defs>' +
  '<linearGradient id="ag" x1="0%" y1="0%" x2="100%" y2="100%">' +
  '<stop offset="0%" style="stop-color:#e0e7ff;stop-opacity:1"/>' +
  '<stop offset="100%" style="stop-color:#c7d2fe;stop-opacity:1"/>' +
  '</linearGradient>' +
  '</defs>' +
  '<rect fill="url(#ag)" width="400" height="500" rx="40"/>' +
  '<circle cx="200" cy="165" r="72" fill="#a5b4fc" opacity="0.5"/>' +
  '<circle cx="200" cy="165" r="58" fill="#818cf8" opacity="0.7"/>' +
  '<circle cx="200" cy="155" r="42" fill="#6366f1"/>' +
  '<ellipse cx="200" cy="420" rx="130" ry="105" fill="#818cf8" opacity="0.6"/>' +
  '<ellipse cx="200" cy="410" rx="105" ry="85" fill="#6366f1" opacity="0.8"/>' +
  '</svg>'
)

export default {
  name: 'ExpertView',
  data() {
    const auth = useAuth()
    return {
      auth,
      loading: false,
      experts: [],
      total: 0,
      filterDomain: ['全部'],
      searchKeyword: '',
      currentData: [],
      currentPage: 1,
      pageSize: 6,
      jumpPage: 1,
      view: 'list',
      currentDetail: {
        id: 0,
        name: '',
        gender: '',
        title: '',
        unit: '',
        edu: '',
        school: '',
        level: '',
        personal_profile: '',
        honor: '',
        exp: '',
        domains: [],
        patents: '',
        projects: '',
        awards: '',
        image: ''
      }
    }
  },
  computed: {
    paginatedData() {
      const start = (this.currentPage - 1) * this.pageSize
      const end = start + this.pageSize
      return this.currentData.slice(start, end)
    },
    totalPages() {
      return Math.ceil(this.currentData.length / this.pageSize) || 1
    },
    paginationPages() {
      const totalPages = this.totalPages
      const currentPage = this.currentPage
      let pages = []

      if (totalPages <= 7) {
        for (let i = 1; i <= totalPages; i++) pages.push(i)
      } else {
        if (currentPage <= 4) {
          pages = [1, 2, 3, 4, 5, '...', totalPages]
        } else if (currentPage >= totalPages - 3) {
          pages = [1, '...', totalPages - 4, totalPages - 3, totalPages - 2, totalPages - 1, totalPages]
        } else {
          pages = [1, '...', currentPage - 1, currentPage, currentPage + 1, '...', totalPages]
        }
      }
      return pages
    },
    activeFilterCount() {
      if (this.filterDomain.includes('全部')) return 0
      return this.filterDomain.length
    },
    activeFilterChips() {
      if (this.filterDomain.includes('全部')) return []
      return this.filterDomain.map(opt => ({ option: opt }))
    }
  },
  methods: {
    getExpertImage(expert) {
      if (expert.attachments) {
        const photos = expert.attachments['近期生活照或职业照一张']
        if (photos && photos.length > 0 && photos[0].file_url) {
          return window.location.origin + photos[0].file_url
        }
      }
      return DEFAULT_AVATAR
    },
    mapExpert(item) {
      return {
        id: item.id,
        name: item.name || '',
        gender: item.gender || '',
        title: item.position_title || '',
        unit: item.work_unit || '',
        edu: item.highest_education || '',
        school: item.school_major || '',
        level: item.technical_title || '',
        personal_profile: item.personal_profile || '',
        honor: item.honors || '',
        exp: item.work_years != null ? String(item.work_years) : '0',
        domains: item.professional_fields || [],
        patents: item.patents || '',
        projects: item.research_projects || '',
        awards: item.awards || '',
        image: this.getExpertImage(item),
        attachments: item.attachments
      }
    },
    async fetchExperts() {
      this.loading = true
      try {
        const params = { page: 1, page_size: 999 }
        if (this.searchKeyword.trim()) {
          params.keyword = this.searchKeyword.trim()
        }
        const res = await request.get('/api/publish/public/experts', { params })
        if (res.code === 200 && res.data) {
          this.experts = res.data.map(item => this.mapExpert(item))
          this.total = res.total || res.data.length
        } else {
          this.experts = []
          this.total = 0
        }
      } catch (err) {
        console.error('获取专家数据失败:', err)
        this.experts = []
        this.total = 0
      } finally {
        this.loading = false
        this.applyFilters()
      }
    },
    applyFilters() {
      let filteredData = this.experts

      if (!this.filterDomain.includes('全部')) {
        filteredData = filteredData.filter(item =>
          item.domains.some(d => this.filterDomain.includes(d))
        )
      }

      if (this.searchKeyword.trim() !== '') {
        const keyword = this.searchKeyword.trim().toLowerCase()
        filteredData = filteredData.filter(item =>
          item.name.toLowerCase().includes(keyword) ||
          item.unit.toLowerCase().includes(keyword) ||
          item.title.toLowerCase().includes(keyword) ||
          item.domains.some(d => d.toLowerCase().includes(keyword))
        )
      }

      this.currentData = filteredData
      let totalPages = Math.ceil(this.currentData.length / this.pageSize) || 1
      if (this.currentPage > totalPages) this.currentPage = totalPages
      this.jumpPage = this.currentPage
    },
    executeSearch() {
      this.currentPage = 1
      this.fetchExperts()
    },
    resetSearch() {
      this.searchKeyword = ''
      this.resetAllFilters()
    },
    handleFilterClick(option) {
      const state = this.filterDomain

      if (option === '全部') {
        this.filterDomain = ['全部']
      } else {
        const allIndex = state.indexOf('全部')
        if (allIndex > -1) {
          state.splice(allIndex, 1)
        }

        const optionIndex = state.indexOf(option)
        if (optionIndex > -1) {
          state.splice(optionIndex, 1)
          if (state.length === 0) {
            this.filterDomain = ['全部']
          }
        } else {
          state.push(option)
        }
      }

      this.currentPage = 1
      this.applyFilters()
    },
    removeFilter(option) {
      const idx = this.filterDomain.indexOf(option)
      if (idx >= 0) this.filterDomain.splice(idx, 1)
      if (this.filterDomain.length === 0) this.filterDomain = ['全部']
      this.currentPage = 1
      this.applyFilters()
    },
    resetAllFilters() {
      this.filterDomain = ['全部']
      this.currentPage = 1
      this.applyFilters()
    },
    changePage(action) {
      if (action === 'prev' && this.currentPage > 1) {
        this.currentPage--
      } else if (action === 'next' && this.currentPage < this.totalPages) {
        this.currentPage++
      } else if (typeof action === 'number') {
        this.currentPage = action
      }
      this.jumpPage = this.currentPage
      window.scrollTo({ top: 0, behavior: 'smooth' })
    },
    changePageSize(size) {
      this.pageSize = parseInt(size)
      this.currentPage = 1
      this.applyFilters()
    },
    jumpToPage(val) {
      let page = parseInt(val)
      if(!isNaN(page) && page >= 1 && page <= this.totalPages) {
        this.currentPage = page
        this.jumpPage = page
        window.scrollTo({ top: 0, behavior: 'smooth' })
      }
    },
    openDetail(item) {
      if (!this.auth.state.token) {
        this.auth.openLoginPrompt(this.$route.fullPath)
        return
      }
      this.currentDetail = { ...item }
      this.view = 'detail'
      window.scrollTo({ top: 0, behavior: 'smooth' })
    },
    closeDetail() {
      this.view = 'list'
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }
  },
  mounted() {
    this.fetchExperts()
  }
}
</script>

<style scoped>
.expert-container {
  /* 局部变量覆盖，与项目整体风格保持一致 */
  --primary-color: #1890ff;
  --primary-dark: #096dd9;
  --primary-hover: var(--primary-dark, #096dd9);
  --primary-light: rgba(24, 144, 255, 0.08);
  --accent: #1890ff;
  --bg-color: #f0f2f5;
  --bg-main: var(--bg-color, #f0f2f5);
  --bg-card: #ffffff;
  --text-main: rgba(0, 0, 0, 0.85);
  --text-dark: var(--text-main, rgba(0, 0, 0, 0.85));
  --text-secondary: rgba(0, 0, 0, 0.65);
  --text-regular: var(--text-secondary, rgba(0, 0, 0, 0.65));
  --text-muted: rgba(0, 0, 0, 0.45);
  --border-color: #f0f0f0;
  --border-subtle: var(--border-color, #f0f0f0);
  --white: #ffffff;
  --radius-md: 8px;
  --radius-lg: 12px;
  --shadow-float: 0 4px 12px rgba(0, 0, 0, 0.05);
  --shadow-hover: 0 8px 24px rgba(0, 0, 0, 0.08);
  --transition: all 0.3s cubic-bezier(0.25, 0.8, 0.2, 1);
}

.expert-container * {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', sans-serif;
}

.expert-container a { text-decoration: none; color: inherit; }
.expert-container ul { list-style: none; }

/* --- 主内容区 --- */
.expert-container main {
  min-height: calc(100vh - 70px);
  padding-bottom: 80px;
  background-color: var(--bg-main);
  color: var(--text-dark);
  line-height: 1.6;
}

.expert-container .container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px 0;
}

/* ================= 搜索区域（与成果中心一致） ================= */
.search-section {
  background-size: cover;
  background-position: center;
  padding: 55px 20px 65px;
  text-align: center;
  color: white;
  max-width: 1200px;
  margin: 20px auto 16px;
  border-radius: 16px;
  position: relative;
  overflow: hidden;
}
.search-section::before {
  content: '';
  position: absolute;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.3);
  z-index: 0;
}
.search-container {
  position: relative;
  z-index: 1;
  max-width: 720px;
  margin: 0 auto;
  display: flex;
}
.search-input {
  flex: 1;
  padding: 12px 15px;
  font-size: 16px;
  border: none;
  border-radius: 4px 0 0 4px;
  outline: none;
}
.search-btn {
  padding: 12px 20px;
  background-color: #2196f3;
  color: white;
  border: none;
  border-radius: 0 4px 4px 0;
  cursor: pointer;
  transition: background 0.3s;
}
.search-btn:hover {
  background: #0076e4;
}

/* ================= 筛选区域（与成果中心一致） ================= */
.filter-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px 24px 3px;
  margin-bottom: 20px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.filter-card-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 16px;
}
.filter-card-title {
  font-size: 15px; font-weight: 600; color: #1a1a1a;
  display: flex; align-items: center; gap: 8px;
}
.filter-dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: #1890ff; display: inline-block;
}
.filter-reset {
  font-size: 13px; color: #999; background: none; border: 1px solid #e0e0e0;
  padding: 5px 14px; border-radius: 16px; cursor: pointer;
  transition: all 0.2s;
}
.filter-reset:hover { color: #ff4d4f; border-color: #ff4d4f; }
.filter-badge {
  font-size: 12px; color: #1890ff; background: #e6f7ff;
  padding: 2px 10px; border-radius: 10px; font-weight: 500;
}
.filter-row {
  display: flex; align-items: flex-start; gap: 12px;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px dashed #f0f0f0;
}
.filter-row:last-of-type { border-bottom: none; }
.filter-card .filter-label {
  width: 90px; flex-shrink: 0;
  font-size: 13px; font-weight: 600; color: #666;
  padding-top: 5px;
}
.filter-card .filter-tags {
  flex: 1; display: flex; flex-wrap: wrap; gap: 8px;
}
.filter-chip {
  padding: 5px 15px;
  border: 1px solid #e8e8e8;
  border-radius: 20px;
  font-size: 13px; color: #555;
  cursor: pointer; user-select: none;
  transition: all 0.2s;
  background: #fafafa;
}
.filter-chip:hover {
  border-color: #91d5ff;
  background: #f0f9ff;
  color: #1890ff;
}
.filter-chip.active {
  background: #1890ff;
  color: #fff;
  border-color: #1890ff;
  box-shadow: 0 2px 8px rgba(24,144,255,0.3);
}
.active-summary {
  display: flex; align-items: center; flex-wrap: wrap; gap: 8px;
  padding: 12px 0 16px;
}
.active-chip {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 4px 12px;
  background: #e6f7ff; color: #1890ff;
  border-radius: 20px; font-size: 12px; font-weight: 500;
  animation: chipIn 0.25s ease;
}
.active-chip-rm {
  margin-left: 2px; cursor: pointer;
  width: 16px; height: 16px; border-radius: 50%;
  display: inline-flex; align-items: center; justify-content: center;
  font-size: 12px; line-height: 1;
  transition: all 0.15s;
}
.active-chip-rm:hover { background: #ff4d4f; color: #fff; }
.active-clear {
  font-size: 12px; color: #999; cursor: pointer;
}
.active-clear:hover { color: #ff4d4f; }
@keyframes chipIn {
  from { opacity: 0; transform: scale(0.8); }
  to   { opacity: 1; transform: scale(1); }
}

/* --- 专家名片网格 --- */
#list-view {
  animation: fadeIn 0.6s var(--transition);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(15px); }
  to { opacity: 1; transform: translateY(0); }
}

.grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}

.expert-card {
  background: var(--bg-card);
  border-radius: var(--radius-md);
  padding: 28px;
  display: flex;
  gap: 24px;
  cursor: pointer;
  transition: var(--transition);
  border: 1px solid var(--border-subtle);
  box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}

.expert-card:hover {
  border-color: var(--primary-light);
  box-shadow: var(--shadow-hover);
  transform: translateY(-4px);
}

.expert-avatar-box {
  width: 100px;
  height: 130px;
  flex-shrink: 0;
  border-radius: 8px;
  overflow: hidden;
  position: relative;
}

.expert-avatar-box img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: grayscale(10%);
  transition: var(--transition);
}

.expert-card:hover .expert-avatar-box img {
  filter: grayscale(0%);
  transform: scale(1.05);
}

.expert-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.expert-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 6px;
}

.expert-name {
  font-size: 20px;
  font-weight: 800;
  color: var(--text-dark);
  letter-spacing: 0.5px;
}

.expert-title {
  font-size: 13px;
  color: var(--primary-color);
  font-weight: 600;
}

.expert-unit {
  font-size: 14px;
  color: var(--text-regular);
  margin-bottom: 12px;
  font-weight: 500;
}

.expert-domains {
  display: flex;
  gap: 8px;
  margin-bottom: auto;
  flex-wrap: wrap;
}

.domain-tag {
  font-size: 12px;
  color: var(--text-regular);
  background: var(--bg-main);
  padding: 4px 10px;
  border-radius: 4px;
  border: 1px solid var(--border-subtle);
  font-weight: 500;
}

/* 数据化徽章排版 */
.expert-stats {
  margin-top: 20px;
  display: flex;
  gap: 12px;
}

.stat-badge {
  background: var(--primary-light);
  color: var(--primary-color);
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.stat-badge span {
  font-size: 16px;
  font-weight: 800;
}

/* --- 完美还原的复杂分页 --- */
.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 50px;
}

.pagination-complex {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  color: var(--text-regular);
}

.page-total {
  color: var(--text-muted);
  margin-right: 12px;
  font-weight: 500;
}

.page-controls {
  display: flex;
  align-items: center;
  gap: 4px;
}

.page-btn {
  min-width: 32px;
  height: 32px;
  padding: 0 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: 6px;
  color: var(--text-regular);
  cursor: pointer;
  transition: var(--transition);
  user-select: none;
  font-weight: 500;
}

.page-btn:hover:not(:disabled):not(.dots) {
  color: var(--primary-color);
  border-color: var(--primary-color);
  background: var(--primary-light);
}

.page-btn.active {
  background: var(--primary-color);
  color: var(--bg-card);
  border-color: var(--primary-color);
  pointer-events: none;
  font-weight: bold;
}

.page-btn:disabled {
  background: var(--bg-main);
  color: rgba(0, 0, 0, 0.25);
  cursor: not-allowed;
  border-color: var(--border-subtle);
}

.page-btn.dots {
  border: none;
  background: transparent;
  cursor: default;
  padding: 0;
  min-width: 24px;
}

.page-sizer {
  display: flex;
  align-items: center;
}

.page-select {
  height: 32px;
  padding: 0 10px;
  border: 1px solid var(--border-subtle);
  border-radius: 6px;
  outline: none;
  font-size: 13px;
  color: var(--text-dark);
  cursor: pointer;
  background: var(--bg-card);
  transition: var(--transition);
}

.page-select:focus {
  border-color: var(--primary-color);
}

.page-jumper {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--text-muted);
}

.jump-input {
  width: 44px;
  height: 32px;
  border: 1px solid var(--border-subtle);
  border-radius: 6px;
  text-align: center;
  outline: none;
  font-size: 14px;
  font-weight: 600;
  transition: var(--transition);
  color: var(--text-dark);
}

.jump-input:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px var(--primary-light);
}

/* ==========================================================
   专家详情页 (非对称 Dossier 布局)
   ========================================================== */
#detail-view {
  animation: fadeUp 0.4s;
}

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.back-nav {
  margin-bottom: 24px;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  color: var(--text-regular);
  font-size: 14px;
  font-weight: 600;
  transition: var(--transition);
  padding: 8px 16px;
  background: var(--bg-card);
  border-radius: 20px;
  border: 1px solid var(--border-subtle);
}

.back-btn:hover {
  color: var(--primary-color);
  border-color: var(--primary-color);
  transform: translateX(-4px);
}

/* 核心布局：左侧名片 + 右侧履历 */
.dossier-layout {
  display: flex;
  gap: 32px;
  align-items: flex-start;
}

/* 左侧吸顶名片 */
.dossier-sidebar {
  width: 320px;
  flex-shrink: 0;
  position: sticky;
  top: 100px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.profile-card {
  background: var(--bg-card);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-subtle);
  overflow: hidden;
  box-shadow: var(--shadow-float);
}

.profile-card-header {
  background: var(--primary-color);
  height: 80px;
}

.profile-card-body {
  padding: 0 24px 24px 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  margin-top: -40px;
}

.avatar-lg {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  border: 4px solid var(--bg-card);
  object-fit: cover;
  margin-bottom: 16px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  background: #fff;
}

.name-lg {
  font-size: 24px;
  font-weight: 800;
  color: var(--text-dark);
  margin-bottom: 4px;
}

.title-lg {
  font-size: 14px;
  color: var(--primary-color);
  font-weight: 600;
  background: var(--primary-light);
  padding: 4px 12px;
  border-radius: 12px;
  margin-bottom: 16px;
}

.unit-lg {
  font-size: 14px;
  color: var(--text-regular);
  font-weight: 500;
}

/* 基本信息块 */
.info-card {
  background: var(--bg-card);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-subtle);
  padding: 24px;
  box-shadow: var(--shadow-float);
}

.info-row {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid var(--bg-main);
  font-size: 14px;
}

.info-row:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.info-label {
  color: var(--text-muted);
  font-weight: 500;
}

.info-val {
  color: var(--text-dark);
  font-weight: 600;
  text-align: right;
}

/* 隐私保护声明 */
.privacy-box {
  background: rgba(24, 144, 255, 0.08);
  border: 1px solid rgba(24, 144, 255, 0.2);
  border-radius: var(--radius-md);
  padding: 16px;
  color: #096dd9;
  font-size: 12px;
  line-height: 1.6;
}

/* 右侧主体履历 */
.dossier-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.section-box {
  background: var(--bg-card);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-subtle);
  padding: 40px;
  box-shadow: var(--shadow-float);
}

.section-header {
  font-size: 20px;
  font-weight: 800;
  color: var(--text-dark);
  margin-bottom: 32px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.section-header::before {
  content: '';
  display: block;
  width: 6px;
  height: 20px;
  background: var(--primary-color);
  border-radius: 4px;
}

/* 个人简介文本 */
.bio-text {
  font-size: 15px;
  line-height: 1.8;
  color: var(--text-dark);
  white-space: pre-wrap;
}

/* 资质网格 */
.qual-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.qual-item {
  padding: 20px;
  background: var(--bg-main);
  border-radius: 8px;
  border: 1px solid var(--border-subtle);
}

.qual-item h4 {
  font-size: 13px;
  color: var(--text-muted);
  font-weight: 600;
  margin-bottom: 6px;
  text-transform: uppercase;
}

.qual-item p {
  font-size: 16px;
  color: var(--text-dark);
  font-weight: 700;
}

/* 成果列表 */
.achievement-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.achieve-item h4 {
  font-size: 16px;
  color: var(--text-dark);
  font-weight: 700;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.achieve-item h4::before {
  content: '';
  display: block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  border: 2px solid var(--accent);
}

.achieve-item p {
  font-size: 14px;
  color: var(--text-regular);
  line-height: 1.8;
  white-space: pre-line;
  background: var(--bg-main);
  padding: 20px;
  border-radius: 8px;
  border: 1px solid var(--border-subtle);
}

.empty-state {
  text-align: center;
  padding: 100px 0;
  color: var(--text-muted);
  grid-column: span 2;
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .dossier-layout {
    flex-direction: column;
  }

  .dossier-sidebar {
    width: 100%;
    position: static;
  }
}

@media (max-width: 768px) {
  .grid {
    grid-template-columns: 1fr;
  }

  .search-section {
    padding: 28px 12px 34px;
    margin: 12px 0 10px;
    border-radius: 0;
  }

  .search-container { flex-direction: column; }
  .search-input {
    border-radius: 4px;
    margin-bottom: 8px;
    padding: 10px 14px;
    font-size: 14px;
  }
  .search-btn {
    border-radius: 4px;
    padding: 10px 16px;
    font-size: 14px;
  }

  .filter-card { padding: 12px 12px 3px; }
  .filter-chip { padding: 4px 12px; font-size: 12px; }

  .expert-card {
    flex-direction: column;
    gap: 20px;
  }

  .expert-avatar-box {
    width: 100%;
    height: 200px;
  }

  .pagination-complex {
    flex-wrap: wrap;
    justify-content: center;
    gap: 8px;
  }

  .qual-grid {
    grid-template-columns: 1fr;
  }

  .section-box {
    padding: 24px;
  }
}
/* --- 响应式增强 --- */
@media (max-width: 1024px) {
  .expert-container .container {
    padding: 16px 0;
  }

  .search-section {
    padding: 35px 16px 40px;
    margin: 16px auto 12px;
  }
}

@media (max-width: 768px) {
  .expert-card {
    padding: 20px;
  }

  .expert-name {
    font-size: 18px;
  }

  .expert-unit {
    font-size: 13px;
  }
}

@media (max-width: 480px) {
  .grid {
    grid-template-columns: 1fr;
  }

  .expert-card {
    padding: 16px;
    gap: 16px;
  }

  .expert-avatar-box {
    width: 80px;
    height: 100px;
  }

  .expert-name {
    font-size: 16px;
  }

  .expert-unit {
    font-size: 12px;
  }

  .expert-title {
    font-size: 12px;
  }

  .domain-tag {
    font-size: 11px;
    padding: 3px 8px;
  }

  .search-section {
    padding: 22px 12px 27px;
  }
  .filter-chip {
    font-size: 12px;
    padding: 4px 12px;
  }
}
</style>
