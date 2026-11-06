from flask import Blueprint, jsonify, request, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models import User
from ..mongo_models import MongoCustomerServiceSession, MongoCustomerServiceMessage, MongoAgentStatus, MongoChatMessage, FAQ
from ..services import AgentService
from ..faq_service import FAQMatcher
from datetime import datetime, timedelta
import functools
from bson import ObjectId

chat_bp = Blueprint('chat', __name__)

# 角色验证装饰器
def role_required(*allowed_roles):
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = g.user_id
            user = User.query.get(user_id)
            if not user:
                return jsonify({"code": 401, "msg": "用户不存在"}), 401
            if user.role not in allowed_roles:
                return jsonify({"code": 403, "msg": "权限不足"}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Token验证装饰器
def token_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        # 放行 OPTIONS 请求
        if request.method == 'OPTIONS':
            return '', 200

        auth_header = request.headers.get('Authorization', '')
        token = None
        if auth_header.startswith('Bearer '):
            token = auth_header[7:].strip()
        elif 'token' in request.args:
            token = request.args.get('token')

        if not token:
            return jsonify({"code": 401, "msg": "缺少访问令牌"}), 401

        if token.startswith('user_token_'):
            try:
                parts = token.split('_')
                if len(parts) >= 3:
                    user_id = int(parts[2])
                    user = User.query.get(user_id)
                    if user:
                        if user.status != 1:
                            return jsonify({"code": 401, "msg": "账号已被禁用"}), 401
                        g.user_id = user_id
                        return f(*args, **kwargs)
                    else:
                        return jsonify({"code": 401, "msg": "用户不存在"}), 401
                else:
                    return jsonify({"code": 401, "msg": "无效的token格式"}), 401
            except (ValueError, IndexError):
                return jsonify({"code": 401, "msg": "token解析失败"}), 401

        try:
            from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, exceptions
            verify_jwt_in_request()
            g.user_id = int(get_jwt_identity())
            try:
                user = User.query.get(g.user_id)
                if user and user.status != 1:
                    return jsonify({"code": 401, "msg": "账号已被禁用"}), 401
            except Exception:
                pass
            return f(*args, **kwargs)
        except exceptions.JWTExtendedException:
            return jsonify({"code": 401, "msg": "JWT token无效或已过期"}), 401
    return decorated_function

# 健康检查
@chat_bp.route('/health', methods=['GET'])
def chat_health():
    return jsonify({"code": 200, "msg": "聊天模块正常"})

# 获取客服会话列表
@chat_bp.route('/customer-service/sessions', methods=['GET'])
@token_required
def get_customer_service_sessions():
    user_id = g.user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 401, "msg": "用户不存在"}), 401

    # 查询参数
    keyword = (request.args.get('keyword') or '').strip()
    status = (request.args.get('status') or '').strip()
    date_from = (request.args.get('date_from') or '').strip()
    date_to = (request.args.get('date_to') or '').strip()
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)

    if user.is_admin:
        # 构建 MongoDB 查询
        query = {}

        # 状态筛选
        if status and status in ['pending', 'active', 'closed']:
            query['status'] = status

        # 日期范围
        if date_from or date_to:
            date_filter = {}
            if date_from:
                date_filter['$gte'] = datetime.fromisoformat(date_from)
            if date_to:
                date_filter['$lte'] = datetime.fromisoformat(date_to.replace(' ', 'T')) + timedelta(days=1)
            if date_filter:
                query['created_at'] = date_filter

        # 关键词搜索（用户名/手机号/消息内容）
        if keyword:
            # 先在 MySQL 查匹配的用户
            matched_users = User.query.filter(
                db.or_(
                    User.username.contains(keyword),
                    User.phone.contains(keyword),
                    User.real_name.contains(keyword)
                )
            ).all()
            matched_user_ids = [u.id for u in matched_users]

            conditions = []
            if matched_user_ids:
                conditions.append({'user_id': {'$in': matched_user_ids}})
            # 同时在会话消息内容中搜索
            conditions.append({'messages.content': {'$regex': keyword, '$options': 'i'}})
            if conditions:
                query['$or'] = conditions

        total = MongoCustomerServiceSession._collection.count_documents(query)
        sessions_cursor = MongoCustomerServiceSession._collection.find(query) \
            .sort('updated_at', -1) \
            .skip((page - 1) * page_size) \
            .limit(page_size)
        sessions = [MongoCustomerServiceSession.from_dict(doc) for doc in sessions_cursor]
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    elif user.is_agent:
        query = {
            '$or': [
                {'agent_id': user_id},
                {'status': 'pending', 'agent_id': None}
            ]
        }
        sessions_cursor = MongoCustomerServiceSession._collection.find(query).sort('updated_at', -1)
        sessions = [MongoCustomerServiceSession.from_dict(doc) for doc in sessions_cursor]
        total = len(sessions)
        total_pages = 0
    else:
        sessions_cursor = MongoCustomerServiceSession._collection.find({'user_id': user_id}).sort('updated_at', -1)
        sessions = [MongoCustomerServiceSession.from_dict(doc) for doc in sessions_cursor]
        total = len(sessions)
        total_pages = 0

    sessions_data = []
    for session in sessions:
        last_message = session.messages[-1] if session.messages else None
        unread_count = session.get_unread_count(user_id) if hasattr(session, 'get_unread_count') else 0
        session_user = User.query.get(session.user_id) if session.user_id else None
        session_agent = User.query.get(session.agent_id) if session.agent_id else None
        message_count = len(session.messages) if session.messages else 0

        sessions_data.append({
            'id': str(session._id),
            'user_id': session.user_id,
            'user_name': session_user.username if session_user else f'用户{session.user_id}',
            'user_phone': session_user.phone if session_user else None,
            'user_real_name': session_user.real_name if session_user else None,
            'agent_id': session.agent_id,
            'agent_name': session_agent.username if session_agent else None,
            'status': session.status,
            'close_type': session.close_type if hasattr(session, 'close_type') else None,
            'closed_at': session.closed_at.isoformat() if hasattr(session, 'closed_at') and session.closed_at else None,
            'created_at': session.created_at.isoformat() if session.created_at else None,
            'updated_at': session.updated_at.isoformat() if session.updated_at else None,
            'unread_count': unread_count,
            'message_count': message_count,
            'last_message': {
                'content': last_message.content if last_message else '',
                'created_at': last_message.created_at.isoformat() if last_message else None,
                'sender_type': last_message.sender_type if last_message else None
            } if last_message else None
        })

    result = {"code": 200, "data": sessions_data}
    if user.is_admin:
        result['total'] = total
        result['page'] = page
        result['page_size'] = page_size
        result['total_pages'] = total_pages
    return jsonify(result)

# 获取会话消息（修复类型 + OPTIONS）
@chat_bp.route('/customer-service/sessions/<string:session_id>/messages', methods=['GET', 'OPTIONS'])
@token_required
def get_session_messages(session_id):
    if request.method == 'OPTIONS':
        return '', 200

    user_id = g.user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 401, "msg": "用户不存在"}), 401

    try:
        obj_id = ObjectId(session_id)
    except:
        return jsonify({"code": 400, "msg": "无效的会话ID"}), 400

    session_dict = MongoCustomerServiceSession._collection.find_one({'_id': obj_id})
    if not session_dict:
        return jsonify({"code": 404, "msg": "会话不存在"}), 404
    session = MongoCustomerServiceSession.from_dict(session_dict)

    if not user.is_admin:
        if user.is_agent:
            if session.agent_id != user.id:
                return jsonify({"code": 403, "msg": "无权访问此会话"}), 403
        else:
            if session.user_id != user.id:
                return jsonify({"code": 403, "msg": "无权访问此会话"}), 403

    limit = request.args.get('limit', 50, type=int)
    messages = session.messages if session.messages else []
    messages = sorted(messages, key=lambda msg: msg.created_at)
    if limit and limit < len(messages):
        messages = messages[:limit]

    messages_data = [{
        'id': str(msg._id),
        'sender_type': msg.sender_type,
        'sender_id': msg.sender_id,
        'content': msg.content,
        'created_at': msg.created_at.isoformat(),
        'is_read': msg.is_read
    } for msg in messages]

    if user.is_agent:
        session.mark_messages_as_read(user_id)
        session.save()

    return jsonify({"code": 200, "data": messages_data})

# 创建客服会话
@chat_bp.route('/customer-service/sessions', methods=['POST'])
@token_required
def create_customer_service_session():
    user_id = g.user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 401, "msg": "用户不存在"}), 401
    if user.is_agent:
        return jsonify({"code": 400, "msg": "客服不能创建客服会话"}), 400

    session = AgentService.create_session(user_id)
    session_data = {
        'id': str(session._id),
        'user_id': session.user_id,
        'agent_id': session.agent_id,
        'status': session.status,
        'created_at': session.created_at.isoformat(),
        'updated_at': session.updated_at.isoformat()
    }
    return jsonify({"code": 200, "data": session_data, "msg": "会话创建成功"})

# 获取在线客服列表
@chat_bp.route('/customer-service/online-agents', methods=['GET', 'OPTIONS'])
@token_required
def get_online_agents():
    user_id = g.user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 401, "msg": "用户不存在"}), 401
    online_agents = AgentService.get_online_agents()
    return jsonify({"code": 200, "data": online_agents})

# 更新客服状态
# 更新客服状态
@chat_bp.route('/customer-service/agent/status', methods=['POST'])
@token_required
def update_agent_status():
    user_id = g.user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 401, "msg": "用户不存在"}), 401
    if not user.is_agent:
        return jsonify({"code": 403, "msg": "只有客服可以更新状态"}), 403

    data = request.get_json()
    status = data.get('status')
    if status not in ['online', 'busy', 'offline']:
        return jsonify({"code": 400, "msg": "状态值无效"}), 400

    # 更新数据库中的客服状态
    agent_status = MongoAgentStatus.find_one(agent_id=user_id)
    if not agent_status:
        agent_status = MongoAgentStatus(agent_id=user_id, online_status=status, last_heartbeat=datetime.now())
        agent_status.save()
    else:
        agent_status.online_status = status
        agent_status.last_heartbeat = datetime.now()
        agent_status.save()

    # ========== 新增：通过 Socket.IO 实时广播状态变更 ==========
    try:
        from flask_socketio import emit
        # 构建查询条件：所有等待中的会话 + 已分配给该客服的进行中会话
        query = {
            '$or': [
                {'agent_id': user_id, 'status': 'active'},
                {'status': 'pending'}
            ]
        }
        related_sessions = MongoCustomerServiceSession._collection.find(query)
        message = '客服已上线，可继续咨询' if status == 'online' else '客服暂时离线，请稍后'
        sent_count = 0
        for session_doc in related_sessions:
            session_user_id = session_doc.get('user_id')
            if session_user_id:
                # 向用户专属房间发送事件
                emit('agent_availability', {
                    'message': message,
                    'online_status': status,
                    'agent_id': user_id,
                    'timestamp': datetime.now().isoformat()
                }, room=f'user_{session_user_id}', namespace='/')
                sent_count += 1
        print(f"[INFO] 手动切换状态：已向 {sent_count} 个关联会话的用户广播客服状态: {status}")
    except Exception as e:
        print(f"[WARN] 广播客服状态失败: {e}")
    # =================================================

    return jsonify({"code": 200, "msg": "状态更新成功"})

# 关闭会话（修复类型 + OPTIONS）
@chat_bp.route('/customer-service/sessions/<string:session_id>/close', methods=['POST', 'OPTIONS'])
@token_required
def close_customer_service_session(session_id):
    if request.method == 'OPTIONS':
        return '', 200

    user_id = g.user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 401, "msg": "用户不存在"}), 401

    try:
        obj_id = ObjectId(session_id)
    except:
        return jsonify({"code": 400, "msg": "无效的会话ID"}), 400

    session_dict = MongoCustomerServiceSession._collection.find_one({'_id': obj_id})
    if not session_dict:
        return jsonify({"code": 404, "msg": "会话不存在"}), 404
    session = MongoCustomerServiceSession.from_dict(session_dict)

    if user.is_agent:
        if session.agent_id != user.id:
            return jsonify({"code": 403, "msg": "无权操作此会话"}), 403
        close_type = 'agent_closed'
    else:
        if session.user_id != user.id:
            return jsonify({"code": 403, "msg": "无权操作此会话"}), 403
        close_type = 'user_closed'

    if session.status == 'closed':
        return jsonify({"code": 400, "msg": "会话已关闭"}), 400

    session.status = 'closed'
    session.closed_at = datetime.now()
    session.close_type = close_type
    session.updated_at = datetime.now()
    session.save()
    if session.agent_id:
        AgentService.release_agent(session.agent_id)

    # 通过 Socket.IO 通知双方
    try:
        from flask_socketio import emit
        session_closed_data = {
            'session_id': session_id,
            'closed_at': session.closed_at.isoformat(),
            'close_type': close_type,
            'initiated_by': 'agent' if user.is_agent else 'user'
        }
        emit('session_closed', session_closed_data,
             room=f'session_{session_id}')
    except Exception as e:
        print(f"[WARN] REST 关闭会话时广播 Socket 事件失败: {e}")

    return jsonify({"code": 200, "msg": "会话已关闭"})

# 删除会话（仅管理员）
@chat_bp.route('/customer-service/sessions/<string:session_id>', methods=['DELETE', 'OPTIONS'])
@token_required
def delete_customer_service_session(session_id):
    if request.method == 'OPTIONS':
        return '', 200

    user_id = g.user_id
    user = User.query.get(user_id)
    if not user or not user.is_admin:
        return jsonify({"code": 403, "msg": "仅管理员可删除会话"}), 403

    try:
        obj_id = ObjectId(session_id)
    except:
        return jsonify({"code": 400, "msg": "无效的会话ID"}), 400

    session_dict = MongoCustomerServiceSession._collection.find_one({'_id': obj_id})
    if not session_dict:
        return jsonify({"code": 404, "msg": "会话不存在"}), 404
    session = MongoCustomerServiceSession.from_dict(session_dict)

    # 保存用户和客服信息用于通知
    session_user_id = session.user_id
    session_agent_id = session.agent_id

    # 如果会话进行中，先释放客服
    if session.status in ('active', 'pending', 'waiting') and session_agent_id:
        AgentService.release_agent(session_agent_id)

    # 删除会话（含所有嵌入消息）
    result = session.delete()
    print(f"[DEBUG] 删除会话 {session_id}: result={result}")

    # 通过 Socket.IO 通知双方会话已删除
    try:
        from ..socket_events import get_socketio
        sio = get_socketio()
        if sio:
            deleted_data = {
                'session_id': session_id,
                'user_id': session_user_id,
                'agent_id': session_agent_id,
                'deleted_by': 'admin'
            }
            if session_user_id:
                sio.emit('session_deleted', deleted_data, room=f'user_{session_user_id}')
            if session_agent_id:
                sio.emit('session_deleted', deleted_data, room=f'agent_{session_agent_id}')
            sio.emit('session_deleted', deleted_data, room='agents_all')
            print(f"[INFO] 已广播 session_deleted 事件: user_{session_user_id}, agent_{session_agent_id}, agents_all")
        else:
            print("[WARN] 无法获取 socketio 实例（_socketio 为 None）")
    except Exception as e:
        import traceback
        print(f"[WARN] 删除会话时广播 Socket 事件失败: {e}")
        traceback.print_exc()

    print(f"[INFO] 管理员 {user_id} 删除了会话 {session_id}（用户: {session_user_id}, 客服: {session_agent_id}）")
    return jsonify({"code": 200, "msg": "会话已删除"})

# 批量删除某用户的所有会话（仅管理员）
@chat_bp.route('/customer-service/sessions/by-user/<int:target_user_id>', methods=['DELETE', 'OPTIONS'])
@token_required
def delete_user_all_sessions(target_user_id):
    if request.method == 'OPTIONS':
        return '', 200

    user_id = g.user_id
    user = User.query.get(user_id)
    if not user or not user.is_admin:
        return jsonify({"code": 403, "msg": "仅管理员可删除会话"}), 403

    # 查找该用户所有会话
    sessions_cursor = MongoCustomerServiceSession._collection.find({'user_id': target_user_id})
    sessions = [MongoCustomerServiceSession.from_dict(doc) for doc in sessions_cursor]

    if not sessions:
        # 没有客服会话，但可能仍有机器人聊天记录，继续清理
        pass

    deleted_count = 0
    session_agent_ids = set()

    for session in sessions:
        if session.agent_id and session.status in ('active', 'pending', 'waiting'):
            session_agent_ids.add(session.agent_id)
        session.delete()
        deleted_count += 1

    # 同时删除该用户的机器人聊天记录（使用用户名和手机号两个可能的room_id）
    target_user = User.query.get(target_user_id)
    bot_room_id = (target_user.username or target_user.phone) if target_user else None
    bot_deleted = 0
    if bot_room_id:
        bot_result = MongoChatMessage._collection.delete_many({'room_id': bot_room_id})
        bot_deleted = bot_result.deleted_count
        print(f"[INFO] 已删除用户 {target_user_id} 的 {bot_deleted} 条机器人聊天记录 (room_id={bot_room_id})")
    # 兜底：用户名和手机号不同时，再尝试用手机号删除
    if target_user and target_user.username and target_user.phone and target_user.username != target_user.phone:
        bot_result2 = MongoChatMessage._collection.delete_many({'room_id': target_user.phone})
        if bot_result2.deleted_count > 0:
            bot_deleted += bot_result2.deleted_count
            print(f"[INFO] 额外删除 room_id={target_user.phone} 的 {bot_result2.deleted_count} 条机器人记录")

    # 如果没有任何可删除的内容
    if deleted_count == 0 and bot_deleted == 0:
        return jsonify({"code": 404, "msg": "该用户没有聊天记录"}), 404

    # 释放所有涉及的客服
    for agent_id in session_agent_ids:
        AgentService.release_agent(agent_id)

    # 通过 Socket.IO 通知用户和所有相关客服
    try:
        from ..socket_events import get_socketio
        sio = get_socketio()
        if sio:
            deleted_data = {
                'user_id': target_user_id,
                'deleted_count': deleted_count,
                'deleted_by': 'admin'
            }
            # 通知用户
            sio.emit('session_deleted', deleted_data, room=f'user_{target_user_id}')
            # 通知相关客服
            for agent_id in session_agent_ids:
                sio.emit('session_deleted', deleted_data, room=f'agent_{agent_id}')
            # 通知所有客服刷新列表
            sio.emit('session_deleted', deleted_data, room='agents_all')
            print(f"[INFO] 已广播 session_deleted 事件: user_{target_user_id}, {len(session_agent_ids)}个客服, agents_all")
    except Exception as e:
        import traceback
        print(f"[WARN] 批量删除时广播 Socket 事件失败: {e}")
        traceback.print_exc()

    print(f"[INFO] 管理员 {user_id} 批量删除了用户 {target_user_id} 的 {deleted_count} 条会话 + {bot_deleted} 条机器人聊天记录")
    return jsonify({"code": 200, "msg": f"已删除 {deleted_count} 条会话和 {bot_deleted} 条机器人聊天记录", "data": {"deleted_count": deleted_count, "bot_deleted": bot_deleted}})

# 发送客服消息（HTTP备用，修复类型 + OPTIONS）
@chat_bp.route('/customer-service/sessions/<string:session_id>/messages', methods=['POST', 'OPTIONS'])
@token_required
def send_customer_service_message(session_id):
    if request.method == 'OPTIONS':
        return '', 200

    user_id = g.user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 401, "msg": "用户不存在"}), 401

    data = request.get_json()
    content = data.get('content')
    if not content or not content.strip():
        return jsonify({"code": 400, "msg": "消息内容不能为空"}), 400

    try:
        obj_id = ObjectId(session_id)
    except:
        return jsonify({"code": 400, "msg": "无效的会话ID"}), 400

    session_dict = MongoCustomerServiceSession._collection.find_one({'_id': obj_id})
    if not session_dict:
        return jsonify({"code": 404, "msg": "会话不存在"}), 404
    session = MongoCustomerServiceSession.from_dict(session_dict)

    if user.is_agent:
        if session.agent_id != user.id:
            return jsonify({"code": 403, "msg": "无权访问此会话"}), 403
        sender_type = 'agent'
    else:
        if session.user_id != user.id:
            return jsonify({"code": 403, "msg": "无权访问此会话"}), 403
        sender_type = 'user'

    message = session.add_message(sender_type, user_id, content.strip())
    session.save()
    message_data = {
        'id': str(message._id),
        'session_id': str(session._id),
        'sender_type': sender_type,
        'sender_id': user_id,
        'content': message.content,
        'created_at': message.created_at.isoformat(),
        'is_read': message.is_read
    }
    return jsonify({"code": 200, "data": message_data, "msg": "消息发送成功"})

# 标记已读（修复类型 + OPTIONS，当前前端已注释调用，但保留修复）
@chat_bp.route('/customer-service/sessions/<string:session_id>/mark-read', methods=['POST', 'OPTIONS'])
@token_required
def mark_session_messages_read(session_id):
    if request.method == 'OPTIONS':
        return '', 200

    user_id = g.user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 401, "msg": "用户不存在"}), 401

    try:
        obj_id = ObjectId(session_id)
    except:
        return jsonify({"code": 400, "msg": "无效的会话ID"}), 400

    session_dict = MongoCustomerServiceSession._collection.find_one({'_id': obj_id})
    if not session_dict:
        return jsonify({"code": 404, "msg": "会话不存在"}), 404
    session = MongoCustomerServiceSession.from_dict(session_dict)

    if not user.is_admin:
        if user.is_agent:
            if session.agent_id != user.id:
                return jsonify({"code": 403, "msg": "无权操作此会话"}), 403
        else:
            if session.user_id != user.id:
                return jsonify({"code": 403, "msg": "无权操作此会话"}), 403

    updated_count = AgentService.mark_messages_as_read(session_id, user_id)
    return jsonify({"code": 200, "msg": "消息已标记为已读", "count": updated_count})

# 获取客服会话详情
@chat_bp.route('/customer-service/sessions/<string:session_id>', methods=['GET'])
@token_required
def get_customer_service_session_detail(session_id):
    user_id = g.user_id
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 401, "msg": "用户不存在"}), 401

    try:
        obj_id = ObjectId(session_id)
    except:
        return jsonify({"code": 400, "msg": "无效的会话ID"}), 400

    session_dict = MongoCustomerServiceSession._collection.find_one({'_id': obj_id})
    if not session_dict:
        return jsonify({"code": 404, "msg": "会话不存在"}), 404
    session = MongoCustomerServiceSession.from_dict(session_dict)

    if user.is_agent:
        if session.agent_id != user.id:
            return jsonify({"code": 403, "msg": "无权访问此会话"}), 403
    else:
        if session.user_id != user.id:
            return jsonify({"code": 403, "msg": "无权访问此会话"}), 403

    session_user = User.query.get(session.user_id) if session.user_id else None
    session_agent = User.query.get(session.agent_id) if session.agent_id else None
    message_count = len(session.messages) if session.messages else 0
    unread_count = session.get_unread_count(user_id) if hasattr(session, 'get_unread_count') else 0

    session_data = {
        'id': str(session._id),
        'user_id': session.user_id,
        'user_name': session_user.username if session_user else f'用户{session.user_id}',
        'user_phone': session_user.phone if session_user else None,
        'agent_id': session.agent_id,
        'agent_name': session_agent.username if session_agent else None,
        'status': session.status,
        'created_at': session.created_at.isoformat(),
        'updated_at': session.updated_at.isoformat(),
        'message_count': message_count,
        'unread_count': unread_count,
        'last_message': None
    }

    if session.messages and len(session.messages) > 0:
        last_message = session.messages[-1]
        session_data['last_message'] = {
            'content': last_message.content,
            'created_at': last_message.created_at.isoformat(),
            'sender_type': last_message.sender_type
        }

    return jsonify({"code": 200, "data": session_data})

# ==================== FAQ 知识库管理 API ====================

@chat_bp.route('/faqs', methods=['GET'])
@token_required
def get_faqs():
    """获取FAQ列表（客服/管理员查看，支持搜索和状态筛选）"""
    user_id = g.user_id
    user = User.query.get(user_id)
    if not user or not (user.is_agent or user.is_admin):
        return jsonify({"code": 403, "msg": "权限不足"}), 403

    keyword = request.args.get('keyword', '').strip()
    status = request.args.get('status', '')
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)

    query = {}
    if keyword:
        query['question'] = {'$regex': keyword, '$options': 'i'}
    if status and status in ['draft', 'published']:
        query['status'] = status

    total = FAQ._collection.count_documents(query)
    cursor = FAQ._collection.find(query).sort('updated_at', -1).skip((page - 1) * page_size).limit(page_size)
    faqs = []
    for doc in cursor:
        faqs.append({
            'id': str(doc['_id']),
            'question': doc.get('question', ''),
            'answer': doc.get('answer', ''),
            'display_text': doc.get('display_text', ''),
            'status': doc.get('status', 'published'),
            'created_at': doc['created_at'].isoformat() if doc.get('created_at') else None,
            'updated_at': doc['updated_at'].isoformat() if doc.get('updated_at') else None
        })

    return jsonify({
        "code": 200,
        "data": {
            "faqs": faqs,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    })


@chat_bp.route('/faqs', methods=['POST', 'OPTIONS'])
@token_required
def create_faq():
    """创建FAQ（管理员）"""
    if request.method == 'OPTIONS':
        return '', 200

    user_id = g.user_id
    user = User.query.get(user_id)
    if not user or not user.is_admin:
        return jsonify({"code": 403, "msg": "只有管理员可以创建FAQ"}), 403

    data = request.get_json()
    question = (data.get('question') or '').strip()
    answer = (data.get('answer') or '').strip()
    display_text = (data.get('display_text') or '').strip()
    status = data.get('status', 'published')

    if not question or not answer:
        return jsonify({"code": 400, "msg": "问题和答案不能为空"}), 400
    if status not in ['draft', 'published']:
        return jsonify({"code": 400, "msg": "状态值无效"}), 400

    existing = FAQ._collection.find_one({'question': question})
    if existing:
        return jsonify({"code": 400, "msg": "该问题已存在"}), 400

    faq = FAQ(question=question, answer=answer, display_text=display_text, status=status)
    faq.save()
    # 通知匹配器刷新
    FAQMatcher.mark_dirty()

    return jsonify({
        "code": 200,
        "data": {
            "id": str(faq._id),
            "question": faq.question,
            "answer": faq.answer,
            "status": faq.status,
            "created_at": faq.created_at.isoformat() if faq.created_at else None
        },
        "msg": "FAQ创建成功"
    })


@chat_bp.route('/faqs/<string:faq_id>', methods=['PUT', 'OPTIONS'])
@token_required
def update_faq(faq_id):
    """更新FAQ（管理员）"""
    if request.method == 'OPTIONS':
        return '', 200

    user_id = g.user_id
    user = User.query.get(user_id)
    if not user or not user.is_admin:
        return jsonify({"code": 403, "msg": "只有管理员可以修改FAQ"}), 403

    try:
        obj_id = ObjectId(faq_id)
    except Exception:
        return jsonify({"code": 400, "msg": "无效的FAQ ID"}), 400

    doc = FAQ._collection.find_one({'_id': obj_id})
    if not doc:
        return jsonify({"code": 404, "msg": "FAQ不存在"}), 404

    data = request.get_json()
    question = (data.get('question') or '').strip()
    answer = (data.get('answer') or '').strip()
    display_text = (data.get('display_text') or '').strip()
    status = data.get('status')

    if not question or not answer:
        return jsonify({"code": 400, "msg": "问题和答案不能为空"}), 400

    update_fields = {
        'question': question,
        'answer': answer,
        'display_text': display_text,
        'updated_at': datetime.now()
    }
    if status and status in ['draft', 'published']:
        update_fields['status'] = status

    # 检查重复（排除自身）
    dup = FAQ._collection.find_one({'question': question, '_id': {'$ne': obj_id}})
    if dup:
        return jsonify({"code": 400, "msg": "该问题已存在"}), 400

    FAQ._collection.update_one({'_id': obj_id}, {'$set': update_fields})
    FAQMatcher.mark_dirty()

    return jsonify({"code": 200, "msg": "FAQ更新成功"})


@chat_bp.route('/faqs/<string:faq_id>', methods=['DELETE', 'OPTIONS'])
@token_required
def delete_faq(faq_id):
    """删除FAQ（管理员）"""
    if request.method == 'OPTIONS':
        return '', 200

    user_id = g.user_id
    user = User.query.get(user_id)
    if not user or not user.is_admin:
        return jsonify({"code": 403, "msg": "只有管理员可以删除FAQ"}), 403

    try:
        obj_id = ObjectId(faq_id)
    except Exception:
        return jsonify({"code": 400, "msg": "无效的FAQ ID"}), 400

    result = FAQ._collection.delete_one({'_id': obj_id})
    if result.deleted_count == 0:
        return jsonify({"code": 404, "msg": "FAQ不存在"}), 404

    FAQMatcher.mark_dirty()
    return jsonify({"code": 200, "msg": "FAQ已删除"})


@chat_bp.route('/faqs/<string:faq_id>/status', methods=['PUT', 'OPTIONS'])
@token_required
def toggle_faq_status(faq_id):
    """切换FAQ状态（管理员）"""
    if request.method == 'OPTIONS':
        return '', 200

    user_id = g.user_id
    user = User.query.get(user_id)
    if not user or not user.is_admin:
        return jsonify({"code": 403, "msg": "只有管理员可以修改FAQ状态"}), 403

    try:
        obj_id = ObjectId(faq_id)
    except Exception:
        return jsonify({"code": 400, "msg": "无效的FAQ ID"}), 400

    doc = FAQ._collection.find_one({'_id': obj_id})
    if not doc:
        return jsonify({"code": 404, "msg": "FAQ不存在"}), 404

    new_status = 'draft' if doc.get('status') == 'published' else 'published'
    FAQ._collection.update_one({'_id': obj_id}, {'$set': {'status': new_status, 'updated_at': datetime.now()}})
    FAQMatcher.mark_dirty()

    return jsonify({"code": 200, "data": {"status": new_status}, "msg": f"FAQ状态已切换为{new_status}"})


@chat_bp.route('/faqs/match', methods=['GET'])
def match_faq():
    """匹配用户输入到FAQ（公开接口，机器人调用）"""
    query = (request.args.get('q') or '').strip()
    if not query:
        return jsonify({"code": 400, "msg": "缺少查询参数q"}), 400

    matcher = FAQMatcher()
    answer, score = matcher.match(query)

    return jsonify({
        "code": 200,
        "data": {
            "matched": answer is not None,
            "answer": answer,
            "score": round(score, 4) if score else 0
        }
    })


def _get_site_name():
    """从MongoDB获取站点名称，默认返回'科创中心'"""
    try:
        from ..extensions import get_mongodb
        db = get_mongodb()
        if db is None:
            return '科创中心'
        doc = db.site_config.find_one({'key': 'site_name'})
        if doc and doc.get('value'):
            return doc['value']
    except Exception:
        pass
    return '科创中心'


@chat_bp.route('/faqs/site-name', methods=['GET'])
def get_site_name():
    """获取站点名称（公开接口）"""
    name = _get_site_name()
    return jsonify({"code": 200, "data": {"site_name": name}})


@chat_bp.route('/faqs/site-name', methods=['PUT'])
@token_required
def update_site_name():
    """更新站点名称（管理员）"""
    user_id = g.user_id
    user = User.query.get(user_id)
    if not user or not user.is_admin:
        return jsonify({"code": 403, "msg": "权限不足"}), 403

    data = request.get_json()
    name = (data.get('site_name') or '').strip()
    if not name:
        return jsonify({"code": 400, "msg": "站点名称不能为空"}), 400
    if len(name) > 50:
        return jsonify({"code": 400, "msg": "站点名称不能超过50个字符"}), 400

    try:
        from ..extensions import get_mongodb
        db = get_mongodb()
        db.site_config.update_one(
            {'key': 'site_name'},
            {'$set': {'key': 'site_name', 'value': name, 'updated_at': datetime.now()}},
            upsert=True
        )
        return jsonify({"code": 200, "msg": "站点名称已更新", "data": {"site_name": name}})
    except Exception as e:
        return jsonify({"code": 500, "msg": f"更新失败: {str(e)}"}), 500


@chat_bp.route('/faqs/greeting', methods=['GET'])
def get_greeting():
    """获取机器人欢迎语（公开接口，自动从已发布且设置了display_text的FAQ生成）"""
    site_name = _get_site_name()
    docs = list(FAQ._collection.find({
        'status': 'published',
        'display_text': {'$exists': True, '$ne': ''}
    }).sort('question', 1))

    if docs:
        items = []
        for d in docs:
            num = d.get('question', '').strip()
            label = d.get('display_text', '').strip()
            if num and label:
                items.append(f'{num}. {label}')
        if items:
            greeting = (
                f'您好！欢迎来到{site_name}。<br>请直接回复数字 / 关键词，我为您解答：<br>'
                + '<br>'.join(items)
            )
            return jsonify({"code": 200, "data": {"greeting": greeting}})

    # 兜底默认欢迎语
    default = (
        f'您好！欢迎来到{site_name}。<br>请直接回复数字 / 关键词，我为您解答：<br>'
        '1. 成果发布<br>2. 需求发布<br>3. 专家认证<br>'
        '4. 成果 & 需求对接<br>5. 账号与信息修改<br>6. 人工客服'
    )
    return jsonify({"code": 200, "data": {"greeting": default}})


# ==================== 聊天记录管理 API ====================

@chat_bp.route('/records/search', methods=['GET'])
@token_required
def search_chat_records():
    """跨会话全文搜索消息内容（管理员）"""
    user_id = g.user_id
    user = User.query.get(user_id)
    if not user or not user.is_admin:
        return jsonify({"code": 403, "msg": "权限不足"}), 403

    keyword = (request.args.get('keyword') or '').strip()
    if not keyword:
        return jsonify({"code": 400, "msg": "缺少搜索关键词"}), 400

    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)

    results = []

    # 1. 搜索人工客服会话消息
    session_query = {'messages.content': {'$regex': keyword, '$options': 'i'}}
    total_sessions = MongoCustomerServiceSession._collection.count_documents(session_query)
    session_cursor = MongoCustomerServiceSession._collection.find(session_query) \
        .sort('updated_at', -1) \
        .skip((page - 1) * page_size) \
        .limit(page_size)

    for doc in session_cursor:
        session = MongoCustomerServiceSession.from_dict(doc)
        session_user = User.query.get(session.user_id) if session.user_id else None
        session_agent = User.query.get(session.agent_id) if session.agent_id else None

        # 找匹配的消息
        matched_msgs = []
        for msg in (session.messages or []):
            if keyword.lower() in (msg.content or '').lower():
                matched_msgs.append({
                    'content': msg.content,
                    'sender_type': msg.sender_type,
                    'created_at': msg.created_at.isoformat() if msg.created_at else None
                })

        results.append({
            'source': 'human_session',
            'session_id': str(session._id),
            'user_name': session_user.username if session_user else f'用户{session.user_id}',
            'user_phone': session_user.phone if session_user else None,
            'agent_name': session_agent.username if session_agent else None,
            'status': session.status,
            'match_count': len(matched_msgs),
            'matched_messages': matched_msgs[:5],
            'created_at': session.created_at.isoformat() if session.created_at else None
        })

    # 2. 搜索机器人聊天消息
    bot_query = {'content': {'$regex': keyword, '$options': 'i'}, 'sender': 'user'}
    bot_cursor = MongoChatMessage._collection.find(bot_query) \
        .sort('created_at', -1) \
        .limit(page_size)
    for doc in bot_cursor:
        results.append({
            'source': 'bot_chat',
            'room_id': doc.get('room_id', ''),
            'sender': doc.get('sender', ''),
            'content': doc.get('content', ''),
            'created_at': doc['created_at'].isoformat() if doc.get('created_at') else None
        })

    return jsonify({
        "code": 200,
        "data": {
            "results": results,
            "total_sessions": total_sessions,
            "page": page,
            "page_size": page_size
        }
    })


@chat_bp.route('/records/export/<string:session_id>', methods=['GET'])
@token_required
def export_session_chat(session_id):
    """导出会话聊天记录为 JSON（管理员）"""
    user_id = g.user_id
    user = User.query.get(user_id)
    if not user or not (user.is_admin or user.is_agent):
        return jsonify({"code": 403, "msg": "权限不足"}), 403

    try:
        obj_id = ObjectId(session_id)
    except Exception:
        return jsonify({"code": 400, "msg": "无效的会话ID"}), 400

    session_dict = MongoCustomerServiceSession._collection.find_one({'_id': obj_id})
    if not session_dict:
        return jsonify({"code": 404, "msg": "会话不存在"}), 404
    session = MongoCustomerServiceSession.from_dict(session_dict)

    session_user = User.query.get(session.user_id) if session.user_id else None
    session_agent = User.query.get(session.agent_id) if session.agent_id else None

    messages = []
    for msg in (session.messages or []):
        messages.append({
            'sender_type': msg.sender_type,
            'sender_name': session_user.username if msg.sender_type == 'user' else (session_agent.username if session_agent else '客服'),
            'content': msg.content,
            'time': msg.created_at.isoformat() if msg.created_at else None
        })

    export_data = {
        'session_id': str(session._id),
        'user_name': session_user.username if session_user else '',
        'user_phone': session_user.phone if session_user else '',
        'agent_name': session_agent.username if session_agent else '',
        'status': session.status,
        'created_at': session.created_at.isoformat() if session.created_at else None,
        'closed_at': session.closed_at.isoformat() if hasattr(session, 'closed_at') and session.closed_at else None,
        'message_count': len(messages),
        'messages': messages,
        'exported_at': datetime.now().isoformat()
    }

    return jsonify({"code": 200, "data": export_data})


# 获取用户机器人聊天历史（管理员/客服）
@chat_bp.route('/bot-history/<int:user_id>', methods=['GET'])
@token_required
def get_user_bot_history(user_id):
    requester = User.query.get(g.user_id)
    if not requester or not (requester.is_admin or requester.is_agent):
        return jsonify({"code": 403, "msg": "权限不足"}), 403

    target_user = User.query.get(user_id)
    bot_room_id = (target_user.username or target_user.phone) if target_user else None
    if not bot_room_id:
        return jsonify({"code": 404, "msg": "未找到用户或无法确定聊天标识"}), 404

    messages_cursor = MongoChatMessage._collection.find(
        {'room_id': bot_room_id}
    ).sort('created_at', 1).limit(500)

    result = []
    for msg in messages_cursor:
        result.append({
            'sender': msg.get('sender', ''),
            'content': msg.get('content', ''),
            'created_at': msg['created_at'].isoformat() if msg.get('created_at') else None
        })
    return jsonify({"code": 200, "data": result, "room_id": bot_room_id})


# 获取通用聊天历史
@chat_bp.route('/history', methods=['GET'])
def get_chat_history():
    try:
        room_id = request.args.get('room_id')
        if not room_id:
            return jsonify({"code": 400, "msg": "缺少room_id参数"}), 400

        messages = MongoChatMessage._collection.find({'room_id': room_id}).sort('created_at', 1).limit(100)
        result = []
        for msg in messages:
            result.append({
                'from': msg['sender'],
                'text': msg['content'],
                'time': msg['created_at'].strftime('%H:%M'),
                'create_time': msg['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            })
        return jsonify({"code": 200, "data": result})
    except Exception as e:
        return jsonify({"code": 500, "msg": f"获取历史记录失败：{str(e)}"}), 500