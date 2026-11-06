from datetime import datetime, timedelta
from .models import db, User
from .mongo_models import MongoCustomerServiceSession, MongoCustomerServiceMessage, MongoAgentStatus

class AgentService:
    """客服服务类，处理客服分配和状态管理"""

    @staticmethod
    def try_assign_agent(session_id):
        """尝试为会话分配客服"""
        session = MongoCustomerServiceSession.get(session_id)
        if not session or session.status != 'pending':
            return None

        # 查找在线的客服
        online_agents = MongoAgentStatus.find(online_status='online')
        print(f"try_assign_agent: 会话 {session_id}, 在线客服数量: {len(online_agents)}")

        # 优先选择空闲客服（没有当前会话的）
        free_agents = [agent for agent in online_agents if not agent.current_session_id]
        print(f"try_assign_agent: 空闲客服数量: {len(free_agents)}")

        if free_agents:
            # 选择最早空闲的客服
            assigned_agent = min(free_agents, key=lambda a: a.last_heartbeat)
        elif online_agents:
            # 所有在线客服都有会话，选择最近活跃的
            assigned_agent = min(online_agents, key=lambda a: a.last_heartbeat)
        else:
            # 没有在线客服
            print("try_assign_agent: 没有在线客服")
            return None

        # 分配客服
        session.agent_id = assigned_agent.agent_id
        session.status = 'active'
        session.updated_at = datetime.now()
        session.save()

        assigned_agent.current_session_id = session_id
        assigned_agent.last_heartbeat = datetime.now()
        assigned_agent.save()

        print(f"try_assign_agent: 分配客服 {assigned_agent.agent_id} 给会话 {session_id}")
        return assigned_agent.agent_id

    @staticmethod
    def release_agent(agent_id):
        """释放客服，使其可以接收新会话"""
        agent_status = MongoAgentStatus.find_one(agent_id=agent_id)
        if agent_status:
            agent_status.current_session_id = None
            agent_status.last_heartbeat = datetime.now()
            agent_status.save()

    @staticmethod
    def get_online_agents():
        """获取在线客服列表"""
        # 查找在线和忙碌的客服
        online_agents_cursor = MongoAgentStatus._collection.find({'online_status': {'$in': ['online', 'busy']}})
        online_agents = [MongoAgentStatus.from_dict(doc) for doc in online_agents_cursor]
        result = []
        for agent_status in online_agents:
            user = User.query.get(agent_status.agent_id)
            if user:
                result.append({
                    'id': user.id,
                    'username': user.username,
                    'status': agent_status.online_status,
                    'current_session_id': agent_status.current_session_id,
                    'last_heartbeat': agent_status.last_heartbeat.isoformat() if agent_status.last_heartbeat else None
                })
        return result

    @staticmethod
    def update_agent_heartbeat(agent_id):
        """更新客服心跳"""
        agent_status = MongoAgentStatus.find_one(agent_id=agent_id)
        if agent_status:
            agent_status.last_heartbeat = datetime.now()
            agent_status.save()

    @staticmethod
    def create_session(user_id):
        """为用户创建新的客服会话"""
        # 检查用户是否有未关闭的会话 - 使用MongoDB原生查询
        existing_session = MongoCustomerServiceSession._collection.find_one({
            'user_id': user_id,
            'status': {'$in': ['pending', 'active', 'waiting']}
        })

        if existing_session:
            return MongoCustomerServiceSession.from_dict(existing_session)

        # 检查是否有已关闭的会话，有则重新打开（复用，与 request_human 流程一致）
        closed_session = MongoCustomerServiceSession._collection.find_one({
            'user_id': user_id,
            'status': 'closed'
        }, sort=[('updated_at', -1)])
        if closed_session:
            session = MongoCustomerServiceSession.from_dict(closed_session)
            session.status = 'pending'
            session.agent_id = None
            session.close_type = None
            session.closed_at = None
            session.updated_at = datetime.now()
            session.save()
            # 清理该用户其他未关闭的会话（防止积累重复会话）
            MongoCustomerServiceSession._collection.update_many(
                {'user_id': user_id, 'status': {'$in': ['pending', 'active', 'waiting']}, '_id': {'$ne': session._id}},
                {'$set': {'status': 'closed', 'closed_at': datetime.now(), 'close_type': 'auto_merged', 'updated_at': datetime.now()}}
            )
            return session

        # 创建新会话
        new_session = MongoCustomerServiceSession(
            user_id=user_id,
            status='pending',
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        print(f"[DEBUG] AgentService.create_session: 创建会话对象, user_id={user_id}, agent_id={new_session.agent_id}")
        success = new_session.save()
        print(f"[DEBUG] AgentService.create_session: 保存结果 success={success}, 会话ID={new_session.id if hasattr(new_session, 'id') else 'None'}")

        return new_session

    @staticmethod
    def get_user_sessions(user_id):
        """获取用户的所有客服会话"""
        # 使用MongoDB查询获取用户会话，按创建时间降序排列
        sessions_cursor = MongoCustomerServiceSession._collection.find(
            {'user_id': user_id}
        ).sort('created_at', -1)  # -1表示降序

        sessions = [MongoCustomerServiceSession.from_dict(doc) for doc in sessions_cursor]

        result = []
        for session in sessions:
            # 统计该会话的消息数量（从嵌入式messages数组）
            message_count = len(session.messages) if session.messages else 0

            result.append({
                'id': str(session._id),
                'agent_id': session.agent_id,
                'status': session.status,
                'created_at': session.created_at.isoformat() if session.created_at else None,
                'updated_at': session.updated_at.isoformat() if session.updated_at else None,
                'message_count': message_count
            })

        return result

    @staticmethod
    def get_session_messages(session_id, limit=50):
        """获取会话消息"""
        # 获取会话并从中获取嵌入式消息
        session = MongoCustomerServiceSession.get(session_id)
        if not session:
            return []

        messages = session.messages if session.messages else []

        # 按创建时间升序排序（最早的在前）
        messages = sorted(messages, key=lambda msg: msg.created_at)

        # 限制数量
        if limit and limit < len(messages):
            messages = messages[:limit]

        result = []
        for msg in messages:
            result.append({
                'id': str(msg._id),
                'sender_type': msg.sender_type,
                'sender_id': msg.sender_id,
                'content': msg.content,
                'created_at': msg.created_at.isoformat() if msg.created_at else None,
                'is_read': msg.is_read
            })

        return result

    @staticmethod
    def mark_messages_as_read(session_id, user_id):
        """标记消息为已读（针对接收者）"""
        session = MongoCustomerServiceSession.get(session_id)
        if not session:
            return 0

        updated_count = session.mark_messages_as_read(user_id)
        session.save()

        return updated_count