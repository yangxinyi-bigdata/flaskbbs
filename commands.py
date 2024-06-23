from models.post import BoardModel, PostModel
from models.auth import UserModel, RoleModel, Permission
from exts import db
import random


# 用来初始化数据库的命令
def init_boards():
    boards = ["Python", "Flask", "Django", "Tornado", "数据库", "前端", "后端", "人工智能", "大数据", "爬虫", "机器学习", "深度学习"]
    for index, board in enumerate(boards):
        board_model = BoardModel(name=board, priority=len(boards)-index)
        db.session.add(board_model)
    db.session.commit()
    print("板块初始化成功")


def create_test_posts():
    # 取出所有板块标题形成一个列表
    boards = list(BoardModel.query.all())
    # 循环99次
    for x in range(99):
        # 将数字填充进标题
        title = "我是标题%d" % x
        content = "我是内容%d" % x
        # 提取出第一个用户数据
        author = UserModel.query.first()
        # 随机生成一个整数
        index = random.randint(0, len(boards) - 1)
        # 随机取一个板块
        board = boards[index]
        # 使用这些数据生成一个文章
        post_model = PostModel(title=title, content=content, author=author, board=board)
        db.session.add(post_model)
    db.session.commit()
    print("测试帖子添加成功")


def init_roles():
    # 运营
    operator_role = RoleModel(name="运营", desc="负责管理帖子和评论",
                         permissions=Permission.POST | Permission.COMMENT | Permission.USER)
    # 管理员
    admin_role = RoleModel(name="管理员", desc="负责整个网站的管理",
                      permissions=Permission.POST | Permission.COMMENT | Permission.USER | Permission.STAFF)
    # 开发者（权限是最大的）
    developer_role = RoleModel(name="开发者", desc="负责网站的开发", permissions=Permission.ALL_PERMISSION)

    db.session.add_all([operator_role, admin_role, developer_role])
    db.session.commit()
    print("角色添加成功！")


def init_developer():
    role = RoleModel.query.filter_by(name="开发者").first()
    user = UserModel(username="hynever", email="hynever@qq.com", password='111111', is_staff=True, role=role)
    db.session.add(user)
    db.session.commit()
    print("开发者角色下的用户创建成功")


def bind_roles():
    user1 = UserModel.query.filter_by(email="yangyuehaha@qq.com").first()
    user2 = UserModel.query.filter_by(email="yangyuegaga@qq.com").first()
    user3 = UserModel.query.filter_by(email="yunwei@qq.com").first()

    role1 = RoleModel.query.filter_by(name="开发者").first()
    role2 = RoleModel.query.filter_by(name="运营").first()
    role3 = RoleModel.query.filter_by(name="管理员").first()

    user1.role = role1
    user2.role = role3
    user3.role = role2

    db.session.commit()
    print("用户和角色绑定成功!")
