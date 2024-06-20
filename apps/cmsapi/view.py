from flask import Blueprint, current_app
from utils import restful
from flask_jwt_extended import jwt_required, get_jwt_identity
from apps.cmsapi.forms import UploadImageForm, AddBannerForm, EditBannerForm
from flask import request
import time, os
from hashlib import md5
from flask import (Blueprint, request, redirect, url_for, session, g,
                   render_template, jsonify, current_app, make_response as 制作响应)
from exts import db
from models.auth import UserModel, Permission
from models.post import BannerModel, PostModel, CommentModel, BoardModel
from exts import db
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from .decorators import permission_required


bp = Blueprint("cmsapi", __name__, url_prefix="/cmsapi")


@bp.before_request
@jwt_required()
def cmsapi_before_request():
    #  验证有没有jwt
    if request.method == "OPTIONS":
        return
    identity = get_jwt_identity()
    # identity 就是之前传的用户id
    user = UserModel.query.filter_by(id=identity).first()
    if user:
        setattr(g, "user", user)




@bp.get("/")
@jwt_required()
def mytest():
    # 获取到当时传进来的 identity, 也就是user.id
    identity = get_jwt_identity()
    return restful.ok(message="success", data={"identity": identity})


@bp.post("/banner/image/upload")
@permission_required(Permission.BANNER)
# @jwt_required()
def upload_banner_image():
    form = UploadImageForm(request.files)
    if form.validate():  # 如果验证通过了
        image = form.image.data  # 从表单中提取出图片
        # 最好不要使用用户上传上来的用户名
        filename = image.filename  # 提取图片文件
        ext = os.path.splitext(filename)[1]
        filename = md5((g.user.email + str(time.time())).encode("utf-8")).hexdigest() + ext

        image_path = os.path.join(current_app.config["BANNER_IMAGES_SAVE_PATH"], filename)  # 有了图片路径
        image.save(image_path)
        return restful.ok(data={"image_url": filename})
    else:
        message = form.messages[0]
        return restful.params_error(message=message)


# 思考: 为什么要添加这个接口? 前台传输图片之后, 图片传到后台,
@bp.post("/banner/add")
@permission_required(Permission.BANNER)
def add_banner():
    form = AddBannerForm(request.form)
    if form.validate():
        name = form.name.data
        image_url = form.image_url.data
        link_url = form.link_url.data
        priority = form.priority.data
        banner_model = BannerModel(name=name, image_url=image_url, link_url=link_url, priority=priority)
        db.session.add(banner_model)
        db.session.commit()
        # banner_model.to_dict()
        return restful.ok(data=banner_model.to_dict())
    else:
        return restful.params_error(message=form.messages[0])



@bp.get("/banner/list")
@permission_required(Permission.BANNER)
def banner_list():
    banners = BannerModel.query.order_by(BannerModel.create_time.desc()).all()
    banner_dicts = [banner.to_dict() for banner in banners]
    return restful.ok(data=banner_dicts)


@bp.post("/banner/delete")
@permission_required(Permission.BANNER)
def delete_banner():
    banner_id = request.form.get("id")
    if not banner_id:
        return restful.params_error(message="没有找到传入的id")
    try:
        banner = BannerModel.query.get(banner_id)
    except Exception as e:
        return restful.params_error(message="这个轮播图不存在")
    # 如果前边两个都没有返回, 那么删除这个轮播图
    db.session.delete(banner)
    db.session.commit()
    return restful.ok()


@bp.post("/banner/edit")
@permission_required(Permission.BANNER)
def edit_banner():
    # 这里使用一个表格保存数据, 因为这里要保存的数据有很多, 哪张图片, 图片连接, 图片跳转等等
    form = EditBannerForm(request.form)
    if form.validate():
        banner_id = form.id.data
        try:
            banner_model = BannerModel.query.get(banner_id)
        except Exception as e:
            return restful.params_error(message="轮播图不存在")
        # 如果代码走到了这个地方, 说明轮播图是存在的, 接下来我们要根据接收到的修改信息对轮播图的各个属性进行修改
        name = form.name.data
        image_url = form.image_url.data
        link_url = form.link_url.data
        priority = form.priority.data

        banner_model.name = name
        banner_model.image_url = image_url
        banner_model.link_url = link_url
        banner_model.priority = priority

        db.session.commit()
        return restful.ok(data=banner_model.to_dict())

    else:
        return restful.params_error(message=form.messages[0])


@bp.get("/post/list")
@permission_required(Permission.POST)
def post_list():
    page = request.args.get("page", default=1, type=int)
    per_page_count = current_app.config['PER_PAGE_COUNT']
    start = (page-1)*per_page_count
    end = start + per_page_count
    query_obj = PostModel.query.order_by(PostModel.create_time.desc())
    total_count = query_obj.count()
    posts = query_obj.slice(start, end)
    post_list = [post.to_dict() for post in posts]
    return restful.ok(data={'total_count': total_count, 'post_list': post_list, 'page': page})


@bp.post("/post/delete")
@permission_required(Permission.POST)
def delete_post():
    post_id = request.form.get("id")
    print(post_id)
    try:
        post_model = PostModel.query.get(post_id)
    except Exception as e:
        return restful.params_error(message="帖子不存在")
    db.session.delete(post_model)
    db.session.commit()
    return restful.ok()


@bp.post("/comment/delete")
@permission_required(Permission.COMMENT)
def delete_comment():
    # 思路: vue那边访问这个接口, 会传过来一个comment_id, 通过这个id, 从数据库中取出这个comment, 然后执行删除.
    comment_id = request.form.get("comment_id")
    print(comment_id)
    try:
        comment_model = CommentModel.query.get(comment_id)
    except Exception as e:
        return restful.params_error(message="评论不存在")

    db.session.delete(comment_model)
    db.session.commit()

    return restful.ok()


@bp.get("/comment/list")
@permission_required(Permission.COMMENT)
def comment_list():
    # 评论也得分页吗? 一页显示多少个呢? 也是10个吧
    page = request.args.get("page", default=1, type=int)
    per_page_count = current_app.config['PER_PAGE_COUNT']
    start = (page-1)*per_page_count
    end = start + per_page_count

    comment_obj = CommentModel.query.order_by(CommentModel.create_time.desc())

    total_count = comment_obj.count()


    comments = comment_obj.slice(start, end)
    comment_list = [comment.to_dict() for comment in comments]
    return restful.ok(data={'total_count': total_count, 'comment_list': comment_list, 'page': page})


# 用户管理, 激活用户, 关闭用户功能需要, 比如说员工离职了.
# @bp.get("/user/list")
# @permission_required(Permission.USER)
# def user_list():
#     users = UserModel.query.order_by(UserModel.join_time.desc()).all()
#     user_dict_list = [user.to_dict() for user in users]
#     return restful.ok(data=user_dict_list)


# 改造一下, 可以通过传入一个参数, 判断, 参数是怎么传来着.
@bp.get("/user/list")
@permission_required(Permission.USER)
def user_list():
    is_staff = request.args.get("is_staff", type=int)
    if is_staff:
        # 传递员工用户数据
        users = UserModel.query.filter_by(is_staff=1).all()
    else:
        users = UserModel.query.filter_by(is_staff=0).all()

    user_dict_list = [user.to_dict() for user in users]
    return restful.ok(data=user_dict_list)



@bp.post("/user/active")
@permission_required(Permission.USER)
def user_active():
    # is_active , id
    is_active = request.form.get("is_active", type=int)
    user_id = request.form.get("user_id")
    # 这里判断一下是不是本人, 如何判断呢? 应该是在哪里储存了
    if g.user.id != user_id:
        user = UserModel.query.get(user_id)
        user.is_active = bool(is_active)
        db.session.commit()
        print(user.to_dict())
        return restful.ok(data=user.to_dict())
    else:  # 本身, 禁止操作
        return restful.permission_error(message={"message": "不能操作本人"})


@bp.get("/board/post/count")
def board_post_count():
    # 要获取板块下的帖子数量
    board_post_count_list = db.session.query(BoardModel.name, func.count(BoardModel.name)).join(PostModel).group_by(BoardModel.name).all()
    # print(board_post_count_list)
    board_names = []
    post_counts = []
    [(board_names.append(board_name), post_counts.append(post_count)) for board_name, post_count in board_post_count_list]
    return restful.ok(data={"board_names": board_names, "post_counts": post_counts})


@bp.get("/day7/post/count")
def day7_post_count():
    # 统计日期, 统计帖子的数量.
    # 我们的帖子发布的时间, 我们存成Datetime, 除了日期还包含时间, 如果我们直接使用create_time分组肯定不行.
    # mysql数据库, 使用 date_format 函数
    # sqlite数据库: 用的是另一个
    # 首先获取当前时间, 然后在当前时间基础上往前再减7天
    now = datetime.now()
    # 减6天, 就是7天前
    # 一定一把时分秒都要减为零, 不然就只能获取当前时间之前的一天
    seven_day_age = now - timedelta(days=6, hours=now.hour, minutes=now.minute, seconds=now.second,
                      microseconds=now.microsecond)
    day7_post_count_list = db.session.query(func.date_format(PostModel.create_time, "%Y-%m-%d"), func.count(PostModel.id)).group_by(func.date_format(PostModel.create_time, "%Y-%m-%d")).filter(PostModel.create_time >= seven_day_age).all()
    day7_post_count_dict = dict(day7_post_count_list)
    for x in range(7):
        date = seven_day_age + timedelta(days=x)
        date_str = date.strftime("%Y-%m-%d")
        if not day7_post_count_dict.get(date_str):
            day7_post_count_dict[date_str] = 0

    dates = sorted(list(day7_post_count_dict.keys()))
    counts = []
    for date in dates:
        counts.append(day7_post_count_dict[date])
    return restful.ok(data={"dates": dates, "counts": counts})






















