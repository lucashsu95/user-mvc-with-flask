from controllers import app

if __name__ == '__main__':
    with app.app_context():
        from models import db

        db.drop_all()
        db.create_all()

        from seeder import seed_data
        seed_data()
        
    app.run(host='0.0.0.0')
    # app.run(host='0.0.0.0',debug=True)