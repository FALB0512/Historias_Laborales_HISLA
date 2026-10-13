from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Debe iniciar sesión para continuar."

    from .models import Usuario
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(Usuario, int(user_id))

    from .auth import auth_bp
    from .main import main_bp
    from .historias import historias_bp
    from .usuarios import usuarios_bp
    from .centros import centros_bp
    from .auditoria import auditoria_bp
    from .prestamos import prestamos_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(historias_bp, url_prefix="/historias")
    app.register_blueprint(usuarios_bp, url_prefix="/usuarios")
    app.register_blueprint(centros_bp, url_prefix="/centros")
    app.register_blueprint(auditoria_bp, url_prefix="/auditoria")
    app.register_blueprint(prestamos_bp, url_prefix="/prestamos")

    with app.app_context():
        db.create_all()
    return app
