<template>
  <div class="placeholder-page">
    <div class="main-container">
      <div class="content-card">
        <svg class="premium-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10" stroke-width="1"/>
          <path d="M12 8v4l3 3" />
        </svg>

        <div class="empty-title">敬请期待</div>
        <div class="empty-subtitle">{{ pageTitle }}模块，正在精心筹备</div>

        <div class="decorator-line"></div>

        <div class="empty-en">Coming Soon</div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PlaceholderView',
  computed: {
    pageTitle() {
      const map = {
        'incubation': '项目孵化',
        'talent': '人才培养'
      }
      return map[this.$route.name] || ''
    }
  }
}
</script>

<style scoped>
.placeholder-page {
  min-height: calc(100vh - 70px);
  background-color: #f7f8fc;
  color: #333;
  display: flex;
  flex-direction: column;
}

.main-container {
  width: 1200px;
  max-width: 100%;
  margin: 32px auto 60px;
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 0 16px;
}

.content-card {
  width: 100%;
  flex: 1;
  min-height: 400px;
  background-color: #ffffff;
  border-radius: 12px;
  box-shadow: 0 8px 40px -12px rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  transition: transform 0.3s ease;
}

.premium-icon {
  width: 64px;
  height: 64px;
  margin-bottom: 28px;
  color: #cdd0d6;
  stroke-width: 1;
}

.empty-title {
  color: #2c313c;
  font-size: 24px;
  font-weight: 500;
  letter-spacing: 6px;
  margin-bottom: 12px;
  padding-left: 6px;
}

.empty-subtitle {
  color: #8a8e99;
  font-size: 14px;
  letter-spacing: 1px;
  font-weight: 300;
}

.decorator-line {
  width: 40px;
  height: 1px;
  background-color: #e4e7ed;
  margin: 24px 0;
}

.empty-en {
  color: #a0a5b3;
  font-size: 12px;
  letter-spacing: 4px;
  font-weight: 300;
  text-transform: uppercase;
}
</style>
