<template>
  <div class="finance-container">
    <main>
      <div class="container">
        <div id="list-view" v-show="view === 'list'">
          <div class="search-bar">
            <input type="text" class="search-input" placeholder="搜索机构名称、简介、服务..." v-model="searchKeyword" @input="searchKeyword = $event.target.value">
            <button class="search-btn" @click="searchKeyword = searchKeyword">搜索</button>
            <button class="search-btn search-btn-reset" @click="searchKeyword = ''">重置</button>
          </div>

          <div class="grid" id="card-grid">
            <div v-if="filteredData.length === 0" class="empty-state">暂无金融服务机构数据，敬请期待。</div>
            <div class="card" v-for="item in paginatedData" :key="item.id" @click="openDetail(item)">
              <div class="card-img-wrapper">
                <img :src="item.image" :alt="item.title" class="card-img" loading="lazy">
              </div>
              <div class="card-name">{{ item.title }}</div>
            </div>
          </div>

          <div class="pagination" v-if="filteredData.length > 0">
            <button class="page-btn" @click="changePage('prev')" :disabled="currentPage === 1">&lt;</button>
            <button class="page-btn" v-for="page in totalPages" :key="page" @click="changePage(page)" :class="{ active: page === currentPage }">{{ page }}</button>
            <button class="page-btn" @click="changePage('next')" :disabled="currentPage === totalPages">&gt;</button>
            <select class="page-btn page-select" @change="changePageSize($event.target.value)">
              <option value="6" :selected="pageSize === 6">6 条/页</option>
              <option value="12" :selected="pageSize === 12">12 条/页</option>
            </select>
          </div>
        </div>

        <div id="detail-view" v-show="view === 'detail'">
          <div class="back-btn" @click="closeDetail">
            &larr; 返回列表
          </div>
          <div class="detail-header">
            <h1 class="detail-title">{{ currentDetail.title }}</h1>
          </div>
          <div class="detail-content">
            <h3>机构简介</h3>
            <p>{{ currentDetail.intro }}</p>
            <h3>可提供的服务</h3>
            <p>{{ currentDetail.services }}</p>
          </div>
          <div class="gallery-section" v-if="currentDetail.images && currentDetail.images.length > 0">
            <h3>机构照片</h3>
            <div class="gallery-grid">
              <div class="gallery-item" v-for="(img, idx) in currentDetail.images" :key="idx" @click="openPreview(fullUrl(img.file_url))">
                <img :src="fullUrl(img.file_url)" :alt="'机构照片 ' + (idx + 1)" loading="lazy">
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- 图片放大预览 -->
    <div class="preview-overlay" :class="{ active: previewVisible }" @click="closePreview">
      <div class="preview-close" @click="closePreview">×</div>
      <img class="preview-image" :src="previewImageUrl" alt="预览">
    </div>
  </div>
</template>

<script>
import request from '../utils/request'
import useAuth from '../composables/useAuth'

const FLASK_BASE_URL = window.location.origin

export default {
  name: 'FinancialView',
  data() {
    const auth = useAuth()
    return {
      auth,
      allData: [],
      searchKeyword: '',
      currentPage: 1,
      pageSize: 6,
      view: 'list',
      currentDetail: {
        title: '',
        intro: '',
        services: '',
        images: []
      },
      previewVisible: false,
      previewImageUrl: ''
    }
  },
  computed: {
    filteredData() {
      let result = this.allData
      if (this.searchKeyword.trim()) {
        const kw = this.searchKeyword.toLowerCase().trim()
        result = result.filter(item =>
          item.title.toLowerCase().includes(kw) ||
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
      return 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&h=300&fit=crop'
    },
    async fetchFinancialServices() {
      try {
        const response = await request.get('/api/publish/public/financial-services', {
          params: { limit: 50 }
        })
        if (response.code === 200) {
          this.allData = (response.data || []).map(item => ({
            id: item.id,
            title: item.name,
            intro: item.intro,
            services: item.services,
            images: item.images || [],
            image: this.getFirstImage(item.images)
          }))
        }
      } catch (error) {
        console.error('获取金融服务数据失败:', error)
      }
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
    openPreview(url) {
      this.previewImageUrl = url
      this.previewVisible = true
    },
    closePreview() {
      this.previewVisible = false
    }
  },
  mounted() {
    this.fetchFinancialServices()
  }
}
</script>

<style scoped>
.finance-container {
  --primary-color: #1890ff;
  --primary-hover: #096dd9;
  --bg-color: #f0f2f5;
  --text-main: rgba(0, 0, 0, 0.85);
  --text-regular: rgba(0, 0, 0, 0.65);
  --text-muted: rgba(0, 0, 0, 0.45);
  --border-color: #f0f0f0;
  --white: #ffffff;
  --transition-fast: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.finance-container * {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, "PingFang SC", sans-serif;
}
.finance-container a { text-decoration: none; color: inherit; }
.finance-container ul { list-style: none; }

.finance-container main {
  min-height: calc(100vh - 70px);
  padding-bottom: 80px;
  background-color: var(--bg-color);
  color: var(--text-main);
  line-height: 1.6;
}
.finance-container .container {
  max-width: 1200px;
  margin: 40px auto;
  padding: 0 20px;
}
.finance-container #list-view {
  display: block;
  animation: fadeUp 0.4s ease-out;
}
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(15px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 搜索栏 */
.finance-container .search-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 24px;
}
.finance-container .search-input {
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
.finance-container .search-input:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(24, 144, 255, 0.1);
}
.finance-container .search-btn {
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
.finance-container .search-btn:hover {
  background: var(--primary-hover);
}
.finance-container .search-btn-reset {
  background: var(--white);
  color: var(--primary-color);
}
.finance-container .search-btn-reset:hover {
  background: #e6f7ff;
}

/* 卡片网格 - 3列 */
.finance-container .grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.finance-container .card {
  background: var(--white);
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: var(--transition-fast);
  border: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
}
.finance-container .card:hover {
  border-color: var(--primary-color);
  box-shadow: 0 8px 24px rgba(0,0,0,0.08);
  transform: translateY(-4px);
}

.finance-container .card-img-wrapper {
  width: 100%;
  height: 200px;
  overflow: hidden;
  background: var(--bg-color);
}
.finance-container .card-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}
.finance-container .card:hover .card-img {
  transform: scale(1.05);
}

.finance-container .card-name {
  padding: 20px;
  font-size: 20px;
  font-weight: 800;
  color: var(--text-main);
  text-align: center;
  letter-spacing: 0.5px;
}

/* 分页 */
.finance-container .pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 40px;
  gap: 6px;
  align-items: center;
}
.finance-container .page-btn {
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
.finance-container .page-btn:hover:not(:disabled) {
  border-color: var(--primary-color);
  color: var(--primary-color);
}
.finance-container .page-btn.active {
  background: var(--primary-color);
  color: var(--white);
  border-color: var(--primary-color);
  pointer-events: none;
}
.finance-container .page-btn:disabled {
  background: #f9f9f9;
  color: #d2d2d7;
  cursor: not-allowed;
  border-color: #e5e5ea;
}
.finance-container .page-select {
  outline: none;
  cursor: pointer;
}

/* 空状态 */
.finance-container .empty-state {
  text-align: center;
  padding: 80px 0;
  color: var(--text-muted);
  grid-column: span 3;
  font-size: 15px;
}

/* 详情页 */
.finance-container #detail-view {
  display: block;
  background: var(--white);
  border-radius: 4px;
  border: 1px solid var(--border-color);
  padding: 40px 50px;
  animation: fadeUp 0.4s;
}
.finance-container .back-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  margin-bottom: 20px;
  cursor: pointer;
  color: var(--text-muted);
  font-size: 14px;
  transition: var(--transition-fast);
}
.finance-container .back-btn:hover {
  color: var(--primary-color);
}
.finance-container .detail-header {
  border-bottom: 2px solid var(--text-main);
  padding-bottom: 20px;
  margin-bottom: 30px;
}
.finance-container .detail-title {
  font-size: 26px;
  font-weight: bold;
  margin-bottom: 10px;
  color: var(--text-main);
}
.finance-container .detail-content h3 {
  font-size: 16px;
  font-weight: bold;
  background: var(--bg-color);
  padding: 8px 12px;
  border-left: 4px solid var(--primary-color);
  color: var(--text-main);
  margin: 30px 0 15px 0;
}
.finance-container .detail-content p {
  color: var(--text-regular);
  margin-bottom: 20px;
  font-size: 15px;
  line-height: 1.8;
}

/* 图片展示区 */
.finance-container .gallery-section {
  margin-top: 50px;
  padding-top: 30px;
  border-top: 1px solid var(--border-color);
}
.finance-container .gallery-section h3 {
  font-size: 16px;
  font-weight: bold;
  background: var(--bg-color);
  padding: 8px 12px;
  border-left: 4px solid var(--primary-color);
  color: var(--text-main);
  margin-bottom: 20px;
}
.finance-container .gallery-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}
.finance-container .gallery-item {
  border-radius: 6px;
  overflow: hidden;
  cursor: pointer;
  border: 1px solid var(--border-color);
  aspect-ratio: 4 / 3;
  transition: var(--transition-fast);
}
.finance-container .gallery-item:hover {
  border-color: var(--primary-color);
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.15);
}
.finance-container .gallery-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
  display: block;
}
.finance-container .gallery-item:hover img {
  transform: scale(1.08);
}

/* 图片放大预览 */
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

/* 响应式 */
@media (max-width: 1024px) {
  .finance-container .grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .finance-container .empty-state {
    grid-column: span 2;
  }
}

@media (max-width: 768px) {
  .finance-container .container {
    padding: 0 12px;
    margin: 20px auto;
  }
  .finance-container .grid {
    grid-template-columns: 1fr;
  }
  .finance-container .empty-state {
    grid-column: span 1;
  }
  .finance-container .search-bar {
    flex-direction: column;
    gap: 8px;
  }
  .finance-container .search-btn {
    width: 100%;
  }
  .finance-container .pagination {
    flex-wrap: wrap;
    justify-content: center;
    gap: 4px;
  }
  .finance-container #detail-view {
    padding: 20px;
  }
  .finance-container .detail-title {
    font-size: 20px;
  }
  .finance-container .gallery-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .finance-container .card-img-wrapper {
    height: 180px;
  }
  .finance-container .card-name {
    font-size: 17px;
    padding: 16px;
  }
  .finance-container #detail-view {
    padding: 16px;
  }
}
</style>
