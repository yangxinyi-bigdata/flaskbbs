# 注册表单
import wtforms
from wtforms import ValidationError, Form, StringField, IntegerField, FileField
from wtforms.validators import Email, Length, EqualTo
from flask_wtf.file import FileAllowed, FileSize
from models.auth import UserModel
from exts import db, cache
from flask import request


class BaseForm(Form):
    @property
    def messages(self):
        message_list = []
        if self.errors:
            for errors in self.errors.values():
                message_list.extend(errors)
        return message_list


# Form 主要就是用来验证前端提交的数据是否满足要求
class RegisterForm(BaseForm):
    email = wtforms.StringField(validators=[Email(message="邮箱格式错误!")])
    email_captcha = wtforms.StringField(validators=[Length(min=2, max=2, message="验证码格式错误!")])
    username = wtforms.StringField(validators=[Length(min=3, max=20, message="用户名格式错误!")])
    password = wtforms.StringField(validators=[Length(min=6, max=20, message="密码格式错误!")])
    repeat_password = wtforms.StringField(validators=[EqualTo("password", message="两次密码不一致！")])
    graph_captcha = wtforms.StringField(validators=[Length(min=4, max=4, message="图形验证码错误!")])

    # 自定义验证: 1. 邮箱是否已经被注册, 验证码是否正确.
    # 还需要进行如果邮箱已经被注册过了, 那就不能再让他注册了
    # 验证码错误了, 需要让他重新验证
    def validate_email(self, field):
        # 如果你验证的是邮箱, 这个field就代表邮箱的字段
        # 从这个模型里面搜索一下, 如果已经存在了, 就说明之前已经注册过了
        email = field.data
        user = UserModel.query.filter_by(email=email).first()
        if user:
            raise ValidationError(message="该邮箱已经被注册过")
            # 如果有这个用户存在, 就应该抛出一个错误

    # 验证码是否正确
    def validate_email_captcha(self, field):
        email_captcha = field.data
        email = self.email.data
        cache_captcha = cache.get(email)
        if not cache_captcha or email_captcha != cache_captcha :
            # 没找到说明有错误
            raise ValidationError(message="邮箱或验证码错误!")
        # 可以删掉captcha_model ,  也可以写一些脚本, 定期的删除一些没用的验证码, 可以加一个字段
        # else:
        #     db.session.delete(captcha_model)
        #     db.session.commit()

    def validate_graph_captcha(self, field):
        key = request.cookies.get("_graph_captcha_key")
        cache_captcha = cache.get(key)
        graph_captcha = field.data
        if not cache_captcha or cache_captcha.lower() != graph_captcha.lower():
            raise ValidationError(message="图形验证码错误!")




class LoginForm(wtforms.Form):
    email = wtforms.StringField(validators=[Email(message="邮箱格式错误!")])
    password = wtforms.StringField(validators=[Length(min=6, max=20, message="密码格式错误!")])
    remember = IntegerField()


class EditProfileForm(BaseForm):
    signature = StringField(validators=[Length(min=1, max=50, message="个性长度在1-50之间")])


class UploadAvatarForm(BaseForm):
    image = FileField(validators=[FileAllowed(['jpg', 'png', 'jpeg'], message="只能上传图片"), FileSize(1024*1024*5, message="图片大小不能超过5M")])


class UploadImageForm(BaseForm):
    image = FileField(validators=[FileAllowed(['jpg', 'png', 'jpeg'], message="只能上传图片"),
                                  FileSize(1024 * 1024 * 5, message="图片大小不能超过5M")])


class PublicPostForm(BaseForm):
    board_id = IntegerField(validators=[wtforms.validators.InputRequired(message="必须要传入板块id")])
    title = StringField(validators=[Length(min=3, max=200, message="标题长度在3-200之间")])
    content = StringField(validators=[wtforms.validators.InputRequired(message="内容不能为空")])


class PublicComment(BaseForm):
    post_id = IntegerField(validators=[wtforms.validators.InputRequired(message="必须要传入帖子id")])
    content = StringField(validators=[wtforms.validators.InputRequired(message="内容不能为空")])
