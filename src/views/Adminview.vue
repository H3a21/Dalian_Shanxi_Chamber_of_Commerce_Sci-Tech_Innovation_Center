<template>
  <div class="admin-container">
    <div class="sidebar" id="sidebar">
      <div class="logo">
        <div class="logo-text">
          网站后台
        </div>
      </div>
      <div class="menu">
        <div class="menu-item" :class="{ active: currentPage === 'dashboard' }" data-page="dashboard" @click="switchPage('dashboard')">
          <span class="menu-icon"></span>
          <span>仪表板</span>
        </div>
        <div class="menu-item" :class="{ active: currentPage === 'users' }" data-page="users" @click="switchPage('users')">
          <span class="menu-icon"></span>
          <span>用户管理</span>
        </div>
        <div class="menu-item" :class="{ active: currentPage === 'send_notify' }" data-page="send_notify" @click="switchPage('send_notify')">
          <span class="menu-icon"></span>
          <span>发送通知</span>
        </div>
        <div class="menu-item" :class="{ active: currentPage === 'agents' }" data-page="agents" @click="switchPage('agents')">
          <span class="menu-icon"></span>
          <span>客服管理</span>
        </div>
        <div class="menu-item" :class="{ active: currentPage === 'audit' }" data-page="audit" @click="switchPage('audit')">
          <span class="menu-icon"></span>
          <span>内容管理</span>
        </div>
        <div class="menu-item" :class="{ active: currentPage === 'experts' }" data-page="experts" @click="switchPage('experts')">
          <span class="menu-icon"></span>
          <span>专家中心</span>
        </div>
        <div class="menu-item" :class="{ active: currentPage === 'partners' }" data-page="partners" @click="switchPage('partners')">
          <span class="menu-icon"></span>
          <span>合作伙伴</span>
        </div>
        <div class="menu-item" :class="{ active: currentPage === 'partner_applies' }" data-page="partner_applies" @click="switchPage('partner_applies')">
          <span class="menu-icon"></span>
          <span>合作申请</span>
        </div>
        <div class="menu-item" :class="{ active: currentPage === 'financial_services' }" data-page="financial_services" @click="switchPage('financial_services')">
          <span class="menu-icon"></span>
          <span>金融服务</span>
        </div>
        <div class="menu-item" :class="{ active: currentPage === 'content' }" data-page="content" @click="switchPage('content')">
          <span class="menu-icon"></span>
          <span>网站编辑</span>
        </div>
        <div class="menu-item" :class="{ active: currentPage === 'faqs' }" data-page="faqs" @click="switchPage('faqs')">
          <span class="menu-icon"></span>
          <span>FAQ管理</span>
        </div>
        <div class="menu-item" :class="{ active: currentPage === 'visit_logs' }" data-page="visit_logs" @click="switchPage('visit_logs')">
          <span class="menu-icon"></span>
          <span>访客日志</span>
        </div>
      </div>
    </div>

    <div class="main-content">
      <div class="header">
        <div class="header-left">
          <button class="menu-toggle" id="menuToggle" @click="toggleSidebar">☰</button>
        </div>
        <div class="header-right">
          <div class="user-tag">👤 Admin</div>
        </div>
      </div>

      <div class="content-area" id="contentArea">
        <div class="page" :class="{ active: currentPage === 'dashboard' }" id="page-dashboard">
          <div class="dashboard-container">

            <!-- 板块一：待办审批概览 -->
            <div class="dashboard-section">
              <div class="section-title">待办审批概览</div>
              <div class="stat-card-row">
                <div class="stat-card stat-card-blue stat-card-clickable" @click="switchPage('audit')">
                  <div class="stat-card-icon">
                    <svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="#1890ff" stroke-width="2"><path d="M9 12l2 2 4-4"/><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
                  </div>
                  <div class="stat-card-body">
                    <div class="stat-card-label">待审核成果</div>
                    <div class="stat-card-value">{{ dashboardData.pending_review.pending_achievements }}</div>
                  </div>
                </div>
                <div class="stat-card stat-card-orange stat-card-clickable" @click="switchPage('audit')">
                  <div class="stat-card-icon">
                    <svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="#fa8c16" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
                  </div>
                  <div class="stat-card-body">
                    <div class="stat-card-label">待审核需求</div>
                    <div class="stat-card-value">{{ dashboardData.pending_review.pending_requirements }}</div>
                  </div>
                </div>
                <div class="stat-card stat-card-purple stat-card-clickable" @click="switchPage('partner_applies')">
                  <div class="stat-card-icon">
                    <svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="#b37feb" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
                  </div>
                  <div class="stat-card-body">
                    <div class="stat-card-label">合作申请待处理</div>
                    <div class="stat-card-value">{{ dashboardData.pending_review.cooperation_applications }}</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 板块二：平台数据总览 -->
            <div class="dashboard-section">
              <div class="section-title">平台数据总览</div>
              <div class="dashboard-top-row">
                <div class="dashboard-left-column">
                  <div ref="chartRef" class="echarts-chart"></div>
                </div>
              </div>
            </div>

            <!-- 板块三：内容分布情况 -->
            <div class="dashboard-section">
              <div class="section-title">内容分布情况</div>
              <div class="chart-row-2col">
                <div class="chart-col">
                  <div class="chart-col-title">成果技术领域分布</div>
                  <div ref="techFieldChartRef" class="echarts-chart pie-chart"></div>
                </div>
                <div class="chart-col">
                  <div class="chart-col-title">成果/需求状态分布</div>
                  <div ref="statusDistChartRef" class="echarts-chart pie-chart"></div>
                </div>
              </div>
            </div>

            <!-- 板块四：客服运营状态 -->
            <div class="dashboard-section">
              <div class="section-title">客服运营状态</div>
              <div class="stat-card-row">
                <div class="stat-card stat-card-green">
                  <div class="stat-card-icon">
                    <svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="#52c41a" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
                  </div>
                  <div class="stat-card-body">
                    <div class="stat-card-label">进行中的会话</div>
                    <div class="stat-card-value">{{ dashboardData.customer_service.active_sessions }}</div>
                  </div>
                </div>
                <div class="stat-card stat-card-yellow">
                  <div class="stat-card-icon">
                    <svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="#faad14" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                  </div>
                  <div class="stat-card-body">
                    <div class="stat-card-label">排队中的会话</div>
                    <div class="stat-card-value">{{ dashboardData.customer_service.waiting_sessions }}</div>
                  </div>
                </div>
                <div class="stat-card stat-card-cyan">
                  <div class="stat-card-icon">
                    <svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="#13c2c2" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
                  </div>
                  <div class="stat-card-body">
                    <div class="stat-card-label">在线客服数</div>
                    <div class="stat-card-value">{{ dashboardData.customer_service.online_agents }}</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 板块五：近7天趋势数据 -->
            <div class="dashboard-section">
              <div class="section-title">近7天趋势数据</div>
              <div ref="trendChartRef" class="echarts-chart trend-chart"></div>
            </div>

            <!-- 板块六：网站日独立访客 -->
            <div class="dashboard-section">
              <div class="section-title">网站日独立访客（近7天）</div>
              <div ref="visitChartRef" class="echarts-chart trend-chart"></div>
            </div>

          </div>
        </div>

        <div class="page" :class="{ active: currentPage === 'users' }" id="page-users">
          <div class="card">
            <div class="card-header">
              <div class="card-title">用户管理列表</div>
              <button class="btn btn-primary" @click="showAddUserModal">
                + 新增用户
              </button>
            </div>
            <div class="card-body">
              <div class="search-box">
                <input type="text" class="search-input" placeholder="输入用户名、真实姓名或手机号检索..." v-model="userSearch">
                <select class="search-select" v-model="userRoleFilter">
                  <option value="">全部角色</option>
                  <option value="admin">管理员</option>
                  <option value="agent">客服</option>
                  <option value="common">普通用户</option>
                </select>
                <select class="search-select" v-model="userStatusFilter">
                  <option value="">全部状态</option>
                  <option value="1">正常</option>
                  <option value="0">禁用</option>
                </select>
                <button class="btn btn-primary" @click="searchUsers">搜索</button>
                <button class="btn btn-default" @click="resetSearch">重置</button>
              </div>

              <div class="table-container">
                <div v-if="userLoading" style="text-align:center;padding:40px;color:#999;">加载中...</div>
                <table v-else class="data-table">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>用户名</th>
                      <th>真实姓名</th>
                      <th>身份证号</th>
                      <th>手机号</th>
                      <th>角色</th>
                      <th>状态</th>
                      <th>最后活跃</th>
                      <th>操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="user in paginatedUsers" :key="user.id">
                      <td>{{ user.id }}</td>
                      <td style="font-weight: 500;">{{ user.username || '-' }}</td>
                      <td>{{ user.real_name || '-' }}</td>
                      <td style="font-size:13px;color:#888;">{{ user.id_card || '-' }}</td>
                      <td>{{ user.phone }}</td>
                      <td>
                        <span :class="['role-badge', `role-${user.role}`]">
                          {{ user.role === 'admin' ? '管理员' : user.role === 'agent' ? '客服' : '普通用户' }}
                        </span>
                      </td>
                      <td>
                        <span :class="['status-badge', user.status === 1 ? 'status-active' : 'status-inactive']">
                          {{ user.status === 1 ? '正常' : '禁用' }}
                        </span>
                      </td>
                      <td style="color: #666;font-size:13px;">{{ user.last_active ? formatTime(user.last_active) : '-' }}</td>
                      <td>
                        <button class="btn btn-sm btn-default" @click="editUser(user.id)" style="margin-right:4px;">编辑</button>
                        <button :class="['btn btn-sm', user.status === 1 ? 'btn-warning' : 'btn-success']" @click="toggleUserStatus(user)" style="margin-right:4px;">
                          {{ user.status === 1 ? '禁用' : '启用' }}
                        </button>
                        <button class="btn btn-sm btn-error" @click="deleteUser(user.id)">删除</button>
                      </td>
                    </tr>
                    <tr v-if="filteredUsers.length === 0">
                      <td colspan="9" style="text-align:center;padding:40px;color:#999;">暂无用户数据</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <!-- 分页 -->
              <div v-if="filteredUsers.length > 0" class="pagination-bar">
                <div class="pagination-info">共 {{ userTotal }} 条，第 {{ userPage }} / {{ userTotalPages }} 页</div>
                <div class="pagination-controls">
                  <span class="pagination-size-select">
                    每页
                    <select v-model.number="userPageSize" @change="handleUserPageSizeChange(userPageSize)">
                      <option :value="5">5</option>
                      <option :value="10">10</option>
                      <option :value="15">15</option>
                      <option :value="20">20</option>
                    </select>
                    条
                  </span>
                  <button class="btn btn-sm btn-default" :disabled="userPage <= 1" @click="handleUserPageChange(userPage - 1)">上一页</button>
                  <button
                    v-for="p in userTotalPages"
                    :key="p"
                    :class="['btn btn-sm', p === userPage ? 'btn-primary' : 'btn-default']"
                    @click="handleUserPageChange(p)"
                    v-show="p === 1 || p === userTotalPages || Math.abs(p - userPage) <= 1"
                  >{{ p }}</button>
                  <button class="btn btn-sm btn-default" :disabled="userPage >= userTotalPages" @click="handleUserPageChange(userPage + 1)">下一页</button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 发送通知 -->
        <div class="page" :class="{ active: currentPage === 'send_notify' }" id="page-send-notify">
          <div class="card">
            <div class="card-header">
              <div class="card-title">发送系统通知</div>
            </div>
            <div class="card-body">
              <div class="notify-form">
                <div class="form-group">
                  <label class="form-label">通知标题</label>
                  <input type="text" class="form-input" v-model="notifyForm.title" placeholder="请输入通知标题" maxlength="100">
                </div>
                <div class="form-group">
                  <label class="form-label">接收对象</label>
                  <div class="form-static">全部普通用户</div>
                </div>
                <div class="form-group">
                  <label class="form-label">通知内容</label>
                  <textarea class="form-textarea" v-model="notifyForm.content" placeholder="请输入通知内容，支持多行文本" rows="8" maxlength="500"></textarea>
                  <div class="form-tip">{{ notifyForm.content.length }} / 500</div>
                </div>
                <div class="form-preview" v-if="notifyForm.title || notifyForm.content">
                  <div class="preview-label">预览效果</div>
                  <div class="preview-card">
                    <div class="preview-title">{{ notifyForm.title || '（标题）' }}</div>
                    <div class="preview-content">{{ notifyForm.content || '（内容）' }}</div>
                  </div>
                </div>
                <div class="form-actions">
                  <button class="btn btn-primary" @click="sendNotification" :disabled="sending">
                    {{ sending ? '发送中...' : '发送通知' }}
                  </button>
                  <button class="btn btn-default" @click="resetNotifyForm">重置</button>
                </div>
                <div v-if="sendResult" class="notify-result" :class="sendResult.type">
                  {{ sendResult.msg }}
                </div>
              </div>
            </div>
          </div>

          <!-- 消息管理 -->
          <div class="card" style="margin-top:24px;">
            <div class="card-header">
              <div class="card-title">消息管理</div>
            </div>
            <div class="card-body">
              <div class="search-box">
                <input type="text" class="search-input" placeholder="搜索标题、内容、业务编号..." v-model="msgKeyword" @keyup.enter="searchMessages">
                <select class="search-select" v-model="msgTypeFilter">
                  <option value="">全部类型</option>
                  <option value="system">系统通知</option>
                  <option value="result">审核通知</option>
                </select>
                <button class="btn btn-primary" @click="searchMessages">搜索</button>
                <button class="btn btn-default" @click="resetMsgSearch">重置</button>
              </div>

              <div v-if="msgLoading" style="text-align:center;padding:40px;color:#999;">加载中...</div>

              <div v-else class="table-container">
                <table class="data-table">
                  <thead>
                    <tr>
                      <th style="width:50px">ID</th>
                      <th>标题</th>
                      <th>内容</th>
                      <th style="width:90px">消息类型</th>
                      <th style="width:70px">业务</th>
                      <th style="width:110px">业务编号</th>
                      <th style="width:110px">接收对象</th>
                      <th style="width:50px">已读</th>
                      <th style="width:140px">发送时间</th>
                      <th style="width:120px">操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-if="msgList.length === 0">
                      <td colspan="10" style="text-align:center;padding:40px;color:#999;">暂无消息数据</td>
                    </tr>
                    <tr v-for="msg in msgList" :key="msg.id">
                      <td>{{ msg.id }}</td>
                      <td style="max-width:150px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" :title="msg.title">{{ msg.title }}</td>
                      <td style="max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" :title="msg.content">{{ msg.content }}</td>
                      <td>
                        <span class="status-badge" :class="msgBadgeClass(msg)">
                          {{ msgBadgeLabel(msg) }}
                        </span>
                      </td>
                      <td style="font-size:13px;color:#888;">{{ msg.biz_type === 'achievement' ? '成果' : msg.biz_type === 'demand' ? '需求' : '-' }}</td>
                      <td style="font-size:13px;color:#888;">{{ msg.biz_id || '-' }}</td>
                      <td>{{ msg.receive_username }}</td>
                      <td>{{ msg.is_read ? '是' : '否' }}</td>
                      <td style="font-size:13px;color:#888;">{{ msg.create_time }}</td>
                      <td>
                        <button class="btn btn-sm btn-default" @click="editMsg(msg)" style="margin-right:4px;">编辑</button>
                        <button class="btn btn-sm btn-error" @click="deleteMsg(msg)">删除</button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <div v-if="msgTotal > 0" class="pagination-bar" style="margin-top:16px;">
                <div class="pagination-info">共 {{ msgTotal }} 条，第 {{ msgPage }} / {{ msgTotalPages }} 页</div>
                <div class="pagination-controls">
                  <span class="pagination-size-select">
                    每页
                    <select v-model.number="msgPageSize" @change="handleMsgPageSizeChange">
                      <option :value="5">5</option>
                      <option :value="10">10</option>
                      <option :value="15">15</option>
                      <option :value="20">20</option>
                    </select>
                    条
                  </span>
                  <button class="btn btn-sm btn-default" :disabled="msgPage <= 1" @click="handleMsgPageChange(msgPage - 1)">上一页</button>
                  <button v-for="p in msgDisplayPages" :key="p" :class="['btn btn-sm', p === msgPage ? 'btn-primary' : 'btn-default']" @click="handleMsgPageChange(p)" v-show="p === 1 || p === msgTotalPages || Math.abs(p - msgPage) <= 1">{{ p }}</button>
                  <button class="btn btn-sm btn-default" :disabled="msgPage >= msgTotalPages" @click="handleMsgPageChange(msgPage + 1)">下一页</button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 消息编辑弹窗 -->
        <div class="modal" :class="{ active: editMsgModalVisible }" id="editMsgModal">
          <div class="modal-content">
            <div class="modal-header">
              <div class="modal-title">编辑消息</div>
              <button class="modal-close" @click="closeEditMsgModal">&times;</button>
            </div>
            <div class="modal-body">
              <div class="form-row">
                <div class="form-group flex-1">
                  <label class="form-label">消息标题</label>
                  <input type="text" class="form-input" v-model="editMsgForm.title" maxlength="100">
                </div>
              </div>
              <div class="form-row">
                <div class="form-group flex-1">
                  <label class="form-label">消息内容</label>
                  <textarea class="form-textarea" v-model="editMsgForm.content" rows="6" maxlength="500"></textarea>
                </div>
              </div>
              <div class="form-row">
                <div class="form-group flex-1">
                  <label class="form-label">消息类型</label>
                  <select class="form-input" v-model="editMsgForm.msg_type">
                    <option value="system">系统通知</option>
                    <option value="result">审核通知</option>
                  </select>
                </div>
              </div>
            </div>
            <div class="modal-footer">
              <button class="btn btn-default" @click="closeEditMsgModal">取消</button>
              <button class="btn btn-primary" @click="submitEditMsg" :disabled="editMsgSaving">{{ editMsgSaving ? '保存中...' : '保存' }}</button>
            </div>
          </div>
        </div>

        <div class="page" :class="{ active: currentPage === 'agents' }" id="page-agents">
          <div class="card">
            <div class="card-header">
              <div class="card-title">客服系统历史记录</div>
            </div>
            <div class="card-body">
              <div class="table-header" style="margin-bottom:16px;display:flex;align-items:center;gap:12px;flex-wrap:wrap;">
                <input v-model="crKeyword" type="text" placeholder="用户名/手机号/消息关键词" style="width:200px;height:36px;border:1px solid #dcdfe6;border-radius:4px;padding:0 12px;" @keyup.enter="loadChatRecords" />
                <select v-model="crStatus" @change="loadChatRecords" style="height:36px;border:1px solid #dcdfe6;border-radius:4px;padding:0 8px;">
                  <option value="">全部状态</option>
                  <option value="pending">等待中</option>
                  <option value="active">进行中</option>
                  <option value="closed">已关闭</option>
                </select>
                <input v-model="crDateFrom" type="date" @change="loadChatRecords" style="height:36px;border:1px solid #dcdfe6;border-radius:4px;padding:0 8px;" title="开始日期" />
                <span style="color:#999;">至</span>
                <input v-model="crDateTo" type="date" @change="loadChatRecords" style="height:36px;border:1px solid #dcdfe6;border-radius:4px;padding:0 8px;" title="结束日期" />
                <button class="btn" @click="loadChatRecords">搜索</button>
              </div>
              <div class="table-container">
                <table class="data-table">
                  <thead>
                    <tr>
                      <th>用户</th>
                      <th>手机号</th>
                      <th>状态</th>
                      <th>消息数</th>
                      <th>创建时间</th>
                      <th>操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="s in crSessions" :key="s.user_id">
                      <td>{{ s.user_real_name || s.user_name }}</td>
                      <td>{{ s.user_phone || '-' }}</td>
                      <td>
                        <span :class="['status-tag', s.status === 'active' ? 'status-published' : s.status === 'pending' ? 'status-draft' : '']" :style="s.status === 'closed' ? 'background:#f0f0f0;color:#999;border-color:#ddd;' : ''">
                          {{ s.status === 'active' ? '进行中' : s.status === 'pending' ? '等待中' : '已关闭' }}
                        </span>
                        <span v-if="(s._allSessionIds || []).length > 1" style="font-size:11px;color:#999;margin-left:4px;">({{ s._allSessionIds.length }}条会话)</span>
                      </td>
                      <td>{{ s.message_count }}</td>
                      <td>{{ formatTime(s.created_at) }}</td>
                      <td class="action-cell">
                        <button class="btn btn-sm" style="background:#e6f7ff;color:#1890ff;border:1px solid #91d5ff;" @click="viewChatDetail(s)">详情</button>
                        <button class="btn btn-sm" style="background:#fff2f0;color:#ff4d4f;border:1px solid #ffa39e;" @click="deleteChatRecord(s)">删除</button>
                      </td>
                    </tr>
                    <tr v-if="crSessions.length === 0">
                      <td colspan="6" style="text-align:center;color:#999;padding:30px;">暂无聊天记录</td>
                    </tr>
                  </tbody>
                </table>
                <div class="pagination" v-if="crTotal > crPageSize" style="margin-top:16px;display:flex;align-items:center;justify-content:center;gap:12px;">
                  <button :disabled="crPage <= 1" @click="goToCrPage(crPage - 1)">上一页</button>
                  <span>第 {{ crPage }} / {{ crTotalPages }} 页（共 {{ crTotal }} 条）</span>
                  <button :disabled="crPage >= crTotalPages" @click="goToCrPage(crPage + 1)">下一页</button>
                </div>
                <div v-else-if="crTotal > 0" style="margin-top:16px;text-align:center;color:#999;font-size:13px;">共 {{ crTotal }} 条记录</div>
              </div>
            </div>
          </div>

          <!-- 聊天记录详情弹窗 -->
          <div class="modal" :class="{ active: crDetailVisible }" @click.self="crDetailVisible = false">
            <div class="modal-content" style="max-width:750px;max-height:85vh;">
              <div class="modal-header">
                <div class="modal-title">聊天记录详情 - {{ crDetailUser }}</div>
                <button class="modal-close" @click="crDetailVisible = false">&times;</button>
              </div>
              <div class="modal-body" style="max-height:60vh;overflow-y:auto;padding:16px 20px;background:#f5f6f7;">
                <div v-if="crDetailLoading" style="text-align:center;padding:40px;color:#999;">加载中...</div>
                <template v-else>
                  <template v-for="(msg, idx) in crDetailMessages" :key="idx">
                    <!-- 不同会话之间的分隔线 -->
                    <div v-if="idx > 0 && msg._sessionId !== crDetailMessages[idx-1]._sessionId"
                         style="text-align:center;margin:16px 0;position:relative;">
                      <span style="display:inline-block;padding:4px 16px;background:#e8e8e8;border-radius:12px;font-size:11px;color:#888;">
                        {{ msg._sessionId === '_bot' ? '机器人聊天' : '会话 ' + (msg._sessionId ? msg._sessionId.substring(0, 8) + '...' : '') }}
                      </span>
                    </div>
                    <!-- 系统消息：居中 -->
                    <div v-if="msg.sender_type === 'system'" style="text-align:center;margin:8px 0;">
                      <span style="display:inline-block;padding:4px 12px;background:#e8e8e8;border-radius:10px;font-size:12px;color:#888;max-width:80%;">
                        {{ msg.content }}
                      </span>
                    </div>
                    <!-- 用户消息：右侧 -->
                    <div v-else-if="msg.sender_type === 'user'" style="display:flex;justify-content:flex-end;margin:10px 0;align-items:flex-start;gap:8px;">
                      <div style="max-width:65%;">
                        <div style="display:flex;justify-content:flex-end;align-items:center;gap:6px;margin-bottom:2px;">
                          <span style="font-size:11px;color:#999;">{{ formatTime(msg.created_at) }}</span>
                          <span style="font-size:12px;color:#1890ff;font-weight:500;">用户</span>
                        </div>
                        <div style="background:#1890ff;color:#fff;padding:8px 14px;border-radius:14px 4px 14px 14px;font-size:14px;line-height:1.6;word-break:break-all;white-space:pre-wrap;">{{ msg.content }}</div>
                      </div>
                      <div style="width:30px;height:30px;border-radius:50%;background:#1890ff;display:flex;align-items:center;justify-content:center;flex-shrink:0;font-size:12px;color:#fff;font-weight:bold;">U</div>
                    </div>
                    <!-- 机器人消息：左侧 -->
                    <div v-else-if="msg.sender_type === 'bot'" style="display:flex;justify-content:flex-start;margin:10px 0;align-items:flex-start;gap:8px;">
                      <div style="width:30px;height:30px;border-radius:50%;background:#fa8c16;display:flex;align-items:center;justify-content:center;flex-shrink:0;font-size:12px;color:#fff;font-weight:bold;">机</div>
                      <div style="max-width:65%;">
                        <div style="display:flex;align-items:center;gap:6px;margin-bottom:2px;">
                          <span style="font-size:12px;color:#333;font-weight:500;">机器人</span>
                          <span style="font-size:11px;color:#999;">{{ formatTime(msg.created_at) }}</span>
                        </div>
                        <div style="background:#fff7e6;color:#333;padding:8px 14px;border-radius:4px 14px 14px 14px;font-size:14px;line-height:1.6;word-break:break-all;white-space:pre-wrap;border:1px solid #ffd591;" v-html="msg.content"></div>
                      </div>
                    </div>
                    <!-- 客服消息：左侧 -->
                    <div v-else style="display:flex;justify-content:flex-start;margin:10px 0;align-items:flex-start;gap:8px;">
                      <div style="width:30px;height:30px;border-radius:50%;background:#52c41a;display:flex;align-items:center;justify-content:center;flex-shrink:0;font-size:12px;color:#fff;font-weight:bold;">客</div>
                      <div style="max-width:65%;">
                        <div style="display:flex;align-items:center;gap:6px;margin-bottom:2px;">
                          <span style="font-size:12px;color:#333;font-weight:500;">客服</span>
                          <span style="font-size:11px;color:#999;">{{ formatTime(msg.created_at) }}</span>
                        </div>
                        <div style="background:#fff;color:#333;padding:8px 14px;border-radius:4px 14px 14px 14px;font-size:14px;line-height:1.6;word-break:break-all;white-space:pre-wrap;border:1px solid #e8e8e8;">{{ msg.content }}</div>
                      </div>
                    </div>
                  </template>
                </template>
              </div>
            </div>
          </div>
        </div>

        <div class="page" :class="{ active: currentPage === 'audit' }" id="page-audit">
          <div class="card">
            <div class="card-header">
              <div class="card-title">内容管理</div>
            </div>
            <div class="card-body">
              <div class="tabs">
                <div class="tab" :class="{ active: auditSubTab === 'achievement' }" @click="switchAuditTab('achievement')">成果管理</div>
                <div class="tab" :class="{ active: auditSubTab === 'requirement' }" @click="switchAuditTab('requirement')">需求管理</div>
              </div>

              <!-- 成果管理 -->
              <div v-show="auditSubTab === 'achievement'">
                <div class="search-box">
                  <input type="text" class="search-input" placeholder="搜索成果名称、编号、持有人..." v-model="achievementKeyword" @keyup.enter="searchAchievement">
                  <select class="search-select" v-model="achievementStatusFilter">
                    <option value="">全部状态</option>
                    <option value="pending">待审核</option>
                    <option value="approved">已通过</option>
                    <option value="rejected">已驳回</option>
                  </select>
                  <button class="btn btn-primary" @click="searchAchievement">搜索</button>
                  <button class="btn btn-default" @click="resetAchievementSearch">重置</button>
                </div>

                <div v-if="achievementLoading" style="text-align:center;padding:40px;color:#999;">加载中...</div>

                <div v-else class="table-container">
                  <table class="data-table">
                    <thead>
                      <tr>
                        <th style="width:50px">序号</th>
                        <th>成果编号</th>
                        <th>成果名称</th>
                        <th>用户ID</th>
                        <th>持有人</th>
                        <th>技术领域</th>
                        <th>技术成熟度</th>
                        <th style="width:80px">状态</th>
                        <th style="width:80px">展示</th>
                        <th style="width:140px">创建时间</th>
                        <th style="width:200px">操作</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-if="achievements.length === 0">
                        <td colspan="11" style="text-align:center;padding:40px;color:#999;">暂无成果数据</td>
                      </tr>
                      <tr v-for="(item, idx) in achievements" :key="item.id">
                        <td>{{ idx + 1 + (achievementPage - 1) * achievementPageSize }}</td>
                        <td style="font-size:13px;color:#888;">{{ item.achievement_code }}</td>
                        <td style="font-weight:500;">{{ item.achievement_name }}</td>
                        <td style="font-size:13px;color:#888;">{{ item.user_id }}</td>
                        <td>{{ item.owner }}</td>
                        <td>{{ formatFieldsWithOther(item.tech_fields, item.tech_fields_other) }}</td>
                        <td style="font-size:13px;color:#888;">{{ item.tech_maturity || '-' }}</td>
                        <td><span :class="'status-badge status-' + item.status">{{ getStatusText(item.status) }}</span></td>
                        <td>
                          <span :style="{ color: item.is_display ? '#52c41a' : '#999', fontSize: '13px' }">
                            {{ item.is_display ? '展示中' : '已隐藏' }}
                          </span>
                        </td>
                        <td style="font-size:13px;color:#888;">{{ formatTime(item.created_at) }}</td>
                        <td>
                          <button class="btn btn-sm btn-default" @click="viewAchievementDetail(item.id)" style="margin-right:4px;">查看</button>
                          <button class="btn btn-sm btn-primary" @click="editAchievement(item)" style="margin-right:4px;">编辑</button>
                          <button v-if="item.status === 'pending'" class="btn btn-sm btn-primary" @click="reviewAchievement(item.id, 'approved')" style="margin-right:4px;">通过</button>
                          <button v-if="item.status === 'pending'" class="btn btn-sm btn-error" @click="reviewAchievement(item.id, 'rejected')" style="margin-right:4px;">驳回</button>
                          <button v-if="item.status === 'approved'" class="btn btn-sm btn-default" @click="toggleAchievementDisplay(item)" style="margin-right:4px;">{{ item.is_display ? '隐藏' : '展示' }}</button>
                          <button class="btn btn-sm btn-error" @click="deleteAchievement(item.id)">删除</button>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>

                <div v-if="achievements.length > 0" class="pagination-bar" style="margin-top:16px;">
                  <div class="pagination-info">共 {{ achievementTotal }} 条，第 {{ achievementPage }} / {{ achievementTotalPages }} 页</div>
                  <div class="pagination-controls">
                    <span class="pagination-size-select">
                      每页
                      <select v-model.number="achievementPageSize" @change="handleAchievementPageSizeChange(achievementPageSize)">
                        <option :value="5">5</option>
                        <option :value="10">10</option>
                        <option :value="15">15</option>
                        <option :value="20">20</option>
                      </select>
                      条
                    </span>
                    <button class="btn btn-sm btn-default" :disabled="achievementPage <= 1" @click="handleAchievementPageChange(achievementPage - 1)">上一页</button>
                    <button v-for="p in achievementTotalPages" :key="p" :class="['btn btn-sm', p === achievementPage ? 'btn-primary' : 'btn-default']" @click="handleAchievementPageChange(p)" v-show="p === 1 || p === achievementTotalPages || Math.abs(p - achievementPage) <= 1">{{ p }}</button>
                    <button class="btn btn-sm btn-default" :disabled="achievementPage >= achievementTotalPages" @click="handleAchievementPageChange(achievementPage + 1)">下一页</button>
                  </div>
                </div>
              </div>

              <!-- 需求管理 -->
              <div v-show="auditSubTab === 'requirement'">
                <div class="search-box">
                  <input type="text" class="search-input" placeholder="搜索需求名称、编号、企业..." v-model="requirementKeyword" @keyup.enter="searchRequirement">
                  <select class="search-select" v-model="requirementStatusFilter">
                    <option value="">全部状态</option>
                    <option value="pending">待审核</option>
                    <option value="approved">已通过</option>
                    <option value="rejected">已驳回</option>
                  </select>
                  <button class="btn btn-primary" @click="searchRequirement">搜索</button>
                  <button class="btn btn-default" @click="resetRequirementSearch">重置</button>
                </div>

                <div v-if="requirementLoading" style="text-align:center;padding:40px;color:#999;">加载中...</div>

                <div v-else class="table-container">
                  <table class="data-table">
                    <thead>
                      <tr>
                        <th style="width:50px">序号</th>
                        <th>需求编号</th>
                        <th>需求名称</th>
                        <th>用户ID</th>
                        <th>企业名称</th>
                        <th>应用领域</th>
                        <th>预算(万元)</th>
                        <th style="width:80px">审核状态</th>
                        <th style="width:90px">供需状态</th>
                        <th style="width:80px">展示</th>
                        <th style="width:140px">创建时间</th>
                        <th style="width:200px">操作</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-if="requirements.length === 0">
                        <td colspan="12" style="text-align:center;padding:40px;color:#999;">暂无需求数据</td>
                      </tr>
                      <tr v-for="(item, idx) in requirements" :key="item.id">
                        <td>{{ idx + 1 + (requirementPage - 1) * requirementPageSize }}</td>
                        <td style="font-size:13px;color:#888;">{{ item.demand_code }}</td>
                        <td style="font-weight:500;">{{ item.demand_name }}</td>
                        <td style="font-size:13px;color:#888;">{{ item.user_id }}</td>
                        <td>{{ item.company_name }}</td>
                        <td>{{ formatFieldsWithOther(item.tech_fields, item.tech_fields_other) }}</td>
                        <td style="font-size:13px;color:#888;">{{ item.budget != null ? item.budget : '-' }}</td>
                        <td><span :class="'status-badge status-' + item.status">{{ getStatusText(item.status) }}</span></td>
                        <td><span :class="'match-status-badge match-' + (item.match_status || '待对接')">{{ item.match_status || '待对接' }}</span></td>
                        <td>
                          <span :style="{ color: item.is_display ? '#52c41a' : '#999', fontSize: '13px' }">
                            {{ item.is_display ? '展示中' : '已隐藏' }}
                          </span>
                        </td>
                        <td style="font-size:13px;color:#888;">{{ formatTime(item.created_at) }}</td>
                        <td>
                          <button class="btn btn-sm btn-default" @click="viewRequirementDetail(item.id)" style="margin-right:4px;">查看</button>
                          <button class="btn btn-sm btn-primary" @click="editRequirement(item)" style="margin-right:4px;">编辑</button>
                          <button v-if="item.status === 'pending'" class="btn btn-sm btn-primary" @click="reviewRequirement(item.id, 'approved')" style="margin-right:4px;">通过</button>
                          <button v-if="item.status === 'pending'" class="btn btn-sm btn-error" @click="reviewRequirement(item.id, 'rejected')" style="margin-right:4px;">驳回</button>
                          <button v-if="item.status === 'approved'" class="btn btn-sm btn-default" @click="toggleRequirementDisplay(item)" style="margin-right:4px;">{{ item.is_display ? '隐藏' : '展示' }}</button>
                          <span class="custom-dropdown" :data-id="item.id">
                            <button class="btn btn-sm btn-default dropdown-trigger" @click="toggleMatchDropdown($event, item.id)">
                              {{ item.match_status || '待对接' }}
                              <span class="dropdown-arrow">▼</span>
                            </button>
                            <div v-if="activeMatchDropdown === item.id" class="dropdown-menu" :style="dropdownStyle" @click.stop @mouseleave="activeMatchDropdown = null">
                              <div class="dropdown-item" :class="{ active: (item.match_status || '待对接') === '待对接' }" @click="quickUpdateMatchStatus(item.id, '待对接')">待对接</div>
                              <div class="dropdown-item" :class="{ active: (item.match_status || '待对接') === '对接中' }" @click="quickUpdateMatchStatus(item.id, '对接中')">对接中</div>
                              <div class="dropdown-item" :class="{ active: (item.match_status || '待对接') === '已完成' }" @click="quickUpdateMatchStatus(item.id, '已完成')">已完成</div>
                            </div>
                          </span>
                          <button class="btn btn-sm btn-error" @click="deleteRequirement(item.id)">删除</button>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>

                <div v-if="requirements.length > 0" class="pagination-bar" style="margin-top:16px;">
                  <div class="pagination-info">共 {{ requirementTotal }} 条，第 {{ requirementPage }} / {{ requirementTotalPages }} 页</div>
                  <div class="pagination-controls">
                    <span class="pagination-size-select">
                      每页
                      <select v-model.number="requirementPageSize" @change="handleRequirementPageSizeChange(requirementPageSize)">
                        <option :value="5">5</option>
                        <option :value="10">10</option>
                        <option :value="15">15</option>
                        <option :value="20">20</option>
                      </select>
                      条
                    </span>
                    <button class="btn btn-sm btn-default" :disabled="requirementPage <= 1" @click="handleRequirementPageChange(requirementPage - 1)">上一页</button>
                    <button v-for="p in requirementTotalPages" :key="p" :class="['btn btn-sm', p === requirementPage ? 'btn-primary' : 'btn-default']" @click="handleRequirementPageChange(p)" v-show="p === 1 || p === requirementTotalPages || Math.abs(p - requirementPage) <= 1">{{ p }}</button>
                    <button class="btn btn-sm btn-default" :disabled="requirementPage >= requirementTotalPages" @click="handleRequirementPageChange(requirementPage + 1)">下一页</button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 成果详情弹窗（管理优化版） -->
          <div class="modal" :class="{ active: achievementDetailVisible }" id="achievementDetailModal">
            <div class="modal-content modal-lg" style="max-width:960px;width:900px;">
              <div class="modal-header">
                <div class="modal-title">成果详情</div>
                <button class="modal-close" @click="achievementDetailVisible = false">&times;</button>
              </div>
              <div class="modal-body" style="padding:20px 24px;">
                <div v-if="achievementDetailData" class="admin-detail">
                  <!-- 状态栏 -->
                  <div class="detail-status-bar">
                    <div class="status-item">
                      <span class="status-label">审核状态</span>
                      <span :class="'status-badge status-' + achievementDetailData.status">{{ getStatusText(achievementDetailData.status) }}</span>
                    </div>
                    <div class="status-item">
                      <span class="status-label">展示状态</span>
                      <span :style="{ color: achievementDetailData.is_display ? '#52c41a' : '#999', fontWeight:600 }">
                        {{ achievementDetailData.is_display ? '展示中' : '已隐藏' }}
                      </span>
                    </div>
                    <div class="status-item">
                      <span class="status-label">用户ID</span>
                      <span style="color:#666;font-size:13px;">{{ achievementDetailData.user_id || '-' }}</span>
                    </div>
                    <div class="status-item">
                      <span class="status-label">创建时间</span>
                      <span style="color:#888;font-size:13px;">{{ formatTime(achievementDetailData.created_at) }}</span>
                    </div>
                    <div class="status-item">
                      <span class="status-label">更新时间</span>
                      <span style="color:#888;font-size:13px;">{{ formatTime(achievementDetailData.updated_at) }}</span>
                    </div>
                  </div>

                  <!-- 基本信息 -->
                  <div class="detail-section">
                    <div class="detail-section-title">一、成果基本信息</div>
                    <div class="detail-grid-3col">
                      <div class="detail-field">
                        <span class="detail-label">成果名称</span>
                        <span class="detail-value" style="font-weight:600;color:#1890ff;">{{ achievementDetailData.achievement_name || '-' }}</span>
                      </div>
                      <div class="detail-field">
                        <span class="detail-label">成果编号</span>
                        <span class="detail-value">{{ achievementDetailData.achievement_code || '-' }}</span>
                      </div>
                      <div class="detail-field">
                        <span class="detail-label">持有人</span>
                        <span class="detail-value">{{ achievementDetailData.owner || '-' }}</span>
                      </div>
                      <div class="detail-field">
                        <span class="detail-label">所属地区</span>
                        <span class="detail-value">{{ formatRegion(achievementDetailData.region) }}</span>
                      </div>
                      <div class="detail-field">
                        <span class="detail-label">技术领域</span>
                        <span class="detail-value">{{ formatFieldsWithOther(achievementDetailData.tech_fields, achievementDetailData.tech_fields_other) }}</span>
                      </div>
                      <div class="detail-field">
                        <span class="detail-label">技术成熟度</span>
                        <span class="detail-value" style="font-weight:600;color:#1890ff;">{{ achievementDetailData.tech_maturity || '-' }}</span>
                      </div>
                      <div class="detail-field full-width">
                        <span class="detail-label">转化方式</span>
                        <span class="detail-value">{{ formatTransferMethods(achievementDetailData.transfer_methods, achievementDetailData.transfer_methods_other) }}</span>
                      </div>
                    </div>
                  </div>

                  <!-- 成果描述 -->
                  <div class="detail-section">
                    <div class="detail-section-title">二、成果描述</div>
                    <div class="detail-grid-1col">
                      <div class="detail-field">
                        <span class="detail-label">成果摘要</span>
                        <div class="detail-text">{{ achievementDetailData.description?.summary || '-' }}</div>
                      </div>
                      <div class="detail-field">
                        <span class="detail-label">创新性评价</span>
                        <span class="detail-value">{{ achievementDetailData.description?.innovation_level || '-' }}</span>
                      </div>
                      <div class="detail-field">
                        <span class="detail-label">与现有技术相比的优势</span>
                        <div class="detail-text">{{ achievementDetailData.description?.advantages || '-' }}</div>
                      </div>
                      <div class="detail-field">
                        <span class="detail-label">核心技术指标</span>
                        <div class="detail-text">{{ achievementDetailData.description?.core_indicators || '-' }}</div>
                      </div>
                      <div class="detail-field">
                        <span class="detail-label">知识产权</span>
                        <div class="detail-text">{{ achievementDetailData.description?.intellectual_property || '-' }}</div>
                      </div>
                    </div>
                  </div>

                  <!-- 成果转化期望 -->
                  <div class="detail-section">
                    <div class="detail-section-title">三、成果转化期望</div>
                    <div class="detail-grid-2col">
                      <div class="detail-field full-width">
                        <span class="detail-label">合作方式偏好及财务预期</span>
                        <span class="detail-value" style="color:#faad14;font-weight:600;">{{ formatTransferPreference(achievementDetailData.transfer_preference) }}</span>
                      </div>
                      <div class="detail-field">
                        <span class="detail-label">期望完成时间</span>
                        <span class="detail-value">{{ formatExpectedCompleteDate(achievementDetailData.transfer_preference?.expected_complete_date) || '未指定' }}</span>
                      </div>
                    </div>
                  </div>
                </div>
                <div v-else style="text-align:center;padding:40px;color:#999;">加载中...</div>
              </div>
              <div class="modal-footer">
                <button class="btn btn-default" @click="achievementDetailVisible = false">关闭</button>
              </div>
            </div>
          </div>

          <!-- 成果编辑弹窗（照搬成果采集表样式） -->
          <div class="modal" :class="{ active: achievementEditVisible }" id="achievementEditModal">
            <div class="modal-content modal-lg" style="max-width:1000px;width:960px;">
              <div class="modal-header">
                <div class="modal-title">编辑成果 - 《成果采集表》</div>
                <button class="modal-close" @click="achievementEditVisible = false">&times;</button>
              </div>
              <div class="modal-body frontend-form">
                <el-form ref="achievementEditFormRef" :model="achievementEditData" label-position="left" label-width="160px">
                  <div class="form-card">
                    <div class="form-section-title">一、成果基本信息</div>
                    <table class="form-table">
                      <tbody>
                        <tr>
                          <th><span class="required">*</span> 成果名称</th>
                          <td>
                            <el-form-item class="table-form-item">
                              <el-input v-model="achievementEditData.achievement_name" placeholder="请输入完整成果名称" />
                            </el-form-item>
                          </td>
                        </tr>
                        <tr>
                          <th><span class="required">*</span> 成果持有人</th>
                          <td>
                            <el-form-item class="table-form-item">
                              <el-input v-model="achievementEditData.owner" placeholder="高校/科研院所/企业/团队负责人" />
                            </el-form-item>
                          </td>
                        </tr>
                        <tr>
                          <th><span class="required">*</span> 所属地区</th>
                          <td>
                            <el-form-item class="table-form-item">
                              <div class="region-selectors">
                                <el-select v-model="achievementEditData.province" placeholder="选择省份">
                                  <el-option v-for="p in provinces" :key="p" :label="p" :value="p" />
                                </el-select>
                                <el-select v-model="achievementEditData.city" :placeholder="achievementEditData.province && ['北京市','天津市','上海市','重庆市'].includes(achievementEditData.province) ? '选择区' : '选择城市'" :disabled="!achievementEditData.province">
                                  <el-option v-for="c in (citiesMap[achievementEditData.province] || [])" :key="c" :label="c" :value="c" />
                                </el-select>
                              </div>
                              <div v-if="achievementEditData.province" style="margin-top:8px;color:#666;font-size:14px;">
                                已选择：{{ achievementEditData.province }}{{ achievementEditData.city ? ' ' + achievementEditData.city : '' }}
                              </div>
                            </el-form-item>
                          </td>
                        </tr>
                        <tr>
                          <th><span class="required">*</span> 技术领域</th>
                          <td>
                            <el-form-item class="table-form-item">
                              <el-select v-model="achievementEditData.tech_field" placeholder="--请选择--">
                                <el-option v-for="opt in achievementTechFieldOptions" :key="opt" :label="opt" :value="opt" />
                              </el-select>
                            </el-form-item>
                            <el-form-item v-if="achievementEditData.tech_field === '其他'" class="table-form-item">
                              <el-input v-model="achievementEditData.tech_field_other" placeholder="请填写具体领域" />
                            </el-form-item>
                          </td>
                        </tr>
                        <tr>
                          <th><span class="required">*</span> 技术成熟度</th>
                          <td>
                            <el-form-item class="table-form-item">
                              <el-select v-model="achievementEditData.tech_maturity" placeholder="--请选择--">
                                <el-option label="实验室理论阶段" value="实验室理论阶段" />
                                <el-option label="中试阶段" value="中试阶段" />
                                <el-option label="可规模量产" value="可规模量产" />
                              </el-select>
                            </el-form-item>
                          </td>
                        </tr>
                        <tr>
                          <th>转化方式</th>
                          <td>
                            <el-form-item class="table-form-item">
                              <el-checkbox-group v-model="achievementEditData.transfer_methods">
                                <div class="checkbox-vertical">
                                  <el-checkbox value="技术转让">技术转让</el-checkbox>
                                  <el-checkbox value="技术许可">技术许可</el-checkbox>
                                  <el-checkbox value="技术入股">技术入股</el-checkbox>
                                  <el-checkbox value="合作开发">合作开发</el-checkbox>
                                  <el-checkbox value="其他">其他</el-checkbox>
                                </div>
                              </el-checkbox-group>
                            </el-form-item>
                            <el-input v-if="achievementEditData.transfer_methods.includes('其他')" v-model="achievementEditData.transfer_other" placeholder="请填写具体转化方式" style="margin-top:8px;width:300px;" />
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>

                  <div class="form-card">
                    <div class="form-section-title">二、成果描述</div>
                    <table class="form-table">
                      <tbody>
                        <tr>
                          <th><span class="required">*</span> 成果摘要</th>
                          <td>
                            <el-form-item class="table-form-item">
                              <el-input v-model="achievementEditData.description.summary" type="textarea" :rows="4" placeholder="请简要描述成果的主要内容" />
                            </el-form-item>
                          </td>
                        </tr>
                        <tr>
                          <th>技术优势描述</th>
                          <td>
                            <div style="margin-bottom:15px;">
                              <div class="field-label">创新性：</div>
                              <el-radio-group v-model="achievementEditData.innovation_level">
                                <el-radio value="国际领先">国际领先</el-radio>
                                <el-radio value="国内领先">国内领先</el-radio>
                                <el-radio value="行业领先">行业领先</el-radio>
                              </el-radio-group>
                            </div>
                            <div>
                              <div class="field-label">与现有技术相比的优势：</div>
                              <el-input v-model="achievementEditData.description.advantages" type="textarea" :rows="3" placeholder="请描述与现有技术相比的优势" />
                            </div>
                          </td>
                        </tr>
                        <tr>
                          <th>核心技术指标</th>
                          <td>
                            <el-input v-model="achievementEditData.description.core_indicators" type="textarea" :rows="3" placeholder="请填写核心技术指标" />
                          </td>
                        </tr>
                        <tr>
                          <th>获得的知识产权</th>
                          <td>
                            <el-input v-model="achievementEditData.description.intellectual_property" type="textarea" :rows="3" placeholder="请填写已获得的知识产权情况（专利、软件著作权等）" />
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>

                  <div class="form-card">
                    <div class="form-section-title">三、成果转化期望</div>
                    <table class="form-table">
                      <tbody>
                        <tr>
                          <th><span class="required">*</span> 合作方式偏好</th>
                          <td>
                            <el-form-item class="table-form-item">
                              <el-radio-group v-model="achievementEditData.cooperationPref">
                                <div class="checkbox-vertical">
                                  <div class="radio-with-extra">
                                    <el-radio value="技术转让">技术转让</el-radio>
                                    <span v-if="achievementEditData.cooperationPref === '技术转让'" class="extra-input">
                                      （转让费：期望 <el-input-number v-model.number="achievementEditData.transfer_fee" :precision="2" :controls="false" size="small" style="width:120px;" placeholder="万元" /> 万元）
                                    </span>
                                  </div>
                                  <div class="radio-with-extra">
                                    <el-radio value="技术许可">技术许可</el-radio>
                                    <span v-if="achievementEditData.cooperationPref === '技术许可'" class="extra-input">
                                      （许可方式：
                                      <el-radio-group v-model="achievementEditData.licenseType" size="small">
                                        <el-radio value="独占">独占</el-radio>
                                        <el-radio value="排他">排他</el-radio>
                                        <el-radio value="普通">普通</el-radio>
                                      </el-radio-group>
                                      ）
                                    </span>
                                  </div>
                                  <div class="radio-with-extra">
                                    <el-radio value="技术入股">技术入股</el-radio>
                                    <span v-if="achievementEditData.cooperationPref === '技术入股'" class="extra-input">
                                      （作价 <el-input-number v-model.number="achievementEditData.investment_valuation" :precision="2" :controls="false" size="small" style="width:120px;" placeholder="万元" /> 万元，占 <el-input-number v-model.number="achievementEditData.equityPercent" :controls="false" :min="0" :max="100" :precision="2" :step="0.1" size="small" style="width:100px;" /> 股%）
                                    </span>
                                  </div>
                                  <el-radio value="合作开发">合作开发</el-radio>
                                  <div class="radio-with-extra">
                                    <el-radio value="其他">其他</el-radio>
                                    <span v-if="achievementEditData.cooperationPref === '其他'" class="extra-input">
                                      <el-input v-model="achievementEditData.cooperationOther" placeholder="请填写" size="small" style="width:200px;" />
                                    </span>
                                  </div>
                                </div>
                              </el-radio-group>
                            </el-form-item>
                          </td>
                        </tr>
                        <tr>
                          <th>期望转化时间</th>
                          <td>
                            <div class="inline-row">
                              <el-date-picker v-model="achievementEditData.expectDate" type="month" placeholder="选择月份" format="YYYY年M月" class="expect-date-picker" />
                              <span style="color:#666;white-space:nowrap;">前完成转化</span>
                            </div>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </el-form>
              </div>
              <div class="modal-footer">
                <button class="btn btn-default" @click="achievementEditVisible = false">取消</button>
                <button class="btn btn-primary" @click="saveAchievementEdit">保存</button>
              </div>
            </div>
          </div>

          <!-- 需求详情弹窗（管理优化版） -->
          <div class="modal" :class="{ active: requirementDetailVisible }" id="requirementDetailModal">
            <div class="modal-content modal-lg" style="max-width:960px;width:900px;">
              <div class="modal-header">
                <div class="modal-title">需求详情</div>
                <button class="modal-close" @click="requirementDetailVisible = false">&times;</button>
              </div>
              <div class="modal-body" style="padding:20px 24px;">
                <div v-if="!requirementDetailData" style="text-align:center;padding:40px;color:#999;">加载中...</div>
                <div v-else class="admin-detail">
                  <!-- 状态栏 -->
                  <div class="detail-status-bar">
                    <div class="status-item">
                      <span class="status-label">审核状态</span>
                      <span :class="'status-badge status-' + requirementDetailData.status">{{ getStatusText(requirementDetailData.status) }}</span>
                    </div>
                    <div class="status-item">
                      <span class="status-label">展示状态</span>
                      <span :style="{ color: requirementDetailData.is_display ? '#52c41a' : '#999', fontWeight:600 }">
                        {{ requirementDetailData.is_display ? '展示中' : '已隐藏' }}
                      </span>
                    </div>
                    <div class="status-item">
                      <span class="status-label">供需状态</span>
                      <span :class="'match-status-badge match-' + (requirementDetailData.match_status || '待对接')" style="font-size:13px;padding:3px 12px;">
                        {{ requirementDetailData.match_status || '待对接' }}
                      </span>
                    </div>
                    <div class="status-item">
                      <span class="status-label">用户ID</span>
                      <span style="color:#666;font-size:13px;">{{ requirementDetailData.user_id || '-' }}</span>
                    </div>
                    <div class="status-item">
                      <span class="status-label">创建时间</span>
                      <span style="color:#888;font-size:13px;">{{ formatTime(requirementDetailData.created_at) }}</span>
                    </div>
                    <div class="status-item">
                      <span class="status-label">更新时间</span>
                      <span style="color:#888;font-size:13px;">{{ formatTime(requirementDetailData.updated_at) }}</span>
                    </div>
                  </div>

                  <!-- 基本信息 -->
                  <div class="detail-section">
                    <div class="detail-section-title">一、需求基本信息</div>
                    <div class="detail-grid-3col">
                      <div class="detail-field">
                        <span class="detail-label">需求名称</span>
                        <span class="detail-value" style="font-weight:600;color:#1890ff;">{{ requirementDetailData.demand_name || '-' }}</span>
                      </div>
                      <div class="detail-field">
                        <span class="detail-label">需求编号</span>
                        <span class="detail-value">{{ requirementDetailData.demand_code || '-' }}</span>
                      </div>
                      <div class="detail-field">
                        <span class="detail-label">企业名称</span>
                        <span class="detail-value">{{ requirementDetailData.company_name || '-' }}</span>
                      </div>
                      <div class="detail-field">
                        <span class="detail-label">所属地区</span>
                        <span class="detail-value">{{ formatRegion(requirementDetailData.region) }}</span>
                      </div>
                      <div class="detail-field">
                        <span class="detail-label">应用领域</span>
                        <span class="detail-value">{{ formatFieldsWithOther(requirementDetailData.tech_fields, requirementDetailData.tech_fields_other) }}</span>
                      </div>
                      <div class="detail-field">
                        <span class="detail-label">需求类型</span>
                        <span class="detail-value">{{ formatFieldsWithOther(requirementDetailData.demand_types, requirementDetailData.demand_types_other) }}</span>
                      </div>
                      <div class="detail-field">
                        <span class="detail-label">项目预算</span>
                        <span class="detail-value">{{ requirementDetailData.description?.budget != null ? requirementDetailData.description.budget + '万元' : '未指定' }}</span>
                      </div>
                    </div>
                  </div>

                  <!-- 需求描述 -->
                  <div class="detail-section">
                    <div class="detail-section-title">二、需求描述</div>
                    <div class="detail-grid-1col">
                      <div class="detail-field">
                        <span class="detail-label">需求概述</span>
                        <div class="detail-text">{{ requirementDetailData.description?.overview || '-' }}</div>
                      </div>
                      <div class="detail-field">
                        <span class="detail-label">期望解决的问题</span>
                        <div class="detail-text">{{ requirementDetailData.description?.target_problems || '-' }}</div>
                      </div>
                    </div>
                  </div>

                  <!-- 供需状态操作 -->
                  <div class="detail-section">
                    <div class="detail-section-title">三、供需状态</div>
                    <div class="detail-grid-2col">
                      <div class="detail-field">
                        <span class="detail-label">当前状态</span>
                        <span :class="'match-status-badge match-' + (requirementDetailData.match_status || '待对接')" style="font-size:14px;padding:4px 16px;">
                          {{ requirementDetailData.match_status || '待对接' }}
                        </span>
                      </div>
                      <div class="detail-field full-width" style="margin-top:4px;">
                        <span class="detail-label">设置状态</span>
                        <div style="display:flex;gap:8px;">
                          <button class="btn btn-sm" :class="requirementDetailData.match_status === '待对接' ? 'btn-primary' : 'btn-default'" @click="updateRequirementMatchStatus('待对接')" :disabled="requirementDetailData.match_status === '待对接'">待对接</button>
                          <button class="btn btn-sm" :class="requirementDetailData.match_status === '对接中' ? 'btn-primary' : 'btn-default'" @click="updateRequirementMatchStatus('对接中')" :disabled="requirementDetailData.match_status === '对接中'">对接中</button>
                          <button class="btn btn-sm" :class="requirementDetailData.match_status === '已完成' ? 'btn-primary' : 'btn-default'" @click="updateRequirementMatchStatus('已完成')" :disabled="requirementDetailData.match_status === '已完成'">已完成</button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div class="modal-footer">
                <button class="btn btn-default" @click="requirementDetailVisible = false">关闭</button>
              </div>
            </div>
          </div>

          <!-- 需求编辑弹窗（照搬需求采集表样式） -->
          <div class="modal" :class="{ active: requirementEditVisible }" id="requirementEditModal">
            <div class="modal-content modal-lg" style="max-width:1000px;width:960px;">
              <div class="modal-header">
                <div class="modal-title">编辑需求 - 《需求采集表》</div>
                <button class="modal-close" @click="requirementEditVisible = false">&times;</button>
              </div>
              <div class="modal-body frontend-form">
                <el-form ref="requirementEditFormRef" :model="requirementEditData" label-position="left" label-width="160px">
                  <div class="form-card">
                    <div class="form-section-title">一、需求基本信息</div>
                    <table class="form-table">
                      <tbody>
                        <tr>
                          <th><span class="required">*</span> 企业名称</th>
                          <td>
                            <el-form-item class="table-form-item">
                              <el-input v-model="requirementEditData.company_name" placeholder="请输入企业全称" />
                            </el-form-item>
                          </td>
                        </tr>
                        <tr>
                          <th><span class="required">*</span> 需求名称</th>
                          <td>
                            <el-form-item class="table-form-item">
                              <el-input v-model="requirementEditData.demand_name" placeholder="请输入需求名称" />
                            </el-form-item>
                          </td>
                        </tr>
                        <tr>
                          <th><span class="required">*</span> 所属地区</th>
                          <td>
                            <el-form-item class="table-form-item">
                              <div class="region-selectors">
                                <el-select v-model="requirementEditData.province" placeholder="选择省份">
                                  <el-option v-for="p in provinces" :key="p" :label="p" :value="p" />
                                </el-select>
                                <el-select v-model="requirementEditData.city" :placeholder="requirementEditData.province && ['北京市','天津市','上海市','重庆市'].includes(requirementEditData.province) ? '选择区' : '选择城市'" :disabled="!requirementEditData.province">
                                  <el-option v-for="c in (citiesMap[requirementEditData.province] || [])" :key="c" :label="c" :value="c" />
                                </el-select>
                              </div>
                              <div v-if="requirementEditData.province" style="margin-top:8px;color:#666;font-size:14px;">
                                已选择：{{ requirementEditData.province }}{{ requirementEditData.city ? ' ' + requirementEditData.city : '' }}
                              </div>
                            </el-form-item>
                          </td>
                        </tr>
                        <tr>
                          <th><span class="required">*</span> 应用领域</th>
                          <td>
                            <el-form-item class="table-form-item">
                              <div class="industry-group">
                                <div class="industry-category">
                                  <div class="category-title">战略性新兴产业（最多选一个）</div>
                                  <el-radio-group v-model="requirementEditData.emergingIndustry">
                                    <el-radio value="节能环保产业">节能环保产业</el-radio>
                                    <el-radio value="新一代信息技术产业">新一代信息技术产业</el-radio>
                                    <el-radio value="高端装备制造产业">高端装备制造产业</el-radio>
                                    <el-radio value="新能源产业">新能源产业</el-radio>
                                    <el-radio value="新材料产业">新材料产业</el-radio>
                                    <el-radio value="生物产业">生物产业</el-radio>
                                    <el-radio value="新能源汽车产业">新能源汽车产业</el-radio>
                                    <el-radio value="数字创意产业">数字创意产业</el-radio>
                                  </el-radio-group>
                                </div>
                                <div class="industry-category">
                                  <div class="category-title">传统产业（最多选一个）</div>
                                  <el-radio-group v-model="requirementEditData.traditionalIndustry">
                                    <el-radio value="农、林、牧、渔业">农、林、牧、渔业</el-radio>
                                    <el-radio value="采矿业">采矿业</el-radio>
                                    <el-radio value="制造业">制造业</el-radio>
                                    <el-radio value="水利环境">水利环境</el-radio>
                                    <el-radio value="教育，医疗卫生">教育，医疗卫生</el-radio>
                                    <el-radio value="文化、体育和娱乐">文化、体育和娱乐</el-radio>
                                    <el-radio value="电力、热力和燃气">电力、热力和燃气</el-radio>
                                    <el-radio value="建筑业">建筑业</el-radio>
                                    <el-radio value="交通运输和仓储">交通运输和仓储</el-radio>
                                    <el-radio value="住宿和餐饮业">住宿和餐饮业</el-radio>
                                    <el-radio value="信息传输、软件和信息技术服务业">信息传输、软件和信息技术服务业</el-radio>
                                    <el-radio value="金融业">金融业</el-radio>
                                    <el-radio value="房地产业">房地产业</el-radio>
                                    <el-radio value="新能源">新能源</el-radio>
                                    <el-radio value="科学研究和技术服务">科学研究和技术服务</el-radio>
                                  </el-radio-group>
                                </div>
                              </div>
                            </el-form-item>
                          </td>
                        </tr>
                        <tr>
                          <th><span class="required">*</span> 需求类型</th>
                          <td>
                            <el-form-item class="table-form-item">
                              <el-select v-model="requirementEditData.demand_type" placeholder="--请选择--">
                                <el-option label="技术需求" value="技术需求" />
                                <el-option label="金融需求" value="金融需求" />
                                <el-option label="场景需求" value="场景需求" />
                                <el-option label="其他" value="其他" />
                              </el-select>
                            </el-form-item>
                            <el-form-item v-if="requirementEditData.demand_type === '其他'" class="table-form-item" style="margin-top:8px;">
                              <el-input v-model="requirementEditData.demand_type_other" placeholder="请填写具体需求类型" />
                            </el-form-item>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                  <div class="form-card">
                    <div class="form-section-title">二、需求描述</div>
                    <table class="form-table">
                      <tbody>
                        <tr>
                          <th><span class="required">*</span> 需求概述</th>
                          <td>
                            <el-form-item class="table-form-item">
                              <el-input v-model="requirementEditData.description.overview" type="textarea" :rows="4" placeholder="请详细描述需求的主要内容" />
                            </el-form-item>
                          </td>
                        </tr>
                        <tr>
                          <th><span class="required">*</span> 期望解决的问题</th>
                          <td>
                            <el-form-item class="table-form-item">
                              <el-input v-model="requirementEditData.description.target_problems" type="textarea" :rows="4" placeholder="请描述期望通过该需求解决的具体问题" />
                            </el-form-item>
                          </td>
                        </tr>
                        <tr>
                          <th>项目预算</th>
                          <td>
                            <div style="display:flex;align-items:center;gap:10px;">
                              <el-input-number v-model.number="requirementEditData.description.budget" :precision="2" :controls="false" placeholder="请输入金额" style="width:200px;" />
                              <el-select v-model="requirementEditData.budget_unit" style="width:120px;">
                                <el-option label="元" value="元" />
                                <el-option label="万元" value="万元" />
                                <el-option label="百万元" value="百万元" />
                                <el-option label="亿元" value="亿元" />
                              </el-select>
                            </div>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </el-form>
              </div>
              <div class="modal-footer">
                <button class="btn btn-default" @click="requirementEditVisible = false">取消</button>
                <button class="btn btn-primary" @click="saveRequirementEdit">保存</button>
              </div>
            </div>
          </div>
        </div>

        <div class="page" :class="{ active: currentPage === 'experts' }" id="page-experts">
          <div class="card">
            <div class="card-header">
              <div class="card-title">专家管理</div>
              <button class="btn btn-primary" @click="showAddExpertModal">
                + 录入新专家
              </button>
            </div>
            <div class="card-body">
              <div class="search-box">
                <input type="text" class="search-input" placeholder="搜索姓名、单位、职称..." v-model="expertKeyword" @keyup.enter="fetchExperts">
                <button class="btn btn-primary" @click="fetchExperts">搜索</button>
                <button class="btn btn-default" @click="expertKeyword = ''; fetchExperts()">重置</button>
              </div>

              <div v-if="expertLoading" style="text-align:center;padding:40px;color:#999;">加载中...</div>

              <div v-else-if="filteredExperts.length === 0" style="text-align:center;padding:40px;color:#999;">
                暂无专家数据
              </div>

              <div v-else class="experts-grid">
                <div class="expert-card" v-for="exp in filteredExperts" :key="exp.id">
                  <div class="expert-avatar">{{ (exp.name || '?')[0] }}</div>
                  <div class="expert-info">
                    <div class="expert-name">{{ exp.name }}</div>
                    <div class="expert-title">{{ exp.position_title || '未填写' }}</div>
                    <div class="expert-org">{{ exp.work_unit || '未知单位' }}</div>
                    <div class="expert-fields">
                      <template v-if="exp.professional_fields && exp.professional_fields.length > 0">
                        <span
                          class="field-tag"
                          v-for="field in getVisibleFields(exp.professional_fields, 2).visible"
                          :key="field"
                          :style="{ background: getFieldStyle(field).bg, color: getFieldStyle(field).color, borderColor: getFieldStyle(field).border }"
                          :title="'专业领域：' + field"
                        >
                          {{ field }}
                        </span>
                        <span
                          v-if="getVisibleFields(exp.professional_fields, 2).remaining > 0"
                          class="field-tag field-tag-more"
                          :title="'全部领域：' + exp.professional_fields.join('、')"
                        >
                          +{{ getVisibleFields(exp.professional_fields, 2).remaining }}
                        </span>
                      </template>
                      <span v-else class="field-tag field-tag-empty">未设置领域</span>
                    </div>
                  </div>
                  <div class="expert-actions">
                    <button class="btn btn-sm btn-default" @click="viewExpertDetail(exp.id)">查看</button>
                    <button class="btn btn-sm btn-default" @click="editExpert(exp.id)">编辑</button>
                    <button class="btn btn-sm btn-error" @click="deleteExpert(exp.id)">删除</button>
                  </div>
                </div>
              </div>

              <div v-if="expertPagination.total_pages > 1" class="pagination-container" style="margin-top:20px;display:flex;justify-content:center;gap:8px;align-items:center;">
                <button class="btn btn-sm btn-default" :disabled="expertPagination.page <= 1" @click="handleExpertPageChange(expertPagination.page - 1)">上一页</button>
                <span style="font-size:14px;color:#666;">第 {{ expertPagination.page }} / {{ expertPagination.total_pages }} 页</span>
                <button class="btn btn-sm btn-default" :disabled="expertPagination.page >= expertPagination.total_pages" @click="handleExpertPageChange(expertPagination.page + 1)">下一页</button>
                <span style="font-size:13px;color:#999;margin-left:8px;">共 {{ expertPagination.total }} 条</span>
              </div>
            </div>
          </div>
        </div>

        <div class="page" :class="{ active: currentPage === 'partners' }" id="page-partners">
          <div class="card">
            <div class="card-header">
              <div class="card-title">合作伙伴管理</div>
              <button class="btn btn-primary" @click="showAddPartnerModal">+ 新增合作方</button>
            </div>
            <div class="card-body">
              <div class="search-box">
                <input type="text" class="search-input" placeholder="搜索平台名称、地址、领域、联系人..." v-model="partnerKeyword" @keyup.enter="searchPartner">
                <select class="search-select" v-model="partnerTypeFilter">
                  <option value="">全部类型</option>
                  <option value="概念验证平台">概念验证平台</option>
                  <option value="中试基地">中试基地</option>
                  <option value="产业化试验基地">产业化试验基地</option>
                </select>
                <button class="btn btn-primary" @click="searchPartner">搜索</button>
                <button class="btn btn-default" @click="resetPartnerSearch">重置</button>
              </div>

              <div v-if="partnerLoading" style="text-align:center;padding:40px;color:#999;">加载中...</div>

              <div v-else class="table-container">
                <table class="data-table">
                  <thead>
                    <tr>
                      <th>平台名称</th>
                      <th>类型</th>
                      <th>所在地址</th>
                      <th>行业领域</th>
                      <th>联系人及电话</th>
                      <th>创建时间</th>
                      <th>操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="item in partners" :key="item.id">
                      <td style="font-weight: 500;">{{ item.name }}</td>
                      <td>{{ item.type }}</td>
                      <td style="font-size:13px;color:#888;">{{ item.address }}</td>
                      <td>{{ item.industry }}</td>
                      <td>{{ item.contact || '-' }}</td>
                      <td style="font-size:13px;color:#888;">{{ item.created_at ? formatTime(item.created_at) : '-' }}</td>
                      <td>
                        <button class="btn btn-sm btn-default" @click="viewPartnerDetail(item.id)" style="margin-right:4px;">查看</button>
                        <button class="btn btn-sm btn-default" @click="editPartner(item.id)" style="margin-right:4px;">编辑</button>
                        <button class="btn btn-sm btn-error" @click="deletePartner(item.id)">删除</button>
                      </td>
                    </tr>
                    <tr v-if="partners.length === 0">
                      <td colspan="7" style="text-align:center;padding:40px;color:#999;">暂无合作伙伴数据</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <div v-if="partnerTotalPages > 1" class="pagination-bar">
                <div class="pagination-info">共 {{ partnerTotal }} 条，第 {{ partnerPage }} / {{ partnerTotalPages }} 页</div>
                <div class="pagination-controls">
                  <span class="pagination-size-select">
                    每页
                    <select v-model.number="partnerPageSize" @change="handlePartnerPageSizeChange(partnerPageSize)">
                      <option :value="5">5</option>
                      <option :value="10">10</option>
                      <option :value="15">15</option>
                      <option :value="20">20</option>
                    </select>
                    条
                  </span>
                  <button class="btn btn-sm btn-default" :disabled="partnerPage <= 1" @click="handlePartnerPageChange(partnerPage - 1)">上一页</button>
                  <button
                    v-for="p in partnerTotalPages"
                    :key="p"
                    :class="['btn btn-sm', p === partnerPage ? 'btn-primary' : 'btn-default']"
                    @click="handlePartnerPageChange(p)"
                    v-show="p === 1 || p === partnerTotalPages || Math.abs(p - partnerPage) <= 1"
                  >{{ p }}</button>
                  <button class="btn btn-sm btn-default" :disabled="partnerPage >= partnerTotalPages" @click="handlePartnerPageChange(partnerPage + 1)">下一页</button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="page" :class="{ active: currentPage === 'partner_applies' }" id="page-partner-applies">
          <div class="card">
            <div class="card-header">
              <div class="card-title">合作申请管理</div>
            </div>
            <div class="card-body">
              <div class="search-box">
                <input type="text" class="search-input" placeholder="搜索联系人、单位..." v-model="partnerApplyKeyword" @keyup.enter="searchPartnerApply">
                <button class="btn btn-primary" @click="searchPartnerApply">搜索</button>
                <button class="btn btn-default" @click="partnerApplyKeyword = ''; searchPartnerApply()">重置</button>
              </div>

              <div v-if="partnerApplyLoading" style="text-align:center;padding:40px;color:#999;">加载中...</div>

              <div v-else class="table-container">
                <table class="data-table">
                  <thead>
                    <tr>
                      <th style="width:50px">序号</th>
                      <th>联系人</th>
                      <th>联系电话</th>
                      <th>联系邮箱</th>
                      <th>联系单位</th>
                      <th>联系地址</th>
                      <th>意向说明</th>
                      <th>关联平台</th>
                      <th style="width:150px">提交时间</th>
                      <th style="width:120px">操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-if="partnerApplies.length === 0">
                      <td colspan="10" style="text-align:center;padding:40px;color:#999;">暂无合作申请数据</td>
                    </tr>
                    <tr v-for="(item, idx) in partnerApplies" :key="idx">
                      <td>{{ idx + 1 }}</td>
                      <td style="font-weight:500;">{{ item.contact_name || '-' }}</td>
                      <td>{{ item.contact_phone || '-' }}</td>
                      <td>{{ item.contact_email || '-' }}</td>
                      <td>{{ item.company || '-' }}</td>
                      <td>
                        <span class="text-ellipsis" style="display:inline-block;max-width:120px;" :title="item.address">{{ item.address || '-' }}</span>
                      </td>
                      <td>
                        <span class="text-ellipsis" style="display:inline-block;max-width:160px;" :title="item.intention">{{ item.intention || '-' }}</span>
                      </td>
                      <td>{{ item.partner_info?.name || '-' }}</td>
                      <td style="font-size:13px;color:#888;">{{ formatTime(item.created_at) }}</td>
                      <td>
                        <button class="btn btn-sm btn-default" @click="viewPartnerApplyDetail(item)" style="margin-right:4px;">查看</button>
                        <button class="btn btn-sm btn-error" @click="deletePartnerApply(item)">删除</button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- 合作申请详情弹窗 -->
          <div class="modal" :class="{ active: partnerApplyDetailVisible }" id="partnerApplyDetailModal">
            <div class="modal-content" style="width: 700px;">
              <div class="modal-header">
                <div class="modal-title">合作申请详情</div>
                <button class="modal-close" @click="closePartnerApplyDetail">&times;</button>
              </div>
              <div class="modal-body">
                <div class="detail-section">
                  <h4 class="detail-section-title">申请人信息</h4>
                  <div class="detail-grid">
                    <div class="detail-item">
                      <span class="detail-label">联系人姓名</span>
                      <span class="detail-value">{{ partnerApplyDetail?.contact_name || '-' }}</span>
                    </div>
                    <div class="detail-item">
                      <span class="detail-label">联系电话</span>
                      <span class="detail-value">{{ partnerApplyDetail?.contact_phone || '-' }}</span>
                    </div>
                    <div class="detail-item">
                      <span class="detail-label">联系邮箱</span>
                      <span class="detail-value">{{ partnerApplyDetail?.contact_email || '-' }}</span>
                    </div>
                    <div class="detail-item">
                      <span class="detail-label">联系单位</span>
                      <span class="detail-value">{{ partnerApplyDetail?.company || '-' }}</span>
                    </div>
                    <div class="detail-item">
                      <span class="detail-label">联系地址</span>
                      <span class="detail-value">{{ partnerApplyDetail?.address || '-' }}</span>
                    </div>
                    <div class="detail-item full-width">
                      <span class="detail-label">意向说明</span>
                      <span class="detail-value">{{ partnerApplyDetail?.intention || '-' }}</span>
                    </div>
                    <div class="detail-item">
                      <span class="detail-label">提交时间</span>
                      <span class="detail-value">{{ partnerApplyDetail?.created_at || '-' }}</span>
                    </div>
                  </div>
                </div>
                <div class="detail-section" v-if="partnerApplyDetail?.partner_info">
                  <h4 class="detail-section-title">关联平台信息</h4>
                  <div class="detail-grid">
                    <div class="detail-item">
                      <span class="detail-label">平台名称</span>
                      <span class="detail-value">{{ partnerApplyDetail.partner_info.name || '-' }}</span>
                    </div>
                    <div class="detail-item">
                      <span class="detail-label">平台类型</span>
                      <span class="detail-value">{{ partnerApplyDetail.partner_info.type || '-' }}</span>
                    </div>
                    <div class="detail-item">
                      <span class="detail-label">行业领域</span>
                      <span class="detail-value">{{ partnerApplyDetail.partner_info.industry || '-' }}</span>
                    </div>
                    <div class="detail-item">
                      <span class="detail-label">所在地址</span>
                      <span class="detail-value">{{ partnerApplyDetail.partner_info.address || '-' }}</span>
                    </div>
                    <div class="detail-item full-width">
                      <span class="detail-label">平台介绍</span>
                      <span class="detail-value">{{ partnerApplyDetail.partner_info.intro || '-' }}</span>
                    </div>
                    <div class="detail-item full-width">
                      <span class="detail-label">可提供服务</span>
                      <span class="detail-value">{{ partnerApplyDetail.partner_info.services || '-' }}</span>
                    </div>
                  </div>
                </div>
              </div>
              <div class="modal-footer">
                <button class="btn btn-default" @click="closePartnerApplyDetail">关闭</button>
              </div>
            </div>
          </div>
        </div>

        <div class="page" :class="{ active: currentPage === 'financial_services' }" id="page-financial-services">
          <div class="card">
            <div class="card-header">
              <div class="card-title">金融服务管理</div>
              <button class="btn btn-primary" @click="showAddFinancialServiceModal">+ 新增服务机构</button>
            </div>
            <div class="card-body">
              <div class="search-box">
                <input type="text" class="search-input" placeholder="搜索机构名称、简介、服务..." v-model="financialServiceKeyword" @keyup.enter="searchFinancialService">
                <button class="btn btn-primary" @click="searchFinancialService">搜索</button>
                <button class="btn btn-default" @click="resetFinancialServiceSearch">重置</button>
              </div>

              <div v-if="financialServiceLoading" style="text-align:center;padding:40px;color:#999;">加载中...</div>

              <div v-else class="table-container">
                <table class="data-table">
                  <thead>
                    <tr>
                      <th>机构名称</th>
                      <th>简介</th>
                      <th>联系人及电话</th>
                      <th>创建时间</th>
                      <th>操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="item in financialServices" :key="item.id">
                      <td style="font-weight: 500;">{{ item.name }}</td>
                      <td style="font-size:13px;color:#888;max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{{ item.intro || '-' }}</td>
                      <td>{{ item.contact || '-' }}</td>
                      <td style="font-size:13px;color:#888;">{{ item.created_at ? formatTime(item.created_at) : '-' }}</td>
                      <td>
                        <button class="btn btn-sm btn-default" @click="viewFinancialServiceDetail(item.id)" style="margin-right:4px;">查看</button>
                        <button class="btn btn-sm btn-default" @click="editFinancialService(item.id)" style="margin-right:4px;">编辑</button>
                        <button class="btn btn-sm btn-error" @click="deleteFinancialService(item.id)">删除</button>
                      </td>
                    </tr>
                    <tr v-if="financialServices.length === 0">
                      <td colspan="5" style="text-align:center;padding:40px;color:#999;">暂无金融服务机构数据</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <div v-if="financialServiceTotalPages > 1" class="pagination-bar">
                <div class="pagination-info">共 {{ financialServiceTotal }} 条，第 {{ financialServicePage }} / {{ financialServiceTotalPages }} 页</div>
                <div class="pagination-controls">
                  <span class="pagination-size-select">
                    每页
                    <select v-model.number="financialServicePageSize" @change="handleFinancialServicePageSizeChange(financialServicePageSize)">
                      <option :value="5">5</option>
                      <option :value="10">10</option>
                      <option :value="15">15</option>
                      <option :value="20">20</option>
                    </select>
                    条
                  </span>
                  <button class="btn btn-sm btn-default" :disabled="financialServicePage <= 1" @click="handleFinancialServicePageChange(financialServicePage - 1)">上一页</button>
                  <button
                    v-for="p in financialServiceTotalPages"
                    :key="p"
                    :class="['btn btn-sm', p === financialServicePage ? 'btn-primary' : 'btn-default']"
                    @click="handleFinancialServicePageChange(p)"
                    v-show="p === 1 || p === financialServiceTotalPages || Math.abs(p - financialServicePage) <= 1"
                  >{{ p }}</button>
                  <button class="btn btn-sm btn-default" :disabled="financialServicePage >= financialServiceTotalPages" @click="handleFinancialServicePageChange(financialServicePage + 1)">下一页</button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="page" :class="{ active: currentPage === 'content' }" id="page-content">
          <div class="empty-state">
            <div class="empty-icon">🌐</div>
            <h3 style="margin-bottom: 10px; color: #333;">网站可视化设置</h3>
            <p style="margin-bottom: 16px;">管理网站 Logo、名称、导航栏菜单、主页轮播图及"关于我们"页面的核心内容</p>
            <button class="btn btn-primary" @click="$router.push('/admin-editor')">进入网站设置</button>
          </div>
        </div>

        <!-- FAQ 管理 -->
        <div class="page" :class="{ active: currentPage === 'faqs' }" id="page-faqs">
          <div class="faq-layout">
            <!-- 左侧管理列表 -->
            <div class="faq-manage">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
                <h2 style="font-size:18px;font-weight:600;">快捷引导管理</h2>
                <button class="btn btn-primary" @click="openFaqDialog()">+ 新增</button>
              </div>
              <!-- 站点名称编辑 -->
              <div class="site-name-row">
                <label>欢迎语站点名称：</label>
                <input v-model="siteName" type="text" class="form-input site-name-input"
                  placeholder="科创中心" @blur="saveSiteName" />
                <span class="site-name-hint">修改后自动保存，刷新预览查看效果</span>
              </div>
              <div class="faq-list">
                <div v-for="faq in faqList" :key="faq.id" class="faq-card" :class="{ 'faq-draft': faq.status === 'draft' }">
                  <div class="faq-card-num">{{ faq.question }}</div>
                  <div class="faq-card-body">
                    <div class="faq-card-title">{{ faq.display_text || faq.question }}</div>
                    <div class="faq-card-preview">{{ (faq.answer || '').replace(/<[^>]+>/g,'').substring(0, 50) }}</div>
                  </div>
                  <div class="faq-card-status">
                    <span class="faq-status-dot" :class="faq.status === 'published' ? 'dot-on' : 'dot-off'"
                      @click="toggleFaqStatus(faq)" :title="faq.status === 'published' ? '点击下架' : '点击发布'"></span>
                  </div>
                  <div class="faq-card-actions">
                    <button class="btn btn-sm" @click="openFaqDialog(faq)" title="编辑">✏️</button>
                    <button class="btn btn-sm btn-danger" @click="deleteFaq(faq)" title="删除">🗑️</button>
                  </div>
                </div>
                <div v-if="faqList.length === 0" class="faq-empty">
                  <div style="font-size:40px;margin-bottom:12px;">💬</div>
                  <div>暂无快捷引导问题</div>
                  <div style="font-size:13px;color:#999;margin-top:6px;">点击上方"新增"创建第一条</div>
                </div>
              </div>
            </div>

            <!-- 右侧客服聊天预览 -->
            <div class="faq-preview-box">
              <div class="preview-header">📱 客服聊天预览</div>
              <div class="preview-chat" ref="previewChatRef">
                <!-- 机器人欢迎语 -->
                <div class="msg-row bot">
                  <div class="msg-avatar">🤖</div>
                  <div class="msg-bubble bot" v-html="greetingPreview"></div>
                </div>
                <!-- 测试对话记录 -->
                <div v-for="(msg, i) in testMessages" :key="i" class="msg-row" :class="msg.role">
                  <div v-if="msg.role === 'bot'" class="msg-avatar">🤖</div>
                  <div class="msg-bubble" :class="msg.role" v-html="msg.content"></div>
                  <div v-if="msg.role === 'user'" class="msg-avatar user">我</div>
                </div>
              </div>
              <div class="preview-input-row">
                <input v-model="testInput" type="text" class="preview-input"
                  placeholder="输入数字（如 1）测试自动回复..." @keydown.enter="sendTestMessage" :disabled="testLoading" />
                <button class="preview-send-btn" @click="sendTestMessage" :disabled="testLoading || !testInput.trim()">
                  {{ testLoading ? '...' : '发送' }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 访客日志管理 -->
        <div class="page" :class="{ active: currentPage === 'visit_logs' }" id="page-visit-logs">
          <div class="card">
            <div class="card-header">
              <div class="card-title">访客日志管理</div>
              <div>
                <button class="btn btn-default" @click="refreshVisitLogs" style="margin-right:8px;">刷新</button>
                <button class="btn btn-error" @click="clearAllVisitLogs">清空全部</button>
              </div>
            </div>
            <div class="card-body">
              <div class="search-box">
                <input type="text" class="search-input" placeholder="搜索 IP 地址..." v-model="visitLogSearch.ip">
                <input type="text" class="search-input" placeholder="搜索访问路径..." v-model="visitLogSearch.path" style="margin-left:8px;">
                <input type="date" class="search-input" v-model="visitLogSearch.date_from" style="margin-left:8px;width:150px;">
                <span style="margin:0 4px;color:#999;">至</span>
                <input type="date" class="search-input" v-model="visitLogSearch.date_to" style="width:150px;">
                <button class="btn btn-primary" @click="searchVisitLogs" style="margin-left:8px;">搜索</button>
                <button class="btn btn-default" @click="resetVisitLogSearch">重置</button>
              </div>

              <div class="table-container">
                <div v-if="visitLogLoading" style="text-align:center;padding:40px;color:#999;">加载中...</div>
                <table v-else class="data-table">
                  <thead>
                    <tr>
                      <th style="width:60px;">#</th>
                      <th style="width:130px;">IP 地址</th>
                      <th style="width:160px;">访问路径</th>
                      <th>页面标题</th>
                      <th>User-Agent</th>
                      <th style="width:160px;">访问时间</th>
                      <th style="width:80px;">操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(log, idx) in visitLogs" :key="log._id">
                      <td>{{ (visitLogPage - 1) * visitLogPageSize + idx + 1 }}</td>
                      <td><code style="background:#f5f5f5;padding:2px 6px;border-radius:3px;font-size:12px;">{{ log.ip }}</code></td>
                      <td style="font-size:13px;">{{ log.path }}</td>
                      <td style="font-size:13px;max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" :title="log.title">{{ log.title || '-' }}</td>
                      <td style="font-size:12px;color:#888;max-width:250px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" :title="log.user_agent">{{ log.user_agent || '-' }}</td>
                      <td style="font-size:13px;color:#666;">{{ log.created_at }}</td>
                      <td>
                        <button class="btn btn-sm btn-error" @click="deleteVisitLog(log._id)">删除</button>
                      </td>
                    </tr>
                    <tr v-if="visitLogs.length === 0">
                      <td colspan="7" style="text-align:center;padding:40px;color:#999;">暂无访客日志数据</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <!-- 分页 -->
              <div v-if="visitLogTotal > 0" class="pagination-bar">
                <div class="pagination-info">共 {{ visitLogTotal }} 条，第 {{ visitLogPage }} / {{ visitLogTotalPages }} 页</div>
                <div class="pagination-controls">
                  <span class="pagination-size-select">
                    每页
                    <select v-model.number="visitLogPageSize" @change="fetchVisitLogs">
                      <option :value="10">10</option>
                      <option :value="20">20</option>
                      <option :value="50">50</option>
                    </select>
                    条
                  </span>
                  <button class="btn btn-sm btn-default" :disabled="visitLogPage <= 1" @click="visitLogPageChange(visitLogPage - 1)">上一页</button>
                  <button
                    v-for="p in visitLogTotalPages"
                    :key="p"
                    :class="['btn btn-sm', p === visitLogPage ? 'btn-primary' : 'btn-default']"
                    @click="visitLogPageChange(p)"
                    v-show="p === 1 || p === visitLogTotalPages || Math.abs(p - visitLogPage) <= 1"
                  >{{ p }}</button>
                  <button class="btn btn-sm btn-default" :disabled="visitLogPage >= visitLogTotalPages" @click="visitLogPageChange(visitLogPage + 1)">下一页</button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- FAQ 编辑弹窗（简单三字段） -->
        <div class="modal" :class="{ active: faqDialogVisible }" @click.self="faqDialogVisible = false">
          <div class="modal-content" style="max-width:500px;">
            <div class="modal-header">
              <div class="modal-title">{{ editingFaq.id ? '编辑快捷引导' : '新增快捷引导' }}</div>
              <button class="modal-close" @click="faqDialogVisible = false">&times;</button>
            </div>
            <div class="modal-body">
              <div class="form-group">
                <label>回复数字 <span style="color:red">*</span></label>
                <input v-model="editingFaq.question" type="text" class="form-input" placeholder="如：1、2、7" />
                <div style="font-size:12px;color:#888;margin-top:4px;">用户在客服聊天框输入此数字，即触发自动回复。</div>
              </div>
              <div class="form-group">
                <label>显示标题 <span style="color:red">*</span></label>
                <input v-model="editingFaq.display_text" type="text" class="form-input" placeholder="如：成果发布" />
                <div style="font-size:12px;color:#888;margin-top:4px;">
                  客服界面显示的示例问题文字，效果: <strong v-if="editingFaq.question && editingFaq.display_text">{{ editingFaq.question }}. {{ editingFaq.display_text }}</strong>
                  <span v-else>【数字】. 【标题】</span>
                </div>
              </div>
              <div class="form-group">
                <label>回复内容 <span style="color:red">*</span></label>
                <textarea v-model="editingFaq.answer" class="form-textarea" rows="5" placeholder="输入自动回复的内容，支持 HTML 如 &lt;br&gt; 换行"></textarea>
              </div>
            </div>
            <div class="modal-footer">
              <button class="btn" @click="faqDialogVisible = false">取消</button>
              <button class="btn btn-primary" @click="saveFaq" :disabled="!editingFaq.question.trim() || !(editingFaq.display_text||'').trim() || !editingFaq.answer.trim()">保存</button>
            </div>
          </div>
        </div>

      <!-- 模态框 -->
      <div class="modal" :class="{ active: addUserModalVisible }" id="addUserModal">
        <div class="modal-content">
          <div class="modal-header">
            <div class="modal-title">新增系统用户</div>
            <button class="modal-close" @click="closeAddUserModal">×</button>
          </div>
          <div class="modal-body">
            <form id="addUserForm">
              <div class="form-row">
                <div class="form-group flex-1">
                  <label class="form-label">用户名</label>
                  <input type="text" class="form-input" placeholder="登录账号，留空自动生成" v-model="userForm.username">
                </div>
                <div class="form-group flex-1">
                  <label class="form-label">真实姓名</label>
                  <input type="text" class="form-input" placeholder="请输入真实姓名" v-model="userForm.real_name">
                </div>
              </div>
              <div class="form-row">
                <div class="form-group flex-1">
                  <label class="form-label">手机号 <span style="color:red;">*</span></label>
                  <input type="tel" class="form-input" placeholder="11位手机号码" v-model="userForm.phone">
                </div>
                <div class="form-group flex-1">
                  <label class="form-label">身份证号</label>
                  <input type="text" class="form-input" placeholder="18位身份证号" v-model="userForm.id_card">
                </div>
              </div>
              <div class="form-row">
                <div class="form-group flex-1">
                  <label class="form-label">初始密码 <span style="color:red;">*</span></label>
                  <input type="password" class="form-input" placeholder="不少于6位字符" v-model="userForm.password">
                </div>
                <div class="form-group flex-1">
                  <label class="form-label">分配角色</label>
                  <select class="form-input" v-model="userForm.role">
                    <option value="common">普通用户</option>
                    <option value="agent">客服</option>
                    <option value="admin">管理员</option>
                  </select>
                </div>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button class="btn btn-default" @click="closeAddUserModal">取消</button>
            <button class="btn btn-primary" @click="submitAddUser">确认创建</button>
          </div>
        </div>
      </div>

      <div class="modal" :class="{ active: editUserModalVisible }" id="editUserModal">
        <div class="modal-content">
          <div class="modal-header">
            <div class="modal-title">编辑用户</div>
            <button class="modal-close" @click="closeEditUserModal">×</button>
          </div>
          <div class="modal-body">
            <form id="editUserForm">
              <div class="form-row">
                <div class="form-group flex-1">
                  <label class="form-label">用户名</label>
                  <input type="text" class="form-input" placeholder="登录账号" v-model="userForm.username">
                </div>
                <div class="form-group flex-1">
                  <label class="form-label">真实姓名</label>
                  <input type="text" class="form-input" placeholder="请输入真实姓名" v-model="userForm.real_name">
                </div>
              </div>
              <div class="form-row">
                <div class="form-group flex-1">
                  <label class="form-label">手机号 <span style="color:red;">*</span></label>
                  <input type="tel" class="form-input" placeholder="11位手机号码" v-model="userForm.phone">
                </div>
                <div class="form-group flex-1">
                  <label class="form-label">身份证号</label>
                  <input type="text" class="form-input" placeholder="18位身份证号" v-model="userForm.id_card">
                </div>
              </div>
              <div class="form-row">
                <div class="form-group flex-1">
                  <label class="form-label">角色</label>
                  <select class="form-input" v-model="userForm.role">
                    <option value="common">普通用户</option>
                    <option value="agent">客服</option>
                    <option value="admin">管理员</option>
                  </select>
                </div>
                <div class="form-group flex-1">
                  <label class="form-label">新密码 <span style="color:#999;font-weight:normal;">（留空不修改）</span></label>
                  <input type="password" class="form-input" placeholder="输入新密码" v-model="userForm.password">
                </div>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button class="btn btn-default" @click="closeEditUserModal">取消</button>
            <button class="btn btn-primary" @click="submitEditUser">保存修改</button>
          </div>
        </div>
      </div>

      <!-- 专家新增/编辑弹窗 -->
      <div class="modal" :class="{ active: expertModalVisible }" id="expertModal">
        <div class="modal-content modal-lg">
          <div class="modal-header">
            <div class="modal-title">{{ expertModalTitle }}</div>
            <button class="modal-close" @click="closeExpertModal">×</button>
          </div>
          <div class="modal-body">
            <div class="expert-form-section">
              <div class="expert-form-section-title">一、基本信息</div>
              <div class="form-row">
                <div class="form-group flex-1">
                  <label class="form-label">姓名 <span style="color:red;">*</span></label>
                  <input type="text" class="form-input" v-model="expertForm.name" placeholder="请输入姓名">
                </div>
                <div class="form-group flex-1">
                  <label class="form-label">性别</label>
                  <select class="form-input" v-model="expertForm.gender">
                    <option value="">请选择</option>
                    <option value="男">男</option>
                    <option value="女">女</option>
                  </select>
                </div>
              </div>
              <div class="form-row">
                <div class="form-group flex-1">
                  <label class="form-label">身份证号 <span style="color:red;">*</span></label>
                  <input type="text" class="form-input" v-model="expertForm.id_card" placeholder="请输入身份证号">
                </div>
                <div class="form-group flex-1">
                  <label class="form-label">最高学历</label>
                  <select class="form-input" v-model="expertForm.highest_education">
                    <option value="">请选择</option>
                    <option value="博士">博士</option>
                    <option value="硕士">硕士</option>
                    <option value="本科">本科</option>
                    <option value="大专">大专</option>
                    <option value="其他">其他</option>
                  </select>
                </div>
              </div>
              <div class="form-group">
                <label class="form-label">毕业院校及专业</label>
                <input type="text" class="form-input" v-model="expertForm.school_major" placeholder="如：清华大学计算机科学与技术">
              </div>
              <div class="form-group">
                <label class="form-label">现工作单位</label>
                <input type="text" class="form-input" v-model="expertForm.work_unit" placeholder="请输入工作单位">
              </div>
              <div class="form-row">
                <div class="form-group flex-1">
                  <label class="form-label">职务/职称</label>
                  <input type="text" class="form-input" v-model="expertForm.position_title" placeholder="如：教授/研究员">
                </div>
                <div class="form-group flex-1">
                  <label class="form-label">联系方式（电话/邮箱）</label>
                  <input type="text" class="form-input" v-model="expertForm.contact" placeholder="电话或邮箱">
                </div>
              </div>
              <div class="form-group">
                <label class="form-label">通讯地址</label>
                <input type="text" class="form-input" v-model="expertForm.address" placeholder="请输入通讯地址">
              </div>
              <div class="form-group">
                <label class="form-label">社会荣誉</label>
                <textarea class="form-input" v-model="expertForm.honors" placeholder="请填写社会荣誉" rows="2"></textarea>
              </div>
            </div>

            <div class="expert-form-section">
              <div class="expert-form-section-title">二、专业领域 <span style="color:#999;font-weight:normal;font-size:13px;">（最多选择2个主领域）</span></div>
              <div class="checkbox-group">
                <label class="checkbox-item" :class="{ checked: expertForm.professional_fields.includes(opt.value) }" v-for="opt in fieldOptions" :key="opt.value" @click.prevent="toggleField(opt.value)">
                  <span class="checkbox-custom">
                    <span v-if="expertForm.professional_fields.includes(opt.value)" class="checkbox-checkmark">✓</span>
                  </span>
                  <span>{{ opt.label }}</span>
                </label>
              </div>
              <div class="form-group" style="margin-top:8px;">
                <label class="form-label">其他（请说明）</label>
                <input type="text" class="form-input" v-model="expertForm.professional_fields_other" placeholder="如不在以上选项中，请说明">
              </div>
            </div>

            <div class="expert-form-section">
              <div class="expert-form-section-title">三、个人简介</div>
              <div class="form-group">
                <label class="form-label">个人简介</label>
                <textarea class="form-input" v-model="expertForm.personal_profile" placeholder="请填写专家个人简介（将显示在专家中心详情页）" rows="4"></textarea>
              </div>
            </div>

            <div class="expert-form-section">
              <div class="expert-form-section-title">四、评估资质</div>
              <div class="expert-form-subsection">
                <div class="expert-form-subsection-title">1. 专业知识水平</div>
                <div class="form-group">
                  <label class="form-label">专业技术职称</label>
                  <select class="form-input" v-model="expertForm.technical_title">
                    <option value="">请选择</option>
                    <option value="正高级">正高级</option>
                    <option value="副高级">副高级</option>
                    <option value="中级">中级</option>
                  </select>
                </div>
              </div>
              <div class="expert-form-subsection">
                <div class="expert-form-subsection-title">2. 从业经验</div>
                <div class="form-group">
                  <label class="form-label">相关领域工作年限</label>
                  <input type="number" class="form-input" v-model.number="expertForm.work_years" min="0" placeholder="年">
                </div>
              </div>
            </div>

            <div class="expert-form-section">
              <div class="expert-form-section-title">五、代表性成果</div>
              <div class="form-group">
                <label class="form-label">专利情况（数量及代表性专利号）</label>
                <textarea class="form-input" v-model="expertForm.patents" placeholder="请填写专利数量和代表性专利号" rows="2"></textarea>
              </div>
              <div class="form-group">
                <label class="form-label">科研项目（主持/参与国家级、省部级项目）</label>
                <textarea class="form-input" v-model="expertForm.research_projects" placeholder="请填写科研项目情况" rows="2"></textarea>
              </div>
              <div class="form-group">
                <label class="form-label">获奖情况</label>
                <textarea class="form-input" v-model="expertForm.awards" placeholder="请填写获奖情况" rows="2"></textarea>
              </div>
            </div>

            <div class="expert-form-section">
              <div class="expert-form-section-title">六、附件清单 <span style="color:#999;font-weight:normal;font-size:13px;">（仅可上传照片）</span></div>
              <div class="attachment-list">
                <div class="attachment-item" v-for="type in attachmentTypes" :key="type">
                  <div class="attachment-label">{{ type }}</div>
                  <div class="attachment-controls">
                    <input type="file" :id="'fu_' + type" style="display:none" @change="onAttachmentFileChange(type, $event)" accept="image/*" multiple>
                    <button class="btn btn-sm btn-default" @click="triggerFileInput(type)">选择照片</button>
                    <span v-if="pendingUploads[type] && pendingUploads[type].length > 0" class="pending-count">已选 {{ pendingUploads[type].length }} 张</span>
                    <span v-if="(!pendingUploads[type] || pendingUploads[type].length === 0) && (!uploadedFiles[type] || uploadedFiles[type].length === 0)" class="no-file">未选择文件</span>
                  </div>
                  <!-- 待上传的照片预览 -->
                  <div v-if="pendingUploads[type] && pendingUploads[type].length > 0" class="uploaded-files">
                    <div class="uploaded-file-item" v-for="(f, idx) in pendingUploads[type]" :key="'pending_' + idx">
                      <img :src="getObjectUrl(f)" :alt="f.name" class="uploaded-file-thumb">
                      <span class="uploaded-file-name" :title="f.name">{{ f.name }}</span>
                      <button class="btn btn-sm btn-error" @click="removePendingFile(type, idx)">移除</button>
                    </div>
                  </div>
                  <!-- 已上传的照片 -->
                  <div v-if="uploadedFiles[type] && uploadedFiles[type].length > 0" class="uploaded-files">
                    <div class="uploaded-file-item" v-for="f in uploadedFiles[type]" :key="f.file_name">
                      <template v-if="isImageFile(f.file_name)">
                        <img :src="fullUrl(f.file_url)" :alt="f.file_name" class="uploaded-file-thumb">
                      </template>
                      <span class="uploaded-file-name" :title="f.file_name">{{ f.file_name }}</span>
                      <button class="btn btn-sm btn-error" @click="deleteUploadedFile(type, f.file_name, editingExpertId)" v-if="isEditing">删除</button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-default" @click="closeExpertModal">取消</button>
            <button class="btn btn-primary" @click="submitExpertForm">{{ isEditing ? '保存修改' : '确认录入' }}</button>
          </div>
        </div>
      </div>

      <!-- 专家详情弹窗 -->
      <div class="modal" :class="{ active: expertDetailVisible }" id="expertDetailModal">
        <div class="modal-content modal-lg">
          <div class="modal-header">
            <div class="modal-title">专家详情</div>
            <button class="modal-close" @click="expertDetailVisible = false">×</button>
          </div>
          <div class="modal-body">
            <div v-if="!expertDetailData" style="text-align:center;padding:20px;color:#999;">加载中...</div>
            <div v-else>
              <div class="detail-section">
                <div class="detail-section-title">一、基本信息</div>
                <div class="detail-grid">
                  <div class="detail-item"><span class="detail-label">姓名</span><span class="detail-value">{{ expertDetailData.name }}</span></div>
                  <div class="detail-item"><span class="detail-label">性别</span><span class="detail-value">{{ expertDetailData.gender || '未填写' }}</span></div>
                  <div class="detail-item"><span class="detail-label">身份证号</span><span class="detail-value">{{ expertDetailData.id_card || '未填写' }}</span></div>
                  <div class="detail-item"><span class="detail-label">最高学历</span><span class="detail-value">{{ expertDetailData.highest_education || '未填写' }}</span></div>
                  <div class="detail-item"><span class="detail-label">毕业院校及专业</span><span class="detail-value">{{ expertDetailData.school_major || '未填写' }}</span></div>
                  <div class="detail-item"><span class="detail-label">现工作单位</span><span class="detail-value">{{ expertDetailData.work_unit || '未填写' }}</span></div>
                  <div class="detail-item"><span class="detail-label">职务/职称</span><span class="detail-value">{{ expertDetailData.position_title || '未填写' }}</span></div>
                  <div class="detail-item"><span class="detail-label">联系方式</span><span class="detail-value">{{ expertDetailData.contact || '未填写' }}</span></div>
                  <div class="detail-item"><span class="detail-label">通讯地址</span><span class="detail-value">{{ expertDetailData.address || '未填写' }}</span></div>
                  <div class="detail-item"><span class="detail-label">社会荣誉</span><span class="detail-value">{{ expertDetailData.honors || '未填写' }}</span></div>
                </div>
              </div>
              <div class="detail-section">
                <div class="detail-section-title">二、专业领域</div>
                <div class="detail-grid">
                  <div class="detail-item">
                    <span class="detail-label">主领域</span>
                    <span class="detail-value">
                      <span v-if="expertDetailData.professional_fields && expertDetailData.professional_fields.length > 0" class="detail-fields">
                        <span
                          class="field-tag"
                          v-for="f in expertDetailData.professional_fields"
                          :key="f"
                          :style="{ background: getFieldStyle(f).bg, color: getFieldStyle(f).color, borderColor: getFieldStyle(f).border }"
                        >{{ f }}</span>
                      </span>
                      <span v-else style="color:#999;">未设置</span>
                    </span>
                  </div>
                  <div class="detail-item"><span class="detail-label">其他</span><span class="detail-value">{{ expertDetailData.professional_fields_other || '无' }}</span></div>
                </div>
              </div>
              <div class="detail-section">
                <div class="detail-section-title">三、评估资质</div>
                <div class="detail-grid">
                  <div class="detail-item"><span class="detail-label">专业技术职称</span><span class="detail-value">{{ expertDetailData.technical_title || '未填写' }}</span></div>
                  <div class="detail-item"><span class="detail-label">工作年限</span><span class="detail-value">{{ expertDetailData.work_years != null ? expertDetailData.work_years + '年' : '未填写' }}</span></div>
                </div>
              </div>
              <div class="detail-section">
                <div class="detail-section-title">四、代表性成果</div>
                <div class="detail-grid">
                  <div class="detail-item"><span class="detail-label">专利情况</span><span class="detail-value">{{ expertDetailData.patents || '未填写' }}</span></div>
                  <div class="detail-item"><span class="detail-label">科研项目</span><span class="detail-value">{{ expertDetailData.research_projects || '未填写' }}</span></div>
                  <div class="detail-item"><span class="detail-label">获奖情况</span><span class="detail-value">{{ expertDetailData.awards || '未填写' }}</span></div>
                </div>
              </div>
              <div class="detail-section">
                <div class="detail-section-title">五、附件清单</div>
                <div v-if="expertDetailData.attachments && Object.keys(expertDetailData.attachments).length > 0">
                  <div class="detail-attachment-type" v-for="(files, type) in expertDetailData.attachments" :key="type">
                    <div class="detail-attachment-type-label">{{ type }}</div>
                    <div v-if="files && files.length > 0">
                      <div class="detail-attachment-file" v-for="f in files" :key="f.file_name">
                        <template v-if="isImageFile(f.file_name)">
                          <div class="attachment-image-preview" @click="openImagePreview(f.file_url)">
                            <img :src="fullUrl(f.file_url)" :alt="f.file_name" class="attachment-thumb">
                            <span class="attachment-image-name">{{ f.file_name }}</span>
                          </div>
                        </template>
                        <template v-else>
                          <a :href="fullUrl(f.file_url)" target="_blank" class="attachment-link">{{ f.file_name }}</a>
                        </template>
                      </div>
                    </div>
                    <div v-else class="no-file">无</div>
                  </div>
                </div>
                <div v-else style="color:#999;padding:8px 12px;">无</div>
              </div>
              <div style="margin-top:12px;color:#999;font-size:13px;text-align:center;">
                创建时间：{{ expertDetailData.created_at || '未知' }}&nbsp;&nbsp;|&nbsp;&nbsp;最后更新：{{ expertDetailData.updated_at || '未知' }}
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-default" @click="expertDetailVisible = false">关闭</button>
          </div>
        </div>
      </div>

      <!-- 合作伙伴新增/编辑弹窗 -->
      <div class="modal" :class="{ active: partnerModalVisible }" id="partnerModal">
        <div class="modal-content modal-lg">
          <div class="modal-header">
            <div class="modal-title">{{ partnerModalTitle }}</div>
            <button class="modal-close" @click="closePartnerModal">×</button>
          </div>
          <div class="modal-body">
            <div class="form-row">
              <div class="form-group flex-1">
                <label class="form-label">平台名称 <span style="color:red;">*</span></label>
                <input type="text" class="form-input" v-model="partnerForm.name" placeholder="请输入平台名称">
              </div>
              <div class="form-group flex-1">
                <label class="form-label">类型</label>
                <select class="form-input" v-model="partnerForm.type">
                  <option value="">请选择</option>
                  <option value="概念验证平台">概念验证平台</option>
                  <option value="中试基地">中试基地</option>
                  <option value="产业化试验基地">产业化试验基地</option>
                </select>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group flex-1">
                <label class="form-label">所在地址 <span style="color:red;">*</span></label>
                <div class="region-selectors" style="display:flex;gap:8px;">
                  <select class="form-input" v-model="partnerForm.province" style="flex:1;">
                    <option value="">选择省份</option>
                    <option v-for="p in provinces" :key="p" :value="p">{{ p }}</option>
                  </select>
                  <select class="form-input" v-model="partnerForm.city" :disabled="!partnerForm.province" style="flex:1;">
                    <option value="">{{ isMunicipality ? '选择区' : '选择城市' }}</option>
                    <option v-for="c in availableCities" :key="c" :value="c">{{ c }}</option>
                  </select>
                </div>
              </div>
              <div class="form-group flex-1">
                <label class="form-label">行业领域</label>
                <input type="text" class="form-input" v-model="partnerForm.industry" placeholder="请输入行业领域">
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">平台介绍</label>
              <textarea class="form-input" v-model="partnerForm.intro" placeholder="请输入平台介绍" rows="3"></textarea>
            </div>
            <div class="form-group">
              <label class="form-label">可提供的服务</label>
              <textarea class="form-input" v-model="partnerForm.services" placeholder="请输入可提供的服务" rows="3"></textarea>
            </div>
            <div class="form-group">
              <label class="form-label">联系人及电话 <span style="color:#999;font-weight:normal;">（不对外展示）</span></label>
              <input type="text" class="form-input" v-model="partnerForm.contact" placeholder="请输入联系人姓名及电话">
            </div>
            <div class="form-group">
              <label class="form-label">附件照片 <span style="color:#999;font-weight:normal;">（仅支持图片格式）</span></label>
              <div class="attachment-controls" style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
                <input type="file" id="partnerImageInput" style="display:none" @change="onPartnerImageSelect" accept="image/*" multiple>
                <button class="btn btn-sm btn-default" @click="triggerPartnerImageInput">选择照片</button>
                <span v-if="pendingPartnerImages.length > 0" class="pending-count">已选 {{ pendingPartnerImages.length }} 张</span>
              </div>
              <!-- 待上传的照片预览 -->
              <div v-if="pendingPartnerImages.length > 0" class="uploaded-files">
                <div class="uploaded-file-item" v-for="(f, idx) in pendingPartnerImages" :key="'pending_' + idx">
                  <img :src="getPartnerImageUrl(f)" :alt="f.name" class="uploaded-file-thumb">
                  <span class="uploaded-file-name" :title="f.name">{{ f.name }}</span>
                  <button class="btn btn-sm btn-error" @click="removePendingPartnerImage(idx)">移除</button>
                </div>
              </div>
              <!-- 已上传的照片 -->
              <div v-if="partnerForm.images && partnerForm.images.length > 0" class="uploaded-files">
                <div class="uploaded-file-item" v-for="f in partnerForm.images" :key="f.file_name">
                  <template v-if="isImageFile(f.file_name)">
                    <img :src="fullUrl(f.file_url)" :alt="f.file_name" class="uploaded-file-thumb">
                  </template>
                  <span class="uploaded-file-name" :title="f.file_name">{{ f.file_name }}</span>
                  <button class="btn btn-sm btn-error" @click="deletePartnerImage(f.file_name)" v-if="isEditingPartner">删除</button>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-default" @click="closePartnerModal">取消</button>
            <button class="btn btn-primary" @click="submitPartnerForm">{{ isEditingPartner ? '保存修改' : '确认创建' }}</button>
          </div>
        </div>
      </div>

      <!-- 合作伙伴详情弹窗 -->
      <div class="modal" :class="{ active: partnerDetailVisible }" id="partnerDetailModal">
        <div class="modal-content modal-lg">
          <div class="modal-header">
            <div class="modal-title">合作方详情</div>
            <button class="modal-close" @click="partnerDetailVisible = false">×</button>
          </div>
          <div class="modal-body">
            <div v-if="!partnerDetailData" style="text-align:center;padding:20px;color:#999;">加载中...</div>
            <div v-else>
              <div class="detail-section">
                <div class="detail-section-title">基本信息</div>
                <div class="detail-grid">
                  <div class="detail-item"><span class="detail-label">平台名称</span><span class="detail-value">{{ partnerDetailData.name }}</span></div>
                  <div class="detail-item"><span class="detail-label">类型</span><span class="detail-value">{{ partnerDetailData.type || '未设置' }}</span></div>
                  <div class="detail-item"><span class="detail-label">所在地址</span><span class="detail-value">{{ partnerDetailData.address || '未填写' }}</span></div>
                  <div class="detail-item"><span class="detail-label">行业领域</span><span class="detail-value">{{ partnerDetailData.industry || '未填写' }}</span></div>
                  <div class="detail-item"><span class="detail-label">联系人及电话</span><span class="detail-value">{{ partnerDetailData.contact || '未填写' }}</span></div>
                </div>
              </div>
              <div class="detail-section">
                <div class="detail-section-title">详细介绍</div>
                <div class="detail-grid">
                  <div class="detail-item" style="grid-column: span 2;"><span class="detail-label">平台介绍</span><span class="detail-value">{{ partnerDetailData.intro || '未填写' }}</span></div>
                  <div class="detail-item" style="grid-column: span 2;"><span class="detail-label">可提供的服务</span><span class="detail-value">{{ partnerDetailData.services || '未填写' }}</span></div>
                </div>
              </div>
              <div class="detail-section">
                <div class="detail-section-title">附件照片</div>
                <div v-if="partnerDetailData.images && partnerDetailData.images.length > 0">
                  <div style="display:flex;flex-wrap:wrap;gap:12px;padding:8px 0;">
                    <div v-for="f in partnerDetailData.images" :key="f.file_name" style="text-align:center;">
                      <template v-if="isImageFile(f.file_name)">
                        <img :src="fullUrl(f.file_url)" :alt="f.file_name" style="width:120px;height:100px;object-fit:cover;border-radius:4px;border:1px solid #eee;cursor:pointer;" @click="openImagePreview(f.file_url)">
                      </template>
                    </div>
                  </div>
                </div>
                <div v-else style="color:#999;padding:8px 12px;">无</div>
              </div>
              <div style="margin-top:12px;color:#999;font-size:13px;text-align:center;">
                创建时间：{{ partnerDetailData.created_at || '未知' }}&nbsp;&nbsp;|&nbsp;&nbsp;最后更新：{{ partnerDetailData.updated_at || '未知' }}
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-default" @click="partnerDetailVisible = false">关闭</button>
          </div>
        </div>
      </div>

      <!-- 金融服务机构新增/编辑弹窗 -->
      <div class="modal" :class="{ active: financialServiceModalVisible }" id="financialServiceModal">
        <div class="modal-content modal-lg">
          <div class="modal-header">
            <div class="modal-title">{{ financialServiceModalTitle }}</div>
            <button class="modal-close" @click="closeFinancialServiceModal">×</button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label class="form-label">机构名称 <span style="color:red;">*</span></label>
              <input type="text" class="form-input" v-model="financialServiceForm.name" placeholder="请输入机构名称">
            </div>
            <div class="form-group">
              <label class="form-label">简介</label>
              <textarea class="form-input" v-model="financialServiceForm.intro" placeholder="请输入机构简介" rows="3"></textarea>
            </div>
            <div class="form-group">
              <label class="form-label">可提供的服务</label>
              <textarea class="form-input" v-model="financialServiceForm.services" placeholder="请输入可提供的服务" rows="3"></textarea>
            </div>
            <div class="form-group">
              <label class="form-label">联系人及电话 <span style="color:#999;font-weight:normal;">（不对外展示）</span></label>
              <input type="text" class="form-input" v-model="financialServiceForm.contact" placeholder="请输入联系人姓名及电话">
            </div>
            <div class="form-group">
              <label class="form-label">机构照片 <span style="color:#999;font-weight:normal;">（仅支持图片格式）</span></label>
              <div class="attachment-controls" style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
                <input type="file" id="financialServiceImageInput" style="display:none" @change="onFinancialServiceImageSelect" accept="image/*" multiple>
                <button class="btn btn-sm btn-default" @click="triggerFinancialServiceImageInput">选择照片</button>
                <span v-if="pendingFinancialServiceImages.length > 0" class="pending-count">已选 {{ pendingFinancialServiceImages.length }} 张</span>
              </div>
              <div v-if="pendingFinancialServiceImages.length > 0" class="uploaded-files">
                <div class="uploaded-file-item" v-for="(f, idx) in pendingFinancialServiceImages" :key="'pending_' + idx">
                  <img :src="getFinancialServiceImageUrl(f)" :alt="f.name" class="uploaded-file-thumb">
                  <span class="uploaded-file-name" :title="f.name">{{ f.name }}</span>
                  <button class="btn btn-sm btn-error" @click="removePendingFinancialServiceImage(idx)">移除</button>
                </div>
              </div>
              <div v-if="financialServiceForm.images && financialServiceForm.images.length > 0" class="uploaded-files">
                <div class="uploaded-file-item" v-for="f in financialServiceForm.images" :key="f.file_name">
                  <template v-if="isImageFile(f.file_name)">
                    <img :src="fullUrl(f.file_url)" :alt="f.file_name" class="uploaded-file-thumb">
                  </template>
                  <span class="uploaded-file-name" :title="f.file_name">{{ f.file_name }}</span>
                  <button class="btn btn-sm btn-error" @click="deleteFinancialServiceImage(f.file_name)" v-if="isEditingFinancialService">删除</button>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-default" @click="closeFinancialServiceModal">取消</button>
            <button class="btn btn-primary" @click="submitFinancialServiceForm">{{ isEditingFinancialService ? '保存修改' : '确认创建' }}</button>
          </div>
        </div>
      </div>

      <!-- 金融服务机构详情弹窗 -->
      <div class="modal" :class="{ active: financialServiceDetailVisible }" id="financialServiceDetailModal">
        <div class="modal-content modal-lg">
          <div class="modal-header">
            <div class="modal-title">金融服务机构详情</div>
            <button class="modal-close" @click="financialServiceDetailVisible = false">×</button>
          </div>
          <div class="modal-body">
            <div v-if="!financialServiceDetailData" style="text-align:center;padding:20px;color:#999;">加载中...</div>
            <div v-else>
              <div class="detail-section">
                <div class="detail-section-title">基本信息</div>
                <div class="detail-grid">
                  <div class="detail-item"><span class="detail-label">机构名称</span><span class="detail-value">{{ financialServiceDetailData.name }}</span></div>
                  <div class="detail-item"><span class="detail-label">联系人及电话</span><span class="detail-value">{{ financialServiceDetailData.contact || '未填写' }}</span></div>
                </div>
              </div>
              <div class="detail-section">
                <div class="detail-section-title">详细介绍</div>
                <div class="detail-grid">
                  <div class="detail-item" style="grid-column: span 2;"><span class="detail-label">机构简介</span><span class="detail-value">{{ financialServiceDetailData.intro || '未填写' }}</span></div>
                  <div class="detail-item" style="grid-column: span 2;"><span class="detail-label">可提供的服务</span><span class="detail-value">{{ financialServiceDetailData.services || '未填写' }}</span></div>
                </div>
              </div>
              <div class="detail-section">
                <div class="detail-section-title">机构照片</div>
                <div v-if="financialServiceDetailData.images && financialServiceDetailData.images.length > 0">
                  <div style="display:flex;flex-wrap:wrap;gap:12px;padding:8px 0;">
                    <div v-for="f in financialServiceDetailData.images" :key="f.file_name" style="text-align:center;">
                      <template v-if="isImageFile(f.file_name)">
                        <img :src="fullUrl(f.file_url)" :alt="f.file_name" style="width:120px;height:100px;object-fit:cover;border-radius:4px;border:1px solid #eee;cursor:pointer;" @click="openImagePreview(f.file_url)">
                      </template>
                    </div>
                  </div>
                </div>
                <div v-else style="color:#999;padding:8px 12px;">无</div>
              </div>
              <div style="margin-top:12px;color:#999;font-size:13px;text-align:center;">
                创建时间：{{ financialServiceDetailData.created_at || '未知' }}&nbsp;&nbsp;|&nbsp;&nbsp;最后更新：{{ financialServiceDetailData.updated_at || '未知' }}
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-default" @click="financialServiceDetailVisible = false">关闭</button>
          </div>
        </div>
      </div>

      <!-- 图片预览遮罩 -->
      <div class="image-preview-overlay" :class="{ active: previewImageUrl }" @click="closeImagePreview">
        <span class="image-preview-close">&times;</span>
        <img v-if="previewImageUrl" :src="fullUrl(previewImageUrl)" class="image-preview-full" @click.stop>
      </div>
      </div>
    </div>
  </div>
</template>

<script>
export default { name: 'AdminView' }
</script>
<script setup>
import { ref, reactive, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import request from '../utils/request'
import * as echarts from 'echarts'

// Flask后端地址（与 request.js 中的 baseURL 保持一致）
const FLASK_BASE_URL = window.location.origin

// 将相对URL转为绝对URL，用于<img>标签直接加载
function fullUrl(url) {
  if (url && url.startsWith('/')) {
    return FLASK_BASE_URL + url
  }
  return url
}

// 响应式状态
const currentPage = ref('dashboard')
const pageTitle = ref('仪表板')
const userSearch = ref('')
const userRoleFilter = ref('')
const userStatusFilter = ref('')
const partnerKeyword = ref('')
const partnerApplies = ref([])
const partnerApplyKeyword = ref('')
const partnerApplyLoading = ref(false)
const partnerApplyDetail = ref(null)
const partnerApplyDetailVisible = ref(false)

// 内容管理（成果/需求）状态
const auditSubTab = ref('achievement')
const achievements = ref([])
const achievementLoading = ref(false)
const achievementPage = ref(1)
const achievementPageSize = ref(10)
const achievementTotal = ref(0)
const achievementTotalPages = ref(0)
const achievementKeyword = ref('')
const achievementStatusFilter = ref('')
const achievementDetailVisible = ref(false)
const achievementDetailData = ref(null)
const achievementEditVisible = ref(false)
const achievementEditData = ref({
  id: '',
  achievement_name: '',
  owner: '',
  province: '',
  city: '',
  tech_field: '',
  tech_field_other: '',
  tech_maturity: '',
  transfer_methods: [],
  transfer_other: '',
  innovation_level: '',
  cooperationPref: '',
  transfer_fee: 0,
  licenseType: '',
  investment_valuation: 0,
  equityPercent: null,
  cooperationOther: '',
  expectDate: null,
  description: {
    summary: '',
    innovation_level: '',
    advantages: '',
    core_indicators: '',
    intellectual_property: ''
  }
})
const achievementEditFormRef = ref(null)

const requirements = ref([])
const requirementLoading = ref(false)
const requirementPage = ref(1)
const requirementPageSize = ref(10)
const requirementTotal = ref(0)
const requirementTotalPages = ref(0)
const requirementKeyword = ref('')
const requirementStatusFilter = ref('')
const requirementDetailVisible = ref(false)
const requirementDetailData = ref(null)
const activeMatchDropdown = ref(null)
const dropdownStyle = ref({})

function toggleMatchDropdown(event, id) {
  if (activeMatchDropdown.value === id) {
    activeMatchDropdown.value = null
    return
  }
  const rect = event.currentTarget.getBoundingClientRect()
  dropdownStyle.value = {
    position: 'fixed',
    top: (rect.bottom + 4) + 'px',
    left: rect.left + 'px',
    minWidth: rect.width + 'px',
    zIndex: 9999
  }
  activeMatchDropdown.value = id
}
const requirementEditVisible = ref(false)
const requirementEditFormRef = ref(null)
const requirementEditData = ref({
  id: '',
  demand_name: '',
  company_name: '',
  province: '',
  city: '',
  emergingIndustry: '',
  traditionalIndustry: '',
  tech_field: '',
  tech_field_other: '',
  demand_type: '',
  demand_type_other: '',
  budget_unit: '万元',
  description: {
    overview: '',
    target_problems: '',
    budget: 0
  }
})

// FAQ 管理状态
const faqList = ref([])
const faqDialogVisible = ref(false)
const editingFaq = ref({ question: '', display_text: '', answer: '', status: 'published' })
const greetingPreview = ref('加载中...')
const siteName = ref('科创中心')

// 访客日志管理状态
const visitLogs = ref([])
const visitLogLoading = ref(false)
const visitLogTotal = ref(0)
const visitLogPage = ref(1)
const visitLogPageSize = ref(20)
const visitLogSearch = reactive({ ip: '', path: '', date_from: '', date_to: '' })
const visitLogTotalPages = computed(() => Math.max(1, Math.ceil(visitLogTotal.value / visitLogPageSize.value)))
// 测试聊天
const testInput = ref('')
const testMessages = ref([])
const testLoading = ref(false)
const previewChatRef = ref(null)

// 聊天记录管理状态
const crKeyword = ref('')
const crStatus = ref('')
const crDateFrom = ref('')
const crDateTo = ref('')
const crSessions = ref([])        // 当前页显示的数据
const crAllGrouped = ref([])     // 全部按用户分组后的数据
const crPage = ref(1)
const crPageSize = 15            // 每页显示条数
const crTotal = ref(0)
const crTotalPages = ref(0)
const crDetailVisible = ref(false)
const crDetailUser = ref('')
const crDetailMessages = ref([])
const crDetailLoading = ref(false)

// 合作伙伴管理状态
const partners = ref([])
const partnerLoading = ref(false)
const partnerPage = ref(1)
const partnerPageSize = ref(10)
const partnerTotal = ref(0)
const partnerTotalPages = ref(0)
const partnerTypeFilter = ref('')
const partnerModalVisible = ref(false)
const partnerModalTitle = ref('')
const isEditingPartner = ref(false)
const editingPartnerId = ref('')
const partnerForm = reactive({
  name: '',
  type: '',
  province: '',
  city: '',
  address: '',
  industry: '',
  intro: '',
  services: '',
  contact: '',
  images: []
})
const pendingPartnerImages = ref([])
const partnerDetailVisible = ref(false)
const partnerDetailData = ref(null)

// ========== 金融服务管理状态 ==========
const financialServices = ref([])
const financialServiceLoading = ref(false)
const financialServicePage = ref(1)
const financialServicePageSize = ref(10)
const financialServiceTotal = ref(0)
const financialServiceTotalPages = ref(0)
const financialServiceKeyword = ref('')
const financialServiceModalVisible = ref(false)
const financialServiceModalTitle = ref('')
const isEditingFinancialService = ref(false)
const editingFinancialServiceId = ref('')
const financialServiceForm = reactive({
  name: '',
  intro: '',
  services: '',
  contact: '',
  images: []
})
const pendingFinancialServiceImages = ref([])
const financialServiceDetailVisible = ref(false)
const financialServiceDetailData = ref(null)

// 省份城市数据
const achievementTechFieldOptions = [
  '新一代信息技术', '生物医药与健康', '航空航天', '新材料',
  '高技术服务', '新能源与节能', '资源与环境', '先进制造与自动化',
  '现代农业', '海洋技术', '其他'
]

const demandTypeOptions = ['技术需求', '金融需求', '场景需求', '其他']

const emergingIndustries = [
  '节能环保产业', '新一代信息技术产业', '高端装备制造产业', '新能源产业',
  '新材料产业', '生物产业', '新能源汽车产业', '数字创意产业'
]

const traditionalIndustries = [
  '农、林、牧、渔业', '采矿业', '制造业', '水利环境', '教育，医疗卫生',
  '文化、体育和娱乐', '电力、热力和燃气', '建筑业', '交通运输和仓储',
  '住宿和餐饮业', '信息传输、软件和信息技术服务业', '金融业',
  '房地产业', '新能源', '科学研究和技术服务'
]

const provinces = [
  '北京市', '天津市', '上海市', '重庆市',
  '河北省', '山西省', '辽宁省', '吉林省', '黑龙江省',
  '江苏省', '浙江省', '安徽省', '福建省', '江西省', '山东省',
  '河南省', '湖北省', '湖南省', '广东省', '海南省',
  '四川省', '贵州省', '云南省', '陕西省', '甘肃省',
  '青海省', '台湾省',
  '内蒙古自治区', '广西壮族自治区', '西藏自治区', '宁夏回族自治区', '新疆维吾尔自治区',
  '香港特别行政区', '澳门特别行政区'
]

const citiesMap = {
  '北京市': ['东城区', '西城区', '朝阳区', '丰台区', '石景山区', '海淀区', '门头沟区', '房山区', '通州区', '顺义区', '昌平区', '大兴区', '怀柔区', '平谷区', '密云区', '延庆区'],
  '天津市': ['和平区', '河东区', '河西区', '南开区', '河北区', '红桥区', '东丽区', '西青区', '津南区', '北辰区', '武清区', '宝坻区', '滨海新区', '宁河区', '静海区', '蓟州区'],
  '上海市': ['黄浦区', '徐汇区', '长宁区', '静安区', '普陀区', '虹口区', '杨浦区', '闵行区', '宝山区', '嘉定区', '浦东新区', '金山区', '松江区', '青浦区', '奉贤区', '崇明区'],
  '重庆市': ['万州区', '涪陵区', '渝中区', '大渡口区', '江北区', '沙坪坝区', '九龙坡区', '南岸区', '北碚区', '綦江区', '大足区', '渝北区', '巴南区', '黔江区', '长寿区', '江津区', '合川区', '永川区', '南川区', '璧山区', '铜梁区', '潼南区', '荣昌区', '开州区', '梁平区', '武隆区', '城口县', '丰都县', '垫江县', '忠县', '云阳县', '奉节县', '巫山县', '巫溪县', '石柱土家族自治县', '秀山土家族苗族自治县', '酉阳土家族苗族自治县', '彭水苗族土家族自治县'],
  '河北省': ['石家庄市', '唐山市', '秦皇岛市', '邯郸市', '邢台市', '保定市', '张家口市', '承德市', '沧州市', '廊坊市', '衡水市'],
  '山西省': ['太原市', '大同市', '阳泉市', '长治市', '晋城市', '朔州市', '晋中市', '运城市', '忻州市', '临汾市', '吕梁市'],
  '辽宁省': ['沈阳市', '大连市', '鞍山市', '抚顺市', '本溪市', '丹东市', '锦州市', '营口市', '阜新市', '辽阳市', '盘锦市', '铁岭市', '朝阳市', '葫芦岛市'],
  '吉林省': ['长春市', '吉林市', '四平市', '辽源市', '通化市', '白山市', '松原市', '白城市', '延边朝鲜族自治州'],
  '黑龙江省': ['哈尔滨市', '齐齐哈尔市', '鸡西市', '鹤岗市', '双鸭山市', '大庆市', '伊春市', '佳木斯市', '七台河市', '牡丹江市', '黑河市', '绥化市', '大兴安岭地区'],
  '江苏省': ['南京市', '无锡市', '徐州市', '常州市', '苏州市', '南通市', '连云港市', '淮安市', '盐城市', '扬州市', '镇江市', '泰州市', '宿迁市'],
  '浙江省': ['杭州市', '宁波市', '温州市', '嘉兴市', '湖州市', '绍兴市', '金华市', '衢州市', '舟山市', '台州市', '丽水市'],
  '安徽省': ['合肥市', '芜湖市', '蚌埠市', '淮南市', '马鞍山市', '淮北市', '铜陵市', '安庆市', '黄山市', '滁州市', '阜阳市', '宿州市', '六安市', '亳州市', '池州市', '宣城市'],
  '福建省': ['福州市', '厦门市', '莆田市', '三明市', '泉州市', '漳州市', '南平市', '龙岩市', '宁德市'],
  '江西省': ['南昌市', '景德镇市', '萍乡市', '九江市', '新余市', '鹰潭市', '赣州市', '吉安市', '宜春市', '抚州市', '上饶市'],
  '山东省': ['济南市', '青岛市', '淄博市', '枣庄市', '东营市', '烟台市', '潍坊市', '济宁市', '泰安市', '威海市', '日照市', '临沂市', '德州市', '聊城市', '滨州市', '菏泽市'],
  '河南省': ['郑州市', '开封市', '洛阳市', '平顶山市', '安阳市', '鹤壁市', '新乡市', '焦作市', '濮阳市', '许昌市', '漯河市', '三门峡市', '南阳市', '商丘市', '信阳市', '周口市', '驻马店市'],
  '湖北省': ['武汉市', '黄石市', '十堰市', '宜昌市', '襄阳市', '鄂州市', '荆门市', '孝感市', '荆州市', '黄冈市', '咸宁市', '随州市', '恩施土家族苗族自治州'],
  '湖南省': ['长沙市', '株洲市', '湘潭市', '衡阳市', '邵阳市', '岳阳市', '常德市', '张家界市', '益阳市', '郴州市', '永州市', '怀化市', '娄底市', '湘西土家族苗族自治州'],
  '广东省': ['广州市', '韶关市', '深圳市', '珠海市', '汕头市', '佛山市', '江门市', '湛江市', '茂名市', '肇庆市', '惠州市', '梅州市', '汕尾市', '河源市', '阳江市', '清远市', '东莞市', '中山市', '潮州市', '揭阳市', '云浮市'],
  '海南省': ['海口市', '三亚市', '三沙市', '儋州市'],
  '四川省': ['成都市', '自贡市', '攀枝花市', '泸州市', '德阳市', '绵阳市', '广元市', '遂宁市', '内江市', '乐山市', '南充市', '眉山市', '宜宾市', '广安市', '达州市', '雅安市', '巴中市', '资阳市', '阿坝藏族羌族自治州', '甘孜藏族自治州', '凉山彝族自治州'],
  '贵州省': ['贵阳市', '六盘水市', '遵义市', '安顺市', '毕节市', '铜仁市', '黔西南布依族苗族自治州', '黔东南苗族侗族自治州', '黔南布依族苗族自治州'],
  '云南省': ['昆明市', '曲靖市', '玉溪市', '保山市', '昭通市', '丽江市', '普洱市', '临沧市', '楚雄彝族自治州', '红河哈尼族彝族自治州', '文山壮族苗族自治州', '西双版纳傣族自治州', '大理白族自治州', '德宏傣族景颇族自治州', '怒江傈僳族自治州', '迪庆藏族自治州'],
  '陕西省': ['西安市', '铜川市', '宝鸡市', '咸阳市', '渭南市', '延安市', '汉中市', '榆林市', '安康市', '商洛市'],
  '甘肃省': ['兰州市', '嘉峪关市', '金昌市', '白银市', '天水市', '武威市', '张掖市', '平凉市', '酒泉市', '庆阳市', '定西市', '陇南市', '临夏回族自治州', '甘南藏族自治州'],
  '青海省': ['西宁市', '海东市', '海北藏族自治州', '黄南藏族自治州', '海南藏族自治州', '果洛藏族自治州', '玉树藏族自治州', '海西蒙古族藏族自治州'],
  '台湾省': ['台北市', '高雄市', '基隆市', '台中市', '台南市', '新竹市', '嘉义市', '新北市', '宜兰县', '桃园市', '苗栗县', '彰化县', '南投县', '云林县', '屏东县', '台东县', '花莲县', '澎湖县', '金门县', '连江县'],
  '内蒙古自治区': ['呼和浩特市', '包头市', '乌海市', '赤峰市', '通辽市', '鄂尔多斯市', '呼伦贝尔市', '巴彦淖尔市', '乌兰察布市', '兴安盟', '锡林郭勒盟', '阿拉善盟'],
  '广西壮族自治区': ['南宁市', '柳州市', '桂林市', '梧州市', '北海市', '防城港市', '钦州市', '贵港市', '玉林市', '百色市', '贺州市', '河池市', '来宾市', '崇左市'],
  '西藏自治区': ['拉萨市', '日喀则市', '昌都市', '林芝市', '山南市', '那曲市', '阿里地区'],
  '宁夏回族自治区': ['银川市', '石嘴山市', '吴忠市', '固原市', '中卫市'],
  '新疆维吾尔自治区': ['乌鲁木齐市', '克拉玛依市', '吐鲁番市', '哈密市', '昌吉回族自治州', '博尔塔拉蒙古自治州', '巴音郭楞蒙古自治州', '阿克苏地区', '克孜勒苏柯尔克孜自治州', '喀什地区', '和田地区', '伊犁哈萨克自治州', '塔城地区', '阿勒泰地区'],
  '香港特别行政区': ['香港岛', '九龙', '新界'],
  '澳门特别行政区': ['澳门半岛', '氹仔岛', '路环岛']
}

const availableCities = computed(() => {
  if (partnerForm.province && citiesMap[partnerForm.province]) {
    return citiesMap[partnerForm.province]
  }
  return []
})

const isMunicipality = computed(() => {
  return partnerForm.province && ['北京市', '天津市', '上海市', '重庆市'].includes(partnerForm.province)
})

watch(() => partnerForm.province, () => {
  partnerForm.city = ''
})

// 用户管理 - 真实API数据
const users = ref([])
const userLoading = ref(false)
const userPage = ref(1)
const userPageSize = ref(10)
const userForm = reactive({
  username: '',
  real_name: '',
  id_card: '',
  phone: '',
  password: '',
  role: 'common'
})

// 模态框状态
const addUserModalVisible = ref(false)
const editUserModalVisible = ref(false)
const editingUserId = ref(null)

// 专家管理状态
const experts = ref([])
const expertLoading = ref(false)
const expertKeyword = ref('')
const expertPagination = reactive({
  page: 1,
  page_size: 10,
  total: 0,
  total_pages: 0
})
const expertModalVisible = ref(false)
const expertModalTitle = ref('')
const expertDetailVisible = ref(false)
const expertDetailData = ref(null)
const previewImageUrl = ref('')
const isEditing = ref(false)
const editingExpertId = ref('')
const expertForm = reactive({
  name: '',
  gender: '',
  id_card: '',
  highest_education: '',
  school_major: '',
  work_unit: '',
  position_title: '',
  contact: '',
  address: '',
  honors: '',
  professional_fields: [],
  professional_fields_other: '',
  personal_profile: '',
  technical_title: '',
  professional_certification: '',
  foreign_language: '',
  work_years: 0,
  successful_cases: 0,
  patents: '',
  publications: '',
  research_projects: '',
  awards: '',
  attachments: {}
})

// 附件上传状态（暂存待上传的文件）
const pendingUploads = reactive({})   // { type: [File, File, ...] }
const uploadedFiles = reactive({})    // { type: [{file_name, file_url}, ...] }

// 附件类型列表
const attachmentTypes = [
  '近期生活照或职业照一张', '学历学位证书',
  '职称证明', '代表性成果证明', '其他证明材料'
]

// 专业领域选项
const fieldOptions = [
  { label: '新一代信息技术', value: '新一代信息技术' },
  { label: '人工智能', value: '人工智能' },
  { label: '大数据', value: '大数据' },
  { label: '区块链', value: '区块链' },
  { label: '云计算', value: '云计算' },
  { label: '高端装备制造', value: '高端装备制造' },
  { label: '机器人', value: '机器人' },
  { label: '航空航天', value: '航空航天' },
  { label: '海洋工程', value: '海洋工程' },
  { label: '新材料', value: '新材料' },
  { label: '新能源', value: '新能源' },
  { label: '节能环保', value: '节能环保' },
  { label: '生物医药', value: '生物医药' },
  { label: '医疗器械', value: '医疗器械' },
  { label: '现代农业', value: '现代农业' },
]

// 专业领域颜色映射（按类别分组配色）
const fieldColorMap = {
  '新一代信息技术': { bg: '#e6f7ff', color: '#1890ff', border: '#91d5ff' },
  '人工智能':       { bg: '#f0f5ff', color: '#2f54eb', border: '#adc6ff' },
  '大数据':         { bg: '#e6fffb', color: '#13c2c2', border: '#87e8de' },
  '区块链':         { bg: '#fff7e6', color: '#d46b08', border: '#ffd591' },
  '云计算':         { bg: '#e6f7ff', color: '#1890ff', border: '#91d5ff' },
  '高端装备制造':   { bg: '#f9f0ff', color: '#722ed1', border: '#d3adf7' },
  '机器人':         { bg: '#f9f0ff', color: '#531dab', border: '#d3adf7' },
  '航空航天':       { bg: '#f0f5ff', color: '#1d39c4', border: '#adc6ff' },
  '海洋工程':       { bg: '#e6fffb', color: '#08979c', border: '#87e8de' },
  '新材料':         { bg: '#f6ffed', color: '#52c41a', border: '#b7eb8f' },
  '新能源':         { bg: '#f6ffed', color: '#389e0d', border: '#b7eb8f' },
  '节能环保':       { bg: '#f6ffed', color: '#237804', border: '#b7eb8f' },
  '生物医药':       { bg: '#fff0f6', color: '#eb2f96', border: '#ffadd2' },
  '医疗器械':       { bg: '#fff0f6', color: '#c41d7f', border: '#ffadd2' },
  '现代农业':       { bg: '#fffbe6', color: '#d48806', border: '#ffe58f' },
}

// 获取领域的样式信息
function getFieldStyle(field) {
  return fieldColorMap[field] || { bg: '#f5f5f5', color: '#666', border: '#d9d9d9' }
}

// 限制显示的领域数量
function getVisibleFields(fields, max = 2) {
  if (!fields || fields.length === 0) return { visible: [], remaining: 0 }
  return {
    visible: fields.slice(0, max),
    remaining: fields.length - max
  }
}

// 计算属性：过滤后的专家列表
const filteredExperts = computed(() => {
  if (!expertKeyword.value.trim()) return experts.value
  const kw = expertKeyword.value.toLowerCase()
  return experts.value.filter(e =>
    (e.name || '').toLowerCase().includes(kw) ||
    (e.work_unit || '').toLowerCase().includes(kw) ||
    (e.position_title || '').toLowerCase().includes(kw)
  )
})

// 获取专家列表
async function fetchExperts() {
  expertLoading.value = true
  try {
    const response = await request.get('/api/publish/experts', {
      params: {
        page: expertPagination.page,
        page_size: expertPagination.page_size,
        keyword: expertKeyword.value
      }
    })
    if (response.code === 200) {
      experts.value = response.data || []
      expertPagination.total = response.total || 0
      expertPagination.total_pages = response.total_pages || 0
    }
  } catch (error) {
    console.error('获取专家列表失败:', error)
  } finally {
    expertLoading.value = false
  }
}

// 专家分页切换
function handleExpertPageChange(newPage) {
  expertPagination.page = newPage
  fetchExperts()
}

// 打开新增专家弹窗
function showAddExpertModal() {
  isEditing.value = false
  editingExpertId.value = ''
  expertModalTitle.value = '录入新专家'
  Object.assign(expertForm, {
    name: '', gender: '', id_card: '', highest_education: '',
    school_major: '', work_unit: '', position_title: '', contact: '',
    address: '', honors: '', professional_fields: [], professional_fields_other: '',
    personal_profile: '',
    technical_title: '', professional_certification: '', foreign_language: '',
    work_years: 0, successful_cases: 0, patents: '', publications: '',
    research_projects: '', awards: '', attachments: {}
  })
  // 清空附件上传状态（同时释放预览URL）
  clearPendingAttachments()
  expertModalVisible.value = true
}

// 打开编辑专家弹窗
async function editExpert(expertId) {
  isEditing.value = true
  editingExpertId.value = expertId
  expertModalTitle.value = '编辑专家信息'
  try {
    const response = await request.get(`/api/publish/experts/${expertId}`)
    if (response.code === 200) {
      const d = response.data
      Object.assign(expertForm, {
        name: d.name || '',
        gender: d.gender || '',
        id_card: d.id_card || '',
        highest_education: d.highest_education || '',
        school_major: d.school_major || '',
        work_unit: d.work_unit || '',
        position_title: d.position_title || '',
        contact: d.contact || '',
        address: d.address || '',
        honors: d.honors || '',
        professional_fields: d.professional_fields || [],
        professional_fields_other: d.professional_fields_other || '',
        personal_profile: d.personal_profile || '',
        technical_title: d.technical_title || '',
        professional_certification: d.professional_certification || '',
        foreign_language: d.foreign_language || '',
        work_years: d.work_years || 0,
        successful_cases: d.successful_cases || 0,
        patents: d.patents || '',
        publications: d.publications || '',
        research_projects: d.research_projects || '',
        awards: d.awards || '',
        attachments: d.attachments || {}
      })
      // 清空并重新填充已上传文件列表
      clearPendingAttachments()
      if (d.attachments) {
        Object.keys(d.attachments).forEach(type => {
          uploadedFiles[type] = d.attachments[type] || []
        })
      }
      expertModalVisible.value = true
    }
  } catch (error) {
    console.error('获取专家详情失败:', error)
    alert('获取专家详情失败')
  }
}

// 查看专家详情
async function viewExpertDetail(expertId) {
  try {
    const response = await request.get(`/api/publish/experts/${expertId}`)
    if (response.code === 200) {
      expertDetailData.value = response.data
      expertDetailVisible.value = true
    }
  } catch (error) {
    console.error('获取专家详情失败:', error)
    alert('获取专家详情失败')
  }
}

// 格式化带"其他"的字段数组
function formatFieldsWithOther(fields, other) {
  if (!fields || !Array.isArray(fields)) return '-'
  const filtered = fields.filter(f => f !== '其他')
  let result = filtered.join('、')
  if (other && other.trim()) {
    result += (result ? '、' : '') + `其他：${other}`
  }
  return result || '-'
}

// 格式化地区
function formatRegion(region) {
  if (!region) return '-'
  if (typeof region === 'string') return region || '-'
  const province = region.province || ''
  const city = region.city || ''
  if (province && city && city !== province) {
    return `${province}${city}`
  }
  return province || city || '-'
}

// 格式化转化方式
function formatTransferMethods(methods, other) {
  if (!methods || !Array.isArray(methods)) return '-'
  const filtered = methods.filter(m => m !== '其他')
  let result = filtered.join('、')
  if (other && other.trim()) {
    result += (result ? '、' : '') + `其他：${other}`
  }
  return result || '-'
}

// 格式化合作方式偏好（用于详情展示）
function formatTransferPreference(pref) {
  if (!pref) return '未指定'
  const parts = []
  if (pref.tech_transfer?.enabled) {
    let text = '技术转让'
    if (pref.tech_transfer.expected_fee) text += `（${pref.tech_transfer.expected_fee}万元）`
    parts.push(text)
  }
  if (pref.tech_license?.enabled) parts.push('技术许可')
  if (pref.tech_investment?.enabled) {
    let text = '技术入股'
    if (pref.tech_investment.valuation) text += `（作价${pref.tech_investment.valuation}万元）`
    parts.push(text)
  }
  if (pref.cooperation_dev) parts.push('合作开发')
  if (pref.other) parts.push(`其他：${pref.other}`)
  return parts.length > 0 ? parts.join('、') : '未指定'
}

// 格式化期望完成日期
function formatExpectedCompleteDate(dateObj) {
  if (!dateObj || !dateObj.year) return null
  if (dateObj.month) {
    return `${dateObj.year}年${dateObj.month}月`
  }
  return `${dateObj.year}年`
}
function formatTime(isoStr) {
  if (!isoStr) return '-'
  try {
    const d = new Date(isoStr)
    const pad = n => String(n).padStart(2, '0')
    return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
  } catch { return isoStr }
}

// ==================== FAQ 管理 ====================
async function loadFaqs() {
  try {
    const [faqRes, siteRes] = await Promise.all([
      fetch(`${FLASK_BASE_URL}/api/chat/faqs?page=1&page_size=99`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token') || ''}` }
      }),
      fetch(`${FLASK_BASE_URL}/api/chat/faqs/site-name`)
    ])
    const faqData = await faqRes.json()
    if (faqData.code === 200) {
      faqList.value = faqData.data.faqs
    }
    const siteData = await siteRes.json()
    if (siteData.code === 200 && siteData.data.site_name) {
      siteName.value = siteData.data.site_name
    }
  } catch (e) {
    console.error('加载FAQ失败:', e)
  }
}

function openFaqDialog(faq = null) {
  if (faq) {
    editingFaq.value = { id: faq.id, question: faq.question, display_text: faq.display_text || '', answer: faq.answer, status: faq.status }
  } else {
    editingFaq.value = { question: '', display_text: '', answer: '', status: 'published' }
  }
  faqDialogVisible.value = true
}

async function saveFaq() {
  const faq = editingFaq.value
  const isEdit = !!faq.id
  try {
    const url = isEdit ? `${FLASK_BASE_URL}/api/chat/faqs/${faq.id}` : `${FLASK_BASE_URL}/api/chat/faqs`
    const method = isEdit ? 'PUT' : 'POST'
    const body = {
      question: faq.question.trim(),
      answer: faq.answer.trim(),
      display_text: (faq.display_text || '').trim(),
      status: 'published'
    }
    const res = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('token') || ''}` },
      body: JSON.stringify(body)
    })
    const data = await res.json()
    if (data.code === 200) {
      alert(isEdit ? '已更新' : '已创建')
      faqDialogVisible.value = false
      loadFaqs()
      refreshGreetingPreview()
    } else {
      alert(data.msg || '操作失败')
    }
  } catch (e) {
    console.error('保存FAQ失败:', e)
    alert('操作失败')
  }
}

async function refreshGreetingPreview() {
  try {
    const res = await fetch(`${FLASK_BASE_URL}/api/chat/faqs/greeting`)
    const data = await res.json()
    if (data.code === 200 && data.data.greeting) {
      greetingPreview.value = data.data.greeting
    } else {
      greetingPreview.value = '暂无快捷引导问题'
    }
  } catch (e) {
    greetingPreview.value = '加载失败'
  }
}

async function saveSiteName() {
  try {
    await fetch(`${FLASK_BASE_URL}/api/chat/faqs/site-name`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('token') || ''}` },
      body: JSON.stringify({ site_name: siteName.value.trim() || '科创中心' })
    })
  } catch (e) {
    console.error('保存站点名称失败:', e)
  }
}

// 右侧聊天预览的测试功能
async function sendTestMessage() {
  const text = testInput.value.trim()
  if (!text || testLoading.value) return
  testInput.value = ''
  testMessages.value.push({ role: 'user', content: text })
  testLoading.value = true
  // 自动滚动到底部
  nextTick(() => { scrollPreviewChat() })
  try {
    const res = await fetch(`${FLASK_BASE_URL}/api/chat/faqs/match?q=${encodeURIComponent(text)}`)
    const data = await res.json()
    if (data.code === 200 && data.data.matched) {
      testMessages.value.push({ role: 'bot', content: data.data.answer })
    } else {
      testMessages.value.push({ role: 'bot', content: '没有匹配到答案，请检查数字是否正确或该FAQ是否已发布。' })
    }
  } catch (e) {
    testMessages.value.push({ role: 'bot', content: '请求失败，请确认后端服务是否运行。' })
  }
  testLoading.value = false
  nextTick(() => { scrollPreviewChat() })
}
function scrollPreviewChat() {
  if (previewChatRef.value) {
    previewChatRef.value.scrollTop = previewChatRef.value.scrollHeight
  }
}

async function toggleFaqStatus(faq) {
  try {
    const res = await fetch(`${FLASK_BASE_URL}/api/chat/faqs/${faq.id}/status`, {
      method: 'PUT',
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token') || ''}` }
    })
    const data = await res.json()
    if (data.code === 200) {
      loadFaqs()
      refreshGreetingPreview()
    } else {
      alert(data.msg || '操作失败')
    }
  } catch (e) {
    console.error('切换FAQ状态失败:', e)
  }
}

async function deleteFaq(faq) {
  if (!confirm(`确定删除FAQ「${faq.question}」？`)) return
  try {
    const res = await fetch(`${FLASK_BASE_URL}/api/chat/faqs/${faq.id}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token') || ''}` }
    })
    const data = await res.json()
    if (data.code === 200) {
      loadFaqs()
      refreshGreetingPreview()
    } else {
      alert(data.msg || '删除失败')
    }
  } catch (e) {
    console.error('删除FAQ失败:', e)
    alert('删除失败')
  }
}
// ================================================

// ==================== 访客日志管理 ====================
async function fetchVisitLogs() {
  visitLogLoading.value = true
  try {
    const params = {
      page: visitLogPage.value,
      page_size: visitLogPageSize.value,
      ip: visitLogSearch.ip,
      path: visitLogSearch.path,
      date_from: visitLogSearch.date_from,
      date_to: visitLogSearch.date_to
    }
    const query = Object.entries(params).filter(([, v]) => v !== '').map(([k, v]) => k + '=' + encodeURIComponent(v)).join('&')
    const res = await request.get('/api/publish/admin/visit-logs?' + query)
    if (res.code === 200) {
      visitLogs.value = res.data || []
      visitLogTotal.value = res.total || 0
    }
  } catch (e) {
    console.error('Failed to fetch visit logs:', e)
    visitLogs.value = []
  } finally {
    visitLogLoading.value = false
  }
}

function searchVisitLogs() {
  visitLogPage.value = 1
  fetchVisitLogs()
}

function resetVisitLogSearch() {
  visitLogSearch.ip = ''
  visitLogSearch.path = ''
  visitLogSearch.date_from = ''
  visitLogSearch.date_to = ''
  visitLogPage.value = 1
  fetchVisitLogs()
}

function refreshVisitLogs() {
  fetchVisitLogs()
}

function visitLogPageChange(page) {
  visitLogPage.value = page
  fetchVisitLogs()
}

async function deleteVisitLog(id) {
  if (!confirm('确定要删除该访客日志吗？')) return
  try {
    const res = await request.delete('/api/publish/admin/visit-logs/' + id)
    if (res.code === 200) {
      fetchVisitLogs()
    } else {
      alert(res.msg || '删除失败')
    }
  } catch (e) {
    alert('删除失败')
  }
}

async function clearAllVisitLogs() {
  if (!confirm('确定要清空所有访客日志吗？此操作不可恢复！')) return
  try {
    const res = await request.delete('/api/publish/admin/visit-logs/clear')
    if (res.code === 200) {
      alert(res.msg)
      fetchVisitLogs()
    } else {
      alert(res.msg || '清空失败')
    }
  } catch (e) {
    alert('清空失败')
  }
}
// ================================================

// ==================== 聊天记录管理 ====================
// ================================================

// ==================== 聊天记录管理 ====================
async function loadChatRecords() {
  try {
    const params = { page: 1, page_size: 2000 }
    if (crKeyword.value) params.keyword = crKeyword.value
    if (crStatus.value) params.status = crStatus.value
    if (crDateFrom.value) params.date_from = crDateFrom.value
    if (crDateTo.value) params.date_to = crDateTo.value
    const res = await fetch(`${FLASK_BASE_URL}/api/chat/customer-service/sessions?${new URLSearchParams(params)}`, {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token') || ''}` }
    })
    const data = await res.json()
    if (data.code === 200) {
      const rawSessions = data.data || []
      // 按 user_id 分组，每个用户只显示一条记录
      const userMap = new Map()
      const statusPriority = { 'active': 0, 'waiting': 1, 'pending': 2, 'closed': 3 }
      rawSessions.forEach(s => {
        const existing = userMap.get(s.user_id)
        const entry = {
          id: s.id,
          user_id: s.user_id,
          user_name: s.user_name,
          user_phone: s.user_phone,
          user_real_name: s.user_real_name,
          agent_name: s.agent_name,
          status: s.status,
          message_count: s.message_count || 0,
          created_at: s.created_at,
          _allSessionIds: [s.id],
          _totalMessages: s.message_count || 0
        }
        if (!existing) {
          userMap.set(s.user_id, entry)
        } else {
          const ep = statusPriority[entry.status] ?? 99
          const xp = statusPriority[existing.status] ?? 99
          if (ep < xp) {
            existing.status = entry.status
            existing.id = entry.id
            existing.agent_name = entry.agent_name
            existing.created_at = entry.created_at
          }
          existing._allSessionIds.push(s.id)
          existing._totalMessages += entry._totalMessages
          existing.message_count = existing._totalMessages
        }
      })
      crAllGrouped.value = Array.from(userMap.values())
      crTotal.value = crAllGrouped.value.length
      crTotalPages.value = Math.ceil(crTotal.value / crPageSize) || 1
      // 重置到第一页并切片
      crPage.value = 1
      crSessions.value = crAllGrouped.value.slice(0, crPageSize)
    }
  } catch (e) {
    console.error('加载聊天记录失败:', e)
  }
}

function goToCrPage(page) {
  crPage.value = page
  const start = (page - 1) * crPageSize
  crSessions.value = crAllGrouped.value.slice(start, start + crPageSize)
}

async function viewChatDetail(record) {
  crDetailUser.value = record.user_real_name || record.user_name
  crDetailVisible.value = true
  crDetailMessages.value = []
  crDetailLoading.value = true
  try {
    const allMsgs = []
    // 获取客服会话消息
    for (const sid of (record._allSessionIds || [record.id])) {
      const res = await fetch(`${FLASK_BASE_URL}/api/chat/customer-service/sessions/${sid}/messages`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token') || ''}` }
      })
      const data = await res.json()
      if (data.code === 200 && data.data) {
        data.data.forEach(msg => {
          allMsgs.push({ ...msg, _sessionId: sid, _source: 'human' })
        })
      }
    }
    // 获取机器人聊天记录
    try {
      const botRes = await fetch(`${FLASK_BASE_URL}/api/chat/bot-history/${record.user_id}`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token') || ''}` }
      })
      const botData = await botRes.json()
      if (botData.code === 200 && botData.data) {
        botData.data.forEach(msg => {
          allMsgs.push({
            sender_type: msg.sender,
            content: msg.content,
            created_at: msg.created_at,
            _sessionId: '_bot',
            _source: 'bot'
          })
        })
      }
    } catch (e) {
      console.error('加载机器人聊天记录失败:', e)
    }
    // 按时间排序
    allMsgs.sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
    crDetailMessages.value = allMsgs
  } catch (e) {
    console.error('加载聊天详情失败:', e)
  } finally {
    crDetailLoading.value = false
  }
}

async function deleteChatRecord(record) {
  const sessionCount = (record._allSessionIds || [record.id]).length
  if (!confirm(`确定要删除用户"${record.user_real_name || record.user_name}"的所有 ${sessionCount} 条会话记录吗？\n\n此操作不可恢复，用户端和客服端数据也会同步删除。`)) return

  try {
    const res = await fetch(`${FLASK_BASE_URL}/api/chat/customer-service/sessions/by-user/${record.user_id}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token') || ''}` }
    })
    const data = await res.json()
    if (data.code !== 200) {
      alert(`删除失败：${data.msg}`)
      return
    }
    // 从分组列表和当前页中移除
    crAllGrouped.value = crAllGrouped.value.filter(s => s.user_id !== record.user_id)
    crTotal.value = crAllGrouped.value.length
    crTotalPages.value = Math.ceil(crTotal.value / crPageSize) || 1
    // 如果当前页超出范围，回退到最后一页
    if (crPage.value > crTotalPages.value) crPage.value = crTotalPages.value
    crSessions.value = crAllGrouped.value.slice((crPage.value - 1) * crPageSize, crPage.value * crPageSize)
  } catch (e) {
    console.error('删除失败:', e)
    alert('删除失败，请稍后重试')
  }
}
// ===================================================

// 判断是否为图片文件
function isImageFile(fileName) {
  const ext = (fileName || '').split('.').pop().toLowerCase()
  return ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'svg'].includes(ext)
}

// 打开图片预览
function openImagePreview(url) {
  previewImageUrl.value = url
}

// 关闭图片预览
function closeImagePreview() {
  previewImageUrl.value = ''
}

// 关闭专家弹窗
function closeExpertModal() {
  clearPendingAttachments()
  expertModalVisible.value = false
}

// 提交专家表单（新增/编辑）
async function submitExpertForm() {
  if (!expertForm.name.trim()) {
    alert('请输入专家姓名')
    return
  }
  if (!expertForm.id_card.trim()) {
    alert('请输入身份证号')
    return
  }
  try {
    let response
    if (isEditing.value) {
      // 提交前将已上传文件状态同步到表单，避免旧数据覆盖已删除的附件
      syncAttachmentsToForm()
      response = await request.put(`/api/publish/experts/${editingExpertId.value}`, expertForm)
    } else {
      response = await request.post('/api/publish/experts', expertForm)
    }
    if (response.code === 200) {
      const expertId = isEditing.value ? editingExpertId.value : response.data.id
      // 上传待上传的附件文件
      const pendingTypes = Object.keys(pendingUploads).filter(t => pendingUploads[t] && pendingUploads[t].length > 0)
      if (pendingTypes.length > 0) {
        for (const type of pendingTypes) {
          const files = pendingUploads[type] || []
          for (const file of files) {
            if (file) {
              const formData = new FormData()
              formData.append('file', file)
              formData.append('attachment_type', type)
              try {
                await request.post(`/api/publish/experts/${expertId}/upload`, formData, {
                  headers: { 'Content-Type': 'multipart/form-data' }
                })
              } catch (e) {
                console.error(`上传附件 ${type} 失败:`, e)
              }
            }
          }
        }
      }
      alert(isEditing.value ? '专家信息更新成功' : '专家创建成功')
      closeExpertModal()
      fetchExperts()
    } else {
      alert(response.msg || '操作失败')
    }
  } catch (error) {
    console.error('保存专家失败:', error)
    // 显示后端返回的具体错误信息（如"身份证号已存在"）
    const msg = error.response?.data?.msg || error.response?.data?.message || error.message || '保存专家失败'
    alert(msg)
  }
}

// 删除专家
async function deleteExpert(expertId) {
  if (!confirm('确定要移除该专家吗？此操作不可撤销。')) return
  try {
    const response = await request.delete(`/api/publish/experts/${expertId}`)
    if (response.code === 200) {
      alert('专家已移除')
      fetchExperts()
    } else {
      alert(response.msg || '删除失败')
    }
  } catch (error) {
    console.error('删除专家失败:', error)
    alert('删除专家失败')
  }
}

// 切换专业领域选择（最多2个）
function toggleField(field) {
  const idx = expertForm.professional_fields.indexOf(field)
  if (idx > -1) {
    expertForm.professional_fields = expertForm.professional_fields.filter(f => f !== field)
  } else {
    if (expertForm.professional_fields.length >= 2) {
      alert('最多选择2个主领域')
      return
    }
    expertForm.professional_fields = [...expertForm.professional_fields, field]
  }
}

// 触发文件选择
function triggerFileInput(type) {
  document.getElementById('fu_' + type)?.click()
}

// 选择附件文件（支持多选）
function onAttachmentFileChange(type, event) {
  const files = Array.from(event.target.files || [])
  if (files.length === 0) return
  if (!pendingUploads[type]) {
    pendingUploads[type] = []
  }
  for (const file of files) {
    // 为每个文件创建预览URL（后续由 clearPendingAttachments 释放）
    file._previewUrl = URL.createObjectURL(file)
    pendingUploads[type].push(file)
  }
  // 重置input值，允许重复选择同一文件
  event.target.value = ''
}

// 为待上传的文件生成临时预览URL
function getObjectUrl(file) {
  return file ? (file._previewUrl || '') : ''
}

// 清空附件状态并释放预览URL
function clearPendingAttachments() {
  Object.keys(pendingUploads).forEach(type => {
    const files = pendingUploads[type]
    if (files && Array.isArray(files)) {
      files.forEach(f => {
        if (f._previewUrl) {
          URL.revokeObjectURL(f._previewUrl)
        }
      })
    }
    delete pendingUploads[type]
  })
  Object.keys(uploadedFiles).forEach(k => delete uploadedFiles[k])
}

// 删除已上传的附件
async function deleteUploadedFile(type, fileName, expertId) {
  if (!confirm(`确定要删除 ${fileName} 吗？`)) return
  try {
    await request.delete(`/api/publish/experts/${expertId}/attachments`, {
      params: { attachment_type: type, file_name: fileName }
    })
    if (uploadedFiles[type]) {
      uploadedFiles[type] = uploadedFiles[type].filter(f => f.file_name !== fileName)
    }
    if (!uploadedFiles[type] || uploadedFiles[type].length === 0) {
      delete uploadedFiles[type]
    }
    // 同步更新 expertForm.attachments，防止提交旧数据覆盖删除操作
    syncAttachmentsToForm()
  } catch (error) {
    console.error('删除附件失败:', error)
    alert('删除附件失败')
  }
}

// 将 uploadedFiles 同步到 expertForm.attachments
function syncAttachmentsToForm() {
  expertForm.attachments = {}
  Object.keys(uploadedFiles).forEach(type => {
    expertForm.attachments[type] = uploadedFiles[type]
  })
}

// 移除待上传的文件（尚未保存到服务器）
function removePendingFile(type, index) {
  if (pendingUploads[type] && pendingUploads[type].length > index) {
    pendingUploads[type].splice(index, 1)
    if (pendingUploads[type].length === 0) {
      delete pendingUploads[type]
    }
  }
}

// 计算属性
const filteredUsers = computed(() => {
  let result = users.value
  const search = userSearch.value.toLowerCase().trim()
  if (search) {
    result = result.filter(user =>
      (user.username || '').toLowerCase().includes(search) ||
      (user.real_name || '').toLowerCase().includes(search) ||
      (user.phone || '').includes(search)
    )
  }
  if (userRoleFilter.value) {
    result = result.filter(user => user.role === userRoleFilter.value)
  }
  if (userStatusFilter.value !== '') {
    result = result.filter(user => user.status === Number(userStatusFilter.value))
  }
  return result
})

const paginatedUsers = computed(() => {
  const start = (userPage.value - 1) * userPageSize.value
  const end = start + userPageSize.value
  return filteredUsers.value.slice(start, end)
})

const userTotalPages = computed(() => Math.ceil(filteredUsers.value.length / userPageSize.value))
const userTotal = computed(() => filteredUsers.value.length)

function handleUserPageChange(page) {
  if (page < 1 || page > userTotalPages.value) return
  userPage.value = page
}

function handleUserPageSizeChange(size) {
  userPageSize.value = size
  userPage.value = 1
}

// 页面切换
const switchPage = (pageId) => {
  currentPage.value = pageId
  const titles = {
    dashboard: '仪表板',
    users: '用户权限管理',
    send_notify: '发送系统通知',
    agents: '在线客服中心',
    audit: '内容合规审核',
    experts: '智库专家管理',
    partners: '合作伙伴维护',
    partner_applies: '合作申请管理',
    financial_services: '金融服务管理',
    content: '门户内容运营',
    faqs: 'FAQ 知识库管理'
  }
  pageTitle.value = titles[pageId] || '仪表板'

  if (pageId === 'agents') {
    loadChatRecords()
  }
  if (pageId === 'experts') {
    fetchExperts()
  }
  if (pageId === 'users') {
    fetchUsers()
  }
  if (pageId === 'faqs') {
    loadFaqs()
    refreshGreetingPreview()
  }
  if (pageId === 'partners') {
    fetchPartners()
  }
  if (pageId === 'partner_applies') {
    fetchPartnerApplies()
  }
  if (pageId === 'financial_services') {
    fetchFinancialServices()
  }
  if (pageId === 'audit') {
    auditSubTab.value = 'achievement'
    fetchAchievements()
  }
  if (pageId === 'send_notify') {
    fetchMessages()
  }
  if (pageId === 'visit_logs') {
    fetchVisitLogs()
  }

  // 更新菜单激活状态（通过CSS类处理）
  // 实际激活状态由模板中的:class绑定控制
}

// 侧边栏切换
const toggleSidebar = () => {
  const sidebar = document.getElementById('sidebar')
  if (sidebar) sidebar.classList.toggle('collapsed')
}

// ===== 用户管理操作 =====
const showAddUserModal = () => {
  Object.assign(userForm, {
    username: '', real_name: '', id_card: '', phone: '', password: '', role: 'common'
  })
  addUserModalVisible.value = true
}
const closeAddUserModal = () => { addUserModalVisible.value = false }

async function fetchUsers() {
  userLoading.value = true
  try {
    const response = await request.get('/api/admin/users')
    if (response.code === 200) {
      users.value = response.data || []
    }
  } catch (error) {
    console.error('获取用户列表失败:', error)
  } finally {
    userLoading.value = false
  }
}

async function submitAddUser() {
  if (!userForm.phone || userForm.phone.length !== 11) {
    alert('请输入正确的11位手机号')
    return
  }
  if (!userForm.password || userForm.password.length < 6) {
    alert('密码长度不能少于6位')
    return
  }
  try {
    const response = await request.post('/api/admin/users', { ...userForm })
    if (response.code === 200) {
      alert('用户创建成功')
      closeAddUserModal()
      fetchUsers()
    } else {
      alert(response.msg || response.message || '创建失败')
    }
  } catch (error) {
    const msg = error.response?.data?.message || error.response?.data?.msg || '创建用户失败'
    alert(msg)
  }
}

async function editUser(id) {
  editingUserId.value = id
  const user = users.value.find(u => u.id === id)
  if (!user) return
  Object.assign(userForm, {
    username: user.username || '',
    real_name: user.real_name || '',
    id_card: user.id_card || '',
    phone: user.phone || '',
    password: '',
    role: user.role || 'common'
  })
  editUserModalVisible.value = true
}
const closeEditUserModal = () => { editUserModalVisible.value = false }

async function submitEditUser() {
  const payload = {
    username: userForm.username,
    real_name: userForm.real_name,
    id_card: userForm.id_card,
    phone: userForm.phone,
    role: userForm.role
  }
  if (userForm.password) {
    if (userForm.password.length < 6) {
      alert('密码长度不能少于6位（如不修改密码请留空）')
      return
    }
    payload.password = userForm.password
  }
  try {
    const response = await request.put(`/api/admin/users/${editingUserId.value}`, payload)
    if (response.code === 200) {
      alert('用户信息更新成功')
      closeEditUserModal()
      fetchUsers()
    } else {
      alert(response.msg || response.message || '更新失败')
    }
  } catch (error) {
    const msg = error.response?.data?.message || error.response?.data?.msg || '更新用户失败'
    alert(msg)
  }
}

async function deleteUser(id) {
  if (!confirm('确定要删除该用户吗？此操作不可撤销。')) return
  try {
    const response = await request.delete(`/api/admin/users/${id}`)
    if (response.code === 200) {
      alert('用户已删除')
      fetchUsers()
    } else {
      alert(response.msg || response.message || '删除失败')
    }
  } catch (error) {
    const msg = error.response?.data?.message || error.response?.data?.msg || '删除失败'
    alert(msg)
  }
}

async function toggleUserStatus(user) {
  const action = user.status === 1 ? '禁用' : '启用'
  if (!confirm(`确定要${action}用户「${user.username || user.phone}」吗？`)) return
  try {
    const response = await request.put(`/api/admin/users/${user.id}/status`)
    if (response.code === 200) {
      user.status = response.data.status
      alert(`用户已${action}`)
    } else {
      alert(response.msg || response.message || '操作失败')
    }
  } catch (error) {
    const msg = error.response?.data?.message || error.response?.data?.msg || '操作失败'
    alert(msg)
  }
}


// ===== 合作伙伴管理操作 =====

function resetPartnerForm() {
  Object.assign(partnerForm, {
    name: '', type: '', province: '', city: '', address: '', industry: '',
    intro: '', services: '', contact: '', images: []
  })
  pendingPartnerImages.value = []
}

function searchPartnerApply() {
  fetchPartnerApplies()
}

function deletePartnerApply(item) {
  if (!confirm('确定要删除该合作申请吗？')) return
  request.delete('/api/publish/admin/cooperation/' + item.id).then(() => {
    fetchPartnerApplies()
  }).catch(error => {
    console.error('删除合作申请失败:', error)
  })
}

function viewPartnerApplyDetail(item) {
  partnerApplyDetail.value = item
  partnerApplyDetailVisible.value = true
}

function closePartnerApplyDetail() {
  partnerApplyDetailVisible.value = false
  partnerApplyDetail.value = null
}

async function fetchPartnerApplies() {
  partnerApplyLoading.value = true
  try {
    const response = await request.get('/api/publish/admin/cooperation/list', {
      params: { keyword: partnerApplyKeyword.value }
    })
    if (response.code === 200) {
      partnerApplies.value = response.data || []
    }
  } catch (error) {
    console.error('获取合作申请列表失败:', error)
  } finally {
    partnerApplyLoading.value = false
  }
}

function getStatusText(status) {
  const map = { pending: '待审核', approved: '已通过', rejected: '已驳回' }
  return map[status] || status
}

function switchAuditTab(tab) {
  auditSubTab.value = tab
  if (tab === 'achievement') {
    achievementPage.value = 1
    fetchAchievements()
  } else {
    requirementPage.value = 1
    fetchRequirements()
  }
}

async function fetchAchievements() {
  achievementLoading.value = true
  try {
    const response = await request.get('/api/publish/admin/achievements', {
      params: {
        page: achievementPage.value,
        page_size: achievementPageSize.value,
        keyword: achievementKeyword.value,
        status: achievementStatusFilter.value
      }
    })
    if (response.code === 200) {
      achievements.value = response.data || []
      achievementTotal.value = response.total || 0
      achievementTotalPages.value = response.total_pages || 0
    }
  } catch (error) {
    console.error('获取成果列表失败:', error)
  } finally {
    achievementLoading.value = false
  }
}

async function fetchRequirements() {
  requirementLoading.value = true
  try {
    const response = await request.get('/api/publish/admin/requirements', {
      params: {
        page: requirementPage.value,
        page_size: requirementPageSize.value,
        keyword: requirementKeyword.value,
        status: requirementStatusFilter.value
      }
    })
    if (response.code === 200) {
      requirements.value = response.data || []
      requirementTotal.value = response.total || 0
      requirementTotalPages.value = response.total_pages || 0
    }
  } catch (error) {
    console.error('获取需求列表失败:', error)
  } finally {
    requirementLoading.value = false
  }
}

function handleAchievementPageChange(page) {
  achievementPage.value = page
  fetchAchievements()
}

function handleAchievementPageSizeChange(size) {
  achievementPageSize.value = size
  achievementPage.value = 1
  fetchAchievements()
}

function handleRequirementPageChange(page) {
  requirementPage.value = page
  fetchRequirements()
}

function handleRequirementPageSizeChange(size) {
  requirementPageSize.value = size
  requirementPage.value = 1
  fetchRequirements()
}

function searchAchievement() {
  achievementPage.value = 1
  fetchAchievements()
}

function resetAchievementSearch() {
  achievementKeyword.value = ''
  achievementStatusFilter.value = ''
  achievementPage.value = 1
  fetchAchievements()
}

function searchRequirement() {
  requirementPage.value = 1
  fetchRequirements()
}

function resetRequirementSearch() {
  requirementKeyword.value = ''
  requirementStatusFilter.value = ''
  requirementPage.value = 1
  fetchRequirements()
}

async function viewAchievementDetail(id) {
  try {
    const response = await request.get('/api/publish/achievement/' + id)
    if (response.code === 200) {
      achievementDetailData.value = response.data
      achievementDetailVisible.value = true
    }
  } catch (error) {
    console.error('获取成果详情失败:', error)
  }
}

async function viewRequirementDetail(id) {
  try {
    const response = await request.get('/api/publish/requirement/' + id)
    if (response.code === 200) {
      requirementDetailData.value = response.data
      requirementDetailVisible.value = true
    }
  } catch (error) {
    console.error('获取需求详情失败:', error)
  }
}

async function editAchievement(item) {
  try {
    const response = await request.get('/api/publish/achievement/' + item.id)
    if (response.code === 200) {
      const d = response.data
      const region = d.region || {}
      const tp = d.transfer_preference || {}

      // 确定合作方式偏好（单选）
      const pref = tp.preferred_method || ''
      let cooperationPref = ''
      if (pref) {
        cooperationPref = pref
      } else if (tp.tech_transfer?.enabled) {
        cooperationPref = '技术转让'
      } else if (tp.tech_license?.enabled) {
        cooperationPref = '技术许可'
      } else if (tp.tech_investment?.enabled) {
        cooperationPref = '技术入股'
      } else if (tp.cooperation_dev) {
        cooperationPref = '合作开发'
      } else if (tp.other) {
        cooperationPref = '其他'
      }

      achievementEditData.value = {
        id: item.id,
        achievement_name: d.achievement_name || '',
        owner: d.owner || '',
        province: region.province || '',
        city: region.city || '',
        tech_field: Array.isArray(d.tech_fields) && d.tech_fields.length > 0 ? d.tech_fields[0] : '',
        tech_field_other: d.tech_fields_other || '',
        tech_maturity: d.tech_maturity || '',
        transfer_methods: Array.isArray(d.transfer_methods) ? d.transfer_methods : [],
        transfer_other: d.transfer_methods_other || '',
        innovation_level: d.description?.innovation_level || '',
        cooperationPref,
        transfer_fee: tp.tech_transfer?.expected_fee || 0,
        licenseType: tp.tech_license?.type || '',
        investment_valuation: tp.tech_investment?.valuation || 0,
        equityPercent: tp.tech_investment?.share_ratio ?? null,
        cooperationOther: tp.other || '',
        expectDate: tp.expected_complete_date?.year && tp.expected_complete_date?.month
          ? new Date(tp.expected_complete_date.year, tp.expected_complete_date.month - 1, 1)
          : null,
        description: {
          summary: d.description?.summary || '',
          innovation_level: d.description?.innovation_level || '',
          advantages: d.description?.advantages || '',
          core_indicators: d.description?.core_indicators || '',
          intellectual_property: d.description?.intellectual_property || ''
        }
      }
      achievementEditVisible.value = true
    }
  } catch (error) {
    console.error('获取成果详情失败:', error)
  }
}

async function saveAchievementEdit() {
  try {
    const techFieldVal = achievementEditData.value.tech_field
    const data = {
      ...achievementEditData.value,
      tech_fields: techFieldVal === '其他' ? ['其他'] : (techFieldVal ? [techFieldVal] : []),
      tech_fields_other: techFieldVal === '其他' ? (achievementEditData.value.tech_field_other || '') : '',
      transfer_methods: achievementEditData.value.transfer_methods || [],
      transfer_methods_other: achievementEditData.value.transfer_other || '',
      region: { province: achievementEditData.value.province || '', city: achievementEditData.value.city || '' }
    }
    delete data.tech_field
    delete data.tech_field_other
    delete data.transfer_other
    delete data.innovation_level
    // build transfer_preference object from cooperationPref
    const pref = achievementEditData.value.cooperationPref
    data.transfer_preference = {
      tech_transfer: { enabled: pref === '技术转让', expected_fee: achievementEditData.value.transfer_fee || 0 },
      tech_license: { enabled: pref === '技术许可', type: achievementEditData.value.licenseType || '' },
      tech_investment: { enabled: pref === '技术入股', valuation: achievementEditData.value.investment_valuation || 0, share_ratio: achievementEditData.value.equityPercent || 0 },
      cooperation_dev: pref === '合作开发',
      other: pref === '其他' ? (achievementEditData.value.cooperationOther || '') : '',
      preferred_method: pref,
      expected_complete_date: achievementEditData.value.expectDate
        ? { year: achievementEditData.value.expectDate.getFullYear(), month: achievementEditData.value.expectDate.getMonth() + 1 }
        : {}
    }
    delete data.cooperationPref
    delete data.transfer_fee
    delete data.licenseType
    delete data.investment_valuation
    delete data.equityPercent
    delete data.cooperationOther
    delete data.expectDate
    delete data.province
    delete data.city
    const response = await request.put('/api/publish/admin/achievement/' + achievementEditData.value.id, data)
    if (response.code === 200) {
      alert('成果更新成功')
      achievementEditVisible.value = false
      fetchAchievements()
    } else {
      alert(response.msg || '更新失败')
    }
  } catch (error) {
    console.error('更新成果失败:', error)
    alert('更新成果失败')
  }
}

async function editRequirement(item) {
  try {
    const response = await request.get('/api/publish/requirement/' + item.id)
    if (response.code === 200) {
      const d = response.data
      const region = d.region || {}
      const techFields = Array.isArray(d.tech_fields) ? d.tech_fields : []
      let emergingIndustry = ''
      let traditionalIndustry = ''
      let tech_field_other = d.tech_fields_other || ''
      // classify each tech field into the right category
      techFields.forEach(f => {
        if (emergingIndustries.includes(f)) emergingIndustry = f
        else if (traditionalIndustries.includes(f)) traditionalIndustry = f
        else if (f !== (d.tech_fields_other || '').trim()) {
          // not matching known categories, treat as other if "其他" in fields
        }
      })
      const demandTypes = Array.isArray(d.demand_types) ? d.demand_types : []
      let demand_type = ''
      let demand_type_other = ''
      demandTypes.forEach(t => {
        if (demandTypeOptions.includes(t)) demand_type = t
        else demand_type_other = t
      })
      if (d.demand_types_other) demand_type_other = d.demand_types_other
      // 如果 demand_types 为空但有 demand_types_other，说明类型为"其他"
      if (!demand_type && demand_type_other) {
        demand_type = '其他'
      }
      requirementEditData.value = {
        id: item.id,
        demand_name: d.demand_name || '',
        company_name: d.company_name || '',
        province: region.province || '',
        city: region.city || '',
        emergingIndustry,
        traditionalIndustry,
        tech_field: techFields.length === 1 && techFields[0] === '其他' ? '其他' : techFields[0] || '',
        tech_field_other,
        demand_type,
        demand_type_other,
        description: {
          overview: d.description?.overview || '',
          target_problems: d.description?.target_problems || '',
          budget: d.description?.budget ?? 0
        }
      }
      requirementEditVisible.value = true
    }
  } catch (error) {
    console.error('获取需求详情失败:', error)
  }
}

async function saveRequirementEdit() {
  try {
    // collect tech fields from both radio groups and other input
    const techFields = []
    if (requirementEditData.value.emergingIndustry) techFields.push(requirementEditData.value.emergingIndustry)
    if (requirementEditData.value.traditionalIndustry) techFields.push(requirementEditData.value.traditionalIndustry)
    const demandTypes = []
    if (requirementEditData.value.demand_type) demandTypes.push(requirementEditData.value.demand_type)

    const data = {
      ...requirementEditData.value,
      tech_fields: techFields,
      tech_fields_other: requirementEditData.value.tech_field_other || '',
      demand_types: demandTypes,
      demand_types_other: requirementEditData.value.demand_type_other || '',
      region: { province: requirementEditData.value.province || '', city: requirementEditData.value.city || '' }
    }
    delete data.emergingIndustry
    delete data.traditionalIndustry
    delete data.tech_field
    delete data.tech_field_other
    delete data.demand_type
    delete data.demand_type_other
    delete data.budget_unit
    delete data.province
    delete data.city
    const response = await request.put('/api/publish/admin/requirement/' + requirementEditData.value.id, data)
    if (response.code === 200) {
      alert('需求更新成功')
      requirementEditVisible.value = false
      fetchRequirements()
    } else {
      alert(response.msg || '更新失败')
    }
  } catch (error) {
    console.error('更新需求失败:', error)
    alert('更新需求失败')
  }
}

async function reviewAchievement(id, status) {
  let reason = ''
  if (status === 'rejected') {
    reason = prompt('请填写拒绝理由：')
    if (reason === null) return
    if (!reason.trim()) {
      alert('拒绝理由不能为空')
      return
    }
  }
  if (status === 'approved') {
    if (!confirm('确定要通过该成果的审核吗？审核通过后将对外展示。')) return
  } else {
    if (!confirm('确定要驳回该成果的审核吗？')) return
  }
  try {
    const response = await request.post('/api/publish/achievement/' + id + '/review', { status, reason: reason.trim() })
    if (response.code === 200) {
      alert(status === 'approved' ? '成果审核已通过，将对用户展示。' : '成果审核已驳回。')
      fetchAchievements()
    }
  } catch (error) {
    console.error('审核成果失败:', error)
  }
}

async function reviewRequirement(id, status) {
  let reason = ''
  if (status === 'rejected') {
    reason = prompt('请填写拒绝理由：')
    if (reason === null) return
    if (!reason.trim()) {
      alert('拒绝理由不能为空')
      return
    }
  }
  if (status === 'approved') {
    if (!confirm('确定要通过该需求的审核吗？审核通过后将对外展示。')) return
  } else {
    if (!confirm('确定要驳回该需求的审核吗？')) return
  }
  try {
    const response = await request.post('/api/publish/requirement/' + id + '/review', { status, reason: reason.trim() })
    if (response.code === 200) {
      alert(status === 'approved' ? '需求审核已通过，将对用户展示。' : '需求审核已驳回。')
      fetchRequirements()
    }
  } catch (error) {
    console.error('审核需求失败:', error)
  }
}

async function toggleAchievementDisplay(item) {
  const newState = !item.is_display
  if (newState) {
    const displayedCount = achievements.value.filter(a => a.is_display).length
    if (displayedCount >= 3) {
      alert('最多展示三个成果')
      return
    }
  }
  const action = newState ? '展示' : '隐藏'
  if (!confirm('确定要' + action + '该成果吗？' + (newState ? '（已展示的成果将在主页展示）' : ''))) return
  try {
    const response = await request.post('/api/publish/achievement/' + item.id + '/display', { is_display: newState })
    if (response.code === 200) {
      fetchAchievements()
    }
  } catch (error) {
    console.error('切换成果展示状态失败:', error)
  }
}

async function toggleRequirementDisplay(item) {
  const newState = !item.is_display
  if (newState) {
    const displayedCount = requirements.value.filter(r => r.is_display).length
    if (displayedCount >= 3) {
      alert('最多展示三个需求')
      return
    }
  }
  const action = newState ? '展示' : '隐藏'
  if (!confirm('确定要' + action + '该需求吗？' + (newState ? '（已展示的需求将在主页展示）' : ''))) return
  try {
    const response = await request.post('/api/publish/requirement/' + item.id + '/display', { is_display: newState })
    if (response.code === 200) {
      fetchRequirements()
    }
  } catch (error) {
    console.error('切换需求展示状态失败:', error)
  }
}

async function updateRequirementMatchStatus(status) {
  const id = requirementDetailData.value?._id || requirementDetailData.value?.id
  if (!id) return
  if (!confirm('确定将供需状态设为「' + status + '」吗？')) return
  try {
    const response = await request.put('/api/publish/admin/requirement/' + id, { match_status: status })
    if (response.code === 200) {
      requirementDetailData.value.match_status = status
      fetchRequirements()
    } else {
      alert('设置失败：' + (response.msg || '未知错误'))
    }
  } catch (error) {
    console.error('更新供需状态失败:', error)
    alert('网络错误')
  }
}

async function quickUpdateMatchStatus(id, status) {
  if (!confirm('确定将供需状态设为「' + status + '」吗？')) return
  try {
    const response = await request.put('/api/publish/admin/requirement/' + id, { match_status: status })
    if (response.code === 200) {
      fetchRequirements()
    } else {
      alert('设置失败：' + (response.msg || '未知错误'))
    }
  } catch (error) {
    console.error('更新供需状态失败:', error)
    alert('网络错误')
  }
}

async function deleteAchievement(id) {
  if (!confirm('确定要删除该成果吗？此操作不可撤销。')) return
  try {
    const response = await request.delete('/api/publish/achievement/' + id)
    if (response.code === 200) {
      alert('成果已删除')
      fetchAchievements()
    }
  } catch (error) {
    console.error('删除成果失败:', error)
  }
}

async function deleteRequirement(id) {
  if (!confirm('确定要删除该需求吗？此操作不可撤销。')) return
  try {
    const response = await request.delete('/api/publish/requirement/' + id)
    if (response.code === 200) {
      alert('需求已删除')
      fetchRequirements()
    }
  } catch (error) {
    console.error('删除需求失败:', error)
  }
}

function showAddPartnerModal() {
  isEditingPartner.value = false
  editingPartnerId.value = ''
  partnerModalTitle.value = '新增合作方'
  resetPartnerForm()
  partnerModalVisible.value = true
}

function closePartnerModal() {
  partnerModalVisible.value = false
  pendingPartnerImages.value = []
}

async function fetchPartners() {
  partnerLoading.value = true
  try {
    const params = {
      page: partnerPage.value,
      page_size: partnerPageSize.value,
      keyword: partnerKeyword.value
    }
    if (partnerTypeFilter.value) {
      params.type = partnerTypeFilter.value
    }
    const response = await request.get('/api/publish/partners', { params })
    if (response.code === 200) {
      partners.value = response.data || []
      partnerTotal.value = response.total || 0
      partnerTotalPages.value = response.total_pages || 0
    }
  } catch (error) {
    console.error('获取合作伙伴列表失败:', error)
  } finally {
    partnerLoading.value = false
  }
}

function handlePartnerPageChange(page) {
  if (page < 1 || page > partnerTotalPages.value) return
  partnerPage.value = page
  fetchPartners()
}

function handlePartnerPageSizeChange(size) {
  partnerPageSize.value = size
  partnerPage.value = 1
  fetchPartners()
}

function searchPartner() {
  partnerPage.value = 1
  fetchPartners()
}

function resetPartnerSearch() {
  partnerKeyword.value = ''
  partnerTypeFilter.value = ''
  partnerPage.value = 1
  fetchPartners()
}

async function submitPartnerForm() {
  if (!partnerForm.name.trim()) {
    alert('请输入平台名称')
    return
  }
  if (!partnerForm.province) {
    alert('请选择省份')
    return
  }
  // 组合地址
  const submitData = { ...partnerForm }
  if (submitData.province && submitData.city) {
    submitData.address = submitData.province + ' ' + submitData.city
  } else if (submitData.province) {
    submitData.address = submitData.province
  }
  try {
    let response
    if (isEditingPartner.value) {
      response = await request.put(`/api/publish/partners/${editingPartnerId.value}`, submitData)
    } else {
      response = await request.post('/api/publish/partners', submitData)
    }

    if (response.code === 200) {
      const partnerId = isEditingPartner.value ? editingPartnerId.value : response.data.id
      // 上传待上传的图片
      if (pendingPartnerImages.value.length > 0) {
        for (const file of pendingPartnerImages.value) {
          const formData = new FormData()
          formData.append('file', file)
          try {
            await request.post(`/api/publish/partners/${partnerId}/upload`, formData, {
              headers: { 'Content-Type': 'multipart/form-data' }
            })
          } catch (e) {
            console.error('上传图片失败:', e)
          }
        }
      }
      alert(isEditingPartner.value ? '合作方信息更新成功' : '合作方创建成功')
      closePartnerModal()
      fetchPartners()
    } else {
      alert(response.msg || '操作失败')
    }
  } catch (error) {
    const msg = error.response?.data?.msg || error.message || '保存失败'
    alert(msg)
  }
}

async function editPartner(id) {
  isEditingPartner.value = true
  editingPartnerId.value = id
  partnerModalTitle.value = '编辑合作方'
  try {
    const response = await request.get(`/api/publish/partners/${id}`)
    if (response.code === 200) {
      const d = response.data
      // 解析地址: "北京市 海淀区" -> province="北京市", city="海淀区"
      let province = '', city = ''
      if (d.address) {
        const parts = d.address.split(/\s+/)
        province = parts[0] || ''
        city = parts[1] || ''
      }
      Object.assign(partnerForm, {
        name: d.name || '',
        type: d.type || '',
        province,
        city,
        address: d.address || '',
        industry: d.industry || '',
        intro: d.intro || '',
        services: d.services || '',
        contact: d.contact || '',
        images: d.images || []
      })
      pendingPartnerImages.value = []
      partnerModalVisible.value = true
    }
  } catch (error) {
    console.error('获取合作方详情失败:', error)
    alert('获取合作方详情失败')
  }
}

async function deletePartner(id) {
  if (!confirm('确定要删除该合作方吗？此操作不可撤销。')) return
  try {
    const response = await request.delete(`/api/publish/partners/${id}`)
    if (response.code === 200) {
      alert('合作方已删除')
      fetchPartners()
    } else {
      alert(response.msg || '删除失败')
    }
  } catch (error) {
    console.error('删除合作方失败:', error)
    alert('删除合作方失败')
  }
}

async function viewPartnerDetail(id) {
  try {
    const response = await request.get(`/api/publish/partners/${id}`)
    if (response.code === 200) {
      partnerDetailData.value = response.data
      partnerDetailVisible.value = true
    }
  } catch (error) {
    console.error('获取合作方详情失败:', error)
    alert('获取合作方详情失败')
  }
}

// 合作伙伴图片上传
function triggerPartnerImageInput() {
  document.getElementById('partnerImageInput')?.click()
}

function onPartnerImageSelect(event) {
  const files = Array.from(event.target.files || [])
  for (const file of files) {
    file._previewUrl = URL.createObjectURL(file)
    pendingPartnerImages.value.push(file)
  }
  event.target.value = ''
}

function removePendingPartnerImage(index) {
  const file = pendingPartnerImages.value[index]
  if (file && file._previewUrl) {
    URL.revokeObjectURL(file._previewUrl)
  }
  pendingPartnerImages.value.splice(index, 1)
}

async function deletePartnerImage(fileName) {
  if (!confirm(`确定要删除该图片吗？`)) return
  try {
    await request.delete(`/api/publish/partners/${editingPartnerId.value}/images`, {
      params: { file_name: fileName }
    })
    partnerForm.images = partnerForm.images.filter(f => f.file_name !== fileName)
  } catch (error) {
    console.error('删除图片失败:', error)
    alert('删除图片失败')
  }
}

function getPartnerImageUrl(file) {
  if (file._previewUrl) return file._previewUrl
  return fullUrl(file.file_url)
}

// ========== 金融服务管理方法 ==========

function resetFinancialServiceForm() {
  financialServiceForm.name = ''
  financialServiceForm.intro = ''
  financialServiceForm.services = ''
  financialServiceForm.contact = ''
  financialServiceForm.images = []
}

function showAddFinancialServiceModal() {
  isEditingFinancialService.value = false
  editingFinancialServiceId.value = ''
  financialServiceModalTitle.value = '新增金融服务机构'
  resetFinancialServiceForm()
  pendingFinancialServiceImages.value = []
  financialServiceModalVisible.value = true
}

function closeFinancialServiceModal() {
  financialServiceModalVisible.value = false
  pendingFinancialServiceImages.value = []
}

async function fetchFinancialServices() {
  financialServiceLoading.value = true
  try {
    const params = {
      page: financialServicePage.value,
      page_size: financialServicePageSize.value
    }
    if (financialServiceKeyword.value.trim()) {
      params.keyword = financialServiceKeyword.value.trim()
    }
    const res = await request.get('/api/publish/financial-services', { params })
    if (res.code === 200) {
      financialServices.value = res.data || []
      financialServiceTotal.value = res.total || 0
      financialServiceTotalPages.value = res.total_pages || 0
    }
  } catch (e) {
    console.error('获取金融服务列表失败:', e)
  } finally {
    financialServiceLoading.value = false
  }
}

function handleFinancialServicePageChange(page) {
  financialServicePage.value = page
  fetchFinancialServices()
}

function handleFinancialServicePageSizeChange(size) {
  financialServicePageSize.value = size
  financialServicePage.value = 1
  fetchFinancialServices()
}

function searchFinancialService() {
  financialServicePage.value = 1
  fetchFinancialServices()
}

function resetFinancialServiceSearch() {
  financialServiceKeyword.value = ''
  financialServicePage.value = 1
  fetchFinancialServices()
}

async function submitFinancialServiceForm() {
  if (!financialServiceForm.name.trim()) {
    alert('请填写机构名称')
    return
  }
  try {
    const data = { ...financialServiceForm }
    let res
    if (isEditingFinancialService.value) {
      res = await request.put(`/api/publish/financial-services/${editingFinancialServiceId.value}`, data)
    } else {
      res = await request.post('/api/publish/financial-services', data)
    }
    if (res.code === 200) {
      // 上传待上传的图片
      const fsId = res.data?.id || editingFinancialServiceId.value
      if (pendingFinancialServiceImages.value.length > 0 && fsId) {
        for (const file of pendingFinancialServiceImages.value) {
          const formData = new FormData()
          formData.append('file', file)
          await request.post(`/api/publish/financial-services/${fsId}/upload`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
          })
        }
      }
      alert(isEditingFinancialService.value ? '修改成功' : '创建成功')
      closeFinancialServiceModal()
      fetchFinancialServices()
    } else {
      alert(res.msg || '操作失败')
    }
  } catch (e) {
    console.error('提交金融服务机构失败:', e)
    alert('操作失败，请稍后重试')
  }
}

async function editFinancialService(id) {
  try {
    const res = await request.get(`/api/publish/financial-services/${id}`)
    if (res.code === 200 && res.data) {
      const d = res.data
      isEditingFinancialService.value = true
      editingFinancialServiceId.value = id
      financialServiceModalTitle.value = '编辑金融服务机构'
      financialServiceForm.name = d.name || ''
      financialServiceForm.intro = d.intro || ''
      financialServiceForm.services = d.services || ''
      financialServiceForm.contact = d.contact || ''
      financialServiceForm.images = d.images || []
      pendingFinancialServiceImages.value = []
      financialServiceModalVisible.value = true
    }
  } catch (e) {
    console.error('获取金融服务机构详情失败:', e)
  }
}

async function deleteFinancialService(id) {
  if (!confirm('确定要删除该金融服务机构吗？此操作不可恢复。')) return
  try {
    const res = await request.delete(`/api/publish/financial-services/${id}`)
    if (res.code === 200) {
      alert('删除成功')
      fetchFinancialServices()
    } else {
      alert(res.msg || '删除失败')
    }
  } catch (e) {
    console.error('删除金融服务机构失败:', e)
    alert('删除失败，请稍后重试')
  }
}

async function viewFinancialServiceDetail(id) {
  try {
    financialServiceDetailVisible.value = true
    financialServiceDetailData.value = null
    const res = await request.get(`/api/publish/financial-services/${id}`)
    if (res.code === 200 && res.data) {
      financialServiceDetailData.value = res.data
    }
  } catch (e) {
    console.error('获取金融服务机构详情失败:', e)
  }
}

function triggerFinancialServiceImageInput() {
  document.getElementById('financialServiceImageInput').click()
}

function onFinancialServiceImageSelect(event) {
  const files = event.target.files
  if (!files || files.length === 0) return
  for (let i = 0; i < files.length; i++) {
    const file = files[i]
    file._previewUrl = URL.createObjectURL(file)
    pendingFinancialServiceImages.value.push(file)
  }
  event.target.value = ''
}

function removePendingFinancialServiceImage(index) {
  const file = pendingFinancialServiceImages.value[index]
  if (file._previewUrl) URL.revokeObjectURL(file._previewUrl)
  pendingFinancialServiceImages.value.splice(index, 1)
}

async function deleteFinancialServiceImage(fileName) {
  if (!confirm('确定要删除该照片吗？')) return
  try {
    const res = await request.delete(`/api/publish/financial-services/${editingFinancialServiceId.value}/images`, {
      params: { file_name: fileName }
    })
    if (res.code === 200) {
      financialServiceForm.images = financialServiceForm.images.filter(f => f.file_name !== fileName)
    }
  } catch (e) {
    console.error('删除照片失败:', e)
  }
}

function getFinancialServiceImageUrl(file) {
  if (file._previewUrl) return file._previewUrl
  return fullUrl(file.file_url)
}

const searchUsers = () => {
  // 搜索通过 computed filteredUsers 实时过滤，无需额外操作
}
const resetSearch = () => {
  userSearch.value = ''
  userRoleFilter.value = ''
  userStatusFilter.value = ''
  userPage.value = 1
}

// ===== 发送通知 =====
const notifyForm = reactive({
  title: '',
  content: ''
})
const sending = ref(false)
const sendResult = ref(null)
let sendResultTimer = null

function resetNotifyForm() {
  notifyForm.title = ''
  notifyForm.content = ''
  sendResult.value = null
  if (sendResultTimer) {
    clearTimeout(sendResultTimer)
    sendResultTimer = null
  }
}

async function sendNotification() {
  if (!notifyForm.title.trim()) {
    alert('请输入通知标题')
    return
  }
  if (!notifyForm.content.trim()) {
    alert('请输入通知内容')
    return
  }
  sending.value = true
  sendResult.value = null
  try {
    const res = await request.post('/api/admin/messages/send', {
      title: notifyForm.title.trim(),
      content: notifyForm.content.trim()
    })
    if (res.code === 200) {
      sendResult.value = { type: 'success', msg: res.msg || `通知发送成功` }
      notifyForm.title = ''
      notifyForm.content = ''
    } else {
      sendResult.value = { type: 'error', msg: res.msg || '发送失败' }
    }
  } catch (e) {
    sendResult.value = { type: 'error', msg: '发送失败，请检查网络连接' }
  } finally {
    // 5秒后自动消失
    if (sendResultTimer) clearTimeout(sendResultTimer)
    sendResultTimer = setTimeout(() => {
      sendResult.value = null
      sendResultTimer = null
    }, 5000)
    sending.value = false
  }
}

// 审核操作（已迁移至成果/需求管理）

// ===== 消息管理 =====
const msgList = ref([])
const msgLoading = ref(false)
const msgPage = ref(1)
const msgPageSize = ref(10)
const msgTotal = ref(0)
const msgTotalPages = ref(0)
const msgKeyword = ref('')
const msgTypeFilter = ref('')

const msgDisplayPages = computed(() => {
  const pages = []
  const total = msgTotalPages.value
  const current = msgPage.value
  let start = Math.max(1, current - 2)
  let end = Math.min(total, current + 2)
  if (end - start < 4) {
    if (start === 1) end = Math.min(total, start + 4)
    else start = Math.max(1, end - 4)
  }
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})

async function fetchMessages() {
  msgLoading.value = true
  try {
    const params = {
      page: msgPage.value,
      page_size: msgPageSize.value,
      keyword: msgKeyword.value,
      msg_type: msgTypeFilter.value
    }
    const res = await request.get('/api/admin/messages', { params })
    if (res.code === 200) {
      msgList.value = res.data || []
      msgTotal.value = res.total || 0
      msgTotalPages.value = res.total_pages || 0
    }
  } catch (e) {
    console.error('获取消息列表失败', e)
  } finally {
    msgLoading.value = false
  }
}

// 消息类型徽标类名
function msgBadgeClass(msg) {
  if (msg.biz_type === 'achievement') return 'badge-achievement'
  if (msg.biz_type === 'demand') return 'badge-demand'
  if (msg.msg_type === 'system') return 'badge-system'
  return 'badge-achievement'
}

// 消息类型徽标文字
function msgBadgeLabel(msg) {
  if (msg.biz_type === 'achievement') return '成果通知'
  if (msg.biz_type === 'demand') return '需求通知'
  if (msg.msg_type === 'system') return '系统通知'
  return '审核通知'
}

function searchMessages() {
  msgPage.value = 1
  fetchMessages()
}

function resetMsgSearch() {
  msgKeyword.value = ''
  msgTypeFilter.value = ''
  msgPage.value = 1
  fetchMessages()
}

function handleMsgPageChange(page) {
  if (page < 1 || page > msgTotalPages.value) return
  msgPage.value = page
  fetchMessages()
}

function handleMsgPageSizeChange() {
  msgPage.value = 1
  fetchMessages()
}

// 编辑消息
const editMsgModalVisible = ref(false)
const editMsgForm = reactive({ title: '', content: '', msg_type: 'system' })
const editingMsgId = ref(null)
const editMsgSaving = ref(false)

function editMsg(msg) {
  editingMsgId.value = msg.id
  editMsgForm.title = msg.title
  editMsgForm.content = msg.content
  editMsgForm.msg_type = msg.msg_type
  editMsgModalVisible.value = true
}

function closeEditMsgModal() {
  editMsgModalVisible.value = false
  editingMsgId.value = null
}

async function submitEditMsg() {
  if (!editMsgForm.title.trim()) {
    alert('请输入消息标题')
    return
  }
  if (!editMsgForm.content.trim()) {
    alert('请输入消息内容')
    return
  }
  editMsgSaving.value = true
  try {
    const res = await request.put(`/api/admin/messages/${editingMsgId.value}`, {
      title: editMsgForm.title.trim(),
      content: editMsgForm.content.trim(),
      msg_type: editMsgForm.msg_type
    })
    if (res.code === 200) {
      alert('消息已更新')
      closeEditMsgModal()
      fetchMessages()
    } else {
      alert(res.msg || '更新失败')
    }
  } catch (e) {
    alert('更新消息失败')
  } finally {
    editMsgSaving.value = false
  }
}

// 删除消息
async function deleteMsg(msg) {
  if (!confirm(`确定要删除消息「${msg.title}」吗？此操作不可撤销。`)) return
  try {
    const res = await request.delete(`/api/admin/messages/${msg.id}`)
    if (res.code === 200) {
      alert('消息已删除')
      fetchMessages()
    } else {
      alert(res.msg || '删除失败')
    }
  } catch (e) {
    alert('删除消息失败')
  }
}

// 图表引用
const chartRef = ref(null)
const techFieldChartRef = ref(null)
const statusDistChartRef = ref(null)
const trendChartRef = ref(null)
const visitChartRef = ref(null)

let chartInstance = null
let techFieldChartInstance = null
let statusDistChartInstance = null
let trendChartInstance = null
let visitChartInstance = null

// 仪表板数据
const dashboardData = reactive({
  pending_review: { pending_achievements: 0, pending_requirements: 0, cooperation_applications: 0 },
  customer_service: { active_sessions: 0, waiting_sessions: 0, online_agents: 0 },
  content_distribution: { tech_fields: [], achievement_status: [], requirement_status: [] },
  trends: { dates: [], achievements: [], requirements: [], users: [], visits: [] }
})

let dashboardTimer = null

async function fetchDashboardStats() {
  try {
    const res = await request.get('/api/publish/admin/dashboard/stats')
    if (res.code === 200) {
      const d = res.data
      // 更新响应式数据
      dashboardData.pending_review = d.pending_review || { pending_achievements: 0, pending_requirements: 0, cooperation_applications: 0 }
      dashboardData.customer_service = d.customer_service || { active_sessions: 0, waiting_sessions: 0, online_agents: 0 }
      dashboardData.content_distribution = d.content_distribution || { tech_fields: [], achievement_status: [], requirement_status: [] }
      dashboardData.trends = d.trends || { dates: [], achievements: [], requirements: [], users: [], visits: [] }

      // 渲染板块二的柱状图
      const chartData = [
        { name: '普通用户总数', value: d.common_users || 0, color: '#1890ff' },
        { name: '成果总数', value: d.achievements || 0, color: '#52c41a' },
        { name: '需求总数', value: d.requirements || 0, color: '#faad14' },
        { name: '专家总数', value: d.experts || 0, color: '#ff7a45' },
        { name: '伙伴总数', value: d.partners || 0, color: '#b37feb' }
      ]
      renderChart(chartData)

      // 其他图表需要 nextTick 确保 DOM 已渲染
      nextTick(() => {
        renderTechFieldChart(d.content_distribution.tech_fields || [])
        renderStatusDistChart(d.content_distribution.achievement_status || [], d.content_distribution.requirement_status || [])
        renderTrendChart(d.trends || { dates: [], achievements: [], requirements: [], users: [], visits: [] })
        renderVisitChart(d.trends || { dates: [], visits: [] })
      })
    }
  } catch (e) {
    console.error('获取仪表板统计数据失败', e)
  }
}

function renderChart(data) {
  nextTick(() => {
    if (!chartRef.value) return
    if (chartInstance) chartInstance.dispose()
    chartInstance = echarts.init(chartRef.value)

    const option = {
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        backgroundColor: 'rgba(255,255,255,0.95)',
        borderColor: '#e8e8e8',
        borderWidth: 1,
        textStyle: { color: '#333', fontSize: 13 },
        formatter: function (params) {
          const p = params[0]
          return `<strong>${p.name}</strong><br/>数量: <strong style="color:${p.color}">${p.value.toLocaleString()}</strong>`
        }
      },
      grid: {
        left: '8%',
        right: '15%',
        top: '10%',
        bottom: '12%',
        containLabel: true
      },
      xAxis: {
        type: 'value',
        axisLine: { show: false },
        axisTick: { show: false },
        splitLine: {
          lineStyle: { color: '#f0f0f0', type: 'dashed' }
        },
        axisLabel: {
          color: '#999',
          fontSize: 12
        }
      },
      yAxis: {
        type: 'category',
        data: data.map(d => d.name),
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: {
          color: '#666',
          fontSize: 13,
          fontWeight: 500,
          padding: [0, 10, 0, 0]
        }
      },
      series: [{
        type: 'bar',
        data: data.map(d => ({
          value: d.value,
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
              { offset: 0, color: d.color + '99' },
              { offset: 1, color: d.color }
            ]),
            borderRadius: [0, 6, 6, 0],
            shadowColor: d.color + '40',
            shadowBlur: 8,
            shadowOffsetX: 2
          }
        })),
        barWidth: 36,
        barGap: '30%',
        label: {
          show: true,
          position: 'right',
          formatter: function (p) {
            return p.value.toLocaleString()
          },
          color: '#333',
          fontWeight: 'bold',
          fontSize: 16,
          fontFamily: 'Arial',
          offset: [8, 0]
        },
        animationDuration: 1200,
        animationEasing: 'cubicOut'
      }]
    }

    chartInstance.setOption(option)
    chartInstance.on('click', function () {})

    const ro = new ResizeObserver(() => {
      chartInstance && chartInstance.resize()
    })
    ro.observe(chartRef.value)
    chartRef.value._resizeObserver = ro
  })
}

function renderTechFieldChart(data) {
  nextTick(() => {
    if (!techFieldChartRef.value) return
    if (techFieldChartInstance) techFieldChartInstance.dispose()
    techFieldChartInstance = echarts.init(techFieldChartRef.value)

    const colorPalette = ['#1890ff', '#52c41a', '#faad14', '#ff7a45', '#b37feb', '#13c2c2', '#eb2f96', '#a0d911', '#fa8c16', '#2f54eb']

    const hasData = data && data.length > 0
    const option = {
      tooltip: {
        trigger: 'item',
        formatter: '{b}<br/>数量: {c} ({d}%)',
        backgroundColor: 'rgba(255,255,255,0.95)',
        borderColor: '#e8e8e8',
        borderWidth: 1,
        textStyle: { color: '#333', fontSize: 13 }
      },
      series: [{
        type: 'pie',
        radius: ['35%', '60%'],
        center: ['50%', '50%'],
        avoidLabelOverlap: true,
        itemStyle: {
          borderRadius: 4,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: hasData,
          formatter: '{b}\n{d}%',
          fontSize: 12,
          color: '#666'
        },
        emphasis: {
          label: { show: true, fontSize: 14, fontWeight: 'bold' }
        },
        data: hasData
          ? data.map((item, index) => ({
              name: item.name || item._id || '未知',
              value: item.count || 0,
              itemStyle: { color: colorPalette[index % colorPalette.length] }
            }))
          : [{ name: '暂无数据', value: 1, itemStyle: { color: '#f0f0f0', label: { show: false } } }]
      }]
    }

    techFieldChartInstance.setOption(option)
    const ro = new ResizeObserver(() => {
      techFieldChartInstance && techFieldChartInstance.resize()
    })
    ro.observe(techFieldChartRef.value)
    techFieldChartRef.value._resizeObserver = ro
  })
}

function renderStatusDistChart(achievementStatus, requirementStatus) {
  nextTick(() => {
    if (!statusDistChartRef.value) return
    if (statusDistChartInstance) statusDistChartInstance.dispose()
    statusDistChartInstance = echarts.init(statusDistChartRef.value)

    const statusLabels = ['pending', 'approved', 'rejected']
    const statusLabelMap = { 'pending': '待审核', 'approved': '已通过', 'rejected': '已拒绝' }
    const categories = statusLabels.map(s => statusLabelMap[s])

    const achievementMap = {}
    ;(achievementStatus || []).forEach(item => { achievementMap[item.name] = item.count })
    const requirementMap = {}
    ;(requirementStatus || []).forEach(item => { requirementMap[item.name] = item.count })

    const option = {
      tooltip: {
        trigger: 'axis',
        backgroundColor: 'rgba(255,255,255,0.95)',
        borderColor: '#e8e8e8',
        borderWidth: 1,
        textStyle: { color: '#333', fontSize: 13 }
      },
      legend: {
        data: ['成果', '需求'],
        bottom: 0,
        icon: 'circle',
        itemWidth: 8,
        itemHeight: 8
      },
      grid: {
        left: '10%',
        right: '8%',
        top: '8%',
        bottom: '22%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: categories,
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: { color: '#666', fontSize: 13 }
      },
      yAxis: {
        type: 'value',
        splitLine: { lineStyle: { color: '#f0f0f0', type: 'dashed' } },
        axisLabel: { color: '#999', fontSize: 12 }
      },
      series: [
        {
          name: '成果',
          type: 'bar',
          data: statusLabels.map(s => achievementMap[s] || 0),
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#1890ff' },
              { offset: 1, color: '#1890ff66' }
            ]),
            borderRadius: [4, 4, 0, 0]
          },
          barWidth: 24
        },
        {
          name: '需求',
          type: 'bar',
          data: statusLabels.map(s => requirementMap[s] || 0),
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#52c41a' },
              { offset: 1, color: '#52c41a66' }
            ]),
            borderRadius: [4, 4, 0, 0]
          },
          barWidth: 24
        }
      ]
    }

    statusDistChartInstance.setOption(option)
    const ro = new ResizeObserver(() => {
      statusDistChartInstance && statusDistChartInstance.resize()
    })
    ro.observe(statusDistChartRef.value)
    statusDistChartRef.value._resizeObserver = ro
  })
}

function renderTrendChart(trendData) {
  nextTick(() => {
    if (!trendChartRef.value) return
    if (trendChartInstance) trendChartInstance.dispose()
    trendChartInstance = echarts.init(trendChartRef.value)

    const dates = (trendData.dates || []).map(d => {
      if (typeof d === 'string' && d.length >= 10) return d.slice(5)
      return d
    })

    const option = {
      tooltip: {
        trigger: 'axis',
        backgroundColor: 'rgba(255,255,255,0.95)',
        borderColor: '#e8e8e8',
        borderWidth: 1,
        textStyle: { color: '#333', fontSize: 13 }
      },
      legend: {
        data: ['成果提交', '需求提交', '用户注册'],
        bottom: 0,
        icon: 'circle',
        itemWidth: 8,
        itemHeight: 8
      },
      grid: {
        left: '6%',
        right: '6%',
        top: '10%',
        bottom: '20%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: dates,
        boundaryGap: false,
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: { color: '#999', fontSize: 12 }
      },
      yAxis: {
        type: 'value',
        minInterval: 1,
        splitLine: { lineStyle: { color: '#f0f0f0', type: 'dashed' } },
        axisLabel: { color: '#999', fontSize: 12 }
      },
      series: [
        {
          name: '成果提交',
          type: 'line',
          smooth: true,
          data: trendData.achievements || [],
          symbol: 'circle',
          symbolSize: 8,
          lineStyle: { width: 3, color: '#1890ff' },
          itemStyle: { color: '#1890ff' },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#1890ff40' },
              { offset: 1, color: '#1890ff05' }
            ])
          }
        },
        {
          name: '需求提交',
          type: 'line',
          smooth: true,
          data: trendData.requirements || [],
          symbol: 'diamond',
          symbolSize: 8,
          lineStyle: { width: 3, color: '#52c41a' },
          itemStyle: { color: '#52c41a' },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#52c41a40' },
              { offset: 1, color: '#52c41a05' }
            ])
          }
        },
        {
          name: '用户注册',
          type: 'line',
          smooth: true,
          data: trendData.users || [],
          symbol: 'roundRect',
          symbolSize: 8,
          lineStyle: { width: 3, color: '#faad14' },
          itemStyle: { color: '#faad14' },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#faad1440' },
              { offset: 1, color: '#faad1405' }
            ])
          }
        }
      ]
    }

    trendChartInstance.setOption(option)
    const ro = new ResizeObserver(() => {
      trendChartInstance && trendChartInstance.resize()
    })
    ro.observe(trendChartRef.value)
    trendChartRef.value._resizeObserver = ro
  })
}

function renderVisitChart(trendData) {
  nextTick(() => {
    if (!visitChartRef.value) return
    if (visitChartInstance) visitChartInstance.dispose()
    visitChartInstance = echarts.init(visitChartRef.value)

    const dates = (trendData.dates || []).map(d => {
      if (typeof d === 'string' && d.length >= 10) return d.slice(5)
      return d
    })

    const option = {
      tooltip: {
        trigger: 'axis',
        backgroundColor: 'rgba(255,255,255,0.95)',
        borderColor: '#e8e8e8',
        borderWidth: 1,
        textStyle: { color: '#333', fontSize: 13 }
      },
      grid: {
        left: '6%',
        right: '6%',
        top: '10%',
        bottom: '12%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: dates,
        boundaryGap: false,
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: { color: '#999', fontSize: 12 }
      },
      yAxis: {
        type: 'value',
        minInterval: 1,
        splitLine: { lineStyle: { color: '#f0f0f0', type: 'dashed' } },
        axisLabel: { color: '#999', fontSize: 12 }
      },
      series: [{
        name: '独立访客(UV)',
        type: 'line',
        smooth: true,
        data: trendData.visits || [],
        symbol: 'circle',
        symbolSize: 8,
        lineStyle: { width: 3, color: '#ff7a45' },
        itemStyle: { color: '#ff7a45' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#ff7a4540' },
            { offset: 1, color: '#ff7a4505' }
          ])
        },
        markLine: {
          silent: true,
          data: [
            { type: 'average', name: '日均UV' }
          ],
          lineStyle: { color: '#ff7a45', type: 'dashed', width: 1 },
          label: { formatter: '平均: {c}', color: '#999', fontSize: 11 }
        }
      }]
    }

    visitChartInstance.setOption(option)
    const ro = new ResizeObserver(() => {
      visitChartInstance && visitChartInstance.resize()
    })
    ro.observe(visitChartRef.value)
    visitChartRef.value._resizeObserver = ro
  })
}

// 初始化
onMounted(() => {
  fetchUsers()
  fetchDashboardStats()
  // 每30秒自动刷新仪表板数据
  dashboardTimer = setInterval(fetchDashboardStats, 30000)
})

onBeforeUnmount(() => {
  if (dashboardTimer) clearInterval(dashboardTimer)
  const cleanup = (ref, instance) => {
    if (ref && ref.value && ref.value._resizeObserver) {
      ref.value._resizeObserver.disconnect()
    }
    if (instance) {
      instance.dispose()
    }
  }
  cleanup(chartRef, chartInstance)
  cleanup(techFieldChartRef, techFieldChartInstance)
  cleanup(statusDistChartRef, statusDistChartInstance)
  cleanup(trendChartRef, trendChartInstance)
  cleanup(visitChartRef, visitChartInstance)
})
</script>

<style scoped>
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');

:root {
  --primary-color: #1890ff;
  --primary-hover: #096dd9;
  --secondary-bg: #e6f7ff;
  --secondary-border: #91d5ff;
  --success-color: #52c41a;
  --warning-color: #faad14;
  --error-color: #ff4d4f;
  --bg-color: #f0f2f5;
  --sidebar-bg: #ffffff;
  --sidebar-text: rgba(0, 0, 0, 0.65);
  --sidebar-active: #1890ff;
  --header-height: 70px;
  --sidebar-width: 260px;
  --border-color: #f0f0f0;
  --white: #ffffff;
  --text-main: rgba(0, 0, 0, 0.85);
  --text-secondary: rgba(0, 0, 0, 0.65);
  --text-muted: rgba(0, 0, 0, 0.45);
  --box-shadow-base: 0 2px 10px rgba(0, 0, 0, 0.05);
  --box-shadow-hover: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.admin-container * {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
}

.admin-container {
  background-color: var(--bg-color);
  color: var(--text-main);
  overflow: hidden;
  line-height: 1.6;
  display: flex;
  height: calc(100% - 70px);
  padding-top: 20px;
}

/* 侧边栏 */
.sidebar {
  width: var(--sidebar-width);
  background-color: var(--sidebar-bg);
  display: flex;
  flex-direction: column;
  transition: width 0.3s;
  border-right: 1px solid var(--border-color);
  position: relative;
  z-index: 20;
}

.sidebar.collapsed {
  width: 64px;
}

.sidebar.collapsed .logo-text {
  display: none;
}

.sidebar.collapsed .menu-item span:not(.menu-icon) {
  display: none;
}

.sidebar.collapsed .menu-item {
  justify-content: center;
  padding: 0;
}

.sidebar.collapsed .menu-icon {
  margin-right: 0;
  font-size: 18px;
}

.logo {
  height: var(--header-height);
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid var(--border-color);
  padding: 0 20px;
}

.logo-text {
  font-size: 22px;
  font-weight: bold;
  color: #1890ff;
  letter-spacing: 1px;
  white-space: nowrap;
  overflow: hidden;
}

.menu {
  flex: 1;
  overflow-y: auto;
  padding: 16px 12px;
}

.menu-item {
  height: 44px;
  display: flex;
  align-items: center;
  padding: 0 16px;
  color: var(--sidebar-text);
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 8px;
  border-radius: 6px;
  font-weight: 500;
}

.menu-item:hover {
  background-color: #f8f9fa;
  color: var(--primary-color);
}

.menu-item.active {
  color: var(--primary-color);
  background-color: var(--secondary-bg);
  border-left: 4px solid var(--primary-color);
}

.menu-icon {
  margin-right: 12px;
  font-size: 16px;
}

/* 主内容区 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 顶部导航 */
.header {
  height: var(--header-height);
  background-color: var(--bg-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  z-index: 10;
}

.header-left {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-main);
  display: flex;
  align-items: center;
  gap: 15px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.user-tag {
  visibility: hidden;
}

.user-tag:hover {
  color: var(--primary-color);
}

/* 内容区 */
.content-area {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  background-color: var(--bg-color);
}

/* 卡片样式 */
.card {
  background-color: var(--white);
  border-radius: 8px;
  border: 1px solid var(--border-color);
  box-shadow: var(--box-shadow-base);
  margin-bottom: 24px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.card:hover {
  box-shadow: var(--box-shadow-hover);
}

.card-header {
  padding: 16px 24px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #fcfcfc;
}

.card-title {
  font-size: 16px;
  font-weight: bold;
  color: var(--text-main);
  border-left: 3px solid var(--primary-color);
  padding-left: 10px;
}

.card-body {
  padding: 24px;
}

/* 表格样式 */
.table-container {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  white-space: nowrap;
}

.data-table th,
.data-table td {
  padding: 14px 16px;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
  font-size: 14px;
}

.data-table th {
  background-color: #f8f9fa;
  font-weight: bold;
  color: var(--text-secondary);
}

.data-table tr {
  transition: background-color 0.3s ease;
}

.data-table tr:hover {
  background-color: #fcfcfc;
}

/* 状态标签 */
.status-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-active {
  background-color: #e8f5e9;
  color: #2e7d32;
  border: 1px solid #c8e6c9;
}

.status-inactive {
  background-color: #fff3e0;
  color: #ef6c00;
  border: 1px solid #ffe0b2;
}
.status-pending {
  background-color: #fff7e6;
  color: #d48806;
  border: 1px solid #ffe58f;
}
.status-approved {
  background-color: #e8f5e9;
  color: #2e7d32;
  border: 1px solid #c8e6c9;
}
.status-rejected {
  background-color: #fbe9e7;
  color: #c62828;
  border: 1px solid #ffccbc;
}

.match-status-badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}
.match-待对接 {
  background-color: #fff7e6;
  color: #d48806;
  border: 1px solid #ffe58f;
}
.match-对接中 {
  background-color: #e6f7ff;
  color: #1890ff;
  border: 1px solid #91d5ff;
}
.match-已完成 {
  background-color: #e8f5e9;
  color: #2e7d32;
  border: 1px solid #c8e6c9;
}

.status-admin {
  background-color: var(--secondary-bg);
  color: var(--primary-color);
  border: 1px solid var(--secondary-border);
}

/* 消息类型徽标色彩 */
.badge-achievement {
  background-color: #e6f7ff;
  color: #1890ff;
  border: 1px solid #91d5ff;
}
.badge-demand {
  background-color: #e8f5e9;
  color: #2e7d32;
  border: 1px solid #c8e6c9;
}
.badge-system {
  background-color: #fff7e6;
  color: #d46b08;
  border: 1px solid #ffd591;
}

/* 角色标签样式 */
.role-badge {
  display: inline-flex;
  align-items: center;
  padding: 3px 14px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  letter-spacing: 0.3px;
  white-space: nowrap;
  transition: all 0.3s ease;
}
.role-admin {
  background: linear-gradient(135deg, #4a6cf7 0%, #7c3aed 100%);
  color: #fff;
  box-shadow: 0 2px 8px rgba(74, 108, 247, 0.3);
}
.role-agent {
  background: linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%);
  color: #fff;
  box-shadow: 0 2px 8px rgba(14, 165, 233, 0.3);
}
.role-common {
  background: #f0f2f5;
  color: #8c8c8c;
  border: 1px solid #e8e8e8;
}
.role-common::before {
  background: #bfbfbf;
}

/* 按钮样式 */
.btn {
  padding: 8px 16px;
  border-radius: 4px;
  border: 1px solid transparent;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.btn-primary {
  background-color: var(--primary-color);
  color: white;
}

.btn-primary:hover {
  background-color: var(--primary-hover);
}

.btn-default {
  background-color: white;
  color: var(--primary-color);
  border: 1px solid var(--primary-color);
}

.btn-default:hover {
  background-color: var(--secondary-bg);
}

.btn-success {
  background-color: var(--success-color);
  color: #333;
}

.btn-warning {
  background-color: var(--warning-color);
  color: #333;
}

.btn-error {
  background-color: transparent;
  color: var(--error-color);
  border: 1px solid var(--error-color);
}
.btn-error:hover {
  background-color: #fff1f0;
  color: var(--error-color);
  border-color: var(--error-color);
}

.btn-sm {
  padding: 4px 10px;
  font-size: 13px;
}

/* 供需状态下拉框 */
/* 自定义供需状态下拉 */
.custom-dropdown {
  display: inline-block;
  margin-right: 4px;
}
.dropdown-trigger {
  display: inline-flex !important;
  align-items: center;
  gap: 4px;
}
.dropdown-arrow {
  font-size: 10px;
  color: #999;
  line-height: 1;
}
.dropdown-menu {
  background: #fff;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.12);
  overflow: hidden;
}
.dropdown-item {
  padding: 5px 12px;
  font-size: 13px;
  color: #333;
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.15s;
}
.dropdown-item:hover {
  background: #f0f9ff;
  color: #1890ff;
}
.dropdown-item.active {
  background: #e6f7ff;
  color: #1890ff;
  font-weight: 500;
}

/* 分页样式 */

/* 分页样式 */
.pagination-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}
.pagination-info {
  font-size: 13px;
  color: var(--text-muted);
}
.pagination-controls {
  display: flex;
  align-items: center;
  gap: 6px;
}
.pagination-size-select {
  font-size: 13px;
  color: var(--text-secondary);
  margin-right: 8px;
  display: flex;
  align-items: center;
  gap: 4px;
}
.pagination-size-select select {
  padding: 4px 8px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 13px;
  color: var(--text-secondary);
  background: #fff;
  cursor: pointer;
  outline: none;
}
.pagination-size-select select:focus {
  border-color: var(--primary-color);
}

/* 表单样式 */
.form-group {
  margin-bottom: 16px;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  color: var(--text-secondary);
  font-weight: 600;
  font-size: 14px;
}

.form-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 14px;
  transition: all 0.3s ease;
}

.form-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.2);
}

/* 弹窗 */
.modal {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  align-items: center;
  justify-content: center;
  animation: modalFadeIn 0.3s ease;
}

@keyframes modalFadeIn {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}

.modal.active {
  display: flex;
}

.modal-content {
  background-color: var(--white);
  border-radius: 8px;
  width: 500px;
  max-width: 90%;
  max-height: 90%;
  overflow-y: auto;
  border: 1px solid #888;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.modal-header {
  padding: 16px 24px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #f8fbff;
}

.modal-title {
  font-size: 18px;
  font-weight: bold;
  color: var(--primary-color);
}

.modal-close {
  cursor: pointer;
  font-size: 24px;
  color: #aaa;
  background: none;
  border: none;
  transition: all 0.3s;
}

.modal-close:hover {
  color: #000;
  transform: scale(1.1);
}

.modal-body {
  padding: 24px;
}

.modal-footer {
  padding: 16px 24px;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  background-color: #fafafa;
}

/* 仪表板卡片 */
.dashboard-top-row {
  display: flex;
  gap: 24px;
  margin-bottom: 24px;
  flex-wrap: wrap;
  align-items: stretch;
}

.dashboard-left-column {
  flex: 1.5;
  min-width: 300px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.echarts-chart {
  width: 100%;
  height: 360px;
  background: var(--white);
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  border: 1px solid var(--border-color);
  padding: 8px;
  transition: all 0.3s ease;
}

.echarts-chart:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

/* 仪表板分区卡片 */
.dashboard-section {
  background: var(--white);
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  border: 1px solid var(--border-color);
  padding: 24px;
  margin-bottom: 24px;
  transition: all 0.3s ease;
}

.dashboard-section:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-main);
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 2px solid var(--primary-color);
  display: inline-block;
}

/* 统计卡片行 */
.stat-card-row {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.stat-card {
  flex: 1;
  min-width: 180px;
  display: flex;
  align-items: center;
  padding: 20px 24px;
  border-radius: 10px;
  background: #fafafa;
  border: 1px solid var(--border-color);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.stat-card-clickable {
  cursor: pointer;
}

.stat-card-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  margin-right: 16px;
  flex-shrink: 0;
}

.stat-card-blue .stat-card-icon { background: #e6f7ff; }
.stat-card-orange .stat-card-icon { background: #fff7e6; }
.stat-card-purple .stat-card-icon { background: #f9f0ff; }
.stat-card-green .stat-card-icon { background: #f6ffed; }
.stat-card-yellow .stat-card-icon { background: #fffbe6; }
.stat-card-cyan .stat-card-icon { background: #e6fffb; }

.stat-card-body { flex: 1; }

.stat-card-label {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.stat-card-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-main);
  font-family: Arial, sans-serif;
  line-height: 1.2;
}

/* 两列图表布局 */
.chart-row-2col {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
}

.chart-col {
  flex: 1;
  min-width: 280px;
}

.chart-col-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
  text-align: center;
  margin-bottom: 12px;
}

.pie-chart {
  height: 300px;
}

.trend-chart {
  height: 350px;
}

/* 发送通知 */
.notify-form {
  max-width: 680px;
  padding: 20px 0;
}
.form-group {
  margin-bottom: 20px;
}
.form-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: rgba(0,0,0,0.85);
  margin-bottom: 8px;
}
.form-input {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #d9d9d9;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
  box-sizing: border-box;
  background: white;
}
.form-input:focus {
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24,144,255,0.1);
}
.form-static {
  width: 100%;
  padding: 10px 14px;
  font-size: 14px;
  color: #333;
  background: #f5f5f5;
  border: 1px solid #d9d9d9;
  border-radius: 8px;
  box-sizing: border-box;
}
.form-textarea {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #d9d9d9;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
  box-sizing: border-box;
  resize: vertical;
  font-family: inherit;
  line-height: 1.6;
  background: white;
}
.form-textarea:focus {
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24,144,255,0.1);
}
.form-tip {
  text-align: right;
  font-size: 12px;
  color: #bbb;
  margin-top: 4px;
}
.form-preview {
  margin-bottom: 20px;
}
.preview-label {
  font-size: 13px;
  color: #999;
  margin-bottom: 10px;
}
.preview-card {
  background: #fafafa;
  border: 1px dashed #e8e8e8;
  border-radius: 8px;
  padding: 16px 20px;
}
.preview-title {
  font-size: 15px;
  font-weight: 600;
  color: rgba(0,0,0,0.85);
  margin-bottom: 8px;
}
.preview-content {
  font-size: 13px;
  color: #666;
  line-height: 1.6;
  white-space: pre-wrap;
}
.form-actions {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}
.btn {
  padding: 9px 24px;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  border: 1px solid #d9d9d9;
  transition: all 0.2s;
}
.btn-primary {
  background: #1890ff;
  color: white;
  border-color: #1890ff;
}
.btn-primary:hover {
  background: #40a9ff;
  border-color: #40a9ff;
}
.btn-primary:disabled {
  background: #91d5ff;
  border-color: #91d5ff;
  cursor: not-allowed;
}
.btn-default {
  background: white;
  color: #666;
}
.btn-default:hover {
  color: #1890ff;
  border-color: #1890ff;
}
.notify-result {
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 14px;
}
.notify-result.success {
  background: #f6ffed;
  border: 1px solid #b7eb8f;
  color: #52c41a;
}
.notify-result.error {
  background: #fff2f0;
  border: 1px solid #ffccc7;
  color: #ff4d4f;
}

/* 选项卡 */
.tabs {
  display: flex;
  border-bottom: 1px solid var(--border-color);
  margin-bottom: 20px;
  gap: 15px;
}

.tab {
  padding: 10px 15px;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  font-weight: 500;
  color: var(--text-secondary);
  transition: all 0.3s;
}

.tab:hover {
  color: var(--primary-color);
}

.tab.active {
  color: var(--primary-color);
  border-bottom-color: var(--primary-color);
}

/* 搜索框 */
.search-box {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.search-input {
  flex: 1;
  max-width: 400px;
  padding: 10px 15px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  transition: all 0.3s ease;
}

.search-input:focus {
  box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.2);
  outline: none;
}

.search-select {
  padding: 10px 15px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 14px;
  color: var(--text-secondary);
  background: #fff;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 120px;
}
.search-select:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.2);
}

.menu-toggle {
  display: none;
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: var(--text-main);
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 60px 24px;
  color: var(--text-secondary);
  background-color: var(--white);
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.7;
}

/* 专家卡片页面的网格 */
.experts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}
.expert-card {
  display: flex;
  align-items: center;
  padding: 20px;
  background-color: var(--white);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  box-shadow: var(--box-shadow-base);
  gap: 15px;
  transition: all 0.3s ease;
}
.expert-card:hover {
  box-shadow: var(--box-shadow-hover);
}
.expert-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background-color: var(--secondary-bg);
  color: var(--primary-color);
  border: 2px solid var(--secondary-border);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: bold;
}
.expert-info {
  flex: 1;
}
.expert-name {
  font-size: 16px;
  font-weight: bold;
  color: var(--text-main);
  margin-bottom: 4px;
}
.expert-title {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}
.expert-org {
  font-size: 13px;
  color: var(--primary-color);
  font-weight: 500;
  margin-bottom: 8px;
}
.tag {
  display: inline-block;
  padding: 4px 10px;
  background-color: var(--secondary-bg);
  color: var(--primary-hover);
  border-radius: 4px;
  font-size: 12px;
  margin-right: 6px;
}

/* 专家卡片专业领域标签 */
.expert-fields {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 8px;
}
.field-tag {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 12px;
  border: 1px solid;
  transition: all 0.2s ease;
  cursor: default;
  white-space: nowrap;
}
.field-tag:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 6px rgba(0,0,0,0.1);
}
.field-tag-more {
  background: #f5f5f5 !important;
  color: #888 !important;
  border-color: #d9d9d9 !important;
  font-weight: 600;
  cursor: pointer;
}
.field-tag-more:hover {
  background: #e8e8e8 !important;
  color: #555 !important;
}
.field-tag-empty {
  background: #fafafa !important;
  color: #bbb !important;
  border-color: #eee !important;
  font-style: italic;
  font-size: 12px;
  padding: 3px 12px !important;
  border-radius: 12px !important;
  cursor: default;
}
.expert-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* 动态内容控制 */
.tab-content, .page {
  display: none;
}
.tab-content.active, .page.active {
  display: block;
  animation: fadeIn 0.4s ease;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(5px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 审核列表优化 */
.audit-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.audit-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background-color: var(--white);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  transition: all 0.3s ease;
}
.audit-item:hover {
  box-shadow: var(--box-shadow-hover);
}
.audit-info {
  flex: 1;
}
.audit-title {
  font-size: 16px;
  font-weight: bold;
  color: var(--text-main);
  margin-bottom: 6px;
}
.audit-meta {
  font-size: 13px;
  color: var(--text-muted);
  margin-bottom: 10px;
}
.audit-desc {
  font-size: 14px;
  color: var(--text-secondary);
  background-color: #f9f9f9;
  padding: 8px 12px;
  border-radius: 4px;
  border-left: 3px solid var(--primary-color);
}
.audit-actions {
  display: flex;
  gap: 10px;
  margin-left: 20px;
}

/* 响应式 */
@media (max-width: 768px) {
  .sidebar { width: 0; border: none; }
  .sidebar.active { width: var(--sidebar-width); position: fixed; height: 100%; z-index: 100; box-shadow: 4px 0 10px rgba(0,0,0,0.1); }
  .menu-toggle { display: block; }
  .dashboard-top-row { flex-direction: column; }
  .dashboard-left-column { min-width: 100%; }
  .stat-card-row { flex-direction: column; }
  .stat-card { min-width: 100%; }
  .chart-row-2col { flex-direction: column; }
  .pie-chart { height: 250px; }
  .trend-chart { height: 280px; }
  .header-left span { font-size: 16px; }
  .expert-card { flex-direction: column; align-items: flex-start; }
  .expert-actions { flex-direction: row; width: 100%; }
  .expert-actions .btn { flex: 1; }
}
/* 专家表单样式 */
.expert-form-section {
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}
.expert-form-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}
.expert-form-section-title {
  font-size: 16px;
  font-weight: bold;
  color: var(--primary-color);
  margin-bottom: 16px;
  padding-left: 8px;
  border-left: 3px solid var(--primary-color);
}
.expert-form-subsection {
  margin-bottom: 16px;
  padding: 12px 16px;
  background: #f9fafb;
  border-radius: 6px;
}
.expert-form-subsection-title {
  font-size: 14px;
  font-weight: 600;
  color: #555;
  margin-bottom: 12px;
}
.form-row {
  display: flex;
  gap: 16px;
}
.flex-1 {
  flex: 1;
}
.checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.checkbox-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
  user-select: none;
}
.checkbox-item.checked {
  background-color: var(--secondary-bg);
  border-color: var(--primary-color);
  color: var(--primary-color);
}
.checkbox-custom {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  border: 2px solid #999;
  border-radius: 3px;
  flex-shrink: 0;
  transition: all 0.2s;
}
.checkbox-item.checked .checkbox-custom {
  border-color: var(--primary-color);
  background-color: var(--primary-color);
}
.checkbox-checkmark {
  color: #fff;
  font-size: 12px;
  font-weight: bold;
  line-height: 1;
}
.modal-lg {
  width: 900px;
  max-width: 95%;
}
/* 专家详情样式 */
.detail-section {
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #eee;
}
.detail-section:last-child {
  border-bottom: none;
}
.detail-section-title {
  font-size: 15px;
  font-weight: bold;
  color: var(--primary-color);
  margin-bottom: 12px;
  padding-left: 8px;
  border-left: 3px solid var(--primary-color);
}
.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}
.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 8px 12px;
  background: #f9fafb;
  border-radius: 4px;
}
.detail-item.full-width {
  grid-column: span 2;
}
.detail-label {
  font-size: 12px;
  color: #999;
  font-weight: 500;
}
.detail-value {
  font-size: 14px;
  color: #333;
}
.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.text-ellipsis {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
/* 附件上传样式 */
.attachment-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.attachment-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  background: #f9fafb;
  border: 1px solid #eee;
  border-radius: 6px;
  flex-wrap: wrap;
}
.attachment-label {
  font-size: 14px;
  font-weight: 600;
  color: #555;
  min-width: 130px;
}
.attachment-controls {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}
.pending-file {
  font-size: 13px;
  color: var(--primary-color);
}
.no-file {
  font-size: 13px;
  color: #ccc;
}
.pending-count {
  font-size: 13px;
  color: var(--primary-color);
  font-weight: 500;
}
.uploaded-files {
  width: 100%;
  margin-top: 6px;
  padding-top: 6px;
  border-top: 1px dashed #ddd;
}
.uploaded-file-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 8px;
  background: #fff;
  border-radius: 4px;
  margin-bottom: 4px;
}
.uploaded-file-thumb {
  width: 32px;
  height: 32px;
  object-fit: cover;
  border-radius: 3px;
  border: 1px solid #eee;
  flex-shrink: 0;
}
.uploaded-file-name {
  font-size: 13px;
  color: #333;
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.attachment-link {
  color: var(--primary-color);
  text-decoration: none;
  font-size: 13px;
}
.attachment-link:hover {
  text-decoration: underline;
}
.detail-attachment-type {
  margin-bottom: 12px;
  padding: 8px 12px;
  background: #f9fafb;
  border-radius: 6px;
}
.detail-attachment-type-label {
  font-size: 13px;
  font-weight: 600;
  color: #555;
  margin-bottom: 6px;
}
.detail-attachment-file {
  padding: 2px 0;
}
/* 附件图片缩略图 */
.attachment-image-preview {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background 0.2s;
}
.attachment-image-preview:hover {
  background: #e6f7ff;
}
.attachment-thumb {
  width: 48px;
  height: 48px;
  object-fit: cover;
  border-radius: 4px;
  border: 1px solid #e8e8e8;
  transition: transform 0.2s;
}
.attachment-image-preview:hover .attachment-thumb {
  transform: scale(1.1);
}
.attachment-image-name {
  font-size: 13px;
  color: var(--primary-color);
}
/* 图片预览遮罩 */
.image-preview-overlay {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.85);
  z-index: 2000;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}
.image-preview-overlay.active {
  display: flex;
}
.image-preview-full {
  max-width: 90%;
  max-height: 90%;
  object-fit: contain;
  border-radius: 4px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.4);
  cursor: default;
}
.image-preview-close {
  position: absolute;
  top: 24px;
  right: 32px;
  font-size: 40px;
  color: #fff;
  cursor: pointer;
  opacity: 0.7;
  transition: opacity 0.2s;
  line-height: 1;
}
.image-preview-close:hover {
  opacity: 1;
}

/* ================= FAQ 管理 ================= */
.faq-layout { display: flex; gap: 24px; align-items: flex-start; }
.faq-manage { flex: 1; min-width: 0; }
.faq-list { display: flex; flex-direction: column; gap: 8px; }
.faq-card {
  display: flex; align-items: center; gap: 12px;
  background: #fff; border: 1px solid #e8eaed; border-radius: 8px;
  padding: 10px 14px; transition: all 0.2s;
}
.faq-card:hover { border-color: var(--primary-color); box-shadow: 0 2px 8px rgba(24,144,255,0.1); }
.faq-card.faq-draft { opacity: 0.65; }
.faq-card-num {
  width: 36px; height: 36px; border-radius: 50%;
  background: var(--primary-color); color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 16px; flex-shrink: 0;
}
.faq-card-body { flex: 1; min-width: 0; }
.faq-card-title { font-size: 14px; font-weight: 500; color: #333; }
.faq-card-preview { font-size: 12px; color: #999; margin-top: 2px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.faq-card-status { flex-shrink: 0; }
.faq-status-dot {
  display: inline-block; width: 12px; height: 12px; border-radius: 50%; cursor: pointer;
  transition: all 0.2s;
}
.dot-on { background: #52c41a; box-shadow: 0 0 0 2px rgba(82,196,26,0.2); }
.dot-off { background: #d9d9d9; }
.faq-card-actions { flex-shrink: 0; display: flex; gap: 4px; }
.faq-empty { text-align: center; padding: 40px 0; color: #999; }
/* 站点名称编辑行 */
.site-name-row { display: flex; align-items: center; gap: 10px; padding: 10px 14px; background: #f8f9fb; border-radius: 8px; margin-bottom: 14px; }
.site-name-row label { font-size: 13px; color: #555; white-space: nowrap; }
.site-name-input { width: 160px; padding: 6px 10px !important; font-size: 13px !important; }
.site-name-hint { font-size: 12px; color: #aaa; }
/* 右侧预览 */
.faq-preview-box {
  width: 380px; flex-shrink: 0;
  background: #fff; border: 1px solid #e8eaed; border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.06); overflow: hidden;
  position: sticky; top: 90px;
}
.preview-header {
  padding: 14px 16px; font-weight: 600; font-size: 14px;
  border-bottom: 1px solid #f0f0f0; background: #fafafa;
}
.preview-chat {
  padding: 16px; min-height: 320px; max-height: 420px; overflow-y: auto;
  background: #f5f6fa;
}
.msg-row { display: flex; gap: 8px; margin-bottom: 14px; align-items: flex-start; }
.msg-row.user { justify-content: flex-end; }
.msg-avatar {
  width: 32px; height: 32px; border-radius: 50%; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center; font-size: 16px;
}
.msg-avatar.user {
  background: var(--primary-color); color: #fff; font-size: 12px; font-weight: 600;
}
.msg-bubble {
  max-width: 75%; padding: 10px 14px; font-size: 13px; line-height: 1.7;
  word-break: break-word;
}
.msg-bubble.bot {
  background: #fff; border-radius: 4px 14px 14px 14px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05); color: #333;
}
.msg-bubble.user {
  background: var(--primary-color); color: #fff;
  border-radius: 14px 4px 14px 14px;
}
.preview-input-row {
  display: flex; border-top: 1px solid #f0f0f0; padding: 10px;
  background: #fff;
}
.preview-input {
  flex: 1; height: 36px; border: 1px solid #dcdfe6; border-radius: 18px;
  padding: 0 14px; font-size: 13px; outline: none;
}
.preview-input:focus { border-color: var(--primary-color); }
.preview-send-btn {
  margin-left: 8px; height: 36px; padding: 0 18px;
  background: var(--primary-color); color: #fff; border: none;
  border-radius: 18px; font-size: 13px; cursor: pointer; font-weight: 500;
}
.preview-send-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.preview-send-btn:hover:not(:disabled) { background: var(--primary-hover); }

/* 前台详情页复选框展示样式（匹配前台详情页） */
.frontend-section .info-label {
  background: #f0f2f5;
  padding: 24px;
}

.frontend-section {
  background: #fff;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.frontend-section .section-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.frontend-section .info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.frontend-section .info-item {
  display: flex;
  align-items: flex-start;
}

.frontend-section .info-item.full-width {
  grid-column: 1 / -1;
}

.frontend-section .info-label {
  min-width: 120px;
  font-weight: 500;
  color: #666;
  white-space: nowrap;
  line-height: inherit;
  font-size: inherit;
  display: inline;
}

.frontend-section .info-value {
  flex: 1;
  color: #333;
  line-height: 1.6;
  font-size: inherit;
}

.frontend-section .checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.frontend-section .checkbox-row {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
}

.frontend-section .checkbox-item {
  position: relative;
  padding-left: 20px;
  color: #666;
  font-size: inherit;
  line-height: inherit;
}

.frontend-section .checkbox-item.checked::before {
  content: "✓";
  position: absolute;
  left: 0;
  color: #1890ff;
  font-weight: bold;
}

.frontend-section .checkbox-item.other {
  min-width: 200px;
}

/* 优势描述样式（匹配前台详情页） */
.frontend-detail {
  font-family: -apple-system, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Segoe UI", "Helvetica Neue", Arial, sans-serif;
  line-height: 1.5715;
  color: rgba(0, 0, 0, 0.85);
}

.frontend-section .advantage-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.frontend-section .advantage-item {
  display: flex;
  align-items: flex-start;
}

.frontend-section .advantage-label {
  min-width: 120px;
  font-weight: 500;
  color: #666;
  white-space: nowrap;
  line-height: 1.6;
}

.frontend-section .advantage-text {
  flex: 1;
  color: #333;
  line-height: 1.6;
}

/* ===== 前台采集表样式（匹配 PublishView.vue / RequireView.vue） ===== */
.modal-body.frontend-form {
  background: #f0f2f5;
  padding: 24px;
}

.frontend-form .form-card {
  background: #fff;
  border-radius: 8px;
  padding: 28px 36px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.frontend-form .form-section-title {
  font-size: 20px;
  font-weight: bold;
  color: #333;
  margin: 30px 0 20px 0;
  padding-bottom: 10px;
  border-bottom: 2px solid #1890ff;
}

.frontend-form .form-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 20px;
}

.frontend-form .form-table th,
.frontend-form .form-table td {
  border: 2px solid #333;
  padding: 12px;
  text-align: left;
  vertical-align: top;
}

.frontend-form .form-table th {
  background: #f5f7fa;
  font-weight: bold;
  color: #333;
  width: 180px;
  vertical-align: middle;
}

.frontend-form .form-table td {
  position: relative;
}

.frontend-form .required {
  color: #ff4d4f;
  margin-right: 4px;
}

.frontend-form .table-form-item {
  margin-bottom: 0 !important;
  position: relative;
}

.frontend-form .table-form-item :deep(.el-form-item__error) {
  display: none;
}

.frontend-form .table-form-item :deep(.el-form-item__content) {
  padding: 0 !important;
  margin-left: 0 !important;
}

.frontend-form .form-table td :deep(.el-input),
.frontend-form .form-table td :deep(.el-select),
.frontend-form .form-table td :deep(.el-textarea),
.frontend-form .form-table td :deep(.el-input-number) {
  width: 100% !important;
  box-sizing: border-box;
}

.frontend-form .form-table td :deep(.el-checkbox-group),
.frontend-form .form-table td :deep(.el-radio-group) {
  flex: 1;
  min-width: 0;
  box-sizing: border-box;
}

.frontend-form .checkbox-vertical {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.frontend-form .checkbox-vertical :deep(.el-checkbox),
.frontend-form .checkbox-vertical :deep(.el-radio) {
  height: auto;
  margin-right: 0;
  margin-bottom: 4px;
}

.frontend-form .form-table td :deep(.el-checkbox-group) {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* 表单输入框内边距优化 */
.frontend-form .form-table td :deep(.el-input__wrapper) {
  padding-left: 12px;
  padding-right: 12px;
  box-shadow: 0 0 0 1px #d9d9d9 inset !important;
}

/* Element Plus 2.8+ 新版 select 使用 el-select__wrapper，不再用 el-input__wrapper */
.frontend-form .form-table td :deep(.el-select__wrapper) {
  padding-left: 12px;
  padding-right: 12px;
}

.frontend-form .form-table td :deep(.el-select__wrapper:hover) {
  box-shadow: 0 0 0 1px #4096ff inset !important;
}

.frontend-form .form-table td :deep(.el-select__wrapper.is-focused) {
  box-shadow: 0 0 0 1px #1890ff inset !important;
}

.frontend-form .form-table td :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #4096ff inset !important;
}

.frontend-form .form-table td :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #1890ff inset !important;
}

.frontend-form .form-table td :deep(.el-textarea__inner) {
  padding: 10px 12px;
  box-shadow: 0 0 0 1px #d9d9d9 inset !important;
}

.frontend-form .form-table td :deep(.el-textarea__inner:focus) {
  box-shadow: 0 0 0 1px #1890ff inset !important;
}

.frontend-form .region-selectors {
  display: flex;
  align-items: center;
  gap: 10px;
}

.frontend-form .region-selectors :deep(.el-select) {
  flex: 1;
  min-width: 250px;
}

.frontend-form .field-label {
  font-weight: bold;
  color: #333;
  margin-bottom: 8px;
}

.frontend-form .radio-with-extra {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 4px;
  line-height: 2;
}

.frontend-form .extra-input {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: #333;
  font-size: 14px;
  white-space: nowrap;
}

.frontend-form .radio-with-extra :deep(.el-input-number),
.frontend-form .radio-with-extra :deep(.el-input),
.frontend-form .radio-with-extra :deep(.el-input__wrapper),
.frontend-form .extra-input :deep(.el-input-number),
.frontend-form .extra-input :deep(.el-radio-group) {
  width: auto !important;
}

.frontend-form .inline-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.frontend-form .inline-row :deep(.el-input),
.frontend-form .inline-row :deep(.el-input__wrapper) {
  width: auto !important;
}

.frontend-form .expect-date-picker {
  width: 120px !important;
}

.frontend-form .expect-date-picker :deep(.el-input__wrapper) {
  width: 100% !important;
}

.frontend-form .industry-group {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.frontend-form .industry-category {
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  padding: 14px;
}

.frontend-form .category-title {
  font-size: 14px;
  font-weight: 600;
  color: #1890ff;
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px dashed #f0f0f0;
}

/* 下拉选择框文字样式（兼容新旧版 Element Plus） */
.frontend-form .form-table td :deep(.el-select .el-input__inner) {
  font-size: 14px;
  color: #333;
}
.frontend-form .form-table td :deep(.el-select__wrapper .el-select__selected-item) {
  font-size: 14px;
  color: #333;
}

/* 单选/复选选项间距 */
.frontend-form .form-table td :deep(.el-radio) {
  margin-right: 20px;
  margin-bottom: 8px;
  height: auto;
  line-height: 2;
}

.frontend-form .form-table td .table-form-item {
  width: 100%;
}

.frontend-form .form-table td :deep(.el-radio__label) {
  font-size: 14px;
}

.frontend-form .form-table td :deep(.el-checkbox) {
  margin-right: 20px;
  margin-bottom: 8px;
  height: auto;
}

.frontend-form .form-table td :deep(.el-checkbox__label) {
  font-size: 14px;
}

/* 行业分类内 radio 样式（匹配 RequireView） */
.frontend-form .industry-category :deep(.el-radio) {
  margin-right: 0;
  white-space: nowrap;
}

.frontend-form .industry-category :deep(.el-radio-group) {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

/* ===== Admin 详情展示样式（管理优化版） ===== */
.admin-detail {
  font-size: 14px;
  color: #333;
}

.detail-status-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 16px 32px;
  padding: 12px 16px;
  background: #fafafa;
  border: 1px solid #e8e8e8;
  border-radius: 6px;
  margin-bottom: 20px;
}

.detail-status-bar .status-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.detail-status-bar .status-label {
  font-size: 13px;
  color: #888;
  white-space: nowrap;
}

.detail-section {
  border: 1px solid #e8e8e8;
  border-radius: 6px;
  padding: 16px 20px;
  margin-bottom: 16px;
  background: #fff;
}

.detail-section-title {
  font-size: 15px;
  font-weight: 600;
  color: #333;
  margin-bottom: 14px;
  padding-bottom: 10px;
  border-bottom: 1px solid #f0f0f0;
}

.detail-grid-1col,
.detail-grid-2col,
.detail-grid-3col {
  display: grid;
  gap: 14px;
}

.detail-grid-1col {
  grid-template-columns: 1fr;
}

.detail-grid-2col {
  grid-template-columns: repeat(2, 1fr);
}

.detail-grid-3col {
  grid-template-columns: repeat(3, 1fr);
}

.detail-field {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-field.full-width {
  grid-column: 1 / -1;
}

.detail-label {
  font-size: 13px;
  font-weight: 500;
  color: #888;
}

.detail-value {
  font-size: 14px;
  color: #333;
  padding: 6px 10px;
  background: #f9f9f9;
  border: 1px solid #eee;
  border-radius: 4px;
  word-break: break-all;
  line-height: 1.5;
  min-height: 32px;
}

.detail-text {
  font-size: 14px;
  color: #333;
  padding: 10px 12px;
  background: #f9f9f9;
  border: 1px solid #eee;
  border-radius: 4px;
  word-break: break-all;
  line-height: 1.6;
  min-height: 40px;
}

@media (max-width: 768px) {
  .detail-grid-2col,
  .detail-grid-3col {
    grid-template-columns: 1fr;
  }
  .detail-status-bar {
    gap: 10px 20px;
  }
}

</style>

<!-- 非 scoped 全局样式：覆盖 Element Plus 下拉弹出框（teleport 到 body 根节点） -->
<style>
.el-select-dropdown__item {
  padding-left: 16px !important;
  padding-right: 16px !important;
  font-size: 14px;
}
.el-cascader-node__label {
  padding-left: 8px !important;
}
.el-select-dropdown__empty {
  padding: 12px 16px !important;
}
</style>