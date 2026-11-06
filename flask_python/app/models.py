from .extensions import db
from datetime import datetime


# 用户模型（和登录注册代码完全对应）
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=True)  # 用户名，可选
    real_name = db.Column(db.String(30), nullable=True)  # 真实姓名，可选
    id_card = db.Column(db.String(20), unique=True, nullable=True)  # 身份证号，唯一，可选
    phone = db.Column(db.String(11), unique=True, nullable=False)  # 手机号，必填
    password_hash = db.Column(db.String(255), nullable=False)  # 加密后的密码
    role = db.Column(db.String(20), default='common')  # 角色：common普通用户/agent客服
    status = db.Column(db.Integer, default=1)  # 状态：1正常/0禁用
    last_active = db.Column(db.DateTime, default=datetime.now)  # 最后活动时间
    created_at = db.Column(db.DateTime, default=datetime.now)  # 注册时间

    @property
    def is_agent(self):
        return self.role in ['agent']

    @property
    def is_admin(self):
        return self.role == 'admin'


# 审核记录模型
class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    biz_type = db.Column(db.String(20), nullable=False)         # achievement 或 demand
    biz_id = db.Column(db.String(50), nullable=False)                # 被审核的成果/需求编号（如 CG2025001）
    admin_id = db.Column(db.Integer, nullable=False)              # 执行审核的管理员ID
    result = db.Column(db.Integer, nullable=False)                # 1=approved 0=rejected
    reason = db.Column(db.String(255), nullable=True)             # 不通过原因（通过时为NULL）
    create_time = db.Column(db.DateTime, default=datetime.now)


# 系统消息模型
class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    send_user_id = db.Column(db.Integer, default=0, nullable=False)  # 发送者ID（0=系统）
    receive_user_id = db.Column(db.Integer, nullable=False)           # 接收用户ID（0=全体普通用户广播）
    msg_type = db.Column(db.String(20), nullable=False)               # audit/result/system
    biz_type = db.Column(db.String(20), nullable=False, default='')    # achievement/demand
    biz_id = db.Column(db.String(50), nullable=False, default='')
    title = db.Column(db.String(100), nullable=False, default='')      # 消息标题
    content = db.Column(db.String(500), nullable=False, default='')    # 消息内容
    is_read = db.Column(db.Integer, default=0)                         # 0未读 1已读（对广播消息无意义）
    create_time = db.Column(db.DateTime, default=datetime.now)
    read_time = db.Column(db.DateTime, nullable=True)


class MessageReadStatus(db.Model):
    """广播消息（receive_user_id=0）的每用户已读状态"""
    __tablename__ = 'message_reads'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    message_id = db.Column(db.Integer, nullable=False)                 # 关联消息ID
    user_id = db.Column(db.Integer, nullable=False)                    # 已读用户ID
    read_time = db.Column(db.DateTime, default=datetime.now)

# 通用聊天消息模型（已迁移到 MongoDB，详见 mongo_models.py 中的 MongoChatMessage）
# class ChatMessage(db.Model):
#     __bind_key__ = 'chat'  # 绑定到SQLite数据库
#     __tablename__ = 'chat_message'
#     id = db.Column(db.Integer, primary_key=True)
#     room_id = db.Column(db.String(100), nullable=False, index=True)  # 房间ID，用于区分不同用户/会话
#     sender = db.Column(db.String(20), nullable=False)  # 发送者类型: user, bot, admin, system
#     content = db.Column(db.Text, nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.now)


# 编辑器专属用户模型
class EditorUser(db.Model):
    __tablename__ = 'editor_user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    account = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='editor')
    created_at = db.Column(db.DateTime, default=datetime.now)


# 动态可编辑页面模型
class DynamicPage(db.Model):
    __tablename__ = 'dynamic_pages'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    page_path = db.Column(db.String(100), unique=True, nullable=False)
    page_name = db.Column(db.String(100), nullable=False)
    html_content = db.Column(db.Text(16777215))   # MEDIUMTEXT ~16MB，TEXT只有64KB不够用
    css_content = db.Column(db.Text(16777215))    # MEDIUMTEXT ~16MB
    gjs_data = db.Column(db.Text(4294967295))     # LONGTEXT ~4GB，GrapesJS项目数据可能很大
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


# 站点配置模型（键值对存储）
class SiteConfig(db.Model):
    __tablename__ = 'site_configs'
    id = db.Column(db.Integer, primary_key=True)
    config_key = db.Column(db.String(50), unique=True, nullable=False)
    config_value = db.Column(db.Text)


# 客服状态表（已迁移到 MongoDB，详见 mongo_models.py 中的 MongoAgentStatus）
# class AgentStatus(db.Model):
#     __bind_key__ = 'chat'  # 绑定到SQLite数据库
#     __tablename__ = 'agent_status'
#     user_id = db.Column(db.Integer, primary_key=True)  # 客服用户ID
#     status = db.Column(db.String(20), default='offline')  # online, offline, busy
#     current_session_id = db.Column(db.Integer, nullable=True)  # 当前处理的会话ID
#     last_heartbeat = db.Column(db.DateTime, default=datetime.now)
