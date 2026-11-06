<template>
  <div class="admin-chat-container">
    <div class="admin-chat-layout">
      <div class="sidebar">
        <div class="sidebar-header">
          <h3>当前咨询用户</h3>
          <span class="badge">{{ filteredUsers.length }}{{ searchInput.trim() ? '/' + activeUsers.length : '' }}</span>
        </div>

        <div class="room-join-box">
          <input
            v-model="searchInput"
            type="text"
            placeholder="输入会话ID/用户名/手机号查找"
          />
          <button class="el-button" @click="refreshSessions">刷新</button>
        </div>

        <div class="session-list">
          <div
            v-for="user in filteredUsers"
            :key="user.session_id"
            :class="['session-item', { active: currentUser && currentUser.session_id === user.session_id }]"
            @click="selectUser(user)"
          >
            <div class="session-header">
              <div class="session-title">
                <span :class="['online-indicator', user.isOnline ? 'online' : 'offline']" :title="user.isOnline ? '在线' : '离线'"></span>
                <span class="user-name" style="margin-left: 6px; font-weight: 500;">
                  {{ user.name }}
                </span>
                <span v-if="user.unreadCount > 0" class="unread-badge">{{ user.unreadCount > 99 ? '99+' : user.unreadCount }}</span>
              </div>
              <div style="display: flex; align-items: center; gap: 8px;">
                <span class="session-time">{{ user.lastTime }}</span>
              </div>
            </div>
            <div class="session-preview">{{ user.lastMessage }}</div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <div class="session-info">会话 ID: {{ user.isPending ? '等待分配...' : user.session_id.substring(0, 8) + '...' }}</div>
              <span v-if="user.isPending" class="el-tag danger">等待接收</span>
              <span v-else-if="user.needsHuman" class="el-tag warning">等待接手</span>
              <span v-else-if="user.isClosed" class="el-tag info">已结束</span>
              <span v-else class="el-tag success">进行中</span>
            </div>
          </div>
        </div>
      </div>

      <div class="chat-main">
        <template v-if="currentUser">
          <div class="service-header">
            <div class="header-content">
              <div class="service-title">
                <h2>
                  {{ currentUser.name }}
                  <span :class="['user-online-dot', currentUser.isOnline ? 'online' : 'offline']" :title="currentUser.isOnline ? '用户在线' : '用户离线'"></span>
                  <span class="user-online-text" :style="{color: currentUser.isOnline ? '#52c41a' : '#999'}">{{ currentUser.isOnline ? '在线' : '离线' }}</span>
                </h2>
                <div class="service-status">
                  <span class="agent-info">完整会话号：{{ currentUser.session_id }}</span>
                </div>
              </div>
              <div class="header-actions">
                <button class="el-button" @click="showRealNameInfo(currentUser)" style="border-color: #1890ff; color: #1890ff;">
                  <i class="fas fa-id-card"></i> 查看实名信息
                </button>
                <button v-if="currentUser.referenceType && currentUser.referenceId && !currentUser.isClosed" class="el-button" @click="openReferenceDetail" style="border-color: #67c23a; color: #67c23a;">
                  <i class="fas fa-info-circle"></i> {{ currentUser.referenceType === 'achievement' ? '查看成果详情' : '查看需求详情' }}
                </button>
                <button v-if="currentUser.needsHuman" class="el-button danger" @click="acceptRequest" :disabled="isProcessing">
                  <i class="fas fa-headset"></i> {{ currentUser.isPending ? '接受请求' : '接手此会话' }}
                </button>
                <button v-if="!currentUser.needsHuman && !isSessionClosed" class="el-button" @click="closeSession" :disabled="isProcessing" style="border-color: #f56c6c; color: #f56c6c;">
                  <i class="fas fa-times"></i> 关闭会话
                </button>
              </div>
            </div>
          </div>

          <div class="chat-area">
            <div class="messages-container" ref="chatContentRef">
              <div
                v-for="(msg, index) in chatHistory"
                :key="index"
                :class="[
                  'message-wrapper',
                  msg.from === 'admin' ? 'admin-message' : msg.from === 'system' ? 'system-message-row' : msg.from === 'bot' ? 'bot-message' : 'user-message'
                ]"
              >
                <template v-if="msg.from === 'system'">
                  <div class="system-message">{{ msg.text }}</div>
                </template>

                <template v-else>
                  <div class="message-avatar">
                    {{ msg.from === 'admin' ? '我' : (msg.from === 'bot' ? '机' : '客') }}
                  </div>

                  <div class="message-bubble">
                    <div class="message-header">
                      <span class="sender-name">
                        {{ msg.from === 'admin' ? '客服 (我)' : msg.from === 'bot' ? '机器人' : '用户' }}
                      </span>
                      <span class="message-time">{{ msg.time }}</span>
                    </div>
                    <div class="message-content" v-if="msg.from === 'bot'" v-html="msg.text"></div>
                    <div class="message-content" v-else>{{ msg.text }}</div>
                    <div v-if="msg.from === 'admin'" class="message-status">
                      <span>✓</span><span>已发送</span>
                    </div>
                  </div>
                </template>
              </div>
            </div>

            <div class="input-area">
              <div class="input-container">
                <div class="el-input">
                  <textarea
                    v-model="replyText"
                    :placeholder="currentUser.isPending ? '请先接受请求后再回复...' : isSessionClosed ? '会话已结束，无法继续回复' : '输入回复内容，按 Ctrl+Enter 发送...'"
                    :disabled="currentUser.isPending || isSessionClosed"
                    @keydown.ctrl.enter.prevent="sendReply"
                  ></textarea>
                </div>
                
                <div class="input-actions">
                  <div class="action-left">
                    <div class="file-upload">
                      <button class="file-upload-btn" title="暂未开放">上传文件</button>
                    </div>
                    <button class="file-upload-btn" style="border:none; background:transparent; font-size:16px;">
                      <i class="fas fa-image"></i>
                    </button>
                    <button class="el-button success" @click="sendReply" :disabled="!replyText.trim() || currentUser.isPending || isSessionClosed">
                      发送
                    </button>
                  </div>
                  
                  <div class="action-right">
                    <span class="connection-status">
                      <span :style="{ color: isConnected ? '#67c23a' : '#f56c6c', marginRight: '4px' }">●</span>
                      {{ isConnected ? '已连接 Socket' : '连接断开' }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </template>

        <div v-else class="empty-state">
          <i class="fas fa-comments"></i>
          <p>请先在左侧选择或等待一个用户请求</p>
        </div>
      </div>
    </div>
  </div>

  <!-- 实名信息弹窗 -->
  <el-dialog v-model="realNameDialogVisible" title="实名信息" width="400px">
    <div class="realname-dialog-content">
      <div class="realname-row">
        <span class="realname-label">用户昵称：</span>
        <span class="realname-value">{{ realNameTarget?.name || '未知' }}</span>
      </div>
      <div class="realname-row">
        <span class="realname-label">真实姓名：</span>
        <span class="realname-value">{{ realNameTarget?.realName || '未填写' }}</span>
      </div>
      <div class="realname-row">
        <span class="realname-label">身份证号：</span>
        <span class="realname-value">{{ realNameTarget?.idCard || '未填写' }}</span>
      </div>
      <div class="realname-row">
        <span class="realname-label">手机号：</span>
        <span class="realname-value">{{ realNameTarget?.phone || '未填写' }}</span>
      </div>
    </div>
  </el-dialog>

  <!-- 可移动成果/需求详情弹窗 -->
  <div v-if="referenceDialog.visible" class="reference-overlay" @click="closeReferenceDetail"></div>
  <div v-if="referenceDialog.visible" class="reference-dialog" ref="referenceDialogRef"
       :style="{ left: referenceDialog.x + 'px', top: referenceDialog.y + 'px' }">
    <div class="reference-dialog-header" @mousedown="startDragDialog">
      <span>{{ referenceDialog.type === 'achievement' ? '成果详情' : '需求详情' }}</span>
      <button class="reference-dialog-close" @click="closeReferenceDetail">&times;</button>
    </div>
    <div class="reference-dialog-body">
      <div v-if="referenceDialog.loading" class="reference-loading">加载中...</div>
      <template v-else-if="referenceDialog.data">
        <!-- 成果详情 -->
        <template v-if="referenceDialog.type === 'achievement'">
          <fieldset class="ref-fieldset">
            <legend>一、成果基本信息</legend>
            <div class="ref-form-grid">
              <div class="ref-form-item full-width">
                <label>成果名称：</label>
                <span class="ref-readonly-field" style="font-weight: bold; color: #2196f3;">{{ referenceDialog.data.title || '-' }}</span>
              </div>
              <div class="ref-form-item">
                <label>企业名称/持有人：</label>
                <span class="ref-readonly-field">{{ referenceDialog.data.owner || '-' }}</span>
              </div>
              <div class="ref-form-item">
                <label>成果编号：</label>
                <span class="ref-readonly-field">{{ referenceDialog.data.id || '-' }}</span>
              </div>
              <div class="ref-form-item">
                <label>技术领域：</label>
                <span class="ref-readonly-field">{{ referenceDialog.data.field || '-' }}</span>
              </div>
              <div class="ref-form-item">
                <label>技术成熟度：</label>
                <span class="ref-readonly-field" style="font-weight: bold; color: #2196f3;">{{ referenceDialog.data.maturity || '-' }}</span>
              </div>
              <div class="ref-form-item full-width">
                <label>拟转化方式：</label>
                <span class="ref-readonly-field">{{ referenceDialog.data.transferDisplay || '-' }}</span>
              </div>
            </div>
          </fieldset>

          <fieldset class="ref-fieldset">
            <legend>二、成果描述</legend>
            <div class="ref-form-item full-width" style="margin-bottom: 15px;">
              <label>成果摘要：</label>
              <div class="ref-readonly-field" style="height: auto;">{{ referenceDialog.data.summary || '-' }}</div>
            </div>
            <div class="ref-form-item full-width" style="margin-bottom: 15px;">
              <label>技术优势描述：</label>
              <div class="ref-readonly-field" style="height: auto;">{{ referenceDialog.data.advantage || '-' }}</div>
            </div>
            <div class="ref-form-grid">
              <div class="ref-form-item">
                <label>创新性评价：</label>
                <span class="ref-readonly-field">{{ referenceDialog.data.innovation || '-' }}</span>
              </div>
              <div class="ref-form-item">
                <label>核心技术指标：</label>
                <span class="ref-readonly-field">{{ referenceDialog.data.indicator || '-' }}</span>
              </div>
              <div class="ref-form-item full-width">
                <label>与现有技术相比的优势：</label>
                <div class="ref-readonly-field" style="height: auto;">{{ referenceDialog.data.compare || '-' }}</div>
              </div>
              <div class="ref-form-item full-width">
                <label>获得的知识产权情况：</label>
                <div class="ref-readonly-field" style="height: auto;">{{ referenceDialog.data.ipr || '-' }}</div>
              </div>
            </div>
          </fieldset>

          <fieldset class="ref-fieldset">
            <legend>三、成果转化期望</legend>
            <div class="ref-form-item full-width">
              <label>合作方式偏好及财务预期：</label>
              <span class="ref-readonly-field" style="color: #faad14; font-weight: bold;">{{ referenceDialog.data.collab || '-' }}</span>
            </div>
            <div class="ref-form-item full-width">
              <label>期望完成转化时间：</label>
              <span class="ref-readonly-field">{{ referenceDialog.data.deadline || '-' }}</span>
            </div>
          </fieldset>
        </template>

        <!-- 需求详情 -->
        <template v-else>
          <fieldset class="ref-fieldset">
            <legend>一、需求基本信息</legend>
            <div class="ref-form-grid">
              <div class="ref-form-item full-width">
                <label>需求名称：</label>
                <span class="ref-readonly-field">{{ referenceDialog.data.title || '-' }}</span>
              </div>
              <div class="ref-form-item">
                <label>企业名称：</label>
                <span class="ref-readonly-field">{{ referenceDialog.data.org || '-' }}</span>
              </div>
              <div class="ref-form-item">
                <label>需求编号：</label>
                <span class="ref-readonly-field">{{ referenceDialog.data.id || '-' }}</span>
              </div>
              <div class="ref-form-item">
                <label>所属地区：</label>
                <span class="ref-readonly-field">{{ referenceDialog.data.region || '-' }}</span>
              </div>
              <div class="ref-form-item">
                <label>技术领域：</label>
                <span class="ref-readonly-field">{{ referenceDialog.data.field || '-' }}</span>
              </div>
              <div class="ref-form-item">
                <label>需求类型：</label>
                <span class="ref-readonly-field">{{ referenceDialog.data.type || '-' }}</span>
              </div>
              <div class="ref-form-item">
                <label>供需状态：</label>
                <span class="ref-readonly-field" style="font-weight: bold; color: #2196f3;">{{ referenceDialog.data.status || '-' }}</span>
              </div>
              <div class="ref-form-item">
                <label>项目预算：</label>
                <span class="ref-readonly-field">{{ referenceDialog.data.budget || '-' }}</span>
              </div>
            </div>
          </fieldset>

          <fieldset class="ref-fieldset">
            <legend>二、需求描述</legend>
            <div class="ref-form-item full-width" style="margin-bottom: 15px;">
              <label>需求概述：</label>
              <div class="ref-readonly-field" style="height: auto;">{{ referenceDialog.data.overview || '-' }}</div>
            </div>
            <div class="ref-form-item full-width">
              <label>期望解决的问题：</label>
              <div class="ref-readonly-field" style="height: auto;">{{ referenceDialog.data.issues || '-' }}</div>
            </div>
          </fieldset>
        </template>
      </template>
      <div v-else class="reference-loading">未找到数据</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted, onUnmounted } from 'vue';
import { io } from 'socket.io-client';
import { ElNotification, ElDialog } from 'element-plus';
import request from '@/utils/request';

const BASE_URL = ''; // 空字符串=同源，生产环境通过 Nginx 代理 WebSocket

const searchInput = ref('');
const filteredUsers = computed(() => {
  const keyword = searchInput.value.trim().toLowerCase();
  if (!keyword) return activeUsers.value;
  return activeUsers.value.filter(u => {
    // 支持按会话ID、用户名、手机号、真实姓名搜索
    const sid = (u.session_id || '').toLowerCase();
    const name = (u.name || '').toLowerCase();
    const phone = (u.phone || '').toLowerCase();
    const realName = (u.realName || '').toLowerCase();
    return sid.includes(keyword) || name.includes(keyword) || phone.includes(keyword) || realName.includes(keyword);
  });
});
const activeUsers = ref([]);
const currentUser = ref(null);
const replyText = ref('');
const chatHistory = ref([]);
const chatContentRef = ref(null);
const isConnected = ref(false);
const realNameDialogVisible = ref(false);
const realNameTarget = ref(null);
const isSessionClosed = ref(false);
const isProcessing = ref(false);

const referenceDialogRef = ref(null);

// 可移动参考详情弹窗
const referenceDialog = ref({
  visible: false,
  type: '',      // 'achievement' | 'demand'
  data: null,
  loading: false,
  x: 100,
  y: 80,
  dragging: false,
  dragStartX: 0,
  dragStartY: 0,
  dragOrigX: 0,
  dragOrigY: 0
});

const showRealNameInfo = (user) => {
  realNameTarget.value = user;
  realNameDialogVisible.value = true;
};

let socket = null;
let tempBotHistory = []; // 用于临时存储机器人的历史记录
let currentAgentId = null; // 当前客服自己的ID

const formatTime = (isoString) => {
  if (!isoString) return '';
  const date = new Date(isoString);
  return `${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
};
const formatNow = () => formatTime(new Date().toISOString());

const scrollToBottom = async () => {
  await nextTick();
  if (chatContentRef.value) {
    chatContentRef.value.scrollTop = chatContentRef.value.scrollHeight;
  }
};

// 打开参考详情弹窗
const openReferenceDetail = async () => {
  const type = currentUser.value?.referenceType;
  const id = currentUser.value?.referenceId;
  if (!type || !id) return;

  referenceDialog.value.visible = true;
  referenceDialog.value.type = type;
  referenceDialog.value.loading = true;
  referenceDialog.value.data = null;

  try {
    const apiPath = type === 'achievement'
      ? `/api/publish/achievement/${id}`
      : `/api/publish/requirement/${id}`;
    const response = await request.get(apiPath);
    if (response.code === 200 && response.data) {
      const raw = response.data;
      if (type === 'achievement') {
        // 按成果中心抽屉格式转换字段
        const fieldArr = raw.technologyFields || raw.tech_fields || [];
        const transferArr = raw.transferMethods || raw.transfer_methods || [];
        const pref = raw.transfer_preference || {};
        referenceDialog.value.data = {
          title: raw.title || raw.achievement_name,
          owner: raw.holder || raw.owner,
          id: raw.achievementNumber || raw.achievement_code,
          field: (() => { const f = raw.tech_fields_other || raw.otherTechnologyField || ''; let d = fieldArr.length > 0 ? fieldArr.join('、') : ''; if (f && f.trim()) d += (d ? '、' : '') + '其他：' + f; return d || '其他'; })(),
          maturity: raw.maturity || raw.tech_maturity || '未知',
          transferDisplay: (() => { const o = raw.transfer_methods_other || raw.otherTransferMethod || ''; let d = transferArr.length > 0 ? transferArr.join('、') : ''; if (o && o.trim()) d += (d ? '、' : '') + '其他：' + o; return d || '未指定'; })(),
          summary: raw.summary || '',
          advantage: raw.advantages || '',
          innovation: raw.innovationLevel || '',
          indicator: raw.coreTechnicalIndicators || '',
          compare: raw.advantages || '',
          ipr: raw.intellectualProperties || '',
          collab: formatTransferPreference(pref),
          deadline: raw.expectedCompletionDate || '未指定'
        };
      } else {
        // 按需求中心抽屉格式转换字段
        const techFields = raw.tech_fields || [];
        const demandTypes = raw.demand_types || [];
        const desc = raw.description || {};
        const region = raw.region || {};
        const regionStr = region.province ? (region.province + (region.city && region.city !== region.province ? region.city : '')) : (region || '');
        referenceDialog.value.data = {
          title: raw.demand_name,
          org: raw.company_name,
          id: raw.demand_code,
          region: regionStr,
          field: (() => { const o = raw.tech_fields_other || ''; let d = techFields.length > 0 ? techFields.join('、') : ''; if (o && o.trim()) d += (d ? '、' : '') + '其他：' + o; return d || '其他'; })(),
          type: (() => { const o = raw.demand_types_other || ''; let d = demandTypes.length > 0 ? demandTypes.join('、') : ''; if (o && o.trim()) d += (d ? '、' : '') + '其他：' + o; return d || '其他'; })(),
          status: '待对接',
          budget: desc.budget ? `${desc.budget}万元` : '未指定',
          overview: desc.overview || '',
          issues: desc.target_problems || ''
        };
      }
    }
  } catch (err) {
    console.error('获取参考详情失败:', err);
  } finally {
    referenceDialog.value.loading = false;
  }
};

const formatTransferPreference = (preference) => {
  if (!preference) return '未指定';
  const parts = [];
  if (preference.preferred_method) parts.push(preference.preferred_method);
  if (preference.tech_transfer?.enabled && preference.tech_transfer.expected_fee)
    parts.push(`预期费用：${preference.tech_transfer.expected_fee}万元`);
  else if (preference.tech_license?.enabled && preference.tech_license.expected_fee)
    parts.push(`预期费用：${preference.tech_license.expected_fee}万元`);
  else if (preference.tech_investment?.enabled && preference.tech_investment.valuation)
    parts.push(`估值：${preference.tech_investment.valuation}万元`);
  if (preference.other) parts.push(`其他：${preference.other}`);
  return parts.length > 0 ? parts.join('，') : '未指定';
};

const closeReferenceDetail = () => {
  referenceDialog.value.visible = false;
};

const startDragDialog = (e) => {
  referenceDialog.value.dragging = true;
  referenceDialog.value.dragStartX = e.clientX;
  referenceDialog.value.dragStartY = e.clientY;
  referenceDialog.value.dragOrigX = referenceDialog.value.x;
  referenceDialog.value.dragOrigY = referenceDialog.value.y;
  document.addEventListener('mousemove', doDragDialog);
  document.addEventListener('mouseup', stopDragDialog);
};

const doDragDialog = (e) => {
  if (!referenceDialog.value.dragging) return;
  const dx = e.clientX - referenceDialog.value.dragStartX;
  const dy = e.clientY - referenceDialog.value.dragStartY;
  referenceDialog.value.x = referenceDialog.value.dragOrigX + dx;
  referenceDialog.value.y = referenceDialog.value.dragOrigY + dy;
};

const stopDragDialog = () => {
  referenceDialog.value.dragging = false;
  document.removeEventListener('mousemove', doDragDialog);
  document.removeEventListener('mouseup', stopDragDialog);
};


const initSocket = () => {
  const token = localStorage.getItem('token') || ''; 
  socket = io(BASE_URL, {
    transports: ['websocket'],
    query: { token }
  });

  socket.on('connect', () => {
    isConnected.value = true;
    console.log('✅ 客服管理后台 WebSocket 已连接, sid:', socket.id);
    refreshSessions();
  });

  socket.on('connected', (data) => {
    if (data.user_id) {
      currentAgentId = data.user_id;
    }
  });

  socket.on('connect_error', (err) => {
    console.error('❌ 客服管理后台 WebSocket 连接失败:', err.message);
  });

  socket.on('disconnect', () => {
    isConnected.value = false;
    console.log('❌ 客服管理后台 WebSocket 已断开');
  });

  socket.on('customer_service_sessions', (data) => {
    if (!data || !data.sessions) return;
    // 保存本地已添加的 pending 项，防止服务端响应较晚时的时序竞争
    const localPending = activeUsers.value.filter(u => u.isPending);
    const allEntries = data.sessions.map(session => ({
      session_id: session.id,
      user_id: session.user_id,
      realName: session.user_real_name || '',
      idCard: session.user_id_card || '',
      phone: session.user_phone || '',
      // 这里的 user_name 通常就是前端的 room_id (手机号/用户名)
      name: session.user_name || session.user_phone || `用户 ${session.user_id}`,
      lastMessage: session.status === 'pending' ? '等待客服接收...' : (session.last_message?.content || '暂无消息'),
      lastTime: formatTime(session.last_message?.created_at || session.updated_at),
      needsHuman: session.status === 'waiting' || session.status === 'pending',
      isPending: session.status === 'pending',
      isClosed: session.status === 'closed',
      isOnline: session.user_online || false,
      unreadCount: session.unread_count || 0,
      referenceType: session.reference_type || null,
      referenceId: session.reference_id || null,
      _status: session.status,
      _lastTimeRaw: session.last_message?.created_at || session.updated_at
    }));
    // 按 user_id 去重：每个用户只保留最佳会话（活跃 > 等待 > 待处理 > 最近关闭）
    const statusPriority = { 'active': 0, 'waiting': 1, 'pending': 2, 'closed': 3 };
    const userMap = new Map();
    allEntries.forEach(entry => {
      const existing = userMap.get(entry.user_id);
      if (!existing) {
        userMap.set(entry.user_id, entry);
      } else {
        const ep = statusPriority[entry._status] ?? 99;
        const xp = statusPriority[existing._status] ?? 99;
        if (ep < xp || (ep === xp && entry._lastTimeRaw > existing._lastTimeRaw)) {
          userMap.set(entry.user_id, entry);
        }
      }
    });
    activeUsers.value = Array.from(userMap.values());
    // 恢复本地 pending 项（服务端响应中可能尚未包含这些 pending 请求）
    localPending.forEach(pending => {
      const exists = activeUsers.value.find(u => u.user_id === pending.user_id);
      if (!exists) {
        activeUsers.value.unshift(pending);
      }
    });
  });

  socket.on('customer_service_session_created', (session) => {
    const userId = session.user_id;
    // 保存旧 pending 项的用户信息，用于构建新会话卡片
    const oldItem = activeUsers.value.find(u => u.user_id === userId);
    const wasCurrentUser = currentUser.value && currentUser.value.user_id === userId;

    // 移除旧的 pending 项（用 user_id 匹配，因为乐观更新已改了 isPending）
    const pendingIdx = activeUsers.value.findIndex(u => u.user_id === userId);
    if (pendingIdx !== -1) {
      activeUsers.value.splice(pendingIdx, 1);
    }

    // 用真实会话数据替换 pending 项
    const newSession = {
      session_id: session.id,
      user_id: userId,
      name: oldItem?.name || `用户 ${userId}`,
      lastMessage: '暂无消息',
      lastTime: formatTime(session.updated_at),
      needsHuman: false,
      isPending: false,
      isClosed: false,
      isOnline: oldItem?.isOnline || false,
      idCard: oldItem?.idCard || '',
      phone: oldItem?.phone || '',
      realName: oldItem?.realName || '',
      unreadCount: 0,
      referenceType: session.reference_type || oldItem?.referenceType || null,
      referenceId: session.reference_id || oldItem?.referenceId || null
    };
    activeUsers.value.unshift(newSession);

    // 如果当前选中的是刚被接受的 pending 用户，自动切换到新会话
    if (wasCurrentUser) {
      selectUser(newSession);
    }

    // 与服务端同步确保列表一致
    refreshSessions();

    ElNotification({
      title: '新会话',
      message: `有新会话: ${session.user_name || `用户${userId}`}`,
      type: 'success'
    });
  });

  socket.on('pending_human_request', (data) => {
    console.log('📩 收到 pending_human_request 事件:', data);
    // 仅当用户没有活跃的（非关闭、非 pending）会话时才添加 pending 项
    const hasActiveSession = activeUsers.value.find(u => u.user_id === data.user_id && !u.isPending && !u.isClosed);
    if (!hasActiveSession) {
      // 移除同用户旧的 closed/pending 项，避免重复
      const oldIdx = activeUsers.value.findIndex(u => u.user_id === data.user_id);
      if (oldIdx !== -1) activeUsers.value.splice(oldIdx, 1);
      activeUsers.value.unshift({
        session_id: 'pending_' + data.user_id,
        user_id: data.user_id,
        name: data.username,
        lastMessage: '等待客服接收...',
        lastTime: formatTime(data.timestamp),
        needsHuman: true,
        isPending: true,
        isClosed: false,
        isOnline: true,
        idCard: '',
        phone: data.phone || '',
        unreadCount: 0,
        referenceType: data.reference_type || null,
        referenceId: data.reference_id || null
      });
    }
    ElNotification({
      title: '转人工请求',
      message: '新用户请求人工客服',
      type: 'warning',
      customClass: 'clickable-notification',
      onClick: () => {
        const found = activeUsers.value.find(u => u.session_id === 'pending_' + data.user_id);
        if (found) selectUser(found);
      }
    });

    // 兜底：与服务端同步会话列表，防止本地遗漏 pending 项
    refreshSessions();
  });

  // 🌟 核心优化：将机器人历史记录和人工记录合并展示！
  socket.on('customer_service_messages', (data) => {
    if (currentUser.value && data.session_id === currentUser.value.session_id) {
      const humanHistory = data.messages.map(msg => ({
        from: msg.sender_type === 'agent' ? 'admin' : 'user',
        text: msg.content,
        time: formatTime(msg.created_at),
        _msgId: msg.id || null
      }));
      
      // 合并两段历史记录，并在中间加一条系统提示隔开
      chatHistory.value = [
        ...tempBotHistory,
        { from: 'system', text: '--- 以上为机器人对话历史 ---' },
        { from: 'system', text: '--- 以下为人工客服专属会话 ---' },
        ...humanHistory
      ];
      scrollToBottom();
    }
  });

  socket.on('user_all_history', (data) => {
    if (!currentUser.value) return;
    const allMessages = [];
    // 机器人消息
    (data.bot_messages || []).forEach(msg => {
      allMessages.push({
        from: msg.sender === 'bot' ? 'bot' : (msg.sender === 'system' ? 'system' : 'user'),
        text: msg.content,
        time: formatTime(msg.created_at),
        isBotHistory: true
      });
    });
    // 人工客服消息
    if (data.session_messages && data.session_messages.length > 0) {
      let displayMsgs = data.session_messages;

      // 已结束的会话：只显示该会话及之前会话的消息，不混入后续会话的记录
      if (currentUser.value.isClosed) {
        const targetSid = currentUser.value.session_id;
        let lastTargetIdx = -1;
        for (let i = 0; i < displayMsgs.length; i++) {
          if (displayMsgs[i].session_id === targetSid) {
            lastTargetIdx = i;
          } else if (lastTargetIdx >= 0) {
            break; // 已越过当前会话的消息块
          }
        }
        if (lastTargetIdx >= 0) {
          displayMsgs = displayMsgs.slice(0, lastTargetIdx + 1);
        }
      }

      if (displayMsgs.length > 0) {
        allMessages.push({ from: 'system', text: '--- 人工客服聊天记录 ---' });
        displayMsgs.forEach(msg => {
          allMessages.push({
            from: msg.sender_type === 'agent' ? 'admin' : 'user',
            text: msg.content,
            time: formatTime(msg.created_at),
            _msgId: msg.message_id || null
          });
        });
      }
    }
    chatHistory.value = allMessages;
    // 历史加载完毕，确保当前选中会话未读数清零
    if (currentUser.value) {
      const cur = activeUsers.value.find(u => u.session_id === currentUser.value.session_id);
      if (cur) cur.unreadCount = 0;
    }
    scrollToBottom();
  });

  socket.on('new_customer_service_message', (msg) => {
    if (currentUser.value && msg.session_id === currentUser.value.session_id) {
      // 用服务端 message_id 去重，解决相同内容重复发送被误拦截和多socket连接导致消息重复的问题
      const exists = msg.id && chatHistory.value.some(m => m._msgId === msg.id);
      if (!exists) {
        chatHistory.value.push({
          from: msg.sender_type === 'agent' ? 'admin' : 'user',
          text: msg.content,
          time: formatTime(msg.created_at),
          _msgId: msg.id || null
        });
        scrollToBottom();
      }
      // 正在查看该会话，清零未读数
      const cur = activeUsers.value.find(u => u.session_id === msg.session_id);
      if (cur) cur.unreadCount = 0;
    }
    const index = activeUsers.value.findIndex(u => u.session_id === msg.session_id);
    if (index !== -1) {
      const user = activeUsers.value[index];
      user.lastMessage = msg.content;
      user.lastTime = formatTime(msg.created_at);
      activeUsers.value.splice(index, 1);
      activeUsers.value.unshift(user);
    } else {
      refreshSessions();
    }
  });

  socket.on('session_closed', (data) => {
    // 始终更新侧边栏卡片状态（无论是否正在查看）
    const cardIdx = activeUsers.value.findIndex(u => u.session_id === data.session_id);
    if (cardIdx !== -1) {
      activeUsers.value[cardIdx].isClosed = true;
      activeUsers.value[cardIdx].needsHuman = false;
      activeUsers.value[cardIdx].isPending = false;
      activeUsers.value[cardIdx].referenceType = null;
      activeUsers.value[cardIdx].referenceId = null;
    }
    // 如果正在查看该会话，同步更新聊天界面
    if (currentUser.value && data.session_id === currentUser.value.session_id) {
      if (data.initiated_by === 'user') {
        chatHistory.value.push({ from: 'system', text: '用户已结束会话，无法继续回复' });
        isSessionClosed.value = true;
        // 清除对接参考信息，隐藏查看详情按钮
        currentUser.value.referenceType = null;
        currentUser.value.referenceId = null;
      } else {
        currentUser.value = null;
        chatHistory.value = [];
        isSessionClosed.value = false;
      }
    }
    refreshSessions();
  });

  // 监听会话被管理员删除
  socket.on('session_deleted', (data) => {
    if (!data) return;
    if (data.session_id) {
      // 单条删除：只移除指定会话
      const idx = activeUsers.value.findIndex(u => u.session_id === data.session_id);
      if (idx !== -1) activeUsers.value.splice(idx, 1);
      if (currentUser.value && data.session_id === currentUser.value.session_id) {
        currentUser.value = null;
        chatHistory.value = [];
        isSessionClosed.value = false;
      }
    } else if (data.user_id) {
      // 批量删除：移除该用户的所有会话
      activeUsers.value = activeUsers.value.filter(u => u.user_id !== data.user_id);
      if (currentUser.value && currentUser.value.user_id === data.user_id) {
        currentUser.value = null;
        chatHistory.value = [];
        isSessionClosed.value = false;
      }
    }
  });

  socket.on('customer_session_refresh', (data) => {
    // 更新侧边栏卡片（最新消息预览、移到最顶、未读数）
    const idx = activeUsers.value.findIndex(u => u.session_id === data.session_id);
    if (idx !== -1) {
      const user = activeUsers.value[idx];
      if (data.last_message) {
        user.lastMessage = data.last_message.content;
        user.lastTime = formatTime(data.last_message.created_at);
      }
      // 同步对接参考信息
      if (data.reference_type) user.referenceType = data.reference_type;
      if (data.reference_id) user.referenceId = data.reference_id;
      // 如果客服正在查看该会话，不应显示红点
      if (currentUser.value && currentUser.value.session_id === data.session_id) {
        user.unreadCount = 0;
        // 同步参考信息到当前选中用户
        if (data.reference_type) currentUser.value.referenceType = data.reference_type;
        if (data.reference_id) currentUser.value.referenceId = data.reference_id;
      } else {
        user.unreadCount = data.unread_count;
      }
      activeUsers.value.splice(idx, 1);
      activeUsers.value.unshift(user);
    } else {
      refreshSessions();
    }
    // 不在此处触发全量历史重载；new_customer_service_message 已负责实时展示
  });

  socket.on('user_status_update', (data) => {
    const user = activeUsers.value.find(u => u.user_id === data.user_id);
    if (user) {
      user.isOnline = (data.online_status === 'online');
    }
  });
};

const refreshSessions = () => {
  if (socket && isConnected.value) socket.emit('get_customer_service_sessions');
};

const selectUser = (user) => {
  isSessionClosed.value = user.isClosed || false;
  currentUser.value = user;
  user.unreadCount = 0;  // 选中后清零未读数

  // 通过新事件获取用户所有历史记录（机器人+所有客服会话）
  socket.emit('get_user_all_history', {
    user_id: user.user_id
  });

  // 加入当前会话房间以接收实时消息（pending 请求没有真实会话）
  if (!user.isPending) {
    socket.emit('join_customer_service_session', { session_id: user.session_id });
  }
};

const closeSession = () => {
  if (!socket || !currentUser.value || isProcessing.value) return;
  isProcessing.value = true;
  const closedSessionId = currentUser.value.session_id;
  socket.emit('close_customer_service_session', {
    session_id: closedSessionId
  });
  // 立即更新左侧卡片状态
  const idx = activeUsers.value.findIndex(u => u.session_id === closedSessionId);
  if (idx !== -1) {
    activeUsers.value[idx].isClosed = true;
    activeUsers.value[idx].needsHuman = false;
    activeUsers.value[idx].isPending = false;
  }
  currentUser.value = null;
  chatHistory.value = [];
  isSessionClosed.value = false;
  // 与服务端同步确保列表一致
  refreshSessions();
  setTimeout(() => { isProcessing.value = false; }, 1000);
};

const acceptRequest = () => {
  if (!currentUser.value || !socket || isProcessing.value) return;
  isProcessing.value = true;
  if (currentUser.value.isPending) {
    // 接受 pending 请求 — 通知服务器创建会话
    socket.emit('accept_human_request', {
      user_id: currentUser.value.user_id
    });
    // 乐观更新：立即隐藏按钮，防止重复点击
    currentUser.value.needsHuman = false;
    currentUser.value.isPending = false;
    // 等待服务器响应后刷新，超时保护防止按钮一直禁用
    setTimeout(() => { isProcessing.value = false; }, 3000);
  } else {
    const msgText = `您好，人工客服(编号: ${currentAgentId})已接入，请详细描述您遇到的问题。`;
    socket.emit('customer_service_message', {
      session_id: currentUser.value.session_id,
      content: msgText
    });
    chatHistory.value.push({ from: 'admin', text: msgText, time: formatNow() });
    currentUser.value.needsHuman = false;
    currentUser.value.lastMessage = msgText;
    isSessionClosed.value = false;
    scrollToBottom();
    setTimeout(() => { isProcessing.value = false; }, 1000);
  }
};

const sendReply = () => {
  if (!replyText.value.trim() || !currentUser.value || !socket) return;
  if (isSessionClosed.value) return;
  if (currentUser.value.isPending) return;  // 未接受请求不能发送
  const text = replyText.value.trim();
  socket.emit('customer_service_message', {
    session_id: currentUser.value.session_id,
    content: text
  });
  chatHistory.value.push({ from: 'admin', text, time: formatNow() });
  currentUser.value.lastMessage = text;
  replyText.value = '';
  scrollToBottom();
};

onMounted(() => { initSocket(); });
onUnmounted(() => { if (socket) socket.disconnect(); });
</script>

<style scoped>
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');

/* 使用网站CSS变量 */
:root {
  --primary-color: #1890ff;
  --primary-dark: #096dd9;
  --primary-hover: #096dd9;
  --bg-color: #f0f2f5;
  --text-main: rgba(0, 0, 0, 0.85);
  --text-secondary: rgba(0, 0, 0, 0.65);
  --text-muted: rgba(0, 0, 0, 0.45);
  --border-color: #f0f0f0;
  --white: #ffffff;
  --theme-blue: #1890ff;
  --transition: all 0.3s;
}

/* 全局基础定义 */
.admin-chat-container {
  max-width: 1200px;
  margin: 10px auto 0;
  padding: 0 20px;
  height: calc(100vh - 90px);
  background: var(--bg-color);
}

.admin-chat-layout {
  display: flex;
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-main);
  background: var(--bg-color);
}

/* 标签样式统一 - 使用网站风格 */
.el-tag {
  display: inline-block;
  padding: 0 10px;
  height: 20px;
  line-height: 18px;
  border-radius: 10px;
  font-size: 11px;
  border: 1px solid;
  transition: var(--transition);
}
.el-tag.success { background: #f0f9eb; border-color: #e1f3d8; color: #67c23a; }
.el-tag.info { background: #ecf5ff; border-color: #c6e2ff; color: var(--primary-color); }
.el-tag.warning { background: #fdf6ec; border-color: #faecd8; color: #e6a23c; }
.el-tag.danger { background: #fef0f0; border-color: #fbc4c4; color: #f56c6c; }

/* 按钮样式统一 - 使用网站风格 */
.el-button {
  display: inline-block;
  padding: 0 15px;
  height: 32px;
  line-height: 30px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background: var(--white);
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 13px;
  transition: var(--transition);
  font-family: inherit;
}
.el-button:hover:not(:disabled) {
  color: var(--primary-color);
  border-color: var(--primary-color);
  background: var(--white);
}
.el-button:disabled { opacity: 0.5; cursor: not-allowed; }
.el-button.success {
  background: var(--primary-color);
  border-color: var(--primary-color);
  color: var(--white);
}
.el-button.success:hover:not(:disabled) {
  background: var(--primary-hover);
  border-color: var(--primary-hover);
}
.el-button.danger {
  background: #f56c6c;
  border-color: #f56c6c;
  color: var(--white);
}
.el-button.danger:hover:not(:disabled) {
  background: #f78989;
  border-color: #f78989;
}

/* 左侧栏 - 使用网站卡片风格 */
.sidebar {
  width: 280px;
  background: var(--white);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 8px rgba(0,0,0,0.02);
  z-index: 2;
}

.sidebar-header {
  padding: 15px 20px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 15px;
  font-weight: 500;
  color: var(--text-main);
}
.badge {
  background: #ecf5ff;
  color: var(--primary-color);
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
}

.room-join-box {
  padding: 15px 20px;
  display: flex;
  gap: 8px;
  border-bottom: 1px solid var(--border-color);
}

.room-join-box input {
  flex: 1;
  height: 32px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  padding: 0 10px;
  outline: none;
  font-size: 13px;
  transition: border-color 0.3s;
  font-family: inherit;
  color: var(--text-main);
}
.room-join-box input:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.1);
}

.session-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}
.session-list::-webkit-scrollbar { width: 6px; }
.session-list::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 4px;
}

.session-item {
  padding: 12px;
  border-radius: 6px;
  border: 1px solid var(--border-color);
  margin-bottom: 8px;
  cursor: pointer;
  transition: var(--transition);
  background: var(--white);
}

.session-item:hover {
  border-color: var(--primary-color);
  background: var(--bg-color);
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.1);
}
.session-item.active {
  border-color: var(--primary-color);
  background: #ecf5ff;
}

.session-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 6px;
}


.session-title {
  display: flex;
  align-items: center;
  position: relative;
}
.online-indicator {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}
.online-indicator.online {
  background: #52c41a;
  box-shadow: 0 0 3px rgba(82, 196, 26, 0.5);
}
.online-indicator.offline {
  background: #d9d9d9;
}
.session-time {
  font-size: 11px;
  color: var(--text-muted);
}
.session-preview {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.session-info {
  font-size: 11px;
  color: var(--text-muted);
}

.unread-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 18px;
  height: 18px;
  border-radius: 9px;
  background: #f56c6c;
  color: #fff;
  font-size: 11px;
  font-weight: 600;
  padding: 0 5px;
  margin-left: 6px;
  line-height: 1;
}

/* 右侧聊天主区域 */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--white);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  overflow: hidden;
}

.service-header {
  background: var(--white);
  border-bottom: 1px solid var(--border-color);
  padding: 0 24px;
  z-index: 1;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
}

.service-title {
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.service-title h2 {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
  color: var(--text-main);
}
.service-status {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 4px;
}
.agent-info {
  font-size: 12px;
  color: var(--text-muted);
}
.user-online-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-left: 6px;
  vertical-align: middle;
}
.user-online-dot.online {
  background: #52c41a;
  box-shadow: 0 0 4px rgba(82, 196, 26, 0.6);
}
.user-online-dot.offline {
  background: #d9d9d9;
}
.user-online-text {
  font-size: 12px;
  font-weight: normal;
  margin-left: 4px;
  vertical-align: middle;
}

.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.messages-container {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  background: #fafafa;
}
.messages-container::-webkit-scrollbar { width: 6px; }
.messages-container::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 4px;
}

/* 聊天消息气泡结构 */
.message-wrapper {
  margin-bottom: 24px;
  display: flex;
  align-items: flex-start;
}
.message-wrapper.admin-message {
  flex-direction: row-reverse;
}
.message-wrapper.system-message-row {
  justify-content: center;
}

.system-message {
  background: transparent;
  color: var(--text-muted);
  font-size: 12px;
  padding: 6px 12px;
  font-style: italic;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 4px;
  color: var(--white);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: bold;
  flex-shrink: 0;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
.user-message .message-avatar {
  background: var(--text-muted);
  margin-right: 12px;
}
.admin-message .message-avatar {
  background: var(--primary-color);
  margin-left: 12px;
}

.bot-message .message-avatar {
  background: linear-gradient(135deg, #10b981, #059669);
  margin-right: 12px;
}

.message-bubble {
  max-width: 65%;
  padding: 12px 16px;
  border-radius: 6px;
  position: relative;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

.user-message .message-bubble {
  background: var(--white);
  color: var(--text-main);
  border: 1px solid var(--border-color);
  border-top-left-radius: 2px;
}

.bot-message .message-bubble {
  background: #f0fdf4;
  color: var(--text-main);
  border: 1px solid #bbf7d0;
  border-top-left-radius: 2px;
}

.admin-message .message-bubble {
  background: var(--primary-color);
  color: var(--white);
  border-top-right-radius: 2px;
}

.message-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}
.sender-name {
  font-size: 12px;
  font-weight: 500;
  opacity: 0.9;
}
.message-time {
  font-size: 11px;
  margin-left: auto;
  opacity: 0.7;
}
.admin-message .sender-name,
.admin-message .message-time {
  color: var(--white);
}
.user-message .sender-name,
.user-message .message-time {
  color: var(--text-muted);
}

.message-content {
  line-height: 1.6;
  word-wrap: break-word;
  white-space: pre-wrap;
  font-size: 14px;
}

.message-status {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 4px;
  margin-top: 6px;
  font-size: 11px;
  color: rgba(255,255,255,0.8);
}

/* 底部输入区 */
.input-area {
  border-top: 1px solid var(--border-color);
  padding: 20px 24px;
  background: var(--white);
  box-shadow: 0 -2px 10px rgba(0,0,0,0.02);
}

.input-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}


.el-input textarea {
  width: 100%;
  height: 80px;
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 14px;
  resize: none;
  font-family: inherit;
  box-sizing: border-box;
  color: var(--text-main);
  transition: var(--transition);
}
.el-input textarea:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.1);
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.action-left {
  display: flex;
  gap: 10px;
  align-items: center;
}
.action-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.file-upload-btn {
  padding: 0 12px;
  height: 32px;
  line-height: 30px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background: var(--bg-color);
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 13px;
  transition: var(--transition);
  font-family: inherit;
}
.file-upload-btn:hover {
  color: var(--primary-color);
  border-color: var(--primary-color);
  background: var(--white);
}

.connection-status {
  font-size: 12px;
  color: var(--text-muted);
  display: flex;
  align-items: center;
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: var(--text-muted);
}
.empty-state i {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.5;
  color: var(--text-muted);
}
.empty-state p {
  color: var(--text-secondary);
  font-size: 14px;
}

/* 网站全局滚动条样式 */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background-color: #f5f7fa; border-radius: 4px; }
::-webkit-scrollbar-thumb { background-color: #c0c8d6; border-radius: 4px; border: 2px solid #f5f7fa; background-clip: padding-box; }
::-webkit-scrollbar-thumb:hover { background-color: var(--primary-color); }

/* 实名信息按钮 */
.realname-btn {
  display: inline-block;
  font-size: 11px;
  color: var(--primary-color);
  background: transparent;
  border: 1px solid var(--primary-color);
  border-radius: 3px;
  padding: 1px 8px;
  cursor: pointer;
  margin-top: 4px;
  transition: var(--transition);
}
.realname-btn:hover {
  background: var(--primary-color);
  color: white;
}

.realname-dialog-content {
  padding: 10px 0;
}
.realname-row {
  display: flex;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}
.realname-row:last-child {
  border-bottom: none;
}
.realname-label {
  width: 80px;
  font-size: 14px;
  color: #64748b;
  flex-shrink: 0;
}
.realname-value {
  font-size: 14px;
  color: #1a202c;
  font-weight: 500;
}

/* ================= 可移动详情弹窗 ================= */
.reference-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.3);
  z-index: 999;
}
.reference-dialog {
  position: fixed;
  z-index: 1000;
  width: 560px;
  max-height: 80vh;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 8px 30px rgba(0,0,0,0.2);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.reference-dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 20px;
  background: #f0f2f5;
  border-bottom: 1px solid #e8e8e8;
  cursor: move;
  font-size: 16px;
  font-weight: 600;
  user-select: none;
}
.reference-dialog-close {
  border: none;
  background: none;
  font-size: 22px;
  cursor: pointer;
  color: #999;
  padding: 0 4px;
  line-height: 1;
}
.reference-dialog-close:hover {
  color: #f56c6c;
}
.reference-dialog-body {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}
.reference-loading {
  text-align: center;
  padding: 40px;
  color: #999;
  font-size: 14px;
}
.ref-section {
  margin-bottom: 16px;
}
.ref-section-title {
  font-size: 15px;
  font-weight: 600;
  color: #333;
  padding-bottom: 8px;
  margin-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}
.ref-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px 16px;
}
.ref-item {
  display: flex;
  align-items: flex-start;
  font-size: 13px;
  line-height: 1.5;
}
.ref-item.full {
  grid-column: 1 / -1;
}
.ref-label {
  color: #888;
  white-space: nowrap;
  flex-shrink: 0;
  min-width: 80px;
}
.ref-value {
  color: #333;
  word-break: break-all;
}

/* ================= 可移动弹窗 - drawer风格 ================= */
.ref-fieldset {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 16px;
  background: #fff;
}
.ref-fieldset legend {
  font-size: 15px;
  font-weight: bold;
  color: #333;
  padding: 0 10px;
  width: auto;
  margin-left: 10px;
}
.ref-form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-top: 10px;
}
.ref-form-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.ref-form-item.full-width {
  grid-column: 1 / -1;
}
.ref-form-item label {
  font-size: 13px;
  font-weight: 600;
  color: #555;
}
.ref-readonly-field {
  font-size: 13px;
  color: #333;
  padding: 8px 12px;
  background-color: #f9f9f9;
  border: 1px solid #ddd;
  border-radius: 4px;
  min-height: 36px;
  display: block;
  word-break: break-all;
  line-height: 1.5;
}
</style>

<style>
.clickable-notification {
  cursor: pointer !important;
  transition: all 0.3s ease;
}
.clickable-notification:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
}
</style>