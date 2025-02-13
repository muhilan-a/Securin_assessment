from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.config import Config 
from flasgger import Swagger

app = Flask(__name__)
app.config.from_object(Config)
Swagger(app, template={
    "swagger": "2.0",
    "info": {
        "title": "CVE API Documentation",
        "description": "API for retrieving CVE details from the NVD database",
        "version": "1.0.0"
    },
    "host": "localhost:5000",  
    "basePath": "/",
})

db = SQLAlchemy(app)
def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)

    # Import and register blueprints
    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)

    return app

from app import routes, models
