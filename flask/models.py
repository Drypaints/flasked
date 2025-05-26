from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Optional

db = SQLAlchemy()

class User(db.Model):  # type: ignore
    id: int = db.Column(db.Integer, primary_key=True)
    username: str = db.Column(db.String(80), unique=True, nullable=False)
    password_hash: str = db.Column(db.String(256), nullable=False)
    user_type: str = db.Column(db.String(10), nullable=False, default="normal")  # 'admin' or 'normal'

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)
