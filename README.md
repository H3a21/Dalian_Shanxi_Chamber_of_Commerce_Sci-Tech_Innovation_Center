# 大连山西商会科创中心【项目代码量5w行左右】

网站：https://kczx.net/

## 技术说明

本项目采用前后端分离架构，前端基于 Vue 3 + Element Plus 构建 SPA 应用，后端基于 Flask 提供 RESTful API 和 WebSocket 服务，支持多数据库混合存储。

### 前端技术栈

| 技术 | 用途 |
|------|------|
| **Vue 3** (Composition API) | 核心前端框架，使用 `<script setup>` 语法和组合式 API 构建组件 |
| **Vue Router 4** | 前端路由管理，支持导航守卫（角色鉴权）和路由级懒加载 |
| **Pinia 3** | 状态管理（替代 Vuex），集中管理认证状态、用户信息 |
| **Element Plus 2** | UI 组件库，提供表格、表单、弹窗、下拉菜单等开箱即用的组件（使用中文语言包） |
| **Axios** | HTTP 请求库，封装统一的请求/响应拦截器（自动携带 Token、统一错误处理） |
| **ECharts 6** | 数据可视化图表库，用于后台管理页面的数据统计展示 |
| **Socket.IO Client 4** | WebSocket 客户端，实现即时通讯（在线客服、消息推送） |
| **GrapesJS 0.22** | 拖拽式页面构建器，支持可视化编辑页面（集成 20+ 插件：区块、Flexbox、表单、标签页、样式滤镜、背景图、自定义代码等） |
| **Vue CLI 5** | 项目脚手架与构建工具，集成 Babel 转译和 ESLint 代码检查 |

### 后端技术栈

| 技术 | 用途 |
|------|------|
| **Flask 3.1** | 核心 Web 框架，采用蓝图（Blueprint）模块化组织路由 |
| **Flask-SQLAlchemy 3.1** | ORM 框架，管理 MySQL 数据模型和数据库迁移 |
| **Flask-SocketIO 5.6** | WebSocket 服务端，支持全双工实时通信（聊天、在线状态推送） |
| **Flask-JWT-Extended 4.7** | JWT 认证，提供 access_token 签发、验证、刷新和声明管理 |
| **Flask-CORS** | 跨域资源共享配置，支持前后端分离开发 |
| **PyMySQL** | MySQL 数据库驱动 |
| **Redis** | 缓存服务（短信验证码存储、人机验证 IP 追踪） |
| **PyMongo 4.16** | MongoDB 数据库驱动（聊天记录、FAQ、内容集合） |
| **APScheduler 3.11** | 定时任务调度器（用于计划任务、过期清理等） |
| **Gevent 24.10** | 协程并发支持，提升 WebSocket 长连接性能 |
| **Werkzeug** | WSGI 工具集，提供密码哈希（`generate_password_hash` / `check_password_hash`） |
| **Gunicorn** | 生产环境 WSGI 服务器（配合 gevent worker 部署） |
| **阿里云 SDK** | 短信服务（`alibabacloud-dysmsapi`）和实人认证（`alibabacloud-cloudauth`） |

### 数据库选型

| 数据库 | 用途 |
|--------|------|
| **MySQL** | 用户账户、角色权限、会话管理、站点配置等结构化核心数据 |
| **MongoDB** | 聊天消息、FAQ 知识库、成果/需求/专家/合作伙伴等业务文档型数据 |
| **Redis** | 短信验证码缓存、人机验证 IP 限流、临时会话缓存 |

### 部署架构

```
用户浏览器
    ↓ HTTPS
Nginx（反向代理 + SSL 终结 + 静态资源托管）
    ↓ proxy_pass
Gunicorn + Gevent Worker（WSGI 服务器，运行 Flask 应用）
    ├── MySQL（主数据库）
    ├── MongoDB（文档数据库）
    └── Redis（缓存数据库）
```

- 生产环境使用 **Gunicorn + Gevent** 作为 WSGI 服务器，单 worker 多协程模式
- Nginx 负责静态资源托管、SSL 证书、反向代理和 WebSocket 升级
- 前端构建产物（`dist/`）由 Nginx 直接托管，API 请求反向代理至 Flask 后端
- 所有敏感配置通过 **环境变量** 注入，不写在代码中

## Vue3(当前目录下)

Vue3项目运行：[命令行进入到这个项目的根目录运行下面指令]

    npm install
    npm run serve

## Flask后端(./flask_python)

flask后端运行：[直接运行app.py程序，记得修改config.py里面的配置信息]

    python ./run.py

## 项目目录结构说明：(本仓库代码中的关键信息已经用"#####"替换掉，包括：数据库名、端口号、连接信息等等)

    flask_web/                              # 项目根目录
    ├── dist/                               # npm run build 生成的生产环境静态文件（开发时无需关注）
    │   ├── css/                            # 打包后的样式文件（压缩、合并）
    │   ├── js/                             # 打包后的 JS 文件（应用逻辑、第三方库等）
    │   ├── favicon.ico                     # 网站图标
    │   └── index.html                      # 单页应用入口，自动加载上述 css 和 js 文件
    ├── flask_python/                       # Flask 后端目录
    │   ├── app.py                          # Flask 应用主入口（旧版，如需开发请使用 run.py）
    │   ├── run.py                          # Flask 应用主入口（新版，推荐使用）
    │   ├── config.py                       # 配置文件（MySQL、Redis、MongoDB 等连接信息）
    │   ├── requirements.txt                # Python 依赖包列表
    │   ├── mysql.sql                       # 初始数据库脚本（MySQL）
    │   ├── nginx.conf                      # Nginx 反向代理配置模板
    │   ├── .htaccess                       # Apache 伪静态规则占位
    │   ├── app/                            # 应用核心代码包
    │   │   ├── __init__.py                 # Flask 应用工厂，初始化 app、扩展、蓝图等
    │   │   ├── extensions.py               # 扩展初始化（SQLAlchemy、SocketIO、JWT 等）
    │   │   ├── models.py                   # MySQL / SQLAlchemy 数据模型
    │   │   ├── mongo_models.py             # MongoDB 数据模型
    │   │   ├── mongo_adapter.py            # MongoDB 连接适配器
    │   │   ├── services.py                 # 通用业务逻辑服务
    │   │   ├── faq_service.py              # 常见问题（FAQ）服务
    │   │   ├── publish_service.py          # 内容发布服务
    │   │   ├── socket_events.py            # WebSocket / SocketIO 事件处理
    │   │   ├── auth/                       # 认证模块
    │   │   │   ├── routes.py               # 登录、注册、短信、找回密码等路由
    │   │   │   ├── cloud_auth_service.py   # 阿里云实人认证服务
    │   │   │   └── sms_service.py          # 阿里云短信服务
    │   │   ├── chat/                       # 聊天模块
    │   │   │   └── routes.py               # WebSocket 消息路由
    │   │   ├── editor/                     # 富文本编辑器模块
    │   │   │   ├── __init__.py             # 编辑器蓝图初始化
    │   │   │   └── routes.py               # 编辑器相关路由
    │   │   ├── publish/                    # 发布模块
    │   │   │   └── routes.py               # 内容发布相关路由
    │   │   └── uploads/                    # 上传文件临时存储目录
    │   │       └── site_config/            # 站点配置上传文件
    │   ├── static/                         # Flask 静态资源
    │   │   └── editor-assets/              # 编辑器资源（files/、images/）
    │   ├── experts_images/                 # 专家头像图片
    │   ├── financial_services_images/      # 金融服务相关图片
    │   ├── partners_images/                # 合作伙伴图片
    │   └── uploads/                        # 用户上传文件存储目录
    ├── src/                                # Vue 前端源代码
    │   ├── assets/                         # 需要 Webpack 处理的静态资源（全局 CSS、图片、字体等）
    │   │   ├── beian.png                   # 备案图标
    │   │   ├── find.png                    # 搜索图标
    │   │   └── logo.png                    # 网站 Logo
    │   ├── components/                     # 可复用的 UI 组件
    │   │   ├── AchievementCenterDetail.vue # 成果中心详情弹窗
    │   │   ├── ChatWidget.vue              # 聊天窗口组件
    │   │   ├── DemandCenterDetail.vue      # 需求中心详情弹窗
    │   │   └── HelloWorld.vue              # 示例组件
    │   ├── composables/                    # 可复用的组合式函数（Vue 3 Composition API）
    │   │   ├── useAuth.js                  # 用户认证状态管理
    │   │   └── useClickGuard.js            # 防重复点击守卫
    │   ├── router/                         # Vue Router 路由配置
    │   │   └── index.js                    # 路由表定义
    │   ├── utils/                          # 工具函数
    │   │   ├── centerDetailMappers.js      # 详情数据映射器
    │   │   ├── format.js                   # 格式化工具（日期、数字等）
    │   │   └── request.js                  # HTTP 请求封装（axios）
    │   ├── views/                          # 页面级 Vue 组件
    │   │   ├── HomeView.vue                # 首页
    │   │   ├── AboutView.vue               # 关于我们
    │   │   ├── AuthView.vue                # 登录/注册
    │   │   ├── CaptchaView.vue             # 验证码页面
    │   │   ├── ForgotPasswordView.vue      # 找回密码
    │   │   ├── ProfileView.vue             # 个人资料
    │   │   ├── PersonalCenterView.vue      # 个人中心
    │   │   ├── ExpertView.vue              # 专家库
    │   │   ├── FinancialView.vue           # 金融服务
    │   │   ├── PartnerView.vue             # 合作伙伴
    │   │   ├── AchievementView.vue         # 成果中心
    │   │   ├── AchievementDetailView.vue   # 成果详情
    │   │   ├── DemandCenterView.vue        # 需求中心
    │   │   ├── DynamicPageView.vue         # 动态页面
    │   │   ├── PublishView.vue             # 发布页面
    │   │   ├── RequireView.vue             # 需求发布
    │   │   ├── MessagesView.vue            # 消息中心
    │   │   ├── Adminview.vue               # 后台管理首页
    │   │   ├── AdminChatView.vue           # 后台聊天管理
    │   │   ├── AdminEditorView.vue         # 后台富文本编辑
    │   │   ├── PrivacyView.vue             # 隐私政策
    │   │   ├── TermsView.vue               # 服务条款
    │   │   └── PlaceholderView.vue         # 占位页面
    │   ├── App.vue                         # 整个 Vue 应用的根组件（含路由视图及全局布局）
    │   └── main.js                         # 应用入口文件，创建 Vue 实例
    ├── public/                             # Vue 项目的静态资源（不经 Webpack 处理，直接复制到 dist）
    │   ├── favicon.ico                     # 网站图标
    │   ├── index.html                      # 主页模板（Vue 挂载点）
    │   └── beian.png                       # 备案图标    
    ├── 部署/                               # 部署相关文件
    │   ├── nginx.conf                      # Nginx 配置文件副本
    │   └── 启动指令.txt                    # 生产环境启动命令说明
    ├── .env                                # 开发环境环境变量（敏感配置，不提交到仓库）
    ├── .env.production                     # 生产环境环境变量
    ├── babel.config.js                     # Babel 配置（将 ES6+/JSX 转译为浏览器兼容的 ES5）
    ├── jsconfig.json                       # VSCode 路径别名智能提示配置
    ├── package.json                        # Node.js 项目清单（依赖、脚本、元信息）
    ├── package-lock.json                   # 锁定全部依赖的精确版本号，确保安装一致性
    ├── vue.config.js                       # Vue CLI 自定义配置（覆盖默认 Webpack 配置）
    └── README.md                           # 本文件，项目说明文档

## 网站效果展示

以下是项目的实际运行效果截图（共 36 张）：

> 点击图片可查看大图（部分浏览器支持在新标签页中打开）

### 前台页面

<table>
  <tr>
    <td align="center" width="50%"><b>首页</b><br><img src="./images_demo/5.png" alt="首页" width="100%"></td>
    <td align="center" width="50%"><b>登录</b><br><img src="./images_demo/1.png" alt="登录" width="100%"></td>
  </tr>
  <tr>
    <td align="center" width="50%"><b>注册</b><br><img src="./images_demo/2.png" alt="注册" width="100%"></td>
    <td align="center" width="50%"><b>忘记密码</b><br><img src="./images_demo/4.png" alt="忘记密码" width="100%"></td>
  </tr>
  <tr>
    <td align="center" width="50%"><b>用户服务协议</b><br><img src="./images_demo/3.png" alt="用户服务协议" width="100%"></td>
    <td align="center" width="50%"><b>关于我们</b><br><img src="./images_demo/13.png" alt="关于我们" width="100%"></td>
  </tr>
  <tr>
    <td align="center" width="50%"><b>成果中心</b><br><img src="./images_demo/6.png" alt="成果中心" width="100%"></td>
    <td align="center" width="50%"><b>企业需求</b><br><img src="./images_demo/7.png" alt="企业需求" width="100%"></td>
  </tr>
  <tr>
    <td align="center" width="50%"><b>项目孵化</b><br><img src="./images_demo/8.png" alt="项目孵化" width="100%"></td>
    <td align="center" width="50%"><b>人才培养</b><br><img src="./images_demo/9.png" alt="人才培养" width="100%"></td>
  </tr>
  <tr>
    <td align="center" width="50%"><b>专家中心</b><br><img src="./images_demo/10.png" alt="专家中心" width="100%"></td>
    <td align="center" width="50%"><b>合作伙伴</b><br><img src="./images_demo/11.png" alt="合作伙伴" width="100%"></td>
  </tr>
  <tr>
    <td align="center" width="50%"><b>金融服务</b><br><img src="./images_demo/12.png" alt="金融服务" width="100%"></td>
    <td align="center" width="50%"><b>消息中心</b><br><img src="./images_demo/14.png" alt="消息中心" width="100%"></td>
  </tr>
</table>

### 后台管理

<table>
  <tr>
    <td align="center" width="50%"><b>管理 - 仪表板</b><br><img src="./images_demo/22.png" alt="管理 - 仪表板" width="100%"></td>
    <td align="center" width="50%"><b>基本信息</b><br><img src="./images_demo/15.png" alt="基本信息" width="100%"></td>
  </tr>
  <tr>
    <td align="center" width="50%"><b>我的待办</b><br><img src="./images_demo/16.png" alt="我的待办" width="100%"></td>
    <td align="center" width="50%"><b>成果审核</b><br><img src="./images_demo/17.png" alt="成果审核" width="100%"></td>
  </tr>
  <tr>
    <td align="center" width="50%"><b>需求审核</b><br><img src="./images_demo/18.png" alt="需求审核" width="100%"></td>
    <td align="center" width="50%"><b>管理 - 用户管理</b><br><img src="./images_demo/21.png" alt="管理 - 用户管理" width="100%"></td>
  </tr>
  <tr>
    <td align="center" width="50%"><b>管理 - 访客日志</b><br><img src="./images_demo/19.png" alt="管理 - 访客日志" width="100%"></td>
    <td align="center" width="50%"><b>管理 - 内容管理</b><br><img src="./images_demo/29.png" alt="管理 - 内容管理" width="100%"></td>
  </tr>
  <tr>
    <td align="center" width="50%"><b>管理 - 网站编辑</b><br><img src="./images_demo/30.png" alt="管理 - 网站编辑" width="100%"></td>
    <td align="center" width="50%"><b>管理 - 合作伙伴</b><br><img src="./images_demo/20.png" alt="管理 - 合作伙伴" width="100%"></td>
  </tr>
  <tr>
    <td align="center" width="50%"><b>管理 - 专家中心</b><br><img src="./images_demo/31.png" alt="管理 - 专家中心" width="100%"></td>
    <td align="center" width="50%"><b>管理 - 客服管理</b><br><img src="./images_demo/32.png" alt="管理 - 客服管理" width="100%"></td>
  </tr>
  <tr>
    <td align="center" width="50%"><b>管理 - 金融服务</b><br><img src="./images_demo/26.png" alt="管理 - 金融服务" width="100%"></td>
    <td align="center" width="50%"><b>管理 - 合作申请</b><br><img src="./images_demo/27.png" alt="管理 - 合作申请" width="100%"></td>
  </tr>
  <tr>
    <td align="center" width="50%"><b>管理 - FAQ管理</b><br><img src="./images_demo/28.png" alt="管理 - FAQ管理" width="100%"></td>
    <td align="center" width="50%"><b>管理 - 发送通知</b><br><img src="./images_demo/23.png" alt="管理 - 发送通知" width="100%"></td>
  </tr>
  <tr>
    <td align="center" width="50%"><b>管理 - 发送通知 - 消息管理</b><br><img src="./images_demo/33.png" alt="管理 - 发送通知 - 消息管理" width="100%"></td>
    <td align="center" width="50%"><b>管理 - 仪表板</b><br><img src="./images_demo/24.png" alt="管理 - 仪表板" width="100%"></td>
  </tr>
  <tr>
    <td align="center" width="50%"><b>管理 - 仪表板</b><br><img src="./images_demo/25.png" alt="管理 - 仪表板" width="100%"></td>
    <td align="center" width="50%"><b>网站可编辑器</b><br><img src="./images_demo/34.png" alt="网站可编辑器" width="100%"></td>
  </tr>
</table>

### 其他

<table>
  <tr>
    <td align="center" width="50%"><b>客服界面</b><br><img src="./images_demo/35.png" alt="客服界面" width="100%"></td>
    <td align="center" width="50%"><b>普通用户界面</b><br><img src="./images_demo/36.png" alt="普通用户界面" width="100%"></td>
  </tr>
</table>

## 开发成员9名(名字不分先后)

Zhang Kun、Dou Jiansheng、Song Chengjia、Hu Jiarui、Xiang Zhihang、Zhang Jianing、You Hancheng、Zhang Yiwen、Wang Ying
