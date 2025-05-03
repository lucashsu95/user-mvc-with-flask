from flask import current_app
from flask_login import login_user, logout_user
from werkzeug.security import check_password_hash
from models import db, User
import jwt
import datetime

def check_token(token):
    try:
        user = User.query.filter_by(access_token=token).first()
        if not user:
            return False
        return user
    except:
        return False

def generate_token(user):
    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, current_app.config['SECRET_KEY'], algorithm='HS256')
    
    user.access_token = token
    db.session.commit()
    return token

def authenticate_user(email, password):
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.passwordHash, password):
        login_user(user)
        token = generate_token(user)
        response = user.to_dict()
        response['access_token'] = token
        return response
    return None

def revoke_token(user):
    user.access_token = None
    db.session.commit()