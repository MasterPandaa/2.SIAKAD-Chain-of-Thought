import logging

from config import get_config
from flask import Flask, render_template
from flask_wtf.csrf import generate_csrf

from . import extensions
from .extensions import bcrypt, csrf, db, login_manager, migrate
from .models import RoleEnum


def create_app(config_class=None):
    app = Flask(__name__)
    app.config.from_object(config_class or get_config())

    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    csrf.init_app(app)

    # Login manager after app init
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"

    from .models import User  # local import to avoid circular

    @login_manager.user_loader
    def load_user(user_id: str):
        return db.session.get(User, int(user_id))

    # Jinja globals/filters
    app.jinja_env.globals["RoleEnum"] = RoleEnum
    app.jinja_env.globals["csrf_token"] = generate_csrf

    # Blueprints (registered later when modules exist)
    from .auth.routes import bp as auth_bp
    from .classes.routes import bp as classes_bp
    from .dashboard.routes import bp as dashboard_bp
    from .grades.routes import bp as grades_bp
    from .students.routes import bp as students_bp
    from .subjects.routes import bp as subjects_bp
    from .teachers.routes import bp as teachers_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(teachers_bp)
    app.register_blueprint(subjects_bp)
    app.register_blueprint(classes_bp)
    app.register_blueprint(grades_bp)

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("errors/500.html"), 500

    # Minimal logging in production
    if not app.debug:
        logging.basicConfig(level=logging.INFO)
        app.logger.info("SIAKAD app initialized")

    return app
