<template>
  <div class="achievement-detail" v-if="achievement">
    <!-- 面包屑导航 -->
    <div class="breadcrumb">
      <div class="container">
        <ul class="breadcrumb-list">
          <li><router-link to="/">首页</router-link></li>
          <li class="separator">/</li>
          <li><router-link to="/achievement">成果中心</router-link></li>
          <li class="separator">/</li>
          <li class="current">{{ achievement.title }}</li>
        </ul>
      </div>
    </div>

    <div class="container">
      <!-- 成果基本信息 -->
      <section class="section basic-info">
        <h2 class="section-title">一、成果基本信息</h2>
        <div class="info-grid">
          <div class="info-item">
            <span class="info-label">成果名称：</span>
            <span class="info-value">{{ achievement.title }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">成果编号：</span>
            <span class="info-value">{{ achievement.achievementNumber || 'CG' + String(achievement.id).padStart(8, '0') }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">成果持有人：</span>
            <span class="info-value">{{ achievement.holder || achievement.owner }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">所属地区：</span>
            <span class="info-value">{{ achievement.region }}</span>
          </div>
          <div class="info-item full-width">
            <span class="info-label">技术领域：</span>
            <div class="info-value">
              <div class="checkbox-group">
                <div class="checkbox-row">
                  <span class="checkbox-item" :class="{ checked: hasTechnologyField('新一代信息技术') }">□新一代信息技术</span>
                  <span class="checkbox-item" :class="{ checked: hasTechnologyField('人工智能') }">□人工智能</span>
                  <span class="checkbox-item" :class="{ checked: hasTechnologyField('大数据') }">□大数据</span>
                  <span class="checkbox-item" :class="{ checked: hasTechnologyField('区块链') }">□区块链</span>
                </div>
                <div class="checkbox-row">
                  <span class="checkbox-item" :class="{ checked: hasTechnologyField('高端装备制造') }">□高端装备制造</span>
                  <span class="checkbox-item" :class="{ checked: hasTechnologyField('机器人') }">□机器人</span>
                  <span class="checkbox-item" :class="{ checked: hasTechnologyField('航空航天') }">□航空航天</span>
                </div>
                <div class="checkbox-row">
                  <span class="checkbox-item" :class="{ checked: hasTechnologyField('新材料') }">□新材料</span>
                  <span class="checkbox-item" :class="{ checked: hasTechnologyField('新能源') }">□新能源</span>
                  <span class="checkbox-item" :class="{ checked: hasTechnologyField('节能环保') }">□节能环保</span>
                </div>
                <div class="checkbox-row">
                  <span class="checkbox-item" :class="{ checked: hasTechnologyField('生物医药') }">□生物医药</span>
                  <span class="checkbox-item" :class="{ checked: hasTechnologyField('医疗器械') }">□医疗器械</span>
                  <span class="checkbox-item" :class="{ checked: hasTechnologyField('现代农业') }">□现代农业</span>
                </div>
                <div class="checkbox-row">
                  <span class="checkbox-item other" :class="{ checked: hasOtherTechnologyField }">□其他：{{ otherTechnologyField }}</span>
                </div>
              </div>
            </div>
          </div>
          <div class="info-item full-width">
            <span class="info-label">技术成熟度：</span>
            <div class="info-value">
              <div class="checkbox-group">
                <div class="checkbox-row">
                  <span class="checkbox-item" :class="{ checked: achievement.maturity === '实验室理论阶段' }">□实验室理论阶段</span>
                  <span class="checkbox-item" :class="{ checked: achievement.maturity === '中试阶段' }">□中试阶段</span>
                  <span class="checkbox-item" :class="{ checked: achievement.maturity === '可规模量产' }">□可规模量产</span>
                </div>
              </div>
            </div>
          </div>
          <div class="info-item full-width">
            <span class="info-label">转化方式（可多选）：</span>
            <div class="info-value">
              <div class="checkbox-group">
                <div class="checkbox-row">
                  <span class="checkbox-item" :class="{ checked: hasTransferMethod('技术转让') }">□技术转让</span>
                  <span class="checkbox-item" :class="{ checked: hasTransferMethod('技术许可') }">□技术许可</span>
                  <span class="checkbox-item" :class="{ checked: hasTransferMethod('技术入股') }">□技术入股</span>
                  <span class="checkbox-item" :class="{ checked: hasTransferMethod('合作开发') }">□合作开发</span>
                  <span class="checkbox-item other" :class="{ checked: hasOtherTransferMethod }">□其他：{{ otherTransferMethod }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 成果描述 -->
      <section class="section description">
        <h2 class="section-title">二、成果描述</h2>
        <div class="info-grid">
          <div class="info-item full-width">
            <span class="info-label">成果摘要：</span>
            <div class="info-value">{{ achievement.summary || achievement.intro }}</div>
          </div>
          <div class="info-item full-width">
            <span class="info-label">技术优势描述：</span>
            <div class="info-value">
              <div class="advantage-section">
                <div class="advantage-item">
                  <span class="advantage-label">创新性：</span>
                  <div class="checkbox-group">
                    <span class="checkbox-item" :class="{ checked: achievement.innovationLevel === '国际领先' }">□国际领先</span>
                    <span class="checkbox-item" :class="{ checked: achievement.innovationLevel === '国内领先' }">□国内领先</span>
                    <span class="checkbox-item" :class="{ checked: achievement.innovationLevel === '行业领先' }">□行业领先</span>
                  </div>
                </div>
                <div class="advantage-item">
                  <span class="advantage-label">与现有技术相比的优势：</span>
                  <div class="advantage-text">{{ achievement.advantages }}</div>
                </div>
              </div>
            </div>
          </div>
          <div class="info-item full-width">
            <span class="info-label">核心技术指标：</span>
            <div class="info-value">{{ achievement.coreTechnicalIndicators }}</div>
          </div>
          <div class="info-item full-width">
            <span class="info-label">获得的知识产权：</span>
            <div class="info-value">{{ achievement.intellectualProperties }}</div>
          </div>
        </div>
      </section>

      <!-- 成果转化 -->
      <section class="section transformation">
        <h2 class="section-title">三、成果转化</h2>
        <div class="info-grid">
          <div class="info-item full-width">
            <span class="info-label">合作方式偏好：</span>
            <div class="info-value">
              <div class="checkbox-group">
                <div class="checkbox-row">
                  <span class="checkbox-item" :class="{ checked: hasCollaborationPreference('技术转让') }">
                    □技术转让（转让费：期望{{ achievement.techTransferFee || '____' }}万元）
                  </span>
                </div>
                <div class="checkbox-row">
                  <span class="checkbox-item" :class="{ checked: hasCollaborationPreference('技术许可') }">
                    □技术许可（许可方式：
                    <span class="sub-checkbox" :class="{ checked: achievement.licenseType === '独占' }">□独占</span>
                    <span class="sub-checkbox" :class="{ checked: achievement.licenseType === '排他' }">□排他</span>
                    <span class="sub-checkbox" :class="{ checked: achievement.licenseType === '普通' }">□普通</span>
                    ）
                  </span>
                </div>
                <div class="checkbox-row">
                  <span class="checkbox-item" :class="{ checked: hasCollaborationPreference('技术入股') }">
                    □技术入股（作价{{ achievement.techValuation || '____' }}万元，占{{ achievement.equityPercentage || '____' }}股%）
                  </span>
                </div>
                <div class="checkbox-row">
                  <span class="checkbox-item" :class="{ checked: hasCollaborationPreference('合作开发') }">□合作开发</span>
                </div>
                <div class="checkbox-row">
                  <span class="checkbox-item other" :class="{ checked: hasOtherCollaborationPreference }">
                    □其他：{{ otherCollaborationPreference }}
                  </span>
                </div>
              </div>
            </div>
          </div>
          <div class="info-item">
            <span class="info-label">期望完成转化时间：</span>
            <span class="info-value">{{ achievement.expectedCompletionDate || '____年____月前' }}</span>
          </div>
        </div>
      </section>

      <!-- 操作按钮 -->
      <div class="action-buttons">
        <button class="btn-back" @click="$router.push('/achievement')">返回成果列表</button>
        <button class="btn-contact" @click="openChatModal">我要对接</button>
      </div>
    </div>
  </div>
  <div v-else class="loading">
    加载中...
  </div>
</template>

<script>
import { ref, onMounted, computed, inject } from 'vue'
import { useRoute } from 'vue-router'
import request from '@/utils/request'
import useAuth from '@/composables/useAuth'

export default {
  name: 'AchievementDetailView',
  props: {
    id: {
      type: [String, Number],
      required: true
    }
  },
  setup(props) {
    const achievement = ref(null)
    const loading = ref(true)
    const globalOpenChat = inject('globalOpenChat')
    const auth = useAuth()
    const route = useRoute()

    // 获取成果详情数据
    const fetchAchievementDetail = async () => {
      try {
        loading.value = true
        const response = await request.get(`/api/publish/achievement/${props.id}`)

        if (response.code === 200 && response.data) {
          achievement.value = response.data
          // 确保数组字段存在
          if (!achievement.value.technologyFields) achievement.value.technologyFields = []
          if (!achievement.value.transferMethods) achievement.value.transferMethods = []
          if (!achievement.value.collaborationPreferences) achievement.value.collaborationPreferences = []
        } else {
          console.error('获取成果详情失败:', response.msg)
          achievement.value = null
        }
      } catch (error) {
        console.error('获取成果详情出错:', error)
        achievement.value = null
      } finally {
        loading.value = false
      }
    }

    // 计算属性
    const hasTechnologyField = (field) => {
      return achievement.value?.technologyFields?.includes(field) || false
    }

    const hasOtherTechnologyField = computed(() => {
      return achievement.value?.otherTechnologyField?.length > 0
    })

    const otherTechnologyField = computed(() => {
      return achievement.value?.otherTechnologyField || '__________'
    })

    const hasTransferMethod = (method) => {
      return achievement.value?.transferMethods?.includes(method) || false
    }

    const hasOtherTransferMethod = computed(() => {
      return achievement.value?.otherTransferMethod?.length > 0
    })

    const otherTransferMethod = computed(() => {
      return achievement.value?.otherTransferMethod || '__________'
    })

    const hasCollaborationPreference = (preference) => {
      return achievement.value?.collaborationPreferences?.includes(preference) || false
    }

    const hasOtherCollaborationPreference = computed(() => {
      return achievement.value?.otherCollaborationPreference?.length > 0
    })

    const otherCollaborationPreference = computed(() => {
      return achievement.value?.otherCollaborationPreference || '__________'
    })

    const openChatModal = () => {
      if (!auth.isLoggedIn.value) {
        auth.openLoginPrompt(route.fullPath)
        return
      }
      if (globalOpenChat) {
        globalOpenChat('achievement', props.id)
      }
    }

    onMounted(() => {
      fetchAchievementDetail()
    })

    return {
      achievement,
      loading,
      hasTechnologyField,
      hasOtherTechnologyField,
      otherTechnologyField,
      hasTransferMethod,
      hasOtherTransferMethod,
      otherTransferMethod,
      hasCollaborationPreference,
      hasOtherCollaborationPreference,
      otherCollaborationPreference,
      openChatModal
    }
  }
}
</script>

<style scoped>
.achievement-detail {
  font-family: -apple-system, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Segoe UI", "Helvetica Neue", Arial, sans-serif;
  line-height: 1.5715;
  color: rgba(0, 0, 0, 0.85);
  background-color: #f0f2f5;
  min-height: 100vh;
  padding-bottom: 40px;
}

.container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}

/* 面包屑导航 */
.breadcrumb {
  background: white;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
  margin-bottom: 24px;
}

.breadcrumb-list {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #999;
}

.breadcrumb-list a {
  color: #999;
  transition: color 0.3s;
  text-decoration: none;
}

.breadcrumb-list a:hover {
  color: #1890ff;
}

.breadcrumb-list .current {
  color: #666;
  font-weight: 500;
}

.breadcrumb-list .separator {
  color: #ccc;
}

/* 区块样式 */
.section {
  background: white;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

/* 信息网格 */
.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.info-item {
  display: flex;
  align-items: flex-start;
}

.info-item.full-width {
  grid-column: 1 / -1;
}

.info-label {
  min-width: 120px;
  font-weight: 500;
  color: #666;
  white-space: nowrap;
}

.info-value {
  flex: 1;
  color: #333;
  line-height: 1.6;
}

/* 复选框组样式 */
.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.checkbox-row {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
}

.checkbox-item {
  position: relative;
  padding-left: 20px;
  color: #666;
}

.checkbox-item.checked::before {
  content: '✓';
  position: absolute;
  left: 0;
  color: #1890ff;
  font-weight: bold;
}

.checkbox-item.other {
  min-width: 200px;
}

.sub-checkbox {
  position: relative;
  padding-left: 20px;
  margin: 0 8px;
  color: #666;
}

.sub-checkbox.checked::before {
  content: '✓';
  position: absolute;
  left: 0;
  color: #1890ff;
  font-weight: bold;
}

/* 优势描述样式 */
.advantage-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.advantage-item {
  display: flex;
  align-items: flex-start;
}

.advantage-label {
  min-width: 120px;
  font-weight: 500;
  color: #666;
}

.advantage-text {
  flex: 1;
  color: #333;
  line-height: 1.6;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin-top: 40px;
}

.btn-back, .btn-contact {
  padding: 12px 32px;
  font-size: 16px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
  border: none;
}

.btn-back {
  background: white;
  color: #666;
  border: 1px solid #d9d9d9;
}

.btn-back:hover {
  border-color: #1890ff;
  color: #1890ff;
}

.btn-contact {
  background: #1890ff;
  color: white;
}

.btn-contact:hover {
  background: #40a9ff;
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.3);
}

/* 加载状态 */
.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
  font-size: 16px;
  color: #666;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .info-grid {
    grid-template-columns: 1fr;
  }

  .info-item {
    flex-direction: column;
    gap: 8px;
  }

  .info-label {
    min-width: auto;
  }

  .checkbox-row {
    flex-direction: column;
    gap: 12px;
  }

  .action-buttons {
    flex-direction: column;
    gap: 16px;
  }

  .btn-back, .btn-contact {
    width: 100%;
  }
}

@media (max-width: 1024px) {
  .achievement-detail .container { padding: 0 16px; }
  .section { padding: 20px; }
  .info-item { padding: 10px 14px; }
}

@media (max-width: 480px) {
  .achievement-detail .container { padding: 0 10px; }
  .breadcrumb { padding: 8px 0; }
  .breadcrumb-list { font-size: 12px; flex-wrap: wrap; }
  .section { padding: 14px; margin-bottom: 16px; }
  .section-title { font-size: 16px; }
  .info-grid { gap: 8px; }
  .info-item { padding: 8px 10px; font-size: 13px; }
  .action-buttons { padding: 20px 0; }
}
</style>