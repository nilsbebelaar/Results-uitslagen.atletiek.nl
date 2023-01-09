from flask import Flask

def init_app():
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.Config')

    with app.app_context():
        from app.main import routes as main_routes
        app.register_blueprint(main_routes.main_bp)
        
        return app