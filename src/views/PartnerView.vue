<template>
  <div class="partner-container">
    <main>
      <div class="container">
        <div id="list-view" v-show="view === 'list'">
          <div class="tabs">
            <div class="tab-item" :class="{ active: currentType === '全部' }" @click="switchTab('全部')">全部</div>
            <div class="tab-item" :class="{ active: currentType === '概念验证平台' }" @click="switchTab('概念验证平台')">概念验证平台</div>
            <div class="tab-item" :class="{ active: currentType === '中试基地' }" @click="switchTab('中试基地')">中试基地</div>
            <div class="tab-item" :class="{ active: currentType === '产业化试验基地' }" @click="switchTab('产业化试验基地')">产业化试验基地</div>
          </div>

          <div class="grid" id="card-grid">
            <div class="search-bar">
              <input type="text" class="search-input" placeholder="搜索平台名称、地址、领域、服务..." v-model="searchKeyword" @input="searchKeyword = $event.target.value">
              <button class="search-btn" @click="searchKeyword = searchKeyword">搜索</button>
              <button class="search-btn search-btn-reset" @click="searchKeyword = ''">重置</button>
            </div>
            <div v-if="filteredData.length === 0" class="empty-state">此分类下暂无数据部署，敬请期待。</div>
            <div class="card" v-for="item in paginatedData" :key="item.id" @click="openDetail(item)">
              <div class="card-img-wrapper">
                <img :src="item.image" :alt="item.title" class="card-img" loading="lazy">
              </div>
              <div class="card-info">
                <div class="card-title">{{ item.title }}</div>
                <div class="card-desc">{{ item.intro }}</div>
                <div class="card-meta">
                  <span>📍 {{ item.address.split('市')[0] }}市</span>
                  <span class="card-tag">{{ item.industry }}</span>
                </div>
              </div>
            </div>
          </div>
          <div class="pagination" id="pagination-container" v-if="filteredData.length > 0">
            <button class="page-btn" @click="changePage('prev')" :disabled="currentPage === 1">&lt;</button>
            <button class="page-btn" v-for="page in totalPages" :key="page" @click="changePage(page)" :class="{ active: page === currentPage }">{{ page }}</button>
            <button class="page-btn" @click="changePage('next')" :disabled="currentPage === totalPages">&gt;</button>
            <select class="page-btn" style="outline: none;" @change="changePageSize($event.target.value)">
              <option value="10" :selected="pageSize === 10">10 条/页</option>
              <option value="20" :selected="pageSize === 20">20 条/页</option>
            </select>
          </div>
        </div>

        <div id="detail-view" v-show="view === 'detail'">
          <div class="back-btn" @click="closeDetail">
            &larr; 返回列表
          </div>
          <div class="detail-header">
            <h1 class="detail-title" id="dt-title">{{ currentDetail.title }}</h1>
            <div class="detail-meta">
              <span id="dt-address">📍 地址：{{ currentDetail.address }}</span>
              <span id="dt-industry">💡 领域：{{ currentDetail.industry }}</span>
            </div>
          </div>
          <div class="detail-content">
            <h3>平台介绍</h3>
            <p id="dt-intro">{{ currentDetail.intro }}</p>
            <h3>可提供的服务</h3>
            <p id="dt-services">{{ currentDetail.services }}</p>
          </div>
          <div class="gallery-section" v-if="currentDetail.images && currentDetail.images.length > 0">
            <h3>平台照片</h3>
            <div class="gallery-grid">
              <div class="gallery-item" v-for="(img, idx) in currentDetail.images" :key="idx" @click="openPreview(fullUrl(img.file_url))">
                <img :src="fullUrl(img.file_url)" :alt="'平台照片 ' + (idx + 1)" loading="lazy">
              </div>
            </div>
          </div>

          <div class="action-bar">
            <button class="btn-cooperate" @click="openDrawer">我要对接合作</button>
          </div>
        </div>
      </div>
    </main>

    <div class="drawer-overlay" id="drawer-overlay" :class="{ active: drawerOpen }" @click="closeDrawer"></div>
    <div class="drawer" id="cooperate-drawer" :class="{ active: drawerOpen }">
      <div class="drawer-header">
        <h2 class="drawer-title">对接合作申请</h2>
        <div class="drawer-close" @click="closeDrawer">×</div>
      </div>

      <div class="drawer-body">
        <form id="cooperate-form" @submit.prevent="submitForm">
          <div class="form-grid">
            <div class="form-group">
              <label class="form-label"><span class="req">*</span>联系人姓名</label>
              <input type="text" class="form-input" placeholder="请输入姓名" required v-model="form.contactName">
            </div>
            <div class="form-group">
              <label class="form-label"><span class="req">*</span>联系人电话</label>
              <input type="text" class="form-input" placeholder="请输入手机号" required v-model="form.contactPhone">
            </div>
            <div class="form-group">
              <label class="form-label"><span class="req">*</span>联系邮箱</label>
              <input type="email" class="form-input" placeholder="请输入工作邮箱" required v-model="form.contactEmail">
            </div>
            <div class="form-group">
              <label class="form-label"><span class="req">*</span>联系单位</label>
              <input type="text" class="form-input" placeholder="请输入企业名称" required v-model="form.contactCompany">
            </div>
            <div class="form-group full-width">
              <label class="form-label"><span class="req">*</span>联系地址</label>
              <input type="text" class="form-input" placeholder="请输入详细通讯地址" required v-model="form.contactAddress">
            </div>
            <div class="form-group full-width">
              <label class="form-label"><span class="req">*</span>意向说明</label>
              <textarea class="form-input" placeholder="请简明扼要地说明您的合作意向或需求..." required v-model="form.intention"></textarea>
            </div>
          </div>
        </form>
      </div>

      <div class="drawer-footer">
        <button type="button" class="btn btn-cancel" @click="closeDrawer">取消</button>
        <button type="button" class="btn btn-submit" @click="submitForm">提交申请</button>
      </div>
    </div>

    <!-- 图片放大预览 -->
    <div class="preview-overlay" :class="{ active: previewVisible }" @click="closePreview">
      <div class="preview-close" @click="closePreview">×</div>
      <img class="preview-image" :src="previewImageUrl" alt="预览">
    </div>
  </div>
</template>

<script>
import useAuth from '../composables/useAuth'
import request from '../utils/request'

const FLASK_BASE_URL = window.location.origin

export default {
  name: 'PartnerView',
  data() {
    const auth = useAuth()
    return {
      auth,
      allData: [],
      searchKeyword: '',
      currentType: '全部',
      currentPage: 1,
      pageSize: 10,
      view: 'list',
      currentDetail: {
        title: '',
        address: '',
        industry: '',
        intro: '',
        services: ''
      },
      drawerOpen: false,
      previewVisible: false,
      previewImageUrl: '',
      form: {
        contactName: '',
        contactPhone: '',
        contactEmail: '',
        contactCompany: '',
        contactAddress: '',
        intention: ''
      }
    }
  },
  computed: {
    filteredData() {
      let result = this.allData
      if (this.currentType !== '全部') {
        result = result.filter(item => item.type === this.currentType)
      }
      if (this.searchKeyword.trim()) {
        const kw = this.searchKeyword.toLowerCase().trim()
        result = result.filter(item =>
          item.title.toLowerCase().includes(kw) ||
          item.address.toLowerCase().includes(kw) ||
          item.industry.toLowerCase().includes(kw) ||
          item.intro.toLowerCase().includes(kw) ||
          item.services.toLowerCase().includes(kw)
        )
      }
      return result
    },
    totalPages() {
      return Math.ceil(this.filteredData.length / this.pageSize) || 1
    },
    paginatedData() {
      const start = (this.currentPage - 1) * this.pageSize
      const end = start + this.pageSize
      return this.filteredData.slice(start, end)
    }
  },
  methods: {
    fullUrl(url) {
      if (url && url.startsWith('/')) {
        return FLASK_BASE_URL + url
      }
      return url
    },
    getFirstImage(images) {
      if (images && images.length > 0) {
        return this.fullUrl(images[0].file_url)
      }
      return 'https://images.unsplash.com/photo-1581092160562-40aa08e78837?w=400&h=300&fit=crop'
    },
    async fetchPartners() {
      try {
        const response = await request.get('/api/publish/public/partners', {
          params: { limit: 50 }
        })
        if (response.code === 200) {
          this.allData = (response.data || []).map(item => ({
            id: item.id,
            type: item.type,
            title: item.name,
            address: item.address,
            industry: item.industry,
            intro: item.intro,
            services: item.services,
            images: item.images || [],
            image: this.getFirstImage(item.images)
          }))
        }
      } catch (error) {
        console.error('获取合作伙伴数据失败:', error)
      }
    },
    switchTab(type) {
      this.currentType = type
      this.currentPage = 1
    },
    changePage(action) {
      if (action === 'prev' && this.currentPage > 1) {
        this.currentPage--
      } else if (action === 'next' && this.currentPage < this.totalPages) {
        this.currentPage++
      } else if (typeof action === 'number') {
        this.currentPage = action
      }
      window.scrollTo({ top: 0, behavior: 'smooth' })
    },
    changePageSize(size) {
      this.pageSize = parseInt(size)
      this.currentPage = 1
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
    },
    openDrawer() {
      if (!this.auth.state.token) {
        this.auth.openLoginPrompt(this.$route.fullPath)
        return
      }
      if (!this.auth.requireVerified()) {
        return
      }
      this.drawerOpen = true
    },
    closeDrawer() {
      this.drawerOpen = false
    },
    submitForm() {
      const form = document.getElementById('cooperate-form')
      if (!form.checkValidity()) {
        form.reportValidity()
        return
      }
      const data = {
        partner_id: this.currentDetail.id,
        contact_name: this.form.contactName,
        contact_phone: this.form.contactPhone,
        contact_email: this.form.contactEmail,
        company: this.form.contactCompany,
        address: this.form.contactAddress,
        intention: this.form.intention
      }
      request.post('/api/publish/cooperation/apply', data).then(() => {
        alert('申请提交成功！我们会尽快与您联系。')
        this.closeDrawer()
        this.form = {
          contactName: '',
          contactPhone: '',
          contactEmail: '',
          contactCompany: '',
          contactAddress: '',
          intention: ''
        }
      }).catch(error => {
        console.error('提交合作申请失败:', error)
      })
    },
    openPreview(url) {
      this.previewImageUrl = url
      this.previewVisible = true
    },
    closePreview() {
      this.previewVisible = false
    }
  },
  mounted() {
    this.fetchPartners()
  }
}
</script>

<style scoped>
.partner-container {
  --primary-color: #1890ff;
  --primary-hover: #096dd9;
  --bg-color: #f0f2f5;
  --text-main: rgba(0, 0, 0, 0.85);
  --text-regular: rgba(0, 0, 0, 0.65);
  --text-muted: rgba(0, 0, 0, 0.45);
  --border-color: #f0f0f0;
  --white: #ffffff;
  --theme-blue: #1890ff;
  --transition-fast: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 使用 CSS 变量设置组件内元素的样式 */
.partner-container * {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, "PingFang SC", sans-serif;
}
.partner-container a { text-decoration: none; color: inherit; }
.partner-container ul { list-style: none; }

/* --- 主内容区 --- */
.partner-container main {
  min-height: calc(100vh - 70px);
  padding-bottom: 80px;
  background-color: var(--bg-color);
  color: var(--text-main);
  line-height: 1.6;
}
.partner-container .container {
  max-width: 1200px;
  margin: 40px auto;
  padding: 0 20px;
}
.partner-container #list-view {
  display: block;
  animation: fadeUp 0.4s ease-out;
}
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(15px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 严谨的极线风 Tabs */
.partner-container .tabs {
  display: flex;
  border-bottom: 1px solid var(--border-color);
  margin-bottom: 30px;
}
.partner-container .tab-item {
  padding: 12px 24px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
  color: var(--text-muted);
  position: relative;
  transition: var(--transition-fast);
}
.partner-container .tab-item:hover {
  color: var(--primary-color);
}
.partner-container .tab-item.active {
  color: var(--primary-color);
  font-weight: 600;
}
.partner-container .tab-item.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  width: 100%;
  height: 3px;
  background-color: var(--primary-color);
}

/* 搜索栏 */
.partner-container .search-bar {
  grid-column: span 2;
  display: flex;
  gap: 10px;
  margin-bottom: 4px;
}
.partner-container .search-input {
  flex: 1;
  max-width: 420px;
  padding: 10px 16px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 14px;
  color: var(--text-main);
  transition: var(--transition-fast);
  outline: none;
  background: var(--white);
}
.partner-container .search-input:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(24, 144, 255, 0.1);
}
.partner-container .search-input::placeholder {
  color: #c7c7cc;
}
.partner-container .search-btn {
  padding: 10px 20px;
  border: 1px solid var(--primary-color);
  background: var(--primary-color);
  color: var(--white);
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: var(--transition-fast);
  font-weight: 500;
}
.partner-container .search-btn:hover {
  background: var(--primary-hover);
}
.partner-container .search-btn-reset {
  background: var(--white);
  color: var(--primary-color);
}
.partner-container .search-btn-reset:hover {
  background: #e6f7ff;
}

@media (max-width: 768px) {
  .partner-container .search-bar {
    grid-column: span 1;
    flex-wrap: wrap;
  }
  .partner-container .search-input {
    max-width: 100%;
  }
}

/* --- 修正后的图片格式与卡片排版 --- */
.partner-container .grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .partner-container .grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 1024px) {
  .partner-container .grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.partner-container .card {
  background: var(--white);
  display: flex;
  flex-direction: row;
  gap: 24px;
  padding: 28px;
  cursor: pointer;
  transition: var(--transition-fast);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  position: relative;
}

.partner-container .card::before {
  content: '';
  position: absolute;
  left: -1px;
  top: -1px;
  width: 4px;
  height: calc(100% + 2px);
  background-color: transparent;
  transition: var(--transition-fast);
  border-radius: 6px 0 0 6px;
}
.partner-container .card:hover {
  border-color: var(--primary-color);
  box-shadow: 0 8px 24px rgba(0,0,0,0.08);
  transform: translateY(-4px);
}
.partner-container .card:hover::before {
  background-color: var(--primary-color);
}

.partner-container .card-img-wrapper {
  width: 160px;
  height: 110px;
  flex-shrink: 0;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid var(--border-color);
  background: var(--bg-color);
}

.partner-container .card-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}

.partner-container .card:hover .card-img {
  transform: scale(1.05);
}

.partner-container .card-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.partner-container .card-title {
  font-size: 20px;
  font-weight: 800;
  color: var(--text-main);
  margin-bottom: 6px;
}
.partner-container .card-desc {
  font-size: 13px;
  color: var(--text-regular);
  margin-bottom: 8px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.5;
}

.partner-container .card-meta {
  font-size: 13px;
  color: var(--text-muted);
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
}
.partner-container .card-tag {
  color: var(--primary-color);
  font-weight: 500;
  background: rgba(11, 87, 208, 0.08);
  padding: 2px 8px;
  border-radius: 2px;
  font-size: 12px;
}

/* 分页组件 */
.partner-container .pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 40px;
  gap: 6px;
  align-items: center;
}
.partner-container .page-btn {
  min-width: 32px;
  height: 32px;
  padding: 0 10px;
  border: 1px solid var(--border-color);
  background: var(--white);
  border-radius: 4px;
  font-size: 14px;
  color: var(--text-regular);
  cursor: pointer;
  transition: var(--transition-fast);
}
.partner-container .page-btn:hover:not(:disabled) {
  border-color: var(--primary-color);
  color: var(--primary-color);
}
.partner-container .page-btn.active {
  background: var(--primary-color);
  color: var(--white);
  border-color: var(--primary-color);
  pointer-events: none;
}
.partner-container .page-btn:disabled {
  background: #f9f9f9;
  color: #d2d2d7;
  cursor: not-allowed;
  border-color: #e5e5ea;
}

/* --- 详情页 --- */
.partner-container #detail-view {
  display: block;
  background: var(--white);
  border-radius: 4px;
  border: 1px solid var(--border-color);
  padding: 40px 50px;
  animation: fadeUp 0.4s;
}
.partner-container .back-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  margin-bottom: 20px;
  cursor: pointer;
  color: var(--text-muted);
  font-size: 14px;
  transition: var(--transition-fast);
}
.partner-container .back-btn:hover {
  color: var(--primary-color);
}

.partner-container .detail-header {
  border-bottom: 2px solid var(--text-main);
  padding-bottom: 20px;
  margin-bottom: 30px;
}
.partner-container .detail-title {
  font-size: 26px;
  font-weight: bold;
  margin-bottom: 10px;
  color: var(--text-main);
}
.partner-container .detail-meta {
  color: var(--text-regular);
  font-size: 14px;
  display: flex;
  gap: 30px;
}

.partner-container .detail-content h3 {
  font-size: 16px;
  font-weight: bold;
  background: var(--bg-color);
  padding: 8px 12px;
  border-left: 4px solid var(--primary-color);
  color: var(--text-main);
  margin: 30px 0 15px 0;
}
.partner-container .detail-content p {
  color: var(--text-regular);
  margin-bottom: 20px;
  font-size: 15px;
  line-height: 1.8;
}

.partner-container .action-bar {
  margin-top: 50px;
  text-align: center;
}
.partner-container .btn-cooperate {
  background: var(--primary-color);
  color: var(--white);
  border: none;
  padding: 12px 40px;
  font-size: 16px;
  border-radius: 4px;
  cursor: pointer;
  transition: var(--transition-fast);
  font-weight: 500;
}
.partner-container .btn-cooperate:hover {
  background: var(--primary-hover);
}

.partner-container .empty-state {
  text-align: center;
  padding: 80px 0;
  color: var(--text-muted);
  grid-column: span 2;
  font-size: 15px;
}

@media (max-width: 1024px) {
  .partner-container .empty-state {
    grid-column: span 2;
  }
}

@media (max-width: 768px) {
  .partner-container .empty-state {
    grid-column: span 1;
  }
}

/* --- 企业级右侧抽屉式表单 --- */
.partner-container .drawer-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 10001;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.3s ease;
}
.partner-container .drawer-overlay.active {
  opacity: 1;
  pointer-events: auto;
}

.partner-container .drawer {
  position: fixed;
  right: -650px;
  top: 0;
  width: 600px;
  height: 100vh;
  background: var(--white);
  z-index: 10002;
  transition: right 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: -4px 0 24px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
}
.partner-container .drawer.active {
  right: 0;
}

.partner-container .drawer-header {
  padding: 24px 30px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--bg-color);
}
.partner-container .drawer-title {
  font-size: 20px;
  color: var(--text-main);
  font-weight: bold;
}
.partner-container .drawer-close {
  font-size: 24px;
  cursor: pointer;
  color: var(--text-muted);
  transition: var(--transition-fast);
  line-height: 1;
}
.partner-container .drawer-close:hover {
  color: #ff4d4f;
  transform: scale(1.1);
}

.partner-container .drawer-body {
  padding: 30px;
  overflow-y: auto;
  flex: 1;
}

.partner-container .drawer-footer {
  padding: 20px 30px;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  background: var(--bg-color);
}

.partner-container .form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}
.partner-container .full-width {
  grid-column: span 2;
}
.partner-container .form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.partner-container .form-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-regular);
}
.partner-container .form-label span.req {
  color: #ff4d4f;
  margin-right: 4px;
}

.partner-container .form-input {
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 14px;
  color: var(--text-main);
  transition: var(--transition-fast);
}
.partner-container .form-input::placeholder {
  color: #c7c7cc;
}
.partner-container .form-input:focus {
  border-color: var(--primary-color);
  outline: none;
  box-shadow: 0 0 0 2px rgba(11, 87, 208, 0.1);
}
.partner-container textarea.form-input {
  height: 100px;
  resize: none;
}

.partner-container .btn {
  padding: 10px 24px;
  font-size: 14px;
  border-radius: 4px;
  cursor: pointer;
  transition: var(--transition-fast);
  font-weight: 500;
}
.partner-container .btn-cancel {
  background: var(--white);
  border: 1px solid var(--border-color);
  color: var(--text-regular);
}
.partner-container .btn-cancel:hover {
  color: var(--primary-color);
  border-color: var(--primary-color);
}
.partner-container .btn-submit {
  background: var(--primary-color);
  border: 1px solid var(--primary-color);
  color: var(--white);
}
.partner-container .btn-submit:hover {
  background: var(--primary-hover);
}

/* --- 图片展示区 --- */
.partner-container .gallery-section {
  margin-top: 50px;
  padding-top: 30px;
  border-top: 1px solid var(--border-color);
}
.partner-container .gallery-section h3 {
  font-size: 16px;
  font-weight: bold;
  background: var(--bg-color);
  padding: 8px 12px;
  border-left: 4px solid var(--primary-color);
  color: var(--text-main);
  margin-bottom: 20px;
}
.partner-container .gallery-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}
@media (max-width: 768px) {
  .partner-container .gallery-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
.partner-container .gallery-item {
  border-radius: 6px;
  overflow: hidden;
  cursor: pointer;
  border: 1px solid var(--border-color);
  aspect-ratio: 4 / 3;
  transition: var(--transition-fast);
}
.partner-container .gallery-item:hover {
  border-color: var(--primary-color);
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.15);
}
.partner-container .gallery-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
  display: block;
}
.partner-container .gallery-item:hover img {
  transform: scale(1.08);
}

/* --- 图片放大预览遮罩 --- */
.preview-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.85);
  z-index: 20001;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.3s ease;
}
.preview-overlay.active {
  opacity: 1;
  pointer-events: auto;
}
.preview-close {
  position: absolute;
  top: 24px;
  right: 32px;
  font-size: 40px;
  color: #fff;
  cursor: pointer;
  line-height: 1;
  opacity: 0.7;
  transition: opacity 0.2s;
  z-index: 20002;
}
.preview-close:hover {
  opacity: 1;
}
.preview-image {
  max-width: 90vw;
  max-height: 90vh;
  object-fit: contain;
  border-radius: 4px;
  box-shadow: 0 8px 40px rgba(0,0,0,0.5);
}

/* ====== iPad / 平板 (≤1024px) ====== */
@media (max-width: 1024px) {
  .partner-container .container {
    padding: 0 16px;
  }
  .partner-container .tabs {
    overflow-x: auto;
    white-space: nowrap;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;
  }
  .partner-container .tabs::-webkit-scrollbar {
    display: none;
  }
  .partner-container .tab-item {
    flex-shrink: 0;
  }
  .partner-container .grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* ====== 移动端 (≤768px) ====== */
@media (max-width: 768px) {
  .partner-container .container {
    padding: 0 12px;
    margin: 20px auto;
  }
  .partner-container .tab-item {
    font-size: 14px;
    padding: 10px 16px;
  }
  .partner-container .grid {
    grid-template-columns: 1fr;
  }
  .partner-container .search-bar {
    flex-direction: column;
    gap: 8px;
  }
  .partner-container .search-btn {
    width: 100%;
  }
  .partner-container .card {
    padding: 14px;
    gap: 14px;
  }
  .partner-container .card-img-wrapper {
    width: 120px;
    height: 90px;
  }
  .partner-container .drawer {
    width: 100vw;
    right: -100vw;
  }
  .partner-container .pagination {
    flex-wrap: wrap;
    justify-content: center;
    gap: 4px;
  }
  .partner-container .page-btn {
    min-width: 28px;
    height: 28px;
    font-size: 12px;
  }
  .partner-container #detail-view {
    padding: 20px;
  }
  .partner-container .detail-title {
    font-size: 20px;
  }
  .partner-container .detail-meta {
    flex-direction: column;
    gap: 8px;
  }
  .partner-container .detail-header {
    padding-bottom: 15px;
  }
}

/* ====== 小屏手机 (≤480px) ====== */
@media (max-width: 480px) {
  .partner-container .container {
    padding: 0 10px;
  }
  .partner-container .tab-item {
    font-size: 13px;
    padding: 8px 12px;
  }
  .partner-container .card {
    flex-direction: column;
    padding: 12px;
    gap: 10px;
  }
  .partner-container .card-img-wrapper {
    width: 100%;
    height: 160px;
  }
  .partner-container .card-title {
    font-size: 15px;
  }
  .partner-container .card-desc {
    font-size: 12px;
  }
  .partner-container .card-meta {
    font-size: 12px;
  }
  .partner-container .drawer-header {
    padding: 16px 20px;
  }
  .partner-container .drawer-body {
    padding: 20px;
  }
  .partner-container .drawer-footer {
    padding: 16px 20px;
  }
  .partner-container .drawer-title {
    font-size: 17px;
  }
  .partner-container .form-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  .partner-container .full-width {
    grid-column: span 1;
  }
  .partner-container .detail-title {
    font-size: 18px;
  }
  .partner-container #detail-view {
    padding: 16px;
  }
}
</style>
