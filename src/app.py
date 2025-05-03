from flask import Flask
from flask_login import LoginManager
from flask_cors import CORS
from models import db, User
from config import Config
from routes import register_routes

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 初始化資料庫
    db.init_app(app)
    
    # 初始化CORS
    CORS(app)
    
    # 初始化登入管理
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # 註冊所有路由
    register_routes(app)
    
    return app

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        from models import db

        db.drop_all()
        db.create_all()

        from seeder import seed_data
        seed_data()
        
    app.run(host='0.0.0.0')
    # app.run(host='0.0.0.0',debug=True)