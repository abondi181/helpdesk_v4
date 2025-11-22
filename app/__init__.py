from flask import Flask, redirect, url_for
from .config import Config
from .extensions import db, login_manager, socketio
from .models import User

def create_app(config_class: type[Config] = Config) -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(config_class)

    # Инициализация расширений
    db.init_app(app)
    login_manager.init_app(app)

    from .extensions import migrate
    migrate.init_app(app, db)

    socketio.init_app(app, async_mode="eventlet")

    @login_manager.user_loader
    def load_user(user_id: str):
        return User.query.get(int(user_id))

    login_manager.login_view = "auth.login"

    # Регистрация блюпринтов
    from .blueprints.auth import bp as auth_bp
    from .blueprints.tasks.views import bp as tasks_views_bp
    from .blueprints.tasks.api import bp as tasks_api_bp
    from .blueprints.tasks.exports import bp as tasks_exports_bp
    from .blueprints.users import bp as users_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(tasks_views_bp)
    app.register_blueprint(tasks_api_bp)
    app.register_blueprint(tasks_exports_bp)
    app.register_blueprint(users_bp)


    
    @app.route("/")
    def index():
        return redirect(url_for("tasks_views.list_tasks"))

    return app
