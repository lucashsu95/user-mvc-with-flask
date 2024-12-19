from flask import Flask, render_template, request, redirect, url_for, jsonify,Response
from models import db, User
from flask_restful import Api, Resource
from apiResponse import *
from flask_cors import CORS
from flasgger import Swagger

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

def get_user(id) -> User | bool:
    user = User.query.filter_by(id=id).first()
    print(user)
    if user is None:
        return False
    return user


class UserAPI(Resource):
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
        return success([user.to_dict() for user in users], 200)

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
              required:
                - name
                - email
        responses:
          201:
            description: The created user
          400:
            description: MSG_MISSING_FIELDS
          400:
            description: MSG_EMAIL_EXISTS
        """
        data = request.get_json()

        if ('name' not in data or 'email' not in data) or (data['name'] == "" or data['email'] == ""):
            return missing_fields()
        
        if User.query.filter_by(email=data['email']).first():
            return email_exists()
        
        new_user = User(name=data['name'], email=data['email'])
        db.session.add(new_user)
        db.session.commit()
        return success(new_user.to_dict(), 201)

class UserDetailAPI(Resource):
    def get(self, id):
        """
        Get a single user
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
          200:
            description: A single user
          404:
            description: MSG_USER_NOT_EXISTS
        """
        user: User | False = get_user(id)
        if not user:
            return user_not_exists()
        return success(user.to_dict(), 200)
    
    def put(self, id):
        """
        Update a user
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

        responses:
          200:
            description: User updated successfully
          400:
            description: MSG_MISSING_FIELDS
          404:
            description: MSG_USER_NOT_EXISTS
        """
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
        """
        Update a user
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

        responses:
          200:
            description: User updated successfully
          400:
            description: MSG_MISSING_FIELDS
          404:
            description: MSG_USER_NOT_EXISTS
        """
        user:User|False = get_user(id)
        if not user:
            return user_not_exists()
        
        db.session.delete(user)
        db.session.commit()
        return success("", 204)

class NotFound(Resource):
    def get(self):
        return {'message': 'Resource not found'}, 404


api = Api(app, prefix='/api', catch_all_404s=True, errors={404: "not found"})
api.add_resource(UserAPI, '/users', endpoint='user', methods=['POST', 'GET'])
api.add_resource(UserDetailAPI, '/users/<int:id>', endpoint='user_detail', methods=['GET', 'PUT', 'DELETE'])
api.add_resource(NotFound, '/404')

swagger_config = {
    'title': 'User API CURD',
    'uiversion': 3,
    'specs': [
        {
            'endpoint': 'apispec_1',
            'route': '/apispec_1.json',
            'rule_filter': lambda rule: True,
            'model_filter': lambda tag: True,
        }
    ],
    'static_url_path': '/flasgger_static',
    'swagger_ui': True,
    'specs_route': '/apidocs/',
    'headers': []
}

swagger = Swagger(app, config=swagger_config)