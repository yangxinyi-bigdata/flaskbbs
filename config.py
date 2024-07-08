import os
from datetime import timedelta

SECRET_KEY = "esxdflj:sdsffdsf"
BASE_DIR = os.path.dirname(__file__)  # 项目根路径

# session.permanent=True的情况下的过期时间
PERMANENT_SESSION_LIFETIME = timedelta(days=7)

# MySQL所在的主机名
HOSTNAME = "43.136.124.222"
# MySQL监听的端口号，默认3306
PORT = 3306
# 连接MySQL的用户名，读者用自己设置的
USERNAME = "pythonbbs"
# 连接MySQL的密码，读者用自己的
PASSWORD = "EZHJC6zSDYNGPCHX"
# MySQL上创建的数据库名称
DATABASE = "pythonbbs"

SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}?charset=utf8"
SQLALCHEMY_TRACK_MODIFICATIONS = False

# 邮箱配置
MAIL_SERVER = "smtp.qq.com"
MAIL_USE_SSL = True
MAIL_PORT = 465
MAIL_USERNAME = "yangyuehaha@qq.com"
MAIL_PASSWORD = "yunkrcylslptcada"
MAIL_DEFAULT_SENDER = "yangyuehaha@qq.com"

# Celery 的 redis 配置
CELERY_BROKER_URL = "redis://:yy3534365@139.9.182.20:6379/0"
CELERY_RESULT_BACKEND = "redis://:yy3534365@139.9.182.20:6379/0"

CACHE_TYPE = "RedisCache"
CACHE_DEFAULT_TIMEOUT = 300
CACHE_REDIS_HOST = "139.9.182.20"
CACHE_REDIS_PORT = 6379
CACHE_REDIS_PASSWORD = "yy3534365"

# 头像配置
AVATARS_SAVE_PATH = os.path.join(BASE_DIR, "media", "avatars")


# 帖子图片上传存放路径
POST_IMAGES_SAVE_PATH = os.path.join(BASE_DIR, "media", "post")
# 轮播图图片上传存放路径
BANNER_IMAGES_SAVE_PATH = os.path.join(BASE_DIR, "media", "banner")

# 每个展示帖子的数量
PER_PAGE_COUNT = 10

# 设置JWT过期时间
JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=10)
