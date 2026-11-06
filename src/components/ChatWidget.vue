<template>
  <div>
    <div v-show="!isOpen" class="chat-widget-button" @click="toggleChat">
      <i class="fas fa-comment-dots"></i>
      <span v-if="hasUnreadMessage" class="unread-notification">有新消息</span>
    </div>

    <div class="chat-container" ref="chatContainer" :class="{ show: isOpen }" :style="{ width: containerWidth + 'px', height: containerHeight + 'px' }">
      <div class="resize-handle" @mousedown="startResize"></div>

      <div class="chat-header">
        <div class="header-info">
          <div class="avatar-wrapper">
            <i class="fas fa-robot"></i>
          </div>
          <div class="header-text">
            <span class="header-title">{{ isRequestingHuman ? '人工客服' : '智能客服助手' }}</span>
            <span class="header-status">
              <span :class="['status-dot', agentOnlineStatus]"></span>
              {{ agentStatusText }}
            </span>
          </div>
        </div>
        <button class="close-btn" @click="toggleChat" title="最小化">
          <i class="fas fa-chevron-down"></i>
        </button>
      </div>

      <div class="session-bar">
        <span>会话编号：{{ currentSessionId || roomId }}</span>
        <button v-if="isRequestingHuman && currentSessionId" @click="endSession" class="end-session-btn">结束会话</button>
      </div>

      <div class="chat-messages" ref="messagesContainer">
        <div class="message system">
          <div class="message-content">今天 {{ currentTime }}</div>
        </div>

        <div
          v-for="(msg, index) in messages"
          :key="index"
          :class="['message', msg.type]"
        >
          <div
            v-if="msg.type === 'bot' || msg.type === 'admin' || msg.type === 'system'"
            class="msg-avatar bot-avatar"
          >
            <i
              :class="
                msg.type === 'bot'
                  ? 'fas fa-robot'
                  : msg.type === 'admin'
                  ? 'fas fa-headset'
                  : 'fas fa-bullhorn'
              "
            ></i>
          </div>
          <div v-if="msg.type === 'user'" class="msg-avatar user-avatar">
            <i class="fas fa-user"></i>
          </div>

          <div
            class="message-content"
            :class="{ plain: msg.type === 'user' || msg.type === 'admin' || msg.type === 'system' }"
            v-html="msg.text"
          ></div>
        </div>
      </div>

      <div class="chat-input-area">
        <div class="input-wrapper">
          <input
            type="text"
            v-model="inputText"
            placeholder="描述您的问题，按回车发送..."
            @keypress.enter="sendMessage"
          />
        </div>
        <div class="action-buttons">
          <button
            class="human-btn"
            :class="{ connected: isRequestingHuman && currentSessionId }"
            @click="requestHuman"
            title="人工客服"
            :disabled="isRequestingHuman"
          >
            <i class="fas fa-headset"></i>
            <span>{{ isRequestingHuman ? (currentSessionId ? '已转接' : '转接中...') : '转人工' }}</span>
          </button>
          <button class="send-btn" @click="sendMessage" :disabled="!inputText.trim()">
            <i class="fas fa-paper-plane"></i>
            <span>发送</span>
          </button>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, computed, onMounted, onUnmounted, watch } from 'vue';
import { io } from 'socket.io-client';
import useAuth from '@/composables/useAuth';

const auth = useAuth();
const isOpen = ref(false);
const inputText = ref('');
const messages = ref([]);
const messagesContainer = ref(null);
const chatContainer = ref(null);

const isRequestingHuman = ref(false);
const currentSessionId = ref(''); // 🌟 记录真实客服会话ID
const hasUnreadMessage = ref(false); // 🌟 记录是否有未读的客服消息
const contactReference = ref(null); // { type: 'achievement'|'demand', id: '...' } 来自"我要对接"
const agentOnlineStatus = ref('unknown'); // 'online' | 'offline' | 'busy' | 'unknown'
const agentStatusText = computed(() => {
  if (agentOnlineStatus.value === 'online') return '客服在线';
  if (agentOnlineStatus.value === 'busy') return '客服忙碌';
  if (agentOnlineStatus.value === 'offline') return '客服离线';
  return '在线为您服务';
});

// 🌟 新增：单独存一份机器人的历史记录，防止合并时丢失
let botHistoryMessages = [];

const containerWidth = ref(400);
const containerHeight = ref(620);
const isResizing = ref(false);
const startX = ref(0);
const startY = ref(0);
const startWidth = ref(0);
const startHeight = ref(0);

const defaultGreeting =
  '您好！欢迎来到科创中心。<br>请直接回复数字 / 关键词，我为您解答：<br>1. 成果发布<br>2. 需求发布<br>3. 专家认证<br>4. 成果 & 需求对接<br>5. 账号与信息修改<br>6. 人工客服';

// 动态欢迎语（启动时从服务端拉取，管理员可在FAQ中编辑"系统欢迎语"）
const greetingMessage = ref(defaultGreeting);

const fetchGreeting = async () => {
  try {
    const res = await fetch('/api/chat/faqs/greeting');
    const data = await res.json();
    if (data.code === 200 && data.data.greeting) {
      greetingMessage.value = data.data.greeting;
    }
  } catch (e) {
    console.log('获取动态欢迎语失败，使用默认:', e);
  }
};

const fetchAgentStatus = async () => {
  try {
    const token = auth.state.token;
    if (!token) return;
    const res = await fetch('/api/chat/customer-service/online-agents', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const data = await res.json();
    if (data.code === 200 && Array.isArray(data.data)) {
      const onlineAgents = data.data.filter(a => a.status === 'online');
      if (onlineAgents.length > 0) {
        agentOnlineStatus.value = 'online';
      } else {
        agentOnlineStatus.value = 'offline';
      }
    }
  } catch (e) {
    console.log('获取客服状态失败:', e);
  }
};

let socket = null;

const getGuestRoomId = () => {
  let id = localStorage.getItem('guest_room_id');
  if (!id) {
    id = `guest_${Math.random().toString(36).slice(2, 10)}`;
    localStorage.setItem('guest_room_id', id);
  }
  return id;
};

const roomId = computed(() => {
  return auth.username.value ? String(auth.username.value) : getGuestRoomId();
});

const currentTime = computed(() => {
  const now = new Date();
  return `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
});

const normalizeMsgType = (sender) => {
  if (sender === 'admin' || sender === 'agent') return 'admin';
  if (sender === 'bot') return 'bot';
  if (sender === 'system') return 'system';
  return 'user';
};

const scrollToBottom = async () => {
  await nextTick();
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
  }
};

const ensureDefaultMessage = () => {
  if (!messages.value.length) {
    messages.value = [{ type: 'bot', text: greetingMessage.value }];
  }
};

const appendMessage = (type, text, msgId) => {
  const msg = { type, text };
  if (msgId) msg._msgId = msgId;
  messages.value.push(msg);
  scrollToBottom();
};

const loadHistory = async () => {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000);
    const response = await fetch(`/api/chat/history?room_id=${encodeURIComponent(roomId.value)}`, { signal: controller.signal });
    clearTimeout(timeoutId);
    const data = await response.json();

    if (data.code === 200 && Array.isArray(data.data) && data.data.length > 0) {
      // 🌟 将机器人历史存入单独变量，并记录时间戳用于排序
      botHistoryMessages = data.data.map((item) => ({
        type: normalizeMsgType(item.from),
        text: item.text,
        timestamp: new Date(item.create_time || item.timestamp || Date.now()).getTime()
      }));
    } else {
      botHistoryMessages = [{ type: 'bot', text: greetingMessage.value, timestamp: Date.now() }];
    }

    // 🌟 初始先只显示机器人记录（随后等待 Socket 拉取人工记录并合并）
    if (messages.value.length === 0) {
      messages.value = [...botHistoryMessages];
    }

  } catch (error) {
    console.error('加载历史记录失败:', error);
    ensureDefaultMessage();
  }
  scrollToBottom();
};

const disconnectSocket = () => {
  if (socket) {
    socket.disconnect();
    socket = null;
  }
};

const connectSocket = () => {
  disconnectSocket();

  socket = io({
    transports: ['websocket'],
    query: { token: auth.state.token }
  });

  socket.on('connect', () => {
    socket.emit('join', { room_id: roomId.value, role: 'user' });
    console.log('普通用户 WebSocket 已连接');
    
    // 🌟 核心：连接成功后，主动查询自己是否有未关闭的人工会话
    socket.emit('get_customer_service_sessions'); 
  });

  // 🌟 核心：处理查询结果，恢复刷新前的人工对话
  socket.on('customer_service_sessions', (data) => {
    let hasActive = false;
    if (data.sessions && data.sessions.length > 0) {
      const activeSession = data.sessions.find(s => s.status === 'active' || s.status === 'waiting');
      if (activeSession) {
        currentSessionId.value = activeSession.id;
        isRequestingHuman.value = true;
        hasActive = true;
        socket.emit("join_customer_service_session", { session_id: activeSession.id });
      }
    }
    // 没有活跃会话 → 显示机器人欢迎语（仅前端）
    if (!hasActive && isOpen.value) {
      const hasGreeting = messages.value.some(m => m.type === 'bot' && m.text === greetingMessage.value);
      if (!hasGreeting) {
        messages.value.push({ type: 'bot', text: greetingMessage.value });
        scrollToBottom();
      }
    }
    // 登录用户拉取全量历史（机器人+所有客服会话）
    if (auth.state.token) {
      socket.emit('get_user_all_history', {});
    }
  });

  // 🌟 核心：拿到人工记录后，与机器人记录合并并按时间排序
  socket.on('customer_service_messages', (data) => {
    if (data.messages && data.messages.length > 0) {
      const humanHistoryMessages = data.messages.map(msg => ({
        type: msg.sender_type === 'agent' ? 'admin' : 'user',
        text: msg.content,
        timestamp: new Date(msg.created_at).getTime()
      }));

      // 合并并排序
      messages.value = [...botHistoryMessages, ...humanHistoryMessages].sort((a, b) => a.timestamp - b.timestamp);
      scrollToBottom();
    }
  });

  // 🌟 拿到全量历史（机器人+所有人工会话）后合并展示（不替换，防止竞态丢消息）
  socket.on('user_all_history', (data) => {
    const allItems = [];
    // 机器人消息
    (data.bot_messages || []).forEach(msg => {
      allItems.push({
        type: msg.sender === 'bot' ? 'bot' : (msg.sender === 'system' ? 'system' : 'user'),
        text: msg.content,
        timestamp: new Date(msg.created_at).getTime(),
        _msgId: msg.message_id || null
      });
    });
    // 人工客服消息（所有会话）
    (data.session_messages || []).forEach(msg => {
      allItems.push({
        type: msg.sender_type === 'agent' ? 'admin' : 'user',
        text: msg.content,
        timestamp: new Date(msg.created_at).getTime(),
        _msgId: msg.message_id || null
      });
    });
    if (allItems.length > 0) {
      allItems.sort((a, b) => a.timestamp - b.timestamp);
      // 合并而非替换：保留本地已有消息，用 type+text+timestamp 做去重
      // 注意：_msgId 不出现在 dedup key 中，因为 loadHistory() (HTTP) 加载的消息不带 _msgId，
      // 而 socket user_all_history 带 _msgId，如果 key 包含 _msgId 会导致同一条消息被添加两次。
      const existingKeys = new Set(
        messages.value.map(m => `${m.type}|${m.text}|${m.timestamp || 0}`)
      );
      for (const item of allItems) {
        const key = `${item.type}|${item.text}|${item.timestamp}`;
        if (!existingKeys.has(key)) {
          messages.value.push(item);
        }
      }
      // 重新排序
      messages.value.sort((a, b) => (a.timestamp || 0) - (b.timestamp || 0));
    } else if (messages.value.length === 0) {
      ensureDefaultMessage();
    }
    // 没有活跃会话时，在顶部插入欢迎语（仅前端）
    if (!currentSessionId.value) {
      const hasGreeting = messages.value.some(m => m.type === 'bot' && m.text === greetingMessage.value);
      if (!hasGreeting) {
        messages.value.push({ type: 'bot', text: greetingMessage.value });
      }
    }
    scrollToBottom();
  });

  // 1. 监听通用聊天机器人的消息
  socket.on('receive_message', (data) => {
    if (!data || !data.text) return;
    if (data.room_id && String(data.room_id) !== String(roomId.value)) return;

    const type = normalizeMsgType(data.sender);
    if (type === 'user') return; // 自己发的前端已回显

    // 用服务端 message_id 去重，解决相同内容重复发送被误拦截和多socket连接导致消息重复的问题
    if (data.message_id && messages.value.some(m => m._msgId === data.message_id)) return;

    appendMessage(type, data.text, data.message_id || null);
  });

  // 2. 监听成功创建人工会话
  socket.on('customer_service_session_created', (data) => {
    console.log('✅ 人工客服会话创建，Session ID:', data.id, 'Status:', data.status);
    isRequestingHuman.value = true;
    if (data.status === 'active' || data.status === 'waiting') {
      // 客服已接受 → 设置真实会话ID，按钮变为"已转接"(绿色)
      currentSessionId.value = data.id;
      socket.emit('join_customer_service_session', { session_id: data.id });
    }
    // status === 'pending'：客服尚未接受，只标记请求中不设置 currentSessionId，
    // 按钮保持显示"转接中..."（isRequestingHuman=true 但 currentSessionId=空）
  });

  // 3. 收到刷新通知 — 只更新未读状态，不触发全量历史重载（new_customer_service_message 已负责实时展示）
  socket.on('customer_session_refresh', () => {
    if (!isOpen.value && currentSessionId.value) {
      hasUnreadMessage.value = true;
    }
  });

  // 3b. 收到客服发来的即时消息（欢迎语等），直接显示
  socket.on('new_customer_service_message', (msg) => {
    if (!msg || !currentSessionId.value) return;
    if (msg.session_id !== currentSessionId.value) return;
    // 用服务端 message_id 去重，解决多socket连接导致消息重复的问题
    if (msg.id && messages.value.some(m => m._msgId === msg.id)) return;
    appendMessage('admin', msg.content, msg.id || null);
    if (!isOpen.value) {
      hasUnreadMessage.value = true;
    }
  });

  // 4. 监听会话被关闭（对方关闭时触发）
  socket.on('session_closed', (data) => {
    if (data.session_id === currentSessionId.value) {
      // 会话关闭消息已由服务端持久化并通过 receive_message 推送，
      // 前端不再本地追加，避免历史加载时重复显示。
      isRequestingHuman.value = false;
      currentSessionId.value = '';
      contactReference.value = null;
    }
  });

  // 监听会话被管理员删除
  socket.on('session_deleted', (data) => {
    if (!data) return;
    // 匹配当前会话（单条删除）或用户ID（批量删除）
    const isMySession = data.session_id && data.session_id === currentSessionId.value;
    const isMyUser = data.user_id && data.user_id === (auth.state.user?.id);
    if (isMySession || isMyUser) {
      appendMessage('system', '会话已被管理员删除');
      isRequestingHuman.value = false;
      currentSessionId.value = '';
      contactReference.value = null;
      // 清空聊天记录和机器人历史缓存
      messages.value = [{ type: 'bot', text: greetingMessage.value }];
      botHistoryMessages = [{ type: 'bot', text: greetingMessage.value, timestamp: Date.now() }];
    }
  });

  // 5. 监听客服状态（更新头部状态 + 去重防抖显示系统消息）
  socket.on('agent_availability', (data) => {
    // 实时更新客服在线状态
    agentOnlineStatus.value = data.online_status || 'offline';
    // 去重：相同消息不重复显示
    if (messages.value.length > 0) {
      const lastMsg = messages.value[messages.value.length - 1];
      if (lastMsg.type === 'system' && lastMsg.text === data.message) {
        return;
      }
    }
    appendMessage('system', data.message);
  });

  socket.on('error', (data) => {
    console.error('Socket 错误:', data);
  });
};

const toggleChat = () => {
  isOpen.value = !isOpen.value;
  if (isOpen.value) {
    hasUnreadMessage.value = false;
    // 普通方式打开客服窗口应清除上次遗留的对接上下文，避免从成果/需求页进入后，
    // 再次从右下角图标打开时仍携带旧的对接引用信息。
    contactReference.value = null;
    // 重新查询服务器端有没有活跃会话（不重置 isRequestingHuman/currentSessionId，避免丢消息）
    if (socket) socket.emit('get_customer_service_sessions');
    fetchAgentStatus();
  }
};

const openChat = () => {
  isOpen.value = true;
  contactReference.value = null; // 从主页进入时清除上次遗留的对接信息
  if (socket) socket.emit('get_customer_service_sessions');
  fetchAgentStatus();
};

const openChatWithContext = (type, id) => {
  // 如果已在人工会话中，立即同步对接信息到服务端
  if (isRequestingHuman.value && currentSessionId.value && socket) {
    socket.emit('update_session_reference', {
      session_id: currentSessionId.value,
      reference_type: type,
      reference_id: id
    });
  }
  openChat();
  // 在 openChat() 之后设置，避免被清除
  contactReference.value = { type, id };
};

// eslint-disable-next-line no-undef
defineExpose({ openChat, toggleChat, openChatWithContext });

const handleClickOutside = (event) => {
  if (!isOpen.value || !chatContainer.value) return;
  if (!chatContainer.value.contains(event.target)) {
    const chatButton = document.querySelector('.chat-widget-button');
    if (chatButton && chatButton.contains(event.target)) return;
    isOpen.value = false;
  }
};

const setupClickOutsideListener = () => document.addEventListener('mousedown', handleClickOutside);
const removeClickOutsideListener = () => document.removeEventListener('mousedown', handleClickOutside);

watch(isOpen, (newVal) => {
  if (newVal) nextTick(() => setupClickOutsideListener());
  else removeClickOutsideListener();
});

const sendMessage = () => {
  const text = inputText.value.trim();
  if (!text) return;

  appendMessage('user', text);

  // 如果处于人工客服模式，走专属通道发送
  if (isRequestingHuman.value && currentSessionId.value) {
    if (socket) {
      const payload = {
        session_id: currentSessionId.value,
        content: text
      };
      // 携带对接参考信息（如有）
      if (contactReference.value) {
        payload.reference_type = contactReference.value.type;
        payload.reference_id = contactReference.value.id;
      }
      socket.emit('customer_service_message', payload);
    }
    inputText.value = '';
    return;
  }

  // 机器人模式：检测是否触发人工客服请求
  const humanKeywords = ['人工客服', '人工服务', '转人工', '客服人员', '真人客服', '找人工', '人工'];
  const isHumanRequest = humanKeywords.some(kw => text.includes(kw));

  if (isHumanRequest) {
    if (socket) {
      const payload = { room_id: roomId.value, text };
      if (contactReference.value) {
        payload.reference_type = contactReference.value.type;
        payload.reference_id = contactReference.value.id;
      }
      socket.emit('request_human', payload);
    }
    isRequestingHuman.value = true;
  } else {
    // 所有消息发送到服务端，由 FAQMatcher 匹配并回复
    if (socket) {
      socket.emit('send_message', {
        room_id: roomId.value,
        sender: 'user',
        text,
      });
    }
  }

  inputText.value = '';
};

const endSession = () => {
  if (socket && currentSessionId.value) {
    socket.emit('close_customer_service_session', { session_id: currentSessionId.value });
    isRequestingHuman.value = false;
    currentSessionId.value = '';
    contactReference.value = null;
    appendMessage('system', '会话已结束');
  }
};

const requestHuman = () => {
  if (isRequestingHuman.value) return;

  appendMessage('user', '转人工');

  // 乐观更新：立即禁用按钮，即使会话尚未创建
  isRequestingHuman.value = true;

  if (socket) {
    const payload = {
      room_id: roomId.value,
      text: '转人工',
    };
    if (contactReference.value) {
      payload.reference_type = contactReference.value.type;
      payload.reference_id = contactReference.value.id;
    }
    socket.emit('request_human', payload);
  }
};

// 调整大小相关函数
const startResize = (e) => {
  e.preventDefault();
  e.stopPropagation();
  isResizing.value = true;
  startX.value = e.clientX;
  startY.value = e.clientY;
  startWidth.value = containerWidth.value;
  startHeight.value = containerHeight.value;

  document.addEventListener('mousemove', doResize);
  document.addEventListener('mouseup', stopResize);
};

const doResize = (e) => {
  if (!isResizing.value) return;
  const deltaX = e.clientX - startX.value;
  const deltaY = e.clientY - startY.value;
  containerWidth.value = Math.max(300, Math.min(800, startWidth.value - deltaX));
  containerHeight.value = Math.max(400, Math.min(900, startHeight.value - deltaY));
};

const stopResize = () => {
  isResizing.value = false;
  document.removeEventListener('mousemove', doResize);
  document.removeEventListener('mouseup', stopResize);
};

onMounted(async () => {
  await fetchGreeting();
  await fetchAgentStatus();
  connectSocket();
  // 已登录用户通过 socket user_all_history 加载完整历史（含机器人+人工消息），
  // HTTP loadHistory 会与之产生时间戳不一致导致重复，故跳过。
  // 未登录访客没有 user_all_history，仍靠 loadHistory 加载机器人记录。
  if (!auth.state.token) {
    await loadHistory();
  }
});

watch(roomId, async (newRoom, oldRoom) => {
  if (!newRoom || newRoom === oldRoom) return;
  messages.value = [];
  isRequestingHuman.value = false;
  currentSessionId.value = '';
  botHistoryMessages = []; // 清空之前的机器人记录
  connectSocket();
  if (!auth.state.token) {
    await loadHistory();
  }
});

onUnmounted(() => {
  disconnectSocket();
  removeClickOutsideListener();
});
</script>

<style scoped>
/* 保持所有样式完全不变 */
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css');

* {
  box-sizing: border-box;
}

.chat-widget-button {
  position: fixed;
  bottom: 40px;
  right: 40px;
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, #0084ff, #0056b3);
  color: white;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 28px;
  cursor: pointer;
  box-shadow: 0 8px 25px rgba(0, 86, 179, 0.4);
  transition: all 0.3s ease;
  z-index: 10003;
}

.chat-widget-button:hover {
  transform: scale(1.08) translateY(-3px);
}

.unread-notification {
  position: absolute;
  top: -28px;
  left: 50%;
  transform: translateX(-50%);
  white-space: nowrap;
  font-size: 12px;
  color: #999;
  background: #f5f5f5;
  padding: 4px 12px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  pointer-events: none;
}

.chat-container {
  position: fixed;
  bottom: 110px;
  right: 40px;
  width: 400px;
  height: 620px;
  min-width: 300px;
  min-height: 400px;
  max-width: 800px;
  max-height: 900px;
  background-color: #ffffff;
  border-radius: 20px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.12);
  display: flex;
  flex-direction: column;
  z-index: 10003;
  border: 1px solid rgba(0, 0, 0, 0.05);
  opacity: 0;
  transform: translateY(20px) scale(0.95);
  visibility: hidden;
  transition: opacity 0.3s ease, transform 0.3s ease, visibility 0.3s;
  overflow: hidden;
  resize: none;
}

.chat-container.show {
  opacity: 1;
  transform: translateY(0) scale(1);
  visibility: visible;
}

.resize-handle {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 20px;
  height: 20px;
  background: #0084ff;
  border-radius: 0 0 10px 0;
  cursor: nwse-resize;
  z-index: 10000;
  opacity: 0.7;
  transition: opacity 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.resize-handle:hover {
  opacity: 1;
}

.resize-handle::before {
  content: '';
  position: absolute;
  width: 12px;
  height: 12px;
  border-right: 2px solid white;
  border-bottom: 2px solid white;
  bottom: 3px;
  right: 3px;
}

.chat-header {
  height: 74px;
  background: linear-gradient(135deg, #0084ff, #0056b3);
  color: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 18px;
  flex-shrink: 0;
}

.header-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar-wrapper {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.18);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.header-text {
  display: flex;
  flex-direction: column;
}

.header-title {
  font-size: 16px;
  font-weight: 600;
}

.header-status {
  font-size: 12px;
  opacity: 0.95;
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #2ee59d;
}
.status-dot.online {
  background: #2ee59d;
  box-shadow: 0 0 4px rgba(46, 229, 157, 0.6);
}
.status-dot.busy {
  background: #faad14;
  box-shadow: 0 0 4px rgba(250, 173, 20, 0.6);
}
.status-dot.offline {
  background: #bfbfbf;
}
.status-dot.unknown {
  background: #2ee59d;
}

.close-btn {
  background: transparent;
  border: none;
  color: white;
  cursor: pointer;
  font-size: 18px;
}

.end-session-btn {
  background: #f56c6c;
  border: none;
  color: white;
  cursor: pointer;
  font-size: 12px;
  padding: 2px 10px;
  border-radius: 10px;
  transition: all 0.2s ease;
  margin-left: auto;
}
.end-session-btn:hover {
  background: #f78989;
}

.session-bar {
  padding: 8px 14px;
  background: #f8fbff;
  border-bottom: 1px solid #e8eef5;
  color: #64748b;
  font-size: 12px;
  flex-shrink: 0;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 18px 16px;
  background: #f6f8fb;
}

.message {
  display: flex;
  align-items: flex-start;
  margin-bottom: 14px;
  gap: 10px;
}

.message.user {
  flex-direction: row-reverse;
}

.message.system {
  justify-content: center;
}

.msg-avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  color: white;
  flex-shrink: 0;
}

.bot-avatar {
  background: linear-gradient(135deg, #10b981, #059669);
}

.user-avatar {
  background: linear-gradient(135deg, #f59e0b, #d97706);
}

.message-content {
  max-width: 74%;
  padding: 10px 14px;
  border-radius: 16px;
  line-height: 1.6;
  font-size: 14px;
  word-break: break-word;
  white-space: pre-wrap;
  background: white;
  color: #334155;
  border: 1px solid #e5e7eb;
}

.message.user .message-content {
  background: linear-gradient(135deg, #0084ff, #0056b3);
  color: white;
  border: none;
}

.message.bot .message-content,
.message.admin .message-content {
  background: white;
}

.message.system .message-content {
  background: #eef2f7;
  color: #64748b;
  border: none;
  font-size: 12px;
  padding: 6px 12px;
  max-width: 90%;
}

.chat-input-area {
  padding: 14px;
  border-top: 1px solid #edf2f7;
  background: white;
  flex-shrink: 0;
}

.input-wrapper input {
  width: 100%;
  height: 44px;
  border: 1px solid #dbe4ee;
  border-radius: 12px;
  padding: 0 14px;
  font-size: 14px;
  outline: none;
}

.input-wrapper input:focus {
  border-color: #0084ff;
}

.action-buttons {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  margin-top: 12px;
}

.human-btn,
.send-btn {
  flex: 1;
  height: 42px;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
}

.human-btn {
  background: #fff3f0;
  color: #e85d3f;
  border: 1px solid #ffd2c7;
}

.human-btn.connected {
  background: #f0fff4;
  color: #2e7d32;
  border: 1px solid #c8e6c9;
}

.send-btn {
  background: linear-gradient(135deg, #0084ff, #0056b3);
  color: white;
}

.send-btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 10px;
}

/* ================= ChatWidget 响应式 ================= */
@media (max-width: 768px) {
  .chat-container {
    width: calc(100vw - 24px) !important;
    height: 65vh !important;
    min-width: auto !important;
    bottom: 80px !important;
    right: 12px !important;
    border-radius: 16px !important;
  }
  .chat-toggle-btn {
    width: 52px;
    height: 52px;
    font-size: 24px;
    bottom: 20px;
    right: 20px;
  }
  .chat-header {
    padding: 14px 16px;
  }
  .chat-messages {
    padding: 14px;
  }
  .chat-input-area {
    padding: 10px 14px;
  }
  .input-wrapper input {
    font-size: 14px;
    padding: 10px 12px;
  }
  .chat-bubble {
    max-width: 85%;
    font-size: 14px;
    padding: 10px 14px;
  }
  .human-btn {
    padding: 10px 14px;
    font-size: 14px;
  }
}

@media (max-width: 480px) {
  .chat-container {
    height: 75vh !important;
    bottom: 70px !important;
    right: 8px !important;
    width: calc(100vw - 16px) !important;
    border-radius: 12px !important;
  }
  .chat-toggle-btn {
    width: 48px;
    height: 48px;
    font-size: 22px;
    bottom: 16px;
    right: 16px;
  }
  .chat-header {
    padding: 12px 14px;
  }
  .chat-messages {
    padding: 12px;
  }
}
</style>