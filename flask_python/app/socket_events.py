# 告诉 PyCharm request 具有 sid 属性

from flask import request
from flask_socketio import emit, join_room
from flask_jwt_extended import decode_token
from datetime import datetime
import uuid
# import jwt
# from sqlalchemy import or_

# 全局socketio实例，由run.py初始化
_socketio = None
# 全局Flask应用实例
_app = None
# 存储待注册的事件
_pending_events = []

def init_socketio(socketio_instance, flask_app=None):
    """初始化socketio实例并注册所有事件"""
    global _socketio, _app
    _socketio = socketio_instance
    _app = flask_app

    if _app:
        pass
    # 注册所有待处理的事件
    for event, func in _pending_events:
        _socketio.on(event)(func)

    print(f"[OK] Socket.IO事件注册完成，共{len(_pending_events)}个事件")
    return _socketio

def get_socketio():
    """获取全局socketio实例"""
    return _socketio

# 为了方便，定义一个装饰器函数
def socketio_on(event):
    """socketio事件装饰器"""
    def decorator(func):
        if _socketio:
            # 如果_socketio已初始化，直接注册
            return _socketio.on(event)(func)
        else:
            # 如果_socketio未初始化，存储起来稍后注册
            _pending_events.append((event, func))
            return func
    return decorator

# 导入其他模块
from .extensions import db
from .models import User
from .mongo_models import MongoCustomerServiceSession, MongoAgentStatus, MongoChatMessage, MongoUserStatus
from .services import AgentService

# 内存存储 sid -> user_id 的映射
socket_users = {}

# 内存存储 sid -> room_id 的映射（用于通用聊天）
socket_rooms = {}

# 待处理的人工客服请求（尚未创建会话，客服接受后才创建）
pending_human_requests = {}  # user_id -> {user_id, username, room_id, timestamp}

# 客服房间前缀
AGENT_ROOM_PREFIX = 'agent_'
USER_ROOM_PREFIX = 'user_'

def save_and_emit_system_message(room_id, text):
    """保存系统消息到MongoDB并广播到房间，确保转人工等系统提示持久化"""
    try:
        msg = MongoChatMessage(room_id=room_id, sender='system', content=text)
        msg.save()
        emit('receive_message', {
            'room_id': room_id,
            'sender': 'system',
            'text': text,
            'timestamp': datetime.now().isoformat(),
            'message_id': str(msg._id)
        }, room=room_id)
    except Exception as e:
        print(f"[WARN] 保存/广播系统消息失败: {e}")
        # 至少尝试广播，不丢失即时通知
        emit('receive_message', {
            'room_id': room_id,
            'sender': 'system',
            'text': text,
            'timestamp': datetime.now().isoformat()
        }, room=room_id)

def emit_new_message_event(receive_user_id, message_data):
    """向目标用户实时推送新消息通知"""
    if not _socketio:
        return
    try:
        if receive_user_id == 0:
            # 广播消息：发给所有在线普通用户
            from .models import User
            common_users = User.query.filter_by(role='common').all()
            for u in common_users:
                _socketio.emit('new_message', message_data, room=f'{USER_ROOM_PREFIX}{u.id}')
        else:
            # 发给指定用户
            _socketio.emit('new_message', message_data, room=f'{USER_ROOM_PREFIX}{receive_user_id}')
    except Exception as e:
        print(f"[WARN] 发送实时通知失败: {e}")

def broadcast_agent_status_to_related_sessions(agent_id, online_status):
    """向所有与该客服相关的会话（等待中 + 进行中）的用户广播客服状态"""
    try:
        query = {
            '$or': [
                {'agent_id': agent_id, 'status': 'active'},
                {'status': 'pending'}
            ]
        }
        related_sessions = MongoCustomerServiceSession._collection.find(query)
        if online_status == 'online':
            message = '客服已上线，可继续咨询'
        elif online_status == 'busy':
            message = '客服忙碌，请稍后'
        else:
            message = '客服暂时离线，请稍后'
        sent_count = 0
        for session_doc in related_sessions:
            session = MongoCustomerServiceSession.from_dict(session_doc)
            user_id = session.user_id
            if user_id:
                emit('agent_availability', {
                    'message': message,
                    'online_status': online_status,
                    'agent_id': agent_id,
                    'timestamp': datetime.now().isoformat()
                }, room=f'{USER_ROOM_PREFIX}{user_id}')
                sent_count += 1
        print(f"[INFO] 已向 {sent_count} 个关联会话的用户广播客服状态: {online_status}")
    except Exception as e:
        print(f"[ERROR] 广播客服状态失败: {e}")

@socketio_on('connect')
def handle_connect(auth=None):
    """客户端连接事件，支持认证用户和访客"""
    try:
        token = request.args.get('token')
        print(f"[DEBUG] handle_connect token: {token[:50] if token else 'None'}...")
        print(f"[DEBUG] _app is {'set' if _app else 'None'}, request.sid={request.sid}")

        if not token:
            guest_id = f'guest_{uuid.uuid4().hex[:8]}'
            socket_users[request.sid] = guest_id
            print(f"访客连接: {guest_id}")
            emit('connected', {'message': 'Connected as guest', 'guest_id': guest_id})
            return True

        user_id = None
        if token.startswith('user_token_'):
            try:
                parts = token.split('_')
                if len(parts) >= 3:
                    user_id = int(parts[2])
                else:
                    print(f"旧版token格式错误: {token}")
                    return False
            except (ValueError, IndexError) as e:
                print(f"解析旧版token失败: {e}, token: {token}")
                return False
        else:
            try:
                # 解码JWT token，确保在应用上下文中
                decoded_token = None
                if _app is not None:
                    with _app.app_context():
                        decoded_token = decode_token(token)
                else:
                    # _app为None，假设已经在应用上下文中（由Flask-SocketIO提供）
                    decoded_token = decode_token(token)
                user_id = decoded_token['sub']
                print(f"[DEBUG] JWT验证成功，user_id: {user_id}")
            except Exception as e:
                print(f"JWT token验证失败: {e}")
                print(f"[DEBUG] _app is {'set' if _app else 'None'}")
                if _app:
                    pass
                import traceback
                traceback.print_exc()
                return False

        user = User.query.get(user_id)
        if not user:
            print(f"用户不存在: {user_id}")
            return False

        if user.status != 1:
            print(f"用户已被禁用: {user_id}")
            return False

        socket_users[request.sid] = user.id
        join_room(f'{USER_ROOM_PREFIX}{user.id}')

        user.last_active = datetime.now()
        db.session.commit()

        if user.is_agent:
            join_room('agents_all')
            join_room(f'{AGENT_ROOM_PREFIX}{user.id}')
            print(f"[DEBUG] 客服 {user.username}(ID:{user.id}) 已加入 agents_all / {AGENT_ROOM_PREFIX}{user.id} 房间")
            # ========== 客服连接时强制设为在线 ==========
            agent_status = MongoAgentStatus.find_one(agent_id=user.id)
            if not agent_status:
                agent_status = MongoAgentStatus(agent_id=user.id, online_status='online')
            else:
                agent_status.online_status = 'online'   # 刷新即上线
            agent_status.last_heartbeat = datetime.now()
            agent_status.save()
            current_status = 'online'

            # 广播给其他客服（内部状态更新）
            emit('agent_status_update', {
                'agent_id': user.id,
                'username': user.username,
                'status': current_status,
                'timestamp': datetime.now().isoformat()
            }, broadcast=True, room='agents_all')

            # 向关联用户广播实际状态
            broadcast_agent_status_to_related_sessions(user.id, current_status)
            # ========================================
            print(f"客服连接: {user.username} (ID: {user.id}), 状态: {current_status}")
            emit('connected', {'message': 'Connected as agent', 'user_id': user.id, 'username': user.username})
        else:
            # 更新或创建用户在线状态
            user_status = MongoUserStatus.find_one(user_id=user.id)
            if not user_status:
                user_status = MongoUserStatus(user_id=user.id, online_status='online')
            else:
                user_status.online_status = 'online'
            user_status.last_heartbeat = datetime.now()
            user_status.save()

            # 广播用户上线给所有客服
            emit('user_status_update', {
                'user_id': user.id,
                'username': user.username or user.phone,
                'online_status': 'online',
                'timestamp': datetime.now().isoformat()
            }, room='agents_all')

            print(f"用户连接: {user.username or user.phone} (ID: {user.id})")
            emit('connected', {'message': 'Connected as user', 'user_id': user.id, 'username': user.username or user.phone})

        return True

    except Exception as e:
        print(f"连接错误: {e}")
        import traceback
        traceback.print_exc()
        return False

@socketio_on('disconnect')
def handle_disconnect():
    """客户端断开连接事件"""
    try:
        user_id = socket_users.get(request.sid)
        print(f"[DEBUG] handle_disconnect user_id: {user_id}, sid: {request.sid}")
        if not user_id:
            return

        if isinstance(user_id, str) and user_id.startswith('guest_'):
            if request.sid in socket_users:
                del socket_users[request.sid]
            if request.sid in socket_rooms:
                del socket_rooms[request.sid]
            print(f"访客断开: {user_id}")
            return

        user = User.query.get(user_id)
        if user and user.is_agent:
            agent_status = MongoAgentStatus.find_one(agent_id=user.id)
            if agent_status:
                agent_status.online_status = 'offline'
                agent_status.current_session_id = None
                agent_status.last_heartbeat = datetime.now()
                agent_status.save()

            emit('agent_status_update', {
                'agent_id': user.id,
                'username': user.username,
                'status': 'offline',
                'timestamp': datetime.now().isoformat()
            }, broadcast=True, room='agents_all')

            broadcast_agent_status_to_related_sessions(user.id, 'offline')
            print(f"客服断开: {user.username} (ID: {user.id})")
        else:
            # 用户离线状态更新
            user_status = MongoUserStatus.find_one(user_id=user_id)
            if user_status:
                user_status.online_status = 'offline'
                user_status.save()
            emit('user_status_update', {
                'user_id': user_id,
                'online_status': 'offline',
                'timestamp': datetime.now().isoformat()
            }, room='agents_all')
            print(f"用户断开: ID {user_id}")

        if request.sid in socket_users:
            del socket_users[request.sid]
        if request.sid in socket_rooms:
            del socket_rooms[request.sid]

    except Exception as e:
        print(f"断开连接错误: {e}")

@socketio_on('heartbeat')
def handle_heartbeat(data=None):
    """心跳事件，用于保持连接和更新状态"""
    user_id = socket_users.get(request.sid)
    if not user_id:
        return

    user = User.query.get(user_id)
    if user:
        user.last_active = datetime.now()
        db.session.commit()

        if user.is_agent:
            agent_status = MongoAgentStatus.find_one(agent_id=user.id)
            if agent_status:
                agent_status.last_heartbeat = datetime.now()
                agent_status.save()
        else:
            user_status = MongoUserStatus.find_one(user_id=user.id)
            if user_status:
                user_status.last_heartbeat = datetime.now()
                user_status.save()

        emit('heartbeat_ack', {'timestamp': datetime.now().isoformat()})

@socketio_on('customer_service_message')
def handle_customer_service_message(data):
    """处理客服聊天消息"""
    try:
        print(f"[DEBUG] handle_customer_service_message 收到数据: {data}, sid: {request.sid}, user_id: {socket_users.get(request.sid)}")
        user_id = socket_users.get(request.sid)
        if not user_id:
            emit('error', {'message': '未登录或连接已断开'})
            return

        session_id = data.get('session_id')
        content = data.get('content')

        if not session_id or not content or not content.strip():
            emit('error', {'message': '会话ID和消息内容不能为空'})
            return

        session = MongoCustomerServiceSession.get(session_id)
        if not session:
            emit('error', {'message': '会话不存在'})
            return

        if session.status == 'closed':
            emit('error', {'message': '会话已关闭，无法发送消息'})
            return

        # 同步对接参考信息（用户可能在已有会话中点击了"我要对接"）
        reference_type = data.get('reference_type')
        reference_id = data.get('reference_id')
        ref_updated = False
        if reference_type and reference_type != session.reference_type:
            session.reference_type = reference_type
            ref_updated = True
        if reference_id and reference_id != session.reference_id:
            session.reference_id = reference_id
            ref_updated = True
        if ref_updated:
            session.updated_at = datetime.now()
            session.save()

        user = User.query.get(user_id)
        if not user:
            emit('error', {'message': '用户不存在'})
            return

        if user.status != 1:
            emit('error', {'message': '账号已被禁用'})
            return

        if user.is_agent:
            if session.agent_id != user.id:
                emit('error', {'message': '无权访问此会话'})
                return
            sender_type = 'agent'
            if session.status == 'pending':
                print(f"警告：pending 会话 {session_id} 不应通过发消息自动认领，请走 accept_human_request 流程")
                emit('error', {'message': '此会话等待客服接受，请使用接受按钮'})
                return
        else:
            if session.user_id != user.id:
                emit('error', {'message': '无权访问此会话'})
                return
            sender_type = 'user'

        message = session.add_message(sender_type, user_id, content.strip())
        session.save()

        message_data = {
            'id': str(message._id),
            'session_id': str(session._id),
            'sender_type': sender_type,
            'sender_id': user_id,
            'sender_name': user.username or user.phone,
            'content': message.content,
            'created_at': message.created_at.isoformat(),
            'is_read': message.is_read
        }

        if sender_type == 'user':
            # 用户发的消息：先推送即时消息，再通知负责的客服刷新
            if session.agent_id:
                emit('new_customer_service_message', message_data, room=f'{AGENT_ROOM_PREFIX}{session.agent_id}')
                unread_count = sum(1 for m in session.messages if m.sender_type == 'user' and not m.is_read)
                emit('customer_session_refresh', {
                    'session_id': str(session._id),
                    'unread_count': unread_count,
                    'reference_type': session.reference_type,
                    'reference_id': session.reference_id,
                    'last_message': {
                        'content': message_data['content'],
                        'created_at': message_data['created_at']
                    }
                }, room=f'{AGENT_ROOM_PREFIX}{session.agent_id}')
            else:
                # 会话尚未分配客服（pending），广播给所有客服知晓有新消息
                unread_count = sum(1 for m in session.messages if m.sender_type == 'user' and not m.is_read)
                emit('customer_session_refresh', {
                    'session_id': str(session._id),
                    'unread_count': unread_count,
                    'reference_type': session.reference_type,
                    'reference_id': session.reference_id,
                    'last_message': {
                        'content': message_data['content'],
                        'created_at': message_data['created_at']
                    }
                }, room='agents_all')
        else:
            # 客服发的消息：先推送即时消息，再通知用户刷新
            emit('new_customer_service_message', message_data, room=f'{USER_ROOM_PREFIX}{session.user_id}')
            emit('customer_session_refresh', {
                'session_id': str(session._id),
                'unread_count': 0,
                'reference_type': session.reference_type,
                'reference_id': session.reference_id,
                'last_message': {
                    'content': message_data['content'],
                    'created_at': message_data['created_at']
                }
            }, room=f'{USER_ROOM_PREFIX}{session.user_id}')

        print(f"客服消息: 会话{session_id} {sender_type}{user_id}: {content[:50]}...")

    except Exception as e:
        print(f"处理消息错误: {e}")
        emit('error', {'message': '服务器内部错误'})


@socketio_on('update_session_reference')
def handle_update_session_reference(data):
    """用户点击"我要对接"时更新已有会话的参考信息"""
    try:
        user_id = socket_users.get(request.sid)
        if not user_id:
            emit('error', {'message': '未登录'})
            return

        session_id = data.get('session_id')
        reference_type = data.get('reference_type')
        reference_id = data.get('reference_id')

        if not session_id:
            emit('error', {'message': '会话ID不能为空'})
            return

        session = MongoCustomerServiceSession.get(session_id)
        if not session:
            emit('error', {'message': '会话不存在'})
            return

        if session.user_id != user_id:
            emit('error', {'message': '无权操作此会话'})
            return

        # 更新参考信息
        if reference_type:
            session.reference_type = reference_type
        if reference_id:
            session.reference_id = reference_id
        session.updated_at = datetime.now()
        session.save()

        # 通知客服刷新会话信息
        if session.agent_id:
            emit('customer_session_refresh', {
                'session_id': str(session._id),
                'unread_count': 0,
                'reference_type': session.reference_type,
                'reference_id': session.reference_id,
                'last_message': {
                    'content': f'[用户更新了对接意向]',
                    'created_at': datetime.now().isoformat()
                }
            }, room=f'{AGENT_ROOM_PREFIX}{session.agent_id}')

        print(f"会话参考信息更新: 会话{str(session._id)} reference={reference_type}/{reference_id}")

    except Exception as e:
        print(f"更新会话参考信息错误: {e}")
        emit('error', {'message': '更新失败'})


@socketio_on('delete_customer_service_session')
def handle_delete_customer_service_session(data):
    """管理员删除客服会话（通过Socket.IO触发）"""
    try:
        user_id = socket_users.get(request.sid)
        if not user_id:
            emit('error', {'message': '未登录'})
            return

        user = User.query.get(user_id)
        if not user or not user.is_admin:
            emit('error', {'message': '仅管理员可删除会话'})
            return

        session_id = data.get('session_id')
        if not session_id:
            emit('error', {'message': '需要会话ID'})
            return

        session = MongoCustomerServiceSession.get(session_id)
        if not session:
            emit('error', {'message': '会话不存在'})
            return

        session_user_id = session.user_id
        session_agent_id = session.agent_id

        # 如果会话进行中，先释放客服
        if session.status in ('active', 'pending', 'waiting') and session_agent_id:
            AgentService.release_agent(session_agent_id)

        # 删除会话
        result = session.delete()
        print(f"[DEBUG] Socket删除会话 {session_id}: result={result}")

        # 通知双方
        deleted_data = {
            'session_id': session_id,
            'user_id': session_user_id,
            'agent_id': session_agent_id,
            'deleted_by': 'admin'
        }
        emit('session_deleted', deleted_data)
        if session_user_id:
            emit('session_deleted', deleted_data, room=f'{USER_ROOM_PREFIX}{session_user_id}')
        if session_agent_id:
            emit('session_deleted', deleted_data, room=f'{AGENT_ROOM_PREFIX}{session_agent_id}')
        emit('session_deleted', deleted_data, room='agents_all')

        print(f"[INFO] 管理员 {user_id} 通过Socket删除了会话 {session_id}")

    except Exception as e:
        print(f"删除会话错误: {e}")
        emit('error', {'message': '删除失败'})


@socketio_on('join_customer_service_session')
def handle_join_customer_service_session(data):
    """加入客服会话"""
    try:
        user_id = socket_users.get(request.sid)
        if not user_id:
            return

        session_id = data.get('session_id')
        if not session_id:
            return

        session = MongoCustomerServiceSession.get(session_id)
        if not session:
            emit('error', {'message': '会话不存在'})
            return

        user = User.query.get(user_id)
        if user.is_agent:
            if session.agent_id != user.id:
                emit('error', {'message': '无权访问此会话'})
                return
        else:
            if session.user_id != user.id:
                emit('error', {'message': '无权访问此会话'})
                return

        if user.is_agent:
            AgentService.mark_messages_as_read(session_id, user_id)
        else:
            # ========== 普通用户加入会话时，主动推送当前客服在线状态 ==========
            agent_id = session.agent_id
            if agent_id:
                # 如果会话已分配客服，查询该客服状态
                agent_status = MongoAgentStatus.find_one(agent_id=agent_id)
                if agent_status:
                    online_status = agent_status.online_status
                    if online_status == 'online':
                        message = '客服已上线，可继续咨询'
                    elif online_status == 'busy':
                        message = '客服忙碌，请稍后'
                    else:
                        message = '客服暂时离线，请稍后'
                    emit('agent_availability', {
                        'message': message,
                        'online_status': online_status,
                        'agent_id': agent_id,
                        'timestamp': datetime.now().isoformat()
                    }, room=request.sid)  # 只发给当前用户
            else:
                # 会话未分配客服，查询是否有在线客服
                online_agents = AgentService.get_online_agents()
                if online_agents:
                    # 有在线客服，提示等待分配
                    emit('agent_availability', {
                        'message': '当前有客服在线，正在为您分配...',
                        'online_status': 'online',
                        'agent_id': None,
                        'timestamp': datetime.now().isoformat()
                    }, room=request.sid)
                else:
                    # 无在线客服，提示离线
                    emit('agent_availability', {
                        'message': '暂无在线客服，请稍后再试',
                        'online_status': 'offline',
                        'agent_id': None,
                        'timestamp': datetime.now().isoformat()
                    }, room=request.sid)
            # ==================================================================

        emit('session_joined', {'session_id': session_id})
        print(f"用户 {user_id} 加入会话 {session_id}")

    except Exception as e:
        print(f"加入会话错误: {e}")
        emit('error', {'message': '加入会话失败'})


@socketio_on('get_customer_service_sessions')
def handle_get_customer_service_sessions(data=None):
    """获取用户的客服会话列表"""
    try:
        user_id = socket_users.get(request.sid)
        print(f"[DEBUG] get_customer_service_sessions 被调用, user_id: {user_id}, sid: {request.sid}")
        if not user_id:
            emit('error', {'message': '未登录'})
            return

        user = User.query.get(user_id)
        if not user:
            emit('customer_service_sessions', {'sessions': []})
            return
        if user.is_admin:
            sessions_cursor = MongoCustomerServiceSession._collection.find().sort('updated_at', -1)
            sessions = [MongoCustomerServiceSession.from_dict(doc) for doc in sessions_cursor]
        elif user.is_agent:
            try:
                agent_user_id = int(user_id)
            except:
                agent_user_id = user_id

            query = {
                '$or': [
                    {'agent_id': agent_user_id},
                    {'status': 'pending'},                     # 等待客服接收的请求
                    {'status': 'pending', 'agent_id': None},
                ]
            }
            sessions_cursor = MongoCustomerServiceSession._collection.find(query).sort('updated_at', -1)
            sessions = [MongoCustomerServiceSession.from_dict(doc) for doc in sessions_cursor]
        else:
            sessions_cursor = MongoCustomerServiceSession._collection.find({'user_id': user_id}).sort('updated_at', -1)
            sessions = [MongoCustomerServiceSession.from_dict(doc) for doc in sessions_cursor]

        sessions_data = []
        for session in sessions:
            last_message = session.messages[-1] if session.messages else None
            session_user = User.query.get(session.user_id) if session.user_id else None
            session_agent = User.query.get(session.agent_id) if session.agent_id else None

            # 获取用户在线状态
            user_status_doc = MongoUserStatus._collection.find_one({'user_id': session.user_id})
            user_online = user_status_doc.get('online_status') == 'online' if user_status_doc else False

            # 计算未读数: 用户发送且未读的消息数
            unread_count = 0
            if session.messages:
                unread_count = sum(1 for m in session.messages if m.sender_type == 'user' and not m.is_read)

            sessions_data.append({
                'id': str(session._id),
                'user_id': session.user_id,
                'user_name': session_user.username if session_user else f'用户{session.user_id}',
                'user_phone': session_user.phone if session_user else None,
                'user_real_name': session_user.real_name if session_user else None,
                'user_id_card': session_user.id_card if session_user else None,
                'agent_id': session.agent_id,
                'agent_name': session_agent.username if session_agent else None,
                'status': session.status,
                'reference_type': session.reference_type,
                'reference_id': session.reference_id,
                'created_at': session.created_at.isoformat(),
                'updated_at': session.updated_at.isoformat(),
                'user_online': user_online,
                'unread_count': unread_count,
                'last_message': {
                    'content': last_message.content if last_message else '',
                    'created_at': last_message.created_at.isoformat() if last_message else None,
                    'sender_type': last_message.sender_type if last_message else None
                } if last_message else None
            })

        # 为客服/管理员追加 pending 请求到会话列表
        if user.is_agent or user.is_admin:
            existing_user_ids = {s['user_id'] for s in sessions_data if s.get('user_id')}
            for uid, pending in list(pending_human_requests.items()):
                if uid not in existing_user_ids:
                    ts = pending['timestamp'].isoformat() if isinstance(pending['timestamp'], datetime) else pending['timestamp']
                    pending_user = User.query.get(uid)
                    sessions_data.append({
                        'id': f'pending_{uid}',
                        'user_id': uid,
                        'user_name': pending['username'],
                        'user_phone': pending_user.phone if pending_user else None,
                        'user_real_name': pending_user.real_name if pending_user else None,
                        'user_id_card': pending_user.id_card if pending_user else None,
                        'agent_id': None,
                        'agent_name': None,
                        'status': 'pending',
                        'reference_type': pending.get('reference_type'),
                        'reference_id': pending.get('reference_id'),
                        'created_at': ts,
                        'updated_at': ts,
                        'user_online': True,
                        'unread_count': 0,
                        'last_message': None
                    })

        emit('customer_service_sessions', {'sessions': sessions_data})
        print(f"[DEBUG] get_customer_service_sessions: 返回 {len(sessions_data)} 个会话给用户 {user_id}")

    except Exception as e:
        print(f"获取会话列表错误: {e}")
        emit('error', {'message': '获取会话列表失败'})

@socketio_on('get_customer_service_messages')
def handle_get_customer_service_messages(data):
    """获取客服会话消息"""
    try:
        user_id = socket_users.get(request.sid)
        if not user_id:
            emit('error', {'message': '未登录'})
            return

        session_id = data.get('session_id')
        if not session_id:
            emit('error', {'message': '需要会话ID'})
            return

        session = MongoCustomerServiceSession.get(session_id)
        if not session:
            emit('error', {'message': '会话不存在'})
            return

        user = User.query.get(user_id)
        if user.is_agent:
            if session.agent_id != user.id:
                emit('error', {'message': '无权访问此会话'})
                return
        else:
            if session.user_id != user.id:
                emit('error', {'message': '无权访问此会话'})
                return

        messages = AgentService.get_session_messages(session_id)

        if user.is_agent:
            AgentService.mark_messages_as_read(session_id, user_id)

        emit('customer_service_messages', {
            'session_id': session_id,
            'messages': messages
        })

    except Exception as e:
        print(f"获取消息错误: {e}")
        emit('error', {'message': '获取消息失败'})


@socketio_on('get_user_all_history')
def handle_get_user_all_history(data):
    """获取用户所有聊天历史（机器人+所有客服会话）"""
    try:
        requester_id = socket_users.get(request.sid)
        if not requester_id:
            emit('error', {'message': '未登录'})
            return

        requester = User.query.get(requester_id)
        if not requester:
            emit('error', {'message': '用户不存在'})
            return

        target_user_id = data.get('user_id')

        # 权限校验：客服可以查任意用户，普通用户只能查自己
        if requester.is_agent:
            if not target_user_id:
                emit('error', {'message': '需要user_id'})
                return
            actual_user_id = target_user_id
        else:
            actual_user_id = requester_id

        # 查出用户的 room_id（用于机器人聊天历史）
        target_user = User.query.get(actual_user_id)
        bot_room_id = None
        if target_user:
            bot_room_id = target_user.username or target_user.phone

        # 1. 机器人聊天历史
        bot_messages = []
        if bot_room_id:
            bot_cursor = MongoChatMessage._collection.find(
                {'room_id': bot_room_id}
            ).sort('created_at', 1).limit(200)
            for msg in bot_cursor:
                bot_messages.append({
                    'source': 'bot',
                    'sender': msg.get('sender', ''),
                    'content': msg.get('content', ''),
                    'message_id': str(msg['_id']) if msg.get('_id') else None,
                    'created_at': msg['created_at'].isoformat() if isinstance(msg['created_at'], datetime) else str(msg['created_at'])
                })

        # 2. 所有客服会话的消息（包括已关闭的）
        sessions_cursor = MongoCustomerServiceSession._collection.find(
            {'user_id': actual_user_id}
        ).sort('created_at', 1)

        all_session_messages = []
        for session_doc in sessions_cursor:
            session = MongoCustomerServiceSession.from_dict(session_doc)
            for msg in (session.messages or []):
                all_session_messages.append({
                    'source': 'human',
                    'message_id': str(msg._id) if hasattr(msg, '_id') else None,
                    'session_id': str(session._id),
                    'session_status': session.status,
                    'sender_type': msg.sender_type,
                    'content': msg.content,
                    'created_at': msg.created_at.isoformat() if isinstance(msg.created_at, datetime) else str(msg.created_at)
                })

        emit('user_all_history', {
            'user_id': actual_user_id,
            'bot_messages': bot_messages,
            'session_messages': all_session_messages
        })

    except Exception as e:
        print(f"获取用户全量历史错误: {e}")
        emit('error', {'message': '获取历史记录失败'})


# ==================== 通用聊天事件（兼容前端ChatWidget）====================

@socketio_on('join')
def handle_join(data):
    """加入聊天房间（前端ChatWidget使用）"""
    try:
        room_id = data.get('room_id')
        role = data.get('role', 'user')

        if not room_id:
            emit('error', {'message': 'room_id 不能为空'})
            return

        socket_rooms[request.sid] = room_id
        join_room(room_id)

        emit('joined', {
            'room_id': room_id,
            'role': role,
            'message': f'已加入房间 {room_id}'
        })

        print(f"Socket {request.sid} 加入房间 {room_id} (角色: {role})")

    except Exception as e:
        print(f"加入房间错误: {e}")
        emit('error', {'message': '加入房间失败'})

@socketio_on('send_message')
def handle_send_message(data):
    """处理发送消息（前端ChatWidget使用）"""
    try:
        print(f"[DEBUG] handle_send_message 收到数据: {data}, sid: {request.sid}")
        room_id = data.get('room_id')
        sender = data.get('sender', 'user')
        text = data.get('text', '').strip()

        if not room_id or not text:
            emit('error', {'message': 'room_id 和 text 不能为空'})
            return

        message = MongoChatMessage(room_id=room_id, sender=sender, content=text)
        message.save()

        message_data = {
            'room_id': room_id,
            'sender': sender,
            'text': text,
            'timestamp': datetime.now().isoformat(),
            'message_id': str(message._id)
        }

        emit('receive_message', message_data, room=room_id)

        print(f"消息广播: 房间 {room_id}, 发送者 {sender}, 内容: {text[:50]}...")

        # ========== 新增：后端 FAQ 匹配自动回复 ==========
        if sender == 'user':
            try:
                from .faq_service import FAQMatcher
                matcher = FAQMatcher()
                answer, score = matcher.match(text)
                if answer:
                    bot_message = MongoChatMessage(room_id=room_id, sender='bot', content=answer)
                    bot_message.save()
                    bot_data = {
                        'room_id': room_id,
                        'sender': 'bot',
                        'text': answer,
                        'timestamp': datetime.now().isoformat(),
                        'message_id': str(bot_message._id)
                    }
                    emit('receive_message', bot_data, room=room_id)
                    print(f"FAQ匹配成功: score={score:.2f}, question_keywords='{text[:30]}...'")
                else:
                    print(f"FAQ未匹配: '{text[:50]}...'")
            except Exception as e:
                print(f"FAQ匹配出错: {e}")
        # ===============================================

    except Exception as e:
        print(f"发送消息错误: {e}")
        emit('error', {'message': '发送消息失败'})

@socketio_on('request_human')
def handle_request_human(data):
    """处理转人工客服请求（前端ChatWidget使用）"""
    try:
        print(f"[DEBUG] handle_request_human 收到数据: {data}, sid: {request.sid}, user_id: {socket_users.get(request.sid)}")
        room_id = data.get('room_id')
        reference_type = data.get('reference_type')   # 'achievement' 或 'demand'
        reference_id = data.get('reference_id')       # 成果/需求编号
        user_text = data.get('text', '').strip()      # 用户触发转人工的消息文本

        if not room_id:
            emit('error', {'message': 'room_id 不能为空'})
            return

        user_id = socket_users.get(request.sid)

        if isinstance(user_id, str) and user_id.startswith('guest_'):
            save_and_emit_system_message(room_id, '访客暂不支持人工客服，请先登录。')
            return

        if user_id:
            user = User.query.get(user_id)
            if user and not user.is_agent:
                # 保存用户触发转人工的消息文本到历史
                if user_text:
                    try:
                        user_msg = MongoChatMessage(room_id=room_id, sender='user', content=user_text)
                        user_msg.save()
                    except Exception as e:
                        print(f"[WARN] 保存用户转人工消息失败: {e}")

                # 检查是否已有活跃会话（pending/active/waiting）
                existing_session = MongoCustomerServiceSession._collection.find_one({
                    'user_id': user_id,
                    'status': {'$in': ['pending', 'active', 'waiting']}
                })
                if existing_session:
                    session = MongoCustomerServiceSession.from_dict(existing_session)
                    save_and_emit_system_message(room_id, f'您已有人工客服会话在进行中（#{str(session._id)[-8:]}），请勿重复请求。')
                    session_data = {
                        'id': str(session._id),
                        'user_id': session.user_id,
                        'agent_id': session.agent_id,
                        'status': session.status,
                        'created_at': session.created_at.isoformat(),
                        'updated_at': session.updated_at.isoformat()
                    }
                    emit('customer_service_session_created', session_data)
                    emit('customer_service_session_created', session_data, room='agents_all')
                    return

                # 检查是否有已关闭的会话，有则重新打开（复用）
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
                    # 更新引用信息（如有新的对接需求）
                    if reference_type:
                        session.reference_type = reference_type
                    if reference_id:
                        session.reference_id = reference_id
                    # 没有新的对接引用时，清除旧的引用（用户从右下角图标进入，非特定成果/需求）
                    if not reference_type and not reference_id:
                        session.reference_type = None
                        session.reference_id = None
                    session.save()
                    # 清理该用户其他未关闭的会话（防止积累重复会话）
                    MongoCustomerServiceSession._collection.update_many(
                        {'user_id': user_id, 'status': {'$in': ['pending', 'active', 'waiting']}, '_id': {'$ne': session._id}},
                        {'$set': {'status': 'closed', 'closed_at': datetime.now(), 'close_type': 'auto_merged', 'updated_at': datetime.now()}}
                    )
                    # 加入等待队列（内存缓存）
                    pending_human_requests[user_id] = {
                        'user_id': user_id,
                        'username': user.username or user.phone,
                        'room_id': room_id,
                        'reference_type': reference_type,
                        'reference_id': reference_id,
                        'timestamp': datetime.now()
                    }
                    save_and_emit_system_message(room_id, '已重新为您排队，请稍候，客服接入后会通知您。')
                    # 将会话ID通知用户，使其后续消息能正确发送到会话中
                    session_data = {
                        'id': str(session._id),
                        'user_id': session.user_id,
                        'agent_id': session.agent_id,
                        'status': session.status,
                        'created_at': session.created_at.isoformat(),
                        'updated_at': session.updated_at.isoformat()
                    }
                    emit('customer_service_session_created', session_data)
                    emit('pending_human_request', {
                        'user_id': user_id,
                        'username': user.username or user.phone,
                        'phone': user.phone or '',
                        'room_id': room_id,
                        'reference_type': reference_type,
                        'reference_id': reference_id,
                        'timestamp': datetime.now().isoformat()
                    }, room='agents_all')
                    print(f"转人工请求: 用户 {user_id} 重新打开已关闭会话 {str(session._id)}")
                    return

                # 检查是否已在等待队列（字典或 MongoDB）
                if user_id in pending_human_requests:
                    save_and_emit_system_message(room_id, '您已在等待队列中，请稍候，客服接入后会通知您。')
                    return

                # 检查 MongoDB 中是否有持久化的 pending 会话（服务重启后重建缓存）
                pending_in_db = MongoCustomerServiceSession._collection.find_one({
                    'user_id': user_id,
                    'status': 'pending'
                })
                if pending_in_db:
                    pending_human_requests[user_id] = {
                        'user_id': user_id,
                        'username': user.username or user.phone,
                        'room_id': room_id,
                        'timestamp': datetime.now()
                    }
                    save_and_emit_system_message(room_id, '您已在等待队列中，请稍候，客服接入后会通知您。')
                    return

                # 加入等待队列（内存 + MongoDB持久化）
                pending_human_requests[user_id] = {
                    'user_id': user_id,
                    'username': user.username or user.phone,
                    'room_id': room_id,
                    'reference_type': reference_type,
                    'reference_id': reference_id,
                    'timestamp': datetime.now()
                }

                # 持久化到 MongoDB（防止页面刷新或服务重启后丢失）
                try:
                    pending_session = MongoCustomerServiceSession(
                        user_id=user_id,
                        status='pending',
                        agent_id=None,
                        reference_type=reference_type,
                        reference_id=reference_id
                    )
                    pending_session.save()
                except Exception as e:
                    err_msg = str(e)
                    if 'duplicate key' in err_msg.lower() or 'DuplicateKey' in err_msg:
                        # 竞态：另一个转人工请求已创建了 pending 会话
                        print(f"[WARN] 用户 {user_id} 的 pending 会话已存在（并发创建），跳过持久化")
                        pending_human_requests.pop(user_id, None)
                        save_and_emit_system_message(room_id, '您已在等待队列中，请稍候，客服接入后会通知您。')
                        return
                    print(f"[WARN] 保存 pending 会话到 MongoDB 失败: {e}")

                save_and_emit_system_message(room_id, '已收到您的人工客服请求，请稍候，客服接入后会通知您。')

                # 将会话ID通知用户，使其后续消息能正确发送到会话中
                session_data = {
                    'id': str(pending_session._id),
                    'user_id': user_id,
                    'agent_id': None,
                    'status': 'pending',
                    'created_at': pending_session.created_at.isoformat(),
                    'updated_at': pending_session.updated_at.isoformat()
                }
                emit('customer_service_session_created', session_data)

                # 通知客服有新请求
                emit('pending_human_request', {
                    'user_id': user_id,
                    'username': user.username or user.phone,
                    'phone': user.phone or '',
                    'room_id': room_id,
                    'reference_type': reference_type,
                    'reference_id': reference_id,
                    'timestamp': datetime.now().isoformat()
                }, room='agents_all')

                print(f"转人工请求: 用户 {user_id} 已加入等待队列")
            else:
                save_and_emit_system_message(room_id, '您已经是客服或用户信息异常。')
        else:
            save_and_emit_system_message(room_id, '未识别用户，请重新登录。')

    except Exception as e:
        print(f"转人工请求错误: {e}")
        emit('error', {'message': '转人工请求失败'})


@socketio_on('accept_human_request')
def handle_accept_human_request(data):
    """客服接受人工客服请求，创建会话"""
    try:
        agent_id = socket_users.get(request.sid)
        if not agent_id:
            emit('error', {'message': '未登录'})
            return

        agent = User.query.get(agent_id)
        if not agent or not agent.is_agent:
            emit('error', {'message': '只有客服可以接受请求'})
            return

        user_id = data.get('user_id')
        if not user_id:
            emit('error', {'message': '需要用户ID'})
            return

        # 从等待队列中取出（移除内存缓存）
        pending_human_requests.pop(user_id, None)

        # 二次检查：防止竞态条件导致用户已有活跃会话（pending 的除外，我们正要接受它）
        existing_active = MongoCustomerServiceSession._collection.find_one({
            'user_id': user_id,
            'status': 'active'
        })
        if existing_active:
            emit('error', {'message': '该用户已有进行中的会话，无需重复接受'})
            return

        # 从 MongoDB 查找持久化的 pending 会话
        pending_doc = MongoCustomerServiceSession._collection.find_one({
            'user_id': user_id,
            'status': 'pending'
        })
        if not pending_doc:
            emit('error', {'message': '该用户不在等待队列中或已被其他客服接受'})
            return

        session = MongoCustomerServiceSession.from_dict(pending_doc)
        session.status = 'active'
        session.agent_id = agent_id
        # 添加欢迎消息（防重：检查所有历史消息中是否已有相同欢迎语，防止竞争条件导致重复）
        welcome_text = f'您好，人工客服(编号: {agent_id})已接入，请详细描述您遇到的问题。'
        existing_welcome = None
        for m in (session.messages or []):
            if m.content == welcome_text:
                existing_welcome = m
                break
        if existing_welcome:
            message = existing_welcome
            print(f"[防重] 会话 {str(session._id)} 已有欢迎语，跳过重复添加")
        else:
            message = session.add_message('agent', agent_id, welcome_text)
        session.save()

        # 更新客服状态
        agent_status = MongoAgentStatus.find_one(agent_id=agent_id)
        if agent_status:
            agent_status.current_session_id = str(session._id)
            agent_status.last_heartbeat = datetime.now()
            agent_status.save()

        session_data = {
            'id': str(session._id),
            'user_id': session.user_id,
            'agent_id': session.agent_id,
            'status': session.status,
            'created_at': session.created_at.isoformat(),
            'updated_at': session.updated_at.isoformat()
        }

        # 通知用户
        emit('customer_service_session_created', session_data, room=f'{USER_ROOM_PREFIX}{user_id}')

        # 通知所有客服（新会话来了，该 pending 已消失）
        emit('customer_service_session_created', session_data, room='agents_all')

        # 给用户推送欢迎消息
        message_data = {
            'id': str(message._id),
            'session_id': str(session._id),
            'sender_type': 'agent',
            'sender_id': agent_id,
            'sender_name': agent.username or agent.phone,
            'content': message.content,
            'created_at': message.created_at.isoformat(),
            'is_read': message.is_read
        }
        # 直接推送欢迎消息到用户端，确保即时通知
        emit('new_customer_service_message', message_data, room=f'{USER_ROOM_PREFIX}{user_id}')
        # 也推送给客服端，让客服的聊天窗口同步显示欢迎语
        emit('new_customer_service_message', message_data, room=f'{AGENT_ROOM_PREFIX}{agent_id}')
        # 通知用户刷新（从 MongoDB 获取欢迎语等历史消息）
        emit('customer_session_refresh', {
            'session_id': str(session._id),
            'unread_count': 0,
            'reference_type': session.reference_type,
            'reference_id': session.reference_id,
            'last_message': {
                'content': message_data['content'],
                'created_at': message_data['created_at']
            }
        }, room=f'{USER_ROOM_PREFIX}{user_id}')

        print(f"客服接受请求: 客服 {agent_id} 接受了用户 {user_id} 的请求，会话 {str(session._id)} 已创建")

    except Exception as e:
        print(f"接受请求错误: {e}")
        emit('error', {'message': '接受请求失败'})


@socketio_on('close_customer_service_session')
def handle_close_customer_service_session(data):
    """处理关闭客服会话（用户或客服均可触发）"""
    try:
        user_id = socket_users.get(request.sid)
        if not user_id:
            emit('error', {'message': '未登录'})
            return

        session_id = data.get('session_id')
        if not session_id:
            emit('error', {'message': '需要会话ID'})
            return

        session = MongoCustomerServiceSession.get(session_id)
        if not session:
            emit('error', {'message': '会话不存在'})
            return

        user = User.query.get(user_id)
        if not user:
            emit('error', {'message': '用户不存在'})
            return

        # 权限校验
        if user.is_agent:
            if session.agent_id != user.id:
                emit('error', {'message': '无权操作此会话'})
                return
            close_type = 'agent_closed'
        else:
            if session.user_id != user.id:
                emit('error', {'message': '无权操作此会话'})
                return
            close_type = 'user_closed'

        # 已关闭则忽略
        if session.status == 'closed':
            emit('error', {'message': '会话已关闭'})
            return

        # 关闭会话
        session.status = 'closed'
        session.closed_at = datetime.now()
        session.close_type = close_type
        session.updated_at = datetime.now()
        session.save()

        # 释放客服
        if session.agent_id:
            AgentService.release_agent(session.agent_id)

        # 保存结束系统消息到通用聊天历史并实时推送
        # 这条消息通过 receive_message 事件即时显示，也会随历史加载持久出现
        close_text = '客服已结束会话' if close_type == 'agent_closed' else '用户已结束会话'
        room_id = user.phone or f"user_{user.id}"
        save_and_emit_system_message(room_id, close_text)

        # 通知所有客服刷新列表
        session_closed_data = {
            'session_id': session_id,
            'closed_at': session.closed_at.isoformat(),
            'close_type': close_type,
            'initiated_by': 'agent' if user.is_agent else 'user'
        }
        # 通知负责该会话的客服刷新状态
        if session.agent_id:
            emit('session_closed', session_closed_data, room=f'{AGENT_ROOM_PREFIX}{session.agent_id}')

        # 通知对应用户（客服关闭时需要让用户知道）
        if session.user_id:
            emit('session_closed', session_closed_data, room=f'{USER_ROOM_PREFIX}{session.user_id}')

        # 也发给发起者自己，方便前端统一处理
        emit('session_closed', session_closed_data)

        print(f"会话关闭: {session_id}, 类型: {close_type}, 操作者: {user_id}")

    except Exception as e:
        print(f"关闭会话错误: {e}")
        emit('error', {'message': '关闭会话失败'})