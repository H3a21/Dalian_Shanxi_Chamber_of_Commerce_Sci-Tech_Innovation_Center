# 在导入任何其他模块之前，尽早执行monkey patching以避免警告
# Windows 环境优先使用 gevent，更稳定
async_mode = 'threading'  # 默认回退方案



print(f"最终使用 {async_mode} 模式")

# 现在导入其他模块
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_jwt_extended import create_access_token
import os

# 1. 导入项目内部模块
from config import Config
from app.extensions import db, init_redis, jwt, init_mongodb, get_redis
from app.models import User, Message, MessageReadStatus, EditorUser, DynamicPage, SiteConfig
from app.auth.routes import auth_bp
from app.chat.routes import chat_bp
from app.publish.routes import publish_bp
from app.editor.routes import editor_bp
from app.socket_events import init_socketio
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix
import random
import uuid

# 2. 初始化Flask应用
app = Flask(__name__)

# 3. 加载配置文件
app.config.from_object(Config)

# 信任 Nginx 反向代理转发的 X-Forwarded-For/X-Forwarded-Proto/X-Forwarded-Host
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

# 4. 解决跨域（全接口支持，前端访问必备）
CORS(app, supports_credentials=True, origins="*")

# 5. 初始化 Socket.IO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode=async_mode)
# 初始化socket事件处理器
init_socketio(socketio, app)

# 6. 初始化数据库（绑定app）
db.init_app(app)

# 7. 初始化JWT
jwt.init_app(app)


# JWT错误处理
@jwt.invalid_token_loader
def invalid_token_callback(error_string):
    print(f"JWT无效token错误: {error_string}")
    return jsonify({"code": 422, "msg": "Token无效或已过期"}), 422


@jwt.unauthorized_loader
def unauthorized_callback(error_string):
    print(f"JWT未授权错误: {error_string}")
    return jsonify({"code": 401, "msg": "缺少访问令牌"}), 401


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    print(f"JWT token已过期: {jwt_payload}")
    return jsonify({"code": 422, "msg": "Token已过期"}), 422


# 8. 初始化Redis
init_redis(app)

# 9. 初始化MongoDB
init_mongodb(app)

# 9. 注册蓝图（登录注册接口、聊天接口、发布接口）
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(chat_bp, url_prefix='/api/chat')
app.register_blueprint(publish_bp, url_prefix='/api/publish')
app.register_blueprint(editor_bp, url_prefix='/api/editor')

# 10. 初始化数据库（MySQL和MongoDB）
try:
    with app.app_context():
        db.create_all()

        # 检查并添加缺失的列（MySQL users表）
        from sqlalchemy import inspect, text
        from app.models import User

        engine = db.engine
        inspector = inspect(engine)
        columns = inspector.get_columns('users')
        column_names = [col['name'] for col in columns]

        # 检查并添加缺失的列
        missing_columns = []
        if 'last_active' not in column_names:
            missing_columns.append(('last_active', 'DATETIME DEFAULT NULL'))
        if 'real_name' not in column_names:
            missing_columns.append(('real_name', 'VARCHAR(30) DEFAULT NULL'))
        if 'id_card' not in column_names:
            missing_columns.append(('id_card', 'VARCHAR(20) DEFAULT NULL'))
        if 'created_at' not in column_names:
            missing_columns.append(('created_at', 'DATETIME DEFAULT NULL'))

        if missing_columns:
            print(f"[INFO] 检测到users表缺少{len(missing_columns)}列，正在添加...")
            with engine.connect() as connection:
                for col_name, col_type in missing_columns:
                    print(f"[INFO] 添加列 {col_name} ...")
                    connection.execute(text(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}"))
                connection.commit()
            # 回填 created_at：用 last_active 或当前时间
            if 'created_at' in (c[0] for c in missing_columns):
                with engine.connect() as connection:
                    connection.execute(text("UPDATE users SET created_at = last_active WHERE created_at IS NULL AND last_active IS NOT NULL"))
                    connection.execute(text("UPDATE users SET created_at = NOW() WHERE created_at IS NULL"))
                    connection.commit()
                print("[INFO] 已回填 created_at 列")
            print("[OK] 已成功添加缺失列到users表")
        else:
            print("[OK] users表结构完整，所有列已存在")

        # 检查 messages 表结构
        try:
            msg_columns = [col['name'] for col in inspector.get_columns('messages')]
            msg_missing = []
            if 'title' not in msg_columns:
                msg_missing.append(('title', 'VARCHAR(100) DEFAULT \'\''))
            if 'read_time' not in msg_columns:
                msg_missing.append(('read_time', 'DATETIME DEFAULT NULL'))
            if msg_missing:
                print(f"[INFO] 检测到messages表缺少{len(msg_missing)}列，正在添加...")
                with engine.connect() as connection:
                    for col_name, col_type in msg_missing:
                        print(f"[INFO] 添加列 {col_name} ...")
                        connection.execute(text(f"ALTER TABLE messages ADD COLUMN {col_name} {col_type}"))
                    connection.commit()
                print("[OK] 已成功添加缺失列到messages表")
        except Exception:
            # messages表可能还不存在（db.create_all会在上面创建），忽略
            pass

        # 修复 messages.biz_id 类型：模型定义为 VARCHAR(50) 但旧表为 INT
        try:
            if inspector.has_table('messages'):
                biz_col = [c for c in inspector.get_columns('messages') if c['name'] == 'biz_id']
                if biz_col and 'INT' in str(biz_col[0].get('type', '')).upper():
                    print(f"[INFO] 修复 messages.biz_id 类型 INT -> VARCHAR(50) ...")
                    with engine.connect() as connection:
                        connection.execute(text("ALTER TABLE messages MODIFY COLUMN biz_id VARCHAR(50) NOT NULL DEFAULT ''"))
                        connection.commit()
                    print("[OK] messages.biz_id 类型已修复")
        except Exception as e:
            print(f"[WARN] 修复 biz_id 类型时出错: {e}")
            pass

        # 检查 message_reads 表是否存在
        try:
            if not inspector.has_table('message_reads'):
                print("[INFO] 创建 message_reads 表...")
                MessageReadStatus.__table__.create(engine)
                print("[OK] message_reads 表已创建")
        except Exception as e:
            print(f"[WARN] 创建 message_reads 表时出错: {e}")
            pass

        # ========== 自动创建默认管理员和客服账号 ==========
        from werkzeug.security import generate_password_hash


        def init_default_users():
            admin_username = "admin"
            admin_phone = "18888888888"
            admin_password = "admin123"
            agent_username = "agent_0000"
            agent_phone = "10000000000"
            agent_password = "agent123"

            admin = User.query.filter(
                (User.username == admin_username) | (User.phone == admin_phone)
            ).first()
            if not admin:
                admin = User(
                    username=admin_username,
                    phone=admin_phone,
                    password_hash=generate_password_hash(admin_password),
                    role='admin',
                    status=1,
                    real_name='系统管理员',
                    id_card='110101199001011234'
                )
                db.session.add(admin)
                print(f"[OK] 已创建默认管理员账号：{admin_username} / {admin_password}")

            agent = User.query.filter(
                (User.username == agent_username) | (User.phone == agent_phone)
            ).first()
            if not agent:
                agent = User(
                    username=agent_username,
                    phone=agent_phone,
                    password_hash=generate_password_hash(agent_password),
                    role='agent',
                    status=1
                )
                db.session.add(agent)
                print(f"[OK] 已创建默认客服账号：{agent_username} / {agent_password}")

            db.session.commit()


        init_default_users()
        # ========== 结束 ==========

        # ========== 自动创建默认编辑器账号 ==========
        try:
            editor = EditorUser.query.filter_by(account='editor').first()
            if not editor:
                editor = EditorUser(
                    account='editor',
                    password=generate_password_hash('123456'),
                    role='editor'
                )
                db.session.add(editor)
                db.session.commit()
                print(f"[OK] 已创建默认编辑器账号：editor / 123456")
        except Exception as e:
            db.session.rollback()
            print(f"[WARN] 创建编辑器账号失败（表可能不存在）: {e}")
        # ========== 结束 ==========

        print("[OK] 数据库初始化成功")
        print("[OK] MySQL数据库：用户表")
        print("[OK] MongoDB数据库：客服会话、客服消息、客服状态、通用聊天")
except Exception as e:
    print(f"[WARN] 数据库初始化警告: {e}")
    print("[WARN] 服务将继续启动，但数据库功能可能受限")


# ====================== 健康检查接口 ======================
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"code": 200, "msg": "服务启动成功", "data": "ok"}), 200


# ====================== Vue 静态文件分发（生产环境） ======================
from flask import send_from_directory

DIST_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'dist'))


@app.route('/')
def serve_vue_root():
    """分发 Vue 首页"""
    index_path = os.path.join(DIST_DIR, 'index.html')
    if os.path.exists(index_path):
        return send_from_directory(DIST_DIR, 'index.html')
    return jsonify({"code": 404, "msg": "请先执行 npm run build 构建前端"}), 404


@app.route('/<path:path>')
def serve_vue_spa(path):
    """分发 Vue 静态资源 & SPA fallback"""
    # 跳过 API 路由和 flask 原生静态路由
    if path.startswith('api/') or path.startswith('static/'):
        return jsonify({"code": 404, "msg": "Not found"}), 404

    file_path = os.path.join(DIST_DIR, path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return send_from_directory(DIST_DIR, path)

    # SPA fallback：所有非 API 路由返回 index.html
    index_path = os.path.join(DIST_DIR, 'index.html')
    if os.path.exists(index_path):
        return send_from_directory(DIST_DIR, 'index.html')
    return jsonify({"code": 404, "msg": "请先执行 npm run build"}), 404


# 11. 启动服务（注意：这里改成 socketio.run）
if __name__ == '__main__':
    # [IMPORTANT] 注意：必须用 socketio.run 替代 app.run
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, use_reloader=False, allow_unsafe_werkzeug=True)
