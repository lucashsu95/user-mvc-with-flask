# from faker import Faker
from models import db, User
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

def seed_data():
    # fake = Faker()
    for i in range(1,11):
        user = User(name=f'user{i}', email=f'user{i}@web.tw', passwordHash=generate_password_hash(f'user{i}pass', method='pbkdf2:sha256'))
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()