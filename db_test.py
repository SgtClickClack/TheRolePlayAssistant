from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        # Test database connection
        db.session.execute(text('SELECT 1'))
        db.session.commit()
        print("Database connection successful!")
    except Exception as e:
        print(f"Database connection failed: {str(e)}")
        raise
