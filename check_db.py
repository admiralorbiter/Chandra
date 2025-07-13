#!/usr/bin/env python3
"""
Simple script to check database contents
"""

from app import create_app, db
from app.models import User

app = create_app('development')

with app.app_context():
    print("=== Database Check ===")
    
    # Count users
    user_count = User.query.count()
    print(f"Total users: {user_count}")
    
    # List all users
    users = User.query.all()
    for user in users:
        print(f"User: {user.name} ({user.email}) - Role: {user.role} - Active: {user.is_active}")
        print(f"  Created: {user.created_at}")
        print(f"  Last login: {user.last_login}")
        print() 