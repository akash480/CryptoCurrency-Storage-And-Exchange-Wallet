from main import app, db

with app.app_context():
    # Create all tables
    db.create_all()
    print("Database tables have been created successfully!") 