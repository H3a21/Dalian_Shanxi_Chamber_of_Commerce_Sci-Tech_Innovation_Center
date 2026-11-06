from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import random
import uuid
from ..extensions import db, redis_client, redis_captcha
from flask_jwt_extended import create_access_token, jwt_required, get_jwt, get_jwt_identity
from ..socket_events import emit_new_message_event
from ..models import User, Message

auth_bp = Blueprint('auth', __name__)

# --- 工具函数 ---
def check_phone_registered(phone):
    return User.query.filter_by(phone=phone).first() is not None

def check_username_exists(username):
    if not username:
        return False
    return User.query.filter_by(username=username).first() is not None

def send_registration_notification(user_id):
    """注册成功后发送系统通知"""
    message = Message(
        send_user_id=0,          # 系统消息
        receive_user_id=user_id,
        msg_type='system',
        biz_type='',
        biz_id='',
        title='注册成功',
        content='恭喜您成功注册本网站，请赶紧前往「个人中心→基本信息」完成实名认证，否则无法使用网站全部功能，谢谢您的配合~',
        is_read=0
    )
    db.session.add(message)
    db.session.commit()

    # 实时推送
    emit_new_message_event(user_id, {
        'id': message.id,
        'send_user_id': 0,
        'receive_user_id': user_id,
        'msg_type': 'system',
        'title': '注册成功',
        'content': message.content,
        'is_read': 0,
        'create_time': message.create_time.strftime('%Y-%m-%d %H:%M:%S')
    })

# --- 接口逻辑 ---
# 1. 发送短信验证码接口
@auth_bp.route('/send_sms', methods=['POST'])
def send_sms():
    data = request.get_json()
    phone = data.get('phone')
    sms_type = data.get('type', 'register')

    if not phone or len(phone) != 11:
        return jsonify({'code': 400, 'message': '请输入正确的11位手机号'}), 400

    # 检查Redis是否可用
    r = redis_client['client']
    if r is None:
        return jsonify({'code': 500, 'message': '服务器配置错误：验证码服务不可用'}), 500

    # 60秒频率限制
    lock_key = f"sms_lock:{phone}"
    if r.exists(lock_key):
        return jsonify({'code': 429, 'message': '发送过于频繁，请60秒后再试'}), 429

    # 重置密码时，检查手机号是否注册
    if sms_type == 'reset' and not check_phone_registered(phone):
        return jsonify({'code': 400, 'message': '该手机号未注册'}), 400

    # 验证手机号时，检查手机号是否注册
    if sms_type == 'verify' and not check_phone_registered(phone):
        return jsonify({'code': 400, 'message': '该手机号未注册'}), 400

    # 生成6位验证码
    sms_code = str(random.randint(100000, 999999))
    redis_key = f"sms:{phone}:{sms_type}"

    from flask import current_app

    # 选择对应模板
    template_map = {
        'register': current_app.config['SMS_TEMPLATE_REGISTER'],
        'reset': current_app.config['SMS_TEMPLATE_RESET'],
        'verify': current_app.config['SMS_TEMPLATE_VERIFY'],
    }
    template_code = template_map.get(sms_type, current_app.config['SMS_TEMPLATE_REGISTER'])

    # 先尝试通过阿里云发送短信
    from .sms_service import send_sms as aliyun_send_sms
    result = aliyun_send_sms(
        phone_numbers=phone,
        code=sms_code,
        sign_name=current_app.config['SMS_SIGN_NAME'],
        template_code=template_code
    )

    # 无论阿里云发送成功与否，都将验证码存入 Redis（开发时可通过控制台获取）
    r.setex(redis_key, current_app.config['SMS_CODE_EXPIRE'], sms_code)
    r.setex(lock_key, current_app.config['SMS_LOCK_EXPIRE'], "locked")

    if not result['success']:
        # 阿里云发送失败，打印验证码到控制台作为开发回退，不影响注册流程
        print(f"\n【阿里云短信发送失败】手机号：{phone} | 验证码：{sms_code} | 类型：{sms_type}")
        print(f"【原因】{result['message']}")
        print(f"【开发回退】验证码已存入 Redis，可查看控制台输出\n")
    else:
        print(f"【阿里云短信已发送】手机号：{phone} | 验证码：{sms_code} | 类型：{sms_type}")

    return jsonify({'code': 200, 'message': '验证码已发送'})

# 2. 注册接口
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    phone = data.get('phone')
    password = data.get('password')
    sms_code = data.get('sms_code')

    # 基础校验
    if not phone or len(phone) != 11:
        return jsonify({'code': 400, 'message': '请输入正确的11位手机号'}), 400
    if not password or len(password) < 6:
        return jsonify({'code': 400, 'message': '密码长度不能少于6位'}), 400
    if not sms_code:
        return jsonify({'code': 400, 'message': '请输入验证码'}), 400

    # 验证码校验
    redis_key = f"sms:{phone}:register"
    stored_code = redis_client['client'].get(redis_key)
    if not stored_code or stored_code != sms_code:
        return jsonify({'code': 400, 'message': '验证码错误或已过期'}), 400

    # 检查手机号是否已注册
    if check_phone_registered(phone):
        return jsonify({'code': 400, 'message': '该手机号已注册'}), 400

    # 检查用户名是否重复
    if username and check_username_exists(username):
        return jsonify({'code': 400, 'message': '该用户名已被使用'}), 400

    # 密码加密
    hashed_password = generate_password_hash(password)

    # 创建用户
    new_user = User(
        username=username if username else None,
        phone=phone,
        password_hash=hashed_password,
        role='common',
        status=1
    )
    db.session.add(new_user)
    db.session.commit()

    # 自动生成用户名（如果没填）
    if not new_user.username:
        new_user.username = f"User{new_user.id}"
        db.session.commit()

    # 注册成功后删除验证码
    redis_client['client'].delete(redis_key)

    # 发送注册成功系统通知
    send_registration_notification(new_user.id)

    return jsonify({'code': 200, 'message': '注册成功'})

# 3. 登录接口
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    account = data.get('username')  # 支持手机号/用户名登录
    password = data.get('password')

    if not account or not password:
        return jsonify({'code': 400, 'message': '请输入账号和密码'}), 400

    # 查询用户（支持手机号/用户名登录）
    user = User.query.filter((User.phone == account) | (User.username == account)).first()

    # 校验账号密码
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'code': 401, 'message': '账号或密码错误'}), 401

    # 检查账号状态
    if user.status != 1:
        return jsonify({'code': 401, 'message': '账号已被禁用'}), 401

    # 登录成功，返回JWT token和用户信息
    access_token = create_access_token(identity=str(user.id), additional_claims={
        'username': user.username,
        'phone': user.phone,
        'role': user.role
    })

    return jsonify({
        'code': 200,
        'message': '登录成功',
        'data': {
            'user_id': user.id,
            'username': user.username,
            'phone': user.phone,
            'role': user.role,
            'token': access_token
        }
    })

# 4. 检查手机号是否已注册接口
@auth_bp.route('/check_phone', methods=['POST'])
def check_phone():
    data = request.get_json()
    phone = data.get('phone')
    if not phone:
        return jsonify({'code': 400, 'message': '请输入手机号'}), 400
    registered = check_phone_registered(phone)
    return jsonify({'code': 200, 'registered': registered})

# 5. 重置密码接口
@auth_bp.route('/reset_password', methods=['POST'])
def reset_password():
    data = request.get_json()
    phone = data.get('phone')
    new_password = data.get('new_password')
    sms_code = data.get('sms_code')

    # 基础校验
    if not phone or len(phone) != 11:
        return jsonify({'code': 400, 'message': '请输入正确的11位手机号'}), 400
    if not new_password or len(new_password) < 6:
        return jsonify({'code': 400, 'message': '密码长度不能少于6位'}), 400
    if not sms_code:
        return jsonify({'code': 400, 'message': '请输入验证码'}), 400

    # 检查手机号是否已注册（只有已注册用户才能重置密码）
    if not check_phone_registered(phone):
        return jsonify({'code': 400, 'message': '该手机号未注册'}), 400

    # 验证码校验
    redis_key = f"sms:{phone}:reset"
    stored_code = redis_client['client'].get(redis_key)
    if not stored_code or stored_code != sms_code:
        return jsonify({'code': 400, 'message': '验证码错误或已过期'}), 400

    # 查找用户
    user = User.query.filter_by(phone=phone).first()
    if not user:
        return jsonify({'code': 404, 'message': '用户不存在'}), 404

    # 更新密码
    hashed_password = generate_password_hash(new_password)
    user.password_hash = hashed_password
    db.session.commit()

    # 删除验证码
    redis_client['client'].delete(redis_key)

    return jsonify({'code': 200, 'message': '密码重置成功'})

# 6. 获取用户列表（仅管理员）
@auth_bp.route('/admin/users', methods=['GET'])
@jwt_required()
def get_users():
    # 从JWT token中获取当前用户角色
    claims = get_jwt()
    user_role = claims.get('role')

    if user_role != 'admin':
        return jsonify({'code': 403, 'message': '权限不足'}), 403

    # 查询所有用户
    users = User.query.all()
    users_data = []
    for user in users:
        users_data.append({
            'id': user.id,
            'username': user.username,
            'real_name': user.real_name,
            'id_card': user.id_card,
            'phone': user.phone,
            'role': user.role,
            'status': user.status,
            'last_active': user.last_active.isoformat() if user.last_active else None
        })

    return jsonify({'code': 200, 'data': users_data, 'total': len(users_data)})

# 7. 修改用户角色（仅管理员）
@auth_bp.route('/admin/users/<int:user_id>/role', methods=['PUT'])
@jwt_required()
def update_user_role(user_id):
    # 检查管理员权限
    claims = get_jwt()
    admin_role = claims.get('role')

    if admin_role != 'admin':
        return jsonify({'code': 403, 'message': '权限不足'}), 403

    data = request.get_json()
    new_role = data.get('role')
    if new_role not in ['common', 'agent', 'admin']:
        return jsonify({'code': 400, 'message': '角色无效'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'code': 404, 'message': '用户不存在'}), 404

    user.role = new_role
    db.session.commit()

    return jsonify({'code': 200, 'message': '角色更新成功'})

# 8. 管理员创建用户
@auth_bp.route('/admin/users', methods=['POST'])
@jwt_required()
def admin_create_user():
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'code': 403, 'message': '权限不足'}), 403

    data = request.get_json()
    username = data.get('username', '').strip()
    phone = data.get('phone', '').strip()
    password = data.get('password', '')
    role = data.get('role', 'common')
    real_name = data.get('real_name', '').strip()
    id_card = data.get('id_card', '').strip()

    # 校验
    if not phone or len(phone) != 11:
        return jsonify({'code': 400, 'message': '请输入正确的11位手机号'}), 400
    if not password or len(password) < 6:
        return jsonify({'code': 400, 'message': '密码长度不能少于6位'}), 400
    if role not in ['common', 'agent', 'admin']:
        return jsonify({'code': 400, 'message': '角色无效'}), 400
    if check_phone_registered(phone):
        return jsonify({'code': 400, 'message': '该手机号已注册'}), 400
    if username and check_username_exists(username):
        return jsonify({'code': 400, 'message': '该用户名已被使用'}), 400
    if id_card:
        existing = User.query.filter_by(id_card=id_card).first()
        if existing:
            return jsonify({'code': 400, 'message': '该身份证号已存在'}), 400

    new_user = User(
        username=username if username else None,
        phone=phone,
        password_hash=generate_password_hash(password),
        role=role,
        status=1,
        real_name=real_name if real_name else None,
        id_card=id_card if id_card else None
    )
    db.session.add(new_user)
    db.session.commit()

    if not new_user.username:
        new_user.username = f"User{new_user.id}"
        db.session.commit()

    return jsonify({
        'code': 200,
        'message': '用户创建成功',
        'data': {
            'id': new_user.id,
            'username': new_user.username,
            'real_name': new_user.real_name,
            'id_card': new_user.id_card,
            'phone': new_user.phone,
            'role': new_user.role,
            'status': new_user.status
        }
    })


# 9. 管理员更新用户信息
@auth_bp.route('/admin/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def admin_update_user(user_id):
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'code': 403, 'message': '权限不足'}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({'code': 404, 'message': '用户不存在'}), 404

    data = request.get_json()

    if 'username' in data:
        new_username = data['username'].strip() if data['username'] else ''
        if new_username and new_username != user.username:
            if check_username_exists(new_username):
                return jsonify({'code': 400, 'message': '该用户名已被使用'}), 400
        user.username = new_username if new_username else None

    if 'real_name' in data:
        val = data['real_name'].strip() if data['real_name'] else ''
        user.real_name = val if val else None

    if 'id_card' in data:
        val = data['id_card'].strip() if data['id_card'] else ''
        if val and val != user.id_card:
            existing = User.query.filter(User.id_card == val, User.id != user.id).first()
            if existing:
                return jsonify({'code': 400, 'message': '该身份证号已存在'}), 400
        user.id_card = val if val else None

    if 'phone' in data:
        new_phone = data['phone'].strip()
        if new_phone and new_phone != user.phone:
            if check_phone_registered(new_phone):
                return jsonify({'code': 400, 'message': '该手机号已注册'}), 400
        user.phone = new_phone

    if 'role' in data:
        new_role = data['role']
        if new_role not in ['common', 'agent', 'admin']:
            return jsonify({'code': 400, 'message': '角色无效'}), 400
        user.role = new_role

    if 'password' in data and data['password']:
        if len(data['password']) < 6:
            return jsonify({'code': 400, 'message': '密码长度不能少于6位'}), 400
        user.password_hash = generate_password_hash(data['password'])

    db.session.commit()

    return jsonify({'code': 200, 'message': '用户信息更新成功'})


# 10. 管理员删除用户
@auth_bp.route('/admin/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def admin_delete_user(user_id):
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'code': 403, 'message': '权限不足'}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({'code': 404, 'message': '用户不存在'}), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({'code': 200, 'message': '用户已删除'})


# 11. 管理员切换用户启用/禁用状态
@auth_bp.route('/admin/users/<int:user_id>/status', methods=['PUT'])
@jwt_required()
def admin_toggle_user_status(user_id):
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'code': 403, 'message': '权限不足'}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({'code': 404, 'message': '用户不存在'}), 404

    # 防止管理员禁用自己或其他管理员
    if user.role == 'admin':
        return jsonify({'code': 400, 'message': '无法禁用管理员账号'}), 400

    # 如果是从启用→禁用，强制踢下线（用户下次请求时 token_required 会返回 401）
    user.status = 0 if user.status == 1 else 1
    db.session.commit()

    status_text = '已启用' if user.status == 1 else '已禁用'
    return jsonify({
        'code': 200,
        'message': f'用户{status_text}',
        'data': {'status': user.status}
    })


# 12. 获取当前用户完整信息
@auth_bp.route('/me', methods=['GET', 'OPTIONS'])
def get_current_user():
    # OPTIONS请求直接返回，不需要JWT验证
    if request.method == 'OPTIONS':
        return jsonify({'code': 200}), 200

    # 只对非OPTIONS请求进行JWT验证
    from flask_jwt_extended import verify_jwt_in_request
    verify_jwt_in_request()

    # 从JWT token中获取用户ID（identity存为字符串，查询时转回整数）
    user_id = int(get_jwt_identity())

    # 查询用户
    user = User.query.get(user_id)
    if not user:
        return jsonify({'code': 404, 'message': '用户不存在'}), 404

    # 检查账号是否被禁用
    if user.status != 1:
        return jsonify({'code': 401, 'message': '账号已被禁用'}), 401

    # 返回完整的用户信息
    return jsonify({
        'code': 200,
        'data': {
            'id': user.id,
            'username': user.username,
            'phone': user.phone,
            'role': user.role,
            'status': user.status,
            'real_name': user.real_name,
            'id_card': user.id_card,
            'last_active': user.last_active.isoformat() if user.last_active else None
        }
    })

# 9. 更新用户信息
@auth_bp.route('/update_profile', methods=['PUT', 'OPTIONS'])
def update_profile():
    # OPTIONS请求直接返回，不需要JWT验证
    if request.method == 'OPTIONS':
        return jsonify({'code': 200}), 200

    # 只对非OPTIONS请求进行JWT验证
    from flask_jwt_extended import verify_jwt_in_request
    verify_jwt_in_request()

    # 从JWT token中获取用户ID（identity存为字符串，查询时转回整数）
    user_id = int(get_jwt_identity())

    # 查询用户
    user = User.query.get(user_id)
    if not user:
        return jsonify({'code': 404, 'message': '用户不存在'}), 404

    data = request.get_json()

    # 检查要更新的字段
    if 'username' in data:
        new_username = data.get('username')
        # 检查用户名是否已存在（排除当前用户）
        if new_username and new_username != user.username:
            existing = User.query.filter(User.username == new_username, User.id != user.id).first()
            if existing:
                return jsonify({'code': 400, 'message': '用户名已存在'}), 400
        user.username = new_username

    if 'real_name' in data and 'id_card' in data:
        new_real_name = data.get('real_name', '').strip()
        new_id_card = data.get('id_card', '').strip()

        if new_real_name and new_id_card:
            # 检查身份证号是否已被其他用户使用
            existing_card = User.query.filter(User.id_card == new_id_card, User.id != user.id).first()
            if existing_card:
                return jsonify({'code': 400, 'message': '身份证号已存在'}), 400

            # 调用阿里云三要素核验（姓名 + 身份证号 + 手机号）
            from .cloud_auth_service import verify_identity
            verify_result = verify_identity(
                real_name=new_real_name,
                id_card=new_id_card,
                mobile=user.phone
            )

            if not verify_result['success']:
                return jsonify({'code': 400, 'message': verify_result['message']}), 400

            user.real_name = new_real_name
            user.id_card = new_id_card
        else:
            # 如果传了空值，仅清空字段不做核验
            user.real_name = new_real_name if new_real_name else None
            user.id_card = new_id_card if new_id_card else None

    # 手机号修改需要验证码
    if 'phone' in data:
        new_phone = data.get('phone')
        sms_code = data.get('phone_verify_code')

        if not sms_code:
            return jsonify({'code': 400, 'message': '修改手机号需要验证码'}), 400

        # 验证验证码
        redis_key = f"sms:{user.phone}:verify"
        stored_code = redis_client['client'].get(redis_key)
        if not stored_code or stored_code != sms_code:
            return jsonify({'code': 400, 'message': '验证码错误或已过期'}), 400

        # 检查新手机号是否已存在
        if new_phone and new_phone != user.phone:
            existing = User.query.filter_by(phone=new_phone).first()
            if existing:
                return jsonify({'code': 400, 'message': '手机号已存在'}), 400

        user.phone = new_phone
        # 删除验证码
        redis_client['client'].delete(redis_key)

    db.session.commit()

    return jsonify({'code': 200, 'message': '用户信息更新成功'})

# 10. 修改密码（需要验证当前手机号）
@auth_bp.route('/change_password', methods=['POST', 'OPTIONS'])
def change_password():
    # OPTIONS请求直接返回，不需要JWT验证
    if request.method == 'OPTIONS':
        return jsonify({'code': 200}), 200

    # 只对非OPTIONS请求进行JWT验证
    from flask_jwt_extended import verify_jwt_in_request
    verify_jwt_in_request()

    # 从JWT token中获取用户ID（identity存为字符串，查询时转回整数）
    user_id = int(get_jwt_identity())

    # 查询用户
    user = User.query.get(user_id)
    if not user:
        return jsonify({'code': 404, 'message': '用户不存在'}), 404

    data = request.get_json()
    sms_code = data.get('sms_code')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')

    if not sms_code:
        return jsonify({'code': 400, 'message': '请输入验证码'}), 400
    if not new_password or len(new_password) < 6:
        return jsonify({'code': 400, 'message': '新密码长度不能少于6位'}), 400
    if new_password != confirm_password:
        return jsonify({'code': 400, 'message': '两次输入的密码不一致'}), 400

    # 验证验证码（使用当前手机号）
    redis_key = f"sms:{user.phone}:verify"
    stored_code = redis_client['client'].get(redis_key)
    if not stored_code or stored_code != sms_code:
        return jsonify({'code': 400, 'message': '验证码错误或已过期'}), 400

    # 更新密码
    user.password_hash = generate_password_hash(new_password)
    db.session.commit()

    # 删除验证码
    redis_client['client'].delete(redis_key)

    return jsonify({'code': 200, 'message': '密码修改成功'})


# ==========================================
# 系统消息 API
# ==========================================

from ..models import Message as MessageModel, MessageReadStatus
from datetime import datetime

@auth_bp.route('/messages', methods=['GET'])
@jwt_required()
def get_messages():
    """获取当前用户的消息列表（含全体普通用户广播消息）"""
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    user_role = claims.get('role', '')

    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    msg_type = request.args.get('msg_type', '', type=str)
    unread_only = request.args.get('unread_only', '', type=str)

    from sqlalchemy import or_, and_

    # 查询个人消息 + 广播消息（仅 common 用户能看到广播）
    if user_role == 'common':
        query = MessageModel.query.filter(
            (MessageModel.receive_user_id == user_id) |
            (MessageModel.receive_user_id == 0)
        )
    else:
        query = MessageModel.query.filter_by(receive_user_id=user_id)

    if msg_type:
        query = query.filter(MessageModel.msg_type == msg_type)

    if unread_only == '1':
        # 个人未读：receive_user_id=user_id AND is_read=0
        # 广播未读：receive_user_id=0 AND 用户未在 message_reads 中记录
        read_subquery = db.session.query(MessageReadStatus.message_id).filter(
            MessageReadStatus.user_id == user_id
        ).subquery()
        query = query.filter(
            or_(
                and_(MessageModel.receive_user_id == user_id, MessageModel.is_read == 0),
                and_(MessageModel.receive_user_id == 0, ~MessageModel.id.in_(read_subquery))
            )
        )

    total = query.count()
    messages = query.order_by(MessageModel.create_time.desc()).offset((page - 1) * page_size).limit(page_size).all()

    # 批量查询广播消息的已读状态
    broadcast_ids = [msg.id for msg in messages if msg.receive_user_id == 0]
    read_set = set()
    if broadcast_ids:
        records = MessageReadStatus.query.filter(
            MessageReadStatus.message_id.in_(broadcast_ids),
            MessageReadStatus.user_id == user_id
        ).all()
        read_set = {r.message_id for r in records}

    result = []
    for msg in messages:
        if msg.receive_user_id == 0:
            is_read = msg.id in read_set
        else:
            is_read = msg.is_read == 1
        result.append({
            "id": msg.id,
            "title": msg.title,
            "content": msg.content,
            "msg_type": msg.msg_type,
            "biz_type": msg.biz_type,
            "biz_id": msg.biz_id,
            "is_read": is_read,
            "create_time": msg.create_time.strftime('%Y-%m-%d %H:%M:%S') if msg.create_time else ''
        })

    return jsonify({
        "code": 200,
        "data": result,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if page_size > 0 else 0
    })


@auth_bp.route('/messages/unread-count', methods=['GET'])
@jwt_required()
def get_unread_count():
    """获取未读消息数量（含广播消息）"""
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    user_role = claims.get('role', '')

    # 个人未读数
    personal_unread = MessageModel.query.filter_by(receive_user_id=user_id, is_read=0).count()

    # 广播未读数（仅 common 用户计算）
    broadcast_unread = 0
    if user_role == 'common':
        read_subquery = db.session.query(MessageReadStatus.message_id).filter(
            MessageReadStatus.user_id == user_id
        ).subquery()
        broadcast_unread = MessageModel.query.filter(
            MessageModel.receive_user_id == 0,
            ~MessageModel.id.in_(read_subquery)
        ).count()

    return jsonify({"code": 200, "data": {"count": personal_unread + broadcast_unread}})


@auth_bp.route('/messages/<int:msg_id>/read', methods=['PUT'])
@jwt_required()
def mark_message_read(msg_id):
    """标记单条消息为已读（支持广播消息）"""
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    user_role = claims.get('role', '')

    msg = MessageModel.query.get(msg_id)
    if not msg:
        return jsonify({"code": 404, "msg": "消息不存在"}), 404

    if msg.receive_user_id == 0:
        # 广播消息：仅 common 用户可以操作
        if user_role != 'common':
            return jsonify({"code": 403, "msg": "无权操作"}), 403
        existing = MessageReadStatus.query.filter_by(message_id=msg_id, user_id=user_id).first()
        if not existing:
            db.session.add(MessageReadStatus(message_id=msg_id, user_id=user_id, read_time=datetime.now()))
            db.session.commit()
        return jsonify({"code": 200, "msg": "已标记为已读"})
    elif msg.receive_user_id != user_id:
        return jsonify({"code": 403, "msg": "无权操作"}), 403

    msg.is_read = 1
    msg.read_time = datetime.now()
    db.session.commit()
    return jsonify({"code": 200, "msg": "已标记为已读"})


@auth_bp.route('/messages/read-all', methods=['PUT'])
@jwt_required()
def mark_all_read():
    """标记所有消息为已读（含广播消息）"""
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    user_role = claims.get('role', '')
    now = datetime.now()

    # 标记个人消息全部已读
    MessageModel.query.filter_by(receive_user_id=user_id, is_read=0).update({
        'is_read': 1,
        'read_time': now
    })

    # 标记广播消息全部已读（仅 common 用户）
    if user_role == 'common':
        all_broadcast = MessageModel.query.filter_by(receive_user_id=0).all()
        already_read_ids = {r.message_id for r in MessageReadStatus.query.filter_by(user_id=user_id).all()}
        for msg in all_broadcast:
            if msg.id not in already_read_ids:
                db.session.add(MessageReadStatus(message_id=msg.id, user_id=user_id, read_time=now))

    db.session.commit()
    return jsonify({"code": 200, "msg": "全部已读"})


@auth_bp.route('/admin/messages/send', methods=['POST'])
@jwt_required()
def send_system_message():
    """管理员发送系统通知（所有普通用户共享一条记录，receive_user_id=0）"""
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'code': 403, 'message': '权限不足'}), 403

    data = request.get_json()
    title = (data.get('title') or '').strip()
    content = (data.get('content') or '').strip()

    if not title:
        return jsonify({"code": 400, "msg": "消息标题不能为空"}), 400
    if not content:
        return jsonify({"code": 400, "msg": "消息内容不能为空"}), 400

    # 创建一条广播记录，所有普通用户共享
    msg = MessageModel(
        send_user_id=0,
        receive_user_id=0,  # 0 = 全体普通用户广播
        msg_type='system',
        biz_type='broadcast',  # 系统广播，非具体业务
        biz_id='0',
        title=title,
        content=content,
        is_read=0,
        create_time=datetime.now()
    )
    db.session.add(msg)
    db.session.commit()

    # 实时推送通知给所有在线普通用户
    try:
        emit_new_message_event(0, {
            'id': msg.id,
            'title': msg.title,
            'content': msg.content,
            'msg_type': msg.msg_type,
            'create_time': msg.create_time.strftime('%Y-%m-%d %H:%M:%S') if msg.create_time else ''
        })
    except Exception as e:
        print(f"[WARN] 推送实时通知失败: {e}")

    return jsonify({
        "code": 200,
        "msg": "系统通知已发送给全部普通用户"
    })


# ==========================================
# 管理员消息管理 API（CRUD）
# ==========================================

@auth_bp.route('/admin/messages', methods=['GET'])
@jwt_required()
def admin_get_messages():
    """管理员获取所有消息列表（分页、搜索）"""
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'code': 403, 'message': '权限不足'}), 403

    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    keyword = request.args.get('keyword', '', type=str)
    msg_type = request.args.get('msg_type', '', type=str)

    query = MessageModel.query

    if msg_type:
        query = query.filter(MessageModel.msg_type == msg_type)

    if keyword:
        kw = f'%{keyword}%'
        query = query.filter(
            MessageModel.title.like(kw) |
            MessageModel.content.like(kw) |
            MessageModel.biz_id.like(kw)
        )

    query = query.order_by(MessageModel.create_time.desc())
    total = query.count()
    messages = query.offset((page - 1) * page_size).limit(page_size).all()

    # 批量查询接收用户信息
    user_ids = list(set(m.receive_user_id for m in messages if m.receive_user_id > 0))
    user_map = {}
    if user_ids:
        from ..models import User, Message
        users = User.query.filter(User.id.in_(user_ids)).all()
        user_map = {u.id: u.username for u in users}

    result = []
    for msg in messages:
        receive_info = '全体普通用户' if msg.receive_user_id == 0 else user_map.get(msg.receive_user_id, f'用户{msg.receive_user_id}')
        result.append({
            "id": msg.id,
            "send_user_id": msg.send_user_id,
            "receive_user_id": msg.receive_user_id,
            "receive_username": receive_info,
            "msg_type": msg.msg_type,
            "biz_type": msg.biz_type,
            "biz_id": msg.biz_id,
            "title": msg.title,
            "content": msg.content,
            "is_read": msg.is_read,
            "create_time": msg.create_time.strftime('%Y-%m-%d %H:%M:%S') if msg.create_time else '',
            "read_time": msg.read_time.strftime('%Y-%m-%d %H:%M:%S') if msg.read_time else ''
        })

    return jsonify({
        "code": 200,
        "data": result,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if page_size > 0 else 0
    })


@auth_bp.route('/admin/messages/<int:msg_id>', methods=['PUT'])
@jwt_required()
def admin_update_message(msg_id):
    """管理员编辑消息"""
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'code': 403, 'message': '权限不足'}), 403

    msg = MessageModel.query.get(msg_id)
    if not msg:
        return jsonify({"code": 404, "msg": "消息不存在"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"code": 400, "msg": "请求数据为空"}), 400

    if 'title' in data:
        msg.title = data['title'].strip()
    if 'content' in data:
        msg.content = data['content'].strip()
    if 'msg_type' in data:
        msg.msg_type = data['msg_type']

    db.session.commit()
    return jsonify({"code": 200, "msg": "消息已更新"})


@auth_bp.route('/admin/messages/<int:msg_id>', methods=['DELETE'])
@jwt_required()
def admin_delete_message(msg_id):
    """管理员删除消息"""
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'code': 403, 'message': '权限不足'}), 403

    msg = MessageModel.query.get(msg_id)
    if not msg:
        return jsonify({"code": 404, "msg": "消息不存在"}), 404

    # 如果是广播消息，同时清理已读记录
    if msg.receive_user_id == 0:
        MessageReadStatus.query.filter_by(message_id=msg_id).delete()

    db.session.delete(msg)
    db.session.commit()
    return jsonify({"code": 200, "msg": "消息已删除"})


# ========== 人机验证 IP 追踪（基于 Redis db 1）==========
#   captcha:pending:{ip} — 被风控的 IP，TTL 30 分钟自动过期
#   验证通过后立即删除该 key，不留遗留数据
_CAPTCHA_PENDING_TTL = 1800  # 30 分钟


def _get_ip():
    return request.remote_addr or request.headers.get('X-Forwarded-For', 'unknown')


def _redis():
    """安全获取 captcha Redis 客户端，不可用时返回 None"""
    try:
        return redis_captcha['client']
    except Exception:
        return None


@auth_bp.route('/captcha/trigger', methods=['POST'])
def captcha_trigger():
    """风控触发：IP 写入 Redis db 1，30 分钟自动过期"""
    r = _redis()
    if r is None:
        return jsonify({"code": 500, "msg": "Redis 不可用"}), 500
    try:
        r.setex(f'captcha:pending:{_get_ip()}', _CAPTCHA_PENDING_TTL, '1')
    except Exception as e:
        print(f"[captcha] trigger 写入失败: {e}")
        return jsonify({"code": 500, "msg": "写入失败"}), 500
    return jsonify({"code": 200, "msg": "ok"})


@auth_bp.route('/captcha/status', methods=['GET'])
def captcha_status():
    """检查当前 IP 是否需要人机验证"""
    r = _redis()
    if r is None:
        return jsonify({"code": 200, "data": {"need_captcha": False}})
    try:
        need_captcha = r.exists(f'captcha:pending:{_get_ip()}')
    except Exception as e:
        print(f"[captcha] status 查询失败: {e}")
        need_captcha = False
    return jsonify({"code": 200, "data": {"need_captcha": need_captcha}})


@auth_bp.route('/captcha/verify', methods=['POST'])
def captcha_verify():
    """验证通过：删除 pending key，不留遗留数据"""
    r = _redis()
    if r is None:
        return jsonify({"code": 500, "msg": "Redis 不可用"}), 500
    try:
        r.delete(f'captcha:pending:{_get_ip()}')
    except Exception as e:
        print(f"[captcha] verify 删除失败: {e}")
        return jsonify({"code": 500, "msg": "删除失败"}), 500
    return jsonify({"code": 200, "msg": "ok"})

