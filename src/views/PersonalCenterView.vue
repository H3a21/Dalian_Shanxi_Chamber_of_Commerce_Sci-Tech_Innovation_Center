<template>
  <div class="personal-center">
    <div v-if="isLoggedIn">
      <main class="page-section">
        <div class="personal-container">
          <!-- 页面标题 -->
          <div class="page-header">
            <h2 class="personal-title">个人中心</h2>
            <p class="personal-subtitle">管理您的个人信息和项目</p>
          </div>

          <!-- 主内容区域 -->
          <div class="main-content">
            <!-- 左侧纵向导航 -->
            <div class="sidebar">
              <el-menu
                :default-active="activeTab"
                class="vertical-menu"
                @select="handleMenuSelect"
              >
                <el-menu-item index="basic">
                  <span>基本信息</span>
                </el-menu-item>
                <el-menu-item index="todo">
                  <span>我的待办</span>
                  <span v-if="todoTotalCount > 0" class="menu-badge">{{ todoTotalCount }}</span>
                </el-menu-item>
                <!-- 普通用户菜单 -->
                <template v-if="user.role !== 'admin'">
                  <el-menu-item index="achievement">
                    <span>我的成果</span>
                  </el-menu-item>
                  <el-menu-item index="demand">
                    <span>我的需求</span>
                  </el-menu-item>
                </template>
                <!-- 管理员菜单 -->
                <template v-else>
                  <el-menu-item index="achievement-review">
                    <span>成果审核</span>
                    <span v-if="pendingAchievementCount > 0" class="menu-badge">{{ pendingAchievementCount }}</span>
                  </el-menu-item>
                  <el-menu-item index="demand-review">
                    <span>需求审核</span>
                    <span v-if="pendingRequirementCount > 0" class="menu-badge">{{ pendingRequirementCount }}</span>
                  </el-menu-item>
                </template>
              </el-menu>
            </div>

            <!-- 右侧内容区域 -->
            <div class="content-area">
              <Transition name="fade" mode="out-in">
                <!-- 基本信息 -->
                <div v-if="activeTab === 'basic'" :key="activeTab" class="tab-content basic-info">
                <div class="user-card">
                  <!-- 卡片标题 -->
                  <div class="card-title">
                    <div class="title-line"></div>
                    <span class="title-text">个人信息</span>
                  </div>

                  <!-- 顶部用户信息 -->
                  <div class="user-header">
                    <h3 class="user-name"><span class="welcome-text">欢迎您</span> {{ user.username || '未设置' }}</h3>
                    <p class="user-role">当前权限 {{ user.role }}</p>
                  </div>

                  <!-- 中间信息项 -->
                  <div class="info-section">
                    <div class="info-item">
                      <span class="info-label">用户名：</span>
                      <span class="info-value">{{ user.username }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">手机号：</span>
                      <span class="info-value">{{ user.phone }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">用户角色：</span>
                      <span class="info-value">{{ user.role }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">姓名：</span>
                      <span class="info-value">{{ user.real_name || '未认证' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">身份证号：</span>
                      <span class="info-value">{{ user.id_card || '未认证' }}</span>
                    </div>
                  </div>

                  <!-- 底部操作按钮 -->
                  <div class="action-buttons">
                    <el-button
                      :type="(!user.real_name || !user.id_card) ? 'success' : 'warning'"
                      @click="handleVerify">
                      {{ (!user.real_name || !user.id_card) ? '认证' : '修改认证' }}
                    </el-button>
                    <el-button type="primary" @click="handleEditProfile">修改信息</el-button>
                    <el-button type="warning" @click="handleChangePassword">修改密码</el-button>
                    <el-button type="danger" @click="handleLogout">退出登录</el-button>
                  </div>
                </div>

                <!-- 编辑个人信息对话框 -->
                <el-dialog
                  v-model="dialogVisible"
                  width="460px"
                  class="profile-dialog"
                  :close-on-click-modal="false"
                  top="22vh"
                  :show-close="false"
                >
                  <template #header>
                    <div class="profile-dialog-header">
                      <span class="profile-dialog-title">修改个人信息</span>
                      <button class="profile-dialog-close" @click="dialogVisible = false">×</button>
                    </div>
                  </template>
                  <div class="profile-body">
                    <div class="profile-banner">
                      <span class="profile-banner-icon">✏️</span>
                      <span class="profile-banner-text">修改您的用户名或手机号，修改手机号需要短信验证</span>
                    </div>
                    <el-form :model="editForm" class="profile-form">
                      <el-form-item label="用户名">
                        <div class="profile-input-wrapper">
                          <span class="profile-input-icon">👤</span>
                          <el-input v-model="editForm.username" placeholder="请输入用户名" class="profile-input" maxlength="50" />
                        </div>
                      </el-form-item>
                      <el-form-item label="手机号">
                        <div class="profile-input-wrapper">
                          <span class="profile-input-icon">📱</span>
                          <el-input v-model="editForm.phone" placeholder="请输入手机号" class="profile-input" maxlength="11" />
                        </div>
                      </el-form-item>
                      <el-form-item label="验证码" v-if="editForm.phone !== user.phone">
                        <div class="profile-code-row">
                          <div class="profile-input-wrapper" style="flex:1">
                            <span class="profile-input-icon">✉️</span>
                            <el-input v-model="editForm.sms_code" placeholder="请输入验证码" class="profile-input" />
                          </div>
                          <el-button
                            class="profile-code-btn"
                            :disabled="editSmsCountdown > 0"
                            @click="sendEditSms">
                            <span v-if="editSmsCountdown > 0">{{ editSmsCountdown }}s</span>
                            <span v-else>获取验证码</span>
                          </el-button>
                        </div>
                        <div class="profile-code-hint">修改手机号需要验证当前手机</div>
                      </el-form-item>
                    </el-form>
                    <div class="profile-footer">
                      <el-button class="profile-btn profile-btn-cancel" @click="dialogVisible = false">取消</el-button>
                      <el-button class="profile-btn profile-btn-primary" @click="handleSaveProfile">保存修改</el-button>
                    </div>
                  </div>
                </el-dialog>

                <!-- 认证对话框 -->
                <el-dialog
                  v-model="verifyDialogVisible"
                  width="460px"
                  class="verify-dialog"
                  :close-on-click-modal="false"
                  top="22vh"
                  :show-close="false"
                >
                  <template #header>
                    <div class="verify-dialog-header">
                      <span class="verify-dialog-title">{{ (!user.real_name || !user.id_card) ? '实名认证' : '修改认证信息' }}</span>
                      <button class="verify-dialog-close" @click="verifyDialogVisible = false">×</button>
                    </div>
                  </template>
                  <div class="verify-body">
                    <!-- 顶部提示条 -->
                    <div class="verify-banner">
                      <span class="verify-banner-icon">🛡️</span>
                      <span class="verify-banner-text">为保障平台交易安全，请完成实名认证</span>
                    </div>

                    <!-- 步骤1：验证手机号（仅修改认证时需要） -->
                    <div v-if="verifyStep === 1" class="verify-step-content">
                      <div class="verify-step-title">手机号验证</div>
                      <p class="verify-step-desc">修改认证信息需要验证您的手机号</p>
                      <el-form :model="verifyForm" class="verify-form">
                        <el-form-item label="手机号">
                          <div class="verify-input-wrapper">
                            <span class="verify-input-icon">📱</span>
                            <el-input v-model="verifyForm.phone" disabled class="verify-input" />
                          </div>
                        </el-form-item>
                        <el-form-item label="验证码">
                          <div class="verify-code-row">
                            <div class="verify-input-wrapper" style="flex:1">
                              <span class="verify-input-icon">✉️</span>
                              <el-input v-model="verifyForm.sms_code" placeholder="请输入验证码" class="verify-input" />
                            </div>
                            <el-button
                              class="verify-code-btn"
                              :disabled="smsCountdown > 0"
                              @click="sendVerifySms">
                              <span v-if="smsCountdown > 0">{{ smsCountdown }}s</span>
                              <span v-else>获取验证码</span>
                            </el-button>
                          </div>
                        </el-form-item>
                      </el-form>
                    </div>

                    <!-- 步骤2：填写认证信息 -->
                    <div v-if="verifyStep === 2" class="verify-step-content">
                      <div class="verify-step-title">填写认证信息</div>
                      <p class="verify-step-desc">请如实填写以下信息，提交后无法频繁修改</p>
                      <el-form :model="verifyForm" class="verify-form">
                        <el-form-item label="真实姓名">
                          <div class="verify-input-wrapper">
                            <span class="verify-input-icon">👤</span>
                            <el-input
                              v-model="verifyForm.real_name"
                              placeholder="请输入您的真实姓名"
                              class="verify-input"
                              maxlength="30"
                            />
                          </div>
                        </el-form-item>
                        <el-form-item label="手机号码">
                          <div class="verify-input-wrapper">
                            <span class="verify-input-icon">📱</span>
                            <el-input v-model="verifyForm.phone" disabled class="verify-input" />
                          </div>
                        </el-form-item>
                        <el-form-item label="身份证号">
                          <div class="verify-input-wrapper">
                            <span class="verify-input-icon">🪪</span>
                            <el-input
                              v-model="verifyForm.id_card"
                              placeholder="请输入您的身份证号码"
                              class="verify-input"
                              maxlength="18"
                            />
                          </div>
                        </el-form-item>
                        <el-form-item v-if="user.real_name && user.id_card" label="验证码">
                          <div class="verify-code-row">
                            <div class="verify-input-wrapper" style="flex:1">
                              <span class="verify-input-icon">✉️</span>
                              <el-input v-model="verifyForm.sms_code" placeholder="请输入验证码" class="verify-input" />
                            </div>
                            <el-button
                              class="verify-code-btn"
                              :disabled="smsCountdown > 0"
                              @click="sendVerifySms">
                              <span v-if="smsCountdown > 0">{{ smsCountdown }}s</span>
                              <span v-else>获取验证码</span>
                            </el-button>
                          </div>
                        </el-form-item>
                      </el-form>
                    </div>

                    <!-- 按钮区域 -->
                    <div class="verify-footer">
                      <el-button class="verify-btn verify-btn-cancel" @click="verifyDialogVisible = false">取消</el-button>
                      <el-button
                        v-if="verifyStep === 1"
                        class="verify-btn verify-btn-primary"
                        @click="verifySmsCode">
                        下一步
                      </el-button>
                      <el-button
                        v-if="verifyStep === 2"
                        class="verify-btn verify-btn-primary"
                        @click="submitVerification">
                        <span>✓</span> 提交认证
                      </el-button>
                    </div>
                  </div>
                </el-dialog>

                <!-- 修改密码对话框 -->
                <el-dialog
                  v-model="passwordDialogVisible"
                  width="460px"
                  class="profile-dialog"
                  :close-on-click-modal="false"
                  top="22vh"
                  :show-close="false"
                >
                  <template #header>
                    <div class="profile-dialog-header">
                      <span class="profile-dialog-title">修改密码</span>
                      <button class="profile-dialog-close" @click="passwordDialogVisible = false">×</button>
                    </div>
                  </template>
                  <div class="profile-body">
                    <div class="profile-banner profile-banner-warn">
                      <span class="profile-banner-icon">🔒</span>
                      <span class="profile-banner-text">修改密码后需重新登录，请牢记新密码</span>
                    </div>
                    <el-form :model="passwordForm" class="profile-form">
                      <el-form-item label="手机号">
                        <div class="profile-input-wrapper">
                          <span class="profile-input-icon">📱</span>
                          <el-input v-model="passwordForm.phone" disabled class="profile-input" />
                        </div>
                      </el-form-item>
                      <el-form-item label="验证码">
                        <div class="profile-code-row">
                          <div class="profile-input-wrapper" style="flex:1">
                            <span class="profile-input-icon">✉️</span>
                            <el-input v-model="passwordForm.sms_code" placeholder="请输入验证码" class="profile-input" />
                          </div>
                          <el-button
                            class="profile-code-btn"
                            :disabled="passwordSmsCountdown > 0"
                            @click="sendPasswordSms">
                            <span v-if="passwordSmsCountdown > 0">{{ passwordSmsCountdown }}s</span>
                            <span v-else>获取验证码</span>
                          </el-button>
                        </div>
                      </el-form-item>
                      <el-form-item label="新密码">
                        <div class="profile-input-wrapper">
                          <span class="profile-input-icon">🔑</span>
                          <el-input v-model="passwordForm.new_password" type="password" placeholder="请输入新密码（至少6位）" class="profile-input" show-password />
                        </div>
                      </el-form-item>
                      <el-form-item label="确认密码">
                        <div class="profile-input-wrapper">
                          <span class="profile-input-icon">✓</span>
                          <el-input v-model="passwordForm.confirm_password" type="password" placeholder="请再次输入新密码" class="profile-input" show-password />
                        </div>
                      </el-form-item>
                    </el-form>
                    <div class="profile-footer">
                      <el-button class="profile-btn profile-btn-cancel" @click="passwordDialogVisible = false">取消</el-button>
                      <el-button class="profile-btn profile-btn-primary" @click="submitChangePassword">确定修改</el-button>
                    </div>
                  </div>
                </el-dialog>
              </div>

                <!-- 其他标签页 -->
                <div v-else :key="activeTab" class="tab-content">
                <div class="list-header">
                  <h3>{{ tabTitles[activeTab] }}</h3>
                  <el-button type="primary" size="small">{{ tabActions[activeTab] }}</el-button>
                </div>

                <!-- 成果审核特殊处理 -->
                <template v-if="activeTab === 'achievement-review'">
                  <div v-if="reviewPagination.loading" class="loading-state">
                    <span>加载中...</span>
                  </div>
                  <el-empty v-else-if="!dataLists[activeTab] || !dataLists[activeTab].length" :description="emptyTexts[activeTab]" />
                  <div v-else class="flat-review-list">
                    <!-- 扁平化列表 -->
                    <div
                      v-for="item in dataLists[activeTab]"
                      :key="item.id"
                      class="flat-review-item"
                      @click="openDetailDialog(item)"
                    >
                      <div class="flat-item-header">
                        <div class="flat-item-title">{{ item.achievement_name || '未命名成果' }}</div>
                        <span class="flat-item-status" :class="getStatusClass(item.status)">
                          {{ getStatusText(item.status) }}
                        </span>
                      </div>
                      <div class="flat-item-content">
                        <div class="flat-item-row">
                          <span class="flat-item-label">成果编号：</span>
                          <span class="flat-item-value">{{ item.achievement_code || '未设置' }}</span>
                        </div>
                        <div class="flat-item-row">
                          <span class="flat-item-label">持有人：</span>
                          <span class="flat-item-value">{{ item.owner || '未设置' }}</span>
                        </div>
                        <div class="flat-item-row">
                          <span class="flat-item-label">提交时间：</span>
                          <span class="flat-item-value">{{ formatDate(item.created_at) }}</span>
                        </div>
                      </div>
                      <div class="flat-item-actions">
                        <el-button
                          size="small"
                          type="text"
                          @click.stop="handleReview(item.id, 'approved')"
                          :disabled="item.status !== 'pending'"
                        >
                          通过
                        </el-button>
                        <el-button
                          size="small"
                          type="text"
                          @click.stop="handleReview(item.id, 'rejected')"
                          :disabled="item.status !== 'pending'"
                        >
                          拒绝
                        </el-button>
                      </div>
                    </div>

                    <!-- 分页组件 -->
                    <div v-if="reviewPagination.total_pages > 1" class="pagination-container">
                      <el-pagination
                        v-model:current-page="reviewPagination.page"
                        :page-size="reviewPagination.page_size"
                        :total="reviewPagination.total"
                        layout="prev, pager, next, jumper"
                        @current-change="handlePageChange"
                      />
                    </div>
                  </div>
                </template>

                <!-- 需求审核特殊处理 -->
                <template v-else-if="activeTab === 'demand-review'">
                  <div v-if="demandReviewPagination.loading" class="loading-state">
                    <span>加载中...</span>
                  </div>
                  <el-empty v-else-if="!dataLists[activeTab] || !dataLists[activeTab].length" :description="emptyTexts[activeTab]" />
                  <div v-else class="flat-review-list">
                    <!-- 扁平化列表 -->
                    <div
                      v-for="item in dataLists[activeTab]"
                      :key="item.id"
                      class="flat-review-item"
                      @click="openDemandDetailDialog(item)"
                    >
                      <div class="flat-item-header">
                        <div class="flat-item-title">{{ item.demand_name || '未命名需求' }}</div>
                        <span class="flat-item-status" :class="getStatusClass(item.status)">
                          {{ getStatusText(item.status) }}
                        </span>
                      </div>
                      <div class="flat-item-content">
                        <div class="flat-item-row">
                          <span class="flat-item-label">企业名称：</span>
                          <span class="flat-item-value">{{ item.company_name || '未设置' }}</span>
                        </div>
                        <div class="flat-item-row">
                          <span class="flat-item-label">需求编号：</span>
                          <span class="flat-item-value">{{ item.demand_code || '未设置' }}</span>
                        </div>
                        <div class="flat-item-row">
                          <span class="flat-item-label">所属地区：</span>
                          <span class="flat-item-value">{{ formatRegion(item.region) || '未设置' }}</span>
                        </div>
                        <div class="flat-item-row">
                          <span class="flat-item-label">技术领域：</span>
                          <span class="flat-item-value">{{ formatTechFields(item.tech_fields, item.tech_fields_other) || '未设置' }}</span>
                        </div>
                        <div class="flat-item-row">
                          <span class="flat-item-label">需求类型：</span>
                          <span class="flat-item-value">{{ formatDemandTypes(item.demand_types, item.demand_types_other) || '未设置' }}</span>
                        </div>
                        <div class="flat-item-row">
                          <span class="flat-item-label">项目预算：</span>
                          <span class="flat-item-value">{{ formatBudget(item.description?.budget) || '未设置' }}</span>
                        </div>
                        <div class="flat-item-row">
                          <span class="flat-item-label">提交时间：</span>
                          <span class="flat-item-value">{{ formatDate(item.created_at) }}</span>
                        </div>
                      </div>
                      <div class="flat-item-actions">
                        <el-button
                          size="small"
                          type="text"
                          @click.stop="handleDemandReview(item.id, 'approved')"
                          :disabled="item.status !== 'pending'"
                        >
                          通过
                        </el-button>
                        <el-button
                          size="small"
                          type="text"
                          @click.stop="handleDemandReview(item.id, 'rejected')"
                          :disabled="item.status !== 'pending'"
                        >
                          拒绝
                        </el-button>
                      </div>
                    </div>

                    <!-- 分页组件 -->
                    <div v-if="demandReviewPagination.total_pages > 1" class="pagination-container">
                      <el-pagination
                        v-model:current-page="demandReviewPagination.page"
                        :page-size="demandReviewPagination.page_size"
                        :total="demandReviewPagination.total"
                        layout="prev, pager, next, jumper"
                        @current-change="handleDemandPageChange"
                      />
                    </div>
                  </div>
                </template>

                <!-- 我的成果特殊处理 -->
                <template v-else-if="activeTab === 'achievement'">
                  <div class="todo-sub-tabs">
                    <button
                      :class="['todo-sub-tab', { active: achievementSubTab === 'pending' }]"
                      @click="achievementSubTab = 'pending'; userAchievementPagination.page = 1; fetchUserAchievements()"
                    >
                      待审核
                      <span v-if="achievementPendingCount > 0" class="sub-tab-count">{{ achievementPendingCount }}</span>
                    </button>
                    <button
                      :class="['todo-sub-tab', { active: achievementSubTab === 'approved' }]"
                      @click="achievementSubTab = 'approved'; userAchievementPagination.page = 1; fetchUserAchievements()"
                    >
                      已通过
                      <span v-if="achievementApprovedCount > 0" class="sub-tab-count">{{ achievementApprovedCount }}</span>
                    </button>
                  </div>
                  <div v-if="userAchievementPagination.loading" class="loading-state">
                    <span>加载中...</span>
                  </div>
                  <el-empty v-else-if="!dataLists[activeTab] || !dataLists[activeTab].length" :description="emptyTexts[activeTab]" />
                  <div v-else class="flat-review-list">
                    <!-- 扁平化列表 -->
                    <div
                      v-for="item in dataLists[activeTab]"
                      :key="item.id"
                      class="flat-review-item"
                      @click="openDetailDialog(item)"
                    >
                      <div class="flat-item-header">
                        <div class="flat-item-title">{{ item.achievement_name || '未命名成果' }}</div>
                        <span class="flat-item-status" :class="getStatusClass(item.status)">
                          {{ getStatusText(item.status) }}
                        </span>
                      </div>
                      <div class="flat-item-content">
                        <div class="flat-item-row">
                          <span class="flat-item-label">成果编号：</span>
                          <span class="flat-item-value">{{ item.achievement_code || '未设置' }}</span>
                        </div>
                        <div class="flat-item-row">
                          <span class="flat-item-label">持有人：</span>
                          <span class="flat-item-value">{{ item.owner || '未设置' }}</span>
                        </div>
                        <div class="flat-item-row">
                          <span class="flat-item-label">技术领域：</span>
                          <span class="flat-item-value">{{ formatTechFields(item.tech_fields, item.tech_fields_other) || '未设置' }}</span>
                        </div>
                        <div class="flat-item-row">
                          <span class="flat-item-label">技术成熟度：</span>
                          <span class="flat-item-value">{{ item.tech_maturity || '未设置' }}</span>
                        </div>
                        <div class="flat-item-row">
                          <span class="flat-item-label">提交时间：</span>
                          <span class="flat-item-value">{{ formatDate(item.created_at) }}</span>
                        </div>
                      </div>
                      <div class="flat-item-actions">
                        <el-button
                          size="small"
                          type="text"
                          @click.stop="openDetailDialog(item)"
                        >
                          查看详情
                        </el-button>
                        <el-button
                          v-if="item.status === 'rejected'"
                          size="small"
                          type="warning"
                          @click.stop="openAchievementEditDialog(item)"
                        >
                          编辑修改
                        </el-button>
                      </div>
                      <div v-if="item.status === 'rejected' && item.reject_reason" class="reject-reason">
                        <el-icon style="margin-right:4px;"><WarningFilled /></el-icon>驳回原因：{{ item.reject_reason }}
                      </div>
                    </div>

                    <!-- 分页组件 -->
                    <div v-if="userAchievementPagination.total_pages > 1" class="pagination-container">
                      <el-pagination
                        v-model:current-page="userAchievementPagination.page"
                        :page-size="userAchievementPagination.page_size"
                        :total="userAchievementPagination.total"
                        layout="prev, pager, next, jumper"
                        @current-change="handleUserAchievementPageChange"
                      />
                    </div>
                  </div>
                </template>

                <!-- 我的需求特殊处理 -->
                <template v-else-if="activeTab === 'demand'">
                  <div class="todo-sub-tabs">
                    <button
                      :class="['todo-sub-tab', { active: demandSubTab === 'pending' }]"
                      @click="demandSubTab = 'pending'; userRequirementPagination.page = 1; fetchUserRequirements()"
                    >
                      待审核
                      <span v-if="requirementPendingCount > 0" class="sub-tab-count">{{ requirementPendingCount }}</span>
                    </button>
                    <button
                      :class="['todo-sub-tab', { active: demandSubTab === 'approved' }]"
                      @click="demandSubTab = 'approved'; userRequirementPagination.page = 1; fetchUserRequirements()"
                    >
                      已通过
                      <span v-if="requirementApprovedCount > 0" class="sub-tab-count">{{ requirementApprovedCount }}</span>
                    </button>
                  </div>
                  <div v-if="userRequirementPagination.loading" class="loading-state">
                    <span>加载中...</span>
                  </div>
                  <el-empty v-else-if="!dataLists[activeTab] || !dataLists[activeTab].length" :description="emptyTexts[activeTab]" />
                  <div v-else class="flat-review-list">
                    <!-- 扁平化列表 -->
                    <div
                      v-for="item in dataLists[activeTab]"
                      :key="item.id"
                      class="flat-review-item"
                      @click="openDemandDetailDialog(item)"
                    >
                      <div class="flat-item-header">
                        <div class="flat-item-title">{{ item.demand_name || '未命名需求' }}</div>
                        <span class="flat-item-status" :class="getStatusClass(item.status)">
                          {{ getStatusText(item.status) }}
                        </span>
                      </div>
                      <div class="flat-item-content">
                        <div class="flat-item-row">
                          <span class="flat-item-label">企业名称：</span>
                          <span class="flat-item-value">{{ item.company_name || '未设置' }}</span>
                        </div>
                        <div class="flat-item-row">
                          <span class="flat-item-label">需求编号：</span>
                          <span class="flat-item-value">{{ item.demand_code || '未设置' }}</span>
                        </div>
                        <div class="flat-item-row">
                          <span class="flat-item-label">所属地区：</span>
                          <span class="flat-item-value">{{ formatRegion(item.region) || '未设置' }}</span>
                        </div>
                        <div class="flat-item-row">
                          <span class="flat-item-label">技术领域：</span>
                          <span class="flat-item-value">{{ formatTechFields(item.tech_fields, item.tech_fields_other) || '未设置' }}</span>
                        </div>
                        <div class="flat-item-row">
                          <span class="flat-item-label">需求类型：</span>
                          <span class="flat-item-value">{{ formatDemandTypes(item.demand_types, item.demand_types_other) || '未设置' }}</span>
                        </div>
                        <div class="flat-item-row">
                          <span class="flat-item-label">项目预算：</span>
                          <span class="flat-item-value">{{ formatBudget(item.description?.budget) || '未设置' }}</span>
                        </div>
                        <div class="flat-item-row">
                          <span class="flat-item-label">提交时间：</span>
                          <span class="flat-item-value">{{ formatDate(item.created_at) }}</span>
                        </div>
                      </div>
                      <div class="flat-item-actions">
                        <el-button
                          size="small"
                          type="text"
                          @click.stop="openDemandDetailDialog(item)"
                        >
                          查看详情
                        </el-button>
                        <el-button
                          v-if="item.status === 'rejected'"
                          size="small"
                          type="warning"
                          @click.stop="openDemandEditDialog(item)"
                        >
                          编辑修改
                        </el-button>
                      </div>
                      <div v-if="item.status === 'rejected' && item.reject_reason" class="reject-reason">
                        <el-icon style="margin-right:4px;"><WarningFilled /></el-icon>驳回原因：{{ item.reject_reason }}
                      </div>
                    </div>

                    <!-- 分页组件 -->
                    <div v-if="userRequirementPagination.total_pages > 1" class="pagination-container">
                      <el-pagination
                        v-model:current-page="userRequirementPagination.page"
                        :page-size="userRequirementPagination.page_size"
                        :total="userRequirementPagination.total"
                        layout="prev, pager, next, jumper"
                        @current-change="handleUserRequirementPageChange"
                      />
                    </div>
                  </div>
                </template>

                <!-- 我的待办 - 被驳成果/需求 -->
                <template v-else-if="activeTab === 'todo'">
                  <div class="todo-sub-tabs">
                    <button
                      :class="['todo-sub-tab', { active: todoSubTab === 'rejected-achievement' }]"
                      @click="todoSubTab = 'rejected-achievement'; rejectedAchievementPagination.page = 1; fetchRejectedAchievements()"
                    >
                      被驳成果
                      <span v-if="rejectedAchievementTotal > 0" class="sub-tab-count">{{ rejectedAchievementTotal }}</span>
                    </button>
                    <button
                      :class="['todo-sub-tab', { active: todoSubTab === 'rejected-demand' }]"
                      @click="todoSubTab = 'rejected-demand'; rejectedRequirementPagination.page = 1; fetchRejectedRequirements()"
                    >
                      被驳需求
                      <span v-if="rejectedRequirementTotal > 0" class="sub-tab-count">{{ rejectedRequirementTotal }}</span>
                    </button>
                  </div>

                  <!-- 被驳成果列表 -->
                  <template v-if="todoSubTab === 'rejected-achievement'">
                    <div v-if="rejectedAchievementPagination.loading" class="loading-state">
                      <span>加载中...</span>
                    </div>
                    <el-empty v-else-if="!rejectedAchievementList.length" description="暂无被驳回的成果" />
                    <div v-else class="flat-review-list">
                      <div
                        v-for="item in rejectedAchievementList"
                        :key="item.id"
                        class="flat-review-item"
                        @click="openDetailDialog(item)"
                      >
                        <div class="flat-item-header">
                          <div class="flat-item-title">{{ item.achievement_name || '未命名成果' }}</div>
                          <span class="flat-item-status rejected-status">已拒绝</span>
                        </div>
                        <div class="flat-item-content">
                          <div class="flat-item-row">
                            <span class="flat-item-label">成果编号：</span>
                            <span class="flat-item-value">{{ item.achievement_code || '未设置' }}</span>
                          </div>
                          <div class="flat-item-row">
                            <span class="flat-item-label">持有人：</span>
                            <span class="flat-item-value">{{ item.owner || '未设置' }}</span>
                          </div>
                          <div class="flat-item-row">
                            <span class="flat-item-label">提交时间：</span>
                            <span class="flat-item-value">{{ formatDate(item.created_at) }}</span>
                          </div>
                        </div>
                        <div v-if="item.reject_reason" class="reject-reason">
                          <el-icon style="margin-right:4px;"><WarningFilled /></el-icon>驳回原因：{{ item.reject_reason }}
                        </div>
                        <div class="flat-item-actions">
                          <el-button size="small" type="text" @click.stop="openDetailDialog(item)">查看详情</el-button>
                          <el-button size="small" type="warning" @click.stop="openAchievementEditDialog(item)">编辑修改</el-button>
                        </div>
                      </div>
                      <div v-if="rejectedAchievementPagination.total_pages > 1" class="pagination-container">
                        <el-pagination
                          v-model:current-page="rejectedAchievementPagination.page"
                          :page-size="rejectedAchievementPagination.page_size"
                          :total="rejectedAchievementPagination.total"
                          layout="prev, pager, next, jumper"
                          @current-change="handleRejectedAchievementPageChange"
                        />
                      </div>
                    </div>
                  </template>

                  <!-- 被驳需求列表 -->
                  <template v-if="todoSubTab === 'rejected-demand'">
                    <div v-if="rejectedRequirementPagination.loading" class="loading-state">
                      <span>加载中...</span>
                    </div>
                    <el-empty v-else-if="!rejectedRequirementList.length" description="暂无被驳回的需求" />
                    <div v-else class="flat-review-list">
                      <div
                        v-for="item in rejectedRequirementList"
                        :key="item.id"
                        class="flat-review-item"
                        @click="openDemandDetailDialog(item)"
                      >
                        <div class="flat-item-header">
                          <div class="flat-item-title">{{ item.demand_name || '未命名需求' }}</div>
                          <span class="flat-item-status rejected-status">已拒绝</span>
                        </div>
                        <div class="flat-item-content">
                          <div class="flat-item-row">
                            <span class="flat-item-label">企业名称：</span>
                            <span class="flat-item-value">{{ item.company_name || '未设置' }}</span>
                          </div>
                          <div class="flat-item-row">
                            <span class="flat-item-label">需求编号：</span>
                            <span class="flat-item-value">{{ item.demand_code || '未设置' }}</span>
                          </div>
                          <div class="flat-item-row">
                            <span class="flat-item-label">技术领域：</span>
                            <span class="flat-item-value">{{ formatTechFields(item.tech_fields, item.tech_fields_other) || '未设置' }}</span>
                          </div>
                          <div class="flat-item-row">
                            <span class="flat-item-label">提交时间：</span>
                            <span class="flat-item-value">{{ formatDate(item.created_at) }}</span>
                          </div>
                        </div>
                        <div v-if="item.reject_reason" class="reject-reason">
                          <el-icon style="margin-right:4px;"><WarningFilled /></el-icon>驳回原因：{{ item.reject_reason }}
                        </div>
                        <div class="flat-item-actions">
                          <el-button size="small" type="text" @click.stop="openDemandDetailDialog(item)">查看详情</el-button>
                          <el-button size="small" type="warning" @click.stop="openDemandEditDialog(item)">编辑修改</el-button>
                        </div>
                      </div>
                      <div v-if="rejectedRequirementPagination.total_pages > 1" class="pagination-container">
                        <el-pagination
                          v-model:current-page="rejectedRequirementPagination.page"
                          :page-size="rejectedRequirementPagination.page_size"
                          :total="rejectedRequirementPagination.total"
                          layout="prev, pager, next, jumper"
                          @current-change="handleRejectedRequirementPageChange"
                        />
                      </div>
                    </div>
                  </template>
                </template>

                <!-- 其他标签页的通用显示（cooperation等） -->
                <template v-else>
                  <el-empty v-if="!dataLists[activeTab] || !dataLists[activeTab].length" :description="emptyTexts[activeTab]" />
                  <div v-else class="card-grid">
                    <div
                      v-for="item in (dataLists[activeTab] || [])"
                      :key="item.id"
                      class="content-card"
                    >
                      <div class="card-header">
                        <h4 class="card-title">{{ item.title || item.project }}</h4>
                        <span :class="getCardStatusClass(activeTab)">{{ item.status || item.type }}</span>
                      </div>
                      <div class="card-meta">
                        <span v-if="item.deadline">截止时间：{{ item.deadline }}</span>
                        <span v-else-if="item.date">发布日期：{{ item.date }}</span>
                        <span v-if="item.partner">合作方：{{ item.partner }}</span>
                        <span v-if="item.date && item.partner">开始日期：{{ item.date }}</span>
                      </div>
                      <div class="card-actions">
                        <el-button size="small" type="primary">{{ getCardActionText(activeTab) }}</el-button>
                      </div>
                    </div>
                  </div>
                </template>
              </div>
              </Transition>
            </div>
          </div>
        </div>
      </main>

      <!-- 成果详情弹窗 -->
      <div class="modal" :class="{ active: detailDialogVisible }" @click.self="detailDialogVisible = false">
        <div class="modal-content modal-lg">
          <div class="modal-header">
            <div class="modal-title">{{ user.role === 'admin' ? '成果审核详情' : '成果详情' }}</div>
            <button class="modal-close" @click="detailDialogVisible = false">&times;</button>
          </div>
          <div class="modal-body">
            <div v-if="detailLoading" style="text-align:center;padding:20px;color:#999;">加载中...</div>
            <div v-else-if="achievementDetail">
              <div class="detail-section">
                <div class="detail-section-title">基本信息</div>
                <div class="detail-grid">
                  <div class="detail-item">
                    <span class="detail-label">成果名称</span>
                    <span class="detail-value" style="font-weight:500;color:#1890ff;">{{ achievementDetail.achievement_name || '-' }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">成果编号</span>
                    <span class="detail-value">{{ achievementDetail.achievement_code || '-' }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">企业名称/持有人</span>
                    <span class="detail-value">{{ achievementDetail.owner || '-' }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">所属地区</span>
                    <span class="detail-value">{{ formatRegion(achievementDetail.region) || '-' }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">技术领域</span>
                    <span class="detail-value">{{ formatTechFields(achievementDetail.tech_fields, achievementDetail.tech_fields_other) || '-' }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">技术成熟度</span>
                    <span class="detail-value">{{ achievementDetail.tech_maturity || '-' }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">拟转化方式</span>
                    <span class="detail-value">{{ formatTransferMethods(achievementDetail.transfer_methods, achievementDetail.transfer_methods_other) || '-' }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">提交时间</span>
                    <span class="detail-value">{{ formatDate(achievementDetail.created_at) || '-' }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">当前状态</span>
                    <span class="detail-value"><span :class="'status-badge status-' + achievementDetail.status">{{ getStatusText(achievementDetail.status) }}</span></span>
                  </div>
                </div>
              </div>
              <div class="detail-section">
                <div class="detail-section-title">描述信息</div>
                <div class="detail-grid">
                  <div class="detail-item full-width">
                    <span class="detail-label">成果摘要</span>
                    <span class="detail-value">{{ achievementDetail.description?.summary || '-' }}</span>
                  </div>
                  <div class="detail-item full-width">
                    <span class="detail-label">创新性</span>
                    <span class="detail-value">{{ achievementDetail.description?.innovation_level || '-' }}</span>
                  </div>
                  <div class="detail-item full-width">
                    <span class="detail-label">与现有技术相比的优势</span>
                    <span class="detail-value">{{ achievementDetail.description?.advantages || '-' }}</span>
                  </div>
                  <div class="detail-item full-width">
                    <span class="detail-label">核心技术指标</span>
                    <span class="detail-value">{{ achievementDetail.description?.core_indicators || '-' }}</span>
                  </div>
                  <div class="detail-item full-width">
                    <span class="detail-label">获得的知识产权</span>
                    <span class="detail-value">{{ achievementDetail.description?.intellectual_property || '-' }}</span>
                  </div>
                </div>
              </div>
              <div class="detail-section">
                <div class="detail-section-title">转化期望</div>
                <div class="detail-grid">
                  <div class="detail-item">
                    <span class="detail-label">合作方式偏好及财务预期</span>
                    <span class="detail-value" style="color:#faad14;font-weight:500;">{{ formatTransferPreference(achievementDetail.transfer_preference) || '-' }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">期望完成转化时间</span>
                    <span class="detail-value">{{ achievementDetail.expected_completion_date || '-' }}</span>
                  </div>
                </div>
              </div>
              <!-- 拒绝理由输入（管理员审核拒绝时显示） -->
              <div v-if="user.role === 'admin' && currentAchievement?.status === 'pending'" class="detail-section" style="border:1px solid #e6a23c;border-radius:4px;padding:12px;">
                <div class="detail-section-title">拒绝理由</div>
                <el-input
                  v-model="rejectReason"
                  type="textarea"
                  :rows="3"
                  placeholder="填写拒绝理由（拒绝审核时必须填写）"
                  maxlength="255"
                  show-word-limit
                />
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-default" @click="detailDialogVisible = false">关闭</button>
            <template v-if="user.role === 'admin'">
              <button class="btn btn-primary" @click="handleDetailReview('approved')" :disabled="!currentAchievement || currentAchievement.status !== 'pending'">通过审核</button>
              <button class="btn btn-error" @click="handleDetailReview('rejected')" :disabled="!currentAchievement || currentAchievement.status !== 'pending'">拒绝审核</button>
            </template>
          </div>
        </div>
      </div>

      <!-- 需求详情弹窗 -->
      <div class="modal" :class="{ active: demandDetailDialogVisible }" @click.self="demandDetailDialogVisible = false">
        <div class="modal-content modal-lg">
          <div class="modal-header">
            <div class="modal-title">{{ user.role === 'admin' ? '需求审核详情' : '需求详情' }}</div>
            <button class="modal-close" @click="demandDetailDialogVisible = false">&times;</button>
          </div>
          <div class="modal-body">
            <div v-if="demandDetailLoading" style="text-align:center;padding:20px;color:#999;">加载中...</div>
            <div v-else-if="requirementDetail">
              <div class="detail-section">
                <div class="detail-section-title">基本信息</div>
                <div class="detail-grid">
                  <div class="detail-item">
                    <span class="detail-label">需求名称</span>
                    <span class="detail-value" style="font-weight:500;color:#1890ff;">{{ requirementDetail.demand_name || '-' }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">需求编号</span>
                    <span class="detail-value">{{ requirementDetail.demand_code || '-' }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">企业名称</span>
                    <span class="detail-value">{{ requirementDetail.company_name || '-' }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">所属地区</span>
                    <span class="detail-value">{{ formatRegion(requirementDetail.region) || '-' }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">技术领域</span>
                    <span class="detail-value">{{ formatTechFields(requirementDetail.tech_fields, requirementDetail.tech_fields_other) || '-' }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">需求类型</span>
                    <span class="detail-value">{{ formatDemandTypes(requirementDetail.demand_types, requirementDetail.demand_types_other) || '-' }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">提交时间</span>
                    <span class="detail-value">{{ formatDate(requirementDetail.created_at) || '-' }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">当前状态</span>
                    <span class="detail-value"><span :class="'status-badge status-' + requirementDetail.status">{{ getStatusText(requirementDetail.status) }}</span></span>
                  </div>
                </div>
              </div>
              <div class="detail-section">
                <div class="detail-section-title">描述信息</div>
                <div class="detail-grid">
                  <div class="detail-item full-width">
                    <span class="detail-label">项目预算(万元)</span>
                    <span class="detail-value">{{ formatBudget(requirementDetail.description?.budget) || '-' }}</span>
                  </div>
                  <div class="detail-item full-width">
                    <span class="detail-label">需求概述</span>
                    <span class="detail-value">{{ requirementDetail.description?.overview || '-' }}</span>
                  </div>
                  <div class="detail-item full-width">
                    <span class="detail-label">期望解决的问题</span>
                    <span class="detail-value">{{ requirementDetail.description?.target_problems || '-' }}</span>
                  </div>
                </div>
              </div>
              <!-- 拒绝理由输入（管理员审核拒绝时显示） -->
              <div v-if="user.role === 'admin' && currentRequirement?.status === 'pending'" class="detail-section" style="border:1px solid #e6a23c;border-radius:4px;padding:12px;">
                <div class="detail-section-title">拒绝理由</div>
                <el-input
                  v-model="demandRejectReason"
                  type="textarea"
                  :rows="3"
                  placeholder="填写拒绝理由（拒绝审核时必须填写）"
                  maxlength="255"
                  show-word-limit
                />
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-default" @click="demandDetailDialogVisible = false">关闭</button>
            <template v-if="user.role === 'admin'">
              <button class="btn btn-primary" @click="handleDemandDetailReview('approved')" :disabled="!currentRequirement || currentRequirement.status !== 'pending'">通过审核</button>
              <button class="btn btn-error" @click="handleDemandDetailReview('rejected')" :disabled="!currentRequirement || currentRequirement.status !== 'pending'">拒绝审核</button>
            </template>
          </div>
        </div>
      </div>
      <!-- 成果编辑弹窗 -->
      <div class="modal" :class="{ active: achievementEditVisible }" @click.self="achievementEditVisible = false">
        <div class="modal-content modal-lg">
          <div class="modal-header">
            <div class="modal-title">编辑成果</div>
            <button class="modal-close" @click="achievementEditVisible = false">&times;</button>
          </div>
          <div class="modal-body">
            <div v-if="achievementEditLoading" style="text-align:center;padding:20px;color:#999;">加载中...</div>
            <div v-else-if="achievementEdit">
              <div class="detail-section" style="border:1px solid #e6a23c;border-radius:4px;padding:12px;margin-bottom:16px;background:#fffbe6;">
                <div class="detail-section-title" style="color:#e6a23c;">驳回原因</div>
                <p style="color:#e6a23c;font-size:14px;">{{ achievementEdit.reject_reason || '无' }}</p>
              </div>
              <el-form label-position="left" label-width="120px" class="edit-form">
                <div class="detail-section">
                  <div class="detail-section-title">一、成果基本信息</div>
                  <table class="form-table">
                    <tbody>
                      <tr>
                        <th><span class="required">*</span> 成果名称</th>
                        <td>
                          <el-form-item class="table-form-item">
                            <el-input v-model="achievementEditForm.achievement_name" placeholder="请输入完整成果名称" />
                          </el-form-item>
                        </td>
                      </tr>
                      <tr>
                        <th><span class="required">*</span> 成果持有人</th>
                        <td>
                          <el-form-item class="table-form-item">
                            <el-input v-model="achievementEditForm.owner" placeholder="高校/科研院所/企业/团队负责人" />
                          </el-form-item>
                        </td>
                      </tr>
                      <tr>
                        <th><span class="required">*</span> 所属地区</th>
                        <td>
                          <el-form-item class="table-form-item">
                            <div class="region-selectors">
                              <el-select v-model="achievementEditForm.province" placeholder="选择省份">
                                <el-option v-for="province in provinces" :key="province" :label="province" :value="province" />
                              </el-select>
                              <el-select v-model="achievementEditForm.city" :placeholder="achievementIsMunicipality ? '选择区' : '选择城市'" :disabled="!achievementEditForm.province">
                                <el-option v-for="city in achievementCities" :key="city" :label="city" :value="city" />
                              </el-select>
                            </div>
                          </el-form-item>
                        </td>
                      </tr>
                      <tr>
                        <th><span class="required">*</span> 技术领域</th>
                        <td>
                          <el-form-item class="table-form-item">
                            <el-select v-model="achievementEditForm.techField" placeholder="--请选择--">
                              <el-option v-for="item in techFieldOptions" :key="item" :label="item" :value="item" />
                            </el-select>
                          </el-form-item>
                          <el-form-item v-if="achievementEditForm.techField === '其他'" class="table-form-item" style="margin-top:8px;">
                            <el-input v-model="achievementEditForm.techFieldOther" placeholder="请填写具体领域" />
                          </el-form-item>
                        </td>
                      </tr>
                      <tr>
                        <th><span class="required">*</span> 技术成熟度</th>
                        <td>
                          <el-form-item class="table-form-item">
                            <el-select v-model="achievementEditForm.maturity" placeholder="--请选择--">
                              <el-option label="实验室理论阶段" value="实验室理论阶段" />
                              <el-option label="中试阶段" value="中试阶段" />
                              <el-option label="可规模量产" value="可规模量产" />
                            </el-select>
                          </el-form-item>
                        </td>
                      </tr>
                      <tr>
                        <th><span class="required">*</span> 转化方式</th>
                        <td>
                          <el-form-item class="table-form-item">
                            <el-checkbox-group v-model="achievementEditForm.transformTypes">
                              <div class="checkbox-vertical">
                                <el-checkbox label="技术转让" value="技术转让" />
                                <el-checkbox label="技术许可" value="技术许可" />
                                <el-checkbox label="技术入股" value="技术入股" />
                                <el-checkbox label="合作开发" value="合作开发" />
                                <el-checkbox label="其他" value="其他" />
                              </div>
                            </el-checkbox-group>
                            <el-input v-if="achievementEditForm.transformTypes.includes('其他')" v-model="achievementEditForm.transformOther" placeholder="请填写具体转化方式" style="margin-top:8px;" />
                          </el-form-item>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <div class="detail-section">
                  <div class="detail-section-title">二、成果描述</div>
                  <table class="form-table">
                    <tbody>
                      <tr>
                        <th><span class="required">*</span> 成果摘要</th>
                        <td>
                          <el-form-item class="table-form-item">
                            <el-input v-model="achievementEditForm.summary" type="textarea" :rows="4" placeholder="请简要描述成果的主要内容" />
                          </el-form-item>
                        </td>
                      </tr>
                      <tr>
                        <th>技术优势描述</th>
                        <td>
                          <div style="margin-bottom:15px;">
                            <div class="field-label">创新性：</div>
                            <el-radio-group v-model="achievementEditForm.innovation_level">
                              <el-radio value="国际领先">国际领先</el-radio>
                              <el-radio value="国内领先">国内领先</el-radio>
                              <el-radio value="行业领先">行业领先</el-radio>
                            </el-radio-group>
                          </div>
                          <div>
                            <div class="field-label">与现有技术相比的优势：</div>
                            <el-input v-model="achievementEditForm.advantages" type="textarea" :rows="3" placeholder="请描述与现有技术相比的优势" />
                          </div>
                        </td>
                      </tr>
                      <tr>
                        <th>核心技术指标</th>
                        <td>
                          <el-input v-model="achievementEditForm.core_indicators" type="textarea" :rows="3" placeholder="请填写核心技术指标" />
                        </td>
                      </tr>
                      <tr>
                        <th>获得的知识产权</th>
                        <td>
                          <el-input v-model="achievementEditForm.intellectual_property" type="textarea" :rows="3" placeholder="请填写已获得的知识产权情况（专利、软件著作权等）" />
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <div class="detail-section">
                  <div class="detail-section-title">三、成果转化</div>
                  <table class="form-table">
                    <tbody>
                      <tr>
                        <th><span class="required">*</span> 合作方式偏好</th>
                        <td>
                          <el-form-item class="table-form-item">
                            <el-radio-group v-model="achievementEditForm.cooperationPref">
                              <div class="checkbox-vertical">
                                <div class="radio-with-extra">
                                  <el-radio value="技术转让">技术转让</el-radio>
                                  <span v-if="achievementEditForm.cooperationPref === '技术转让'" class="extra-input">
                                    （转让费：期望 <el-input-number v-model="achievementEditForm.transferFee" :precision="2" :controls="false" size="small" style="width:120px;" /> 万元）
                                  </span>
                                </div>
                                <div class="radio-with-extra">
                                  <el-radio value="技术许可">技术许可</el-radio>
                                  <span v-if="achievementEditForm.cooperationPref === '技术许可'" class="extra-input">
                                    （许可方式：
                                    <el-radio-group v-model="achievementEditForm.licenseType" size="small">
                                      <el-radio value="独占">独占</el-radio>
                                      <el-radio value="排他">排他</el-radio>
                                      <el-radio value="普通">普通</el-radio>
                                    </el-radio-group>
                                    ）
                                  </span>
                                </div>
                                <div class="radio-with-extra">
                                  <el-radio value="技术入股">技术入股</el-radio>
                                  <span v-if="achievementEditForm.cooperationPref === '技术入股'" class="extra-input">
                                    （作价 <el-input-number v-model="achievementEditForm.equityValue" :precision="2" :controls="false" size="small" style="width:120px;" /> 万元，占 <el-input-number v-model="achievementEditForm.equityPercent" :controls="false" :min="0" :max="100" :precision="2" size="small" style="width:100px;" /> 股%）
                                  </span>
                                </div>
                                <el-radio value="合作开发">合作开发</el-radio>
                                <div class="radio-with-extra">
                                  <el-radio value="其他">其他</el-radio>
                                  <el-input v-if="achievementEditForm.cooperationPref === '其他'" v-model="achievementEditForm.cooperationOther" placeholder="请填写" style="width:200px;margin-left:8px;" size="small" />
                                </div>
                              </div>
                            </el-radio-group>
                          </el-form-item>
                        </td>
                      </tr>
                      <tr>
                        <th>期望转化时间</th>
                        <td>
                          <div style="display:flex;align-items:center;gap:8px;">
                            <el-date-picker v-model="achievementEditForm.expectDate" type="month" placeholder="选择月份" format="YYYY年M月" />
                            <span style="color:#666;white-space:nowrap;">前完成转化</span>
                          </div>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </el-form>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-default" @click="achievementEditVisible = false">取消</button>
            <button class="btn btn-primary" @click="submitAchievementEdit" :disabled="achievementEditSubmitting">
              {{ achievementEditSubmitting ? '提交中...' : '重新提交审核' }}
            </button>
          </div>
        </div>
      </div>

      <!-- 需求编辑弹窗 -->
      <div class="modal" :class="{ active: demandEditVisible }" @click.self="demandEditVisible = false">
        <div class="modal-content modal-lg">
          <div class="modal-header">
            <div class="modal-title">编辑需求</div>
            <button class="modal-close" @click="demandEditVisible = false">&times;</button>
          </div>
          <div class="modal-body">
            <div v-if="demandEditLoading" style="text-align:center;padding:20px;color:#999;">加载中...</div>
            <div v-else-if="demandEdit">
              <div class="detail-section" style="border:1px solid #e6a23c;border-radius:4px;padding:12px;margin-bottom:16px;background:#fffbe6;">
                <div class="detail-section-title" style="color:#e6a23c;">驳回原因</div>
                <p style="color:#e6a23c;font-size:14px;">{{ demandEdit.reject_reason || '无' }}</p>
              </div>
              <el-form label-position="left" label-width="120px" class="edit-form">
                <div class="detail-section">
                  <div class="detail-section-title">一、需求基本信息</div>
                  <table class="form-table">
                    <tbody>
                      <tr>
                        <th><span class="required">*</span> 企业名称</th>
                        <td>
                          <el-form-item class="table-form-item">
                            <el-input v-model="demandEditForm.company_name" placeholder="请输入企业全称" />
                          </el-form-item>
                        </td>
                      </tr>
                      <tr>
                        <th><span class="required">*</span> 需求名称</th>
                        <td>
                          <el-form-item class="table-form-item">
                            <el-input v-model="demandEditForm.demand_name" placeholder="请输入需求名称" />
                          </el-form-item>
                        </td>
                      </tr>
                      <tr>
                        <th><span class="required">*</span> 所属地区</th>
                        <td>
                          <el-form-item class="table-form-item">
                            <div class="region-selectors">
                              <el-select v-model="demandEditForm.province" placeholder="选择省份">
                                <el-option v-for="province in provinces" :key="province" :label="province" :value="province" />
                              </el-select>
                              <el-select v-model="demandEditForm.city" :placeholder="demandIsMunicipality ? '选择区' : '选择城市'" :disabled="!demandEditForm.province">
                                <el-option v-for="city in demandCities" :key="city" :label="city" :value="city" />
                              </el-select>
                            </div>
                          </el-form-item>
                        </td>
                      </tr>
                      <tr>
                        <th><span class="required">*</span> 技术领域</th>
                        <td>
                          <el-form-item class="table-form-item">
                            <el-select v-model="demandEditForm.techField" placeholder="--请选择--">
                              <el-option v-for="item in techFieldOptions" :key="item" :label="item" :value="item" />
                            </el-select>
                          </el-form-item>
                          <el-form-item v-if="demandEditForm.techField === '其他'" class="table-form-item" style="margin-top:8px;">
                            <el-input v-model="demandEditForm.techFieldOther" placeholder="请填写具体领域" />
                          </el-form-item>
                        </td>
                      </tr>
                      <tr>
                        <th><span class="required">*</span> 需求类型</th>
                        <td>
                          <el-form-item class="table-form-item">
                            <el-select v-model="demandEditForm.demandType" placeholder="--请选择--">
                              <el-option label="技术需求" value="技术需求" />
                              <el-option label="金融需求" value="金融需求" />
                              <el-option label="场景需求" value="场景需求" />
                              <el-option label="其他" value="其他" />
                            </el-select>
                          </el-form-item>
                          <el-form-item v-if="demandEditForm.demandType === '其他'" class="table-form-item" style="margin-top:8px;">
                            <el-input v-model="demandEditForm.demandTypeOther" placeholder="请填写具体需求类型" />
                          </el-form-item>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <div class="detail-section">
                  <div class="detail-section-title">二、需求描述</div>
                  <table class="form-table">
                    <tbody>
                      <tr>
                        <th><span class="required">*</span> 需求概述</th>
                        <td>
                          <el-form-item class="table-form-item">
                            <el-input v-model="demandEditForm.overview" type="textarea" :rows="4" placeholder="请详细描述需求的主要内容" />
                          </el-form-item>
                        </td>
                      </tr>
                      <tr>
                        <th><span class="required">*</span> 期望解决的问题</th>
                        <td>
                          <el-form-item class="table-form-item">
                            <el-input v-model="demandEditForm.target_problems" type="textarea" :rows="4" placeholder="请描述期望通过该需求解决的具体问题" />
                          </el-form-item>
                        </td>
                      </tr>
                      <tr>
                        <th>项目预算</th>
                        <td>
                          <div style="display:flex;align-items:center;gap:10px;">
                            <el-input-number v-model="demandEditForm.budget" :precision="2" :controls="false" placeholder="请输入金额" style="width:200px;" />
                            <el-select v-model="demandEditForm.budgetUnit" style="width:120px;">
                              <el-option v-for="option in budgetUnitOptions" :key="option.value" :label="option.label" :value="option.value" />
                            </el-select>
                          </div>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </el-form>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-default" @click="demandEditVisible = false">取消</button>
            <button class="btn btn-primary" @click="submitDemandEdit" :disabled="demandEditSubmitting">
              {{ demandEditSubmitting ? '提交中...' : '重新提交审核' }}
            </button>
          </div>
        </div>
      </div>
    </div>
    <div v-if="!isLoggedIn" class="unauthorized-prompt">
      <div class="prompt-container">
        <h2>您未登录</h2>
        <p>登录后即可查看个人中心</p>
        <button class="auth-button" @click="openLogin">去登录/注册</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { WarningFilled } from '@element-plus/icons-vue'
import { reactive, ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import useAuth from '../composables/useAuth'
import request from '../utils/request'

const router = useRouter()
const route = useRoute()
const auth = useAuth()
const isLoggedIn = auth.isLoggedIn
const openLogin = () => {
  router.push({
    path: '/auth',
    query: { redirect: route.fullPath, tab: 'login' }
  })
}

const techFieldOptions = [
  '新一代信息技术', '人工智能', '大数据', '区块链',
  '高端装备制造', '机器人', '航空航天', '新材料',
  '新能源', '节能环保', '生物医药', '医疗器械',
  '现代农业', '其他'
]

const budgetUnitOptions = [
  { value: '元', label: '元' },
  { value: '万元', label: '万元' },
  { value: '百万元', label: '百万元' },
  { value: '亿元', label: '亿元' }
]

// 省份数据
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

// 城市映射
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

// 直辖市列表（用于判断城市选择器显示"区"还是"市"）
const municipalities = ['北京市', '天津市', '上海市', '重庆市']

const activeTab = ref('basic')

// 我的待办子标签：被驳成果 / 被驳需求
const todoSubTab = ref('rejected-achievement')

// 我的成果子标签：待审核 / 已通过
const achievementSubTab = ref('pending')
// 我的需求子标签：待审核 / 已通过
const demandSubTab = ref('pending')

// 各状态计数
const achievementPendingCount = ref(0)
const achievementApprovedCount = ref(0)
const requirementPendingCount = ref(0)
const requirementApprovedCount = ref(0)

// 成果编辑：城市选择器计算属性
const achievementIsMunicipality = computed(() => municipalities.includes(achievementEditForm.province))
const achievementCities = computed(() => {
  if (!achievementEditForm.province) return []
  return citiesMap[achievementEditForm.province] || []
})

// 需求编辑：城市选择器计算属性
const demandIsMunicipality = computed(() => municipalities.includes(demandEditForm.province))
const demandCities = computed(() => {
  if (!demandEditForm.province) return []
  return citiesMap[demandEditForm.province] || []
})

// 用户信息
const user = reactive({
  id: '',
  username: '',
  phone: '',
  role: '',
  status: 0,
  real_name: '',
  id_card: ''
})

// 成果审核分页状态
const reviewPagination = reactive({
  page: 1,
  page_size: 5,
  total: 0,
  total_pages: 0,
  loading: false
})

// 需求审核分页状态
const demandReviewPagination = reactive({
  page: 1,
  page_size: 5,
  total: 0,
  total_pages: 0,
  loading: false
})

// 用户成果分页状态
const userAchievementPagination = reactive({
  page: 1,
  page_size: 5,
  total: 0,
  total_pages: 0,
  loading: false
})

// 用户需求分页状态
const userRequirementPagination = reactive({
  page: 1,
  page_size: 5,
  total: 0,
  total_pages: 0,
  loading: false
})

// 被驳成果分页状态
const rejectedAchievementPagination = reactive({
  page: 1,
  page_size: 5,
  total: 0,
  total_pages: 0,
  loading: false
})

// 被驳需求分页状态
const rejectedRequirementPagination = reactive({
  page: 1,
  page_size: 5,
  total: 0,
  total_pages: 0,
  loading: false
})

// 被驳列表数据
const rejectedAchievementList = ref([])
const rejectedRequirementList = ref([])

// 被驳数量
const rejectedAchievementTotal = ref(0)
const rejectedRequirementTotal = ref(0)

// 待办总计数（被驳成果 + 被驳需求）
const todoTotalCount = computed(() => rejectedAchievementTotal.value + rejectedRequirementTotal.value)

// 待审核数量
const pendingAchievementCount = ref(0)
const pendingRequirementCount = ref(0)

// 拒绝理由
const rejectReason = ref('')
const demandRejectReason = ref('')

// 标签页配置
const tabTitles = {
  todo: '我的待办',
  achievement: '我的成果',
  demand: '我的需求',
  'achievement-review': '成果审核',
  'demand-review': '需求审核'
}

const tabActions = {
  todo: '添加任务',
  achievement: '发布成果',
  demand: '发布需求',
  'achievement-review': '审核成果',
  'demand-review': '审核需求'
}

const emptyTexts = {
  todo: '暂无待办任务',
  achievement: '暂无成果',
  demand: '暂无需求',
  'achievement-review': '暂无待审核成果',
  'demand-review': '暂无待审核需求'
}

// 数据状态
const dataLists = reactive({
  achievement: [],
  demand: [],
  'achievement-review': [],
  'demand-review': []
})

onMounted(() => {
  // 从认证状态获取用户信息（先用本地缓存填充，再异步拉取最新数据）
  if (auth.state.user) {
    Object.assign(user, {
      id: auth.state.user.id || user.id,
      username: auth.state.user.username || user.username,
      phone: auth.state.user.phone || user.phone,
      role: auth.state.user.role || user.role,
      status: auth.state.user.status || user.status
    })
  }
  // 只要有token就请求完整用户信息（不依赖本地user是否存在）
  if (auth.state.token) {
    fetchUserInfo()
  }
})

// 获取完整的用户信息
async function fetchUserInfo() {
  try {
    const res = await request.get('/api/me')
    if (res.code === 200) {
      Object.assign(user, {
        id: res.data.id,
        username: res.data.username,
        phone: res.data.phone,
        role: res.data.role,
        status: res.data.status,
        real_name: res.data.real_name || '',
        id_card: res.data.id_card || ''
      })
      // 如果是管理员，获取待审核数量
      if (res.data.role === 'admin') {
        fetchPendingCounts()
      }
    }
  } catch (error) {
    // 拦截器已通过 ElMessage 显示错误，此处不重复提示
    console.error('获取用户信息失败:', error)
  }
}

function handleLogout() {
  auth.logout()
  router.push('/')
}

// 编辑对话框状态
const dialogVisible = ref(false)
const editForm = reactive({
  id: '',
  username: '',
  phone: '',
  sms_code: ''
})
const editSmsCountdown = ref(0)
const editSmsButtonText = ref('获取验证码')

// 认证相关状态
const verifyDialogVisible = ref(false)
const verifyStep = ref(1) // 1: 验证手机号（如果需要），2: 填写认证信息
const verifyForm = reactive({
  real_name: '',
  id_card: '',
  phone: '',
  sms_code: ''
})
const smsCountdown = ref(0)
const smsButtonText = ref('获取验证码')

// 修改密码相关状态
const passwordDialogVisible = ref(false)
const passwordForm = reactive({
  phone: '',
  sms_code: '',
  new_password: '',
  confirm_password: ''
})
const passwordSmsCountdown = ref(0)
const passwordSmsButtonText = ref('获取验证码')

function handleEditProfile() {
  // 打开编辑个人信息的对话框
  Object.assign(editForm, {
    id: user.id,
    username: user.username,
    phone: user.phone,
    sms_code: ''
  })
  dialogVisible.value = true
}

async function sendEditSms() {
  if (editSmsCountdown.value > 0) return
  try {
    // 验证码发送到当前用户的手机号（旧手机号），用于身份验证
    const res = await request.post('/api/send_sms', {
      phone: user.phone,
      type: 'verify'
    })
    if (res.code === 200) {
      editSmsCountdown.value = 60
      const timer = setInterval(() => {
        editSmsCountdown.value--
        editSmsButtonText.value = `${editSmsCountdown.value}秒后重试`
        if (editSmsCountdown.value <= 0) {
          clearInterval(timer)
          editSmsButtonText.value = '获取验证码'
        }
      }, 1000)
      alert('验证码已发送到当前手机号')
    } else {
      alert(res.message)
    }
  } catch (error) {
    alert('发送验证码失败')
  }
}

async function handleSaveProfile() {
  // 检查手机号是否修改
  const phoneChanged = editForm.phone !== user.phone
  if (phoneChanged && !editForm.sms_code) {
    alert('修改手机号需要验证码')
    return
  }

  try {
    const data = {
      username: editForm.username
    }
    if (phoneChanged) {
      data.phone = editForm.phone
      data.phone_verify_code = editForm.sms_code
    }
    const res = await request.put('/api/update_profile', data)
    if (res.code === 200) {
      Object.assign(user, {
        username: editForm.username,
        phone: editForm.phone
      })
      dialogVisible.value = false
      alert('个人信息修改成功')
      // 重新获取用户信息以确保同步
      fetchUserInfo()
    } else {
      alert(res.message)
    }
  } catch (error) {
    alert('保存失败')
  }
}

// 处理认证按钮点击
function handleVerify() {
  // 如果已经认证，直接进入填写认证信息步骤（需要验证码）
  if (user.real_name && user.id_card) {
    verifyStep.value = 2
    verifyForm.phone = user.phone
    verifyForm.sms_code = ''
    verifyForm.real_name = user.real_name
    verifyForm.id_card = user.id_card
  } else {
    verifyStep.value = 2
    verifyForm.phone = user.phone
    verifyForm.sms_code = ''
    verifyForm.real_name = ''
    verifyForm.id_card = ''
  }
  verifyDialogVisible.value = true
}

// 发送验证码
async function sendVerifySms() {
  if (smsCountdown.value > 0) return
  try {
    const res = await request.post('/api/send_sms', {
      phone: verifyForm.phone,
      type: 'verify'
    })
    if (res.code === 200) {
      smsCountdown.value = 60
      const timer = setInterval(() => {
        smsCountdown.value--
        smsButtonText.value = `${smsCountdown.value}秒后重试`
        if (smsCountdown.value <= 0) {
          clearInterval(timer)
          smsButtonText.value = '获取验证码'
        }
      }, 1000)
      alert('验证码已发送')
    } else {
      alert(res.message)
    }
  } catch (error) {
    alert('发送验证码失败')
  }
}

// 验证验证码并进入下一步
function verifySmsCode() {
  if (!verifyForm.sms_code) {
    alert('请输入验证码')
    return
  }
  verifyStep.value = 2
}

// 提交认证信息
async function submitVerification() {
  if (!verifyForm.real_name || !verifyForm.id_card) {
    alert('请填写姓名和身份证号')
    return
  }
  // 身份证号格式校验（18位数字或17位数字+X）
  const idCardReg = /^[1-9]\d{5}(18|19|20)?\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]$/
  if (!idCardReg.test(verifyForm.id_card)) {
    alert('请输入正确的身份证号码')
    return
  }
  try {
    const data = {
      real_name: verifyForm.real_name,
      id_card: verifyForm.id_card
    }
    // 如果是修改认证且已验证手机号，需要带上验证码
    if (user.real_name && user.id_card && verifyStep.value === 2) {
      data.phone = verifyForm.phone
      data.phone_verify_code = verifyForm.sms_code
    }
    const res = await request.put('/api/update_profile', data)
    if (res.code === 200) {
      alert('认证信息更新成功')
      verifyDialogVisible.value = false
      // 重新获取用户信息
      fetchUserInfo()
      // 同步到全局 auth 状态，让其他页面立即感知
      auth.fetchUserProfile()
    } else {
      alert(res.message)
    }
  } catch (error) {
    alert('更新失败')
  }
}

// 修改密码相关函数
function handleChangePassword() {
  passwordForm.phone = user.phone
  passwordForm.sms_code = ''
  passwordForm.new_password = ''
  passwordForm.confirm_password = ''
  passwordDialogVisible.value = true
}

async function sendPasswordSms() {
  if (passwordSmsCountdown.value > 0) return
  try {
    const res = await request.post('/api/send_sms', {
      phone: passwordForm.phone,
      type: 'verify'
    })
    if (res.code === 200) {
      passwordSmsCountdown.value = 60
      const timer = setInterval(() => {
        passwordSmsCountdown.value--
        passwordSmsButtonText.value = `${passwordSmsCountdown.value}秒后重试`
        if (passwordSmsCountdown.value <= 0) {
          clearInterval(timer)
          passwordSmsButtonText.value = '获取验证码'
        }
      }, 1000)
      alert('验证码已发送')
    } else {
      alert(res.message)
    }
  } catch (error) {
    alert('发送验证码失败')
  }
}

async function submitChangePassword() {
  if (!passwordForm.sms_code) {
    alert('请输入验证码')
    return
  }
  if (!passwordForm.new_password || passwordForm.new_password.length < 6) {
    alert('新密码长度不能少于6位')
    return
  }
  if (passwordForm.new_password !== passwordForm.confirm_password) {
    alert('两次输入的密码不一致')
    return
  }
  try {
    const res = await request.post('/api/change_password', {
      sms_code: passwordForm.sms_code,
      new_password: passwordForm.new_password,
      confirm_password: passwordForm.confirm_password
    })
    if (res.code === 200) {
      alert('密码修改成功')
      passwordDialogVisible.value = false
    } else {
      alert(res.message)
    }
  } catch (error) {
    alert('修改密码失败')
  }
}

async function handleMenuSelect(key) {
  activeTab.value = key
  // 菜单切换时的动画效果（已移除可能导致闪烁的动画）

  // 如果切换到成果审核标签页，加载待审核成果
  if (key === 'achievement-review') {
    await fetchPendingAchievements()
  }
  // 如果切换到需求审核标签页，加载待审核需求
  else if (key === 'demand-review') {
    await fetchPendingRequirements()
  }
  // 如果切换到我的成果标签页，加载用户成果和计数
  else if (key === 'achievement') {
    await Promise.all([
      fetchUserAchievements(),
      fetchAchievementCounts()
    ])
  }
  // 如果切换到我的需求标签页，加载用户需求和计数
  else if (key === 'demand') {
    await Promise.all([
      fetchUserRequirements(),
      fetchRequirementCounts()
    ])
  }
  // 如果切换到我的待办标签页，加载被驳数据
  else if (key === 'todo') {
    await Promise.all([
      fetchRejectedAchievements(),
      fetchRejectedRequirements()
    ])
  }
}

// 卡片状态样式
function getCardStatusClass(tab) {
  if (tab === 'achievement') return 'card-type'
  if (tab === 'demand') return 'card-status demand-status'
  if (tab === 'achievement-review' || tab === 'demand-review') return 'card-status review-status'
  return 'card-status'
}

// 卡片操作文本
function getCardActionText(tab) {
  if (tab === 'todo') return '处理'
  if (tab === 'achievement-review' || tab === 'demand-review') return '审核'
  return '查看'
}

// 获取待审核数量
async function fetchPendingCounts() {
  if (user.role !== 'admin') {
    return
  }
  try {
    // 并行获取成果和需求数量
    const [achievementRes, requirementRes] = await Promise.all([
      request.get('/api/publish/pending_achievements', { params: { page: 1, page_size: 1 } }),
      request.get('/api/publish/pending_requirements', { params: { page: 1, page_size: 1 } })
    ])
    if (achievementRes.code === 200) {
      pendingAchievementCount.value = achievementRes.total || 0
    }
    if (requirementRes.code === 200) {
      pendingRequirementCount.value = requirementRes.total || 0
    }
  } catch (error) {
    console.error('获取待审核数量失败:', error)
  }
}

// 获取待审核成果
async function fetchPendingAchievements() {
  if (user.role !== 'admin') {
    console.warn('非管理员用户尝试访问成果审核')
    return
  }

  reviewPagination.loading = true
  try {
    const response = await request.get('/api/publish/pending_achievements', {
      params: {
        page: reviewPagination.page,
        page_size: reviewPagination.page_size
      }
    })

    if (response.code === 200) {
      dataLists['achievement-review'] = response.data || []
      reviewPagination.total = response.total || 0
      reviewPagination.total_pages = response.total_pages || 0
      pendingAchievementCount.value = response.total || 0
    } else {
      console.error('获取待审核成果失败:', response.msg)
      alert(`获取待审核成果失败: ${response.msg}`)
    }
  } catch (error) {
    console.error('获取待审核成果时出错:', error)
    alert('获取待审核成果时出错')
  } finally {
    reviewPagination.loading = false
  }
}

// 获取待审核需求
async function fetchPendingRequirements() {
  if (user.role !== 'admin') {
    console.warn('非管理员用户尝试访问需求审核')
    return
  }

  demandReviewPagination.loading = true
  try {
    const response = await request.get('/api/publish/pending_requirements', {
      params: {
        page: demandReviewPagination.page,
        page_size: demandReviewPagination.page_size
      }
    })

    if (response.code === 200) {
      dataLists['demand-review'] = response.data || []
      demandReviewPagination.total = response.total || 0
      demandReviewPagination.total_pages = response.total_pages || 0
      pendingRequirementCount.value = response.total || 0
    } else {
      console.error('获取待审核需求失败:', response.msg)
      alert(`获取待审核需求失败: ${response.msg}`)
    }
  } catch (error) {
    console.error('获取待审核需求时出错:', error)
    alert('获取待审核需求时出错')
  } finally {
    demandReviewPagination.loading = false
  }
}

// 处理分页改变
function handlePageChange(newPage) {
  reviewPagination.page = newPage
  fetchPendingAchievements()
}

// 处理需求审核分页改变
function handleDemandPageChange(newPage) {
  demandReviewPagination.page = newPage
  fetchPendingRequirements()
}

// 获取用户成果列表
async function fetchUserAchievements() {
  userAchievementPagination.loading = true
  try {
    const params = {
      page: userAchievementPagination.page,
      page_size: userAchievementPagination.page_size,
      status: achievementSubTab.value
    }
    const response = await request.get('/api/publish/achievements', { params })

    if (response.code === 200) {
      dataLists['achievement'] = response.data || []
      userAchievementPagination.total = response.total || 0
      userAchievementPagination.total_pages = response.total_pages || 0
    } else {
      console.error('获取用户成果失败:', response.msg)
      alert(`获取用户成果失败: ${response.msg}`)
    }
  } catch (error) {
    console.error('获取用户成果时出错:', error)
    alert('获取用户成果时出错')
  } finally {
    userAchievementPagination.loading = false
  }
}

// 获取用户需求列表
async function fetchUserRequirements() {
  userRequirementPagination.loading = true
  try {
    const params = {
      page: userRequirementPagination.page,
      page_size: userRequirementPagination.page_size,
      status: demandSubTab.value
    }
    const response = await request.get('/api/publish/requirements', { params })

    if (response.code === 200) {
      dataLists['demand'] = response.data || []
      userRequirementPagination.total = response.total || 0
      userRequirementPagination.total_pages = response.total_pages || 0
    } else {
      console.error('获取用户需求失败:', response.msg)
      alert(`获取用户需求失败: ${response.msg}`)
    }
  } catch (error) {
    console.error('获取用户需求时出错:', error)
    alert('获取用户需求时出错')
  } finally {
    userRequirementPagination.loading = false
  }
}

// 获取成果各状态计数
async function fetchAchievementCounts() {
  try {
    const [pendingRes, approvedRes] = await Promise.all([
      request.get('/api/publish/achievements', { params: { page: 1, page_size: 1, status: 'pending' } }),
      request.get('/api/publish/achievements', { params: { page: 1, page_size: 1, status: 'approved' } })
    ])
    if (pendingRes.code === 200) achievementPendingCount.value = pendingRes.total || 0
    if (approvedRes.code === 200) achievementApprovedCount.value = approvedRes.total || 0
  } catch (error) {
    console.error('获取成果计数失败:', error)
  }
}

// 获取需求各状态计数
async function fetchRequirementCounts() {
  try {
    const [pendingRes, approvedRes] = await Promise.all([
      request.get('/api/publish/requirements', { params: { page: 1, page_size: 1, status: 'pending' } }),
      request.get('/api/publish/requirements', { params: { page: 1, page_size: 1, status: 'approved' } })
    ])
    if (pendingRes.code === 200) requirementPendingCount.value = pendingRes.total || 0
    if (approvedRes.code === 200) requirementApprovedCount.value = approvedRes.total || 0
  } catch (error) {
    console.error('获取需求计数失败:', error)
  }
}

// 处理用户成果分页改变
function handleUserAchievementPageChange(newPage) {
  userAchievementPagination.page = newPage
  fetchUserAchievements()
}

// 处理用户需求分页改变
function handleUserRequirementPageChange(newPage) {
  userRequirementPagination.page = newPage
  fetchUserRequirements()
}

// 获取被驳回的成果列表
async function fetchRejectedAchievements() {
  rejectedAchievementPagination.loading = true
  try {
    const response = await request.get('/api/publish/rejected_achievements', {
      params: {
        page: rejectedAchievementPagination.page,
        page_size: rejectedAchievementPagination.page_size
      }
    })
    if (response.code === 200) {
      rejectedAchievementList.value = response.data || []
      rejectedAchievementPagination.total = response.total || 0
      rejectedAchievementPagination.total_pages = response.total_pages || 0
      rejectedAchievementTotal.value = response.total || 0
    }
  } catch (error) {
    console.error('获取被驳回成果失败:', error)
  } finally {
    rejectedAchievementPagination.loading = false
  }
}

// 获取被驳回的需求列表
async function fetchRejectedRequirements() {
  rejectedRequirementPagination.loading = true
  try {
    const response = await request.get('/api/publish/rejected_requirements', {
      params: {
        page: rejectedRequirementPagination.page,
        page_size: rejectedRequirementPagination.page_size
      }
    })
    if (response.code === 200) {
      rejectedRequirementList.value = response.data || []
      rejectedRequirementPagination.total = response.total || 0
      rejectedRequirementPagination.total_pages = response.total_pages || 0
      rejectedRequirementTotal.value = response.total || 0
    }
  } catch (error) {
    console.error('获取被驳回需求失败:', error)
  } finally {
    rejectedRequirementPagination.loading = false
  }
}

// 处理被驳成果分页改变
function handleRejectedAchievementPageChange(newPage) {
  rejectedAchievementPagination.page = newPage
  fetchRejectedAchievements()
}

// 处理被驳需求分页改变
function handleRejectedRequirementPageChange(newPage) {
  rejectedRequirementPagination.page = newPage
  fetchRejectedRequirements()
}

// 审核成果（通过/拒绝）
async function handleReview(achievementId, status) {
  let reason = ''
  if (status === 'rejected') {
    reason = prompt('请填写拒绝理由：')
    if (reason === null) return  // 用户取消
    if (!reason.trim()) {
      alert('拒绝理由不能为空')
      return
    }
  }

  if (!confirm(`确定要${status === 'approved' ? '通过' : '拒绝'}该成果吗？`)) {
    return
  }

  try {
    const response = await request.post(`/api/publish/achievement/${achievementId}/review`, {
      status: status,
      reason: reason.trim()
    })

    if (response.code === 200) {
      alert(response.msg || '操作成功')
      // 刷新待审核成果列表
      await fetchPendingAchievements()
    } else {
      alert(response.msg || '操作失败')
    }
  } catch (error) {
    console.error('审核成果时出错:', error)
    alert('审核成果时出错')
  }
}

// 审核需求（通过/拒绝）
async function handleDemandReview(requirementId, status) {
  let reason = ''
  if (status === 'rejected') {
    reason = prompt('请填写拒绝理由：')
    if (reason === null) return  // 用户取消
    if (!reason.trim()) {
      alert('拒绝理由不能为空')
      return
    }
  }

  if (!confirm(`确定要${status === 'approved' ? '通过' : '拒绝'}该需求吗？`)) {
    return
  }

  try {
    const response = await request.post(`/api/publish/requirement/${requirementId}/review`, {
      status: status,
      reason: reason.trim()
    })

    if (response.code === 200) {
      alert(response.msg || '操作成功')
      // 刷新待审核需求列表
      await fetchPendingRequirements()
    } else {
      alert(response.msg || '操作失败')
    }
  } catch (error) {
    console.error('审核需求时出错:', error)
    alert('审核需求时出错')
  }
}

// 格式化日期
function formatDate(dateString) {
  if (!dateString) return '未知时间'
  try {
    const date = new Date(dateString)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (e) {
    return dateString
  }
}

// 状态样式
function getStatusClass(status) {
  if (status === 'pending') return 'review-status'
  if (status === 'approved') return 'approved-status'
  if (status === 'rejected') return 'rejected-status'
  return 'review-status'
}

// 状态文本
function getStatusText(status) {
  const statusMap = {
    pending: '待审核',
    approved: '已通过',
    rejected: '已拒绝',
    reviewed: '已审核'
  }
  return statusMap[status] || status
}

// 格式化技术领域
function formatTechFields(fields, other) {
  if (!fields || !Array.isArray(fields)) return '未设置'
  const filtered = fields.filter(f => f !== '其他')
  let result = filtered.join('、')
  if (other && other.trim()) {
    result += (result ? '、' : '') + `其他：${other}`
  }
  return result || '未设置'
}

// 格式化转化方式
function formatTransferMethods(methods, other) {
  if (!methods || !Array.isArray(methods)) return '未设置'
  const filtered = methods.filter(m => m !== '其他')
  let result = filtered.join('、')
  if (other && other.trim()) {
    result += (result ? '、' : '') + `其他：${other}`
  }
  return result || '未设置'
}

// 格式化转化偏好
function formatTransferPreference(pref) {
  if (!pref) return '未填写'
  const parts = []
  if (pref.tech_transfer?.enabled) {
    parts.push(`技术转让（期望费用：${pref.tech_transfer.expected_fee || 0}万元）`)
  }
  if (pref.tech_license?.enabled) {
    parts.push(`技术许可（许可方式：${pref.tech_license.type || '未指定'}）`)
  }
  if (pref.tech_investment?.enabled) {
    parts.push(`技术入股（作价${pref.tech_investment.valuation || 0}万元，占${pref.tech_investment.share_ratio || 0}%）`)
  }
  if (pref.cooperation_dev) {
    parts.push('合作开发')
  }
  if (pref.other) {
    parts.push(`其他：${pref.other}`)
  }
  return parts.join('；') || '未填写'
}

// 格式化需求类型
function formatDemandTypes(types, other) {
  if (!types || !Array.isArray(types)) return '未设置'
  const filtered = types.filter(t => t !== '其他')
  let result = filtered.join('、')
  if (other && other.trim()) {
    result += (result ? '、' : '') + `其他：${other}`
  }
  return result || '未设置'
}

// 格式化地区
function formatRegion(region) {
  if (!region) return '未设置'
  const province = region.province || ''
  const city = region.city || ''
  if (province && city) {
    return `${province}${city}`
  } else if (province) {
    return province
  } else if (city) {
    return city
  }
  return '未设置'
}

// 格式化预算
function formatBudget(budget) {
  if (!budget) return '未设置'
  // 预算存储单位为万元，显示为"X万元"
  return `${budget}万元`
}

// 详情对话框状态
const detailDialogVisible = ref(false)
const currentAchievement = ref(null)
const achievementDetail = ref(null)
const detailLoading = ref(false)

// 需求详情对话框状态
const demandDetailDialogVisible = ref(false)
const currentRequirement = ref(null)
const requirementDetail = ref(null)
const demandDetailLoading = ref(false)

// 打开详情对话框
async function openDetailDialog(item) {
  currentAchievement.value = item
  detailLoading.value = true
  detailDialogVisible.value = true

  try {
    // 调用API获取成果详情
    const response = await request.get(`/api/publish/achievement/${item.id}`)
    if (response.code === 200) {
      achievementDetail.value = response.data
    } else {
      alert(`加载详情失败: ${response.msg}`)
      // 回退到现有数据
      achievementDetail.value = item
    }
  } catch (error) {
    console.error('获取成果详情失败:', error)
    alert('获取成果详情失败')
    // 回退到现有数据
    achievementDetail.value = item
  } finally {
    detailLoading.value = false
  }
}

// 打开需求详情对话框
async function openDemandDetailDialog(item) {
  currentRequirement.value = item
  demandDetailLoading.value = true
  demandDetailDialogVisible.value = true

  try {
    // 调用API获取需求详情
    const response = await request.get(`/api/publish/requirement/${item.id}`)
    if (response.code === 200) {
      requirementDetail.value = response.data
    } else {
      alert(`加载详情失败: ${response.msg}`)
      // 回退到现有数据
      requirementDetail.value = item
    }
  } catch (error) {
    console.error('获取需求详情失败:', error)
    alert('获取需求详情失败')
    // 回退到现有数据
    requirementDetail.value = item
  } finally {
    demandDetailLoading.value = false
  }
}

// 详情对话框中审核成果
async function handleDetailReview(status) {
  if (!currentAchievement.value) return

  // 拒绝时必须填写理由
  if (status === 'rejected' && !rejectReason.value.trim()) {
    alert('请填写拒绝理由')
    return
  }

  if (!confirm(`确定要${status === 'approved' ? '通过' : '拒绝'}该成果吗？`)) {
    return
  }

  try {
    const response = await request.post(`/api/publish/achievement/${currentAchievement.value.id}/review`, {
      status: status,
      reason: rejectReason.value.trim()
    })

    if (response.code === 200) {
      alert(response.msg || '操作成功')
      // 关闭对话框
      detailDialogVisible.value = false
      rejectReason.value = ''  // 清空理由
      // 刷新待审核成果列表
      await fetchPendingAchievements()
    } else {
      alert(response.msg || '操作失败')
    }
  } catch (error) {
    console.error('审核成果时出错:', error)
    alert('审核成果时出错')
  }
}

// 需求详情对话框中审核需求
async function handleDemandDetailReview(status) {
  if (!currentRequirement.value) return

  // 拒绝时必须填写理由
  if (status === 'rejected' && !demandRejectReason.value.trim()) {
    alert('请填写拒绝理由')
    return
  }

  if (!confirm(`确定要${status === 'approved' ? '通过' : '拒绝'}该需求吗？`)) {
    return
  }

  try {
    const response = await request.post(`/api/publish/requirement/${currentRequirement.value.id}/review`, {
      status: status,
      reason: demandRejectReason.value.trim()
    })

    if (response.code === 200) {
      alert(response.msg || '操作成功')
      // 关闭对话框
      demandDetailDialogVisible.value = false
      demandRejectReason.value = ''  // 清空理由
      // 刷新待审核需求列表
      await fetchPendingRequirements()
    } else {
      alert(response.msg || '操作失败')
    }
  } catch (error) {
    console.error('审核需求时出错:', error)
    alert('审核需求时出错')
  }
}

// ==================== 成果编辑弹窗 ====================
const achievementEditVisible = ref(false)
const achievementEditLoading = ref(false)
const achievementEdit = ref(null)
const achievementEditSubmitting = ref(false)
const achievementEditForm = reactive({
  achievement_name: '',
  owner: '',
  province: '',
  city: '',
  techField: '',
  techFieldOther: '',
  maturity: '',
  transformTypes: [],
  transformOther: '',
  summary: '',
  innovation_level: '',
  advantages: '',
  core_indicators: '',
  intellectual_property: '',
  cooperationPref: '',
  transferFee: 0,
  licenseType: '',
  equityValue: 0,
  equityPercent: 0,
  cooperationOther: '',
  expectDate: null
})

async function openAchievementEditDialog(item) {
  achievementEdit.value = item
  achievementEditLoading.value = true
  achievementEditVisible.value = true

  try {
    const response = await request.get(`/api/publish/achievement/${item.id}`)
    if (response.code === 200) {
      const d = response.data
      achievementEdit.value = d

      // 基本信息
      achievementEditForm.achievement_name = d.achievement_name || ''
      achievementEditForm.owner = d.owner || ''
      achievementEditForm.province = d.region?.province || ''
      achievementEditForm.city = d.region?.city || ''
      achievementEditForm.techField = (d.tech_fields && d.tech_fields[0]) || ''
      achievementEditForm.techFieldOther = d.tech_fields_other || ''
      if ((!d.tech_fields || d.tech_fields.length === 0) && d.tech_fields_other) {
        achievementEditForm.techField = '其他'
      }
      achievementEditForm.maturity = d.tech_maturity || ''
      achievementEditForm.transformTypes = d.transfer_methods || []
      achievementEditForm.transformOther = d.transfer_methods_other || ''
      if (d.transfer_methods_other) {
        if (!achievementEditForm.transformTypes.includes('其他')) {
          achievementEditForm.transformTypes.push('其他')
        }
      }

      // 描述信息
      achievementEditForm.summary = d.description?.summary || ''
      achievementEditForm.innovation_level = d.description?.innovation_level || ''
      achievementEditForm.advantages = d.description?.advantages || ''
      achievementEditForm.core_indicators = d.description?.core_indicators || ''
      achievementEditForm.intellectual_property = d.description?.intellectual_property || ''

      // 转化偏好
      const pref = d.transfer_preference || {}
      achievementEditForm.cooperationPref = pref.preferred_method || ''
      if (pref.tech_transfer) {
        achievementEditForm.transferFee = pref.tech_transfer.expected_fee || 0
      }
      if (pref.tech_license) {
        achievementEditForm.licenseType = pref.tech_license.type || ''
      }
      if (pref.tech_investment) {
        achievementEditForm.equityValue = pref.tech_investment.valuation || 0
        achievementEditForm.equityPercent = pref.tech_investment.share_ratio || 0
      }
      achievementEditForm.cooperationOther = pref.other || ''

      // 期望转化时间
      const dateObj = pref.expected_complete_date || {}
      if (dateObj.year && dateObj.month) {
        achievementEditForm.expectDate = new Date(dateObj.year, dateObj.month - 1)
      } else {
        achievementEditForm.expectDate = null
      }
    } else {
      alert('加载详情失败')
    }
  } catch (error) {
    console.error('获取成果详情失败:', error)
    alert('获取成果详情失败')
  } finally {
    achievementEditLoading.value = false
  }
}

async function submitAchievementEdit() {
  if (!achievementEdit.value) return
  if (!achievementEditForm.achievement_name.trim()) {
    alert('请输入成果名称')
    return
  }

  achievementEditSubmitting.value = true
  try {
    const response = await request.put(`/api/publish/achievement/${achievementEdit.value.id}`, {
      name: achievementEditForm.achievement_name,
      holder: achievementEditForm.owner,
      province: achievementEditForm.province,
      city: achievementEditForm.city,
      techField: achievementEditForm.techField,
      techFieldOther: achievementEditForm.techFieldOther,
      maturity: achievementEditForm.maturity,
      transformTypes: achievementEditForm.transformTypes,
      transformOther: achievementEditForm.transformOther,
      summary: achievementEditForm.summary,
      innovationLevel: achievementEditForm.innovation_level,
      advantages: achievementEditForm.advantages,
      techIndicators: achievementEditForm.core_indicators,
      intellectualProperty: achievementEditForm.intellectual_property,
      cooperationPref: achievementEditForm.cooperationPref,
      transferFee: achievementEditForm.transferFee,
      licenseType: achievementEditForm.licenseType,
      equityValue: achievementEditForm.equityValue,
      equityPercent: achievementEditForm.equityPercent,
      cooperationOther: achievementEditForm.cooperationOther,
      expectDate: achievementEditForm.expectDate
    })
    if (response.code === 200) {
      alert('修改成功，已重新提交审核')
      achievementEditVisible.value = false
      await fetchUserAchievements()
    } else {
      alert(response.msg || '提交失败')
    }
  } catch (error) {
    console.error('提交失败:', error)
    alert('提交失败，请稍后重试')
  } finally {
    achievementEditSubmitting.value = false
  }
}

// ==================== 需求编辑弹窗 ====================
const demandEditVisible = ref(false)
const demandEditLoading = ref(false)
const demandEdit = ref(null)
const demandEditSubmitting = ref(false)
const demandEditForm = reactive({
  company_name: '',
  demand_name: '',
  province: '',
  city: '',
  techField: '',
  techFieldOther: '',
  demandType: '',
  demandTypeOther: '',
  overview: '',
  target_problems: '',
  budget: 0,
  budgetUnit: '万元'
})

async function openDemandEditDialog(item) {
  demandEdit.value = item
  demandEditLoading.value = true
  demandEditVisible.value = true

  try {
    const response = await request.get(`/api/publish/requirement/${item.id}`)
    if (response.code === 200) {
      const d = response.data
      demandEdit.value = d
      demandEditForm.company_name = d.company_name || ''
      demandEditForm.demand_name = d.demand_name || ''
      demandEditForm.province = d.region?.province || ''
      demandEditForm.city = d.region?.city || ''
      demandEditForm.techField = (d.tech_fields && d.tech_fields[0]) || ''
      demandEditForm.techFieldOther = d.tech_fields_other || ''
      if ((!d.tech_fields || d.tech_fields.length === 0) && d.tech_fields_other) {
        demandEditForm.techField = '其他'
      }
      demandEditForm.demandType = (d.demand_types && d.demand_types[0]) || ''
      demandEditForm.demandTypeOther = d.demand_types_other || ''
      if ((!d.demand_types || d.demand_types.length === 0) && d.demand_types_other) {
        demandEditForm.demandType = '其他'
      }
      demandEditForm.overview = d.description?.overview || ''
      demandEditForm.target_problems = d.description?.target_problems || ''
      demandEditForm.budget = d.description?.budget || 0
      demandEditForm.budgetUnit = '万元'
    } else {
      alert('加载详情失败')
    }
  } catch (error) {
    console.error('获取需求详情失败:', error)
    alert('获取需求详情失败')
  } finally {
    demandEditLoading.value = false
  }
}

async function submitDemandEdit() {
  if (!demandEdit.value) return
  if (!demandEditForm.demand_name.trim()) {
    alert('请输入需求名称')
    return
  }

  demandEditSubmitting.value = true
  try {
    const response = await request.put(`/api/publish/requirement/${demandEdit.value.id}`, {
      companyName: demandEditForm.company_name,
      demandName: demandEditForm.demand_name,
      province: demandEditForm.province,
      city: demandEditForm.city,
      techField: demandEditForm.techField,
      techFieldOther: demandEditForm.techFieldOther,
      demandType: demandEditForm.demandType,
      demandTypeOther: demandEditForm.demandTypeOther,
      description: demandEditForm.overview,
      expectedProblem: demandEditForm.target_problems,
      budget: demandEditForm.budget,
      budgetUnit: demandEditForm.budgetUnit
    })
    if (response.code === 200) {
      alert('修改成功，已重新提交审核')
      demandEditVisible.value = false
      await fetchUserRequirements()
    } else {
      alert(response.msg || '提交失败')
    }
  } catch (error) {
    console.error('提交失败:', error)
    alert('提交失败，请稍后重试')
  } finally {
    demandEditSubmitting.value = false
  }
}
</script>

<style scoped>
/* 全局样式 */
.personal-container {
  padding: 40px;
  max-width: 1200px;
  margin: 0 auto;
}

/* 页面标题 */
.page-header {
  text-align: left;
  margin-bottom: 40px;
}

.personal-title {
  font-size: 32px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 8px;
  animation: fadeInUp 0.6s ease;
}

.personal-subtitle {
  font-size: 14px;
  color: #909399;
  animation: fadeInUp 0.6s ease 0.2s both;
}

/* 主内容区域 */
.main-content {
  display: flex;
  gap: 30px;
  animation: fadeIn 0.6s ease;
}

/* 左侧侧边栏 */
.sidebar {
  flex: 0 0 200px;
}

.vertical-menu {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  overflow: hidden;
}

.vertical-menu .el-menu-item {
  font-size: 14px;
  padding: 16px 24px;
  margin: 0;
  transition: all 0.3s ease;
}

.vertical-menu .el-menu-item:hover {
  background-color: #f0f9ff;
  color: #409eff;
}

.vertical-menu .el-menu-item.is-active {
  background-color: #ecf5ff;
  color: #409eff;
  font-weight: 600;
}

.vertical-menu .el-menu-item.is-active::after {
  border-right: 2px solid #409eff;
  height: 80%;
}

/* 右侧内容区域 */
.content-area {
  flex: 1;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  padding: 30px;
  min-height: 600px;
}

/* 标签内容样式 */
.tab-content {
  /* 动画由Vue Transition组件处理 */
  position: relative;
}

/* fade过渡动画 */
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}


/* 基本信息样式 */
.basic-info {
  padding: 20px 0;
}

.user-card {
  width: 100%;
  animation: fadeInUp 0.6s ease;
  background: #ffffff;
  border: 1px solid #f0f2f5;
  border-radius: 0;
  padding: 20px;
  transition: none;
}

/* 用户头部信息 */
.user-header {
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e9ecef;
  text-align: right;
}

.user-name {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.welcome-text {
  color: #409eff;
  font-weight: 600;
  margin-right: 8px;
}

.user-role {
  font-size: 14px;
  color: #909399;
  margin-bottom: 0;
}

/* 卡片标题 */
.card-title {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.title-line {
  width: 4px;
  height: 20px;
  background-color: #409eff;
  margin-right: 10px;
  border-radius: 2px;
}

/* 信息部分 */
.info-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 30px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #ffffff;
  border-bottom: 1px solid #f0f2f5;
  border-radius: 0;
  transition: none;
}

.info-item:hover {
  background-color: #f8f9fa;
}

.info-label {
  font-size: 14px;
  color: #606266;
  min-width: 90px;
  flex-shrink: 0;
  font-weight: 500;
}

.info-value {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  flex: 1;
  line-height: 1.5;
}

.status-active {
  color: #67c23a;
}

.status-inactive {
  color: #e6a23c;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  margin-top: 30px;
  border-top: 1px solid #e9ecef;
  padding-top: 20px;
}

.action-buttons .el-button {
  padding: 10px 24px;
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.action-buttons .el-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.action-buttons .el-button--primary {
  background: linear-gradient(135deg, #409eff, #69c0ff);
  border: none;
}

.action-buttons .el-button--danger {
  background: linear-gradient(135deg, #f56c6c, #f78989);
  border: none;
}

/* 列表样式 */
.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  animation: fadeInUp 0.6s ease;
}

.list-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

/* 任务列表 */
.task-list {
  width: 100%;
}

.task-card, .content-card {
  background: #f9fafb;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 16px;
  transition: all 0.3s ease;
  animation: fadeInUp 0.6s ease;
}

.task-card:hover, .content-card:hover {
  background: #f0f2f5;
  transform: translateY(-2px);
}

/* 卡片网格 */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
  width: 100%;
}

.content-card {
  padding: 16px;
}

/* 卡片通用样式 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.card-header .card-title {
  font-size: 16px;
  margin: 0;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-status, .card-type {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.card-status {
  background: #e6f7ff;
  color: #409eff;
}

.card-type {
  background: #f0f9eb;
  color: #67c23a;
}

.demand-status {
  background: #fef0f0;
  color: #f56c6c;
}

.review-status {
  background: #fff7e6;
  color: #e6a23c;
}
.approved-status {
  background: #f6ffed;
  color: #52c41a;
}
.rejected-status {
  background: #fff1f0;
  color: #ff4d4f;
}

/* 审核卡片样式 */
.review-list {
  width: 100%;
}

.review-card {
  background: #ffffff;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  border: 1px solid #e9ecef;
  transition: all 0.3s ease;
  animation: fadeInUp 0.6s ease;
}

.review-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.review-card .card-header {
  margin-bottom: 16px;
}

.review-card .card-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0;
  flex: 1;
}

.review-card .card-meta {
  margin-bottom: 20px;
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
}

.meta-row {
  display: flex;
  align-items: flex-start;
  margin-bottom: 8px;
  gap: 8px;
}

.meta-label {
  min-width: 100px;
  color: #909399;
  font-weight: 500;
  flex-shrink: 0;
}

.meta-value {
  flex: 1;
  color: #303133;
}

.review-card .card-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid #f0f2f5;
}

.loading-state {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px;
  font-size: 14px;
  color: #909399;
}

/* 分页容器 */
.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #f0f2f5;
}

.card-meta {
  margin-bottom: 16px;
  font-size: 14px;
  color: #909399;
  line-height: 1.5;
}

.card-actions {
  text-align: right;
}

/* 动画效果 */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes slideIn {
  from { opacity: 0; transform: translateX(20px); }
  to { opacity: 1; transform: translateX(0); }
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .personal-container {
    padding: 24px;
  }
  .personal-title { font-size: 26px; }
  .sidebar { min-width: 180px; }
  .vertical-menu .el-menu-item { padding: 0 14px; }
}

@media (max-width: 768px) {
  .personal-container {
    padding: 20px;
  }

  .page-header {
    margin-bottom: 30px;
  }

  .personal-title {
    font-size: 24px;
  }
  .personal-subtitle { font-size: 14px; }

  /* 主内容区域变为垂直布局 */
  .main-content {
    flex-direction: column;
    gap: 20px;
  }

  /* 侧边栏变为横向导航 */
  .sidebar {
    flex: 1;
    min-width: auto;
    width: 100%;
    overflow-x: auto;
  }

  .vertical-menu {
    display: flex;
    overflow-x: auto;
    flex-wrap: nowrap;
  }

  .vertical-menu .el-menu-item {
    white-space: nowrap;
    border-right: 1px solid #f0f2f5;
    height: 48px;
    line-height: 48px;
    flex-shrink: 0;
  }

  .vertical-menu .el-menu-item.is-active::after {
    border-right: none;
    border-bottom: 2px solid #409eff;
    width: 80%;
    height: 2px;
  }

  /* 内容区域调整 */
  .content-area {
    padding: 20px;
    min-height: 500px;
  }

  .info-section {
    gap: 16px;
  }

  .info-item {
    padding: 12px;
    flex-direction: column;
    gap: 4px;
  }

  .action-buttons {
    flex-direction: column;
    gap: 12px;
  }
  .action-buttons button {
    width: 100%;
  }

  .list-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .card-grid {
    grid-template-columns: 1fr;
  }
  .card {
    padding: 16px;
  }

  /* 扁平化审核列表响应式调整 */
  .flat-review-item {
    padding: 12px 16px;
  }

  .flat-item-content {
    grid-template-columns: 1fr;
    gap: 8px;
  }

  .flat-item-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .flat-item-title {
    white-space: normal;
    margin-right: 0;
    font-size: 15px;
  }

  .flat-item-actions {
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 8px;
  }
  .flat-item-actions button {
    flex: 1;
    min-width: 80px;
    font-size: 12px;
    padding: 6px 12px;
  }

}

@media (max-width: 480px) {
  .personal-container { padding: 12px; }
  .content-area { padding: 12px; min-height: auto; }
  .personal-title { font-size: 20px; }
  .user-header { margin-bottom: 20px; }
  .user-card { padding: 16px; }
  .form-grid { grid-template-columns: 1fr; gap: 12px; }
  .page-header { margin-bottom: 20px; }
  .vertical-menu .el-menu-item { font-size: 13px; padding: 0 10px; }
  .flat-review-item { padding: 10px 12px; }
}

/* ================= 扁平化审核列表样式 ================= */
.flat-review-list {
  width: 100%;
}

.flat-review-item {
  background: #ffffff;
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 10px;
  border: 1px solid #e9ecef;
  transition: all 0.3s ease;
  cursor: pointer;
  display: flex;
  flex-direction: column;
}

.flat-review-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border-color: #2196f3;
  transform: translateY(-1px);
}

.flat-item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.flat-item-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-right: 12px;
}

.flat-item-status {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
  flex-shrink: 0;
}

.flat-item-content {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 12px;
}

.flat-item-row {
  display: flex;
  align-items: center;
  font-size: 14px;
}

.flat-item-label {
  color: #666;
  margin-right: 8px;
  flex-shrink: 0;
}

.flat-item-value {
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.flat-item-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid #f0f2f5;
}

.reject-reason {
  display: flex;
  align-items: center;
  margin-top: 10px;
  padding: 8px 12px;
  background: #fffbe6;
  border: 1px solid #ffe58f;
  border-radius: 4px;
  font-size: 13px;
  color: #d48806;
  line-height: 1.5;
}

/* ================= 弹窗样式（与管理后台统一） ================= */
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
  background-color: #fff;
  border-radius: 8px;
  width: 500px;
  max-width: 90%;
  max-height: 90%;
  overflow-y: auto;
  border: 1px solid #888;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.modal-lg {
  width: 800px;
  max-width: 95%;
}

.modal-header {
  padding: 16px 24px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #f8fbff;
}

.modal-title {
  font-size: 18px;
  font-weight: bold;
  color: #1890ff;
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
  border-top: 1px solid #f0f0f0;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  background-color: #fafafa;
}

/* 详情区块样式 */
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
  color: #1890ff;
  margin-bottom: 12px;
  padding-left: 8px;
  border-left: 3px solid #1890ff;
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
  background-color: #1890ff;
  color: white;
}
.btn-primary:hover {
  background-color: #096dd9;
}
.btn-default {
  background-color: white;
  color: #1890ff;
  border: 1px solid #1890ff;
}
.btn-default:hover {
  background-color: #e6f7ff;
}
.btn-error {
  background-color: transparent;
  color: #ff4d4f;
  border: 1px solid #ff4d4f;
}
.btn-error:hover {
  background-color: #fff1f0;
  color: #ff4d4f;
  border-color: #ff4d4f;
}
.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 状态标签 */
.status-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
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

/* ================= 未登录提示样式 ================= */
.unauthorized-prompt {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
  padding: 40px;
}
.prompt-container {
  text-align: center;
  background: var(--white);
  padding: 60px 80px;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  max-width: 500px;
  width: 100%;
}
.prompt-container h2 {
  font-size: 28px;
  color: #333;
  margin-bottom: 16px;
}
.prompt-container p {
  font-size: 16px;
  color: #666;
  margin-bottom: 32px;
}
.auth-button {
  background-color: var(--theme-blue);
  color: var(--white);
  border: none;
  padding: 14px 40px;
  border-radius: 30px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}
.auth-button:hover {
  background-color: #0073e6;
}

/* 菜单徽章 */
.menu-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 18px;
  height: 18px;
  padding: 0 4px;
  background-color: #f56c6c;
  color: white;
  font-size: 12px;
  font-weight: 600;
  border-radius: 9px;
  margin-left: 6px;
  vertical-align: middle;
}

/* ================= 表单表格样式（与发布页统一） ================= */
.edit-form {
  width: 100%;
}
.form-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 10px;
}
.form-table th {
  width: 130px;
  padding: 12px 8px;
  text-align: right;
  font-weight: 500;
  color: #606266;
  font-size: 14px;
  vertical-align: top;
  border-bottom: 1px solid #f0f0f0;
}
.form-table td {
  padding: 8px 8px;
  border-bottom: 1px solid #f0f0f0;
}
.form-table .required {
  color: #f56c6c;
  margin-right: 4px;
}
.table-form-item {
  margin-bottom: 0 !important;
}
.table-form-item .el-form-item__content {
  line-height: inherit;
}
.region-selectors {
  display: flex;
  gap: 12px;
}
.region-selectors .el-select {
  width: 160px;
}
.checkbox-vertical {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.radio-with-extra {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.extra-input {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #666;
}
.field-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 8px;
}

/* ================= 我的待办子标签页 ================= */
.todo-sub-tabs {
  display: flex;
  gap: 0;
  margin-bottom: 20px;
  border-bottom: 2px solid #e9ecef;
}

.todo-sub-tab {
  padding: 10px 24px;
  font-size: 14px;
  font-weight: 500;
  color: #606266;
  background: none;
  border: none;
  cursor: pointer;
  position: relative;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 6px;
}

.todo-sub-tab:hover {
  color: #409eff;
}

.todo-sub-tab.active {
  color: #409eff;
}

.todo-sub-tab.active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 100%;
  height: 2px;
  background-color: #409eff;
}

.sub-tab-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  background-color: #f56c6c;
  color: white;
  font-size: 11px;
  font-weight: 600;
  border-radius: 9px;
  line-height: 1;
}

/* ================= 实名认证弹窗 ================= */
.verify-dialog :deep(.el-dialog__body) {
  padding: 0;
}
.verify-dialog {
  border-radius: 12px;
  overflow: hidden;
}

/* 自定义标题栏 */
.verify-dialog-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px 28px 0;
}
.verify-dialog-title {
  font-size: 18px;
  font-weight: 700;
  color: #303133;
  letter-spacing: 0.5px;
}
.verify-dialog-close {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: #f5f5f5;
  border-radius: 50%;
  font-size: 18px;
  color: #999;
  cursor: pointer;
  transition: all 0.2s ease;
  line-height: 1;
  padding: 0;
}
.verify-dialog-close:hover {
  background: #ff4d4f;
  color: #fff;
  transform: rotate(90deg);
}

.verify-body {
  padding: 6px 28px 20px;
}

/* 顶部提示条 */
.verify-banner {
  display: flex;
  align-items: center;
  gap: 10px;
  background: linear-gradient(135deg, #e8f4fd 0%, #f0f9ff 100%);
  border: 1px solid #b3d8f0;
  border-radius: 10px;
  padding: 14px 18px;
  margin-bottom: 24px;
}
.verify-banner-icon {
  font-size: 22px;
  flex-shrink: 0;
}
.verify-banner-text {
  font-size: 13px;
  color: #2c6b9e;
  line-height: 1.5;
  font-weight: 500;
}

/* 步骤标题 */
.verify-step-title {
  font-size: 17px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 6px;
  padding-left: 2px;
}
.verify-step-desc {
  font-size: 13px;
  color: #909399;
  margin-bottom: 22px;
  padding-left: 2px;
  line-height: 1.5;
}

/* 表单 */
.verify-form {
  max-width: 100%;
}
.verify-form :deep(.el-form-item) {
  margin-bottom: 20px;
  flex-wrap: wrap;
}
.verify-form :deep(.el-form-item__label) {
  font-size: 13px;
  font-weight: 600;
  color: #606266;
  padding-bottom: 6px;
  line-height: 1.5;
  height: auto;
  float: none;
  display: block;
  text-align: left;
}
.verify-form :deep(.el-form-item__content) {
  width: 100%;
  flex: 0 0 100%;
  margin-left: 0 !important;
  display: block;
}
.verify-input-wrapper {
  position: relative;
  width: 100%;
}
.verify-input-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  z-index: 2;
  font-size: 16px;
  pointer-events: none;
  line-height: 1;
}
.verify-input :deep(.el-input__wrapper) {
  padding-left: 44px;
  border-radius: 8px;
  box-shadow: 0 0 0 1px #dcdfe6 inset;
  transition: all 0.25s ease;
  background: #fafafa;
}
.verify-input :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #409eff inset;
}
.verify-input :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #409eff inset, 0 0 0 3px rgba(64,158,255,0.12);
  background: #fff;
}
.verify-input :deep(.el-input__inner) {
  height: 44px;
  font-size: 14px;
}
.verify-input :deep(.el-input.is-disabled .el-input__wrapper) {
  background: #f5f7fa;
  box-shadow: 0 0 0 1px #e4e7ed inset;
}
.verify-input :deep(.el-input.is-disabled .el-input__inner) {
  color: #606266;
  -webkit-text-fill-color: #606266;
  font-weight: 600;
}

/* 验证码行 */
.verify-code-row {
  display: flex;
  gap: 12px;
  width: 100%;
  align-items: flex-start;
}
.verify-code-btn {
  flex-shrink: 0;
  height: 44px;
  padding: 0 18px;
  border-radius: 8px;
  border: 1px solid #409eff;
  color: #409eff;
  background: #fff;
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
  transition: all 0.25s ease;
  min-width: 100px;
}
.verify-code-btn:hover:not(:disabled) {
  background: #ecf5ff;
  border-color: #409eff;
}
.verify-code-btn:disabled {
  border-color: #dcdfe6;
  color: #c0c4cc;
  background: #f5f7fa;
  cursor: not-allowed;
}

/* 底部按钮 */
.verify-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 8px;
  border-top: 1px solid #f0f0f0;
  margin-top: 6px;
}
.verify-btn {
  height: 42px;
  padding: 0 28px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.25s ease;
}
.verify-btn-cancel {
  border: 1px solid #dcdfe6;
  color: #606266;
  background: #fff;
}
.verify-btn-cancel:hover {
  color: #409eff;
  border-color: #409eff;
  background: #ecf5ff;
}
.verify-btn-primary {
  background: linear-gradient(135deg, #409eff 0%, #1890ff 100%);
  border: none;
  color: #fff;
  box-shadow: 0 4px 12px rgba(64,158,255,0.35);
}
.verify-btn-primary:hover {
  box-shadow: 0 6px 20px rgba(64,158,255,0.5);
  transform: translateY(-1px);
}
.verify-btn-primary:active {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(64,158,255,0.3);
}
.verify-btn-primary span {
  margin-right: 4px;
  font-size: 15px;
}

/* 动画 */
.verify-step-content {
  animation: verifyFadeIn 0.35s ease;
}
@keyframes verifyFadeIn {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* ================= 修改信息 / 修改密码弹窗 ================= */
.profile-dialog {
  border-radius: 12px;
  overflow: hidden;
}
.profile-dialog :deep(.el-dialog__body) {
  padding: 0;
}

/* 自定义标题栏 */
.profile-dialog-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px 28px 0;
}
.profile-dialog-title {
  font-size: 18px;
  font-weight: 700;
  color: #303133;
  letter-spacing: 0.5px;
}
.profile-dialog-close {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: #f5f5f5;
  border-radius: 50%;
  font-size: 18px;
  color: #999;
  cursor: pointer;
  transition: all 0.2s ease;
  line-height: 1;
  padding: 0;
}
.profile-dialog-close:hover {
  background: #ff4d4f;
  color: #fff;
  transform: rotate(90deg);
}

.profile-body {
  padding: 6px 28px 20px;
}

/* 顶部提示条 */
.profile-banner {
  display: flex;
  align-items: center;
  gap: 10px;
  background: linear-gradient(135deg, #e8f4fd 0%, #f0f9ff 100%);
  border: 1px solid #b3d8f0;
  border-radius: 10px;
  padding: 14px 18px;
  margin-bottom: 24px;
}
.profile-banner-warn {
  background: linear-gradient(135deg, #fff7e6 0%, #fffbe6 100%);
  border-color: #ffe58f;
}
.profile-banner-warn .profile-banner-text {
  color: #ad8b3a;
}
.profile-banner-icon {
  font-size: 22px;
  flex-shrink: 0;
}
.profile-banner-text {
  font-size: 13px;
  color: #2c6b9e;
  line-height: 1.5;
  font-weight: 500;
}

/* 表单 */
.profile-form {
  max-width: 100%;
}
.profile-form :deep(.el-form-item) {
  margin-bottom: 20px;
  flex-wrap: wrap;
}
.profile-form :deep(.el-form-item__label) {
  font-size: 13px;
  font-weight: 600;
  color: #606266;
  padding-bottom: 6px;
  line-height: 1.5;
  height: auto;
  float: none;
  display: block;
  text-align: left;
}
.profile-form :deep(.el-form-item__content) {
  width: 100%;
  flex: 0 0 100%;
  margin-left: 0 !important;
  display: block;
}
.profile-input-wrapper {
  position: relative;
  width: 100%;
}
.profile-input-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  z-index: 2;
  font-size: 16px;
  pointer-events: none;
  line-height: 1;
}
.profile-input :deep(.el-input__wrapper) {
  padding-left: 44px;
  border-radius: 8px;
  box-shadow: 0 0 0 1px #dcdfe6 inset;
  transition: all 0.25s ease;
  background: #fafafa;
}
.profile-input :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #409eff inset;
}
.profile-input :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #409eff inset, 0 0 0 3px rgba(64,158,255,0.12);
  background: #fff;
}
.profile-input :deep(.el-input__inner) {
  height: 44px;
  font-size: 14px;
}
.profile-input :deep(.el-input.is-disabled .el-input__wrapper) {
  background: #f5f7fa;
  box-shadow: 0 0 0 1px #e4e7ed inset;
}
.profile-input :deep(.el-input.is-disabled .el-input__inner) {
  color: #606266;
  -webkit-text-fill-color: #606266;
  font-weight: 600;
}

/* 验证码行 */
.profile-code-row {
  display: flex;
  gap: 12px;
  width: 100%;
  align-items: flex-start;
}
.profile-code-btn {
  flex-shrink: 0;
  height: 44px;
  padding: 0 18px;
  border-radius: 8px;
  border: 1px solid #409eff;
  color: #409eff;
  background: #fff;
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
  transition: all 0.25s ease;
  min-width: 100px;
}
.profile-code-btn:hover:not(:disabled) {
  background: #ecf5ff;
  border-color: #409eff;
}
.profile-code-btn:disabled {
  border-color: #dcdfe6;
  color: #c0c4cc;
  background: #f5f7fa;
  cursor: not-allowed;
}
.profile-code-hint {
  font-size: 12px;
  color: #909399;
  margin-top: 6px;
  padding-left: 2px;
}

/* 底部按钮 */
.profile-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 8px;
  border-top: 1px solid #f0f0f0;
  margin-top: 6px;
}
.profile-btn {
  height: 42px;
  padding: 0 28px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.25s ease;
}
.profile-btn-cancel {
  border: 1px solid #dcdfe6;
  color: #606266;
  background: #fff;
}
.profile-btn-cancel:hover {
  color: #409eff;
  border-color: #409eff;
  background: #ecf5ff;
}
.profile-btn-primary {
  background: linear-gradient(135deg, #409eff 0%, #1890ff 100%);
  border: none;
  color: #fff;
  box-shadow: 0 4px 12px rgba(64,158,255,0.35);
}
.profile-btn-primary:hover {
  box-shadow: 0 6px 20px rgba(64,158,255,0.5);
  transform: translateY(-1px);
}
.profile-btn-primary:active {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(64,158,255,0.3);
}
</style>