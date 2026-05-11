"""Database initialization and management utilities"""
from __init__ import app, db, User
import os

def init_db():
    """Initialize the database with tables"""
    with app.app_context():
        db.create_all()
        print("✓ Database tables created successfully")

def reset_db():
    """Drop and recreate all tables (WARNING: deletes all data)"""
    with app.app_context():
        confirm = input("⚠️  This will delete ALL data. Type 'yes' to confirm: ")
        if confirm.lower() == 'yes':
            db.drop_all()
            db.create_all()
            print("✓ Database reset successfully")
        else:
            print("✗ Database reset cancelled")

def create_test_user():
    """Create a test user for development"""
    with app.app_context():
        if User.query.filter_by(username='testuser').first():
            print("✗ Test user already exists")
            return
        
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        print("✓ Test user created: username='testuser', password='password123'")

if __name__ == '__main__':
    init_db()
