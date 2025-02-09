import sys
import os

# Add the root directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db

# Create the application context
with app.app_context():
    # Create all database tables
    db.create_all()
    print("Database tables created successfully!")