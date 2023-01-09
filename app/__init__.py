from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_app():
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.Config')

    db.init_app(app)

    with app.app_context():
        from app.main import routes as main_routes
        app.register_blueprint(main_routes.main_bp)
        
        db.create_all()
        return app