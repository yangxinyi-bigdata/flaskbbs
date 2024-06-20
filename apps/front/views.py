from flask import (Blueprint, request, redirect, url_for, session, g,
                   render_template, jsonify, current_app, make_response as 制作响应)
import string, random
from flask_mail import Message
from exts import mail, cache
from utils import restful
from utils.captcha import Captcha
import time, os
from hashlib import md5
from io import BytesIO
from .forms import RegisterForm, LoginForm, EditProfileForm, UploadAvatarForm, UploadImageForm, PublicPostForm, PublicComment
from models.auth import UserModel, Permission
from werkzeug.security import generate_password_hash, check_password_hash
from exts import db
from .decorators import login_required
from hashlib import md5
from flask_avatars import Identicon
from models.post import PostModel, BannerModel, BoardModel, CommentModel
from flask_paginate import Pagination, get_page_parameter
from sqlalchemy.sql import func
from flask_jwt_extended import create_access_token


bp = Blueprint("front", __name__, url_prefix="/")


@bp.before_request
def my_before_request():
    user_id = session.get("user_id")
    # 有可能取到的是空的, 我们
    if user_id:
        user = UserModel.query.get(user_id)
        # 拿到这个用户对象之后, 我们后面肯定要用, 所以需要保存起来, 让视图函数能够拿到这个数据
        # 保存在哪里呢? 这里就是保存在一个全局对象当中. g : 就是global缩写
        setattr(g, "user", user)
    else:
        #  我们也设置一个变量
        setattr(g, "user", None)


# 上下文处理器
@bp.context_processor
def front_context_processor():
    if hasattr(g, "user"):
        return {"user": g.user}
    else:
        return {}


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'GET':
        return render_template("front/login.html")
    else:
        form = LoginForm(request.form)
        if form.validate():
            email = form.email.data
            password = form.password.data
            remember = form.remember.data
            user = UserModel.query.filter_by(email=email).first()
            print(password)
            if not user:
                return restful.params_error("邮箱错误！")
            if not user.check_password(password):
                print(user.check_password(password))
                return restful.params_error("邮箱或密码错误！")
            # if not user.is_active:
            #     return restful.params_error("此用户不可用！")
            session['user_id'] = user.id
            permissions = []
            token = ""
            # 如果是员工, 才生成Token
            print(user.is_staff)
            if user.is_staff:
                token = create_access_token(identity=user.id)
                for attr in dir(Permission):
                    if not attr.startswith("_"):
                        permission = getattr(Permission, attr)
                        if user.has_permission(permission):
                            permissions.append(attr.lower())
            if remember == 1:
                # 默认session过期时间，就是只要浏览器关闭了就会过期
                session.permanent = True
            user_dict = user.to_dict()
            user_dict["permissions"] = permissions
            return restful.ok(data={"token": token, "user": user_dict})
        else:
            return restful.params_error(message="")


@bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@bp.route("setting")
@login_required
def setting():
    email_hash = md5(g.user.email.encode("utf-8")).hexdigest()
    return render_template("front/setting.html", email_hash=email_hash)


@bp.get("/cms")
def cms():
    return render_template("cms/index.html")


@bp.post("/avatar/upload")
@login_required
def upload_avatar():
    #     上传头像, 第一个验证, 你必须上传的是图片
    # 第二个你不能上传太大的
    form = UploadAvatarForm(request.files)
    if form.validate():  # 如果验证通过了
        image = form.image.data  # 从表单中提取出图片
        # 最好不要使用用户上传上来的用户名
        filename = image.filename  # 提取图片文件
        ext = os.path.splitext(filename)[1]
        filename = md5((g.user.email + str(time.time())).encode("utf-8")).hexdigest() + ext

        image_path = os.path.join(current_app.config["AVATARS_SAVE_PATH"], filename)  # 有了图片路径
        image.save(image_path)
        # 看个人需求, 是否图片上传完成后要立马修改用户的头像字段
        g.user.avatar = filename
        db.session.commit()
        return restful.ok(data={"avatar": filename})
    else:
        message = form.messages[0]
        return restful.params_error(message=message)


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == 'GET':
        return render_template("front/register.html")
    else:
        form = RegisterForm(request.form)
        if form.validate():
            # 如果走到这个地方说明验证成功了
            email = form.email.data
            username = form.username.data
            password = form.password.data
            identicon = Identicon()
            email_hash = md5(email.encode("utf-8")).hexdigest()
            filenames = identicon.generate(text=email_hash)
            avatar = filenames[2]
            # 密码不能明文保存
            user = UserModel(email=email, username=username, password=password, avatar=avatar)
            db.session.add(user)
            db.session.commit()
            return restful.ok(message="注册成功!")
            # return redirect(url_for("auth.login"))
        else:

            # 如果这个地方验证失败了, 肯定还是回到注册页面
            message = form.messages[0]
            return restful.params_error(message=message)
            # return redirect(url_for("auth.register"))



@bp.route('/')
def index():  # put application's code here
    st = request.args.get("st", default=1, type=int)
    board_id = request.args.get("board_id", type=int, default=None)
    print(board_id)
    boards = BoardModel.query.order_by(BoardModel.priority.desc()).all()
    # posts = PostModel.query.order_by(PostModel.create_time.desc()).all()
    # 改成分页的形式, 现在就不是直接获取帖子列表了, 而是获取帖子的分页对象

    # 这里根据板块参数进行修改, 首先过滤出当前板块的文章, 然后再进行后续操作.

    if st == 1:
        post_query = PostModel.query.order_by(PostModel.create_time.desc())
    elif st == 2:
        post_query = db.session.query(PostModel).outerjoin(CommentModel).group_by(PostModel.id).order_by(
            func.count(CommentModel.id).desc(), PostModel.create_time.desc())

    page = request.args.get(get_page_parameter(), type=int, default=1)
    # 计算一下应该取多少个数字
    start = (page - 1)*current_app.config["PER_PAGE_COUNT"]
    end = start + current_app.config["PER_PAGE_COUNT"]

    if board_id:
        post_query.filter(PostModel.board_id == board_id)
        # post_query = post_query.filter_by(board_id=board_id)
        # post_query = post_query.filter(PostModel.board_id=board_id)

    posts = post_query.slice(start, end)

    # 生成一个分页对象
    pagination = Pagination(bs_version=3, page=page, total=post_query.count())
    banners = BannerModel.query.order_by(BannerModel.priority.desc()).all()

    return render_template("front/index.html", boards=boards, posts=posts, pagination=pagination, st=st, board_id=board_id, banners=banners)


# @bp.get('/email/captcha')
# def email_captcha():
#     email = request.args.get('email')
#     if not email:
#         return jsonify({"code": 400, "message": "请先传入邮箱!"})
#     # 随机生成一个4位的数字
#     source = list(string.digits)
#     captcha = ''.join(random.sample(source, 6))
#     message = Message(subject='邮箱验证码', recipients=[email], body='您的验证码是：' + captcha)
#     try:
#         mail.send(message)
#     except Exception as e:
#         print("邮件发送失败!")
#         print(e)
#         return jsonify({"code": 500, "message": "邮件发送失败!"})
#
#
#     # 用数据库表的方式存储邮箱验证码
#     # email_captcha = EmailCaptchaModel(email=email, captcha=captcha)
#     # db.session.add(email_captcha)
#     # db.session.commit()
#     # RESTFul API
#     # {code: 200/400/500, message: "其他错误原因", data: {}}
#     return jsonify({'code': 200, 'message': '发送验证码成功!', 'data': {}})


@bp.get('/email/captcha')
def email_captcha():
    email = request.args.get('email')
    if not email:
        return restful.params_error(message="请先传入邮箱!")

    # 随机生成一个4位的数字
    source = list(string.digits)
    captcha = ''.join(random.sample(source, 2))
    subject = "[杨心一Notion]注册验证码"
    body = '您的验证码是：' + captcha
    current_app.celery.send_task("send_mail", (email, subject, body))
    cache.set(email, captcha)
    print(cache.get(email))



    # 用数据库表的方式存储邮箱验证码
    # email_captcha = EmailCaptchaModel(email=email, captcha=captcha)
    # db.session.add(email_captcha)
    # db.session.commit()
    # RESTFul API
    # {code: 200/400/500, message: "其他错误原因", data: {}}
    return restful.ok(message="发送验证码成功!")


@bp.route("/graph/captcha")
def graph_captcha():
    验证码, 图片 = Captcha.gene_graph_captcha()
    print(验证码)
#   key , value  将图形验证码设置到缓存当中
#     经过md5加密之后的一个hash值
    键 = md5((验证码+str(time.time())).encode("utf-8")).hexdigest()
    cache.set(键, 验证码)
    #     需要先将图片转换成二进制
    #     with open("captcha.png", "wb") as f:
    #         image.save(f, "png")
    out = BytesIO()
    图片.save(out, "png")
    out.seek(0)
    # 创建一个响应
    响应 = 制作响应(out.read())
    响应.content_type = "image/png"
    # 我们将图片返回给客户端之后, 当用户输入了这个验证码, 我们还需要匹配是否一致
    # 取这个验证码需要使用key, 到redis里面去取, 但这里返回的是一个图片, 我们无法把key放到图片里面进行返回
    # 所以这里使用cookie, 将key保存到用户那边去
    响应.set_cookie("_graph_captcha_key", 键, max_age=3600)

    return 响应


@bp.post("/profile/edit")
@login_required
def edit_profile():
    form = EditProfileForm(request.form)
    if form.validate():
        signature = form.signature.data  # 从表单中提取出签名
        g.user.signature = signature  # 将该数据给当前用户的字段
        db.session.commit()  # 修改数据库
        return restful.ok()
    else:
        return restful.params_error(message=form.messages[0])


@bp.route("/post/public", methods=['GET', 'POST'])
def public_post():
    if request.method == 'GET':
        boards = BoardModel.query.all()
        return render_template("front/public_post.html", boards=boards)
    else:
        form = PublicPostForm(request.form)
        if form.validate():
            title = form.title.data
            content = form.content.data
            board_id = form.board_id.data
            try:
                board = BoardModel.query.get(board_id)
            except Exception as e:
                return restful.params_error(message="没有这个板块")
            post_model = PostModel(title=title, content=content, board_id=board_id, author=g.user)
            db.session.add(post_model)
            db.session.commit()
            return restful.ok(data={"id": post_model.id})
        else:
            return restful.params_error(message=form.messages[0])


@bp.post("/post/image/upload")
@login_required
def upload_post_image():
    #     上传头像, 第一个验证, 你必须上传的是图片
    # 第二个你不能上传太大的
    form = UploadImageForm(request.files)
    if form.validate():  # 如果验证通过了

        image = form.image.data  # 从表单中提取出图片
        # 最好不要使用用户上传上来的用户名
        filename = image.filename  # 提取图片文件
        ext = os.path.splitext(filename)[1]
        filename = md5((g.user.email + str(time.time())).encode("utf-8")).hexdigest() + ext

        image_path = os.path.join(current_app.config["POST_IMAGES_SAVE_PATH"], filename)  # 有了图片路径
        image.save(image_path)

        return jsonify(
            {
                "errno": 0,
                "data": [{
                    "url": url_for("media.get_post_image", filename=filename),
                    "alt": filename,
                    "href": ""
                }]
            })
    else:
        message = form.messages[0]
        return restful.params_error(message=message)


@bp.get("post/detail/<int:post_id>")
def post_detail(post_id):
    post_model = PostModel.query.get(post_id)
    if post_model:
        comment_count = CommentModel.query.filter_by(post_id=post_id).count()
        context = {
            "post": post_model,
            "comment_count": comment_count
        }
        return render_template("front/post_detail.html", **context)
    else:
        return restful.params_error("没有这篇帖子！")


@bp.post("/comment")
@login_required
def public_comment():
    form = PublicComment(request.form)
    if form.validate():
        content = form.content.data
        post_id = form.post_id.data
        try:
            post_model = PostModel.query.get(post_id)
        except Exception as e:
            return restful.params_error("没有这篇帖子！")

        comment = CommentModel(content=content, post_id=post_id, author=g.user)
        db.session.add(comment)
        db.session.commit()
        return restful.ok()
    else:
        return restful.params_error(message=form.messages[0])











