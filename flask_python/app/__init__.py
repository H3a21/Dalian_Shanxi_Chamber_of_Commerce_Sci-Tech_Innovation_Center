from flask import Flask
from flask_socketio import SocketIO
from werkzeug.middleware.proxy_fix import ProxyFix
from .extensions import db, jwt, init_mongodb

# 导出扩展实例
__all__ = ['db', 'jwt', 'create_app']


def create_app():
    """应用工厂函数，用于测试或替代入口"""
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # 信任 Nginx 反向代理转发的 X-Forwarded-For/X-Forwarded-Proto/X-Forwarded-Host
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    # 初始化扩展
    db.init_app(app)
    jwt.init_app(app)
    init_mongodb(app)

    # 初始化Socket.IO（使用线程模式，避免eventlet问题）
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

    # 导入并初始化socket事件
    from .socket_events import init_socketio
    init_socketio(socketio)

    # 注册蓝图
    from .auth.routes import auth_bp
    from .chat.routes import chat_bp
    from .publish.routes import publish_bp
    from .editor.routes import editor_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    app.register_blueprint(publish_bp, url_prefix='/api/publish')
    app.register_blueprint(editor_bp, url_prefix='/api/editor')

    # 初始化数据库表
    with app.app_context():
        db.create_all()
        # 迁移：将 biz_id 从 INT 改为 VARCHAR(50)（兼容已有数据）
        try:
            db.session.execute('ALTER TABLE audit_logs MODIFY biz_id VARCHAR(50) NOT NULL')
        except Exception:
            pass  # 可能已经是 VARCHAR
        try:
            db.session.execute('ALTER TABLE messages MODIFY biz_id VARCHAR(50) NOT NULL DEFAULT ""')
        except Exception:
            pass
        db.session.commit()

    return app, socketio
