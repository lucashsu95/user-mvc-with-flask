from faker import Faker
from models import db, User
from sqlalchemy.exc import IntegrityError

def seed_data():
    fake = Faker()
    for _ in range(10):
        user = User(name=fake.name(), email=fake.email())
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()