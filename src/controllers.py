from flask import Flask, render_template, request, redirect, url_for, jsonify,Response
from models import db, User
from flask_restful import Api, Resource
from apiResponse import *
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db.init_app(app)

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

@app.route('/create', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':

        if ('name' not in request.form or 'email' not in request.form) or (request.form['name'] == "" or request.form['email'] == ""):
            return missing_fields()
        
        name = request.form['name']
        email = request.form['email']

        if(User.query.filter_by(email=email).first()):
            return email_exists()
        
        new_user = User(name=name, email=email)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('create.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        user.name = request.form['name']
        user.email = request.form['email']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit.html', user=user)

@app.route('/delete/<int:id>')
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
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

        if ('name' not in data or 'email' not in data) or (data['name'] == "" or data['email'] == ""):
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
            if data['name'] == "":
                return missing_fields()
            user.name = data['name']
        if 'email' in data:
            if data['email'] == "":
                return missing_fields()
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