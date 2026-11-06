<template>
  <div class="dynamic-page-wrapper">
    <div v-if="loading" class="page-loading">
      <div class="loader-spinner"></div>
      <span>加载中...</span>
    </div>
    <div v-else-if="error" class="page-error">
      <p>{{ error }}</p>
    </div>
    <div
      v-else
      ref="contentEl"
      class="page-content"
      v-html="bodyHtml"
    ></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, computed, nextTick } from 'vue'
import { useRoute } from 'vue-router'

console.log('[DynamicPageView] ✅ 组件已加载')

const route = useRoute()

const pagePath = computed(() => {
  if (route.params.pagePath) return route.params.pagePath
  return route.path.replace(/^\//, '')
})

const bodyHtml = ref('')
const loading = ref(true)
const error = ref('')
const contentEl = ref(null)
let observer = null

const ANIMATION_CLASSES = ['animate-fade-in', 'animate-fade-left', 'animate-fade-right', 'animate-scale-in']
const ANIMATION_SELECTOR = ANIMATION_CLASSES.map(c => '.' + c).join(',')
const SKIP_TAGS = { script: 1, style: 1, link: 1, meta: 1, noscript: 1, title: 1, base: 1 }

// 提取后端返回 HTML 中的 <style> 和 <body> 内容
function extractBodyContent(html) {
  const styleRegex = /<style[^>]*>([\s\S]*?)<\/style>/gi
  let styles = ''
  let match
  while ((match = styleRegex.exec(html)) !== null) {
    styles += match[1] + '\n'
  }

  const bodyRegex = /<body[^>]*>([\s\S]*?)<\/body>/i
  const bodyMatch = html.match(bodyRegex)
  let body = bodyMatch ? bodyMatch[1] : html

  // 移除 script 标签（后端 script 是为 iframe 设计的，v-html 中不需要）
  body = body.replace(/<script[^>]*>[\s\S]*?<\/script>/gi, '')

  return `<style>${styles}</style>${body}`
}

// 给容器直接子元素注入动画类名
function injectAnimationClasses(root) {
  const children = root.children
  let count = 0
  for (let i = 0; i < children.length; i++) {
    const el = children[i]
    if (SKIP_TAGS[el.tagName.toLowerCase()]) continue
    if (ANIMATION_CLASSES.some(c => el.classList.contains(c))) continue
    el.classList.add('animate-fade-in')
    if (count < 5) {
      el.classList.add('animate-delay-' + (count + 1))
    }
    count++
  }
}

// 启动滚动动画
function setupScrollAnimation() {
  const root = contentEl.value
  if (!root) {
    console.log('[动画] contentEl 不存在，跳过')
    return
  }

  // 1. 注入动画类名
  injectAnimationClasses(root)

  // 2. 查找所有动画元素
  const animatedEls = root.querySelectorAll(ANIMATION_SELECTOR)
  console.log('[动画] 页面元素总数:', root.querySelectorAll('*').length)
  console.log('[动画] 动画元素数:', animatedEls.length)

  if (animatedEls.length === 0) {
    console.log('[动画] 无动画元素')
    root.classList.add('anim-ready')
    return
  }

  // 3. 首屏可见元素直接显示
  let visibleCount = 0
  animatedEls.forEach(el => {
    const rect = el.getBoundingClientRect()
    if (rect.top < window.innerHeight - 60 && rect.height > 0) {
      el.classList.add('visible')
      visibleCount++
    }
  })
  console.log('[动画] 首屏可见:', visibleCount, '/', animatedEls.length)

  // 4. 激活动画模式：没有 .visible 的元素进入"待动画"隐藏状态
  root.classList.add('anim-ready')

  // 5. IntersectionObserver 监听滚动
  observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible')
        observer.unobserve(entry.target)
      }
    })
  }, { threshold: 0.1 })

  const invisibleEls = root.querySelectorAll(
    ANIMATION_CLASSES.map(c => '.' + c + ':not(.visible)').join(',')
  )
  console.log('[动画] 等待滚动触发:', invisibleEls.length)
  invisibleEls.forEach(el => observer.observe(el))
}

async function fetchPage(path) {
  loading.value = true
  error.value = ''
  bodyHtml.value = ''
  if (observer) {
    observer.disconnect()
    observer = null
  }
  try {
    console.log('[DynamicPageView] 请求页面:', path)
    const res = await fetch(`/api/editor/site/pages/${path}/view`)
    if (!res.ok) {
      error.value = '页面不存在或尚未发布'
      loading.value = false
      console.log('[DynamicPageView] API 返回错误:', res.status)
      return
    }
    const fullHtml = await res.text()
    console.log('[DynamicPageView] API 返回成功，HTML长度:', fullHtml.length)
    bodyHtml.value = extractBodyContent(fullHtml)
    loading.value = false
    await nextTick()
    console.log('[DynamicPageView] nextTick 完成，启动动画')
    setupScrollAnimation()
  } catch (e) {
    console.error('[DynamicPageView] 加载失败:', e)
    error.value = '无法加载页面：' + e.message
    loading.value = false
  }
}

onMounted(() => {
  console.log('[DynamicPageView] onMounted, pagePath:', pagePath.value)
  fetchPage(pagePath.value)
})

onBeforeUnmount(() => {
  if (observer) {
    observer.disconnect()
    observer = null
  }
})

watch(pagePath, (newPath) => {
  if (newPath) {
    console.log('[DynamicPageView] 路由变化:', newPath)
    fetchPage(newPath)
  }
})
</script>

<style scoped>
.dynamic-page-wrapper {
  width: 100%;
  min-height: 100vh;
  position: relative;
}

.page-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 80px 20px;
  color: #666;
  font-size: 15px;
}

.loader-spinner {
  width: 28px;
  height: 28px;
  border: 3px solid #e0e0e0;
  border-top-color: #4a90d9;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.page-error {
  text-align: center;
  padding: 80px 20px;
  color: #999;
  font-size: 15px;
}

.page-content {
  width: 100%;
  min-height: 100vh;
  background: #fff;
}

/* 隔离编辑器页面的基础样式 */
.page-content :deep(img) {
  max-width: 100%;
  height: auto;
}

</style>

<!-- 滚动动画样式（非 scoped，作用于 v-html 注入的元素） -->
<!-- 策略：默认元素可见（防白屏），JS 初始化后给 .page-content 加 .anim-ready，非 .visible 元素才进入隐藏+动画待命状态 -->
<style>
/* 链接继承父元素文字颜色 */
.page-content a {
  color: inherit !important;
}

/* 默认：元素可见 */
.animate-fade-in,
.animate-fade-left,
.animate-fade-right,
.animate-scale-in {
  opacity: 1;
}

/* anim-ready 激活后：非 visible 元素进入隐藏+待动画状态 */
.page-content.anim-ready .animate-fade-in:not(.visible),
.page-content.anim-ready .animate-fade-left:not(.visible),
.page-content.anim-ready .animate-fade-right:not(.visible),
.page-content.anim-ready .animate-scale-in:not(.visible) {
  opacity: 0;
  visibility: visible;
  transition: opacity 0.8s ease, transform 0.8s ease;
}

.page-content.anim-ready .animate-fade-in:not(.visible) { transform: translateY(40px); }
.page-content.anim-ready .animate-fade-left:not(.visible) { transform: translateX(-50px); }
.page-content.anim-ready .animate-fade-right:not(.visible) { transform: translateX(50px); }
.page-content.anim-ready .animate-scale-in:not(.visible) { transform: scale(0.9); }

/* visible 状态：显示 + 恢复 */
.page-content.anim-ready .animate-fade-in.visible,
.page-content.anim-ready .animate-fade-left.visible,
.page-content.anim-ready .animate-fade-right.visible,
.page-content.anim-ready .animate-scale-in.visible {
  opacity: 1;
  transform: translate(0) scale(1);
}

/* 延迟变体 */
.animate-delay-1.visible { transition-delay: 0.15s; }
.animate-delay-2.visible { transition-delay: 0.30s; }
.animate-delay-3.visible { transition-delay: 0.45s; }
.animate-delay-4.visible { transition-delay: 0.60s; }
.animate-delay-5.visible { transition-delay: 0.75s; }

@media (prefers-reduced-motion: reduce) {
  .page-content.anim-ready .animate-fade-in:not(.visible),
  .page-content.anim-ready .animate-fade-left:not(.visible),
  .page-content.anim-ready .animate-fade-right:not(.visible),
  .page-content.anim-ready .animate-scale-in:not(.visible) {
    opacity: 1;
    transform: none;
    transition: none;
  }
}
</style>
