from models import db, User
from werkzeug.security import generate_password_hash

def get_all_users():
    return User.query.all()

def get_user_by_id(id):
    user = User.query.filter_by(id=id).first()
    if user is None:
        return False
    return user

def get_user_by_email(email):
    return User.query.filter_by(email=email).first()

def create_user(name, email, password):
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = User(name=name, email=email, passwordHash=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return new_user

def update_user(user, name=None, email=None, password=None):
    if name:
        user.name = name
    if email:
        user.email = email
    if password:
        user.passwordHash = generate_password_hash(password, method='pbkdf2:sha256')
    db.session.commit()
    return user

def delete_user(user):
    db.session.delete(user)
    db.session.commit()