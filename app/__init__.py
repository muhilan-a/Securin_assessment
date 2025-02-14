from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.config import Config 
from flasgger import Swagger
from flask_cors import CORS

app = Flask(__name__)
CORS(app) 

app.config.from_object(Config)

Swagger(app, template={
    "swagger": "2.0",
    "info": {
        "title": "CVE Tracker API",
        "description": "API for accessing National Vulnerability Database (NVD) CVE records",
        "version": "2.0.0"
    },
    "host": "localhost:5000",
    "basePath": "/",
    "schemes": ["http"],
    "definitions": {
        "CVEListResponse": {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/CVESummary"}
                },
                "page": {"type": "integer"},
                "per_page": {"type": "integer"},
                "total": {"type": "integer"}
            }
        },
        "CVESummary": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "published": {"type": "string", "format": "date-time"},
                "last_modified": {"type": "string", "format": "date-time"},
                "status": {"type": "string"},
                "base_score_v2": {"type": "number"},
                "base_score_v3": {"type": "number"}
            }
        },
        "CVEDetail": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "published": {"type": "string", "format": "date-time"},
                "last_modified": {"type": "string", "format": "date-time"},
                "description": {"type": "string"},
                "cvss_v2_vector": {"type": "string"},
                "cvss_v2_severity": {"type": "string"},
                "cvss_v3_vector": {"type": "string"},
                "cvss_v3_severity": {"type": "string"},
                "exploitability_score": {"type": "number"},
                "impact_score": {"type": "number"},
                "cpe_list": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "criteria": {"type": "string"},
                            "vulnerable": {"type": "boolean"}
                        }
                    }
                }
            }
        }
    }
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