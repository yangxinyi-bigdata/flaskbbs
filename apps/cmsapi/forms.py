# 注册表单
import wtforms
from wtforms import ValidationError, Form, StringField, IntegerField, FileField
from wtforms.validators import Email, Length, EqualTo, InputRequired
from flask_wtf.file import FileAllowed, FileSize
from exts import db, cache
from flask import request
from apps.front.forms import BaseForm


class UploadImageForm(BaseForm):
    image = FileField(validators=[FileAllowed(['jpg', 'png', 'jpeg'], message="只能上传图片"),
                                  FileSize(1024 * 1024 * 5, message="图片大小不能超过5M")])


class AddBannerForm(BaseForm):
    name = StringField(validators=[Length(min=1, max=20, message="请输入正确的轮播图名称")])
    image_url = StringField(validators=[Length(min=1, max=200, message="请输入正确的图片链接")])
    link_url = StringField(validators=[Length(min=1, max=200, message="请输入正确的跳转链接")])
    priority = IntegerField(validators=[wtforms.validators.InputRequired(message="请输入正确的优先级")])


class EditBannerForm(AddBannerForm):
    id = IntegerField(validators=[InputRequired(message="请输入轮播图id")])











