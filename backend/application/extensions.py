from flask_bcrypt import Bcrypt  # 给app加密用的
from flask_jwt_extended import JWTManager

bcrypt = Bcrypt()
jwt = JWTManager()
