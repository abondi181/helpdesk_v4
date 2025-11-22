from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from ..extensions import db
from ..core.constants import ROLE_EMPLOYEE


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    full_name = db.Column(db.String(128), nullable=True)
    email = db.Column(db.String(255), nullable=True)

    password_hash = db.Column(db.String(255), nullable=False)

    role = db.Column(db.String(32), default=ROLE_EMPLOYEE, nullable=False)
    department = db.Column(db.String(80), nullable=True)

    manager_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    manager = db.relationship(
        "User",
        remote_side=[id],
        backref="subordinates",
        lazy="joined"
    )

    is_active_flag = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)



    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def is_active(self) -> bool:  # Flask-Login compatibility
        return self.is_active_flag

    def __repr__(self) -> str:
        return f"<User {self.username}>"
