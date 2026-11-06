<template>
  <div class="center-detail" v-if="data">
    <fieldset class="form-section">
      <legend>一、需求基本信息</legend>
      <div class="form-grid">
        <div class="form-item full-width">
          <label>需求名称：</label>
          <span class="readonly-field">{{ data.title || '-' }}</span>
        </div>
        <div class="form-item">
          <label>企业名称：</label>
          <span class="readonly-field">{{ data.org || '-' }}</span>
        </div>
        <div class="form-item">
          <label>需求编号：</label>
          <span class="readonly-field">{{ data.id || '-' }}</span>
        </div>
        <div class="form-item">
          <label>所属地区：</label>
          <span class="readonly-field">{{ data.region || '-' }}</span>
        </div>
        <div class="form-item">
          <label>应用领域：</label>
          <span class="readonly-field">{{ data.field || '-' }}</span>
        </div>
        <div class="form-item">
          <label>需求类型：</label>
          <span class="readonly-field">{{ data.type || '-' }}</span>
        </div>
        <div class="form-item">
          <label>供需状态：</label>
          <span class="readonly-field" style="font-weight: bold; color: #2196f3;">{{ data.status || '-' }}</span>
        </div>
        <div class="form-item">
          <label>项目预算：</label>
          <span class="readonly-field">{{ data.budget || '-' }}</span>
        </div>
      </div>
    </fieldset>

    <fieldset class="form-section">
      <legend>二、需求描述</legend>
      <div class="form-item full-width" style="margin-bottom: 15px;">
        <label>需求概述：</label>
        <div class="readonly-field" style="height: auto;">{{ data.overview || '-' }}</div>
      </div>
      <div class="form-item full-width">
        <label>期望解决的问题：</label>
        <div class="readonly-field" style="height: auto;">{{ data.issues || '-' }}</div>
      </div>
    </fieldset>
  </div>
  <div v-else class="center-detail-loading">加载中...</div>
</template>

<script>
export default {
  name: 'DemandCenterDetail',
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
