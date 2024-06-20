from flask import Blueprint, send_from_directory, current_app
import os


bp = Blueprint('media', __name__, url_prefix='/media')


# /media/avatar/abc.jpg
# 部署的时候在nginx中配置一个/media前缀的url, 访问/media.的时候, 指定从media文件夹下寻找文件

@bp.route("/avatar/<path:filename>")
def get_avatar(filename):
    return send_from_directory(current_app.config["AVATARS_SAVE_PATH"], filename)


@bp.route("/post/<path:filename>")
def get_post_image(filename):
    return send_from_directory(current_app.config["POST_IMAGES_SAVE_PATH"], filename)


@bp.route("/banner/<path:filename>")
def get_banner_image(filename):
    return send_from_directory(current_app.config["BANNER_IMAGES_SAVE_PATH"], filename)