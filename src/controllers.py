from flask import Flask, render_template, request, redirect, url_for
from flask_restful import Api, Resource
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required
from models import db, User
from apiResponse import *
from werkzeug.security import check_password_hash,generate_password_hash
import jwt
import datetime
import os
from flasgger import Swagger

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db.init_app(app)

@app.route('/')
def index():
    users = User.query.all()
    displayUsers = [user.to_dict() for user in users]
    return render_template('index.html', users=displayUsers)

@app.route('/create', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(name=name, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('create.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    user: User = User.query.get_or_404(id)
    if request.method == 'POST':
        user.name = request.form['name']
        user.email = request.form['email']
        password = request.form['password']
        if(password):
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            user.password = hashed_password
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit.html', user=user)

@app.route('/delete/<int:id>')
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('index'))

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        is_correct = check_password_hash(user.passwordHash, password)
        
        if user and is_correct:
            login_user(user)
            return redirect(url_for('index'))
        return 'Invalid credentials'
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# <--------------------------------------API-------------------------------------->

def get_user(id) -> User|bool:
    user = User.query.filter_by(id=id).first()
    print(user)
    if user is None:
        return False
    return user


def check_token(token) -> User|bool:
    try:
        user = User.query.filter_by(access_token=token).first()
        if not user:
            return False
        return user
    except:
        return False

def check_authorization():
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header.split(' ')[0] != 'Bearer':
        return invalid_access_token(), None
    token = auth_header.split(' ')[1]
    existsUser = check_token(token)
    if not existsUser:
        return invalid_access_token(), None
    return None, existsUser

def get_user_or_404(user_id):
    user = get_user(user_id)
    if not user:
        return user_not_exists(), None
    return None, user


class UserAPI(Resource):
    def get(self, id=None):
        """
        Get user(s)
        ---
        tags:
          - Users
        parameters:
          - name: id
            in: path
            type: integer
            required: false
            description: The user's ID
        responses:
          200:
            description: A list of users or a single user
        """
        if id is None:
            users = User.query.all()
            return success([user.to_dict() for user in users], 200)
        
        user:User|False = get_user(id)
        if not user:
            return user_not_exists()
        return success(user.to_dict(), 200)

    def post(self):
        """
        Create a new user
        ---
        tags:
          - Users
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                name:
                  type: string
                email:
                  type: string
                password:
                  type: string
        responses:
          201:
            description: The created user
        """
        data = request.get_json()

        if 'name' not in data or 'email' not in data or 'password' not in data:
            return missing_fields()
        
        if User.query.filter_by(email=data['email']).first():
            return email_exists()
        
        if len(data['password']) < 8:
            return password_too_short()
        
        new_user = User(name=data['name'], email=data['email'],passwordHash=generate_password_hash(data['password'], method='pbkdf2:sha256'))
        db.session.add(new_user)
        db.session.commit()
        return success(new_user.to_dict(), 201)
    
    def put(self, id):
        """
        Update an existing user
        ---
        tags:
          - Users
        parameters:
          - name: id
            in: path
            type: integer
            required: true
            description: The user's ID
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                name:
                  type: string
                email:
                  type: string
                password:
                  type: string
        responses:
          201:
            description: The updated user
        """
        # 檢查有沒有 access token, 並且檢查 token 是否有效
        error, existsUser = check_authorization()
        if error:
            return error

        # 檢查 user 是否存在
        error, user = get_user_or_404(id)
        if error:
            return error

        # 只有自己才可以修改
        if user.id != existsUser.id:
            return permission_deny()
        
        data = request.get_json()
        if 'name' in data:
            user.name = data['name']
        if 'email' in data:
            user.email = data['email']
        if 'password' in data:
            user.passwordHash = generate_password_hash(data['password'], method='pbkdf2:sha256')

        db.session.commit()
        return success(user.to_dict(), 201)
    
    def delete(self, id):
        """
        Delete a user
        ---
        tags:
          - Users
        parameters:
          - name: id
            in: path
            type: integer
            required: true
            description: The user's ID
        responses:
          204:
            description: No content
        """
        error, existsUser = check_authorization()
        if error:
            return error

        error, user = get_user_or_404(id)
        if error:
            return error

        # 只有自己才可以刪除
        if user.id != existsUser.id:
            return permission_deny()
        
        db.session.delete(user)
        db.session.commit()
        return success("", 204)


class AuthAPI(Resource):
    def post(self):
        """
        User login
        ---
        tags:
          - Auth
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                email:
                  type: string
                password:
                  type: string
        responses:
          200:
            description: The logged-in user with access token
          401:
            description: Invalid login
        """
        data = request.get_json()
        if 'email' not in data or 'password' not in data:
            return missing_fields()
        
        user = User.query.filter_by(email=data['email']).first()
        if user and check_password_hash(user.passwordHash, data['password']):
            login_user(user)
            
            token = jwt.encode({
                'user_id': user.id,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            }, app.config['SECRET_KEY'], algorithm='HS256')
            
            user.access_token = token
            db.session.commit()
            
            response = user.to_dict()
            response['access_token'] = token
            return success(response, 200)
        return invalid_login()

    def delete(self):
        """
        User logout
        ---
        tags:
          - Auth
        responses:
          204:
            description: No content
        """
        logout_user()
        error, existsUser = check_authorization()
        if error:
            return error
        existsUser.access_token = None
        db.session.commit()
        return success("", 204)
    
    def get(self):
        """
        Get all users
        ---
        tags:
          - Users
        responses:
          200:
            description: A list of users
        """
        users = User.query.all()
        return success([user.to_all() for user in users], 200)


api = Api(app)
swagger = Swagger(app)
api.add_resource(UserAPI, '/api/users', '/api/users/<int:id>')
api.add_resource(AuthAPI, '/api/auth')