<template>
  <div class="about-page">
    <!-- 页面横幅 -->
    <section class="page-banner">
      <div class="container">
        <div class="banner-content">
          <h1>关于我们</h1>
        </div>
      </div>
    </section>

    <!-- 商会简介 -->
    <section class="about-intro-section">
      <div class="container">
        <div class="about-intro-grid">
          <div class="about-intro-content animate-on-scroll">
            <div class="intro-text-block">
              <span class="intro-label">ABOUT US</span>
              <h2>简介</h2>
              <div class="intro-divider"></div>
              <p>{{ aboutContent.intro_text || '大连市山西商会科创中心（英文名称" Dalian Shanxi Chamber of Commerce Science and Technology Innovation Center "）是在自愿、平等、合作、互利的基础上，由大连市山西商会发起，联合企业、高校和科研院所有识之士共同组建的产学研成果对接和创业孵化非营利性组织。中心隶属于大连市山西商会，在大连市山西商会指导下开展工作，服务对象包括企业，高校和科研院所创新创业群体，以及认同商会章程的社会各界组织和人士。' }}</p>
            </div>
          </div>
          <div class="about-intro-image animate-on-scroll right">
            <div class="image-frame">
              <!-- 图片待添加 -->
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 使命与愿景 -->
    <section class="mission-vision-section">
      <div class="container">
        <div class="section-header">
          <h2>使命与愿景</h2>
        </div>
        <div class="mission-vision-grid">
          <div
            v-for="(item, index) in aboutContent.mission_items"
            :key="index"
            class="mv-card animate-on-scroll"
            :class="'delay-' + (index + 1)"
          >
            <div class="mv-icon" :style="{ background: missionColors[index % missionColors.length] }">
              <i :class="item.icon || 'fas fa-star'"></i>
            </div>
            <h3>{{ item.title || '使命愿景' }}</h3>
            <p>{{ item.desc || '' }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 核心优势 -->
    <section class="advantages-section">
      <div class="container">
        <div class="section-header">
          <h2>核心优势</h2>
        </div>
        <div class="advantages-grid">
          <div
            v-for="(item, index) in aboutContent.advantage_items"
            :key="index"
            class="advantage-card animate-on-scroll"
            :class="'delay-' + (index + 1)"
          >
            <div class="advantage-icon"><i :class="item.icon || 'fas fa-check-circle'"></i></div>
            <h3>{{ item.title || '优势' }}</h3>
            <p>{{ item.desc || '' }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 运行机制 -->
    <section class="mechanism-section">
      <div class="container">
        <div class="section-header">
          <h2>运行机制</h2>
        </div>
        <div class="mechanism-grid">
          <div
            v-for="(item, index) in aboutContent.mechanism_items"
            :key="index"
            class="mechanism-card animate-on-scroll"
            :class="'delay-' + (index + 1)"
          >
            <div class="mechanism-icon"><i :class="item.icon || 'fas fa-cog'"></i></div>
            <h3>{{ item.title || '运行机制' }}</h3>
            <p>{{ item.desc || '' }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 页脚 -->
    <footer class="footer">
      <div class="container">
        <div class="footer-content">
          <div class="footer-section">
            <h3>{{ siteName || '大连山西商会科创中心' }}</h3>
            <div class="social-links">
              <a href="#"><i class="fab fa-weixin"></i></a>
              <a href="#"><i class="fab fa-weibo"></i></a>
              <a href="#"><i class="fab fa-qq"></i></a>
              <a href="#"><i class="fab fa-linkedin"></i></a>
            </div>
          </div>
          <div class="footer-section">
            <h4>快速链接</h4>
            <ul>
              <li><router-link to="/achievement">成果中心</router-link></li>
              <li><router-link to="/demand">需求中心</router-link></li>
              <li><router-link to="/expert">专家中心</router-link></li>
              <li><router-link to="/partner">合作伙伴</router-link></li>
            </ul>
          </div>
          <div class="footer-section">
            <h4>服务支持</h4>
            <ul>
              <li><a href="#">帮助中心</a></li>
              <li><a href="#">客服中心</a></li>
              <li><a href="#">使用指南</a></li>
              <li><a href="#">常见问题</a></li>
            </ul>
          </div>
          <div class="footer-section">
            <h4>联系我们</h4>
            <ul class="contact-info">
              <li><i class="fas fa-map-marker-alt"></i> {{ aboutContent.contact_address || 'xxxxxxxxx' }}</li>
              <li><i class="fas fa-phone"></i> {{ aboutContent.contact_phone || 'xxxxxxxx' }}</li>
              <li><i class="fas fa-envelope"></i> {{ aboutContent.contact_email || 'xxxxxxxx' }}</li>
            </ul>
          </div>
        </div>
        <div class="footer-bottom">
          <p>&copy; 2024 {{ siteName || '大连山西商会科创中心' }} 版权所有 <span>|</span> <router-link to="/privacy">隐私政策</router-link> <span>|</span> <router-link to="/terms">使用条款</router-link></p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, reactive, ref } from 'vue'


const aboutContent = reactive({
  intro_text: '',
  mission_items: [],
  advantage_items: [],
  mechanism_items: [],
  contact_address: '',
  contact_phone: '',
  contact_email: ''
})

const siteName = ref('')
const missionColors = [
  'linear-gradient(135deg, #1890ff, #096dd9)',
  'linear-gradient(135deg, #52c41a, #389e0d)',
  'linear-gradient(135deg, #722ed1, #531dab)',
  'linear-gradient(135deg, #faad14, #d48806)',
  'linear-gradient(135deg, #ff4d4f, #cf1322)',
  'linear-gradient(135deg, #13c2c2, #08979c)'
]

async function fetchAboutContent() {
  try {
    const res = await fetch('/api/editor/config/all')
    const data = await res.json()
    if (data.code === 200 && data.data) {
      if (data.data.site_name) siteName.value = data.data.site_name
      if (data.data.about_content) {
        const ac = data.data.about_content
        if (ac.intro_text) aboutContent.intro_text = ac.intro_text
        if (Array.isArray(ac.mission_items) && ac.mission_items.length > 0) aboutContent.mission_items = ac.mission_items
        if (Array.isArray(ac.advantage_items) && ac.advantage_items.length > 0) aboutContent.advantage_items = ac.advantage_items
        if (Array.isArray(ac.mechanism_items) && ac.mechanism_items.length > 0) aboutContent.mechanism_items = ac.mechanism_items
        if (ac.contact_address) aboutContent.contact_address = ac.contact_address
        if (ac.contact_phone) aboutContent.contact_phone = ac.contact_phone
        if (ac.contact_email) aboutContent.contact_email = ac.contact_email
      }
    }
  } catch (e) {
    console.error('加载关于我们内容失败:', e)
  }

  // 如果API没有返回数据，使用默认值
  if (aboutContent.mission_items.length === 0) {
    aboutContent.mission_items = [
      { title: '高水平转化一批成果', desc: '推动科研成果高效转化，打通从实验室到产业化的关键通道。' },
      { title: '高产值孵化一批公司', desc: '孵化培育具有核心竞争力的科技型企业，实现高产值增长。' },
      { title: '高技术赋能一批企业', desc: '以先进技术赋能传统企业，助力产业升级和数字化转型。' },
      { title: '高质量培养一批人才', desc: '培养产学研复合型高端人才，为创新发展提供坚实的人才支撑。' }
    ]
  }
  if (aboutContent.advantage_items.length === 0) {
    aboutContent.advantage_items = [
      { title: '专业团队', desc: '汇聚行业顶尖专家和技术人才，平均从业经验超过 10 年。' },
      { title: '安全可靠', desc: '严格的质量控制体系和完善的安全保障机制。' },
      { title: '生态合作', desc: '与产业链上下游企业建立深度合作关系。' }
    ]
  }
  if (aboutContent.mechanism_items.length === 0) {
    aboutContent.mechanism_items = [
      { title: '信息互通机制', desc: '采用多种形式高效率的发布成果信息和需求信息。' },
      { title: '交流对接机制', desc: '举办交流对接和讲座研讨活动，促进产学研深度合作。' },
      { title: '互访联动机制', desc: '组织企业和高校走访调研，收集需求与成果。' }
    ]
  }
}

let observer = null

onMounted(() => {
  fetchAboutContent()

  const observerOptions = {
    root: null,
    rootMargin: '0px',
    threshold: 0.1
  }
  observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('show')
      }
    })
  }, observerOptions)
  // 使用 setTimeout 等待数据渲染后再观察
  setTimeout(() => {
    document.querySelectorAll('.animate-on-scroll').forEach(el => {
      observer.observe(el)
    })
  }, 500)
})

onUnmounted(() => {
  if (observer) {
    observer.disconnect()
  }
})
</script>

<style>
/* 基础样式 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

:root {
  --primary-color: #1890ff;
  --primary-dark: #096dd9;
  --text-color: rgba(0, 0, 0, 0.85);
  --text-secondary: rgba(0, 0, 0, 0.65);
  --text-light: rgba(0, 0, 0, 0.45);
  --transition: all 0.3s;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  line-height: 1.5715;
  color: var(--text-color);
  background-color: #f0f2f5;
}

.container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

a { text-decoration: none; color: inherit; }
ul { list-style: none; }

/* 页面横幅 */
.page-banner {
  position: relative;
  height: 280px;
  background: linear-gradient(135deg, rgba(24, 144, 255, 0.85), rgba(0, 21, 41, 0.85)), url('https://images.unsplash.com/photo-1551288049-bebda4e38f71?ixlib=rb-4.0.3&auto=format&fit=crop&w=1600&q=80');
  background-size: cover;
  background-position: center;
  display: flex;
  align-items: center;
  justify-content: center;
}

.banner-content {
  text-align: center;
  color: white;
}

.banner-content h1 {
  font-size: 36px;
  font-weight: 600;
  margin-bottom: 12px;
}

.banner-content p {
  font-size: 16px;
  opacity: 0.85;
  max-width: 700px;
  margin: 0 auto;
}

/* 通用部分样式 */
.section-header {
  text-align: center;
  margin-bottom: 40px;
}

.section-header h2 {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 12px;
}

.section-header p {
  color: var(--text-secondary);
  font-size: 14px;
}

/* 商会简介 */
.about-intro-section {
  padding: 64px 0;
  background: white;
}

.about-intro-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 56px;
  align-items: center;
}

.intro-text-block {
  position: relative;
  padding-left: 28px;
}

.intro-text-block::before {
  content: '';
  position: absolute;
  left: 0;
  top: 4px;
  width: 3px;
  height: calc(100% - 8px);
  background: linear-gradient(180deg, var(--primary-color), rgba(24, 144, 255, 0.2));
  border-radius: 2px;
}

.intro-label {
  display: inline-block;
  font-size: 11px;
  letter-spacing: 4px;
  text-transform: uppercase;
  color: var(--primary-color);
  font-weight: 500;
  margin-bottom: 8px;
}

.about-intro-content h2 {
  font-size: 28px;
  font-weight: 300;
  letter-spacing: 3px;
  margin-bottom: 16px;
  color: rgba(0, 0, 0, 0.85);
}

.intro-divider {
  width: 40px;
  height: 2px;
  background: var(--primary-color);
  margin-bottom: 20px;
  border-radius: 1px;
}

.about-intro-content p {
  font-size: 15px;
  line-height: 1.9;
  letter-spacing: 0.5px;
  color: rgba(0, 0, 0, 0.62);
  text-align: justify;
}

.image-frame {
  position: relative;
  padding: 12px;
  min-height: 320px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-frame::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border: 2px solid var(--primary-color);
  border-radius: 10px;
  opacity: 0.2;
  z-index: 0;
  pointer-events: none;
}

.about-intro-image img {
  position: relative;
  width: 100%;
  border-radius: 6px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  display: block;
  z-index: 1;
}

/* 使命愿景 */
.mission-vision-section {
  padding: 48px 0;
  background: #fafafa;
}

.mission-vision-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  margin-top: 40px;
}

.mv-card {
  background: white;
  padding: 32px 24px;
  border-radius: 8px;
  text-align: center;
  border: 1px solid #f0f0f0;
  transition: all 0.3s;
}

.mv-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border-color: #d9d9d9;
}

.mv-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: white;
}

.mission-card .mv-icon { background: linear-gradient(135deg, var(--primary-color), var(--primary-dark)); }
.vision-card .mv-icon { background: linear-gradient(135deg, #52c41a, #389e0d); }
.values-card .mv-icon { background: linear-gradient(135deg, #722ed1, #531dab); }
.talent-card .mv-icon { background: linear-gradient(135deg, #faad14, #d48806); }

.mv-card h3 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 16px;
}

.mv-card p {
  font-size: 14px;
  color: var(--text-secondary);
}

/* 核心优势 */
.advantages-section {
  padding: 48px 0;
  background: white;
}

.advantages-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  margin-top: 40px;
}

.advantage-card {
  padding: 32px 24px;
  border-radius: 8px;
  border: 1px solid #f0f0f0;
  text-align: center;
  transition: all 0.3s;
}

.advantage-card:hover {
  border-color: var(--primary-color);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.advantage-icon {
  width: 56px;
  height: 56px;
  margin: 0 auto 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
  color: white;
  font-size: 24px;
}

.advantage-card h3 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
}

.advantage-card p {
  font-size: 14px;
  color: var(--text-secondary);
}

/* 运行机制 */
.mechanism-section {
  padding: 48px 0;
  background: #fafafa;
}

.mechanism-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  margin-top: 40px;
}

.mechanism-card {
  padding: 32px 24px;
  border-radius: 8px;
  border: 1px solid #f0f0f0;
  background: white;
  text-align: center;
  transition: all 0.3s;
}

.mechanism-card:hover {
  border-color: var(--primary-color);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.mechanism-icon {
  width: 56px;
  height: 56px;
  margin: 0 auto 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
  color: white;
  font-size: 24px;
}

.mechanism-card h3 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
}

.mechanism-card p {
  font-size: 14px;
  color: var(--text-secondary);
}

/* 团队介绍 */
.team-section {
  padding: 48px 0;
  background: #fafafa;
}

.team-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  margin-top: 40px;
}

.team-card {
  background: white;
  padding: 24px;
  border-radius: 8px;
  text-align: center;
  border: 1px solid #f0f0f0;
  transition: all 0.3s;
}

.team-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border-color: #d9d9d9;
}

.team-avatar {
  width: 100px;
  height: 100px;
  margin: 0 auto 20px;
  border-radius: 50%;
  overflow: hidden;
  border: 2px solid #f0f0f0;
}

.team-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.team-card h3 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 8px;
}

.team-role {
  font-size: 14px;
  color: var(--primary-color);
  margin-bottom: 12px;
}

.team-desc {
  font-size: 13px;
  color: var(--text-secondary);
}

/* 发展历程 */
.timeline-section {
  padding: 48px 0;
  background: #fafafa;
}

.timeline {
  position: relative;
  max-width: 900px;
  margin: 40px auto 0;
}

.timeline::before {
  content: '';
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  width: 2px;
  height: 100%;
  background: #f0f0f0;
}

.timeline-item {
  position: relative;
  margin-bottom: 48px;
}

.timeline-item:last-child { margin-bottom: 0; }

.timeline-marker {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  width: 12px;
  height: 12px;
  background: white;
  border: 3px solid var(--primary-color);
  border-radius: 50%;
  z-index: 2;
}

.timeline-content {
  position: relative;
  width: 45%;
  padding: 24px;
  background: white;
  border-radius: 8px;
  border: 1px solid #f0f0f0;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.03);
}

.timeline-item:nth-child(odd) .timeline-content { left: 0; }
.timeline-item:nth-child(even) .timeline-content { left: 55%; }

.timeline-year {
  display: inline-block;
  padding: 4px 12px;
  background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
  color: white;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  margin-bottom: 12px;
}

.timeline-content h3 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
}

.timeline-content p {
  font-size: 14px;
  color: var(--text-secondary);
}

/* 页脚 */
.footer {
  background: #fafafa;
  color: var(--text-color);
  padding: 48px 0 24px;
  border-top: 1px solid #f0f0f0;
}

.footer-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 48px;
  margin-bottom: 40px;
}

.footer-section h3, .footer-section h4 {
  font-weight: 600;
  margin-bottom: 20px;
}

.footer-section p {
  color: var(--text-secondary);
  font-size: 14px;
  margin-bottom: 16px;
}

.social-links {
  display: flex;
  gap: 12px;
}

.social-links a {
  width: 32px;
  height: 32px;
  background: #f5f5f5;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  transition: all 0.3s;
}

.social-links a:hover {
  background: var(--primary-color);
  color: white;
}

.footer-section ul li {
  margin-bottom: 12px;
}

.footer-section ul li a {
  color: var(--text-secondary);
  font-size: 14px;
  transition: all 0.3s;
}

.footer-section ul li a:hover { color: var(--primary-color); }

.contact-info li {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
  color: var(--text-secondary);
  font-size: 14px;
}

.footer-bottom {
  text-align: center;
  padding-top: 24px;
  border-top: 1px solid #f0f0f0;
  color: var(--text-light);
  font-size: 14px;
}

.footer-bottom a {
  color: var(--text-light);
  transition: color 0.3s;
}

.footer-bottom a:hover { color: var(--primary-color); }
.footer-bottom span { margin: 0 16px; }

/* 响应式 */
@media (max-width: 1200px) {
  .team-grid, .advantages-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .mission-vision-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 1024px) {
  .container {
    padding: 0 16px;
  }

  .about-intro-grid {
    gap: 40px;
  }

  .about-intro-content h2 {
    font-size: 24px;
  }

  .mission-vision-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 992px) {
  .about-intro-grid, .mission-vision-grid, .advantages-grid, .team-grid, .mechanism-grid {
    grid-template-columns: 1fr;
  }

  .about-intro-image { order: -1; }

  .timeline::before, .timeline-marker { left: 30px; }
  .timeline-content {
    width: calc(100% - 80px);
    left: 80px !important;
  }
}

@media (max-width: 768px) {
  .page-banner {
    height: 200px;
  }

  .banner-content h1 {
    font-size: 28px;
  }

  .banner-content p {
    font-size: 14px;
  }

  .about-intro-grid {
    grid-template-columns: 1fr;
    gap: 32px;
  }

  .about-intro-image {
    order: 1;
  }

  .about-intro-content {
    order: 0;
  }

  .about-intro-content h2 {
    font-size: 22px;
  }

  .about-intro-content p {
    font-size: 14px;
  }

  .intro-text-block {
    padding-left: 16px;
  }

  .image-frame {
    padding: 8px;
  }

  .mission-vision-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
  }

  .advantages-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .mechanism-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .mv-card {
    padding: 24px 16px;
  }

  .mv-card h3 {
    font-size: 16px;
  }

  .mv-card p {
    font-size: 13px;
  }

  .advantage-card,
  .mechanism-card {
    padding: 24px 16px;
  }

  .advantage-card h3,
  .mechanism-card h3 {
    font-size: 15px;
  }

  .advantage-card p,
  .mechanism-card p {
    font-size: 13px;
  }

  .mv-icon {
    width: 56px;
    height: 56px;
    font-size: 24px;
  }

  .advantage-icon,
  .mechanism-icon {
    width: 48px;
    height: 48px;
    font-size: 20px;
  }

  .about-intro-section {
    padding: 48px 0;
  }

  .mission-vision-section,
  .advantages-section,
  .mechanism-section {
    padding: 36px 0;
  }

  .section-header {
    margin-bottom: 32px;
  }

  .section-header h2 {
    font-size: 22px;
  }

  .footer-content {
    gap: 32px;
  }

  .footer {
    padding: 36px 0 20px;
  }
}

@media (max-width: 480px) {
  .container {
    padding: 0 12px;
  }

  .page-banner {
    height: 160px;
  }

  .banner-content h1 {
    font-size: 22px;
  }

  .banner-content p {
    font-size: 13px;
  }

  .mission-vision-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .advantages-grid,
  .mechanism-grid {
    gap: 12px;
  }

  .about-intro-grid {
    gap: 24px;
  }

  .about-intro-content h2 {
    font-size: 20px;
  }

  .about-intro-content p {
    font-size: 13px;
  }

  .about-intro-section {
    padding: 36px 0;
  }

  .mission-vision-section,
  .advantages-section,
  .mechanism-section {
    padding: 28px 0;
  }

  .section-header {
    margin-bottom: 24px;
  }

  .section-header h2 {
    font-size: 20px;
  }

  .mv-card {
    padding: 20px 12px;
  }

  .mv-card h3 {
    font-size: 15px;
  }

  .advantage-card,
  .mechanism-card {
    padding: 20px 12px;
  }

  .advantage-card h3,
  .mechanism-card h3 {
    font-size: 14px;
  }

  .mv-icon {
    width: 48px;
    height: 48px;
    font-size: 20px;
    margin-bottom: 16px;
  }

  .advantage-icon,
  .mechanism-icon {
    width: 44px;
    height: 44px;
    font-size: 18px;
    margin-bottom: 16px;
  }

  .intro-text-block {
    padding-left: 12px;
  }

  .image-frame {
    padding: 6px;
  }

  .about-intro-image img {
    width: 100%;
  }

  .footer-content {
    grid-template-columns: 1fr;
    gap: 24px;
  }

  .footer {
    padding: 28px 0 16px;
  }
}

/* 滚动动画效果 */
.animate-on-scroll {
  opacity: 0;
  transform: translateX(-50px);
  transition: opacity 0.8s ease, transform 0.8s ease;
}
.animate-on-scroll.show {
  opacity: 1;
  transform: translateX(0);
}
/* 右侧进入 */
.animate-on-scroll.right {
  transform: translateX(50px);
}
.animate-on-scroll.right.show {
  transform: translateX(0);
}
/* 延迟 */
.animate-on-scroll.delay-1 { transition-delay: 0.2s; }
.animate-on-scroll.delay-2 { transition-delay: 0.4s; }
.animate-on-scroll.delay-3 { transition-delay: 0.6s; }
.animate-on-scroll.delay-4 { transition-delay: 0.8s; }
.animate-on-scroll.delay-5 { transition-delay: 1.0s; }
.animate-on-scroll.delay-6 { transition-delay: 1.2s; }
</style>