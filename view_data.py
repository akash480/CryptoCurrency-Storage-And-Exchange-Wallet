from main import app, db, User, Wallet, Transaction

def print_table_data(model, name):
    print(f"\n=== {name.upper()} TABLE ===")
    
    # Get column names
    columns = model.__table__.columns.keys()
    print("Columns:", ", ".join(columns))
    
    with app.app_context():
        # Get all records
        records = model.query.all()
        print(f"\nNumber of records: {len(records)}")
        print("\nData:")
        
        for record in records:
            print("-" * 50)
            for column in columns:
                print(f"{column}: {getattr(record, column)}")

# View all three tables
print_table_data(User, "User")
print_table_data(Wallet, "Wallet")
print_table_data(Transaction, "Transaction") 