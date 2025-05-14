from main import app, db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    # First, create all tables
    db.create_all()
    
    # Create a test user
    test_user = User(
        username='test_user',
        password_hash=generate_password_hash('test123')
    )
    
    # Add the user to the database
    db.session.add(test_user)
    db.session.commit()
    
    # Verify the user was created
    users = User.query.all()
    print("\nUsers in database:")
    for user in users:
        print(f"Username: {user.username}")
        
    # Print all table names
    print("\nAll tables in database:")
    for table in db.metadata.tables.keys():
        print(f"- {table}") 