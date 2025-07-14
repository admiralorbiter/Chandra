"""
Seed script for creating initial users and roles
"""

from app import db, create_app
from app.models import User
from datetime import datetime

def seed_users():
    """Create initial users and roles."""
    app = create_app()
    
    with app.app_context():
        # Check if admin user already exists
        admin_user = User.query.filter_by(email='admin@chandra.edu').first()
        if not admin_user:
            admin_user = User(
                name='Administrator',
                email='admin@chandra.edu',
                password='admin123',  # Change this in production!
                role='admin'
            )
            admin_user.created_at = datetime.utcnow()
            db.session.add(admin_user)
            print("✅ Created admin user: admin@chandra.edu")
        else:
            print("ℹ️  Admin user already exists")
        
        # Create sample author
        author_user = User.query.filter_by(email='author@chandra.edu').first()
        if not author_user:
            author_user = User(
                name='Content Author',
                email='author@chandra.edu',
                password='author123',  # Change this in production!
                role='author'
            )
            author_user.created_at = datetime.utcnow()
            db.session.add(author_user)
            print("✅ Created author user: author@chandra.edu")
        else:
            print("ℹ️  Author user already exists")
        
        # Create sample student
        student_user = User.query.filter_by(email='student@chandra.edu').first()
        if not student_user:
            student_user = User(
                name='Sample Student',
                email='student@chandra.edu',
                password='student123',  # Change this in production!
                role='student'
            )
            student_user.created_at = datetime.utcnow()
            db.session.add(student_user)
            print("✅ Created student user: student@chandra.edu")
        else:
            print("ℹ️  Student user already exists")
        
        try:
            db.session.commit()
            print("✅ Database seeded successfully!")
            print("\n📋 Default Login Credentials:")
            print("Admin: admin@chandra.edu / admin123")
            print("Author: author@chandra.edu / author123")
            print("Student: student@chandra.edu / student123")
            print("\n⚠️  IMPORTANT: Change these passwords in production!")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error seeding database: {e}")

if __name__ == '__main__':
    seed_users() 