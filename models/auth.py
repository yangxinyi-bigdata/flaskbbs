from werkzeug.security import generate_password_hash
import shortuuid
from datetime import datetime

from flask import Blueprint, render_template, jsonify, redirect, url_for, session
from flask import request
from flask_mail import Message
from sqlalchemy_serializer import SerializerMixin

from exts import mail, db
from werkzeug.security import generate_password_hash, check_password_hash


bp = Blueprint("auth", __name__, url_prefix="/auth")


# Path: blueprints/auth.py

class Permission(object):
    # 255的二进制方式来表示 1111 1111
    ALL_PERMISSION = 0b11111111
    # 1. 访问者权限
    VISITOR =        0b00000001
    # 2. 管理帖子权限
    POST =         0b00000010
    # 3. 管理评论的权限
    COMMENT =      0b00000100
    # 4. 管理板块的权限
    BANNER =        0b00001000
    # 5. 管理前台用户的权限
    USER =      0b00010000
    # 6. 管理后台管理员的权限
    STAFF =        0b01000000


class RoleModel(db.Model, SerializerMixin):
    serialize_only = ("id", "name", "desc", "create_time")
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    desc = db.Column(db.String(200),nullable=True)
    create_time = db.Column(db.DateTime,default=datetime.now)
    permissions = db.Column(db.Integer,default=Permission.VISITOR)


class UserModel(db.Model, SerializerMixin):
    # serialize_rules = ("-_password",)
    serialize_rules = ("-_password", "-posts", "-comments")
    # serialize_only = ("id", "email", "username", "avatar", "signature", "join_time", "is_staff", "is_active")
    __tablename__ = "user"
    id = db.Column(db.String(100), primary_key=True, default=shortuuid.uuid)
    email = db.Column(db.String(50), unique=True, nullable=False)
    username = db.Column(db.String(50), nullable=False)
    _password = db.Column(db.String(200), nullable=False)
    avatar = db.Column(db.String(100))
    signature = db.Column(db.String(100))
    join_time = db.Column(db.DateTime, default=datetime.now)
    is_staff = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"))

    role = (db.relationship("RoleModel", backref="users"))


    def __init__(self, *args, **kwargs):
        if "password" in kwargs:
            self.password = kwargs.get('password')
            kwargs.pop("password")
        super(UserModel, self).__init__(*args, **kwargs)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, newpwd):
        self._password = generate_password_hash(newpwd)

    def check_password(self, rawpwd):
        return check_password_hash(self.password, rawpwd)

    def has_permission(self, permissions):
        """用户当前所拥有的权限和你传进来的进行与操作
        如果拥有的权限和你传过来的权限进行与操作
        假设传进来的是post权限 010  ,  这个用户的权限是 011 那么与操作 为 010
         所以一定和传进来的相同, 0一定还是0, 1一定是在对位也是1的情况下, 才会是1"""
        return (self.role.permissions & permissions) == permissions








# class RoleModel(db.Model, SerializerMixin):
#     serialize_only = ("id", "name", "desc", "create_time")
#     __tablename__ = 'role'
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     name = db.Column(db.String(50), nullable=False)
#     desc = db.Column(db.String(200),nullable=True)
#     create_time = db.Column(db.DateTime,default=datetime.now)
#     permissions = db.Column(db.Integer,default=Permission.VISITOR)










