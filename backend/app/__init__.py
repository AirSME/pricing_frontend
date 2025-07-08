from flask import Flask
from app.services.json_to_csv import json_to_csv_bp
from app.services.excel_formatter import excel_formatter_bp
from backend.config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.register_blueprint(json_to_csv_bp, url_prefix='/json_to_csv')
    app.register_blueprint(excel_formatter_bp, url_prefix='/excel_formatter')
    return app
