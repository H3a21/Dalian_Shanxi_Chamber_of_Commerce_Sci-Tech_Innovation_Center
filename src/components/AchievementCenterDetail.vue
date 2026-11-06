<template>
  <div class="center-detail" v-if="data">
    <fieldset class="form-section">
      <legend>一、成果基本信息</legend>
      <div class="form-grid">
        <div class="form-item full-width">
          <label>成果名称：</label>
          <span class="readonly-field" style="font-weight: bold; color: #2196f3;">{{ data.title || '-' }}</span>
        </div>
        <div class="form-item">
          <label>企业名称/持有人：</label>
          <span class="readonly-field">{{ data.owner || '-' }}</span>
        </div>
        <div class="form-item">
          <label>成果编号：</label>
          <span class="readonly-field">{{ data.id || '-' }}</span>
        </div>
        <div class="form-item">
          <label>技术领域：</label>
          <span class="readonly-field">{{ data.field || '-' }}</span>
        </div>
        <div class="form-item">
          <label>技术成熟度：</label>
          <span class="readonly-field" style="font-weight: bold; color: #2196f3;">{{ data.maturity || '-' }}</span>
        </div>
        <div class="form-item full-width">
          <label>拟转化方式：</label>
          <span class="readonly-field">{{ data.transferDisplay || '-' }}</span>
        </div>
      </div>
    </fieldset>

    <fieldset class="form-section">
      <legend>二、成果描述</legend>
      <div class="form-item full-width" style="margin-bottom: 15px;">
        <label>成果摘要：</label>
        <div class="readonly-field" style="height: auto;">{{ data.summary || '-' }}</div>
      </div>
      <div class="form-item full-width" style="margin-bottom: 15px;">
        <label>技术优势描述：</label>
        <div class="readonly-field" style="height: auto;">{{ data.advantage || '-' }}</div>
      </div>
      <div class="form-grid">
        <div class="form-item">
          <label>创新性评价：</label>
          <span class="readonly-field">{{ data.innovation || '-' }}</span>
        </div>
        <div class="form-item">
          <label>核心技术指标：</label>
          <span class="readonly-field">{{ data.indicator || '-' }}</span>
        </div>
        <div class="form-item full-width">
          <label>与现有技术相比的优势：</label>
          <div class="readonly-field" style="height: auto;">{{ data.compare || '-' }}</div>
        </div>
        <div class="form-item full-width">
          <label>获得的知识产权情况：</label>
          <div class="readonly-field" style="height: auto;">{{ data.ipr || '-' }}</div>
        </div>
      </div>
    </fieldset>

    <fieldset class="form-section">
      <legend>三、成果转化期望</legend>
      <div class="form-item full-width">
        <label>合作方式偏好及财务预期：</label>
        <span class="readonly-field" style="color: #faad14; font-weight: bold;">{{ data.collab || '-' }}</span>
      </div>
      <div class="form-item full-width">
        <label>期望完成转化时间：</label>
        <span class="readonly-field">{{ data.deadline || '-' }}</span>
      </div>
    </fieldset>
  </div>
  <div v-else class="center-detail-loading">加载中...</div>
</template>

<script>
export default {
  name: 'AchievementCenterDetail',
  props: {
    data: {
      type: Object,
      default: null
    }
  }
}
</script>

<style scoped>
.center-detail-loading {
  text-align: center;
  padding: 40px 20px;
  color: #999;
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

@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr !important;
    gap: 12px;
  }
  .form-section {
    padding: 14px;
  }
}
</style>
