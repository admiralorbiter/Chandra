#!/usr/bin/env python3
"""
Database seeding script for Chandra Education Engine
Creates initial admin, author, and student users
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.auth.seed import seed_users

if __name__ == '__main__':
    print("🌱 Seeding Chandra Education Database...")
    print("=" * 50)
    
    try:
        seed_users()
        print("\n✅ Database seeding completed successfully!")
        print("\n📝 Next steps:")
        print("1. Start the application: python run.py")
        print("2. Login with one of the default accounts")
        print("3. Change default passwords in production!")
        
    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        sys.exit(1) 