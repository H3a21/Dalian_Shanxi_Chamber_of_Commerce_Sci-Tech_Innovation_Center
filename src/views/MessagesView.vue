<template>
  <div class="messages-page">
    <!-- 顶部导航 -->
    <div class="messages-header">
      <button class="back-btn" @click="$router.back()">
        <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="15 18 9 12 15 6"/>
        </svg>
        返回
      </button>
      <div class="header-title">
        <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#1890ff" stroke-width="2">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
        </svg>
        消息中心
      </div>
      <button class="mark-all-btn" @click="markAllRead" v-if="unreadTotal > 0">
        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="9 11 12 14 22 4"/>
          <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
        </svg>
        全部已读
      </button>
    </div>

    <!-- 筛选标签 -->
    <div class="filter-tabs">
      <span v-for="tab in filterTabs" :key="tab.key"
        class="filter-tab"
        :class="{ active: currentFilter === tab.key }"
        @click="switchFilter(tab.key)">
        {{ tab.label }}
        <span class="tab-count" v-if="tab.count > 0">{{ tab.count }}</span>
      </span>
    </div>

    <!-- 消息列表 -->
    <div class="messages-body">
      <div v-if="loading" class="loading-state">加载中...</div>

      <div v-else-if="messages.length === 0" class="empty-state">
        <svg viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="#d9d9d9" stroke-width="1.5">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
        </svg>
        <p>暂无消息</p>
      </div>

      <div v-else class="message-list">
        <div v-for="msg in messages" :key="msg.id"
          class="message-card"
          :class="[msgCardType(msg), { unread: !msg.is_read }]"
          @click="handleMessageClick(msg)">
          <div class="msg-icon" :class="msgCardType(msg)">
            <svg v-if="msg.biz_type === 'achievement'" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
              <polyline points="22 4 12 14.01 9 11.01"/>
            </svg>
            <svg v-else-if="msg.biz_type === 'demand'" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
              <line x1="9" y1="10" x2="15" y2="10"/>
              <line x1="12" y1="7" x2="12" y2="13"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="16" x2="12" y2="12"/>
              <line x1="12" y1="8" x2="12.01" y2="8"/>
            </svg>
          </div>
          <div class="msg-body">
            <div class="msg-header">
              <span class="msg-title">{{ msg.title }}</span>
              <span class="msg-time">{{ msg.create_time }}</span>
            </div>
            <div class="msg-content">{{ msg.content }}</div>
          </div>
          <div class="msg-status" v-if="!msg.is_read">
            <span class="unread-dot"></span>
          </div>
        </div>
      </div>

      <!-- 分页 -->
      <div class="pagination" v-if="total > 0">
        <span class="page-size-select">
          每页
          <select v-model.number="pageSize" @change="handlePageSizeChange(pageSize)">
            <option :value="5">5</option>
            <option :value="10">10</option>
            <option :value="15">15</option>
            <option :value="20">20</option>
          </select>
          条
        </span>
        <div class="pagination-center">
          <span class="page-total-info">共 {{ total }} 条</span>
          <template v-if="totalPages > 1">
            <button :disabled="currentPage <= 1" @click="changePage(currentPage - 1)">上一页</button>
            <span v-for="p in displayPages" :key="p" class="page-num"
              :class="{ active: p === currentPage }"
              @click="changePage(p)">{{ p }}</span>
            <button :disabled="currentPage >= totalPages" @click="changePage(currentPage + 1)">下一页</button>
          </template>
        </div>
      </div>
    </div>

    <!-- 消息详情弹窗 -->
    <div class="modal-overlay" v-if="showDetailModal" @click.self="closeDetailModal">
      <div class="modal-box">
        <div class="modal-header">
          <span class="modal-title">{{ detailMsg.title }}</span>
          <button class="modal-close" @click="closeDetailModal">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <div class="detail-meta">
            <span class="detail-type" :class="detailMsg.msg_type">
              {{ detailMsg.msg_type === 'result' ? '审核通知' : '系统通知' }}
            </span>
            <span class="detail-time">{{ detailMsg.create_time }}</span>
          </div>
          <div class="detail-content">{{ detailMsg.content }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, inject } from 'vue'
import request from '../utils/request'

const messages = ref([])

// 消息类型对应 CSS class
function msgCardType(msg) {
  if (msg.biz_type === 'achievement') return 'type-achievement'
  if (msg.biz_type === 'demand') return 'type-demand'
  if (msg.msg_type === 'system') return 'type-system'
  return 'type-achievement'
}
const loading = ref(false)
const currentPage = ref(1)
const total = ref(0)
const totalPages = ref(0)
const currentFilter = ref('all')
const unreadTotal = ref(0)
const allTotal = ref(0)
const resultTotal = ref(0)
const systemTotal = ref(0)
const refreshMessageCount = inject('refreshMessageCount', null)

const filterTabs = computed(() => [
  { key: 'all', label: '全部', count: allTotal.value },
  { key: 'unread', label: '未读', count: unreadTotal.value },
  { key: 'result', label: '审核通知', count: resultTotal.value },
  { key: 'system', label: '系统通知', count: systemTotal.value }
])

const pageSize = ref(15)

const displayPages = computed(() => {
  const pages = []
  const total = totalPages.value
  const current = currentPage.value
  let start = Math.max(1, current - 2)
  let end = Math.min(total, current + 2)
  if (end - start < 4) {
    if (start === 1) end = Math.min(total, start + 4)
    else start = Math.max(1, end - 4)
  }
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})

async function fetchMessages() {
  loading.value = true
  try {
    const params = { page: currentPage.value, page_size: pageSize.value }
    if (currentFilter.value === 'unread') {
      params.unread_only = '1'
    } else if (currentFilter.value !== 'all') {
      params.msg_type = currentFilter.value
    }
    const res = await request.get('/api/messages', { params })
    if (res.code === 200) {
      messages.value = res.data || []
      total.value = res.total || 0
      totalPages.value = res.total_pages || 0
    }
    // 独立获取各标签计数
    await fetchTabCounts()
  } catch (e) {
    console.error('获取消息失败', e)
  } finally {
    loading.value = false
  }
}

async function fetchTabCounts() {
  try {
    const [allRes, resultRes, systemRes] = await Promise.all([
      request.get('/api/messages', { params: { page: 1, page_size: 1 } }),
      request.get('/api/messages', { params: { msg_type: 'result', page: 1, page_size: 1 } }),
      request.get('/api/messages', { params: { msg_type: 'system', page: 1, page_size: 1 } })
    ])
    if (allRes.code === 200) allTotal.value = allRes.total || 0
    if (resultRes.code === 200) resultTotal.value = resultRes.total || 0
    if (systemRes.code === 200) systemTotal.value = systemRes.total || 0
  } catch (e) {
    // ignore
  }
}

async function fetchUnreadCount() {
  try {
    const res = await request.get('/api/messages/unread-count')
    if (res.code === 200) {
      unreadTotal.value = res.data.count || 0
    }
  } catch (e) {
    // ignore
  }
}

function switchFilter(filter) {
  currentFilter.value = filter
  currentPage.value = 1
  fetchMessages()
}

function changePage(page) {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  fetchMessages()
}

function handlePageSizeChange(size) {
  pageSize.value = size
  currentPage.value = 1
  fetchMessages()
}

const showDetailModal = ref(false)
const detailMsg = ref({})

function closeDetailModal() {
  showDetailModal.value = false
}

async function handleMessageClick(msg) {
  // 打开详情弹窗
  detailMsg.value = msg
  showDetailModal.value = true

  if (!msg.is_read) {
    try {
      await request.put(`/api/messages/${msg.id}/read`)
      msg.is_read = true
      fetchUnreadCount()
      refreshMessageCount && refreshMessageCount()
    } catch (e) {
      // ignore
    }
  }
}

async function markAllRead() {
  try {
    await request.put('/api/messages/read-all')
    messages.value.forEach(m => { m.is_read = true })
    unreadTotal.value = 0
    refreshMessageCount && refreshMessageCount()
  } catch (e) {
    // ignore
  }
}

onMounted(() => {
  fetchMessages()
  fetchUnreadCount()
})

// 切换标签时重新获取未读数
watch(currentFilter, () => {
  if (currentFilter.value === 'unread') {
    fetchUnreadCount()
  }
})
</script>

<style scoped>
.messages-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  min-height: calc(100vh - 80px);
}

.messages-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 0;
  border-bottom: 1px solid #f0f0f0;
  margin-bottom: 16px;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  border: none;
  background: none;
  color: #666;
  cursor: pointer;
  font-size: 14px;
  padding: 6px 12px;
  border-radius: 6px;
  transition: all 0.2s;
}
.back-btn:hover {
  background: #f5f5f5;
  color: #1890ff;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: rgba(0,0,0,0.85);
}

.mark-all-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  border: 1px solid #e8e8e8;
  background: white;
  color: #1890ff;
  cursor: pointer;
  font-size: 13px;
  padding: 6px 14px;
  border-radius: 6px;
  transition: all 0.2s;
}
.mark-all-btn:hover {
  background: #e6f7ff;
  border-color: #91d5ff;
}

.filter-tabs {
  display: flex;
  gap: 4px;
  margin-bottom: 16px;
  background: white;
  padding: 4px;
  border-radius: 8px;
  border: 1px solid #f0f0f0;
}

.filter-tab {
  flex: 1;
  text-align: center;
  padding: 8px 16px;
  font-size: 14px;
  color: #666;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}
.filter-tab:hover {
  color: #1890ff;
  background: #f0f8ff;
}
.filter-tab.active {
  color: white;
  background: #1890ff;
  font-weight: 500;
}
.filter-tab.active .tab-count {
  background: rgba(255,255,255,0.3);
  color: white;
}

.tab-count {
  font-size: 11px;
  background: #f5f5f5;
  color: #999;
  padding: 1px 7px;
  border-radius: 10px;
  min-width: 18px;
  text-align: center;
}

.messages-body {
  background: white;
  border-radius: 12px;
  border: 1px solid #f0f0f0;
  min-height: 300px;
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  color: #999;
  font-size: 14px;
  gap: 16px;
}
.empty-state p {
  margin: 0;
  font-size: 15px;
  color: #bbb;
}

.message-list {
  padding: 0;
}

.message-card {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 16px 20px;
  border-bottom: 1px solid #f5f5f5;
  cursor: pointer;
  transition: background 0.2s;
  position: relative;
}
.message-card:last-child {
  border-bottom: none;
}
.message-card:hover {
  background: #fafafa;
}
.message-card.unread {
  background: #f0f8ff;
}
.message-card.unread:hover {
  background: #e6f4ff;
}

/* 消息类型渐变左边框（使用伪元素实现渐变色） */
.message-card.type-achievement::before,
.message-card.type-demand::before,
.message-card.type-system::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  width: 4px;
  height: 100%;
  pointer-events: none;
}
.message-card.type-achievement::before {
  background: linear-gradient(180deg, #0050b3 0%, #ffffff 100%);
}
.message-card.type-demand::before {
  background: linear-gradient(180deg, #237804 0%, #ffffff 100%);
}
.message-card.type-system::before {
  background: linear-gradient(180deg, #d46b08 0%, #ffffff 100%);
}

.msg-icon {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 2px;
}
.msg-icon.type-achievement {
  background: #e6f7ff;
  color: #1890ff;
}
.msg-icon.type-demand {
  background: #e8f5e9;
  color: #2e7d32;
}
.msg-icon.type-system {
  background: #fff7e6;
  color: #d46b08;
}

.msg-body {
  flex: 1;
  min-width: 0;
}

.msg-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}
.msg-title {
  font-size: 14px;
  font-weight: 500;
  color: rgba(0,0,0,0.85);
}
.message-card.unread .msg-title {
  font-weight: 600;
  color: #000;
}
.msg-time {
  font-size: 12px;
  color: #bbb;
  white-space: nowrap;
}

.msg-content {
  font-size: 13px;
  color: #888;
  line-height: 1.5;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.msg-status {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  padding-top: 6px;
}
.unread-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #1890ff;
  box-shadow: 0 0 0 2px rgba(24,144,255,0.2);
}

.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 4px;
  padding: 20px;
}
.pagination-center {
  display: flex;
  align-items: center;
  gap: 4px;
}
.pagination button {
  border: 1px solid #e8e8e8;
  background: white;
  color: #666;
  padding: 6px 14px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}
.pagination button:hover:not(:disabled) {
  color: #1890ff;
  border-color: #1890ff;
}
.pagination button:disabled {
  color: #d9d9d9;
  cursor: not-allowed;
}
.page-num {
  width: 34px;
  height: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  color: #666;
  transition: all 0.2s;
}
.page-num:hover {
  color: #1890ff;
  background: #f0f8ff;
}
.page-num.active {
  background: #1890ff;
  color: white;
  font-weight: 500;
}

/* 消息详情弹窗 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.modal-box {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 520px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0,0,0,0.15);
  animation: modal-in 0.2s ease;
}
@keyframes modal-in {
  from { opacity: 0; transform: scale(0.95) translateY(10px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}
.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 24px;
  border-bottom: 1px solid #f0f0f0;
}
.modal-title {
  font-size: 16px;
  font-weight: 600;
  color: rgba(0,0,0,0.85);
  flex: 1;
  margin-right: 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.modal-close {
  border: none;
  background: #f5f5f5;
  color: #999;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
}
.modal-close:hover {
  background: #e8e8e8;
  color: #666;
}
.modal-body {
  padding: 20px 24px 24px;
  overflow-y: auto;
}
.detail-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}
.detail-type {
  font-size: 12px;
  padding: 2px 10px;
  border-radius: 4px;
  font-weight: 500;
}
.detail-type.result {
  background: #e6f7ff;
  color: #1890ff;
}
.detail-type.system {
  background: #fff7e6;
  color: #fa8c16;
}
.detail-time {
  font-size: 13px;
  color: #bbb;
}
.detail-content {
  font-size: 14px;
  color: rgba(0,0,0,0.65);
  line-height: 1.8;
  white-space: pre-wrap;
  word-break: break-word;
}

/* 每页条数选择 */
.page-size-select {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #999;
  margin-right: 12px;
}
.page-size-select select {
  padding: 4px 8px;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  font-size: 13px;
  color: #666;
  background: white;
  cursor: pointer;
  outline: none;
}
.page-size-select select:focus {
  border-color: #1890ff;
}
.page-total-info {
  font-size: 13px;
  color: #999;
  margin-right: 8px;
}

/* ================= 响应式 ================= */
@media (max-width: 768px) {
  .messages-page { padding: 0; }
  .messages-header { padding: 12px 16px; flex-wrap: wrap; gap: 8px; }
  .header-title { font-size: 17px; }
  .back-btn { font-size: 13px; }
  .mark-all-btn { font-size: 12px; padding: 5px 10px; }
  .filter-tabs { padding: 0 16px; overflow-x: auto; flex-wrap: nowrap; gap: 0; }
  .filter-tab { flex-shrink: 0; padding: 10px 14px; font-size: 13px; }
  .message-card { padding: 14px; margin: 0 16px 10px; }
  .msg-title { font-size: 15px; }
  .msg-content { font-size: 13px; }
  .msg-time { font-size: 11px; }
  .pagination { flex-wrap: wrap; gap: 4px; padding: 16px; }
  .pagination button { padding: 4px 8px; font-size: 13px; min-width: 28px; }
  .page-size-select { margin-right: 0; }
  .page-total-info { width: 100%; text-align: center; margin-bottom: 8px; }
}

@media (max-width: 480px) {
  .messages-header { padding: 10px 12px; }
  .filter-tabs { padding: 0 12px; }
  .message-card { padding: 12px; margin: 0 12px 8px; }
  .msg-title { font-size: 14px; }
  .empty-state { padding: 40px 20px; }
  .empty-state svg { width: 36px; height: 36px; }
}
</style>
