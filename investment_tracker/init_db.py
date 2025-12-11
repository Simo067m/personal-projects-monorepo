from app import db

if __name__ == "__main__":
    print("Initializing Investment Tracker database...")
    db.initialize_database()