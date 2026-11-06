"""
MongoDB 模型定义 - 按照客服服务表数据设计规范
采用文档嵌入模式，提高查询性能
"""
from datetime import datetime
from bson import ObjectId
from .mongo_adapter import MongoModel

# 枚举常量定义
VALID_SENDER_TYPES = {'user', 'agent', 'system'}
VALID_MSG_TYPES = {'text', 'image', 'file', 'system'}
VALID_SESSION_STATUS = {'pending', 'waiting', 'active', 'closed'}
VALID_CLOSE_TYPES = {'agent_closed', 'user_closed', 'system_auto_closed', 'timeout'}
VALID_ONLINE_STATUS = {'online', 'offline', 'busy'}
VALID_FAQ_STATUS = {'draft', 'published'}
VALID_CHAT_SENDER_TYPES = {'user', 'bot', 'admin', 'system'}

# 成果和需求相关枚举
VALID_ACHIEVEMENT_STATUS = {'pending', 'approved', 'rejected'}
VALID_REQUIREMENT_STATUS = {'pending', 'approved', 'rejected'}
VALID_TECH_MATURITY = {'实验室理论阶段', '中试阶段', '可规模量产'}
VALID_DEMAND_TYPES = {'技术需求', '金融需求', '场景需求', '其他'}
VALID_MATCH_STATUS = {'待对接', '对接中', '已完成'}


class Message:
    """消息结构（嵌入在 Session 文档中）"""

    def __init__(self, **kwargs):
        self._id = kwargs.get('_id', ObjectId())

        # 验证并设置 sender_type
        sender_type = kwargs.get('sender_type')
        if sender_type not in VALID_SENDER_TYPES:
            raise ValueError(f"无效的 sender_type: {sender_type}，有效值: {VALID_SENDER_TYPES}")
        self.sender_type = sender_type

        self.sender_id = kwargs.get('sender_id')      # 发送者用户ID
        self.content = kwargs.get('content', '')      # 消息内容

        # 验证并设置 msg_type
        msg_type = kwargs.get('msg_type', 'text')
        if msg_type not in VALID_MSG_TYPES:
            raise ValueError(f"无效的 msg_type: {msg_type}，有效值: {VALID_MSG_TYPES}")
        self.msg_type = msg_type

        self.is_read = kwargs.get('is_read', False)   # 是否已读
        self.created_at = kwargs.get('created_at', datetime.now())  # 发送时间

    def to_dict(self):
        """转换为字典"""
        return {
            '_id': self._id,
            'sender_type': self.sender_type,
            'sender_id': self.sender_id,
            'content': self.content,
            'msg_type': self.msg_type,
            'is_read': self.is_read,
            'created_at': self.created_at
        }

    @classmethod
    def from_dict(cls, data):
        """从字典创建 Message 实例"""
        if not data:
            return None
        return cls(
            _id=data.get('_id'),
            sender_type=data.get('sender_type'),
            sender_id=data.get('sender_id'),
            content=data.get('content'),
            msg_type=data.get('msg_type', 'text'),
            is_read=data.get('is_read', False),
            created_at=data.get('created_at')
        )


class Session(MongoModel):
    """客服会话表（单会话单文档，消息直接嵌入）"""

    def __init__(self, **kwargs):
        self._id = kwargs.get('_id', ObjectId())
        self.user_id = kwargs.get('user_id')                     # 发起用户ID
        self.agent_id = kwargs.get('agent_id')                # 接待客服ID，未分配时为None

        # 验证并设置 status
        status = kwargs.get('status', 'pending')
        if status not in VALID_SESSION_STATUS:
            raise ValueError(f"无效的 status: {status}，有效值: {VALID_SESSION_STATUS}")
        self.status = status

        self.reference_type = kwargs.get('reference_type')        # 关联类型: achievement/demand
        self.reference_id = kwargs.get('reference_id')            # 关联ID

        self.messages = kwargs.get('messages', [])               # 消息列表（嵌入）
        self.created_at = kwargs.get('created_at', datetime.now())  # 会话创建时间
        self.closed_at = kwargs.get('closed_at')                 # 会话关闭时间

        # 验证并设置 close_type
        close_type = kwargs.get('close_type')
        if close_type and close_type not in VALID_CLOSE_TYPES:
            raise ValueError(f"无效的 close_type: {close_type}，有效值: {VALID_CLOSE_TYPES}")
        self.close_type = close_type

        self.updated_at = kwargs.get('updated_at', datetime.now())  # 最后更新时间

        # 处理 messages 列表，确保都是 Message 对象
        if self.messages and isinstance(self.messages[0], dict):
            self.messages = [Message.from_dict(msg) for msg in self.messages]

        # 记录已保存的消息数，用于 save() 时增量推送新消息
        self._saved_message_count = len(self.messages)

    @classmethod
    def init_collection(cls, db):
        """初始化集合和索引"""
        cls._collection = db.sessions
        # 创建索引
        cls._collection.create_index('user_id')
        cls._collection.create_index('agent_id')
        cls._collection.create_index('status')
        cls._collection.create_index([('created_at', 1)])
        cls._collection.create_index([('updated_at', 1)])
        # 唯一索引：确保每个用户最多只有一个 pending 状态的会话（防止竞态条件导致重复）
        try:
            cls._collection.create_index(
                [('user_id', 1)],
                unique=True,
                partialFilterExpression={'status': 'pending'}
            )
        except Exception as e:
            print(f"[WARN] 创建 pending 唯一索引失败（可能已有重复数据）: {e}")
        print(f"[OK] MongoDB 集合初始化: sessions")

    def to_dict(self):
        """转换为字典（用于保存到 MongoDB）"""
        data = {
            '_id': self._id,
            'user_id': self.user_id,
            'agent_id': self.agent_id,
            'status': self.status,
            'messages': [msg.to_dict() for msg in self.messages] if self.messages else [],
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        if self.reference_type:
            data['reference_type'] = self.reference_type
        if self.reference_id:
            data['reference_id'] = self.reference_id
        if self.closed_at:
            data['closed_at'] = self.closed_at
        if self.close_type:
            data['close_type'] = self.close_type
        return data

    @classmethod
    def from_dict(cls, data):
        """从字典创建 Session 实例"""
        if not data:
            return None
        return cls(
            _id=data.get('_id'),
            user_id=data.get('user_id'),
            agent_id=data.get('agent_id'),
            status=data.get('status', 'pending'),
            reference_type=data.get('reference_type'),
            reference_id=data.get('reference_id'),
            messages=data.get('messages', []),
            created_at=data.get('created_at'),
            closed_at=data.get('closed_at'),
            close_type=data.get('close_type'),
            updated_at=data.get('updated_at')
        )

    def save(self):
        """
        保存会话，使用 $set + $push 实现安全并发写入。

        - 有新增消息（并发发消息场景）：标量字段用 $set，新消息用 $push 追加，
          避免 replace_one 的 read-modify-write 竞态导致消息丢失。
        - 无新增消息（标记已读、更新状态等）：全量 $set（含 messages），
          此时不存在并发写入消息的竞态，$set 安全且能持久化 is_read 等修改。
        """
        self.updated_at = datetime.now()

        if not self.__class__._ensure_collection_initialized():
            return False

        data = self.to_dict()

        if '_id' not in data:
            return super().save()

        # 计算 __init__/from_dict 之后新增的消息
        saved_count = self._saved_message_count
        if saved_count > len(self.messages):
            saved_count = len(self.messages)
        new_messages = self.messages[saved_count:]

        if new_messages:
            # 有新增消息：$set 标量字段 + $push 新消息（原子追加，避免竞态）
            set_data = {k: v for k, v in data.items() if k != 'messages'}
            update = {'$set': set_data}
            update['$push'] = {'messages': {'$each': [m.to_dict() for m in new_messages]}}
        else:
            # 无新增消息（标记已读、更新状态等）：全量 $set，确保修改被持久化
            update = {'$set': data}

        result = self.__class__._collection.update_one(
            {'_id': data['_id']}, update, upsert=True
        )
        self._saved_message_count = len(self.messages)
        return result.matched_count > 0 or result.upserted_id is not None

    def add_message(self, sender_type, sender_id, content, msg_type='text'):
        """向会话添加消息"""
        message = Message(
            sender_type=sender_type,
            sender_id=sender_id,
            content=content,
            msg_type=msg_type,
            is_read=False
        )
        self.messages.append(message)
        self.updated_at = datetime.now()
        return message

    def mark_messages_as_read(self, reader_id):
        """标记对方发送的消息为已读"""
        updated_count = 0
        for msg in self.messages:
            if msg.sender_id != reader_id and not msg.is_read:
                msg.is_read = True
                updated_count += 1
        return updated_count

    def get_unread_count(self, reader_id):
        """获取未读消息数量"""
        return sum(1 for msg in self.messages
                  if msg.sender_id != reader_id and not msg.is_read)


class AgentStatus(MongoModel):
    """客服实时状态表"""

    def __init__(self, **kwargs):
        self._id = kwargs.get('_id', ObjectId())
        self.agent_id = kwargs.get('agent_id', 0)                    # 单客服系统：默认0表示无客服或未分配

        # 验证并设置 online_status
        online_status = kwargs.get('online_status', 'offline')
        if online_status not in VALID_ONLINE_STATUS:
            raise ValueError(f"无效的 online_status: {online_status}，有效值: {VALID_ONLINE_STATUS}")
        self.online_status = online_status

        self.current_session_id = kwargs.get('current_session_id')  # 当前正在处理的会话ID
        self.last_heartbeat = kwargs.get('last_heartbeat', datetime.now())  # 最后心跳时间
        self.updated_at = kwargs.get('updated_at', datetime.now())  # 最后状态变更时间

    @classmethod
    def init_collection(cls, db):
        """初始化集合和索引"""
        cls._collection = db.agent_status
        # 创建索引
        cls._collection.create_index('agent_id', unique=True)
        cls._collection.create_index('online_status')
        cls._collection.create_index([('last_heartbeat', 1)])
        cls._collection.create_index([('updated_at', 1)])
        print(f"[OK] MongoDB 集合初始化: agent_status")

    def save(self):
        """保存前更新 updated_at 和 last_heartbeat（如果在线）"""
        self.updated_at = datetime.now()
        if self.online_status in ['online', 'busy']:
            self.last_heartbeat = datetime.now()

        # 使用 agent_id 作为过滤条件原子性地 upsert，避免并发重复
        self.__class__._collection.replace_one(
            {'agent_id': self.agent_id},
            self.to_dict(),
            upsert=True
        )

    def to_dict(self):
        """转换为字典（用于保存到 MongoDB）"""
        data = {
            '_id': self._id,
            'agent_id': self.agent_id,
            'online_status': self.online_status,
            'last_heartbeat': self.last_heartbeat,
            'updated_at': self.updated_at
        }
        if self.current_session_id:
            data['current_session_id'] = self.current_session_id
        return data

    @classmethod
    def from_dict(cls, data):
        """从字典创建 AgentStatus 实例"""
        if not data:
            return None
        return cls(
            _id=data.get('_id'),
            agent_id=data.get('agent_id', 0),
            online_status=data.get('online_status', 'offline'),
            current_session_id=data.get('current_session_id'),
            last_heartbeat=data.get('last_heartbeat'),
            updated_at=data.get('updated_at')
        )

    @classmethod
    def ensure_single_agent(cls, agent_id=0):
        """确保系统中只有一个客服状态记录，如果不存在则创建默认记录"""
        agent = cls.find_one(agent_id=agent_id)
        if not agent:
            agent = cls(agent_id=agent_id, online_status='offline')
            agent.save()
            print(f"[INFO] 创建默认客服状态记录，agent_id: {agent_id}")
        return agent

    @classmethod
    def get_or_create_agent(cls, agent_id=0):
        """获取或创建客服状态记录（便捷方法）"""
        return cls.ensure_single_agent(agent_id)


class UserStatus(MongoModel):
    """用户实时状态表"""

    def __init__(self, **kwargs):
        self._id = kwargs.get('_id', ObjectId())
        self.user_id = kwargs.get('user_id')                     # 对应用户ID

        # 验证并设置 online_status
        online_status = kwargs.get('online_status', 'offline')
        if online_status not in VALID_ONLINE_STATUS:
            raise ValueError(f"无效的 online_status: {online_status}，有效值: {VALID_ONLINE_STATUS}")
        self.online_status = online_status

        self.current_session_id = kwargs.get('current_session_id')  # 用户当前正在进行的会话ID
        self.last_heartbeat = kwargs.get('last_heartbeat', datetime.now())  # 最后心跳时间
        self.updated_at = kwargs.get('updated_at', datetime.now())  # 最后状态变更时间

    @classmethod
    def init_collection(cls, db):
        """初始化集合和索引"""
        cls._collection = db.user_status
        # 创建索引
        cls._collection.create_index('user_id', unique=True)
        cls._collection.create_index('online_status')
        cls._collection.create_index([('last_heartbeat', 1)])
        cls._collection.create_index([('updated_at', 1)])
        print(f"[OK] MongoDB 集合初始化: user_status")

    def save(self):
        """保存前更新 updated_at 和 last_heartbeat（如果在线）"""
        self.updated_at = datetime.now()
        if self.online_status in ['online', 'busy']:
            self.last_heartbeat = datetime.now()

        # 使用 user_id 作为过滤条件原子性地 upsert，避免并发重复
        self.__class__._collection.replace_one(
            {'user_id': self.user_id},
            self.to_dict(),
            upsert=True
        )


class FAQ(MongoModel):
    """常见问题表"""

    def __init__(self, **kwargs):
        self._id = kwargs.get('_id', ObjectId())
        self.question = kwargs.get('question')                   # 问题标题（数字快捷方式或语义匹配文本）
        self.answer = kwargs.get('answer')                       # 问题答案
        self.display_text = kwargs.get('display_text', '')       # 客服界面显示的示例问题文本（空=不显示在快捷引导中）

        # 验证并设置 status
        status = kwargs.get('status', 'published')
        if status not in VALID_FAQ_STATUS:
            raise ValueError(f"无效的 status: {status}，有效值: {VALID_FAQ_STATUS}")
        self.status = status

        self.created_at = kwargs.get('created_at', datetime.now())  # 创建时间
        self.updated_at = kwargs.get('updated_at', datetime.now())  # 最后编辑时间

    @classmethod
    def init_collection(cls, db):
        """初始化集合和索引"""
        cls._collection = db.faqs
        # 创建索引
        cls._collection.create_index('question', unique=True)
        cls._collection.create_index('status')
        cls._collection.create_index([('created_at', 1)])
        cls._collection.create_index([('updated_at', 1)])

        # 插入默认常见问题（如果集合为空）
        if cls._collection.count_documents({}) == 0:
            default_faqs = [
                # 快捷引导问题（display_text 有值 = 出现在客服界面的示例问题中）
                {
                    'question': '1',
                    'display_text': '成果发布',
                    'answer': '<b>【1. 成果发布】</b><br><b>如何发布科技成果？</b><br>登录账号→进入【成果发布】→按照表单标注填写对应内容→提交审核。<br><b>审核时间？</b><br>1-2个工作日完成审核。<br><b>信息填错了怎么办？</b><br>请联系人工客服退回修改。',
                    'status': 'published',
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                },
                {
                    'question': '2',
                    'display_text': '需求发布',
                    'answer': '<b>【2. 需求发布】</b><br><b>如何发布技术需求？</b><br>登录账号→进入【需求发布】→按照表单标注填写对应内容→提交审核。<br><b>审核时间？</b><br>1-2个工作日完成审核。',
                    'status': 'published',
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                },
                {
                    'question': '3',
                    'display_text': '专家认证',
                    'answer': '<b>【3. 专家认证】</b><br>平台暂不支持自主认证，请联系人工客服提供相应资料（身份证、学历证书、职称证书、代表性成果等），通过审核后由平台管理员登记至专家中心。',
                    'status': 'published',
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                },
                {
                    'question': '4',
                    'display_text': '成果 & 需求对接',
                    'answer': '<b>【4. 成果 & 需求对接】</b><br>在成果/需求详情页，找到您想要对接的条目，点击页面中的【我要对接】按钮即可提交对接申请。<br><b>对接后怎么跟进？</b><br>可在【我的对接】中查看进度。<br><b>对接收费吗？</b><br>基础对接服务免费，深度撮合及落地服务按标准执行。',
                    'status': 'published',
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                },
                {
                    'question': '5',
                    'display_text': '账号与信息修改',
                    'answer': '<b>【5. 账号与信息修改】</b><br>修改密码/手机号：请在【个人中心】按照提示操作。<br>修改已发布内容：需在【我的发布】中编辑并重新提交审核。<br>修改实名信息：请联系人工客服处理。',
                    'status': 'published',
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                },
                {
                    'question': '6',
                    'display_text': '人工客服',
                    'answer': '人工客服工作时间：工作日 9:00-17:00。<br>如需转人工，请直接输入"转人工"或点击下方"转人工"按钮，客服接入后会通知您。',
                    'status': 'published',
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                },
                # 语义问题（用户输入自然语言也能匹配）
                {
                    'question': '如何发布科技成果？',
                    'answer': '<b>如何发布科技成果？</b><br>登录账号→进入【成果发布】→按照表单标注填写对应内容→提交审核。<br><b>审核时间？</b><br>1-2个工作日完成审核。<br><b>信息填错了怎么办？</b><br>请联系人工客服退回修改。',
                    'status': 'published',
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                },
                {
                    'question': '如何发布技术需求？',
                    'answer': '<b>如何发布技术需求？</b><br>登录账号→进入【需求发布】→按照表单标注填写对应内容→提交审核。<br><b>审核时间？</b><br>1-2个工作日完成审核。<br><b>信息填错了怎么办？</b><br>请联系人工客服退回修改。',
                    'status': 'published',
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                },
                {
                    'question': '如何进行专家认证？',
                    'answer': '<b>如何进行专家认证？</b><br>平台暂不支持自主认证，请联系人工客服提供相应资料（身份证、学历证书、职称证书、代表性成果等），通过审核后由平台管理员登记至专家中心。',
                    'status': 'published',
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                },
                {
                    'question': '如何进行成果和需求对接？',
                    'answer': '<b>如何进行成果和需求对接？</b><br>在成果/需求详情页，找到您想要对接的条目，点击页面中的【我要对接】按钮即可提交对接申请。<br><b>对接后怎么跟进？</b><br>可在【我的对接】中查看进度。<br><b>对接收费吗？</b><br>基础对接服务免费，深度撮合及落地服务按标准执行。',
                    'status': 'published',
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                },
                {
                    'question': '如何修改账号信息？',
                    'answer': '<b>如何修改账号信息？</b><br>修改密码/手机号：请在【个人中心】按照提示操作。<br>修改已发布内容：需在【我的发布】中编辑并重新提交审核。<br>修改实名信息：请联系人工客服处理。',
                    'status': 'published',
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                },
                {
                    'question': '人工客服工作时间？',
                    'answer': '人工客服工作时间：工作日 9:00-17:00。<br>非工作时间您也可以留言，客服上线后会尽快回复您。紧急问题请拨打客服热线。',
                    'status': 'published',
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                },
            ]
            cls._collection.insert_many(default_faqs)
            print(f"[OK] MongoDB 集合初始化: faqs（已插入 {len(default_faqs)} 条默认FAQ）")
        else:
            print(f"[OK] MongoDB 集合初始化: faqs")

    def save(self):
        """保存前更新 updated_at"""
        self.updated_at = datetime.now()
        return super().save()


class ChatMessage(MongoModel):
    """通用聊天消息表（保持不变）"""

    def __init__(self, **kwargs):
        self._id = kwargs.get('_id', ObjectId())
        self.room_id = kwargs.get('room_id')                     # 房间ID

        # 验证并设置 sender
        sender = kwargs.get('sender')
        if sender not in VALID_CHAT_SENDER_TYPES:
            raise ValueError(f"无效的 sender: {sender}，有效值: {VALID_CHAT_SENDER_TYPES}")
        self.sender = sender

        self.content = kwargs.get('content')                     # 消息内容
        self.created_at = kwargs.get('created_at', datetime.now())  # 创建时间

    @classmethod
    def init_collection(cls, db):
        """初始化集合和索引"""
        cls._collection = db.chat_messages
        # 创建索引
        cls._collection.create_index('room_id')
        cls._collection.create_index([('created_at', 1)])
        print(f"[OK] MongoDB 集合初始化: chat_messages")


class Achievement(MongoModel):
    """成果表"""

    def __init__(self, **kwargs):
        self._id = kwargs.get('_id', ObjectId())
        self.user_id = kwargs.get('user_id')  # 提交用户ID
        self.achievement_name = kwargs.get('achievement_name')  # 成果名称
        self.achievement_code = kwargs.get('achievement_code')  # 成果编号，系统生成
        self.owner = kwargs.get('owner')  # 持有人

        # 地区信息
        self.region = kwargs.get('region', {})
        if not self.region:
            self.region = {
                'province': kwargs.get('province'),
                'city': kwargs.get('city')
            }

        # 技术领域
        self.tech_fields = kwargs.get('tech_fields', [])  # 数组
        self.tech_fields_other = kwargs.get('tech_fields_other', '')  # 其他技术领域

        # 验证并设置技术成熟度
        tech_maturity = kwargs.get('tech_maturity')
        if tech_maturity and tech_maturity not in VALID_TECH_MATURITY:
            # 如果不在预定义值中，允许自定义（如前端其他选项）
            pass
        self.tech_maturity = tech_maturity

        # 转化方式
        transfer_methods = kwargs.get('transfer_methods', [])
        # 确保 transfer_methods 是列表
        if isinstance(transfer_methods, str):
            if transfer_methods.strip():
                transfer_methods = [item.strip() for item in transfer_methods.split(',')]
            else:
                transfer_methods = []
        elif not isinstance(transfer_methods, list):
            transfer_methods = [transfer_methods] if transfer_methods is not None else []
        self.transfer_methods = transfer_methods  # 数组
        self.transfer_methods_other = kwargs.get('transfer_methods_other', '')  # 其他转化方式

        # 描述信息
        self.description = kwargs.get('description', {})
        if not self.description:
            self.description = {
                'summary': kwargs.get('summary', ''),
                'innovation_level': kwargs.get('innovation_level', ''),
                'advantages': kwargs.get('advantages', ''),
                'core_indicators': kwargs.get('core_indicators', ''),
                'intellectual_property': kwargs.get('intellectual_property', '')
            }

        # 转化偏好
        self.transfer_preference = kwargs.get('transfer_preference', {})
        if not self.transfer_preference:
            self.transfer_preference = {
                'tech_transfer': kwargs.get('tech_transfer', {'enabled': False, 'expected_fee': 0}),
                'tech_license': kwargs.get('tech_license', {'enabled': False, 'type': ''}),
                'tech_investment': kwargs.get('tech_investment', {'enabled': False, 'valuation': 0, 'share_ratio': 0}),
                'cooperation_dev': kwargs.get('cooperation_dev', False),
                'other': kwargs.get('transfer_other', ''),
                'expected_complete_date': kwargs.get('expected_complete_date', {'year': 0, 'month': 0})
            }

        # 状态
        status = kwargs.get('status', 'pending')
        if status not in VALID_ACHIEVEMENT_STATUS:
            raise ValueError(f"无效的 status: {status}，有效值: {VALID_ACHIEVEMENT_STATUS}")
        self.status = status

        # 展示状态
        self.is_display = kwargs.get('is_display', False)

        # 审核信息
        self.reviewer_id = kwargs.get('reviewer_id')  # 审核人ID
        self.reviewed_at = kwargs.get('reviewed_at')  # 审核时间
        self.reject_reason = kwargs.get('reject_reason', '')  # 驳回原因

        # 时间戳
        self.created_at = kwargs.get('created_at', datetime.now())
        self.updated_at = kwargs.get('updated_at', datetime.now())

    @classmethod
    def init_collection(cls, db):
        """初始化集合和索引"""
        cls._collection = db.achievements
        # 创建索引（按照规范）
        cls._collection.create_index('achievement_code', unique=True)  # 成果编号唯一
        cls._collection.create_index('owner')  # 成果持有人索引
        cls._collection.create_index('tech_fields')  # 技术领域索引
        cls._collection.create_index([('region.province', 1), ('region.city', 1)])  # 地区复合索引（规范要求）
        cls._collection.create_index([('created_at', -1)])  # 按时间倒排
        cls._collection.create_index('user_id')  # 用户ID索引
        cls._collection.create_index('status')  # 状态索引
        print(f"[OK] MongoDB 集合初始化: achievements")

    def save(self):
        """保存前更新 updated_at"""
        self.updated_at = datetime.now()
        return super().save()


class Requirement(MongoModel):
    """需求表"""

    def __init__(self, **kwargs):
        self._id = kwargs.get('_id', ObjectId())
        self.user_id = kwargs.get('user_id')  # 提交用户ID
        self.company_name = kwargs.get('company_name')  # 企业名称
        self.demand_name = kwargs.get('demand_name')  # 需求名称
        self.demand_code = kwargs.get('demand_code')  # 需求编号，系统生成

        # 地区信息
        self.region = kwargs.get('region', {})
        if not self.region:
            self.region = {
                'province': kwargs.get('province'),
                'city': kwargs.get('city')
            }

        # 技术领域
        self.tech_fields = kwargs.get('tech_fields', [])  # 数组
        self.tech_fields_other = kwargs.get('tech_fields_other', '')  # 其他技术领域

        # 需求类型
        self.demand_types = kwargs.get('demand_types', [])  # 数组
        self.demand_types_other = kwargs.get('demand_types_other', '')  # 其他需求类型

        # 描述信息
        self.description = kwargs.get('description', {})
        if not self.description:
            self.description = {
                'overview': kwargs.get('overview', ''),
                'target_problems': kwargs.get('target_problems', ''),
                'budget': kwargs.get('budget', 0)
            }

        # 状态
        status = kwargs.get('status', 'pending')
        if status not in VALID_REQUIREMENT_STATUS:
            raise ValueError(f"无效的 status: {status}，有效值: {VALID_REQUIREMENT_STATUS}")
        self.status = status

        # 供需状态（待对接/对接中/已完成）
        match_status = kwargs.get('match_status', '待对接')
        if match_status not in VALID_MATCH_STATUS:
            raise ValueError(f"无效的 match_status: {match_status}，有效值: {VALID_MATCH_STATUS}")
        self.match_status = match_status

        # 展示状态
        self.is_display = kwargs.get('is_display', False)

        # 审核信息
        self.reviewer_id = kwargs.get('reviewer_id')  # 审核人ID
        self.reviewed_at = kwargs.get('reviewed_at')  # 审核时间
        self.reject_reason = kwargs.get('reject_reason', '')  # 驳回原因

        # 时间戳
        self.created_at = kwargs.get('created_at', datetime.now())
        self.updated_at = kwargs.get('updated_at', datetime.now())

    @classmethod
    def init_collection(cls, db):
        """初始化集合和索引"""
        cls._collection = db.requirements
        # 创建索引（按照规范）
        cls._collection.create_index('demand_code', unique=True)  # 需求编号唯一
        cls._collection.create_index('company_name')  # 企业名称索引
        cls._collection.create_index('tech_fields')  # 技术领域索引
        cls._collection.create_index([('region.province', 1), ('region.city', 1)])  # 地区复合索引（规范要求）
        cls._collection.create_index([('created_at', -1)])  # 按创建时间倒序
        cls._collection.create_index('user_id')  # 用户ID索引
        cls._collection.create_index('status')  # 状态索引
        cls._collection.create_index('match_status')  # 供需状态索引
        print(f"[OK] MongoDB 集合初始化: requirements")

    def save(self):
        """保存前更新 updated_at"""
        self.updated_at = datetime.now()
        return super().save()


class Expert(MongoModel):
    """专家信息表"""

    def __init__(self, **kwargs):
        self._id = kwargs.get('_id', ObjectId())

        # 一、基本信息
        self.name = kwargs.get('name', '')                     # 姓名
        self.gender = kwargs.get('gender', '')                 # 性别
        self.id_card = kwargs.get('id_card', '')               # 身份证号
        self.highest_education = kwargs.get('highest_education', '')  # 最高学历
        self.school_major = kwargs.get('school_major', '')     # 毕业院校及专业
        self.work_unit = kwargs.get('work_unit', '')           # 现工作单位
        self.position_title = kwargs.get('position_title', '') # 职务/职称
        self.contact = kwargs.get('contact', '')               # 联系方式（电话/邮箱）
        self.address = kwargs.get('address', '')               # 通讯地址
        self.honors = kwargs.get('honors', '')                 # 社会荣誉

        # 二、专业领域（最多2个主领域）
        self.professional_fields = kwargs.get('professional_fields', [])  # 数组，最多2个
        self.professional_fields_other = kwargs.get('professional_fields_other', '')  # 其他

        # 个人简介
        self.personal_profile = kwargs.get('personal_profile', '')

        # 三、评估资质
        # 1. 专业知识水平
        self.technical_title = kwargs.get('technical_title', '')          # 专业技术职称
        self.professional_certification = kwargs.get('professional_certification', '')  # 职业资格认证
        self.foreign_language = kwargs.get('foreign_language', '')        # 外语能力

        # 2. 从业经验
        self.work_years = kwargs.get('work_years', 0)                    # 工作年限
        self.successful_cases = kwargs.get('successful_cases', 0)        # 成功案例数

        # 四、代表性成果
        self.patents = kwargs.get('patents', '')                         # 专利情况
        self.publications = kwargs.get('publications', '')               # 论文著作
        self.research_projects = kwargs.get('research_projects', '')     # 科研项目
        self.awards = kwargs.get('awards', '')                           # 获奖情况

        # 五、附件清单（仅管理员可查看），存储为 {type: [{file_name, file_path, file_url}, ...]}
        self.attachments = kwargs.get('attachments', {})

        # 时间戳
        self.created_at = kwargs.get('created_at', datetime.now())
        self.updated_at = kwargs.get('updated_at', datetime.now())

    @classmethod
    def init_collection(cls, db):
        """初始化集合和索引"""
        cls._collection = db.experts
        cls._collection.create_index('name')
        cls._collection.create_index('id_card', unique=True, sparse=True)
        cls._collection.create_index('professional_fields')
        cls._collection.create_index('work_unit')
        cls._collection.create_index([('created_at', -1)])
        print(f"[OK] MongoDB 集合初始化: experts")

    def save(self):
        """保存前更新 updated_at"""
        self.updated_at = datetime.now()
        return super().save()


class Partner(MongoModel):
    """合作伙伴信息表"""

    def __init__(self, **kwargs):
        self._id = kwargs.get('_id', ObjectId())
        self.name = kwargs.get('name', '')                     # 平台名称
        self.type = kwargs.get('type', '')                     # 分类：概念验证平台/中试基地/产业化试验基地
        self.address = kwargs.get('address', '')               # 所在地址
        self.industry = kwargs.get('industry', '')             # 行业领域
        self.intro = kwargs.get('intro', '')                   # 平台介绍
        self.services = kwargs.get('services', '')             # 可提供的服务
        self.contact = kwargs.get('contact', '')               # 联系人及电话（不对外展示）
        self.images = kwargs.get('images', [])                 # 照片列表 [{file_name, file_path, file_url}, ...]
        self.created_at = kwargs.get('created_at', datetime.now())
        self.updated_at = kwargs.get('updated_at', datetime.now())

    @classmethod
    def init_collection(cls, db):
        """初始化集合和索引"""
        cls._collection = db.partners
        cls._collection.create_index('name')
        cls._collection.create_index('type')
        cls._collection.create_index('industry')
        cls._collection.create_index([('created_at', -1)])
        print(f"[OK] MongoDB 集合初始化: partners")

    def save(self):
        """保存前更新 updated_at"""
        self.updated_at = datetime.now()
        return super().save()


class FinancialService(MongoModel):
    """金融服务机构表"""

    def __init__(self, **kwargs):
        self._id = kwargs.get('_id', ObjectId())
        self.name = kwargs.get('name', '')                     # 机构名称
        self.intro = kwargs.get('intro', '')                   # 简介
        self.services = kwargs.get('services', '')             # 可提供的服务
        self.contact = kwargs.get('contact', '')               # 联系人及电话（不对外展示）
        self.images = kwargs.get('images', [])                 # 照片列表 [{file_name, file_path, file_url}, ...]
        self.created_at = kwargs.get('created_at', datetime.now())
        self.updated_at = kwargs.get('updated_at', datetime.now())

    @classmethod
    def init_collection(cls, db):
        """初始化集合和索引"""
        cls._collection = db.financial_services
        cls._collection.create_index('name')
        cls._collection.create_index([('created_at', -1)])
        print(f"[OK] MongoDB 集合初始化: financial_services")

    def save(self):
        """保存前更新 updated_at"""
        self.updated_at = datetime.now()
        return super().save()


class Cooperation(MongoModel):
    """合作申请表（普通用户从合作伙伴详情页提交）"""

    def __init__(self, **kwargs):
        self._id = kwargs.get('_id', ObjectId())
        self.partner_id = kwargs.get('partner_id')             # 对应 partners 集合中的 _id
        self.contact_name = kwargs.get('contact_name', '')     # 联系人姓名
        self.contact_phone = kwargs.get('contact_phone', '')   # 联系人电话
        self.contact_email = kwargs.get('contact_email', '')   # 联系邮箱
        self.company = kwargs.get('company', '')               # 联系单位
        self.address = kwargs.get('address', '')               # 联系地址
        self.intention = kwargs.get('intention', '')           # 意向说明
        self.created_at = kwargs.get('created_at', datetime.now())

    @classmethod
    def init_collection(cls, db):
        """初始化集合和索引"""
        cls._collection = db.cooperation
        cls._collection.create_index('partner_id')
        cls._collection.create_index([('created_at', -1)])
        print(f"[OK] MongoDB 集合初始化: cooperation")

    def save(self):
        return super().save()


class VisitLog(MongoModel):
    """网站访问日志"""

    def __init__(self, **kwargs):
        self._id = kwargs.get('_id', ObjectId())
        self.path = kwargs.get('path', '')                    # 访问路径
        self.ip = kwargs.get('ip', '')                        # 访问者IP
        self.user_agent = kwargs.get('user_agent', '')        # 浏览器标识
        self.created_at = kwargs.get('created_at', datetime.now())

    @classmethod
    def init_collection(cls, db):
        cls._collection = db.visit_logs
        # 7天 TTL 索引：到期自动删除旧记录 + 按创建时间排序查询
        cls._collection.create_index('created_at', expireAfterSeconds=7 * 24 * 3600)
        print(f"[OK] MongoDB 集合初始化: visit_logs (TTL: 7天自动过期)")


def init_all_collections(db):
    """初始化所有集合"""
    print(f"[DEBUG] init_all_collections: 开始初始化MongoDB集合, 数据库: {db.name}")

    print("[DEBUG] 初始化 Session...")
    Session.init_collection(db)
    print("[DEBUG] 初始化 AgentStatus...")
    AgentStatus.init_collection(db)
    print("[DEBUG] 初始化 UserStatus...")
    UserStatus.init_collection(db)
    print("[DEBUG] 初始化 FAQ...")
    FAQ.init_collection(db)
    print("[DEBUG] 初始化 ChatMessage...")
    ChatMessage.init_collection(db)
    print("[DEBUG] 初始化 Achievement...")
    Achievement.init_collection(db)
    print("[DEBUG] 初始化 Requirement...")
    Requirement.init_collection(db)
    print("[DEBUG] 初始化 Expert...")
    Expert.init_collection(db)
    print("[DEBUG] 初始化 Partner...")
    Partner.init_collection(db)
    print("[DEBUG] 初始化 FinancialService...")
    FinancialService.init_collection(db)
    print("[DEBUG] 初始化 Cooperation...")
    Cooperation.init_collection(db)
    print("[DEBUG] 初始化 VisitLog...")
    VisitLog.init_collection(db)

    # 列出所有集合以验证
    collections = db.list_collection_names()
    print(f"[DEBUG] init_all_collections: 数据库中的所有集合: {collections}")
    print("[OK] 所有 MongoDB 集合初始化完成")


# ============================================================================
# 向后兼容别名（已弃用，建议迁移到新模型）
# ============================================================================

import warnings

class MongoCustomerServiceSession(Session):
    """客服会话 - MongoDB 版本（已弃用，请使用 Session 类）"""

    def __init__(self, **kwargs):
        warnings.warn("MongoCustomerServiceSession 已弃用，请使用 Session 类", DeprecationWarning, stacklevel=2)
        # 转换参数：旧模型可能有不同的字段名
        # 旧模型: id, user_id, agent_id, status, created_at, updated_at
        # 新模型: _id, user_id, agent_id, status, created_at, updated_at, messages, closed_at, close_type
        super().__init__(**kwargs)


class MongoCustomerServiceMessage(MongoModel):
    """客服聊天消息 - MongoDB 版本（已弃用，消息已嵌入 Session 中）"""

    def __init__(self, **kwargs):
        warnings.warn("MongoCustomerServiceMessage 已弃用，消息已嵌入 Session 中", DeprecationWarning, stacklevel=2)
        self._id = kwargs.get('_id', ObjectId())
        self.session_id = kwargs.get('session_id')

        # 验证并设置 sender_type
        sender_type = kwargs.get('sender_type')
        if sender_type not in VALID_SENDER_TYPES:
            raise ValueError(f"无效的 sender_type: {sender_type}，有效值: {VALID_SENDER_TYPES}")
        self.sender_type = sender_type

        self.sender_id = kwargs.get('sender_id')
        self.content = kwargs.get('content')
        self.created_at = kwargs.get('created_at', datetime.now())
        self.is_read = kwargs.get('is_read', False)

    @classmethod
    def init_collection(cls, db):
        """初始化集合和索引（空实现，不推荐使用）"""
        cls._collection = db.customer_service_messages
        warnings.warn("MongoCustomerServiceMessage 集合已弃用，请使用 Session.messages", DeprecationWarning, stacklevel=2)
        # 可选：创建索引以保持兼容性
        cls._collection.create_index('session_id')
        cls._collection.create_index('sender_id')
        cls._collection.create_index([('created_at', 1)])
        cls._collection.create_index('is_read')
        print(f"[WARN] MongoDB 集合初始化（已弃用）: customer_service_messages")

    def save(self):
        """保存（已弃用，建议使用 Session.add_message()）"""
        warnings.warn("MongoCustomerServiceMessage.save() 已弃用，请使用 Session.add_message()", DeprecationWarning, stacklevel=2)
        # 实际保存到独立集合以保持兼容性
        return super().save()


# 别名定义（保持现有导入工作）
MongoAgentStatus = AgentStatus
MongoChatMessage = ChatMessage
MongoUserStatus = UserStatus