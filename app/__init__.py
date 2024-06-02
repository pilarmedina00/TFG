from flask import Flask

def create_app():
    app = Flask(__name__)

    # Registrar blueprints y rutas
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
