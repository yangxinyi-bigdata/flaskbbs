from flask import Flask, session, g
import config
from exts import db, mail, cache, csrf, avatars, jwt, cors
from flask_migrate import Migrate
from apps.front import front_bp
from bbs_celery import make_celery
from apps.media import media_bp
from apps.cmsapi import cmsapi_bp
import commands

# 排除cmsapi的csrf验证
csrf.exempt(cmsapi_bp)


app = Flask(__name__)
app.config.from_object(config)

db.init_app(app)
mail.init_app(app)
cache.init_app(app)
csrf.init_app(app)
avatars.init_app(app)
jwt.init_app(app)
# 所有以api开始的路由, 都允许跨域, origins 是星号, 代表所有来源. 后面可以改成只允许固定域名
cors.init_app(app, resources={r"/cmsapi/*": {"origins": "*"}})


migrate = Migrate(app, db)

mycelery = make_celery(app)

# 注册蓝图
app.register_blueprint(front_bp)
app.register_blueprint(media_bp)
app.register_blueprint(cmsapi_bp)


# 注册命令
# app.cli.command("init_boards")(commands.init_boards)
# app.cli.command("create_test_posts")(commands.create_test_posts)
# app.cli.command("init_roles")(commands.init_roles)
# app.cli.command("bind_roles")(commands.bind_roles)
app.cli.command("init_developer")(commands.init_developer)


if __name__ == '__main__':
    app.run()
