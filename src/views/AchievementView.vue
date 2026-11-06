<template>
  <div class="achievement-center">
    <section class="search-section" :style="{ backgroundImage: `url(${require('@/assets/find.png')})` }">
      <div class="search-container">
        <input
          type="text"
          class="search-input"
          v-model="searchKeyword"
          placeholder="输入成果标题、机构名称或技术领域关键词..."
          @keyup.enter="handleSearch"
        />
        <button class="search-btn" @click="handleSearch">搜索</button>
      </div>
    </section>

    <div class="container">
      <!-- 筛选区域 -->
      <div class="filter-card">
        <div class="filter-card-header">
          <div class="filter-card-title">
            <span class="filter-dot"></span>筛选条件
            <span class="filter-badge" v-if="activeFilterCount > 0">{{ activeFilterCount }}</span>
          </div>
          <button class="filter-reset" @click="resetAllFilters">重置筛选</button>
        </div>
        <div class="filter-row" v-for="filter in filtersConfig" :key="filter.id">
          <div class="filter-label">{{ filter.name }}</div>
          <div class="filter-tags">
            <span
              v-for="option in filter.options"
              :key="option"
              class="filter-chip"
              :class="{ active: option === '全部' ? filterState[filter.id].length === 0 : filterState[filter.id].includes(option) }"
              @click="handleFilterClick(filter.id, option)"
            >{{ option }}</span>
          </div>
        </div>
        <div class="active-summary" v-if="activeFilterChips.length > 0 || searchKeyword">
          <span class="active-chip" v-if="searchKeyword" style="background:#fff7e6;color:#d48806">
            搜索：{{ searchKeyword }}
            <span class="active-chip-rm" @click="searchKeyword='';handleSearch()">&times;</span>
          </span>
          <span class="active-chip" v-for="chip in activeFilterChips" :key="chip.group + chip.option">
            {{ chip.option }}
            <span class="active-chip-rm" @click="removeFilter(chip.group, chip.option)">&times;</span>
          </span>
          <span class="active-clear" @click="resetAllFilters">清除全部</span>
        </div>
      </div>

      <!-- 成果列表 -->
      <section id="resultList">
        <!-- 加载状态 -->
        <div v-if="loading" class="loading-container" style="text-align: center; padding: 60px;">
          <div style="font-size: 16px; color: #666;">正在加载成果数据...</div>
        </div>

        <!-- 数据列表 -->
        <template v-else>
          <div class="achievement-card" v-for="achievement in paginatedAchievements" :key="achievement.id" @click="openDrawer(achievement.id)">
            <div class="card-accent"></div>
            <div class="card-body">
              <div class="card-header-row">
                <div class="card-title-area">
                  <span class="card-badge card-badge-id">{{ achievement.id }}</span>
                  <h3 class="card-title">{{ achievement.title }}</h3>
                  <span class="card-tag maturity-tag">{{ achievement.maturity }}</span>
                </div>
              </div>
              <div class="card-meta-grid">
                <div class="card-meta-field">
                  <span class="meta-label">持有人</span>
                  <span class="meta-value">{{ achievement.owner }}</span>
                </div>
                <div class="card-meta-field">
                  <span class="meta-label">技术领域</span>
                  <span class="meta-value">{{ achievement.field }}</span>
                </div>
                <div class="card-meta-field">
                  <span class="meta-label">转化方式</span>
                  <span class="meta-value">{{ achievement.transferDisplay }}</span>
                </div>
                <div class="card-meta-field">
                  <span class="meta-label">所在地区</span>
                  <span class="meta-value">{{ achievement.region || '未指定' }}</span>
                </div>
              </div>
            </div>
            <div class="card-actions">
              <button class="btn-action btn-primary" @click.stop="openDirectChat(achievement.title, achievement.id)">
                我要对接
              </button>
              <button class="btn-action btn-outline" @click.stop="openDrawer(achievement.id)">
                查看详情 →
              </button>
            </div>
          </div>

          <!-- 无数据提示 -->
          <div v-if="filteredAchievements.length === 0" style="text-align:center; padding:60px; color:#999; background:white; border-radius:8px; border: 1px solid #f0f0f0;">
            暂无符合条件的科技成果
          </div>
        </template>
      </section>

      <!-- 分页 -->
      <div class="pagination" v-if="filteredAchievements.length > 0">
        <a @click="changePage(-1)" :style="currentPage === 1 ? 'pointer-events:none;color:#ccc;' : ''">上一页</a>
        <a class="active">{{ currentPage }}</a>
        <a @click="changePage(1)" :style="currentPage === totalPages ? 'pointer-events:none;color:#ccc;' : ''">下一页</a>
        <span style="font-size:14px; color:#8c8c8c; margin-left:12px;">共 {{ filteredAchievements.length }} 条 / {{ totalPages }} 页</span>
      </div>
    </div>

    <!-- 抽屉详情 -->
    <div class="drawer-overlay" :class="{ active: showDrawer }" @click="closeDrawer"></div>
    <div class="drawer" :class="{ active: showDrawer }">
      <div class="drawer-header">
        <h2 class="drawer-title">成果详情</h2>
        <div class="drawer-close" @click="closeDrawer">&times;</div>
      </div>
      <div class="drawer-body">
        <fieldset class="form-section">
          <legend>一、成果基本信息</legend>
          <div class="form-grid">
            <div class="form-item full-width">
              <label>成果名称：</label>
              <span class="readonly-field" style="font-weight: bold; color: #2196f3;">{{ selectedAchievement.title || '-' }}</span>
            </div>
            <div class="form-item">
              <label>企业名称/持有人：</label>
              <span class="readonly-field">{{ selectedAchievement.owner || '-' }}</span>
            </div>
            <div class="form-item">
              <label>成果编号：</label>
              <span class="readonly-field">{{ selectedAchievement.id || '-' }}</span>
            </div>
            <div class="form-item">
              <label>技术领域：</label>
              <span class="readonly-field">{{ selectedAchievement.field || '-' }}</span>
            </div>
            <div class="form-item">
              <label>技术成熟度：</label>
              <span class="readonly-field" style="font-weight: bold; color: #2196f3;">{{ selectedAchievement.maturity || '-' }}</span>
            </div>
            <div class="form-item full-width">
              <label>拟转化方式：</label>
              <span class="readonly-field">{{ selectedAchievement.transferDisplay || '-' }}</span>
            </div>
          </div>
        </fieldset>

        <fieldset class="form-section">
          <legend>二、成果描述</legend>
          <div class="form-item full-width" style="margin-bottom: 15px;">
            <label>成果摘要：</label>
            <div class="readonly-field" style="height: auto;">{{ selectedAchievement.summary || '-' }}</div>
          </div>
          <div class="form-item full-width" style="margin-bottom: 15px;">
            <label>技术优势描述：</label>
            <div class="readonly-field" style="height: auto;">{{ selectedAchievement.advantage || '-' }}</div>
          </div>
          <div class="form-grid">
            <div class="form-item">
              <label>创新性评价：</label>
              <span class="readonly-field">{{ selectedAchievement.innovation || '-' }}</span>
            </div>
            <div class="form-item">
              <label>核心技术指标：</label>
              <span class="readonly-field">{{ selectedAchievement.indicator || '-' }}</span>
            </div>
            <div class="form-item full-width">
              <label>与现有技术相比的优势：</label>
              <div class="readonly-field" style="height: auto;">{{ selectedAchievement.compare || '-' }}</div>
            </div>
            <div class="form-item full-width">
              <label>获得的知识产权情况：</label>
              <div class="readonly-field" style="height: auto;">{{ selectedAchievement.ipr || '-' }}</div>
            </div>
          </div>
        </fieldset>

        <fieldset class="form-section">
          <legend>三、成果转化期望</legend>
          <div class="form-item full-width">
            <label>合作方式偏好及财务预期：</label>
            <span class="readonly-field" style="color: #faad14; font-weight: bold;">{{ selectedAchievement.collab || '-' }}</span>
          </div>
          <div class="form-item full-width">
            <label>期望完成转化时间：</label>
            <span class="readonly-field">{{ selectedAchievement.deadline || '-' }}</span>
          </div>
        </fieldset>
      </div>
      <div class="drawer-footer">
        <button class="contact-btn" style="width: 260px; height: 45px; font-size: 16px; font-weight: bold;" @click="handleDrawerContact">立即对接</button>
      </div>
    </div>

    <!-- 客服对话窗口 -->
    <div id="chatModal" class="modal" v-show="showChatModal">
      <div class="modal-content">
        <div class="chat-header">
          <h3>在线对接咨询</h3>
          <span class="close" @click="closeChatModal">&times;</span>
        </div>
        <div class="chat-body" ref="chatWindow">
          <div class="msg kefu" v-if="chatMessages.length === 0">
            <div class="bubble">
              您好！我是对接专员，请问您对<b>【{{ currentTargetFruit || '该成果' }}】</b>的哪方面最感兴趣？<br><br>
              1. 核心技术指标<br>
              2. 知识产权现状<br>
              3. 期望合作模式与价格<br>
              您可以回复序号，或直接输入您的疑问。
            </div>
          </div>
          <div class="msg" :class="msg.type" v-for="(msg, index) in chatMessages" :key="index">
            <div class="bubble">{{ msg.text }}</div>
          </div>
        </div>
        <div class="chat-footer">
          <input
            type="text"
            v-model="chatInput"
            @keyup.enter="sendMsg"
            placeholder="请输入内容..."
          />
          <button @click="sendMsg">发送</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, nextTick, inject } from 'vue'
import { useRoute } from 'vue-router'
import request from '@/utils/request'
import useAuth from '@/composables/useAuth'

export default {
  name: 'AchievementView',
  setup() {
    // 获取全局打开聊天函数
    const globalOpenChat = inject('globalOpenChat')
    const auth = useAuth()
    const route = useRoute()

    // 搜索关键词
    const searchKeyword = ref('')

    // 筛选配置
    const filtersConfig = [
      {
        id: 'field',
        name: '技术领域',
        options: ['全部', '新一代信息技术', '生物医药与健康', '航空航天', '新材料', '高技术服务', '新能源与节能', '资源与环境', '先进制造与自动化', '现代农业', '海洋技术', '其他']
      },
      {
        id: 'maturity',
        name: '成熟度',
        options: ['全部', '实验室理论阶段', '中试阶段', '可规模量产']
      },
      {
        id: 'transfer',
        name: '拟转化方式',
        options: ['全部', '技术转让', '技术许可', '技术入股', '合作开发', '其他']
      }
    ]

    // 筛选状态
    const filterState = ref({
      field: ['全部'],
      maturity: ['全部'],
      transfer: ['全部']
    })

    // 成果数据（从后端API获取）
    const allAchievements = ref([])
    const loading = ref(false)

    // 格式化带"其他"的字段
    const formatFieldWithOther = (fields, other) => {
      const arr = Array.isArray(fields) ? fields.filter(f => f !== '其他') : []
      let result = arr.join('、')
      if (other && other.trim()) {
        result += (result ? '、' : '') + `其他：${other}`
      }
      return result || '其他'
    }

    // 构建筛选用的字段数组（包含"其他"的自定义内容）
    const buildFieldArray = (fields, other) => {
      const arr = Array.isArray(fields) ? fields.filter(f => f !== '其他') : []
      if (other && other.trim()) {
        arr.push(other)
      }
      return arr
    }

    // 格式化转化偏好信息
    const formatTransferPreference = (preference) => {
      if (!preference) return '未指定'

      const parts = []
      if (preference.preferred_method) {
        parts.push(preference.preferred_method)
      }

      // 检查各种转化方式的预期费用
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
    }

    // 格式化期望完成时间
    const formatExpectedCompleteDate = (dateObj) => {
      if (!dateObj || !dateObj.year) return null
      if (dateObj.month) {
        return `${dateObj.year}年${dateObj.month}月`
      }
      return `${dateObj.year}年`
    }


    // 从后端API获取所有已审核的成果
    const fetchAchievements = async () => {
      loading.value = true
      try {
        const response = await request.get('/api/publish/public/achievements/center', {
          params: {
            limit: 100  // 获取足够多的数据，以便前端分页和筛选
          }
        })

        console.log('API响应:', response)
        if (response.code === 200 && response.data) {
          console.log('原始数据项示例:', response.data[0])
          // 转换数据格式，匹配前端模板的字段名
          allAchievements.value = response.data.map(item => ({
            id: item.achievement_code,  // 使用成果编号作为ID
            title: item.achievement_name,
            field: formatFieldWithOther(item.tech_fields, item.tech_fields_other),
            fieldArray: buildFieldArray(item.tech_fields, item.tech_fields_other),
            type: '科技成果', // 默认类型
            maturity: item.tech_maturity || '未知',
            transfer: Array.isArray(item.transfer_methods) ? item.transfer_methods : (item.transfer_methods ? [item.transfer_methods] : []), // 转化方式数组
            transferDisplay: formatFieldWithOther(item.transfer_methods, item.transfer_methods_other) || '未指定',
            owner: item.owner || '未知',
            region: item.region || '', // API返回的是字符串，不是对象
            summary: item.summary || '',
            advantage: item.advantages || '',
            innovation: item.innovation_level || '',
            compare: item.advantages || '', // 用优势描述作为比较
            indicator: item.core_indicators || '',
            ipr: item.intellectual_property || '',
            collab: formatTransferPreference(item.transfer_preference),
            deadline: formatExpectedCompleteDate(item.transfer_preference?.expected_complete_date) || '未指定'
          }))
        }
      } catch (error) {
        console.error('获取成果数据失败:', error)
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      fetchAchievements()
    })

    // 分页相关
    const pageSize = 5
    const currentPage = ref(1)

    // 抽屉相关
    const showDrawer = ref(false)
    const selectedAchievement = ref({})

    // 聊天相关
    const showChatModal = ref(false)
    const chatInput = ref('')
    const chatMessages = ref([])
    const chatWindow = ref(null)
    const currentTargetFruit = ref('')

    // 处理筛选点击
    const handleFilterClick = (key, option) => {
      const state = filterState.value[key]

      if (option === '全部') {
        filterState.value[key] = ['全部']
      } else {
        const allIndex = state.indexOf('全部')
        if (allIndex > -1) {
          state.splice(allIndex, 1)
        }

        const optionIndex = state.indexOf(option)
        if (optionIndex > -1) {
          state.splice(optionIndex, 1)
          if (state.length === 0) {
            filterState.value[key] = ['全部']
          }
        } else {
          state.push(option)
        }
      }

      currentPage.value = 1
    }

    // 筛选统计
    const activeFilterCount = computed(() => {
      let count = 0
      filtersConfig.forEach(f => {
        const s = filterState.value[f.id]
        if (s && !s.includes('全部')) count += s.length
      })
      if (searchKeyword.value.trim()) count++
      return count
    })
    const activeFilterChips = computed(() => {
      const chips = []
      filtersConfig.forEach(f => {
        const s = filterState.value[f.id]
        if (s && !s.includes('全部')) {
          s.forEach(opt => chips.push({ group: f.id, option: opt }))
        }
      })
      return chips
    })
    const removeFilter = (groupId, option) => {
      const s = filterState.value[groupId]
      const idx = s.indexOf(option)
      if (idx >= 0) s.splice(idx, 1)
      if (s.length === 0) filterState.value[groupId] = ['全部']
      currentPage.value = 1
    }
    const resetAllFilters = () => {
      filtersConfig.forEach(f => { filterState.value[f.id] = ['全部'] })
      searchKeyword.value = ''
      currentPage.value = 1
    }

    // 处理搜索
    const handleSearch = () => {
      currentPage.value = 1
    }

    // 分页改变
    const changePage = (delta) => {
      const total = totalPages.value
      if (currentPage.value + delta >= 1 && currentPage.value + delta <= total) {
        currentPage.value += delta
        window.scrollTo({ top: 300, behavior: 'smooth' })
      }
    }

    // 打开抽屉详情
    const openDrawer = (id) => {
      if (!auth.isLoggedIn.value) {
        auth.openLoginPrompt(route.fullPath)
        return
      }
      const achievement = allAchievements.value.find(item => item.id === id)
      if (achievement) {
        selectedAchievement.value = { ...achievement }
        currentTargetFruit.value = achievement.title
        showDrawer.value = true
      }
    }

    const closeDrawer = () => {
      showDrawer.value = false
    }

    // 抽屉内对接 — 打开客服小窗（浮于抽屉上方）
    const handleDrawerContact = () => {
      if (!auth.isLoggedIn.value) {
        showDrawer.value = false
        auth.openLoginPrompt(route.fullPath)
        return
      }
      if (!auth.requireVerified()) {
        return
      }
      const id = selectedAchievement.value.id
      if (globalOpenChat) {
        globalOpenChat('achievement', id)
      } else {
        openChatModal()
      }
    }

    // 直接打开聊天
    const openDirectChat = (title, id) => {
      if (!auth.isLoggedIn.value) {
        auth.openLoginPrompt(route.fullPath)
        return
      }
      if (!auth.requireVerified()) {
        return
      }
      currentTargetFruit.value = title
      if (globalOpenChat) {
        globalOpenChat('achievement', id)
      } else {
        openChatModal()
      }
    }

    // 聊天功能
    const openChatModal = () => {
      showChatModal.value = true
      chatMessages.value = []
      nextTick(() => {
        if (chatWindow.value) {
          chatWindow.value.scrollTop = chatWindow.value.scrollHeight
        }
      })
    }

    const closeChatModal = () => {
      showChatModal.value = false
      chatInput.value = ''
    }

    const sendMsg = () => {
      const val = chatInput.value.trim()
      if (!val) return

      chatMessages.value.push({ text: val, type: 'user' })
      chatInput.value = ''

      nextTick(() => {
        if (chatWindow.value) {
          chatWindow.value.scrollTop = chatWindow.value.scrollHeight
        }
      })

      setTimeout(() => {
        let reply = ""
        if (val === "1" || val.includes("指标")) {
          reply = "该成果的技术参数均已通过第三方验证：响应时间<2s，精准度>95%。若想深入了解请问【2.产权现状】。"
        } else if (val === "2" || val.includes("产权")) {
          reply = "产权情况明晰：目前该成果已获得国家发明专利授权 2 项，无任何权属纠纷。"
        } else if (val === "3" || val.includes("合作") || val.includes("钱") || val.includes("价格")) {
          reply = "对方倾向于【技术转让或排他性技术许可】，预期落地费用在 100-300 万元不等。需要帮您呼叫人工经纪人深入沟通吗？"
        } else if (val.includes("人工")) {
          reply = "系统提示：正在为您转接人工技术经纪人... <br>当前排队人数：2。请稍候，工作人员马上为您深度解答。"
        } else {
          reply = "已收到您的对接意向。稍后将由专属技术经理通过预留电话与您联系，请保持通讯畅通。"
        }

        chatMessages.value.push({ text: reply, type: 'kefu' })
        nextTick(() => {
          if (chatWindow.value) {
            chatWindow.value.scrollTop = chatWindow.value.scrollHeight
          }
        })
      }, 600)
    }

    // 计算过滤后的成果
    const filteredAchievements = computed(() => {
      const kw = searchKeyword.value.trim().toLowerCase()

      return allAchievements.value.filter(d => {
        const matchField = filterState.value.field.includes('全部') || filterState.value.field.includes(d.field)
        const matchMat = filterState.value.maturity.includes('全部') || filterState.value.maturity.includes(d.maturity)
        const matchTrans = filterState.value.transfer.includes('全部') ||
          (Array.isArray(d.transfer) && d.transfer.some(t => filterState.value.transfer.includes(t)))
        const matchKw = d.title.toLowerCase().includes(kw) || d.owner.toLowerCase().includes(kw) || d.indicator.toLowerCase().includes(kw)

        return matchField && matchMat && matchTrans && matchKw
      })
    })

    // 计算分页后的成果
    const paginatedAchievements = computed(() => {
      const start = (currentPage.value - 1) * pageSize
      const end = start + pageSize
      return filteredAchievements.value.slice(start, end)
    })

    // 计算总页数
    const totalPages = computed(() => {
      return Math.ceil(filteredAchievements.value.length / pageSize) || 1
    })

    return {
      searchKeyword,
      filtersConfig,
      filterState,
      paginatedAchievements,
      filteredAchievements,
      currentPage,
      totalPages,
      showDrawer,
      selectedAchievement,
      showChatModal,
      chatInput,
      chatMessages,
      chatWindow,
      currentTargetFruit,
      loading,
      allAchievements,

      activeFilterCount,
      activeFilterChips,
      removeFilter,
      resetAllFilters,
      handleFilterClick,
      handleSearch,
      changePage,
      openDrawer,
      closeDrawer,
      handleDrawerContact,
      openDirectChat,
      openChatModal,
      closeChatModal,
      sendMsg
    }
  }
}
</script>

<style scoped>
/* ================= 全局样式重置 ================= */
.achievement-center * {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.achievement-center {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  background-color: #f5f5f5;
  color: #333;
  line-height: 1.6;
  min-height: 100vh;
  padding-bottom: 40px;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px 0;
}

/* ================= 搜索区域 ================= */
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

/* ================= 筛选区域 ================= */
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
.filter-badge {
  font-size: 12px; color: #1890ff; background: #e6f7ff;
  padding: 2px 10px; border-radius: 10px; font-weight: 500;
}
.filter-reset {
  font-size: 13px; color: #999; background: none; border: 1px solid #e0e0e0;
  padding: 5px 14px; border-radius: 16px; cursor: pointer;
  transition: all 0.2s;
}
.filter-reset:hover { color: #ff4d4f; border-color: #ff4d4f; }
.filter-row {
  display: flex; align-items: flex-start; gap: 12px;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px dashed #f0f0f0;
}
.filter-row:last-of-type { border-bottom: none; }
.filter-label {
  width: 90px; flex-shrink: 0;
  font-size: 13px; font-weight: 600; color: #666;
  padding-top: 5px;
}
.filter-tags {
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

/* ================= 成果列表卡片 ================= */
.achievement-card {
  background: #ffffff;
  border-radius: 12px;
  margin-bottom: 16px;
  border: 1px solid #e8e8e8;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  display: flex;
  overflow: hidden;
  position: relative;
}
.achievement-card:hover {
  box-shadow: 0 8px 24px rgba(24, 144, 255, 0.12);
  border-color: #1890ff;
  transform: translateY(-3px);
}

/* 左侧彩色装饰条 */
.achievement-card .card-accent {
  width: 4px;
  flex-shrink: 0;
  background: linear-gradient(180deg, #1890ff, #69c0ff);
}

/* 卡片主体 */
.achievement-card .card-body {
  flex: 1;
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-width: 0;
}

/* 标题行 */
.achievement-card .card-header-row {
  display: flex;
  align-items: center;
  gap: 12px;
}
.achievement-card .card-title-area {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}
.achievement-card .card-title {
  font-size: 17px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: 1.4;
}
.achievement-card:hover .card-title {
  color: #1890ff;
}

/* 编号徽章 */
.achievement-card .card-badge-id {
  flex-shrink: 0;
  display: inline-block;
  padding: 2px 10px;
  background: #f0f5ff;
  color: #1890ff;
  border: 1px solid #d6e4ff;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.3px;
}

/* 成熟度标签 */
.achievement-card .maturity-tag {
  flex-shrink: 0;
  padding: 4px 14px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
  background: linear-gradient(135deg, #e6f7ff 0%, #bae7ff 100%);
  color: #0050b3;
  border: 1px solid #91d5ff;
}

/* 元数据网格 */
.achievement-card .card-meta-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px 24px;
}
.achievement-card .card-meta-field {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  line-height: 1.5;
  padding: 3px 0;
  border-bottom: 1px dashed #f0f0f0;
}
.achievement-card .card-meta-field:last-child:nth-child(odd) {
  grid-column: 1 / 2;
}
.achievement-card .meta-label {
  color: #8c8c8c;
  flex-shrink: 0;
  min-width: 5em;
  letter-spacing: 0.5px;
}
.achievement-card .meta-value {
  color: #262626;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 操作按钮区域 */
.achievement-card .card-actions {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 8px;
  padding: 20px 24px 20px 0;
  flex-shrink: 0;
}
.achievement-card .btn-action {
  padding: 8px 20px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.25s;
  white-space: nowrap;
  border: none;
  outline: none;
}
.achievement-card .btn-primary {
  background: linear-gradient(135deg, #1890ff, #096dd9);
  color: white;
  box-shadow: 0 2px 6px rgba(24, 144, 255, 0.3);
}
.achievement-card .btn-primary:hover {
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.45);
  transform: translateY(-1px);
}
.achievement-card .btn-outline {
  background: white;
  color: #1890ff;
  border: 1px solid #1890ff;
}
.achievement-card .btn-outline:hover {
  background: #f0f7ff;
  border-color: #096dd9;
  color: #096dd9;
}
.contact-btn {
  padding: 8px 16px;
  background: #1890ff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.3s;
}
.contact-btn:hover { background: #096dd9; }

/* ================= 分页 ================= */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 40px;
  gap: 8px;
  font-size: 14px;
}
.pagination a {
  padding: 6px 14px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  cursor: pointer;
  transition: 0.3s;
  font-size: 14px;
  background: white;
  color: #595959;
}
.pagination a:hover {
  color: #1890ff;
  border-color: #1890ff;
}
.pagination a.active {
  background: #1890ff;
  color: white;
  border-color: #1890ff;
  pointer-events: none;
}

/* ================= 按需更新抽屉样式为需求中心样式 ================= */
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

.btn-submit-large {
  padding: 9px;
  background: #2196f3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background 0.3s;
  width: 100%;
  max-width: 300px;
  height: 44px;
}
.btn-submit-large:hover {
  background: #0076e4;
}

/* ================= 响应式 ================= */
@media (max-width: 1024px) {
  .search-section {
    padding: 35px 16px 40px;
    margin: 16px auto 12px;
  }
  .container {
    padding: 16px 0;
  }
  .search-input { font-size: 14px; }
  .filter-card { padding: 16px 16px 3px; }
  .filter-row { flex-direction: column; gap: 8px; }
  .filter-label { width: auto; }
}

@media (max-width: 768px) {
  .achievement-center { padding-bottom: 24px; }
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
  .achievement-card {
    flex-direction: column;
  }
  .achievement-card .card-body {
    padding: 16px;
  }
  .achievement-card .card-title {
    font-size: 16px;
  }
  .achievement-card .card-header-row {
    flex-wrap: wrap;
  }
  .achievement-card .card-meta-grid {
    grid-template-columns: 1fr;
    gap: 4px;
  }
  .achievement-card .card-actions {
    flex-direction: row;
    padding: 0 16px 16px;
    gap: 8px;
  }
  .achievement-card .btn-action {
    flex: 1;
    text-align: center;
    font-size: 13px;
    padding: 8px 12px;
  }
  .achievement-card .card-accent {
    width: 100%;
    height: 3px;
  }
  .filter-card { padding: 12px 12px 3px; }
  .filter-chip { padding: 4px 12px; font-size: 12px; }
  .filter-row { gap: 6px; }
  .pagination { flex-wrap: wrap; gap: 6px; }
  .pagination a { padding: 4px 10px; font-size: 13px; }

  /* 抽屉全屏 */
  .drawer { width: 100vw !important; left: -100vw !important; }
  .drawer-header { padding: 16px 20px; }
  .drawer-title { font-size: 17px; }
  .drawer-body { padding: 16px; }
  .drawer-footer { padding: 16px 20px; }
  .form-section { padding: 14px; }
  .form-grid { grid-template-columns: 1fr !important; gap: 12px; }

  /* 客服弹窗适应手机 */
  .modal-content { width: calc(100vw - 32px) !important; height: 60vh !important; }
  .modal { right: 16px !important; bottom: 16px !important; }
}

@media (max-width: 480px) {
  .search-section { padding: 22px 12px 27px; }
  .search-container { max-width: 100%; }
  .achievement-card .card-body { padding: 14px; }
  .achievement-card .card-title { font-size: 15px; }
  .achievement-card .card-meta-item { font-size: 12px; padding: 3px 8px; }
  .filter-chip { font-size: 11px; padding: 3px 10px; }
  .btn-submit-large { max-width: 100%; }
}

/* ================= 客服对话窗口 ================= */
.modal {
  position: fixed;
  z-index: 2000;
  bottom: 20px;
  right: 20px;
  background: transparent;
  display: none;
}
.modal.active {
  display: block;
}
.modal-content {
  background: white;
  width: 380px;
  height: 500px;
  border-radius: 12px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.15);
  border: 1px solid #e0e0e0;
  animation: slideUp 0.3s ease-out;
}
@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
.chat-header {
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #f0f0f0;
  background: #fff;
}
.chat-header h3 {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  margin: 0;
}
.chat-header .close {
  font-size: 22px;
  cursor: pointer;
  color: #999;
  line-height: 1;
}
.chat-header .close:hover {
  color: #f5222d;
}
.chat-body {
  flex: 1;
  background: #f9f9f9;
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.msg {
  display: flex;
  max-width: 85%;
  flex-direction: column;
}
.msg.kefu {
  align-self: flex-start;
}
.msg.user {
  align-self: flex-end;
}
.bubble {
  padding: 10px 14px;
  border-radius: 4px;
  font-size: 14px;
  line-height: 1.5;
  word-break: break-word;
}
.msg.kefu .bubble {
  background: #e6f7ff;
  border: 1px solid #91d5ff;
  color: #333;
}
.msg.user .bubble {
  background: #1890ff;
  color: white;
  border: 1px solid #1890ff;
}
.chat-footer {
  padding: 16px 20px;
  background: white;
  border-top: 1px solid #f0f0f0;
  display: flex;
  gap: 12px;
}
.chat-footer input {
  flex: 1;
  padding: 10px 14px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  outline: none;
  font-size: 14px;
}
.chat-footer input:focus {
  border-color: #1890ff;
}
.chat-footer button {
  padding: 0 24px;
  background: #1890ff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: bold;
}
.chat-footer button:hover {
  background: #40a9ff;
}
</style>
