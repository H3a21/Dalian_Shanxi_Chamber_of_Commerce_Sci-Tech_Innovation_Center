from flask_sqlalchemy import SQLAlchemy
import redis
from pymongo import MongoClient
from flask_jwt_extended import JWTManager
from sqlalchemy import event

# 初始化数据库实例（先不绑定app，在run.py里绑定）
db = SQLAlchemy()

# 初始化JWT管理器
jwt = JWTManager()

# 初始化Redis客户端（先占位，在run.py里初始化）
redis_client = {
    'client': None
}

# 人机验证专用 Redis（db 1，与验证码隔离）
redis_captcha = {
    'client': None
}

# 初始化MongoDB客户端（先占位，在run.py里初始化）
mongo_client = {
    'client': None,
    'db': None
}


def init_redis(app):
    """
    初始化Redis客户端并测试连接
    使用 redis.Redis 替代 StrictRedis（兼容 redis-py 5.x+）
    """
    try:
        # 从配置中获取Redis参数，提供默认值
        redis_config = {
            'host': app.config.get('REDIS_HOST', 'localhost'),
            'port': app.config.get('REDIS_PORT', 6379),
            'db': app.config.get('REDIS_DB', 0),
            'password': app.config.get('REDIS_PASSWORD', None),
            'decode_responses': True,  # 自动解码字符串
            'socket_connect_timeout': 5  # 连接超时设置（秒）
        }

        # 使用 redis.Redis（redis-py 5.x 推荐，StrictRedis 已弃用）
        redis_client['client'] = redis.Redis(**redis_config)

        # 测试连接
        redis_client['client'].ping()
        print("[OK] Redis 连接成功")
        print(f"   地址: {redis_config['host']}:{redis_config['port']}")
        print(f"   数据库: {redis_config['db']}")

        # 单独初始化人机验证 Redis 连接（db 1）
        # 嵌套 try/except，不影响主 Redis
        try:
            captcha_config = dict(redis_config)
            captcha_config['db'] = 1
            redis_captcha['client'] = redis.Redis(**captcha_config)
            redis_captcha['client'].ping()
            print("[OK] Redis 人机验证数据库 (db 1) 连接成功")
        except Exception as e:
            print(f"[ERROR] Redis 人机验证数据库 (db 1) 连接失败: {e}")
            print("[WARN] 人机验证 IP 追踪功能不可用")
            redis_captcha['client'] = None

    except redis.ConnectionError:
        print("[ERROR] Redis 连接失败：无法连接到服务器")
        print("[WARN] 请检查：")
        print("   1. Redis 服务是否已启动")
        print("   2. REDIS_HOST 和 REDIS_PORT 配置是否正确")
        print("   3. 防火墙是否阻止了连接")
        redis_client['client'] = None  # 标记为未连接

    except redis.AuthenticationError:
        print("[ERROR] Redis 连接失败：密码错误")
        print("[WARN] 请检查 REDIS_PASSWORD 配置")
        redis_client['client'] = None

    except Exception as e:
        print(f"[ERROR] Redis 初始化异常：{str(e)}")
        redis_client['client'] = None

def get_redis():
    """
    获取Redis客户端的便捷函数
    使用前请检查是否为 None
    """
    if redis_client['client'] is None:
        raise RuntimeError("Redis 未初始化，请先调用 init_redis(app)")
    return redis_client['client']


def init_mongodb(app):
    """
    初始化MongoDB连接并测试连接
    """
    try:
        # 从配置中获取MongoDB参数，提供默认值
        uri = app.config.get('MONGODB_URI', 'mongodb://localhost:27017/')
        db_name = app.config.get('MONGODB_DB', 'website')


        mongo_client['client'] = MongoClient(
            uri,
            maxPoolSize=app.config.get('MONGODB_MAX_POOL_SIZE', 100),
            connectTimeoutMS=app.config.get('MONGODB_CONNECT_TIMEOUT_MS', 20000)
        )
        mongo_client['db'] = mongo_client['client'][db_name]


        # 测试连接
        mongo_client['client'].admin.command('ping')
        print("[OK] MongoDB 连接成功")

        # 初始化集合和索引
        from .mongo_models import init_all_collections
        print(f"[DEBUG] init_mongodb: 开始初始化集合...")
        try:
            init_all_collections(mongo_client['db'])
        except Exception as e:
            print(f"[ERROR] init_mongodb: 集合初始化失败: {e}")
            import traceback
            traceback.print_exc()
            raise

    except Exception as e:
        print(f"[ERROR] MongoDB 连接失败: {str(e)}")
        import traceback
        traceback.print_exc()
        mongo_client['client'] = None
        mongo_client['db'] = None
        print(f"[WARN] MongoDB 不可用，聊天/FAQ 功能将受限。应用继续启动。")


def get_mongodb():
    """
    获取MongoDB数据库实例的便捷函数
    使用前请检查是否为 None
    """
    if mongo_client['db'] is None:
        raise RuntimeError("MongoDB 未初始化，请先调用 init_mongodb(app)")
    return mongo_client['db']