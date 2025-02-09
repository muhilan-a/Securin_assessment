from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.config import Config  # # Import Config from app.config

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db = SQLAlchemy(app)

# Import routes and models after initializing app and db to avoid circular imports
from app import routes, models