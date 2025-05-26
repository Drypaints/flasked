from flask import (
    Flask,
    request,
    redirect,
    session,
    render_template,
    abort,
    url_for,
    jsonify,
)
from dotenv import load_dotenv
from typing import Dict, Any
import os
import base64
from subprocess import Popen as run
from bot import Bot
from urllib.parse import urlparse, urlunparse
import asyncio

from models import db, User

ENVIRONMENT: dict = os.environ.copy()

load_dotenv()

from flask_wtf import CSRFProtect


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")

    db.init_app(app)

    @app.before_request
    def create_tables() -> None:
        app.before_request_funcs[None].remove(create_tables)  # run once
        db.create_all()

    @app.before_request
    def create_admin() -> None:
        app.before_request_funcs[None].remove(create_admin)
        username = "admin"
        password = os.getenv(
            "ADMIN_APP_PASSWORD", base64.b64encode(os.urandom(18)).decode("utf-8")
        )

        if not User.query.filter_by(username=username).first():
            admin = User(username=username, user_type="admin")  # type: ignore
            admin.set_password(password)
            db.session.add(admin)
            db.session.commit()
            print(f"Created admin user '{username}' with password: {password}")
        else:
            print(f"Admin user '{username}' already exists.")

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password", "")
            user_type = "normal"

            if User.query.filter_by(username=username).first():
                return "Username already exists", 400

            user = User(username=username, user_type=user_type)  # type: ignore
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for("login"))
        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")

            user = User.query.filter_by(username=username).first()
            if not user or not user.check_password(password):
                return "Invalid credentials", 401

            session["username"] = user.username
            session["user_type"] = user.user_type
            return redirect(url_for("index"))
        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("index"))

    @app.route("/profile")
    def profile():
        username = session.get("username")
        if not username:
            return redirect(url_for("login"))

        user = User.query.filter_by(username=username).first()
        if not user:
            abort(404)

        return render_template("profile.html", user=user)

    @app.route("/admin")
    def admin():
        if session.get("user_type") != "admin":
            abort(403)
        users = User.query.all()
        return render_template("admin.html", users=users)

    @app.route("/api/promote/<int:user_id>", methods=["POST"])
    def promote(user_id: int):
        if session.get("user_type") != "admin":
            abort(403)
        user = User.query.get_or_404(user_id)
        user.user_type = "admin"
        db.session.commit()
        return redirect(url_for("admin"))

    @app.route("/env", methods=["GET", "POST", "PUT", "DELETE"])  # type: ignore
    def manage_env():
        global ENVIRONMENT

        if session.get("user_type") != "admin":
            abort(403)

        if request.method == "GET":
            try:
                with open("/app/webflag.txt") as f:
                    webflag = f.read()
            except Exception as e:
                webflag = f"Error reading webflag: {e}"
            return render_template("env.html", environment=ENVIRONMENT, webflag=webflag)

        key = request.form.get("key")
        if not key:
            return "Missing key", 400

        if request.method == "POST" or request.method == "PUT":
            if key in ENVIRONMENT:
                status = 200
            else:
                status = 201
            ENVIRONMENT[key] = request.form.get("value", "")
            return f"Added {key}", status

        if request.method == "DELETE":
            if key not in ENVIRONMENT:
                return "Key not found", 404
            del ENVIRONMENT[key]
            return f"Deleted {key}", 200

    @app.route("/start_backup", methods=["POST"])
    def start_backup():
        if session.get("user_type") != "admin":
            abort(403)

        try:
            run(
                ["/usr/local/bin/python", "/app/scripts/backup.py"],
                env=ENVIRONMENT,
            )
            return "Backup started successfully!", 200
        except Exception as e:
            return f"Failed to start backup: {e}", 500

    @app.route("/api/search_analytics/<term>")
    def search_analytics(term: str):
        username = session.get("username", "guest")
        return {"username": username, "function": "search"}

    @app.route("/api/analytics_user/<username>", methods=["POST"])
    def analytics_user(username: str):
        data = request.get_json()
        print(f"Analytics received from {username}: {data}")
        return "Logged", 200

    @app.route("/api/user/<int:userid>")
    def api_user(userid):
        if "username" not in session:
            return jsonify({"error": "Authentication required"}), 401

        requesting_user = User.query.filter_by(username=session["username"]).first()
        target_user = User.query.get(userid)

        if not target_user:
            return jsonify({"error": "User not found"}), 404

        if requesting_user.user_type != "admin" and requesting_user.id != userid:  # type: ignore
            return jsonify({"error": "Unauthorized"}), 403

        return jsonify(
            {
                "id": target_user.id,
                "username": target_user.username,
                "user_type": target_user.user_type,
            }
        )

    @app.route("/report", methods=["GET", "POST"])
    def report():
        if "username" not in session:
            return redirect(url_for("login"))

        if request.method == "POST":
            url = request.form.get("url", "").strip()
            if not url:
                return "Missing URL", 400

            try:
                parsed = urlparse(url)
                # Force hostname to localhost
                safe_url = urlunparse(
                    parsed._replace(scheme="http", netloc="127.0.0.1:5000")
                )
            except Exception:
                return "Invalid URL", 400

            bot = Bot()
            asyncio.run(bot.visit(safe_url))

            return render_template("report.html", submitted=True, url=safe_url)

        return render_template("report.html", submitted=False)

    @app.route("/health")
    def health():
        return "OK", 200

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("403.html"), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html"), 404

    return app


if __name__ == "__main__":
    app = create_app()
    app.secret_key = os.urandom(16)
    csrf = CSRFProtect(app)
    app.run(host="0.0.0.0")
