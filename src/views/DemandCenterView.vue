<template>
  <div class="demand-center">
    <!-- 搜索区域 -->
    <section class="search-section" :style="{ backgroundImage: `url(${require('@/assets/find.png')})` }">
      <div class="search-container">
        <input type="text" class="search-input" placeholder="输入需求标题、机构名称或应用领域关键词..." v-model="searchKeyword" @keyup.enter="handleSearch">
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
            <!-- 常规平铺筛选（无分组） -->
            <template v-if="!filter.groups">
              <span
                v-for="option in filter.options"
                :key="option"
                class="filter-chip"
                :class="{ active: option === '全部' ? filterState[filter.id].length === 0 : filterState[filter.id].includes(option) }"
                @click="handleFilterClick(filter.id, option)"
              >{{ option }}</span>
            </template>
            <!-- 二级分类筛选（应用领域，可展开） -->
            <template v-else>
              <div class="filter-group-wrapper">
                <!-- 全部（始终内联） -->
                <span
                  class="filter-chip"
                  :class="{ active: filterState[filter.id].length === 0 }"
                  @click="handleFilterClick(filter.id, '全部')"
                >全部</span>
                <!-- 一级分类：收起时内联chip，展开时隐藏 -->
                <template v-for="(group, gi) in filter.groups" :key="'chip-'+gi">
                  <span v-if="!expandedGroups[group.label]"
                    class="filter-chip filter-chip-primary"
                    @click="toggleGroup(group.label)"
                  >
                    {{ group.label }}
                    <span class="expand-icon">+</span>
                  </span>
                </template>
                <!-- 展开区域：全宽panel，header在左上角 -->
                <template v-for="(group, gi) in filter.groups" :key="'exp-'+gi">
                  <Transition name="expand">
                    <div v-if="expandedGroups[group.label]" class="filter-expanded-section">
                      <div class="filter-expanded-header" @click="toggleGroup(group.label)">
                        <span>{{ group.label }}</span>
                        <span class="expand-icon">−</span>
                      </div>
                      <div class="filter-sub-items">
                        <span
                          v-for="option in group.options"
                          :key="option"
                          class="filter-chip"
                          :class="{ active: filterState[filter.id].includes(option) }"
                          @click="handleFilterClick(filter.id, option)"
                        >{{ option }}</span>
                      </div>
                    </div>
                  </Transition>
                </template>
              </div>
            </template>
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

      <!-- 需求列表 -->
      <section class="demand-list">
        <!-- 加载状态 -->
        <div v-if="loading" class="loading-container" style="text-align: center; padding: 60px;">
          <div style="font-size: 16px; color: #666;">正在加载需求数据...</div>
        </div>

        <!-- 数据列表 -->
        <template v-else>
          <div class="demand-card" v-for="demand in paginatedDemands" :key="demand.id" @click="openDrawer(demand.id)">
            <div class="card-accent"></div>
            <div class="card-body">
              <div class="card-header-row">
                <div class="card-title-area">
                  <span class="card-badge card-badge-id">{{ demand.id }}</span>
                  <h3 class="card-title">{{ demand.title }}</h3>
                  <span class="card-tag" :class="'status-tag-' + (demand.status || '待对接')">{{ demand.status || '待对接' }}</span>
                </div>
              </div>
              <div class="card-meta-grid">
                <div class="card-meta-field">
                  <span class="meta-label">需求方</span>
                  <span class="meta-value">{{ demand.org }}</span>
                </div>
                <div class="card-meta-field">
                  <span class="meta-label">应用领域</span>
                  <span class="meta-value">{{ demand.field }}</span>
                </div>
                <div class="card-meta-field">
                  <span class="meta-label">需求类型</span>
                  <span class="meta-value">{{ demand.type }}</span>
                </div>
                <div class="card-meta-field">
                  <span class="meta-label">所在地区</span>
                  <span class="meta-value">{{ demand.region }}</span>
                </div>
              </div>
            </div>
            <div class="card-actions">
              <button class="btn-action btn-primary" @click.stop="openDirectChat(demand.title, demand.id)">
                我要对接
              </button>
              <button class="btn-action btn-outline" @click.stop="openDrawer(demand.id)">
                查看详情 →
              </button>
            </div>
          </div>

          <!-- 无数据提示 -->
          <div v-if="filteredDemands.length === 0" class="no-data">
            暂无匹配结果
          </div>
        </template>
      </section>

      <!-- 分页控件 -->
      <div class="pagination">
        <a @click="changePage(-1)">上一页</a>
        <a class="active">{{ currentPage }}</a>
        <a @click="changePage(1)">下一页</a>
        <span class="page-info">共 {{ totalPages }} 页</span>
      </div>
    </div>

    <!-- 抽屉详情 -->
    <div class="drawer-overlay" :class="{ active: showDrawer }" @click="closeDrawer"></div>
    <div class="drawer" :class="{ active: showDrawer }">
      <div class="drawer-header">
        <h2 class="drawer-title">需求详情</h2>
        <div class="drawer-close" @click="closeDrawer">&times;</div>
      </div>
      <div class="drawer-body">
        <fieldset class="form-section">
          <legend>一、需求基本信息</legend>
          <div class="form-grid">
            <div class="form-item full-width">
              <label>需求名称：</label>
              <span id="dt-title" class="readonly-field">{{ selectedDemand.title || '-' }}</span>
            </div>
            <div class="form-item">
              <label>企业名称：</label>
              <span id="dt-org" class="readonly-field">{{ selectedDemand.org || '-' }}</span>
            </div>
            <div class="form-item">
              <label>需求编号：</label>
              <span id="dt-id" class="readonly-field">{{ selectedDemand.id || '-' }}</span>
            </div>
            <div class="form-item">
              <label>所属地区：</label>
              <span id="dt-region" class="readonly-field">{{ selectedDemand.region || '-' }}</span>
            </div>
            <div class="form-item">
              <label>应用领域：</label>
              <span id="dt-field" class="readonly-field">{{ selectedDemand.field || '-' }}</span>
            </div>
            <div class="form-item">
              <label>需求类型：</label>
              <span id="dt-type" class="readonly-field">{{ selectedDemand.type || '-' }}</span>
            </div>
            <div class="form-item">
              <label>供需状态：</label>
              <span id="dt-status" class="readonly-field" style="font-weight: bold; color: #2196f3;">{{ selectedDemand.status || '-' }}</span>
            </div>
            <div class="form-item">
              <label>项目预算：</label>
              <span id="dt-budget" class="readonly-field">{{ selectedDemand.budget || '-' }}</span>
            </div>
          </div>
        </fieldset>

        <fieldset class="form-section">
          <legend>二、需求描述</legend>
          <div class="form-item full-width" style="margin-bottom: 15px;">
            <label>需求概述：</label>
            <div id="dt-overview" class="readonly-field" style="height: auto;">{{ selectedDemand.overview || '-' }}</div>
          </div>
          <div class="form-item full-width">
            <label>期望解决的问题：</label>
            <div id="dt-issues" class="readonly-field" style="height: auto;">{{ selectedDemand.issues || '-' }}</div>
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
        <div style="display:flex; justify-content:space-between; margin-bottom:15px;">
          <h3 style="font-size:16px;">在线对接咨询</h3>
          <span style="cursor:pointer; font-weight:bold;" @click="closeChatModal">&times;</span>
        </div>
        <div class="chat-window" ref="chatWindow">
          <div class="msg kefu" v-if="chatMessages.length === 0">
            <div>您好！我是对接专员，请问您对<b>【{{ currentTargetDemand || '该需求' }}】</b>的哪方面最感兴趣？<br><br>
              1. 技术解决方案<br>
              2. 实施周期与成本<br>
              3. 已有技术积累<br>
              您可以回复序号，或直接输入您的疑问。</div>
          </div>
          <div class="msg" :class="msg.type" v-for="(msg, index) in chatMessages" :key="index">
            {{ msg.text }}
          </div>
        </div>
        <div style="display:flex; gap:5px;">
          <input type="text" v-model="chatInput" @keyup.enter="sendChatMessage" style="flex:1; padding:8px; border:1px solid #ddd; border-radius:4px;" placeholder="请输入内容...">
          <button class="contact-btn" style="padding: 5px 15px;" @click="sendChatMessage">发送</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, nextTick, inject } from 'vue'
import { useRoute } from 'vue-router'
import request from '@/utils/request'
import useAuth from '@/composables/useAuth'

export default {
  name: 'DemandCenterView',
  setup() {
    // 获取全局打开聊天函数
    const globalOpenChat = inject('globalOpenChat')
    const auth = useAuth()
    const route = useRoute()

    // 搜索关键词
    const searchKeyword = ref('')

    // 筛选配置 [参考10.html lines 180-201]
    const filtersConfig = [
      {
        id: 'field',
        name: '应用领域',
        groups: [
          {
            label: '战略性新兴产业',
            options: ['节能环保产业', '新一代信息技术产业', '高端装备制造产业', '新能源产业', '新材料产业', '生物产业', '新能源汽车产业', '数字创意产业']
          },
          {
            label: '传统产业',
            options: ['农、林、牧、渔业', '采矿业', '制造业', '水利环境', '教育，医疗卫生', '文化、体育和娱乐', '电力、热力和燃气', '建筑业', '交通运输和仓储', '住宿和餐饮业', '信息传输、软件和信息技术服务业', '金融业', '房地产业', '新能源', '科学研究和技术服务']
          }
        ],
        options: ['全部', '节能环保产业', '新一代信息技术产业', '高端装备制造产业', '新能源产业', '新材料产业', '生物产业', '新能源汽车产业', '数字创意产业', '农、林、牧、渔业', '采矿业', '制造业', '水利环境', '教育，医疗卫生', '文化、体育和娱乐', '电力、热力和燃气', '建筑业', '交通运输和仓储', '住宿和餐饮业', '信息传输、软件和信息技术服务业', '金融业', '房地产业', '新能源', '科学研究和技术服务']
      },
      {
        id: 'type',
        name: '需求类型',
        options: ['全部', '技术需求', '金融需求', '场景需求', '其他']
      },
      {
        id: 'region',
        name: '所在地区',
        options: ['全部', '北京市', '天津市', '河北省', '山西省', '内蒙古自治区', '辽宁省', '吉林省', '黑龙江省', '上海市', '江苏省', '浙江省', '安徽省', '福建省', '江西省', '山东省', '河南省', '湖北省', '湖南省', '广东省', '广西壮族自治区', '海南省', '重庆市', '四川省', '贵州省', '云南省', '西藏自治区', '陕西省', '甘肃省', '青海省', '宁夏回族自治区', '新疆维吾尔自治区', '香港特别行政区', '澳门特别行政区', '台湾省']
      },
      {
        id: 'status',
        name: '供需状态',
        options: ['全部', '待对接', '对接中', '已完成']
      }
    ]

    // 筛选状态 [参考10.html line 208]
    const filterState = ref({
      field: ['全部'],
      type: ['全部'],
      region: ['全部'],
      status: ['全部']
    })

    // 应用领域一级分类展开状态（默认全部收起）
    const expandedGroups = reactive({
      '战略性新兴产业': false,
      '传统产业': false
    })
    const toggleGroup = (label) => {
      expandedGroups[label] = !expandedGroups[label]
    }

    // 需求数据（从后端API获取）
    const allDemands = ref([])
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

    // 构建筛选用的字段数组
    const buildFieldArray = (fields, other) => {
      const arr = Array.isArray(fields) ? fields.filter(f => f !== '其他') : []
      if (other && other.trim()) {
        arr.push(other)
      }
      return arr
    }

    // 从后端API获取所有已审核的需求
    const fetchDemands = async () => {
      loading.value = true
      try {
        const response = await request.get('/api/publish/public/requirements/center', {
          params: {
            limit: 100  // 获取足够多的数据，以便前端分页和筛选
          }
        })

        if (response.code === 200 && response.data) {
          // 转换数据格式，匹配前端模板的字段名
          allDemands.value = response.data.map(item => ({
            id: item.demand_code,  // 使用需求编号作为ID
            title: item.demand_name,
            field: formatFieldWithOther(item.tech_fields, item.tech_fields_other),
            fieldArray: buildFieldArray(item.tech_fields, item.tech_fields_other),
            region: item.region || '',
            type: formatFieldWithOther(item.demand_types, item.demand_types_other),
            typeArray: buildFieldArray(item.demand_types, item.demand_types_other),
            status: item.match_status || '待对接', // 供需状态（待对接/对接中/已完成）
            org: item.company_name || '未知',
            budget: item.budget ? `${item.budget}万元` : '未指定',
            overview: item.overview || '',
            issues: item.target_problems || ''
          }))
        }
      } catch (error) {
        console.error('获取需求数据失败:', error)
      } finally {
        loading.value = false
      }
    }

    // 分页相关
    const pageSize = 5
    const currentPage = ref(1)

    // 抽屉相关
    const showDrawer = ref(false)
    const selectedDemand = ref({})

    // 聊天相关
    const showChatModal = ref(false)
    const chatInput = ref('')
    const chatMessages = ref([])
    const chatWindow = ref(null)
    const currentTargetDemand = ref('')

    // 处理筛选点击 [参考10.html lines 226-240]
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

    // 处理搜索 [参考10.html line 311]
    const handleSearch = () => {
      currentPage.value = 1
    }

    // 分页改变 [参考10.html lines 312-315]
    const changePage = (delta) => {
      const total = totalPages.value
      if (currentPage.value + delta >= 1 && currentPage.value + delta <= total) {
        currentPage.value += delta
      }
    }

    // 打开抽屉详情 [参考10.html lines 289-304]
    const openDrawer = (id) => {
      if (!auth.isLoggedIn.value) {
        auth.openLoginPrompt(route.fullPath)
        return
      }
      const demand = allDemands.value.find(item => item.id === id)
      if (demand) {
        selectedDemand.value = { ...demand }
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
      const id = selectedDemand.value.id
      if (globalOpenChat) {
        globalOpenChat('demand', id)
      } else {
        openDirectChat(selectedDemand.value.title)
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
      currentTargetDemand.value = title
      if (globalOpenChat) {
        globalOpenChat('demand', id)
      } else {
        openChatModal()
      }
    }

    // 聊天功能 [参考10.html lines 323-334]
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

    const sendChatMessage = () => {
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
        if (val === "1" || val.includes("方案") || val.includes("解决")) {
          reply = "该需求已明确技术路线：采用模块化架构，核心算法成熟度≥90%。需详细沟通可问【2.实施周期】。"
        } else if (val === "2" || val.includes("周期") || val.includes("成本") || val.includes("时间")) {
          reply = "典型实施周期：3-6个月（含测试验收），总预算范围在50-200万元。具体根据定制化程度浮动。"
        } else if (val === "3" || val.includes("积累") || val.includes("经验") || val.includes("技术")) {
          reply = "我们已梳理匹配供应商库：5家上市公司+12家专精特新企业具备同类项目经验，平均案例数≥3个。需要帮您转接人工项目经理吗？"
        } else if (val.includes("人工") || val.includes("经理") || val.includes("专")) {
          reply = "系统提示：正在为您转接人工项目经理... <br>当前排队人数：1。请稍候，工作人员马上为您深度解答。"
        } else {
          reply = "已收到您的对接意向。稍后将由专属项目经理通过预留电话与您联系，请保持通讯畅通。"
        }

        chatMessages.value.push({ text: reply, type: 'kefu' })
        nextTick(() => {
          if (chatWindow.value) {
            chatWindow.value.scrollTop = chatWindow.value.scrollHeight
          }
        })
      }, 600)
    }

    // 计算过滤后的需求 [参考10.html lines 242-251]
    const filteredDemands = computed(() => {
      const kw = searchKeyword.value.trim().toLowerCase()

      return allDemands.value.filter(d => {
        // 技术领域筛选（支持数组）
        const matchField = filterState.value.field.includes('全部') ||
          (Array.isArray(d.fieldArray) && d.fieldArray.some(f => filterState.value.field.includes(f)))

        // 需求类型筛选（支持数组）
        const matchType = filterState.value.type.includes('全部') ||
          (Array.isArray(d.typeArray) && d.typeArray.some(t => filterState.value.type.includes(t)))

        // 地区筛选
        const matchRegion = filterState.value.region.includes('全部') ||
          filterState.value.region.some(r => d.region.includes(r.replace(/省|市|自治区|特别行政区/g, '')))

        // 状态筛选（后端没有状态字段，但保留筛选器结构）
        const matchStatus = filterState.value.status.includes('全部') || filterState.value.status.includes(d.status)

        // 关键词搜索（支持搜索技术领域数组）
        const matchKw = d.title.toLowerCase().includes(kw) ||
                      d.org.toLowerCase().includes(kw) ||
                      (Array.isArray(d.fieldArray) && d.fieldArray.some(f => f.toLowerCase().includes(kw))) ||
                      d.region.toLowerCase().includes(kw)

        return matchField && matchType && matchRegion && matchStatus && matchKw
      })
    })

    // 计算分页后的需求 [参考10.html line 253]
    const paginatedDemands = computed(() => {
      const start = (currentPage.value - 1) * pageSize
      const end = start + pageSize
      return filteredDemands.value.slice(start, end)
    })

    // 计算总页数
    const totalPages = computed(() => {
      return Math.ceil(filteredDemands.value.length / pageSize) || 1
    })

    onMounted(() => {
      console.log('需求中心页面加载完成')
      fetchDemands()
    })

    return {
      // 数据
      searchKeyword,
      filtersConfig,
      filterState,
      paginatedDemands,
      filteredDemands,
      currentPage,
      totalPages,
      showDrawer,
      selectedDemand,
      showChatModal,
      chatInput,
      chatMessages,
      chatWindow,
      currentTargetDemand,
      loading,
      allDemands,

      // 方法
      activeFilterCount,
      activeFilterChips,
      removeFilter,
      resetAllFilters,
      handleFilterClick,
      handleSearch,
      changePage,
      toggleGroup,
      expandedGroups,
      openDrawer,
      closeDrawer,
      handleDrawerContact,
      openDirectChat,
      openChatModal,
      closeChatModal,
      sendChatMessage
    }
  }
}
</script>

<style scoped>
/* ================= 全局样式重置 ================= */
.demand-center * { margin: 0; padding: 0; box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif; }
.demand-center body { background-color: #f5f5f5; color: #333; line-height: 1.6; min-height: 100vh; padding-bottom: 40px; }
.demand-center a { text-decoration: none; color: inherit; cursor: pointer; }
.demand-center ul, .demand-center li { list-style: none; }

.container { max-width: 1200px; margin: 0 auto; padding: 20px 0; }

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
.filter-group-wrapper {
  width: 100%;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.filter-chip-primary {
  background: #f0f9ff;
  border-color: #91d5ff;
  color: #1890ff;
  font-weight: 500;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
.filter-chip-primary:hover {
  background: #e6f7ff;
  border-color: #69c0ff;
  color: #096dd9;
}
.expand-icon {
  font-size: 14px;
  font-weight: 500;
  color: #69c0ff;
  line-height: 1;
  margin-left: 2px;
}
.filter-expanded-section {
  width: 100%;
  margin: 8px 0 0;
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.filter-expanded-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  background: #fafafa;
  font-size: 13px;
  font-weight: 600;
  color: #1890ff;
  cursor: pointer;
  user-select: none;
  border-bottom: 1px solid #f0f0f0;
  transition: background 0.2s;
}
.filter-expanded-header:hover {
  background: #f0f9ff;
}
.filter-expanded-header .expand-icon {
  color: #1890ff;
  font-weight: 600;
}
.filter-sub-items {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 12px 16px;
}
/* 展开/收缩动画 */
.expand-enter-active {
  animation: expandIn 0.3s ease-out;
}
.expand-leave-active {
  animation: expandIn 0.25s ease-in reverse;
}
@keyframes expandIn {
  0% {
    opacity: 0;
    max-height: 0;
    transform: translateY(-8px);
  }
  100% {
    opacity: 1;
    max-height: 500px;
    transform: translateY(0);
  }
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

/* ================= 需求列表卡片 ================= */
.demand-card {
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
.demand-card:hover {
  box-shadow: 0 8px 24px rgba(82, 196, 26, 0.12);
  border-color: #52c41a;
  transform: translateY(-3px);
}
.demand-card .card-accent {
  width: 4px;
  flex-shrink: 0;
  background: linear-gradient(180deg, #52c41a, #95de64);
}
.demand-card .card-body {
  flex: 1;
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-width: 0;
}
.demand-card .card-header-row {
  display: flex;
  align-items: center;
  gap: 12px;
}
.demand-card .card-title-area {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}
.demand-card .card-title {
  font-size: 17px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: 1.4;
}
.demand-card:hover .card-title {
  color: #52c41a;
}
.demand-card .card-badge-id {
  flex-shrink: 0;
  display: inline-block;
  padding: 2px 10px;
  background: #f6ffed;
  color: #52c41a;
  border: 1px solid #b7eb8f;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.3px;
}
.demand-card .status-tag-待对接 {
  flex-shrink: 0;
  padding: 4px 14px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
  background: linear-gradient(135deg, #fff7e6 0%, #ffe58f 100%);
  color: #ad6800;
  border: 1px solid #ffd666;
}
.demand-card .status-tag-对接中 {
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
.demand-card .status-tag-已完成 {
  flex-shrink: 0;
  padding: 4px 14px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
  background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
  color: #2e7d32;
  border: 1px solid #a5d6a7;
}
.demand-card .card-meta-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px 24px;
}
.demand-card .card-meta-field {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  line-height: 1.5;
  padding: 3px 0;
  border-bottom: 1px dashed #f0f0f0;
}
.demand-card .card-meta-field:last-child:nth-child(odd) {
  grid-column: 1 / 2;
}
.demand-card .meta-label {
  color: #8c8c8c;
  flex-shrink: 0;
  min-width: 5em;
  letter-spacing: 0.5px;
}
.demand-card .meta-value {
  color: #262626;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.demand-card .card-budget-row {
  margin-top: 2px;
}
.demand-card .budget-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 14px;
  background: #fffbe6;
  border: 1px solid #ffe58f;
  border-radius: 6px;
  font-size: 13px;
  color: #ad6800;
}
.demand-card .budget-tag strong {
  font-size: 15px;
  color: #d48806;
}
.demand-card .card-actions {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 8px;
  padding: 20px 24px 20px 0;
  flex-shrink: 0;
}
.demand-card .btn-action {
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
.demand-card .btn-primary {
  background: linear-gradient(135deg, #1890ff, #096dd9);
  color: white;
  box-shadow: 0 2px 6px rgba(24, 144, 255, 0.3);
}
.demand-card .btn-primary:hover {
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.45);
  transform: translateY(-1px);
}
.demand-card .btn-outline {
  background: white;
  color: #1890ff;
  border: 1px solid #1890ff;
}
.demand-card .btn-outline:hover {
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

.no-data {
  text-align: center;
  padding: 40px;
  color: #999;
  background: white;
  border-radius: 8px;
  font-size: 16px;
}

/* ================= 分页 ================= */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 30px;
  gap: 10px;
}
.pagination a {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  transition: 0.3s;
  font-size: 14px;
}
.pagination a:hover {
  background-color: #f8f9fa;
}
.pagination a.active {
  background: #2196f3;
  color: white;
  border-color: #2196f3;
}
.page-info {
  font-size: 14px;
  color: #666;
  margin-left: 10px;
}

/* ================= 抽屉(Drawer) 左侧弹出 ================= */
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

/* ================= 客服对话 ================= */
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
.chat-window {
  flex: 1;
  border: 1px solid #eee;
  overflow-y: auto;
  padding: 20px;
  background: #f9f9f9;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.msg {
  padding: 8px 12px;
  border-radius: 4px;
  max-width: 80%;
  font-size: 14px;
}
.msg.kefu {
  background: #e3f2fd;
  align-self: flex-start;
}
.msg.user {
  background: #c8e6c9;
  align-self: flex-end;
}

/* ================= 增强响应式 ================= */
@media (max-width: 1024px) {
  .search-section {
    padding: 35px 16px 40px;
    margin: 16px auto 12px;
  }
  .container {
    padding: 16px 0;
  }
  .filter-card { padding: 16px 16px 3px; }
  .filter-row { flex-direction: column; gap: 8px; }
  .filter-label { width: auto; }
}

@media (max-width: 768px) {
  .demand-center { padding-bottom: 24px; }
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
  .demand-card {
    flex-direction: column;
  }
  .demand-card .card-body {
    padding: 16px;
  }
  .demand-card .card-title {
    font-size: 16px;
  }
  .demand-card .card-header-row {
    flex-wrap: wrap;
  }
  .demand-card .card-meta-grid {
    grid-template-columns: 1fr;
    gap: 4px;
  }
  .demand-card .card-actions {
    flex-direction: row;
    padding: 0 16px 16px;
    gap: 8px;
  }
  .demand-card .btn-action {
    flex: 1;
    text-align: center;
    font-size: 13px;
    padding: 8px 12px;
  }
  .demand-card .card-accent {
    width: 100%;
    height: 3px;
  }
  .filter-card { padding: 12px 12px 3px; }
  .filter-chip { padding: 4px 12px; font-size: 12px; }
  .pagination { flex-wrap: wrap; gap: 6px; }
  .pagination a { padding: 4px 10px; font-size: 13px; }

  /* 抽屉全屏 */
  .drawer { width: 100vw !important; }
  .drawer-header { padding: 16px 20px; }
  .drawer-title { font-size: 17px; }
  .drawer-body { padding: 16px; }
  .form-section { padding: 14px; }
  .form-grid { grid-template-columns: 1fr !important; gap: 12px; }
}

@media (max-width: 480px) {
  .search-section { padding: 22px 12px 27px; }
  .demand-card .card-body { padding: 14px; }
  .demand-card .card-title { font-size: 15px; }
  .demand-card .card-meta-item { font-size: 12px; padding: 3px 8px; }
  .filter-chip { font-size: 11px; padding: 3px 10px; }
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
</style>