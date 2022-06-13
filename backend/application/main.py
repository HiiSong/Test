# 该文件是后端程序的入口
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token  # 制作json web令牌，保护路由
from .extensions import bcrypt  # 加密

from orm_interface.entities.user import User  # 用户对象
# 使用sqlalchemy创建引擎连接PostgreSQL数据库，通过session绑定引擎，通过base构造基类
from orm_interface.base import Base, Session, engine

main = Blueprint("main", __name__)  # 创建一个flask蓝图，main.py是蓝图的名称将包含蓝图实现

Base.metadata.create_all(engine)
session = Session()


# main.route（）是flask蓝图最常用的装饰器之一，允许将视图函数关联到URL路由
@main.route('/login', methods=['POST'])
def login():
    email = request.get_json()['email']
    password = request.get_json()['password']
    user = session.query(User).filter(User.email == email).first()

    if user is None:
        return jsonify({"error": "User not registered"})

    else:
        if bcrypt.check_password_hash(user.password, password):
            access_token = create_access_token(identity={
                'firstname': user.firstname,
                'lastname': user.lastname,
                'email': user.email,
            })
            return jsonify({'token': access_token})
        else:
            return jsonify({'error': 'Wrong password!'})


@main.route('/register', methods=['POST'])
def register():
    email = request.get_json()['email']
    password = request.get_json()['password']
    firstname = request.get_json()['firstname']
    lastname = request.get_json()['lastname']

    user = session.query(User).filter(User.email == email).first()

    if user is None:
        hash_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(
            firstname=firstname,
            lastname=lastname,
            email=email,
            password=hash_password
        )
        session.add(new_user)
        session.commit()
        return jsonify({"success": "User registered"})

    else:
        return jsonify({"error": "User is already registered"})


@main.route('/commence_scraping', methods=['GET', 'POST'])
def scrape():
    import os
    import yaml  # yaml是一种人类可读的数据序列化语言。它通常用于配置文件，但也用于数据存储（例如调试输出）或传输（例如文档标题）
    # multiprocessing用于进程并行，在 multiprocessing 中通过创建一个 Process 对象然后调用它的 start() 方法来生成进程
    from multiprocessing import Process
    from .scraper.scrape_control import run

    with open(os.path.join(os.path.dirname(__file__), "scraper", "config.yaml"), "r") as file:
        config = file.read()
    config = yaml.safe_load(config)  # 配置文件

    if request.method == 'GET':
        return {"statusMessage": config["statusMessage"]}

    e3_url = request.json["e3"]  # 这两行是从前端发来的请求json中拿到键值对的值
    insight_url = request.json["insight"]

    config["statusMessage"] = "running..."
    with open(os.path.join(os.path.dirname(__file__), "scraper", "config.yaml"), "w") as file:
        file.write(yaml.dump(config))  # 转储数据

    # 创建一个进程，找到目标函数run并传入参数args
    scraper = Process(target=run, args=(config, insight_url, e3_url,))
    scraper.start()
    return ""
