from pathlib import Path
import json
from flask import Flask, jsonify, render_template
from app.config import Config
from app.extensions import db, login_manager, csrf, limiter
from app.models import User, Resume, Analysis

def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)
    app.jinja_env.filters['from_json'] = json.loads
    if not app.config.get("SECRET_KEY"):
        raise RuntimeError("Set SECRET_KEY in your .env file before starting ResumeIQ.")

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    upload_dir = Path(app.instance_path) / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    app.config["UPLOAD_FOLDER"] = str(upload_dir)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    login_manager.login_view = "auth.login"

    from app.auth.routes import auth_bp
    from app.main.routes import main_bp
    from app.resumes.routes import resumes_bp
    from app.matching.routes import matching_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(resumes_bp)
    app.register_blueprint(matching_bp)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "application": "ResumeIQ"}), 200

    @app.errorhandler(404)
    def not_found(error):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template("500.html"), 500

    with app.app_context():
        db.create_all()  # Convenient for this starter; use Flask-Migrate in production.

    return app
