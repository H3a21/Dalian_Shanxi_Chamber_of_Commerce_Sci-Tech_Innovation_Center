import os


class Config:
    # --- 核心配置 ---
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-kczx-2026')

    # --- MySQL 数据库配置（用户数据）---
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'mysql+pymysql://root:123456@localhost:3306/smart_mine_db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- Redis 配置 ---
    REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
    REDIS_DB = int(os.environ.get('REDIS_DB', 0))
    REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', '123456')
    REDIS_DECODE_RESPONSES = True

    # --- MongoDB 配置（聊天数据）---
    MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/')
    MONGODB_DB = os.environ.get('MONGODB_DB', 'website')
    MONGODB_MAX_POOL_SIZE = int(os.environ.get('MONGODB_MAX_POOL_SIZE', 100))
    MONGODB_CONNECT_TIMEOUT_MS = int(os.environ.get('MONGODB_CONNECT_TIMEOUT_MS', 20000))

    # --- JWT配置 ---
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'dev-jwt-secret-kczx-2026')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 86400))
    JWT_COOKIE_CSRF_PROTECT = False
    JWT_CSRF_CHECK_FORM = False
    JWT_CSRF_IN_COOKIES = False

    # --- 短信验证码配置 ---
    SMS_CODE_EXPIRE = int(os.environ.get('SMS_CODE_EXPIRE', 300))
    SMS_LOCK_EXPIRE = int(os.environ.get('SMS_LOCK_EXPIRE', 60))

    # --- 阿里云短信配置 ---
    SMS_SIGN_NAME = os.environ.get('SMS_SIGN_NAME', '######')         #####
    SMS_TEMPLATE_REGISTER = os.environ.get('SMS_TEMPLATE_REGISTER', '########')        #####
    SMS_TEMPLATE_RESET = os.environ.get('SMS_TEMPLATE_RESET', '######')         #####
    SMS_TEMPLATE_VERIFY = os.environ.get('SMS_TEMPLATE_VERIFY', '#####')            #####

    # --- 阿里云 AccessKey 配置 ---
    ALIBABA_CLOUD_ACCESS_KEY_ID = os.environ.get('ALIBABA_CLOUD_ACCESS_KEY_ID', '#####')    #####
    ALIBABA_CLOUD_ACCESS_KEY_SECRET = os.environ.get('ALIBABA_CLOUD_ACCESS_KEY_SECRET', '#####')     #####

    # --- CORS 允许的域名（生产环境应设置为具体域名） ---
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')
