import os
from flask import Flask, render_template
from app.config import Config
from app.extensions import db, migrate, login_manager, csrf


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.employee import employee_bp
    from app.routes.manager import manager_bp
    from app.routes.superuser import superuser_bp
    from app.routes.recommendation import recommendation_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(employee_bp)
    app.register_blueprint(manager_bp)
    app.register_blueprint(superuser_bp)
    app.register_blueprint(recommendation_bp)

    # Landing page
    @app.route('/')
    def index():
        return render_template('landing.html')

    # Error handlers
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('shared/403.html'), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template('shared/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('shared/500.html'), 500

    # CLI command for seeding
    @app.cli.command('seed')
    def seed_command():
        from app.utils.seed_data import seed_all
        seed_all()

    # Context processor — inject current_user info into all templates
    @app.context_processor
    def inject_globals():
        return {'app_name': 'SkillMatch Pro'}

    return app
