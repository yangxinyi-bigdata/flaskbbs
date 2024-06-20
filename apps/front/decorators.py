from functools import wraps
from flask import g, redirect, url_for


# 登录验证装饰器
def login_required(func):
    # 报错func的信息
    @wraps(func)
    # func(a, b, c)
    def inner(*args, **kwargs):
        if g.user:
            return func(*args, **kwargs)
        else:
            return redirect(url_for("front.login"))

    return inner