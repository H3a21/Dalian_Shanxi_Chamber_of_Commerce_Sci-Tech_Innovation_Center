"""
智慧矿山联合实验室 - Flask 后端
功能：用户注册、登录、忘记密码、阿里云短信验证码
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_socketio import SocketIO, emit, join_room, leave_room
from datetime import datetime
import random
import uuid
import redis

import pymysql

pymysql.install_as_MySQLdb()  # 加上这一行

# 【新增】导入配置文件
from config import Config

# ================= 1. 初始化 Flask 应用 =================
app = Flask(__name__)

# 【修改】从配置类加载配置
app.config.from_object(Config)

# 【关键修正】允许所有前端地址跨域（开发环境用，彻底解决跨域）
CORS(app, origins="*", supports_credentials=True)

# ================= 2. 数据库初始化 =================
db = SQLAlchemy(app)

# ================= 3. Redis 连接初始化 (从Config读取) =================
redis_client = redis.Redis(
    host=app.config['REDIS_HOST'],
    port=app.config['REDIS_PORT'],
    db=app.config['REDIS_DB'],
    decode_responses=app.config['REDIS_DECODE_RESPONSES'],
    password=app.config['REDIS_PASSWORD']
)

# ================= 4. SocketIO 初始化 =================
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')


# ================= 4. 工具函数 =================
def check_phone_registered(phone):
    """检查手机号是否已注册"""
    return User.query.filter_by(phone=phone).first() is not None


def check_username_exists(username):
    """检查用户名是否已被使用（自定义用户名时）"""
    if username is None:
        return False
    return User.query.filter_by(username=username).first() is not None


# ================= 5. 数据库用户表模型（username 允许为空，无唯一约束） =================
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=True, comment='用户名，可空，未设置时自动生成 User+id')
    phone = db.Column(db.String(20), unique=True, nullable=False, comment='手机号')
    password_hash = db.Column(db.String(255), nullable=False, comment='加密密码')
    role = db.Column(db.String(20), default='common', comment='角色：common/admin')
    status = db.Column(db.Integer, default=1, comment='状态：1正常，0禁用')


# ================= 5. 聊天消息表模型 =================
class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    room_id = db.Column(db.String(100), nullable=False, index=True)
    sender = db.Column(db.String(20), nullable=False)  # 'user', 'bot', 'admin', 'system'
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# 创建表（如果不存在）
with app.app_context():
    db.create_all()

    # ================= 初始化管理员用户 =================
    admin_phone = '#####'
    admin_username = '#####'
    admin_exists = User.query.filter(
        (User.phone == admin_phone) | (User.username == admin_username)
    ).first()

    if not admin_exists:
        hashed_pw = generate_password_hash('#####')
        admin_user = User(
            username=admin_username,
            phone=admin_phone,
            password_hash=hashed_pw,
            role='#####',
            status=1,
            real_name='系统管理员',
            id_card='#####'
        )
        db.session.add(admin_user)
        db.session.commit()
        print("✅ 管理员用户已创建（手机号：#####，用户名：#####，密码：#####）")
    else:
        print("ℹ️ 管理员用户已存在，无需重复创建")

    # ================= 初始化客服用户 =================


# ================= 6. API 接口逻辑 =================

# --- 接口 A: 发送短信验证码（阿里云短信） ---
@app.route('/api/send_sms', methods=['POST', 'OPTIONS'])
def send_sms():
    if request.method == 'OPTIONS':
        return jsonify({'code': 200}), 200

    data = request.get_json()
    phone = data.get('phone')
    sms_type = data.get('type', 'register')

    if not phone:
        return jsonify({'code': 400, 'message': '请输入手机号'}), 400

    # 60秒频率限制
    lock_key = f"sms_lock:{phone}"
    if redis_client.exists(lock_key):
        return jsonify({'code': 429, 'message': '发送过于频繁，请60秒后再试'}), 429

    # 重置密码场景校验
    if sms_type == 'reset' and not check_phone_registered(phone):
        return jsonify({'code': 400, 'message': '该手机号未注册，请先注册'}), 400

    # 生成6位验证码
    sms_code = str(random.randint(100000, 999999))

    redis_key = f"sms:{phone}:{sms_type}"

    # 选择对应模板并调用阿里云短信
    template_map = {
        'register': app.config['SMS_TEMPLATE_REGISTER'],
        'reset': app.config['SMS_TEMPLATE_RESET'],
        'verify': app.config['SMS_TEMPLATE_VERIFY'],
    }
    template_code = template_map.get(sms_type, app.config['SMS_TEMPLATE_REGISTER'])

    from app.auth.sms_service import send_sms as aliyun_send_sms
    with app.app_context():
        result = aliyun_send_sms(
            phone_numbers=phone,
            code=sms_code,
            sign_name=app.config['SMS_SIGN_NAME'],
            template_code=template_code
        )

    # 无论阿里云发送成功与否，都将验证码存入 Redis（开发时可通过控制台获取）
    redis_client.setex(redis_key, app.config['SMS_CODE_EXPIRE'], sms_code)
    redis_client.setex(lock_key, app.config['SMS_LOCK_EXPIRE'], "locked")

    if not result['success']:
        # 阿里云发送失败，打印验证码到控制台作为开发回退
        print(f"\n【阿里云短信发送失败】手机号：{phone} | 验证码：{sms_code} | 类型：{sms_type}")
        print(f"【原因】{result['message']}")
        print(f"【开发回退】验证码已存入 Redis，可查看控制台输出\n")
    else:
        print(f"【阿里云短信已发送】手机号：{phone} | 验证码：{sms_code} | 类型：{sms_type}")

    return jsonify({'code': 200, 'message': '验证码已发送'})


# --- 接口 B: 检查手机号是否已注册 ---
@app.route('/api/check_phone', methods=['POST', 'OPTIONS'])
def check_phone():
    if request.method == 'OPTIONS':
        return jsonify({'code': 200}), 200

    data = request.get_json()
    phone = data.get('phone')

    if not phone:
        return jsonify({'code': 400, 'message': '请输入手机号'}), 400

    registered = check_phone_registered(phone)
    return jsonify({'code': 200, 'registered': registered})


# --- 接口 C: 用户注册（username 可选，自动生成 User+id） ---
@app.route('/api/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        return jsonify({'code': 200}), 200

    data = request.get_json()
    username = data.get('username')  # 可选字段
    phone = data.get('phone')
    password = data.get('password')
    sms_code = data.get('sms_code')

    if not phone or not password or not sms_code:
        return jsonify({'code': 400, 'message': '请填写完整信息（手机号、密码、验证码）'}), 400

    # 校验验证码
    redis_key = f"sms:{phone}:register"
    stored_code = redis_client.get(redis_key)
    if not stored_code or stored_code != sms_code:
        return jsonify({'code': 400, 'message': '短信验证码错误或已过期'}), 400

    if check_phone_registered(phone):
        return jsonify({'code': 400, 'message': '该手机号已注册，请直接登录'}), 400

    # 如果前端提供了自定义用户名，需检查是否已被占用
    if username is not None and username.strip() != '':
        if check_username_exists(username):
            return jsonify({'code': 400, 'message': '用户名已被占用，请更换'}), 400
        final_username = username.strip()
    else:
        final_username = None  # 暂不设置，等commit后生成

    # 保存用户（先不填username）
    hashed_password = generate_password_hash(password)
    new_user = User(
        username=final_username,
        phone=phone,
        password_hash=hashed_password,
        role='common',
        status=1
    )
    db.session.add(new_user)
    db.session.commit()  # 此时新用户的 id 已生成

    # 如果 username 为空，则自动生成 "User{id}"
    if final_username is None:
        auto_username = f"User{new_user.id}"
        new_user.username = auto_username
        db.session.commit()
        print(f"✅ 为用户 {phone} 自动生成用户名：{auto_username}")

    redis_client.delete(redis_key)
    return jsonify({'code': 200, 'message': '注册成功！请前往登录'})


# --- 接口 C: 用户登录（支持手机号或用户名，用户名可为空但不会影响查询） ---
@app.route('/api/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return jsonify({'code': 200}), 200

    data = request.get_json()
    account = data.get('username')  # 前端字段名仍为 username，实际可以是手机号或用户名
    password = data.get('password')

    if not account or not password:
        return jsonify({'code': 400, 'message': '请填写账号密码'}), 400

    # 支持手机号或用户名登录（用户名可能为 None，但 account 非空，不会匹配到 username 为 NULL 的记录）
    user = User.query.filter(
        (User.phone == account) | (User.username == account)
    ).first()

    if user:
        if user.status != 1:
            return jsonify({'code': 401, 'message': '账号已被禁用，请联系管理员'}), 401
        # 状态为1，检查密码
        if check_password_hash(user.password_hash, password):
            return jsonify({
                'code': 200,
                'message': '登录成功！',
                'data': {
                    'id': user.id,
                    'username': user.username,  # 可能为 None 或自动生成的字符串
                    'phone': user.phone,
                    'role': user.role,
                    'status': user.status,
                    'token': f"user_token_{user.id}_{uuid.uuid4()}"
                }
            })
        else:
            return jsonify({'code': 401, 'message': '密码错误'}), 401
    else:
        return jsonify({'code': 401, 'message': '账号或密码错误'}), 401


# --- 接口 D: 重置密码 ---
@app.route('/api/reset_password', methods=['POST', 'OPTIONS'])
def reset_password():
    if request.method == 'OPTIONS':
        return jsonify({'code': 200}), 200

    data = request.get_json()
    phone = data.get('phone')
    new_password = data.get('new_password')
    sms_code = data.get('sms_code')

    if not phone or not new_password or not sms_code:
        return jsonify({'code': 400, 'message': '请填写完整信息'}), 400

    redis_key = f"sms:{phone}:reset"
    stored_code = redis_client.get(redis_key)
    if not stored_code or stored_code != sms_code:
        return jsonify({'code': 400, 'message': '短信验证码错误或已过期'}), 400

    user = User.query.filter_by(phone=phone).first()
    if not user:
        return jsonify({'code': 400, 'message': '该手机号未注册'}), 400

    user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    redis_client.delete(redis_key)

    return jsonify({'code': 200, 'message': '密码重置成功！请使用新密码登录'})


# if __name__ == '__main__':
#     # 检查Redis连接
#     try:
#         redis_client.ping()
#         print("✅ Redis 连接成功！")
#     except Exception as e:
#         print(f"❌ Redis 连接失败：{e}")
#         exit(1)
#
#     app.run(debug=True, host='0.0.0.0', port=)
