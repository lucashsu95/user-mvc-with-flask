from flask import request
from flask_restful import Resource
from flask_login import logout_user

from models import User
from services.user_service import get_all_users, get_user_by_id, create_user, update_user, delete_user
from services.auth_service import authenticate_user, check_token, revoke_token
from apiResponse import *

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
    user = get_user_by_id(user_id)
    if not user:
        return user_not_exists(), None
    return None, user

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
        users = get_all_users()
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
                password:
                  type: string
              required:
                - name
                - email
                - password

        responses:
          201:
            description: The created user
          400:
            description: MSG_PASSWORD_TOO_SHORT
          400:
            description: MSG_MISSING_FIELDS
          400:
            description: MSG_EMAIL_EXISTS
        """
        data = request.get_json()
        if 'name' not in data or 'email' not in data or 'password' not in data:
            return missing_fields()
        if User.query.filter_by(email=data['email']).first():
            return email_exists()
        if len(data['password']) < 8:
            return password_too_short()
        
        new_user = create_user(data['name'], data['email'], data['password'])
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
        user = get_user_by_id(id)
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
          - name: Authorization
            in: header
            type: string
            required: true
            description: Bearer token
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
          200:
            description: User updated successfully
          400:
            description: MSG_MISSING_FIELDS
          400:
            description: MSG_PASSWORD_TOO_SHORT
          401:
            description: MSG_INVALID_ACCESS_TOKEN
          403:
            description: MSG_PERMISSION_DENY
          404:
            description: MSG_USER_NOT_EXISTS
        """
        # 檢查有沒有 access token, 並且檢查 token 是否有效
        error, existsUser = check_authorization()
        if error:
            return error
        error, user = get_user_or_404(id)
        if error:
            return error
        if user.id != existsUser.id:
            return permission_deny()
        if User.query.filter_by(email=data['email']).first():
            return email_exists()
        
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        
        updated_user = update_user(user, name, email, password)
        return success(updated_user.to_dict(), 201)
    
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
          - name: Authorization
            in: header
            type: string
            required: true
            description: Bearer token
        responses:
          204:
            description: No content
          401:
            description: MSG_INVALID_ACCESS_TOKEN
          403:
            description: MSG_PERMISSION_DENY
          404:
            description: MSG_USER_NOT_EXISTS
        """
        error, existsUser = check_authorization()
        if error:
            return error
        error, user = get_user_or_404(id)
        if error:
            return error
        if user.id != existsUser.id:
            return permission_deny()
        
        delete_user(user)
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
                  example: "user1@web.com"
                password:
                  type: string
                  example: "user1pass"
              required:
                - email
                - password
        responses:
          200:
            description: The logged-in user with access token
          401:
            description: MSG_INVALID_LOGIN
        """
        data = request.get_json()
        if 'email' not in data or 'password' not in data:
            return missing_fields()
        
        response = authenticate_user(data['email'], data['password'])
        if response:
            return success(response, 200)
        return invalid_login()

    def delete(self):
        """
        User logout
        ---
        tags:
          - Auth
        parameters:
          - name: Authorization
            in: header
            type: string
            required: true
            description: Bearer token
        responses:
          204:
            description: No content
        """
        logout_user()
        error, existsUser = check_authorization()
        if error:
            return error
        
        revoke_token(existsUser)
        return success("", 204)

class NotFound(Resource):
    def get(self):
        return {'message': 'Resource not found'}, 404