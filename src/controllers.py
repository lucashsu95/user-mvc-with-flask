from flask import Flask, render_template, request, redirect, url_for, jsonify,Response
from models import db, User
from flask_restful import Api, Resource
from apiResponse import *
from flask_cors import CORS
from werkzeug.security import check_password_hash,generate_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import os

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
    user:User = User.query.get_or_404(id)
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


class UserAPI(Resource):
    def get(self, id=None):
        if id is None:
            users = User.query.all()
            return success([user.to_dict() for user in users], 200)
        
        user:User|False = get_user(id)
        if not user:
            return user_not_exists()
        return success(user.to_dict(), 200)

    def post(self):
        data = request.get_json()

        if 'name' not in data or 'email' not in data:
            return missing_fields()
        
        if User.query.filter_by(email=data['email']).first():
            return email_exists()
        
        new_user = User(name=data['name'], email=data['email'])
        db.session.add(new_user)
        db.session.commit()
        return success(new_user.to_dict(), 201)
    
    def put(self, id):
        user:User|False = get_user(id)
        if not user:
            return user_not_exists()
    
        data = request.get_json()
        if 'name' in data:
            user.name = data['name']
        if 'email' in data:
            user.email = data['email']
        db.session.commit()
        return success(user.to_dict(), 201)
    
    def delete(self, id):
        user:User|False = get_user(id)
        if not user:
            return user_not_exists()
        
        db.session.delete(user)
        db.session.commit()
        return success("", 204)

api = Api(app)
api.add_resource(UserAPI, '/api/users', '/api/users/<int:id>')